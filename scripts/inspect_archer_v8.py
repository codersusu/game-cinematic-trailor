from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];d=R/'assets/v8/licensed/archer/Animations/Blender';out={}
for p in sorted(d.glob('*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 out[p.name]={'fps':bpy.context.scene.render.fps,'frame':[bpy.context.scene.frame_start,bpy.context.scene.frame_end], 'objects':[{'name':o.name,'type':o.type,'dim':list(o.dimensions),'verts':len(o.data.vertices) if o.type=='MESH' else None,'bones':list(o.data.bones.keys()) if o.type=='ARMATURE' else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None} for o in bpy.context.scene.objects], 'actions':[{'name':a.name,'frames':list(a.frame_range),'slots':[s.identifier for s in a.slots]} for a in bpy.data.actions], 'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]}
(R/'renders/v8/combat/archer-inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
