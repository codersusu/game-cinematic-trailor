"""Render changed finger-performance frames for the mixed-camera review."""
from pathlib import Path
import bpy, hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
report = json.loads((ROOT/'previews/v11/room-edit-report.json').read_text())
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() == report['scene_sha256']
assert (scene.frame_start, scene.frame_end) == (37, 576)
folder = ROOT/'previews/v11/room-frames'
folder.mkdir(parents=True, exist_ok=True)
scene.render.engine = 'CYCLES'
scene.cycles.use_denoising = True
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.metalrt = 'OFF'
prefs.kernel_optimization_level = 'OFF'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'METAL'
assert any(device.use for device in prefs.devices)
scene.cycles.device = 'GPU'
scene.render.use_persistent_data = True
scene.render.use_simplify = True
scene.cycles.texture_limit_render = '8192'
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
if hasattr(scene.cycles, 'debug_use_texture_cache_eviction'):
    scene.cycles.debug_use_texture_cache_eviction = False
if bpy.data.objects.get('Airborne illuminated dust'):
    bpy.data.objects['Airborne illuminated dust'].hide_render = True
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.cycles.samples = 32
scene.cycles.adaptive_threshold = .04
identity = {'scene_sha256': report['scene_sha256'], 'resolution': [960,540],
            'samples': 32, 'adaptive_threshold': .04, 'engine': 'CYCLES',
            'source_fps': 24, 'output_fps': 12, 'new_frames': list(range(419,576,2))}
stamp = folder/'new-frame-source.json'
if stamp.exists():
    assert json.loads(stamp.read_text()) == identity
stamp.write_text(json.dumps(identity, indent=2)+'\n')
timings = []
frames = [419,477] + [f for f in range(419,576,2) if f not in (419,477)]
for frame in frames:
    target = folder/f'{frame:04d}.png'
    if target.exists():
        continue
    scene.frame_set(frame)
    temporary = folder/f'.{frame:04d}.partial.png'
    scene.render.filepath = str(temporary)
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    temporary.replace(target)
    timings.append({'frame':frame,'seconds':time.monotonic()-start})
    print('V11_FRAME',frame,round(timings[-1]['seconds'],2),flush=True)
(folder/'render-timings.json').write_text(json.dumps(timings,indent=2)+'\n')
print('V11_RENDER_COMPLETE',flush=True)
