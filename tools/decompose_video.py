#!/usr/bin/env python3
"""decompose_video — download a video and extract the raw material for 7-axis analysis.

trendwatch Step 5 helper. Pulls keyframes (via ffmpeg), isolates the
thumb-stop frame (first ~1.5s), and optionally transcribes the audio (Whisper)
so the agent can reason about thumb-stop vs hook separately. Emits file paths +
the transcript; the agent does the actual axis interpretation.

Usage:
  python decompose_video.py --url https://tiktok.com/@x/video/123 --out ./frames
  python decompose_video.py --file local.mp4 --out ./frames --transcribe

Requires: ffmpeg on PATH; yt-dlp (for --url); openai-whisper (for --transcribe).
"""

import argparse
import glob
import os
import shutil
import subprocess

import _common as c


def run_ffmpeg(cmd, what):
    """Run an ffmpeg command, failing with a clean envelope (never a traceback)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:  # ffmpeg present on PATH but not spawnable
        c.fail(f"ffmpeg {what} could not run: {exc}", code="ffmpeg_failed")
    if proc.returncode != 0:
        c.fail(f"ffmpeg {what} failed: {(proc.stderr or '').strip()[-500:]}",
               code="ffmpeg_failed")


def download(url, workdir):
    from yt_dlp import YoutubeDL
    target = os.path.join(workdir, "source.%(ext)s")
    with YoutubeDL({"quiet": True, "no_warnings": True, "outtmpl": target,
                    "format": "mp4/best"}) as ydl:
        ydl.download([url])
    files = glob.glob(os.path.join(workdir, "source.*"))
    if not files:
        c.fail("Download produced no file.", code="fetch_failed")
    return files[0]


def main():
    p = argparse.ArgumentParser(description="Extract frames + transcript for video analysis.")
    p.add_argument("--url", help="Video URL (downloaded via yt-dlp).")
    p.add_argument("--file", help="Local video file.")
    p.add_argument("--out", default="./frames", help="Output directory.")
    p.add_argument("--fps", type=float, default=0.5, help="Keyframes per second (default 1 / 2s).")
    p.add_argument("--thumbstop-sec", type=float, default=1.5, help="Thumb-stop window length.")
    p.add_argument("--transcribe", action="store_true", help="Transcribe audio (Whisper).")
    p.add_argument("--whisper-model", default="base")
    args = p.parse_args()
    c.set_tool("decompose_video")

    if not args.url and not args.file:
        c.fail("Pass --url or --file.", code="bad_input", exit_code=2)
    if not shutil.which("ffmpeg"):
        c.fail("ffmpeg not found on PATH.", code="missing_dependency", dependency="ffmpeg")

    os.makedirs(args.out, exist_ok=True)

    if args.url:
        c.require("yt_dlp", "yt-dlp")
        src = download(args.url, args.out)
    else:
        if not os.path.exists(args.file):
            c.fail(f"File not found: {args.file}", code="not_found")
        src = args.file

    # keyframes across the whole clip
    frame_tmpl = os.path.join(args.out, "frame_%03d.jpg")
    run_ffmpeg(["ffmpeg", "-y", "-i", src, "-vf", f"fps={args.fps}", frame_tmpl],
               "keyframe extraction")
    frames = sorted(glob.glob(os.path.join(args.out, "frame_*.jpg")))

    # dedicated thumb-stop frame at the midpoint of the first window
    thumb = os.path.join(args.out, "thumbstop.jpg")
    run_ffmpeg(["ffmpeg", "-y", "-ss", str(args.thumbstop_sec / 2), "-i", src,
                "-frames:v", "1", thumb], "thumb-stop frame")

    transcript = None
    if args.transcribe:
        whisper = c.require("whisper", "openai-whisper")
        model = whisper.load_model(args.whisper_model)
        res = model.transcribe(src)
        transcript = {
            "text": res.get("text", "").strip(),
            "segments": [{"start": round(s["start"], 2), "end": round(s["end"], 2),
                          "text": s["text"].strip()} for s in res.get("segments", [])],
        }

    c.emit({
        "source": src,
        "thumbstop_frame": thumb,
        "keyframes": frames,
        "n_keyframes": len(frames),
        "transcript": transcript,
        "hint": "Read thumbstop.jpg for the 0-1.5s thumb-stop axis; read keyframes + "
                "transcript for hook/format/message. Sound & comments come from the collector.",
    })


if __name__ == "__main__":
    main()
