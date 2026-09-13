# The Last Observatory

A 24-second Blender cinematic: a weathered keeper witnesses an ancient astronomical machine awaken inside a ruined observatory. Four shots combine a reused studio character, scanned surfaces and rocks, custom architecture and mechanical detail, authored animation, and original/generated sound design.

## Deliverables

| File | Contents |
|---|---|
| `The Last Observatory.mp4` | Completed movie: native 1920 × 1080, 24 fps, 24 seconds, stereo audio |
| `renders/hero-4k.png` | Separately rendered 3840 × 2160 hero still |
| `previews/motion-test.mp4` | Two-second native 1080p motion proof extracted from the corrected final frames |
| `observatory.blend` | Editable environment, character, lighting, cameras and animation |
| `audio/last_observatory_mix.wav` | Completed 24-second, 48 kHz stereo soundtrack |
| `audio/stems/` | Five separate full-length audio layers for editing |
| `renders/title-card-preview.png` | Title and credit layout preview |

The video places a roughly 2.39:1 active picture inside a 16:9 frame using black mattes. It is not a 4K video upscale. The hero image is a separate native 4K render. All listed delivery outputs are complete. The movie was decoded and checked for all 576 frames, 24-second duration, 1080p resolution, and 24 fps. Representative frames, the character blink, title/credit layout, and audio levels were checked.

Double-click `Open Observatory.command` to open the editable scene in the bundled Blender with the tested GPU settings applied to that session. The completed film and still show the final lighting; the editor opens in camera view for scene work.

## Rebuild and render

The project uses the Apple Silicon Blender 4.5 application at `tools/Blender4.5.app`. Run commands from this project folder. The render scripts select Cycles Metal, disable MetalRT and kernel optimization for the compatibility configuration, and enable denoising. Host GPU access is required for Metal; `OBS_CPU=1` explicitly selects CPU rendering.

```sh
./tools/Blender4.5.app/Contents/MacOS/Blender --background --python scripts/build_scene.py
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory.blend --python scripts/render.py -- preview 390 210 70
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory.blend --python scripts/render.py -- hero 420
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory.blend --python scripts/render.py -- test 180 227
./tools/Blender4.5.app/Contents/MacOS/Blender --background observatory.blend --python scripts/render.py -- final 1 576
python3 scripts/encode.py final --dry-run
python3 scripts/encode.py final
```

Python needs Pillow and imageio-ffmpeg; project-local packages are in `tools/python`, which the encoder imports automatically. If system Python cannot use those packages, use the same bundled Python interpreter that installed them. `python3 scripts/encode.py test` encodes a completed motion test. `--prepare-overlays` renders only the title/credit graphics and never starts a movie encode.

Final rendering resumes by skipping existing frame PNGs. Move prior frames out of `renders/frames/` before re-rendering a changed scene; skipped files are not automatically checked against scene revisions. The encoder refuses incomplete sequences, damaged PNGs, inconsistent dimensions, or an incorrectly sized soundtrack. Keep `assets/` alongside the Blender file so relative texture and source paths resolve.

## Credits

**Einar Rig (CC-BY) Blender Foundation | studio.blender.org**

Einar is the Blender Studio character from *Charge*, reused under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Original source](https://studio.blender.org/characters/einar/v1/). Changes include placement, pose, animation, and shader/driver compatibility adaptations. The original character was not generated or modeled for this project. Required attribution appears in the final credit overlay, video metadata, and accompanying source notes. See [character attribution](assets/character/ATTRIBUTION.md) and [integration notes](docs/character-plan.md).

Six Poly Haven asset sets provide scanned surfaces, rocks, and sky illumination under **CC0**. **Powered by Poly Haven.** Individual creators, links, and exact files appear in [asset credits](docs/assets-manifest.md) and `assets/download-manifest.json`.

Three effects were generated specifically for the film with **ElevenLabs Sound Effects V2**, using an existing authorized account key. The underscore, anticipatory air, and low impact were synthesized for this project. Generated ElevenLabs audio is **not CC0**; its usage rights depend on the account plan and service terms. Generation succeeded, but the API did not allow subscription-tier verification. See [audio sources and rights](docs/audio_manifest.md).

Architecture, armillary assembly, procedural detail, scene arrangement, camera animation, and typography were constructed for this project. Meshy credentials were located, but no Meshy generation was needed for this version. No API credentials are included in project scripts, asset manifests, or the Blender scene.

## Production details

[Production notes](docs/production.md) document implemented features, shot timing, render settings, and completed verification. Legacy source-character geometry attributes can emit nonfatal compatibility warnings. Changes made for the current scene do not make the source rig automatically portable to a game engine; a playable adaptation would need material, rig, effects, and performance work.
