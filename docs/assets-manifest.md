# The Last Observatory — asset manifest

Downloaded 2026-09-11 from the official Poly Haven public API and download CDN. **Powered by Poly Haven.** All six asset sets are **CC0**, including commercial use and redistribution. [Asset license](https://polyhaven.com/license). [API terms](https://github.com/Poly-Haven/Public-API/blob/master/ToS.md). These Poly Haven downloads required no paid assets or account credentials. This CC0 statement applies only to the six Poly Haven sets listed below; the Rain and original Einar characters are CC BY 4.0 and generated ElevenLabs audio follows its separate service license. See [character attribution](../assets/character/ATTRIBUTION.md) and [audio sources](audio_manifest.md).

Every downloaded production file is recorded with original URL, byte count and verified MD5 in `assets/download-manifest.json`. Download script: `assets/download_polyhaven.py`. API metadata is retained under `assets/metadata/`. The original overcast sky is retained for reference; Arrival uses the NASA panorama described in sky-v2.md. Material diffuse maps were visually inspected as a contact sheet at `assets/material-contact-sheet.jpg`.

| Asset | Role | Creator(s) | Local location | Source |
|---|---|---|---|---|
| Monastery Stone Floor | Weathered irregular slate floor, approx. 1.8 m tile | Amal Kumar | `assets/texture/monastery_stone_floor/` | https://polyhaven.com/a/monastery_stone_floor |
| Old Stone Wall 02 | Weathered masonry, approx. 2.085 m tile | Charlotte Baglioni | `assets/texture/old_stone_wall_02/` | https://polyhaven.com/a/old_stone_wall_02 |
| Rusty Metal 04 | Pitting/roughness pattern for bronze; source is rusty steel | Amal Kumar | `assets/texture/rusty_metal_04/` | https://polyhaven.com/a/rusty_metal_04 |
| Stone 01 | Scanned small rock, about 0.15 m long; scalable rubble | Dario Barresi; Rico Cilliers | `assets/model/stone_01/stone_01_2k.gltf` | https://polyhaven.com/a/stone_01 |
| Rock Face 01 | Scanned large rock face, about 7 m long; exposed ruin foundation | Dario Barresi | `assets/model/rock_face_01/rock_face_01_2k.gltf` | https://polyhaven.com/a/rock_face_01 |
| Kloofendal Overcast (Pure Sky) | Cool cloudy sky illumination | Greg Zaal | `assets/hdri/kloofendal_overcast_puresky/kloofendal_overcast_puresky_2k.exr` | https://polyhaven.com/a/kloofendal_overcast_puresky |

## Material channel wiring

Each texture directory contains four separate 2K maps; substitute the asset ID for `{id}`:

- `{id}_diff_2k.jpg`: sRGB → Principled BSDF Base Color.
- `{id}_rough_2k.jpg`: Non-Color → Roughness. For wet slate, mix toward 0.12–0.22 in puddled regions rather than lowering the entire surface uniformly.
- `{id}_nor_gl_2k.exr`: Non-Color → Normal Map node (Tangent Space) → Principled Normal. OpenGL Y-positive convention, correct for Blender; do not invert green.
- `{id}_disp_2k.png`: Non-Color → Displacement or Bump Height. Tune scale to the physical material; begin with 0.01–0.03 m for stone and 0.0002–0.001 m for metal. For true displacement, subdivide sufficiently and enable displacement in Cycles material settings. Keep wall/floor tile sizes close to the approximate dimensions above for believable scale.

The metal scan is **not bronze**: reuse its roughness and pitting, then author a copper-gold exposed metal plus dark/turquoise nonmetallic patina. Applying the original diffuse directly would create painted rusty steel. Color choices and procedural mask modification are original art direction, not a separate downloaded asset.

Both glTF models include their geometry `.bin` and texture dependencies in the correct relative structure. Blender glTF import should wire their materials automatically. Their `_arm_2k.jpg` packed texture is Non-Color: R = AO, G = Roughness, B = Metallic. `_nor_gl_2k.jpg` is the tangent-space normal, `_diff_2k.jpg` is sRGB base color. Preserve their UVs. Actual imported bounds should be measured before arranging/scaling.

The sky EXR feeds an Environment Texture node into World Background Color. Use a low/moderate strength for ambient illumination and an art-directed key light through the dome; the overcast sky alone will intentionally give soft, low-contrast light. A 2K lighting environment is adequate for an enclosed composition where the horizon is mostly obscured.

## Reproducibility and future quality passes

The kit is intentionally compact. All channels are 2K; the API metadata also exposes higher-resolution files if macro shots reveal texel limitations. Upgrade only surfaces actually seen close to camera. High-quality geometry, bevels and hero engravings must be built separately; texture detail cannot substitute for their silhouette.
