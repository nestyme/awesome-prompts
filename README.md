# awesome-prompts

Prompts and agent skills I actually use, with the rules that make them work.

[![Follow @nestymee on X](https://img.shields.io/badge/%40nestymee-more%20of%20this%20%2B%20building%20in%20public-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/nestymee)

## Prompts

- [Startup Roast → Action Plan](prompts/startup-roast-review.md) — make an AI agent roast your business using your real data (analytics connectors + web search), then turn the roast into 5 blind spots, a bear case, and an action plan with targets and 30-day checkpoints.
- [Meta Ads — Safe Zones & Policy-Proofing](prompts/meta-ads-safe-zones.md) — the rules to bake into every image-gen prompt for Meta paid creatives: top/bottom 10% safe bands, 300×300 thumbnail readability, 1:1→4:5 crop survival, personal-attributes policy reworks (how to keep the idea and lose the flag), and how to ship screenshot-style ads without "deceptive UI" strikes.

## Skills

- [Trendwatch](skills/trendwatch/SKILL.md) — a self-bootstrapping agent skill for organic TikTok/Reels growth: mines competitor accounts (including shadow accounts and partnered influencers), decomposes viral videos on 7 axes (thumb-stop ≠ hook), filters out celebrity-tier placements that don't transfer, generates adapted hook ideas mapped to your production stack, and compounds learnings in an experiments log — winners get variant-iterated (message locked, creator/setting varied), losers get killed fast. Drop the folder into your agent's skills directory; on first run it interviews you for 5 strategic questions and auto-discovers the rest.
- [Viral Content Factory](skills/viral-content-factory/SKILL.md) — end-to-end generation of TikTok/IG carousels and mannequin outfit-change videos with AI characters: character archetypes that work (unlikely expert, age-defying, pet judge), Gemini prompt templates with anti-artifact constraints, the anchor-first technique for consistent backgrounds across frames, Kling 3 animation via fal.ai, and a 50+ entry viral hook library organized by mechanic (bait & switch, revenge energy, transformation, save-worthy).
- [Voice Realism](skills/voice-realism/SKILL.md) — voice is the #1 tell that a video is AI-generated; this skill rewrites any video/TTS prompt with spoken lines so the voice survives scrutiny. It bundles every line as emotion + action + dialogue, auto-picks delivery from scene context (whisper is the cheat code — synthesis artifacts vanish in whispered speech), fixes per-model dialogue syntax (Veo colon, Seedance quotes, ElevenLabs audio tags), checks words-per-second against clip length, bakes acoustics and lipsync-friendly framing into the prompt, and outputs a scene-matched post-processing checklist (cut the 2–4 kHz AI ring, 5–10% room reverb, −50 dB noise bed, barely-there voice morphing).
- [Carousel Conveyor](skills/carousel-conveyor/SKILL.md) — the production half of the content system (trendwatch decides WHAT, this produces and schedules it): stand up a recurring AI persona for ~$0.60, then output unlimited carousels at $0. Key ideas: one locked reference selfie → ~6 cover photos (never edit an edit — one hop only), all text composited in PIL not generated, the battle-tested UGC-realism prompt block that kills the "AI gloss" (amateur camera artifacts + unretouched skin + hard negative clause), and a mandatory human gate before anything auto-schedules.

## Tools

Universal, composable CLIs the skills call on demand — collect, analyze, generate, distribute. Every tool is single-purpose, takes JSON/flags, and emits a uniform JSON envelope on stdout, so they chain together (e.g. `tiktok_account.py → account_stats.py → engagement.py`). The offline analytics core (engagement, account-stats) needs no keys or network. Full registry with flags and canonical chains: [`tools/README.md`](tools/README.md).
