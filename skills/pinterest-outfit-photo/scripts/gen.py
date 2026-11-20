#!/usr/bin/env python3
"""Generate N variants of one shot, or apply one edit, with a reference-capable image model on OpenRouter.

  python gen.py --manifest refs/<key>.json --prompt prompt.txt --out out/ [--n 2] [--pose-ref photo.jpg] [--aspect 3:4] [--tag r2]
  python gen.py --edit out/<key>_a.png [--ref refs/<key>_3.jpg] --prompt fix.txt --out out/      (one edit: fix a drifted item or erase text)

Reference order sent to the model: the manifest images (image 1..k), then --pose-ref LAST if given.
Outputs <out>/<key>_a.png, _b.png ... (with --tag r2: <key>_r2a.png ..., so a regeneration round never overwrites round 1).
Edits write <out>/<name>_fix.png. Every call appends {"out", "cost"} to <out>/_costs.jsonl.

Model: $IMAGE_MODEL or google/gemini-3.1-flash-image (Nano Banana 2, about $0.07 per image at 3:4).
Key: $OPENROUTER_API_KEY. Failed attempts are retried up to 3 times, and each billed attempt is logged.
"""
import argparse, base64, json, os, string, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

MODEL = os.environ.get("IMAGE_MODEL", "google/gemini-3.1-flash-image")


def call(prompt, refs, out, aspect):
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("set OPENROUTER_API_KEY")
    content = [{"type": "text", "text": prompt}]
    for r in refs:
        mime = "jpeg" if r.lower().endswith((".jpg", ".jpeg")) else "png"
        content.append({"type": "image_url", "image_url": {"url": f"data:image/{mime};base64," + base64.b64encode(open(r, "rb").read()).decode()}})
    body = {"model": MODEL, "messages": [{"role": "user", "content": content}], "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": aspect}, "usage": {"include": True}}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last = ""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                res = json.loads(resp.read())
            with open(os.path.join(os.path.dirname(out), "_costs.jsonl"), "a") as f:
                f.write(json.dumps({"out": os.path.basename(out), "cost": (res.get("usage") or {}).get("cost"),
                                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
            msg = res["choices"][0]["message"]
            imgs = msg.get("images") or []
            if not imgs:
                last = "no image: " + (msg.get("content") or "")[:120]
                continue
            url = imgs[0]["image_url"]["url"]
            data = base64.b64decode(url.split(",", 1)[1]) if url.startswith("data:") else urllib.request.urlopen(url).read()
            open(out, "wb").write(data)
            return out
        except Exception as e:  # network / 5xx: retry
            last = f"{type(e).__name__}: {e}"
            time.sleep(5 * (attempt + 1))
    return f"FAILED {out}: {last}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--edit", help="image to edit; sent first")
    ap.add_argument("--ref", action="append", default=[], help="with --edit: extra reference images, after the edited one")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--pose-ref", help="a real photo for framing and photo quality; sent LAST")
    ap.add_argument("--aspect", default="3:4")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    prompt = open(a.prompt).read()
    if a.edit:
        name = os.path.splitext(os.path.basename(a.edit))[0]
        print(call(prompt, [a.edit] + a.ref, os.path.join(os.path.abspath(a.out), f"{name}_fix.png"), a.aspect))
        return
    if not a.manifest:
        sys.exit("--manifest is required unless --edit is given")
    m = json.load(open(a.manifest))
    refs = [im["path"] for im in m["images"]] + ([a.pose_ref] if a.pose_ref else [])
    outs = [os.path.join(os.path.abspath(a.out), f"{m['key']}_{a.tag}{v}.png") for v in string.ascii_lowercase[:a.n]]
    with ThreadPoolExecutor(a.n) as ex:
        for res in ex.map(lambda o: call(prompt, refs, o, a.aspect), outs):
            print(res)


if __name__ == "__main__":
    main()
