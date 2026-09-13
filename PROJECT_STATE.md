# Current completed film — V13 native 1080p

V13 raises the picture to native 1920×1080, adds the original instrumental score **Beyond the Threshold**, and fixes the arrow passing through the bow hand. The arrow rests above the grip, follows a consistent release trajectory, and the bow arm is nearly extended with an outward bow tilt.

The final edit uses forest source frames 10–132 followed by room source frames 37–575 every other frame: **32.75 seconds, 393 frames, 12fps**. The first 0.75 seconds of inherited idle are omitted because the bow passed too close to the first-person camera. The same heroine, roll/run escape, run/look-back/walk entrance, single later surprise and index-finger approach remain.

## V13 files and finishing

- Forest: `bear-bow-forest-v13.blend`, approved SHA256 `9b39cf38ebb29f738b8e074e6cdb548d23054572633cc4746e859447c4bfb93a`.
- Room: `observatory-v12-run-entry.blend`, unchanged for this version.
- Final music: `audio/v13/forest_to_astra_music_final.wav`; original composition and untrimmed masters are preserved.
- Completed movie: `previews/v13/Forest-to-Astra-V13-1080p.mp4` — all 393 frames and the audio stream decode successfully; representative native images and the assembled contact sheet have been visually reviewed.
- Completed short shot check: `previews/v13/Bow-fix-1080p.mp4`.
- `scripts/finish_render_v13.py` resumes the missing frames sequentially and encodes the scored film. Run only one GPU job at a time. `previews/v13/pause-render` requests a graceful stop between frames.
- `previews/v13/review-state.json` records current state. Archery evidence is indexed by `archery-final-qa-manifest.md`; music checks are in `audio/v13/final-edit-qa.json`. Final encoding creates `combined-movie-qa.json` and a contact sheet for visual review.

Only verified native 1080p room frames are reused. All previous videos and source scenes remain available. Credits and the render approach are in `previews/v13/CREDITS.md` and `docs/v13/render-and-music.md`.

# Previous completed review — V12

Accepted direction: first-person forest escape, third-person Astra chamber. Use the same Microsoft Rocketbox FemaleAdult04 woman in both. She shoots the bow at the bear, rolls away and runs to the door. Inside she runs in, checks behind her, then walks toward the middle. Keep one later surprise/wonder close-up and the index-finger reach toward Astra.

## Current scenes and outputs

- `bear-bow-forest-v12.blend`: V10 dense forest and accepted bear/bow choreography with the actual room heroine; cropped copies of her real hands and jacket sleeves for first person. The first-person camera matches her eye height.
- `observatory-v12-run-entry.blend`: native run/stop, shoulder check, then native walking; later room performance preserved from source frame 225.
- `previews/v12/Room-entry-run-look-back-walk.mp4`: completed 6.5-second entrance review.
- `previews/v12/Forest-to-Astra-V12.mp4`: completed combined preview, decode-verified and reviewed in representative images.

The combined review uses 11 seconds of forest followed by 22.5 seconds of room footage, at 12fps with a 960×540 picture and review bands. It is silent. Final sound, final rendering quality, and the exterior/interior doorway geometry still need production work. Older scenes and films are preserved.

## Validation and rebuilding

`previews/v12/forest-character-build.json`, `forest-character-collision-audit.json` and `room-entry-audit.json` record the scene hashes and numerical checks. `docs/v12/performance-continuity.md` explains the performance changes. Sources for the new native run clips are recorded under `assets/character/heroine_v12/`.

Build with `scripts/build_forest_character_v12.py` and `scripts/build_room_entry_v12.py`. Render only one GPU job at a time using `scripts/render_review_v12.py`. Room footage from frame 227 onward can reuse V11 through the guarded `scripts/reuse_room_v12.py`; frame 225 is rerendered for motion-blur continuity. Encode the combined preview with `scripts/encode_review_v12.py`.

Licensed archer source assets and Blender scenes containing them remain local. The last public repository release is V7; newer local previews have not been submitted there.
