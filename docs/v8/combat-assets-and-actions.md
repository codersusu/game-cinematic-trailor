# V8 combat asset and action choices

The leading reusable setup is a short defensive exchange with a stone guardian in the forest clearing. Sword and bow variants are both under review. The woman evades its committed strike, counters with her sword, then escapes through the newly revealed entrance. A six to eight second exchange gives space for anticipation, weight transfer, contact and recovery. The existing woman and Astra galaxy stay central to the story.

## Available production sources

| Asset | Local source | Verified contents | License and source |
|---|---|---|---|
| Forest guardian | `assets/v8/combat/forest-monster/forest-monster-final.blend` | 2,803-vertex body, 76-bone rig, six native actions, 2K body color/normal/specular maps | CC0, Čestmír Dammer (CDmir), with TinyWorlds/Rick Hoppmann texture credit. [Author page](https://opengameart.org/content/forest-monster). Current archive includes `Licenses.txt`; author confirms the earlier restricted tree texture was replaced in 2015. |
| Human sword movements | `assets/v8/combat/quaternius/UAL1_Standard.glb`, `UAL2_Standard.glb` | 45 and 43 actual clips, respectively, on 65-bone humanoid rig | CC0, Quaternius. [Library 1](https://quaternius.com/packs/universalanimationlibrary.html), [Library 2](https://quaternius.com/packs/universalanimationlibrary2.html). Files acquired from [public CC0 mirror](https://github.com/richardanaya/metaverse-avatar/tree/master/anims); mirror provenance retained. |
| Uplon sword | `assets/v8/combat/uplon/uplon.blend` | 3,294 vertices, editable single mesh and separate-parts file, base color/metallic/roughness/normal/emissive maps | CC0, ninelionar. [Author page](https://opengameart.org/content/sci-fi-sword-uplon). |
| Heroine | Existing Rocketbox Female Adult 04 | Existing native walk, facial morphs and accepted appearance | Existing project attribution/license retained. |

These are editable assets that can be distributed with the project under their stated licenses. They are a usable starting point, not a guarantee of final cinematic quality. The guardian particularly needs moss, surface detail, scale and lighting work; its old leaf-card canopy is removed in the inspection proof. No paid purchase or API generation was used.

## Action plan

1. **Recognition and guard:** the guardian rises from the moss and turns toward her. She plants her feet and raises the sword. Source: guardian `Idle`/`Melee_Hold`, human `Sword_Idle`.
2. **Committed attack and evasion:** guardian `Attack` visibly winds up before its broad forearm strike. Use the native human `Roll_RM` for a lateral evasive move, positioned to clear the attack arc and preserve foot/hand ground contacts.
3. **Counter:** use the first two strikes from `Sword_Regular_Combo`, preserving its native body progression. A clear sword-to-stone contact produces a few chips, dust and sparks. A separately authored guardian recoil is required; no source hit-reaction clip is present.
4. **Recovery and exit:** she settles into guard, then uses the established native walk/run transition toward the door. The guardian remains a threat; no death animation is necessary.

Suggested editorial duration: 1.5 seconds preparation, 1.5 seconds forearm swipe/evade, 2–3 seconds counter, 1–2 seconds recovery/door transition. These are staging targets, not a locked final timeline.

## Exact inspected source actions

Guardian source is 24 fps:

| Clip | Source frames | Intended use |
|---|---:|---|
| `Idle` | 0–191 | Resting/breathing creature |
| `Melee_Hold` | 0–50 | Threatening pose |
| `Attack` | 0–30 | Anticipation 0–10, strike 10–15, recovery 15–30 (author timing notes) |
| `Walk` | 0–40 | Grounded approach |
| `Dying` | 0–35 | Available but not planned |
| `Stand` | 0 | Static rest pose |

Useful human clips actually present in the free standard files:

| Library | Clip | Native duration |
|---|---|---:|
| UAL1 | `Sword_Attack`, `Sword_Attack_RM`, `Sword_Idle`, `Roll`, `Roll_RM` | See machine-readable clip inventory |
| UAL2 | `Sword_Block` | 1.233 s |
| UAL2 | `Sword_Dash_RM` | 1.567 s |
| UAL2 | `Sword_Regular_A` / `_A_Rec` | 0.433 / 0.967 s |
| UAL2 | `Sword_Regular_B` / `_B_Rec` | 0.533 / 1.033 s |
| UAL2 | `Sword_Regular_C` | 2.000 s |
| UAL2 | `Sword_Regular_Combo` | 3.000 s |
| UAL2 | `Hit_Knockback`, `Hit_Knockback_RM` | 0.833 s |

**Root-motion finding:** the measured `Sword_Regular_Combo` moves its root 2.343 m even though its name has no `_RM` suffix. `Sword_Dash_RM` moves about 3.69 m. Retargeting must account for actual root curves, rig scale and terrain contact; the clip name alone is not a reliable in-place indicator. The proof camera follows root travel so the mannequin remains visible.

The Quaternius source rig has `root`, `pelvis`, three spine bones, clavicles, upper/lower arms, hands, complete finger chains, thighs/calves/feet/toes. Bind transforms and action endpoint measurements are recorded in `renders/v8/combat/sword-rig-inspection.json`. Rocketbox's skeleton differs; torso, shoulder and hand retargeting still require validation on the accepted woman.

## Review evidence and next quality gate

- `previews/v8/combat/forest_guardian.png`: small textured look-development still, native body with canopy removed.
- `previews/v8/combat/guardian-attack-native.mp4`: native creature attack, 31 frames at 24 fps, 480×480.
- `previews/v8/combat/sword-combo-native.mp4`: source humanoid combo with the Uplon sword attached, 72 frames at 24 fps, 480×480.
- `previews/v8/combat/bow-shot-native.mp4`: licensed native feminine load/hold/release, 92 frames at 30 fps, 640×640. The bow/arrow mesh is included with that pack; visible string and arrow departure are authored for the proof.
- `previews/v8/combat/bow-native-review.jpg`: eight inspected stages from the bow proof.
- `previews/v8/combat/native-actions-review.jpg`: six inspected stages each from the sword and guardian proofs.
- `renders/v8/combat/asset-inspection.json`: actual native creature geometry/actions/images.
- `renders/v8/combat/sword-rig-inspection.json`: human bind transforms and sword geometry.

Before heavy rendering, retarget on the woman; lock planted feet and grip; establish collision-free weapon arcs; coordinate the two performances; inspect contact in side and front views; refine guardian materials and moss; then review a low-cost continuous action proof. Source clips show reusable action quality; they do not yet prove the final two-character fight.

## Alternatives researched

The downloaded Quaternius wolf has attack, gallop/jump, hit reactions and walk, but its 983-vertex faceted appearance does not match this trailer. The tomek wolf has nine native actions but only 692 vertices and legacy/missing texture references. Neither is selected.

Kevin Iglesias's [Human Archer Animations FREE](https://keviniglesias.gumroad.com/l/human-archer-animations-free) is a viable later bow option: 136 animation files (67 feminine, 67 masculine and two masked hand poses), feminine and masculine actions, front shot, idles and locomotion. It uses the Standard Asset Store EULA and cannot be redistributed as accessible reusable source. The $0 Gumroad download requires an email address; the alternate itch page presented a security challenge. The user subsequently supplied the ZIP, which is now extracted into assets/v8/licensed/archer and excluded from Git. Native female Load/Hold/Release clips and a rigged bow/arrow are available. No bow clips are present in the two downloaded CC0 standard libraries. Bow animation can now be reviewed using the supplied licensed pack.

## Bow variant now available

The user-supplied pack contains native feminine `HumanF@BowShot01 - Load`, `Hold` and `Release`, two bow idles, directional movement and draw/stow motions. Its included Blender source has an editable control rig plus dedicated prop attachment bones, and the prop file contains a bow with a six-bone rig, an arrow and quiver. The native scene runs at 30 fps. The source Load action includes negative-frame editing handles; the review uses Load 1–26, Hold 1–41 and Release 1–25.

A bow-versus-guardian sequence can show an alert turn, draw, held aim, release and a stone impact, followed by retreat toward the entrance. This tests two-hand coordination and precise release timing. The bow pose is quieter and more readable than the acrobatic sword combo; final retargeting must keep the draw hand near the face and the bow grip stable. The source body animation is native; the inspection preview's prop attachment, visible string and arrow departure are authored for demonstration. The final bow bend and string simulation remain to be polished.

Source alternatives for the enemy remain under review. The downloaded wolves are suitable for action blocking only; a higher-detail animal would require its own verified rig, textures and native attack/reaction clips before selection.
