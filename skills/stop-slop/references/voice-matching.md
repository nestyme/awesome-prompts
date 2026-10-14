# Matching a specific person's voice

A neutral rewrite removes what makes text sound like a machine. A voice match adds what makes it sound like one particular person. The two are different jobs: neutral prose from a skilled editor is still nobody's voice.

## Why a profile instead of "write like this sample"

Asked to imitate a sample by feel, a model grabs the most visible features (a catchphrase, the lowercase, one memorable joke) and overuses them. The result is a caricature: recognizable and wrong. A profile forces you to measure the quieter features that actually carry a voice, such as typical sentence length, how a paragraph opens, how certain the writer sounds, and what they never do. Then you write to match those distributions.

## What makes a good sample

- **Written by the person without AI help.** If the sample has AI patterns in it, you'll be matching a machine. Say so if you notice.
- **Same genre as the target, if possible.** People write emails, tweets, and essays differently. A tweet sample won't tell you how they write a long newsletter.
- **Enough of it.** 300+ words total is a useful minimum; 1,000+ is better. Two or three short pieces beat one long one, because you can tell habits from one-offs.
- **Recent.** Voices drift.

Messages, emails, Slack threads, old posts, and transcripts of the person talking all work. Transcribed speech is often the best source for someone who "doesn't write".

If the samples come from different genres, note which features are shared across them (those are the voice) and which belong to one genre (those are the channel).

## The profile

Read the sample twice: once normally, once measuring. Fill in what the sample supports; leave out what it doesn't.

| Dimension | What to look at | Example observations |
|---|---|---|
| Sentence length | Typical length and the spread. Count a few paragraphs. | "Mostly 8-14 words, with an occasional 30-word sentence that lists things." |
| Paragraphing | Length, and how paragraphs open | "1-3 sentences. Opens with the fact, not context." |
| Openings | How a piece starts | "Starts mid-situation, no greeting or setup." |
| Endings | How a piece ends | "Ends on a direct ask." / "Ends on a wry one-liner." |
| Register and vocabulary | Plain vs. elaborate, slang, jargon, swearing, Latinate vs. Anglo-Saxon words | "Plain, technical where needed, distrusts buzzwords (puts them in quotes)." |
| Punctuation | Dashes, parentheses, semicolons, colons, exclamation marks, ellipses, capitalization | "All lowercase. Commas and colons, no dashes. Never uses exclamation marks." |
| Person and address | I / we / you; how they refer to the reader | "First person singular. Talks to the reader as a peer." |
| Certainty | How they handle claims and doubt | "States things flatly. Admits unknowns briefly: 'no idea yet'." |
| Humor | Type and frequency | "Dry understatement, about once a paragraph, often in parentheses." |
| Detail | What kinds of specifics they reach for | "Numbers with before/after. Device names. Prices." |
| Formatting | Lists, headers, bold, emoji, links | "Never uses lists, even when listing things." |
| Spelling and dialect | US/UK, idioms | "British: jumper, colour, 'reckon'." |
| Signature moves | Recurring constructions or phrases | "Tends to undercut a win with a small qualifier: 'I'll take it.'" |
| Never does | Conspicuous absences | "No rhetorical questions. No motivational language." |

Show the user a short version (3 to 6 bullets, the most distinctive dimensions) alongside the rewrite. They know their voice better than any profile, and a wrong bullet is quick for them to correct.

## Procedure

1. **Build the profile** from the sample.
2. **Extract the meaning** of the text you're rewriting (the same step 1 as in SKILL.md).
3. **Draft against the profile.** Check the dimensions as you write: does this paragraph open the way they open theirs? Is this sentence length in their range? Would they use this word?
4. **Compare side by side** with the sample, paragraph by paragraph. Fix what drifts.
5. **Run the stop-slop checklist,** with exceptions only where the profile shows the author really does that thing (if they use em dashes, keep em dashes).

## Pitfalls

- **Flatness.** The opposite failure, and the more common one after a stop-slop pass: the rewrite is clean and correct and sounds like nobody. Caution about inventing facts doesn't mean avoiding the author's moves. If they open inside a concrete scene, open inside one (a hypothetical or general scene is fine when the draft has no real one; just don't present it as something that happened to them). If they're wry, be wry about this subject. Test: would a regular reader recognize the author without the byline?
- **Caricature.** Using a signature phrase every paragraph, or turning every sentence into their kind of joke. Use a signature move at most once or twice per piece, about as often as they do.
- **Importing content.** The sample is evidence of style, not a source of facts. Don't reuse its anecdotes, opinions, examples, or named people in the new text, unless the user asks. (In the worked example below, the "nine navy jumpers" would be tempting to reuse. Don't.)
- **Matching their mistakes.** Typos and grammatical slips aren't voice. Leave them out unless the user asks for them.
- **Matching AI tics in the sample.** If the sample is itself full of slop, ask whether to match it or to keep the voice and drop the tics.
- **Overfitting to one piece.** If there's only one short sample, treat the profile as tentative and say so.
- **Overriding the channel.** A person's tweets in a formal grant application won't work. Match the voice within the norms of the target genre.

Imitating a writer the user admires (for practice, pastiche, or a ghostwritten piece they'll sign) is fine. Don't produce text meant to pass as another real person's own statement, such as a quote or endorsement they never gave.

---

## Worked example

Both samples below are invented to show the method.

### The text to rewrite

> After careful consideration, we've made the decision to transition our newsletter to a monthly cadence. This change will allow us to deliver more in-depth, high-quality content that truly adds value to your inbox. We're excited about this new chapter and grateful for your continued support!

Meaning: the newsletter is going from weekly to monthly, so that each issue has more in it.

### Neutral rewrite

> The newsletter is going monthly. Weekly was too often to have something worth sending every time, so each issue will now be longer and, we hope, better.

### Voice A: Maya (founder's product newsletter)

**Sample**
> we shipped the new search on tuesday. it's faster. not "feels faster", actually faster: 3.8s to 0.9s on a five-year-old laptop. the trick was boring, we stopped loading every thumbnail up front.
>
> support tickets about search went from ~40 a week to 6. i'll take it.
>
> next up is search in spanish. we've been putting this off for a year because sorting is a mess (does "ñ" come after "n"? depends who you ask). if you've built this before, i want to hear how.

**Profile (as shown to the user)**
- All lowercase; short paragraphs of one to three sentences.
- Numbers first, as before → after.
- Dry understatement, often undercutting a win ("i'll take it").
- Distrusts vague claims and puts them in quotes; jokes in parentheses.
- Ends on a direct ask to the reader.
- No exclamation marks, no em dashes, no adjectives of praise.

**Rewrite**
> this newsletter is going monthly. weekly meant some issues didn't have much in them (you noticed, i'm sure). monthly, each one should.
>
> [one sentence on what a monthly issue will have that a weekly one didn't.]
>
> if you liked weekly better, tell me. i might be wrong about this.

Note: her "not X, actually Y" construction is a real habit, but this text doesn't need it, so it isn't forced in. The closing ask is hers; in a neutral rewrite it would be a template, but here it's voice.

### Voice B: Tom (personal essay newsletter)

**Sample**
> I've never been good at getting dressed. My mother, who could make a cardigan look like a decision, used to watch me come down the stairs in the morning with the patient expression of someone reading a badly translated menu. I am forty-one now and I still own, by my count, nine navy jumpers, which is either a uniform or a cry for help, and I've stopped being sure which.
>
> So when a friend suggested I let an app tell me what to wear, I laughed, and then, a week later, downloaded it anyway.

**Profile (as shown to the user)**
- Long, cumulative sentences with subordinate clauses, balanced by short plain ones.
- Self-deprecating; the joke is usually on himself.
- Similes from ordinary domestic life ("a badly translated menu").
- British English; commas and parentheses, no dashes.
- Paragraphs end on a wry turn rather than a conclusion.

**Rewrite**
> From now on this newsletter will arrive once a month rather than every week, which will come as a relief to those of you who have been politely archiving it unread, and, I hope, as a small disappointment to the rest. Writing it weekly had started to feel like being asked to say something interesting at the same dinner party every seven days. Once a month, I think I can manage.

Note: the nine jumpers, the mother, and the menu all stay in the sample. The rewrite borrows the sentence shapes, the domestic simile, and the self-directed joke, not the content.
