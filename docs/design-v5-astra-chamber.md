# V5 design — Astra Chamber

Status as of 2026-09-12: the editable V5 scene is built as `observatory-v5.blend`, Cycles still previews have been reviewed, and the short motion proof is rendering. The final 24-second film, its final visual review and the 4K hero render are pending. [Build and render instructions](build-v5.md) describe the current pipeline.

![Actual V5 Cycles room preview](../previews/v5/frame_0420.png)

## Art direction and completed room

The new orbital observatory surrounds the existing Astra galaxy with pale manufactured shells, cool satin alloy structure, restrained copper fittings and a charcoal deck. Warm architectural strips balance the cool stellar instrument. Panoramic glazing and a ribbed glass roof expose the NASA catalog starfield; its visible exposure is reduced so the central galaxy remains dominant.

The room is actual editable Blender geometry. The builder replaces the masonry, rubble, antique doorway and telescope with:

- a continuous deck at the existing native sole-contact height, radial joints and recessed light rings;
- nine flush rubber walkway inserts and eighteen progressively illuminated guide segments;
- a sliding two-leaf airlock, separate structural casing and a warmly lit approach corridor;
- curved window bays, titanium mullions, dome ribs and pale perimeter shells;
- six service bays containing 24 reused wall, locker, pipe and vent objects;
- two low observation consoles with modeled controls and original orbital display graphics.

The custom instrument has a stepped circular platform, bearing uprights, captive fasteners and two precision rings. Its satin hoops, polished rails, pale inserts and small illuminated indices replace the antique bronze treatment and markings. The rings turn +125° and −150° over frames 1–576 in fixed tilted planes. Their asymmetrical clamps and inserts make rotation visible. The existing stellar spiral retains its original geometry, materials and differential motion.

Downloaded parts supply background detail; the foreground architecture, airlock, platform and precision rings are original geometry. The Irondust panels rely mostly on mapped relief and the small vent atlas is deliberately kept away from hero close-ups. [Resource selection and adaptations](resources-v5.md) explain their limits.

## Preserved performance and edit

The same Microsoft Rocketbox Female Adult 04, clothing, baked native walk/start/stop/idle and authored surprise/wonder controls remain. The preservation audit found no changes to the actor's three-object family or the galaxy's nineteen-object family. This includes mesh data, facial morphs, rig rest matrices, relevant animation curves and material nodes.

The six-cut schedule remains at 24 fps. The threshold, instrument, wide and closing cameras were reframed for the new room; the entrance walk and wonder shot retain their V4 camera setup.

| Frames | Time | Current shot |
|---|---|---|
| 1–36 | 0–1.5 s | Threshold portrait, 58 mm; airlock opens by frame 34. |
| 37–192 | 1.5–8 s | Native entrance walk, 30 mm; guide lights sequence along the route. |
| 193–288 | 8–12 s | Galaxy and counter-rotating precision rings, 44 mm. |
| 289–344 | 12–14.33 s | Existing wonder reaction and small smile, 75 mm. |
| 345–480 | 14.33–20 s | Moving chamber reveal, 18 mm. |
| 481–576 | 20–24 s | Closing movement, 17 mm; title and credits added during encoding. |

## Sound and review status

The completed V5 stereo mix retains the original score and eleven measured gait contacts. Filtered footfalls gain short damped metal/rubber resonances; locally synthesized layers provide the airlock, ventilation and instrument hum. No rain or antique grinding is used. Technical audio QA is complete; final perceptual balance and synchronization still require the finished film. See [soundtrack records](../audio/v5/README.md).

Still previews cover the entrance, instrument, reaction and room. The six-second motion proof samples the walk, rings and room reveal. A passed structural/dependency audit is evidence of preservation and portability, not a substitute for reviewing the complete movie.

## Version preservation and deliverables

V5 is saved separately. The original, Arrival, Celestial and Wonder movies and earlier Blender scenes remain on disk. No prior movie or scene was deleted for the redesign.

- Built: `observatory-v5.blend`, `previews/v5/frame_*.png`, V5 soundtrack and scene audit.
- In progress: `previews/v5/Astra-Chamber-motion-proof.mp4`.
- Pending: `The Last Observatory - Astra Chamber.mp4`, `renders/v5/frames/`, final movie QA and `renders/v5/hero-4k.png`.

## Concept provenance

![Earlier image-generated design concept](concepts/v5/astra-chamber-concept.png)

The concept was generated with the built-in image generation tool using `renders/v4/frames/0420.png` as an edit reference. It established the visual direction; it is distinct from the actual Cycles preview above. Saved concept: [astra-chamber-concept.png](concepts/v5/astra-chamber-concept.png). Exact prompt: [image-prompt.txt](concepts/v5/image-prompt.txt).
