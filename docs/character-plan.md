# Character: observatory keeper

Selected source: **Einar**, Blender Studio / Blender Foundation, protagonist of the open film *Charge*.

- Official page: https://studio.blender.org/characters/einar/v1/
- License: CC-BY 4.0 (official page links https://creativecommons.org/licenses/by/4.0/). Required source credit: **Einar Rig (CC-BY) Blender Foundation | studio.blender.org**
- Download: official page → Download Source, 552 MiB ZIP. Saved to `assets/character/einar.zip`.
- Local source-page snapshot: `assets/character/einar-source.html`.
- Reference preview: `assets/character/einar-reference.jpg`.
- Target use: realistic older observatory keeper, face reveal, eye movement, restrained expression, mechanical arm detail. His worn clothes and scavenged bronze mechanism fit the proposed ancient observatory with minimal redesign.

## Why this asset

This is an actual production character, already clothed, shaded, groomed and rigged. The official preview shows facial poses for anger, contentment, eye closure, sadness, fear, and squinting. It avoids betting the central human performance on a newly generated unrigged mesh. Reuse is free under attribution.

## Integration caveats

Official requirement: Blender 3.5 or later. Comments by the rig author note the older rig UI does not use Blender 4 bone collections. We can manipulate pose bones through Python without relying on that UI, but need a rendered compatibility check. The model uses bendy bones, which are not directly portable through normal FBX/glTF export. A later realtime edition would need a simpler deformation rig or baked deformation. This does not block the Blender cinematic.

Keep the original source ZIP and files untouched. Link or append collection `CH-einar` into the production scene. Official instructions recommend linking it and making a library override. Verify image paths, grooming, rig drivers and eye materials before the portrait render. Inspect any bundled scripts before enabling them.

## Initial performance

A gentle head lift toward the astronomical mechanism, eye focus change, one blink and a tightening brow should provide a credible human reaction without distracting speech or exaggerated acting. Use a warm side light from the mechanism and a cool edge light from the broken dome. The close-up should establish this keeper as a witness to the mechanism awakening.

## Alternatives researched

- Rain v3: https://studio.blender.org/characters/rain/v3/ — production quality stylized female, updated for Blender 4.1+, facial rig and correctives, CC-BY. Useful if Einar compatibility proves costly, but less realistic and weaker visual fit.
- Existing local Unity Mario Tennis athlete assets: rigged Meshy characters found, but sports clothing/style and uncertain facial rig make them less suitable.
- Existing local Hades project: stylized fantasy characters and procedural heroes found. They are useful for gameplay prototypes, but not a better realistic close-up candidate than Einar.

## Verified delivery

Downloaded and extracted to `assets/character/einar/einar_release_v1.blend` (70 archive entries, 582 MB extracted). Confirmed the full source character has 799 main rig bones, 64 images and 11 named facial poses, including blink, scared and content. No keys, login or payment were required.

`assets/character/integrate.py` exposes:

```python
from integrate import add_keeper
keeper = add_keeper(location=(-2.8, -0.3, 0.2), rotation_z=0, height=1.8)
face_target = keeper['face_target']
```

Returned dictionary also contains `rig`, `root`, `collection` and source path. The pose lowers both arms, hides the optional satchel/tool accessories, and authors subtle head, brow, breath and blink animation, especially during frames 145–288. The root supports positioning and scale without baking the character.

Compatibility work: fixed original relative texture paths; replaced missing optional wrench texture references with packed neutral images; removed obsolete source-camera/geometry-socket driver paths; replaced the old layered skin surface with a current Cycles Principled surface using the original 4K painted albedo, original authored normals and restrained subsurface scattering. These edits are applied on append; the original archive stays untouched. No bundled Python UI was executed.

Rendering verified in Blender 5.2.1: `assets/character/keeper-portrait.png` and `keeper-portrait.blend`. 1000-square, 32-sample Cycles portrait rendered successfully in about 20 seconds including prep. Source legacy Geometry Nodes still emit nonfatal attribute warnings in 5.2. The portrait confirms cloth, skin, beard, eyes and mechanical arm visually render. This is a compatibility/lighting proof, not the final trailer shot.

Animation diagnostics: `assets/character/animation-check.json` and `keeper-blink.png`.


## Final eye-material repair
Full-resolution review exposed black eye sockets in the legacy material setup. `scripts/fix_eyes.py` preserves the original painted eye texture, Eyes UV map, mesh, and animation while replacing the three underlying eye surfaces and clear corneal shell. Transparent shadow rays through the cornea allow the sclera/iris to receive direct light with refractive caustics disabled. The corrected proof shows blue-gray irises, visible sclera, and corneal highlights. The source integration invokes the same repair on rebuild.
