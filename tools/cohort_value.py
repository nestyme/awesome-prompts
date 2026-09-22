#!/usr/bin/env python3
"""cohort_value — price "almost paid" cohorts and render the one-screen dashboard.

The almost-paid skill's numbers step. Takes the exported cohorts (one CSV or one
JSON list of users, each tagged with a segment), the ARPPU per platform, and the
assumed conversion per segment; emits per-segment size, expected revenue,
revenue per contact, the margin a discount would cost, a priority rank — and
optionally fills the dashboard template.

Pure compute — no network, no keys. Every projection is labelled as an
assumption in the output; replace assumed rates with measured ones after the
first send (``--conversion segment=rate``).

Usage:
  # CSV with columns: user_id, segment[, platform][, trigger_ts][, channel_address]
  python cohort_value.py --in cohorts.csv --arppu 14.99

  # per-platform ARPPU (web has a different price and refund rate than the app store)
  python cohort_value.py --in cohorts.csv --arppu web=13.9 --arppu ios=17.5 \\
      --refund-rate web=0.07 --refund-rate ios=0.014

  # override an assumed conversion with a measured one, and render the dashboard
  python cohort_value.py --in cohorts.csv --arppu 14.99 --conversion checkout_abandoned=0.11 \\
      --dashboard almost-paid.html

  # what would a 50% discount to the trial_lapsed segment cost in margin?
  python cohort_value.py --in cohorts.csv --arppu 14.99 --discount trial_lapsed=0.5

Input JSON alternative: a list of {"user_id", "segment", ...} objects, or an
object with a "users" list. Segment names are normalized (case, spaces, dashes).
"""

import argparse
import csv
import io
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import _common as c

c.set_tool("cohort_value")

# Ordered hottest → coolest. Conversion defaults are deliberately conservative;
# the skill replaces them with measured rates after the first campaign.
SEGMENTS = [
    ("checkout_abandoned", "Checkout abandoned", "hottest", 0.08, "one-tap resume link, no discount on first touch"),
    ("payment_failed", "Payment failed", "hot", 0.25, "retry link — never a discount"),
    ("hit_the_wall", "Hit the wall mid-task", "hot", 0.06, "finish-the-task credit"),
    ("paywall_repeated", "Paywall, repeated", "warm", 0.03, "value-add: extended trial / bonus, time-boxed"),
    ("trial_lapsed", "Trial lapsed, engaged", "warm", 0.04, "time-boxed discount, once, hard expiry"),
    ("paywall_once", "Paywall once, deep", "cool", 0.015, "education touch or normal lifecycle"),
]
ORDER = {key: i for i, (key, *_rest) in enumerate(SEGMENTS)}
ALIASES = {
    "abandoned_checkout": "checkout_abandoned", "checkout": "checkout_abandoned", "cart_abandoned": "checkout_abandoned",
    "billing_error": "payment_failed", "declined": "payment_failed", "billing_issue": "payment_failed",
    "credits_exhausted": "hit_the_wall", "limit_hit": "hit_the_wall", "wall": "hit_the_wall", "insufficient_credits": "hit_the_wall",
    "paywall_repeat": "paywall_repeated", "paywall_2x": "paywall_repeated",
    "trial_expired": "trial_lapsed", "trial": "trial_lapsed",
    "paywall": "paywall_once", "paywall_1x": "paywall_once",
}


def norm_segment(raw: str) -> str:
    key = (raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(key, key)


def parse_kv(values, name, cast=float):
    """--flag key=value (repeatable) or --flag value (applies to all) → dict with '*' default."""
    out = {}
    for item in values or []:
        if "=" in item:
            key, _, val = item.partition("=")
            out[key.strip().lower()] = cast(val)
        else:
            out["*"] = cast(item)
    return out


def lookup(table, key, default=None):
    return table.get(key, table.get("*", default))


def load_users(path: str) -> list[dict]:
    raw = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    stripped = raw.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        data = json.loads(raw)
        users = data.get("users", data) if isinstance(data, dict) else data
    else:
        users = list(csv.DictReader(io.StringIO(raw)))
    if not isinstance(users, list):
        c.fail("Input must be a CSV, a JSON list of users, or {\"users\": [...]}", code="bad_input", exit_code=2)
    return users


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="inp", required=True, help="cohort CSV/JSON path, or - for stdin")
    p.add_argument("--arppu", action="append", required=True, help="ARPPU (list price net of nothing): a number, or platform=number, repeatable")
    p.add_argument("--refund-rate", action="append", help="refund share to subtract from ARPPU: number or platform=number")
    p.add_argument("--conversion", action="append", help="assumed or measured conversion per segment: segment=rate")
    p.add_argument("--discount", action="append", help="discount to cost out per segment: segment=fraction (0.5 = 50%%)")
    p.add_argument("--holdout", type=float, default=0.15, help="share held out of each send for measurement (default 0.15)")
    p.add_argument("--exclude-hours", type=float, default=24, help="drop users whose trigger is younger than this (default 24)")
    p.add_argument("--now", help="ISO timestamp for the recency cut (default: now, UTC)")
    p.add_argument("--dashboard", help="write the filled dashboard HTML here")
    p.add_argument("--csv-dir", help="also write one CSV per segment (send lists) into this directory")
    args = p.parse_args()

    users = load_users(args.inp)
    arppu = parse_kv(args.arppu, "arppu")
    refund = parse_kv(args.refund_rate, "refund-rate")
    conversion_override = parse_kv(args.conversion, "conversion")
    discounts = parse_kv(args.discount, "discount")
    now = datetime.fromisoformat(args.now).astimezone(timezone.utc) if args.now else datetime.now(timezone.utc)

    # Exclude triggers younger than the cut: many "abandoned" checkouts complete on their own within a day,
    # and contacting them earlier books organic conversions to the campaign.
    kept, too_fresh, unknown_segment = [], 0, Counter()
    for u in users:
        seg = norm_segment(u.get("segment"))
        if seg not in ORDER:
            unknown_segment[seg or "(blank)"] += 1
            continue
        ts = u.get("trigger_ts")
        if ts:
            try:
                when = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                if (now - when).total_seconds() < args.exclude_hours * 3600:
                    too_fresh += 1
                    continue
            except ValueError:
                pass
        kept.append({**u, "segment": seg})

    by_segment = defaultdict(list)
    for u in kept:
        by_segment[u["segment"]].append(u)

    rows = []
    for key, label, temperature, default_rate, offer in SEGMENTS:
        members = by_segment.get(key, [])
        if not members:
            continue
        platforms = Counter((u.get("platform") or "*").lower() for u in members)
        # Net ARPPU per member, by platform: list price minus that platform's refund share.
        net_total = 0.0
        missing_arppu = set()
        for plat, count in platforms.items():
            price = lookup(arppu, plat)
            if price is None:
                missing_arppu.add(plat)
                continue
            net_total += count * price * (1 - lookup(refund, plat, 0.0))
        if missing_arppu:
            c.fail(f"No --arppu for platform(s): {sorted(missing_arppu)} (pass --arppu {next(iter(missing_arppu))}=<price> or a bare --arppu for all)",
                   code="missing_arppu", exit_code=2)
        size = len(members)
        net_arppu = net_total / size
        rate = conversion_override.get(key, default_rate)
        measured = key in conversion_override
        sendable = int(round(size * (1 - args.holdout)))
        expected = sendable * net_arppu * rate
        row = {
            "segment": key, "label": label, "temperature": temperature,
            "size": size, "sendable_after_holdout": sendable, "held_out": size - sendable,
            "platforms": dict(platforms),
            "net_arppu": round(net_arppu, 2),
            "conversion": rate, "conversion_source": "measured" if measured else "assumed",
            "expected_revenue": round(expected, 2),
            "revenue_per_contact": round(net_arppu * rate, 3),
            "offer": offer,
        }
        d = discounts.get(key)
        if d is not None:
            # Margin given away to the people who would have paid at full price anyway, at the segment's own rate.
            row["discount"] = d
            row["discount_cost_on_organic"] = round(sendable * net_arppu * rate * d, 2)
            row["breakeven_extra_conversion"] = round(rate * d / (1 - d), 4) if d < 1 else None
        rows.append(row)

    rows.sort(key=lambda r: (-r["revenue_per_contact"], ORDER[r["segment"]]))
    for i, r in enumerate(rows, 1):
        r["priority"] = i

    total_expected = round(sum(r["expected_revenue"] for r in rows), 2)
    data = {
        "as_of": now.isoformat(timespec="seconds"),
        "assumption_note": "expected_revenue uses assumed conversion rates unless conversion_source is 'measured'; "
                           "replace after the first send (--conversion segment=rate)",
        "totals": {
            "users_in": len(users), "users_kept": len(kept), "excluded_too_fresh": too_fresh,
            "unknown_segments": dict(unknown_segment), "expected_revenue": total_expected,
            "holdout": args.holdout, "exclude_hours": args.exclude_hours,
        },
        "segments": rows,
    }

    if args.csv_dir:
        os.makedirs(args.csv_dir, exist_ok=True)
        fields = ["user_id", "channel_address", "segment", "platform", "trigger_ts", "offer_code", "expiry"]
        for key, members in by_segment.items():
            with open(os.path.join(args.csv_dir, f"{key}.csv"), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
                w.writeheader()
                for u in members:
                    w.writerow({f: u.get(f, "") for f in fields})
        data["csv_dir"] = args.csv_dir
        c.log(f"wrote {len(by_segment)} segment CSVs to {args.csv_dir}")

    if args.dashboard:
        template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "almost-paid", "templates", "dashboard.html")
        if not os.path.exists(template):
            c.fail(f"dashboard template not found at {template}", code="missing_template")
        html = open(template, "r", encoding="utf-8").read().replace("/*__DATA__*/null", json.dumps(data, default=str))
        with open(args.dashboard, "w", encoding="utf-8") as fh:
            fh.write(html)
        data["dashboard"] = args.dashboard
        c.log(f"wrote dashboard to {args.dashboard}")

    c.emit(data)


if __name__ == "__main__":
    main()
