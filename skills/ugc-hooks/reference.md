# UGC hooks — reference

## 1. Hook taxonomy (app-promo UGC, TikTok, Apr–Oct 2026)

15 formats from ~250 viral app promos (100k+ views, last 6 months). Lines are
patterns, not quotes to copy word for word.

| id | Format | Emotion | Pattern | Shot |
|---|---|---|---|---|
| `wdym_late_discovery` | WDYM / late discovery | disbelief, FOMO | "wdym you don't have to [painful way] anymore???", "y'all were [doing X] this whole time???", "been [doing X] for N years and i'm JUST NOW finding this???" | frozen shocked face or hand over mouth, 1–2 s → screen recording of the shortcut |
| `gratitude_girl_who` | Gratitude to whoever showed me | gratitude, relief | "i'll never forget the girl who told me [outcome] was this easy", "i could literally KISS whoever made this app", "whoever made this app deserves a raise" | close-up selfie, soft smile / hand on chest / air kiss → app doing it |
| `compliment_reveal` | Compliment → reveal | social proof, envy | two-line dialogue: "you look happier." / "thanks, i found the best [category] app." | dancing / walking / vibing clip, quote text → demo |
| `girl_to_girl` | Girl to girl | intimacy, insider | "girl to girl: [intimate question]?" — caption or pinned comment "i'll go first: [app]" | GRWM or talking head, looks up into the camera → answer is the app |
| `pov_pain` | POV / pain call-out | recognition | "POV: you have 200 items and 'nothing to wear'", "if you keep [pain] every morning" | the pain acted out (clothes pile, phone at 3am) → app fixes it |
| `before_after` | Before → after | transformation | "how to turn this? → to this..!", "BEFORE / AFTER", "2 girls have a different [X]" | two halves joined by a motion match-cut, app is the bridge |
| `bare_hype` | One line over the app | excitement | "okay but this app…", "found peak app", "idk abt you guys but i luv this app" | phone-in-hand or screen recording, 5–10 s of the most satisfying feature |
| `your_sign` | Your sign | belonging | "your sign to get this app with your [bf/bestie]", "apps every girl downloads before [moment]" | couple / friends clip → shared feature |
| `listicle_underrated` | Underrated listicle | curiosity | "apps that feel illegal to know", "top 5 niche apps for your phone" | phone in hand, quick cuts, your app #1 or #3 |
| `founder_built` | I built this | authenticity | "i built an app that [bold promise]", "be honest, would you use this?" | founder to camera / laptop → demo |
| `experiment_story` | Experiment / storytime | suspense | "i let [AI/app] [do X] for a week and…", "my bf dressed me using ONLY ai" | setup with cliffhanger text → reveal in app |
| `relatable_meme` | Relatable meme | humor | "me standing in front of a full closet like it's empty" | meme clip on a trending sound, app as the punchline |
| `game_challenge` | Game / challenge | competition | "[me] vs [app] — i had no chance" | filmed attempt with app UI / score |
| `hot_take` | Hot take / comparison | controversy | "hot take: [your app] > [big app]", "why everyone is deleting [big app]" | confident face → side-by-side demo |
| `value_tip` | Value tip with soft plug | utility | a genuinely useful tip as the hook, app shown 1–2 s as the tool | tip first, product second |

Signature hooks: take the app's differentiator (the thing competitors make
painful) and write it into 3–4 of the formats above. Those are filmed first;
they are the ones that make viewers ask "what app is this?".

## 2. Shot list template (one block per hook format)

```
## H<n> — <format name>
Text on screen: "<hook line>"            (2–3 alternatives below)
Emotion: <one word>   Length: 1.5–3 s used, film 5–6 s × 3 takes
Shot: <framing, action, where the eyes go, what is behind you>
First frame: already <emotion> — no wind-up
Cut to: <demo moment D#>
References: <url 1> (<views>), <url 2> (<views>)
```

Demo moments get their own blocks (`D0 … D6`): which screen, which gesture,
5–10 s screen recording, what must be visible in the first second.

## 3. Remotion composition (multi-clip demo, step captions, sound)

`tools/render_video.py` renders one hook + one demo. For batches with several
demo clips per video, step captions and a trend sound, a spec per video plus
one component is enough:

```ts
type Demo = {clip: string; maxSec?: number; caption?: string; plain?: boolean};
type VideoSpec = {id: string; hook: string; text: string; demos: Demo[]; sound: string};
const SOUNDS = {sweet: {drop: 4.45}, pov: {}};   // drop = second of the beat drop in the sound

// in the component
const hookFrames = framesOf(spec.hook);            // whole frames, one short of the file end
let start = hookFrames;
const playing = spec.demos.find((d) => (start += framesOf(d.clip, d.maxSec)) > frame);
const step = frame >= hookFrames && playing?.caption !== undefined;
const text = step ? playing!.caption! : spec.text;  // step captions replace the hook text
// <Caption text={text} boxed={frame >= hookFrames && !playing?.plain} step={step} />
//   plain white + outline over the face, translucent box over app screens,
//   "main\nsub" → first line 56px, rest 40px; top padding ≈400px of 1920
// <Audio src={sound} trimBefore={Math.max(0, drop*FPS - hookFrames)}
//        volume={(f) => interpolate(f, [total-15, total-1], [1, 0], clamp)} />
//   → the beat drop lands on the hook → demo cut, 0.5 s fade at the end
```

Use `plain: true` for the "after" half of a before/after (it is footage of a
person, not an app screen). Keep each video's clips as pre-cut files in
`public/` with their durations in a JSON next to the spec, so the timeline is
computed from data and a re-cut only means re-running the cut script.

## 4. Sound checks (per candidate reference sound)

| Check | How | Keep if |
|---|---|---|
| voice or music | Whisper on the first 15 s | transcript is `[Music]` / empty |
| where the reference starts in the full sound | cross-correlate 50 ms RMS envelopes of the video audio and `playUrl` | — (usually 0 s; sometimes 10+ s in) |
| beat drop | largest rise of the 0.5 s mean energy within the first 8 s | ≥ +10 dB = a usable drop |
| length | full sound ≥ video length + offset | else loop or pick another |

## 5. Privacy gate (any clip from the user's own phone)

- Gallery / camera-roll scans: crop the changing photo card, export at 8 fps,
  look at every frame. Cut windows with underwear, other people, documents,
  addresses; splice the safe parts; re-check the rendered video.
- Shared lists, chats, "sharing" panels, notifications: other people's names
  and avatars. Start screen recordings after them.
- Original footage of the person: check every take for underwear / undressing
  before it is selected; when unsure, ask instead of deleting.

## 6. Posting checklist (TikTok, Oct 2026)

- [ ] Content disclosure → **Your brand** (own product)
- [ ] **AI-generated** label if a realistic AI person (try-on avatar) is visible
- [ ] Sound added in-app from the reference sound page, original audio at 0, start shifted to the drop
- [ ] Caption: keyword phrase first, app named once, ≤1 emoji, 2–5 hashtags, no links
- [ ] Pinned comment posted and pinned (unique per video; mostly a question)
- [ ] First hour: reply to every comment in your own words; video-reply to the top question
- [ ] Tracking row: status, date, link, 24 h views
- [ ] Next post ≥4 h later, different format

## 7. Reply bank skeleton

| They write | Meaning of the reply | Note |
|---|---|---|
| what's the app?? | app name + "search it in the app store" | most common comment under any promo |
| do I have to [painful setup]? | "nope" + how the differentiator works | answer with a video reply |
| is it free? | free to download / what is paid, honestly | hiding the price gets called out |
| android? / not in my country | the real availability, no promised dates | |
| is this AI? / AI ruins everything | calm, one line on what it actually does | never argue |
| is this real? | yes + a screen recording as a video reply | |
