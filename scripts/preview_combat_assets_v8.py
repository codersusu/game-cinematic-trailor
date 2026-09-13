"""Small standalone creature lookdev comparisons; no production scene writes."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'previews/v8/combat';OUT.mkdir(parents=True,exist_ok=True)
FILES={'forest_guardian':'assets/v8/combat/forest-monster/forest-monster-final.blend','tomek_wolf':'assets/v8/combat/tomek/wolf.blend','quaternius_wolf':'assets/v8/combat/quaternius/Wolf.blend'}
def material(name,color=(.22,.25,.28,1),image=None,normal=None):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;n=m.node_tree.nodes;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=color;b.inputs['Roughness'].default_value=.78
 if image:
  t=n.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
 if normal:
  t=n.new('ShaderNodeTexImage');t.image=normal;t.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],b.inputs['Normal'])
 return m
for key,rel in FILES.items():
 if '--guardian-motion' in sys.argv and key!='forest_guardian':continue
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/rel),load_ui=False,use_scripts=False);sc=bpy.context.scene
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 for o in list(sc.objects):
  if o.type in ['LIGHT','CAMERA'] or o.name in ['Root','Tree'] or o.name=='wolf_male2':bpy.data.objects.remove(o,do_unlink=True)
 rig=next(o for o in sc.objects if o.type=='ARMATURE');rig.animation_data_create();rig.animation_data.action=bpy.data.actions.get('Idle') or bpy.data.actions.get('wolf_idle')
 for t in rig.animation_data.nla_tracks:t.mute=True
 sc.frame_set(0);bpy.context.view_layer.update()
 for o in sc.objects:
  if o.type!='MESH':continue
  if key=='forest_guardian':
   im=bpy.data.images.get('forest-monster-skin1.png' if o.name=='Monster' else 'skin_dieing.png');norm=bpy.data.images.get('forest-monster-norm.png' if o.name=='Monster' else 'tree-norm.png');o.data.materials.clear();o.data.materials.append(material('PBR_'+o.name,image=im,normal=norm))
  elif key=='tomek_wolf':o.data.materials.clear();o.data.materials.append(material('wolf',image=bpy.data.images.get('wolf_female.png')))
  else:
   for m in o.data.materials:
    c=tuple(m.diffuse_color);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Base Color'].default_value=c
 mesh=[o for o in sc.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(c) for o in mesh for c in o.bound_box];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));center=(lo+hi)/2;span=max(hi-lo)
 bpy.ops.object.camera_add(location=center+Vector((1.4,-2.3,.85))*span);cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=span*1.38;sc.camera=cam
 for name,off,power,size in [('key',(1,-1,1.8),100,1.5),('fill',(-1,-.5,1),50,2),('rim',(0,1,1.2),150,1)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(off)*span);o=bpy.context.object;o.data.energy=power*span*span;o.data.shape='DISK';o.data.size=size*span;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
 sc.world=bpy.data.worlds.new('studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.05,.065,.085,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=8;sc.cycles.use_denoising=True
 sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 sc.render.filepath=str(OUT/(key+'.png'));bpy.ops.render.render(write_still=True)
 if '--guardian-motion' in sys.argv:
  rig.animation_data.action=bpy.data.actions['Attack'];sc.render.resolution_x=480;sc.render.resolution_y=480;sc.cycles.samples=4
  for frame in range(31):
   sc.frame_set(frame);sc.render.filepath=str(OUT/'guardian-attack-frames'/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
