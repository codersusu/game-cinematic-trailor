"""Native second approach, then retimed V6 right-hand reach (Blender CPU).

Preserves delivered V6 through frame344, existing mesh/materials/facial morphs,
character scale and the original entrance. Native start + half-cycle + mirrored
stop lasts3.3seconds and advances2.0032m; idle never supplies planar translation.
"""
from pathlib import Path
import math,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import numpy as np
from mathutils import Vector,Matrix,Quaternion
from heroine_motion_v4 import _import,_matrix_blend,ASSETS,CLIPS

ROOT=Path(__file__).resolve().parents[1]

def smooth(a,b,f):
 t=max(0.,min(1.,(f-a)/(b-a)));return t*t*(3-2*t)

def mirror_name(name):
 if ' L ' in name:return name.replace(' L ',' R ')
 if ' R ' in name:return name.replace(' R ',' L ')
 return name

def add_approach_v7(scene=None,rig=None,endpoint=(-2.9,1.0,.14)):
 scene=scene or bpy.context.scene;rig=rig or bpy.data.objects.get('Bip01')
 if rig is None or not rig.animation_data:raise ValueError('Delivered V6 Bip01 performer required')
 if rig.get('v7_approach'):raise ValueError('Approach already applied; build from V6')
 root=rig.parent;original=rig.animation_data.action;film_fps=scene.render.fps;previous_frame=scene.frame_current
 bones=rig.pose.bones;rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
 face={b.name for b in rig.data.bones if any(a.name=='Bip01 Head' for a in b.parent_recursive)}
 body=[b.name for b in bones if b.name not in face]
 reach_names=['Bip01 Spine1','Bip01 Spine2','Bip01 R Clavicle','Bip01 R UpperArm','Bip01 R Forearm','Bip01 R Hand']+[b.name for b in bones if b.name.startswith('Bip01 R Finger')]
 scene.frame_set(344);bpy.context.view_layer.update()
 initial_world=rig.matrix_world.copy();initial_pose={n:bones[n].matrix.copy() for n in body}
 scale=float(root.scale.x);start=initial_world.translation.copy();start.z=float(endpoint[2])
 meshes=[o for o in root.children_recursive if o.type=='MESH'];boot_indices={}
 for obj in meshes:
  groups={g.index:g.name for g in obj.vertex_groups};boot_indices[obj.name]={side:[] for side in ['L','R']}
  for v in obj.data.vertices:
   for side in ['L','R']:
    if sum(g.weight for g in v.groups if groups.get(g.group) in [f'Bip01 {side} Foot',f'Bip01 {side} Toe0'])>.60:boot_indices[obj.name][side].append(v.index)
 before={kind:set(getattr(bpy.data,kind)) for kind in ['objects','actions','meshes','armatures','materials','images']}
 # The target bind frame provides the side-axis correction for geometric pose
 # mirroring. Reflection + side swap + reflected bind axes retains proper
 # rotations; merely swapping L/R animation channels would corrupt this FBX rig.
 bind_objects=_import(ASSETS/'Female_Adult_04_facial.fbx');bind=next(o for o in bind_objects if o.type=='ARMATURE')
 reflect=Matrix.Diagonal(Vector((-1,1,1,1)))
 bind_rot={b.name:(bind.matrix_world@b.matrix_local).to_quaternion().to_matrix().to_4x4() for b in bind.data.bones}
 side_correction={n:bind_rot[mirror_name(n)].inverted()@reflect@bind_rot[n] for n in body}
 sources={};imported=set(bind_objects)
 for key in ['start','walk','stop','idle']:
  obs=_import(ASSETS/CLIPS[key]);imported|=obs;sr=next(o for o in obs if o.type=='ARMATURE');act=sr.animation_data.action;a,z=map(float,act.frame_range)
  scene.frame_set(int(a));first=sr.matrix_world.translation.copy();scene.frame_set(int(z));last=sr.matrix_world.translation.copy()
  sources[key]={'rig':sr,'a':a,'z':z,'first':first,'delta':last-first}
  for o in obs:o.hide_render=True;o.hide_set(True)
 for o in bind_objects:o.hide_render=True;o.hide_set(True)
 scene.render.fps=film_fps
 # Source V5 and reviewed V6 bone rotations isolate the reach from native idle.
 # Appending just the action preserves all current rendered geometry and look.
 with bpy.data.libraries.load(str(ROOT/'observatory-v5.blend'),link=False) as (_,loaded):loaded.actions=['Bip01Action']
 baseline=loaded.actions[0]
 if baseline is None:raise ValueError('Missing published V5 native action')
 def q_at(action,name,f):
  path=bones[name].path_from_id('rotation_quaternion');fc=[action.fcurves.find(path,index=i) for i in range(4)]
  return Quaternion([curve.evaluate(f) for curve in fc]).normalized()
 deltas={}
 for f in range(345,577):
  source_frame=360 if f<=418 else (360+(f-418)*88/60 if f<=478 else 448+(f-478)*.5)
  deltas[f]={n:q_at(baseline,n,source_frame).inverted()@q_at(original,n,source_frame) for n in reach_names}
 action=original.copy();action.name='V7 | Native second approach and nearby reach';rig.animation_data.action=action
 # End the walk on the opposite foot: half of the 36-frame cycle needs a
 # mirrored native stop. The stop displacement is mirrored by the same rule.
 walk=sources['walk'];scene.frame_set(19);half=walk['rig'].matrix_world.translation-walk['first']
 stop_delta=sources['stop']['delta'].copy();stop_delta.x*=-1
 native_end=sources['start']['delta']+half+stop_delta;native_end.z=0
 desired=Vector(endpoint)-start;desired.z=0
 heading=math.atan2(desired.y,desired.x)-math.atan2(native_end.y,native_end.x)
 course=Matrix.Rotation(heading,4,'Z')
 actual_end=start+course.to_3x3()@(native_end*scale)
 if abs((actual_end-start).length-desired.length)>.08:raise ValueError('Endpoint differs from native2.003m stride; adjust endpoint, not character scale')
 start_offset=sources['start']['delta'].copy();start_offset.z=0
 half_offset=start_offset+half;half_offset.z=0
 rate=99/79
 metrics=[];last_segment=None;previous_pose=None;transition_pose=None
 def sample(key,u,mirror=False):
  src=sources[key];time=src['a']+min(max(u,0),src['z']-src['a']);scene.frame_set(int(time),subframe=time%1)
  sr=src['rig'];world=sr.matrix_world.copy();pose={n:sr.pose.bones[n].matrix.copy() for n in body}
  displacement=world.translation-src['first'];displacement.z=0
  if mirror:
   bone_world={n:world@pose[n] for n in body};world.translation.x*=-1;displacement.x*=-1
   pose={n:world.inverted()@reflect@bone_world[mirror_name(n)]@side_correction[n] for n in body}
  return world,pose,displacement
 def foot_geometry():
  info={side:{'z':float('inf'),'points':[]} for side in ['L','R']}
  deps=bpy.context.evaluated_depsgraph_get()
  for obj in meshes:
   ev=obj.evaluated_get(deps);me=ev.to_mesh();arr=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',arr);arr=arr.reshape(-1,3);mw=np.asarray(ev.matrix_world)
   for side in ['L','R']:
    idx=boot_indices[obj.name][side]
    if idx:
     points=arr[idx]@mw[:3,:3].T+mw[:3,3];info[side]['z']=min(info[side]['z'],float(points[:,2].min()));info[side]['points'].extend(points.tolist())
   ev.to_mesh_clear()
  return info
 for f in range(345,577):
  timeline=(f-345)*rate
  if timeline<28:key='start';u=timeline;offset=Vector();mirrored=False
  elif timeline<46:key='walk';u=timeline-28;offset=start_offset;mirrored=False
  elif timeline<99:key='stop';u=timeline-46;offset=half_offset;mirrored=True
  else:key='idle';u=((f-424)*30/film_fps)%80;offset=native_end;mirrored=True
  world,pose,disp=sample(key,u,mirrored)
  if key!=last_segment:transition_pose=previous_pose;transition_start=f;last_segment=key
  if transition_pose and f-transition_start<4:
   t=smooth(transition_start-1,transition_start+3,f)
   pose={n:_matrix_blend(transition_pose[n],m,t) for n,m in pose.items()}
  previous_pose={n:m.copy() for n,m in pose.items()}
  scene.frame_set(f)
  turn=math.pi+(heading-math.pi)*smooth(345,365,f)
  rotation=Matrix.Rotation(turn,4,'Z')
  desired_world=Matrix.Diagonal(Vector((scale,scale,scale,1)))@rotation@world
  progress=offset+disp;progress.z=0
  position=start+course.to_3x3()@(progress*scale);position.z=start.z+scale*world.translation.z
  desired_world.translation=position
  initial_blend=smooth(344,352,f)
  if f<352:
   desired_world=_matrix_blend(initial_world,desired_world,initial_blend)
   pose={n:_matrix_blend(initial_pose[n],p,initial_blend) for n,p in pose.items()}
  rig.matrix_world=desired_world
  for n in body:
   b=bones[n]
   if b.parent:b.matrix_basis=rest[n].inverted()@rest[b.parent.name]@pose[b.parent.name].inverted()@pose[n]
   else:b.matrix_basis=rest[n].inverted()@pose[n]
  bpy.context.view_layer.update()
  # Keep her attention on the apparatus as the body turns. Facial shape keys
  # remain completely unchanged; this rotates the native head bone only.
  head=bones['Bip01 Head'];head_world=rig.matrix_world@head.matrix;target=Vector((0,2,3.7))-head_world.translation
  body_yaw=turn-math.pi;look_yaw=-math.atan2(target.x,target.y)-body_yaw
  gaze_weight=smooth(344,357,f)
  q=Quaternion((0,0,1),look_yaw*gaze_weight)
  right=Quaternion((0,0,1),body_yaw+look_yaw)@Vector((1,0,0))
  q=Quaternion(right,math.radians(17)*gaze_weight)@q
  loc,rot,sc=head_world.decompose();head.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(loc,q@rot,sc)
  # Reuse reviewed V6 reach deltas as an upper-body layer during final settling.
  for n in reach_names:bones[n].rotation_quaternion=bones[n].rotation_quaternion@deltas[f][n]
  bpy.context.view_layer.update()
  # The reviewed V6 delta was authored farther from the apparatus. Swing the
  # entire bent arm about its shoulder toward the nearer, steeper star ray.
  # Rotating only the upper-arm joint preserves arm length, elbow bend and the
  # relative wrist/palm pose; lower-body/head/facial channels are untouched.
  align=smooth(418,478,f)
  if align>0:
   upper=bones['Bip01 R UpperArm'];shoulder=rig.matrix_world@upper.head
   wrist=rig.matrix_world@bones['Bip01 R Hand'].head
   present=wrist-shoulder;toward=Vector((0,2,3.7))-shoulder
   if present.length>1e-6:
    swing=Quaternion().slerp(present.normalized().rotation_difference(toward.normalized()),align)
    location=upper.location.copy();bone_scale=upper.scale.copy()
    position,rotation,size=(rig.matrix_world@upper.matrix).decompose()
    upper.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(position,swing@rotation,size)
    upper.location=location;upper.scale=bone_scale
    bpy.context.view_layer.update()
  feet=foot_geometry();floor_shift=start.z-min(feet[s]['z'] for s in feet)
  adjusted=rig.matrix_world.copy();adjusted.translation.z+=floor_shift;rig.matrix_world=adjusted;bpy.context.view_layer.update()
  for prop in ['location','rotation_quaternion','scale']:rig.keyframe_insert(prop,frame=f)
  for n in body:
   b=bones[n];b.rotation_mode='QUATERNION'
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f,group=n)
  foot_rows={}
  for side,info in feet.items():
   points=np.array(info['points']);points[:,2]+=floor_shift
   foot_rows[side]={'sole_clearance_m':float(points[:,2].min()-start.z),
                    'center':list((points.min(axis=0)+points.max(axis=0))/2),
                    'min_platform_radius_m':float(np.sqrt(points[:,0]**2+(points[:,1]-2)**2).min())}
  metrics.append({'frame':f,'segment':key,'source_frame':float(sources[key]['a']+u),'mirrored':mirrored,
                  'rig_xyz':list(rig.matrix_world.translation),'feet':foot_rows,
                  'wrist':list(rig.matrix_world@bones['Bip01 R Hand'].head),
                  'shoulder':list(rig.matrix_world@bones['Bip01 R UpperArm'].head),
                  'elbow':list(rig.matrix_world@bones['Bip01 R Forearm'].head),
                  'reach_alignment_degrees':math.degrees(((rig.matrix_world@bones['Bip01 R Hand'].head)-(rig.matrix_world@bones['Bip01 R UpperArm'].head)).angle(Vector((0,2,3.7))-(rig.matrix_world@bones['Bip01 R UpperArm'].head)))})
 for fc in action.fcurves:
  for k in fc.keyframe_points:
   if k.co.x>=345:k.interpolation='LINEAR'
 contacts=[]
 for side in ['L','R']:
  airborne=False;last=-99
  for m in metrics:
   if m['frame']>430:break
   clearance=m['feet'][side]['sole_clearance_m']
   if clearance>.025:airborne=True
   if airborne and clearance<.008 and m['frame']-last>7:
    last=m['frame'];contacts.append({'frame':last,'foot':'left' if side=='L' else 'right','time_seconds':(last-1)/24});airborne=False
 contacts.sort(key=lambda x:x['frame'])
 for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
 for a in list(bpy.data.actions):
  if a not in before['actions'] and a!=action:bpy.data.actions.remove(a)
 for kind in ['meshes','armatures','materials','images']:
  for block in list(getattr(bpy.data,kind)):
   if block not in before[kind] and block.users==0:getattr(bpy.data,kind).remove(block)
 rig['v7_approach']='Native start + half walk + mirrored stop, then nearby reach'
 scene.render.fps=film_fps;scene.frame_set(previous_frame)
 return {'strategy':'Native Rocketbox second approach at unchanged character scale; half-cycle with mirrored stop; retimed reviewed V6 reach',
         'start_frame':345,'stop_frame':424,'reach_settle_start':418,'reach_peak':478,'reach_hold_end':576,'arm_alignment':'Shoulder-centered swing toward actual galaxy ray, blended418–478; no arm extension',
         'preserved_frames':[1,344],'character_scale':scale,'native_fps':30,'source_frames_per_film_frame':rate,
         'native_sequence_frames':[28,18,53],'requested_endpoint':list(endpoint),'actual_endpoint_ground':list(actual_end),
         'native_travel_distance_m':(actual_end-start).length,'floor_z':start.z,'platform_center':[0,2],'platform_radius_m':2.72,
         'minimum_boot_platform_radius_m':min(row['feet'][s]['min_platform_radius_m'] for row in metrics for s in ['L','R']),
         'foot_contacts':contacts,'frames':metrics,'facial_morphs_modified':False,'temporary_assets_removed':True}


if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'observatory-v6.blend'),use_scripts=False)
 report=add_approach_v7()
 print('APPROACH_PROBE',json.dumps({k:v for k,v in report.items() if k!='frames'}))
 for f in [345,352,367,381,400,418,424,440,478,576]:print(json.dumps(next(r for r in report['frames'] if r['frame']==f)))
