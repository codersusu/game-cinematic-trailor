"""Reuse verified, unchanged room frames at preview resolution."""
from pathlib import Path
import hashlib, json
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads((ROOT/path).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
audit = read('previews/v8/finger/gesture-audit.json')
edit = read('previews/v11/room-edit-report.json')
source = read('renders/v7/frame-source.json')
assert audit['status']=='passed' and audit['maximum_finger_curve_difference_through_417']==0
assert audit['source_sha256']==source['scene_sha256']==sha(ROOT/'observatory-v7.blend')
assert audit['study_sha256']==edit['source_sha256']==sha(ROOT/'observatory-v8-finger-study.blend')
assert edit['all_animation_curves_unchanged'] and edit['scene_sha256']==sha(ROOT/edit['scene'])
folder = ROOT/'previews/v11/room-frames'
folder.mkdir(parents=True, exist_ok=True)
rows = []
for frame in range(37,418,2):
    original = ROOT/'renders/v7/frames'/f'{frame:04d}.png'
    target = folder/original.name
    with Image.open(original) as image:
        assert image.size==(1920,1080)
        image.convert('RGB').resize((960,540),Image.Resampling.LANCZOS).save(target)
    rows.append({'frame':frame,'source_sha256':sha(original),'preview_sha256':sha(target)})
(folder/'reused-frame-source.json').write_text(json.dumps({
    'source':source,'audit':'previews/v8/finger/gesture-audit.json',
    'room_edit':'previews/v11/room-edit-report.json','frames':rows},indent=2)+'\n')
print('Reused verified unchanged room range:',len(rows),'frames')
