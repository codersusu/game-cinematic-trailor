# V5 orbital observatory material kit

Four downloaded CC0 PBR surfaces selected for the orbital observatory redesign. The existing Astra galaxy remains a separate project asset. Nothing here changes production scenes.

| Material | Local directory | Realistic use after visual inspection |
|---|---|---|
| [Metal032](https://ambientcg.com/view?id=Metal032), 2K | `Metal032/` | Quiet cool grey satin alloy for the main structural rings, supports and trim. Broad soft highlights and fine surface grain; no rust. This is the preferred general-purpose metal. |
| [Metal050A](https://ambientcg.com/view?id=Metal050A), 4K | `Metal050A/` | Bright polished aluminum with fine multidirectional handling scratches. Suitable for machined fittings, narrow edge bands and hero hardware. It is not a directional brushed-metal finish. |
| [Plastic010](https://ambientcg.com/view?id=Plastic010), 2K | `Plastic010/` | Pale smooth polymer, with restrained fine scratches. Suitable for manufactured panel shells and console housings. Its base-color map is light grey; the reference preview appears paler under lighting. |
| [Rubber Tiles](https://polyhaven.com/a/rubber_tiles), 2K | `rubber_tiles/` | Near-black matte rectangular rubber tiles with shallow seams and modest scuffs. Useful for technical walkway inserts and anti-slip zones; it is used flooring, not pristine metallic decking. |

All four base-color maps were inspected together in [the local contact sheet](metadata/diffuse-contact-sheet.jpg). The three ambientCG material previews were also inspected and retained in `metadata/`. No Poly Haven website preview renders were copied: its material assets and website imagery have different terms.

## Blender integration

`metadata/manifest.json` gives precise file/channel mappings, source URLs and SHA256 hashes. Paths there are relative to this directory. `metadata/SHA256SUMS` provides a flat inventory. Original ambientCG ZIPs and supplied material wrappers are retained; use the image channels directly for controlled scene integration.

- Color / Diffuse: **sRGB**, to Principled Base Color.
- Roughness / Rough: **Non-Color**, to Principled Roughness.
- Metalness: **Non-Color**, to Principled Metallic for both metals. Plastic010 and rubber use Metallic = 0.
- NormalGL / nor_gl: **Non-Color**, through a Normal Map node with real UVs. Blender uses the OpenGL map; do not also connect NormalDX.
- Displacement: **Non-Color**. For these clean close-fitting surfaces, prefer a restrained Bump node; begin with roughly 0.1–0.3 mm micro-detail and inspect at shot scale. Rubber seam depth may need a little more. These are artistic starting values, not source-calibrated heights.
- Avoid combining strong normal and displacement bumps: the manufactured surfaces should keep clean silhouettes. For box projection, a small height-based bump is safer than feeding tangent-space normals a mismatched mapping.
- Rubber Tiles covers 2 m per texture repeat according to its official page. The ambientCG materials have no physical scale asserted here. Panel joins, fasteners, vents and structural silhouette should be modeled separately; these are surface finishes, not ready-made spacecraft panels.

Use Metal032 for the large-area satin finish, Metal050A sparingly for sparkle, Plastic010 for pale shells and Rubber Tiles for dark walking surfaces. Directional brushed grain would require an intentional shader adaptation or a different source material.

## Sources and license

The three ambientCG assets and their material preview renders are [CC0 1.0](https://docs.ambientcg.com/license/), including commercial use, modification and redistribution. Rubber Tiles by **Amal Kumar / Poly Haven** is [CC0](https://polyhaven.com/license). These asset licenses do not change the surrounding project's license. Credit is optional under the asset licenses; suggested credit: “Materials: ambientCG; Rubber Tiles by Amal Kumar / Poly Haven.”

Powered by Poly Haven. Its API response was used to resolve direct material downloads; `metadata/rubber_tiles-files.json` records the response. Every downloaded Poly Haven channel was checked against the provider's byte count and MD5, then given a SHA256 in the manifest. No account, API key or paid download was needed.
