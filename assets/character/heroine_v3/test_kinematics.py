import bpy,sys,math,json
from pathlib import Path
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
data=bpy.data.armatures.new('synthetic');rig=bpy.data.objects.new('synthetic',data);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(n,h,t,parent=None):
 b=data.edit_bones.new(n);b.head=h;b.tail=t
 if parent:b.parent=data.edit_bones[parent]
 return b
bone('Hips',(0,0,.9),(0,0,1.05));bone('Spine',(0,0,1.05),(0,0,1.4),'Hips');bone('Head',(0,0,1.4),(0,0,1.7),'Spine')
for s,x in [('Left',.1),('Right',-.1)]:
 bone(s+'UpLeg',(x,0,.9),(x,-.02,.5),'Hips');bone(s+'Leg',(x,-.02,.5),(x,0,.10),s+'UpLeg');bone(s+'Foot',(x,0,.1),(x,-.12,.05),s+'Leg');bone(s+'ToeBase',(x,-.12,.05),(x,-.20,.05),s+'Foot')
 bone(s+'Arm',(x,0,1.4),(x*4,0,1.4),'Spine')
bpy.ops.object.mode_set(mode='OBJECT')
for f in range(1,30):
 for side,sgn in [('Left',1),('Right',-1)]:
  b=rig.pose.bones[side+'Arm'];b.rotation_mode='XYZ';b.rotation_euler=(.12*math.sin((f-1)*2*math.pi/28),0,sgn*1.3);b.keyframe_insert('rotation_euler',frame=f)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.86));mesh=bpy.context.object;mesh.scale=(.6,.25,1.72);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
g=mesh.vertex_groups.new(name='Hips');g.add(list(range(len(mesh.data.vertices))),1,'REPLACE');mod=mesh.modifiers.new('skin','ARMATURE');mod.object=rig
bpy.ops.wm.save_as_mainfile(filepath='/tmp/heroine_synthetic.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
from heroine_v3 import add_heroine
r=add_heroine(model_path='/tmp/heroine_synthetic.blend',source_cycle=(1,29));rig=r['rig'];results={}
for f in [1,8,15,22,64,240,252,576]:
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update();results[f]={n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ['LeftFoot','RightFoot']}
print('KINEMATICS',json.dumps(results));print('DONE')
