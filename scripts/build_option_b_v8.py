"""Eight-second source-action sword/guardian selection rehearsal. No final render.

The human is the licensed CC0 source mannequin, not a Rocketbox retarget.
Native roll distance is mapped onto an arc; the full native sword combo root
motion is preserved. Environment, V7 and previous studies are read-only.
"""
from pathlib import Path
import bpy,math,json,sys,hashlib
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'previews/v8/options/b';OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'option-b-sword-guardian.blend'
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def smooth(a,b,f):
 t=max(0,min(1,(f-a)/(b-a)));return t*t*(3-2*t)
def bind_action(rig,action):
 rig.animation_data_create();rig.animation_data.action=action
 for t in rig.animation_data.nla_tracks:t.mute=True
 if hasattr(action,'slots') and len(action.slots):rig.animation_data.action_slot=action.slots[0]
def sample(rig,action,frame):
 bind_action(rig,action);bpy.context.scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update()
 return {b.name:b.matrix.copy() for b in rig.pose.bones}
def rootpos(p):return p['root'].translation.copy()
def matblend(a,b,t):
 la,qa,sa=a.decompose();lb,qb,sb=b.decompose();return Matrix.LocRotScale(la.lerp(lb,t),qa.slerp(qb,t),sa.lerp(sb,t))
def material(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.55;return m

def build():
 source=ROOT/'forest-v8-layout.blend';source_sha=sha(source)
 bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.context.scene
 for ob in list(s.objects):
  if ob.name=='Heroine v4 • native root motion' or ob.name.startswith('Bip01') or ob.name.startswith('f004_') or ob.name.startswith('V8 | forest air depth'):
   bpy.data.objects.remove(ob,do_unlink=True)
 for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
 # Flatten only this study's combat clearing; the discovery scene stays intact.
 center=Vector((-3.8,-14.3,0))
 for ob in s.objects:
  if ob.name=='V8 | gently banked trail terrain':
   ob.data=ob.data.copy()
   for v in ob.data.vertices:
    distance=(Vector((v.co.x,v.co.y,0))-center).length
    weight=1-smooth(5.4,7.2,distance);v.co.z=v.co.z*(1-weight)+.14*weight
  if ob.instance_type=='COLLECTION' and (ob.name.startswith('V8 | fern bank') or ob.name.startswith('V8 | moss stone')):
   if (Vector((ob.location.x,ob.location.y,0))-center).length<4.8:ob.hide_render=True
 s.frame_start=1;s.frame_end=192;s.render.fps=24
 # Import matching animation libraries; use UAL2's native mesh/rig and UAL1's
 # compatible bone actions on the same source skeleton, without retargeting.
 prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/v8/combat/quaternius/UAL1_Standard.glb'))
 first=set(bpy.data.objects)-prior
 human1=next(o for o in first if o.type=='ARMATURE');acts1={n:bpy.data.actions[n] for n in ['Sword_Idle','Roll_RM','Walk_Loop']}
 prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/v8/combat/quaternius/UAL2_Standard.glb'))
 second=set(bpy.data.objects)-prior;human=next(o for o in second if o.type=='ARMATURE')
 combo=bpy.data.actions['Sword_Regular_Combo']
 # Verify identical bind transforms before sharing native source actions.
 assert all(max(abs(v) for row in (human.data.bones[b.name].matrix_local-b.matrix_local) for v in row)<1e-5 for b in human1.data.bones)
 for o in first:bpy.data.objects.remove(o,do_unlink=True)
 human.name='B | SOURCE MANNEQUIN — retarget pending'
 for o in second:
  if o.type=='MESH':o.data.materials.clear();o.data.materials.append(material('B | source mannequin teal',(.11,.39,.48)))
 with bpy.data.libraries.load(str(ROOT/'assets/v8/combat/forest-monster/forest-monster-final.blend'),link=False) as (available,loaded):
  loaded.objects=['Armature','Monster'];loaded.actions=['Idle','Melee_Hold','Attack','Walk']
 guardian,monster=loaded.objects
 for ob in loaded.objects:s.collection.objects.link(ob)
 gacts={a.name.split('.')[0]:a for a in loaded.actions}
 guardian.name='B | Guardian native rig';monster.name='B | Forest guardian'
 monster.data.materials.clear();monster.data.materials.append(material('B | guardian moss stone',(.25,.32,.19)))
 # Recover native body texture for inexpensive Eevee if requested.
 gm=monster.data.materials[0];nodes=gm.node_tree.nodes;links=gm.node_tree.links
 image=bpy.data.images.load(str(ROOT/'assets/v8/combat/forest-monster/texture/forest-monster-skin1.png'),check_existing=True)
 if image:
  tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(tex.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color'])
  norm=nodes.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(ROOT/'assets/v8/combat/forest-monster/texture/forest-monster-norm.png'),check_existing=True);norm.image.colorspace_settings.name='Non-Color'
  bump=nodes.new('ShaderNodeNormalMap');links.new(norm.outputs['Color'],bump.inputs['Color']);links.new(bump.outputs['Normal'],nodes['Principled BSDF'].inputs['Normal']);nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
 with bpy.data.libraries.load(str(ROOT/'assets/v8/combat/uplon/uplon.blend'),link=False) as (a,b):b.objects=['Sword']
 sword=b.objects[0];s.collection.objects.link(sword);sword.name='B | Uplon sword';sword.data=sword.data.copy()
 for v in sword.data.vertices:
  x,y,z=v.co;v.co=(-.25*(x-1.8),.25*z,.25*y)
 sword.location=(0,0,0);sword.rotation_euler=(0,0,0);sword.scale=(1,1,1);sword.data.materials.clear();sword.data.materials.append(material('B | Uplon steel',(.64,.7,.77),.8))
 # Sample all native source poses before replacing actions. Guardian constraint
 # results are baked from evaluated pose matrices, then constraints removed.
 hp={};gp={};root_rows=[];gcenter=Vector((-3.8,-14.3,.14));radius=3.2
 roll_first=rootpos(sample(human,acts1['Roll_RM'],0));roll_last=rootpos(sample(human,acts1['Roll_RM'],35.2));roll_distance=(roll_last-roll_first).length
 combo_first=rootpos(sample(human,combo,0));combo_last=rootpos(sample(human,combo,72));combo_distance=(combo_last-combo_first).length
 theta0=-math.pi/2;theta_end=theta0-roll_distance/radius
 endroll=gcenter+Vector((radius*math.cos(theta_end),radius*math.sin(theta_end),0))
 toward=(gcenter-endroll);toward.z=0;toward.normalize();counter_yaw=math.atan2(toward.x,-toward.y)
 last_pose=None;last_phase=None;blend_from=None
 for f in range(1,193):
  if f<=24:
   phase='guard';pose=sample(human,acts1['Sword_Idle'],(f-1)%40);root=rootpos(pose);pos=gcenter+Vector((0,-radius,0));yaw=math.pi+math.pi/2*smooth(16,28,f)
  elif f<=60:
   phase='evade';u=(f-25)*35.2/35;pose=sample(human,acts1['Roll_RM'],u);root=rootpos(pose);distance=(root-roll_first).length
   theta=theta0-distance/radius;pos=gcenter+Vector((radius*math.cos(theta),radius*math.sin(theta),0));tangent=Vector((math.sin(theta),-math.cos(theta),0));yaw=math.atan2(tangent.x,-tangent.y)
   delta_yaw=(counter_yaw-yaw+math.pi)%(2*math.pi)-math.pi;yaw+=delta_yaw*smooth(55,60,f)
  elif f<=132:
   phase='counter';u=(f-61)*72/71;pose=sample(human,combo,u);root=rootpos(pose);delta=root-combo_first;pos=endroll+Matrix.Rotation(counter_yaw,3,'Z')@Vector((delta.x,delta.y,0));yaw=counter_yaw
  elif f<=168:
   phase='withdraw';u=(32-(f-133))%32;pose=sample(human,acts1['Walk_Loop'],u);root=rootpos(pose);progress=(f-133)/24*.82;pos=endroll+toward*(combo_distance-progress);yaw=counter_yaw
  else:
   phase='guard_out';pose=sample(human,acts1['Sword_Idle'],f-169);root=rootpos(pose);pos=endroll+toward*(combo_distance-35/24*.82);yaw=counter_yaw
  # Remove only the planar source root from the local pose; it is represented
  # exactly once in the actor's world placement above. Native vertical motion
  # (including the roll) stays inside the source pose.
  for n in pose:pose[n].translation-=Vector((root.x,root.y,0))
  if phase!=last_phase:blend_from=last_pose;transition=f;last_phase=phase
  if blend_from is not None and f-transition<5:
   weight=smooth(transition-1,transition+4,f);pose={n:matblend(blend_from[n],m,weight) for n,m in pose.items()}
  last_pose={n:m.copy() for n,m in pose.items()};hp[f]=(pose,pos.copy(),yaw,phase)
  if f<=18:gaction=gacts['Melee_Hold'];gu=(f-1)*.5
  elif f<=49:gaction=gacts['Attack'];gu=(f-19)*30/30
  elif f<=66:gaction=gacts['Melee_Hold'];gu=10
  elif f<=132:gaction=gacts['Walk'];gu=(40-(f-67))%40
  else:gaction=gacts['Melee_Hold'];gu=(f-133)%50
  gpose=sample(guardian,gaction,gu)
  recoil=sum(smooth(hit-2,hit+2,f)*(1-smooth(hit+2,hit+11,f)) for hit in [114])
  if recoil:
   pivot=gpose['Spine2'].translation.copy();turn=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-7)*recoil,4,'X')@Matrix.Translation(-pivot)
   for bone in guardian.data.bones:
    if bone.name=='Spine2' or any(p.name=='Spine2' for p in bone.parent_recursive):gpose[bone.name]=turn@gpose[bone.name]
  gpos=gcenter+toward*(.95*smooth(65,92,f)+.20*smooth(118,132,f))
  # Turn to follow the evasion; settle facing the counter before blade arrives.
  current_human=pos-gpos;gyaw=math.atan2(current_human.x,-current_human.y)
  gp[f]=(gpose,gpos,gyaw,gaction.name,gu)
  root_rows.append({'frame':f,'phase':phase,'human_root':list(pos),'guardian_root':list(gpos)})
 # Bake and remove source constraints, leaving a self-contained editable study.
 for rig in [human,guardian]:
  rig.animation_data_clear();rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new('B | baked '+rig.name)
  for bone in rig.pose.bones:
   for constraint in list(bone.constraints):bone.constraints.remove(constraint)
   bone.rotation_mode='QUATERNION'
  rig.rotation_mode='QUATERNION'
 previous={}
 for f in range(1,193):
  s.frame_set(f)
  for rig,entry,size in [(human,hp[f],1),(guardian,gp[f],.10)]:
   pose,pos,yaw=entry[:3]
   rig.location=pos;rig.rotation_quaternion=Quaternion((0,0,1),yaw);rig.scale=(size,)*3
   rootkey=(rig.name,'__object__')
   if rootkey in previous and rig.rotation_quaternion.dot(previous[rootkey])<0:rig.rotation_quaternion.negate()
   previous[rootkey]=rig.rotation_quaternion.copy()
   for n,m in pose.items():
    bone=rig.pose.bones[n];rest=rig.data.bones[n].matrix_local
    if bone.parent:bone.matrix_basis=rest.inverted()@rig.data.bones[bone.parent.name].matrix_local@pose[bone.parent.name].inverted()@m
    else:bone.matrix_basis=rest.inverted()@m
    key=(rig.name,n)
    if key in previous and bone.rotation_quaternion.dot(previous[key])<0:bone.rotation_quaternion.negate()
    previous[key]=bone.rotation_quaternion.copy()
    for prop in ['location','rotation_quaternion','scale']:bone.keyframe_insert(prop,frame=f,group=n)
   for prop in ['location','rotation_quaternion','scale']:rig.keyframe_insert(prop,frame=f)
  bpy.context.view_layer.update()
  sword.matrix_world=human.matrix_world@human.pose.bones['hand_r'].matrix@Matrix.Translation((0,.08,0));sword.rotation_mode='QUATERNION'
  for prop in ['location','rotation_quaternion','scale']:sword.keyframe_insert(prop,frame=f)
 for rig in [human,guardian,sword]:
  for fc in rig.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 # A restrained camera move keeps complete bodies and the weapon visible.
 cam=bpy.data.objects.new('B | Fight selection camera',bpy.data.cameras.new('B | Fight selection camera'));s.collection.objects.link(cam)
 cam.data.lens=34;cam.data.clip_end=250;cam.rotation_mode='QUATERNION'
 for f,pos,target in [(1,(-12,-21.5,3.4),(-5,-15.5,1.45)),(192,(-12,-19.8,3.1),(-5,-15,1.45))]:
  cam.location=pos;cam.rotation_quaternion=(Vector(target)-cam.location).to_track_quat('-Z','Y');cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f)
 s.camera=cam;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=768;s.render.resolution_y=432;s.render.resolution_percentage=100
 s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_motion_blur=False
 sh=s.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.07,.10,.12)
 s.frame_set(85)
 bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
 assert sha(source)==source_sha
 report={'option':'B — sword versus forest guardian','status':'paired source-motion selection study; production retarget pending','human':'Quaternius CC0 native mannequin proxy, not accepted Rocketbox heroine','frames':192,'source_fps':24,'preview_frames':96,'preview_fps':12,'duration_seconds':8,'scene':DEST.name,'scene_sha256':sha(DEST),'forest_source_sha256':source_sha,'heavy_render':False,'native_roll_distance_m':roll_distance,'roll_arc_radius_m':radius,'native_combo_distance_m':combo_distance,'timeline':[{'frames':[1,24],'action':'Threat recognition / sword guard'},{'frames':[25,60],'action':'Native rolling evade around committed guardian attack'},{'frames':[61,132],'action':'Complete native sword combo; guardian gives ground'},{'frames':[133,192],'action':'Backward withdrawal and guard'}],'limitations':['Source human proxy; Rocketbox retargeting remains pending user selection.','Roll translation remapped onto a curved path; exact contact/foot cleanup not a finished choreography.','Guardian gives ground with reversed native Walk and a small authored spine recoil at measured blade impacts; exact collision cleanup remains pending.','Workbench lighting; no final materials, effects or sound.'],'root_samples':root_rows}
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('B_BUILD_READY',DEST)

def render():
 bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False);s=bpy.context.scene
 s.render.engine='BLENDER_WORKBENCH';s.render.image_settings.file_format='PNG';s.render.resolution_x=768;s.render.resolution_y=432
 frames=[1,35,49,61,85,109,132,168] if '--stills' in ARGS else list(range(1,193,2))
 folder=OUT/('stills' if '--stills' in ARGS else 'frames');folder.mkdir(parents=True,exist_ok=True)
 for i,f in enumerate(frames,1):
  s.frame_set(f);s.render.filepath=str(folder/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
 print('B_RENDER_READY',len(frames))
def audit():
 from mathutils.bvhtree import BVHTree
 bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False)
 s=bpy.context.scene;monster=bpy.data.objects['B | Forest guardian'];human=bpy.data.objects['B | SOURCE MANNEQUIN — retarget pending'];sword=bpy.data.objects['B | Uplon sword']
 meshes=[o for o in s.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==human for m in o.modifiers)]
 intersections=[];contacts=[]
 for frame in range(1,193):
  s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
  def tree(ob):
   evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();vertices=[evaluated.matrix_world@v.co for v in mesh.vertices];polygons=[list(p.vertices) for p in mesh.polygons];result=BVHTree.FromPolygons(vertices,polygons);evaluated.to_mesh_clear();return result
  guardian_tree=tree(monster)
  pairs=sum(len(guardian_tree.overlap(tree(ob))) for ob in meshes)
  if pairs:intersections.append({'frame':frame,'intersecting_triangle_pairs':pairs})
  if 61<=frame<=132:
   samples=[]
   for v in [v for v in sword.data.vertices if v.co.x>.12][::8]:
    point=sword.matrix_world@v.co;hit,normal,index,distance=guardian_tree.find_nearest(point)
    if hit is not None:samples.append((distance,list(point),list(hit)))
   best=min(samples);contacts.append({'frame':frame,'blade_surface_distance_m':best[0],'blade_point':best[1],'guardian_surface':best[2]})
 scene_hash=sha(DEST)
 body={'status':'passed' if not intersections else 'intersections_found','scene_sha256':scene_hash,'method':'Evaluated character and guardian mesh triangle overlap at all192frames','intersections':intersections}
 (OUT/'body-contact-qa.json').write_text(json.dumps(body,indent=2)+'\n')
 contact={'status':'diagnostic closest blade surface samples; not full weapon collision QA','scene_sha256':scene_hash,'minimum':min(contacts,key=lambda x:x['blade_surface_distance_m']),'rows':contacts}
 (OUT/'contact-samples.json').write_text(json.dumps(contact,indent=2)+'\n')
 print('B_BODY_QA',body['status'],'CONTACT',contact['minimum'])
 assert not intersections
if '--render' in ARGS:render()
elif '--audit' in ARGS:audit()
else:build()
