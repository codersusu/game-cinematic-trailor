"""Reuse genuine1080p room renders through the verified preservation chain."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
room=read('previews/v12/room-entry-audit.json')
edit=read('previews/v11/room-edit-report.json')
finger=read('previews/v8/finger/gesture-audit.json')
render=read('renders/v7/frame-source.json')
assert room['status']=='passed' and room['maximum_later_pose_difference']==0
assert room['scene_sha256']==sha(ROOT/room['scene'])
assert room['source_sha256']==edit['scene_sha256']==sha(ROOT/edit['scene'])
assert edit['source_sha256']==finger['study_sha256']==sha(ROOT/edit['source'])
assert finger['status']=='passed' and finger['maximum_finger_curve_difference_through_417']==0
assert finger['source_sha256']==render['scene_sha256']==sha(ROOT/'observatory-v7.blend')
assert render['resolution']==[1920,1080]
output=ROOT/'previews/v13/room-frames';output.mkdir(parents=True,exist_ok=True)
stamp=read('previews/v13/room-frames/source.json')
assert stamp['sha256']==room['scene_sha256'] and stamp['resolution']==[1920,1080]
references=read('previews/v11/room-frames/reused-frame-source.json')['frames']
rows=[]
for row in references:
    frame=row['frame']
    if not 227<=frame<=417:continue
    source=ROOT/'renders/v7/frames'/f'{frame:04d}.png'
    assert sha(source)==row['source_sha256']
    with Image.open(source) as image:assert image.size==(1920,1080)
    target=output/source.name
    if target.exists():assert sha(target)==row['source_sha256']
    else:shutil.copy2(source,target)
    rows.append({'frame':frame,'sha256':row['source_sha256']})
assert len(rows)==96
(output/'reused-frames.json').write_text(json.dumps({'native_resolution':[1920,1080],
    'scene_sha256':room['scene_sha256'],'original_scene_sha256':render['scene_sha256'],
    'source':'renders/v7/frames','safe_sampled_range':[227,417],
    'motion_blur_boundary_frames_excluded':[225,419],'frames':rows},indent=2)+'\n')
print('V13_NATIVE_1080P_FRAMES_REUSED',len(rows))
