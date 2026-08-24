---
name: carousel-styles
description: Design photo-carousel slides by cloning proven Pinterest/TikTok visual languages instead of inventing layouts. Trigger when the user wants carousel/pin designs, says a carousel "looks too plain/AI", drops a design reference to adapt, or asks for design variations of an existing carousel. Ships 10 reusable visual systems (notebook, statement, moodboard, scan, journal, lookbook, recipe card, magazine cover, iMessage, tweet) as PIL recipes, plus the hard rules that keep generated slides believable.
---

# Carousel Styles

Never invent a slide layout from scratch. Every design here was found on
Pinterest/TikTok as a proven, save-worthy genre, decomposed into its working
mechanics, and rebuilt as a deterministic PIL recipe. The pipeline:

**find a ref → decompose the mechanic → rebuild as code → batch it.**

## The hard rules (each one paid for by a real failure)

1. **Never bake text into generated images.** Image models garble letters
   ("ZOICM", "Bowtle Lingii") and platforms crop-clip baked captions. Generate
   photos text-free (`NO text, NO logos` in every prompt); draw ALL type in
   PIL on top. Exception: a strong image-edit model (nano-banana class) CAN
   render clean typography as a *design pass over a finished photo* — use it
   for callout/infographic looks, never for body copy.
2. **Text must never contradict the photo.** If a line names a colour or a
   garment, the photo must show it. Caption your photo bank once with a vision
   model (colours + garment types), then pick photos by token overlap with the
   line (colour matches weigh double). When the bank can't match — or the
   photo set is too small to choose from — switch that carousel to **neutral
   copy**: advice true over any outfit ("one accent, then stop", "press it,
   don't replace it"). Neutral beats mismatched every time.
3. **Vary faceless poses.** "No face" prompts collapse into everyone standing
   with their back to the camera. Rotate: crop at the lips, side profile,
   looking down at a bag, dark sunglasses; from-behind only occasionally.
4. **The narrative arc is pain → more pain (the bad fix) → hope → solution.**
   One beat per slide, one line per beat. The bad fix gets named explicitly
   ("folding? it lasts three days").
5. **No trailing periods** in display copy. Catchy hook on slide 1 — numeral-
   first or curiosity-gap — with ONE big image, never a pile of objects.
6. **Wrap by measured width, not character count**, and autofit font size.
   Check your display font has the glyphs you use (Poppins has no "→",
   PIL default fonts have no emoji — draw shapes instead).
7. **Fonts are part of the ref.** Identify the actual family (geometric
   grotesque like Poppins vs a heavy grotesque like Arial Black reads
   completely differently). Bundle OFL fonts with the repo so CI renders
   identically.
8. **Photos come from a bank, not fresh generation.** Generate a photo once,
   caption it, reuse forever. A 5-photo palette set (~$0.70 once) powers
   unlimited carousels and pins at $0.

## The 10 visual systems

Each entry: the mechanic that makes it work + layout recipe. Full PIL
primitives in [reference.md](reference.md).

| System | Mechanic | Skeleton |
|---|---|---|
| **notebook** | grid paper + torn sheet = handmade authority; numbered rule pages | Poppins ExtraBold headline w/ italic accent → Didot italic accent line → bold intro / Key takeaway / PUT IT IN PRACTICE → hand-circled labels with a cursor |
| **statement** | one huge lowercase line over a full-bleed photo; sassy voice | mint (186,242,214) or rose (248,198,214) Poppins SemiBold, centred, soft shadow, darkened photo |
| **moodboard** | overlapping tilted polaroids prove a palette | paint-dot palette header → 4 photos at ±2-6° with soft shadows → handwritten scribbles in the gaps |
| **scan** | "the machine annotated this street shot" | full-bleed photo, thin white inner border, mono metadata corners (SCAN 02/76), red item boxes with leader lines |
| **journal** | grainy b/w + huge script = quiet luxury | b/w photo, oversized script word + small italic qualifier, serif annotations with rule lines |
| **lookbook** | catalogue density rewards the save | giant serif title OVER the figure, spec-strip footer (pieces/outfits/bought), numbered look grid |
| **recipe card** | cooking metaphor makes an outfit teachable | arch-masked photo, INGREDIENTS / THE RECIPE two columns, chef's note italic |
| **magazine cover** | persona as cover star = instant aspiration | full-bleed portrait, Didot masthead behind the head, cover lines both sides, issue line + barcode |
| **iMessage** | advice disguised as a leaked screenshot | blurred photo bg, message bubble, reaction pill glued to the bubble TOP, long-press menu under it SAME left edge — alignment is what sells it |
| **tweet** | a hot take with fake engagement counts | white tweet card over blurred photo: avatar, verified tick, take in 3-4 lines, reposts/likes/saves row, a reply-teaser card carrying the CTA |

## Batch pipeline

1. **Specs first.** Generate copy specs (hook / sub / 3-5 tips / CTA / caption)
   with an LLM against your measured winners; validate hard (highlight word
   must appear verbatim, length caps, banned diary openers) and dedupe against
   everything already built before rendering anything.
2. **Render is $0.** Photos from the captioned bank (rule 2), type in PIL.
   Route specs to systems by content: colour topics → statement/moodboard,
   rules/capsules → notebook/lookbook, classics → journal.
3. **Review gate.** Nothing ships without a human eyeballing slides. Batch
   into waves (~100); replace-in-place when a fix lands so the queue never
   holds duplicates.
4. **Measure by save rate, not views**, per visual system (tag each carousel
   with its system) — then let the winners take the next wave's volume.

## Adapting a new ref (the loop that grows this skill)

1. Screenshot the ref; note WHERE text sits relative to the image (type as a
   physical object — receipt, Pantone card, tag — beats type floating over).
2. Name the save-trigger: is it a reference (palette), a checklist (rules), a
   test (flowchart), an identity (cover)?
3. Rebuild the skeleton in PIL with your fonts/colours; keep their layout
   maths, replace their brand voice.
4. Ship a 1-slide probe first; only then batch.
