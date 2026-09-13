"""Read-only native combat-candidate audit. No render or script auto-execution."""
from pathlib import Path
import bpy, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/v8/combat';OUT.mkdir(parents=True,exist_ok=True)
FILES={'forest_guardian':'assets/v8/combat/forest-monster/forest-monster-final.blend','tomek_wolf':'assets/v8/combat/tomek/wolf.blend','quaternius_wolf':'assets/v8/combat/quaternius/Wolf.blend'}
report={}
for key,rel in FILES.items():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/rel),load_ui=False,use_scripts=False)
 sc=bpy.context.scene
 report[key]={'file':rel,'fps':sc.render.fps,'frames':[sc.frame_start,sc.frame_end],
 'objects':[{'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'vertices':len(o.data.vertices) if o.type=='MESH' else None,'bones':len(o.data.bones) if o.type=='ARMATURE' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'nla':[{'name':t.name,'strips':[{'name':s.name,'action':s.action.name if s.action else None,'frames':[s.frame_start,s.frame_end]} for s in t.strips]} for t in o.animation_data.nla_tracks] if o.animation_data else []} for o in sc.objects],
 'actions':[{'name':a.name,'frames':list(a.frame_range),'fcurves':len(a.fcurves)} for a in bpy.data.actions],
 'images':[{'name':i.name,'size':list(i.size),'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images], 'embedded_texts':list(bpy.data.texts.keys())}
(OUT/'asset-inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:{'actions':v['actions'],'objects':[(o['name'],o['vertices'],o['bones']) for o in v['objects']]} for k,v in report.items()},indent=2))
