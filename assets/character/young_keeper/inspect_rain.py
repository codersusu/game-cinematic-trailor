import bpy, json
from pathlib import Path
out=Path(__file__).resolve().parent
summary={
 'blender_version':bpy.app.version_string,
 'file':bpy.data.filepath,
 'collections':[{'name':c.name,'objects':len(c.all_objects)} for c in bpy.data.collections],
 'objects':[{'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'location':list(o.location),'hide_render':o.hide_render,'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]} for o in bpy.data.objects],
 'armatures':{},
 'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images],
 'actions':[a.name for a in bpy.data.actions],
 'texts':[{'name':t.name,'use_module':t.use_module,'length':len(t.as_string())} for t in bpy.data.texts],
 'materials':[m.name for m in bpy.data.materials]
}
for o in bpy.data.objects:
 if o.type=='ARMATURE':
  summary['armatures'][o.name]=[{'name':b.name,'loc':list(b.location),'rot':list(b.rotation_euler),'head':list(b.head),'tail':list(b.tail),'rotation_mode':b.rotation_mode,'custom_properties':{k:str(v) for k,v in b.items()},'constraints':[{'name':c.name,'type':c.type} for c in b.constraints]} for b in o.pose.bones]
for t in bpy.data.texts:
 if t.name.endswith('.py'):
  (out/('rain_bundled_'+t.name.replace('/','_'))).write_text(t.as_string())
(out/'rain-inspection.json').write_text(json.dumps(summary,indent=2))
print('CHARACTER_INSPECTED',len(bpy.data.objects),'objects',len(bpy.data.images),'images')
