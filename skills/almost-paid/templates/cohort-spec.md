# Cohort spec — {product} — {date}

The spec is the artifact. Queries are derived from it; if a query and this
file disagree, the file wins and the query gets fixed.

## Sources

| Thing | Source of truth | How queried |
|---|---|---|
| product events | {analytics tool} | {MCP / SQL / export} |
| purchases, trials, billing errors, refunds | {billing provider} | {webhook table / API / export} |
| user ↔ purchase join key | {user id field on both sides} | |
| channel addresses | email: {source}; push: {token table} | |
| marketing opt-outs | {table / flag} | |

## Event trust (from Step 1)

| Event | Verdict | Evidence |
|---|---|---|
| {paywall_shown} | ok / suspect / broken | {daily uniques vs new users = 0.93 → fires on onboarding} |
| {checkout_started} | | |
| {purchase} | | {undercounts provider by 27% → provider wins} |
| {trial_expired} | | |
| {limit_hit} | | |

## Global exclusions

- purchased on any platform, ever
- active trial
- refund or chargeback, ever
- marketing opt-out
- contacted by any campaign in the last 14 days
- trigger younger than 24 hours
- internal / test accounts: {how identified}

## Segments

For each: trigger event, window, depth condition, size at spec time.

### 1 checkout_abandoned
- trigger: {checkout_started} without {purchase} (provider)
- window: last {7} days
- depth: —
- notes: {web and app separately — different price and refund rate}

### 2 payment_failed
- trigger: provider {BILLING_ERROR / declined}
- window: last {14} days
- depth: —
- offer rule: retry link only, never a discount

### 3 hit_the_wall
- trigger: {credits_exhausted / limit_hit / gated_action_refused}
- window: last {7} days
- depth: completed the gated action ≥ 1× before, or was mid-flow

### 4 paywall_repeated
- trigger: {paywall_shown} in ≥ 2 distinct sessions
- window: last {14} days
- depth: ≥ 1 {core action}

### 5 trial_lapsed
- trigger: provider trial expired, no conversion
- window: last {30} days
- depth: ≥ {N} {core actions} during the trial

### 6 paywall_once
- trigger: {paywall_shown} exactly once
- window: last {14} days
- depth: ≥ 3 {core actions} before it

## Export format

`user_id, channel_address, segment, platform, trigger_ts, offer_code, expiry`
— one row per user, one segment per user (hottest wins if a user qualifies
for several).
