import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
from heroine_v3 import _import,_norm
args=sys.argv[sys.argv.index('--')+1:];path=args[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
objects=_import(path);out={'path':path,'objects':[],'rigs':{},'images':[],'materials':[]}
for o in objects:
 item={'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'matrix_world':[list(r) for r in o.matrix_world],'vertices':len(o.data.vertices) if o.type=='MESH' else None,'polygons':len(o.data.polygons) if o.type=='MESH' else None,'modifiers':[(m.name,m.type) for m in o.modifiers]}
 out['objects'].append(item)
 if o.type=='ARMATURE':
  ri={'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length,'parent':b.parent.name if b.parent else None} for b in o.data.bones], 'action':None}
  if o.animation_data:
   a=o.animation_data.action
   if not a:
    strips=[s for t in o.animation_data.nla_tracks for s in t.strips if s.action]
    if strips:
     a=strips[0].action;o.animation_data.action=a
     for t in o.animation_data.nla_tracks:t.mute=True
   if a:
    ri['action']={'name':a.name,'range':list(a.frame_range)};bone_lookup={_norm(b.name):b for b in o.pose.bones};ri['motion']=[]
    hips=bone_lookup.get('hips');left=bone_lookup.get('leftfoot');right=bone_lookup.get('rightfoot');toe=bone_lookup.get('lefttoebase')
    if all([hips,left,right,toe]):
     forward=o.matrix_world.to_3x3()@(toe.bone.head_local-left.bone.head_local);forward.z=0;forward.normalize()
     for f in range(math.floor(a.frame_range[0]),math.ceil(a.frame_range[1])+1):
      bpy.context.scene.frame_set(f);bpy.context.view_layer.update();h=o.matrix_world@hips.head;l=o.matrix_world@left.head;r=o.matrix_world@right.head
      ri['motion'].append({'f':f,'left_forward':(l-h).dot(forward),'right_forward':(r-h).dot(forward),'left_height':l.z,'right_height':r.z,'hips':list(h)})
     motion=ri['motion'];peaks=[motion[i]['f'] for i in range(1,len(motion)-1) if motion[i]['left_forward']>motion[i-1]['left_forward'] and motion[i]['left_forward']>=motion[i+1]['left_forward']]
     ri['left_contact_candidates']=peaks
  out['rigs'][o.name]=ri
for i in bpy.data.images:out['images'].append({'name':i.name,'size':list(i.size),'filepath':i.filepath,'packed':bool(i.packed_file),'source':i.source})
for m in bpy.data.materials:
 if m.use_nodes:out['materials'].append({'name':m.name,'nodes':[(n.name,n.type) for n in m.node_tree.nodes]})
destination=Path(args[1]) if len(args)>1 else BASE/'assets/character/heroine_v3/asset-inspection.json';destination.write_text(json.dumps(out,indent=2));print('INSPECTED',destination)
