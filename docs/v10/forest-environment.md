# Dense forest environment — V10

V10 builds a continuous forest around the accepted shoot / roll / run performance. Both V9 camera animations and all character, bear and weapon actions are preserved exactly; the build records a combined animation checksum.

The clearing is surrounded by overlapping near, middle and distant tree layers rather than ending at an empty horizon. Young conifers, fern colonies and two kinds of grass create a lower vegetation layer. Scanned mossy rocks connect the ground to the cliff entrance. A larger terrain mesh extends beyond the camera views, soft haze separates the distant tree layers, and subtle plant sway adds movement. The door's static equipment wings have a darker, weathered alloy finish.

The planted layout contains 365 mature trees, 246 young conifers, 835 fern colonies, 653 fine grass patches, 3,096 leafy grass clumps and 58 added rock instances. These are shared geometry instances. Trees, large rocks and tall plants are placed around the character paths and camera sight lines; the ground stays flat beneath the validated action. A worn clearing and escape trail remain legible.

## Reused assets

Existing CC0 PolyHaven assets supply mature fir trees, ferns, mossy rocks, the cliff face and the textured forest floor. New CC0 additions are Grass Bermuda 01, Grass Medium 01 and Fir Sapling. Downloads, source pages, hashes and exact object names are recorded in `assets/v10/downloads/`.

The imported grass shaders required compatibility work. The native Grass Medium node group imported zero BSDF Weight values in Blender 4.5. The final leafy material uses explicit native diffuse, alpha and normal maps with an authored green albedo mix; the fine Bermuda patches use a direct PBR leaf material. These material changes preserve the source files. Sapling twig alpha is connected explicitly.

Distant saplings and trees use reduced mesh variants. Nearby plants retain their source detail, and original source meshes are kept intact. The exact counts and triangle reductions are in `previews/v10/lod-report.json`.

## Review outputs

- Third person: `previews/v10/third/Forest-Escape-third-person.mp4`
- First person: `previews/v10/first/Forest-Escape-first-person.mp4`
- Editable local scene: `bear-bow-forest-v10.blend`

Each comparison is 12 seconds at 12fps, rendered with Eevee at 960×540 and 16 samples. Encoding adds title bands. The temporary female animation model is retained for this environment comparison; the accepted final heroine, final sound and production rendering remain later work.

The environment clearance audit checks all 144 frames against new trees and rocks, moving door leaves, camera surface proximity and the terrain beneath the character. Decorative grass and fern contact, small foliage visibility changes and motion between sampled frames remain artistic review concerns. Movie decode checks and representative image review are recorded per camera; full real-time playback is not claimed.

## Build

Run `scripts/build_forest_v10.py` in Blender 4.5 using the V9 scene and downloaded local assets. It uses `forest_grass_material_v10.py`, `forest_leafy_material_v10.py` and `forest_lod_v10.py`. Render with `render_forest_v10.py -- third|first motion`, then encode with `encode_forest_v10.py third|first`.

The scene contains licensed archer source data and remains local. Previous film versions, the Astra observatory, and the V8/V9 studies are preserved.
