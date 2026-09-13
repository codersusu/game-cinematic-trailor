"""Small workbench hand rehearsal: 31 frames, no production lighting."""
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'observatory-v8-finger-study.blend'),use_scripts=False)
s=bpy.context.scene;r=bpy.data.objects['Bip01'];s.frame_set(478)
out=ROOT/'previews/v8/finger/motion-frames';out.mkdir(parents=True,exist_ok=True)
hero={o for o in r.parent.children_recursive if o.type in {'MESH','ARMATURE'}}
for o in s.objects:
    if o.type not in {'CAMERA','LIGHT'} and o not in hero:o.hide_render=True
# Isolate the weighted hand surface for this diagnostic: as her arm turns, her
# torso would otherwise occlude a camera that follows the palm. The source
# scene is never saved after this inspection-only mesh copy.
for original in [o for o in hero if o.type=='MESH']:
    copy=original.copy();copy.data=original.data.copy();s.collection.objects.link(copy)
    original.hide_render=True
    groups={g.index for g in copy.vertex_groups if g.name=='Bip01 R Hand' or g.name.startswith('Bip01 R Finger')}
    keep={v.index for v in copy.data.vertices if sum(g.weight for g in v.groups if g.group in groups)>.03}
    mesh=bmesh.new();mesh.from_mesh(copy.data);mesh.verts.ensure_lookup_table()
    bmesh.ops.delete(mesh,geom=[v for v in mesh.verts if v.index not in keep],context='VERTS')
    mesh.to_mesh(copy.data);mesh.free()
s.render.engine='BLENDER_WORKBENCH'
s.render.resolution_x=600;s.render.resolution_y=500;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.render.use_compositing=False;s.render.use_sequencer=False
s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.4
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.67,.73)
s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.3
s.display.shading.background_type='WORLD';s.world.color=(.035,.045,.06)
cam=bpy.data.objects.new('V8 | Finger motion inspection',bpy.data.cameras.new('V8 | Finger motion inspection'))
s.collection.objects.link(cam)
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.29
def point(n):return r.matrix_world@r.pose.bones[n].head
for index,frame in enumerate(range(418,479,2),1):
    s.frame_set(frame)
    wrist=point('Bip01 R Hand');forward=(point('Bip01 R Finger2')-wrist).normalized()
    across=(point('Bip01 R Finger4')-point('Bip01 R Finger1')).normalized()
    normal=forward.cross(across).normalized();center=wrist+forward*.10
    cam.location=center+(normal+across*.4).normalized()*.8
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    s.camera=cam;bpy.context.view_layer.update()
    s.render.filepath=str(out/f'{index:04d}.png');bpy.ops.render.render(write_still=True)
print('WORKBENCH_MOTION_COMPLETE')
