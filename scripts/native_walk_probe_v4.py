"""Isolated V4 probe: preserve the complete imported Meshy Walking_Woman pose.
No production scene is changed. Measures native sole trajectories, estimates path
speed from stance feet, and renders two cycles without procedural leg overrides.
"""
import bpy, math, json, statistics
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'previews/v4/native-walk-probe'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(BASE/'assets/character/heroine_v3/walking-woman.glb'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
for o in bpy.data.objects:
 if o.type=='MESH' and o not in meshes:o.hide_render=True
act=rig.animation_data.action
if not act:
 act=next(st.action for tr in rig.animation_data.nla_tracks for st in tr.strips)
 rig.animation_data.action=act
 for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.data.pose_position='REST';bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
height=max(p.z for p in pts)-min(p.z for p in pts);factor=1.72/height
fwd=sum((rig.matrix_world.to_3x3()@(rig.data.bones[side+'ToeBase'].head_local-rig.data.bones[side+'Foot'].head_local) for side in ['Left','Right']),Vector());fwd.z=0;fwd.normalize()
root=bpy.data.objects.new('Native locomotion root',None);s.collection.objects.link(root)
for o in [rig]+[o for o in meshes if o.parent is None]:
 w=o.matrix_world.copy();o.parent=root;o.matrix_world=w
root.scale=(factor,)*3
rig.data.pose_position='POSE'
# Identify each boot by native skin weights; inspect deformed geometry, not targets.
foot_indices={}
for o in meshes:
 inds={side:[] for side in ['Left','Right']}
 vg={g.index:g.name for g in o.vertex_groups}
 for v in o.data.vertices:
  weights={side:sum(g.weight for g in v.groups if vg.get(g.group) in (side+'Foot',side+'ToeBase')) for side in inds}
  for side,w in weights.items():
   if w>.65:inds[side].append(v.index)
 foot_indices[o.name]=inds
cycle=28;start,end=map(float,act.frame_range);samples=[];measures=[]
for i in range(cycle):
 sf=start+(end-start)*i/cycle;s.frame_set(int(sf),subframe=sf%1)
 samples.append({b.name:b.matrix_basis.copy() for b in rig.pose.bones})
 row={'sample':i,'source_frame':sf,'feet':{}}
 for side in ['Left','Right']:
  foot=rig.matrix_world@rig.pose.bones[side+'Foot'].head
  zs=[]
  for o in meshes:
   eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3)
   selected=a[foot_indices[o.name][side]];mw=np.array(eo.matrix_world);world=selected@mw[:3,:3].T+mw[:3,3]
   zs.extend(world[:,2].tolist());eo.to_mesh_clear()
  row['feet'][side]={'ankle_xyz':list(foot),'forward_position':foot.dot(fwd),'sole_z':min(zs)}
 measures.append(row)
# Estimate forward velocity from each foot's lowest 40% of native poses.
velocities=[]
for side in ['Left','Right']:
 threshold=sorted(r['feet'][side]['sole_z'] for r in measures)[int(cycle*.4)]
 for i,r in enumerate(measures):
  if r['feet'][side]['sole_z']<=threshold:
   prev=measures[(i-1)%cycle]['feet'][side]['forward_position'];nxt=measures[(i+1)%cycle]['feet'][side]['forward_position']
   v=-(nxt-prev)*12
   if v>.03:velocities.append(v)
speed=statistics.median(velocities)
floor_offset=-min(min(r['feet'][side]['sole_z'] for side in ['Left','Right']) for r in measures)
rig.animation_data_clear()
for f in range(1,cycle*2+1):
 s.frame_set(f)
 for b in rig.pose.bones:
  b.matrix_basis=samples[(f-1)%cycle][b.name];b.rotation_mode='QUATERNION'
  for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(data_path=prop,frame=f)
 root.location=fwd*(speed*(f-1)/24)+Vector((0,0,floor_offset));root.keyframe_insert(data_path='location',frame=f)
for o in [root,rig]:
 for fc in o.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
# Neutral studio with fixed grid makes foot travel visible.
def mat(name,c,rough=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=rough;return m
floor=mat('Neutral grey',(.1,.115,.135));line=mat('Floor grid',(.19,.22,.25))
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(floor)
for axis in range(2):
 for i in range(-6,7):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(i*.5 if axis==0 else 0,0 if axis==0 else i*.5,.0005));o=bpy.context.object;o.scale=(.006,6,.0005) if axis==0 else (6,.006,.0005);o.data.materials.append(line)
mid=fwd*(speed*(cycle*2-1)/48)
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=mid+Vector((3,-4.6,2.1)));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=3.7;point(cam,mid+Vector((0,0,.87)));s.camera=cam
for name,pos,power,size in [('Key',(-3,-4,5),650,4),('Fill',(4,-2,3),300,3),('Rim',(0,4,4),700,3)]:
 bpy.ops.object.light_add(type='AREA',location=mid+Vector(pos));o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,mid+Vector((0,0,1)))
s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.13,.16,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.metalrt='OFF';p.kernel_optimization_level='OFF';p.get_devices()
for d in p.devices:d.use=d.type=='METAL'
s.cycles.device='GPU';s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.film_transparent=False;s.frame_start=1;s.frame_end=cycle*2
report={'source_action':act.name,'source_frame_range':[start,end],'source_seconds':(end-start)/24,'film_cycle_frames':cycle,'film_cycle_seconds':cycle/24,'measured_speed_m_s':speed,'distance_per_full_cycle_m':speed*cycle/24,'scale_to_1_72m':factor,'floor_offset_m':floor_offset,'stance_velocity_candidates_m_s':velocities,'native_samples':measures,'notes':['Every native pelvis, leg, foot and toe pose is retained.','No IK, procedural bobbing or facial alterations.','Travel speed estimated from native low-foot backward movement.','This is a diagnostic mesh/proxy, not final full-resolution heroine.']}
(OUT/'measurements.json').write_text(json.dumps(report,indent=2))
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'native-walk-probe.blend'),compress=True)
for f in range(1,cycle*2+1):
 s.frame_set(f);s.render.filepath=str(OUT/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('NATIVE_WALK_PROBE_COMPLETE',json.dumps({k:v for k,v in report.items() if k not in ['native_samples','stance_velocity_candidates_m_s']}))
