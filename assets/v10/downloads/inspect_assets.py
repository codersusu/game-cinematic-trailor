"""Inspect downloaded vegetation in background Blender without rendering."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
report={'rendered':False,'assets':{}}
for asset,fmt in [('grass_bermuda_01','blend'),('fir_sapling','gltf'),('grass_medium_01','blend')]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 file=R/asset/(asset+'_2k.'+fmt)
 if fmt=='blend':
  with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.objects=list(src.objects)
  for ob in dst.objects:
   if ob:bpy.context.scene.collection.objects.link(ob)
 else:bpy.ops.import_scene.gltf(filepath=str(file))
 bpy.context.view_layer.update();rows=[]
 for ob in bpy.data.objects:
  r={'name':ob.name,'type':ob.type,'location':list(ob.location),'dimensions':list(ob.dimensions),'scale':list(ob.scale),'parent':ob.parent.name if ob.parent else None,'modifiers':[{'name':m.name,'type':m.type} for m in ob.modifiers]}
  if ob.type=='MESH':
   ob.data.calc_loop_triangles();r['vertices']=len(ob.data.vertices);r['triangles']=len(ob.data.loop_triangles);r['materials']=[m.name if m else None for m in ob.data.materials]
   if ob.data.vertices:r['local_mesh_bounds']={'min':[min(v.co[a] for v in ob.data.vertices) for a in range(3)],'max':[max(v.co[a] for v in ob.data.vertices) for a in range(3)]}
  rows.append(r)
 mats=[]
 for m in bpy.data.materials:
  mats.append({'name':m.name,'node_types':[n.type for n in m.node_tree.nodes] if m.use_nodes else [],'node_links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else [],'alpha_links':[(link.from_node.name,link.from_socket.name) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED' for link in n.inputs['Alpha'].links] if m.use_nodes else []})
 images=[]
 for i in bpy.data.images:
  if i.source=='FILE':
   p=Path(bpy.path.abspath(i.filepath)).resolve();images.append({'name':i.name,'path':str(p.relative_to(R)) if p.is_relative_to(R) else p.name,'exists':p.exists(),'size':list(i.size)})
 report['assets'][asset]={'objects':rows,'materials':mats,'images':images}
(R/'asset-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
for asset,data in report['assets'].items():
 print(asset)
 for r in data['objects']:print(r['name'],r.get('triangles'),r['dimensions'],r.get('local_mesh_bounds'))
 print('images',len(data['images']),'missing',[i['name'] for i in data['images'] if not i['exists']])
