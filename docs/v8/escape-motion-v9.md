# Bow, roll, run — reusable actor sampling

`sample_escape_motion(scene, target_rig)` in `scripts/escape_actor_motion_v9.py` returns all target-bone pose matrices in rig-local coordinates. The target is the same 117-bone, already-baked female Rig used in option C. The helper creates temporary source rigs, evaluates them at their original origin, and removes them after sampling. It does not render or alter the production actor's animation.

| Return key | Contents |
|---|---|
| `roll` | 18 poses over the complete native Quaternius `Roll_RM` (about 1.467 s) |
| `roll_progress` | 18 measured root displacement fractions, 0–1 |
| `roll_distance` | 4.9914317 m |
| `run` | 19 native female poses, source frames 1–19 inclusive |
| `run_cycle_distance` | 2.39999985 m |
| `run_source_fps` | 30 |
| `sheathe` | 10 native `HumanF@SheatheBack01_L` poses, source 1–23 |
| `report` | Rest compatibility, source frames, ground clearance and limb checks |

All planar root displacement is removed from the returned matrices. Place the actor once along the chosen world path. Vertical motion remains in the pose. The run's endpoint duplicates its initial gait pose; interpolate between adjacent samples and omit the duplicated endpoint when cycling. Its 18-frame cycle is 0.6 seconds at the original 30 fps, corresponding to 4 m/s. The complete action's longer range includes editing handles and a partial extra stride; it is not the correct loop boundary.

The roll advances throughout the dive and stops translating during its native recovery. Use `roll_progress`, not linear movement over all 18 samples. Its airborne phase comes from the native diving-roll animation. Quaternions should be slerped between adjacent samples; do not interpolate Euler angles across the full rotation.

The licensed archer pack includes forward/directional runs and strafes but no roll, dodge, jump or sprint clip. Therefore, the roll comes from the downloaded CC0 Quaternius UAL1. The retarget maps source bone rotations through their rest axes and rebuilds the female skeleton's own joint offsets. The intermediate source spine chain is reduced to her spine/chest, while hands and fingers retain their mapped motion; hand prop bones inherit their exact target-rest hand offsets. The helper keeps the native source skin's vertical clearance profile and corrects for target proportions, with a recorded maximum correction around 18.5 cm in the initial inspection.

The female source controller actions cannot be assigned directly to the already-baked production FK rig. Run and sheathe are evaluated on a fresh original controller rig and sampled to matrices first. The target rest matrices match exactly. Initial QA measured a run endpoint pose difference below 1.2 micrometres and roll joint-offset error below 1.3 micrometres; sampled final mesh floor contact is at zero during grounded stages, and airborne clearance is retained. These numerical checks do not replace the composed scene's visual review and weapon/terrain contact inspection.

Report: `renders/v9/escape-actor-motion-inspection.json`. Native archer assets and any scene containing them remain local under the Standard Asset Store EULA. The helper source can be published without the licensed data.
