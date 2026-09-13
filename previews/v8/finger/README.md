# V8 single-finger rehearsal

The existing woman reaches toward Astra with her right index finger. Her middle, ring and little fingers curl independently, with a relaxed thumb. The source V7 scene and every previous movie remain unchanged.

- `Astra-index-finger-workbench.mp4`: 3.58-second silent, inexpensive gesture rehearsal, including a one-second final hold. The diagnostic isolates the weighted hand surface so the torso cannot block inspection; the saved study keeps the full performer.
- `finger-motion-strip.jpg`: reviewed poses at source frames 418, 434, 450, 466 and 478.
- `palm-478.png`, `back-478.png`, `side-478.png`: three reviewed views of the final gesture on the original full performer.
- `gesture-audit.json`: all 750 nonfinger action curves match V7 exactly. Earlier finger motion through frame 417 has zero difference. The index ray points toward Astra at the settled pose.
- `gesture-report.json`: integration timing and source/study hashes.

Load V7, then call `add_finger_reach_v8(scene, rig)` from `scripts/heroine_finger_v8.py` before any whole-film timeline shift. The gesture transitions during frames 421–475; index alignment settles at 478 and the pose holds through 576. The walking, arm, wrist and facial animation remain unchanged. `observatory-v8-finger-study.blend` is an isolated study with the original production room and camera settings.

These are workbench previews, not finished lighting or production renders. The existing Rocketbox hand geometry is visibly coarse at extreme magnification; the intended medium shot works, but a true macro fingertip shot should use a higher-detail hand asset. The source animation has been sampled visually; full real-time playback has not been independently reviewed.
