"""Copy later room footage only after the V12 preservation audit passes."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
audit=read('previews/v12/room-entry-audit.json')
assert audit['status']=='passed' and audit['maximum_later_pose_difference']==0
assert audit['scene_sha256']==sha(ROOT/audit['scene'])
assert audit['source_sha256']==sha(ROOT/audit['source_scene'])
old=read('previews/v11/combined-movie-qa.json')
assert old['room_scene_sha256']==audit['source_sha256']
folder=ROOT/'previews/v12/room-frames';folder.mkdir(parents=True,exist_ok=True)
identity=read('previews/v12/room-frames/source.json')
assert identity['sha256']==audit['scene_sha256']
reused=[]
for row in old['frames_mapping']:
    # The first preserved integer frame has a motion-blur shutter reaching
    # backward into the changed interval. Render that frame again as well.
    if row['section']!='room' or row['source_frame']<audit['preserved_from_frame']+2:continue
    frame=row['source_frame'];original=ROOT/'previews/v11/room-frames'/f'{frame:04d}.png'
    assert sha(original)==row['source_sha256']
    target=folder/original.name
    if target.exists():assert sha(target)==row['source_sha256']
    else:shutil.copy2(original,target)
    reused.append({'frame':frame,'sha256':row['source_sha256']})
(folder/'reused-frames.json').write_text(json.dumps({'audit':'previews/v12/room-entry-audit.json',
    'source_scene_sha256':audit['source_sha256'],'scene_sha256':audit['scene_sha256'],
    'preserved_from_frame':audit['preserved_from_frame'],'frames':reused},indent=2)+'\n')
print('V12_REUSED_ROOM_FRAMES',len(reused))
