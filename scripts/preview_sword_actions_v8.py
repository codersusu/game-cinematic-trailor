"""CPU-only source-man­nequin action proof; no retargeting or production rendering."""
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'previews/v8/combat/sword-combo-frames';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/v8/combat/quaternius/UAL2_Standard.glb'))
sc=bpy.context.scene;sc.render.fps=24
rig=next(o for o in sc.objects if o.type=='ARMATURE');rig.animation_data_create()
for t in rig.animation_data.nla_tracks:t.mute=True
act=next(a for a in bpy.data.actions if 'Sword_Regular_Combo' in a.name);rig.animation_data.action=act
if hasattr(act,'slots') and len(act.slots):rig.animation_data.action_slot=act.slots[0]
sc.frame_set(1);bpy.context.view_layer.update();print('action',act.name,list(act.frame_range),'bones',len(rig.data.bones))
mesh=[o for o in sc.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(c) for o in mesh for c in o.bound_box];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));center=(lo+hi)/2;span=max(hi-lo)
with bpy.data.libraries.load(str(ROOT/'assets/v8/combat/uplon/uplon.blend'),link=False) as (src,dst):dst.objects=['Sword']
sword=dst.objects[0];sc.collection.objects.link(sword)
sword.data=sword.data.copy()
for v in sword.data.vertices:
 x,y,z=v.co;v.co=(-.25*(x-1.8),.25*z,.25*y)
sword.location=(0,0,0);sword.rotation_euler=(0,0,0);sword.scale=(1,1,1)
m=bpy.data.materials.new('Uplon PBR preview');m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF');lk=m.node_tree.links
for mapname,socket in [('BaseColor','Base Color'),('Metallic','Metallic'),('Roughness','Roughness')]:
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/v8/combat/uplon/textures'/f'{mapname}.png'))
 if mapname!='BaseColor':t.image.colorspace_settings.name='Non-Color'
 lk.new(t.outputs['Color'],bs.inputs[socket])
t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/v8/combat/uplon/textures/Normal.png'));t.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');lk.new(t.outputs['Color'],nm.inputs['Color']);lk.new(nm.outputs['Normal'],bs.inputs['Normal'])
sword.data.materials.clear();sword.data.materials.append(m)
for o in mesh:
 m=bpy.data.materials.new('source mannequin');m.diffuse_color=(.2,.36,.45,1);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Roughness'].default_value=.5;o.data.materials.clear();o.data.materials.append(m)
bpy.ops.object.camera_add(location=center+Vector((1.4,-2.3,.7))*span);cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.2;sc.camera=cam
for off,power in [((1,-1,1.8),100),((-1,-.5,1),50),((0,1,1.2),150)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(off)*span);o=bpy.context.object;o.data.energy=power*span*span;o.data.size=span*1.5;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
sc.world=bpy.data.worlds.new('studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.05,.065,.085,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=4;sc.cycles.use_denoising=True;sc.render.resolution_x=480;sc.render.resolution_y=480;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
startroot=None
camstart=cam.location.copy()
for frame in range(1,73):
 sc.frame_set(frame);bpy.context.view_layer.update();sword.matrix_world=rig.matrix_world@rig.pose.bones['hand_r'].matrix@Matrix.Translation((0,.08,0))
 root=rig.pose.bones['root'].head.copy()
 if startroot is None:startroot=root.copy()
 cam.location=camstart+(root-startroot)
 sc.render.filepath=str(OUT/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
