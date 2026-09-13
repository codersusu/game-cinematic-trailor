# C — Bow versus realistic bear

Eight-second, 12fps selection rehearsal using the user-provided bear and the same native feminine bow performance as option A. The source mannequin is a temporary animation stand-in. The accepted Rocketbox heroine, expressions, detailed forest dressing, sound and final lighting remain later work.

The bear approaches through two native walking cycles, makes a short low lunge, then reacts to the arrow. This tests a wildlife encounter against the two supernatural guardian options. No gore is included.

| Draft frames | Action |
|---|---|
| 1–42 | Native bear walk; its 3.52m root travel is preserved across cycle boundaries |
| 25–35 | Archer loads |
| 36–59 | Archer aims; bear transitions into native low-attack anticipation |
| 60 | Arrow release |
| 63 | Arrow contacts the evaluated bear mesh |
| 63–96 | Native standing hit reaction; archer recovers |

The walk/threat and threat/hit transitions are blended. Source foot penetration is corrected against the central forest path. Arrow contact follows an actual deformed surface triangle through the reaction. The encounter is staged with the bear's native pose animation; the standing clips' object translation is removed to prevent unintended travel. This is a selected and blended excerpt, not a complete unmodified attack clip.

The older source mesh showed a long rectangular mouth when its jaw opened to about 40 degrees. The draft caps positive `RigJaw` local Z rotation at 12 degrees, preserving its translation, scale and other rotations. The body performance is unchanged. The uncorrected first pass is preserved under `previews/v8/options/c/first-pass/` for comparison.

Build: `scripts/build_option_c_v8.py`. Reuses the constraint-aware visual bake in `scripts/build_option_a_v8.py`. Saved scene: `option-c-bow-bear.blend`. Draft export uses `scripts/render_combat_option_v8.py` and `scripts/encode_combat_option_v8.py`; 768×432 Eevee at eight samples, with titles added during encoding. No Cycles production rendering.

Bear attribution: **WildMesh 3D**, “Realistic Animated Bear 3D Model,” [Sketchfab listing](https://sketchfab.com/3d-models/realistic-animated-bear-3d-model-bffc3c87d2d148ff8533e1cc8a11c9f1), uploader-declared CC-BY 4.0. Local modifications: motion selection, transition blending, placement, ground correction and material roughness. Asset provenance notes and original file hashes are recorded in `assets/v8/combat/bear/`.

Keep this scene local: it contains the licensed Kevin Iglesias archer source. The rendered review movie can be shared. The previous films and scenes are preserved.
