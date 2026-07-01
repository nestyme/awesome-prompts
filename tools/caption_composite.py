#!/usr/bin/env python3
"""caption_composite — composite caption text over a photo with platform-safe margins.

The carousel-conveyor "text is free" step: never regenerate a photo to change
words. Text is drawn deterministically in PIL so it is always correctly spelled,
inside the safe zone, and re-renderable at $0.

Enforces: left/right safe margin = 8.5% of width, top band = 10%, bottom band =
10% (platform UI covers those), font auto-fit so text never overflows.

Usage:
  python caption_composite.py --image cover.png --out slide_01.png \\
      --text "you don't need more clothes" --position lower --box

Emits the output path + the final geometry used.
"""

import argparse
import os

import _common as c

SAFE_X = 0.085   # left/right safe margin
TOP_BAND = 0.10  # platform UI (top)
BOT_BAND = 0.10  # platform UI (bottom)


def find_font(size, font_path=None):
    from PIL import ImageFont
    candidates = [font_path] if font_path else []
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    p = argparse.ArgumentParser(description="Composite caption text onto a photo (PIL).")
    p.add_argument("--image", required=True, help="Source cover photo.")
    p.add_argument("--out", required=True, help="Output PNG path.")
    p.add_argument("--text", required=True, help="Caption text (kept verbatim).")
    p.add_argument("--position", choices=["upper", "center", "lower"], default="lower")
    p.add_argument("--font", help="Path to a .ttf/.ttc font.")
    p.add_argument("--font-size", type=int, help="Max font size; auto-fits down.")
    p.add_argument("--color", default="#FFFFFF")
    p.add_argument("--box", action="store_true", help="Draw a translucent panel behind text.")
    p.add_argument("--box-color", default="#000000")
    p.add_argument("--box-opacity", type=int, default=110, help="0-255.")
    args = p.parse_args()
    c.set_tool("caption_composite")

    c.require("PIL", "Pillow")
    from PIL import Image, ImageDraw

    if not os.path.exists(args.image):
        c.fail(f"Image not found: {args.image}", code="not_found", exit_code=1)

    img = Image.open(args.image).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    safe_x = int(W * SAFE_X)
    max_text_w = W - 2 * safe_x
    top_limit = int(H * TOP_BAND)
    bot_limit = int(H * (1 - BOT_BAND))
    usable_h = bot_limit - top_limit

    # Auto-fit: shrink until wrapped text fits width AND the usable band.
    size = args.font_size or int(W * 0.075)
    while size >= 12:
        font = find_font(size, args.font)
        lines = wrap(draw, args.text, font, max_text_w)
        line_h = int(size * 1.25)
        block_h = line_h * len(lines)
        widest = max((draw.textlength(ln, font=font) for ln in lines), default=0)
        if block_h <= usable_h and widest <= max_text_w:
            break
        size -= 2
    else:
        font = find_font(12, args.font)
        lines = wrap(draw, args.text, font, max_text_w)
        line_h = int(12 * 1.25)
        block_h = line_h * len(lines)

    if args.position == "upper":
        y0 = top_limit + int(usable_h * 0.05)
    elif args.position == "center":
        y0 = top_limit + (usable_h - block_h) // 2
    else:
        y0 = bot_limit - block_h - int(usable_h * 0.05)

    if args.box:
        pad = int(size * 0.4)
        box_rgb = tuple(int(args.box_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        draw.rounded_rectangle(
            [safe_x - pad, y0 - pad, W - safe_x + pad, y0 + block_h + pad],
            radius=pad, fill=box_rgb + (max(0, min(255, args.box_opacity)),))

    color = tuple(int(args.color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    y = y0
    for ln in lines:
        lw = draw.textlength(ln, font=font)
        x = (W - lw) / 2
        # subtle shadow for readability
        draw.text((x + 2, y + 2), ln, font=font, fill=(0, 0, 0, 140))
        draw.text((x, y), ln, font=font, fill=color)
        y += line_h

    out = Image.alpha_composite(img, overlay).convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out.save(args.out)

    c.emit({
        "out": args.out, "size": [W, H], "font_size": size, "lines": lines,
        "safe_margins": {"x_px": safe_x, "top_px": top_limit, "bottom_px": H - bot_limit},
        "position": args.position,
    })


if __name__ == "__main__":
    main()
