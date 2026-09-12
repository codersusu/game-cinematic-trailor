# The Last Observatory — Astra Approach

V7 brings the woman close to the Astra machine before she reaches toward it with her right hand. After her existing entrance and reaction, she takes a second natural walk of about two metres, stops beside the platform, and lifts her hand toward the galaxy. The approach shot shows her feet and the machine together; a closer side view follows the reaching gesture.

**Motion preview complete; final film rendering.** The continuous 5.67-second preview includes the extra walk and one-handed reach. Scene preservation, platform clearance, synchronized audio and portable rebuild checks have passed.

![Approaching Astra](docs/preview-v7.png)

[Watch the approach preview](https://media.githubusercontent.com/media/codersusu/game-cinematic-trailor/main/previews/v7/Astra-Approach-motion-proof.mp4).

The accepted Rocketbox character, entrance walk, facial expressions, sci-fi room and rotating Astra galaxy are retained. Previous films and scenes remain available, including [Astra Reach V6](README-v6.md) and [Astra Chamber V5](README-v5.md).

## Files

| File | Purpose |
|---|---|
| `observatory-v7.blend` | Editable scene with the second approach and one-handed reach |
| `Open Astra Approach.command` | Mac launcher using an installed Blender |
| `The Last Observatory - Astra Approach.mp4` | Revised 24-second, 1080p film |
| `scripts/heroine_approach_v7.py` | Native motion transfer and authored reach |
| `renders/v7/approach-performance.json` | Movement timing, distance and foot contact measurements |
| `renders/v7/scene-audit.json` | Preservation, continuity and platform-clearance checks |
| `audio/v7/README.md` | Additional synchronized footsteps and source attribution |

## Rebuild

Use Blender 4.5 LTS and the Python dependencies in `requirements.txt`. Keep the earlier scenes and all referenced assets in their repository locations.

```sh
python3 -m pip install -r requirements.txt
export BLENDER_BIN=blender
export PYTHON_BIN=python3
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/build_scene_v7.py
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v7.py
"$PYTHON_BIN" scripts/audio_mix_v7.py
sh scripts/finish_film_v7.sh
"$PYTHON_BIN" scripts/encode_acting_v7.py --native
```

The final renderer uses Cycles at 1920 × 1080 and 24 fps, up to 64 samples, denoising and motion blur. A verified V6 frame sequence allows the unchanged first 343 frames to be reused. Without that cache, a clean checkout renders all 576 frames. Rebuilds preserve the old scenes and movies.

Asset attribution remains in the [V5 source list](docs/resources-v5.md), [character attribution](assets/character/heroine_v4/ATTRIBUTION.md), [sky attribution](docs/sky-v2.md) and [V7 audio notes](audio/v7/README.md). No new paid API requests or downloaded character assets are required.
