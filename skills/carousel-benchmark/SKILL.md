---
name: carousel-benchmark
description: "Find the TikTok photo-mode carousels (slideshows) that actually go viral in a niche and the accounts behind them, rank them by organic quality (save-rate, like-rate, boost detection) instead of raw views, and turn the winners into a leaderboard + format breakdown you can copy. Trigger whenever the user wants to research viral carousels / slideshows / photo posts for their app or brand, asks 'who is winning with carousels in X', wants references before launching a carousel account, or asks whether a competitor's carousel numbers are organic or Spark Ads. Works for any niche — fashion, fitness, study, productivity, dating, home."
---

# Carousel benchmark

**Give me a niche — I return the carousel accounts that win there, ranked by
organic quality, with the formats that carry them and a slide-by-slide read of
the best posts.** Made by [@nestymee](https://x.com/nestymee) while launching a
carousel account; the tricks below are what a full day of scraping taught.

```bash
# 1. discover (Top search — the only search that returns carousels)
python3 ../../tools/carousel_scan.py --queries "digital closet app" "apps every girl needs" --per-query 30 > search.json
# 2. profile-scan the candidates (≈$0.003/post on Apify)
python3 ../../tools/carousel_scan.py --profiles handle1 handle2 handle3 --per-profile 25 > profiles.json
# 3. rank
python3 ../../tools/carousel_leaderboard.py --in profiles.json --min-slides 5 --md leaderboard.md
# 4. look at the slides of the top posts
python3 ../../tools/carousel_scan.py --posts URL1 URL2 --slides-dir slides/
```

Needs `APIFY_TOKEN` in `tools/.env`. A niche-wide benchmark (≈50 queries, ≈80
profiles, ≈3,400 posts) costs about $11 on Apify's $50 Starter plan.

## Why carousels need their own method

Photo-mode posts are counted, distributed and bought differently from videos,
so the usual video research silently fails on them:

- **Search hides them.** Apify's TikTok scraper returns *zero* slideshows for
  `searchSection: "/video"` and for hashtag scrapes. Only the default *Top*
  section mixes them in (≈40% of results). A profile scan always includes them
  (`isSlideshow: true`). If your first scan shows no carousels, it is the
  query mode, not the niche.
- **Views are the cheapest metric to fake.** Spark Ads on a slideshow buy
  millions of "views" with almost no likes. In one fashion sample the organic
  like-rate median on 50k+ carousels was **5%** and the bottom decile **0.9%**;
  the "viral" shadow network everyone envied sat at **0.2–0.8%**. Rank by
  save-rate and like-rate, flag the rest as `boost?`.
- **The winners are rarely the official accounts.** Brands run shadow pages
  (1–4k followers, no brand name in the handle, app only as a watermark or a
  "btw it's called…" last slide) and the aggregators ("apps every girl
  needs") drive more installs than the brand's own page. You have to find them
  by content, not by name.

## Operating principles

1. **Auto-discover before asking.** Handles come from tools, not the user:
   Top-section keyword search, public slideshow banks, X posts by growth people,
   competitor bios. Ask the user only for the niche, their product, and taste.
2. **Never guess a handle from an app name.** `@stylebook`, `@umax`, `@quittr`,
   `@acloset` were all random people in our run. Confirm every candidate by bio
   + link + captions before it enters the leaderboard, and drop the misses.
3. **Engagement over views, always.** Median views ranks reach; save-rate ranks
   whether the content is worth anything; like-rate under 1% on a 50k+ post is
   a paid smell. Say so in the deliverable.
4. **Profile-scan, don't search-scan, for metrics.** Search gives one post per
   account; medians and cadence need the last 25–30 posts. Search is for
   discovery only; label search-only rows as such.
5. **Separate the format from the numbers.** A boosted account can still show
   the best format in the niche (the fashion shadow network's "try on clothes
   from any website" was exactly that). Take the format, refuse the benchmark.
6. **Keep the raw data.** Save every Apify dataset; re-ranking is free,
   re-scraping is not.

## The procedure

### Step 1 — Frame the niche (5 min)

Write down: the product's one-line promise, 3 adjacent niches the buyer also
scrolls (a closet app's buyer also watches study, self-care and "apps you
need" slideshows), and 5–10 competitor apps. Everything below runs on this.

### Step 2 — Discover candidates (3 sources, run in parallel)

**a. Top-section keyword search** (`carousel_scan.py --queries …`). Use the
phrases people type, not brand names: "apps every girl needs", "this app
changed my life", "outfit ideas app", "aesthetic apps", "productive apps you
need", "hidden iphone apps", plus the niche's own hooks. 20–25 queries × 30
results ≈ $2. Keep every author whose result is a slideshow.

**b. Public slideshow banks.** `autovirality.com/tiktok/slideshows` (and
`/category/<niche>?page=N&sort=like`) lists the top-rated slideshows with
handles and view/like/save counts; it is plain HTML, fetchable. Pull the
categories nearest your niche and take every creator that promotes an app.

**c. Growth-people chatter on X.** Search X (Grok with `x_search`, or plain
search) for "slideshow", "photo mode", "carousel farm", "notification format"
+ your niche. This yields playbooks and screenshots more than handles, but the
screenshots name accounts. Expect 5–10 handles per hour here, not 50.

Also worth one look: `tiktok.com/discover/<query-slug>` pages render in a
browser and list posts (video and photo) with handles for a search phrase.

### Step 3 — Profile-scan everything (the $5 step)

`carousel_scan.py --profiles … --per-profile 25` on every candidate, including
the official accounts of the competitor apps. Before trusting a row, read its
bio and link: mark it `official` (bio sells the app), `shadow` (persona
account whose link is the app's invite link or whose captions always end with
the app name), or `creator` (independent). Drop handles that turn out to be
someone else.

### Step 4 — Rank (`carousel_leaderboard.py`)

The table you hand over, per account: carousels/posts, median and best
carousel views, hit-rate ≥100k, save-rate, like-rate, `boost?` count,
posts/week, last post, plus the three best posts with links. Sort by median,
then read it through the quality columns:

| Signal | Healthy | Suspicious |
|---|---|---|
| like-rate on 50k+ posts | 3–10% | <1% → Spark Ads |
| save-rate | 2–5% on advice/list formats | <0.5% on "advice" = the advice is filler |
| comments on "help me choose" posts | 1–3% of views | — |
| cadence of the winners | 1–6 posts/week | 3/day with a 1k median = frequency isn't the fix |

`calibration` in the JSON gives this sample's own like-rate p10/median; if the
niche runs lower (some do), move the 1% line to its p10.

### Step 5 — Read the slides of the top 10

`carousel_scan.py --posts URL… --slides-dir slides/` downloads every slide and
builds a contact sheet per post. For each, write down: slide 1 (hook: photo,
text card, notification, product screenshot?), slides 2–N (what each one
earns the swipe with), where the product appears (never / watermark /
last slide / every slide), and what the caption asks for (vote, save, part 2).
This is the part founders skip and the part that actually transfers.

### Step 6 — Deliver

`leaderboard.md` + the slide sheets + a one-page read with: (1) the 5–8
accounts that are the real benchmark and why, (2) the 4–6 formats behind
their numbers, each with the best example URL and its engagement, (3) the
accounts whose numbers are bought, so nobody copies their volume, (4) the
save-rate / cadence targets for the user's own account. Optional: render the
JSON into a sortable HTML page; the `--md` table is enough for most.

## Formats that carried the numbers (cross-niche, 2026 sample)

| Format | Example | Organic signal |
|---|---|---|
| **"Help me choose"** — same person, same spot, 5–6 options, numbered | interior "which corner design?" 125M; virtual-try-on "help me pick a prom dress" 1.2M / 32k comments | comments 2–3%, saves low |
| **Numbered list on a brand template, product only on the last slide** | self-care app "you need 4 hobbies" 4.8M | save-rate 5.4% |
| **Notes-card on an aesthetic photo, one app per slide, "this one is mine"** | app-recs page 64k / 2.4% saves; same template 3 months earlier did 1.7k → the hook, not the template, made the difference | saves 1.5–2.5% |
| **Roundup "N apps every girl needs" with icons only** | 757k / 4.4% saves, zero production | saves 4%+ |
| **Ask for recs + personal ratings** ("phone games y'all are obsessed with, 11/10") | 4.3M / 27k comments / 4.7% saves | both |
| **Problem → math → steps → product** | closet-math carousel, structurally perfect but 9k views: pink text on photos was unreadable and an official 1k-follower account got no seed | needs readable slides + a persona account |
| **Try-on / transformation from a shadow persona** | "btw the app is called …" 1–7M | like-rate 0.2–0.8% → bought; steal the format, not the numbers |

Two things held across every niche we looked at: the winning *official* app
accounts post content that is not about the app (motivation, rules, lists)
with the app in the bio and on the last slide, and the winners post 1–6 times
a week, not 3 times a day.

## Reference accounts (scanned 2026-09-29, last 25 posts each)

Public accounts, so you can open them and see the format live. Numbers are
carousel-only: median views, best post, pooled save-rate and like-rate. They
will drift; the *pattern* is the point.

| Account | Niche | Sells | Median | Best | Save | Like | Read |
|---|---|---|---:|---:|---:|---:|---|
| [@grindai.app](https://www.tiktok.com/@grindai.app) | self-improvement | own app (bio + last slide) | 37k | 28.4M | 1.3% | 10.3% | motivation lists, 6 posts/wk, app never on slide 1 |
| [@the.atomic.reset](https://www.tiktok.com/@the.atomic.reset) | discipline / fitness | own app | 26k | 10.7M | 2.4% | 12.5% | one post a week is enough when saves are this high |
| [@sourhealing](https://www.tiktok.com/@sourhealing) | self-care | own app | 20k | 4.8M | 4.6% | 9.2% | text-only brand template, numbered lists, CTA on slide 6 only |
| [@homedecorave](https://www.tiktok.com/@homedecorave) | interior | own app (link in bio) | 12k | 125M | 0.2% | 3.3% | "which one should I go with" + AI renders; reach from comments, not saves |
| [@visualize.ai.app](https://www.tiktok.com/@visualize.ai.app) | interior | own app | 5k | 33M | 1.0% | 8.6% | same mechanic as above, 18k followers |
| [@heather.xoxo](https://www.tiktok.com/@heather.xoxo) | dating advice | nothing on-slide | 41k | 7.5M | 2.7% | 9.7% | pure text advice, hashtags only — the ceiling for "no product" content |
| [@themodestfemme](https://www.tiktok.com/@themodestfemme) | modest fashion | IG / shop | 38k | 1.7M | 2.5% | 8.0% | style guides, "want a part 2?" |
| [@onstyle_app](https://www.tiktok.com/@onstyle_app) | fashion | own app | 31k | 1.0M | 1.5% | 2.8% | colour-decoding carousels "what colours should we decode next?" |
| [@theappshelf](https://www.tiktok.com/@theappshelf) | app recs | own app inside roundups | 5k | 451k | 3.8% | 6.9% | Notes-card per app on aesthetic photos, "this one is mine" |
| [@flora_inspox](https://www.tiktok.com/@flora_inspox) | girly inspo | nothing | 2.6k | 757k | 3.7% | 6.5% | "apps every girl needs" with icons only, zero production |
| [@quierodulcito](https://www.tiktok.com/@quierodulcito) | girly inspo | nothing | 1.9k | 4.3M | 4.4% | 9.9% | "phone games y'all are obsessed with, 11/10" — ask for recs + personal ratings |
| [@dreamfits.chlo](https://www.tiktok.com/@dreamfits.chlo) | fashion (shadow) | try-on app, "btw it's called…" | 645k | 4.9M | 0.03% | 0.4% | **bought**: 7 of 9 carousels flagged; copy the try-on format, not the numbers |

The 1% like-rate line came from this sample: 273 carousels with 50k+ views,
median 5.0%, bottom decile 0.89%. Re-derive it for your niche with
`carousel_leaderboard.py` (`calibration` in the output) before trusting it.

## Deliverable template

```
# <niche> carousel benchmark — <date>
## Who actually wins (organic)
- @handle — median X, best Y, save Z%, like-rate W%, cadence N/wk — why it works
## Formats to copy (with the best example each)
## Bought numbers — do not benchmark against
## Targets for our account
## Method + limits (queries used, profiles scanned, cost, what's unverified)
```

## Shared tools

| Step | Tool | Use |
|---|---|---|
| 2, 3, 5 | `carousel_scan.py` | Apify Top search / profile scans / single posts with slide download; marks `is_slideshow` |
| 4 | `carousel_leaderboard.py` ⭐ | offline: per-account medians, save/like-rate, boost flag, cadence, top posts, markdown table |
| 3 | `account_stats.py`, `engagement.py` | the generic video analytics if you want pinned-excluded medians or freshness on the same data |
| 2 | `tiktok_account.py` | keyless fallback collector (TikTokApi / yt-dlp) when there is no Apify budget — note it does not flag slideshows |
