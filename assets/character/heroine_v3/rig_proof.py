"""Build and verify actual heroine from manifest; optional --render images."""
import bpy,sys,json,math,time
from pathlib import Path
from mathutils import Vector
import numpy as np
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
from heroine_v3 import add_heroine
bpy.ops.wm.read_factory_settings(use_empty=True)
t0=time.monotonic();result=add_heroine();print('BAKE_SECONDS',time.monotonic()-t0,flush=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False;scene.render.use_persistent_data=True
scene.render.resolution_x=700;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Rig proof world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.14));floor=bpy.context.object;mat=bpy.data.materials.new('proof floor');mat.diffuse_color=(.14,.15,.17,1);floor.data.materials.append(mat)
def light(name,loc,target,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
key=light('key',(-1,-3,4),(-3.8,-6,1),300,3);fill=light('fill',(-7,-4,3),(-3.8,-6,1),100,3);rim=light('rim',(-5,-9,4),(-3.8,-6,1),350,2)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2.0
out=BASE/'assets/character/heroine_v3/rig-proof';out.mkdir(exist_ok=True)
render='--render' in sys.argv
if render:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 scene.cycles.device='GPU'
metrics={};visible=[o for o in result['objects'] if o.type=='MESH' and not o.hide_render]
for frame in [1,8,15,22,64,130,240,252,390]:
 scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();zs={'left':[],'right':[]}
 for obj in visible:
  ev=obj.evaluated_get(dg);mesh=ev.to_mesh();arr=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',arr);arr=arr.reshape((-1,3));m=np.array(ev.matrix_world);world=arr@m[:3,:3].T+m[:3,3]
  zs['left'].append(float(world[world[:,0]<-3.8,2].min()));zs['right'].append(float(world[world[:,0]>=-3.8,2].min()));ev.to_mesh_clear()
 metrics[frame]={s:min(values) for s,values in zs.items()};print('SOLE',frame,metrics[frame],flush=True)
 pos=Vector((-3.8,-7.6+6.8*min(1,(frame-1)/239),.14));cam.location=pos+Vector((2,3.7,1.4));cam.rotation_euler=(pos+Vector((0,0,.86))-cam.location).to_track_quat('-Z','Y').to_euler()
 for l,delta in [(key,(2,2.5,3.5)),(fill,(-3,2,2.5)),(rim,(-1,-2,3))]:l.location=pos+Vector(delta);l.rotation_euler=(pos+Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
 if render and frame in [1,8,15,22,64,252]:scene.render.filepath=str(out/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
(out/'sole-metrics.json').write_text(json.dumps(metrics,indent=2));scene.frame_set(64);bpy.ops.wm.save_as_mainfile(filepath=str(out/'heroine-rig-proof.blend'));print('PROOF_DONE',flush=True)
