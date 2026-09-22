---
name: almost-paid
description: "Find the users who almost paid — saw the paywall, started checkout, ran out of free credits, let a trial lapse — size what they are worth, and turn them into a one-screen dashboard with a ready-to-send offer per segment (email + push drafts, CSV export, send gate). Trigger when the user asks about \"almost paid\", \"abandoned checkout\", \"paywall drop-off\", \"trial expired\", \"win-back\", \"recover revenue\", \"who should I send an offer to\", or wants a revenue-recovery dashboard. Works on any product analytics (Amplitude / Mixpanel / PostHog / warehouse SQL / CSV export) — it needs events, not a vendor. Never sends anything itself: it produces the list, the copy and the numbers, and hands off to the user's own sender behind a confirm gate."
tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch
---

# Almost Paid

Most products have a pile of people who got within one tap of paying and
didn't. They are the cheapest revenue you will ever get: you already paid to
acquire them, they already understood the product, and they told you exactly
where they stopped. This skill finds them, prices them, and puts an offer in
front of each segment — with the discipline that keeps this from turning into
"blast a 50% coupon at everyone who ever opened the app".

It runs in four steps: **validate the events → cut the segments → price them
→ build the dashboard + drafts**. Sending is a separate, gated action.

## Operating principles

1. **Validate the trigger events before you build anything on them.** The
   whole skill rests on events like `paywall_shown` and `purchase`. In real
   products these are wrong more often than right: a paywall event that fires
   on every onboarding screen, a purchase event that undercounts by a quarter
   against the billing provider, a "checkout started" that also fires on
   restore. Step 1 exists to catch this. A cohort built on an unvalidated
   event is confidently wrong, and a discount sent to it is money out the door.
2. **"Almost paid" is not one cohort. It's six, and they want different
   offers.** Someone whose card was declined needs a retry link, not a
   discount. Someone who ran out of free credits mid-task needs the task
   finished, not a sales pitch. Collapsing them into one blast throws away the
   only thing you know about each person — where they stopped.
3. **Cheap signal beats big signal.** The best predictor of "will pay with a
   nudge" is *recency + depth*: reached the paywall in the last 7 days AND did
   the thing the paywall gates. A person who saw the paywall 90 days ago on
   day one is not "almost paid"; they are churned, and belong to a different
   playbook.
4. **Price the cohort honestly, and say what's an assumption.** Expected
   revenue = size × ARPPU × assumed conversion. ARPPU is a fact from billing.
   The conversion rate is a guess until the first send — mark it as one, use a
   conservative default (see Step 3), and replace it with the measured number
   after the first campaign. Never put an unlabeled projection on a dashboard
   a founder will screenshot.
5. **Discounts are the last lever, not the first.** Order of offers:
   *remove friction* (retry link, finish-the-task credit, one-tap resume) →
   *add value* (a bonus, a longer trial, a feature unlock) → *lower price*
   (time-boxed, once). A discount that reaches someone who would have paid
   full price is a loss, and "almost paid" cohorts are exactly where those
   people live.
6. **Exclude before you include.** Already paid (on any platform), refunded,
   chargebacked, unsubscribed from marketing, contacted in the last N days,
   under 24h since the trigger (they may still convert on their own). The
   exclusion list is where the legal and reputational risk sits — build it
   first and keep it in the spec.
7. **One message per person per campaign, logged per user.** A send that can
   be re-run without a per-user log will double-send the moment something is
   interrupted. "I stopped the script" does not mean "nothing went out".
   Require a sent-log keyed by user id, and make re-runs skip logged users.
8. **The dashboard answers three questions, on one screen: who, how much, what
   to send.** Segments with sizes; expected revenue with the assumption
   visible; the offer per segment with a draft ready. Anything else is
   decoration. It should be worth a screenshot.
9. **The skill never sends.** It produces the list (CSV), the copy, the
   numbers and a *command* for the user's own sender that defaults to dry-run
   and requires an explicit count to go live. Sending is a human decision
   about real people, and the tooling for it is different in every company.
10. **Measure the lift, not the sends.** A campaign "worked" if the treated
    segment converted above a held-out slice of the same segment. Hold out
    10–20% on the first send of any new offer; otherwise you will credit the
    offer for conversions that were going to happen anyway (see principle 6,
    the 24h exclusion — same logic).

## Step 0 — Bootstrap (first run only)

Auto-discover before asking. Read the codebase for analytics calls, grep for
event names, fetch the billing provider's event list, look at any existing
win-back or lifecycle code. Then ask **only** what tools cannot answer:

1. Where do events live, and how do I query them? (analytics MCP / SQL /
   export path)
2. What is the source of truth for *purchases* — analytics or the billing
   provider? (Almost always the billing provider.)
3. ARPPU or price list, per platform if they differ.
4. Which channels can reach users, and what is the unsubscribe mechanism?
5. Any segment you refuse to discount? (e.g. current trial users, a region,
   a plan.)

Write the answers to `brief.md` next to this file (gitignored; product-specific).

## Step 1 — Validate the trigger events

For every event the segments depend on, produce a one-line verdict before
using it. The check is cheap and it is the step people skip.

| Event | Check | Red flag |
|---|---|---|
| paywall shown | daily uniques vs daily new users | ratio ≈ 1.0 → fires on every onboarding, not on intent |
| checkout started | vs billing-provider "purchase initiated" or trial starts | wildly higher → also fires on restore / relaunch |
| purchase | vs billing provider's purchase events, same window | undercount > 10% → use the provider, not analytics |
| trial started / expired | vs provider | mismatch → provider wins |
| credits exhausted / limit hit | fires before or after the block? | fires before the gate → not a real block |

Rule: **for money events, the billing provider is the truth.** Analytics
events tell you *where* in the product it happened; the provider tells you
*whether* it happened. Join them on user id.

Record the verdicts in `brief.md` under "Event trust". A segment built on a
red-flagged event gets a warning on the dashboard, not silent use.

## Step 2 — Cut the segments

Six standard segments, from hottest to coolest. Each has a trigger, a window,
and a *depth* condition that separates intent from browsing. Adjust windows
to the product's decision cycle (a weekly-billed app: shorter; B2B: longer).

| # | Segment | Trigger | Window | Depth condition (must also hold) | Temperature |
|---|---|---|---|---|---|
| 1 | **Checkout abandoned** | checkout / purchase-sheet opened, no purchase | 1–7 days | — | hottest |
| 2 | **Payment failed** | provider: billing error / declined | 1–14 days | — | hot (not a discount case) |
| 3 | **Hit the wall mid-task** | limit / credits exhausted / gated action refused | 1–7 days | had completed the gated action ≥ 1× before, or was mid-flow | hot |
| 4 | **Paywall, repeated** | paywall shown ≥ 2 sessions | 2–14 days | ≥ 2 distinct sessions, ≥ 1 core action | warm |
| 5 | **Trial lapsed, engaged** | trial expired without conversion | 1–30 days | ≥ N core actions during trial | warm |
| 6 | **Paywall, once, deep** | paywall shown 1×, no purchase | 1–14 days | ≥ 3 core actions before it | cool |

Everyone else who saw a paywall is *not* a segment. They are the top of the
funnel, and they get the product's normal lifecycle, not an offer.

**Exclusions (apply to all):** purchased on any platform; active trial;
refund / chargeback ever; marketing opt-out; contacted by any campaign in the
last 14 days; trigger < 24h old; internal/test accounts.

Write the spec to `cohorts/spec.md` using `templates/cohort-spec.md`. The
spec is the artifact — the query is derived from it, not the other way round.

## Step 3 — Price the segments

Run `tools/cohort_value.py` on the exported cohort CSV. Per segment it gives
size, expected revenue, revenue per contact, and a priority rank.

Default assumed conversion rates — **conservative, labelled, replaced after
the first send:**

| Segment | Default assumed conversion | Why |
|---|---|---|
| 1 checkout abandoned | 8% | closest to the money; friction, not doubt |
| 2 payment failed | 25% | they already decided; a working retry link converts |
| 3 hit the wall | 6% | intent proven by the block, but the task may be done by now |
| 4 paywall repeated | 3% | interest, not decision |
| 5 trial lapsed | 4% | knew the product, chose not to pay once already |
| 6 paywall once | 1.5% | mostly browsing |

Expected revenue = size × ARPPU × conversion. ARPPU is per platform when
platforms differ (web billing and app stores routinely do — different prices,
different refund rates). Refund rate is subtracted: if a channel refunds 5%,
its ARPPU is 95% of list.

The tool also emits a **"what a discount costs" line**: for a segment that
would have converted at rate *r* without an offer, a *d*% discount sent to all
of them costs `size × ARPPU × r × d` in margin from people who'd have paid
anyway. Show this next to the projected lift; it is the argument for
principle 5.

## Step 4 — Offers per segment

Match the offer to *where they stopped*. Drafts live in
`templates/offers.md` with placeholders; adapt the voice, keep the structure.

| Segment | Offer | Channel | Cadence |
|---|---|---|---|
| 1 checkout abandoned | one-tap resume link to the exact plan; no discount on first touch | push (same day) → email (day 2) | 2 touches, 3 days |
| 2 payment failed | "your card didn't go through" + retry link; never a discount | email (immediate) → push (day 1) | 2 touches |
| 3 hit the wall | finish-the-task credit: a small grant that completes what they were doing | push (same day) | 1 touch, then normal lifecycle |
| 4 paywall repeated | value-add: extended trial / bonus feature, time-boxed | email | 1 touch + reminder day 3 |
| 5 trial lapsed | time-boxed discount, once, with a hard expiry in the link | email (day 1) → email (day 5, "expires tomorrow") | 2 touches |
| 6 paywall once | nothing paid; a content/education touch, or leave to lifecycle | email | 1 touch |

Rules baked into every draft: one clear CTA; the offer's terms stated
exactly as the billing system will charge them (if the code is edited later
the email starts lying — keep the numbers in one place); a working
unsubscribe; an expiry the link actually enforces.

## Step 5 — Dashboard

Fill `templates/dashboard.html` with the JSON that `cohort_value.py` emits
(`--dashboard out.html` does it in one go). One screen:

- headline: total recoverable revenue, with the assumption label ("at assumed
  conversion rates — replace after first send")
- per segment: size, temperature, expected revenue, revenue per contact,
  event-trust flag, chosen offer, CSV export button
- footer: exclusions applied, hold-out %, date of the data pull

If this screen is not worth a screenshot, the segments are wrong, not the
template.

## Step 6 — Hand-off to the sender (gated)

The skill's output for sending is: per segment, a CSV
(`user_id, channel_address, segment, trigger_ts, offer_code, expiry`) and a
command for **the user's own** sender. Whatever that sender is, the command
must:

- default to `--dry-run` and print the count it *would* send;
- require `--execute --confirm <exact count>` to go live — a wrong number
  refuses;
- write `sent/{campaign}/{user_id}` before each send and skip logged users
  on re-run;
- hold out 10–20% on a new offer (`--holdout 0.15`), logging who was held.

If the user's sender lacks any of these, say so and offer to add them before
the first live run. Do not send from inside this skill.

## Step 7 — Measure and compound

Seven days after each send, compare conversion in treated vs held-out per
segment. Write the measured conversion into `brief.md` and replace the
assumed rate for that segment. The dashboard's projections get more honest
with every campaign, which is the point.

Log every campaign in `campaigns.md` (gitignored): date, segment, size,
offer, holdout, measured lift, refunds at day 30. Refunds are the number that
turns a "successful" discount campaign into a loss — always close the loop
at day 30.

## Local state (gitignored)

- `brief.md` — event sources, ARPPU, channels, event-trust verdicts
- `cohorts/spec.md` — segment definitions as run
- `cohorts/*.csv` — exports (never commit; they contain user ids)
- `campaigns.md` — send log with measured lift

## Shared tools

| Step | Tool |
|---|---|
| 3, 5 | `tools/cohort_value.py` — offline: cohort CSV + ARPPU + assumed conversion → size, expected revenue, discount cost, priority; `--dashboard` renders the HTML |

Querying the analytics source is done with whatever the user has (MCP, SQL,
export) — the skill specifies *what* to pull (`templates/cohort-spec.md`),
not how.

## Tactical notes

- **Web billing ≠ app store.** Same product, two populations: different
  price, different refund rate, different reachability (web users have an
  email; app-store users may only have a push token). Always split.
- **A per-user identity split across platforms will inflate every segment.**
  If the web checkout and the app create separate user ids for the same
  person, "abandoned on web, paid in app" looks like an abandoned checkout.
  Check for a linking key before trusting cross-platform segments.
- **Push tokens go stale — around 10% of a mature base.** Clean on every
  send (delete tokens the provider reports as unregistered) or delivery
  numbers lie.
- **Timezone matters for push, and most products don't store it.** If there
  is no per-user timezone, either derive it from analytics geo or send in a
  band that is daytime for the top two regions. Never 3am.
- **The 24h exclusion is not a nicety.** A meaningful share of "abandoned"
  checkouts complete on their own within a day. Contacting them earlier
  attributes organic conversions to the campaign and trains you to over-send.
