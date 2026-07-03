#!/usr/bin/env python3
"""tiktok_account — pull an account's recent videos + stats (+ optional top comments).

trendwatch Step 4 collection. Tries TikTokApi (rich stats); on any failure falls
back to yt-dlp flat extraction so collection never hard-blocks. Output is the
shared account shape ({handle, follower_count, videos:[...]}) so it pipes into
account_stats.py and engagement.py.

Usage:
  python tiktok_account.py --handle someone --count 30
  python tiktok_account.py --handle someone --count 30 --comments 20

Requires one of: TikTokApi (pip install TikTokApi && playwright install) or
yt-dlp. TikTokApi gives saves/collect counts and comments; yt-dlp does not.
"""

import argparse

import _common as c


def via_tiktokapi(handle, count, n_comments):
    import asyncio
    from TikTokApi import TikTokApi

    async def run():
        async with TikTokApi() as api:
            await api.create_sessions(num_sessions=1, sleep_after=3)
            user = api.user(username=handle)
            info = await user.info()
            videos = []
            async for v in user.videos(count=count):
                d = v.as_dict
                nv = c.normalize_video(d)
                if n_comments:
                    try:
                        cmts = []
                        async for cm in v.comments(count=n_comments):
                            cd = cm.as_dict
                            cmts.append({"text": cd.get("text"),
                                         "likes": c.to_int(cd.get("digg_count"))})
                        nv["top_comments"] = cmts
                    except Exception as exc:
                        nv["top_comments_error"] = str(exc)
                videos.append(nv)
            stats = (info.get("stats") or info.get("statsV2") or {})
            follower = c.to_int(stats.get("followerCount"))
            bio = (info.get("user") or {}).get("signature")
            return {"handle": handle, "follower_count": follower, "bio": bio,
                    "videos": videos, "source": "TikTokApi"}

    return asyncio.run(run())


def via_ytdlp(handle, count):
    from yt_dlp import YoutubeDL
    url = f"https://www.tiktok.com/@{handle}"
    opts = {"quiet": True, "no_warnings": True, "skip_download": True,
            "extract_flat": False, "playlistend": count}
    videos = []
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        for entry in (info.get("entries") or [])[:count]:
            if not entry:
                continue
            videos.append(c.normalize_video({
                "id": entry.get("id"), "url": entry.get("webpage_url"),
                "caption": entry.get("title") or entry.get("description"),
                "view_count": entry.get("view_count"), "like_count": entry.get("like_count"),
                "comment_count": entry.get("comment_count"), "duration": entry.get("duration"),
                "upload_date": entry.get("upload_date") or entry.get("timestamp"),
            }))
        follower = c.to_int(info.get("channel_follower_count"))
    return {"handle": handle, "follower_count": follower, "videos": videos, "source": "yt-dlp"}


def main():
    p = argparse.ArgumentParser(description="Collect a TikTok account's videos + stats.")
    p.add_argument("--handle", required=True, help="Handle without the @.")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--comments", type=int, default=0, help="Top comments per video (TikTokApi only).")
    p.add_argument("--force-ytdlp", action="store_true", help="Skip TikTokApi.")
    args = p.parse_args()
    c.set_tool("tiktok_account")
    handle = args.handle.lstrip("@")

    tiktokapi_err = None
    if not args.force_ytdlp:
        try:
            __import__("TikTokApi")
            try:
                c.emit(via_tiktokapi(handle, args.count, args.comments))
            except Exception as exc:
                tiktokapi_err = str(exc)
                c.log(f"TikTokApi failed ({tiktokapi_err}); falling back to yt-dlp.")
        except ImportError:
            c.log("TikTokApi not installed; trying yt-dlp.")

    try:
        __import__("yt_dlp")
    except ImportError:
        c.fail("Neither TikTokApi nor yt-dlp is available.",
               code="missing_dependency", dependency="TikTokApi or yt-dlp",
               tiktokapi_error=tiktokapi_err)
    try:
        result = via_ytdlp(handle, args.count)
    except Exception as exc:
        c.fail(f"yt-dlp collection failed: {exc}", code="fetch_failed",
               tiktokapi_error=tiktokapi_err)
    if tiktokapi_err:
        result["tiktokapi_error"] = tiktokapi_err
    c.emit(result)


if __name__ == "__main__":
    main()
