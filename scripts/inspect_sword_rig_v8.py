from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];out={}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'assets/v8/combat/quaternius/UAL2_Standard.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
out['source_rig']={'name':rig.name,'matrix':list(map(list,rig.matrix_world)), 'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'matrix':list(map(list,b.matrix_local))} for b in rig.data.bones], 'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions]}
for t in rig.animation_data.nla_tracks:t.mute=True
sample={}
for name in ['Sword_Regular_Combo','Sword_Block','Sword_Dash_RM','Hit_Knockback_RM']:
 a=bpy.data.actions[name];rig.animation_data.action=a
 if len(a.slots):rig.animation_data.action_slot=a.slots[0]
 p=[]
 for f in [int(a.frame_range[0]),int(a.frame_range[1])]:
  bpy.context.scene.frame_set(f);p.append({'frame':f,'rig_location':list(rig.location),'root':list(rig.pose.bones['root'].head) if 'root' in rig.pose.bones else None,'hips':list(rig.pose.bones['pelvis'].head) if 'pelvis' in rig.pose.bones else None,'hand_r':list(rig.pose.bones['hand_r'].head)})
 sample[name]=p
out['motion_endpoints']=sample
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/v8/combat/uplon/uplon.blend'),load_ui=False,use_scripts=False)
out['sword']={'objects':[{'name':o.name,'type':o.type,'dim':list(o.dimensions),'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'vertices':len(o.data.vertices) if o.type=='MESH' else None,'bounds_local':[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)] if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []} for o in bpy.context.scene.objects], 'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images]}
(R/'renders/v8/combat/sword-rig-inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['sword'],indent=2))
