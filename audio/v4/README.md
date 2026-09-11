# The Last Observatory — V4 soundtrack

The 24-second soundtrack follows the native Rocketbox walk, retaining the original atmospheric score, continuous bronze machinery, and the alignment accent at 20 seconds. It reuses the existing recordings and synthetic layers. No new service requests or spoken dialogue were added.

## Timing

Frame 1 is time zero, so audio contacts use `(frame - 1) / 24` seconds. The opening hold at frames 1–36 has no footsteps. The 11 impacts follow the verified native motion: **50R, 68L, 82R, 97L, 110R, 126L, 139R, 155L, 168R, 180L, 191R**. The last impact is at **7.9167 seconds**; the remaining settling animation has no invented impacts.

The native pelvis crosses the doorway plane at Y = −5.8 at interpolated frame **82.7314**, or **3.4055 seconds**. The quiet change-of-room air cue is centered at that measured crossing. Timing comes from `previews/v4/rocketbox-native-motion/motion-report.json`; the compact schedule is preserved in `walk_sync.json`.

## Delivery and verification

- `last_observatory_v4_mix.wav`: exactly **24 seconds**, **48 kHz stereo**, **16-bit PCM**.
- Measured integrated loudness: **−18.00 LUFS**; true peak: **−2.88 dBTP**; **zero clipped samples**.
- `last_observatory_v4_premaster.wav`: balanced mix before loudness processing.
- `stems/`: eight full-length stereo layers, starting at time zero.
- `footstep_variants/`: reused footfall recording split into short individual steps.
- `mix_qa.json`: measured format, loudness, clipping, contacts, extraction details and source hashes.
- `generation_manifest.json`: reuse record and hashes of the delivered master and mixer.

The stems share the premaster gain. They do not sum directly to the loudness-processed master. Verification covers timing, file format, finite samples and loudness; final perceptual synchronization should also be judged in the finished film.

## Sources

The original underscore, anticipation and low alignment impact were synthesized for this project. Ambience, bronze mechanisms and footfalls reuse the v1/v2 ElevenLabs recordings. Original generation records are in `../generation_manifest.json` and `../v2/generation_manifest.json`; their existing account-plan terms apply. No audio here is newly generated through a paid API, and the ElevenLabs recordings are not labeled CC0.

## Rebuild

From the project root, run `python scripts/audio_mix_v4.py` with NumPy, SciPy and FFmpeg available through the project's bundled dependencies. `--sync PATH` overrides the timing schedule and `--ffmpeg PATH` overrides FFmpeg. The script validates that contacts use 24 fps and that the doorway crossing was supplied. It reads existing source recordings and writes only `audio/v4/`.
