#!/usr/bin/env python3
"""video_metadata — the universal collector. One URL -> normalized metadata + stats.

yt-dlp speaks TikTok, Instagram, YouTube/Shorts, and more, so this is the
always-works fallback in every skill when TikTokApi / instaloader break. Output
is normalized to the shared video schema, so it pipes straight into
engagement.py.

Usage:
  python video_metadata.py --url https://www.tiktok.com/@x/video/123
  python video_metadata.py --url-file urls.txt        # one URL per line -> list

Requires: yt-dlp (pip install yt-dlp).
"""

import argparse

import _common as c


def fetch(url, ydl):
    info = ydl.extract_info(url, download=False)
    v = c.normalize_video({
        "id": info.get("id"),
        "url": info.get("webpage_url") or url,
        "caption": info.get("title") or info.get("description"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "comment_count": info.get("comment_count"),
        "repost_count": info.get("repost_count"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date") or info.get("timestamp"),
    })
    v["uploader"] = info.get("uploader") or info.get("channel")
    v["handle"] = info.get("uploader_id")
    return v


def main():
    p = argparse.ArgumentParser(description="Fetch normalized video metadata via yt-dlp.")
    p.add_argument("--url", help="A single video URL.")
    p.add_argument("--url-file", help="File with one URL per line -> returns a list.")
    args = p.parse_args()
    c.set_tool("video_metadata")

    if not args.url and not args.url_file:
        c.fail("Pass --url or --url-file.", code="bad_input", exit_code=2)

    c.require("yt_dlp", "yt-dlp")
    from yt_dlp import YoutubeDL

    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": False}
    urls = [args.url] if args.url else [
        ln.strip() for ln in open(args.url_file) if ln.strip() and not ln.startswith("#")]

    results, errors = [], []
    with YoutubeDL(opts) as ydl:
        for u in urls:
            try:
                results.append(fetch(u, ydl))
            except Exception as exc:  # yt-dlp raises many subclasses
                errors.append({"url": u, "error": str(exc)})

    if not results and errors:
        c.fail("All URLs failed.", code="fetch_failed", errors=errors)

    c.emit(results[0] if (args.url and results) else {"videos": results, "errors": errors})


if __name__ == "__main__":
    main()
