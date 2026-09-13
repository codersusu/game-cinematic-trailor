"""Trim the repeated entrance reaction; preserve the reviewed room performance."""
from pathlib import Path
import hashlib
import json
import bpy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'observatory-v8-finger-study.blend'
destination = ROOT / 'observatory-v11-single-reaction.blend'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
scene = bpy.context.scene


def animation_digest():
    rows = []
    for action in sorted(bpy.data.actions, key=lambda action: action.name):
        for curve in action.fcurves:
            rows.append((action.name, curve.data_path, curve.array_index, [
                (list(key.co), key.interpolation, list(key.handle_left), list(key.handle_right))
                for key in curve.keyframe_points
            ]))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


before = animation_digest()
removed = []
for marker in list(scene.timeline_markers):
    if marker.camera and marker.frame < 37:
        removed.append({'name': marker.name, 'frame': marker.frame, 'camera': marker.camera.name})
        scene.timeline_markers.remove(marker)
assert removed, 'Expected the original entrance reaction camera cut'
entrance = next(marker for marker in scene.timeline_markers if marker.frame == 37 and marker.camera)
assert any(marker.frame == 289 and marker.camera for marker in scene.timeline_markers)
scene.frame_start = 37
scene.frame_end = 576
scene.use_preview_range = False
scene.camera = entrance.camera
scene.frame_set(37)
scene['v11_editorial_note'] = 'Single surprise: quiet entrance, later wonder close-up, then index-finger approach.'
scene['planned_camera_structure'] = 'First-person forest; third-person Astra chamber.'
assert animation_digest() == before
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
out = ROOT / 'previews/v11'
out.mkdir(parents=True, exist_ok=True)
report = {
    'status': 'Room editorial change saved; no video rendered',
    'source': source.name, 'source_sha256': source_sha,
    'scene': destination.name, 'scene_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
    'removed_camera_cuts': removed,
    'frame_range': [37, 576], 'fps': scene.render.fps,
    'duration_seconds': 540 / (scene.render.fps / scene.render.fps_base),
    'removed_opening_seconds': 36 / (scene.render.fps / scene.render.fps_base),
    'later_wonder_shot_preserved': [289, 344],
    'index_finger_performance_preserved': True,
    'all_animation_curves_unchanged': animation_digest() == before,
    'animation_sha256': before,
    'previous_scene_unchanged': True,
    'production_render_performed': False,
    'combined_forest_room_edit_rendered': False,
}
(out / 'room-edit-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
