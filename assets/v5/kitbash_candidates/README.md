# V5 downloaded mechanical asset candidates

Two author-hosted CC0 asset archives were acquired and inspected in Blender 4.5 with embedded scripts disabled. The archive and every extracted file have SHA-256 checksums in `acquisition-manifest.json`. The `kenney/` sibling directory was acquired separately and is outside this manifest.

| Candidate | Actual local source | Inspection | Intended use |
| --- | --- | --- | --- |
| Industrial PBR, rubberduck / a52 | `industrial/OGA_industrial_a52_version/industrial_final_cycles.blend` | 59 meshes, 11,633 base vertices; mostly 1K textures, some 2K | Pipes, service fittings, tanks, console silhouettes |
| Sci-fi environment, Irondust | `irondust/Sci-fi env2/Meshes.blend` and `Meshes.fbx` | 23 meshes, 244 base vertices; three 4K color atlases plus 2K ramp maps | Background panel/door/locker texture dressing |

The first pack has the stronger actual geometry. Useful object names are `pipe_01` through `pipe_11`, `control_terminal_mat`, `tank_control_panel_mat`, `tank_2_mat`, `vent_mat`, and `wall_thing_mat`. Source dimensions vary considerably; normalize against the intended scene scale when appending.

Irondust's walls and doors are mostly cuboids: nearly all apparent grooves and panel detail come from an atlas normal map. It is unsuitable as the main close-up airlock or hero console without added geometry. Its legacy `.blend` has a non-node material and an unresolved `BluePack_Albedo.tga` reference. Available atlases are named `BlueColor_*`, `WhiteColor_*`, and `OrangeColor_*`. The inspection preview explicitly connects WhiteColor albedo, normal, and emission maps to a Cycles material in memory. The original files remain unmodified. FBX files are present but have not been separately imported or verified.

The industrial `.blend` contains 112 image datablocks, of which 15 point to unavailable legacy/baked images. This does not mean 15 production materials fail; some are unused remnants. The main PBR texture folders are supplied, and the selected render proof checks their actual appearance. A historical absolute author texture path exists in the unmodified upstream `.blend`; public inspection metadata records only its filename. Do not copy stale image references into a production scene. Reconnect chosen materials to supplied maps, then pack or use repository-relative paths.

`proof/contact-sheet.jpg` is a neutral Cycles evaluation of nine selected parts, not the final film. `preview_candidates.py` is a local inspection helper only, not production code. It normalizes each displayed part to the same bounding size, so relative object scale is intentionally not preserved. Visual review found all nine selected parts usable without missing-texture magenta. The industrial pipe bundle and vent add useful silhouettes; the Irondust WhiteColor panels read convincingly at medium distance. Fine grooves remain normal-map shading on flat cuboids, and the service props have dated or low-resolution surfaces. The proof does not demonstrate AAA hero-asset quality. These packs offer supplementary detail, not finished hero architecture.

## Sources and redistribution

- [PBR Industrial Asset Pack — a52](https://opengameart.org/content/pbr-industrial-asset-pack): CC0; modern Blender/PBR adaptation.
- [Original industrial assets — rubberduck](https://opengameart.org/content/high-quality-industrial-asset-pack): author states all models and textures are CC0; some textures by yughues. The separately mentioned CC BY-SA preview background is not an asset used here. Do not use upstream preview images as film material.
- [Sci-fi environment pack — Irondust](https://opengameart.org/content/sci-fi-environment-pack): CC0.
- [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/): source asset license; allows copying, modification, and redistribution. Credits are retained for provenance.

The manifest records the exact public download routes and file integrity. These are author-published license statements, not proof of authorship beyond the source attribution.

## Promising but not acquired

- [Designersoup, 42 kitbash parts](https://designersoup.itch.io/free-kitbash-parts): listing states CC BY 4.0, but the anonymous download route returned HTTP 403. No file obtained.
- [Chuck_CG, 12 free sci-fi panels](https://chuckcg.gumroad.com/l/WISiT): Gumroad checkout/email route and insufficiently clear redistribution terms. No checkout or email submission.
- [Markom3D free kitbash](https://markom3d.gumroad.com/l/Free3DKitbash): CC0 listing but checkout required. No file obtained.
- [masterxeon1001 mech kitbash](https://blendswap.com/blend/9655): CC0 listing; official download requires sign-in. No protected viewer extraction or authentication bypass.
