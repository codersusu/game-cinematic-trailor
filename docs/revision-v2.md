# The Last Observatory — Arrival revision

The revision turns the original atmospheric tableau into an arrival sequence. A young woman crosses an open bronze doorway, enters the ruined observatory, and approaches the continuously rotating instrument beneath an astronomical star panorama. Her performance is restrained; the environment and machine carry the later shots.

## Editorial plan

| Frames | Time | Shot |
|---|---|---|
| 1–192 | 0–8 s | Full-body entrance through open doors; slow lateral camera move |
| 193–288 | 8–12 s | Close view of rotating bronze gimbals |
| 289–480 | 12–20 s | Observatory reveal, keeper beside the instrument, Milky Way through the dome |
| 481–576 | 20–24 s | Luminous constellation inlays, continuing rotation, title and credits |

The walk starts at (-3.8,-7.6,0.14), passes the doorway at Y=-5.8, and ends at (-3.8,-0.8,0.14). The character remains outside the raised central dais. Individual footfalls are synchronized in audio/v2/walk_sync.json. Both door leaves are already open; no door-opening sound is implied.

The machine uses nested gimbals so shared-axis bearings remain attached during large rotations. The fixed pedestal supports an outer 78° yaw and inner 180°/−210°/240° travel over 24 seconds. Subtle banner motion adds life without distracting from the mechanism.

The visible sky is NASA's 8K Deep Star Maps 2020 EXR, using real catalog positions, brightness and color. It is oriented for the shot, rather than calibrated to a specific geographic location/date. It remains fixed in world space during camera movement. See sky-v2.md for provenance and credits.

## Working files

- scripts/build_scene_v2.py: reproducible scene assembly.
- scripts/young_keeper.py: appended Rain rig, outfit adaptation, foot plants and walking animation.
- scripts/armillary_v2.py: nested mechanical rotation.
- scripts/star_sky_v2.py: astronomical background and separate diffuse illumination.
- scripts/render_v2.py: Cycles Metal render, previews and resumable final frames.
- scripts/encode_v2.py:24 fps movie, title, credits and sound.
- scripts/finish_film_v2.sh: final render, encode and decode validation.
- renders/v2/ and previews/v2/: isolated v2 outputs; v1 is preserved.

Final rendering uses Blender 4.5 LTS, Cycles Metal, MetalRT off, kernel optimization off, AgX, motion blur, denoising, native 1920 × 1080 frames and a 2.39:1 letterboxed composition. The sky texture cap is 8192, preserving stars rather than reducing the panorama to 2K.

## Review status

Environment, character integration, and the native 1080p walking proof passed visual review. Character foot contacts and mechanical axle attachment were checked. The delivered movie passed full decode and visual review: 576 frames, 24 seconds, 1920 × 1080, 24 fps. Encoded audio measures −18.02 LUFS and −2.68 dBTP without clipping. The two-second native walking proof includes synchronized sound. See renders/v2/movie-qa.json and render-manifest.json for final records. The old oversized triangular dust mesh is hidden in both the editable scene and renderer.
