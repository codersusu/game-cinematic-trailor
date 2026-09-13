import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import heroine_forest_v12 as h
bpy.ops.wm.open_mainfile(filepath=str(R/'bear-bow-forest-v12.blend'),use_scripts=False);sc=bpy.context.scene;tar=bpy.data.objects['V12 | FemaleAdult04 forest rig'];src=bpy.data.objects['Rig'];body=bpy.data.objects['V12 | FemaleAdult04 full body'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];C=Matrix.Rotation(-math.pi/2,4,'Z')@Matrix.Diagonal((.009357154369354248,)*3+(1,));tr,sr,mp,cal,grips=h._calibration(tar,src,C);rows=[]
for f in [1,20,32,35,45,50,51,59,68,69,96,120,144]:
 sc.frame_set(f);bpy.context.view_layer.update();lo,hi=h.mesh_bounds(body);eyes=sum((tar.matrix_world@tar.pose.bones[n].head for n in ['Bip01 LEye','Bip01 REye']),Vector())*.5;hands={}
 for side in 'LR':
  hand=tar.pose.bones[f'Bip01 {side} Hand'];p=tar.matrix_world@hand.matrix@(grips[side]/.009357154369354248);goal=src.matrix_world@src.pose.bones[f'B-handProp.{side}'].matrix.translation;hands[side]=(p-goal).length
 rows.append({'frame':f,'body_bounds':[lo.tolist(),hi.tolist()],'eye_world':list(eyes),'first_camera_z':bpy.data.objects['V9 | First-person escape'].matrix_world.translation.z,'hand_anchor_error':hands})
report={'scene':'bear-bow-forest-v12.blend','scene_sha256':hashlib.sha256((R/'bear-bow-forest-v12.blend').read_bytes()).hexdigest(),'sampled_frames':rows,'facial_action':body.data.shape_keys.animation_data.action.name if body.data.shape_keys.animation_data and body.data.shape_keys.animation_data.action else None,'shape_values_nonzero':[(k.name,k.value) for k in body.data.shape_keys.key_blocks if abs(k.value)>1e-6],'material_images':{m.name:[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] for m in body.data.materials},'blue_meshes_remaining':[n for n in ['HumanF_BodyMesh','V9 | First-person arms only'] if n in bpy.data.objects]};(R/'previews/v12/forest-character-saved-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
