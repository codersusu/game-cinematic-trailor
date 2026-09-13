# The Last Observatory — Forest to Astra (V13)

The latest film combines a first-person forest encounter and escape with a third-person Astra chamber sequence. The same Rocketbox heroine shoots an arrow at the bear, rolls away, runs to the doorway, checks behind her inside, then approaches the rotating galaxy. One later expression of wonder and an index-finger reach complete the scene.

**V13: native 1920 × 1080, 32.75 seconds, 12 fps, with the original instrumental score _Beyond the Threshold_.** This is an offline cinematic, not an interactive game. The arrow now rests above the bow grip and follows a consistent release direction. The opening omits 0.75 seconds of obstructed idle.

[Watch/download the newest video with music](https://media.githubusercontent.com/media/codersusu/game-cinematic-trailor/main/previews/v13/Forest-to-Astra-V13-1080p.mp4) · [Video file](previews/v13/Forest-to-Astra-V13-1080p.mp4) · [Credits](previews/v13/CREDITS.md)

![V13 film contact sheet](previews/v13/combined-contact-sheet.jpg)

## Sources and editable assets

This revision includes all project scripts and redistributable source assets, including earlier models and experiments. The [upload inventory](docs/v13/upload-manifest.json) records exact paths, sizes, hashes and exclusions. Large files use **Git LFS**.

- [Editable sci-fi room](observatory-v12-run-entry.blend): heroine, native run/look-back/walk entrance, facial acting, Astra mechanism and finger gesture.
- [Editable forest and bear](forest-environment-v13.blend): final dense forest, bear, lighting and cameras, with restricted archer data removed.
- [Project scripts](scripts/): scene construction, animation adaptation, shaders, rendering, music composition, encoding and verification.
- [Source assets](assets/): character models, vegetation, surfaces, sci-fi parts and source manifests/licenses.
- [Original music master and sources](audio/v13/README.md): final WAV/MP3, original composition, instrument samples, stems and measurements.
- [Redistribution audit and local rebuild order](docs/v13/redistribution-audit.md).

**Archer-pack exception:** Kevin Iglesias _Human Archer Animations FREE_ permits the rendered film but not public redistribution of raw/extractable pack data. The raw pack, its derived bow-scene files and two complete skeleton dumps are therefore absent. The full local production scenes remain intact. Independently acquire the pack through the creator's official download and follow the linked rebuild instructions to restore the full editable forest performance. The public forest copy preserves the environment and bear without those restricted components.

Blender installations, Python runtime bundles, credentials, signed service responses, automatic backups and individual render-frame caches are not source assets and are excluded. Research images without established redistribution rights are also excluded. Original files retain their individual licenses; this repository does not assign one blanket license to third-party assets.

## Download

Install Git LFS before downloading large files:

```sh
git lfs install
git clone https://github.com/codersusu/game-cinematic-trailor.git
```

To fetch only the latest video without all historical assets:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/codersusu/game-cinematic-trailor.git
cd game-cinematic-trailor
git lfs pull --include="previews/v13/Forest-to-Astra-V13-1080p.mp4"
```

## Render and verify

Use Blender 4.5 LTS and `python3 -m pip install -r requirements.txt`. The current room renderer is configured for Cycles/Metal on macOS; forest footage uses Eevee. The finishing driver accepts `BLENDER_BIN=/path/to/blender`. Restore the separately licensed forest pack/scene before running the complete film driver. The room and public environment scene can be opened independently.

[Render settings and edit](docs/v13/render-and-music.md) · [Video QA](previews/v13/combined-movie-qa.json) · [Archery QA](previews/v13/archery-final-qa-manifest.md) · [Music QA](audio/v13/final-edit-qa.json)

All 393 output frames decoded at 1920 × 1080/12 fps, and the audio stream decoded successfully. Representative native images and the assembled contact sheet were visually reviewed. The final original score is stereo 48 kHz, approximately −18 LUFS and −3.4 dBTP before AAC encoding. Full real-time playback and perceptual listening were not performed by the agent.

## Historical films — elevenlabs.io

Previous films and lightweight combat/camera reviews remain archived in this repository. See [V7](README-v7.md), [V6](README-v6.md), [V5](README-v5.md), and the versioned `previews/` folders. Earlier sound effects were generated with **elevenlabs.io**; their source manifests and service conditions remain attached. The old generation subscription tier is unverified, so those historical service outputs are not represented as CC0 or as commercially licensed. V13 uses its separate original composition and verified CC0 instrument recordings.
