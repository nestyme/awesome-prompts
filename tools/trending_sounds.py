#!/usr/bin/env python3
"""trending_sounds — pull trending sounds / hashtags from TikTok Creative Center.

trendwatch Step 3 helper. Fetches the public Creative Center trend lists for a
region + vertical so the agent can recommend sounds that are actually rising/
peaking (never a stale one). Because Creative Center is JS-heavy and rate-limits,
this uses its public JSON endpoints and degrades gracefully with a clear hint to
fall back to WebFetch if the layout changed.

Usage:
  python trending_sounds.py --kind songs --region US --limit 20
  python trending_sounds.py --kind hashtags --region GB

Requires: requests (pip install requests). Falls back with guidance if TikTok
changes the endpoint.
"""

import argparse

import _common as c

BASE = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend"
ENDPOINTS = {
    "songs": f"{BASE}/sound/list",
    "hashtags": f"{BASE}/hashtag/list",
}


def main():
    p = argparse.ArgumentParser(description="Fetch TikTok Creative Center trends.")
    p.add_argument("--kind", choices=["songs", "hashtags"], default="songs")
    p.add_argument("--region", default="US", help="ISO country code, e.g. US, GB, DE.")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--period", type=int, default=7, help="Trailing window in days: 7/30/120.")
    args = p.parse_args()
    c.set_tool("trending_sounds")

    requests = c.require("requests")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Accept": "application/json",
        "referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/",
    }
    params = {"page": 1, "limit": args.limit, "period": args.period,
              "country_code": args.region, "rank_type": "popular"}
    try:
        r = requests.get(ENDPOINTS[args.kind], params=params, headers=headers, timeout=20)
        r.raise_for_status()
        body = r.json()
    except Exception as exc:
        c.fail(f"Creative Center fetch failed: {exc}. TikTok gates this endpoint and "
               f"rotates it often — fall back to WebFetch of "
               f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/"
               f"{args.kind}/pc/en",
               code="fetch_failed", region=args.region, kind=args.kind)

    items = (body.get("data") or {}).get("list") or body.get("list") or []
    trimmed = []
    for it in items[: args.limit]:
        trimmed.append({
            "title": it.get("song_title") or it.get("title") or it.get("hashtag_name"),
            "author": it.get("author"),
            "id": it.get("song_id") or it.get("hashtag_id") or it.get("clip_id"),
            "rank": it.get("rank"),
            "trend": it.get("trend"),  # rising/flat as reported
            "publish_count": it.get("publish_cnt") or it.get("video_views"),
        })

    if not trimmed:
        c.fail("Endpoint returned no items (layout may have changed). Fall back to WebFetch.",
               code="empty", raw_keys=list(body.keys()))

    c.emit({"kind": args.kind, "region": args.region, "period_days": args.period,
            "items": trimmed,
            "note": "Cross-check lifecycle: only recommend sounds still rising/peaking; "
                    "verify freshness against the video that surfaced them."})


if __name__ == "__main__":
    main()
