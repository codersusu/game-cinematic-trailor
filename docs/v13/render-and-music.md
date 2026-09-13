# V13 — Native 1080p, music and arrow clearance

The requested update raises the picture from 960×540 to 1920×1080, adds an original instrumental score, and corrects the arrow passing through the bow hand. The final sequence is32.75 seconds with first-person forest and third-person room, at the current 12fps review cadence. The export uses a clean 16:9 picture without review title bands.

Forest frames render with Eevee at 16 samples; changed room frames use Cycles at 32 samples with denoising. Only verified source frames already rendered at 1920×1080 are reused. No upscaling substitutes for the new renders. The safe cached room range is 227–417, sampled every other source frame for 12fps delivery.

The score moves from forest tension to a restrained doorway pause and a warmer Astra reveal. Music sources, cue timings and mastering checks are recorded in `audio/v13/`. The final movie uses 48kHz stereo AAC audio.

The arrow now uses a physical shelf above the grip and a narrower shaft. Bow aiming and release share one trajectory; the nearly extended bow arm and outward bow tilt keep the pose readable. Native1080p first-person frames20 and32 were visually accepted before the full forest render. Arrow geometry and contact checks are recorded under `previews/v13/archery*.json`. Previous scene and video versions are preserved.

The existing single room surprise, native run/look-back/walk entrance, same heroine in both scenes, and index-finger approach remain part of this cut. The exterior/interior doorway geometry and full sound-effects pass remain separate production work.

The sequential finishing driver is `scripts/finish_render_v13.py`. It locks the approved scene hashes, resumes missing native frames, renders one GPU job at a time, and calls `scripts/encode_review_v13.py` only after both sections complete. The encoder checks all393 input images, decodes all393 output frames and the audio stream, and creates a representative contact sheet for final review.

The final edit starts the forest at sourceframe10, omitting0.75 seconds of the inherited idle in which the bow upper limb crossed too close to the first-person camera. The accepted shot, roll and run are retained. Music uses `audio/v13/forest_to_astra_music_final.wav`, trimmed by the same amount with a120ms fade-in. The room cut is now at10.25 seconds.
