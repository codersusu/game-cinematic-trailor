"""Rocketbox FemaleAdult04 retarget onto the baked forest archer performance.

Reuse the exact room mesh, materials, facial shapes and opacity hair. Source
actor bones remain as the unchanged driver for existing props/cameras. No
rendering is performed. V12 objects carry explicit first/third visibility tags.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
import numpy as np
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1]
ROOM=ROOT/'observatory-v11-single-reaction.blend'

def matrix_blend(a,b,t):
 at,aq,asc=a.decompose();bt,bq,bsc=b.decompose()
 return Matrix.LocRotScale(at.lerp(bt,t),aq.slerp(bq,t),asc.lerp(bsc,t))

def mapping():
 d={'Bip01 Pelvis':'B-hips','Bip01 Spine':'B-spine','Bip01 Spine1':'B-spine','Bip01 Spine2':'B-chest','Bip01 Neck':'B-neck','Bip01 Head':'B-head'}
 for side in 'LR':
  for t,s in [('Clavicle','shoulder'),('UpperArm','upperArm'),('Forearm','forearm'),('Hand','hand'),('Thigh','thigh'),('Calf','shin'),('Foot','foot'),('Toe0','toe')]:d[f'Bip01 {side} {t}']=f'B-{s}.{side}'
  for i,s in enumerate(['thumb','indexFinger','middleFinger','ringFinger','pinky']):
   for j in range(3):d[f'Bip01 {side} Finger{i}'+('' if j==0 else str(j))]=f'B-{s}{j+1:02}.{side}'
 return d

def palm_frame(points,side,source):
 wrist=points[f'B-hand.{side}'] if source else points[f'Bip01 {side} Hand']
 middle=points[f'B-middleFinger01.{side}'] if source else points[f'Bip01 {side} Finger2']
 index=points[f'B-indexFinger01.{side}'] if source else points[f'Bip01 {side} Finger1']
 pinky=points[f'B-pinky01.{side}'] if source else points[f'Bip01 {side} Finger4']
 y=(middle-wrist).normalized();x=index-pinky;x=(x-y*x.dot(y)).normalized();z=x.cross(y).normalized();x=y.cross(z).normalized()
 m=Matrix((x,y,z)).transposed().to_4x4();m.translation=wrist
 return m,(middle-wrist).length,(index-pinky).length

def mesh_bounds(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);m=np.array(ev.matrix_world);pts=np.einsum('ij,kj->ik',v,m[:3,:3])+m[:3,3];assert np.isfinite(pts).all(),ob.name;ev.to_mesh_clear();return pts.min(0),pts.max(0)

def apply_pose(rig,pose):
 for b in rig.pose.bones:
  kw={} if b.parent is None else {'parent_matrix':pose[b.parent.name],'parent_matrix_local':b.parent.bone.matrix_local}
  b.matrix_basis=b.bone.convert_local_to_pose(pose[b.name],b.bone.matrix_local,invert=True,**kw)
 bpy.context.view_layer.update()

def _clear_animation(obj):
 obj.animation_data_clear()
 for c in list(obj.constraints):obj.constraints.remove(c)
 if obj.type=='ARMATURE':
  for b in obj.pose.bones:
   for c in list(b.constraints):b.constraints.remove(c)
   b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
 if obj.type=='MESH' and obj.data.shape_keys:
  obj.data.shape_keys.animation_data_clear()
  for k in obj.data.shape_keys.key_blocks:
   if k.name!='Basis':k.value=0

def _calibration(target,source,C):
 tr={b.name:Matrix.Translation((C@b.matrix_local).translation)@(C.to_quaternion()@b.matrix_local.to_quaternion()).to_matrix().to_4x4() for b in target.data.bones};sr={b.name:b.matrix_local.copy() for b in source.data.bones};mp=mapping();cal={n:Quaternion() for n in mp}
 children={}
 for side in 'LR':
  for n,nextn in [('Clavicle','UpperArm'),('UpperArm','Forearm'),('Forearm','Hand'),('Thigh','Calf'),('Calf','Foot'),('Foot','Toe0')]:children[f'Bip01 {side} {n}']=f'Bip01 {side} {nextn}'
 for n,ch in children.items():
  td=tr[ch].translation-tr[n].translation;sd=sr[mp[ch]].translation-sr[mp[n]].translation;cal[n]=td.normalized().rotation_difference(sd.normalized())
 grips={};palm_cals={}
 for side in 'LR':
  tf,tl,tw=palm_frame({n:m.translation for n,m in tr.items()},side,False);sf,sl,sw=palm_frame({n:m.translation for n,m in sr.items()},side,True)
  palm_cals[side]=sf.to_quaternion()@tf.to_quaternion().inverted()
  hand=f'Bip01 {side} Hand';cal[hand]=palm_cals[side]
  for n in mp:
   if n.startswith(f'Bip01 {side} Finger'):cal[n]=palm_cals[side]
  relative=sf.inverted()@sr[f'B-handProp.{side}'].translation;relative.x*=tw/sw;relative.y*=tl/sl;relative.z*=min(tw/sw,tl/sl)
  point=tf@relative;grips[side]=tr[hand].inverted()@point
 return tr,sr,mp,cal,grips

def _retarget_pose(target,src,tr,sr,mp,cal):
 out={}
 for b in target.data.bones:
  n=b.name;rest=tr[n];parent=b.parent
  pos=out[parent.name]@(tr[parent.name].inverted()@rest).translation if parent else src['B-hips'].translation.copy()
  if n.startswith('Bip01 ') and n.endswith(' Clavicle'):
   # Rocketbox parents clavicles to Neck; compensate that hierarchy so the
   # chest drives shoulder placement while the head can turn independently.
   pos=out['Bip01 Spine2']@(tr['Bip01 Spine2'].inverted()@rest).translation
  if n.startswith('Bip01 ') and n.endswith(' Thigh'):
   pos=out['Bip01 Pelvis']@(tr['Bip01 Pelvis'].inverted()@rest).translation
  s=mp.get(n)
  if s:
   sm=src[s]
   if n=='Bip01 Spine1':sm=matrix_blend(src['B-spine'],src['B-chest'],.50);srq=sr['B-spine'].to_quaternion().slerp(sr['B-chest'].to_quaternion(),.5)
   else:srq=sr[s].to_quaternion()
   q=sm.to_quaternion()@srq.inverted()@cal[n]@rest.to_quaternion();out[n]=Matrix.Translation(pos)@q.to_matrix().to_4x4()
  elif parent:out[n]=out[parent.name]@(tr[parent.name].inverted()@rest)
  else:out[n]=rest.copy()
 return out

def _solve_hand(target,pose,tr,src,side,grip):
 names=[f'Bip01 {side} {part}' for part in ['UpperArm','Forearm','Hand']];upper,fore,hand=names
 old={n:pose[n].copy() for n in pose};a=pose[upper].translation.copy();b=pose[fore].translation.copy();c=pose[hand].translation.copy()
 goal=src[f'B-handProp.{side}'].translation.copy();handq=pose[hand].to_quaternion();wrist=goal-handq@grip
 l1=(tr[fore].translation-tr[upper].translation).length;l2=(tr[hand].translation-tr[fore].translation).length;vector=wrist-a;dist=vector.length;axis=vector.normalized()
 reach=max(0,dist-(l1+l2-.001));shift=axis*reach
 # A small shoulder reach handles the differing palm/forearm proportions;
 # upper/lower arms retain their authored lengths and the torso is untouched.
 a+=shift;dist=(wrist-a).length;axis=(wrist-a).normalized();d=max(abs(l1-l2)+.0001,min(l1+l2-.0001,dist));along=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-along*along))
 # Keep the native elbow on its authored bend side and away from the torso.
 pole=src[f'B-forearm.{side}'].translation-a;pole-=axis*pole.dot(axis)
 if pole.length<1e-5:pole=b-a-axis*(b-a).dot(axis)
 if pole.length<1e-5:pole=Vector((0,0,-1))
 pole.normalize();elbow=a+axis*along+pole*height
 qu=(b-old[upper].translation).normalized().rotation_difference((elbow-a).normalized())@old[upper].to_quaternion()
 qf=(c-b).normalized().rotation_difference((wrist-elbow).normalized())@old[fore].to_quaternion()
 pose[upper]=Matrix.Translation(a)@qu.to_matrix().to_4x4();pose[fore]=Matrix.Translation(elbow)@qf.to_matrix().to_4x4();pose[hand]=Matrix.Translation(wrist)@handq.to_matrix().to_4x4()
 change=pose[hand]@old[hand].inverted()
 for bone in target.data.bones:
  if any(p.name==hand for p in bone.parent_recursive):pose[bone.name]=change@old[bone.name]
 return {'grip_error_m':((pose[hand]@grip)-goal).length,'shoulder_reach_m':reach,'upper_arm_length_error_m':abs((pose[fore].translation-pose[upper].translation).length-l1),'forearm_length_error_m':abs((pose[hand].translation-pose[fore].translation).length-l2)}

def _arms_copy(scene,body):
 arms=body.copy();arms.data=body.data.copy();arms.name='V12 | FemaleAdult04 first-person arms';scene.collection.objects.link(arms)
 if arms.data.shape_keys:arms.shape_key_clear()
 allowed={g.index for g in arms.vertex_groups if any(token in g.name for token in [' UpperArm',' Forearm',' Hand',' Finger'])}
 keep={v.index for v in arms.data.vertices if sum(g.weight for g in v.groups if g.group in allowed)>.15}
 bm=bmesh.new();bm.from_mesh(arms.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(arms.data);bm.free()
 arms['v12_visibility']='first';arms['source_character']='Same Rocketbox FemaleAdult04 mesh/materials as room and full body';arms.hide_render=True;return arms

def replace_forest_heroine(scene,report_path=None):
 source=bpy.data.objects['Rig'];source_body=bpy.data.objects['HumanF_BodyMesh'];start,end=scene.frame_start,scene.frame_end
 snapshots={}
 for f in range(start,end+1):
  scene.frame_set(f);bpy.context.view_layer.update();ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());lo,hi=mesh_bounds(source_body);snapshots[f]={'pose':{b.name:b.matrix.copy() for b in ev.pose.bones},'world':ev.matrix_world.copy(),'floor':float(lo[2])}
 original=set(bpy.data.objects)
 with bpy.data.libraries.load(str(ROOM),link=False) as (available,loaded):loaded.objects=['Bip01','f004_hipoly_81_bones_opacity']
 target=next(o for o in loaded.objects if o.type=='ARMATURE');body=next(o for o in loaded.objects if o.type=='MESH')
 for o in loaded.objects:scene.collection.objects.link(o)
 # Appended dependencies can include the old room path empty. Preserve mesh-to-
 # rig transform, then sever the room path. The actual materials remain intact.
 scene.frame_set(1);bpy.context.view_layer.update();relative=target.matrix_world.inverted()@body.matrix_world
 worldscale=target.matrix_world.to_scale();scale=sum(abs(x) for x in worldscale)/3
 if not .007<scale<.012:scale=.0093571553
 target.parent=None;target.matrix_parent_inverse=Matrix.Identity(4);_clear_animation(target);_clear_animation(body);body.parent=target;body.matrix_parent_inverse=Matrix.Identity(4);body.matrix_basis=relative
 target.name='V12 | FemaleAdult04 forest rig';body.name='V12 | FemaleAdult04 full body';body['v12_visibility']='third';body['source_character']='Exact mesh/materials from observatory-v11-single-reaction.blend';body.hide_render=False
 for modifier in body.modifiers:
  if modifier.type=='ARMATURE':modifier.object=target
 # Centimetre bind with +X forward -> metres with -Y forward, as in archer.
 C=Matrix.Rotation(-math.pi/2,4,'Z')@Matrix.Diagonal((scale,scale,scale,1));invC=C.inverted();tr,sr,mp,cal,grips=_calibration(target,source,C)
 for material in body.data.materials:
  if material and material.use_nodes:
   for n in material.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image and n.image.filepath:n.image.filepath=bpy.path.abspath(n.image.filepath)
 target.rotation_mode='QUATERNION';previous={};rows=[]
 for f,sample in snapshots.items():
  scene.frame_set(f);target.matrix_world=sample['world']@C;pose=_retarget_pose(target,sample['pose'],tr,sr,mp,cal)
  local={n:Matrix.Translation(invC@m.translation)@(invC.to_quaternion()@m.to_quaternion()).to_matrix().to_4x4() for n,m in pose.items()};apply_pose(target,local);lo,hi=mesh_bounds(body);correction=sample['floor']-float(lo[2])
  for m in pose.values():m.translation.z+=correction
  hands={side:_solve_hand(target,pose,tr,sample['pose'],side,grips[side]) for side in 'LR'}
  local={n:Matrix.Translation(invC@m.translation)@(invC.to_quaternion()@m.to_quaternion()).to_matrix().to_4x4() for n,m in pose.items()};apply_pose(target,local);lo,hi=mesh_bounds(body)
  if f>=51:
   # Once the bow is stowed, keep the real glove/body skin above the native
   # floor profile; palm-to-string contact is no longer constrained.
   post_correction=sample['floor']-float(lo[2])
   for m in pose.values():m.translation.z+=post_correction
   local={n:Matrix.Translation(invC@m.translation)@(invC.to_quaternion()@m.to_quaternion()).to_matrix().to_4x4() for n,m in pose.items()};apply_pose(target,local);lo,hi=mesh_bounds(body)
  for b in target.pose.bones:
   q=b.rotation_quaternion
   if b.name in previous and previous[b.name].dot(q)<0:q.negate();b.rotation_quaternion=q
   previous[b.name]=q.copy()
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f)
  for prop in ['location','rotation_quaternion','scale']:target.keyframe_insert(prop,frame=f)
  rows.append({'frame':f,'source_floor_world_z':sample['floor'],'target_floor_world_z':float(lo[2]),'target_height_m':float(hi[2]-lo[2]),'whole_body_vertical_correction_m':correction,'hands':hands})
 for fc in target.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 target.animation_data.action.name='V12 | retargeted FemaleAdult04 shoot roll escape'
 # Remove both visible blue surfaces permanently; retain original source rig for
 # existing bow/camera motion and repeatable comparison/auditing.
 deleted=[]
 for n in ['HumanF_BodyMesh','V9 | First-person arms only']:
  o=bpy.data.objects.get(n)
  if o:deleted.append(n);bpy.data.objects.remove(o,do_unlink=True)
 arms=_arms_copy(scene,body)
 # Clean only extra appended room objects, not either production actor mesh.
 for o in list(bpy.data.objects):
  if o not in original and o not in [target,body,arms]:
   if o.type=='EMPTY':bpy.data.objects.remove(o,do_unlink=True)
 scene.frame_set(20);bpy.context.view_layer.update()
 report={'source_room':ROOM.name,'source_forest':'bear-bow-forest-v10.blend','character':'Microsoft Rocketbox FemaleAdult04','room_scale_m_per_unit':scale,'target_bones':len(target.data.bones),'mapped_bones':len(mp),'body_vertices':len(body.data.vertices),'first_person_vertices':len(arms.data.vertices),'materials':[m.name for m in body.data.materials],'mesh_geometry_reused':True,'old_blue_meshes_deleted':deleted,'cameras_bear_props_source_motion_edited':False,'strategy':'anatomical rest calibration, native source motion, target limb lengths, two-bone palm contact IK, source vertical floor profile','frames':rows,'max_grip_error_m':max(h['grip_error_m'] for r in rows for h in r['hands'].values()),'max_shoulder_reach_m':max(h['shoulder_reach_m'] for r in rows for h in r['hands'].values()),'max_floor_profile_error_m':max(abs(r['target_floor_world_z']-r['source_floor_world_z']) for r in rows),'rendered':False,'visual_review_pending':True}
 p=Path(report_path) if report_path else ROOT/'previews/v12/forest-character-retarget.json';p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(report,indent=2));return {'rig':target,'body':body,'arms':arms,'report':report}


def adjust_first_person_eye_height(scene):
 """Offset only first-camera height; keep its stabilized roll path unchanged."""
 camera=bpy.data.objects['V9 | First-person escape']
 if camera.get('v12_eyeheight_applied'):return dict(camera['v12_eyeheight_details'])
 action=camera.animation_data.action.copy();camera.animation_data.action=action;action.name='V12 | First-person camera at FemaleAdult04 eye height'
 def smooth(a,b,x):
  t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
 def offset(frame):
  if frame<=51:return -.17*(1-smooth(44,51,frame))
  return -.17*smooth(68,77,frame)
 curve=next(f for f in action.fcurves if f.data_path=='location' and f.array_index==2)
 for k in curve.keyframe_points:
  delta=offset(float(k.co.x));k.co.y+=delta;k.handle_left.y+=delta;k.handle_right.y+=delta
 camera['v12_eyeheight_applied']=True
 details={'shoot_run_offset_m':-.17,'ease_out_frames':[44,51],'roll_unchanged_frames':[51,68],'ease_in_frames':[68,77],'rotation_xy_other_cameras_unchanged':True}
 camera['v12_eyeheight_details']=details;scene.frame_set(scene.frame_current);bpy.context.view_layer.update();return details
