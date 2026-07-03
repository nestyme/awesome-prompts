#!/usr/bin/env python3
"""schedule_post — schedule a carousel/video to social channels via Postiz.

carousel-conveyor Step 6. Wraps the Postiz API: list channels (to confirm the
handle->id mapping) and schedule a post with the AI-content flag set. Defaults to
--dry-run: it will NOT post live unless you pass --live. Always sets
video_made_with_ai / AI-disclosure true (principle 6).

Usage:
  python schedule_post.py --list-channels
  python schedule_post.py --channel-id abc123 --when 2026-07-02T08:30:00 \\
      --caption "$(cat caption.txt)" --media slide_01.png --media slide_02.png --dry-run

Requires: requests + env POSTIZ_API_KEY (and optional POSTIZ_BASE_URL).
"""

import argparse
import os

import _common as c


def api(requests, base, key, method, path, **kw):
    url = base.rstrip("/") + path
    headers = {"Authorization": key, "Content-Type": "application/json"}
    r = requests.request(method, url, headers=headers, timeout=30, **kw)
    r.raise_for_status()
    return r.json() if r.text else {}


def main():
    p = argparse.ArgumentParser(description="Schedule a post via Postiz (AI-disclosed).")
    p.add_argument("--list-channels", action="store_true", help="List channels then exit.")
    p.add_argument("--channel-id", action="append", default=[])
    p.add_argument("--when", help="ISO datetime for the slot, e.g. 2026-07-02T08:30:00.")
    p.add_argument("--caption", default="")
    p.add_argument("--media", action="append", default=[], help="Media file paths (slides/video).")
    p.add_argument("--as-draft", action="store_true")
    live = p.add_mutually_exclusive_group()
    live.add_argument("--dry-run", action="store_true", default=True)
    live.add_argument("--live", dest="dry_run", action="store_false",
                      help="Actually POST to Postiz. Only after the visual gate.")
    args = p.parse_args()
    c.set_tool("schedule_post")

    requests = c.require("requests")
    key = c.env("POSTIZ_API_KEY")
    base = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com")

    if args.list_channels:
        try:
            data = api(requests, base, key, "GET", "/public/v1/integrations")
        except Exception as exc:
            c.fail(f"Listing channels failed: {exc}", code="api_error")
        chans = [{"id": ch.get("id"), "name": ch.get("name"),
                  "platform": ch.get("identifier") or ch.get("platform")}
                 for ch in (data if isinstance(data, list) else data.get("integrations", []))]
        c.emit({"channels": chans})

    if not args.channel_id or not args.when:
        c.fail("Need --channel-id and --when (or --list-channels).", code="bad_input", exit_code=2)
    for m in args.media:
        if not os.path.exists(m):
            c.fail(f"Media not found: {m}", code="not_found")

    post = {
        "type": "draft" if args.as_draft else "schedule",
        "date": args.when,
        "posts": [{
            "integration": {"id": cid},
            "value": [{"content": args.caption, "media": args.media}],
            "settings": {"video_made_with_ai": True, "ai_disclosure": True},
        } for cid in args.channel_id],
    }

    if args.dry_run:
        c.emit({"dry_run": True, "would_post": post,
                "note": "No request sent. Re-run with --live after the Step 5 visual gate."})

    try:
        resp = api(requests, base, key, "POST", "/public/v1/posts", json=post)
    except Exception as exc:
        c.fail(f"Scheduling failed: {exc}", code="api_error")
    c.emit({"dry_run": False, "scheduled": True, "response": resp})


if __name__ == "__main__":
    main()
