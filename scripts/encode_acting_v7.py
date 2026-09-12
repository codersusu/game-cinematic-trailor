"""Encode the reach proof, or use --native for its finished 1080p close-up."""
from pathlib import Path
import json
import subprocess
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import imageio_ffmpeg

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native', action='store_true')
args = parser.parse_args()
folder = ROOT / ('renders/v7/frames' if args.native else 'previews/v7/acting-frames')
first = 345 if args.native else 1
width, height = (1920, 1080) if args.native else (960, 540)
if not args.native:
    mapping = json.loads((folder / 'mapping.json').read_text())
    assert mapping['source_frames'] == list(range(345, 481))
assert all((folder / f'{frame:04d}.png').is_file() for frame in range(first, first + 136))
out = ROOT / ('previews/v7/Astra-Approach-closeup-1080p.mp4' if args.native else 'previews/v7/Astra-Approach-motion-proof.mp4')
partial = out.with_name('.' + out.stem + '.partial.mp4')
bar = round((height - width / 2.39) / 2)
filters = (
    f'[0:v]drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,'
    f'drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill,'
    'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
    'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];'
    '[1:a]atrim=start=14.3333333333333:end=20,asetpts=PTS-STARTPTS[a]'
)
subprocess.run([
    imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-framerate', '24', '-start_number', str(first),
    '-i', str(folder / '%04d.png'), '-i', str(ROOT / 'audio/v7/last_observatory_v7_mix.wav'),
    '-filter_complex', filters, '-map', '[v]', '-map', '[a]', '-frames:v', '136', '-t', str(136/24),
    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-c:a', 'aac', '-b:a', '256k',
    '-movflags', '+faststart', str(partial),
], check=True)
partial.replace(out)
frames = imageio_ffmpeg.read_frames(str(out))
metadata = next(frames)
count = sum(1 for _ in frames)
assert count == 136 and metadata['size'] == (width, height)
(ROOT / ('previews/v7/closeup-qa.json' if args.native else 'previews/v7/acting-proof-qa.json')).write_text(json.dumps({
    'file': str(out.relative_to(ROOT)), 'decoded_frames': count, 'metadata': metadata,
    'source_frames': [345, 480], 'technical_checks': 'passed',
    'visual_review': 'awaiting inspection',
}, indent=2) + '\n')
print(out)
