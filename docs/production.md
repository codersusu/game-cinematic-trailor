# The Last Observatory — production notes

This project is a 24-second offline cinematic made on an Apple Silicon Mac. A keeper reacts to an ancient armillary awakening in a ruined observatory. The brief prioritizes one compact setting, detailed materials, lighting, camera work, and a restrained human performance. 

## Shot and sound timing

| Timeline | Frames at 24 fps | Picture | Sound |
|---|---|---|---|
| 0–6 s | 1–144 | Close study of the bronze instrument; 65 mm camera, shallow depth of field | Rain and stone-chamber ambience |
| 6–12 s | 145–288 | Keeper portrait; subtle head/brow/blink/breath animation; 65 mm camera | Original low harmonic texture enters |
| 12–20 s | 289–480 | Moving 32 mm wide view reveals the armillary and ruined architecture | Bronze mechanism builds, with an anticipatory rise near 20 s |
| 20–24 s | 481–576 | 34 mm final view; luminous inlays and warm bounce light; transition to title | Edited alignment event begins at 20 s and decays into the ending |

The credit block fades in at 20.0–20.5 seconds and remains legible through 23.4 seconds. The title and the story line “THE STARS REMEMBER” fade in at 20.8–21.6 seconds. The scene fades toward black from 21–23 seconds; title and credits fade out with the entire picture at 23.4–24 seconds. Credits are two lines in the lower black matte, at approximately 22 and 20 pixels high in the 1080p master. The exact Einar attribution is retained.

## Implemented visual work

- Custom observatory construction, broken arches and masonry, floor design, scattered scanned rock, and procedural ruin detail.
- Custom nested armillary rings, engraved/mechanical geometry, celestial globe detail, and authored settling/rotation animation.
- Poly Haven 2K scanned textures adapted for slate, stone and weathered bronze. The source metal texture is rusty steel; bronze color and patina treatment are authored adaptations.
- Small refractive water beads on the mechanism and a spatially varying wet-floor material. The soundtrack suggests rain; this version does not implement a full falling-rain fluid simulation.
- Licensed Einar character appended from Blender Studio, with original clothing, groom, rig and painted textures. Integration repairs texture paths and outdated drivers/material connections, adapts the skin shader, and authors the restrained performance.
- Soft area lighting, cool sky/rim illumination, warm metal highlights, eye catchlights, animated lens illumination, a thin atmospheric volume, and sparse illuminated dust geometry.
- Cycles path tracing, AgX color management, camera depth of field, motion blur, denoising, and a restrained compositing glow when the compositor configuration is supported.
- A separate 24-second stereo mix with generated rain/mechanism/alignment effects and an original synthesized tonal underscore. No spoken dialogue or borrowed musical recording.

The scene contains editable three-dimensional geometry and camera animation. It is not an AI-generated image animated with camera pans. The project does not include gameplay input, enemy AI, damage systems, combat, or an engine-ready character export.

## Render configuration

| Output | Configuration |
|---|---|
| Native movie frame sequence | 1920 × 1080 PNG, 24 fps, frames 1–576, up to 48 Cycles samples per frame, adaptive threshold 0.03, denoising |
| Hero still | 3840 × 2160 PNG, up to 128 samples, adaptive threshold 0.015, denoising |
| Delivered motion proof | Native 1920 × 1080, final corrected frames 180–227, 48 frames / 2 seconds; the general test render mode remains 960 × 540 |
| Preview stills | 960 × 540, 24 samples |
| Movie encode | H.264 CRF 16, slow preset, yuv420p, AAC stereo 320 kbps, fast-start metadata |
| Audio master | 48 kHz stereo PCM WAV; measured −19.53 LUFS integrated, −1.63 dBTP, no clipped samples |

The selected compatibility configuration uses Blender 4.5 Cycles Metal with MetalRT **off** and kernel optimization **off**. Reflective/refractive caustics are disabled; rendered texture resolution is capped at 2K. The native 4K still therefore increases output resolution but does not automatically increase all source texture resolutions. Blender 5.2 GPU experiments stalled, so production uses 4.5. Consecutive full-HD GPU benchmark frames took approximately 20 seconds each, compared with roughly 56 seconds on CPU in the local comparison. These are short-test measurements, not a guarantee for every shot; the final movie has now completed decoding and representative-frame review. The two-second portrait test was inspected through the blink and passed continuity checks.

The 16:9 movie contains black top and bottom mattes, leaving an approximately 1920 × 804 active image. The separately rendered hero still retains its full 3840 × 2160 canvas. Delivering a native 1080p film and a separate 4K still avoids presenting an upscale as a higher-resolution render.

## Verification and delivery status

Completed: 576 Cycles frames, the 24-second H.264/AAC movie, the native 3840 × 2160 hero still, the corrected native 1080p two-second motion proof, and the editable Blender scene. The complete movie decoded successfully: 1920 × 1080, 24 fps, 24.0 seconds, BT.709 video and AAC audio. Frame integrity and sequence completeness passed before encoding.

Representative decoded frames from all four shots and the final title/credit overlays were visually inspected. The corrected open, closed, and reopened eyes were checked at frames 145, 191 and 195; the final motion proof uses frames 180–227. The final AAC soundtrack measured −19.2 LUFS integrated and −1.6 dBFS true peak, with no clipping. Audio verification was technical; perceptual listening was not performed by the agent.

`renders/movie-qa.json`, `renders/render-manifest.json`, `previews/motion-qa.json`, and `previews/final-contact-sheet.jpg` record the checks. `scripts/validate_movie.py` reproduces the movie decode and contact sheet. `scripts/motion_from_final.py` recreates the corrected motion proof from the final native frames.

## Source and portability records

- [Poly Haven asset manifest](assets-manifest.md): six asset sets, creator credits, licensing, map wiring and source URLs.
- [Character integration](character-plan.md): Einar source, CC BY attribution, adaptations, compatibility checks and rig limitations.
- [Audio manifest](audio_manifest.md): all effect prompts, synthesis description, source rights, timing and reproduction.
- `assets/download-manifest.json`: downloaded file URLs, sizes and verified checksums.
- `assets/character/ATTRIBUTION.md`: character attribution to carry with redistribution.

The free CC0 status of the Poly Haven resources does not apply to the CC BY character or generated ElevenLabs audio. Original source assets are retained for reproducibility. Credentials are read from authorized external projects and are never copied into the deliverable.

Opening-shot optimization: the off-camera `CH-einar` collection is excluded for frames 1–144 and restored before frame 145. A full-resolution macro frame was inspected after this change. Lights remain enabled.
