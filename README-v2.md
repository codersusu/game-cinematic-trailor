# The Last Observatory — Arrival

A 24-second cinematic revision with a young woman walking through an open bronze doorway, continuously rotating astronomical rings, and a Milky Way sky made from real star-catalog data. The character uses Blender Studio's stylized Rain rig; the detailed stone, bronze and lighting retain the original observatory setting.

## Deliverables

| File | Contents |
|---|---|
| `The Last Observatory - Arrival.mp4` | Revised 24-second movie, native 1920×1080, 24 fps, stereo sound |
| `observatory-v2.blend` | Editable scene, young keeper, walking animation, four cameras, animated gimbals and star world |
| `Open Arrival.command` | Opens the scene in bundled Blender 4.5 with tested GPU settings |
| `previews/v2/Arrival-motion-1080p.mp4` | Two-second native 1080p doorway crossing with synchronized sound |
| `audio/v2/last_observatory_v2_mix.wav` | 24-second 48 kHz stereo master with synchronized footfalls and continuous machinery |
| `audio/v2/stems/` | Eight editable full-length audio layers |
| `previews/v2/final-contact-sheet.jpg` | Representative frames decoded from the finished movie |
| `renders/v2/movie-qa.json` | Final movie decode and format verification |

The active image is approximately 2.39:1 inside a 1920×1080 frame with black mattes. Original v1 outputs remain untouched: `The Last Observatory.mp4`, `observatory.blend`, `renders/hero-4k.png`, and the original soundtrack. See `README-v1.md` for the earlier version.

**Production status: complete.** All 576 frames were rendered, encoded and decoded successfully. The delivered movie is exactly 24 seconds at 1920 × 1080 and 24 fps. The doorway walk, changing ring orientations, star background, title and credits passed visual review. Encoded audio measures −18.02 LUFS and −2.68 dBTP without clipping; footfall timing is synchronized to the animation.

## Movement

The opening eight seconds show her approaching and crossing the doorway, with planted-foot animation, alternating arm swing, body weight shifts and a settling glance toward the machine. Both doors are already open. The next four seconds examine the moving metalwork; the final twelve reveal the whole observatory and luminous celestial inlays.

The instrument's nested gimbals rotate throughout the film. Shared-axis supports stay attached, while the pedestal remains fixed. Banners also move subtly. The star map is fixed in world space and responds naturally to camera movement; its orientation is composed for the scene, rather than tied to a real site and date.

## Rebuild

Run from this directory:

```sh
./tools/Blender4.5.app/Contents/MacOS/Blender --background --python scripts/build_scene_v2.py
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory-v2.blend --python scripts/render_v2.py -- preview 64 130 390 520
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory-v2.blend --python scripts/render_v2.py -- final 1 576
python3 scripts/encode_v2.py final
python3 scripts/validate_movie_v2.py
```

`caffeinate -i /bin/zsh scripts/finish_film_v2.sh` runs rendering, encoding and validation in order. The Python encoder needs Pillow and the included imageio-ffmpeg package; use the bundled Python interpreter if system Python cannot import those dependencies.

The render uses Cycles Metal, MetalRT off, kernel optimization off, 48 samples with adaptive sampling and denoising, AgX and motion blur. The panorama texture cap is 8192 to preserve star detail. `OBS_CPU=1` selects CPU rendering. Blender needs access to host graphics even when run in background on this Mac.

Final rendering is resumable: existing numbered PNGs in `renders/v2/frames/` are skipped. Move old frames aside before rebuilding a changed scene; the renderer does not automatically invalidate them. Keep `assets/` alongside the Blender project so relative image paths resolve. A machine-readable completion check requires all 576 frames and the correct 24-second stereo audio before encoding.

## Sources and credits

**Rain Rig (CC) Blender Foundation | studio.blender.org** — [Blender Studio Rain](https://studio.blender.org/characters/rain/v3/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The model, rig and textures are reused; costume colors, walking animation, pose and corneal shadow handling were adapted for this film. [Character source and verification](assets/character/young_keeper/ATTRIBUTION.md).

**NASA/Goddard Space Flight Center Scientific Visualization Studio. Gaia DR2: ESA/Gaia/DPAC.** The 8K panorama is from [Deep Star Maps 2020](https://svs.gsfc.nasa.gov/4851/), visualization by Ernie Wright. The original EXR is preserved, with scene orientation/exposure adjustments. [Source, checksum and usage terms](docs/sky-v2.md).

**Powered by Poly Haven.** Scanned stone, metal, rock and original environment resources are CC0. [Individual assets and creators](docs/assets-manifest.md).

Sound effects use the authorized ElevenLabs account; the tonal underscore and additional atmospheric synthesis were authored for the film. One new footstep source was added for this revision. Generated audio is not CC0; usage rights depend on the account's plan and service terms. [Sound sources, synchronization and measured levels](audio/v2/README.md). No API keys are included in the scene or scripts.

The new scene assembly, architectural portal, lighting, cameras, nested mechanism animation, costume adaptation, walking choreography, audio edit and title design were created for this project. [Revision notes](docs/revision-v2.md) describe the shot plan and implementation.
