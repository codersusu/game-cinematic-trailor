# Public asset redistribution audit — V13

The finished movie and music can be published. Most source assets can also be published with their existing notices. The Kevin Iglesias archer pack is the exception: its raw models, rigs, props and extractable native/baked/retargeted motions stay local. Changing the visible woman to Rocketbox did not remove the archer animation data from the forest scenes.

This audit classifies the local asset sources and inspects Blender datablock inventories. It is not a blanket assignment of all upstream assets to the project's code license. Machine-readable packaging decisions are in `redistribution-rules.json`; the original 53-file scene inventory is in `blend-redistribution-inventory.json`.

## Editable public forest copy

`forest-environment-v13.blend` is a separate public copy containing the dense forest, airlock, textured animated bear and project cameras. The human, bow, arrow, string, support, all human rigs and their derived motion are removed. Orphan meshes, materials, images, shape keys and actions were purged, including source fake-user datablocks. The only surviving armature is the bear's `RigRoot`.

- Public copy SHA-256: `969beed816213ee4e9a9d44c5d343e5e4745e5be1b286b165e1f69e179775deb`.
- Size: 110,186,700 bytes.
- Original production scene remains unchanged: `9b39cf38ebb29f738b8e074e6cdb548d23054572633cc4746e859447c4bfb93a`.
- Reopened-file audit: no known `Human_*`, `HumanF`, `HumanM`, archer, retargeted-motion, `B-*` or `Bip01` skeleton data remains.
- Bear pose/path and both main cameras evaluate identically for all 144 frames. Retained animation curves are unchanged. Remaining animation is bear performance, camera motion, procedural vegetation wind and airlock doors.
- Texture files are packed or have available relative asset paths. Ship the `assets` tree alongside the scene. Some packed bear images retain upstream path names that do not exist locally; their packed image data remains available.

Reproduction script: `scripts/package_forest_environment_v13.py`. Evidence: `forest-environment-redistribution.json`. No GPU rendering was used in this packaging step.

## Required private files

Exclude the entire `assets/v8/licensed/archer/` tree from public source distribution. Keep its license/acquisition instructions publicly as documentation, without including the pack itself. The user-supplied ZIP's SHA-256 is `87565026f3a3b0aa8aeaadbcc155533ee58d927f5c443a6b2a11f396a461c904`.

The scene inventory found embedded archer identifiers in these files:

```text
bear-bow-escape-v9.blend
bear-bow-escape-v9.blend1
bear-bow-forest-v10.blend
bear-bow-forest-v10.blend1
bear-bow-forest-v12.blend
bear-bow-forest-v12.blend1
bear-bow-forest-v13-aim-test.blend1
bear-bow-forest-v13-before-arm-staging.blend
bear-bow-forest-v13-before-opening-fix.blend
bear-bow-forest-v13-initial-archery.blend
bear-bow-forest-v13.blend
bear-bow-forest-v13.blend1
option-a-bow-guardian.blend
option-a-bow-guardian.blend1
option-c-bow-bear.blend
option-c-bow-bear.blend1
```

Use the broader exclusion patterns `bear-bow-*.blend*`, `option-a-bow-guardian.blend*`, and `option-c-bow-bear.blend*` so subsequent backups are covered. Do not republish equivalent exports or archives under different names.

Also exclude complete source skeleton dumps `renders/v8/combat/archer-locomotion-inspection.json` and `previews/v12/forest-character-inspection.json`, or remove the licensed skeleton sections before publication. Clip names, durations, counts, scalar QA measurements, collision reports, checksums and code implementing retargeting are publishable documentation; they are not complete source performances.

The local pack README identifies the Standard Asset Store EULA and permits rendered production use. Its public-source exclusion is consistent with the EULA's embedded-product distribution grant and limitations on other redistribution. [Kevin Iglesias licensing](https://www.keviniglesias.com/#license), [Unity Asset Store EULA](https://unity.com/legal/as-terms).

## Included asset families and notices

| Asset family | Public source decision | Required attribution / qualification |
| --- | --- | --- |
| Poly Haven forest/HDRI/PBR, ambientCG materials | Include | CC0; keep acquisition manifests. [Poly Haven license](https://polyhaven.com/license) |
| Kenney kits; Irondust/rubberduck/a52 industrial meshes; Quaternius animation/wolf; Uplon sword | Include model packages | CC0 per package provenance. Upstream web preview backgrounds may have separate licensing. |
| Forest monster/guardian | Include | CC0; retain Čestmír Dammer/CDmir's `Licenses.txt`. |
| Microsoft Rocketbox FemaleAdult04 and native mocap | Include | MIT; preserve Microsoft copyright and license. [Source](https://github.com/microsoft/Microsoft-Rocketbox) |
| Einar / Rain archives, rigs, textures and proof scenes | Include | Blender Studio CC BY4.0; preserve Blender Foundation credits and modification notices. [Einar](https://studio.blender.org/characters/einar/v1/), [Rain](https://studio.blender.org/characters/rain/v3/) |
| Nilda native archive/model | Include | Artist-declared CC BY4.0, ijiklvn / Kelvin Carvalho; preserve `assets/character/candidates_v4/README.md`. [Model](https://sketchfab.com/3d-models/nilda-female-character-walk-animation-d3f65ad04ec845b197a689db48ec4329) |
| Graphic Cat female native archive/model | Include | Artist-declared CC BY4.0, Fat cat / Graphic cat; preserve source README. [Model](https://sketchfab.com/3d-models/free-lowpoly-female-7052ca1e09404ce39af47a964e08ee40) |
| Realistic animated bear | Include | Uploader WildMesh 3D declares CC BY4.0. Retain credit, link and modifications. This audit did not independently establish original authorship beyond uploader provenance. [Model](https://sketchfab.com/3d-models/realistic-animated-bear-3d-model-bffc3c87d2d148ff8533e1cc8a11c9f1) |
| Animal alternatives | Include according to each manifest | CoinCoin wolf CC BY4.0; Teh_Bucket boar and tomek wolf selected CC0 license. |
| NASA star panorama | Include with source credit | NASA imagery usage conditions, not CC0. Credit NASA/Goddard SVS; Gaia DR2 ESA/Gaia/DPAC; visualization Ernie Wright. [Panorama](https://svs.gsfc.nasa.gov/4851/) |
| Meshy V3 heroine master, complete rigged/walking outputs and proof scenes | Include with Meshy terms/credit | See explanation below; not a blanket CC0 asset. |
| V13 original score, stems, source and VSCO2 CE samples | Include | Original code-composed music with CC0 samples. Retain `audio/v13/sources/LICENSE` and acquisition provenance. [VSCO Community Edition](https://versilian-studios.com/vsco-community/) |

Meshy §§3.1–3.2 were fetched from the official terms during this audit. They permit distribution of service assets incorporated into and necessary for exploiting generated customer output; free output has a CC BY4.0 grant. Thus the complete generated heroine with its incorporated rig/motion can remain in the source package. This does not grant a general right to extract Meshy's service motion library and distribute it independently. Preserve `assets/character/heroine_v3/ATTRIBUTION.md` and credit **Original heroine • Meshy 7 Ultra**. [Meshy terms](https://www.meshy.ai/terms-of-use).

Earlier ElevenLabs audio is not CC0. Its generation account plan was not verified by the old audio workflow; paid/free publication conditions differ. Keep that distinction in any historical audio package. The newest V13 score has its own confirmed original/CC0 provenance. [ElevenLabs publication conditions](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform).

Omit borrowed research preview images where their own license is not established: Nilda/Jungle Jim website previews and the industrial candidate `preview.png` are listed in the machine rules. This does not exclude the corresponding licensed mesh textures. Parent separately checks credentials and excludes raw signed-URL source pages/API responses. Do not copy `renders/v3/service-tasks/` or the identified signed-source HTML files into the repository.

No known Kevin archer identifiers were found in the observatory room scenes, including `observatory-v12-run-entry.blend`, which uses native Rocketbox run/stop data. `forest-v8-layout.blend` and `option-b-sword-guardian.blend` also do not contain the archer pack. Each still needs its ordinary upstream notices.

## Acquire the missing pack and reconstruct locally

1. Obtain **Human Archer Animations FREE** from [Kevin Iglesias's product page](https://keviniglesias.gumroad.com/l/human-archer-animations-free) under its own license. An authorized local copy is needed; the repository does not convey that license or contain the raw pack.
2. Extract under `assets/v8/licensed/archer/`, preserving the archive layout. Required file: `Animations/Blender/HumanF_ArcherAnimationsFREE_2.0.blend`; props: `Animations/Blender/HumanArcherAnimations_BowAndProps.blend`. The original acquired pack contains 142 FBX files. The bow/arrow FBXs and source rig remain local.
3. Start with public `forest-v8-layout.blend`, the CC-BY bear source under `assets/v8/combat/bear/`, CC0 Quaternius `UAL1_Standard.glb`, and the Rocketbox room asset. Use Blender 4.5 LTS with the project's assets at their recorded relative paths.
4. Scene build dependency order: `scripts/build_option_c_v8.py` (uses the actor helper in `build_option_a_v8.py`) → `build_escape_v9.py` → `build_forest_v10.py` → `build_forest_character_v12.py` → `fix_archery_v13.py`.
5. V13's reviewed correction pipeline then uses `correct_aim_v13.py` followed by `refine_bow_arm_v13.py`. Preserve the initial V13 result as `bear-bow-forest-v13-initial-archery.blend`. The aim script writes `bear-bow-forest-v13-aim-test.blend`; use that accepted result as `bear-bow-forest-v13-before-arm-staging.blend` for the arm staging script. The latter writes `bear-bow-forest-v13-arm-test.blend`; after its checks pass, promote that candidate locally to `bear-bow-forest-v13.blend`. Never publish these rebuilt extractable scenes.
6. Native clips: `HumanF@BowShot01 - Load`, `HumanF@BowShot01 - Hold`, `HumanF@BowShot01 - Release`, `HumanF@Run01_Forward [RM]`, `HumanF@SheatheBack01_L`. Run uses 19 source samples at 30 fps; sheathe uses 10 samples over source frames 1–23. `escape_actor_motion_v9.py` supplies the CC0 Quaternius roll retarget. It evaluates source rigs locally rather than storing full performances in Python.
7. Use the current rendering/encoding scripts and QA manifests for production. The final first-person editorial cut starts at frame 10, avoiding the defective original idle opening. `fix_opening_carry_v13.py` was an unpromoted experiment; it is not part of the accepted rebuild chain.

The stripped public scene is immediately editable without the archer pack. Reconstructing the full encounter requires the separately acquired pack and the scripted build chain. This packaging audit did not rerun that full multi-version build from a clean checkout, so the dependency order is documented rather than claimed as a newly validated one-command build.
