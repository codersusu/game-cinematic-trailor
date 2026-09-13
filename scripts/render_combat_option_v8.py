"""Bounded draft rendering for combat choice; never a production-quality run."""
from pathlib import Path
import bpy, sys, json, time, hashlib

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(args) < 2 or args[0] not in ['a', 'b', 'c'] or args[1] not in ['stills', 'motion']:
    raise ValueError('Usage: -- a|b|c stills|motion [frames]')
option, mode = args[:2]
scene = bpy.context.scene
source_fps = scene.render.fps / scene.render.fps_base
seconds = (scene.frame_end - scene.frame_start + 1) / source_fps
if seconds > 10.01: raise ValueError('Selection study cannot exceed ten seconds')
output_count = round(seconds * 12)
folder = ROOT / f'previews/v8/options/{option}'
frames_dir = folder / ('frames' if mode == 'motion' else 'stills')
frames_dir.mkdir(parents=True, exist_ok=True)
frames = list(range(1, output_count + 1)) if mode == 'motion' else [int(f) for f in args[2:]] or [1, 36, 63, 88]
if mode == 'stills' and len(frames) > 6: raise ValueError('Six review stills maximum')
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 8
scene.render.resolution_x = 768; scene.render.resolution_y = 432; scene.render.resolution_percentage = 100
scene.render.use_motion_blur = False
scene.render.use_compositing = False; scene.render.use_sequencer = False
scene.render.image_settings.file_format = 'PNG'
scene.render.use_simplify = True; scene.render.simplify_subdivision = 1
scene_hash = hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
stamp = frames_dir / 'source.json'
identity = {'scene': Path(bpy.data.filepath).name, 'sha256': scene_hash, 'resolution': [768, 432], 'fps': 12, 'source_fps': source_fps, 'source_frame_start': scene.frame_start, 'source_frame_end': scene.frame_end, 'engine': 'EEVEE', 'samples': 8}
if stamp.exists() and json.loads(stamp.read_text()) != identity and any(frames_dir.glob('[0-9]*.png')):
    raise ValueError('Changed study: archive old frames before resuming')
stamp.write_text(json.dumps(identity, indent=2)+'\n')
timings = []
for frame in frames:
    source_frame = scene.frame_start + (frame-1)*source_fps/12
    scene.frame_set(int(source_frame), subframe=source_frame%1)
    marks = [m for m in scene.timeline_markers if m.camera and m.frame <= source_frame]
    if marks: scene.camera = max(marks, key=lambda m: m.frame).camera
    output = frames_dir / f'{frame:04d}.png'
    if output.exists(): continue
    scene.render.filepath = str(output)
    start = time.monotonic(); bpy.ops.render.render(write_still=True)
    elapsed = round(time.monotonic() - start, 3)
    timings.append({'frame': frame, 'source_frame': source_frame, 'seconds': elapsed})
    print('DRAFT_FRAME', option, frame, elapsed, flush=True)
(folder / f'{mode}-render.json').write_text(json.dumps({'source': identity, 'frames_requested': frames, 'new_frame_timings': timings, 'heavy_render': False, 'status': 'rendered for review'}, indent=2)+'\n')
