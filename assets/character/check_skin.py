import bpy,json
from pathlib import Path
r={}
for m in bpy.data.materials:
 if any(w in m.name.lower() for w in ['skin','face','eye']):
  r[m.name]={'nodes':[{'name':n.name,'type':n.bl_idname,'group':n.node_tree.name if n.type=='GROUP' else None,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None,'inputs':{s.name:str(s.default_value) for s in n.inputs if hasattr(s,'default_value')},'links':[(l.from_node.name,l.from_socket.name,l.to_socket.name) for s in n.inputs for l in s.links]} for n in m.node_tree.nodes] if m.use_nodes else []}
for o in bpy.data.objects:
 if o.type=='MESH' and 'head' in o.name.lower():print('HEAD',o.name,list(o.dimensions),list(o.matrix_world.translation),[m.name for m in o.data.materials])
rig=bpy.data.objects['RIG-einar'];print('HEAD_POS',list(rig.matrix_world@rig.pose.bones['FK-Head'].head))
Path(__file__).with_name('skin-check.json').write_text(json.dumps(r,indent=2))
