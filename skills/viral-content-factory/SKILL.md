---
name: viral-content-factory
description: Create viral social media content (TikTok/Instagram carousels and outfit-change videos) for app promotion. Generates AI characters, carousel image sets via Gemini, and animated mannequin videos via Kling 3/fal.ai. This skill should be used when the user wants to create new carousel content, mannequin videos, or expand the content library for any character.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Viral Content Factory

End-to-end system for generating viral TikTok/Instagram content promoting a product through AI-generated characters. Creates two content types:
1. **Carousels** — sets of 7-8 styled images per topic (Gemini image generation)
2. **Mannequin videos** — outfit-change animations using morph suit figures (Gemini + Kling 3)

---

## Shared tools

The repo's [`tools/`](../../tools/README.md) CLIs wrap the paid generation steps so they can be scripted per frame/slide with a uniform JSON envelope:

| Phase | Tool | Use |
|---|---|---|
| 2 | `gen_image.py` | Gemini text→image / image-edit (character ref, carousel slides, anchor frame). No baked text. |
| 3 | `gen_video.py` | Kling (fal.ai) image→video for the mannequin animation frames |
| 2/4 | `caption_composite.py` | Composite text overlays deterministically in PIL — free, correctly spelled, re-renderable |
| 3 | `render_video.py` | Assemble the final 9:16 cut — animated **hook (~3s) + app demo** — via Remotion (replaces the manual ffmpeg trim/concat + editor step) |
| 4 | `safe_zones.py` | QC a frame vs safe zones + thumbnail readability before shipping |

Keys: `GEMINI_API_KEY`, `FAL_KEY`. `render_video.py` needs Node.js 18+. Full map + flags in [`tools/README.md`](../../tools/README.md).

---

## Phase 0: Gather Requirements

Before generating anything, collect this information from the user:

### Required
1. **Product** — What app/product are we promoting? What does it do? What's the price?
2. **Characters** — Who are the AI personas? For each character:
   - Name and handle (@)
   - Visual description (age, ethnicity, build, hair, style aesthetic)
   - Voice/personality (how they talk, what makes them unique)
   - Content themes that work for them
3. **Reference images** — Ask user to provide:
   - Style reference images (Pinterest, TikTok screenshots) in an `ideas/` folder
   - Character reference photos if they exist
4. **API keys** — Check for:
   - Gemini API key (for image generation)
   - fal.ai API key (for Kling video generation)
5. **Existing content** — Check what's already been generated to continue numbering

### Optional
- Aspect ratio preference (4:5 for carousels, 9:16 for videos)
- Specific themes or viral hooks the user wants
- Brand guidelines (colors, typography, tone)

---

## Phase 1: Character Creation

When creating new characters, design them to be:
- **Visually distinctive** — recognizable across all content
- **Personality-driven** — each has a unique voice and perspective
- **Meme-worthy** — something about them is shareable (a cat giving fashion advice, a 65yo who dresses better than everyone)
- **Relatable** — viewers see themselves or aspire to be like them

### Character Archetypes That Work
| Type | Example | Why It Works |
|------|---------|-------------|
| Unlikely expert | Cat giving fashion tips | Humor + real advice |
| Age-defying | 65yo woman outfitting 25yos | Aspiration + relatability |
| Transformation | Morph suit before/after | Visual hook + satisfaction |
| Cocky insider | Young guy with swagger | Confidence + tips |
| Brand voice | Editorial infographic | Save-worthy + authority |

### Character Template

```python
CHARACTER_NAME = (
    "[Physical description — age, ethnicity, build, hair, distinguishing features] "
    "[Style aesthetic — what fashion world they live in] "
    "[Energy/vibe — how they carry themselves] "
)

STYLE = (
    "PHOTO STYLE: REAL iPhone photo — [specific setting and lighting]. "
    "NOT a studio shot. NOT AI-looking. [Platform reference]. "
    "IMPORTANT: NO AI artifacts — no extra fingers, no weird hands, no garbled text. "
    "[Aspect ratio]. "
)

TEXT = (
    "TEXT OVERLAY: Simple white text, clean sans-serif font. "
    "Subtle shadow for readability. [Position]. "
    "Plain white text, casual lowercase. MUST be spelled correctly. "
)

ONE_IMAGE = (
    "CRITICAL: Generate exactly ONE single image, not a collage or grid. "
    "NO AI artifacts — realistic hands with 5 fingers, natural proportions. "
)
```

---

## Phase 2: Carousel Generation

### Folder Structure
```
project_root/
├── .venv/                    # Python venv with google-genai, Pillow, fal-client
├── ideas/                    # Reference images (Pinterest saves, screenshots)
├── old/                      # Archive of previous batches
├── character_name/
│   ├── generate_name_XX_YY.py   # Generator script
│   ├── reference_photo.jpeg     # Character reference image
│   ├── old/                     # Previous carousels
│   ├── XX_carousel_name/        # Output folder
│   │   ├── slide_01.png
│   │   └── ...
│   └── ...
```

### Generator Script Pattern

Every generator script follows this exact structure:

```python
#!/usr/bin/env python3
import io, os, time
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-pro-image-preview"
W, H = 1080, 1350  # 4:5 for carousels, 1080x1920 for 9:16 video frames
ASPECT = "4:5"      # or "9:16"

BASE = Path(__file__).parent
CLIENT = genai.Client(api_key=API_KEY)
```

### Key Functions
- `gen(prompt, ref_images, retries=3)` — calls Gemini, returns PIL Image
- `save(img, folder, num)` — resizes + saves as slide_XX.png
- `gen_native(prompt, refs)` — wraps gen() with ONE_IMAGE + STYLE + TEXT constants
- `load_refs()` — loads character reference photos + idea images
- `generate_carousel(key, data)` — iterates slides, calls gen_native, saves

### Style Types

**Native influencer style** (for character accounts):
- Real iPhone photo aesthetic, NOT studio
- Natural lighting, warm tones, casual composition
- White text overlay, lowercase, sans-serif, Instagram stories style
- ONE image per generation (no grids/collages)
- Anti-artifact prompt: "NO AI artifacts — no extra fingers, no weird hands, no garbled text"

**Editorial brand style** (for brand accounts):
- Warm beige/cream background (#F5F0E8)
- Product cutouts on neutral bg, flatlay catalog style
- Bold serif titles + clean sans-serif body text
- ✓/✗ for do/don't comparisons
- Pinterest-save-worthy infographic feel

**Pet character style** (for animal accounts):
- Real iPhone photo by pet owner
- Animal always dignified, unbothered, slightly judgy
- Same cozy apartment background
- Humor comes from pet's "opinion" on the topic

### Carousel Data Structure

Each carousel is defined in a `CAROUSELS` dict:
```python
CAROUSELS = {
    "XX_carousel_name": {
        "title": "hook title for the carousel",
        "slides": [
            f"{CHARACTER}COVER: [description]. White text: '[hook]'. Lowercase.",
            f"{CHARACTER}[Slide 2 description]. White text: '[caption]'.",
            # ... 5 more content slides
            f"{CHARACTER}[Last slide — subtle {{brand}} mention]. White text: '[{{brand}} plug]'. Lowercase.",
        ],
    },
    # ... more carousels
}
```

### Running Generation
```bash
cd project_root
.venv/bin/python character_name/generate_name_XX_YY.py
```

Multiple scripts can run in parallel (they share the Gemini API). Expect ~3-5 minutes per carousel (7 slides).

### Moving Old Content
Before generating new batches, move existing carousels to old/:
```bash
mkdir -p character_name/old
for d in character_name/[0-9]*; do [ -d "$d" ] && mv "$d" character_name/old/; done
```

---

## Phase 3: Mannequin Video Generation

### Concept
A person in a **black full-body morph suit** (zentai/spandex) gets "dressed" in different outfits. Each outfit is a separate frame, then animated with Kling 3 via fal.ai.

### Step 1: Generate Frames (Gemini)

**Anchor-first approach** for consistent background:
1. Generate `frame_00_anchor` — morph suit person, clean room, no clothes
2. For ALL other frames, feed anchor as input + prompt "change only the outfit"

Key prompt for redressing:
```python
REDRESS = (
    "Take this exact image — same room, same wall, same floor, same lighting, "
    "same camera angle, same body shape, same person. "
    "CRITICALLY IMPORTANT: The person MUST remain a FACELESS figure in a BLACK MORPH SUIT. "
    "HEAD covered in BLACK FABRIC — NO face, NO eyes, NO skin, NO hair visible. "
    "HANDS in BLACK GLOVES. ALL skin covered in black lycra. "
    "Do NOT turn them into a real person. Do NOT add a face. "
    "ONLY change the outfit ON TOP of the black morph suit. "
    "Dress them in: "
)
```

**Common issues and fixes:**
- Gemini removes morph suit → add stronger "MUST remain faceless" language
- Background changes → always feed anchor frame as reference
- Body shape changes → emphasize "same body shape" in prompt
- Outfit previews leak from references → add "NO sketches on wall" when not wanted

### Step 2: Animate Frames (Kling 3 via fal.ai)

```python
import fal_client
os.environ["FAL_KEY"] = "<fal-api-key>"

# Upload frame
image_url = fal_client.upload_file(frame_path)

# Generate 5s video clip
result = fal_client.subscribe(
    "fal-ai/kling-video/v2/master/image-to-video",
    arguments={
        "prompt": "A faceless person in a black morph suit wearing [outfit] ...",
        "image_url": image_url,
        "duration": "5",
        "aspect_ratio": "9:16",
    },
    with_logs=True,
)
video_url = result["video"]["url"]
```

### Step 3: Trim and Concatenate

```bash
# Trim each clip to desired duration
ffmpeg -y -i clip.mp4 -t 1.5 -c:v libx264 -preset fast -crf 18 -r 30 -pix_fmt yuv420p -an trimmed.mp4

# Concatenate all clips
ffmpeg -y -f concat -safe 0 -i clips.txt -c copy final.mp4
```

**Timing guide:**
- First "before" clip: 3-5s (longer, establish the cringe)
- Each "after" outfit: 1-2s (quick cuts, satisfying transitions)
- Total target: 10-15s + app demo at the end

### Step 4: Add Text and Demo
After generating the raw video, add in a video editor:
- Text overlay: "my style 1 year ago vs..." → "my style now"
- App demo screen recording at the end: "I used this app to find my style"

---

## Phase 4: Quality Control

### Anti-Artifact Checklist
Before approving frames, check for:
- [ ] Extra fingers or malformed hands
- [ ] Garbled/repeated text in overlays
- [ ] Inconsistent background between frames
- [ ] Morph suit removed (face/skin visible)
- [ ] Body shape changed between frames
- [ ] Unnatural proportions or poses
- [ ] Items floating or disconnected from body

If artifacts found: regenerate the specific frame with stronger anti-artifact prompts. Don't regenerate the whole batch.

---

## Viral Hook Library

### Bait & Switch
- "the app i've been using for 40 years" (reveal: it's her brain)
- "this $15 trick changed my entire wardrobe" (reveal: tailoring)
- "the outfit that got me fired" (reveal: she looked too good)

### Revenge/Ex Energy
- "my ex invited me to his wedding. this is what i wore"
- "my ex texted 3 minutes after i posted this fit"
- "outfits i wore to run into my ex 'accidentally'"
- "dressed for my ex's wedding like i won the breakup"

### Bold/Savage
- "i'm 65 and i dress better than your girlfriend. sorry"
- "my granddaughter asked me to stop dressing like this"
- "outfits that got me in trouble"
- "outfits that got me free drinks"
- "stole every look at the party and didn't even try"

### Transformation
- "{month year} vs now — same closet, different person"
- "same body, different outfit, different person"
- "how she went from 'cute' to 'WHO IS SHE'"
- "my style 1 year ago vs now (he finally proposed)"
- "your closet before vs after"

### Practical/Save-Worthy
- "your jeans can make you look taller — 4 tips"
- "the fabric cheat sheet that saves money"
- "4 shoes that go with literally everything"
- "the tuck that changes everything"
- "what shoes to wear with each skirt"

### Rating/Judgment
- "{pet name} rates your shoe collection"
- "girls rated my outfits 1-10"
- "rate my fit — spring edition"
- "outfits i judged 6 months ago — i was right"

### Nostalgia/Comparison
- "at 25 i chased trends. at 65 i chase quality"
- "how my style evolved: 25, 45, 65"
- "dressed like my dad in 1995 vs me in 2026"
- "what i stopped wearing (not because of age)"

### Challenge/Formula
- "one hoodie, five fits"
- "1 blazer, 5 outfits"
- "7 days, 7 looks from 12 pieces"
- "one scarf, six ways"
- "10 spring essentials — the checklist"

### Humor/Pet
- "pov: your cat has better style than you"
- "{pet name} was banned from fashion week"
- "{pet name}'s dating profile"
- "outfits my cat approved (and he was right)"
- "{pet name} stole my date"

### Hook Rules
1. **First 3 words decide everything** — front-load the intrigue
2. **Personal > general** — "my ex" beats "how to style"
3. **Numbers perform** — "5 outfits", "4 tips", "$87 total"
4. **Conflict hooks** — "vs", "but", "stopped", "never again"
5. **Emotion hooks** — revenge, jealousy, surprise, aspiration
6. **Always lowercase** — casual energy, not corporate
7. **End with a {brand} plug** — natural, conversational, not ad-like

---

## Quick Reference

### Dependencies
```bash
pip install google-genai Pillow fal-client
# Also needs: ffmpeg (for video concat)
```

### API Keys
- Gemini: from environment / project .env files
- fal.ai: from environment / project .env files
- Never commit keys to git
