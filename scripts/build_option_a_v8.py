"""Option A: local-only licensed source proxy, bow versus forest guardian.

Build only. Rendering is a separate coordinated command. Functions prepare_forest,
add_archer, bake_archer_props and setup_camera are reusable by the bear option.
No handlers or embedded scripts are required by the saved scene.
"""
from pathlib import Path
import bpy, math, random, json
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1]
LICENSED=R/'assets/v8/licensed/archer/Animations/Blender'
OUT=R/'previews/v8/options/a';OUT.mkdir(parents=True,exist_ok=True)

def mat(name,color,rough=.65,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m

def prepare_forest():
 bpy.ops.wm.open_mainfile(filepath=str(R/'forest-v8-layout.blend'),load_ui=False,use_scripts=False)
 sc=bpy.context.scene
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 actor=bpy.data.objects.get('Heroine v4 • native root motion')
 if actor:
  for ob in [*actor.children_recursive,actor]:bpy.data.objects.remove(ob,do_unlink=True)
 for ob in list(sc.objects):
  if ob.type == 'CAMERA' or 'mist volume' in ob.name.lower():
   bpy.data.objects.remove(ob,do_unlink=True)
   continue
  elif ob.name.startswith('V8 | distant forest') or (ob.instance_type=='COLLECTION' and (ob.location.x>-.2 or ob.location.y < -28)):
   ob.hide_render=True
  if ob.name.startswith('V8 | linked fir') and ob.location.x > 0 and -28 < ob.location.y < -12:
   ob.hide_render=False
 for m in list(sc.timeline_markers):sc.timeline_markers.remove(m)
 sc.frame_start=1;sc.frame_end=96;sc.render.fps=12
 sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=8;sc.render.resolution_x=768;sc.render.resolution_y=432;sc.render.resolution_percentage=100;sc.render.film_transparent=False;sc.render.use_compositing=False
 sc['review_label']='OPTION A — BOW / FOREST GUARDIAN — SOURCE ACTOR PROXY';sc['licensed_source']='LOCAL ONLY: Kevin Iglesias archer source; do not publish this .blend';sc['purpose']='8 second choreography comparison before final heroine retargeting'
 return sc

def nla(obj,clips):
 obj.animation_data_create();obj.animation_data.action=None
 for t in list(obj.animation_data.nla_tracks):obj.animation_data.nla_tracks.remove(t)
 tr=obj.animation_data.nla_tracks.new();tr.name='A | Native source performance'
 for name,start,end,srcstart,srcend in clips:
  a=bpy.data.actions[name];s=tr.strips.new(name,int(start),a);s.action_frame_start=srcstart;s.action_frame_end=srcend;s.frame_start=start;s.frame_end=end;s.extrapolation='HOLD_FORWARD';s.blend_type='REPLACE'
  if hasattr(s,'action_slot') and len(a.slots):s.action_slot=a.slots[0]
 return tr

def bake_visual_source_rig(sc,rig):
 # Native author controls include world-space constraints. Bake evaluated bone
 # transforms at the source origin before placing/rotating the complete actor.
 cache={}
 for f in range(1,97):
  sc.frame_set(f);bpy.context.view_layer.update();ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());cache[f]={b.name:b.matrix.copy() for b in ev.pose.bones}
 rig.animation_data_clear()
 for c in list(rig.constraints):rig.constraints.remove(c)
 for b in rig.pose.bones:
  for c in list(b.constraints):b.constraints.remove(c)
  b.rotation_mode='QUATERNION'
 for f,poses in cache.items():
  sc.frame_set(f)
  for b in rig.pose.bones:
   kwargs={} if b.parent is None else {'parent_matrix':poses[b.parent.name],'parent_matrix_local':b.parent.bone.matrix_local}
   b.matrix_basis=b.bone.convert_local_to_pose(poses[b.name],b.bone.matrix_local,invert=True,**kwargs);b.keyframe_insert('location',frame=f,group=b.name);b.keyframe_insert('rotation_quaternion',frame=f,group=b.name);b.keyframe_insert('scale',frame=f,group=b.name)
 rig.animation_data.action.name='A | baked native feminine bow performance'

def add_archer(sc):
 with bpy.data.libraries.load(str(LICENSED/'HumanF_ArcherAnimationsFREE_2.0.blend'),link=False) as (src,dst):
  dst.objects=['Rig','HumanF_BodyMesh'];dst.actions=[a for a in src.actions if a.startswith('HumanF@Bow')]
 for o in dst.objects:sc.collection.objects.link(o)
 rig=next(o for o in dst.objects if o.type=='ARMATURE');body=next(o for o in dst.objects if o.type=='MESH')
 place=bpy.data.objects.new('A | archer placement',None);sc.collection.objects.link(place);place.location=(0,0,0);place.rotation_euler.z=0
 for o in dst.objects:
  if o.parent is None:o.parent=place
 body.data.materials.clear();body.data.materials.append(mat('A | proxy explorer suit',(.12,.3,.34),.6))
 nla(rig,[('HumanF@BowIdle01',1,25,1,51),('HumanF@BowShot01 - Load',25,36,1,26),('HumanF@BowShot01 - Hold',36,60,1,41),('HumanF@BowShot01 - Release',60,71,1,25),('HumanF@BowIdle01',71,97,1,51)])
 bake_visual_source_rig(sc,rig)
 place.location=(-3.8,-20,.14);place.rotation_euler.z=math.pi
 with bpy.data.libraries.load(str(LICENSED/'HumanArcherAnimations_BowAndProps.blend'),link=False) as (src,dst):dst.objects=['Human_Bow','Human_BowMesh','Human_Arrow']
 for o in dst.objects:sc.collection.objects.link(o)
 bow=next(o for o in dst.objects if o.type=='ARMATURE');arrow=next(o for o in dst.objects if o.name.startswith('Human_Arrow'));bowmesh=next(o for o in dst.objects if o.name.startswith('Human_BowMesh'))
 for o in [bowmesh,arrow]:o.data.materials.clear();o.data.materials.append(mat('A | wooden equipment',(.2,.08,.025),.4))
 curve=bpy.data.curves.new('A | working bowstring','CURVE');curve.dimensions='3D';curve.bevel_depth=.003;curve.bevel_resolution=1;sp=curve.splines.new('POLY');sp.points.add(2);string=bpy.data.objects.new('A | working bowstring',curve);sc.collection.objects.link(string);curve.materials.append(mat('A | bowstring',(.62,.56,.4)))
 return {'rig':rig,'body':body,'place':place,'bow':bow,'arrow':arrow,'string':string,'spline':sp}

def blend_guardian_walk_to_hold(rig):
 # Keep Walk held underneath the upright stance for a five-frame crossfade.
 # Timing of the native attack and arrow release remains unchanged.
 base=rig.animation_data.nla_tracks[0]
 later=[(s.name,s.action,s.frame_start,s.frame_end,s.action_frame_start,s.action_frame_end) for s in list(base.strips)[2:]]
 for s in list(base.strips)[2:]:base.strips.remove(s)
 tr=rig.animation_data.nla_tracks.new(prev=base);tr.name='A | smooth native guardian stance'
 for index,(name,action,start,end,srcstart,srcend) in enumerate(later):
  s=tr.strips.new(name,int(start),action);s.action_frame_start=srcstart;s.action_frame_end=srcend;s.frame_start=start;s.frame_end=end;s.extrapolation='HOLD_FORWARD';s.blend_type='REPLACE'
  if hasattr(s,'action_slot') and len(action.slots):s.action_slot=action.slots[0]
  if index==0:s.blend_in=5

def add_guardian(sc):
 p=R/'assets/v8/combat/forest-monster/forest-monster-final.blend'
 with bpy.data.libraries.load(str(p),link=False) as (src,dst):dst.objects=['Armature','Monster'];dst.actions=['Idle','Walk','Attack','Melee_Hold']
 for o in dst.objects:sc.collection.objects.link(o)
 rig=next(o for o in dst.objects if o.type=='ARMATURE');body=next(o for o in dst.objects if o.type=='MESH')
 place=bpy.data.objects.new('A | guardian placement',None);sc.collection.objects.link(place);place.location=(-3.8,-14.9,.14);place.scale=(.105,)*3
 for o in dst.objects:
  if o.parent is None:o.parent=place
 m=mat('A | weathered guardian stone',(.22,.28,.12),.85);nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
 for fname,socket in [('forest-monster-skin1.png','Base Color')]:
  t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(p.parent/'texture'/fname),check_existing=True);links.new(t.outputs['Color'],bs.inputs[socket])
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(p.parent/'texture/forest-monster-norm.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';n=nodes.new('ShaderNodeNormalMap');links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bs.inputs['Normal']);body.data.materials.clear();body.data.materials.append(m)
 nla(rig,[('Walk',1,21,0,40),('Walk',21,41,0,40),('Melee_Hold',41,50,0,18),('Attack',50,66,0,30),('Melee_Hold',66,97,0,50)])
 blend_guardian_walk_to_hold(rig)
 # Native in-place foot sweep ≈.25 source units/frame; .105 scale gives .63m/s.
 for f,y in [(1,-14.9),(41,-17.0),(96,-17.0)]:place.location.y=y;place.keyframe_insert('location',frame=f)
 for fc in place.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 # Author the impact recoil on the source rig's upper-body IK controller.
 action=bpy.data.actions.new('A | authored stone impact recoil');rig.animation_data.action=action
 b=rig.pose.bones['IK-Spine'];b.rotation_mode='QUATERNION'
 for f,angle in [(1,0),(62,0),(65,-.18),(70,.075),(78,0),(96,0)]:b.rotation_quaternion=Quaternion((1,0,0),angle);b.keyframe_insert('rotation_quaternion',frame=f,group=b.name)
 rig.animation_data.action=None;tr=rig.animation_data.nla_tracks.new();tr.name='A | authored impact recoil';s=tr.strips.new(action.name,1,action);s.blend_type='COMBINE';s.extrapolation='HOLD_FORWARD'
 return {'rig':rig,'body':body,'place':place}

def setup_camera(sc):
 def cam(name,frame,pos,target,lens):
  d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=200;mark=sc.timeline_markers.new(name,frame=frame);mark.camera=o;return o
 sc.camera=cam('A | forest encounter wide',1,(-14.5,-18.2,3.2),(-3.8,-18.2,1.4),34)
 cam('A | draw and anchor',36,(-7.7,-22.1,1.8),(-3.75,-19.65,1.25),36)
 cam('A | arrow impact and recovery',60,(-13.8,-18.2,2.8),(-3.8,-18.3,1.45),34)

def bake_archer_props(sc,actor,target_provider,release=60,impact=63):
 rig,bow,arrow=actor['rig'],actor['bow'],actor['arrow'];sp=actor['spline'];release_origin=None;release_target=None;rot=None
 for f in range(1,97):
  sc.frame_set(f);bpy.context.view_layer.update()
  left=(rig.matrix_world@rig.pose.bones['B-handProp.L'].matrix).translation;right=(rig.matrix_world@rig.pose.bones['B-handProp.R'].matrix).translation
  x=(left-right).normalized();z=Vector((0,0,1));y=z.cross(x).normalized();z=x.cross(y).normalized();basis=Matrix((x,y,z)).transposed().to_4x4();basis.translation=left;bow.matrix_world=basis@Matrix.Diagonal((.85,.85,.85,1));bow.rotation_mode='QUATERNION';bow.keyframe_insert('location',frame=f);bow.keyframe_insert('rotation_quaternion',frame=f);bow.keyframe_insert('scale',frame=f)
  nock=right
  if f<release:
   arrow.matrix_world=Matrix.Translation(right)@x.to_track_quat('Z','Y').to_matrix().to_4x4()
  else:
   if release_origin is None:
    release_origin=right.copy();release_target=Vector(target_provider(impact));rot=(release_target-release_origin).to_track_quat('Z','Y')
   nock=bow.matrix_world@Vector((-.327,0,0));t=min(1,(f-release)/max(1,impact-release));point=release_origin.lerp(release_target,t)
   if f>=impact:point=Vector(target_provider(f))
   arrow.matrix_world=Matrix.Translation(point)@rot.to_matrix().to_4x4()
  arrow.rotation_mode='QUATERNION';arrow.keyframe_insert('location',frame=f);arrow.keyframe_insert('rotation_quaternion',frame=f)
  # Arrow local Z runs forward from its nock; retract so its tip meets the stone.
  if f>=impact:
   arrow.location-=rot@Vector((0,0,.8));arrow.keyframe_insert('location',frame=f)
  for p,co in zip(sp.points,[bow.matrix_world@Vector((-.327,0,.924)),nock,bow.matrix_world@Vector((-.327,0,-.924))]):p.co=(*co,1);p.keyframe_insert('co',frame=f)
 return release_target

def impact_fx(sc,point,frame=63):
 rng=random.Random(808);spark=mat('A | stone impact sparks',(1,.35,.055),emission=8);stone=mat('A | stone fragments',(.14,.18,.1))
 for i in range(22):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.025 if i<14 else .065,location=point);o=bpy.context.object;o.name=f'A | impact fragment {i:02d}';o.data.materials.append(spark if i<14 else stone)
  vec=Vector((rng.uniform(-2,2),rng.uniform(-2,-.3),rng.uniform(.5,2.5)))
  for f in [1,frame-1,frame,frame+3,frame+7,96]:
   t=max(0,(f-frame)/12);o.location=Vector(point)+vec*t+Vector((0,0,-4.9*t*t));o.scale=(1,)*3 if frame<=f<=frame+5 else (.001,)*3;o.keyframe_insert('location',frame=f);o.keyframe_insert('scale',frame=f)

def main():
 sc=prepare_forest();actor=add_archer(sc);guard=add_guardian(sc);setup_camera(sc)
 # Sample a front chest point in rig space; bake coordinates so no handlers remain.
 points={}
 for f in range(1,97):
  sc.frame_set(f);bpy.context.view_layer.update();p=guard['rig'].matrix_world@guard['rig'].pose.bones['Spine2'].head;points[f]=p+Vector((-.05,-.32,0))
 impact=bake_archer_props(sc,actor,lambda f:points[f]);impact_fx(sc,impact)
 for a in bpy.data.actions:
  if a.name.startswith('A |'):
   for fc in a.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
 sc.frame_set(54);bpy.context.view_layer.update()
 for i in bpy.data.images:
  if i.filepath and not i.packed_file:i.filepath=bpy.path.abspath(i.filepath)
 path=R/'option-a-bow-guardian.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
 report={'option':'A — Bow versus forest guardian','frames':96,'fps':12,'duration':8,'actor':'Native licensed feminine source proxy; not yet retargeted to accepted Rocketbox woman','release_frame':60,'impact_frame':63,'guardian_walk':'Native in-place Walk, 2 cycles, matching2.1m travel over40frames','timeline':['1–24 guardian approaches while woman readies','25–35 load','36–59 hold/aim, guardian winds up','60 release','63 stone impact','64–78 recoil','79–96 recover'],'licensed_source_scene_local_only':True,'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'impact_point':list(impact),'scene':path.name}
 (OUT/'scene-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
