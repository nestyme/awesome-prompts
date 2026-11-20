#!/usr/bin/env python3
"""Build the reference images for one outfit, in the order the prompt will name them.

  python make_refs.py outfit.json --out refs/

outfit.json:
  {"key": "soft-grunge-1",
   "items": [{"image": "jacket.png" or "https://...", "kind": "outerwear", "desc": "black leather biker jacket"},
             {"image": "...", "kind": "top|dress|bottom|shoes|bag|accessory", "desc": "..."}]}

Writes, in this order:
  <out>/<key>_1.jpg ...  one garment per image on white: outerwear, top, dress, bottom, shoes, then the bag
  <out>/<key>_N.jpg      one board with all small accessories side by side (jewelry, hat, scarf, sunglasses, belt)
  <out>/<key>.json       manifest: absolute image paths in order plus what each shows, for the "(image k)" lines
Product cutouts on transparent PNGs work best; plain product photos on white work too.
One garment per image matters: with several garments in one image, or more than ~7 images, items blend.
"""
import argparse, hashlib, json, os, socket, urllib.request
from PIL import Image

socket.setdefaulttimeout(30)
ORDER = ["outerwear", "top", "dress", "bottom", "shoes", "bag"]


def local(src, cache):
    if not src.startswith("http"):
        return src
    p = os.path.join(cache, hashlib.md5(src.encode()).hexdigest() + os.path.splitext(src.split("?")[0])[1][:5])
    if not os.path.exists(p):
        tmp = f"{p}.{os.getpid()}.part"  # unique temp name: parallel runs may share the cache
        urllib.request.urlretrieve(src, tmp)
        os.replace(tmp, p)
    return p


def flat(src, dst, size=1024):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((size - 80, size - 80))
    bg = Image.new("RGB", (size, size), "white")
    bg.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    bg.save(dst, quality=92)


def board(srcs, dst, h=600):
    ims = []
    for s in srcs:
        im = Image.open(s).convert("RGBA")
        im.thumbnail((520, h - 80))
        ims.append(im)
    bg = Image.new("RGB", (sum(i.width for i in ims) + 80 * (len(ims) + 1), h), "white")
    x = 80
    for im in ims:
        bg.paste(im, (x, (h - im.height) // 2), im)
        x += im.width + 80
    bg.save(dst, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outfit")
    ap.add_argument("--out", default="refs")
    a = ap.parse_args()
    spec = json.load(open(a.outfit))
    out = os.path.abspath(a.out)
    cache = os.path.join(out, "_cache")
    os.makedirs(cache, exist_ok=True)
    items = spec["items"]
    bad = [i for i in items if i.get("kind") not in ORDER + ["accessory"]]
    if bad:
        raise SystemExit(f"unknown kind in {bad}; use one of {ORDER + ['accessory']}")
    big = sorted([i for i in items if i["kind"] != "accessory"], key=lambda i: ORDER.index(i["kind"]))
    small = [i for i in items if i["kind"] == "accessory"]
    images = []
    for i in big:
        dst = os.path.join(out, f"{spec['key']}_{len(images) + 1}.jpg")
        flat(local(i["image"], cache), dst)
        images.append({"path": dst, "items": [{"kind": i["kind"], "desc": i.get("desc", "")}]})
    if small:
        dst = os.path.join(out, f"{spec['key']}_{len(images) + 1}.jpg")
        board([local(i["image"], cache) for i in small], dst)
        images.append({"path": dst, "items": [{"kind": "accessory", "desc": i.get("desc", "")} for i in small]})
    json.dump({"key": spec["key"], "images": images}, open(os.path.join(out, f"{spec['key']}.json"), "w"), indent=1)
    for k, im in enumerate(images, 1):
        print(f"image {k}: " + " + ".join(f"{x['kind']}: {x['desc']}" for x in im["items"]))
    if len(images) > 7:
        print("WARNING: more than 7 reference images; items will blend. Drop the photo reference or merge accessories.")


if __name__ == "__main__":
    main()
