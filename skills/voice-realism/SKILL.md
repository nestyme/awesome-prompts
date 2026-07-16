---
name: voice-realism
description: Rewrite AI video / text-to-speech prompts so the generated VOICE sounds like a real human, not a robot. Takes any video prompt (Veo, Seedance, Kling) or TTS script (ElevenLabs) with spoken lines and returns (1) a rewritten prompt with emotion, delivery, acoustics, and framing baked in — parameters like whisper, sighs, laughs, tone words are chosen automatically from scene context — and (2) a post-processing checklist to strip the remaining AI polish. Use this skill whenever a prompt contains dialogue, a talking head, a voiceover, narration, or any character who speaks — even if the user only asks to "improve" or "fix" the prompt and doesn't mention voice. Also use it when the user complains that generated speech sounds robotic, synthetic, flat, or "AI-like".
tools: Read, Write, Edit
---

# Voice Realism

Image quality in AI video is nearly past the uncanny valley — speech is not. Voice is the #1 tell that a video is generated. This skill rewrites prompts so the voice track survives scrutiny, and prescribes the post-processing that removes what prompting can't.

The core mindset: **write the prompt like literary prose with epithets, not a dry algorithm.** Generic elements produce generic (robotic) speech; details and shading produce a performance. A voice model infers pacing, pitch, and micro-emotion from *everything* around the line — so the job is to surround every line with context.

---

## Workflow

Given an input prompt (or script), do these steps in order:

### 1. Parse the input

Identify:
- **Target model** — Veo, Seedance, Kling, ElevenLabs, or unspecified. Syntax rules differ (step 3). If unspecified, ask or output a model-agnostic version plus per-model dialogue syntax notes.
- **Every spoken line** — dialogue, voiceover, narration.
- **Scene context** — who is speaking, where, what just happened, what they feel. This drives the automatic parameter choices in step 2.
- **Clip duration**, if set — needed for the pacing check in step 4.

### 2. Choose the delivery automatically (don't ask the user)

Derive emotion, volume, and vocal texture from context. The user gives the scene; the skill picks the performance. Defaults by mood:

| Scene context | Delivery to write in |
|---|---|
| Intimate, late night, secret, bedside | **whisper** (also the cheat code — see below) |
| Tired, end of day, defeated | weary voice, sighs, slower pace, trailing off |
| Excited, reveal, unboxing, good news | shouts excitedly / breathless, faster pace, laughs |
| Nervous, confession, first date | hesitant, filler words, clears throat, uneven pace |
| Confident, expert, direct-to-camera | calm, measured, slight smile in the voice |
| Sad, breakup, loss | quiet, cracked voice, long pauses, sniffs |
| Casual vlog / UGC | conversational, mid-sentence starts, self-corrections |

**The whisper cheat.** Synthesis artifacts are nearly inaudible in whispered speech — no pitch contour to get wrong, no resonance to ring. If the scene plausibly allows it (intimacy, secrecy, ASMR, night), prefer moving the line to a whisper. If a generated voice keeps "reading as AI" after other fixes, rewriting the scene so whispering is natural is a legitimate move.

Vocal texture is also free realism: an accent, a slight rasp, a smoker's voice, an age — one clause in the prompt, big payoff. Add one when the character description supports it.

### 3. Rewrite each line — the bundle rule

Never write bare dialogue. Every line gets rewritten as **emotion + physical action + line, in one breath**:

> ❌ `She says: "hi"`
> ✅ `She smiles wearily, looks away, and quietly says: "hi"`

The model adjusts facial animation, tempo, and intonation to match the description. Tone words (*weary voice*, *shouts excitedly*, *barely audible*) are the cheapest way to kill robovoice.

**Model syntax** — get the dialogue delimiter right or the model may read stage directions aloud:
- **Veo**: line comes after a colon — `she says: hello there`
- **Seedance**: line in double quotes — `she says "hello there"`
- **ElevenLabs v3**: supports inline audio tags — `[whispers]`, `[sighs]`, `[laughs]`, `[clears throat]`, and custom tags (they're interpreted semantically, so descriptive custom tags like `[tired chuckle]` work). Place them where the sound happens: `Another long day [sighs]`. There's also an auto-tag mode where the model sprinkles tags over plain text for you — fine as a first pass, then hand-tune.
- **Other / newer models**: check current docs before assuming — delimiter conventions change between versions.

**Write like people talk, not like people write:**
- No long, complex sentences — no nested clauses
- Filler words, hesitations, "uh", "hm" where natural
- Audible breaths in and out
- Skip heavy punctuation, but ellipses and dashes are excellent — they read as pauses and trail-offs

### 4. Pacing check

If the clip duration is fixed, count the words. Natural speech runs roughly **2–2.5 words/second** English (casual is slower). A 5-second clip fits ~10–12 words; more than that and the model compresses delivery into a 4× voicemail. Cut the line or extend the clip — say which you did.

### 5. Bake acoustics into the prompt

The model has heard rooms during training — describe the space and it will render the reverb:
- `wind audible in the microphone`, `small 10 m² room`, `speaking loudly in a vast vaulted cathedral, 20 m ceilings`
- Match acoustics to the visual scene — a street shot with studio-dry voice is an instant tell.

**Seedance 2.0** generates video + audio in one pass and accepts an explicit mix priority — always include one when targeting it, e.g.:
`dialogue clean and prominent, music low, ambient subtle`
Without it, layers turn to mush.

### 6. Frame for lipsync

If the character speaks on camera, constrain the shot in the prompt:
- **Medium or close-up shot** — on wide shots lips don't get enough resolution and start living their own life
- **Static camera** while the line is delivered
- **Face frontal or three-quarter** to the camera

If the source prompt asks for a wide shot with dialogue, either tighten the shot or move the line to voiceover — flag the change.

### 7. Output

Return exactly this structure:

```
## Rewritten prompt
[the full rewritten prompt, ready to paste]

## What changed and why
[3-6 bullets: delivery chosen and the context cue that drove it,
syntax fixes, pacing math, acoustics added, framing changes]

## Post-processing checklist
[the subset of the post chain below that applies to THIS video,
with the reasoning — e.g. which background noise matches the scene]
```

---

## Post-processing chain

Prompting gets ~80% there; the last 20% is de-idealizing the audio in post. Recommend from this menu (tailor to the scene, don't dump the whole list blindly):

1. **Cut 2–4 kHz** a few dB — this band carries the characteristic "AI ring" / synthetic sheen.
2. **Room reverb, 5–10% wet** — restores the acoustic space that synthesis flattens. Match the room size to the visual.
3. **Background noise bed at ≈ −50 dB** — pick the bed from the scene (street rumble, room tone, café murmur, wind). A voice with zero floor noise sounds like a studio, and nothing in real life is a studio.
4. **Voice morpher at very low intensity** — "phone call" or "bad microphone" style degradation. Barely perceptible settings only; the goal is imperfection, not an effect.

The unifying principle: **remove polish**. Real recordings are slightly wrong in a dozen tiny ways — pick 2–3 of those ways and add them back.

---

## Worked example

**Input** (target: Seedance, 5 s):
> A woman comes home and says: I got the job. Wide shot of the apartment.

**Rewritten:**
> Medium close-up, static camera, her face in three-quarter view. A woman in her 30s pushes the door shut behind her, drops her keys, exhausted but glowing. She exhales, breaks into a shaky laugh, and half-whispers "I got... I got the job." Small apartment hallway, ~8 m², soft evening light, her voice slightly muffled by the close walls. Audio: dialogue clean and prominent, ambient room tone subtle, no music.

**What changed:** wide shot → medium close-up + static camera (lipsync); bare line → emotion + action + line bundle; delivery derived from context (big news + coming home tired → shaky laugh + half-whisper, which also masks synthesis artifacts); Seedance double-quote syntax; 7 words ≈ 3 s of speech — fits 5 s with the physical business; room size stated for acoustics; mix priority appended.

**Post for this clip:** −3 dB dip at 2–4 kHz; small-room reverb ~7% wet; apartment room tone + faint street bleed at −50 dB.

---

## Scope notes

- The job is always to make the voice **better**, never to remove it — don't suggest going voiceless; the user chose a speaking concept deliberately.
- This skill rewrites prompts and prescribes post steps; it doesn't run generation. Pair with `gen_video.py` / `render_video.py` from [`tools/`](../../tools/README.md) when the user wants the video actually produced.
