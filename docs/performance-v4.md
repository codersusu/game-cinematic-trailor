# V4 character performance

The V3 entrance used a full-body source clip but replaced the pelvis and lower-body motion with a procedural planting solve. That kept the feet near the floor while removing pelvis rotation, ankle roll and toe-off. Its imposed 0.68 m/s travel also disagreed with the source clip's roughly 1.42 m/s stride. V4 preserves a coherent authored gait and matches displacement to it.

## Acceptance criteria

- Native or authored whole-body walking motion, including pelvis rotation, natural opposing arm swing, knee swing, heel strike and toe-off.
- Root travel follows the stride; floor corrections stay small and do not replace the leg performance.
- An actual walk-to-stop transition leads into a relaxed idle, with head/eye attention toward the machine.
- Facial surprise at the threshold: brief brow lift, widened eyes and a small jaw opening, followed by a blink and recovery.
- Later wonder: eyes find the bright nucleus, chin lifts slightly, lips part into a soft rounded “wow” shape, and the expression eases into a restrained delighted smile.
- Separate eye, lid, lip/jaw and brow controls. A painted expression on the old fused face does not meet this requirement.
- Both facial beats need readable close framing. Preserve moving cinematic shots of the entrance, galaxy and observatory around the reaction inserts.
- Review short rendered motion and expression sequences before launching the complete final render. Grounding measurements alone do not establish convincing acting.

## Implemented edit

The film remains 24 seconds at 24 fps. Times below mark cut boundaries; numbered frames are inclusive.

| Frames | Time | Shot |
|---|---|---|
| 1–36 | 0–1.50 s | Moving 72 mm threshold portrait; surprise builds, peaks at frame 15, then eases into a blink and recovery. |
| 37–192 | 1.50–8.00 s | Moving 30 mm entrance shot; native acceleration and walking carry her through the doorway. |
| 193–288 | 8.00–12.00 s | Moving 48 mm close view of the rotating stellar machine. |
| 289–344 | 12.00–14.33 s | Moving 75 mm reaction portrait; gaze lifts, the mouth rounds into wonder at frame 317, then softens into a restrained smile at frame 331. |
| 345–480 | 14.33–20.00 s | Moving 29 mm observatory wide shot. |
| 481–576 | 20.00–24.00 s | Moving 30 mm closing view and title. |

The later “wow” is a visible facial performance; this revision contains no spoken dialogue. It uses real jaw, lip funnel/pucker, eyebrow, eyelid, gaze and cheek controls rather than a painted expression. Seven blinks and a restrained head turn add secondary motion.

## Native body motion and sound

The selected Microsoft Rocketbox Female Adult 04 uses its library's authored start, four complete neutral walk cycles, stop, and breathing idle. All 80 character bone names match the source rigs, but the FBX rest poses differ. The integration converts absolute source poses into the character's bind basis; directly copying rotation channels would deform it incorrectly.

The 30 fps source is sampled at 1.25 source frames per 24 fps film frame, preserving its timing. Start/walk/stop spans film frames 37–217 (7.50 seconds). The character and its native root path are uniformly scaled by approximately 0.9357 to cover 6.80 metres together, preserving the relationship between body size and stride. Native pelvis, leg, ankle and toe articulation remain intact. A four-frame orientation blend joins clips; a whole-character vertical correction handles floor clearance without replacing the legs with procedural IK.

The source motion proof measured floor corrections from −5.36 mm to +11.40 mm. These measurements describe the evaluated base mesh and do not independently prove final subdivided foot contact or convincing motion. Reviewed scene stills show planted boots, a clear doorway crossing and no obvious body/cloth clipping.

Eleven sound contacts follow frames 50, 68, 82, 97, 110, 126, 139, 155, 168, 180 and 191. The doorway transition is aligned to the measured crossing at frame 82.73 (3.405 seconds). Exact timing and source references are in [the audio synchronization record](../audio/v4/walk_sync.json).

## Review evidence and visual limits

The [acting preview](../previews/v4/Native-walk-and-expressions.mp4) contains 140 decoded frames at 960 × 540 and 24 fps: surprise frames 1–36, walking frames 97–144, and wonder frames 289–344. The [contact sheet](../previews/v4/acting-contact-sheet.jpg) is refreshed from that sequence's stronger final facial poses. The final movie now contains all 576 frames at native 1920 × 1080, 24 fps and 24 seconds. Full decoding passed; [representative final frames](../previews/v4/final-contact-sheet.jpg) were inspected for facial readability, doorway clearance, composition and title legibility. [Movie QA](../renders/v4/movie-qa.json) records these checks and their limits. Encoded audio measures −17.8 LUFS and −2.8 dBTP without clipping.

The stronger stills make surprise and wonder readable without visible eyelid inversion, mouth tearing or a neck discontinuity. Native walk poses show heel-led stepping, toe-off and relaxed arms. Still images cannot establish cadence, transition smoothness or speech synchronization; this revision has no speech track to synchronize.

This remains an older game character: 5,170 source vertices, 175 facial shapes including 52 ARKit channels, and seven 2K texture maps. Hair cards, smooth skin, bright eyes and a largely dark mouth interior limit portrait realism. Surface smoothing and Cycles materials improve presentation but do not make it a modern cinematic character scan.

## Asset decision

See [candidate research](character-research-v4.md). Rocketbox is the selected working replacement because its downloaded body clips and facial controls were verified. The more realistic Jungle Jim Sketchfab candidate still requires authenticated download and source inspection. It is not claimed to be acquired or used. Existing V3 deliverables remain intact alongside this revision.
