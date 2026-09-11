import bpy,sys,os,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'preview'
scene=bpy.context.scene
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
 prepare_frame(390);scene.render.filepath=str(ROOT/'previews/v2'/'compat45.png');t=time.time();bpy.ops.render.render(write_still=True);print('COMPAT45_DONE',round(time.time()-t,2),flush=True)
elif mode=='preview':
 scene.render.resolution_percentage=50;scene.cycles.samples=24;scene.cycles.adaptive_threshold=.07
 frames=[int(x) for x in args[1:]] or [390]
 for f in frames:
  prepare_frame(f);scene.render.filepath=str(ROOT/'previews/v2'/f'frame_{f:04d}.png');print('PREVIEW_FRAME',f,flush=True);t=time.time();bpy.ops.render.render(write_still=True);print('PREVIEW_DONE',f,round(time.time()-t,2),flush=True)
elif mode=='hero':
 scene.render.resolution_percentage=100;scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.cycles.samples=128;scene.cycles.adaptive_threshold=.015
 f=int(args[1]) if len(args)>1 else 420;prepare_frame(f);scene.render.filepath=str(ROOT/'renders/v2'/'hero-4k.png');bpy.ops.render.render(write_still=True)
elif mode in ['test','final']:
 scene.render.resolution_percentage=100 if mode=='final' else 50
 scene.cycles.samples=48 if mode=='final' else 24
 scene.cycles.adaptive_threshold=.03 if mode=='final' else .06
 start=int(args[1]) if len(args)>1 else 1;end=int(args[2]) if len(args)>2 else (576 if mode=='final' else start+47)
 folder=ROOT/'renders/v2'/('frames' if mode=='final' else 'motion-test');folder.mkdir(parents=True,exist_ok=True)
 for f in range(start,end+1):
  path=folder/f'{f:04d}.png'
  if path.exists():continue
  prepare_frame(f);partial=folder/f'.{f:04d}.partial.png';scene.render.filepath=str(partial);t=time.time();bpy.ops.render.render(write_still=True)
  partial.replace(path)
  print('FRAME_DONE',f,round(time.time()-t,2),flush=True)
