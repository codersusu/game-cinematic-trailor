# V8 — Forest discovery and combat: preproduction

Status: assets and action selection. Heavy rendering is on hold at the user’s request. V7 remains unchanged. The user reopened the combat choice after downloading the archer pack; no weapon is currently locked.

## Story

The same woman explores a misty wooded trail, discovers a manufactured door embedded in a rocky outcrop, encounters its guardian, and enters the chamber. Inside she discovers Astra, approaches the platform and reaches toward the galaxy with one extended index finger.

## Proposed edit

| Beat | Approximate duration | Action |
|---|---:|---|
| Explore | 7–9 s | Reuse the accepted native walk on a clear forest path; camera reveals vegetation before the entrance. |
| Discover | 2 s | Stop, notice the door and react to a sound from the clearing. |
| Combat | 6–8 s | One readable exchange with an opponent; weapon and exact choreography pending user selection. |
| Enter | 2–3 s | Recover, put the weapon away, approach the threshold; door opens and light draws her inside. |
| Astra chamber | Existing 24 s | Retain entrance, reaction, galaxy, approach and final index-finger gesture. |

Approximate total 41–46 seconds. Final timing depends on the selected native clips, preserving their stride lengths and ground contacts.

## What is actually built

- `forest-v8-layout.blend`: separate editable 12-second discovery layout with the accepted character, native walking, four cameras, a closed portal, 72 shared fir instances, ferns, mossy stones, roots, scanned rock face, leaf-litter ground and atmospheric haze. It is a staging study, not the final edit.
- `observatory-v8-finger-study.blend`: full V7 chamber and performer with the new finger gesture. Only the fifteen right-finger rotation channels change after frame418; nonfinger animation and V7 files are unchanged.
- Small forest Eevee stills and a hand Workbench motion proof are in `previews/v8/`. No final Cycles frame sequence has been started.
- Combat previews use source rigs. They demonstrate asset motion, not a completed retarget to our heroine or a coordinated two-character fight.

## Forest source selection

See [acquired forest assets](forest-assets-v8.md). Poly Haven CC0 fir LOD1 b/c variants, Fern02, RockMossSet01, DeadTreeTrunk, RootCluster01 and ForestFloor are downloaded and import-tested. RockFace01 and the portal reuse earlier project assets. Forest dressing, doorway joints, wind, gaze, audio and the final threshold crossing remain production work.

## Action checks before expensive rendering

Review the retargeted heroine in a full-body clay preview, then inspect hand/weapon attachment, bowstring and arrow timing if selected, planted feet, enemy-to-hero spacing, camera readability, and the transitions from exploration to combat to entry. Review the opponent’s material/detail treatment in a few stills. Heavy rendering stays on hold until the assets and performance are settled with the user.

## Local licensed source

The user supplied Human Archer Animations FREE.zip. Its extracted contents live under `assets/v8/licensed/archer/` and are excluded from public Git. Rendered previews can be shared under its source terms. The original files and any production .blend containing reusable licensed animation or props must remain local; a public rebuild can require each user to supply the pack.
