#!/usr/bin/env python3
"""account_stats — aggregate a set of an account's videos into account-level signals.

Computes the baselines the other tools need (median views, posting cadence),
finds outlier videos, and surfaces the paid-amplification / shadow-account
heuristics from trendwatch principles 8 & 10. Pure compute, no network.

Usage:
  python tiktok_account.py --handle someone | python account_stats.py --in -

Emits account_median_views + follower_count so the result can be piped straight
into engagement.py, and a "signals" block flagging paid-amp / shadow patterns.
"""

import argparse
import statistics

import _common as c

# Disclosure / amplification markers seen in captions or bios.
PAID_MARKERS = ("#ad", "#sponsored", "#partnership", "#paidpartnership", "sponsored",
                "paid partnership", "thanks @", "gifted", "#gifted")


def caption_paid_hits(text: str):
    if not text:
        return []
    low = text.lower()
    return [m for m in PAID_MARKERS if m in low]


def main():
    p = argparse.ArgumentParser(description="Aggregate account-level stats & signals.")
    p.add_argument("--in", dest="infile", help="JSON file, '-' for stdin, or pipe.")
    p.add_argument("--follower-count", type=int, help="Override follower count.")
    p.add_argument("--official-cadence-days", type=float,
                   help="Posting interval of the official account, to test shadow overlap.")
    p.add_argument("--now", help="Override 'now' as ISO date.")
    args = p.parse_args()
    c.set_tool("account_stats")

    payload = c.load_input(args.infile)
    if payload is None:
        c.fail("No input. Pass --in <file> or pipe JSON on stdin.", code="bad_input", exit_code=2)

    if isinstance(payload, dict):
        raw_videos = payload.get("videos") or []
        follower_count = args.follower_count or c.to_int(payload.get("follower_count"))
        bio = payload.get("bio") or payload.get("signature") or ""
        handle = payload.get("handle") or payload.get("username")
        promote_badge = bool(payload.get("promote_badge") or payload.get("is_business"))
    elif isinstance(payload, list):
        raw_videos = payload
        follower_count = args.follower_count
        bio, handle, promote_badge = "", None, False
    else:
        c.fail("Input must be an account object or a list of videos.", code="bad_input", exit_code=2)

    if not raw_videos:
        c.fail("No videos found in input.", code="empty", exit_code=1)

    videos = [c.normalize_video(v) for v in raw_videos if isinstance(v, dict)]
    view_list = sorted(v["views"] for v in videos if v.get("views") is not None)

    now = c.now_utc(args.now)
    dates = sorted(d for d in (c.parse_created(v.get("created")) for v in videos) if d)
    for d in dates:
        if not d.tzinfo:
            from datetime import timezone
            d = d.replace(tzinfo=timezone.utc)

    # Posting cadence from the span of collected posts.
    cadence = None
    if len(dates) >= 2:
        span_days = (dates[-1] - dates[0]).days or 1
        cadence = {
            "posts": len(dates),
            "span_days": span_days,
            "posts_per_week": round(len(dates) / span_days * 7, 2),
            "avg_gap_days": round(span_days / (len(dates) - 1), 2),
        }

    median = statistics.median(view_list) if view_list else None
    mean = round(statistics.mean(view_list), 1) if view_list else None

    # Outliers: views > 5x median (the "most rewatched" proxy).
    outliers = []
    if median:
        for v in videos:
            if v.get("views") and v["views"] > 5 * median:
                outliers.append({"id": v.get("id"), "url": v.get("url"),
                                 "views": v["views"], "x_median": round(v["views"] / median, 1)})
        outliers.sort(key=lambda x: x["x_median"], reverse=True)

    # Paid-amp / shadow signals.
    caption_hits = {}
    for v in videos:
        hits = caption_paid_hits(v.get("caption") or "")
        if hits:
            caption_hits[v.get("id") or v.get("url") or f"idx{len(caption_hits)}"] = hits
    bio_hits = caption_paid_hits(bio)

    shadow_overlap = None
    if args.official_cadence_days and cadence:
        # A shadow alt often mirrors the official account's posting rhythm.
        gap = cadence["avg_gap_days"]
        shadow_overlap = abs(gap - args.official_cadence_days) <= max(0.5, 0.15 * args.official_cadence_days)

    follower_bucket = None
    if follower_count is not None:
        follower_bucket = (
            "<10k" if follower_count < 10_000 else
            "10k-250k (PRIME)" if follower_count < 250_000 else
            "250k-500k" if follower_count < 500_000 else
            "500k-1M (gray)" if follower_count < 1_000_000 else
            ">1M (DROP)")

    signals = {
        "paid_amp_captions": caption_hits,
        "paid_amp_bio": bio_hits,
        "promote_badge": promote_badge,
        "shadow_cadence_overlap": shadow_overlap,
        "paid_amp_suspected": bool(caption_hits or bio_hits or promote_badge),
    }

    c.emit({
        "handle": handle,
        "follower_count": follower_count,
        "follower_bucket": follower_bucket,
        "n_videos": len(videos),
        "account_median_views": median,
        "mean_views": mean,
        "max_views": view_list[-1] if view_list else None,
        "cadence": cadence,
        "outliers_over_5x_median": outliers,
        "signals": signals,
        "size_filter_verdict": (
            "drop_celebrity_tier" if follower_count and follower_count > 1_000_000 else
            "prime_for_mining" if follower_count and 10_000 <= follower_count < 250_000 else
            "usable"),
    })


if __name__ == "__main__":
    main()
