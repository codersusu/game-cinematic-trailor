"""Encode the four-second continuous reach proof with its original soundtrack excerpt."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import imageio_ffmpeg

folder = ROOT / 'previews/v6/acting-frames'
mapping = json.loads((folder / 'mapping.json').read_text())
assert mapping['source_frames'] == list(range(385, 481))
assert all((folder / f'{frame:04d}.png').is_file() for frame in range(1, 97))
out = ROOT / 'previews/v6/Astra-Reach-motion-proof.mp4'
partial = out.with_name('.reach.partial.mp4')
filters = (
    '[0:v]drawbox=x=0:y=0:w=iw:h=69:color=black:t=fill,'
    'drawbox=x=0:y=ih-69:w=iw:h=69:color=black:t=fill,'
    'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
    'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];'
    '[1:a]atrim=start=16:end=20,asetpts=PTS-STARTPTS[a]'
)
subprocess.run([
    imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-framerate', '24',
    '-i', str(folder / '%04d.png'), '-i', str(ROOT / 'audio/v5/last_observatory_v5_mix.wav'),
    '-filter_complex', filters, '-map', '[v]', '-map', '[a]', '-frames:v', '96', '-t', '4',
    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-c:a', 'aac', '-b:a', '256k',
    '-movflags', '+faststart', str(partial),
], check=True)
partial.replace(out)
frames = imageio_ffmpeg.read_frames(str(out))
metadata = next(frames)
count = sum(1 for _ in frames)
assert count == 96 and metadata['size'] == (960, 540)
(ROOT / 'previews/v6/acting-proof-qa.json').write_text(json.dumps({
    'file': str(out.relative_to(ROOT)), 'decoded_frames': count, 'metadata': metadata,
    'source_frames': [385, 480], 'technical_checks': 'passed',
    'visual_review': 'awaiting inspection',
}, indent=2) + '\n')
print(out)
