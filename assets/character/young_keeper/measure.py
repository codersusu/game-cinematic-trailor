import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
from young_keeper import add_young_keeper
result=add_young_keeper()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
for d in prefs.devices:d.use=(d.type=='METAL')
scene.cycles.device='GPU';scene.render.use_persistent_data=True
scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.color=(.15,.15,.15)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.14));floor=bpy.context.object
mat=bpy.data.materials.new('proof ground');mat.diffuse_color=(.16,.18,.2,1);floor.data.materials.append(mat)
def light(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-3.8,-6,1))-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-1,-4,5),550,5);light('Rim',(-7,-9,4),650,3)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2.2
out=BASE/'assets/character/young_keeper/proof';out.mkdir(exist_ok=True)
metrics={}
for frame in [1,8,15,22,64,130,240,252]:
 scene.frame_set(frame);bpy.context.view_layer.update()
 pos=result['root'].location.copy();cam.location=pos+Vector((2.4,3.8,1.4));cam.rotation_euler=(pos+Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler()
 dg=bpy.context.evaluated_depsgraph_get();shoe=bpy.data.objects['GEO-rain-shoes'].evaluated_get(dg);mesh=shoe.to_mesh();verts=[shoe.matrix_world@v.co for v in mesh.vertices];shoe.to_mesh_clear()
 left=[v.z for v in verts if v.x<-3.8];right=[v.z for v in verts if v.x>=-3.8]
 metrics[frame]={'left_floor_min':min(left),'right_floor_min':min(right),'height_max':max(v.z for v in verts)}
 if False:
  scene.render.filepath=str(out/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
scene.frame_set(64);pos=result['root'].location.copy();cam.data.ortho_scale=.55;cam.location=pos+Vector((.3,3,1.57));cam.rotation_euler=(pos+Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'face.png')
(out/'metrics.json').write_text(json.dumps(metrics,indent=2));(out/'contacts.json').write_text(json.dumps(result['foot_contacts'],indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'walk-proof.blend'))
print('PROOF_DONE',metrics)
