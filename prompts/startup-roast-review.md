# Startup Roast → Action Plan

Ask an AI agent (with access to your analytics via MCP connectors + web search) to roast your business using your **real data**, then turn the roast into an accountable plan. Works best with Claude (Fable 5) connected to RevenueCat / Amplitude / your stack.

---

## The prompt

```
you have access to my connectors via mcp (<your analytics: revenuecat, amplitude, gmail, notion, drive, ...>) and web search. use all of them.

context: i'm the founder of <company> (<url>), <one-line description of what it does>.
i'm too close to my own project to see clearly.

your job: roast my business, then turn the roast into a plan. not my feelings, my business.

## research steps

1. search the web for <company>, our competitors, and the <category> market in <year>
2. dig through my actual data: revenue, retention, funnels, subscriptions, user behavior
3. find the latest "state of subscription apps" report (revenuecat) and pull benchmarks
   for apps launched in the last 18 months in my category
4. read my app store reviews (especially 1-3 stars) and recent competitor reviews.
   what do users complain about that i haven't fixed?
   what do competitor users beg for that nobody ships?
5. cross-reference what i say publicly vs what my numbers actually show

## rules

- every claim must reference a specific number from my data or a cited source
- if you don't have data for something, write "no data" instead of estimating.
  an honest gap is more useful than a confident guess
- no compliments, no hedging, no "however you're doing great"

## deliverables

a) health_check.html — a dashboard comparing my key metrics (trial-to-paid conversion,
   retention curves, arpu, churn, refund rate, mrr growth) side by side with category
   benchmarks for apps launched in the last 18 months. flag every metric below median
   in red. make it screenshot-ready.

b) exactly 5 blind spots: things visible in my data or market position that i'm likely
   not seeing or actively avoiding. each max 2 sentences. if a point doesn't hurt a
   little, replace it with one that does. rank by how expensive ignoring them will be
   in 12 months.

c) my single biggest dependency (channel, platform, geography, feature) and what
   happens to the business if it breaks tomorrow.

d) a 3-sentence bear case: the most plausible story of why <company> is dead in
   24 months, based on my actual numbers, not generic startup risks.

e) the single question i should be able to answer but probably can't.

f) action_plan.md — one action per blind spot, max. each action must name the specific
   metric it moves, the target number, and a 30-day checkpoint. if an action would
   apply to any startup, it's too generic, replace it.
```

---

## Why it works

- **"every claim must reference a specific number"** kills generic AI advice
- **"no data" instead of estimating** — an honest gap beats a confident guess
- **"if a point doesn't hurt, replace it"** forces past the polite defaults
- **public claims vs actual numbers** — the part you really don't want to read
- deliverables are *artifacts* (dashboard + plan with targets and checkpoints), not vibes

## Tips

- after the first pass, challenge the findings ("recheck retention", "that drop was a
  deliberate spend cut — control for it"). the second iteration is where the real
  insights live: in my run it caught an analytics artifact that had been hiding the
  true retention number
- give it your pitch deck and sent investor updates for step 5. yes, it stings
