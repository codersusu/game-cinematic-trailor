# V8 animal opponent research

**Best visual candidate: WildMesh 3D's realistic animated bear, now acquired from the user and inspected in Blender.** The source preview shows a convincingly textured bear with a more natural silhouette than the freely downloadable stylized wolf options. Native deformation and actions are confirmed; shot-level visual review is still required before locking it for the film.

[Source model and normal download page](https://sketchfab.com/3d-models/realistic-animated-bear-3d-model-bffc3c87d2d148ff8533e1cc8a11c9f1) · Author: WildMesh 3D · [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The public model metadata reports 7,508 triangles, 3,799 vertices, 81 animations and download availability. Its public animation listing confirms these relevant clips:

| Native clip | Duration |
|---|---:|
| `Walk` | 1.667s |
| `Run` | 0.533s |
| `Sprint` | 0.467s |
| `Trans_Stand_to_Run` | 1.133s |
| `Attack_Run_01_AttackF` | 1.833s |
| `Attack_Run_01_Turn` | 1.600s |
| `Attack_StandAngry_01_Low` | 4.000s |
| `Attack_StandAngry_01_High` | 3.000s |
| `Attack_StandAngry_02_High` | 3.000s |
| `Hit_Stand_F01` | 2.867s |

The full listing, source links and thumbnail source are in `assets/v8/combat/research/bear-research.json`. `bear-preview.jpg` is the publisher's source preview, not a render from this project.

The creator states that this older release has **known rigging problems**. The standard download endpoint required a logged-in Sketchfab session; it returned HTTP 401 during initial acquisition. The user subsequently supplied the official ZIP. It contains a 44MB FBX and five textures, safely extracted under `assets/v8/combat/bear/`. No model data was extracted from the viewer. Blender confirms 81 actions at 30fps, with real root motion and deformation. Sampled walk/run poses show several centimetres of ground penetration, requiring floor correction. See `renders/v8/combat/bear-inspection.json` for actual action ranges and integration notes. The uploader-declared license is recorded; original asset ownership was not independently verified.

## Downloaded alternatives

Three small open assets were downloaded for comparison, with original source previews and source files under `assets/v8/animal-candidates/`:

- [CoinCoin's animated wolf](https://opengameart.org/content/animated-wolf), CC-BY 4.0. Textured fantasy wolf, visibly stylized. It is a better creature design than a plain faceted wolf, but does not match the realism target. ZIP includes FBX and a texture atlas.
- [Teh_Bucket's boar](https://opengameart.org/content/boar), CC0. Approximately 1K triangles, textured and rigged, with source-advertised walk and attack. Its angular silhouette is insufficient for a close cinematic opponent without major remodeling.
- [tomek's animated wolf](https://opengameart.org/content/3d-wolf-animation-for-game), CC0 available alongside GPL options. Source advertises idle, walk, run, jump, fly, land, cry, attack and die. The visible character proportions are cartoon-like and unsuitable for the requested realistic scene.

Provider download URLs and SHA-256 hashes are in `download-manifest.json`. `native-animation-inspection.json` records the actual imported action names and frame ranges. These were examined in background Blender without rendering. Source previews were visually inspected. None of these alternatives has been selected or integrated into the trailer.

## Excluded source

The [WildMesh realistic boar](https://sketchfab.com/3d-models/realistic-boar-javali-3d-model-0d6510a6e21b430fa31a345b3fa90a6f) currently reports **zero animations and no download availability** in the public API. It should not be described as an available animated combat asset, regardless of older search snippets.

Research checked 12 September 2026. No purchases, paid downloads, final scenes or heavy renders were made for this research.
