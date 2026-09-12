"""Reuse only the V6 frames proven visually equivalent by the V7 scene audit.

Optional optimization. A clean checkout can instead render all V7 frames.
Copies files, never changes V6 frames; verifies the complete V6 frame-set hash.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/v7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text())


audit = load('renders/v7/scene-audit.json')
assert audit['status'] == 'passed' and audit['early_reuse']['safe']
assert audit['early_reuse']['frames'] == [1, 343]
assert audit['early_reuse']['additional_motion_blur_sample'] == 343.5
assert audit['source_sha256'] == sha(ROOT / 'observatory-v6.blend')
assert audit['candidate_sha256'] == sha(ROOT / 'observatory-v7.blend')
source = load('renders/v6/frame-source.json')
assert source['scene_sha256'] == audit['source_sha256']
assert source['samples'] == 64 and source['resolution'] == [1920, 1080]
assert source['fps'] == 24 and source['adaptive_threshold'] == .025
old_frames = [ROOT / 'renders/v6/frames' / f'{i:04d}.png' for i in range(1, 577)]
old_hashes = {p.name: sha(p) for p in old_frames}
aggregate = hashlib.sha256(''.join(name + ':' + value + '\n'
                                  for name, value in old_hashes.items()).encode()).hexdigest()
assert aggregate == load('renders/v6/render-manifest.json')['frame_set']['aggregate_sha256']
record = dict(source, scene='observatory-v7.blend', scene_sha256=audit['candidate_sha256'])
stamp = OUT / 'frame-source.json'
folder = OUT / 'frames'
folder.mkdir(parents=True, exist_ok=True)
if any(folder.glob('[0-9]*.png')):
    assert stamp.exists() and json.loads(stamp.read_text()) == record, 'Existing V7 frames use different inputs'
stamp.write_text(json.dumps(record, indent=2) + '\n')
copied = []
for old in old_frames[:343]:
    target = folder / old.name
    if target.exists():
        assert sha(target) == old_hashes[old.name], 'Existing cached frame differs: ' + old.name
    else:
        shutil.copy2(old, target)
    copied.append({'frame': int(old.stem), 'sha256': old_hashes[old.name]})
(OUT / 'reused-frames.json').write_text(json.dumps({
    'source_scene_sha256': audit['source_sha256'],
    'candidate_scene_sha256': audit['candidate_sha256'],
    'source_frame_set_verified': True,
    'scene_audit': 'renders/v7/scene-audit.json',
    'unchanged_frame_range': [1, 343], 'count': len(copied), 'frames': copied,
}, indent=2) + '\n')
print('V7_CACHED_FRAMES_READY', len(copied))
