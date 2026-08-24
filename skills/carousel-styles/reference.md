# PIL primitives — the shared parts every system reuses

Generic, brand-free. `W, H = 1080, 1920` for TikTok/IG slides; crop the top
1000×1500 for a Pinterest pin. All colours are placeholders — swap for yours.

## Polaroid (photo on a white card, tilted, soft shadow)
```python
def polaroid(img, w, angle, border=18):
    ph = int(w * img.height / img.width)
    card = Image.new("RGB", (w + 2*border, ph + 2*border), (252, 251, 248))
    card.paste(img.resize((w, ph), Image.LANCZOS), (border, border))
    card = card.convert("RGBA").rotate(angle, expand=True, resample=Image.BICUBIC)
    a = card.split()[3].point(lambda v: min(v, 90))          # shadow from silhouette
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(a)
    out = Image.new("RGBA", (card.width + 30, card.height + 34), (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (18, 22))
    out.alpha_composite(card, (0, 0))
    return out
```

## Torn paper sheet (notebook system)
Organic edge = a random-walk level with rare deep tears — NOT uniform teeth
(that reads as a postage stamp), plus a white fibre rim:
```python
def edge_walk(rnd, length, depth=34):
    pts, x, level = [], 0, rnd.uniform(4, depth*0.4)
    while x < length:
        level = max(2, min(depth, level + rnd.uniform(-6, 6)))
        if rnd.random() < 0.06: level = rnd.uniform(depth*0.6, depth)  # deep tear
        pts.append((x, level)); x += rnd.randint(6, 16)
    return pts
# build a polygon from 4 walked edges -> putalpha; MinFilter(9) the mask and
# paste white at 90% into (mask - eroded) for the fibre rim; grid = 44px lines
# in (188,197,214) on warm white (248,247,242); rotate 0.7-1.2°, blur-shadow.
```

## Statement slide
```python
def statement(photo, lines, color=(186,242,214), dark=0.26):
    base = cover_fit(photo, W, H).convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 10, int(255*dark))))
    size = 150
    while max(measure(ln, size) for ln in lines) > W - 120 and size > 84: size -= 6
    # centred block, per-line: dark offset shadow (+4,+4, alpha 110), then colour
```

## Hand-circled label with cursor (notebook / doll systems)
Handwriting font, two offset ellipses (o and o+3px) = "drawn twice" wobble,
plus a tiny mouse-cursor polygon at the ellipse's 4-o'clock.

## Rounded chip / crossed-ink chips
`rounded_rectangle(radius=height/2)`; for a colour-pair, fill chip A with
colour A and ink it with colour B, and vice versa — the chips ARE the palette.
Always pick the DARKER of a pair for any chip that carries light text.

## Fake-UI cards (tweet / iMessage)
The believability is alignment, not detail. iMessage: reaction pill touches
the bubble's TOP edge; long-press menu sits UNDER the bubble at the SAME left
edge. Tweet: avatar + bold name + blue tick, take in 3-4 short bold lines,
muted meta line, hairline divider, counts row ("saves" included — that's the
metric the genre brags about), and a separate small reply-card that carries
your CTA as if a commenter asked "ok but how".

## Photo-to-text matching
```python
score = 2*len(colour_words(line) & tags(photo)) + len(garment_words(line) & tags(photo))
```
Caption the bank once (vision model, "colours + garment types, 10 words"),
store per-photo; never reuse a photo within one carousel; score 0 anywhere →
switch the whole carousel to neutral copy.
