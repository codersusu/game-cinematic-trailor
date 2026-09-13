"""Build only: V10 forest with the actual V11-room heroine, for root rendering."""
from pathlib import Path
import bpy,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from heroine_forest_v12 import replace_forest_heroine,adjust_first_person_eye_height
source=ROOT/'bear-bow-forest-v10.blend';dest=ROOT/'bear-bow-forest-v12.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
def protected_hash():
 names=['Rig','A | archer placement','RigRoot','Bear_Animated','Human_Bow','Human_Arrow','A | working bowstring','V9 | Third-person escape','V9 | First-person escape'];rows=[]
 for n in names:
  o=bpy.data.objects.get(n)
  if not o:continue
  a=o.animation_data.action if o.animation_data else None
  if a:
   rows.append((n,[(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for f in a.fcurves]))
 return hashlib.sha256(repr(rows).encode()).hexdigest()
before=protected_hash();keeper=replace_forest_heroine(bpy.context.scene);after=protected_hash();assert before==after,'Protected animation changed'
eyeheight=adjust_first_person_eye_height(bpy.context.scene)
bpy.context.scene['v12_character']='Actual observatory FemaleAdult04 replaces blue proxy; same baked source performance'
bpy.ops.wm.save_as_mainfile(filepath=str(dest));report={'scene':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'protected_action_hash_before':before,'protected_action_hash_after':after,'heroine':keeper['body'].name,'first_person_arms':keeper['arms'].name,'first_person_tag':'first','third_person_tag':'third','no_gpu_render':True,'first_camera_eyeheight_adjustment':eyeheight,'max_grip_error_m':keeper['report']['max_grip_error_m'],'max_shoulder_reach_m':keeper['report']['max_shoulder_reach_m'],'max_floor_profile_error_m':keeper['report']['max_floor_profile_error_m']}
p=ROOT/'previews/v12/forest-character-build.json';p.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
