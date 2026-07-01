#!/usr/bin/env python3
"""gen_image — generate or edit an image via Gemini (text->image / image-edit).

The paid step behind viral-content-factory & carousel-conveyor. Two modes:
  - text->image : a fresh generation (the persona anchor / reference selfie).
  - image-edit  : feed reference image(s) + a prompt (every cover is a ONE-hop
                  edit of the locked reference — never edit an edit).

The realism/anti-artifact prompt blocks live in the skills; this tool just
executes the generation and saves the PNG. No text is baked in — captions are
composited later with caption_composite.py.

Usage:
  python gen_image.py --prompt "$(cat prompt.txt)" --out ref_mia.png
  python gen_image.py --prompt "change only the outfit ..." \\
      --ref ref_mia.png --out _cover_bank/mia_counter.png

Requires: google-genai (pip install google-genai) + env GEMINI_API_KEY.
"""

import argparse
import os

import _common as c


def main():
    p = argparse.ArgumentParser(description="Generate/edit an image via Gemini.")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True, help="Output PNG path.")
    p.add_argument("--ref", action="append", default=[], help="Reference image(s) for edit mode.")
    p.add_argument("--model", default="gemini-3-pro-image-preview")
    p.add_argument("--retries", type=int, default=3)
    args = p.parse_args()
    c.set_tool("gen_image")

    c.require("google.genai", "google-genai")
    c.require("PIL", "Pillow")
    api_key = c.env_any(["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
                        label="GEMINI_API_KEY")
    from google import genai
    from google.genai import types
    from PIL import Image
    import io

    for ref in args.ref:
        if not os.path.exists(ref):
            c.fail(f"Reference not found: {ref}", code="not_found")

    client = genai.Client(api_key=api_key)
    parts = [args.prompt] + [Image.open(r) for r in args.ref]

    last_err = None
    for attempt in range(1, args.retries + 1):
        try:
            resp = client.models.generate_content(model=args.model, contents=parts)
            img_bytes = None
            for cand in resp.candidates or []:
                for part in cand.content.parts or []:
                    if getattr(part, "inline_data", None) and part.inline_data.data:
                        img_bytes = part.inline_data.data
                        break
                if img_bytes:
                    break
            if not img_bytes:
                last_err = "no image in response"
                continue
            img = Image.open(io.BytesIO(img_bytes))
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            img.save(args.out)
            c.emit({"out": args.out, "size": list(img.size), "mode": "edit" if args.ref else "generate",
                    "refs": args.ref, "model": args.model, "attempt": attempt})
        except Exception as exc:
            last_err = str(exc)
            c.log(f"attempt {attempt} failed: {last_err}")

    c.fail(f"Generation failed after {args.retries} attempts: {last_err}",
           code="generation_failed")


if __name__ == "__main__":
    main()
