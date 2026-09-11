import bpy,sys,os,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'preview'
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.use_denoising=True
scene.render.fps=24;scene.frame_start=1;scene.frame_end=576
(ROOT/'renders/v4').mkdir(parents=True,exist_ok=True)
(ROOT/'previews/v4').mkdir(parents=True,exist_ok=True)
if bpy.data.objects.get('Airborne illuminated dust'):bpy.data.objects['Airborne illuminated dust'].hide_render=True
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 scene.cycles.device='GPU'
 print('DEVICES',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except:scene.cycles.device='CPU'
scene.render.use_persistent_data=True
scene.render.use_simplify=True
scene.cycles.texture_limit_render='8192'
scene.cycles.caustics_reflective=False
scene.cycles.caustics_refractive=False
if hasattr(scene.cycles,'debug_use_texture_cache_eviction'):scene.cycles.debug_use_texture_cache_eviction=False
if os.environ.get('OBS_CPU')=='1': scene.cycles.device='CPU'
print('RENDER_START',mode,scene.cycles.device,flush=True)
scene.render.image_settings.file_format='PNG'
def prepare_frame(frame):
 scene.frame_set(frame)
if mode=='compat':
 scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.cycles.samples=24;scene.cycles.adaptive_threshold=.07
 prepare_frame(390);scene.render.filepath=str(ROOT/'previews/v4'/'compat45.png');t=time.time();bpy.ops.render.render(write_still=True);print('COMPAT45_DONE',round(time.time()-t,2),flush=True)
elif mode=='preview':
 scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=50;scene.cycles.samples=24;scene.cycles.adaptive_threshold=.07
 frames=[int(x) for x in args[1:]] or [390]
 for f in frames:
  prepare_frame(f);scene.render.filepath=str(ROOT/'previews/v4'/f'frame_{f:04d}.png');print('PREVIEW_FRAME',f,flush=True);t=time.time();bpy.ops.render.render(write_still=True);print('PREVIEW_DONE',f,round(time.time()-t,2),flush=True)
elif mode=='proof':
 scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=50;scene.cycles.samples=24;scene.cycles.adaptive_threshold=.05
 frames=list(range(1,37))+list(range(97,145))+list(range(289,345))
 folder=ROOT/'previews/v4/acting-frames';folder.mkdir(parents=True,exist_ok=True)
 (folder/'mapping.json').write_text(json.dumps({'source_frames':frames,'fps':24,'resolution':[960,540]},indent=2))
 for i,f in enumerate(frames,1):
  path=folder/f'{i:04d}.png'
  if path.exists():continue
  prepare_frame(f);partial=folder/f'.{i:04d}.partial.png';scene.render.filepath=str(partial);t=time.time();bpy.ops.render.render(write_still=True);partial.replace(path)
  print('PROOF_FRAME_DONE',i,f,round(time.time()-t,2),flush=True)
elif mode=='hero':
 scene.render.resolution_percentage=100;scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.cycles.samples=128;scene.cycles.adaptive_threshold=.015
 f=int(args[1]) if len(args)>1 else 420;prepare_frame(f);scene.render.filepath=str(ROOT/'renders/v4'/'hero-4k.png');bpy.ops.render.render(write_still=True)
elif mode in ['test','final']:
 scene.render.resolution_x=1920;scene.render.resolution_y=1080
 scene.render.resolution_percentage=100 if mode=='final' else 50
 scene.cycles.samples=64 if mode=='final' else 24
 scene.cycles.adaptive_threshold=.025 if mode=='final' else .06
 start=int(args[1]) if len(args)>1 else 1;end=int(args[2]) if len(args)>2 else (576 if mode=='final' else start+47)
 if not 1<=start<=end<=576:raise ValueError('Frame range must be within 1–576')
 folder=ROOT/'renders/v4'/('frames' if mode=='final' else 'motion-test');folder.mkdir(parents=True,exist_ok=True)
 for f in range(start,end+1):
  path=folder/f'{f:04d}.png'
  if path.exists():continue
  prepare_frame(f);partial=folder/f'.{f:04d}.partial.png';scene.render.filepath=str(partial);t=time.time();bpy.ops.render.render(write_still=True)
  partial.replace(path)
  print('FRAME_DONE',f,round(time.time()-t,2),flush=True)

else:
 raise ValueError('Unknown render mode: '+mode)
