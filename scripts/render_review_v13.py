"""Bounded V13 review rendering; single GPU job, explicit source identity."""
from pathlib import Path
import bpy, hashlib, json, sys, time
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:]
section,mode=args[:2]
assert section in ('forest','room') and mode in ('stills','motion','workbench','third','diagnostic')
scene=bpy.context.scene
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.use_simplify=True;scene.render.simplify_subdivision=1
if section=='forest':
    view='third' if mode in ('third','diagnostic') else 'first'
    scene.camera=bpy.data.objects['V9 | '+view.title()+'-person escape']
    if mode=='diagnostic':scene.camera=bpy.data.objects['V13 | Arrow rest diagnostic']
    tagged=0
    for ob in scene.objects:
        if ob.get('v12_visibility') in ('first','third'):
            ob.hide_render=ob['v12_visibility']!=view;tagged+=1
    assert tagged,'V13 heroine visibility tags are required'
    for name in ('HumanF_BodyMesh','V9 | First-person arms only'):
        if bpy.data.objects.get(name):bpy.data.objects[name].hide_render=True
    scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16
    scene.render.use_motion_blur=False;scene.render.use_compositing=False;scene.render.use_sequencer=False
    output=ROOT/'previews/v13'/('forest-third-stills' if mode=='third' else 'forest-frames')
    if mode=='diagnostic':output=ROOT/'previews/v13/archery-stills'
    # Begin on the clean bow raise; inherited idle frames1..9 cross the lens.
    frames=list(range(10,133)) if mode=='motion' else [int(f) for f in args[2:]]
    settings={'engine':'EEVEE','samples':16,'view':view,'camera':scene.camera.name}
else:
    if mode=='workbench':
        scene.render.engine='BLENDER_WORKBENCH'
        scene.render.use_compositing=False;scene.render.use_sequencer=False
        scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
        scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
        scene.display.shading.background_type='WORLD';scene.world.color=(.045,.055,.065)
        output=ROOT/'previews/v13/room-workbench'
        settings={'engine':'WORKBENCH'}
    else:
        scene.render.engine='CYCLES';scene.cycles.use_denoising=True
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
        for device in prefs.devices:device.use=device.type=='METAL'
        assert any(device.use for device in prefs.devices)
        scene.cycles.device='GPU';scene.cycles.samples=32;scene.cycles.adaptive_threshold=.04
        scene.render.use_persistent_data=True
        scene.cycles.texture_limit_render='8192';scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
        if hasattr(scene.cycles,'debug_use_texture_cache_eviction'):scene.cycles.debug_use_texture_cache_eviction=False
        if bpy.data.objects.get('Airborne illuminated dust'):bpy.data.objects['Airborne illuminated dust'].hide_render=True
        output=ROOT/'previews/v13/room-frames'
        settings={'engine':'CYCLES','samples':32,'adaptive_threshold':.04}
    frames=[int(f) for f in args[2:]]
    if mode in ('motion','workbench'):
        start,end=frames;frames=list(range(start,end+1,2))
assert frames
output.mkdir(parents=True,exist_ok=True)
identity={'scene':Path(bpy.data.filepath).name,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'resolution':[1920,1080],'source_fps':scene.render.fps,'output_fps':12,**settings}
stamp=output/'source.json'
if stamp.exists():assert json.loads(stamp.read_text())==identity,'Changed scene: archive earlier V13 frames first'
stamp.write_text(json.dumps(identity,indent=2)+'\n')
timings=[]
paused=False
for frame in frames:
    if (ROOT/'previews/v13/pause-render').exists():
        paused=True;print('V13_PAUSED',section,mode,flush=True);break
    target=output/f'{frame:04d}.png'
    if target.exists():continue
    scene.frame_set(frame)
    temporary=output/f'.{frame:04d}.partial.png';scene.render.filepath=str(temporary)
    start=time.monotonic();bpy.ops.render.render(write_still=True);temporary.replace(target)
    seconds=time.monotonic()-start;timings.append({'frame':frame,'seconds':seconds})
    print('V13_FRAME',section,mode,frame,round(seconds,2),flush=True)
timing_file=output/f'{mode}-timings.json'
previous=json.loads(timing_file.read_text()) if timing_file.exists() else []
by_frame={row['frame']:row for row in previous+timings}
timing_file.write_text(json.dumps(list(by_frame.values()),indent=2)+'\n')
print('V13_RENDER_PAUSED' if paused else 'V13_RENDER_COMPLETE',section,mode,flush=True)
