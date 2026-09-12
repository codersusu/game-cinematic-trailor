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
folder = ROOT / ('renders/v6/frames' if args.native else 'previews/v6/acting-frames')
first = 385 if args.native else 1
width, height = (1920, 1080) if args.native else (960, 540)
if not args.native:
    mapping = json.loads((folder / 'mapping.json').read_text())
    assert mapping['source_frames'] == list(range(385, 481))
assert all((folder / f'{frame:04d}.png').is_file() for frame in range(first, first + 96))
out = ROOT / ('previews/v6/Astra-Reach-closeup-1080p.mp4' if args.native else 'previews/v6/Astra-Reach-motion-proof.mp4')
partial = out.with_name('.' + out.stem + '.partial.mp4')
bar = round((height - width / 2.39) / 2)
filters = (
    f'[0:v]drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,'
    f'drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill,'
    'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
    'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];'
    '[1:a]atrim=start=16:end=20,asetpts=PTS-STARTPTS[a]'
)
subprocess.run([
    imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-framerate', '24', '-start_number', str(first),
    '-i', str(folder / '%04d.png'), '-i', str(ROOT / 'audio/v5/last_observatory_v5_mix.wav'),
    '-filter_complex', filters, '-map', '[v]', '-map', '[a]', '-frames:v', '96', '-t', '4',
    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-c:a', 'aac', '-b:a', '256k',
    '-movflags', '+faststart', str(partial),
], check=True)
partial.replace(out)
frames = imageio_ffmpeg.read_frames(str(out))
metadata = next(frames)
count = sum(1 for _ in frames)
assert count == 96 and metadata['size'] == (width, height)
(ROOT / ('previews/v6/closeup-qa.json' if args.native else 'previews/v6/acting-proof-qa.json')).write_text(json.dumps({
    'file': str(out.relative_to(ROOT)), 'decoded_frames': count, 'metadata': metadata,
    'source_frames': [385, 480], 'technical_checks': 'passed',
    'visual_review': 'awaiting inspection',
}, indent=2) + '\n')
print(out)
