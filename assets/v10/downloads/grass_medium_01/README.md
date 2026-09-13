# Grass Medium 01 — denser V10 groundcover

Source: https://polyhaven.com/a/grass_medium_01
License: CC0-1.0, https://polyhaven.com/license
Artists: Rico Cilliers (modeling), Rob Tuytel (photography).

Downloaded native `grass_medium_01_2k.blend` and five 2K textures: 6 files, 21,249,553 bytes. Provider size/MD5 verified; SHA256 and exact URLs are in the parent `download-manifest.json`. All five native image references resolve. CPU import inspected; no GPU preview or scene edits performed by this acquisition step.

## Recommended clumps

These are dense, broad clumps compared with the earlier Bermuda blades. Use `grass_medium_01_large_a_LOD1`, `grass_medium_01_large_b_LOD1`, `grass_medium_01_large_c_LOD1`, and `grass_medium_01_mid_a_LOD1`. Avoid `geonodes_*` display duplicates and the `geometry_nodes` demo sphere. LOD0/LOD1/LOD2 versions are provided; LOD1 is suitable for preview foreground, LOD2 for farther banks. Reset display X offsets before instancing.

| Mesh | Triangles | Dimensions XYZ, m | Min local Z, m |
|---|---:|---|---:|
| grass_medium_01_large_a_LOD0 | 6422 | 0.317 × 0.327 × 0.147 | -0.0075 |
| grass_medium_01_large_a_LOD1 | 2301 | 0.327 × 0.332 × 0.145 | -0.0057 |
| grass_medium_01_large_a_LOD2 | 1011 | 0.327 × 0.327 × 0.135 | -0.0057 |
| grass_medium_01_large_b_LOD0 | 4626 | 0.284 × 0.276 × 0.169 | -0.0256 |
| grass_medium_01_large_b_LOD1 | 2447 | 0.291 × 0.291 × 0.165 | -0.0214 |
| grass_medium_01_large_b_LOD2 | 890 | 0.291 × 0.291 × 0.165 | -0.0214 |
| grass_medium_01_large_c_LOD0 | 5945 | 0.279 × 0.255 × 0.142 | -0.0215 |
| grass_medium_01_large_c_LOD1 | 2336 | 0.290 × 0.290 × 0.140 | -0.0194 |
| grass_medium_01_large_c_LOD2 | 1032 | 0.290 × 0.290 × 0.137 | -0.0194 |
| grass_medium_01_mid_a_LOD0 | 2287 | 0.216 × 0.221 × 0.218 | -0.0229 |
| grass_medium_01_mid_a_LOD1 | 1309 | 0.219 × 0.216 × 0.218 | -0.0229 |
| grass_medium_01_mid_a_LOD2 | 659 | 0.206 × 0.216 × 0.199 | -0.0041 |
| grass_medium_01_mid_b_LOD0 | 1257 | 0.188 × 0.201 × 0.178 | -0.0033 |
| grass_medium_01_mid_b_LOD1 | 662 | 0.188 × 0.183 × 0.178 | -0.0033 |
| grass_medium_01_mid_b_LOD2 | 334 | 0.188 × 0.182 × 0.178 | -0.0033 |
| grass_medium_01_mid_c_LOD0 | 1466 | 0.192 × 0.203 × 0.145 | -0.0214 |
| grass_medium_01_mid_c_LOD1 | 655 | 0.195 × 0.210 × 0.131 | -0.0077 |
| grass_medium_01_mid_c_LOD2 | 348 | 0.195 × 0.210 × 0.131 | -0.0077 |

## Material correction required in Blender 4.5

The native material correctly routes diffuse, dry diffuse, normal, roughness and alpha into its shader group. However, the group's internal Principled BSDF and Translucent BSDF both import with unlinked `Weight=0`. Set those Weight inputs to 1, or build a replacement material from the same maps, before judging the asset. `Dead Amount=0` already selects the green texture. Defaults: Wetness 0, Translucency .4, Hue .5, Saturation 1, Value 1.

`material-inspection.json` records outer controls and internal shader nodes/links. The parent's `asset-inspection.json` records every object, root bounds, dimensions, material links and image availability. This technical inspection does not certify the final lighting, color or plant density in the trailer.
