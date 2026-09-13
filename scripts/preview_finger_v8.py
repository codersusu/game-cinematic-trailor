"""Isolated workbench gesture study; never runs a production render."""
from pathlib import Path
import bpy, sys, json, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from heroine_finger_v8 import add_finger_reach_v8
source=ROOT/'observatory-v7.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
s=bpy.context.scene;r=bpy.data.objects['Bip01']
report=add_finger_reach_v8(s,r)
s.frame_set(478)
dest=ROOT/'observatory-v8-finger-study.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
out=ROOT/'previews/v8/finger';out.mkdir(parents=True,exist_ok=True)
report.update({'source_scene':source.name,'source_sha256':source_sha,'study_scene':dest.name,'study_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
# For readability the preview isolates the existing skinned character and uses
# flat material lighting. Production room/cameras/settings remain in the study.
hero={o for o in r.parent.children_recursive if o.type in {'MESH','ARMATURE'}}
for o in s.objects:
    if o.type not in {'CAMERA','LIGHT'} and o not in hero:o.hide_render=True
s.render.engine='BLENDER_WORKBENCH'
s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.render.use_compositing=False;s.render.use_sequencer=False
s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.4
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.6,.67,.73)
s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.3
s.display.shading.background_type='WORLD';s.world.color=(.035,.045,.06)
cam=bpy.data.objects.new('V8 | Finger inspection',bpy.data.cameras.new('V8 | Finger inspection'))
s.collection.objects.link(cam)
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
s.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=.28
def point(n):return r.matrix_world@r.pose.bones[n].head
wrist=point('Bip01 R Hand');forward=(point('Bip01 R Finger2')-wrist).normalized()
across=(point('Bip01 R Finger4')-point('Bip01 R Finger1')).normalized()
normal=forward.cross(across).normalized()
center=wrist+forward*.10
for label,direction in [('palm',normal+across*.4),('back',-normal+across*.3),('side',across+normal*.25)]:
    cam.location=center+direction.normalized()*.8
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    s.camera=cam;bpy.context.view_layer.update()
    print('INSPECTION_CAMERA',s.camera.name,list(cam.location),cam.data.ortho_scale,flush=True)
    s.render.filepath=str(out/f'{label}-478.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
(out/'gesture-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('FINGER_STUDY_READY',dest)
