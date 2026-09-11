# Celestial — v3 build and render guide

V3 replaces the earlier character with an original adult expedition heroine and replaces the solid astronomical centerpiece with a rotating, locally modeled galaxy. The ruined observatory, camera travel, 24-second edit, and synchronized v2 soundtrack are retained. Earlier revisions remain separate.

**Status: character binding and the final movie are complete.** The rig, walking animation and detailed master are integrated. Character pose and sole-contact checks are documented in the [validation record](../assets/character/heroine_v3/validation.md), with a retained proof image and measured sole heights. All 576 movie frames decoded successfully at 1920 × 1080, 24 fps, exactly 24 seconds. The encoded AAC soundtrack measures −17.8 LUFS and −2.7 dBTP. Results are retained in [`movie-qa.json`](../renders/v3/movie-qa.json) and the [review contact sheet](../previews/v3/final-contact-sheet.jpg).

## Character and centerpiece

The heroine was designed as an original realistic ImageGen concept, then reconstructed with **Meshy 7 Ultra**. The saved unremeshed master has **3,024,348 triangles**, an **8192 × 8192 base-color image**, and two **4096 × 4096 surface images**. The master itself is unrigged. Concept, exact prompt, settings, geometry/image statistics, and model are retained under [`assets/character/heroine_v3/`](../assets/character/heroine_v3/).

[`heroine_v3.py`](../scripts/heroine_v3.py) is the integration path: a 243,515-triangle proxy carries the rig, and interpolated skin weights bind the high-detail master while preserving its materials and UVs. Alignment guards reject an incompatible master/proxy fit. Imported upper-body motion is combined with authored planted-foot motion on the existing walk path. The walk runs through frame 240, with the final trailing-foot closure at frame 252; existing footsteps remain synchronized. Head gaze is supported, but this is a limited character rig: **no facial-expression or lip-sync performance is claimed**. The confirmed `rigged.glb`, `walking-woman.glb` and `master.glb` paths and source cycle are recorded in [manifest.json](../assets/character/heroine_v3/manifest.json); binding and representative character poses have been verified.

The galaxy is **5,456 modeled stars** arranged in eight meshes, with winding arms, sparse outliers, and a resolved central nucleus. Its tilted disk rotates 165 degrees over the film, with subtle differential rotation. The solid globe, polar spindle, and two inner gimbals are hidden; the **two outer engraved brass gimbals** retain their mechanical animation. [`compositor_v3.py`](../scripts/compositor_v3.py) uses the emission pass for selective glow so the stars receive a halo without broadly washing out stone contrast. The distant NASA star panorama is a separate background, not the locally modeled galaxy. Details: [galaxy notes](galaxy-v3.md) and [sky source](sky-v2.md). The central northern pier is replaced by a broad archway, clearing the night-sky backdrop behind the galaxy in the closing composition.

## Edit and output settings

The timeline is **24 fps, 576 frames, 24 seconds**. Arrival occupies frames 1–192, instrument detail 193–288, wide view 289–480, and final view/title 481–576. Camera travel is retained; camera 02 now uses a **48 mm lens aimed at the nucleus**. The other cameras are unchanged. The title retains **THE STARS REMEMBER**.

| Output | Location and settings |
|---|---|
| Editable scene | `observatory-v3.blend` |
| Final frames | `renders/v3/frames/0001.png`–`0576.png`; native 1920 × 1080, 64 samples, adaptive threshold 0.025, denoising |
| Movie | `The Last Observatory - Celestial.mp4`; H.264 CRF 16, AAC stereo 320 kbps, BT.709 limited range |
| Hero still | `renders/v3/hero-4k.png`; native 3840 × 2160, 128 samples, threshold 0.015 |
| Preview/test render | `previews/v3/` or `renders/v3/motion-test/`; 960 × 540, 24 samples |
| Native motion proof | `previews/v3/Celestial-motion-1080p.mp4`; final frames 49–96 with matching audio |
| Soundtrack | Reused unchanged: `audio/v2/last_observatory_v2_mix.wav` |

The movie uses black mattes for an approximately 2.39:1 active image inside its 16:9 frame. The separate 4K still is not evidence of a 4K movie. Cycles Metal retains the established Mac configuration: MetalRT off, kernel optimization off, 8K texture cap, and reflective/refractive caustics off. `OBS_CPU=1` selects CPU rendering.

## Open or rebuild

On this Mac, double-click [`Open Celestial.command`](../Open%20Celestial.command) to open the editable scene in Blender. The launcher looks for `BLENDER_BIN`, the project-local Blender 4.5 application, Blender on the command path, or `/Applications/Blender.app`.

For scripted work, use Blender 4.5 and Python with Pillow and imageio-ffmpeg. The scripts also load project-local packages from `tools/python/`. Set `BLENDER_BIN` and `PYTHON_BIN` to executable paths, or leave them as command-path names. FFmpeg uses imageio-ffmpeg discovery; `IMAGEIO_FFMPEG_EXE` can override it. `OBS_SERIF_FONT` and `OBS_SANS_FONT` override the macOS/Linux font fallbacks.

Run from the project root. The confirmed rig, animation and master paths are already recorded in `assets/character/heroine_v3/manifest.json`:

```sh
export BLENDER_BIN=blender
export PYTHON_BIN=python3

# Assemble the scene from the retained assets and integration modules.
"$BLENDER_BIN" --background --python scripts/build_scene_v3.py

# Inspect representative frames, a short motion test, and the hero still.
"$BLENDER_BIN" --background observatory-v3.blend --python scripts/render_v3.py -- preview 64 224 390 492
"$BLENDER_BIN" --background observatory-v3.blend --python scripts/render_v3.py -- test 49 96
"$PYTHON_BIN" scripts/encode_v3.py test
"$BLENDER_BIN" --background observatory-v3.blend --python scripts/render_v3.py -- hero 420

# Run the final render, encode, motion-proof extraction, and movie validation.
sh scripts/finish_film_v3.sh

# Read progress without changing the scene or render.
"$PYTHON_BIN" scripts/render_status_v3.py
```

For the project-local Mac application, set `BLENDER_BIN` to the absolute path ending in `tools/Blender4.5.app/Contents/MacOS/Blender`. Building from retained files does not require regenerating the concept or calling Meshy. Keep `assets/` alongside the project; the character manifest records the required file paths.

Rendering is resumable: numbered PNGs already present are skipped, and newly rendered files are renamed from temporary paths only after writing succeeds. **Move old v3 frames aside before rendering a changed scene**, because resume does not detect changes to geometry, lighting, materials, or animation. Earlier versions' frame folders are not used.

Encoding can be run separately with `python3 scripts/encode_v3.py final --dry-run`, followed by the same command without `--dry-run`. It requires all 576 valid, consistently sized frames and the 24-second stereo soundtrack. The movie is renamed from a partial path after encoding succeeds. `proof_v3_from_frames.py` extracts the native motion proof; `validate_movie_v3.py` decodes the film and exports its QA record/contact sheet. Representative final movie frames were visually inspected for doorway clearance, walking poses, spiral visibility, camera compositions, and title/credit legibility. The final AAC stream was decoded and measured for loudness and peak level; its timing reuses the verified v2 soundtrack.

## Credits and source records

- **Original heroine • Meshy 7 Ultra** — [attribution and service terms](../assets/character/heroine_v3/ATTRIBUTION.md), [original concept prompt](../assets/character/heroine_v3/concept-prompt.md), [generation settings](../assets/character/heroine_v3/generation-settings.json), and [measured master statistics](../assets/character/heroine_v3/master-stats.json). The generated character is not CC0. This is also the encoder's default character credit; `OBS_CHARACTER_CREDIT` can override it.
- **Local galaxy** — original procedural geometry and animation; the supplied visual reference informed art direction but its pixels, text and logos are not included. [Galaxy notes](galaxy-v3.md).
- **Distant star map** — NASA/Goddard Space Flight Center Scientific Visualization Studio; Gaia DR2: ESA/Gaia/DPAC; visualization by Ernie Wright. [Source and usage record](sky-v2.md).
- **Scanned environment assets** — Poly Haven, CC0. Individual creators and exact files are in the [asset manifest](assets-manifest.md).
- **Sound** — generated ElevenLabs effects plus original synthesized layers, reused from v2. [Audio sources and rights](../audio/v2/README.md). ElevenLabs output follows the account/service license and is not CC0; the available API did not verify the account tier.

Temporary signed service URLs and API credentials are excluded from public project records. Final frame counts, hashes, settings and review findings are recorded in [`render-manifest.json`](../renders/v3/render-manifest.json).
