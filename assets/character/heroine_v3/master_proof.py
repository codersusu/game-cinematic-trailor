import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
from heroine_v3 import _import,_geometry_bounds
bpy.ops.wm.read_factory_settings(use_empty=True)
objects=_import('assets/character/heroine_v3/master.glb');lo,hi=_geometry_bounds(objects);factor=1.72/(hi.z-lo.z)
for o in objects:o.scale*=factor;o.location.z-=lo.z*factor
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False;scene.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU';scene.render.resolution_x=900;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('proof world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;mat=bpy.data.materials.new('ground');mat.diffuse_color=(.13,.14,.16,1);floor.data.materials.append(mat)
def area(name,loc,target,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('soft key',(1.8,-2.8,3.1),(0,0,1),170,2.5);area('fill',(-1.8,-1,2),(0,0,1.2),70,2);area('hair rim',(0,1,2.5),(0,0,1.2),180,1.5)
bpy.ops.object.camera_add(location=(.4,-4,1.5));cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.96;cam.rotation_euler=(Vector((0,0,.86))-cam.location).to_track_quat('-Z','Y').to_euler()
out=BASE/'assets/character/heroine_v3';scene.render.filepath=str(out/'master-body.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-3,1.60);cam.data.ortho_scale=.48;cam.rotation_euler=(Vector((0,0,1.56))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_y=900;scene.render.filepath=str(out/'master-face.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'master-proof.blend'))
print('BOUNDS',list(lo),list(hi))
