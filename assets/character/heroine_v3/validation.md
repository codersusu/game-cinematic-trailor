# Heroine v3 validation

The authoritative integration is `scripts/heroine_v3.py` → `add_heroine()`, using the paths and source cycle in `manifest.json`.

Final source: `rigged.glb` plus `walking-woman.glb`, with full visual geometry from `master.glb`. Character height1.72m. Source animation24bones; original natural upper-body movement retained, with gentler Walking_Woman arm swing. Source action range0.8–24.0 frames, sampled cyclically from left-contact phase6.0 for23.2sourceframes, retimed to28filmframes.

Geometry retained: visual master3,024,348triangles and1,657,108vertices, packed8Kcolor and two4Ksurface maps. Actual server rig proxy243,515triangles and299,947vertices. The proxy is hidden from rendering; nearest-polygon interpolated skin weights deform the master. Master was aligned using uniformscale0.903556, small0.005576rad yaw and floor/center translation. Post-alignment bounding-box difference0.266%; exact values in `alignment-report.json`. Full-resolution UVs and material maps remain attached to the visual master. Conservative hair-only dielectric/roughness refinement uses an authored rest-position mask.

Important imported-rig quirk: displayed bone tails are100times farther than actual adjacent joints. Film leg kinematics therefore use distances between bone heads, not Blender's display bone.length. Auto-created Icosphere bone widget is excluded from rendering and bounds.

Six high-detail rendered basic-walk poses were visually inspected at frames1,8,15,22,64,252. Final Walking_Woman source was selected after measuring19%gentler arm swing and slightly closer hand/shoulder spacing, then visually verified in the included [frame 8 proof image](rig-proof-woman/0008.png). No visible cloth clipping or crossed legs in reviewed poses. All clothing folds, straps, buckles, boots and hair geometry remain from original master.

Deformed master geometry, not IK targets, was measured at frames1,8,15,22,64,130,240,252,390. Support sole heights relative to floorZ0.14 ranged from−1.453mm at initialcontact to+0.672mm; settled leftsole−0.100mm/rightsole+0.672mm. Swing soles rise~63mm at passing poses and~30mm during finalclosure. The included [sole measurements](rig-proof-woman/sole-metrics.json) report world-space minimum sole Z values in metres, by frame and foot; subtract the floor height of 0.14 m to obtain clearance. Film footstep times remain15,29,…239 and finalleft252, doorway crossing2.63603seconds.

The separate `rig-proof-woman/heroine-rig-proof.blend` is a local production-only inspection scene and is not included in the public submission. The retained PNG and JSON above provide compact review evidence. The delivered `observatory-v3.blend` contains the integrated character; rebuilding the film calls `add_heroine()` from the retained model and animation assets.

Known visual limits: generated facial eyes are painted into a fused mesh and hair is sculpted geometry. This model is suitable for the planned full-body cinematic framing; it does not provide independent facial expression topology or a strand-hair groom. No artificial blink or facial deformation was added. The final gaze uses a restrained head turn.
