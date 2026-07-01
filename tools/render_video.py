#!/usr/bin/env python3
"""render_video — assemble a vertical video (hook ~3s + app demo) via Remotion.

The final-assembly step the skills describe (trim + concat + text + demo) done
programmatically instead of by hand in an editor. Takes a hook line (+ optional
hook background image/video) and an app-demo clip, renders a 9:16 MP4 with an
animated hook card cutting into the demo. Same JSON-envelope contract as the
other tools; wraps the Remotion project in tools/remotion/.

Usage:
  # dry-run: stage media + build props + print the render command (no render)
  python render_video.py --demo demo.mp4 --hook-text "your closet before vs after" \\
      --hook-media cover.png --brand myapp --out final.mp4 --dry-run

  # real render (first run auto-installs node deps unless --no-install)
  python render_video.py --demo demo.mp4 --hook-text "one blazer 5 fits" \\
      --hook-media cover.png --brand myapp --out final.mp4

Requires: Node.js + npx (Remotion). ffprobe (optional) auto-detects demo length.
"""

import argparse
import json
import os
import shutil
import subprocess

import _common as c

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTION_DIR = os.path.join(HERE, "remotion")
PUBLIC_DIR = os.path.join(REMOTION_DIR, "public")
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v"}


def ffprobe_seconds(path):
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
            capture_output=True, text=True, check=True)
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:
        return None


def stage(path, stem):
    """Copy a media file into public/ as <stem><ext>; return (filename, is_video)."""
    ext = os.path.splitext(path)[1].lower()
    for old in os.listdir(PUBLIC_DIR):
        if old.startswith(stem + "."):
            os.remove(os.path.join(PUBLIC_DIR, old))
    dest_name = f"{stem}{ext}"
    shutil.copy(path, os.path.join(PUBLIC_DIR, dest_name))
    return dest_name, ext in VIDEO_EXTS


def main():
    p = argparse.ArgumentParser(description="Assemble a hook+demo vertical video via Remotion.")
    p.add_argument("--demo", required=True, help="App-demo video clip.")
    p.add_argument("--hook-text", required=True)
    p.add_argument("--hook-media", help="Background image or video for the hook (optional).")
    p.add_argument("--out", required=True, help="Output MP4 path.")
    p.add_argument("--hook-seconds", type=float, default=3.0)
    p.add_argument("--demo-seconds", type=float, help="Override; else ffprobe the demo, else 8.")
    p.add_argument("--brand", default="")
    p.add_argument("--demo-caption", default="", help="Defaults to 'i used {brand}'.")
    p.add_argument("--accent", default="#111111")
    p.add_argument("--no-install", action="store_true", help="Skip auto npm install.")
    p.add_argument("--dry-run", action="store_true", help="Stage + build props, skip render.")
    args = p.parse_args()
    c.set_tool("render_video")

    if not os.path.exists(args.demo):
        c.fail(f"Demo not found: {args.demo}", code="not_found")
    if args.hook_media and not os.path.exists(args.hook_media):
        c.fail(f"Hook media not found: {args.hook_media}", code="not_found")
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    demo_name, _ = stage(args.demo, "demo")
    hook_name, hook_is_video = ("", False)
    if args.hook_media:
        hook_name, hook_is_video = stage(args.hook_media, "hook")

    demo_seconds = args.demo_seconds or ffprobe_seconds(args.demo) or 8.0
    props = {
        "hookText": args.hook_text,
        "hookSrc": hook_name,
        "hookIsVideo": hook_is_video,
        "demoSrc": demo_name,
        "demoCaption": args.demo_caption,
        "brand": args.brand,
        "accentColor": args.accent,
        "hookSeconds": args.hook_seconds,
        "demoSeconds": round(demo_seconds, 2),
    }
    props_path = os.path.join(REMOTION_DIR, "props.json")
    with open(props_path, "w") as fh:
        json.dump(props, fh, indent=2)

    out_abs = os.path.abspath(args.out)
    total = round(args.hook_seconds + demo_seconds, 2)
    cmd = ["npx", "remotion", "render", "src/index.ts", "HookDemo", out_abs,
           f"--props={props_path}"]

    if args.dry_run:
        c.emit({"dry_run": True, "props": props, "command": " ".join(cmd),
                "cwd": REMOTION_DIR, "total_seconds": total,
                "note": "No render performed. Re-run without --dry-run to render."})

    if not shutil.which("npx"):
        c.fail("Node.js / npx not found. Install Node 18+ to use Remotion.",
               code="missing_dependency", dependency="node")

    if not os.path.isdir(os.path.join(REMOTION_DIR, "node_modules")) and not args.no_install:
        c.log("Installing Remotion deps (first run, one-time)…")
        inst = subprocess.run(["npm", "install"], cwd=REMOTION_DIR,
                              capture_output=True, text=True)
        if inst.returncode != 0:
            c.fail(f"npm install failed: {inst.stderr[-500:]}", code="install_failed")

    c.log(f"Rendering {total}s video → {out_abs}")
    proc = subprocess.run(cmd, cwd=REMOTION_DIR, capture_output=True, text=True)
    if proc.returncode != 0 or not os.path.exists(out_abs):
        c.fail(f"Remotion render failed: {proc.stderr[-800:]}", code="render_failed",
               stdout_tail=proc.stdout[-300:])

    c.emit({"out": out_abs, "total_seconds": total, "hook_seconds": args.hook_seconds,
            "demo_seconds": round(demo_seconds, 2), "props": props})


if __name__ == "__main__":
    main()
