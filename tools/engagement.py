#!/usr/bin/env python3
"""engagement — compute engagement analytics for one or many videos.

The trendwatch flagship: turn raw video stats into the derived metrics the
skill reasons about (engagement_score, save_rate, engagement_ratio,
vs_account_median), tag freshness/lifecycle by age, and classify each video as
format- / creator- / paid-amp-attributable so ideation only mines the
transferable bucket.

Pure compute — no network, no keys. Feed it whatever a collector returned.

Usage:
  # single video
  python engagement.py --in video.json --follower-count 42000 --account-median 8000

  # batch (list of videos) piped from a collector, ranked by score*recency
  python tiktok_account.py --handle someone | python engagement.py --in - \\
      --follower-count 42000 --account-median 8000

Input JSON: a single video object, a list of video objects, or an object with a
"videos" list. Field aliases (TikTokApi/yt-dlp/instaloader) are auto-normalized.
"""

import argparse

import _common as c


def score(v: dict) -> dict:
    """Derive metrics for one normalized video. Fields may be None if unknown."""
    views = v.get("views")
    likes = v.get("likes") or 0
    comments = v.get("comments") or 0
    shares = v.get("shares") or 0
    saves = v.get("saves")

    out = dict(v)

    # engagement_score = (likes + 2*comments + 3*saves + 5*shares) / views
    if views:
        weighted = likes + 2 * comments + 3 * (saves or 0) + 5 * shares
        out["engagement_score"] = round(weighted / views, 5)
        out["like_rate"] = round(likes / views, 5)
        out["comment_rate"] = round(comments / views, 5)
        out["share_rate"] = round(shares / views, 5)
        # save_rate only meaningful when saves are actually present
        out["save_rate"] = round(saves / views, 5) if saves is not None else None
    else:
        out["engagement_score"] = None
        out["save_rate"] = None

    # save-rate verdict (utility/tool products): >5% strong / 2-5% mid / <1% none
    sr = out.get("save_rate")
    if sr is None:
        out["save_verdict"] = "unknown"
    elif sr >= 0.05:
        out["save_verdict"] = "strong_conversion"
    elif sr >= 0.02:
        out["save_verdict"] = "mid_tweak_cta"
    elif sr >= 0.01:
        out["save_verdict"] = "weak"
    else:
        out["save_verdict"] = "no_conversion"

    return out


def add_age(v: dict, now) -> dict:
    """Add age_days, freshness bucket, and recency_weight."""
    created = c.parse_created(v.get("created"))
    if not created:
        v["age_days"] = None
        v["freshness"] = "unknown"
        v["recency_weight"] = 0.5
        return v
    if not created.tzinfo:
        from datetime import timezone
        created = created.replace(tzinfo=timezone.utc)
    age = max(0, (now - created).days)
    v["age_days"] = age
    if age < 14:
        v["freshness"] = "rising"
    elif age < 30:
        v["freshness"] = "peak"
    elif age < 60:
        v["freshness"] = "declining"
    else:
        v["freshness"] = "evergreen-structure-only"
    v["recency_weight"] = round(max(0.1, 1 - age / 60), 3)
    return v


def add_attribution(v: dict, follower_count, account_median, paid_signals) -> dict:
    """engagement_ratio, vs_account_median, and the attribution bucket."""
    views = v.get("views")

    if follower_count and views:
        v["engagement_ratio"] = round(views / follower_count, 4)
    else:
        v["engagement_ratio"] = None

    if account_median and views:
        v["vs_account_median"] = round(views / account_median, 3)
    else:
        v["vs_account_median"] = None

    # Attribution: does the FORMAT carry the video, or the creator / paid amp?
    er = v.get("engagement_ratio")
    vm = v.get("vs_account_median")
    bucket = "unknown"
    if paid_signals:
        bucket = "paid-amp-suspected"
    elif vm is not None:
        bucket = "format-attributable" if vm >= 2 else (
            "creator-attributable" if vm <= 1.2 else "mixed")
    elif er is not None:
        # engagement_ratio baseline: >0.5x format added value, <0.1x creator carried
        bucket = "format-attributable" if er >= 0.5 else (
            "creator-attributable" if er < 0.1 else "mixed")
    v["attribution"] = bucket
    v["ideation_eligible"] = bucket in ("format-attributable", "mixed")
    return v


def main():
    p = argparse.ArgumentParser(description="Compute engagement analytics for videos.")
    p.add_argument("--in", dest="infile", help="JSON file, '-' for stdin, or pipe.")
    p.add_argument("--follower-count", type=int, help="Account follower count (for engagement_ratio).")
    p.add_argument("--account-median", type=int, help="Account median views (for vs_account_median).")
    p.add_argument("--paid-amp", action="store_true",
                   help="Flag these videos as paid-amp-suspected (from #ad/Promote/etc).")
    p.add_argument("--now", help="Override 'now' as ISO date for reproducible age calc.")
    p.add_argument("--top", type=int, help="Return only top N ranked by score*recency_weight.")
    args = p.parse_args()
    c.set_tool("engagement")

    payload = c.load_input(args.infile)
    if payload is None:
        c.fail("No input. Pass --in <file> or pipe JSON on stdin.", code="bad_input", exit_code=2)

    if isinstance(payload, dict) and isinstance(payload.get("videos"), list):
        follower_count = args.follower_count or c.to_int(payload.get("follower_count"))
        account_median = args.account_median or c.to_int(payload.get("account_median_views"))
        videos = payload["videos"]
    elif isinstance(payload, list):
        follower_count, account_median = args.follower_count, args.account_median
        videos = payload
    else:
        follower_count, account_median = args.follower_count, args.account_median
        videos = [payload]

    now = c.now_utc(args.now)
    scored = []
    for raw in videos:
        v = c.normalize_video(raw) if isinstance(raw, dict) else {}
        v = score(v)
        v = add_age(v, now)
        v = add_attribution(v, follower_count, account_median, args.paid_amp)
        # carry through handle/author if present
        for k in ("handle", "author", "authorName"):
            if isinstance(raw, dict) and raw.get(k):
                v[k] = raw[k]
        v["rank_score"] = round((v.get("engagement_score") or 0) * v.get("recency_weight", 0.5), 6)
        scored.append(v)

    scored.sort(key=lambda x: x["rank_score"], reverse=True)
    if args.top:
        scored = scored[: args.top]

    single = len(scored) == 1 and not isinstance(payload, list) and not (
        isinstance(payload, dict) and "videos" in payload)

    fmt_count = sum(1 for v in scored if v.get("attribution") == "format-attributable")
    summary = {
        "n_videos": len(scored),
        "follower_count": follower_count,
        "account_median_views": account_median,
        "format_attributable": fmt_count,
        "creator_attributable": sum(1 for v in scored if v.get("attribution") == "creator-attributable"),
        "paid_amp_suspected": sum(1 for v in scored if v.get("attribution") == "paid-amp-suspected"),
        "fresh_or_peak": sum(1 for v in scored if v.get("freshness") in ("rising", "peak")),
    }

    c.emit(scored[0] if single else {"summary": summary, "videos": scored})


if __name__ == "__main__":
    main()
