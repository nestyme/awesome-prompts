#!/usr/bin/env python3
"""TikTok shadowban check — probability, likely causes, what to do.

Give it account handles and an Apify token; it returns, per account, a
shadowban probability (0–100%), the distribution-round histogram behind it,
the spam/automation signals it found, what works vs what flops, and a fix list.

    python3 shadowban_check.py handle1 handle2 --apify-key apify_api_xxx
    APIFY_TOKEN=... python3 shadowban_check.py handle1 handle2
    OPENROUTER_API_KEY=...   # optional: adds an LLM "what works / what flops" read

Data: Apify `clockworks~tiktok-profile-scraper` (last ≤30 posts per profile,
≈$0.01/account). Output: a table on stdout + `shadowban_reports/<date>_<handle>.md`.

The model behind the verdict: TikTok distributes in ROUNDS. Every post gets a
seed batch (~200–500 views); only if that batch's watch-time / completion /
saves clear the bar does the post get the next round. So the histogram of
posts by round is the diagnostic, not the average.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROUNDS = [("R0 never left seed", 0, 200), ("R1 seed, no expansion", 200, 500),
          ("R2 one expansion", 500, 2000), ("R3 FYP traction", 2000, 20000),
          ("R4 viral", 20000, 10**12)]


def scrape(handles: list[str], token: str) -> list[dict]:
    url = ("https://api.apify.com/v2/acts/clockworks~tiktok-profile-scraper/"
           f"run-sync-get-dataset-items?token={token}&timeout=300")
    body = {"profiles": handles, "resultsPerPage": 30,
            "shouldDownloadVideos": False, "shouldDownloadCovers": False}
    req = urllib.request.Request(url, json.dumps(body).encode(),
                                 {"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=330) as r:
        return json.load(r)


def round_of(v: int) -> str:
    for name, lo, hi in ROUNDS:
        if lo <= v < hi:
            return name
    return ROUNDS[-1][0]


def analyse(handle: str, posts: list[dict]) -> dict:
    posts = sorted(posts, key=lambda p: p.get("createTimeISO", ""))
    if not posts:
        return {"handle": handle, "error": "no posts returned (private, banned, or wrong handle)"}
    a = posts[0].get("authorMeta", {})
    n = len(posts)
    views = [p.get("playCount", 0) for p in posts]
    tot_v = sum(views) or 1
    eng = sum(p.get("diggCount", 0) + p.get("commentCount", 0) + p.get("shareCount", 0)
              for p in posts) / tot_v * 100
    save_rate = sum(p.get("collectCount", 0) for p in posts) / tot_v * 100
    med = statistics.median(views)
    rounds = Counter(round_of(v) for v in views)
    r0 = rounds[ROUNDS[0][0]] / n
    zero = sum(1 for v in views if v == 0) / n
    last, prev = views[-10:], views[-20:-10]
    trend = (statistics.median(last) / statistics.median(prev)
             if prev and statistics.median(prev) else None)
    times = [datetime.fromisoformat(p["createTimeISO"].replace("Z", "+00:00"))
             for p in posts if p.get("createTimeISO")]
    days = (times[-1] - times[0]).days + 1 if len(times) > 1 else 1
    per_day = n / days
    bursts = sum(1 for i in range(1, len(times))
                 if (times[i] - times[i - 1]).total_seconds() < 3600)
    caps = [re.sub(r"#\S+", "", p.get("text", "") or "").strip().lower() for p in posts]
    dup_caps = n - len(set(c for c in caps if c))
    tags = Counter(t.get("name", "") for p in posts for t in p.get("hashtags", []))
    stale_tags = [t for t, c in tags.most_common(5) if c >= n * 0.6]

    # ---- probability (0–100) ----
    score = 0
    score += min(40, int(r0 * 60))            # share of posts stuck in seed
    score += 20 if med < 300 else (10 if med < 500 else 0)
    score += min(20, int(zero * 60))          # zero-view posts
    score += 10 if bursts >= 3 else 0
    score += 10 if dup_caps >= 3 else 0
    prob = min(100, score)

    causes, fixes = [], []
    if zero > 0.3:
        causes.append(f"{zero:.0%} of posts have ZERO views — posts are not even seeded; "
                      "check Account status in-app (strike / private / under review)")
        fixes.append("Open Settings → Privacy & Safety → Account status; appeal any strike")
    if r0 >= 0.5 and med < 300:
        if eng >= 1.0:
            causes.append(f"engagement is healthy ({eng:.1f}%) yet {r0:.0%} of posts never "
                          "leave the seed batch — the ACCOUNT is throttled, not the content")
            fixes.append("Pause 48–72h, then 1 post/day from the phone with a library sound; "
                         "do NOT recreate the account unless Account status shows strikes")
        else:
            causes.append(f"engagement is low ({eng:.1f}%) and {r0:.0%} of posts die in the "
                          "seed batch — the CONTENT fails TikTok's first test (hook/retention)")
            fixes.append("Fix slide 1 / first 1.5s: specific number + concrete object + "
                         "mistake-or-rule; copy a format that already prints in your niche")
    elif med < 800:
        causes.append("seed batch passes but posts never expand (stuck at R1–R2) — "
                      "retention/saves don't clear the second-round bar")
        fixes.append("Optimise for completion + saves: shorter, one idea per post, "
                     "'save this' payoff on the last slide")
    if bursts >= 3:
        causes.append(f"{bursts} posts published <1h apart — burst posting reads as automation/spam")
        fixes.append("Space posts ≥6h apart, max 2/day, same daily window")
    if per_day > 3:
        causes.append(f"{per_day:.1f} posts/day — above human-normal velocity")
    if dup_caps >= 3:
        causes.append(f"{dup_caps} duplicate captions — near-identical content is FYF-ineligible "
                      "and a pattern of it de-recommends the whole account")
        fixes.append("Unique caption per post; rotate hashtags; never mirror one post across accounts")
    if stale_tags:
        causes.append("same hashtags on ≥60% of posts (" + " ".join("#" + t for t in stale_tags) + ")")
    if trend and trend < 0.6:
        causes.append(f"downtrend: last-10 median is {trend:.0%} of the previous 10")
    if trend and trend > 1.5:
        causes.append(f"uptrend ({trend:.0%}) — something recent worked; see TOP")
    if not causes:
        causes.append("no spam/automation signals; reach is content-limited")

    ranked = sorted(posts, key=lambda p: -p.get("playCount", 0))
    def brief(p):
        kind = "slideshow" if (p.get("videoMeta", {}) or {}).get("duration", 0) == 0 else "video"
        return (f"{p.get('playCount',0):>7,} views · {p.get('collectCount',0)} saves · {kind} · "
                f"{p.get('createTimeISO','')[:10]} · {(p.get('text','') or '')[:110].replace(chr(10),' ')}")
    return {"handle": handle, "followers": a.get("fans", 0), "posts": n, "days": days,
            "per_day": round(per_day, 2), "median": med, "eng": round(eng, 2),
            "save_rate": round(save_rate, 2), "rounds": dict(rounds), "r0": r0,
            "zero": zero, "trend": round(trend, 2) if trend else None,
            "prob": prob, "causes": causes, "fixes": fixes,
            "top": [brief(p) for p in ranked[:5]], "bottom": [brief(p) for p in ranked[-5:]]}


def llm_read(res: dict, key: str) -> str:
    import requests
    prompt = ("You are a TikTok growth analyst. In ≤120 words: (1) WHAT WORKS — what the "
              "top posts share (hook, topic, format); (2) WHAT FLOPS — what the bottom posts "
              "share; (3) three concrete recommendations for next week. Reference posts.\n\n"
              f"@{res['handle']}, followers {res['followers']}, median views {res['median']}, "
              f"eng {res['eng']}%, save-rate {res['save_rate']}%, shadowban probability {res['prob']}%\n"
              "TOP:\n" + "\n".join(res["top"]) + "\nBOTTOM:\n" + "\n".join(res["bottom"]))
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers={"Authorization": f"Bearer {key}"},
                          json={"model": "anthropic/claude-sonnet-4.5",
                                "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(LLM read failed: {str(e)[:60]})"


def report(res: dict, insights: str) -> str:
    L = [f"# @{res['handle']} — shadowban check {datetime.now():%Y-%m-%d}", "",
         f"## Shadowban probability: **{res['prob']}%**", "",
         f"- followers {res['followers']:,} · {res['posts']} posts over {res['days']} days ({res['per_day']}/day)",
         f"- median views **{res['median']:,.0f}** · engagement {res['eng']}% · save-rate {res['save_rate']}%",
         "- rounds: " + " · ".join(f"{k}: {v}" for k, v in sorted(res["rounds"].items())),
         f"- stuck in R0 (<200 views): **{res['r0']:.0%}** · zero-view posts: {res['zero']:.0%}",
         f"- trend (last 10 vs previous 10): {res['trend'] if res['trend'] else '—'}",
         "", "## Likely causes"] + [f"- {c}" for c in res["causes"]]
    L += ["", "## What to do"] + [f"- {f}" for f in res["fixes"] or ["- keep posting; iterate on hooks"]]
    L += ["", "## Top 5"] + [f"- {t}" for t in res["top"]]
    L += ["", "## Bottom 5"] + [f"- {t}" for t in res["bottom"]]
    if insights:
        L += ["", "## What works / what flops / next week", insights]
    L += ["", "## Manual checks (official)",
          "- Settings → Privacy & Safety → Account status: strikes, 'not eligible for recommendation'",
          "- Pause 48–72h → one original post → >500 views in 24h means the throttle is lifting",
          "- Post from the phone with a library sound; different formats per account; never buy accounts"]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok shadowban probability + causes + fixes")
    ap.add_argument("handles", nargs="+")
    ap.add_argument("--apify-key", default=os.environ.get("APIFY_TOKEN"))
    ap.add_argument("--openrouter-key", default=os.environ.get("OPENROUTER_API_KEY"))
    ap.add_argument("--cache", help="reuse a saved Apify JSON instead of scraping")
    ap.add_argument("--out", default="shadowban_reports")
    args = ap.parse_args()
    if not args.cache and not args.apify_key:
        sys.exit("need --apify-key (or APIFY_TOKEN env)")
    items = json.load(open(args.cache)) if args.cache else scrape(args.handles, args.apify_key)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out / f"{datetime.now():%Y-%m-%d}_raw.json").write_text(json.dumps(items))
    by = defaultdict(list)
    for it in items:
        by[it.get("authorMeta", {}).get("name", "?")].append(it)
    print(f"{'handle':<18}{'prob':>6}{'median':>9}{'R0%':>6}{'eng':>7}{'trend':>7}")
    for h in args.handles:
        res = analyse(h, by.get(h, []))
        if "error" in res:
            print(f"{h:<18} — {res['error']}"); continue
        ins = llm_read(res, args.openrouter_key) if args.openrouter_key else ""
        (out / f"{datetime.now():%Y-%m-%d}_{h}.md").write_text(report(res, ins))
        print(f"{h:<18}{res['prob']:>5}%{res['median']:>9,.0f}{res['r0']:>6.0%}"
              f"{res['eng']:>6.1f}%{(str(res['trend']) if res['trend'] else '—'):>7}")
    print(f"\nreports -> {out}/")


if __name__ == "__main__":
    main()
