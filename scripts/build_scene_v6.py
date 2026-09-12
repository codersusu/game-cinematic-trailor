"""Add the late exploratory reach to the saved Astra Chamber; retain V5."""
from pathlib import Path
import hashlib
import json
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from heroine_reach_v6 import layer_reach

source = ROOT / 'observatory-v5.blend'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
scene = bpy.context.scene
report = layer_reach()

# A closer view makes the hand, elbow and shoulder read during the new gesture.
name = 'V6 | The first reach'
data = bpy.data.cameras.new(name)
camera = bpy.data.objects.new(name, data)
scene.collection.objects.link(camera)
focus = bpy.data.objects.new(name + ' focus', None)
scene.collection.objects.link(focus)
data.lens = 48
data.sensor_width = 36
data.clip_end = 300
data.dof.use_dof = True
data.dof.aperture_fstop = 5.6
data.dof.focus_object = focus
camera.rotation_mode = 'QUATERNION'
previous_rotation = None
for frame, position, target in [
    (385, (-3.65, 2.4, 1.95), (-3.45, -.45, 1.46)),
    (480, (-3.15, 2.2, 1.99), (-3.38, -.43, 1.49)),
]:
    camera.location = position
    rotation = (Vector(target) - camera.location).to_track_quat('-Z', 'Y')
    if previous_rotation is not None and rotation.dot(previous_rotation) < 0:
        rotation.negate()
    camera.rotation_quaternion = rotation
    previous_rotation = rotation.copy()
    camera.keyframe_insert('location', frame=frame)
    camera.keyframe_insert('rotation_quaternion', frame=frame)
    focus.location = target
    focus.keyframe_insert('location', frame=frame)
marker = scene.timeline_markers.new(name, frame=385)
marker.camera = camera

scene.frame_set(448)
for text in list(bpy.data.texts):
    bpy.data.texts.remove(text)
bpy.ops.file.make_paths_relative()
destination = ROOT / 'observatory-v6.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
folder = ROOT / 'renders/v6'
folder.mkdir(parents=True, exist_ok=True)
report.update({'source_scene': source.name, 'source_sha256': source_sha,
               'scene': destination.name,
               'scene_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
               'new_camera_cut': 385, 'duration_seconds': 24,
               'previous_version_unchanged': True})
(folder / 'reach-performance.json').write_text(json.dumps(report, indent=2) + '\n')
print('V6_SCENE_READY', destination.name, len(scene.objects), 'objects')
