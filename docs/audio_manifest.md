# The Last Observatory — audio delivery

The final mix is `audio/last_observatory_mix.wav`: exactly 24 seconds, stereo, 48 kHz, signed 16-bit PCM. Use it at timeline time zero. The major alignment sound is edited to start at 20 seconds. The five stems in `audio/stems/` are all full-length and begin at time zero. They sum to the premaster before filtering, fades, and final loudness treatment; they are provided for further editing, not as individually mastered files.

## Design and timing

- 0–6 s: rain through a broken dome, close droplets and distant stone-chamber ambience.
- 6–12 s: original low harmonic texture enters under the architectural reveal.
- 10.8–19.6 s: massive bronze gears awaken. Active movement was stretched, its pitch lowered, and the ending shaped to fit the shot.
- 17.4–20 s: restrained filtered-air anticipation.
- 20–24 s: bronze alignment, original low-frequency weight, and a fading resonant tail.

No dialogue, recognizable song, voice clone, or third-party musical recording is used. The underscore is an original deterministic additive synthesis texture written specifically for this film, with D-based harmonics, gradual beating, and convolution-style synthetic reverberation. It deliberately leaves the physical environment audible.

## Sources and rights

| Files | Source | Status |
|---|---|---|
| `audio/raw/rain_chamber.mp3` | ElevenLabs Sound Effects V2, original prompt | Generated specifically for this project on 2026-09-11 |
| `audio/raw/bronze_mechanism.mp3` | ElevenLabs Sound Effects V2, original prompt | Generated specifically for this project on 2026-09-11 |
| `audio/raw/alignment.mp3` | ElevenLabs Sound Effects V2, original prompt | Generated specifically for this project on 2026-09-11 |
| Underscore, anticipatory air, and sub-impact components | `scripts/audio_mix.py`, original numerical synthesis | Created for this project; no external samples |

The generated effects used the existing authorized ElevenLabs credential found in the City Skyline project. The credential was never copied into this project, printed, or included in a command argument. Three successful sound requests requested 28 seconds total. Full prompts and available billing metadata are in `audio/generation_manifest.json`.

**License verification limit:** sound generation succeeded, but the API refused subscription-tier lookup (HTTP 401). The account tier therefore remains unverified. ElevenLabs states that paid plans include commercial rights for eligible non-beta generations; free-plan output has different restrictions and attribution requirements. Do not describe these generated effects as CC0 or independently licensed stock sounds. For any external commercial release, confirm the plan active at generation time. This does not affect locally previewing the trailer.

- API reference: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- Official publishing/plan guidance: https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform
- Sound Effects overview: https://elevenlabs.io/docs/overview/capabilities/sound-effects

## Rebuilding and verification

Run `scripts/audio_mix.py --ffmpeg PATH_TO_FFMPEG` with a Python interpreter containing NumPy. The already-generated MP3 source files are sufficient; rebuilding the mix does not contact any API. Run `scripts/audio_generate.py --env-file EXTERNAL_ENV_PATH` only to generate missing effects; existing files are reused.

`audio/mix_qa.json` records file and signal checks. All stems and the mix were checked for expected duration, channel count, sample rate, finite values, and clipping. The final mix was loudness processed to a nominal -18 LUFS target, with controlled peaks and retained cinematic dynamics. Generated leading silence was removed so the alignment lands at the intended moment. Perceptual audition has not been performed by this agent; the film review should include listening on headphones and speakers.
