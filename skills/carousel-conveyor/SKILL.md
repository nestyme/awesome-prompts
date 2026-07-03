---
name: carousel-conveyor
description: Turn trendwatched hook ideas into finished TikTok/Instagram photo carousels for a recurring AI persona, then schedule them via a posting tool (e.g. Postiz). Trigger when the user wants to build carousels for a character, stand up a new persona, generate reusable cover photos, render slide decks with captions, or plan/schedule carousel posts. The downstream complement to the trendwatch skill: trendwatch decides WHAT to post; this skill PRODUCES and SCHEDULES it with a specific persona's face and lore. Cost-aware by design — generate a reusable POOL of face photos ONCE per persona, then composite captions for free and reuse the photos across many carousels.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---

# Carousel Conveyor

A factory for turning hook ideas into finished, scheduled photo carousels for a
recurring AI persona. It is the production half of the content system: the
**trendwatch** skill produces the hooks/formats; this skill renders them as
7-slide carousels in a persona's voice and face, then schedules them to TikTok.

> The script names below (`gen_persona_ref.py`, `cover_bank.py`, builders,
> `schedule_batch.py`) refer to a reference implementation — a few hundred lines
> of Python around the Gemini image API, PIL, and the Postiz API. The scripts are
> trivial to rebuild; the **operating principles and the prompt blocks are the
> transferable asset**.

## Shared tools

The repo's [`tools/`](../../tools/README.md) CLIs cover the primitives this skill orchestrates (uniform JSON envelope, composable):

| Step | Tool | Use |
|---|---|---|
| 2-3 | `gen_image.py` | The ONE paid step: generate the locked reference (text→image) and each cover (ONE-hop image-edit of that ref) |
| 4 | `caption_composite.py` | The "text is free" step — composite captions in PIL with 8.5%/10%/10% safe margins; never regenerate a photo to change words |
| 5 | `safe_zones.py` | Optional extra gate: verify slides sit inside platform safe zones + read at thumbnail size |
| 6 | `schedule_post.py` | Batch-schedule via Postiz with AI-disclosure on; **defaults to `--dry-run`, needs `--live` to post** |

Keys: `GEMINI_API_KEY`, `POSTIZ_API_KEY`. Full map + flags in [`tools/README.md`](../../tools/README.md).

The whole design is built around one economic insight (the "AI UGC army"
playbook popularized by Adrià Martinez): the only expensive step is generating
photorealistic faces. So generate a **reusable pool of text-free face photos
ONCE per persona**, then build unlimited carousels by compositing caption text
over those photos **for free** with PIL. A persona costs ~$0.60 to stand up
(one reference + ~6 covers) and then produces dozens of carousels at $0.

## Operating principles

1. **The face is the only paid step — everything else is free.** Each persona
   has exactly ONE locked reference selfie (the only pure text-to-image gen) and
   ~6 "cover" photos (each an image-EDIT of that one reference). Every carousel
   reuses those covers; all caption/headline/watermark text is composited
   deterministically in PIL at $0. Re-rendering captions, layouts, watermarks, or
   whole schedules is always free — never regenerate a photo to change text.
2. **Never edit an edit.** Every cover is an image-edit of the ORIGINAL locked
   reference, never an edit-of-an-edit. Editing a generated image compounds
   drift and the face stops being recognizable. One ref → N covers, always
   one hop.
3. **UGC-natural beats AI-glossy — this is the #1 quality bar.** The covers must
   read as a genuine candid phone selfie an ordinary person took, NOT a polished
   content-creator beauty shot. If a cover looks "neural"/airbrushed, it failed.
   The realism is engineered in the prompt (see "The prompts" below): inject
   controlled imperfections + camera artifacts + a hard negative clause.
4. **Generate at ~1k, not 2k/4k.** TikTok recompresses anyway; 1080×1920 (9:16)
   is the target. Higher res just burns money and reads glossier.
5. **GATE before scheduling — HARD RULE.** The pipeline auto-schedules, so it
   must be gated. ALWAYS: build with no posting, render the slides, present them
   for the user's visual review of **character consistency** (same face, same
   defining features every slide), and schedule ONLY the carousels the user
   approves. Never auto-publish unreviewed faces.
6. **Always disclose AI content.** Every TikTok post sets the platform's
   AI-generated-content flag (`video_made_with_ai: true` in the Postiz API).
   Non-negotiable, keeps the account policy-safe.
7. **No baked text in photos, ever.** Cover photos are generated with an
   explicit NO-TEXT clause. All words live in the PIL overlay layer so they stay
   editable, correctly spelled, and on-brand.
8. **No hook-photo repeats within a single posting day.** When scheduling a
   day's posts, each carousel's slide-1 cover (the "hook photo") must be
   distinct. If a photo must repeat, relegate it to the CTA slide (slide 7),
   never slide 1. Keeps a feed from looking like a copy-paste.
9. **Secrets stay local.** The config file holds LIVE API keys and channel IDs.
   Never commit, print, or paste it anywhere. Add specific files to git, never
   `git add -A`.
10. **Persona lore drives the copy.** A carousel is a trendwatch format poured
    into a persona's brief/voice. Same format ("look expensive on a budget")
    reads completely differently for a 22yo British budget-stylist barista vs a
    34yo busy mum — that difference is the whole point. Pull the voice from the
    persona's `brief`; never write generic copy.

## The economy (why it's cheap)

```
ONE-TIME per persona (the only money spent):
  ref generation   → ref_<slug>.png       (1 text-to-image gen   ~$0.10)
  cover bank       → _cover_bank/*.png    (~6 image-edits of ref ~$0.50)
                                           ───────────────────────
                                           ≈ $0.60 / persona

FREE forever after:
  builders = reuse a banked cover + reuse app-screen images + PIL caption text
  → every carousel = 7 slides at $0
  → reuse the same ~6 covers across 10+ carousels
  → re-render captions / watermarks / handles / layouts at $0
```

## Pipeline

```
0. Intake        → gather persona lore + which hooks to build + channel mapping
1. Persona setup → register persona in code (profiles/themes/scenes), ONCE
2. Reference     → one locked selfie (the anchor)
3. Cover bank    → ~6 reusable text-free covers (each one edit-hop from the ref)
4. Build         → compose covers + app screens + PIL captions → 7-slide decks
5. GATE          → present rendered slides; user visually approves consistency
6. Schedule      → map persona→channel; batch-schedule approved carousels
```

## Step 0 — Intake (ask the user only for what can't be discovered)

Auto-discover first: read the persona registry, config, cover scenes, the
trendwatch `ideas/` + `current-plan.md`, and memory files. Then ask the user
ONLY for judgment/operational facts:

**For a NEW persona (must ask — this is lore, not lookup):**
1. **Name, age, place, handle (@)** — e.g. "Mia, 22, UK, @mia.styled"
2. **Positioning / core thesis** — the one belief the persona evangelizes
   (e.g. "you don't need more money or more clothes — learn to use what you
   already own"). This becomes the `brief`.
3. **Look** — hair, skin, defining features that must stay consistent every
   slide (e.g. "chestnut wavy hair + two candy-pink money-piece strands"). The
   more specific + slightly unusual the feature, the more recognizable the face.
4. **Setting(s)** — where their photos are shot (e.g. barista at a coffee shop /
   a small rented bedroom). Drives the cover scenes.
5. **Voice** — genZ / warm / deadpan / British / etc.

**For BUILDING carousels (ask):**
6. **Which hooks/formats** to build — pull from the trendwatch `ideas/` output,
   or the user names them. Map each to a builder.
7. **Schedule shape** — how many days × posts/day, and start date.

**For SCHEDULING (ask — cannot be guessed):**
8. **Channel mapping** — which posting-tool account each persona posts to.
   Pull the live channel handles with `python3 tools/schedule_post.py
   --list-channels` (returns each channel's handle + platform + id), then
   confirm the persona→handle→id mapping with the user before writing it to
   config. Never hardcode handles — always discover them from the tool.
9. **Final go/no-go** after the visual gate (principle 5).

## Step 1 — Persona setup (register in code, once)

A persona must exist in the registry before any generation. Mirror an existing
persona. The registry entry shape:

```python
"slug": {
    "mode": "character",                 # "character" (has a face) | "text" (brand)
    "handle": "@persona.handle",
    "channel_key": "slug",
    "style_preamble": REF_NOTE + ONE_IMAGE + STYLE + TEXT + "\n\n" + LOOK + SETTING,
    "refs": ["ref_slug.png"],            # the ONE locked reference filename
    "anchor": True,
    "brief": ("... the persona's positioning + thesis + what content performs "
              "+ voice. THIS is the lore that drives every caption ..."),
},
```

Plus: cover scenes (`SCENES["slug"]` = dict of `scene_slug → scene description`),
the locked-traits ref prompt, the text theme (fonts, panel colour, watermark
handle), and per-builder copy blocks in the persona's voice.

## Step 2 — The reference selfie (the anchor)

Generates `ref_<slug>.png` — a plain, real-looking UGC selfie from PURE TEXT
(no refs). This is the persona's permanent locked reference. Every future cover
is an image-edit of THIS file.

Requirements for a good anchor:
- The WHOLE FACE clearly visible — phone held low/to the side, not covering the
  face (a reference must show the face it's locking).
- The defining features stated explicitly (hair, strands, freckles, nose stud).
- The full UGC realism block appended (see "The prompts").

If the phone covers the face or the look is off, edit the prompt and rerun —
this is the one photo worth getting perfect, because everything inherits it.

## Step 3 — The cover bank (reusable text-free photos)

Generates `_cover_bank/<slug>_<scene>.png` — each an image-edit of
`ref_<slug>.png` (one hop, principle 2), text-free (principle 7), in the
persona's settings. These are the candid 9:16 snapshots reused as slide 1
(and CTA slides) of every carousel.

Aim for ~6 varied scenes so the schedule can avoid hook-photo repeats within a
day (principle 8): e.g. counter / mirror / break / bedroom / closet / window.

## The prompts (the actual realism levers)

These three blocks are what make the faces read as real UGC rather than AI
renders. Append them to every cover/ref generation.

**`UGC_STYLE`** (verbatim, battle-tested):

```
STYLE — an extremely ordinary, unremarkable real iPhone front-camera selfie,
the kind a normal person snaps and posts without thinking, NOT professional
photography and NOT a polished content-creator beauty shot. Authentic amateur
snapshot: slightly awkward angle, a little crooked and off-centre framing,
mild overexposure where the window light hits, slightly uneven mixed indoor
lighting, faint front-camera sensor grain and a touch of JPEG softness, the
limited flat dynamic range of a cheap phone camera. REAL UNRETOUCHED SKIN with
visible texture and pores, fine peach fuzz, a little oily T-zone shine, faint
under-eye shadows, slight natural redness around the nose, one or two tiny
blemishes, and a couple of stray flyaway hairs out of place — believable human
imperfection, never flawless. Natural, slightly muted, true-to-life colours,
not punchy or oversaturated. CRITICAL: absolutely NO beauty filter, NO skin
smoothing, NO airbrushing, NO waxy or plastic AI-perfect skin, NO studio
lighting, NO glossy magazine polish, NO flawless symmetrical model perfection
— it must read as a genuine candid photo a real, ordinary person actually took.
```

The three mechanisms stacked: *amateur camera artifacts* + *real unretouched
skin* + a *hard negative clause* (the anti-"neural" lever).

**`NO_TEXT`** (verbatim):

```
CRITICAL: the image must contain absolutely NO text, NO letters, NO words, NO
captions, NO numbers, NO app interface, NO graphics, NO watermark, NO logo and
NO writing of ANY kind ANYWHERE in the frame.
```

(All text is added later in PIL.)

**Text-overlay stripping** — if a persona's style preamble contains a legacy
"TEXT OVERLAY: …" instruction, strip it before generating a cover, so the model
doesn't literally bake the caption spec into the photo.

**PIL overlay safe margins** — the caption compositor enforces: left/right safe
margin = 8.5% of width, top band = 10%, bottom band = 10% (platform UI covers
those), font auto-fit so nothing ever overflows. Captions can't be misspelled
or off-grid because they're code, not generation.

## Step 4 — Build the carousels

Each builder = reuse a banked cover (slide 1) + app-screen images + free PIL
caption text → a 7-slide deck. Map each trendwatch format to a builder
(app-demo / cleanout / shop-your-closet / multi-concept tips listicles…). Each
concept entry per persona holds: `key`, `cover`, `cta_cover`, `hook`,
`highlight`, `sub`, `tips` (list of `(icon, label, headline, highlight, sub)`),
`cta_head`, `cta_sub`, `caption` — written in the persona's brief voice, not
generically.

Builds write `slide_01..07.png`, `slides.json`, and `caption.txt`. Nothing
posts at build time.

## Step 5 — GATE (mandatory visual review)

Before scheduling ANYTHING (principle 5):
1. Read several slides per carousel (at minimum slide_01 cover, one content
   slide, slide_07 CTA) with the Read tool so you can SEE them.
2. Check: same face + same defining features every slide; UGC-natural not
   glossy; captions correct + on-brand; watermark = right @handle.
3. Present them to the user and get explicit approval.
4. Schedule ONLY approved carousels. If a cover looks glossy/inconsistent,
   regenerate that cover (Step 3) and rebuild (Step 4, free) before scheduling.

## Step 6 — Schedule

- List the posting tool's channels with `tools/schedule_post.py --list-channels`,
  confirm persona→handle→id mapping with the user, write to config.
- Batch scheduling is **gap-aware**: build the future slot pool from configured
  posting slots (e.g. 08:30 / 11:30 / 21:00 local), query the tool for slots
  already booked on that channel, drop them, assign each carousel to the
  earliest free slot. Never double-book; record results in a ledger file.
- Ordering: interleave so one app-demo-family carousel lands at each day's
  first slot, and principle 8 holds (no slide-1 cover repeats within a day).
- ⚠️ The batch scheduler POSTS LIVE when run. Only run after the Step 5 gate
  passes and the user gives the final go. Support `--dry-run` and `--as-draft`.

## Invocation modes

- **Full run** — "build carousels for {persona} and schedule them" → all steps.
- **New persona** — "stand up a new persona {name}" → Steps 0–3 (then offer 4–6).
- **Covers only** — "regenerate {persona}'s covers" → Step 3.
- **Build only** — "build the {concept} carousel for {persona}" → Step 4 + gate.
- **Schedule only** — "schedule {persona}'s approved carousels" → Steps 5–6.
- **Re-stamp** — "rename {persona} to @newhandle" → edit theme/registry,
  rebuild (free); no regeneration.

## Failure modes & fallbacks

| Failure | Fallback |
|---|---|
| Cover looks AI-glossy / "neural" | Strengthen `UGC_STYLE` imperfections + negative clause; regenerate that cover only |
| Phone covers the face in the ref | Edit the ref prompt → "hold phone low so the WHOLE FACE is visible"; rerun ref gen |
| Face drifts across covers | You edited an edit — always edit the ORIGINAL `ref_<slug>.png` (principle 2) |
| Image-gen provider exhausted | Route to a fallback provider for the same model |
| Same photo would repeat in a day | Reorder the batch; relegate the repeat to a CTA slide (principle 8) |
| Channel id unknown | List channels via the posting tool; confirm mapping with user before writing config |
| Caption/handle wrong | Just rebuild — text is free PIL, never a regeneration |

## Relationship to trendwatch

`trendwatch` → `carousel-conveyor` is a two-stage pipeline:
- **trendwatch** mines competitors, decomposes winners on 7 axes, and outputs
  ranked hook ideas + formats (`ideas/YYYY-MM-DD.md`, `current-plan.md`).
- **carousel-conveyor** takes those hooks/formats, pours each into a persona's
  face + voice + lore, renders the slides, and schedules them.

When building, pull the source hook from the latest trendwatch `ideas/` file and
keep the persona's `brief` voice. Winners logged in trendwatch's `experiments.md`
should drive which formats you build more variants of (vary persona/cover/setting
per trendwatch principle 7).
