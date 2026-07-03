---
name: trendwatch
description: Reverse-engineer viral organic TikTok/Instagram content from competitor accounts and generate adapted hook ideas for the user's app. Trigger when the user asks about trendwatching, viral content analysis, hook ideation for organic TikTok/Reels growth, "what's working on TikTok for {category}", or wants to analyze a competitor's content strategy. Self-bootstrapping — on first run asks 5 discovery questions and creates state files next to itself; on subsequent runs reads existing state and skips bootstrap.
---

# Trendwatch

A pipeline for organic TikTok/Instagram growth: discover what's working for competitors, decompose why it's working on 7 axes, generate adapted hook ideas for the user's product, and accumulate learnings over time so the skill gets sharper with use.

## Shared tools

Prefer the repo's [`tools/`](../../tools/README.md) CLIs over hand-writing collection/analytics code — they emit a uniform JSON envelope and chain together. Relevant here:

| Step | Tool | Use |
|---|---|---|
| 3 | `trending_sounds.py` | Creative Center trending sounds/hashtags by region + window |
| 4 | `tiktok_account.py` | Collect an account's videos + stats + comments (TikTokApi → yt-dlp fallback) |
| 4 | `video_metadata.py` | Fallback collector for a manual URL list when scrapers are blocked |
| 4-5 | `account_stats.py` | Account median / cadence / outliers / paid-amp + shadow signals / size bucket |
| 4-5 | `engagement.py` ⭐ | Per-video engagement_score, save_rate, ratios, freshness, format-vs-creator-vs-paid attribution |
| 5 | `decompose_video.py` | Keyframes + thumb-stop frame + transcript for the 7-axis decomposition |

Canonical chain: `tiktok_account.py` → `account_stats.py` (get median/signals) → `engagement.py --account-median <M> --top 10` (rank ideation-eligible videos). Full map + flags in [`tools/README.md`](../../tools/README.md).

## Operating principles

1. **Auto-discover before asking — always.** Exhaust tools first: WebSearch (URLs, handles, news), WebFetch (App Store pages, landing pages, competitor profiles), Read/grep (codebase, analytics events, memory files). Ask the user ONLY for: *strategic decisions* (goals, KPIs, where to send traffic), *subjective preferences* (voice, what they value), *operational facts not in any system* (budget, who shoots content), or *validation* of hypotheses already drafted. Never ask for URLs, handles, copy, geo, or anything tools can return. The user's turn is for judgment, not lookup.
2. **Likes lie.** Optimize for completion / save / share signals over raw likes. When completion isn't public, use the proxy formula in Step 4.
3. **Hooks live inside formats.** Always tag a video with its format (POV / GRWM / transition / voiceover-B-roll / etc.) — the same hook fails in the wrong format.
4. **The first 1.5 seconds is not the hook.** Thumb-stop and hook are separate mechanics. Decompose them separately.
5. **Comments are ground truth for copy.** The top comments on a competitor's viral video reveal the audience's actual language and pain — mine them.
6. **`experiments.md` is the compounding asset.** Always read it before ideation. Always offer to update it after the user posts.
7. **Iterate on winners; kill losers fast.** A video that breaks ~1000 views on a cold/new account passed the algo's first gate — that's the signal to *lock the message and vary the variables* (creator look, setting, aesthetic, pace). New ideation is for cold start; variant generation is for proven winners. Most wins after the first winner come from iteration, not from new bets.
8. **Hunt for shadow accounts AND partnered influencers — both produce the non-official product placements that drive real reach.** Well-funded competitors use two parallel mechanisms: (a) shadow alts (unofficial accounts run by the brand itself, disguised as UGC), and (b) partnered influencers (paid independent creators producing branded posts). Both routinely outperform the official account organically; both are the real benchmarks. Detect signals: app-UI watermarks visible in screen recordings, bio links to the competitor's site, identical posting cadence with the official account (shadow signature), `#ad`/`#sponsored`/`#partnership` disclosure (partnership signature), "thanks @brand" mentions, content posted within hours of an official launch, repeated official-marketing phrasings. Track both types in `competitors/{handle}.md` with `type: shadow_of_{X}` or `type: partner_of_{X}` tags. The classification matters for understanding the competitor's budget but **not for format-mining** — both buckets produce equally analyzable product-placement creative.
9. **Recency matters — fresh trumps famous.** A sound or format that peaked 6 months ago is now algorithmically suppressed and audience-tired. Always capture `posted_date` and `age_days` for every analyzed video. Tag freshness: `rising` (<14d) / `peak` (14-30d) / `declining` (30-60d) / `evergreen-structure-only` (>60d). For **sound recommendations**: only use videos in `rising` or `peak`. For **hook/format pattern mining**: extend to 60 days. Videos >60d are useful for evergreen structural patterns (e.g. specific-pain hook framing) but never for "use this exact sound" or "copy this exact creative" advice.
10. **Separate format wins from creator-equity wins and paid-amplification wins.** A 500k-view video on a 2M-follower creator is not proof the format works — it's proof the creator is popular. Same for posts boosted via TikTok Spark Ads / paid partnerships. Compute for every video:
    - **`engagement_ratio = views / follower_count`** (normalized reach) — videos above 0.5× this baseline mean format added value; below 0.1× means creator carried it
    - **`vs_account_median = views / account_median_views`** — videos at >2× median = format-attributable; videos near median = creator-baseline-attributable
    - **Paid-amp signal flags**: sudden spike on an otherwise mid account; `#ad`/`#sponsored`/`#partnership` disclosure; "thanks @brand" mention without organic framing; suspiciously polished editing for the creator's baseline quality; business-account "Promote" badge in profile; viewer-comments pattern matching "is this an ad?"

    When ranking patterns for ideation, **weight only format-attributable wins**. A 50k-view post on a 5k-follower account is far more transferable than a 500k-view post on a 2M-follower account. Tag each analyzed video: `format-attributable` / `creator-attributable` / `paid-amp-suspected` — and pull ideation patterns only from the first bucket.
11. **Compound universal learnings into the playbook.** At the end of every run, ask: "did we learn something that holds across verticals, not just this product?" If yes, append it to the **Tactical playbook** section of this SKILL.md as a new sub-section. Product-specific or vertical-specific learnings stay in `brief.md` and `experiments.md`. The skill compounds in value only if cross-vertical patterns get written down. When in doubt about scope, ask: _"would a SaaS founder, a fitness app, and a fashion brand all benefit from this rule?"_ If yes → playbook. If no → brief/experiments.
12. **Filter for product-placement videos from SMALL-TO-MID accounts only — drop celebrity-tier placements entirely.** What we want for format-mining is: (a) the post is an **explicit product placement** (brand mentioned, UI visible, hashtag, or "thanks @brand"), AND (b) the posting account is **<500k followers**, ideally 10k–250k.

    **Why both filters matter:**
    - Without filter (a) — the placement filter — we end up analyzing a creator's general content, which teaches us about the creator's reach, not the competitor's strategy.
    - Without filter (b) — the size filter — we end up analyzing celebrity placements, which are *reach-buys* with intentionally muted formats (see playbook section "Celebrity-partnership placements rarely transfer"). The metric we'd copy reflects the celebrity's audience pipeline, not the format's lift.

    **Account-size buckets and how to treat each:**
    - **<10k followers**: too small for reliable signal — interesting only if engagement is extreme (>100× baseline)
    - **10k–250k followers**: **PRIME** for format-mining placements — formats here have to do real work
    - **250k–500k followers**: still useful, but normalize by `engagement_ratio` (per principle 10) before treating as format-attributable
    - **500k–1M followers**: gray zone — accept only if the placement post sits clearly *above* the creator's baseline
    - **>1M followers**: **DROP** placements during collection. Celebrity reach dominates; format signal is noise. Their general content may still be a sound-trend reference but never a competitor-strategy reference.

    Detection signals for placement: (a) brand hashtag mention, (b) brand name in caption/title, (c) product UI visible in screen recording, (d) "thanks @brand" disclosure, (e) `#ad`/`#sponsored`/`#partnership` tag, (f) link/handle to product in bio overlay. Tag each video `product-placement-for-{competitor}` or `creator-general-content`, AND tag the source account with its follower bucket. Only count placements from <500k accounts when mining patterns. Celebrity-tier placements may be noted but never pulled into the ideation source set.

## Tactical playbook (universal patterns observed across runs)

These are tactical observations that hold across verticals — apply on every pass. Whenever a run produces a new transferable lesson, add it here so future runs inherit it.

### Diagnostic order when a post underperforms

When a post fails to break the ~1000-view algo gate, diagnose in this priority — the first item is the most common cause:
1. **Thumb-stop visual (0–1.5s)** — was the first frame actually scroll-stopping? Most "bad" posts have a fine hook but an unremarkable first frame.
2. **Sound lifecycle** — was the sound `rising/peak` per principle 9? A stale sound auto-suppresses regardless of content quality.
3. **Format-niche mismatch** — does the format match what the algo has pegged the account for? Cold accounts have no niche yet; the first 3-5 posts define it.
4. **Caption hook copy** — was there a verbal hook in the first sentence, or hashtag-soup? Hashtags belong at the end; hooks belong first.
5. **Account cold-start** — if 1-4 check out and views still ≤500, the account just needs more posts; algo-trust accumulates over 3-10 posts within a niche.

### Cold-start mechanics

- A brand-new account spends each post in a ~200-500 view algo test bucket
- Need **3 posts breaking 1000+ views** to teach the algo the account's niche before the iteration ladder kicks in productively
- Until then: short formats (5-15s) get more chances per algo-dollar (lower per-test cost for the platform)
- After the first 1000+ win: shift mix toward longer-format winners and run variant generation per principle 7

### Save rate is the conversion leading indicator (utility/tool products)

For utility, SaaS, or tool products (apps that DO something), the leading conversion predictor is **save rate**, not likes or views.
- `save_rate = saves / views`
- **>5%** → predicts strong purchase conversion
- **2-5%** → mid; tweak CTA before scaling
- **<1%** → predicts no conversion regardless of view count — format works for awareness, not purchase

Likes correlate with entertainment value; saves correlate with intent. For utility content, optimize save rate, not like rate. (Does not apply to entertainment/lifestyle content — there, shares and follows matter more.)

### Anchor vs variant content split

Two content types do different jobs — don't mix strategies on the same post:

- **Anchor posts** (founder narrative, brand origin, deep how-it-works): DO NOT variant-iterate. Re-record only if dead. Post 1-2 per quarter as account-trust pillars. Founder voice = trust premium that compounds slowly.
- **Variant-friendly posts** (trend-jacks, transformations, aesthetic listicles, "I tried X for a week"): designed to spawn 5-8 variants on first win. The main iteration ladder.

Trying to variant-iterate a founder narrative burns trust without compounding reach.

### CTA mechanics on no-clickable-link platforms (TikTok, IG Reels)

When the platform doesn't support clickable links in the video:
- The brand name must be (a) easy to spell, (b) recall-friendly, (c) mentioned **2× per video** — once in voiceover, once as on-screen end-card text
- **"Link in bio" is the worst possible CTA** — doesn't work on TikTok (no clickable bio link for most accounts) and signals desperation
- A brand-name CTA framed as a utility instruction (`"[brand] · [verb] · [outcome]"`) outperforms an explicit "go download" by roughly 2-3×

### Specific-pain hooks unlock niche-audience virality

Hooks naming a **specific** condition, pain, or behavioral pattern (rather than generic pain) get pushed harder by the algo's niche-recommendation engine. Examples: ADHD/OCD for organization, neurodivergent traits, body-shape specifics, regional habits, age-cohort behaviors.

- Trade-off: niche-pain hooks deliver fewer total views but **higher save rates** (audience self-selects in)
- Use when the account needs save-rate / conversion improvement, not when chasing top-of-funnel reach
- Canonical structure: _"We made [product] for [generic-X], but didn't expect how much it helps people with [specific-pain]"_

### Anti-X framing for substitute products

For any product that REPLACES a habit, "anti-X" framing converts harder than "use X" framing:
- Anti-haul for shopping-replacement tools ("things I stopped buying since I started using...")
- Anti-procrastination for productivity tools
- Anti-meal-prep for cooking-shortcut tools

The mechanic is recommendation-shaped, not pitch-shaped — viewer feels they're getting tips, not sold to. High save rate, KPI-aligned for conversion.

### Listicle anti-pitch

Multi-app or multi-tool listicles ("Top N apps every [persona] needs to [aspirational verb]") work as soft conversion vectors when your product is one of N:
- Lower direct-pressure than single-app pitches → higher save rate
- Risk: your product gets buried — place at position 1 or 5 (start/end primacy effects)
- Always pair with 3-4 genuinely non-competing apps so the recommendation reads authentic
- Best for awareness-stage accounts needing to be seen alongside trusted-app references

### Survey the production stack before ideation

Before generating ideas, audit what tools the product actually has for video production (Higgsfield, CapCut, Sora, real filming, UGC creators, etc.). Constraints of production tools shape what's producible — an idea that requires a 30-person crew is useless to a solo founder with Higgsfield.

- For each major production tool, list its presets / templates / common output formats
- Map each ideated format back to one or more production-tool presets
- If a format has no producible path, demote or rework it
- Document the production stack in a `production-stack.md` file alongside `brief.md`; refresh whenever tools change
- **AI-character/spokesperson note**: for products whose founder doesn't want to film, an AI Influencer with a locked Master reference image gives the trust premium of a recurring face WITHOUT requiring founder time. This converts founder-narrative content from "anchor only, no variants" to fully variant-friendly.

### Celebrity-partnership placements rarely transfer as format templates

When a celebrity creator partners with a brand, the resulting placement videos almost always **underperform the creator's own organic baseline** because:
- The creator uses the lowest-energy format possible for paid content (voiceover-talk-about-app, static product shot, simple launch-announcement)
- Their viral formats (Met Gala emoji + trending sound) are reserved for their non-paid content where they actually want to win
- Brand reach is bought via the audience pipeline, not via format quality

So when mining a celebrity-product-placement video for ideation:
- Treat it as **proof of reach buy**, not proof of format quality
- The actual replicable format is what the creator does for THEIR audience, not what they do for brand partners
- Save rate on placement videos is often <1% (low conversion intent because audience came for the creator, not the product)
- Small-account replications of celebrity-placement formats will fail twice: (a) no audience pipeline to ride, (b) the format itself is intentionally muted

**Diagnostic question**: does the engagement_ratio of the placement post sit ABOVE or BELOW the creator's own baseline? If below, the placement is reach-buy + format-muted. If above (rare), the format actually added value and is worth studying.

### Locked identity vs varied-within-aesthetic (AI-character production)

When generating AI characters for content, two production modes are available:
- **Locked identity** (e.g. Higgsfield Soul Character training, locked Master reference) — same face across every video. Requires 5-20 reference photos + training time (~10 min).
- **Varied-within-aesthetic** — one-off generation per video using a single reference as style guide. Different face each time, but same aesthetic cluster (downtown girl / streetwear / clean girl / etc.).

**Default: varied-within-aesthetic.** It's faster, cheaper, and natively achieves principle 7 (variant generation = vary creator look). Locking identity actively works against variants — you'd burn your variant axis on settings/aesthetic when creator look is the highest-leverage axis.

**Lock identity only when**:
- Founder-narrative anchor content where audience must recognize a recurring face for trust accumulation
- Brand-mascot continuity where character IS the brand (long-running serial)
- The product literally is "this person's style"

For everything else — variant content, trend-jacks, transformations, anti-haul, listicles — the variation across videos is the asset, not the liability.

### Scale-vs-strategy diagnosis (same vs-median ratio across account sizes)

When a small account's best post sits at the same multiplier above its own median (e.g. 1.6×) as a much larger transferable-pattern competitor's best hit, the format and message are already working. The remaining gap is **scale** (algo test bucket size), not strategy.

- Don't change the message — iterate it in variant formats until one breaks the 1000-view algo gate, then variant-spam per principle 7
- This pattern generalizes: "same vs-median ratio = same format quality, regardless of absolute view count"
- Diagnostic question to apply on any small-account post: "what's our vs-median ratio? if it's already 1.5-2× and matches a known winner's ratio, we have a scale problem, not a creative problem"

## Pipeline

```
1. Bootstrap       → check state files, decide first-run vs subsequent
2. Discovery       → first run only: 5 critical questions (rest from local context)
3. Auto-research   → App Store, Creative Center, WebSearch (in parallel)
4. Collection      → competitor video data (TikTokApi / instaloader / yt-dlp fallback)
5. Analysis        → decompose top videos on 7 axes
6. Ideation        → 10 adapted hooks, ranked by impact × ease
7. Outputs         → dated trend report + ideas; offer to update experiments.md
```

## State files (created alongside this SKILL.md)

```
trendwatch/
├── SKILL.md              # this file — generic, shareable
├── brief.md              # product brief — written on first run
├── production-stack.md   # what tools we use (Higgsfield/CapCut/etc) + preset → idea mapping
├── current-plan.md       # LIVING action checklist — what to post next + decision tree
├── mascots/              # curated library of AI-character references for recurring on-screen faces
│   ├── README.md         # index + selection criteria + workflow
│   └── {NN-slug}/        # one folder per mascot (reference.jpg, description.md, master.png)
├── screencasts/          # source clips of the product UI — B-roll for demo cuts in generated videos
│   ├── README.md         # index + recommended clips + naming conventions
│   └── {NN-action}.mov   # one clip per action (gallery upload, outfit gen, try-on, etc.)
├── competitors/
│   └── {handle}.md       # one per tracked account, refreshed each run
├── trends/
│   └── YYYY-MM-DD.md     # dated trend report (historical snapshot)
├── ideas/
│   └── YYYY-MM-DD.md     # dated ideation output (historical snapshot)
└── experiments.md        # accumulating log: tested → metrics → learnings (history)
```

**Two-axis split between historical and living state:**
- **Historical (dated, append-only)**: `trends/YYYY-MM-DD.md`, `ideas/YYYY-MM-DD.md`, `experiments.md`. Snapshots of what we knew/decided at a point in time. Never edited after a date passes.
- **Living (single-file, kept current)**: `brief.md`, `production-stack.md`, `current-plan.md`. Reflect current state of truth; refreshed whenever a relevant fact changes.

**`current-plan.md` is the action document.** It tells the user (and future-you in the next session) what to actually do *right now*. Contains: status + next action + this-week's posting plan with reference video URLs + decision tree (what to do based on each test result) + pre-flight checklist + update log. Updated after every posted experiment.

## Step 1 — Bootstrap

Check if `brief.md` exists in this skill directory.

- **Exists** → subsequent run. Read it. Ask: _"Last brief is from {date}. Anything changed about product, target, or competitors? ('all good' / details)"_. Skip to Step 3.
- **Missing** → first run. Go to Step 2.

Also check `experiments.md` — if it exists, read it before any ideation so prior learnings are applied.

## Step 2 — Discovery (first run only)

**Auto-discovery runs FIRST, in parallel.** Only after exhausting these tools do you ask the user anything.

**Parallel auto-discovery batch:**
- Read `CLAUDE.md` + memory index (`MEMORY.md`) + every referenced memory file
- WebSearch `"{product name}" app store ios` → App Store URL
- WebSearch `"{product name}" tiktok` and `"{product name}" instagram` → official handles
- WebFetch the App Store page → description, features, screenshot subjects, recent reviews (positioning + voice signals)
- WebFetch the landing page → hero copy, brand voice, primary CTA
- For each competitor in memory: WebSearch `"{competitor name}" tiktok` → official handle, follower count, recent post snapshot
- **Shadow-account hunt** (per principle 8): for each competitor, also search `"using {app name}" tiktok creator`, `"{app name} review" tiktok`, `"how to use {app name}"` → surface accounts demonstrating the app. Most are real UGC, some are shadows; cross-reference for signals (watermarks of app UI, bio links to competitor site, posting cadence overlap with official). Flag suspected shadows for separate tracking.
- WebSearch `"{vertical} app TikTok viral {year}"` → unknown viral accounts to flag for the user
- Grep the codebase for analytics event names + onboarding flow → draft 2-3 aha-moment hypotheses

Pre-fill `brief.md` with everything found.

**Then ask the user ONLY for what cannot be discovered:**

**Strategic (must ask):**
1. **Primary acquisition goal right now** — installs / sign-ups / followers / brand awareness
2. **KPI that defines "viral"** — completion / saves / shares / installs
3. **Where to send TikTok traffic** — App Store, web/quiz, or both (affects video CTA)
4. **Content production model** — founder-led / UGC creators / agency

**Validation (confirm hypotheses drafted from auto-discovery):**
5. **Aha moment** — present 2-3 hypotheses drafted from analytics events / onboarding; user picks or refines
6. **Unique angle vs competitors** — present a draft from App Store + memory; user edits in their voice
7. **Brand voice** — present what was parsed from landing + screens; user confirms or overrides
8. **Competitor TikTok handles for analysis** — present auto-found list; user adds/removes

**Soft (smart defaults — user can override later in brief.md):**
- Geo priority (default: from App Store availability)
- Winner thresholds (default: 1000 views cold / above median established)
- Posting cadence (default: 3/week per platform)
- Hard constraints (default: collegial with competitors, no AI-gen explicit; pull from memory)

Write all answers + auto-discovered data into `brief.md` using the template at the bottom.

## Step 3 — Auto-research (run in parallel)

Spawn parallel subagents (or run in parallel tool calls):

**A. Parse the App Store URL** (`WebFetch`) → description, screenshot subjects, top recent reviews → key positioning signals. Cache to `brief.md` under "Auto-discovered".

**B. TikTok Creative Center** (`WebFetch` of `creativecenter.tiktok.com`) → currently trending sounds + hashtags in the product's vertical. Note lifecycle stage (rising / peak / declining) when visible.

**C. Web search supplemental** (`WebSearch`) → `"{vertical} app TikTok viral {current year}"`, `"best {vertical} creators TikTok"`. Cross-reference against the user's handle list; flag handles they missed.

## Step 4 — Collection

For each competitor in `brief.md`:

**Primary tool — TikTokApi (Python, free):**
```python
# uses davidteather/TikTok-Api — install: pip install TikTokApi && playwright install
from TikTokApi import TikTokApi
import asyncio, json

async def pull(handle, count=30):
    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1, sleep_after=3)
        user = api.user(username=handle)
        videos = [v.as_dict async for v in user.videos(count=count)]
        return videos
```

Pull 20-30 top videos per handle. Required fields per video:
- `id`, `desc` (caption), `createTime`
- `stats.playCount`, `diggCount`, `commentCount`, `shareCount`
- `video.duration`
- `music.id`, `music.title`, `music.authorName`
- Top 20 comments (text + likeCount) — separately via the comments endpoint

**Also capture per-account context (per principle 10):**
- `follower_count` — for normalizing reach (engagement_ratio)
- `account_median_views` — for computing per-video `vs_account_median` ratio
- Bio text + recent post history → check for paid-amp signals (#ad disclosures, brand mentions, Promote badge)

**Filter for product placement + account-size band (per principle 12):**

This is a **two-gate filter applied during collection** — both gates must pass for a video to enter the ideation source set:

**Gate 1 — Placement keyword filter:**
- For each non-official creator account, define the target product's keywords (e.g. `["{brand}", "{brand}app", "{brand}daily", "{category-term}"]`)
- Filter pulled videos: keep only those whose title/description/hashtags match the keywords
- If a creator has <2 placement videos in the last 30 days, **drop the account from competitor analysis** — they're not actively partnered/relevant for this brand

**Gate 2 — Account-size filter:**
- Before pulling video data for any partnered creator, fetch their follower count (`yt-dlp --dump-single-json` on user URL, or WebSearch `"@handle" tiktok followers`, or stat-mirror sites like Social Blade)
- **Drop the account from collection if follower_count > 500k**, regardless of how many placements they have
- These celebrity-tier placements are reach-buys with muted formats — they do not transfer (see Tactical playbook: "Celebrity-partnership placements rarely transfer as format templates")
- Note dropped accounts in a `dropped-accounts.md` with reason, so we don't re-spend the cost on them next pass

**Targeted search for missing placements:**
- For creators with high general-content engagement (e.g. 500k+ followers, dropped per Gate 2): targeted web search `"@handle" "{brand}"` can surface their specific placements as **negative-reference examples** (what celebrity placements look like) — useful for the playbook, not for ideation
- For creators in the 10k–500k sweet spot: if the random latest-N pull surfaces 0 placements, run `"@handle" "{brand}" tiktok` web search before dropping the account; placement may exist but not in latest-N

**Instagram Reels — instaloader (Python, free):**
```python
import instaloader
L = instaloader.Instaloader()
profile = instaloader.Profile.from_username(L.context, handle)
reels = [p for p in profile.get_posts() if p.is_video][:30]
```

**Fallback when scrapers break or are blocked** → ask the user for a manual URL list. For each URL, run `yt-dlp --dump-json {url}` to extract metadata. Slower, but always works.

**"Most rewatched" proxy** (since completion rate is not public):
- `engagement_score = (likes + 2*comments + 3*saves + 5*shares) / views`
- Flag outliers: videos with views > 5× the account's median
- Long videos (>30s) with high views + high engagement → almost certainly high completion

**Recency filter (per principle 9):**
- Always capture `posted_date` (from createTime → ISO) and compute `age_days`
- When ranking "top videos", sort by **`engagement_score × recency_weight`** where `recency_weight = max(0.1, 1 - age_days/60)`
- Drop videos older than 60 days from sound/format recommendations; keep only as "evergreen structure reference" if hook framing is exceptional
- For trend reports, hard-filter to last 30 days unless explicitly mining evergreen patterns

Write raw collected data per account to `competitors/{handle}.md`, with a column for `age_days` and a `freshness` tag (`rising` / `peak` / `declining` / `evergreen-structure-only`).

## Step 5 — Analysis

For each competitor, pick the top 5-10 videos by the engagement proxy. Decompose each on 7 axes. If you have many videos, spawn parallel subagents (one per video or one per competitor).

| Axis | What to extract |
|---|---|
| **Thumb-stop (0–1.5s)** | Literally what's on screen + audio in the first 1.5 seconds. This stops the scroll. Often a face, a transformation reveal, a bold text overlay, or a sound spike. |
| **Hook (0–5s)** | The verbal/visual promise that earns the next 10 seconds. Usually a question, a contrast, a "wait for it", or a specific outcome. |
| **Format** | POV / GRWM / transition / voiceover-over-B-roll / static-text-on-screen / talking head / split-screen / before-after / haul / tutorial |
| **Message** | One sentence: what is the video promising the viewer will get? |
| **Sound** | `sound_id` + name + lifecycle stage (rising / peak / declining). Trending audio amplifies reach 2–3×. |
| **CTA** | Implicit (curiosity → profile click) or explicit (download / save / comment X / link in bio) |
| **Comments** | Top 5 comments by likes → what audience pain / language / desire do they reveal? This is gold for copy. |

Write decomposition per video into the relevant `competitors/{handle}.md`.

After all competitors are analyzed, synthesize a **trend report** at `trends/YYYY-MM-DD.md`:
- Top 5 thumb-stop patterns currently winning in the vertical
- Top 5 hook formulas (with template form, e.g. "POV: you {X} but {twist}")
- Top 3 formats over-indexing
- Top 5 trending sounds with lifecycle stage and example videos using them
- Audience pain points / recurring language from comments

## Step 6 — Ideation

Read `experiments.md` first. Skip patterns the user already tested and that didn't work. Bias toward patterns adjacent to ones that did work.

Generate 10 hook ideas adapted to the user's product. Each idea:

```
### Idea {N} — {short name}

- **Source pattern** — which competitor video / why it worked
- **Reference videos** — REQUIRED. 1-3 direct TikTok/Reels URLs from the collected data (or web-search results) that are the closest pattern. Format: `[@handle/video/ID](URL) — why this video is the source (hook / sound / format / vibe)`. Without reference URLs, the production team (or the user) can't actually watch and replicate. If no good reference exists, write `Reference videos: NONE — generic pattern from playbook; higher production risk`.
- **Thumb-stop (0–1.5s)** — what's on screen + audio
- **Hook (0–5s)** — exact verbal/visual line
- **Format** — POV / GRWM / transition / etc.
- **Aha-moment integration** — at which second the product's value lands
- **CTA** — implicit or explicit
- **Sound** — must be from a video currently `rising` (<14d) or `peak` (14-30d). Never recycle a sound from `declining` or older. If no fresh sound matches, write _"trending sound TBD — check Creative Center day-of-posting"_ rather than suggesting a stale one.
- **Production difficulty** — UGC-friendly / requires editing / requires product demo
- **Hypothesized impact** — high/med/low + one-line reason
- **Test variants** — 2–3 A/B angles if this one performs
```

Rank by `impact × (1 / production_difficulty)`. Write to `ideas/YYYY-MM-DD.md` under section `## Fresh ideation — YYYY-MM-DD`.

### Mode B — Variant generation (iterating a winner)

**Triggered when:**
- User says "iterate on Idea-N" / "this got {views} views, what next?"
- OR Step 7 detected a logged winner above threshold and asked "iterate now?"

**Lock these — do not vary (these are the proven elements):**
- Hook line (verbatim wording)
- Format (POV / GRWM / transition / etc.)
- Message / promise
- CTA
- Sound type (same specific sound if still rising; same *kind* of sound if original is stale)

**Vary one axis per variant (or combine two for higher-leverage tests):**
- **Creator look** — ethnicity, age, body type, hair, personal style. _Highest-leverage axis_ — unlocks new audience pockets.
- **Setting** — bedroom / dorm / hotel / car / city street / outdoor / studio / café
- **Aesthetic cluster** (vertical-dependent; for fashion: clean-girl / downtown / preppy / streetwear / cottagecore / old-money / Y2K)
- **Energy / tone** — chill / hype / deadpan / sweet / sarcastic
- **Pace** — slow build / quick cuts / single take
- **Lighting / time of day** — natural morning / golden hour / fluorescent / blue-hour

Generate **5–8 variants**. Each variant:

```
### {Parent}-v{A/B/C} — {variant name}

- **Parent**: Idea-{N} from {date}, hit {metric} on {account state}
- **Locked** (verbatim from parent): hook, format, message, CTA
- **Varied axis**: creator look → {description} ; (and/or) setting → {description}
- **Production note**: same shot list as parent; only swap {creator/location/etc.}
- **Hypothesis**: which new audience segment this variant should unlock
```

Write to `ideas/YYYY-MM-DD.md` under section `## Variants of Idea-{N} — YYYY-MM-DD`, with a link/reference to the parent experiment in `experiments.md`.

**Also update `current-plan.md`** — the living plan must reflect the new variants as the next-action queue, with reference URLs and pre-flight checks. The dated `ideas/` file is the full catalog; `current-plan.md` is the curated action list.

## Step 7 — Update experiments.md

At end of run, prompt: _"When you've posted any of these, run trendwatch with 'log experiment' and I'll record metrics + learnings."_

Log format:
```
## YYYY-MM-DD — {idea name}
- Source pattern (from trend report / idea ref):
- Hook used:
- Format:
- Platform: TikTok / Reels / both
- Metrics: views {X} / completion {Y%} / saves {Z} / shares {W} / installs attributed {N}
- Verdict: SCALE / ITERATE / KILL
- Learning: one sentence
```

This file makes the skill smarter over time. Treat it as the most important state file.

**Winner detection & auto-iteration trigger:**

After logging, compare metrics against thresholds in `brief.md`:
- Cold/new account (<5k followers, <30 posts): **1000+ views** = winner signal (default; user can override in brief)
- Established account: **above account's median view count** = winner signal

If above threshold:
- Tag the experiment `Verdict: SCALE` and `Winner: yes`
- Prompt: _"This passed the algo's first gate ({views} views on {account state}). Iterate now? I'll generate 5–8 variants holding the message constant and varying creator / setting / aesthetic. (y/n)"_
- On `yes` → run Step 6 Mode B with this experiment as parent

_Why 1000 on a cold account matters:_ TikTok's algo gives every video an initial test bucket (~200–500 views). Escaping that bucket on an account with no signal history means the format-message combo resonated with strangers. That is the moment to compound — same message, different faces and settings — before the trend cools or the audience saturates.

## Invocation modes

- **Full run** (default) — "trendwatch" / "find viral hooks for me" → all 7 steps
- **Trends only** — "what's trending in {vertical}" → Steps 3 + 5 (skip collection of competitor-specific data)
- **Ideas from existing data** — "give me 10 new hooks" → Steps 5 + 6 from most recent collection
- **Log experiment** — "log experiment {name}" → Step 7 only
- **Iterate winner** — "iterate on {idea}" / "this got {views} views, what's next" → Step 6 Mode B (variant generation, message locked)

## Failure modes & fallbacks

| Failure | Fallback |
|---|---|
| TikTokApi blocked / broken (TikTok updated their site) | Manual URL list from user → `yt-dlp --dump-json` per URL |
| Instagram rate-limit / blocked | Manual Reel URLs → `yt-dlp` |
| Sound data missing | Analyze visual + hook only; flag sound as "unknown" |
| `experiments.md` empty (first ever run) | Skip historical filtering in Step 6 |
| User skipped soft questions in Step 2 | Smart defaults: geo = global, voice = inferred from App Store screens, KPI = installs |

---

## Templates

### `brief.md`

```markdown
# Product Brief — {Product Name}

_Last updated: YYYY-MM-DD_

## Product
- **One-liner**:
- **App Store / URL**:
- **Vertical**:
- **Aha moment**:
- **Unique angle vs competitors**:

## Audience
- **Target persona**:
- **Geo priority**:
- **Super-user signal** (high-retention behavior):

## Competitors tracked
- @handle1 — direct / adjacent / aspirational — why
- @handle2 — ...

## Brand
- **Voice (one word)**:
- **Reference account**:
- **Hard constraints**:
- **Content production**: founder-led / UGC / agency
- **KPI for "viral"**:

## Cadence target
- N videos/week on {platform(s)}

## Winner thresholds (when to iterate vs kill)
- **Cold/new account** (<5k followers, <30 posts): {N} views = winner (default 1000)
- **Established account**: above account's own median views = winner
- **Platform-specific overrides**: TikTok {N} / Reels {N} (set if signal differs)
- _A winner triggers Step 6 Mode B (variant generation) on the next run, not new ideation._

## Auto-discovered (filled by skill in Step 3)
- Key product features (from App Store):
- Top review themes:
- Additional viral handles found via WebSearch:
- Current trending sounds in vertical (Creative Center):
```

### `competitors/{handle}.md`

```markdown
# @{handle}

_Last updated: YYYY-MM-DD_

- **Followers**:
- **Median views / top video views**:
- **Posting cadence**:
- **Niche signature**:

## Top videos (last 30 pulled, sorted by engagement score)

| Date | URL | Views | Engagement % | Duration | Sound | Format | Hook (truncated) |
|---|---|---|---|---|---|---|---|

## Decomposed top videos

### {video URL}
- **Thumb-stop (0–1.5s)**:
- **Hook (0–5s)**:
- **Format**:
- **Message**:
- **Sound** (id + lifecycle):
- **CTA**:
- **Top comment themes**:
- **Why it worked** (one line):
```

### `experiments.md`

```markdown
# Experiments log

_Append-only. Most recent at top._

## YYYY-MM-DD — {idea name} `Idea-{N}` (or `Idea-{N}-v{A}` if variant)
- **Parent** (if variant): Idea-{N} from {date}, parent metrics: {views} on {account state}
- **Variant axis** (if variant): {what was changed — e.g. "creator: Latina, 22, dorm setting"}
- **Source pattern**: trends/YYYY-MM-DD.md → Idea N
- **Hook** (verbatim):
- **Format**:
- **Platform**: TikTok / Reels
- **Account state**: cold (<5k, <30 posts) / established / verified
- **Metrics**: views {} / completion {%} / saves {} / shares {} / installs {}
- **Verdict**: SCALE / ITERATE / KILL
- **Winner**: yes / no _(auto-tagged if metrics above threshold in brief.md)_
- **Learning** (one sentence):
```
