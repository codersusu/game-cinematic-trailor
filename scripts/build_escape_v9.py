"""Local shoot/dodge/escape camera study; no production render."""
from pathlib import Path
import bpy,sys,math,json,bmesh
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from escape_actor_motion_v9 import sample_escape_motion
from escape_cameras_v9 import add_escape_cameras
OUT=ROOT/'previews/v9';OUT.mkdir(parents=True,exist_ok=True)
N=144

def ease(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def mixpose(a,b,t):return {n:a[n].lerp(m,t) for n,m in b.items()}
def sample_pose(sc,rig,f):
 sc.frame_set(math.floor(f),subframe=f%1);bpy.context.view_layer.update();return {b.name:b.matrix.copy() for b in rig.pose.bones}
def shot_time(f):
 for a,b,x,y in [(1,9,1,25),(9,20,25,36),(20,32,36,60),(32,40,60,71)]:
  if f<=b:return x+(y-x)*(f-a)/(b-a)
 return 71

def arc_path(controls):
 pts=[Vector(p) for p in controls];raw=[]
 for i in range(len(pts)-1):
  p0=pts[max(0,i-1)];p1=pts[i];p2=pts[i+1];p3=pts[min(i+2,len(pts)-1)]
  for k in range(60):
   t=k/60;raw.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 raw.append(pts[-1]);lengths=[0.]
 for a,b in zip(raw,raw[1:]):lengths.append(lengths[-1]+(b-a).length)
 def at(u):
  d=max(0,min(1,u))*lengths[-1]
  for i in range(1,len(raw)):
   if lengths[i]>=d:
    t=(d-lengths[i-1])/max(1e-9,lengths[i]-lengths[i-1]);p=raw[i-1].lerp(raw[i],t);v=(raw[i]-raw[i-1]).normalized();return p,math.atan2(v.x,-v.y)
  return raw[-1],math.pi
 return at,lengths[-1]

def terrain_and_door(sc):
 # A continuous clear route around the committed attack and up to the airlock.
 for ob in sc.objects:
  if ob.name=='V8 | gently banked trail terrain':
   ob.data=ob.data.copy()
   for v in ob.data.vertices:
    if -11<v.co.x<.5 and -26<v.co.y<-3:v.co.z=.14
  if ob.instance_type=='COLLECTION':
   x,y=ob.location.x,ob.location.y
   if -11<x<-.5 and -25<y<-6 and any(k in ob.name for k in ['fern bank','moss stone','fallen timber','exposed roots','linked fir']):ob.hide_render=True
 for ob in sc.objects:
  if ob.name.startswith('V5 | sliding airlock leaf'):
   side=-1 if ob.name.endswith('-1') else 1;ob.animation_data_clear()
   for f,x in [(1,.8),(119,.8),(138,2.6),(144,2.6)]:ob.location.x=side*x;ob.keyframe_insert('location',frame=f)
 # The review only needs a suggestion of the interior beyond the opening.
 from build_option_a_v8 import mat
 wall=mat('V9 | vestibule titanium',(.09,.14,.18),.5,.45);strip=mat('V9 | cyan entry guide',(.08,.65,1),.4,emission=4)
 def box(name,loc,scale,material):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 box('V9 | entry floor',(-3.8,-3.8,.09),(3.2,4,.10),wall)
 box('V9 | vestibule left',(-5.3,-3.8,1.6),(.12,4,3.2),wall);box('V9 | vestibule right',(-2.3,-3.8,1.6),(.12,4,3.2),wall)
 box('V9 | vestibule back',(-3.8,-1.7,1.6),(3.2,.12,3.2),wall)
 for x in [-5.05,-2.55]:box('V9 | entry guide', (x,-3.8,.151),(.025,3.7,.018),strip)
 d=bpy.data.lights.new('V9 | doorway spill','AREA');o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=(-3.8,-4,2.8);o.rotation_euler=(Vector((-3.8,-8,.3))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=180;d.color=(.2,.62,1);d.shape='DISK';d.size=3

def actor_motion(sc,rig):
 shot={f:sample_pose(sc,rig,shot_time(f)) for f in range(1,41)}
 native=sample_escape_motion(sc,rig)
 roll_end=-3.8-native['roll_distance']
 path,length=arc_path([(roll_end,-20,.14),(roll_end-.15,-16,.14),(-7.7,-11.7,.14),(-4.5,-8.7,.14),(-3.8,-6.35,.14)])
 poses={};rows=[];previous=None
 for f in range(1,N+1):
  if f<=40:phase='shoot';pose=shot[f];pos=Vector((-3.8,-20,.14));yaw=math.pi
  elif f<=50:
   phase='sheathe';pose=native['sheathe'][f-41];pos=Vector((-3.8,-20,.14));yaw=math.pi+math.pi*.5*ease(45,51,f)
   if f<=43:pose=mixpose(shot[40],pose,ease(40,44,f))
  elif f<=68:
   phase='roll';idx=f-51;pose=native['roll'][idx];pos=Vector((-3.8-native['roll_distance']*native['roll_progress'][idx],-20,.14));yaw=1.5*math.pi
   if f<=52:pose=mixpose(poses[50],pose,ease(50,53,f))
  else:
   phase='run';u=(f-69)/(144-69);pos,yaw=path(u)
   travelled=u*length;cycle=(travelled/native['run_cycle_distance']%1)*18;i=int(cycle);pose=mixpose(native['run'][i],native['run'][i+1],cycle-i)
   if f<=72:
    pose=mixpose(poses[68],pose,ease(68,73,f));delta=(yaw-1.5*math.pi+math.pi)%(2*math.pi)-math.pi;yaw=1.5*math.pi+delta*ease(68,74,f)
  poses[f]=pose;rows.append({'frame':f,'phase':phase,'position':list(pos),'yaw':yaw})
 rig.animation_data_clear();parent=rig.parent;parent.animation_data_clear();parent.rotation_mode='QUATERNION';previous={}
 for b in rig.pose.bones:b.rotation_mode='QUATERNION'
 for row in rows:
  f=row['frame'];sc.frame_set(f);parent.location=row['position'];parent.rotation_quaternion=Quaternion((0,0,1),row['yaw'])
  for prop in ['location','rotation_quaternion']:parent.keyframe_insert(prop,frame=f)
  pose=poses[f]
  for b in rig.pose.bones:
   kwargs={} if b.parent is None else {'parent_matrix':pose[b.parent.name],'parent_matrix_local':b.parent.bone.matrix_local}
   b.matrix_basis=b.bone.convert_local_to_pose(pose[b.name],b.bone.matrix_local,invert=True,**kwargs)
   if b.name in previous and b.rotation_quaternion.dot(previous[b.name])<0:b.rotation_quaternion.negate()
   previous[b.name]=b.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f,group=b.name)
  bpy.context.view_layer.update()
  ev=bpy.data.objects['HumanF_BodyMesh'].evaluated_get(bpy.context.evaluated_depsgraph_get())
  low=min((ev.matrix_world@Vector(p)).z for p in ev.bound_box)
  if low<.145:
   parent.location.z+=.145-low;parent.keyframe_insert('location',frame=f)
   row['position']=list(parent.location)
 rig.animation_data.action.name='V9 | shoot stow roll run';parent.animation_data.action.name='V9 | escape trajectory'
 return rows,{'run_path_length':length,'run_speed_mps':length/(75/12),'roll_distance':native['roll_distance'],'roll_source':'Quaternius native diving roll, transferred onto archer skeleton'}

def bear_motion(sc,rig,body,place):
 place.animation_data_clear();place.location=(0,0,0);rig.animation_data_clear()
 names=['Walk','Hit_Stand_F01','Attack_StandAngry_01_Low','Trot']
 acts={n:bpy.data.actions[f'RigRoot|{n}|Animation Base Layer'] for n in names}
 def sample(n,t):
  rig.animation_data_create();rig.animation_data.action=acts[n];rig.animation_data.action_slot=acts[n].slots[0];sc.frame_set(math.floor(t),subframe=t%1);bpy.context.view_layer.update()
  pose={b.name:b.matrix_basis.copy() for b in rig.pose.bones};loc,rot,scl=pose['RigJaw'].decompose();e=rot.to_euler('XYZ');e.z=min(e.z,math.radians(12));pose['RigJaw']=Matrix.LocRotScale(loc,e.to_quaternion(),scl)
  return pose,rig.location.copy()
 neutral=sample('Walk',1)[1];walk_delta=place.matrix_world.to_3x3()@(sample('Walk',52)[1]-neutral)
 trot_delta=place.matrix_world.to_3x3()@(sample('Trot',22)[1]-sample('Trot',1)[1]);trot_dist=trot_delta.length
 pursuit,pursuit_len=arc_path([(-3.8,-18,.18),(-6.2,-15.5,.18),(-6.6,-12,.18),(-3.8,-8.9,.18)])
 cache={};places={};last=None
 for f in range(1,N+1):
  if f<35:
   elapsed=(f-1)*2.5;loops=int(elapsed//51);pose,loc=sample('Walk',1+elapsed%51);pos=Vector((-3.8,-13.0,.18))+loops*walk_delta+place.matrix_world.to_3x3()@(loc-neutral);yaw=0
  elif f<44:
   pose,loc=sample('Hit_Stand_F01',1+(f-35)*2.5);pos=places[34][0].copy();yaw=0
   if f<38:pose=mixpose(cache[34],pose,ease(34,38,f))
  elif f<=90:
   pose,loc=sample('Attack_StandAngry_01_Low',1+(f-44)*2.5);start=places[43][0];pos=start.lerp(Vector((-3.8,-18,.18)),ease(44,62,f));yaw=0
   if f<=47:pose=mixpose(cache[43],pose,ease(43,48,f))
  else:
   u=(f-91)/(144-91);pos,yaw=pursuit(u);distance=u*pursuit_len;phase=distance/max(.01,trot_dist)%1;pose,loc=sample('Trot',1+phase*21)
   if f<97:pose=mixpose(cache[90],pose,ease(90,97,f));yaw=((yaw+math.pi)%(2*math.pi)-math.pi)*ease(90,98,f)
  cache[f]=pose;places[f]=(pos.copy(),yaw)
 rig.animation_data_clear();rig.location=neutral;parent_rotation=place.rotation_euler.to_quaternion();place.rotation_mode='QUATERNION'
 for b in rig.pose.bones:b.rotation_mode='QUATERNION'
 floor=[];previous={}
 for f,pose in cache.items():
  sc.frame_set(f)
  for n,m in pose.items():
   b=rig.pose.bones[n];b.matrix_basis=m
   if n in previous and b.rotation_quaternion.dot(previous[n])<0:b.rotation_quaternion.negate()
   previous[n]=b.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=f,group=n)
  pos,yaw=places[f];place.location=pos;place.rotation_quaternion=Quaternion((0,0,1),yaw)@parent_rotation;bpy.context.view_layer.update()
  ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());low=min((ev.matrix_world@Vector(p)).z for p in ev.bound_box);place.location.z+=max(0,.145-low)
  for prop in ['location','rotation_quaternion']:place.keyframe_insert(prop,frame=f)
  floor.append(max(.145,low))
 rig.animation_data.action.name='V9 | bear threat hit missed attack pursuit';place.animation_data.action.name='V9 | bear path'
 return {'trot_source_cycle_distance':trot_dist,'pursuit_distance':pursuit_len,'floor_range': [min(floor),max(floor)]}

def props(sc,rig,bear,body):
 bow=bpy.data.objects['Human_Bow'];arrow=bpy.data.objects['Human_Arrow'];string=bpy.data.objects['A | working bowstring'];spline=string.data.splines[0]
 for o in [bow,arrow]:o.animation_data_clear();o.rotation_mode='QUATERNION'
 string.data.animation_data_clear()
 sc.frame_set(35);bpy.context.view_layer.update();aim=bear.matrix_world@bear.pose.bones['RigSpine2'].head;aim.x-=.2
 sc.frame_set(32);bpy.context.view_layer.update();origin=(rig.matrix_world@rig.pose.bones['B-handProp.R'].matrix).translation.copy()
 sc.frame_set(35);bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in me.vertices];triangles=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(verts,triangles,all_triangles=True);hit,normal,idx,dist=tree.ray_cast(origin,(aim-origin).normalized());assert hit is not None;ids=triangles[idx];basis=[verts[i].copy() for i in ids];ev.to_mesh_clear()
 rot=(hit-origin).to_track_quat('Z','Y');maxz=max(v.co.z for v in arrow.data.vertices);initial_tip=origin+rot@Vector((0,0,maxz));stow_start=None;stow_rot=None
 points={}
 for f in range(1,N+1):
  sc.frame_set(f);bpy.context.view_layer.update();leftmat=rig.matrix_world@rig.pose.bones['B-handProp.L'].matrix;left=leftmat.translation;right=(rig.matrix_world@rig.pose.bones['B-handProp.R'].matrix).translation
  x=(left-right).normalized();z=Vector((0,0,1));y=z.cross(x).normalized();z=x.cross(y).normalized();m=Matrix((x,y,z)).transposed().to_4x4();m.translation=left;m=m@Matrix.Diagonal((.85,.85,.85,1))
  if f==40:hand_offset=leftmat.inverted()@m
  if f>40:
   held=leftmat@hand_offset
   chest=rig.matrix_world@rig.pose.bones['B-chest'].matrix
   # Back attachment is defined in actor forward coordinates; chest supplies
   # the native diving-roll orientation as well as the run's shoulder swing.
   rest=rig.data.bones['B-chest'].matrix_local
   roll_stow=ease(45,51,f)*(1-ease(65,72,f))
   back=rig.matrix_world@rig.pose.bones['B-chest'].matrix@rest.inverted()@Matrix.Translation((0,.25,1.05))@Matrix.Rotation(math.radians(30+60*roll_stow),4,'Y')@Matrix.Diagonal((.85,.85,.85,1))
   m=held.lerp(back,ease(41,49,f))
  bow.matrix_world=m
  for prop in ['location','rotation_quaternion','scale']:bow.keyframe_insert(prop,frame=f)
  nock=right if f<32 else bow.matrix_world@Vector((-.327,0,0))
  for p,co in zip(spline.points,[bow.matrix_world@Vector((-.327,0,.924)),nock,bow.matrix_world@Vector((-.327,0,-.924))]):p.co=(*co,1);p.keyframe_insert('co',frame=f)
  if f<32:arrow.matrix_world=Matrix.Translation(right)@x.to_track_quat('Z','Y').to_matrix().to_4x4()
  else:
   if f<35:tip=initial_tip.lerp(hit,(f-32)/3);arrow_rot=rot
   else:
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();tri=[ev.matrix_world@me.vertices[i].co for i in ids];ev.to_mesh_clear();tip=barycentric_transform(hit,*basis,*tri)
    # Rotate with the struck surface during the turn into pursuit.
    n0=(basis[1]-basis[0]).cross(basis[2]-basis[0]).normalized();n1=(tri[1]-tri[0]).cross(tri[2]-tri[0]).normalized();arrow_rot=n0.rotation_difference(n1)@rot
   arrow.matrix_world=Matrix.Translation(tip-arrow_rot@Vector((0,0,maxz)))@arrow_rot.to_matrix().to_4x4()
  for prop in ['location','rotation_quaternion','scale']:arrow.keyframe_insert(prop,frame=f)
 # Small authored clearance adjustment for the strapped bow during the tuck.
 # Correct the prop alone; lifting the actor would destroy ground contact.
 bowmesh=bpy.data.objects['Human_BowMesh'];needs={};bowposes={};strings={}
 for f in range(1,N+1):
  sc.frame_set(f);bpy.context.view_layer.update();ev=bowmesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
  low=min((ev.matrix_world@Vector(p)).z for p in ev.bound_box)
  needs[f]=max(0,.155-low) if 48<=f<=72 else 0
  bowposes[f]=bow.matrix_world.copy();strings[f]=[p.co.copy() for p in spline.points]
 corrections={}
 for f in range(1,N+1):
  lift=max(needs[g]*(1-ease(0,4,abs(f-g))) for g in range(max(1,f-3),min(N,f+3)+1))
  corrections[f]=lift
  if not lift:continue
  sc.frame_set(f);m=bowposes[f];m.translation.z+=lift;bow.matrix_world=m;bow.keyframe_insert('location',frame=f)
  for p,co in zip(spline.points,strings[f]):co.z+=lift;p.co=co;p.keyframe_insert('co',frame=f)
 return {'release':32,'impact':35,'surface_triangle':list(ids),'hit_point':list(hit),'maximum_roll_prop_clearance_offset_m':max(corrections.values())}

def main():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'option-c-bow-bear.blend'),use_scripts=False);sc=bpy.context.scene
 rig=bpy.data.objects['Rig'];body=bpy.data.objects['HumanF_BodyMesh'];bear=bpy.data.objects['RigRoot'];bearbody=bpy.data.objects['sm_3_0_0'];bearplace=bpy.data.objects['Bear_Animated']
 terrain_and_door(sc);rows,actor_report=actor_motion(sc,rig);bear_report=bear_motion(sc,bear,bearbody,bearplace);prop_report=props(sc,rig,bear,bearbody)
 for marker in list(sc.timeline_markers):sc.timeline_markers.remove(marker)
 cameras=add_escape_cameras(sc,rig,body,rows)
 sc.frame_start=1;sc.frame_end=N;sc.render.fps=12;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=8;sc.render.resolution_x=768;sc.render.resolution_y=432;sc.render.resolution_percentage=100;sc.render.use_motion_blur=False;sc.render.use_compositing=False;sc.render.use_sequencer=False;sc.camera=cameras['third']
 sc['review_label']='V9 — BOW / BEAR — SHOOT, EVADE, ESCAPE — CAMERA STUDY';sc['licensed_source']='LOCAL ONLY: licensed source archer model and motion; final heroine retarget pending'
 for a in bpy.data.actions:
  if a.name.startswith('V9 |'):
   for fc in a.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
 sc.frame_set(1);bpy.context.view_layer.update();path=ROOT/'bear-bow-escape-v9.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
 report={'scene':path.name,'duration_seconds':12,'frames':144,'fps':12,'actor':actor_report,'bear':bear_report,'arrow':prop_report,'cameras':{k:v.name for k,v in cameras.items() if hasattr(v,'name')},'path_rows':rows,'final_heroine_retargeted':False,'heavy_render':False,'native_animation':['female bow, stow, run','Quaternius diving roll transferred to female skeleton','bear walk,hit,lowattack,trot'],'timeline':{'1-40':'aim/shoot','41-50':'stow bow','51-68':'diving roll away from committed attack','69-144':'run around bear to opening airlock'}}
 (OUT/'scene-report.json').write_text(json.dumps(report,indent=2)+'\n');print('ESCAPE_SCENE_READY',path)
if __name__=='__main__':main()
