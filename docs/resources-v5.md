# V5 selected resources and completed integration

Updated 2026-09-12. The V5 room has been built and still previews reviewed. Its motion proof is rendered and representative sequential frames reviewed; the final film is rendering. The central Astra galaxy and baked V4 character performance are preserved.

## Materials used in the scene

| Resource | Download | Actual use in `build_scene_v5.py` |
|---|---|---|
| [ambientCG Metal032](https://ambientcg.com/view?id=Metal032) | 2K, CC0 | Satin structural alloy and a darker charcoal deck variant. |
| [ambientCG Metal050A](https://ambientcg.com/view?id=Metal050A) | 4K, CC0 | Polished machined rails, platform edges, fittings and fasteners. Fine scratches, not directional brushing. |
| [ambientCG Plastic010](https://ambientcg.com/view?id=Plastic010) | 2K, CC0 | Pale perimeter shells, airlock panels and console housings. A polymer surface adapted for the manufactured-shell design. |
| [Poly Haven Rubber Tiles](https://polyhaven.com/a/rubber_tiles), Amal Kumar | 2K, CC0; 2 m repeat | Nine dark walkway inserts. The texture has modest wear and shallow seams; it is not polished metal. |

The three ambientCG finishes use Color, Roughness and Displacement JPG maps. Color is tinted, roughness is remapped into restrained ranges, and the height map drives a 0.2 mm bump with strength 0.18. Object-coordinate box projection keeps the finish continuous without tangent-normal mapping artifacts. Metallic values are authored in the shader; the downloaded metalness and normal maps are not runtime dependencies. Rubber uses only its diffuse and roughness JPGs.

The [material manifest](../assets/v5/materials/metadata/manifest.json) records exact sources and hashes for the full downloads. The [material README](../assets/v5/materials/README.md) and local diffuse contact sheet record visual inspection. The [saved-scene dependency audit](submission-assets-v5.json) identifies the smaller subset actually used.

## Curated service modules used in the scene

`assets/v5/models/service-modules.blend` is the portable production library. It contains four normalized mesh objects, three Cycles materials and six packed images. `scifi_dressing_v5.py` appends these objects and creates six perimeter service bays, for 24 placed objects total.

| Selected object | Source | Adaptation and role |
|---|---|---|
| `Wall1` | [Irondust sci-fi environment pack](https://opengameart.org/content/sci-fi-environment-pack), CC0 | Reconnected WhiteColor atlas; 2.18 × 0.54 × 2.42 m wall panel. |
| `Locker1` | Same Irondust pack, CC0 | Reconnected WhiteColor atlas; 0.52 × 0.50 × 2.22 m locker beside each panel. |
| `pipe_05` | [Industrial PBR pack by a52](https://opengameart.org/content/pbr-industrial-asset-pack), from rubberduck, CC0 | Vertical 0.70 × 0.19 × 1.72 m service strip with clean satin metal. |
| `vent_mat` | Same industrial pack, CC0 | Evaluated bevel, clean casing, original grille texture; 1.10 × 0.34 × 0.78 m background vent. |

The industrial provenance also credits yughues for some original textures. The selected files and archive hashes are recorded in [production provenance](../assets/v5/models/provenance.json). [Curation QA](../assets/v5/models/curation-audit.json) confirms that geometry, UVs, materials, packed image bytes and all 24 instance transforms match the pre-curation dressing. No unrelated source objects, linked libraries, animations or embedded scripts remain in the curated library.

All six image files also exist in `assets/v5/models/textures/` as relative-path fallbacks. Keep them for building: the dressing script checks for these files even though the library images are packed. An already saved V5 scene uses its packed copies.

The panels' grooves are mainly mapped onto simple geometry, and the vent texture is only 272 × 262 pixels. These assets are used as secondary perimeter detail. The panoramic structure, airlock, console forms, hero rings and platform are custom modeled geometry with actual bevels, thickness, connections and fasteners.

## Inherited assets

The builder loads `observatory-v4.blend` and retains the character and galaxy families directly. It does not rerun character import, retargeting or galaxy generation. The actor is Microsoft Rocketbox Female Adult 04 with native motion, 175 source facial morphs and an authored facial performance, under the documented MIT source license. The 5,456-star galaxy is original procedural project work. The exterior 8K star map is NASA/Goddard SVS Deep Star Maps 2020, with ESA/Gaia/DPAC data credits; it is not relabeled CC0. See [V4 performance](performance-v4.md) and [sky provenance](sky-v2.md).

The V5 soundtrack reuses original synthesized music and the prior ElevenLabs footfall recording, with new locally synthesized modern-room layers. These audio assets are not CC0; see [audio provenance](../audio/v5/README.md).

## Research inputs that are not build dependencies

Raw Irondust and industrial archives, their full extracted scenes, the earlier nine-object proof and Kenney candidate packs remain acquisition/research records under `assets/v5/kitbash_candidates/`. They are not loaded by the production builder and need not accompany the runtime project. The same applies to unused texture channels and material ZIPs.

[Kenney Space Station Kit](https://kenney.nl/assets/space-station-kit) and [Modular Space Kit](https://kenney.nl/assets/modular-space-kit) were downloaded and inspected but not selected. Their stylized proportions were a weaker fit. The Chuck_CG panel candidate was not acquired. No paid purchase or account signup was needed for the selected material/model set.

## Records and reproduction

- [Curated model README](../assets/v5/models/README.md) and [source/license/checksum manifest](../assets/v5/models/provenance.json).
- [Original candidate inspection](../assets/v5/kitbash_candidates/README.md) and [acquisition manifest](../assets/v5/kitbash_candidates/acquisition-manifest.json).
- [Saved V5 scene audit](submission-assets-v5.json) and [V4-to-V5 preservation comparison](../renders/v5/preservation-audit.json).
- [Current design and shots](design-v5-astra-chamber.md) and [reproducible build/render instructions](build-v5.md).
