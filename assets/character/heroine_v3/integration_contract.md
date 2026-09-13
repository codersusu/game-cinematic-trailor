# Integration contract (pending actual Meshy rig verification)

`add_heroine(model_path=None, animation_path=None, detail_mesh_path=None, start=(-3.8,-7.6,.14), end=(-3.8,-.8,.14), start_frame=1, end_frame=240, height=1.72, cycle_frames=28, source_cycle=None, forward_axis=None)`

Defaults read `assets/character/heroine_v3/manifest.json`:

```json
{
  "model_path": "assets/character/heroine_v3/rigged.fbx",
  "animation_path": "assets/character/heroine_v3/walking.fbx",
  "detail_mesh_path": "assets/character/heroine_v3/master.glb",
  "source_cycle": [1, 29]
}
```

Only model_path is mandatory; its rig must include animation if animation_path omitted. Omit detail_mesh_path when rigged file already preserves sufficient detail. Paths may be absolute or workspace-relative. Source_cycle must be set after inspecting actual animation; absent value samples the entire source action as one loop. Forward direction is inferred from ankle-to-toe bones; override with authored world-space forward_axis when necessary.

Preserves all imported PBR materials/UVs. Optional master weight transfer uses nearest polygon interpolation in identical rest coordinates, with a bounds guard. Bone names accept standard Mixamo namespaces (Hips, LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase, etc.). Original animation drives upper-body movement; analytic two-bone legs impose the proven world-planted path and contact timing. No facial topology manipulation; only head gaze.

Source files and actual visual proofs are still required before claiming successful integration. Do not render final film from the placeholder contract.
