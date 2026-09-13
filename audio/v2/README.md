# The Last Observatory — v2 soundtrack

The v2 soundtrack accompanies a young woman walking through a doorway into the observatory, with more continuous armillary movement and a fantastic night sky. It retains the original tonal underscore and the major core-light/tonal alignment at 20 seconds while the rings keep turning. It adds leather-boot footsteps, a subtle doorway acoustic transition, continuous mechanical motion across the full 24 seconds, and restrained high harmonic color. There is no dialogue or voice cloning.

## Files

- `last_observatory_v2_mix.wav`: 24-second, 48 kHz stereo, 16-bit PCM master.
- `last_observatory_v2_premaster.wav`: balanced mix before final loudness processing.
- `stems/`: eight full-length stereo layers, all starting at time zero.
- `footstep_variants/`: edited individual footfall samples, extracted from the generated recording.
- `walk_sync.json`: frame-based contact and doorway timing supplied by the character animation. Its `status` field distinguishes provisional timing from confirmed animation sync.
- `mix_qa.json`: measured loudness, peaks, duration, individual contact times, source hashes, and extraction details.
- `generation_manifest.json`: exact new footstep prompt and service metadata.

The master has a nominal −18 LUFS integrated target. All stems share the premaster gain; they are intended for further editing and do not sum directly to the dynamically mastered file. Version 1 remains intact outside this folder.

## Confirmed animation synchronization

The character agent confirmed 18 audible contacts at frames **15, 29, 43, 57, 71, 85, 99, 113, 127, 141, 155, 169, 183, 197, 211, 225, 239, and 252**, with the right foot first. Frame 1 is an already-planted left support and has no artificial impact. Contacts use `(frame − 1) / 24` seconds. The final left-foot closure is at 10.4583 seconds; there are no further footsteps. Doorway crossing is at frame 64.2647, or **2.6360 seconds**. The quiet acoustic transition is centered there. Mechanical motion continues throughout the 24-second film, including underneath the core-light accent at 20 seconds.

## Sources and rights

| Component | Source and adaptation | Rights record |
|---|---|---|
| Rain/chamber ambience | Reused v1 ElevenLabs recording; droplet peaks softened and weather prominence reduced | Original generation in `../generation_manifest.json`; service plan applies |
| Continuous bronze mechanism | Reused active portion of v1 ElevenLabs mechanism; two speed layers, overlapping fades, and authored volume movement | Original generation in `../generation_manifest.json`; service plan applies |
| Alignment | Reused v1 edited bronze alignment and original synthesized low impact, at 20 s | Original generation in `../generation_manifest.json`; service plan applies to generated portion |
| Leather-boot footsteps | One new 8-second ElevenLabs Sound Effects V2 request; individual events extracted, varied slightly, and placed at animation contacts | `generation_manifest.json`; service plan applies |
| Tonal underscore and anticipation | Original numerical synthesis from v1, reused with mix changes | Created for this project; no external samples |
| Doorway arrival and sky harmonics | Original filtered-noise/partial synthesis, with synthetic room response | Created for this project; no external samples |

The doorway cue conveys a change in room scale; it does not depict a door slamming or opening. Footfall left/right alternation uses a small stereo shift and a shared stone-room response. Source footfall timings are replaced by the character's authored contact times, so generated pacing does not dictate the animation.

An existing user-authorized ElevenLabs key was read privately from another project. No key was copied, printed, or stored here. Only one new sound-generation request was made for v2. Subscription-tier lookup was unavailable during v1 creation, although generation succeeded; the account tier remains unverified. Generated ElevenLabs audio must not be labeled CC0. Its publication and commercial-use rights depend on the account plan active when generated and the provider's terms.

- API reference: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- Official publishing guidance: https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform
- Original audio manifest: `../../docs/audio_manifest.md`

## Rebuild

From the project root, run `python scripts/audio_mix_v2.py` with the bundled Python interpreter. The script imports project-local NumPy/SciPy and defaults to the installed project-local ffmpeg. `--sync PATH` selects a different contact-timing file; `--ffmpeg PATH` selects another encoder. Rebuilding the mix uses local files and makes no API calls. The separate `scripts/audio_generate_v2.py` requires `--env-file EXTERNAL_PATH` and only requests the missing footstep source.

The mixer reads existing v1 assets and writes only under `audio/v2/`. The QA file records hashes of the reused sources. Technical checks cover exact duration, stereo format, finite values, loudness and clipping. The audio agent has not performed perceptual listening; review the final video on headphones or speakers for footfall weight, acoustic scale, and synchronization.
