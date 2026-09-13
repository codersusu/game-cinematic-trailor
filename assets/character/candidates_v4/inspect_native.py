import bpy,json
from pathlib import Path
import sys
out=Path(__file__).parent
if '--fbx' in sys.argv or '--rocketbox' in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(out/'rocketbox'/'Female_Adult_04_facial.fbx') if '--rocketbox' in sys.argv else str(out/'nilda'/'female_sketchfab.fbx'))
data={
 'file':Path(bpy.data.filepath).name,
 'fps':bpy.context.scene.render.fps,
 'frame_start':bpy.context.scene.frame_start,
 'frame_end':bpy.context.scene.frame_end,
 'objects':[],
 'actions':[]}
for o in bpy.data.objects:
 d={'name':o.name,'type':o.type,'dimensions':list(o.dimensions)}
 if o.type=='ARMATURE':d['bones']=[b.name for b in o.data.bones]
 if o.type=='MESH':
  d['vertices']=len(o.data.vertices);d['polygons']=len(o.data.polygons)
  d['shape_keys']=[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []
  d['materials']=[m.name if m else None for m in o.data.materials]
 data['objects'].append(d)
for a in bpy.data.actions:
 data['actions'].append({'name':a.name,'range':list(a.frame_range),'fcurves':len(a.fcurves)})
data['images']=[{'name':i.name,'size':list(i.size),'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
(out/('rocketbox/inspection.json' if '--rocketbox' in sys.argv else 'nilda-fbx-inspection.json' if '--fbx' in sys.argv else 'nilda-inspection.json')).write_text(json.dumps(data,indent=2))
print('NATIVE_INSPECTION_COMPLETE',len(data['actions']))
