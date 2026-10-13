---
name: ugc-hooks
description: "Find the organic UGC app-promo formats that are going viral right now (a 1–3 second emotional hook of a person, then a plain screen recording of the app), pull the exact hook line off every video, sort them into hook formats, then film and cut your own founder-UGC versions with the original trend sounds and a posting kit that doesn't look like spam. Trigger whenever the user asks which hooks sell apps on TikTok/Reels right now, wants viral hook research or UGC scripts for an app, wants a shot list for filming themselves, has raw takes to turn into hook + demo videos, or asks how to caption, comment and post app-promo UGC."
---

# UGC hooks

**Give me an app and two days: day 1 finds the hook formats that are selling
apps on TikTok this season, day 2 turns your own takes into a batch of hook +
demo videos ready to post.** Made by [@nestymee](https://x.com/nestymee); one
run took 450 viral videos → 15 hook formats → 88 takes → 28 finished videos in
48 hours. The rules below are what that run taught.

```bash
# Day 1 — research
python3 ../../tools/carousel_scan.py --queries "this app changed my life" "wdym you don't have to" \
    --per-query 30 --save-raw raw.json > found.json          # discovery
jq '{videos: [.data.posts[] | select(.is_slideshow | not)]}' found.json > videos.json   # videos only
python3 ../../tools/engagement.py --in videos.json --top 50  # rank before you read anything
python3 ../../tools/decompose_video.py --url <URL> --out frames/<id> --fps 2 --thumbstop-sec 3.5 --transcribe
# Day 2 — produce
python3 ../../tools/render_video.py --demo demo.mp4 --hook-media hook.mp4 --hook-text "…" --out v01.mp4
python3 ../../tools/safe_zones.py --image frame.png
python3 ../../tools/schedule_post.py --channel-id … --media v01.mp4   # dry-run by default
```

Needs `APIFY_TOKEN` in `tools/.env` for discovery (≈$4 for 60 queries × 12
results), `ffmpeg`, and any OCR (macOS Vision, tesseract) for the hook text.

## What a winning app-promo UGC looks like (2026)

- **One short lowercase line + a face for 1–2 seconds + a plain screen
  recording.** No voiceover, no b-roll, no editing tricks. The text stays on
  screen for the whole video.
- **The format carries the views, not the account.** Accounts with 250–900
  followers pulled 1–6M views with these. Don't filter references by follower
  count.
- **Hooks get cloned across apps within weeks.** The same "been shopping at
  [store] for N years and I'm JUST NOW finding this???" line did 29M for one
  meal-planning app, then 8.2M and 5.8M for two others. Copy the line's
  structure, swap the noun.
- **Six months is the window.** Older formats have already been cloned to
  death; filter discovery to the last 6 months and 100k+ views.

## Operating principles

1. **Search by app/niche phrases, extract the hook afterwards.** Searching for
   hook wording only finds that hook. Search "this app changed my life",
   "apps you need", "<niche> app", then read the hook off each result.
2. **Read the hook from the frames, not the caption.** The hook is on-screen
   text in the first 0–3.5 s; the caption is usually a hashtag line. OCR the
   first frames, add the first 6 s of transcript, and only then label.
3. **Videos only.** Photo-mode carousels are a different game with different
   metrics — use [carousel-benchmark](../carousel-benchmark/SKILL.md) for them
   and drop `is_slideshow` rows here.
4. **Steal the format, not the person.** References are for the hook
   mechanic, the shot and the timing. Never reuse other creators' footage,
   faces or handles in your own posts or decks.
5. **Privacy gate before anything renders.** App demos that touch the camera
   roll, contacts, notifications or shared lists show private photos and
   other people's names. Check every frame of those clips (Step 7).
6. **Rate, then make the next batch from the winners.** Keep a top / not-top
   mark on every finished video and a views-at-24h number on every posted one;
   the next shoot list comes from those, not from taste.

## The procedure

### Step 1 — Frame (10 min)

Write the app's one-line promise, its single strongest differentiator (the
thing competitors make painful — e.g. "you don't have to type in every
ingredient"), 3–5 demo moments that show it in under 6 seconds, and 5 competitor
apps. The differentiator becomes the lead hook family in Step 5.

### Step 2 — Discover (≈$4, 20 min of runtime)

40–65 queries × 12–30 results. Mix: generic app phrases ("this app is insane",
"never deleting this app", "apps you need to download", "i built an app"),
niche phrases ("<niche> app", "<pain> app"), and 5–10 known hook phrases from
[reference.md](reference.md). If you call the Apify actor
(`clockworks~tiktok-scraper`) directly instead of `carousel_scan.py`, these
inputs do the filtering server-side:

```json
{"searchQueries": [...], "searchSection": "/video", "resultsPerPage": 12,
 "videoSearchSorting": "MOST_LIKED", "videoSearchDateFilter": "LAST_6_MONTHS",
 "shouldDownloadVideos": false}
```

Keep: views ≥ 100k, duration ≤ 60 s, not `isAd` / `isSponsored`, not a
slideshow. Save the raw dataset — it carries `musicMeta` (Step 6) and
`commentCount`.

### Step 3 — Extract the hook from every video

Per video: download (yt-dlp), take frames at 0.0 / 0.5 / 1.0 / 1.5 / 2.5 /
3.5 s, OCR them, transcribe the first 6 s. `decompose_video.py` does the frames
and transcript; add an OCR pass. Store `hook_ocr`, `demo_ocr` (frames after the
first cut) and `transcript_6s` per video.

### Step 4 — Label and sort

Send batches of ~40 (hook_ocr + transcript + caption + a contact sheet path)
to an LLM with the taxonomy in [reference.md](reference.md): `is_app_promo`,
`app`, `archetype`, `hook` (exact line), `hook_visual`, `demo` type,
`paid_partner`. Expect roughly half of the results to be real app promos.
Lay them out on a board (FigJam / Miro / a static HTML page) — one section per
archetype, a 3-frame thumbnail + hook line + views per card. The board is what
the person filming will actually look at.

### Step 5 — Write hooks and a shot list

For each archetype that fits the app: 3–5 hook lines in its pattern, adapted to
the app's differentiator, plus 8–10 "signature" lines built purely on the
differentiator. Then a shot list per format with 2 reference videos each
(template in [reference.md](reference.md)). Shooting rules that saved retakes:

- 9:16, 1080p 30 fps (4K files are too big to move around and add nothing).
- 5–6 s per take, 3 takes per hook; only the best 2–3 s survive the edit.
- First frame already in the emotion. Face and action in the centre — TikTok
  covers the top ~8%, bottom ~20% and right ~11%.
- No text, stickers or music while filming; all of it is added in the edit.
- Let the person also record free-form takes (getting ready, dancing, walking
  out of the closet): they get cut into hooks for formats nobody planned.
- Before → after works as a **motion match-cut**: bend down out of frame →
  rise in the new outfit; a towel or hand swept over the lens → reveal. Film
  both halves at the same spot and framing.
- Screen recordings of each demo moment, 5–10 s each, plus any finished older
  videos — their demo halves are often the cleanest footage.

### Step 6 — Take sounds from the viral originals

The reference video's sound is part of the format. From the raw dataset take
`musicMeta.playUrl` (the full sound) for the references of each format.

- **Skip voice sounds.** Many "original sound" entries are a person talking
  ("I can't believe this is real…"). Run Whisper on the first 15 s; if it
  returns sentences instead of `[Music]`, drop it — a stranger's voice over
  your face reads as dubbed.
- **Put the beat drop on the cut.** Compute an RMS envelope (0.1 s windows),
  find the largest jump in the first 8 s, and start the sound at
  `drop − hook_length` so the drop lands exactly where the face cuts to the
  app. Sounds without a clear drop start at 0.
- Loudness-normalise to about −14 LUFS and fade the last 0.5 s.
- For the actual post, add the same sound **inside the app** (see Step 9);
  the baked-in track is for previews and Reels drafts.

### Step 7 — Pick takes, cut, and run the privacy gate

- **Takes**: a contact sheet per take (frames every 0.5–1 s, UI zones shaded),
  pick the 2–4 best per scene with one sentence why, note in/out seconds.
  Prefer: emotion in frame 1, eyes to camera, clean background related to the
  niche.
- **Edit** (Remotion, see [reference.md](reference.md) for the composition):
  hook 1.3–5 s → demo 5–9 s, 7–16 s total. Hook text plain white with an
  outline over the face; over app screens the same text gets a translucent
  box. Text sits below the top UI zone (~400 px of 1920).
- **Multi-screen demos need step captions.** A demo that cuts between 3–4
  screens with the hook text still on top reads as random scrolling — it was
  the only video in our batch rated "not top". Replace the hook text during
  the demo with one caption per screen: a big main line + a smaller second line
  ("snap your fridge / no typing ingredients" → "it plans 7 dinners / from
  what you already have").
- **Privacy gate**: for any clip that shows a photo grid, gallery scan, chat,
  notification or shared list, extract crops of the changing area at 8 fps
  and look at every frame. Cut the unsafe windows and splice around them; if a
  screen recording opens on a panel with someone else's name, start it after
  the panel. Re-check the rendered file, not just the source clip.

### Step 8 — Review loop

Render everything, publish to a review page (one card per video: player, text,
sound name with link, "top / not top" buttons stored in a small DB), and let
the person rate before anything is scheduled. Fix the "not top" ones first —
it is usually the demo, not the hook.

### Step 9 — Posting kit (TikTok, as of Oct 2026)

Rules that changed recently and are easy to miss:

- **Content disclosure → "Your brand"** is required when the account promotes
  its own product (TikTok Community Guidelines, effective 24 Sep 2026). TikTok
  says it does not change distribution. "Branded content" is for paid deals.
- **AI-generated label** on any clip that shows a realistic AI image of a
  person (virtual try-on avatars count).
- **Max 5 hashtags** on TikTok (since mid-2025) and on Instagram (since Dec
  2025). Skip `#fyp`/`#viral`; 2–4 niche tags + the brand tag.
- **No store links in comments** — TikTok ranks comments with links/promos
  lower. Name the app; people search for it.
- Disclosed or business posts may only get the **Commercial Music Library**;
  if the reference sound isn't there, pick a similar one from it.

Anti-spam rules for a batch (all checkable in code before export):

- Every caption and every pinned comment unique; the app name appears once per
  caption and is worded differently each time.
- Hashtag sets vary; never the same set on two consecutive posts.
- ≤1 emoji per caption, no caps-lock, no "link in bio", no "like / follow /
  tag a friend" (engagement bait is excluded from For You).
- Pinned comments are mostly questions to the viewer; only some answer "what
  app / where to get it".
- Reply bank = meaning, not templates: never paste the same reply under
  dozens of comments.

Mine the comments before writing captions: scrape the top 40 comments of the
20 best references (≈$1 on Apify). In fashion/lifestyle app promos the most common
question is "what's the app??" (under one 5M-view promo the creator's reply
"it's an app called X!" collected 1.3k likes), then "is it free?", "not in my
country", "is this AI?". The most-liked *pain* comment (10k likes under one
closet-app promo: "i have too many clothes to photograph them all") is a
ready-made hook and video reply.

Cadence: 1–2 posts a day, ≥4 h apart, alternate formats so two similar videos
never go out back to back; schedule ahead in TikTok Studio. Track status,
date, link and 24 h views per video; the next batch comes from the top
formats.

## Deliverables

```
research/   board link + catalog.csv (url, views, date, archetype, hook, demo type)
hooks.md    hook lines per format + signature lines on the differentiator
shotlist    per format: what to film, how, 2 reference links
selects/    chosen takes with in/out + one-line reason
out/        finished videos + overview contact sheet
posting/    videos in posting order, no-music copies, posting.md/.csv
            (caption, pinned comment, sound + start second, disclosure, AI label),
            replies.md, a tracking sheet
```

## Shared tools

| Step | Tool | Use |
|---|---|---|
| 2 | `carousel_scan.py` | Apify keyword search (Top section) with `--save-raw`; keep `is_slideshow: false` and wrap as `{"videos": [...]}` for the analytics tools |
| 2 | `video_metadata.py` | single-URL fallback when a reference is found by hand |
| 3 | `decompose_video.py` | frames + thumb-stop window + Whisper transcript; add OCR on top |
| 2–4 | `engagement.py` | rank references by engagement/freshness before labelling |
| 6 | `trending_sounds.py` | sanity-check that a reference sound is still trending in the target region |
| 7 | `render_video.py` | single hook + single demo render; for multi-clip demos, step captions and sound use the composition in [reference.md](reference.md) |
| 7 | `safe_zones.py` | check caption placement on a frame grab |
| 9 | `schedule_post.py` | scheduling via Postiz, dry-run by default, disclosure on |
