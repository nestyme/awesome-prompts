#!/usr/bin/env python3
"""carousel_scan — collect TikTok posts (videos AND photo-mode carousels) via Apify.

carousel-benchmark Step 2/3 collection. Two modes, both through Apify's
`clockworks~tiktok-scraper` (pay-per-result, ≈$0.003 per post):

  --queries  "digital closet app" "apps every girl needs"   # keyword discovery
  --profiles handle1 handle2 --per-profile 30                 # full profile scans
  --posts    https://www.tiktok.com/@x/photo/123 ... --slides-dir out/  # single posts + slide images

The one thing that makes this work: keyword search must hit TikTok's *Top*
section. The scraper's `searchSection: "/video"` and `hashtags` inputs return
ZERO photo posts, so a naive search makes carousels invisible. This tool never
sets searchSection, and it marks every post with `is_slideshow` / `slide_count`.

Output: {"posts": [...normalized...], "runs": [...], "cost_usd": x}. Posts carry
the shared fields (views/likes/comments/shares/saves/created/url/caption/pinned)
plus author_* fields, so they pipe straight into carousel_leaderboard.py.

Usage:
  python3 carousel_scan.py --queries "outfit app" "closet app" --per-query 30
  python3 carousel_scan.py --profiles grindai.app sourhealing --per-profile 25
  python3 carousel_scan.py --posts URL1 URL2 --slides-dir slides/
  python3 carousel_scan.py --cache raw.json            # re-normalize a saved Apify dataset

Key: APIFY_TOKEN (or APIFY_API_TOKEN) in env or tools/.env.
"""

import argparse
import json
import os
import sys
import time
import urllib.request

import _common as c

ACTOR = "clockworks~tiktok-scraper"
API = "https://api.apify.com/v2"


def _http(url, payload=None, timeout=120):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def run_actor(token, run_input, label):
    """Start a run, poll until done, return (items, usd)."""
    c.log(f"[apify] start {label}")
    r = _http(f"{API}/acts/{ACTOR}/runs?token={token}", run_input)
    run_id = r["data"]["id"]; ds = r["data"]["defaultDatasetId"]
    while True:
        st = _http(f"{API}/actor-runs/{run_id}?token={token}")["data"]
        if st["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
        time.sleep(8)
    usd = float(st.get("usageTotalUsd") or 0)
    if st["status"] != "SUCCEEDED":
        c.fail(f"Apify run {run_id} ended with {st['status']}", code="apify_failed", run_id=run_id)
    items = _http(f"{API}/datasets/{ds}/items?token={token}&clean=true", timeout=300)
    c.log(f"[apify] {label}: {len(items)} items, ${usd:.3f}")
    return items, usd


def normalize(item, source):
    a = item.get("authorMeta") or {}
    v = c.normalize_video(item)
    slides = item.get("slideshowImageLinks") or []
    v.update({
        "is_slideshow": bool(item.get("isSlideshow")),
        "slide_count": len(slides) if slides else None,
        "slide_urls": [s.get("tiktokLink") for s in slides if isinstance(s, dict)] or None,
        "author": a.get("name"), "author_nick": a.get("nickName"),
        "author_fans": c.to_int(a.get("fans")), "author_bio": a.get("signature"),
        "author_link": a.get("bioLink"), "author_url": a.get("profileUrl"),
        "search_query": item.get("searchQuery"), "source": source,
        "is_ad": bool(item.get("isAd") or item.get("isSponsored")),
    })
    return v


def download_slides(posts, out_dir):
    """Save each carousel's slides + a contact sheet (needs Pillow for the sheet)."""
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for p in posts:
        if not p.get("slide_urls"):
            continue
        tag = f"{p['author']}-{str(p['id'])[-6:]}"
        files = []
        for i, u in enumerate(p["slide_urls"], 1):
            path = os.path.join(out_dir, f"{tag}_{i:02d}.jpg")
            try:
                urllib.request.urlretrieve(u, path); files.append(path)
            except Exception as exc:
                c.log(f"[slides] {tag} #{i}: {exc}")
        try:
            from PIL import Image
            ims = [Image.open(f).convert("RGB") for f in files]
            W = 360; ims = [im.resize((W, int(im.height * W / im.width))) for im in ims]
            H = max(im.height for im in ims); per = 6; rows = (len(ims) + per - 1) // per
            sheet = Image.new("RGB", (W * min(per, len(ims)) + 8 * (min(per, len(ims)) - 1), H * rows + 8 * (rows - 1)), "white")
            for i, im in enumerate(ims):
                sheet.paste(im, ((i % per) * (W + 8), (i // per) * (H + 8)))
            sheet_path = os.path.join(out_dir, f"sheet_{tag}.jpg"); sheet.save(sheet_path, quality=85)
            p["slides_sheet"] = sheet_path
        except ImportError:
            c.log("[slides] Pillow not installed — slides saved, no contact sheet")
        p["slides_files"] = files; saved.append(tag)
    return saved


def main():
    c.set_tool("carousel_scan")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queries", nargs="*", default=[], help="keyword searches (Top section — includes carousels)")
    ap.add_argument("--per-query", type=int, default=30)
    ap.add_argument("--profiles", nargs="*", default=[], help="TikTok handles to scan fully")
    ap.add_argument("--per-profile", type=int, default=30)
    ap.add_argument("--posts", nargs="*", default=[], help="post URLs (video or photo) to fetch")
    ap.add_argument("--slides-dir", help="download slide images of fetched carousels here (+ contact sheet)")
    ap.add_argument("--cache", help="re-normalize a saved raw Apify dataset (JSON array) instead of scraping")
    ap.add_argument("--save-raw", help="write the raw Apify items to this JSON file")
    ap.add_argument("--only-slideshows", action="store_true", help="drop videos from the output")
    args = ap.parse_args()

    raw, runs, cost = [], [], 0.0
    if args.cache:
        raw = json.load(open(args.cache)); runs.append({"cache": args.cache})
    else:
        if not (args.queries or args.profiles or args.posts):
            c.fail("Give --queries, --profiles, --posts or --cache.", code="bad_usage", exit_code=2)
        token = c.env_any(["APIFY_TOKEN", "APIFY_API_TOKEN"], label="APIFY_TOKEN")
        base = {"shouldDownloadCovers": False, "shouldDownloadSlideshowImages": False}
        if args.queries:   # NOTE: no searchSection → Top results, carousels included
            items, usd = run_actor(token, {**base, "searchQueries": args.queries, "resultsPerPage": args.per_query}, "search")
            for it in items: it["_source"] = "search"
            raw += items; cost += usd; runs.append({"kind": "search", "n": len(items), "usd": usd})
        if args.profiles:
            items, usd = run_actor(token, {**base, "profiles": args.profiles, "resultsPerPage": args.per_profile,
                                           "profileSorting": "latest"}, "profiles")
            for it in items: it["_source"] = "profile"
            raw += items; cost += usd; runs.append({"kind": "profiles", "n": len(items), "usd": usd})
        if args.posts:
            items, usd = run_actor(token, {**base, "postURLs": args.posts}, "posts")
            for it in items: it["_source"] = "post"
            raw += items; cost += usd; runs.append({"kind": "posts", "n": len(items), "usd": usd})
        if args.save_raw:
            json.dump(raw, open(args.save_raw, "w"), ensure_ascii=False)

    posts = [normalize(it, it.get("_source", "cache")) for it in raw if it.get("id") and it.get("authorMeta")]
    if args.only_slideshows:
        posts = [p for p in posts if p["is_slideshow"]]
    if args.slides_dir:
        download_slides([p for p in posts if p["is_slideshow"]], args.slides_dir)
    n_slides = sum(1 for p in posts if p["is_slideshow"])
    c.log(f"[scan] {len(posts)} posts, {n_slides} carousels")
    c.emit({"posts": posts, "runs": runs, "cost_usd": round(cost, 3),
            "n_posts": len(posts), "n_slideshows": n_slides})


if __name__ == "__main__":
    main()
