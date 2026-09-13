# Final archery QA — accepted V13

Scene: `bear-bow-forest-v13.blend`  
SHA256: `9b39cf38ebb29f738b8e074e6cdb548d23054572633cc4746e859447c4bfb93a`

FP20 and FP32 were visually accepted. The scene is frozen; final provenance checks made no scene changes.

| Check | Final result | Evidence |
|---|---|---|
| Arrow versus hands, fingers, forearms and sleeves | 217 dense samples; zero triangle intersections | [Clearance](archery-clearance.json) |
| Bow-arm staging and grip | 97% reach,151.85° elbow,25° cant; grip error≤0.0022 mm; limb-length error≤0.029 mm | [Arm staging](archery-arm-staging.json) |
| Shelf and release alignment | Maximum axis/rest miss0.00054 mm; release direction change0.0524° | [Saved-scene provenance](archery-final-provenance.json) |
| Embedded arrow versus full heroine | Zero intersections in every production frame35–144, including123; rerun on final SHA | [Pursuit audit](archery-pursuit-full-body-audit.json) |
| Preservation | Arrow matrices identical across144 frames; root and camera/arrow/bear action data unchanged | [Saved-scene provenance](archery-final-provenance.json) |

Post40 heroine bone matrices differ from the preceding scene by at most5.73×10⁻⁶ per component from pose-bake rounding. The full pursuit collision audit was repeated on this final scene, including the changed35–40 transition.

`first-archery-pass/` and `before-arm-staging/` retain preceding-stage evidence. Reports named `archery-aim-*` describe the earlier7ab aiming correction. They are not final-stage collision proof. The machine-readable [manifest](archery-final-qa-manifest.json) records hashes for the final evidence above.

## Final editorial range

The delivered forest uses source frames 10–132. Inherited idle frames 1–9 are omitted because the bow upper limb passed too close to the first-person camera. This 0.75-second opening trim does not alter the accepted arrow/hand correction, shot, roll or escape. No attempted carry-pose candidate was promoted; the final scene remains `9b39cf38ebb29f738b8e074e6cdb548d23054572633cc4746e859447c4bfb93a`.
