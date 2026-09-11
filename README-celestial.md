# The Last Observatory — Celestial

V3 introduces an original adult expedition heroine and a rotating miniature galaxy inside the observatory. The 24-second arrival, moving camera shots, mechanical rings, and synchronized soundtrack continue from the previous revision.

**[Watch / download the finished trailer](https://media.githubusercontent.com/media/codersusu/game-cinematic-trailor/main/The%20Last%20Observatory%20-%20Celestial.mp4)** · [Walking preview](https://media.githubusercontent.com/media/codersusu/game-cinematic-trailor/main/previews/v3/Celestial-motion-1080p.mp4) · [Editable Blender scene](observatory-v3.blend)

![The rotating stellar spiral inside the observatory](docs/preview-v3.png)

**Movie complete:** all 576 frames rendered and decoded successfully at native **1920 × 1080, 24 fps, 24 seconds**. Representative frames, doorway poses, the galaxy and final titles were visually reviewed. Encoded stereo audio measures **−17.8 LUFS and −2.7 dBTP**, without clipping. [Review contact sheet](previews/v3/final-contact-sheet.jpg) · [Movie verification](renders/v3/movie-qa.json).

## What changed

The heroine starts from an original ImageGen concept reconstructed with **Meshy 7 Ultra**: a **3,024,348-triangle master**, 8K base color, and two 4K surface images. The integration script binds the detailed mesh through a 243,515-triangle rigging proxy and preserves the existing walk/contact timing. The rig supports body motion and head gaze; facial-expression performance is not part of this version.

A locally modeled galaxy contains **5,456 stars**, rotating arms, and a compact nucleus. The two outer brass gimbals remain, while the old solid globe and inner rings are hidden. Selective emission glow adds a stellar halo. Camera 02 uses a 48 mm lens aimed at the nucleus; the other cameras and camera travel are retained.

## Download the project

Large models, scenes, and movies use Git LFS. Install Git LFS before cloning:

```sh
git lfs install
git clone https://github.com/codersusu/game-cinematic-trailor.git
cd game-cinematic-trailor
git lfs pull
```

## Open and render

Double-click [Open Celestial.command](Open%20Celestial.command) on the Mac to open `observatory-v3.blend` in Blender. Keep the `assets/` folder with the scene. Opening and rendering the supplied assets requires no API keys.

| Delivery | File |
|---|---|
| Editable scene | [observatory-v3.blend](observatory-v3.blend) |
| 1080p, 24 fps, 24-second movie | `The Last Observatory - Celestial.mp4` |
| Separate native 4K still | [hero-4k.png](renders/v3/hero-4k.png) |
| Two-second native motion proof | `previews/v3/Celestial-motion-1080p.mp4` |
| Final QA and render manifest | `renders/v3/` |

The final render baseline is 64 Cycles samples with denoising; previews use 24 samples. The movie keeps a cinematic matte inside a native 1920 × 1080 frame. It reuses `audio/v2/last_observatory_v2_mix.wav` unchanged.

See the [v3 build and render guide](docs/revision-v3.md) for asset integration, Blender/Python setup, preview rendering, and the final pipeline. `scripts/finish_film_v3.sh` runs rendering, encoding, motion-proof extraction, validation, a separate 4K still, and the scene dependency audit. It uses `BLENDER_BIN` and `PYTHON_BIN` overrides. The previous [Arrival revision](README-arrival.md) and both earlier movies are preserved. Blender applications, Python runtimes, intermediate frame sequences, and temporary service responses are omitted from the repository.

## Credits

**Original heroine • Meshy 7 Ultra** — [character attribution](assets/character/heroine_v3/ATTRIBUTION.md) and [concept prompt](assets/character/heroine_v3/concept-prompt.md). Local galaxy geometry is original; [galaxy notes](docs/galaxy-v3.md) distinguish it from the distant [NASA/Goddard SVS star map](docs/sky-v2.md).

Scanned environment resources are from [Poly Haven, CC0](docs/assets-manifest.md). The generated character and [ElevenLabs audio](audio/v2/README.md) have separate service terms and are not CC0. Exact source links, adaptations, and license records accompany the assets. No API credentials are included in the public project records.
