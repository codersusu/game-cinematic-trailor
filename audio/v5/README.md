# The Last Observatory — V5 soundtrack

A 24-second soundtrack for the modern observatory interior. The original synthesized music and anticipation remain in their established positions. New local synthesis supplies the soft electric airlock, ventilation, steady instrument hum and a clean resonant alignment at 20 seconds. No antique grinding or rain recording is used in this mix.

## Sound and timing

- The sliding airlock motor runs from **0.00 to 1.45 seconds**, with soft acceleration and deceleration, a muted track sound and no door slam.
- Footsteps retain the native Rocketbox timing: **50R, 68L, 82R, 97L, 110R, 126L, 139R, 155L, 168R, 180L, 191R**, at 24 fps. Frame 1 is time zero; the first sound is at 2.0417 seconds and the last contact is at 7.9167 seconds.
- The prior leather-boot recording is filtered to suppress stone grit and high impact clicks, then layered with short damped metal-panel resonances and a low rubber-sole thump. The short room response suits a furnished instrument chamber.
- The doorway air transition stays at measured frame **82.7314 / 3.4055 seconds**.
- Quiet ventilation and tonal instrument hum support the full film. The musical alignment remains at **20 seconds**, rendered as a clean resonant instrument tone.

## Files and measured delivery

`last_observatory_v5_mix.wav` is exactly **24 seconds / 1,152,000 sample frames**, **48 kHz stereo**, **16-bit PCM**. Measured loudness is **−17.97 LUFS**, with **−3.53 dBTP** true peak and **zero clipped samples**.

`stems/` contains nine full-length layers: ventilation, original underscore, instrument hum, sliding airlock, footsteps, doorway arrival, sky harmonics, alignment and anticipation. All start at zero. Their common gain matches the premaster; they do not sum directly to the loudness-processed master. `footstep_variants/` contains the processed individual floor contacts.

`walk_sync.json` preserves the animation schedule. `mix_qa.json` records loudness, contacts and source hashes. `format_and_cue_qa.json` verifies WAV format and the actual airlock/footstep activity windows. `generation_manifest.json` records source and output hashes. Technical verification is complete. The final movie AAC is also verified in `final-aac-qa.json`: exactly 24 seconds, 48 kHz stereo, −17.7 LUFS, −3.5 dBTP and zero full-scale or over-range samples. This is decoded-audio measurement; perceptual listening was not performed.

## Sources and rebuild

This revision made **zero paid API requests** and contains **no dialogue**. It reuses the project's original synthesized underscore and anticipation plus the existing v2 ElevenLabs footfall recording. The source recording's original account-plan terms apply; it is not labeled CC0. All additional sound layers are locally synthesized by `scripts/audio_mix_v5.py`.

Install the repository dependencies with `python -m pip install -r requirements.txt`, then run `python scripts/audio_mix_v5.py` from the project root. NumPy, SciPy and imageio-ffmpeg are required; imageio-ffmpeg selects an FFmpeg executable for the current platform. The script writes only `audio/v5/`; `--sync PATH` and `--ffmpeg PATH` override its defaults. It needs the existing v1 synthesized stems and v2 footfall WAV but no API key. The master, stems, mix QA and generation manifest regenerate together.
