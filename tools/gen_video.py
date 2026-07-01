#!/usr/bin/env python3
"""gen_video — animate a still frame into a clip via Kling (fal.ai) image-to-video.

viral-content-factory Phase 3 step 2. Takes a generated frame (e.g. a mannequin
outfit frame) and returns a short video clip URL, optionally downloading it.
Trimming/concatenation stays in the skill's ffmpeg recipe — this tool just does
the model call so it can be scripted per frame.

Usage:
  python gen_video.py --image frame_01.png --prompt "faceless morph-suit figure ..." \\
      --duration 5 --aspect 9:16 --out clip_01.mp4

Requires: fal-client (pip install fal-client) + env FAL_KEY.
"""

import argparse
import os

import _common as c


def main():
    p = argparse.ArgumentParser(description="Image-to-video via Kling on fal.ai.")
    p.add_argument("--image", required=True, help="Source frame.")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", help="If set, download the mp4 here; else just return URL.")
    p.add_argument("--duration", default="5", choices=["5", "10"])
    p.add_argument("--aspect", default="9:16")
    p.add_argument("--model", default="fal-ai/kling-video/v2/master/image-to-video")
    args = p.parse_args()
    c.set_tool("gen_video")

    fal_client = c.require("fal_client", "fal-client")
    import os
    os.environ["FAL_KEY"] = c.env_any(["FAL_KEY", "FAL_AI_API_KEY"], label="FAL_KEY")
    if not os.path.exists(args.image):
        c.fail(f"Image not found: {args.image}", code="not_found")

    try:
        image_url = fal_client.upload_file(args.image)
        result = fal_client.subscribe(
            args.model,
            arguments={"prompt": args.prompt, "image_url": image_url,
                       "duration": args.duration, "aspect_ratio": args.aspect},
            with_logs=True,
        )
        video_url = result["video"]["url"]
    except Exception as exc:
        c.fail(f"Video generation failed: {exc}", code="generation_failed")

    out_path = None
    if args.out:
        requests = c.require("requests")
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        r = requests.get(video_url, timeout=120)
        r.raise_for_status()
        with open(args.out, "wb") as fh:
            fh.write(r.content)
        out_path = args.out

    c.emit({"video_url": video_url, "out": out_path, "duration": args.duration,
            "aspect": args.aspect, "model": args.model})


if __name__ == "__main__":
    main()
