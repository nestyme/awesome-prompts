#!/usr/bin/env python3
"""carousel_leaderboard — offline: posts (from carousel_scan) → per-account carousel metrics.

carousel-benchmark Step 4. Answers "who actually wins with carousels, and is it
organic?" for every account in the input. No network, no keys.

Per account:
  posts, slides, slide_share            how much of the output is carousels
  slide_med, slide_max, hit100k         reach (median / best / % of carousels ≥100k)
  save_rate, share_rate, like_rate      quality signals, pooled over carousels
  susp_paid                             # of carousels with ≥50k views and like-rate <1%
                                        (the Spark-Ads smell — bought views, no love)
  posts_per_week, last_post             cadence
  source                                "profile" (full scan) vs "search" (seen 1–2 posts)
  top                                   the 3 best carousels with URLs

Plus `top_posts` (best carousels across everyone, with like_rate + susp_paid)
and `calibration` (like-rate percentiles of the sample, so the 1% threshold can
be re-checked against this niche instead of trusted blindly).

Usage:
  python3 carousel_scan.py --profiles a b c | python3 carousel_leaderboard.py --md leaderboard.md
  python3 carousel_leaderboard.py --in posts.json --min-slides 5 --md leaderboard.md
  python3 carousel_leaderboard.py --in posts.json --labels labels.json   # optional niche/kind tags
"""

import argparse
import json
import statistics as st
from datetime import datetime

import _common as c


def pct(a, b):
    return round(100.0 * a / b, 2) if b else None


def med(xs):
    return int(st.median(xs)) if xs else None


def parse_dt(v):
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            return datetime.utcfromtimestamp(v if v < 1e11 else v / 1000)
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def account_row(handle, posts, labels):
    a = posts[0]
    slides = [p for p in posts if p.get("is_slideshow")]
    sp = [p.get("views") or 0 for p in slides]
    vp = [p.get("views") or 0 for p in posts if not p.get("is_slideshow")]
    times = sorted(t for t in (parse_dt(p.get("created")) for p in posts) if t)
    weeks = max((times[-1] - times[0]).days / 7, 1 / 7) if len(times) > 1 else None
    tot_views = sum(sp)
    lab = labels.get(handle, {})
    top = sorted(slides, key=lambda p: -(p.get("views") or 0))[:3]
    return {
        "handle": handle, "nick": a.get("author_nick"), "fans": a.get("author_fans"),
        "bio": (a.get("author_bio") or "")[:160], "link": a.get("author_link"),
        "url": a.get("author_url") or f"https://www.tiktok.com/@{handle}",
        "source": "profile" if any(p.get("source") == "profile" for p in posts) else "search",
        "niche": lab.get("niche"), "kind": lab.get("kind"),
        "posts": len(posts), "slides": len(slides), "slide_share": pct(len(slides), len(posts)),
        "slide_med": med(sp), "slide_max": max(sp) if sp else None, "video_med": med(vp),
        "hit100k": pct(sum(1 for x in sp if x >= 100_000), len(sp)) if sp else None,
        "save_rate": pct(sum(p.get("saves") or 0 for p in slides), tot_views) if tot_views else None,
        "share_rate": pct(sum(p.get("shares") or 0 for p in slides), tot_views) if tot_views else None,
        "like_rate": pct(sum(p.get("likes") or 0 for p in slides), tot_views) if tot_views else None,
        "susp_paid": sum(1 for p in slides if (p.get("views") or 0) >= 50_000
                         and (p.get("likes") or 0) / max(p.get("views") or 1, 1) < 0.01),
        "posts_per_week": round(len(posts) / weeks, 1) if weeks else None,
        "last_post": times[-1].date().isoformat() if times else None,
        "top": [{"url": p.get("url"), "views": p.get("views"), "saves": p.get("saves"),
                 "caption": (p.get("caption") or "")[:140]} for p in top],
    }


def fmt(n):
    if n is None: return "—"
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.1f}k" if n >= 1e3 else str(n)


def markdown(rows, top_posts, calib):
    out = ["# Carousel leaderboard", "",
           f"_{len(rows)} accounts · sorted by median carousel views · like-rate p10/median in this sample: "
           f"{calib.get('like_rate_p10')}% / {calib.get('like_rate_median')}%_", "",
           "| account | fans | carousels/posts | median | best | hit ≥100k | save-rate | like-rate | boost? | posts/wk | source |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        out.append(f"| [@{r['handle']}]({r['url']}) | {fmt(r['fans'])} | {r['slides']}/{r['posts']} | **{fmt(r['slide_med'])}** | "
                   f"{fmt(r['slide_max'])} | {r['hit100k'] or 0}% | {r['save_rate'] or 0}% | {r['like_rate'] or 0}% | "
                   f"{r['susp_paid'] or ''} | {r['posts_per_week'] or ''} | {r['source']} |")
    out += ["", "## Top carousels", "", "| # | account | views | saves | save-rate | like-rate | boost? | caption |", "|---:|---|---:|---:|---:|---:|---|---|"]
    for i, p in enumerate(top_posts, 1):
        out.append(f"| {i} | [@{p['handle']}]({p['url']}) | {fmt(p['views'])} | {fmt(p['saves'])} | {p['save_rate'] or 0}% | "
                   f"{p['like_rate'] or 0}% | {'⚠️' if p['susp_paid'] else ''} | {p['caption'][:80]} |")
    return "\n".join(out) + "\n"


def main():
    c.set_tool("carousel_leaderboard")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", help="posts JSON (carousel_scan envelope or a list) or '-' for stdin")
    ap.add_argument("--min-slides", type=int, default=1, help="hide accounts with fewer carousels")
    ap.add_argument("--labels", help='optional JSON {"handle": {"niche": "...", "kind": "official|shadow|creator"}}')
    ap.add_argument("--top", type=int, default=40, help="how many top carousels to list")
    ap.add_argument("--md", help="also write a markdown leaderboard here")
    args = ap.parse_args()

    data = c.load_input(args.inp)
    if data is None:
        c.fail("No input. Pipe carousel_scan output or pass --in posts.json", code="bad_usage", exit_code=2)
    posts = data.get("posts") if isinstance(data, dict) else data
    # accept raw Apify items too (re-normalize through carousel_scan) and fill canonical fields
    import carousel_scan
    posts = [carousel_scan.normalize(p, p.get("_source", "cache")) if p.get("authorMeta") else {**c.normalize_video(p), **p}
             for p in posts]
    labels = json.load(open(args.labels)) if args.labels else {}

    by_id = {}
    for p in posts:
        if p.get("id") and p.get("author"):
            by_id.setdefault(str(p["id"]), p)
    posts = list(by_id.values())
    acc = {}
    for p in posts:
        acc.setdefault(p["author"], []).append(p)
    rows = [account_row(h, ps, labels) for h, ps in acc.items()]
    rows = [r for r in rows if r["slides"] >= args.min_slides]
    rows.sort(key=lambda r: -(r["slide_med"] or 0))

    slides = [p for p in posts if p.get("is_slideshow")]
    tops = sorted(slides, key=lambda p: -(p.get("views") or 0))[:args.top]
    top_posts = [{"handle": p["author"], "fans": p.get("author_fans"), "url": p.get("url"), "views": p.get("views"),
                  "likes": p.get("likes"), "saves": p.get("saves"), "comments": p.get("comments"), "shares": p.get("shares"),
                  "save_rate": pct(p.get("saves") or 0, p.get("views") or 0), "like_rate": pct(p.get("likes") or 0, p.get("views") or 0),
                  "susp_paid": (p.get("views") or 0) >= 50_000 and (p.get("likes") or 0) / max(p.get("views") or 1, 1) < 0.01,
                  "date": str(p.get("created") or "")[:10], "caption": (p.get("caption") or "")[:160]} for p in tops]
    lr = sorted(100 * (p.get("likes") or 0) / p["views"] for p in slides if (p.get("views") or 0) >= 50_000)
    calib = {"n_carousels_50k": len(lr),
             "like_rate_p10": round(lr[len(lr) // 10], 2) if lr else None,
             "like_rate_median": round(lr[len(lr) // 2], 2) if lr else None}
    result = {"accounts": rows, "top_posts": top_posts, "calibration": calib,
              "n_posts": len(posts), "n_slideshows": len(slides), "n_accounts": len(rows)}
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(markdown(rows, top_posts, calib))
        c.log(f"[leaderboard] wrote {args.md}")
    c.emit(result)


if __name__ == "__main__":
    main()
