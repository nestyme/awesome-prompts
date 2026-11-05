#!/usr/bin/env python3
"""gen_image — generate or edit an image (text->image / image-edit).

The paid step behind viral-content-factory & carousel-conveyor. Two modes:
  - text->image : a fresh generation (the persona anchor / reference selfie).
  - image-edit  : feed reference image(s) + a prompt (every cover is a ONE-hop
                  edit of the locked reference — never edit an edit).

Two providers:
  - fal    (default when FAL_KEY is set) — Seedream v4 via fal.ai, ~$0.03/image
           (vs ~$0.13-0.15 for Gemini 3 Pro Image). `--model` takes a fal
           endpoint base (the tool appends /text-to-image or /edit by mode),
           e.g. fal-ai/bytedance/seedream/v4. FLUX Kontext etc. also work if
           you pass full endpoints via --model.
  - gemini — Gemini 3 Pro Image via GEMINI_API_KEY (the original path).

The realism/anti-artifact prompt blocks live in the skills; this tool just
executes the generation and saves the PNG. No text is baked in — captions are
composited later with caption_composite.py.

Usage:
  python gen_image.py --prompt "$(cat prompt.txt)" --out ref_mia.png
  python gen_image.py --prompt "change only the outfit ..." \\
      --ref ref_mia.png --out _cover_bank/mia_counter.png

Requires: fal-client + FAL_KEY, or google-genai + GEMINI_API_KEY.
"""

import argparse
import os

import _common as c

FAL_DEFAULT = "fal-ai/bytedance/seedream/v4"
GEMINI_DEFAULT = "gemini-3-pro-image-preview"


def run_fal(args):
    fal_client = c.require("fal_client", "fal-client")
    requests = c.require("requests")
    c.env_any(["FAL_KEY", "FAL_AI_API_KEY"], label="FAL_KEY")
    if os.environ.get("FAL_AI_API_KEY") and not os.environ.get("FAL_KEY"):
        os.environ["FAL_KEY"] = os.environ["FAL_AI_API_KEY"]

    model = args.model or FAL_DEFAULT
    if "/text-to-image" not in model and "/edit" not in model and model.count("/") <= 3:
        endpoint = model + ("/edit" if args.ref else "/text-to-image")
    else:
        endpoint = model
    arguments = {"prompt": args.prompt,
                 "image_size": {"width": args.width, "height": args.height}}
    if args.ref:
        arguments["image_urls"] = [fal_client.upload_file(r) for r in args.ref]

    last_err = None
    for attempt in range(1, args.retries + 1):
        try:
            result = fal_client.subscribe(endpoint, arguments=arguments)
            images = result.get("images") or []
            if not images:
                last_err = f"no image in response: {result}"
                continue
            r = requests.get(images[0]["url"], timeout=120)
            r.raise_for_status()
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "wb") as f:
                f.write(r.content)
            c.emit({"out": args.out, "provider": "fal", "endpoint": endpoint,
                    "mode": "edit" if args.ref else "generate", "refs": args.ref,
                    "seed": result.get("seed"), "attempt": attempt})
        except Exception as exc:
            last_err = str(exc)
            c.log(f"attempt {attempt} failed: {last_err}")
    c.fail(f"Generation failed after {args.retries} attempts: {last_err}",
           code="generation_failed")


def main():
    p = argparse.ArgumentParser(description="Generate/edit an image via fal (Seedream) or Gemini.")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True, help="Output PNG path.")
    p.add_argument("--ref", action="append", default=[], help="Reference image(s) for edit mode.")
    p.add_argument("--provider", choices=["auto", "fal", "gemini"], default="auto",
                   help="auto = fal if FAL_KEY is set, else gemini.")
    p.add_argument("--model", default=None,
                   help=f"Default: {FAL_DEFAULT} (fal) / {GEMINI_DEFAULT} (gemini).")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920, help="fal only; 1080x1920 = 9:16.")
    p.add_argument("--retries", type=int, default=3)
    args = p.parse_args()
    c.set_tool("gen_image")

    for ref in args.ref:
        if not os.path.exists(ref):
            c.fail(f"Reference not found: {ref}", code="not_found")

    provider = args.provider
    if provider == "auto":
        provider = "fal" if (os.environ.get("FAL_KEY") or os.environ.get("FAL_AI_API_KEY")) else "gemini"
    if provider == "fal":
        run_fal(args)
        return
    args.model = args.model or GEMINI_DEFAULT

    c.require("google.genai", "google-genai")
    c.require("PIL", "Pillow")
    api_key = c.env_any(["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
                        label="GEMINI_API_KEY")
    from google import genai
    from google.genai import types
    from PIL import Image
    import io

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
