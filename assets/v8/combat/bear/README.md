# Bear candidate — user supplied source

Source: [Realistic Animated Bear 3D Model](https://sketchfab.com/3d-models/realistic-animated-bear-3d-model-bffc3c87d2d148ff8533e1cc8a11c9f1), uploaded by **WildMesh 3D**. The uploader declares [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Preserve that attribution and identify project modifications. See `source-manifest.json` for provenance qualifications and hashes.

The original downloaded FBX and five textures are unchanged. This asset is being evaluated for a local draft. The creator warns of rigging issues in this older release. Background Blender inspection confirms 81 native clips and actual deformation; a visual pass remains necessary before locking it.

Import `source/Bear Animated.fbx` with Blender's FBX importer. The importer sets source frame rate to **30fps**. Keep the hierarchy `Bear_Animated` → `RigRoot` → `sm_3_0_0`; the visible bear faces **world −Y**. Place, turn and scale its top `Bear_Animated` empty. Its source scale is `(0.012, 0.012, 0.011)`, so multiply this by a uniform desired size factor rather than replacing it with `(1,1,1)`.

Set `RigRoot.animation_data.action` and explicitly assign `action.slots[0]` to `RigRoot.animation_data.action_slot`. Mute NLA tracks when directly evaluating an action. All textures are embedded; their external source paths refer to the creator's prior project and should be rewritten to this folder's corresponding `textures/` files before saving a portable scene.

Recommended paired-encounter clips have names `RigRoot|<name>|Animation Base Layer`:

| Name | Source frames | Staging note |
|---|---:|---|
| `Walk` | 1–52 | 1.75m native travel per cycle |
| `Run` | 1–18 | 4.38m native travel per cycle |
| `Trans_Stand_to_Run` | 1–36 | 3.31m pelvis travel |
| `Attack_StandAngry_01_Low` | 1–121 | Roughly stationary; easiest to place opposite the archer |
| `Attack_Run_01_AttackF` | 1–57 | About 10.95m native travel; requires deliberate path staging |
| `Hit_Stand_F01` | 1–88 | Roughly stationary hit response |

Root motion is on the armature object's local Z location. That becomes world −Y through the parent transform. Cancel that translation when driving a separate staged path; otherwise it doubles the motion. Preserve native pose channels, which contain the stepping and body action. Sampling found ground penetration of a few centimetres in walk/run, up to approximately 8cm in the run transition; the scene needs floor correction.

Inspection script: `scripts/inspect_bear_v8.py`. Report: `renders/v8/combat/bear-inspection.json`. No heavy rendering was performed for inspection.
