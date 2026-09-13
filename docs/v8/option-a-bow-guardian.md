# Option A — bow versus forest guardian

This is an eight-second, 12 fps choreography comparison in the actual forest layout. It uses Kevin Iglesias's native feminine source mannequin as an explicitly identified proxy. The accepted Rocketbox woman has not yet been retargeted for this comparison. The guardian's walk and attack are native; projectile flight, visible string, impact chips and torso recoil are authored.

## Timeline

| Output frames | Action |
|---|---|
| 1–24 | Guardian approaches; woman holds a low bow ready pose |
| 25–35 | Native feminine arrow load |
| 36–59 | Draw and anchor close shot; guardian raises its arms |
| 60 | Release, cut back to the encounter |
| 61–63 | Arrow flight and stone impact |
| 64–78 | Guardian recoils; archer recovers |
| 79–96 | Both settle into ready poses |

Source actions: `HumanF@BowIdle01`, `HumanF@BowShot01 - Load`, `HumanF@BowShot01 - Hold`, `HumanF@BowShot01 - Release`; guardian `Walk`, `Melee_Hold`, `Attack`. The guardian's two in-place walk cycles cover 2.1 m, matched to its measured planted-foot sweep. The 3 m final actor spacing allows a threatening forearm attack while the bow release interrupts its advance.

## Scene and build

- Build: `scripts/build_option_a_v8.py`
- Scene: `option-a-bow-guardian.blend` — local only, contains licensed archer data
- Scene report: `previews/v8/options/a/scene-report.json`
- Shared renderer: `scripts/render_combat_option_v8.py -- a stills 1 36 63 88`, then `-- a motion`

The source archer rig contains world-space control constraints. Rotating it directly distorted the evaluated body, so the native performance is first visually baked at its original origin, using each bone's evaluated parent transform. Controllers and constraints are then removed, and the baked actor is placed in the forest. All saved actions, string points, prop transforms and effects use regular animation data; no frame-change handler or embedded script is required.

## Checks and limits

The evaluated female mesh's lowest vertices remain at z=0.13994–0.13996 m through sampled poses, and its standing height remains approximately 1.7 m. Guardian feet vary by approximately 2 cm across sampled walk and attack poses. The bow grip matches the source left hand prop attachment exactly at ten sampled frames, including load, anchor, release and recovery.

The initial frames 1/36/63/88 and final blue-hour frames 36/63 were visually inspected. Both actors, the full drawn bow and string are readable, and eight restored background firs establish the forest context. The exported movie passes the shared renderer's 96-frame/12-fps/eight-second decode checks. A six-stage contact sheet and 16 additional transition/impact frames were visually inspected; continuous realtime playback is not claimed. The first export exposed an abrupt guardian Walk to Melee_Hold stance change. This was corrected by holding the native Walk underneath a five-frame blend at frames 41–46; evaluated height now rises smoothly from 2.660 m to 3.308 m while the feet remain within 2 cm. The attack and release timings are unchanged. The replacement movie uses scene hash 5580f65b7779d13ff39127cead781c4763b09cc952b9de29c2c5ad411a0f655f. Its consecutive transition frames 39–48 and shot frames 60/63 were visually inspected; the stance change now progresses smoothly. The final movie is `previews/v8/options/a/Option-A-draft.mp4`. These checks do not establish final collision/contact cleanup. The proxy body, final heroine retarget, bow limb flex, guardian moss and cinematic materials remain outside this lightweight comparison's finish level.

## Reuse and licensing

Forest guardian and Uplon/Quaternius alternatives are described in `combat-assets-and-actions.md`. The archer is the user-supplied Kevin Iglesias pack under the Standard Asset Store EULA. Rendered output is usable in the trailer; its reusable meshes, rigs and animation source must remain local and must not be committed to GitHub. This restriction also applies to production `.blend` files containing them.

For the bear comparison, import `build_option_a_v8.py` and call `prepare_forest()`, `add_archer(scene)`, `setup_camera(scene)` and `bake_archer_props(scene, actor, target_provider)`. The target provider returns a world-space impact point at each output frame. `add_archer` includes the required source-pose bake.
