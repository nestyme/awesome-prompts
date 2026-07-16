# Meta Ads — Safe Zones & Policy-Proofing Rules

Rules to bake into every image-generation prompt (and design review) for Meta paid creatives. Learned by shipping creatives and watching what the feed UI covers and what review flags.

## Hard constraints (add to the QUALITY block of every creative prompt)

1. **Top safe zone** — reserve top 10% of canvas CLEAR of critical copy and logo placement.
   Feed UI (profile row, post text preview) can obscure this band.
2. **Bottom safe zone** — reserve bottom 10% of canvas CLEAR of critical copy and logo.
   CTA button + comments snippet can obscure this band.
3. **Middle 80%** — this is where hero image, headline, subhead, and brand mark MUST live.
4. **Thumbnail readability** — main hook must be readable at 300×300 (Meta's thumbnail preview).
   Body copy paragraphs should be minimal / larger font size for this.
5. **No text at the very edges** — if a creative has a "timestamp" or "chapter mark",
   place it at 15% from the top, not at the edge.

## Copy-paste prompt suffix

```
META AD SAFE ZONES:
- Top 10% of canvas MUST be clear — no headline text, no logo placement in the top 10%.
- Bottom 10% of canvas MUST be clear — no headline text, no logo placement.
- All critical typography (hook, subhead, brand mark) lives in the middle 80%.
- Main hook readable at 300x300 thumbnail.
- NO direct weight-loss language, NO "you" + personal attribute framing.
```

## Crop survival (1:1 → 4:5 mobile feed)

Meta auto-crops 1:1 to 4:5 on some mobile feed placements. 4:5 is taller and narrower
than 1:1, so the cover-crop shaves the LEFT + RIGHT edges (not top/bottom).
Combined with the middle-80% rule:
- Hero element: MUST sit in the center 70% horizontally, so the side-crop can't clip it
- Headline: MUST be inside the center 70% width
- Logo: corner placements OK only if still inside the center 70% width

## Policy-risk wording patterns (personal-attributes policy)

Meta's "personal attributes" policy auto-flags copy that addresses the viewer's body, health,
or identity directly. Patterns that get flagged — and reworks that keep the idea:

| Risky copy | Why flagged | Safe rework |
|---|---|---|
| "SCARED YOU WON'T LOSE WEIGHT BEFORE SUMMER?" | "you" + body attribute + weight loss | "SUMMER BODY TALK? SKIP IT." |
| "I DIDN'T LOSE WEIGHT. I FOUND THE OUTFIT." | direct weight-loss mention | "NOT A DIET. JUST A BETTER OUTFIT." |
| BEFORE / AFTER panel labels | weight-loss association (yellow flag) | relabel "TUESDAY" / "WEDNESDAY" or "OUTFIT A" / "OUTFIT B" |

General rules:
- Never combine "you" with a personal attribute (weight, age, health condition, financial state)
- First-person framing ("I", "my") clears review far more reliably than second-person
- "Before/After" as a *visual* is fine; as a *label* it's a flag — rename the panels

## Screenshot-style creatives (tweet/X, iMessage, Reddit, Notes formats)

Real-UI screenshot ads are common and perform, but Meta requires ads not to deceptively
impersonate platforms. To stay safe:
- Add a subtle "Sponsored" / "Ad" tag in a corner (not covering content), or
- Apply a 5-8px soft outer frame (off-white) around the screenshot so it signals
  "stylized content", not a live clickable UI, or
- Re-angle the phone slightly (3-5°) so it reads "photo of a phone", not a live interface

Zero-risk formats that consistently clear review: capsule/outfit grids, magazine-cover
parodies, billboard/poster mockups, embroidery/craft props, screenshot formats with the
framing treatments above.
