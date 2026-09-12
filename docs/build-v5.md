# Build and render Astra Chamber (V5)

Completed on 2026-09-12: the editable scene, six-second motion proof, full 576-frame film and native 4K hero image are delivered. Scene preservation, portable rebuild, full movie decode and encoded audio checks pass. Representative final shots, sequential motion-proof samples, title/credits and the hero still were visually reviewed. Full real-time playback and perceptual listening were not performed. See the [delivery manifest](../renders/v5/render-manifest.json), [movie QA](../renders/v5/movie-qa.json) and [AAC QA](../audio/v5/final-aac-qa.json).

## Software

Use **Blender 4.5** with Cycles. This project uses the local macOS ARM build at `tools/Blender4.5.app/Contents/MacOS/Blender`; Blender is not expected to be bundled in a portable submission. Run commands from the project root. Geometry building and the audit do not require a GPU.

Encoding and audio use Python 3 with `Pillow`, `imageio-ffmpeg`, `numpy` and `scipy`. The scripts add `tools/python/` to the module search path; if that local dependency bundle is absent, install those packages in your Python environment. `imageio-ffmpeg` supplies the FFmpeg binary. The encoder accepts `OBS_SERIF_FONT` and `OBS_SANS_FONT` overrides; defaults look for macOS fonts or Linux DejaVu fonts.

```sh
export BLENDER_BIN="$PWD/tools/Blender4.5.app/Contents/MacOS/Blender"
export PYTHON_BIN=python3
```

Set `BLENDER_BIN` to your own Blender 4.5 executable on another machine. The render script selects Metal on macOS and falls back to CPU on setup failure; `OBS_CPU=1` explicitly selects CPU. It does not configure CUDA/OptiX for other platforms. Do not run several renders simultaneously on the same GPU.

## Required project inputs

| Task | Required files |
|---|---|
| Rebuild V5 geometry | `observatory-v4.blend`, `scripts/build_scene_v5.py`, `scripts/scifi_dressing_v5.py`, and the material/model inputs below. |
| Preserve actor appearance | Five external textures under `assets/character/heroine_v4/`: `f004_body_color.tga`, `f004_body_normal.tga`, `f004_head_color.tga`, `f004_head_normal.tga`, `f004_opacity_color.tga`. The rig, native body motion and facial animation are baked into the V4 scene. |
| Exterior sky | `assets/hdri/stars/starmap_2020_8k_gal.exr`; the world nodes are inherited from V4. |
| Manufactured finishes | In `assets/v5/materials/Metal032/`, `Metal050A/` and `Plastic010/`, the matching `*_Color.jpg`, `*_Roughness.jpg`, `*_Displacement.jpg` maps: 2K, 4K and 2K respectively. |
| Walkway | `assets/v5/materials/rubber_tiles/rubber_tiles_diff_2k.jpg` and `rubber_tiles_rough_2k.jpg`. |
| Reused service bays | `assets/v5/models/service-modules.blend` plus all six image fallbacks in `assets/v5/models/textures/`. The builder checks those fallbacks and appends the library's packed images. |
| Render an already built scene | `observatory-v5.blend`, `scripts/render_v5.py`, the five actor images, 8K sky and eleven used material maps. The six service images are packed in the saved scene. |
| Encode final film | All `renders/v5/frames/0001.png` through `0576.png`, `audio/v5/last_observatory_v5_mix.wav`, `scripts/encode_v5.py` and Python/FFmpeg dependencies. |

The V5 builder starts from the baked V4 scene, not from original character FBX imports. It preserves the actor and Astra galaxy directly; `galaxy_v3.py` and original character/motion files are provenance or earlier-stage rebuild inputs, not imports of the V5 builder. Retain the completed V4 scene for both rebuilding and the preservation audit.

**Raw kitbash archives are not runtime or V5 build dependencies.** The complete candidate scenes under `assets/v5/kitbash_candidates/`, Kenney archives, material ZIPs and unused PBR channels are research inputs. Production uses the curated library and explicit images above. Its four meshes have no linked-library dependency. See [production model provenance](../assets/v5/models/provenance.json) and [selected resources](resources-v5.md).

## Build, audit and still previews

```sh
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/build_scene_v5.py
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v5.py
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- preview 15 82 224 317 420 540
```

The builder saves `observatory-v5.blend` and `renders/v5/reused-assets.json`. It reads V4 without saving over it. The audit reloads V4 and V5, writes `renders/v5/preservation-audit.json` and `docs/submission-assets-v5.json`, and raises an error on a failed check. Still previews are 960 × 540 at 24 samples in `previews/v5/frame_####.png`.

Changing the builder does not update the saved scene automatically. Rebuild before rendering changes. Do not rebuild or mix scene versions into an active final frame sequence.

## Motion proof

```sh
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- proof
"$PYTHON_BIN" scripts/encode_acting_v5.py
```

This produces 144 proof frames at 960 × 540, using source frames 97–144 (walk), 205–252 (galaxy/rings), and 401–448 (room). The mapping is written beside them under `previews/v5/acting-frames/`. The six-second proof movie is `previews/v5/Astra-Chamber-motion-proof.mp4` with matching soundtrack excerpts. Its encoder verifies 144 decoded frames. Review this motion proof before starting the final sequence.

## Audio

A completed 24-second, 48 kHz stereo master already exists at `audio/v5/last_observatory_v5_mix.wav`. Rebuilding it is optional for rendering/encoding. If needed, retain `audio/v5/walk_sync.json`, `audio/stems/original_underscore.wav`, `audio/stems/anticipation.wav`, `audio/v2/raw/stone_footsteps.wav`, and both `scripts/audio_mix_v5.py` and its imported helper `scripts/audio_mix.py`.

```sh
"$PYTHON_BIN" scripts/audio_mix_v5.py
```

The script discovers the platform FFmpeg executable through `imageio_ffmpeg.get_ffmpeg_exe()`; `--ffmpeg /absolute/path/to/ffmpeg` optionally overrides it. Audio regeneration needs no service credentials or new paid API request. [Audio documentation](../audio/v5/README.md) records source terms and measured mix results.

## Final render and encode

After motion review, the convenience command runs the final sequence, encode, decoded-frame validation, 4K hero render, scene audit, encoded audio verification and delivery manifest in order:

```sh
sh scripts/finish_film_v5.sh
```

The script uses the exported `BLENDER_BIN` and `PYTHON_BIN`. Alternatively, run the stages separately:

```sh
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- final 1 576
"$PYTHON_BIN" scripts/encode_v5.py final
"$PYTHON_BIN" scripts/validate_movie_v5.py
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- hero 420
```

Final render settings: 1920 × 1080, 24 fps, frames 1–576, Cycles 64 samples with adaptive threshold 0.025, denoising, shutter 0.4 and an 8192 texture limit to retain the catalog sky. The optional hero image is 3840 × 2160 at 128 samples.

The frame renderer writes temporary partial files before renaming and skips completed frames on resume. `renders/v5/frame-source.json` records the scene hash and render settings. If those change while frames exist, it refuses to combine them: move the previous V5 frame directory aside intentionally before rendering a new scene revision. Proof/test frames do not use this final-source guard and should likewise be kept consistent when rebuilding.

The final encoder requires all 576 valid, consistently sized PNGs plus a 24-second stereo mix. It applies the 2.39:1 matte, fades, title and credits, then writes H.264/AAC with BT.709 tags to `The Last Observatory - Astra Chamber.mp4`. `--prepare-overlays` generates title/credit previews alone; `--dry-run` validates inputs and prints the planned encode without making the movie. The movie validator checks decoded frame count, dimensions, rate and duration, then exports `previews/v5/final-contact-sheet.jpg`. That still requires visual inspection; it is not an automated artistic approval.

## Current preservation evidence

The latest [scene audit](submission-assets-v5.json) and [comparison report](../renders/v5/preservation-audit.json) pass for V5 SHA256 `50c416d855eb24389c44683ac7f8f1a1ed2929b5044044344af8ac4c69045f5c`, against V4 SHA256 `6f745b8ca4607860564a3b790287c3601ef1abcb47d2856754c4fc0ccb8990f7`.

- 524 scene objects; 24 reused service objects from exactly four selected source meshes.
- Actor family: three objects unchanged; 80 rig bones, 5,170 source mesh vertices and 175 facial morphs excluding Basis. Sampled surprise, wonder and smile controls remain active.
- Galaxy family: nineteen objects unchanged. Geometry, topology, UVs, morph coordinates, rest bones, relevant animation curves, material nodes and frame-1 transforms are compared, not merely object names.
- No retained legacy environmental meshes and no embedded text datablocks.
- All 23 image dependencies resolve: seventeen external project-relative images and six packed service images; no missing or external unpacked paths.
- Six camera cuts at frames 1, 37, 193, 289, 345 and 481; two animated precision-ring roots.
- Open airlock width about 3.62 m; sampled actor lateral clearances exceed 1.56 m at frames 37 and 82. This is a sampled bounds check, not an exhaustive collision simulation.

The original, Arrival, Celestial and Wonder movies remain separate, as do earlier scene versions. The audit verifies V4-to-V5 content preservation. Final V5 movie QA passes for 576 decoded frames at 1920 × 1080, 24 fps and exactly 24 seconds; encoded audio measures −17.7 LUFS and −3.5 dBTP with zero full-scale samples. The delivery manifest also verifies the previous movies and V4 scene against their original hashes.
