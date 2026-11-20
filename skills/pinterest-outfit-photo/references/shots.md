# Shot types, angles, settings

## Shot types and the mix for a set

| Type | Share of a set | Poses | Capture sentence (adapt) |
|---|---|---|---|
| Mirror selfie | ~30% | M1–M12 | "She takes it on her iPhone in a {mirror} in her {room}. The photo is not straight-on: she stands at an angle to the mirror, so its frame cuts diagonally through the image and the room recedes sideways; the picture is tilted a few degrees." |
| Influencer street post (phone) | ~15% | W1–W5, W7–W10, L5, X1, X3, X6 | "Her photographer friend shot it on an iPhone from a low three-quarter angle, so she looks tall and fills most of the frame, the street running diagonally behind her." |
| Fashion-week street style (camera, long lens) | ~10% | W6, W1, X2, X4 | "Shot by a street-style photographer with a longer lens, crouching low at a three-quarter angle as {he} walks diagonally across the frame; the camera tilted a few degrees; the background falls into soft focus." |
| Seated or indoor candid | ~20% | S1–S10, L9 | "Her friend shoots from above and slightly behind at a three-quarter angle, so the {counter, bench} runs diagonally across the frame." |
| Leans, doorways, stairs | ~15% | L1–L4, L6–L11, T1–T6, X5 | "Shot from below at a slight angle, so the {door frame, banister, fence} cuts the frame diagonally." |
| Waist-up portrait or POV | ≤10% | P1–P8 | "A waist-up shot from a three-quarter angle…" or "POV: she looks down at her own outfit…" |

Night flash is a light, not a shot type: combine it with any type above (an elevator mirror with flash is a mirror selfie).

Neighbour rule: consecutive photos in a feed or tab never share a shot type, a person, a setting or a light. Across a trend's 4 outfits, use at least 3 different shot types.

## Angle phrases that break straight perspective

Use one or two per prompt. Always add the CRITICAL "no straight-on symmetrical composition".
- "from a low three-quarter angle, tilted up"
- "from above and slightly behind, at a three-quarter angle"
- "the camera tilted a few degrees, so the building lines lean"
- "the {mirror frame / counter / kerb / banister / zebra stripes} cuts diagonally across the frame"
- "she stands at an angle to the mirror; the room recedes sideways"
- "shot through a doorway, the frame edge on one side"
- "phone held low at the hip, angled up"
- "a long lens from across the street, with passers-by blurred in the foreground"

## Light (pick one, name it)

- Low golden winter sun from the side, with long soft shadows. Flattering, the default for streets.
- Bright overcast, soft and even, with a sheen on the leather. Good for street style.
- Hard low sun with a graphic shadow on a pale wall. Good for men and graphic looks.
- Warm lamp light plus a little cool window light. Good for mirror selfies at home in the evening.
- Morning window light in a café.
- iPhone flash at blue hour or at night, the background falling into the dark. Good for grunge, party and leather.
- Moody dusk without flash: foggy blue-grey dusk with warm shop or street lamps coming on. Good for whimsigoth, dark romance and poetcore.

## Settings by trend vibe

| Vibe (trends) | Street | Indoor |
|---|---|---|
| Soft grunge, indie sleaze, 90s grunge, dark archive | Soho or Lower East Side cobblestones at blue hour with flash, a record-shop front, a bar facade with amber light, a metal shutter | A dim bar booth, a stairwell of an old walk-up, a cluttered bedroom mirror with posters |
| Y2K / winter bimbo, party season | A hotel entrance at night, the back of a cab, a glossy mall escalator | A pink bedroom with a wavy mirror, tulips and a mushroom lamp; a hotel-bathroom mirror; an elevator with flash |
| Poetcore, heritage tartan, fisherman, grandpa knits | Library steps, a honey-stone university street, a seaside promenade in winter, a harbour | A bookshop aisle, a café with books, a window seat, a wood-panelled study |
| Downtown girl, leopard, cherry red, power suiting | A Tribeca or Soho crosswalk, a deli with coffee, a doorway in a cast-iron building | A café window counter, a gallery, a hallway mirror by the front door |
| Old money, winter whites, oxblood, plum, soft tailoring, chocolate and ecru | A Paris Haussmann street with a café terrace, an arcade, a gallery entrance | A hotel lobby, an apartment with herringbone floors and an arched mirror |
| Après-ski, faux fur, gorpcore | A snowy alpine village street, a chalet balcony, a gondola station, a trailhead parking lot with mountains | A ski-lodge fireplace, a cabin hallway with boots |
| Whimsigoth, dark romance | A foggy park path at dusk, a vintage-shop front, a wrought-iron gate | A candlelit apartment, a velvet armchair, an antique mirror |
| Suede boho, leather season | A flower market, an ochre wall, a vintage car on a sunny street | A plant-filled apartment, a rattan chair, a wavy mirror |
| Skater, street layers, bomber, workwear (men) | A skatepark edge, a warehouse district, concrete stairs, a hardware-store front | A garage, a sneaker-filled bedroom mirror |
| Night out (men), leather and suede | A fashion-week courtyard in Paris, a Milan street with a Vespa, a neon-lit night street with flash | A bar, an elevator with flash |

Places must look aspirational and specific: 3–5 concrete details, real life in the background on streets. Avoid empty, tidy, stock-looking streets and grey dead walls.

## A real photo as the last reference

A real outfit photo with the framing you want, passed as the LAST reference image, is the strongest single lever for photo quality. Use only photos you have the rights to (your own shots, licensed images, your brand's pins).

- Pass it with `gen.py --pose-ref <file>` and add the line: "The last image is only a reference for pose, framing and photo quality; do not copy that person, their face or their clothes."
- Pick it for framing, not for clothes: an angled home mirror selfie for M1/M2, a staircase walk for T1, a sunny crossing for W1/W2, a man against a sunlit wall with a hard shadow for L3.
- **References leak.** Even when passed last, its garments can replace yours when they are the same type (its boots for your boots, its mini for your mini). Don't use a reference photo whose outfit shares garment types with the outfit you are shooting. A straight-on reference also pulls the result straight-on.
- Seated, POV and fashion-week street-style shots came out well with no photo reference at all. Words are enough for most shots; the approved batch of 152 photos used none.
