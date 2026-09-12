# The Last Observatory — Astra Reach

V6 adds a one-handed reach after the woman stops and reacts to the Astra galaxy. She turns her shoulders slightly, raises her right arm along a gentle arc, opens her fingers and holds the gesture. A new four-second close camera makes the movement visible before the closing room shot.

**Final film rendering:** the new scene, preservation checks, portable rebuild and four-second motion preview are complete. The revised full-resolution film is rendering.

![The one-handed reach](docs/preview-v6.png)

[Watch the reach preview](https://media.githubusercontent.com/media/codersusu/game-cinematic-trailor/main/previews/v6/Astra-Reach-motion-proof.mp4).

The same character, native entrance walk, surprise/wonder expressions, sci-fi room and Astra galaxy remain. This is an attempt to reach toward the distant stars; she remains standing and does not physically contact the galaxy. The V5 soundtrack and 24-second running time are retained.

## Files

| File | Purpose |
|---|---|
| `observatory-v6.blend` | Editable scene with the baked reach and new camera |
| `Open Astra Reach.command` | Mac launcher using the installed Blender |
| `The Last Observatory - Astra Reach.mp4` | Revised 1080p film; pending |
| `previews/v6/Astra-Reach-motion-proof.mp4` | Continuous four-second reach preview, decoded and sampled for visual review |
| `scripts/heroine_reach_v6.py` | Authored upper-body, arm, wrist and finger animation |
| `renders/v6/scene-audit.json` | Detailed V5-to-V6 preservation and motion checks |

## Rebuild and render

Use the same Blender 4.5 LTS and Python dependencies as [V5](README-v5.md). Keep `observatory-v5.blend` and its `assets/` alongside the new scene. No new downloaded assets or service credentials are required.

```sh
python3 -m pip install -r requirements.txt
export BLENDER_BIN=blender
export PYTHON_BIN=python3
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/build_scene_v6.py
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v6.py
"$BLENDER_BIN" --background --disable-autoexec observatory-v6.blend --python-exit-code 1 --python scripts/render_v6.py -- proof
"$PYTHON_BIN" scripts/encode_acting_v6.py
sh scripts/finish_film_v6.sh
```

The final pipeline uses Cycles at native 1920 × 1080, 24 fps and up to 64 samples, with denoising and motion blur. It encodes a 2.39:1 active image, title and credits inside the 1080p frame. If the verified original V5 frame sequence is available, it copies frames 1–359 and renders the remaining 217 frames. A clean checkout renders all 576 frames. The frame-source hash guard prevents mixing different V6 scenes.

## Preservation and animation

The read-only scene audit compares every rig bone and camera over frames 1–359, plus a motion-blur boundary sample at 359.5. All sampled values match V5 exactly. Root, pelvis, legs and feet remain unchanged for the entire film. Geometry, materials, facial shape animation, environment, galaxy, sky and render settings are also unchanged.

Only upper-spine, right shoulder, arm, wrist and finger rotations change after frame 360. The gesture is authored and baked onto a copy of the native action. It uses the actual exported joint positions and leaves no live IK constraints or external control dependencies. The lowest spine bone stays untouched because this rig's thighs inherit from it. The new camera uses quaternion interpolation to keep its short orbit continuous.

The new gesture is animation, not interactive gameplay. It does not add sitting, physical contact, dialogue or a machine reaction. The accepted Rocketbox model retains its existing skin and hair detail.

All earlier films and scenes are preserved. [Astra Chamber V5](README-v5.md) · [Wonder V4](README-v4.md) · [Celestial V3](README-celestial.md) · [Arrival V2](README-arrival.md).

Asset attribution remains in the [V5 source list](docs/resources-v5.md), [character attribution](assets/character/heroine_v4/ATTRIBUTION.md), [sky attribution](docs/sky-v2.md) and [audio documentation](audio/v5/README.md). No new paid API requests were made.
