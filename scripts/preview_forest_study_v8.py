"""Limited cheap layout review only: four small stills, never a final render."""
from pathlib import Path
import bpy, sys, json, time
ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
mode = args[0] if args else 'layout'
frames = [int(x) for x in args[1:]] or [60, 160, 230, 270]
if len(frames) > 6: raise ValueError('Study limited to six small stills')
folder = ROOT / 'previews/v8/forest'
folder.mkdir(parents=True, exist_ok=True)
scene.render.resolution_x = 960; scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.use_compositing = False; scene.render.use_sequencer = False
scene.render.image_settings.file_format = 'PNG'
scene.render.use_motion_blur = False
if mode == 'layout':
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'; shading.color_type = 'MATERIAL'
    shading.show_shadows = True; shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.background_type = 'WORLD'; scene.world.color = (.08, .11, .14)
elif mode == 'material':
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 16
else: raise ValueError('Only layout or material study modes are supported')
rows = []
for frame in frames:
    scene.frame_set(frame)
    marker = max((m for m in scene.timeline_markers if m.frame <= frame), key=lambda m: m.frame)
    scene.camera = marker.camera
    path = folder / f'{mode}-{frame:03d}.png'
    scene.render.filepath = str(path)
    start = time.monotonic(); bpy.ops.render.render(write_still=True)
    rows.append({'frame': frame, 'camera': scene.camera.name, 'seconds': round(time.monotonic()-start, 2), 'image': str(path.relative_to(ROOT))})
(folder / f'{mode}-review.json').write_text(json.dumps({'status': 'rendered awaiting visual inspection', 'mode': mode, 'resolution': [960, 540], 'heavy_render': False, 'stills': rows}, indent=2)+'\n')
