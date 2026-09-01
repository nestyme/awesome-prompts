---
name: influencer-outreach
description: Build and run a paid micro-influencer outreach pipeline end to end — scrape creators by niche hashtags, verify their real reach, score who to write first, draft outreach in the creator's language, negotiate, contract, and pay for actual results. Trigger when the user wants to find and pay creators/influencers for product videos, asks how to run influencer outreach, cold-email creators at scale, price a collab, decide what to pay a creator, or build a creator CRM. Self-bootstrapping — asks only for strategy and budget, discovers the rest.
---

# Influencer Outreach

A pipeline for buying reach from micro-creators: discover them, verify their real numbers, write to them in their language, negotiate without insulting anyone, and pay for views that actually happened.

Built and battle-tested on a live run: **2,157 creators scraped for ~$26, 54 cold emails, 17 replies (31%), 3 signed creators in 8 days, ~$40 total tooling spend.** Every warning below cost real money or real embarrassment.

_Skill by [@nestymee](https://x.com/nestymee)._

## Shared tools

Prefer the repo's [`tools/`](../../tools/README.md) CLIs for the analysis half — they emit a uniform JSON envelope and chain together.

| Step | Tool | Use |
|---|---|---|
| 2 | `tiktok_account.py` | Collect a creator's videos + stats (TikTokApi → yt-dlp fallback) |
| 3 | `account_stats.py` | Median views **excluding pinned** (`--keep-pinned` to disable), cadence, paid-amp signals |
| 3 | `engagement.py` | Per-video engagement score, save rate, freshness — for quality screening |
| 2 | `video_metadata.py` | Fallback collector when scrapers are blocked |

The outreach half (CRM, drafting, sending, payouts) is a small local codebase you generate — see [reference.md](reference.md) for the schema, the scoring formula, and email templates.

## Operating principles

1. **Never let an agent press send.** Draft everything, send nothing. The human clicks. Enforce it in code, not in intent: `send_message()` takes `sent_by_user=True` that only the UI route sets — scripts and agents physically cannot send. Every email goes out from a real person's domain, to a real person, promising real money; the blast radius of an automated mistake is the domain's reputation.
2. **Pinned videos destroy median views — exclude them everywhere.** Scrapers return pinned posts first, and creators pin their best-ever video. In the source run this inflated medians for **half the database, worst case ×28** (a creator whose real median was 560 showed 17,050). Pricing built on that number would have sent a $250 offer to a creator worth $30. Take 6+ recent videos, drop `isPinned`, take the median of 5.
3. **The views/followers ratio is not a filter for that bug.** The ×28 creator had a ratio of 2.9 — well under any suspicious threshold — because her follower count was small too. The only real check is re-scraping and recomputing. The ratio is useful for *targeting*, never for *data validation*.
4. **Two species of creators reply to email, and they want opposite things.**
   - **Production sellers** (`ugc` in the handle/bio, or a dedicated `*collabs@` / `*contact@` address): reply ~**40%** of the time — email is their business channel — but they sell *production* off a rate card ($150–1000/video, +30% for posting, +30% for usage rights). They compare your offer to that card, not to their reach.
   - **Reach creators**: reply ~**6%**, but a price tied to their actual views reads as market rate.

   You are buying reach. Sellers will price you out; reach creators will ghost you. Both facts are structural — plan volume around the 6%, and detect sellers before writing so the offer doesn't insult them.
5. **Creators price themselves by follower count; you should pay by views.** A 175k-follower account doing 5k views expects hundreds of dollars. A 3k-follower account doing 11k views is thrilled with market rate. The golden segment is **small accounts whose views outperform their followers** — in the source run, *every single signed deal* came from ≤60k followers with live views.
6. **Ask for their rate in the very first email.** One line — *"what would your rate be for one short video? asking upfront because we're small: if we can't afford you, we'd rather not waste your time"* — and rate-card creators self-identify **before** they ever see your numbers. It converts better than "open to a collab?" (a concrete question gets answered), and it prevents the failure mode where a professional reads your offer as an insult. Before this line existed, the run collected one *"this is an insult to the profession"* from a 3k-follower creator charging an effective $28 CPM.
7. **Price on results, not on predictions.** `base + bonus per N views actually reached, capped`. This makes principle 2 survivable: if your scraped median is wrong, you simply don't overpay. Never derive the offer from the median — use the median only to *rank* who to write and to show an illustrative example ("going by your recent videos that'd be about $X").
8. **Pay the base upfront, before filming.** It is the single strongest trust signal available to an unknown brand and it costs $25–75 to buy. In the source run a creator who got paid before confirming replied *"mil gracias por confiar en mí"* and delivered her own concept, better than anything in the brief.
9. **Lock the view count on a fixed day.** "Views counted on day 14, that figure is final" protects both sides: you don't carry an open-ended liability if the video resurfaces in six months, and the creator knows the exact date of the second payment instead of "sometime".
10. **The same offer gets "thanks, door's open" and "this is not dignified".** The offer is not the variable — the person is. Log every decline reason; they are a free audit of the funnel. In the source run five price declines shared one shape: a rate card of $150–1000 against a real median of 5–20k views.
11. **Open every platform a creator bills you for.** One creator priced $450 for "cross-posting to TikTok, Instagram and YouTube" — the Instagram was empty and the YouTube was blocked. Thirty seconds of clicking catches what no scoring formula can.
12. **Follow-ups produce roughly half your replies.** People lose emails; a single "just checking this didn't get buried — if it's not a fit, a quick no is totally fine" resurrects a surprising share of dead threads. Explicit permission to decline is what makes it work: silence is usually embarrassment, and a "no" is worth more than a ghost.

## Step 0 — Bootstrap (first run only)

Auto-discover everything you can before asking: read the codebase, App Store page, landing page and analytics for what the product does, who it's for, and which markets it's live in. Then ask the human **only** for judgment calls:

1. **Monthly budget for creators** (drives base rate, batch size, and how many can be in flight).
2. **Markets/languages** to run — and any region to exclude (payments that don't work there, etc.).
3. **Niche hashtags** to mine — validate your guesses with them rather than asking cold.
4. **Who sends** — the name and domain the emails come from.
5. **Payment rails available** (PayPal, bank transfer, region-specific).

Write the answers to a local `brief.md` next to the skill (gitignored — see repo conventions). Everything else (creator handles, emails, view counts) is discovered, never asked.

## Step 1 — Mail infrastructure (do this before anything else)

A cold-outreach domain takes days to warm up, so it must exist before the first creator email.

- **Separate domain**, never the product's main one. Reputation damage should not be able to reach transactional mail.
- **SPF, DKIM (2048), DMARC (`p=none`)** live before email #1. Verify by mailing yourself and reading `Authentication-Results`: you want `dkim=pass spf=pass dmarc=pass`.
- **SMTP + IMAP with an app password** — no OAuth project, no API keys, ~20 lines of stdlib.
- **Warm up 5–7 emails/day for 4+ days** to a list of real addresses that **reply**. Two-way traffic is the signal; volume alone is not. Vary subjects and bodies — ten short, human, link-free templates rotated.
- **Validate the warmup list itself**: `gmai.com` is not a typo you can ignore, it's a live typosquatter that will deliver your mail to a stranger.
- **Ramp**: ≤30 total/day in week one → 35–40 → 50+. Replies to inbound don't count toward the cap; they're the healthiest traffic you have.
- Cold emails: **plain text, no links** (links belong in live threads only), signature without `http://`.

## Step 2 — Collect

Scrape by hashtag, two kinds:

- **Niche tags** — what your audience actually posts under (`#grwm`, `#outfitinspo`, and the local-language equivalents).
- **Collab tags** (`#letscollab`, `#ugccreator`) — high yield, but they select for *production sellers* (principle 4). Expect to write to them differently.

Localize the tag list per market rather than translating one list. Pull profile + recent videos + bio, extract email from bio, and recursively from a link-in-bio page if present.

Budget note: ~$26 bought 2,157 creators with emails on a $29/mo Apify plan. Triage cheaply (a few videos per profile), verify precisely only for creators you're about to write to.

## Step 3 — Verify reach (the step everyone skips)

For every creator before outreach:

```
videos = scrape(handle, count=6+)
unpinned = [v for v in videos if not v.isPinned]     # principle 2
median = median(unpinned[:5])                         # 5 minimum, 2 is an average not a median
```

Then apply the screening filters — in the source run these cut a 2,157-row database to a few hundred worth writing to:

| Filter | Threshold | Why |
|---|---|---|
| Median views | ≥ 2,000 | Below this a video costs more per thousand views than paid ads |
| Views / followers | ≥ 0.7 | An audience that doesn't watch its own creator won't watch your integration |
| Views / followers | < 15 | Above this it's bought views, not algorithmic reach |
| Followers | ≤ 50–60k | Above it, self-assessment outruns your budget (principle 5) |
| Email domain | agency keywords | `agency`/`agence`/`agencia`/`agentur`/`mgmt`/`talent` — slower, dearer, usually a no |
| Email validity | syntax + typo list + MX | Catches typosquatters and dead domains before they become bounces |

## Step 4 — Score who to write first

Rank by **expected views per dollar × probability the deal actually happens**, where that probability splits in two:

```
score = (median_views / your_cost) × p_reply × p_accept × upside
```

- `p_reply` — 0.40 for production sellers, ~0.08 for reach creators (measured, not guessed — recalibrate from your own replies after ~50 emails).
- `p_accept` — your payout ÷ what they think they're worth, where their self-assessment is `max(views × CPM, followers × ~$2/1k, and for sellers a floor at the going production rate ~$220)`.
- `upside` — reward creators whose views beat their followers; halve anything above ×15 (bought views).

The formula's job is to keep two failure modes off the top of the queue: creators who reply eagerly but will never accept your price, and creators who'd accept but never open email. Full implementation in [reference.md](reference.md).

## Step 5 — Write (in their language)

Detect language **from the bio**, not from the hashtag you found them under, then draft in it. Keep a template per language rather than machine-translating at send time.

The intro that works, in four beats:
1. One specific compliment on their content + what the product is, in one sentence.
2. **Who you are, honestly and small**: *"we're a tiny family company — just the two of us, building this app"*. People decline companies easily and people rarely.
3. **The rate question** (principle 6).
4. Nothing else. No links, no attachments, no pitch deck.

The offer, once they're interested, must kill the fear of production work before it quotes money: *"filming shouldn't take more than 20 minutes — you record your reaction, add a voiceover to your taste, and cut in a demo clip of the app that we prepare for you. No script, and we don't approve drafts."* Without that line, professionals read the offer as "full production for pennies" — that is exactly the sentence that triggered the "insult" reply in the source run.

Then: what you pay (base + per-N-views + cap), base upfront before filming, deadline for going live, comments answered for the first week, **no usage rights taken**, a month of premium so their opinion is honest. Close with one video, not a package: *"let's start with one and see how it goes."*

## Step 6 — Triage the answer

| They say | Do |
|---|---|
| A rate ≤ ~2–3× your per-video cost | Send the offer; the scale usually lands in range |
| A rate far above | One warm decline, immediately: *"that's a fair rate, we just can't afford it at this stage"*. Never argue with their number, never reveal your scale afterwards, never counter twice |
| "Tell me more" | Full mechanics + scale in one message; don't drip |
| A counter you want | Restructure rather than raise: *"we can't put $450 into one video, but we'd do $450 for two"* — same total, more reach, and they still get their number |
| Silence, 3+ days | One follow-up with explicit permission to say no (principle 12) |

## Step 7 — Contract and pay

A one-page agreement, in their language plus English, that reads as *confirmation of what we already agreed* rather than legalese — confirmed by replying "I agree" in the thread. Non-obvious clauses worth having:

- **Organic views only** — no bought views *and no paid boost/promote*. Paid amplification is not fraud, but it inflates the number your bonus is computed on. Highlight this clause visually; it's the one that protects your money.
- **Availability through the count date** — the video must stay public at least until day 14.
- **One revision round** — narrowly scoped to factual misrepresentation of the product, explicitly *not* style or script.
- **Rights stay with the creator** — you're buying distribution, not a content library. It costs you nothing and it's worth real money to them (usage rights are a +30% line on most rate cards).
- **Disclosure** — recommend the platform's paid-partnership tool, with the click path spelled out, framed as protecting their video rather than as your requirement.

Then: pay the base, note the deadline, and stop managing them. On day 14 after publication, re-scrape the video, lock the view count, compute the bonus, pay it.

## What this costs to run

| Item | Cost |
|---|---|
| Scraping ~2,000 creators with emails | ~$26 one-off |
| LLM drafting/translation/negotiation | cents per creator |
| Mail (Workspace) | ~$6/mo |
| CRM, dashboard, sending | $0 — SQLite + stdlib |
| Per creator paid | base $25–75 + performance |

At the observed numbers, signed collabs land around **$1–2.5 per thousand views**, cheaper than paid acquisition in the same niche.

## Tactical playbook

Cross-vertical lessons; append new ones after each run.

### Segment by what they sell, not by size
"Openness to collabs" as a ranking signal quietly optimizes for production sellers: the creators who advertise `let's work together` are the ones with rate cards. If you're buying reach, that signal is inverted. Detect the seller (handle, bio, dedicated collab address) and rank them by whether your ceiling can meet their floor, not by how eagerly they answer.

### A trust gesture beats a negotiation tactic
Paying the base before the contract is signed — explicitly framed as *"as a sign of trust, no strings"* — converted the source run's fastest deal and produced the most enthusiastic creator. It's cheap: the downside is one base payment, the upside is a creator who feels obligated in the good way and tells other creators.

### Let them bring the concept
The strongest video in the source run came from a creator who read the brief and proposed her own idea instead. Ship a brief of 4–5 concepts explicitly labelled *ideas, not requirements*, always with a "something else entirely" option, and approve their idea without edits when it's good. They know their audience; the brief exists to remove fear, not to direct.

### Offer to do the work they're afraid of
"We can prepare the in-app demo footage for you, and even edit the whole video — or film it yourself, whichever's easier." This converts creators who like the money but don't want to learn your product, and it costs one screen recording you can reuse.

### Rate cards are anchored on followers and lag reality
Creators quote from historical peak, not current reach: a $1,000 rate card sat on a real median of 5,345 views (an effective $187 CPM). Their case studies ("a 22M-view video") describe an account that no longer exists. Always price from the median you measured this week.

### Localize the send, not just the text
A reply in the creator's own language — especially outside English — measurably warms the thread. Keep templates per language, detect from bio, and let the negotiator answer in-language too. Also localize the *pipeline*: agency keywords, typo domains, and payment rails all differ per market.
