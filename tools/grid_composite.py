#!/usr/bin/env python3
"""grid_composite — tile N images into one clean slide (e.g. 4 app screens, 2x2).

For app-screen showcase slides that need no photo background: rounded-corner
tiles on a flat colour, platform-safe outer margins. Pair with
caption_composite.py for the headline/save-bait text.

Usage:
  python grid_composite.py --image s1.png --image s2.png --image s3.png \\
      --image s4.png --out grid.png --cols 2 --bg "#F5F0E8"

Emits the output path + geometry.
"""

import argparse
import os

import _common as c


def main():
    p = argparse.ArgumentParser(description="Tile images into one slide (PIL).")
    p.add_argument("--image", action="append", required=True, help="Tile images, in order.")
    p.add_argument("--out", required=True)
    p.add_argument("--cols", type=int, default=2)
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--bg", default="#F5F0E8")
    p.add_argument("--gap", type=int, default=28, help="Gap between tiles (px).")
    p.add_argument("--margin-x", type=float, default=0.085, help="Outer margin, fraction of width.")
    p.add_argument("--margin-top", type=float, default=0.16, help="Top band left for headline.")
    p.add_argument("--margin-bottom", type=float, default=0.14, help="Bottom band left for text.")
    p.add_argument("--radius", type=int, default=36, help="Tile corner radius.")
    args = p.parse_args()
    c.set_tool("grid_composite")

    c.require("PIL", "Pillow")
    from PIL import Image, ImageDraw

    for i in args.image:
        if not os.path.exists(i):
            c.fail(f"Image not found: {i}", code="not_found")

    W, H = args.width, args.height
    canvas = Image.new("RGB", (W, H), args.bg)
    n = len(args.image)
    cols = args.cols
    rows = (n + cols - 1) // cols

    x0 = int(W * args.margin_x)
    y0 = int(H * args.margin_top)
    x1 = W - x0
    y1 = H - int(H * args.margin_bottom)
    tile_w = (x1 - x0 - args.gap * (cols - 1)) // cols
    tile_h = (y1 - y0 - args.gap * (rows - 1)) // rows

    for idx, path in enumerate(args.image):
        img = Image.open(path).convert("RGB")
        scale = min(tile_w / img.width, tile_h / img.height)
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width, img.height],
                                               radius=args.radius, fill=255)
        r, col = divmod(idx, cols)
        cx = x0 + col * (tile_w + args.gap) + (tile_w - img.width) // 2
        cy = y0 + r * (tile_h + args.gap) + (tile_h - img.height) // 2
        canvas.paste(img, (cx, cy), mask)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out)
    c.emit({"out": args.out, "tiles": n, "grid": f"{rows}x{cols}",
            "tile_size": [tile_w, tile_h]})


if __name__ == "__main__":
    main()
