from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'observatory-v7.blend'),use_scripts=False)
s=bpy.context.scene;s.frame_set(478);r=bpy.data.objects['Bip01']
for b in r.pose.bones:
 if b.name.startswith('Bip01 R Finger') or b.name=='Bip01 R Hand':
  print('FINGER',json.dumps({'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(r.matrix_world@b.head),'tail':list(r.matrix_world@b.tail),'q':list(b.rotation_quaternion),'basis':list(b.rotation_quaternion.to_euler()),'rest_length':b.length}))
print('HERO_MESHES',[(o.name,len(o.data.vertices)) for o in r.parent.children_recursive if o.type=='MESH'])
