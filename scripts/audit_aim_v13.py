import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
fs=sorted(set([1+i*.25 for i in range(157)]+list(range(41,145))));source={}
for filename,data in [('bear-bow-forest-v13-initial-archery.blend',source),('bear-bow-forest-v13.blend',{})]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/filename),use_scripts=False);sc=bpy.context.scene;r=bpy.data.objects['V12 | FemaleAdult04 forest rig'];a=bpy.data.objects['Human_Arrow'];rows=[]
 for f in fs:
  v.set_frame(sc,f);u,e,h=[(r.matrix_world@r.pose.bones['Bip01 L '+n].matrix).translation for n in ['UpperArm','Forearm','Hand']];record={'l1':(e-u).length,'l2':(h-e).length,'hand':h.copy(),'bow_location':bpy.data.objects['Human_Bow'].matrix_world.translation.copy(),'root':r.matrix_world.copy(),'right_hand':r.matrix_world@r.pose.bones['Bip01 R Hand'].matrix,'tip':a.matrix_world@Vector((0,0,max(x.co.z for x in a.data.vertices)))}
  if not source or filename.endswith('initial-archery.blend'):data[f]=record
  else:rows.append({'frame':f,'upper_length_change_m':abs(record['l1']-source[f]['l1']),'forearm_length_change_m':abs(record['l2']-source[f]['l2']),'root_matrix_error':max(abs(record['root'][i][j]-source[f]['root'][i][j]) for i in range(4) for j in range(4)),'right_hand_matrix_error':max(abs(record['right_hand'][i][j]-source[f]['right_hand'][i][j]) for i in range(4) for j in range(4)),'tip_error_m':(record['tip']-source[f]['tip']).length if f>=35 else None,'left_hand_change_m':(record['hand']-source[f]['hand']).length,'grip_offset_error_m':((record['hand']-record['bow_location'])-(source[f]['hand']-source[f]['bow_location'])).length})
 if rows:
  report={'samples':rows,'max_upper_length_change_m':max(x['upper_length_change_m'] for x in rows),'max_forearm_length_change_m':max(x['forearm_length_change_m'] for x in rows),'max_root_matrix_error':max(x['root_matrix_error'] for x in rows),'max_right_hand_matrix_error':max(x['right_hand_matrix_error'] for x in rows),'max_impact_tip_error_m':max(x['tip_error_m'] or 0 for x in rows),'max_grip_offset_error_m':max(x['grip_offset_error_m'] for x in rows)};print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));(v.OUT/'archery-aim-limb-audit.json').write_text(json.dumps(report,indent=2))
