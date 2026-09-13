# Option B — sword versus forest guardian

An eight-second paired action rehearsal for selecting the fight style. The human is the **Quaternius source mannequin**, not a finished retarget onto the accepted heroine. The Uplon sword, guardian rig, native source motions and forest environment are actual reusable assets.

| Source frames, 24 fps | Action |
|---|---|
| 1–24 | Sword guard; guardian prepares its strike |
| 25–60 | Native rolling evade follows a 3.2 m arc around the striking guardian |
| 61–132 | Complete native sword combo; guardian gives ground, then recoils at the last counter |
| 133–168 | Short backward withdrawal using reversed native walk |
| 169–192 | Settle into guard |

The native roll covers about five metres along the arc. The sword combo retains its entire 2.343 m root progression. The combat clearing is flattened only inside this separate study, preserving the original forest file. Character, guardian, sword and camera animation are baked; no handlers are required.

`body-contact-qa.json` checks evaluated human and guardian mesh triangle overlap at every source frame: zero intersecting pairs in the finalized study. `contact-samples.json` measures blade proximity during the counter; the nearest sampled blade point is approximately 3.4 mm from the guardian at source frame 114. This is a sampled contact check, not a complete blade penetration or physical simulation audit.

`build-report.json` records the scene hash and trajectories. Reproduce the CPU build with `scripts/build_option_b_v8.py`; run that script with `-- --audit` for contact checks. Rendering is intentionally separate and inexpensive for option selection.

Remaining production work after choosing the option: retarget and clean up the accepted woman's performance, polish planted feet and the curved roll contacts, add a tailored guardian hit reaction, improve sword grip and material detail, and add impact chips, sound and final lighting. This selection proof does not claim finished cinematic animation quality. No earlier film or source scene was modified.
