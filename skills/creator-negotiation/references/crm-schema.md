# CRM schema for negotiations

The smallest data model that lets this skill work and keeps its numbers honest. It's SQLite and plain SQL, so it works with any stack. If you already run [influencer-outreach](../../influencer-outreach/reference.md), add the negotiation tables to that CRM rather than building a second one.

The design goal: **every number in SKILL.md can be recomputed from your own log.** The ratio table, the series discount, rounds-to-close and the follow-up rate all come from the `moves` table. We first kept a free-text "quoted rate" column and had to re-read whole threads by hand to recover what anyone had asked for. Store each price as its own row the moment it appears.

## Contents

1. Entities at a glance
2. DDL
3. Views that answer the skill's questions
4. Rules the code should enforce
5. What to log at each step

## 1. Entities at a glance

```
creators ──< audience_snapshots
    │
    ├──< negotiations ──< moves          (every price either side names)
    │         │
    │         └── deals ──< payments
    │               ├──< videos
    │               └──< results         (codes, installs, payers by country)
    │
    └──< messages  (drafts and sent mail; moves point at the message they came from)
```

- A **negotiation** starts at the creator's first reply that contains a number and ends won, lost or paused. One creator can have several over time: the same person declined in October and revisited in March is two negotiations.
- A **move** is one price or position from one side: their quote, their package quote, our counter, an accept, a hold ("I'll keep my minimum"), a decline, a check-in. Each creator move carries a **valuation snapshot**, the three numbers worked out at that moment, so you can later see what you believed when you decided.
- A **deal** exists only after both sides said yes. It points at the move whose terms were accepted.

## 2. DDL

```sql
PRAGMA foreign_keys = ON;

-- One row per creator account you deal with.
CREATE TABLE creators (
  id                INTEGER PRIMARY KEY,
  platform          TEXT NOT NULL CHECK (platform IN ('tiktok','instagram','youtube')),
  handle            TEXT NOT NULL,
  display_name      TEXT,
  lang              TEXT,              -- language you write to them in (from the bio, not the hashtag)
  country           TEXT,              -- where they live, ISO 3166 alpha-2
  followers         INTEGER,
  median_views      INTEGER,           -- last 5 UNPINNED videos
  median_checked_at INTEGER,           -- unix time; re-check if older than ~14 days
  seller_type       TEXT NOT NULL DEFAULT 'direct'
                    CHECK (seller_type IN ('direct','new_to_paid','agency','manager','ugc_studio')),
  email             TEXT,
  payout_rails      TEXT,              -- JSON array: ["paypal","bank","interac","wise"]
  created_at        INTEGER NOT NULL,
  UNIQUE (platform, handle)
);

-- Audience by country, from the creator's screenshot. Decides WHETHER to buy.
CREATE TABLE audience_snapshots (
  id           INTEGER PRIMARY KEY,
  creator_id   INTEGER NOT NULL REFERENCES creators(id),
  platform     TEXT NOT NULL,
  source       TEXT NOT NULL CHECK (source IN ('screenshot','creator_said','tool_estimate')),
  countries    TEXT NOT NULL,          -- JSON object: {"US":0.42,"MX":0.11,...}
  paying_share REAL,                   -- share of viewers in countries where your product sells
  taken_at     INTEGER NOT NULL
);

CREATE TABLE negotiations (
  id               INTEGER PRIMARY KEY,
  creator_id       INTEGER NOT NULL REFERENCES creators(id),
  opened_at        INTEGER NOT NULL,   -- first reply with a number in it
  state            TEXT NOT NULL DEFAULT 'waiting_us'
                   CHECK (state IN ('waiting_us','waiting_them','won','lost','paused')),
  outcome          TEXT CHECK (outcome IN (
                     'won',
                     'declined_gap',           -- we declined: ratio too low
                     'declined_geo',           -- we declined: audience in non-paying countries
                     'declined_by_them',       -- they said no to our number
                     'held_their_rate',        -- they repeated their number; we closed
                     'agency_sheet',           -- rate sheet / manager / studio
                     'silent_after_counter',
                     'silent_after_agreement',
                     'other')),
  outcome_note     TEXT,               -- their words, short; a free audit of your offers
  closed_at        INTEGER,
  revisit_after    INTEGER,            -- when to write again (e.g. next budget review)
  revisit_rate_usd REAL                -- their last per-video ask, so you know if you can afford them now
);

-- Every price or position, in order. The heart of the schema.
CREATE TABLE moves (
  id                 INTEGER PRIMARY KEY,
  negotiation_id     INTEGER NOT NULL REFERENCES negotiations(id),
  seq                INTEGER NOT NULL,          -- 1, 2, 3... in thread order
  side               TEXT NOT NULL CHECK (side IN ('creator','us')),
  kind               TEXT NOT NULL CHECK (kind IN (
                       'quote',          -- single-video price
                       'package_quote',  -- series price
                       'counter',
                       'accept',
                       'hold',           -- "I'd prefer to keep my rate"
                       'decline',
                       'check_in')),     -- no price, just a nudge
  videos             INTEGER,                   -- how many videos this price covers
  platforms          TEXT,                      -- JSON array: ["tiktok","reels","shorts"]
  extras             TEXT,                      -- JSON array: ["link_in_bio_30d","usage_rights_90d","whitelisting","exclusivity_30d","stories:2"]
  amount             REAL,                      -- exactly as written
  currency           TEXT,                      -- as written; NULL while "$" is ambiguous
  currency_confirmed INTEGER NOT NULL DEFAULT 0,
  fx_to_usd          REAL,                      -- rate on the day of the move
  per_video_usd      REAL,                      -- amount * fx_to_usd / videos
  pay_terms          TEXT CHECK (pay_terms IN ('upfront_full','per_video_upfront','half_half','after_post','unspecified')),
  bonus              TEXT,                      -- JSON: {"per_views":N,"usd":N,"cap_usd":N,"organic_only":true}
  -- valuation snapshot, filled on creator moves
  expected_views     INTEGER,                   -- ~1/3 of unpinned median, or your own calibrated share
  paying_share       REAL,
  ceiling_usd        REAL,                      -- expected_views * paying_share / 1000 * your max $ per 1k
  ratio              REAL,                      -- ceiling_usd / per_video_usd
  message_id         INTEGER REFERENCES messages(id),
  at                 INTEGER NOT NULL,
  UNIQUE (negotiation_id, seq)
);

CREATE TABLE messages (
  id             INTEGER PRIMARY KEY,
  creator_id     INTEGER NOT NULL REFERENCES creators(id),
  negotiation_id INTEGER REFERENCES negotiations(id),
  direction      TEXT NOT NULL CHECK (direction IN ('in','out')),
  channel        TEXT NOT NULL CHECK (channel IN ('email','tiktok_dm','ig_dm','whatsapp')),
  kind           TEXT,                 -- intro, offer, counter, decline, check_in, agreement, payment_note, reaction
  lang           TEXT,
  body           TEXT NOT NULL,
  translation    TEXT,                 -- for the human who reviews and sends
  status         TEXT NOT NULL CHECK (status IN ('received','draft','approved','sent','discarded')),
  sent_by_user   INTEGER NOT NULL DEFAULT 0,  -- set only by the UI's send route; agents can't send
  created_at     INTEGER NOT NULL,
  sent_at        INTEGER
);

CREATE TABLE deals (
  id             INTEGER PRIMARY KEY,
  negotiation_id INTEGER NOT NULL UNIQUE REFERENCES negotiations(id),
  final_move_id  INTEGER NOT NULL REFERENCES moves(id),  -- the terms both sides accepted
  videos         INTEGER NOT NULL,
  price_usd      REAL NOT NULL,
  agreement_path TEXT,
  confirmed_at   INTEGER,              -- "I agree" in the thread
  first_deadline INTEGER,
  promo_code     TEXT
);

CREATE TABLE payments (
  id           INTEGER PRIMARY KEY,
  deal_id      INTEGER NOT NULL REFERENCES deals(id),
  purpose      TEXT NOT NULL CHECK (purpose IN ('full','per_video','bonus')),
  video_no     INTEGER,
  amount       REAL NOT NULL,
  currency     TEXT NOT NULL,
  amount_usd   REAL NOT NULL,
  method       TEXT NOT NULL,          -- paypal, bank, interac, wise
  fees_on_us   INTEGER NOT NULL DEFAULT 1,
  sent_at      INTEGER,
  confirmed_at INTEGER                 -- creator said it arrived
);

CREATE TABLE videos (
  id               INTEGER PRIMARY KEY,
  deal_id          INTEGER NOT NULL REFERENCES deals(id),
  video_no         INTEGER NOT NULL,
  platform         TEXT NOT NULL,
  url              TEXT,
  posted_at        INTEGER,
  code_in_caption  INTEGER,
  views_d14        INTEGER,            -- the locked count, if the deal has a bonus
  views_latest     INTEGER,
  views_checked_at INTEGER
);

-- What the deal returned. Fill from your analytics; per-country payers are the number that matters.
CREATE TABLE results (
  id           INTEGER PRIMARY KEY,
  deal_id      INTEGER NOT NULL REFERENCES deals(id),
  measured_at  INTEGER NOT NULL,
  window_days  INTEGER NOT NULL,
  code_redeems INTEGER,
  code_typos   INTEGER,                -- wrong spellings of the code that failed; a reason to accept variants
  installs     INTEGER,
  payers       INTEGER,
  revenue_usd  REAL,
  by_country   TEXT                    -- JSON: {"US":{"installs":N,"payers":N},...}
);

CREATE INDEX moves_neg ON moves(negotiation_id, seq);
CREATE INDEX msg_creator ON messages(creator_id, created_at);
CREATE INDEX neg_state ON negotiations(state, revisit_after);
```

## 3. Views that answer the skill's questions

```sql
-- Recalibrate the ratio table: close rate by the ratio at the creator's FIRST price.
CREATE VIEW v_ratio_calibration AS
WITH first_price AS (
  SELECT m.negotiation_id, m.ratio
  FROM moves m
  WHERE m.side = 'creator' AND m.kind IN ('quote','package_quote') AND m.ratio IS NOT NULL
    AND m.seq = (SELECT MIN(seq) FROM moves x
                 WHERE x.negotiation_id = m.negotiation_id AND x.side = 'creator'
                   AND x.kind IN ('quote','package_quote') AND x.ratio IS NOT NULL)
)
SELECT CASE WHEN f.ratio >= 1    THEN 'a: >=1'
            WHEN f.ratio >= 0.6  THEN 'b: 0.6-1'
            WHEN f.ratio >= 0.33 THEN 'c: 0.33-0.6'
            ELSE                      'd: <0.33' END       AS bucket,
       COUNT(*)                                            AS negotiations,
       ROUND(AVG(n.outcome = 'won') * 100)                 AS won_pct
FROM first_price f JOIN negotiations n ON n.id = f.negotiation_id
WHERE n.state IN ('won','lost')
GROUP BY bucket ORDER BY bucket;

-- How much creators discount themselves for a series.
CREATE VIEW v_series_discount AS
SELECT s.negotiation_id,
       s.per_video_usd                                   AS single_usd,
       p.per_video_usd                                   AS series_per_video_usd,
       ROUND((1 - p.per_video_usd / s.per_video_usd) * 100) AS discount_pct
FROM moves s JOIN moves p
  ON p.negotiation_id = s.negotiation_id
WHERE s.side = 'creator' AND s.kind = 'quote'
  AND p.side = 'creator' AND p.kind = 'package_quote'
  AND s.per_video_usd > 0;

-- Rounds to close: count of priced moves in won negotiations.
CREATE VIEW v_rounds_to_close AS
SELECT n.id AS negotiation_id,
       SUM(m.kind IN ('quote','package_quote','counter')) AS priced_moves
FROM negotiations n JOIN moves m ON m.negotiation_id = n.id
WHERE n.outcome = 'won'
GROUP BY n.id;

-- Today's queue: what each open negotiation needs from us.
CREATE VIEW v_next_actions AS
WITH last_in  AS (SELECT negotiation_id, MAX(created_at) t FROM messages WHERE direction='in'  GROUP BY negotiation_id),
     last_out AS (SELECT negotiation_id, MAX(sent_at)    t FROM messages WHERE direction='out' AND status='sent' GROUP BY negotiation_id),
     checkins AS (SELECT negotiation_id, COUNT(*) c, MAX(at) t FROM moves WHERE kind='check_in' GROUP BY negotiation_id)
SELECT n.id, c.handle,
       CASE
         WHEN COALESCE(li.t,0) > COALESCE(lo.t,0)                           THEN 'reply'
         WHEN COALESCE(ck.c,0) = 0 AND strftime('%s','now') - lo.t > 5*86400 THEN 'one check-in'
         WHEN ck.c >= 1 AND strftime('%s','now') - ck.t > 7*86400            THEN 'close as silent'
         ELSE 'wait'
       END AS action
FROM negotiations n
JOIN creators c ON c.id = n.creator_id
LEFT JOIN last_in li  ON li.negotiation_id = n.id
LEFT JOIN last_out lo ON lo.negotiation_id = n.id
LEFT JOIN checkins ck ON ck.negotiation_id = n.id
WHERE n.state IN ('waiting_us','waiting_them');

-- Creators to write to again.
CREATE VIEW v_revisit_due AS
SELECT c.handle, c.lang, n.outcome, n.revisit_rate_usd, n.outcome_note, n.closed_at
FROM negotiations n JOIN creators c ON c.id = n.creator_id
WHERE n.state = 'lost' AND n.revisit_after <= strftime('%s','now');

-- Deals confirmed but not paid: pay the same day.
CREATE VIEW v_payment_due AS
SELECT d.id AS deal_id, c.handle, d.price_usd, d.confirmed_at
FROM deals d
JOIN negotiations n ON n.id = d.negotiation_id
JOIN creators c ON c.id = n.creator_id
WHERE d.confirmed_at IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.deal_id = d.id AND p.sent_at IS NOT NULL);

-- What each deal actually cost and returned. sponsored_share recalibrates the "about a third" rule.
CREATE VIEW v_deal_economics AS
SELECT d.id AS deal_id, c.handle,
       (SELECT SUM(amount_usd) FROM payments p WHERE p.deal_id = d.id AND p.sent_at IS NOT NULL) AS paid_usd,
       (SELECT SUM(views_latest) FROM videos v WHERE v.deal_id = d.id)                         AS views,
       ROUND(1000.0 * (SELECT SUM(amount_usd) FROM payments p WHERE p.deal_id = d.id AND p.sent_at IS NOT NULL)
             / NULLIF((SELECT SUM(views_latest) FROM videos v WHERE v.deal_id = d.id), 0), 1)  AS usd_per_1k,
       ROUND(1.0 * (SELECT AVG(views_latest) FROM videos v WHERE v.deal_id = d.id AND v.platform = c.platform)
             / NULLIF(c.median_views, 0), 2)                                                    AS sponsored_share,
       (SELECT SUM(payers) FROM results r WHERE r.deal_id = d.id)                              AS payers
FROM deals d
JOIN negotiations n ON n.id = d.negotiation_id
JOIN creators c ON c.id = n.creator_id;
```

## 4. Rules the code should enforce

These protect the human reviewer from the mistakes that are easy to make at speed. Enforce them where drafts are created and approved, not in a prompt.

- **Agents draft, people send.** Only the UI's send route sets `sent_by_user = 1` and `status = 'sent'`.
- **No counter on an unconfirmed currency.** Refuse to approve an outgoing `counter` if the creator's last priced move has `currency IS NULL` or `currency_confirmed = 0`. Draft the confirmation question instead.
- **No counter on a stale valuation.** Warn if `median_checked_at` is older than ~14 days or no `audience_snapshots` row exists before the first payment.
- **Round limit.** Warn before approving a priced move that would make it the fifth priced move in a negotiation (their ask, our counter, their counter, our final step).
- **One check-in.** Refuse a second `check_in` move in the same negotiation; offer to close it as `silent_after_counter`.
- **No extras after yes.** Once a deal exists, an outgoing message that adds items to `extras` should be flagged as a new negotiation, not slipped into a thread.
- **Close with a reason.** A negotiation can't move to `lost` without an `outcome`; `revisit_after` is required for `declined_gap`, `declined_by_them` and `held_their_rate`.

## 5. What to log at each step

| Moment | Write |
|---|---|
| Creator's first reply with a number | `negotiations` row; `moves` row(s) for each price they named (single and package separately), with the valuation snapshot |
| "$" without a currency | `currency = NULL`; the next outgoing draft is the confirmation question |
| Audience screenshot arrives | `audience_snapshots` row; recompute `paying_share` and the ceiling on their latest move |
| You counter, accept, decline or check in | `messages` draft + a `moves` row pointing at it (`side='us'`) |
| They counter or hold | `moves` row with a fresh valuation snapshot |
| "I agree" | `deals` row pointing at the accepted move; `negotiations.state = 'won'` |
| Payment sent / confirmed | `payments` row; set `confirmed_at` when they say it arrived |
| Video goes live | `videos` row; refresh `views_latest` on a schedule, lock `views_d14` if there's a bonus |
| Results come in | `results` row per measurement window, with per-country payers |
| Thread closes without a deal | `outcome`, `outcome_note` in their words, `revisit_after`, `revisit_rate_usd` |
