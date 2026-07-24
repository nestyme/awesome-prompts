#!/usr/bin/env python3
"""schedule_post — schedule a carousel/video to social channels via Buffer or Postiz.

carousel-conveyor Step 6. Two backends behind one CLI:

- **buffer** (GraphQL, api.buffer.com) — personal API key (`BUFFER_API_KEY`).
  Media must be PUBLIC HTTPS URLs (`--media-url`); Buffer has no upload
  endpoint, so host slides first (e.g. a public R2 bucket / Cloudinary) and the
  URL must stay reachable until the post publishes (no expiring signed URLs).
  NOTE: Buffer's API cannot set TikTok's AI-generated-content flag — enable the
  AI-disclosure toggle on the platform/composer side (principle 6 still holds).
- **postiz** (REST) — `POSTIZ_API_KEY` (+ optional `POSTIZ_BASE_URL`). Accepts
  local file paths via `--media`; always sets video_made_with_ai/ai_disclosure.

Backend is auto-picked from whichever key is set (explicit `--backend` wins).
Defaults to --dry-run: it will NOT post live unless you pass --live.

Usage:
  python schedule_post.py --list-channels
  python schedule_post.py --channel-id abc123 --when 2026-07-02T08:30:00 \\
      --caption "$(cat caption.txt)" --media-url https://cdn.example/slide_01.png \\
      --media-url https://cdn.example/slide_02.png --dry-run

`--when` is ISO 8601; a naive datetime is treated as LOCAL time and converted
to UTC for Buffer.

Requires: requests + env BUFFER_API_KEY or POSTIZ_API_KEY.
"""

import argparse
import json
import os
from datetime import datetime, timezone

import _common as c

BUFFER_URL = "https://api.buffer.com"


# --- Postiz (REST) -----------------------------------------------------------

def postiz_api(requests, base, key, method, path, **kw):
    url = base.rstrip("/") + path
    headers = {"Authorization": key, "Content-Type": "application/json"}
    r = requests.request(method, url, headers=headers, timeout=30, **kw)
    r.raise_for_status()
    return r.json() if r.text else {}


def postiz_list_channels(requests, key):
    base = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com")
    data = postiz_api(requests, base, key, "GET", "/public/v1/integrations")
    return [{"id": ch.get("id"), "name": ch.get("name"),
             "platform": ch.get("identifier") or ch.get("platform")}
            for ch in (data if isinstance(data, list) else data.get("integrations", []))]


def postiz_schedule(requests, key, args):
    base = os.environ.get("POSTIZ_BASE_URL", "https://api.postiz.com")
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
        c.emit({"backend": "postiz", "dry_run": True, "would_post": post,
                "note": "No request sent. Re-run with --live after the Step 5 visual gate."})
    resp = postiz_api(requests, base, key, "POST", "/public/v1/posts", json=post)
    c.emit({"backend": "postiz", "dry_run": False, "scheduled": True, "response": resp})


# --- Buffer (GraphQL) --------------------------------------------------------

def buffer_gql(requests, key, query):
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    r = requests.post(BUFFER_URL, headers=headers, json={"query": query}, timeout=30)
    r.raise_for_status()
    body = r.json()
    if body.get("errors"):
        raise RuntimeError("; ".join(e.get("message", "?") for e in body["errors"]))
    return body.get("data") or {}


def buffer_list_channels(requests, key):
    orgs = buffer_gql(requests, key,
                      "query { account { organizations { id name } } }"
                      )["account"]["organizations"]
    chans = []
    for org in orgs:
        data = buffer_gql(requests, key, """
            query {
              channels(input: {organizationId: %s}) {
                id name displayName service isQueuePaused
              }
            }""" % json.dumps(org["id"]))
        for ch in data["channels"]:
            chans.append({"id": ch["id"], "name": ch.get("displayName") or ch.get("name"),
                          "platform": ch.get("service"), "organization": org.get("name"),
                          "queue_paused": ch.get("isQueuePaused")})
    return chans


def buffer_due_at(when: str) -> str:
    """ISO input -> ISO UTC (naive input treated as local time)."""
    try:
        dt = datetime.fromisoformat(when)
    except ValueError:
        c.fail(f"--when is not ISO 8601: {when}", code="bad_input", exit_code=2)
    if dt.tzinfo is None:
        dt = dt.astimezone()  # attach local tz
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def buffer_schedule(requests, key, args):
    if args.media:
        c.fail("The buffer backend needs PUBLIC HTTPS URLs via --media-url "
               "(Buffer's API has no media upload). Host the slides (public R2 "
               "bucket, Cloudinary, ...) and pass their URLs in slide order.",
               code="bad_input", exit_code=2)
    due = buffer_due_at(args.when)
    assets = "".join("{image: {url: %s}}," % json.dumps(u) for u in args.media_url)
    draft = "saveToDraft: true" if args.as_draft else ""
    results = []
    for cid in args.channel_id:
        mutation = """
        mutation {
          createPost(input: {
            text: %s
            channelId: %s
            schedulingType: automatic
            mode: customScheduled
            dueAt: %s
            aiAssisted: true
            %s
            assets: [%s]
          }) {
            ... on PostActionSuccess { post { id status dueAt } }
            ... on MutationError { message }
          }
        }""" % (json.dumps(args.caption), json.dumps(cid), json.dumps(due), draft, assets)
        if args.dry_run:
            results.append({"channel_id": cid, "would_send": mutation.strip()})
            continue
        out = buffer_gql(requests, key, mutation)["createPost"]
        if out.get("message"):
            c.fail(f"Buffer rejected the post for {cid}: {out['message']}", code="api_error")
        results.append({"channel_id": cid, "post": out.get("post")})
    note = ("Buffer's API cannot set the platform AI-generated-content flag — "
            "make sure AI disclosure is enabled on the account/post (principle 6).")
    if args.dry_run:
        c.emit({"backend": "buffer", "dry_run": True, "due_at_utc": due,
                "would_post": results,
                "note": "No request sent. Re-run with --live after the Step 5 visual gate. " + note})
    c.emit({"backend": "buffer", "dry_run": False, "scheduled": True,
            "due_at_utc": due, "results": results, "note": note})


# --- CLI ---------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Schedule a post via Buffer or Postiz (AI-disclosed).")
    p.add_argument("--backend", choices=["auto", "buffer", "postiz"], default="auto",
                   help="auto = whichever API key is set (buffer wins if both).")
    p.add_argument("--list-channels", action="store_true", help="List channels then exit.")
    p.add_argument("--channel-id", action="append", default=[])
    p.add_argument("--when", help="ISO datetime for the slot, e.g. 2026-07-02T08:30:00 (naive = local).")
    p.add_argument("--caption", default="")
    p.add_argument("--media", action="append", default=[],
                   help="Local media file paths (postiz backend only).")
    p.add_argument("--media-url", action="append", default=[],
                   help="Public HTTPS media URLs in slide order (buffer backend).")
    p.add_argument("--as-draft", action="store_true",
                   help="Save as a draft (Buffer: saveToDraft; Postiz: type=draft). Never publishes.")
    live = p.add_mutually_exclusive_group()
    live.add_argument("--dry-run", action="store_true", default=True)
    live.add_argument("--live", dest="dry_run", action="store_false",
                      help="Actually send the request. Only after the visual gate.")
    args = p.parse_args()
    c.set_tool("schedule_post")

    requests = c.require("requests")

    backend = args.backend
    if backend == "auto":
        if os.environ.get("BUFFER_API_KEY"):
            backend = "buffer"
        elif os.environ.get("POSTIZ_API_KEY"):
            backend = "postiz"
        else:
            c.fail("Set BUFFER_API_KEY or POSTIZ_API_KEY (or pass --backend).",
                   code="missing_env", exit_code=2)
    key = c.env("BUFFER_API_KEY" if backend == "buffer" else "POSTIZ_API_KEY")

    if args.list_channels:
        try:
            chans = (buffer_list_channels if backend == "buffer" else postiz_list_channels)(requests, key)
        except Exception as exc:
            c.fail(f"Listing channels failed: {exc}", code="api_error")
        c.emit({"backend": backend, "channels": chans})

    if not args.channel_id or not args.when:
        c.fail("Need --channel-id and --when (or --list-channels).", code="bad_input", exit_code=2)

    try:
        (buffer_schedule if backend == "buffer" else postiz_schedule)(requests, key, args)
    except SystemExit:
        raise
    except Exception as exc:
        c.fail(f"Scheduling failed: {exc}", code="api_error")


if __name__ == "__main__":
    main()
