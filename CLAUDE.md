# CLAUDE.md — agent guide for this repo

Public collection of prompts, agent **skills**, and a CLI **toolbox** for
short-video growth (TikTok / Reels / Meta) and AI content production. This file
tells an agent how the pieces fit and which to reach for.

## The content system (how the pieces fit)

Three skills form one pipeline — **discover → produce → schedule**:

1. **[trendwatch](skills/trendwatch/SKILL.md)** — decides **WHAT** to post.
   Mines competitor accounts (incl. shadow accounts & partnered influencers),
   decomposes viral videos on 7 axes (thumb-stop ≠ hook), normalizes reach
   (`engagement_ratio`, `vs_account_median`), filters celebrity-tier placements,
   ranks adapted hook ideas, and compounds learnings in `experiments.md`.
   Winners get variant-iterated (message locked, creator/setting varied);
   losers get killed fast.
2. **[carousel-conveyor](skills/carousel-conveyor/SKILL.md)** — **PRODUCES &
   SCHEDULES** photo carousels for a recurring AI persona. One locked reference
   selfie → ~6 covers (never edit an edit), captions composited in PIL at $0,
   mandatory human gate before scheduling (Postiz, AI-disclosure on).
3. **[viral-content-factory](skills/viral-content-factory/SKILL.md)** — carousel
   image sets + mannequin outfit-change videos (Gemini + Kling via fal.ai),
   anchor-first technique for consistent backgrounds, 50+ hook library.

**[voice-realism](skills/voice-realism/SKILL.md)** is a standalone helper any
video-producing step can call: rewrites prompts with spoken lines so the voice
sounds human (auto-picked delivery, per-model dialogue syntax, acoustics,
lipsync framing) + scene-matched audio post-processing checklist.

Prompts in [prompts/](prompts/) are standalone (startup roast, Meta ads
safe-zones).

## Tools ([tools/](tools/README.md))

12 composable Python CLIs the skills call on demand. **Uniform contract**: CLI
flags and/or JSON on stdin → exactly ONE JSON envelope on stdout
(`{"ok", "tool", "data"|"error"}`), logs to stderr, exit 0/1/2. Field aliases
from any collector (TikTokApi / yt-dlp / instaloader) are normalized, so tools
pipe into each other. Full map + canonical chains: [tools/README.md](tools/README.md).

| Stage | Tools |
|---|---|
| Collect | `tiktok_account` (TikTokApi→yt-dlp fallback), `video_metadata` (any URL) |
| Analyze (offline, no keys) | `engagement` ⭐ (score/save-rate/freshness/attribution), `account_stats` (median/cadence/paid-amp signals) |
| Decompose | `decompose_video` (keyframes + thumb-stop + transcript) |
| Trends | `trending_sounds` (Creative Center; falls back to WebFetch) |
| Generate | `gen_image` (Gemini), `gen_video` (Kling/fal.ai), `caption_composite` (PIL, safe margins), `render_video` (Remotion: **hook ≤3s + demo**) |
| Distribute/QA | `safe_zones` (bands/crop/thumbnail), `schedule_post` (Postiz, **--dry-run default**, AI-disclosure on) |

Canonical chain: `tiktok_account` → `account_stats` (median/signals) →
`engagement --account-median M --top 10` (ranked ideation-eligible videos).

**Secrets**: `tools/.env` (gitignored; template `tools/.env.example`),
auto-loaded by `_common.py`; key-name synonyms accepted (`GEMINI_API_KEY` /
`GOOGLE_API_KEY`, `FAL_KEY` / `FAL_AI_API_KEY`, `POSTIZ_API_KEY`).
Setup: `tools/.venv` via `python3 -m venv --system-site-packages` + install
from `tools/requirements.txt` only what a tool asks for.

## Conventions

- **Local vs public**: skill state files (`brief.md`, `experiments.md`,
  `competitors/`, `ideas/`, …) and `workspace/` hold product/business specifics
  — they are **gitignored, never commit them**. Only generic, transferable
  material belongs in the repo (skills, tools, playbook patterns).
- **Prefer tools over ad-hoc scripts** — each skill's "Shared tools" section
  maps its steps to tools. If a tool is missing, add one following the
  `_common.py` pattern and add a row to the tools/README map.
- **Live actions are gated**: `schedule_post` posts only with `--live`;
  carousel-conveyor requires visual review before scheduling; AI-content
  disclosure is always on.
- **Compounding**: cross-vertical lessons go into the trendwatch **Tactical
  playbook** section; product-specific lessons stay in local state files.
