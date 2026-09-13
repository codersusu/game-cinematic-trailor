# Combat choice previews

A, B and C are lightweight paired-encounter previews, each eight seconds at 12fps. They use the actual acquired weapons, source stand-in humans, native creature/human actions and an authored forest staging. The final heroine retargets and final lighting remain pending selection.

- [A — Bow versus guardian](../../previews/v8/options/a/Option-A-draft.mp4)
- [B — Sword versus guardian](../../previews/v8/options/b/Option-B-draft.mp4)
- [C — Bow versus bear](../../previews/v8/options/c/Option-C-draft.mp4)

All 96 frames of each delivered clip decode correctly. Representative contact sheets and key stills were inspected. B and C additionally passed whole-sequence character/enemy mesh intersection checks; C also passed bear/bow checks. No full real-time playback was performed. All heavy rendering remains on hold until the user chooses the assets and choreography. Previous films and scenes are preserved.

Bear source: https://sketchfab.com/3d-models/realistic-animated-bear-3d-model-bffc3c87d2d148ff8533e1cc8a11c9f1

The user-provided bear ZIP contained 81 native actions. C uses native walk, low attack and hit reaction, with blended transitions, ground correction and a jaw-opening limit that reduces a source mesh deformation issue. Its earlier draft is preserved in `previews/v8/options/c/first-pass/`.

Rebuild C with `scripts/build_option_c_v8.py`; this reuses the visual-bake and archer helpers in `scripts/build_option_a_v8.py`. Render with `scripts/render_combat_option_v8.py` and encode with `scripts/encode_combat_option_v8.py`. Keep licensed archer sources and any `.blend` containing them local; publish rendered footage and scripts only.
