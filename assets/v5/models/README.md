# Curated V5 service modules

`service-modules.blend` contains only four reusable mesh objects, three Cycles materials and six packed texture images. It is a Blender library for appending, so opening it directly shows an empty scene. Append its objects through `scripts/scifi_dressing_v5.py`.

| Object | Source author | Adaptation |
| --- | --- | --- |
| Wall1 | Irondust | Normalized to 2.18 × 0.54 × 2.42m; WhiteColor atlas connected to Cycles |
| Locker1 | Irondust | Normalized to 0.52 × 0.50 × 2.22m; same atlas |
| pipe_05 | rubberduck, PBR adaptation by a52 | Rotated into a vertical service strip, normalized to 0.70 × 0.19 × 1.72m; clean satin metal |
| vent_mat | rubberduck, PBR adaptation by a52 | Original bevel evaluated; normalized to 1.10 × 0.34 × 0.78m; clean casing with original grille textures |

Geometry, UVs, material assignments, material nodes, packed image bytes and all 24 resulting instance transforms match the original dressing module. `curation-audit.json` records the comparison fingerprint. No original source scene, unrelated meshes, rusty tanks, animations, text scripts or linked libraries are retained. Six external texture copies provide relative-path fallbacks for the packed images.

These are background service assets. The Irondust panel relief is predominantly a normal map on simple geometry. The vent grille source is only 272 × 262px and is intended for small background use.

## Provenance and license

The source assets are published under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/), permitting reuse, modification and redistribution. Credits are retained for provenance.

- [Sci-fi environment pack — Irondust](https://opengameart.org/content/sci-fi-environment-pack). Source for Wall1, Locker1 and four WhiteColor atlas images.
- [PBR Industrial Asset Pack — a52](https://opengameart.org/content/pbr-industrial-asset-pack). Modernized Blender/PBR source for pipe_05 and vent_mat.
- [Original industrial asset pack — rubberduck](https://opengameart.org/content/high-quality-industrial-asset-pack). Original author states all included models and textures are CC0; some original textures are by yughues. Source preview backgrounds are not included or used in this curated library.

`provenance.json` records source archive hashes, source object names and the curated files' SHA-256 checksums. The full candidate downloads are research inputs and are not required to build V5.
