"""Side-by-side QA sheet: generated variants next to the outfit's reference cutouts.

  qa_sheet.py --manifest refs/<key>.json --images out/<key>_a.png out/<key>_b.png --out qa_<key>.jpg
Open the sheet and compare every garment: colour, length, shape, count, hardware, print. For small details (bag flaps,
heel shape, chains) crop the generated image around the item with PIL and open the crop next to the reference.
"""
import argparse, json
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--images", nargs="+", required=True)
ap.add_argument("--out", required=True); a = ap.parse_args()
H = 1400; shots = []
for p in a.images:
    im = Image.open(p).convert("RGB"); im.thumbnail((2000, H)); shots.append(im)
refs = [Image.open(i["path"]).convert("RGB") for i in json.load(open(a.manifest))["images"]]
CW = 480; cell = H // max(len(refs), 1); col = Image.new("RGB", (CW, H), "white"); y = 0
for r in refs:
    r = r.copy(); r.thumbnail((CW, cell - 4)); col.paste(r, ((CW - r.width) // 2, y)); y += cell
W = sum(s.width + 10 for s in shots) + CW + 10; out = Image.new("RGB", (W, H), "white"); x = 0
for s in shots: out.paste(s, (x, 0)); x += s.width + 10
out.paste(col, (x, 0)); out.save(a.out, quality=88); print(a.out)
