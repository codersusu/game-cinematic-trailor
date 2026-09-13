"""Standalone lighting and compatibility proof of the sourced keeper asset."""
import bpy, sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from integrate import add_keeper
bpy.ops.wm.read_factory_settings(use_empty=True)
info=add_keeper(location=(0,0,0),rotation_z=0,height=1.8)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1000
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Portrait darkness')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.025,0.035,0.06,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.2
face=Vector(info['face_target'])
def area(name,loc,power,color,size):
 d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.color=color; d.shape='DISK'; d.size=size
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(face-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm mechanism',(1.2,-2,2.2),220,(1,.62,.3),1.7)
area('Moonlight rim',(-1.5,.6,2.5),300,(.28,.5,1),1.2)
area('Face fill',(-.7,-1.5,1.7),25,(.4,.6,1),1.5)
d=bpy.data.cameras.new('Keeper portrait'); cam=bpy.data.objects.new('Keeper portrait',d);scene.collection.objects.link(cam)
cam.location=face+Vector((.24,-1.7,.06));cam.rotation_euler=(face-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=65;scene.camera=cam
d.dof.use_dof=True;d.dof.focus_distance=(face-cam.location).length;d.dof.aperture_fstop=5.6
scene.frame_set(205)
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(Path(__file__).resolve().parent/'keeper-portrait.png')
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parent/'keeper-portrait.blend'))
bpy.ops.render.render(write_still=True)
