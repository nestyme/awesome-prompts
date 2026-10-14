---
name: stop-slop
description: Rewrite any English text so it stops sounding machine-written. Diagnoses LLM writing patterns (inflated significance, "it's not X, it's Y", rule-of-three padding, hedging, signposting, "-ing" significance tails, synonym cycling, bullet/bold/em-dash overuse, chatbot pleasantries, words like delve/tapestry/leverage) by root cause, then rewrites from the meaning into plain, specific, human prose. Can match a specific person's voice from a reference sample. Use whenever the user wants English text humanized, de-AI'd, de-slopped, tightened, or made to sound less like ChatGPT, less robotic, less generic, more natural; when they paste any draft to improve (post, email, cover letter, product copy, docs, essay, story, speech, paper, newsletter); when they want text in their own voice or in someone's style; when they ask whether a text sounds AI-written; and when drafting English text for publication.
---

# Stop Slop

Slop is text that has the shape of writing without a writer making choices. Every sentence is grammatical and nothing is wrong, yet a reader feels within two lines that nobody meant it. This skill removes that feeling by fixing what causes it, not by deleting a list of words.

## The core idea: patterns are symptoms

Each LLM tic has a cause. Delete the surface pattern and the cause grows a sibling: ban "delve" and you get "dig into"; ban em dashes and you get a colon in every sentence; ban "it's not X, it's Y" and you get "X? No. Y." So diagnose the cause, then fix the cause.

| # | Cause | What it produces | The fix |
|---|---|---|---|
| 1 | **Pull toward the most probable phrasing.** A model predicts likely continuations, so it drifts to the phrase that fits the most contexts. Specifics are improbable; generalities are safe. | Generic claims, clichés, abstract nouns ("enhance the overall experience"), stock metaphors (journey, landscape, tapestry), brochure adjectives. | **Specificity.** Replace the category with the instance: the number, the name, the actual thing that happened. |
| 2 | **Rewarded for looking helpful at a glance.** Preference training uses raters who compare answers quickly. Structure, completeness, and enthusiasm win at a glance. | Headers, bold, bullets, triads, recaps, "comprehensive" coverage, exclamation-level enthusiasm. | **Write for a reader who reads every word.** Prose by default; structure only when the content is a list or a reference. |
| 3 | **Penalized for being wrong or one-sided.** Safety and accuracy training make every claim cheaper to qualify than to commit to. | Hedge stacks ("may potentially"), reflexive both-sidesing, "it's important to note", disclaimers. | **Commit.** Hedge only where there's real uncertainty, once, and say what is uncertain. |
| 4 | **No stake and no taste.** The model doesn't know which detail matters, so it marks everything as mattering, and it has no position of its own. | Significance inflation ("pivotal", "a testament to", "transformative"), narrator-from-nowhere voice, no opinions. | **Decide what matters and say why.** Let small things be small. Cut the rest. |
| 5 | **Absorbed genre templates.** Training data is heavy with marketing copy, SEO posts, LinkedIn, school essays, TED-style talks. | "In today's fast-paced world", "Here's the thing:", "The result?", "Let's dive in", "In conclusion", hook-then-reveal. | **Name the template and step out of it.** Start with the point. |
| 6 | **Sentence-by-sentence generation with a weak model of the reader.** Each sentence tries to close itself; the model can't tell the reader already got it. | Paragraphs ending in a moral, "-ing" tails that restate significance, signposting, recaps, explaining the obvious. | **Trust the reader.** End the paragraph when its content ends. |
| 7 | **Trained-in repetition avoidance and uniformity.** | Synonym cycling ("the company... the firm... the tech giant"), relentless parallelism, metronome rhythm, or its newer opposite: staccato fragments for drama. | **Repeat the key noun. Let rhythm follow the content.** |
| 8 | **The assistant persona.** The text was produced as a reply to someone. | "Great question!", "I hope this helps", "Let me know if...", "Certainly!", flattering warmth. | **Remove the chat frame.** The text is not a reply. |

When you diagnose a draft, name the cause for each cluster of patterns. That tells you what to write instead, which a banned-word list never does.

## Workflow

1. **Read for meaning first.** Before touching a sentence, write down (for yourself) the one to three things the text actually claims, asks, or announces. Who reads it, and what should they think or do afterwards? If you can extract almost nothing, the draft is mostly padding and the rewrite will be much shorter. That's the correct outcome.

2. **Fix the target voice.** Genre, channel, audience, register. A LinkedIn post, a cold email, a README, and a short story have different norms (see "Genre norms" below). If the user supplied a writing sample, build a voice profile first (see "Matching a specific person's voice"). Ask a question only if the channel or audience is truly unclear and it would change the rewrite; otherwise infer and say what you assumed.

3. **Diagnose.** Scan with the pattern map below and `references/patterns.md`. Look for clusters, not single words. One "crucial" means nothing. Three inflated adjectives, a triad, and an "-ing" tail in one paragraph is the tell. For each cluster, name the cause.

4. **Rewrite from the meaning, not from the sentences.** Line-editing a slop draft keeps its skeleton: the hook, the triad, the moral at the end. Write a fresh draft from the claims you extracted in step 1, using the original as a source of facts rather than of structure. Keep every fact, number, name, link, and real claim. If the original's order serves the reader, keep the order.

5. **Never invent facts to sound human, but don't write flat either.** No made-up anecdotes, numbers, customer quotes, credentials, or "I remember when..." presented as true: fabricated specifics are worse than vague ones. That rule covers factual claims about the author, the company, real people, and events. It doesn't cover style. A hypothetical addressed to the reader ("the gym membership you bought in January and used twice"), a simile, a joke, or a generic illustration is writing, not fabrication, and it's often what makes the text sound like a person. Use them, especially when matching a voice. In fiction, invented concrete detail is the craft itself: replace stock images with specific ones, but don't change plot facts (who did what, what happened), and say which details are your suggestions.

   **Placeholders.** When the original makes a vague claim that only a specific could fix (`"rapidly growing"`, `"valuable insights"`), cut it if the text works without it; if the text doesn't work without it, replace it with a bracketed placeholder, e.g. `[how many customers signed up in week one]`. Don't add placeholder slots for content the original never had (deal terms, a new section). Put those in a short "you could also add" note instead, two or three items at most. Write each placeholder so the text still reads correctly if the author simply deletes it. The goal is a text that's usable as delivered and better once filled in. The exception is a genre that's worthless without specifics the source lacks (a "lessons learned" post, a personal essay): there a skeleton with placeholders, or questions for the author, is the right output.

6. **Audit the rewrite** with the checklist at the bottom. Then read it aloud in your head: would a competent person say this to a colleague they respect? Wherever you'd stumble or wince, fix it.

7. **Deliver** in the output format below.

## What natural English prose does

Avoiding patterns isn't enough; the rewrite needs positive qualities.

- **Specific over general.** "Cut onboarding from 9 screens to 4" beats "streamlined the onboarding experience".
- **Verbs over nouns.** "We decided" beats "a decision was made"; "we tested" beats "the implementation of testing".
- **Plain words.** use, help, start, show, about, but, so, get, need, try, make. Latinate words where they're the precise term, not as decoration.
- **Contractions** (it's, don't, we're) in anything that isn't legal, academic, or deliberately formal. Their absence is one of the strongest "machine" signals in casual English.
- **Claim first, then support.** Readers forgive bluntness faster than throat-clearing.
- **Rhythm that follows thought.** A long sentence when a chain of reasoning needs it; a short one when a point lands. Not engineered variety, and not every line a fragment.
- **The same name for the same thing,** every time.
- **Paragraphs as long as the thought,** which means uneven lengths.
- **Opinions with reasons, and uncertainty with specifics** ("we don't know yet whether it holds for enterprise customers").
- **Endings that stop.** The last sentence carries information or an ask, not a moral.
- **Formatting only where the reader will scan:** docs, instructions, comparisons, changelogs. Emails, posts, essays, bios, and letters are prose.

## Genre norms

The causes are the same everywhere, but what "natural" means depends on the genre. Formal isn't slop, and lists aren't slop where readers scan.

| Genre | What the reader needs | Typical slop | What the rewrite needs |
|---|---|---|---|
| Social posts (LinkedIn, X, Threads) | One idea, backed by a story or a number | Hooks, fragments, emoji bullets, "thrilled to announce", engagement bait | The real story or number, a plain first line, a specific question if any |
| Cold emails, outreach, pitches | Why them, what you want, how to answer | Pleasantries, generic praise, "explore a potential collaboration" | One specific reason, a concrete ask, an easy reply |
| Work messages (Slack, memos, status updates) | The decision or the ask | "Circle back", "align", "let me know your thoughts" | A proposal and a deadline |
| Marketing and product copy | What it does, for whom, one checkable fact | Brochure adjectives, "elevate", "No X, no Y, just Z", unverifiable superlatives | The concrete function; specs as a list where people scan |
| Technical docs, READMEs, release notes | What it does and how to use it | "Powerful, flexible, easy-to-use", emoji headings, "blazing fast" | Commands, specifics, numbers; headings and lists are right here |
| Academic and research writing | Method and findings | delve, underscore, pivotal, "pave the way for future research" | Keep the formal register; make every sentence carry content |
| Cover letters, résumés, bios | Evidence of what the person did | "Proven track record", "spearheaded", "passionate about" | Results with numbers, one real reason for this employer |
| Essays, personal writing, speeches, toasts | The author's actual moments | Abstractions about the experience, journeys, morals | The author's details; ask them questions rather than invent |
| Fiction | Particular images, action over named emotion | Stock scenes (rain on the window, cold coffee), "couldn't help but feel", "a wave of X washed over her" | Specific detail and action; invented detail is allowed here, plot changes aren't |
| Support replies and customer messages | Acknowledgement of their actual problem and a next step | Performed empathy, "rest assured", hedged workarounds, "The Team" | The problem in their words, a plain instruction, a named person |

Examples for each of these are in `references/examples.md`.

## Pattern map (quick reference)

Full catalog with causes and before/after examples for every pattern: `references/patterns.md`. Word-level list with plain replacements: `references/vocabulary.md`. Whole-text rewrites across genres: `references/examples.md`. Read `patterns.md` on first use in a session; it's where the judgment lives.

| Pattern | Looks like | Fix |
|---|---|---|
| Significance inflation | "marks a pivotal moment", "stands as a testament to", "plays a crucial role" | Say what happened. If it matters, show the consequence. |
| Brochure register | "nestled", "boasts", "vibrant", "seamless", "cutting-edge", "elevate your" | Describe the thing plainly. Let a fact do the selling. |
| "-ing" significance tail | "..., highlighting the importance of X" / "ensuring a seamless experience" | Cut it, or make it a real sentence with a real causal claim. |
| Negative parallelism | "It's not just X, it's Y", "X isn't about A. It's about B." | State Y. Keep the contrast only if readers actually believe X. |
| "No X, no Y, just Z" | "No fluff. No jargon. Just results." | Say what it is. |
| Rule of three | "fast, reliable, and scalable"; three-beat sentences everywhere | Count the real items. Two is fine. One is fine. |
| Q-then-answer reveal | "The result? 40% more signups." "Why does this matter?" | Plain statement. |
| Announcement colon | "Here's the thing:", "The kicker:", "The truth is:" | Delete the announcement; say the thing. |
| Throat-clearing opener | "In today's fast-paced world", "In an era where", "When it comes to" | Start with the point. |
| Dramatic fragments | "And it worked. Beautifully." "Let that sink in." one-line paragraphs | Join into normal sentences; keep one short line if it earns it. |
| False range | "from boardrooms to bedrooms", "from beginners to seasoned pros" | Name the actual scope or drop it. |
| Hedge stack | "may potentially help to some extent" | One hedge, on the real uncertainty, or none. |
| Reflexive balance | "While X offers benefits, it's important to consider..." | Take a position, or present the trade-off concretely. |
| Importance markers | "It's important to note", "It's worth mentioning", "Keep in mind" | Delete; if it's important, the content shows it. |
| Signposting | "Let's dive in", "In this post, we'll explore", "Let's break it down" | Delete; start the content. |
| Moral/recap ending | "Ultimately, ...", "In conclusion", "At the end of the day", "By doing X, you'll Y" | End on the last piece of information or the ask. |
| Transition stacking | "Moreover", "Furthermore", "Additionally" opening consecutive sentences | Delete most; use "and", "but", "so", or nothing. |
| Copula avoidance | "serves as", "stands as", "functions as", "boasts", "features" | "is", "has". |
| Synonym cycling | "the app... the platform... the tool... the solution" | Pick one name and repeat it. |
| Nominalization | "the utilization of", "facilitate the implementation of" | Use the verb: "use", "help", "build". |
| Vague attribution | "Experts say", "Studies show", "Many believe" | Name the source, or own the claim, or cut it. |
| Generic universal reader | "Whether you're a beginner or a seasoned pro" | Write to the actual reader. |
| Stock metaphor | journey, landscape, tapestry, beacon, navigate, unlock, ecosystem | Literal description. |
| Emotional labeling | "I'm thrilled to announce", "We're incredibly excited" | Announce. Let the reader decide how exciting it is. |
| Sincerity/intensity markers | "truly", "genuinely", "honestly", "incredibly", "deeply" | Delete; they signal the opposite. |
| The "quiet/honest" family (2024-26) | "quietly", "the quiet power of", "the honest answer", "real trade-offs", "load-bearing", "doing a lot of work" | Delete the decoration; say the claim. |
| Contrarian hook | "Most people think X. They're wrong." | State your view and the reason. |
| Formatting leakage | headers/bold in a 200-word post, "**Speed:** ..." bullets, emoji bullets, Title Case Headings | Prose. Sentence-case headings where headings belong. |
| Em dash density | several "—" per paragraph | Default to none; use the mark that fits the job (comma, period, parentheses). |
| Chatbot residue | "Great question!", "I hope this helps", "Feel free to reach out", "Let me know if you'd like" | Delete. |
| Uniform rhythm | every sentence 15-20 words, every paragraph 3 sentences | Vary because content varies. |

## Don't overcorrect

Over-cleaned text has its own tells, and some of the popular "anti-AI" rules make writing worse.

- **Synonym swapping isn't rewriting.** "Delve" → "dig into" leaves the sentence's skeleton, which is what readers actually detect.
- **Don't trade em dashes for colons and semicolons wholesale.** Choose by function: an aside goes in commas or parentheses, a new thought gets a period, an explanation might get a colon. More than one colon-reveal per piece is a new tic.
- **Presence isn't the tell; density is.** Humans use "additionally", passive voice, adverbs, "crucial", and triads. Keep them where they're the right tool. Don't delete every adverb or every passive sentence because a rulebook said so.
- **Don't strip real hedges.** If the claim is genuinely uncertain, the hedge is information.
- **Don't fake humanity.** No inserted typos, forced slang, "lol", random lowercase, fake vulnerability ("I'll be honest, I almost gave up"), or invented anecdotes. That is "humanized slop", and readers spot it fast.
- **Don't go staccato.** The common overcorrection is: Short lines. Fragments. Every sentence its own paragraph. That reads as LinkedIn-bro slop.
- **Don't flatten an actual voice.** If the author's sample shows flourishes, long sentences, or em dashes, those are theirs. Keep them.
- **Don't change meaning, register, or required content.** A legal notice stays formal. A CTA stays. A required disclaimer stays.
- **Formal isn't slop.** Academic or technical prose can be clean and still formal: precise terms, no inflation, claims with evidence.

## Matching a specific person's voice

A neutral rewrite removes the machine. A voice-matched rewrite makes the text sound like one particular person. Full method, profile template, and a worked example in `references/voice-matching.md`.

**When to ask for a reference text.**
- The user says "in my voice", "make it sound like me", "like [person]", or the text is personal (founder post, personal bio, newsletter, a message signed by them) and they seem to care how it sounds. If they gave no sample, ask for one: 1 to 3 pieces in the same genre if possible, 300+ words in total, written without AI help. Old emails, posts, Slack messages, and transcripts of them talking all work.
- Otherwise, don't block on it. Do the neutral rewrite and offer once, at the end, in one line: "If you send a sample of your own writing, I can match your voice instead of a neutral one."

**How to use a sample.**
1. Build a voice profile across the dimensions in `voice-matching.md`: sentence length and spread, how paragraphs open, register and vocabulary, punctuation habits, person (I/we/you), humor, how they handle certainty, formatting habits, spelling variety (US/UK), signature moves, and things they never do.
2. Show the user a short version of the profile (3 to 6 bullets) along with the rewrite, so they can correct it.
3. Write against the profile. Match its distributions, not its phrases. Use a signature phrase at most once, or the result becomes a caricature. The bar is recognition: someone who reads the author regularly should recognize them in the rewrite. A clean, neutral rewrite fails this mode. If the author opens inside a concrete moment and the draft has none, open inside a hypothetical or general one in their manner; if they're wry, be wry about the draft's subject.
4. Don't import facts, opinions, or anecdotes from the sample into the new text.
5. Compare the result with the sample side by side and fix what drifts.

If the sample itself is full of AI patterns, say so and ask whether to match it anyway or to keep the voice and remove the tics. Imitating the style of a writer the user admires is fine. Don't produce text meant to pass as a real third party's own statement (fake quotes, fake endorsements).

## Output format

Default:

**Rewrite**

(the rewritten text, formatted for its channel)

**What changed**
3 to 5 bullets, most impactful first, each one or two sentences: name the pattern, quote a short fragment of the original, say what you did. Group small fixes into one bullet. The explanation should be shorter than the rewrite; the user came for the text.

**Needs your input** (only if you left `[placeholders]`; one line each)

Variants:
- **"Just the text"**: give only the rewrite.
- **Audit** ("does this sound like AI?", "what gives it away?"): verdict in one line, then the clusters with quoted evidence, the cause, and the fix. No rewrite unless asked.
- **Several options** (headlines, hooks, subject lines): give 3 to 5 that differ in approach, not in synonyms.
- **Long documents**: rewrite everything; don't summarize or skip sections. For very long texts, go section by section and keep terminology consistent across sections.
- **Writing from scratch** (no draft): apply the same principles while drafting, then run the checklist before showing it.

Reply to the user in the language they wrote to you in; the rewrite stays in English.

## Final checklist

- The first sentence carries content (no throat-clearing, "In today's...", "Imagine...", or question hook unless the author's voice does that).
- No "not X, but Y" / "it's not just X" unless X is a belief the reader actually holds.
- Every list of three really has three distinct items.
- No sentence ends in an "-ing" phrase commenting on significance.
- No inflation word (pivotal, testament, transformative, landscape, crucial...) standing in for a specific claim.
- Each remaining hedge marks a real, specific uncertainty.
- No paragraph ends in a moral or a recap.
- The same thing has the same name throughout.
- Em dashes: zero by default, one at most, unless the voice sample uses them. Colon reveals: one at most.
- Sentence lengths vary; neither all fragments nor all medium.
- Formatting fits the channel.
- No chatbot residue.
- Contractions wherever a person would use them.
- Every fact from the original survived; nothing was invented.
- It's shorter than the original, unless the original lacked necessary specifics.
