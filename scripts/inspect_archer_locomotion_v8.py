"""CPU-only native archer locomotion / roll-compatibility inspection."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];S=R/'assets/v8/licensed/archer/Animations/Blender/HumanF_ArcherAnimationsFREE_2.0.blend';OUT=R/'renders/v8/combat/archer-locomotion-inspection.json'
bpy.ops.wm.open_mainfile(filepath=str(S),use_scripts=False);sc=bpy.context.scene;rig=next(o for o in sc.objects if o.type=='ARMATURE');rig.animation_data_create()
for t in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(t)
report={'source':str(S.relative_to(R)),'fps':sc.render.fps,'rig':rig.name,'bones':{},'actions':[]}
for b in rig.data.bones:report['bones'][b.name]={'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'matrix_local':[list(row) for row in b.matrix_local]}
for a in bpy.data.actions:
 if any(x in a.name.lower() for x in ['run','roll','dodge','sprint','jump','stow','draw']):
  rig.animation_data.action=a
  if hasattr(rig.animation_data,'action_slot') and len(a.slots):rig.animation_data.action_slot=a.slots[0]
  start,end=map(float,a.frame_range);row={'name':a.name,'range':[start,end],'duration':(end-start)/sc.render.fps,'samples':[]}
  for f in [max(1,start),end]:
   sc.frame_set(int(f));bpy.context.view_layer.update();ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());row['samples'].append({'frame':f,'object_translation':list(rig.matrix_world.translation),'bones':{n:list((ev.matrix_world@ev.pose.bones[n].matrix).translation) for n in ['B-root','B-hips','B-foot.L','B-foot.R'] if n in rig.pose.bones}})
  if 'B-root' in row['samples'][0]['bones']:row['root_travel']=list(Vector(row['samples'][1]['bones']['B-root'])-Vector(row['samples'][0]['bones']['B-root']))
  report['actions'].append(row)
report['all_action_names']=[a.name for a in bpy.data.actions];OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2));print(json.dumps({'source':report['source'],'fps':report['fps'],'bones':len(report['bones']),'actions':report['actions']},indent=2))
