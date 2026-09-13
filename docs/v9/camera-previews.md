# Bow / bear escape — camera comparison

The user selected option C: bow versus the realistic bear. The new twelve-second study uses the same continuous performance and staging for two camera views, at 768×432, 12fps and eight Eevee samples. Title bands are added during encoding. These are motion and camera drafts with the licensed source female mannequin, not the final Rocketbox heroine or final cinematography.

- Third person: `previews/v9/third/Bear-Escape-third-person.mp4`
- First person: `previews/v9/first/Bear-Escape-first-person.mp4`
- Editable local scene: `bear-bow-escape-v9.blend`

| Frames | Performance |
|---|---|
| 1–31 | Bear approaches while she loads and aims |
| 32 / 35 | Bow release / arrow contact |
| 41–50 | She stows the bow as the bear commits to its attack |
| 51–68 | Native diving roll, transferred onto the female skeleton, carries her sideways out of the attack |
| 69–144 | She runs around the bear to the opening airlock; the bear turns into pursuit |

Native archer bow, stow and running motion are reused. The run's actual 18-frame gait cycle is sampled according to distance along the curved route, preserving foot speed. The existing Quaternius diving roll provides the body performance and measured 4.99m travel; its native acceleration and recovery are preserved. The bear uses its native walk, hit reaction, low attack and trot, with blends between clips.

The longbow turns across the back during the roll and receives a small, smoothly blended prop-only ground-clearance offset. Final evaluated character skin is grounded after the pose blends. The arrow meets an actual evaluated bear surface triangle and follows that triangle during the reaction and pursuit. The previous bear jaw correction remains in effect.

Both cameras are baked from the same scene. Third person transitions from the combat shoulder view to an offset chase view, keeping the pursuer from blocking the woman and doorway. First person follows the evaluated head with smoothing; the roll banks up to 55 degrees and has a reduced camera dip. It uses an independent arms-only mesh to prevent head/torso geometry covering the lens. No animation is changed between camera renders.

The final scene passed all 144-frame character/bear, bow/bear, floor and doorway intersection checks. See `previews/v9/collision-audit.json`. Sampled frame checks do not cover continuous subframe collision, cloth or fur. Movie decode checks and visual review are recorded separately in each camera's `movie-qa.json`. Full real-time playback has not been performed.

Build with `scripts/build_escape_v9.py`, using `escape_actor_motion_v9.py` and `escape_cameras_v9.py`. Render with `render_escape_v9.py -- third|first motion`; encode with `encode_escape_v9.py third|first`. Original film, accepted heroine, Astra scene and previous studies remain preserved. Heavy production rendering remains on hold. Source scenes containing the licensed archer remain local.
