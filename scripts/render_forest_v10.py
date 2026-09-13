"""Render a bounded lightweight perspective study from one baked scene."""
from pathlib import Path
import bpy,sys,json,time,hashlib
ROOT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];view,mode=args[:2];assert view in ['first','third'] and mode in ['stills','motion']
sc=bpy.context.scene;assert sc.frame_end==144 and sc.render.fps==12
sc.camera=bpy.data.objects['V9 | '+('First' if view=='first' else 'Third')+'-person escape']
bpy.data.objects['HumanF_BodyMesh'].hide_render=view=='first';bpy.data.objects['V9 | First-person arms only'].hide_render=view!='first'
sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.use_motion_blur=False;sc.render.use_compositing=False;sc.render.use_sequencer=False;sc.render.use_simplify=True;sc.render.simplify_subdivision=1
folder=ROOT/'previews/v10'/view/('frames' if mode=='motion' else 'stills');folder.mkdir(parents=True,exist_ok=True)
identity={'scene':Path(bpy.data.filepath).name,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'view':view,'frames':144,'fps':12,'seconds':12,'resolution':[960,540],'engine':'EEVEE','samples':16,'heavy_render':False}
stamp=folder/'source.json'
if stamp.exists() and json.loads(stamp.read_text())!=identity and any(folder.glob('*.png')):raise ValueError('Archive old render frames before changed-scene render')
stamp.write_text(json.dumps(identity,indent=2)+'\n');frames=list(range(1,145)) if mode=='motion' else [int(f) for f in args[2:]];assert mode=='motion' or len(frames)<=6
times=[]
for f in frames:
 sc.frame_set(f);p=folder/f'{f:04d}.png'
 if p.exists():continue
 sc.render.filepath=str(p);start=time.monotonic();bpy.ops.render.render(write_still=True);times.append({'frame':f,'seconds':time.monotonic()-start});print('ESCAPE_FRAME',view,f,flush=True)
(folder.parent/(mode+'-render.json')).write_text(json.dumps({'source':identity,'timings':times,'status':'rendered for review'},indent=2)+'\n')
