import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.samples=24; s.cycles.use_denoising=True
s.render.resolution_x=440; s.render.resolution_y=440; s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral world'); s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='METAL'; prefs.use_metalrt='OFF'; prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.view_settings.view_transform='AgX'
bpy.ops.object.camera_add(location=(3,-5,3.1)); cam=bpy.context.object
s.camera=cam; cam.data.type='ORTHO';cam.data.ortho_scale=3.5
cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
for loc,energy,size in [((1,-3,5),500,4),((-3,-1,3),250,3),((2,3,4),600,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200); floor=bpy.context.object
m=bpy.data.materials.new('Neutral ground');m.diffuse_color=(.13,.13,.13,1);floor.data.materials.append(m)
selections=[('industrial','control_terminal_mat'),('industrial','pipe_05'),('industrial','tank_control_panel_mat'),('industrial','tank_2_mat'),('industrial','vent_mat'),('industrial','wall_thing_mat'),('irondust','Door1'),('irondust','Wall1'),('irondust','Locker1')]
ind=ROOT/'industrial/OGA_industrial_a52_version/industrial_final_cycles.blend'
iro=ROOT/'irondust/Sci-fi env2/Meshes.blend'
# Restore old Blender Internal texture atlas with explicit Cycles nodes, no scene save.
im=bpy.data.materials.new('Irondust White atlas (preview hookup)');im.use_nodes=True
n=im.node_tree.nodes;l=im.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.48;p.inputs['Metallic'].default_value=.35
for suffix,socket in [('Albedo.tga','Base Color'),('Emission.png','Emission Color')]:
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(iro.parent/('WhiteColor_'+suffix)));l.new(t.outputs['Color'],p.inputs[socket])
p.inputs['Emission Strength'].default_value=.6
t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(iro.parent/'WhiteColor_NormalMap.png'));t.image.colorspace_settings.name='Non-Color';normal=n.new('ShaderNodeNormalMap');l.new(t.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
(ROOT/'proof').mkdir(exist_ok=True)
checks=[]
for source,name in selections:
 path=ind if source=='industrial' else iro
 with bpy.data.libraries.load(str(path),link=False) as (frm,to):to.objects=[name]
 o=to.objects[0];s.collection.objects.link(o)
 bpy.context.view_layer.update()
 # Relink author-relative texture paths against the originating asset folder.
 for img in bpy.data.images:
  if img.source=='FILE' and not img.packed_file and img.filepath.startswith('//'):
   target=path.parent/img.filepath[2:]
   if target.exists():img.filepath=str(target)
 if source=='irondust':o.data.materials.clear();o.data.materials.append(im)
 corners=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector([min(c[i] for c in corners) for i in range(3)]);hi=Vector([max(c[i] for c in corners) for i in range(3)])
 scale=2.3/max(hi-lo)
 o.scale*=scale;o.location*=scale;bpy.context.view_layer.update()
 corners=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector([min(c[i] for c in corners) for i in range(3)]);hi=Vector([max(c[i] for c in corners) for i in range(3)])
 o.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));bpy.context.view_layer.update()
 checks.append({'source':source,'name':name,'vertices':len(o.data.vertices),'uv_layers':len(o.data.uv_layers),'dimensions_normalized':list(o.dimensions),'material_count':len(o.data.materials)})
 s.render.filepath=str(ROOT/'proof'/f'{source}-{name}.png');bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(o,do_unlink=True)
(ROOT/'proof/inspection.json').write_text(json.dumps(checks,indent=2))
