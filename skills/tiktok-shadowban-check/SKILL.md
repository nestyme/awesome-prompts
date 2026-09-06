---
name: tiktok-shadowban-check
description: Tell whether TikTok accounts are shadowbanned / throttled, how likely, why, and what to do. Trigger whenever the user gives a list of TikTok handles plus an Apify key (or asks "am I shadowbanned", "why did my reach drop", "why 200 views", "what works on @handle", or is about to abandon/recreate an account). Returns a shadowban probability per account, the distribution-round histogram behind it, the spam/automation signals found, what works vs what flops, and a fix list.
---

# TikTok shadowban check

**Give me a list of accounts and an Apify key — I return, per account, a
shadowban probability, the likely causes, and what to do about it.**

```bash
python3 ../../tools/shadowban_check.py handle1 handle2 --apify-key apify_api_xxx
# optional: OPENROUTER_API_KEY=... adds a "what works / what flops" LLM read
```
Output: one table on stdout + `shadowban_reports/<date>_<handle>.md` per account
(≈$0.01 per account via Apify `clockworks~tiktok-profile-scraper`, last ≤30 posts).

## The model behind the verdict

TikTok distributes in **rounds**. Every post gets a seed batch (~200–500 views);
only if that batch's watch-time / completion / saves clear the bar does the post
get the next round. So the *histogram of posts by round* is the diagnostic, not
the average:

| Round | Views | Meaning |
|---|---|---|
| R0 | <200 | never left the seed batch — throttled or dead on arrival |
| R1 | 200–500 | seeded, no expansion — hook/retention failed the first test |
| R2 | 500–2k | one expansion |
| R3 | 2k–20k | FYP traction |
| R4 | >20k | viral |

**Probability score (0–100):** share of posts stuck in R0 (up to 40) + median
<300 (20) + zero-view posts (up to 20) + burst posting (10) + duplicate captions
(10).

**The one split that matters:** at the same low median, **engagement ≥1% means
the account is throttled** (people who see it like it — TikTok just won't
distribute), while **engagement <1% means the content fails the seed test**.
Same symptom, opposite fix.

## Signals it flags (each is a documented FYF-ineligibility or automation cue)

- ≥3 posts published <1h apart · >3 posts/day → burst/automation pattern
- duplicate captions · same hashtags on ≥60% of posts → near-identical content;
  a pattern of it de-recommends the whole account
- zero-view posts → not even seeded: check Account status (strike / private)
- last-10 vs previous-10 trend → what just changed

## What to do with the verdict

- **Throttled, healthy engagement** → change *how* you post, not *what*: pause
  48–72h, then 1/day from the phone with a library sound, ≥6h apart. Do **not**
  recreate the account unless Account status shows strikes — restrictions expire.
- **Content fails seed** → fix slide 1 / the first 1.5s: specific number +
  concrete object + mistake-or-rule; clone a format that already prints in the
  niche (look for accounts with a stable 100k+/30d median, not one viral fluke).
- **Duplicate / burst signals** → unique caption per post, rotate hashtags, never
  mirror one post across accounts, spread posting times.
- **New account** only for: strikes, a device/IP that has carried many accounts,
  or wrong geo. Create (clean phone, target-country region + real number or
  mobile proxy, ≤3 accounts/device, 7–14 days of consumption before posting);
  never buy — bought accounts flag on device/IP mismatch.

## What's known vs believed

Official TikTok docs: unaudited API clients post private-only; audited ones are
allowed (~15 posts/day cap) with no documented reach penalty — but API posts
cannot carry library sounds or in-app behavioural signals. What *is* documented
is account-level de-recommendation for repeated duplicate / spam content. No
controlled API-vs-manual study exists; treat "schedulers get you shadowbanned" as
a hypothesis and A/B it: same content, manual vs API, 7 days, compare R0 share.
