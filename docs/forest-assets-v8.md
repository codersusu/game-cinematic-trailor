# V8 forest asset selection

The planned exterior uses a misty fir woodland with ferns, exposed roots, fallen timber and mossy rocks. A narrow path reveals the existing sci-fi doorway inside a wooded rock face. This preserves the accepted room and Astra galaxy while establishing a natural place outside it.

**Status: assets acquired and import compatibility verified.** This report does not claim that final forest lighting, shot composition or environmental animation is visually approved. Those belong to the V8 scene and motion review before heavy rendering.

All newly selected assets come from **Poly Haven** under [CC0](https://polyhaven.com/license). The assets can be reused, modified and redistributed with the project. Their original artists are credited below. No generative service, API key or paid asset was needed.

| Asset | Artist | Source geometry | Use |
|---|---|---:|---|
| [Fir Tree 01](https://polyhaven.com/a/fir_tree_01) | Rico Cilliers; photography Rob Tuytel | Three tree variants; provider reports 7.85M triangles across the asset | Detailed conifer canopy and trunks; native Blender file preserves Geometry Nodes and LODs |
| [Fern 02](https://polyhaven.com/a/fern_02) | Rico Cilliers; scans Rob Tuytel | Four clumps; 6,232 triangles total | Near-camera foliage and path edge |
| [Rock Moss Set 01](https://polyhaven.com/a/rock_moss_set_01) | Kless Gyzen | Six rocks; 63,127 triangles total | Mossy foreground stones and roots of cliff |
| [Dead Tree Trunk](https://polyhaven.com/a/dead_tree_trunk) | Rob Tuytel | 101,802 triangles | Fallen log beside the path |
| [Root Cluster 01](https://polyhaven.com/a/root_cluster_01) | Jenelle van Heerden; Rico Cilliers | 225,261 triangles | Ground relief near tree bases and doorway |
| [Forest Floor](https://polyhaven.com/a/forest_floor) | eye-candy.xyz | PBR texture, approximately 2.1m tile | Leaf litter, mud, roughness and shallow displacement |

Existing `assets/model/rock_face_01` can be reused for the doorway cliff. The existing overcast sky may also be reused for illumination. The exterior can use a restrained cold dawn grade and drifting low fog, with the warm/cyan doorway drawing the character onward.

## Local files

All assets are under `assets/v8/forest/`. Ground and small props use the provider's 2K texture variants. The fir uses the native 2K `.blend`, including all 18 texture dependencies. The unmodified native file is 219MB before its textures. Use linked mesh/collection instances when dressing the forest, rather than duplicating the underlying mesh data for every tree.

- `fir_tree_01/fir_tree_01_2k.blend`
- `fern_02/fern_02_2k.gltf`
- `rock_moss_set_01/rock_moss_set_01_2k.gltf`
- `dead_tree_trunk/dead_tree_trunk_2k.gltf`
- `root_cluster_01/root_cluster_01_2k.gltf`
- `forest_floor/forest_floor_diff_2k.jpg`
- `forest_floor/forest_floor_nor_gl_2k.jpg`
- `forest_floor/forest_floor_rough_2k.jpg`
- `forest_floor/forest_floor_disp_2k.png`

The fern glTF material needs its separate alpha map connected to the Principled Alpha input: `fern_02/textures/fern_02_alpha_2k.png`. Set the alpha texture to non-color data. This preserves the fine frond silhouettes. The fir native Blender material already contains its alpha/mask setup.

## Verified Blender structure

Blender 4.5.13 successfully imported all four glTF assets and appended the fir library. All 30 imported image references resolved. All 44 downloaded files matched the provider MD5 and file size; total asset data is 485,774,270 bytes (486MB decimal). No frames were rendered in this asset inspection.

The fir has baked tree meshes ready to append individually, so no procedural conversion is required:

| Object | Vertices | Height | Suggested placement |
|---|---:|---:|---|
| `fir_tree_01_a_LOD1` | 138,058 | 19m | Main tall forest tree |
| `fir_tree_01_b_LOD1` | 90,714 | 14m | Main alternate tree |
| `fir_tree_01_c_LOD1` | 43,277 | 14.5m | Lighter canopy variation |
| `fir_tree_01_a_LOD2` | 73,227 | 19m | Distant instances |
| `fir_tree_01_b_LOD2` | 48,164 | 14m | Distant instances |
| `fir_tree_01_c_LOD2` | 22,574 | 14.5m | Distant instances |
| `fir_tree_01_c_LOD0` | 620,039 | 14.5m | Near-camera hero tree with modeled needles |

Append only the selected objects with `bpy.data.libraries.load(...).objects`, then link them into the scene. Appending the entire root collection would bring every LOD and all construction parts into view together. The B and C variants are displayed at X=6m and X=12m in the source library; their placement should be reset when instanced in the exterior. Their original mesh data can be shared across object instances. LOD0 A/B use approximately 5.34M/2.90M vertices, so reserve those for genuinely close views if needed.

## Acquisition and verification

`assets/v8/forest/download_assets.py` downloads only the curated files and checks provider file size and MD5 before accepting them. The local download manifest also records SHA-256. It can be rerun to verify or restore the selected files. Original provider file manifests and selected metadata are kept in `metadata/`.

`assets/v8/forest/inspect_assets.py` imports and inspects geometry, collections and texture references in background Blender without rendering. Its report is `asset-inspection.json`. This asset pass does not launch a final cinematic render.

Selection researched on 12 September 2026 using the primary asset pages and public Poly Haven API. The [current API page](https://polyhaven.com/our-api) states that API use is also free, including commercial use; the project clearly credits Poly Haven.
