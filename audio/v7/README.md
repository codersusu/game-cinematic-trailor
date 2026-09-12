# The Last Observatory — V7 approach soundtrack

This revision adds quiet muted deck footsteps to the heroine's second approach. It uses the V5 mastered program intact as the base, preserving its original entrance footfalls, airlock, doorway transition, instrument hum, music and 20-second alignment. Only the added approach contacts and a transparent overall loudness trim change the mix.

The new contact times must come from the native animation report; none are supplied as invented defaults. The mixer reads a `foot_contacts` array containing explicit `frame` and `foot` fields, with frame 1 at time zero and 24 frames per second. The source report and its hash are recorded alongside each added contact in `walk_sync.json` and `mix_qa.json` after generation.

The measured new contacts are **359R, 377L, 387R and 398L**, corresponding to **14.9167, 15.6667, 16.0833 and 16.5417 seconds**. The original 11 entrance contacts remain unchanged; this revision adds four steps, for 15 audible contacts across the film. The additional stem is silent before the measured first approach contact.

## Outputs

- `last_observatory_v7_mix.wav`: completed 24-second, 48 kHz stereo, 16-bit PCM delivery master.
- `last_observatory_v7_premaster.wav`: V5 program plus approach contacts before the final linear trim.
- `stems/v5_program.wav`: original program with the same overall trim as the master.
- `stems/approach_footsteps.wav`: additional quiet steps with short damped chamber reflections.
- `mix_qa.json`: measured loudness, true peak, sample checks, source/output hashes, trim amount and added contacts.
- `walk_sync.json`: compact schedule extracted from the measured native animation report.

The existing `audio/v5/footstep_variants` supply the muted metal/rubber footfalls. No new API requests, speech or music are generated. Original source terms continue to apply; see `../v5/README.md` and the earlier source manifests.

## Rebuild

Install the repository Python requirements, then run `python scripts/audio_mix_v7.py`. By default it reads `renders/v7/approach-performance.json`; `--contacts PATH` overrides that report and `--ffmpeg PATH` overrides the platform executable selected by imageio-ffmpeg. It writes only `audio/v7/`. A missing or invalid contact report stops the build before audio is written.

The delivery target is approximately −18 LUFS with true peak at or below −2.5 dBTP, finite samples and no clipping. QA is technical; it does not claim perceptual listening. The completed master measures **−18.00 LUFS**, **−3.56 dBTP**, and **zero full-scale or over-range samples**. All technical checks pass. A **−0.03 dB** overall trim preserves the established mix balance.
