# V10 forest additions

Three reusable vegetation assets downloaded from Poly Haven for the denser forest preview. These files passed background Blender 4.5 import inspection; this is availability/material inspection, not final scene or rendered visual approval. No scene files were modified and no GPU rendering was performed.

## Sources and license

Both assets are CC0-1.0 according to the provider pages and [Poly Haven license](https://polyhaven.com/license).

- [Grass Bermuda 01](https://polyhaven.com/a/grass_bermuda_01): Rico Cilliers.
- [Grass Medium 01](https://polyhaven.com/a/grass_medium_01): Rico Cilliers (modeling), Rob Tuytel (photography). See `grass_medium_01/README.md` for clump choices and the required shader Weight correction.
- [Fir Sapling](https://polyhaven.com/a/fir_sapling): Rico Cilliers (modeling), Rob Tuytel (photography).

The download manifest records source URLs, provider MD5, local SHA256 and sizes. All 20 downloaded files passed provider size/MD5 verification: 64,407,318 bytes total. Fifteen imported image references resolve locally; the additional sapling alpha map is also downloaded.

## Import guidance

### Grass

Append selected objects from `grass_bermuda_01/grass_bermuda_01_2k.blend`. Prefer `grass_bermuda_01_medium_a` through `_medium_f`, plus `_seedling_a` through `_seedling_d`. Do not append the `geometry_nodes` demonstration sphere or duplicate `geometry_*` source objects.

These are individual grass blades/small tufts, approximately 7–15 cm high, not square-meter patches. Combine many with randomized rotation into patches or scatter linked instances densely. The native `grass_bermuda_01` material routes the downloaded alpha map through its shader group. Outer-link inspection alone does not establish usable shader output: check internal BSDF Weight inputs in Blender 4.5; the scene integration subsequently required a material correction. Reset source display positions before placing tufts. Local bounds and all variants are in `asset-inspection.json`.

| Object suffix | Triangles | Width × depth × height, m |
|---|---:|---|
| medium_a | 17 | 0.039 × 0.029 × 0.098 |
| medium_b | 8 | 0.051 × 0.022 × 0.075 |
| medium_c | 20 | 0.057 × 0.092 × 0.067 |
| medium_d | 14 | 0.055 × 0.016 × 0.102 |
| medium_e | 24 | 0.066 × 0.037 × 0.083 |
| medium_f | 30 | 0.041 × 0.026 × 0.113 |
| seedling_a | 147 | 0.068 × 0.046 × 0.151 |
| seedling_b | 140 | 0.077 × 0.049 × 0.127 |
| seedling_c | 128 | 0.037 × 0.045 × 0.092 |
| seedling_d | 268 | 0.070 × 0.083 × 0.152 |

### Saplings

Import `fir_sapling/fir_sapling_2k.gltf`. This imports exactly three variants, with no LOD variants in the file. Reset their source X positions (0, 1, 2 m) when placing them. Reuse linked mesh data.

| Object | Triangles | Height, m |
|---|---:|---:|
| fir_sapling_a | 157,402 | 1.301 |
| fir_sapling_b | 150,876 | 0.952 |
| fir_sapling_c | 124,743 | 0.736 |

The imported `fir_sapling_twigs` material does not wire alpha. Connect `fir_sapling/textures/fir_sapling_twigs_alpha_2k.png` as Non-Color to the Principled Alpha input and configure EEVEE transparency. The branch material requires no alpha change. Variant A mesh extends 7.9 mm below its root; B and C start essentially at zero.

## Existing large trees for background reuse

The V8 native `fir_tree_01_2k.blend` already supplies these lower-detail tree variants:

| Object | Vertices | Height, m | Source X offset, m |
|---|---:|---:|---:|
| fir_tree_01_a_LOD2 | 73,227 | 18.96 | 0 |
| fir_tree_01_b_LOD2 | 48,164 | 14.08 | 6 |
| fir_tree_01_c_LOD2 | 22,574 | 14.55 | 12 |

Reset display offsets; append only chosen objects, not all LOD/source collections. V8 also has reusable fern clumps, moss rocks, roots, fallen timber and forest floor maps. No local grass assets preceded this acquisition.

## Reproduction

`download_assets.py` fetches/resumes only verified selected asset files. `inspect_assets.py` imports them with Blender on CPU and writes object geometry, bounds, materials and image availability to `asset-inspection.json`. Candidate metadata includes researched but unselected alternatives; it does not imply those assets were acquired.
