"""Native archer run/stow and Quaternius roll retarget, CPU only.

sample_escape_motion(scene, target_rig) returns evaluated rig-local matrices for
all 117 target bones. No persistent source objects or actions remain. Source
archer data and scenes containing it must remain local (Standard Asset EULA).
"""
from pathlib import Path
import bpy, math, json
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
ARCHER=ROOT/'assets/v8/licensed/archer/Animations/Blender/HumanF_ArcherAnimationsFREE_2.0.blend'
ROLL=ROOT/'assets/v8/combat/quaternius/UAL1_Standard.glb'

def _set_action(rig,action):
 rig.animation_data_create()
 for t in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(t)
 rig.animation_data.action=action
 if hasattr(rig.animation_data,'action_slot') and len(action.slots):rig.animation_data.action_slot=action.slots[0]

def _pose(scene,rig,frame):
 scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
 ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
 return {b.name:b.matrix.copy() for b in ev.pose.bones}

def _planar_strip(pose,root):
 delta=pose[root].translation.copy();delta.z=0
 for m in pose.values():m.translation-=delta
 return delta

def _apply(rig,pose):
 for b in rig.pose.bones:
  kw={} if b.parent is None else {'parent_matrix':pose[b.parent.name],'parent_matrix_local':b.parent.bone.matrix_local}
  b.matrix_basis=b.bone.convert_local_to_pose(pose[b.name],b.bone.matrix_local,invert=True,**kw)
 bpy.context.view_layer.update()

def _bounds(objects):
 deps=bpy.context.evaluated_depsgraph_get();lo=1e9;hi=-1e9
 for ob in objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(deps);me=ev.to_mesh()
  for v in me.vertices:
   z=(ev.matrix_world@v.co).z;lo=min(lo,z);hi=max(hi,z)
  ev.to_mesh_clear()
 return lo,hi

def _mapping():
 m={'B-root':'root','B-hips':'pelvis','B-spine':'spine_01','B-chest':'spine_03','B-neck':'neck_01','B-head':'Head'}
 for side in ['L','R']:
  s=side.lower()
  for t,u in [('shoulder','clavicle'),('upperArm','upperarm'),('forearm','lowerarm'),('hand','hand'),('thigh','thigh'),('shin','calf'),('foot','foot'),('toe','ball')]:m[f'B-{t}.{side}']=f'{u}_{s}'
  for t,u in [('indexFinger','index'),('middleFinger','middle'),('ringFinger','ring'),('pinky','pinky'),('thumb','thumb')]:
   for j in [1,2,3]:m[f'B-{t}{j:02}.{side}']=f'{u}_{j:02}_{s}'
 return m

def _retarget(source,target,pose,scale):
 """Transfer armature-space angular deltas; rebuild target limb offsets."""
 mapping=_mapping();out={};bones=target.data.bones
 for b in bones:
  rest=b.matrix_local;parent=b.parent
  if parent:
   offset=(parent.matrix_local.inverted()@rest).translation
   pos=out[parent.name]@offset
  else:pos=rest.translation.copy()
  srcname=mapping.get(b.name)
  if srcname in pose:
   src_rest=source.data.bones[srcname].matrix_local
   q=pose[srcname].to_quaternion()@src_rest.to_quaternion().inverted()@rest.to_quaternion()
   if b.name=='B-root':pos=Vector((0,0,pose[srcname].translation.z*scale))
   elif b.name=='B-hips':
    delta=pose[srcname].translation-src_rest.translation;pos=rest.translation+delta*scale
   out[b.name]=Matrix.Translation(pos)@q.to_matrix().to_4x4()
  elif parent:out[b.name]=out[parent.name]@(parent.matrix_local.inverted()@rest)
  else:out[b.name]=rest.copy()
 # Unused source control bones still receive a meaningful placement from the
 # deform chain. Props remain exact target-hand rest offsets.
 controls={'Hips':'B-hips','Spine':'B-spine','Chest':'B-chest','Neck':'B-neck','Head':'B-head','Jaw':'B-jaw','B-spineProxy':'B-spine'}
 for side in ['L','R']:
  for prefix,deform in [('Shoulder','shoulder'),('FK_UpperArm','upperArm'),('FK_Forearm','forearm'),('FK_Hand','hand'),('IK_UpperArm','upperArm'),('IK_Forearm','forearm'),('IK_Hand','hand'),('IKHand','hand'),('IKLeg','foot'),('Toe','toe'),('HandProp','handProp')]:controls[f'{prefix}.{side}']=f'B-{deform}.{side}'
 for name,driver in controls.items():
  if name in bones and driver in bones:out[name]=out[driver]@bones[driver].matrix_local.inverted()@bones[name].matrix_local
 return out

def sample_escape_motion(scene,target_rig):
 """Return roll18, run19 (1–19 inclusive), sheathe10 sampled poses + metadata."""
 before_objects=set(bpy.data.objects);before_actions=set(bpy.data.actions);saved_frame=scene.frame_current;saved_subframe=scene.frame_subframe
 report={'native_run_source_frames':[1,19],'native_run_source_fps':30,'native_run_cycle_seconds':.6,'native_sheathe_frames':[1,23],'target_bone_count':len(target_rig.data.bones),'roll_frames':[]}
 try:
  with bpy.data.libraries.load(str(ARCHER),link=False) as (src,dst):
   dst.objects=['Rig','HumanF_BodyMesh'];dst.actions=['HumanF@Run01_Forward [RM]','HumanF@SheatheBack01_L']
  for o in dst.objects:scene.collection.objects.link(o)
  native=next(o for o in dst.objects if o.type=='ARMATURE');body=next(o for o in dst.objects if o.type=='MESH');actions={a.name.split('.')[0]:a for a in dst.actions}
  # Preserve the original controllers at origin for evaluation, but never copy
  # their control action directly onto the already-baked production FK rig.
  native.matrix_world=Matrix.Identity(4)
  assert set(native.data.bones.keys())==set(target_rig.data.bones.keys()),'Archer skeleton mismatch'
  bind_error=max(abs(v) for b in native.data.bones for row in (b.matrix_local-target_rig.data.bones[b.name].matrix_local) for v in row)
  assert bind_error<1e-4,('Target rest mismatch',bind_error)
  report['target_bind_max_error']=bind_error
  _set_action(native,actions['HumanF@Run01_Forward [RM]']);run=[];root_positions=[]
  for f in range(1,20):
   pose=_pose(scene,native,f);root_positions.append(pose['B-root'].translation.copy());_planar_strip(pose,'B-root');run.append(pose)
  run_distance=(root_positions[-1]-root_positions[0]).length
  _set_action(native,actions['HumanF@SheatheBack01_L']);sheathe=[]
  for i in range(10):
   pose=_pose(scene,native,1+22*i/9);_planar_strip(pose,'B-root');sheathe.append(pose)
  # Fresh native rig becomes a disposable FK receiver for numerical skin QA.
  native.animation_data_clear()
  for b in native.pose.bones:
   for c in list(b.constraints):b.constraints.remove(c)
  prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROLL));imported=set(bpy.data.objects)-prior
  source=next(o for o in imported if o.type=='ARMATURE');source_meshes=[o for o in imported if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==source for m in o.modifiers)];action=next(a for a in bpy.data.actions if a not in before_actions and a.name.split('.')[0]=='Roll_RM');_set_action(source,action)
  start,end=map(float,action.frame_range);report['roll_source_frames']=[start,end];report['roll_source_fps']=scene.render.fps
  # Both sources face -Y and use metre-sized bodies. Match hip height, preserve
  # target limb lengths and correct only the skin's vertical clearance profile.
  scale=target_rig.data.bones['B-hips'].head_local.z/source.data.bones['pelvis'].head_local.z
  report['retarget_hip_scale']=scale;roll=[];source_root=[]
  for i in range(18):
   frame=start+(end-start)*i/17;srcpose=_pose(scene,source,frame);src_min,src_max=_bounds(source_meshes);source_root.append(srcpose['root'].translation.copy());_planar_strip(srcpose,'root');pose=_retarget(source,target_rig,srcpose,scale);_apply(native,pose);tgt_min,tgt_max=_bounds([body]);desired=max(0,src_min*scale);correction=desired-tgt_min
   for m in pose.values():m.translation.z+=correction
   _apply(native,pose);fixed_min,fixed_max=_bounds([body]);max_length_error=0
   for b in target_rig.data.bones:
    if b.parent and b.name!='B-hips' and b.name.startswith('B-') and b.name!='B-spineProxy':
     rest_length=(b.head_local-b.parent.head_local).length;posed_length=(pose[b.name].translation-pose[b.parent.name].translation).length;max_length_error=max(max_length_error,abs(rest_length-posed_length))
   report['roll_frames'].append({'index':i,'source_frame':frame,'source_skin_min_z':src_min,'target_before_min_z':tgt_min,'clearance_correction_z':correction,'target_final_min_z':fixed_min,'target_final_max_z':fixed_max,'max_deform_joint_offset_error':max_length_error});roll.append(pose)
  roll_distance=(source_root[-1]-source_root[0]).length;roll_progress=[(p-source_root[0]).length/roll_distance for p in source_root];report['roll_progress']=roll_progress;report['roll_distance']=roll_distance;report['run_cycle_distance']=run_distance;report['run_endpoint_pose_max_error']=max((run[0][n].translation-run[-1][n].translation).length for n in run[0]);report['map']=_mapping();report['max_adjacent_body_rotation_degrees']={n:max(math.degrees(2*math.acos(min(1,abs(roll[i-1][n].to_quaternion().dot(roll[i][n].to_quaternion()))))) for i in range(1,len(roll))) for n in ['B-hips','B-spine','B-chest','B-head']}
  out=ROOT/'renders/v9/escape-actor-motion-inspection.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2))
  return {'roll':roll,'run':run,'sheathe':sheathe,'roll_progress':roll_progress,'roll_distance':roll_distance,'run_cycle_distance':run_distance,'run_source_fps':30,'roll_source_fps':report['roll_source_fps'],'roll_duration':(end-start)/report['roll_source_fps'],'retarget_scale':scale,'report':report}
 finally:
  for o in list(bpy.data.objects):
   if o not in before_objects:bpy.data.objects.remove(o,do_unlink=True)
  for a in list(bpy.data.actions):
   if a not in before_actions and a.users==0:bpy.data.actions.remove(a)
  scene.frame_set(saved_frame,subframe=saved_subframe)

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'option-c-bow-bear.blend'),use_scripts=False)
 rig=bpy.data.objects.get('Rig')
 if rig is None:rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and 'B-hips' in o.data.bones)
 result=sample_escape_motion(bpy.context.scene,rig)
 print(json.dumps({k:v for k,v in result.items() if k not in ['roll','run','sheathe','report']},indent=2));print('POSE COUNTS',len(result['roll']),len(result['run']),len(result['sheathe']))
