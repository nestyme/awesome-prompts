# awesome-prompts

Prompts and agent skills I actually use, with the rules that make them work.

## Prompts

- [Startup Roast → Action Plan](prompts/startup-roast-review.md) — make an AI agent roast your business using your real data (analytics connectors + web search), then turn the roast into 5 blind spots, a bear case, and an action plan with targets and 30-day checkpoints.
- [Meta Ads — Safe Zones & Policy-Proofing](prompts/meta-ads-safe-zones.md) — the rules to bake into every image-gen prompt for Meta paid creatives: top/bottom 10% safe bands, 300×300 thumbnail readability, 1:1→4:5 crop survival, personal-attributes policy reworks (how to keep the idea and lose the flag), and how to ship screenshot-style ads without "deceptive UI" strikes.

## Skills

- [Trendwatch](skills/trendwatch/SKILL.md) — a self-bootstrapping agent skill for organic TikTok/Reels growth: mines competitor accounts (including shadow accounts and partnered influencers), decomposes viral videos on 7 axes (thumb-stop ≠ hook), filters out celebrity-tier placements that don't transfer, generates adapted hook ideas mapped to your production stack, and compounds learnings in an experiments log — winners get variant-iterated (message locked, creator/setting varied), losers get killed fast. Drop the folder into your agent's skills directory; on first run it interviews you for 5 strategic questions and auto-discovers the rest.
- [Viral Content Factory](skills/viral-content-factory/SKILL.md) — end-to-end generation of TikTok/IG carousels and mannequin outfit-change videos with AI characters: character archetypes that work (unlikely expert, age-defying, pet judge), Gemini prompt templates with anti-artifact constraints, the anchor-first technique for consistent backgrounds across frames, Kling 3 animation via fal.ai, and a 50+ entry viral hook library organized by mechanic (bait & switch, revenge energy, transformation, save-worthy).
- [Carousel Conveyor](skills/carousel-conveyor/SKILL.md) — the production half of the content system (trendwatch decides WHAT, this produces and schedules it): stand up a recurring AI persona for ~$0.60, then output unlimited carousels at $0. Key ideas: one locked reference selfie → ~6 cover photos (never edit an edit — one hop only), all text composited in PIL not generated, the battle-tested UGC-realism prompt block that kills the "AI gloss" (amateur camera artifacts + unretouched skin + hard negative clause), and a mandatory human gate before anything auto-schedules.
