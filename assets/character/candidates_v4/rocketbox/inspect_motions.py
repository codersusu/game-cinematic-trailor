import bpy,json
from pathlib import Path
R=Path(__file__).parent
report=[]
for name in ['Female_Adult_04_facial.fbx','f_walk_neutral_01.max.fbx','f_walk_start.max.fbx','f_walk_stop.max.fbx','f_idle_breathe_01.max.fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(R/name))
 d={'file':name,'fps':bpy.context.scene.render.fps,'actions':[],'rigs':[]}
 for a in bpy.data.actions:d['actions'].append({'name':a.name,'range':list(a.frame_range),'fcurves':len(a.fcurves)})
 for o in bpy.data.objects:
  if o.type=='ARMATURE':d['rigs'].append({'name':o.name,'bones':[b.name for b in o.data.bones],'scale':list(o.scale),'rotation':list(o.rotation_euler),'location':list(o.location)})
 report.append(d)
(R/'motion-inspection.json').write_text(json.dumps(report,indent=2))
