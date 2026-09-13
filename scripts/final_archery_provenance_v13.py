"""Read-only final saved-scene provenance and numerical preservation audit."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
SOURCE=ROOT/'bear-bow-forest-v13-before-arm-staging.blend'
def action_record(o):
 if not o.animation_data or not o.animation_data.action:return None
 return [(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for f in o.animation_data.action.fcurves]
def obj_hash(names):return hashlib.sha256(repr([(n,action_record(bpy.data.objects[n])) for n in names]).encode()).hexdigest()
names=['Human_Arrow','V9 | First-person escape','V9 | Third-person escape','RigRoot','Bear_Animated','A | archer placement']
original={};sourcehash=None
for path in [SOURCE,v.DEST]:
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['V12 | FemaleAdult04 forest rig'];bow=bpy.data.objects['Human_Bow'];arrow=bpy.data.objects['Human_Arrow'];present=[n for n in names if n in bpy.data.objects];ahash=obj_hash(present)
 if path==SOURCE:sourcehash=ahash
 else:assert ahash==sourcehash,'Protected object action changed'
 rows=[];directions={};grips=[];restrows=[]
 for f in range(1,145):
  v.set_frame(sc,f);record={'bones':{b.name:rig.matrix_world@b.matrix for b in rig.pose.bones},'bowhand':bow.matrix_world.inverted()@rig.matrix_world@rig.pose.bones['Bip01 L Hand'].matrix,'root':rig.matrix_world.copy(),'arrow':arrow.matrix_world.copy()}
  if path==SOURCE:original[f]=record;continue
  base=original[f];maxmatrix=max(abs(record['bones'][n][i][j]-base['bones'][n][i][j]) for n in record['bones'] for i in range(4) for j in range(4));grip=max(abs(record['bowhand'][i][j]-base['bowhand'][i][j]) for i in range(4) for j in range(4));rows.append({'frame':f,'max_bone_world_matrix_difference':maxmatrix,'bow_grip_local_matrix_difference':grip,'root_matrix_difference':max(abs(record['root'][i][j]-base['root'][i][j]) for i in range(4) for j in range(4)),'arrow_matrix_difference':max(abs(record['arrow'][i][j]-base['arrow'][i][j]) for i in range(4) for j in range(4))})
 if path==v.DEST:
  for f in sorted(set([1+i*.25 for i in range(125)]+[31.75,31.875,32,32.125,32.5,33])):
   v.set_frame(sc,f);o=arrow.matrix_world.translation;d=arrow.matrix_world.to_quaternion()@Vector((0,0,1));rest=bow.matrix_world@v.REST_LOCAL;miss=(o+d*(rest-o).dot(d)-rest).length;restrows.append({'frame':f,'rest_axis_miss_m':miss});directions[f]=d
  report={'final_scene_sha256':hashlib.sha256(v.DEST.read_bytes()).hexdigest(),'preceding_scene_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_object_names':present,'protected_object_action_hash':ahash,'protected_actions_identical':True,'max_arrow_matrix_difference_all144':max(r['arrow_matrix_difference'] for r in rows),'max_actor_root_matrix_difference':max(r['root_matrix_difference'] for r in rows),'max_post40_hero_bone_matrix_difference':max(r['max_bone_world_matrix_difference'] for r in rows if r['frame']>40),'max_bow_grip_local_matrix_difference':max(r['bow_grip_local_matrix_difference'] for r in rows),'max_loaded_and_release_rest_axis_miss_m':max(r['rest_axis_miss_m'] for r in restrows),'release_direction_change_degrees':math.degrees(directions[31.75].angle(directions[32])),'pose_samples':rows,'rest_samples':restrows};(v.OUT/'archery-final-provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:x for k,x in report.items() if k not in ['pose_samples','rest_samples']},indent=2))
