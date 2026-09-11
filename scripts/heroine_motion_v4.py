"""Rocketbox FemaleAdult04 native locomotion, including authored start and stop.
The FBXs have matching names but different exported rest poses. Source absolute
pose-space matrices are converted into the target bind basis; copying channels
would corrupt the character. All body/leg/foot articulation is native animation.
Only a whole-character vertical floor correction is applied (no procedural IK).
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
BASE=Path(__file__).resolve().parents[1]
ASSETS=BASE/'assets/character/heroine_v4'
CLIPS={'start':'f_walk_start.max.fbx','walk':'f_walk_neutral_01.max.fbx','stop':'f_walk_stop.max.fbx','idle':'f_idle_breathe_01.max.fbx'}

def _import(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path),use_anim=True)
 return set(bpy.data.objects)-before

def _matrix_blend(a,b,t):
 at,aq,asc=a.decompose();bt,bq,bsc=b.decompose();return Matrix.LocRotScale(at.lerp(bt,t),aq.slerp(bq,t),asc.lerp(bsc,t))

def add_heroine_v4(start=(-3.8,-7.6,.14),end=(-3.8,-.8,.14),start_frame=37,stop_frame=217,film_end=576,cycles=4,report_path=None):
 film_fps=bpy.context.scene.render.fps
 objects=_import(ASSETS/'Female_Adult_04_facial.fbx');rig=next(o for o in objects if o.type=='ARMATURE');meshes=[o for o in objects if o.type=='MESH']
 for o in objects:
  if o.animation_data:o.animation_data_clear()
 for m in meshes:
  if m.data.shape_keys:
   if m.data.shape_keys.animation_data:m.data.shape_keys.animation_data_clear()
   for k in m.data.shape_keys.key_blocks:k.value=0
 # Facial skeleton remains in the target bind basis and inherits native head motion.
 facial={b.name for b in rig.data.bones if b.parent and (b.parent.name=='Bip01 Head' or b.parent.name.startswith(('Bip01 M','Bip01 LEye','Bip01 REye','Bip01 LMouth','Bip01 RMouth')))}
 facial|={b.name for b in rig.data.bones if any(a.name=='Bip01 Head' for a in b.parent_recursive)}
 rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
 sources={};source_objects=set();compatibility={}
 for key,filename in CLIPS.items():
  obs=_import(ASSETS/filename);source_objects|=obs;sr=next(o for o in obs if o.type=='ARMATURE');act=sr.animation_data.action;a,z=map(float,act.frame_range);source_fps=bpy.context.scene.render.fps
  bpy.context.scene.frame_set(int(a),subframe=a%1);initial=sr.matrix_world.translation.copy()
  bpy.context.scene.frame_set(int(z),subframe=z%1);final=sr.matrix_world.translation.copy()
  sources[key]={'rig':sr,'action':act,'range':(a,z),'initial':initial,'delta':final-initial,'duration':z-a,'fps':source_fps}
  compatibility[key]={'matched_bones':sum(n in sr.pose.bones for n in rest),'target_bones':len(rest),'max_exported_rest_translation_difference_cm':max((rest[b.name].translation-b.matrix_local.translation).length for b in sr.data.bones if b.name in rest),'source_frames':[a,z],'source_fps':source_fps,'source_duration_seconds':(z-a)/source_fps,'root_displacement_m':list(final-initial)}
  for o in obs:o.hide_render=True;o.hide_set(True)
 bpy.context.scene.render.fps=film_fps
 # Use complete native cycles; scaling character and its root path equally retains stride contact.
 native_distance=-(sources['start']['delta'].y+cycles*sources['walk']['delta'].y+sources['stop']['delta'].y)
 start,end=Vector(start),Vector(end);travel=end-start;travel.z=0;distance=travel.length;scale=distance/native_distance
 angle=math.atan2(travel.y,travel.x)-math.atan2(-1,0)
 root=bpy.data.objects.new('Heroine v4 • native root motion',None);bpy.context.scene.collection.objects.link(root)
 for o in objects:
  if o.parent not in objects:
   world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
 root.scale=(scale,)*3;root.rotation_euler.z=angle;root.location=start
 native_duration=sources['start']['duration']+cycles*sources['walk']['duration']+sources['stop']['duration'];rate=native_duration/(stop_frame-start_frame)
 sequence=[('start',0.0)];cursor=sources['start']['duration']
 for i in range(cycles):sequence.append(('walk',cursor));cursor+=sources['walk']['duration']
 sequence.append(('stop',cursor))
 offsets=[];offset=Vector()
 for key,at in sequence:offsets.append(offset.copy());offset+=sources[key]['delta']*Vector((1,1,0))
 final_offset=offset.copy()
 # Boot skin membership, evaluated after deformation, supplies floor clearance only.
 boot_indices={}
 for obj in meshes:
  groups={g.index:g.name for g in obj.vertex_groups};boot_indices[obj.name]={side:[] for side in ['L','R']}
  for v in obj.data.vertices:
   for side in ['L','R']:
    if sum(g.weight for g in v.groups if groups.get(g.group) in [f'Bip01 {side} Foot',f'Bip01 {side} Toe0'])>.60:boot_indices[obj.name][side].append(v.index)
 def native_sample(key,u):
  c=sources[key];sf=c['range'][0]+max(0,min(c['duration'],u));bpy.context.scene.frame_set(int(sf),subframe=sf%1);sr=c['rig'];pose={n:sr.pose.bones[n].matrix.copy() for n in rest if n in sr.pose.bones}
  return sr.matrix_world.copy(),pose
 def apply_pose(world,pose):
  rig.matrix_world=root.matrix_world@world
  for b in rig.pose.bones:
   if b.name in facial:b.matrix_basis=Matrix.Identity(4);continue
   if b.name not in pose:continue
   if b.parent:b.matrix_basis=rest[b.name].inverted()@rest[b.parent.name]@pose[b.parent.name].inverted()@pose[b.name]
   else:b.matrix_basis=rest[b.name].inverted()@pose[b.name]
  bpy.context.view_layer.update()
 metrics=[];last_segment=None;previous_pose=None
 for f in range(1,film_end+1):
  if f<start_frame:key='idle';u=((f-1)*sources['idle']['fps']/film_fps)%sources['idle']['duration'];path_offset=Vector();segment='initial idle'
  elif f>=stop_frame:key='idle';u=((f-stop_frame)*sources['idle']['fps']/film_fps)%sources['idle']['duration'];path_offset=final_offset;segment='final idle'
  else:
   timeline=(f-start_frame)*rate;j=max(i for i,(_,at) in enumerate(sequence) if at<=timeline);key,at=sequence[j];u=timeline-at;path_offset=offsets[j];segment=f'{key}:{j}'
  world,pose=native_sample(key,u);world.translation+=path_offset-Vector((sources[key]['initial'].x,sources[key]['initial'].y,0))
  # Adjacent native clips already match their locomotion phase. Blend only a small
  # orientation discrepancy over four film frames; root translation is untouched.
  if segment!=last_segment:
   transition_pose=previous_pose;transition_start=f;last_segment=segment
  if transition_pose and f-transition_start<4:
   t=(f-transition_start+1)/4;t=t*t*(3-2*t)
   pose={n:_matrix_blend(transition_pose[n],m,t) if n in transition_pose else m for n,m in pose.items()}
  previous_pose={n:m.copy() for n,m in pose.items()}
  bpy.context.scene.frame_set(f);root.location=start;bpy.context.view_layer.update();apply_pose(world,pose)
  feet={}
  for side in ['L','R']:
   zs=[]
   for obj in meshes:
    idx=boot_indices[obj.name][side]
    if not idx:continue
    eo=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();arr=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',arr);arr=arr.reshape(-1,3);mw=np.array(eo.matrix_world);v=arr[idx]@mw[:3,:3].T+mw[:3,3];zs.extend(v[:,2].tolist());eo.to_mesh_clear()
   feet[side]=min(zs) if zs else start.z
  correction=start.z-min(feet.values());root.location.z+=correction;bpy.context.view_layer.update()
  for ob in [root,rig]:
   ob.rotation_mode='QUATERNION' if ob==rig else 'XYZ'
   for prop in ['location','rotation_quaternion' if ob==rig else 'rotation_euler','scale']:ob.keyframe_insert(data_path=prop,frame=f)
  for b in rig.pose.bones:
   b.rotation_mode='QUATERNION'
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(data_path=prop,frame=f)
  metrics.append({'frame':f,'segment':segment,'root_xyz':list(rig.matrix_world.translation),'floor_correction_m':correction,'sole_clearance_m':{side:feet[side]+correction-start.z for side in feet}})
 # Detect each swing-to-support transition from the final deformed boot clearance.
 contacts=[]
 for side in ['L','R']:
  airborne=False;last=-99
  for m in metrics:
   if m['sole_clearance_m'][side]>.025:airborne=True
   if airborne and m['sole_clearance_m'][side]<.008 and m['frame']-last>7:
    last=m['frame'];contacts.append({'frame':last,'time_seconds':(last-1)/24,'foot':'left' if side=='L' else 'right'});airborne=False
 contacts.sort(key=lambda x:x['frame'])
 for ob in [root,rig]:
  for fc in ob.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 for o in source_objects:bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update();head=rig.matrix_world@rig.pose.bones['Bip01 Head'].head
 report={'model':'Microsoft Rocketbox FemaleAdult04','strategy':'native absolute pose-space transfer with authored root motion, start/walk/stop/idle; whole-character floor correction','start_frame':start_frame,'stop_frame':stop_frame,'cycles':cycles,'uniform_character_and_motion_scale':scale,'native_distance_m':native_distance,'delivered_distance_m':distance,'source_frames_per_film_frame':rate,'film_fps':film_fps,'delivered_motion_seconds':(stop_frame-start_frame)/film_fps,'source_compatibility':compatibility,'foot_contacts':contacts,'frames':metrics}
 if report_path:
  p=Path(report_path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2))
 return {'objects':objects,'meshes':meshes,'root':root,'rig':rig,'face_target':tuple(head),'foot_contacts':contacts,'motion_report':report,'source':str(ASSETS/'Female_Adult_04_facial.fbx')}
