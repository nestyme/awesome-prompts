# Influencer Outreach — reference

Implementation detail for [SKILL.md](SKILL.md): the CRM schema, the pricing and
scoring formulas, the email templates, and the payout loop. Everything here is
stdlib + SQLite — no framework, no dependencies, one file per concern.

## Why SQLite and not a real CRM

At a few thousand rows and one operator, a SaaS CRM is the heavier choice. The
schema below matches the funnel exactly instead of someone's idea of a funnel,
the agent reads and writes it in plain SQL with no API keys, the whole CRM is
one file you can copy and `git`-commit, and adding a column ("the rate they
quoted") takes one line. Cost: you write your own UI — about a day.

## Schema

```sql
CREATE TABLE influencers (
  id INTEGER PRIMARY KEY,
  platform TEXT, username TEXT, url TEXT, name TEXT, bio TEXT,
  followers INTEGER,
  median_views INTEGER,        -- of UNPINNED videos only (see SKILL principle 2)
  views_checked INTEGER DEFAULT 0,   -- 1 = precisely re-verified, safe to write
  is_seller INTEGER DEFAULT 0,       -- sells production off a rate card
  lang TEXT, lang_src TEXT,          -- 'bio' beats 'hashtag'
  region TEXT,
  quoted_rate TEXT,            -- what THEY asked for, verbatim — the funnel audit
  status TEXT,                 -- see state machine below
  notes TEXT, created_at INTEGER
);

CREATE TABLE contacts (            -- one creator can have several
  id INTEGER PRIMARY KEY, influencer_id INTEGER, kind TEXT,  -- email|telegram
  value TEXT, source TEXT,
  email_ok INTEGER, email_note TEXT,  -- validation result
  UNIQUE(influencer_id, kind, value)
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY, influencer_id INTEGER,
  direction TEXT,              -- out|in
  kind TEXT,                   -- intro|offer|brief|followup1|decline|reply|manual
  subject TEXT, body TEXT,
  status TEXT,                 -- draft|sent|received|discarded
  attachment TEXT,             -- path to a PDF, if any
  translation TEXT,            -- cached English translation for review
  gmail_id TEXT,               -- Message-ID: makes inbox sync idempotent
  created_at INTEGER, sent_at INTEGER
);

CREATE TABLE deals (
  id INTEGER PRIMARY KEY, influencer_id INTEGER,
  videos_count INTEGER, price_usd REAL, upfront_usd REAL,
  bonus_per_step REAL, bonus_cap REAL, created_at INTEGER
);

CREATE TABLE videos (            -- delivered content, for the payout loop
  id INTEGER PRIMARY KEY, influencer_id INTEGER, deal_id INTEGER,
  url TEXT UNIQUE, platform TEXT,
  posted_at INTEGER, views INTEGER,
  views_checked_at INTEGER, views_locked INTEGER DEFAULT 0,
  bonus_paid_usd REAL DEFAULT 0
);

CREATE TABLE log (id INTEGER PRIMARY KEY, influencer_id INTEGER,
                  event TEXT, detail TEXT, at INTEGER);
```

**State machine.** `new → enriched → ready → contacted → replied → negotiating →
agreed → producing → published → paid`, with `no_contact` / `skipped` /
`rejected` / `dead` as exits. Two rules that keep the UI honest: a row with a
pending draft always sorts to the top (it's the only place a human is needed),
and anything that ends with a real conversation goes to a **History** view
rather than vanishing — decline reasons are the funnel's audit trail.

## Pricing

```python
BASE_PER_VIDEO      = 25    # 75 for creators whose typical video does 50k+
BONUS_PER_STEP      = 25
BONUS_STEP_VIEWS    = 25_000
MAX_TOTAL_PER_VIDEO = 500   # the whole payout, not just the bonus
VIEW_LOCK_DAYS      = 14

def per_video(actual_views, creator_median):
    base = 75 if (creator_median or 0) >= 50_000 else 25
    bonus = BONUS_PER_STEP * (actual_views // BONUS_STEP_VIEWS)
    return min(base + bonus, MAX_TOTAL_PER_VIDEO)
```

**Calibrating the step to your own database.** The step should be reachable by
~25% of your database on a typical video, and at the step the deal should equal
your target CPM. In the source run: a 10k step was hit by 47% but cost $3 per
thousand views (too rich), 50k by 16% (decorative), 25k by 27% at exactly
$2/1000 — the target. Recompute this from your own median distribution;
copying `25_000` blindly is the one number here that doesn't transfer.

**Why a cap at all**, and why it's the *total*: it bounds a viral video's
liability while still paying properly — at the cap a thousand views costs about
$1, half your baseline. Announce it as "up to $500 per video"; it's the number
creators notice first.

**Tiered base.** A creator whose typical video does 100k views reads a $25 base
as a typo. One tier ($25 / $75 at a 50k-median boundary) keeps "one scale for
creators your size" a true sentence in every email — say *that*, never "one
scale for everyone", or two creators comparing notes will catch you.

## Scoring

```python
def expected_rate(median_views, followers, is_seller):
    """What the creator thinks they're worth."""
    by_views     = median_views / 1000 * CPM_USD          # ~$2 in the US
    by_followers = followers / 1000 * 2.0                 # brands pay "by size"
    exp = max(by_views, by_followers)
    if is_seller:
        exp = max(exp, UGC_PRODUCTION_RATE)               # ~$220, median of live rate cards
    return exp

def p_reply(is_seller, followers, is_agency):
    p = 0.40 if is_seller else 0.08                       # measured, recalibrate at ~50 emails
    if is_agency:      p *= 0.5
    if followers > 200_000: p *= 0.6
    return p

def p_accept(median_views, followers, is_seller):
    ours = per_video(median_views, median_views)
    exp  = expected_rate(median_views, followers, is_seller)
    return 1.0 if exp <= ours else max(ours / exp, 0.05)

def score(median_views, followers, is_seller, is_agency, views_checked):
    cost = per_video(median_views, median_views)
    per_dollar = median_views / cost
    er = median_views / followers if followers else 0
    upside = 0.5 if er >= 15 else 1.25 if er >= 1 else 1.1 if er >= 0.5 else 1.0
    s = per_dollar * p_reply(is_seller, followers, is_agency) \
                   * p_accept(median_views, followers, is_seller) * upside
    if 2_000 <= median_views <= 100_000 and followers <= 60_000 and not is_seller:
        s *= 1.5           # the segment every signed deal came from
    if not views_checked:
        s *= 0.4           # a number you haven't verified shouldn't lead the queue
    return round(s)
```

Two detectors the formula depends on:

```python
SELLER_MARKERS = ("collab", "ugc", "booking", "brand", "contact")   # in the email local part
AGENCY_MARKERS = ("mgmt", "manag", "talent", "agency", "agence",    # localize these!
                  "agencia", "agentur", "agent", "group", "media.", "partners")
```

`agence` / `agencia` / `agentur` matter: an English-only keyword list let a
French agency address through as a personal one in the source run.

## Email validation before sending

Three layers, no dependencies — the third one needs `dig`:

1. **Syntax** — a plain regex.
2. **Typo domains** — a hand-kept dictionary: `gmai.com`, `gmial.com`,
   `hotmial.com`, `outlok.com`, `yaho.com`, `iclod.com`… These are not
   harmless mistakes; several are live typosquatters that will deliver your
   email to a stranger. Reject, don't autocorrect.
3. **MX / A record** — a domain that can't receive mail eats the message
   silently and pollutes your bounce rate. Skip the lookup for known mailbox
   providers, cache the rest.

Wire it in three places: a hard guard inside `send_message()`, a filter on the
queue view, and a preference for the valid address when a creator has several.

## Email templates

Keep one template file **per language** and detect the language from the bio,
not from the hashtag you found them under. The four that matter:

**intro** — compliment, one-line product, who you are (small and human), the
rate question. No links, no attachments.

**offer** — the sequence matters:
1. Who you are and why the base is modest — *before* any number.
2. The scale: base + per-N-views + cap, and an illustrative total from their
   own recent views.
3. **The work is small**: ~20 minutes, their reaction plus a demo clip you
   prepare, no script, no draft approvals. Put this *before* the asks.
4. The asks: live within N days, answer comments for the first week.
5. What they keep: the video, the rights, no exclusivity.
6. Close on **one** video.

**brief** — 4–5 concepts, each with a concrete opening shot, explicitly framed
as *ideas, not requirements*, always including "something else entirely". Add
the two lines that unblock most creators: you can prepare the in-app footage
(or even edit the whole video), and they never have to open the app if they
don't want to.

**decline** — one warm paragraph, never a counter-argument about their number:
*"that's a fair rate for your work, it's just beyond us at this stage"*, plus a
door left open. Send it once and stop; a second counter from you turns a clean
no into a haggle.

## The payout loop

The half everyone forgets to build. Ship it before the first video goes live:

```
inbound email → detect video URLs → videos row (posted_at)
day == posted_at + VIEW_LOCK_DAYS
  → re-scrape the video's current views
  → views_locked = 1, bonus = per_video(views, median) - base
  → report what's owed, pay, log it
```

Locked numbers are never recomputed — that's the promise made in the email, and
it's what makes the deadline credible in both directions.

## Deliverables to generate per creator

A one-page agreement PDF in **their language plus English** (two pages, one per
language) reads as respect and costs nothing to produce. Non-obvious clauses
are listed in SKILL.md Step 7 — the one to highlight visually is *organic views
only, no paid boost*, because it's the clause that protects the number your
bonus is computed on.

If you generate PDFs with ReportLab and a system serif (Charter is a good
Cyrillic-capable default on macOS): **arrows and checkmarks are not in most
serif faces** — `→` and `✓` render as empty boxes. Use `»`, or set marker
glyphs in a font you've verified.
