# Beyond the Threshold — V13 original score

**Final film music master:** `forest_to_astra_music_final.wav` — **32.75 seconds, 48 kHz stereo, 24-bit PCM**. Use this file from time zero underneath the final film, which begins at forest source frame 10 and contains 10.25 seconds of forest followed by 22.5 seconds in the room. `forest_to_astra_music_final.mp3` is the matching 256 kbps listening preview.

The final editorial change removes exactly the first **0.75 seconds / 36,000 samples** from the existing score and adds a gentle **120 ms / 5,760-sample sin-squared fade-in**. The composition was not regenerated or renormalized. Every sample after the new fade-in exactly matches the corresponding original sample, including the existing final fade. The original `forest_to_astra_music.wav` and `.mp3` remain byte-for-byte unchanged at **33.5 seconds**; the six stems and `score-events.json` also retain their original timeline.

The original composition moves from a D-minor forest pulse into a quieter doorway passage, then opens into D-major orchestral colors for Astra. It contains 165 note events performed with sampled cello and violin sections, French horn, flute, harp, glockenspiel and orchestral percussion. A restrained synthesized bass layer supports the acoustic instruments. Six separate, aligned stems are included.

| Final film time | Musical treatment |
|---|---|
| 0–10.25 s | Bowed eighth-note pulse, low strings and measured percussion build tension |
| 10.25 s | Cymbal transition releases into a thinner doorway texture |
| 10.25–14.25 s | Quiet open fifths and spaced harp notes leave room for the vigilance/shoulder check |
| 14.25–16.75 s | Suspended harmony anticipates discovery |
| 16.75 s onward | Warmer strings, a rising flute motif and harp introduce Astra |
| 21.95 s | The melodic phrase broadens for the expressive revelation |
| 28.55 s | A restrained glockenspiel accent and major added-note chord accompany the fingertip gesture |
| 30.25–32.75 s | Resolution and a smooth reverberant fade |

The final WAV measures **−17.99 LUFS integrated**, **−3.40 dBTP**, with zero clipped samples; the final MP3 measures −17.99 LUFS and −3.39 dBTP and decodes to exactly 32.75 seconds. `final-edit-qa.json` records the trim, shifted cues, sample-exact preservation checks, file hashes and final measurements. The original master measured −18.0 LUFS and −3.4 dBTP; its measurements, hashes and original cue levels remain in `music-qa.json`. `score-events.json` records every original note and source recording. Full perceptual listening has not been independently reviewed by the agent; the MP3 is provided for audition.

No speech, existing musical recording, old footsteps or previously timed surprise/impact effects were used. The percussion here is part of the new musical composition. No service API, API key or paid generation request was used.

## Credits and reuse

Composition, arrangement and production: **original music for The Last Observatory**, authored in `scripts/music_v13.py` as deterministic note sequencing, orchestration, envelopes, stereo placement and algorithmic reverberation. No existing melody or score was sampled.

Instrument recordings: **VSCO 2 Community Edition**, Versilian Studios. The repository credits Sam Gossner and Simon Dalzell for recording and Elan Hickler/Soundemote for sample cutting. The library is released under **CC0-1.0**.

- [Official VSCO Community Edition page](https://versilian-studios.com/vsco-community/)
- [Official sample repository](https://github.com/sgossner/VSCO-2-CE)
- Pinned source revision: `440300901dfe9275fd84e0b7763af1f8443ae62e`
- Local license: `sources/LICENSE`
- Exact 24-file source inventory, download URLs and verified Git-blob/SHA-256 hashes: `sources/acquisition.json`

The CC0 statement applies to the instrument recordings. The composition is newly created project work; this document does not assign a new public license to the user's project.

Reproduce only the final editorial trim with the project's Python runtime: `python3 audio/v13/edit_final.py`. This reads the preserved original master and writes only the two final audio files and `final-edit-qa.json`.

To rebuild the original 33.5-second composition, use `python3 scripts/music_v13.py`. It requires NumPy, SciPy, SoundFile and imageio-ffmpeg, already available through `tools/python`. Existing source samples must remain at their recorded paths. The composition script writes only `audio/v13` and does not apply the final editorial trim.
