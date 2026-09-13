"""Small CPU proof of licensed native feminine bow animations; no source export."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];D=R/'assets/v8/licensed/archer/Animations/Blender';O=R/'previews/v8/combat/bow-shot-frames';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'HumanF_ArcherAnimationsFREE_2.0.blend'),load_ui=False,use_scripts=False)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
sc=bpy.context.scene;rig=bpy.data.objects['Rig']
for t in rig.animation_data.nla_tracks:t.mute=True
for o in list(sc.objects):
 if o.type in ['CAMERA','LIGHT'] or o.name=='Human_BycocketHat':bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(D/'HumanArcherAnimations_BowAndProps.blend'),link=False) as (src,dst):dst.objects=['Human_Bow','Human_BowMesh','Human_Arrow']
for o in dst.objects:sc.collection.objects.link(o)
bow=bpy.data.objects['Human_Bow'];arrow=bpy.data.objects['Human_Arrow']
print('bow matrix',list(map(list,bow.matrix_world)));print('arrow',arrow.location[:],arrow.rotation_euler[:]);print('bow bones',[(b.name,list(b.head_local),list(b.tail_local)) for b in bow.data.bones]);
for o in sc.objects:
 if o.type!='MESH':continue
 m=bpy.data.materials.new('native preview '+o.name);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.13,.29,.36,1) if 'Body' in o.name else (.2,.09,.04,1);bs.inputs['Roughness'].default_value=.56;o.data.materials.clear();o.data.materials.append(m)
rig.animation_data.action=bpy.data.actions['HumanF@BowShot01 - Hold'];rig.animation_data.action_slot=rig.animation_data.action.slots[0];sc.frame_set(15);bpy.context.view_layer.update()
# Preview attachment: prop bone is the author's dedicated attachment point.
basebow=bow.matrix_world.copy()
curve=bpy.data.curves.new('bowstring preview','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=1;sp=curve.splines.new('POLY');sp.points.add(2);string=bpy.data.objects.new('bowstring preview',curve);sc.collection.objects.link(string)
def props(release_frame=None):
 left=(rig.matrix_world@rig.pose.bones['B-handProp.L'].matrix).translation
 right=(rig.matrix_world@rig.pose.bones['B-handProp.R'].matrix).translation
 x=(left-right).normalized();z=Vector((0,0,1));y=z.cross(x).normalized();z=x.cross(y).normalized();basis=Matrix((x,y,z)).transposed().to_4x4();basis.translation=left
 bow.matrix_world=basis@Matrix.Diagonal((.85,.85,.85,1))
 arrow.matrix_world=Matrix.Translation(right)@x.to_track_quat('Z','Y').to_matrix().to_4x4()
 nock=right
 if release_frame is not None:
  arrow.hide_render=release_frame>4
  arrow.matrix_world.translation=right+x*max(0,release_frame-1)*.8
  nock=bow.matrix_world@Vector((-.327,0,0))
 for p,co in zip(sp.points,[bow.matrix_world@Vector((-.327,0,.924)),nock,bow.matrix_world@Vector((-.327,0,-.924))]):p.co=(*co,1)
props();bpy.context.view_layer.update()
print('rigmatrix',list(map(list,rig.matrix_world)));print('hands',[(n,list((rig.matrix_world@rig.pose.bones[n].matrix).translation)) for n in ['B-hand.L','B-hand.R','B-handProp.L','B-handProp.R']])
center=Vector((0,0,.95));span=1.8
bpy.ops.object.camera_add(location=(3,-4,2.2));cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.1;sc.camera=cam
for off,power in [((1,-1,1.8),100),((-1,-.5,1),50),((0,1,1.2),150)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(off)*span);o=bpy.context.object;o.data.energy=power*span*span;o.data.size=span*1.5;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
sc.world=bpy.data.worlds.new('studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.05,.065,.085,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=4;sc.cycles.use_denoising=True;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if '--still' in sys.argv:
 sc.render.filepath=str(O.parent/'bow-hold-native.png');bpy.ops.render.render(write_still=True)
else:
 i=0
 for action,start,end in [('HumanF@BowShot01 - Load',1,26),('HumanF@BowShot01 - Hold',1,41),('HumanF@BowShot01 - Release',1,25)]:
  rig.animation_data.action=bpy.data.actions[action];rig.animation_data.action_slot=rig.animation_data.action.slots[0]
  for frame in range(start,end+1):
   sc.frame_set(frame);bpy.context.view_layer.update();props(frame if 'Release' in action else None);sc.render.filepath=str(O/f'{i:04d}.png');bpy.ops.render.render(write_still=True);i+=1
