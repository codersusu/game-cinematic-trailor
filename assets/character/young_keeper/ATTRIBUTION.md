# Rain walking keeper

**Rain Rig (CC) Blender Foundation | studio.blender.org**

- Source: https://studio.blender.org/characters/rain/v3/
- License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/
- Official archive: https://studio.blender.org/download-source/files/ee/a7/eea73e55dba1cea31c09848df6a794b2-4.zip
- Downloaded September 11, 2026. Archive contains `Rain v3.3/rain_v3.2.blend` and complete textures.
- Film adaptations: original world-planted walk animation, costume color grade, gravity pose for ponytail, transparent corneal shadow rays for Cycles without refractive caustics. The model, topology, rig, textures and shading detail are reused. No source bundled Python scripts are executed.

Rain is a stylized young adult woman. This is an intentional full-body animation asset choice; it is not a photorealistic facial replacement for Einar.

## Integration

`from young_keeper import add_young_keeper`

`add_young_keeper()` appends the character collection and authors frames 1–288, with held pose thereafter. Defaults: start=(-3.8,-7.6,.14), end=(-3.8,-.8,.14), start_frame=1, end_frame=240, height=1.68, cycle_frames=28. These default timing values are the reviewed production motion.

Return dictionary: `root`, `rig`, `collection`, `face_target` (world-space tuple at initial frame), `face_object` (bone-parented empty), `feet_targets` (initial world ankle target tuples), `foot_contacts` (frame/time/foot dictionaries), `doorway_crossing_frame`, `source`, `height`.

Root crosses doorway Y=-5.8 at frame64.2647059 (2.636029412 seconds). Heel/sole contact events: 15,29,43,57,71,85,99,113,127,141,155,169,183,197,211,225,239,252. First event right; alternate until239right; final trailing left252. Initial frame1 support is silent.

## Verification

Blender4.5.13, Cycles Metal, MetalRT OFF, kernel optimization OFF. Skin, face freckles, iris/sclera, clothing and hair rendered successfully with complete image maps. Four 720px full-body poses and a face proof are in `proof/`; these images precede final costume recoloring and ponytail gravity adjustment. The final revised rig is `proof/walk-proof.blend`.

Deformed shoe sole vertices were measured after final rig adjustments, not just IK control positions. At planted contacts1,15,252, minimum sole Z is0.139988–0.139997 against floorZ0.14 (maximum numerical floor penetration0.012mm). Passing poses8,22,64 keep support sole grounded and swing sole raised approximately69mm. Final settle240 keeps support grounded and trailing sole32mm above floor. Measurements in `proof/metrics.json`.
