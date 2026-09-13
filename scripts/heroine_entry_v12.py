"""Native Rocketbox run-stop, doorway check and unhurried walk into the room.

All original rig motion from frame225 onward is preserved. The accepted model,
scale, original later wonder expression and index-finger reach stay intact.
"""
from pathlib import Path
import math,sys
import bpy
import numpy as np
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from heroine_motion_v4 import _import,_matrix_blend


def smooth(a,b,f):
 t=max(0,min(1,(f-a)/(b-a)));return t*t*(3-2*t)


def add_room_entry_v12(scene=None,rig=None):
 s=scene or bpy.context.scene;rig=rig or bpy.data.objects['Bip01'];parent=rig.parent
 original=rig.animation_data.action;fps=s.render.fps;saved=s.frame_current
 if rig.get('v12_entry'):raise ValueError('Build this entry once from V11')
 bones=rig.pose.bones;rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
 face={b.name for b in rig.data.bones if any(p.name=='Bip01 Head' for p in b.parent_recursive)}
 body=[b.name for b in bones if b.name not in face];modified=body+['Bip01 LEye','Bip01 REye']
 originals={}
 for f in range(37,226):
  s.frame_set(f);originals[f]={'world':rig.matrix_world.copy(),'basis':{n:bones[n].matrix_basis.copy() for n in modified}}
 meshes=[o for o in parent.children_recursive if o.type=='MESH'];boot={}
 for ob in meshes:
  names={g.index:g.name for g in ob.vertex_groups};boot[ob.name]={}
  for side in ['L','R']:boot[ob.name][side]=[v.index for v in ob.data.vertices if sum(g.weight for g in v.groups if names.get(g.group) in [f'Bip01 {side} Foot',f'Bip01 {side} Toe0'])>.6]
 before={kind:set(getattr(bpy.data,kind)) for kind in ['objects','actions','meshes','armatures','materials','images']}
 sources={};imported=set();paths={'run_stop':ROOT/'assets/character/heroine_v12/f_run_stop.max.fbx'}
 for name,file in [('start','f_walk_start.max.fbx'),('walk','f_walk_neutral_01.max.fbx'),('stop','f_walk_stop.max.fbx'),('idle','f_idle_breathe_01.max.fbx')]:paths[name]=ROOT/'assets/character/heroine_v4'/file
 for key,path in paths.items():
  objects=_import(path);imported|=objects;sr=next(o for o in objects if o.type=='ARMATURE');a,z=map(float,sr.animation_data.action.frame_range)
  s.frame_set(int(a));first=sr.matrix_world.translation.copy();s.frame_set(int(z));last=sr.matrix_world.translation.copy()
  sources[key]={'rig':sr,'a':a,'duration':z-a,'first':first,'delta':last-first,'file':str(path.relative_to(ROOT))}
  for ob in objects:ob.hide_render=True;ob.hide_set(True)
 s.render.fps=fps
 scale=float(parent.scale.x);travel=sources['run_stop']['delta']+sources['start']['delta']+2*sources['walk']['delta']+sources['stop']['delta'];travel.z=0
 yaw=Matrix.Rotation(math.pi,4,'Z');scale_matrix=Matrix.Diagonal(Vector((scale,scale,scale,1)))
 endpoint=Vector((-3.7701607,-.8,.14));start=endpoint-yaw.to_3x3()@(travel*scale);start.z=.14
 action=original.copy();action.name='V12 | Native run entry, doorway check, then walk';rig.animation_data.action=action
 sequence=[('start',0),('walk',28),('walk',64),('stop',100)];offsets=[sources['run_stop']['delta'].copy()]
 for i in range(1,4):offsets.append(offsets[-1]+sources[sequence[i-1][0]]['delta'])
 rate=30/fps;previous_pose=None;last_segment=None;metrics=[];previous_q={}
 def sample(key,u):
  source=sources[key];time=source['a']+min(max(u,0),source['duration']);s.frame_set(int(time),subframe=time%1);sr=source['rig']
  return sr.matrix_world.copy(),{n:sr.pose.bones[n].matrix.copy() for n in body}
 def foot_geometry():
  result={side:[] for side in ['L','R']};deps=bpy.context.evaluated_depsgraph_get()
  for ob in meshes:
   ev=ob.evaluated_get(deps);mesh=ev.to_mesh();array=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',array);array=array.reshape(-1,3);matrix=np.asarray(ev.matrix_world)
   for side in result:
    indices=boot[ob.name][side]
    if indices:result[side].extend((array[indices]@matrix[:3,:3].T+matrix[:3,3]).tolist())
   ev.to_mesh_clear()
  return {side:np.asarray(points) for side,points in result.items()}
 for f in range(37,225):
  if f<77:key='run_stop';u=(f-37)*rate;offset=Vector();segment='native run and deceleration'
  elif f<87:key='idle';u=(f-77)*rate;offset=sources['run_stop']['delta'].copy();segment='check doorway'
  elif f<210:
   timeline=(f-87)*rate;i=max(i for i,(_,at) in enumerate(sequence) if at<=timeline);key,at=sequence[i];u=timeline-at;offset=offsets[i].copy();segment=f'native {key} {i}'
  else:key='idle';u=(f-210)*rate;offset=travel.copy();segment='settle to original idle'
  world,pose=sample(key,u)
  src=sources[key];progress=offset+world.translation-src['first'];progress.z=0
  desired_world=scale_matrix@yaw@world;desired_world.translation=start+yaw.to_3x3()@(progress*scale)+Vector((0,0,scale*world.translation.z))
  if segment!=last_segment:blend_from=previous_pose;transition=f;last_segment=segment
  if blend_from is not None and f-transition<4:pose={n:_matrix_blend(blend_from[n],m,smooth(transition-1,transition+3,f)) for n,m in pose.items()}
  previous_pose={n:m.copy() for n,m in pose.items()}
  # Airborne phases in the running source are retained; the subsequent walk
  # uses the established deformed-boot floor correction from the accepted gait.
  sr=src['rig'];flight=0.
  if key=='run_stop' and u<25:
   heel=min((sr.matrix_world@sr.pose.bones['Bip01 '+side+' Foot'].head).z for side in ['L','R'])
   toe=min((sr.matrix_world@sr.pose.bones['Bip01 '+side+' Toe0'].head).z for side in ['L','R'])
   flight=max(0,min(heel-.105,toe-.015))*scale
  s.frame_set(f);rig.matrix_world=desired_world
  for n,m in pose.items():
   b=bones[n]
   b.matrix_basis=rest[n].inverted()@rest[b.parent.name]@pose[b.parent.name].inverted()@m if b.parent else rest[n].inverted()@m
  for n in ['Bip01 LEye','Bip01 REye']:bones[n].matrix_basis=originals[f]['basis'][n]
  bpy.context.view_layer.update()
  glance=smooth(56,77,f)*(1-smooth(88,108,f))
  # Turn toward the actual entrance behind her over the right shoulder. The
  # rotation is distributed through three torso joints, neck, head and eyes.
  for n,angle in [('Bip01 Spine',-12),('Bip01 Spine1',-16),('Bip01 Spine2',-18),('Bip01 Neck',-18),('Bip01 Head',-76),('Bip01 LEye',-22),('Bip01 REye',-22)]:
   if not glance:continue
   b=bones[n];position,rotation,size=(rig.matrix_world@b.matrix).decompose();location=b.location.copy();sc=b.scale.copy()
   b.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(position,Quaternion((0,0,1),math.radians(angle)*glance)@rotation,size)
   b.location=location;b.scale=sc;bpy.context.view_layer.update()
  feet=foot_geometry();lowest=min(v[:,2].min() for v in feet.values());correction=.14+flight-lowest
  mw=rig.matrix_world.copy();mw.translation.z+=correction;rig.matrix_world=mw;bpy.context.view_layer.update()
  if f>=210:
   weight=smooth(210,225,f);rig.matrix_world=_matrix_blend(rig.matrix_world,originals[f]['world'],weight)
   for n in modified:bones[n].matrix_basis=_matrix_blend(bones[n].matrix_basis,originals[f]['basis'][n],weight)
   bpy.context.view_layer.update()
  for ob,name in [(rig,'__rig__')]+[(bones[n],n) for n in modified]:
   ob.rotation_mode='QUATERNION'
   if name in previous_q and ob.rotation_quaternion.dot(previous_q[name])<0:ob.rotation_quaternion.negate()
   previous_q[name]=ob.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:ob.keyframe_insert(prop,frame=f,group='' if ob==rig else name)
  finalfeet=foot_geometry();headpos=rig.matrix_world@bones['Bip01 Head'].head
  metrics.append({'frame':f,'segment':segment,'root':list(rig.matrix_world.translation),'glance_weight':glance,'head':list(headpos),'door_target':[-3.8,-5.8,1.5],'native_airborne_clearance_m':flight,'minimum_boot_clearance_m':float(min(v[:,2].min() for v in finalfeet.values())-.14)})
 for curve in action.fcurves:
  for key in curve.keyframe_points:
   if 37<=key.co.x<225:key.interpolation='LINEAR'
 for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
 for kind in ['actions','meshes','armatures','materials','images']:
  for block in list(getattr(bpy.data,kind)):
   if block not in before[kind] and block!=action and block.users==0:getattr(bpy.data,kind).remove(block)
 rig['v12_entry']='Native running deceleration, over-shoulder door check, native start/two walks/stop; original from225'
 s.render.fps=fps;s.frame_set(saved)
 return {'modified_frame_range':[37,224],'preserved_frame_range':[225,576],'preserved_from_frame':225,'source_action':original.name,'action':action.name,'character_scale_unchanged':scale,'native_run':'f_run_stop.max.fbx','native_run_source_fps':30,'native_frames_per_film_frame':rate,'start_ground':list(start),'endpoint_ground':list(endpoint),'native_total_travel_m':float((travel*scale).length),'door_check_frames':[56,108],'door_check_peak':[77,88],'gaze_strategy':'Right shoulder: distributed torso46deg + neck18 + head76 + eyes22, directed back toward entrance','face_morph_animation_unchanged':True,'single_later_wonder_preserved':True,'sources':{k:{'file':v['file'],'duration_frames':v['duration'],'root_delta':list(v['delta'])} for k,v in sources.items()},'frames':metrics,'production_render_performed':False}
