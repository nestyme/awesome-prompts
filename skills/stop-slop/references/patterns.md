# Pattern catalog

Patterns are grouped by root cause (the cause table is in SKILL.md). Each entry gives the tell, the cause, the fix, when the pattern is fine, and before/after pairs from different kinds of writing.

**About the examples.** The "after" versions show the direction of a fix. Some use concrete numbers or details to show what good looks like; those details are illustrative. In a real rewrite, every specific must come from the source text or go into a `[placeholder]` for the author. Never fill the gap with invented facts. "Acme" and every person, company, and number in the examples are made up.

**Density, not presence.** Almost every pattern here appears in good human writing too. One triad, one "crucial", or one em dash proves nothing. Fix clusters, and fix any instance where the pattern stands in for content the sentence should have had.

## Contents

- **A. Empty content** (the most-probable-phrasing pull; no stake)
  A1 Significance inflation · A2 Brochure register · A3 Vague abstractions · A4 "-ing" significance tails · A5 Vague attribution · A6 Challenges-and-outlook ending · A7 Stock metaphors · A8 The universal reader · A9 Emotional labeling
- **B. Borrowed rhetoric** (genre templates; looking insightful)
  B1 Negative parallelism · B2 "No X, no Y, just Z" · B3 Rule of three · B4 Question-then-answer reveal · B5 Announcement colon · B6 Throat-clearing openers · B7 Dramatic fragmentation · B8 False ranges · B9 Manufactured twist · B10 Contrarian hook · B11 "This is where X comes in" · B12 Engagement-bait closer
- **C. Over-qualification** (penalty avoidance)
  C1 Hedge stacking · C2 Reflexive balance · C3 Importance markers · C4 Sincerity and intensity markers
- **D. No model of the reader** (sentence-by-sentence generation)
  D1 Signposting · D2 Moral and recap endings · D3 Transition stacking · D4 Explaining the obvious
- **E. Word-level habits**
  E1 AI vocabulary clusters · E2 Copula avoidance · E3 Synonym cycling · E4 Nominalization · E5 Missing contractions · E6 False agency · E7 The quiet/honest/real family · E8 Critic-speak
- **F. Rhythm**
  F1 Metronome sentences · F2 Parallelism everywhere
- **G. Formatting** (skim-rewarding; markdown habits)
  G1 Headers and bold in short text · G2 Inline-header bullets · G3 Bullets for non-list content · G4 Emoji as structure · G5 Em dash density · G6 Title Case Headings
- **H. Chatbot residue** (the assistant persona)
  H1 Assistant openers and closers · H2 Sycophantic validation · H3 Knowledge and sourcing disclaimers · H4 Template placeholders left in

---

## A. Empty content

### A1. Significance inflation

**Tell:** "marks a pivotal moment", "stands as a testament to", "plays a crucial/key/vital role", "underscores the importance of", "a significant milestone", "reshaping the landscape", "leaves an indelible mark", "setting the stage for", "a turning point", "a defining moment".

**Cause:** The model can't judge which detail matters, so it marks everything as mattering. And in training data, the things people write about at length (famous companies, landmarks, historical events) are described in glowing language, so that register becomes the default for anything.

**Fix:** Say what happened. If it really matters, show why with a consequence, a number, or a comparison. Usually, just cut the significance claim and let the reader decide.

**Fine when:** You have evidence and the significance is the point: "It was the first time a US court ruled that..."

> **Before:** The release of version 3.0 marks a pivotal moment in our journey and stands as a testament to our commitment to developers.
> **After:** Version 3.0 is out. The main change: builds that took 40 seconds now take 6.

> **Before:** The bakery has played a crucial role in the local community, serving as a beloved gathering place for generations.
> **After:** The bakery has been on Elm Street since 1962. On Saturday mornings the line goes out the door.

> **Before:** This grant underscores the growing importance of digital literacy in rural communities.
> **After:** The grant pays for two trainers and forty laptops at the county library.

### A2. Brochure register

**Tell:** nestled, boasts, vibrant, bustling, rich (history/heritage/culture), stunning, breathtaking, seamless, cutting-edge, state-of-the-art, world-class, unparalleled, elevate, curated, effortless, in the heart of, a must-visit, renowned, iconic, sun-drenched.

**Cause:** Travel guides, real estate listings, and press releases are a huge share of descriptive text online. When the model describes anything, the most probable register is a sales one.

**Fix:** Describe plainly and let one well-chosen fact do the selling. Praise adjectives are claims the reader can't check. Facts are claims they can.

**Fine when:** It's real ad copy and the claim is backed. Even then, one strong adjective beats five.

> **Before:** Nestled in the heart of Lisbon, this charming boutique hotel boasts stunning views and a vibrant atmosphere.
> **After:** The hotel is a ten-minute walk uphill from Rossio station, and the rooftop looks straight across at the castle.

> **Before:** Elevate your workflow with our cutting-edge platform, seamlessly integrating every tool your team loves.
> **After:** Acme pulls tasks from your issue tracker, your inbox, and your team chat into one list.

> **Before:** This stunning, sun-drenched home boasts an open-concept layout perfect for entertaining.
> **After:** Three bedrooms. The living room faces south, and the kitchen opens onto it, so you can cook while people are over.

> **Before:** The city boasts a rich cultural heritage and a vibrant culinary scene.
> **After:** The old town is a UNESCO site, and you can eat well on most streets for under fifteen euros.
> *(If the source has no specifics, cut the sentence. It carried nothing.)*

### A3. Vague abstractions

**Tell:** "drive meaningful impact", "unlock value", "enhance the overall experience", "deliver results", "valuable insights", "key learnings", "various aspects", "a wide range of", "solutions", "outcomes", "in a meaningful way", "take it to the next level".

**Cause:** Abstract nouns fit every context, which makes them the most probable fill. They're also impossible to be wrong about.

**Fix:** Ask "for example?" and write the example instead. If there's no example, the sentence was empty; cut it or leave a placeholder.

> **Before:** Our new dashboard provides valuable insights that help teams make better decisions and drive meaningful impact.
> **After:** The new dashboard shows which marketing channels brought customers who stayed past three months, so you can stop paying for the ones that don't.

> **Before:** The workshop covered various aspects of personal branding.
> **After:** The workshop covered how to write a bio, which photos to use, and how often to post.

> **Before:** We're committed to enhancing the overall user experience.
> **After:** We fixed the crash on file upload and cut the search page's load time from four seconds to under one.

> **Before (cover letter):** I have a proven track record of delivering results in fast-paced environments.
> **After:** At my last job I ran the move from paper invoices to online billing. Payments that used to take 45 days started arriving in 12.

### A4. "-ing" significance tails

**Tell:** A factual clause followed by a participle phrase that comments on it: ", highlighting...", ", underscoring...", ", reflecting...", ", showcasing...", ", ensuring...", ", fostering...", ", contributing to...", ", paving the way for...", ", making it a...", ", solidifying its position as...", ", cementing...".

**Cause:** Sentence-by-sentence generation: the model finishes the fact, then appends a gloss about what it means, because commentary looks like analysis. It's analysis-shaped, not analysis. The claim in the tail is almost never supported.

**Fix:** Cut the tail. If it held a real claim, give that claim its own sentence with a subject and a causal verb, and check that it's true.

> **Before:** The company grew to 200 employees in 2023, reflecting its rapid expansion and solidifying its position as a market leader.
> **After:** The company grew to 200 employees in 2023.

> **Before:** The museum added free Thursday evenings, fostering a deeper connection with the local community.
> **After:** The museum added free Thursday evenings. Thursday attendance tripled in the first three months.
> *(Second sentence only if the source has the number.)*

> **Before:** We added dark mode, ensuring a comfortable experience for users at night.
> **After:** We added dark mode.

### A5. Vague attribution

**Tell:** "Experts say", "Studies show", "Research suggests", "Many believe", "Critics argue", "Industry reports indicate", "It is widely accepted that", "Observers have noted", "According to many".

**Cause:** Attribution looks responsible and lets the model avoid owning the claim (penalty avoidance). Models with web search also attach claims to sources that don't say them.

**Fix:** Name a checkable source, or state the claim as your own view, or cut it. Never invent a source.

> **Before:** Studies show that remote workers are more productive.
> **After:** In a [year] study of [who], [source] found that [specific result].
> **Or, owning it:** On our team, people who work from home ship as much as people in the office, and fewer of them quit.

> **Before:** Experts agree that consistency is key to growing on social media.
> **After:** I think posting regularly matters more than polish. Our reach roughly doubled the month we went from two posts a week to five.

### A6. Challenges-and-outlook ending

**Tell:** "Despite these challenges, ...", "faces several challenges, including...", "The future looks bright", "As X continues to evolve, ...", "It remains to be seen", "Looking ahead, ...", "poised for growth", "the possibilities are endless".

**Cause:** Genre template. Essay outlines and encyclopedia-style articles end with a "Challenges" section followed by a hopeful "Future" one, and the model reproduces the outline whether or not it has anything to put in it.

**Fix:** If there are real challenges, name them concretely, where they belong. Cut generic optimism. End on the last real piece of information.

> **Before:** Despite facing challenges such as increased competition and changing consumer preferences, the bookstore remains poised for continued growth as it navigates the evolving retail landscape.
> **After:** The bookstore's biggest problem is price: online retailers sell most new titles for about a third less. It hasn't found an answer yet.

> **Before:** As AI continues to evolve, the possibilities are endless.
> **After:** *(cut)*

### A7. Stock metaphors

**Tell:** journey, landscape, tapestry, realm, beacon, symphony, dance (of ideas), labyrinth, ecosystem, roadmap, north star, treasure trove, double-edged sword, game-changer, navigate (anything that isn't a route), unlock, unleash, embark, delve, at the intersection of, a rich tapestry of, a testament to.

**Cause:** Dead metaphors are high-probability precisely because they've been used millions of times. That's also why they no longer create an image.

**Fix:** Literal description. If a metaphor really helps, make it a fresh, concrete one that fits this situation, and use only one.

> **Before:** Navigating the complex landscape of health insurance can feel like a daunting journey.
> **After:** Most people don't understand their health insurance until they get a bill they didn't expect.

> **Before:** The novel weaves a rich tapestry of family, memory, and loss.
> **After:** The novel follows three sisters who each remember their mother's death differently.

> **Before:** Our platform unlocks the full potential of your data.
> **After:** Acme lets you ask questions about your sales data in plain English instead of writing SQL.

### A8. The universal reader

**Tell:** "Whether you're a seasoned professional or just starting out", "Whether you're X, Y, or Z, this is for you", "for everyone from beginners to experts".

**Cause:** Covering every possible reader looks helpful and inclusive, and the model has no particular reader in mind.

**Fix:** Write to the actual reader. If you really serve several groups, say what each one gets.

> **Before:** Whether you're a seasoned investor or just getting started, Acme has something for you.
> **After:** Acme is for people who have savings sitting in a bank account and keep meaning to invest them.

> **Before:** Whether you're a founder, a marketer, or a student, these tips will help you write better.
> **After:** These are the edits I make most often to founders' first drafts.

### A9. Emotional labeling

**Tell:** "I'm thrilled to announce", "We're incredibly excited to share", "I'm humbled and honored", "It is with great pleasure", "We couldn't be prouder", "I'm beyond grateful".

**Cause:** The LinkedIn and press-release template, plus rater preference: enthusiasm reads as warmth at a glance.

**Fix:** Make the announcement. If there's a feeling worth sharing, give its reason in specific terms. Readers decide how exciting the news is.

> **Before:** I'm thrilled and humbled to announce that I've joined Acme as Head of Growth!
> **After:** I've joined Acme as Head of Growth. [The real reason you took the job, in one sentence.]

> **Before:** We're incredibly excited to share that we've raised our Series A!
> **After:** We've raised a $12M Series A, led by [fund]. It pays for the two things customers ask about most: a mobile app and support in Spanish.

---

## B. Borrowed rhetoric

### B1. Negative parallelism

**Tell:** "It's not just X, it's Y." "This isn't about X. It's about Y." "Not only X but also Y." "X isn't a feature, it's a philosophy." "It's less about X and more about Y." "Y rather than X." Chained versions: "It's not a tool. It's not an app. It's a movement."

**Cause:** Persuasive writing uses the reframe to signal insight, and it's cheap: refuting a claim nobody made makes Y feel like a revelation. Raters reward insight-shaped sentences, so models learned to produce the shape without the insight.

**Fix:** State Y directly. Keep a contrast only if X is something your reader actually believes, and then name it plainly ("Most teams treat onboarding as a tutorial. We treat it as...").

**Fine when:** Correcting a real misconception: "It's not an allergy, it's a fungal infection, so antihistamines won't help."

> **Before:** Acme isn't just a project management tool. It's a whole new way to think about work.
> **After:** Acme keeps your team's tasks, docs, and deadlines in one place.

> **Before:** This isn't about working harder. It's about working smarter.
> **After:** We stopped writing the weekly report by hand. A script pulls the numbers, and the team spends that hour on what the numbers mean.

> **Before:** Great onboarding isn't about features, it's about feelings.
> **After:** People who finished onboarding in under two minutes were twice as likely to come back the next day, so we cut it to four screens.

> **Before:** Not only does it save time, but it also reduces stress.
> **After:** It saves about ten minutes every morning, and that's the part people mention first.

### B2. "No X, no Y, just Z"

**Tell:** "No fluff. No jargon. Just results." "No gimmicks, no hidden fees, just honest pricing." "No sign-up, no credit card, no hassle."

**Cause:** Ad-copy template that defines a product by what it isn't. The negatives are usually things nobody suspected.

**Fix:** Say what it is. If one specific absence matters to the reader, state it once, plainly.

**Fine when:** A single factual reassurance: "No credit card required."

> **Before:** No complicated setup. No learning curve. Just results.
> **After:** Connect your bank account and you'll see your first report in about five minutes.

> **Before:** No fluff, no filler, just actionable insights.
> **After:** *(cut; the reader will judge whether there's fluff)*

### B3. Rule of three

**Tell:** Triads of adjectives ("fast, reliable, and secure"), of phrases, of clauses; exactly three bullets; three-beat slogans ("Learn. Grow. Thrive."). Often two of the three are near-synonyms, or the third is vaguer than the first two because it was added to complete the rhythm.

**Cause:** Triads feel complete (they run through rhetoric from Cicero to stand-up), and completeness reads as quality to a skimming rater. The model pads to three.

**Fix:** Count the real, distinct items and use however many exist. Collapse synonyms into the best one. If a triad survives, make sure it's earned and that it isn't the third triad in a row.

> **Before:** Our platform is fast, efficient, and streamlined.
> **After:** Pages load in under a second.

> **Before:** The course will help you build confidence, develop new skills, and unlock your potential.
> **After:** The course teaches you to edit your own photos in Lightroom.

> **Before (reference letter):** She was talented, driven, and passionate about her work.
> **After:** She rewrote the pitch deck twice the night before the meeting because she didn't like the second slide.

### B4. Question-then-answer reveal

**Tell:** "The result? ...", "The catch? ...", "Why does this matter? Because...", "What does this mean for you? ...", "So what changed? Everything.", "The best part?", "Sound familiar?"

**Cause:** Copywriting and LinkedIn templates for manufactured suspense. The reader didn't ask the question.

**Fix:** A plain statement. Keep a real question only if the reader is actually asking it (FAQ pages, or an essay that opens a genuine question it then works through).

> **Before:** We rebuilt the checkout from scratch. The result? A 40% jump in completed orders.
> **After:** We rebuilt the checkout, and completed orders went up 40%.

> **Before:** Why does this matter? Because first impressions count.
> **After:** Most visitors decide within a few seconds whether a site is for them, and most never come back.

### B5. Announcement colon

**Tell:** "Here's the thing:", "Here's what most people miss:", "The truth is:", "The kicker:", "Plot twist:", "The bottom line:", "The secret?", "Spoiler:", "Hot take:", "Real talk:", "One word:".

**Cause:** Genre template plus rater preference: the drumroll reads as emphasis.

**Fix:** Delete the announcement and say the thing. If the content is surprising, it'll surprise without the drumroll.

**Fine when:** It's in the author's established voice and used once. (People do say "Here's the thing" in conversation.)

> **Before:** Here's the thing: most meetings could be an email.
> **After:** Most of our meetings could have been an email.

> **Before:** The bottom line: you need fewer tools.
> **After:** You probably need fewer tools.

### B6. Throat-clearing openers

**Tell:** "In today's fast-paced world", "In today's digital age", "In an era where", "In the ever-evolving world of", "When it comes to X", "Imagine a world where", "Picture this:", "Have you ever wondered", "We've all been there", "Let's face it", "It's no secret that", "X is more important than ever", "Now more than ever".

**Cause:** School essays and SEO posts warm up before the point. The model reproduces the warm-up because it's the most common way such texts begin.

**Fix:** Delete the opener. The second or third sentence of the original is usually the real start.

**Fine when:** A question hook in ad copy, used once, when the voice calls for it. Still, starting with the answer usually works better.

> **Before:** In today's fast-paced world, finding time to cook healthy meals can be a challenge. That's why we built Acme.
> **After:** Acme plans a week of dinners and orders the groceries in about five minutes.

> **Before:** When it comes to hiring, culture fit is more important than ever.
> **After:** The two engineers we let go last year were both strong. They hated pairing, and we pair on everything.

> **Before:** Have you ever opened your fridge, stared at it, and closed it again?
> **After:** A full fridge with nothing to eat is usually a planning problem, not a food problem.

### B7. Dramatic fragmentation

**Tell:** "And it worked. Beautifully." "Let that sink in." "Full stop." "Period." "Every. Single. Time." Stacks of one-sentence paragraphs. Verbless one-word sentences used as punchlines ("Simple." "Game-changer.").

**Cause:** The LinkedIn-ghostwriter style, and the newest overcorrection: models trained away from long uniform paragraphs overshoot into fragments, because fragments read as "punchy" and "human" at a glance.

**Fix:** Join fragments into normal sentences. One short sentence that lands a real point is fine; a column of them isn't.

> **Before:**
> We tried everything.
> Ads. Partnerships. SEO.
> Nothing worked.
> Then we talked to our customers.
> Everything changed.
>
> **After:** We tried ads, partnerships, and SEO, and none of them brought customers who stayed. What finally worked was calling twenty people who'd cancelled and asking why.

> **Before:** She didn't just change the company. She changed the industry. Let that sink in.
> **After:** She was the first in the industry to publish her suppliers' factory addresses. Within two years most competitors did the same.

### B8. False ranges

**Tell:** "from X to Y" where X and Y aren't endpoints of a real scale: "from boardrooms to bedrooms", "from scrappy startups to Fortune 500 giants", "from beginners to seasoned pros", "everything from skincare to spirituality".

**Cause:** Sounds comprehensive (rewarded) without committing to a scope (safe).

**Fix:** Name the actual scope, or one representative example, or drop it.

> **Before:** Our consultants work with businesses of every size, from scrappy startups to Fortune 500 giants.
> **After:** Most of our clients have between 50 and 500 employees.

> **Before:** Our community includes everyone from first-time founders to seasoned executives.
> **After:** Most of our members run companies with fewer than ten people.

### B9. Manufactured twist

**Tell:** "But here's where it gets interesting.", "But that's not the whole story.", "Here's where things get tricky.", "But there's a catch.", "Little did we know..."

**Cause:** Suspense template from storytelling-style marketing.

**Fix:** Delete it and go straight to the interesting part.

> **Before:** The first version of our shared-list app worked fine. But here's where it gets interesting: users started using it in ways we never expected.
> **After:** Within a month, people were using the first version of our shared-list app for something we hadn't planned: packing lists for trips.

### B10. Contrarian hook

**Tell:** "Most people think X. They're wrong.", "Unpopular opinion:", "Everyone tells you X. Don't.", "Stop doing X.", "X is dead."

**Cause:** Engagement template that invents a mistaken majority so the author can be the one who sees clearly.

**Fix:** State your view and the reason. If you really disagree with a common view, name who holds it.

> **Before:** Most founders think they need more features. They're wrong.
> **After:** We grew faster in the quarter we shipped nothing new and fixed onboarding instead.

### B11. "This is where X comes in"

**Tell:** "That's where [product] comes in.", "Enter: [product].", "That's exactly why we built...", "This is where we can help."

**Cause:** The problem-agitate-solution ad template.

**Fix:** Introduce the product by showing it do something.

> **Before:** Chasing late invoices is exhausting. That's where Acme comes in.
> **After:** Acme emails your client a reminder when an invoice is a week late, so you don't have to.

### B12. Engagement-bait closer

**Tell:** "What do you think? Let me know in the comments!", "Thoughts?", "Agree or disagree?", "Drop a 🔥 if...", "Tag someone who needs this.", "Share below! 👇"

**Cause:** Social-media template plus the assistant habit of ending with an invitation.

**Fix:** Depends on the channel. On LinkedIn a real, specific question can be fine, because it's one people can actually answer. Generic ones go.

> **Before:** What's the biggest challenge you've faced when hiring? Let me know below! 👇
> **After:** If you've hired your first salesperson, did you pay them mostly salary or mostly commission? We're deciding now.

---

## C. Over-qualification

### C1. Hedge stacking

**Tell:** "may potentially", "could possibly", "might help to some extent", "it's possible that this may", "tends to generally", "in some cases it may be", "arguably", "somewhat", "relatively", "to a certain degree".

**Cause:** Accuracy and safety training make every claim cheaper to qualify than to commit to. Several hedges on one claim means the model is protecting itself, not informing the reader.

**Fix:** Decide what you know and state it. If there's real uncertainty, use one hedge, placed on the uncertain part, ideally with the reason.

> **Before:** This approach may potentially help improve engagement in some cases.
> **After:** This should raise engagement among people who already open the app weekly. We don't know yet whether it helps new users.

> **Before:** It could be argued that the redesign was somewhat successful.
> **After:** The redesign helped retention and hurt conversion.

### C2. Reflexive balance

**Tell:** "While X has its benefits, it's important to consider the drawbacks.", "Both approaches have their merits.", "Ultimately, the right choice depends on your needs.", "There's no one-size-fits-all answer.", "It's a matter of personal preference."

**Cause:** One-sidedness is penalized; balance looks fair and safe.

**Fix:** Take a position and give the reason, or lay out the trade-off concretely enough that the reader can decide ("Pick A if..., pick B if..."). Balance with content is fine. Balance as a reflex is filler.

> **Before:** While paid ads offer quick results, organic content provides long-term value. Ultimately, the right strategy depends on your goals.
> **After:** Paid ads got us customers within a week, but most were gone a month later. Content took three months to work, and those customers stayed. If you need numbers for a fundraise next month, buy ads. Otherwise start with content.

> **Before:** Both renting and buying have their advantages, and the right choice depends on your individual circumstances.
> **After:** If you'll stay less than five years, renting usually comes out cheaper once you count fees and maintenance. Past that, buying tends to win.

### C3. Importance markers and didactic asides

**Tell:** "It's important to note that", "It's worth mentioning", "It's worth noting", "Keep in mind that", "Remember that", "It should be noted", "Notably,", "Importantly,", "Needless to say", "It goes without saying".

**Cause:** Flagging importance instead of making it obvious, plus the teacherly tone of instruction tuning.

**Fix:** Delete the marker. If the point is important, put it first or give it its own sentence.

> **Before:** It's important to note that the discount only applies to annual plans.
> **After:** The discount only applies to annual plans.

> **Before:** It's worth mentioning that results may vary.
> **After:** Results depend on how much history you import. With less than three months of data, the forecasts are mostly guesses.

### C4. Sincerity and intensity markers

**Tell:** truly, genuinely, honestly, really, incredibly, deeply, profoundly, absolutely, remarkably, extremely, super, "I have to say", "to be honest", "frankly".

**Cause:** Warmth and enthusiasm read well at a glance. These words are also near-universal fillers that fit anywhere.

**Fix:** Delete. Sincerity markers signal the opposite of sincerity. If the strength matters, show it with a fact.

> **Before:** We're truly grateful for our incredibly supportive community.
> **After:** Thank you to everyone who sent bug reports during the beta. There were 1,400 of them, and we read every one.

> **Before:** This feature is genuinely useful.
> **After:** I use this feature every morning.

---

## D. No model of the reader

### D1. Signposting and meta-commentary

**Tell:** "Let's dive in", "Let's dive deeper", "Let's break it down", "Let's explore", "In this article, we'll", "Here's what you need to know", "Without further ado", "First, let's take a look at", "Now, let's turn to", "As mentioned above", "In the following section".

**Cause:** The model narrates its own structure, a habit from tutorials and from generating sequentially.

**Fix:** Delete and start. A long document may need one line of orientation; make it informative ("Part 2 covers pricing. Skip it if you're on the free plan.").

> **Before:** Choosing a database can be tricky. Let's dive into the key factors you should consider.
> **After:** Start with the shape of your data. If most of it is rows with the same fields, use a relational database.

> **Before:** In this post, we'll explore five strategies to grow your newsletter.
> **After:** *(cut; start with strategy one)*

### D2. Moral and recap endings

**Tell:** "Ultimately, ...", "In conclusion, ...", "At the end of the day, ...", "In the end, ...", "The key takeaway is...", "By [doing X], you can [Y].", "So the next time you..., remember...", "And that's what makes X so special." Also the paragraph-level version: the last sentence restates the first.

**Cause:** School-essay structure, plus generation that can't tell the reader already got it.

**Fix:** End on the last piece of information or on the ask. In an essay, end on your strongest specific point, not a summary of your points.

> **Before:** ...and that's how we cut churn in half. Ultimately, listening to your customers is the key to building a product people love.
> **After:** ...and that's how we cut churn in half.

> **Before:** By following these tips, you'll be well on your way to a résumé that truly reflects who you are.
> **After:** *(cut)*

### D3. Transition stacking

**Tell:** Consecutive sentences opening with Moreover, Furthermore, Additionally, In addition, Also, Notably, Consequently, As a result, That said, That being said, However, On the other hand.

**Cause:** Explicit connectives make local coherence visible, so the model overuses them.

**Fix:** Most sentences need no connective; order does the work. When one is needed, use the plain ones: and, but, so, also, still, then.

> **Before:** The app is free to download. Additionally, it offers a premium tier. Furthermore, premium users get unlimited projects. Moreover, they can export to PDF.
> **After:** The app is free. Premium adds unlimited projects and PDF export.

### D4. Explaining the obvious

**Tell:** Defining common terms for readers who know them ("Instagram, a popular social media platform,"), restating the question before answering it, "In other words" after a sentence that was already clear, explaining what an example shows right after the example.

**Cause:** Thoroughness reads as helpfulness, and the model has no picture of what this reader already knows.

**Fix:** Decide who the reader is and delete what they know.

> **Before (written for marketers):** TikTok, a popular short-form video platform owned by ByteDance, has become an increasingly important channel for app marketing.
> **After:** TikTok now brings us most of our installs.

> **Before (written for engineers):** Git, a widely used version control system, allows developers to track changes to their code.
> **After:** *(cut; start with what they need to do in Git)*

---

## E. Word-level habits

### E1. AI vocabulary clusters

**Tell:** Several of: delve, tapestry, testament, landscape, realm, pivotal, crucial, leverage, foster, seamless, robust, elevate, unlock, empower, navigate, multifaceted, intricate, nuanced, showcase, underscore, journey. Full list with replacements in `vocabulary.md`.

**Cause:** Preference training. Experiments that simulate the rating step find that raters prefer variants containing some of these words, so the tuned model uses them far more often than people do. The specific words drift with each model generation; the mechanism doesn't.

**Fix:** Don't swap them for synonyms. Rewrite the sentence around the specific claim it was avoiding.

> **Before:** In the ever-evolving landscape of personal finance, Acme leverages cutting-edge AI to foster a seamless, personalized budgeting journey.
> **After:** Acme uses AI to sort your card payments into a budget.

### E2. Copula avoidance

**Tell:** "serves as", "stands as", "functions as", "acts as", "represents", "marks", "boasts", "features", "offers" where "is" or "has" would do.

**Cause:** Repetition avoidance makes plain "is" feel repetitive, and the fancier verb sounds more formal.

**Fix:** Use is, are, has.

> **Before:** The dashboard serves as a central hub for all your projects.
> **After:** The dashboard shows all your projects in one place.

> **Before:** The apartment boasts two bedrooms and features a private balcony.
> **After:** The apartment has two bedrooms and a balcony.

### E3. Synonym cycling

**Tell:** The same entity gets a new name in each sentence: "Acme... the app... the platform... the AI-powered tool... the solution... the startup".

**Cause:** Repetition penalties during generation, plus the school rule "don't repeat words".

**Fix:** Pick a name and repeat it; use "it" when the reference is clear. Readers track a repeated noun easily, and a new noun makes them wonder whether "the platform" is something different from "the app".

> **Before:** Acme launched in March. The app quickly gained traction, and the platform now has 50,000 users. The AI-powered tool plans to expand to Europe, where the startup sees strong demand.
> **After:** Acme launched in March and now has 50,000 users. Next it's expanding to Europe, where a third of its waitlist lives.

### E4. Nominalization and bureaucratic verbs

**Tell:** "the utilization of", "the implementation of", "facilitate", "leverage", "utilize", "optimize", "operationalize", "enable", "conduct an analysis", "make a decision", "provide assistance", "in order to", "with regard to", "in terms of", "prior to".

**Cause:** Formal and corporate registers in the training data are dense with nouns made from verbs.

**Fix:** Turn the nouns back into verbs and use the short word.

> **Before:** We conducted an analysis of user behavior in order to facilitate the optimization of the onboarding flow.
> **After:** We looked at where users dropped off and shortened onboarding.

> **Before:** Leverage our AI to enable better hiring decisions.
> **After:** Use our AI to rank applicants.

### E5. Missing contractions

**Tell:** "It is", "do not", "we are", "you will", "that is" throughout a casual text; "It is important that you do not miss this."

**Cause:** Formal register is the safe default.

**Fix:** Contract wherever a person would. Keep uncontracted forms for emphasis ("I did not say that") and for formal or legal registers.

> **Before:** We are excited to let you know that you will not need to update the app. It is all automatic.
> **After:** You don't need to update the app. It happens automatically.

### E6. False agency

**Tell:** Inanimate subjects doing human things: "The data tells a story", "The numbers speak for themselves", "This approach invites us to", "History reminds us", "Your team deserves", "This moment calls for", "The results speak volumes".

**Cause:** A rhetorical habit of essays and marketing; it lets the writer avoid saying who did or concluded what.

**Fix:** Put the real actor in the subject slot, or state the content directly.

**Fine when:** It's occasional and fresh, or an established idiom in the field ("the market rewards speed" in a finance note).

> **Before:** The numbers speak for themselves.
> **After:** Retention doubled.

> **Before:** Your team deserves better tools.
> **After:** Your team spends a day a week copying data between spreadsheets.

### E7. The quiet/honest/real family (2024-2026)

**Tell:** "quietly" (quietly revolutionizing, quietly building), "the quiet power of", "the honest answer is", "the real question is", "real trade-offs", "here's the honest version", "the unglamorous truth", "the hard part", "sit with that", "small but mighty", "the part nobody talks about".

**Cause:** Newer models were trained away from the loud 2023 register ("revolutionary", "game-changing") and drifted into performed understatement and candor. The marker of humility became the new inflation.

**Fix:** Delete the marker. Honest statements don't need the label. If something is hard, say what's hard.

> **Before:** The honest answer is that we don't know yet.
> **After:** We don't know yet.

> **Before:** Acme is quietly changing how small businesses do their taxes.
> **After:** Twelve thousand small businesses filed their taxes through Acme this year.

> **Before:** Here's the part nobody talks about: retention is harder than acquisition.
> **After:** Keeping customers has been harder for us than getting them.

### E8. Critic-speak

**Tell:** "load-bearing" (as a metaphor), "doing a lot of (heavy) lifting", "lands" ("the joke lands"), "earned", "sharp", "crisp", "clean", "punchy", "the move", "the unlock", "table stakes", "a forcing function", "signal", "north star", "first principles".

**Cause:** Vocabulary of tech Twitter and editorial feedback. Models picked it up as the register of smart commentary.

**Fix:** Plain description of the actual effect.

> **Before:** The word "simply" is doing a lot of heavy lifting in that sentence.
> **After:** "Simply" hides the hard part, which is getting people to import three years of receipts.

> **Before:** The real unlock was making onboarding a forcing function for connecting a bank account.
> **After:** What made the difference was asking people to connect a bank account before showing the first report.

---

## F. Rhythm

### F1. Metronome sentences

**Tell:** Most sentences are the same length (often 15 to 22 words) and the same shape (subject, verb, object, trailing clause). Every paragraph has three or four sentences.

**Cause:** Averaging produces averages.

**Fix:** Let content set length. A chain of reasoning can be a long sentence; a conclusion can be short. Don't randomize lengths; respond to what each sentence is doing. Read it aloud: if you can tap out a beat, it's metronomic.

> **Before:** Our tool helps teams track their time efficiently. It uses AI to categorize their daily activities. Users then receive weekly reports tailored to their work. This saves time and improves productivity.
> **After:** Acme watches which apps and documents you have open and sorts your week into projects, so by Friday the timesheet is already filled in. Most people check it and hit submit.

### F2. Parallelism everywhere

**Tell:** Sentences or bullets built on the same frame ("It helps you X. It helps you Y. It helps you Z."; "Smarter budgets. Faster savings. Happier you."); anaphora in plain informational text.

**Cause:** Parallel structure looks organized at a glance, and slogans are built on it.

**Fix:** Use parallel structure when the items really are parallel and you want them compared. Otherwise write them as they come.

> **Before:** Smarter budgets. Faster savings. A future you'll love.
> **After:** A budget that updates itself every time you pay for something.

---

## G. Formatting

### G1. Headers and bold in short text

**Tell:** A 200-word post or email with headers, bolded phrases every few lines, a "Key takeaways" section.

**Cause:** Structure is rewarded at a glance, and chat interfaces render markdown, so models default to it. Recent research also traces some prose habits to heavy markdown in training.

**Fix:** Prose. Bold only if the channel supports it, and only for the one thing a skimmer must not miss (a deadline, a price). Headers only in documents long enough to need navigation.

> **Before (an email):**
> **Quick Update on Your Order**
> We wanted to let you know about your order status. **Your package has shipped** and is on its way!
> **What's Next?**
> You'll receive tracking info soon.
>
> **After:** Your order shipped today and should arrive Thursday. Tracking: [link]

### G2. Inline-header bullets

**Tell:** "- **Speed:** Our app is fast..." / "- **Collaboration:** ..." Every bullet starts with a bold label and a colon, followed by a sentence that restates the label.

**Cause:** README, slide-deck, and listicle conventions in training data, reinforced because they look organized.

**Fix:** If it's a real list, use plain bullets that start with the content. If the items form an argument, write a paragraph.

> **Before:**
> - **Automation:** Save hours with powerful automated workflows.
> - **Collaboration:** Work together seamlessly in real time.
> - **Security:** Your data is always safe with us.
>
> **After:** Acme runs your recurring tasks on a schedule, and your whole team can edit the same board at once. Data is encrypted at rest and in transit.

### G3. Bullets for non-list content

**Tell:** Reasoning, narrative, or a single idea split into bullets; bullets that only make sense in order and connect with "This means...", "As a result...", "However...".

**Cause:** Bullets look scannable and organized.

**Fix:** If the bullets connect with "because", "so", or "but", they're a paragraph.

> **Before:**
> - We launched on TikTok first.
> - This was because most of our customers are under 30.
> - As a result, we saw strong early growth.
> - However, retention was lower than expected.
>
> **After:** We launched on TikTok first because most of our customers are under 30. Growth was fast; retention wasn't.

### G4. Emoji as structure

**Tell:** 🚀 ✨ 💡 ✅ 👉 🔥 1️⃣ used as bullets or before headings, especially in professional text; a rocket on every announcement.

**Cause:** Social-media templates, plus rater preference for friendly-looking text.

**Fix:** Remove them, unless the voice sample or the channel's established style uses them (a brand account that always does). If kept, use them sparingly and not as structure.

### G5. Em dash density

**Tell:** Several "—" per paragraph, used interchangeably for asides, reveals, lists, and emphasis. "X — and that's the point."

**Cause:** Still debated. The best current evidence suggests a tendency already present before preference tuning (possibly from markdown-heavy and professionally edited training text) that post-training amplifies. Whatever the cause, readers now treat dense em dashes as a machine marker, fair or not.

**Fix:** Default to none. Choose punctuation by function: an aside goes in commas or parentheses; a separate thought gets a period; an explanation or list after a complete clause can take a colon (sparingly); a contrast gets "but". Keep one if it's clearly the best mark, or if the author's voice sample uses them.

> **Before:** Our clinic offers same-day appointments — even on weekends — so you never have to wait — and you can book online in seconds.
> **After:** We have same-day appointments, including weekends, and you can book online.

> **Before:** The results were clear — customers loved it.
> **After:** Customers loved it. Repeat orders doubled in the first month.

### G6. Title Case Headings

**Tell:** "How To Build An Emergency Fund That Actually Works" in blog or doc headings where the house style is sentence case.

**Cause:** SEO and markdown-heavy training data.

**Fix:** Sentence case unless the publication uses title case. While you're there, make headings informative rather than clever: a heading should say what the section says.

---

## H. Chatbot residue

### H1. Assistant openers and closers

**Tell:** "Certainly!", "Absolutely!", "Of course!", "Sure! Here's...", "Great question!", "I hope this helps!", "Let me know if you have any other questions", "Feel free to reach out", "Happy to help", "Don't hesitate to contact us", "Here's a revised version:", "I hope this email finds you well".

**Cause:** The assistant persona. The text was generated as a reply in a chat.

**Fix:** Delete. In an email, a closing is fine if it's specific ("Call me if Thursday doesn't work"). "I hope this email finds you well" goes; if the email needs a warm-up, use one real sentence of context instead.

> **Before:** I hope this email finds you well! I wanted to reach out to see if you'd be interested in a potential collaboration. Please don't hesitate to let me know if you have any questions!
> **After:** I run partnerships at Acme, a budgeting app. We'd like to sponsor one episode of your podcast in March. Interested?

### H2. Sycophantic validation

**Tell:** "What a great idea!", "You're absolutely right", "That's a fantastic question", "I love this"; in outreach, generic praise of the recipient ("I absolutely love your content and your amazing insights!").

**Cause:** The assistant persona plus rater preference for warmth.

**Fix:** Remove it. In outreach, replace generic praise with one specific, true observation showing you actually saw their work. If you don't know one, leave a placeholder for the author.

> **Before:** I absolutely love your content and your amazing insights!
> **After:** [One specific thing from their work you liked, e.g. "Your post on pricing a first consulting project is the one I send to every new freelancer."]

### H3. Knowledge and sourcing disclaimers

**Tell:** "As of my last update", "I don't have access to real-time data", "Specific details are not widely documented", "Information on this is limited", "It's unclear from available sources".

**Cause:** The assistant persona plus penalty avoidance. With web search, these are often claims about the model's failed search, not about the world.

**Fix:** Delete. Supply the fact, or leave a placeholder for the author.

### H4. Template placeholders left in

**Tell:** "[Your Name]", "[Company]", "Insert link here", "Dear [Recipient]".

**Fix:** Fill from context, or list them under "Needs your input". The only bracketed placeholders in a finished rewrite should be ones you added on purpose for the author.
