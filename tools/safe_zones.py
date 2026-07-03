#!/usr/bin/env python3
"""safe_zones — audit a creative against platform safe zones & thumbnail readability.

Bakes prompts/meta-ads-safe-zones.md into a checkable tool. Verifies that no
critical content sits in the top/bottom 10% UI bands, that a 1:1 -> 4:5 crop
keeps the subject, and that the creative is still readable as a 300x300
thumbnail. Pure compute (PIL), no network.

Usage:
  python safe_zones.py --image ad.png
  python safe_zones.py --image ad.png --text-boxes boxes.json   # optional overlay regions

--text-boxes is a JSON list of [x,y,w,h] in pixels for text/logo regions you
placed; the tool reports which ones intrude into a UI band.
"""

import argparse
import json
import os

import _common as c

TOP_BAND = 0.10
BOT_BAND = 0.10
SIDE_BAND = 0.085


def contrast_ratio(img):
    """Rough thumbnail legibility proxy: stdev of luminance after 300x300 downscale."""
    from PIL import Image
    small = img.convert("L").resize((300, 300), Image.LANCZOS)
    px = list(small.tobytes())
    n = len(px)
    mean = sum(px) / n
    var = sum((p - mean) ** 2 for p in px) / n
    return round(var ** 0.5, 1)


def main():
    p = argparse.ArgumentParser(description="Audit a creative against platform safe zones.")
    p.add_argument("--image", required=True)
    p.add_argument("--text-boxes", help="JSON file with [[x,y,w,h],...] overlay regions.")
    p.add_argument("--target-ratio", default="4:5", help="Crop-survival target, e.g. 4:5.")
    args = p.parse_args()
    c.set_tool("safe_zones")

    c.require("PIL", "Pillow")
    from PIL import Image

    if not os.path.exists(args.image):
        c.fail(f"Image not found: {args.image}", code="not_found", exit_code=1)

    img = Image.open(args.image).convert("RGB")
    W, H = img.size
    top = int(H * TOP_BAND)
    bot = int(H * (1 - BOT_BAND))
    side = int(W * SIDE_BAND)

    findings = []

    boxes = []
    if args.text_boxes:
        with open(args.text_boxes) as fh:
            boxes = json.load(fh)
        for i, (x, y, w, h) in enumerate(boxes):
            intrusions = []
            if y < top:
                intrusions.append("top_10pct_ui_band")
            if y + h > bot:
                intrusions.append("bottom_10pct_ui_band")
            if x < side or x + w > W - side:
                intrusions.append("side_safe_margin")
            if intrusions:
                findings.append({"box": i, "rect": [x, y, w, h], "intrudes": intrusions})

    # 1:1 -> target crop survival: center-crop to target ratio, report retained area.
    tw, th = (int(n) for n in args.target_ratio.split(":"))
    target_ar = tw / th
    src_ar = W / H
    if src_ar > target_ar:
        keep_w = int(H * target_ar)
        retained = keep_w / W
        crop_note = f"vertical target crops {round((1-retained)*100)}% off the sides"
    else:
        keep_h = int(W / target_ar)
        retained = keep_h / H
        crop_note = f"target crop keeps full width; {round((1-retained)*100)}% off top/bottom"

    legibility = contrast_ratio(img)
    thumb_verdict = ("readable" if legibility >= 45 else
                     "low_contrast_may_be_muddy" if legibility >= 25 else
                     "likely_unreadable_at_thumbnail")

    c.emit({
        "image": args.image,
        "size": [W, H],
        "aspect_ratio": round(src_ar, 3),
        "safe_zone_px": {"top": top, "bottom": H - bot, "side": side},
        "overlay_findings": findings,
        "overlay_ok": not findings,
        "crop_survival": {
            "target_ratio": args.target_ratio,
            "retained_fraction": round(retained, 3),
            "note": crop_note,
            "ok": retained >= 0.8,
        },
        "thumbnail_readability": {
            "luminance_stdev": legibility,
            "verdict": thumb_verdict,
        },
        "pass": not findings and retained >= 0.8 and legibility >= 25,
    })


if __name__ == "__main__":
    main()
