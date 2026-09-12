"""Verify the V6 AAC delivery using the same measured audio checks as V5."""
from pathlib import Path
import json
from verify_audio_v5 import verify, imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
report = verify(ROOT / 'The Last Observatory - Astra Reach.mp4', imageio_ffmpeg.get_ffmpeg_exe())
report['version'] = 6
report['source_master'] = 'audio/v5/last_observatory_v5_mix.wav'
output = ROOT / 'renders/v6/audio-qa.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
if report['failed_checks']:
    raise SystemExit('V6 audio checks failed')
