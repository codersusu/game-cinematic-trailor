import bpy,json
out={}
for m in bpy.data.materials:
 if m.name in ['MAT-rain.top','MAT-rain.jeans','MAT-rain.scarf','MAT-rain.shoes','MAT-rain.laces','MAT-rain.socks']:
  out[m.name]=[{'name':n.name,'type':n.type,'inputs':[(s.name,list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value) for s in n.inputs if hasattr(s,'default_value') and s.name in ['Base Color','Color','Roughness']]} for n in m.node_tree.nodes]
print('MATS',json.dumps(out))
for n in ['FK-Hair_Ponytail1','FK-Hair_Ponytail2']:
 b=bpy.data.objects['RIG-rain'].data.bones[n];print(n,'xaxis',b.x_axis[:])
print('BLINK',[b.name for b in bpy.data.objects['RIG-rain'].pose.bones if 'blink' in b.name.lower()])
