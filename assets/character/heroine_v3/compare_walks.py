import bpy,sys,json
from pathlib import Path
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
from heroine_v3 import _import,_bone
for file in ['walking.glb','walking-woman.glb']:
 bpy.ops.wm.read_factory_settings(use_empty=True);objects=_import('assets/character/heroine_v3/'+file);rig=next(o for o in objects if o.type=='ARMATURE');a=rig.animation_data.action;lo,hi=a.frame_range;sample=[]
 for i in range(24):
  t=lo+(hi-lo)*i/24;bpy.context.scene.frame_set(int(t),subframe=t%1);bpy.context.view_layer.update()
  h=rig.matrix_world@_bone(rig,'Hips').head;hand=rig.matrix_world@_bone(rig,'LeftHand').head;shoulder=rig.matrix_world@_bone(rig,'LeftArm').head
  sample.append([abs(hand.x-h.x),hand.y-h.y,abs(hand.x-shoulder.x)])
 print('WALK_COMPARE',file,'mean_wrist_lateral',sum(s[0] for s in sample)/24,'arm_swing_range',max(s[1] for s in sample)-min(s[1] for s in sample),'hand_outside_shoulder',sum(s[2] for s in sample)/24,flush=True)
