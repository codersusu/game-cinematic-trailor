"""CPU-only aiming correction candidate. Preserve nock, impact, roots and cameras.
Move bow and actual left arm onto the release line during the existing raise.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
DEST=ROOT/'bear-bow-forest-v13-aim-test.blend'
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def matrix_at(p,q,scale):return Matrix.Translation(p)@q.to_matrix().to_4x4()@Matrix.Diagonal((*scale,1))
def arm_ik(world,delta,rig):
 u,e,h=['Bip01 L '+n for n in ['UpperArm','Forearm','Hand']];a,b,c=[world[n].translation.copy() for n in [u,e,h]];wrist=c+delta;l1=(b-a).length;l2=(c-b).length;dist=(wrist-a).length;axis=(wrist-a).normalized();reach=max(0,dist-(l1+l2-.0005));a+=axis*reach;dist=(wrist-a).length;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));pole=b-a-axis*(b-a).dot(axis);pole.normalize();elbow=a+axis*along+pole*height
 qu=(b-world[u].translation).normalized().rotation_difference((elbow-a).normalized())@world[u].to_quaternion();qe=(c-b).normalized().rotation_difference((wrist-elbow).normalized())@world[e].to_quaternion();out={u:matrix_at(a,qu,world[u].to_scale()),e:matrix_at(elbow,qe,world[e].to_scale()),h:world[h].copy()};out[h].translation=wrist
 change=out[h]@world[h].inverted()
 for bone in rig.data.bones:
  if any(p.name==h for p in bone.parent_recursive):out[bone.name]=change@world[bone.name]
 return out,{'shoulder_reach_m':reach,'upper_length_error_m':abs((elbow-a).length-l1),'forearm_length_error_m':abs((wrist-elbow).length-l2)}
def main():
 source=ROOT/'bear-bow-forest-v13-initial-archery.blend';bpy.ops.wm.open_mainfile(filepath=str(source if source.exists() else v.DEST),use_scripts=False);sc=bpy.context.scene;arrow=bpy.data.objects['Human_Arrow'];bow=bpy.data.objects['Human_Bow'];rig=bpy.data.objects['V12 | FemaleAdult04 forest rig'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];string=bpy.data.objects['A | working bowstring'];sp=string.data.splines[0]
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 times=sorted(set([1+i*.25 for i in range(157)]+[32+i*.125 for i in range(25)]+list(range(41,145))));cache={}
 for f in times:
  v.set_frame(sc,f);cache[f]={'arrow':arrow.matrix_world.copy(),'bow':bow.matrix_world.copy(),'bones':{p.name:rig.matrix_world@p.matrix for p in rig.pose.bones},'string':[Vector(p.co[:3]) for p in sp.points]}
 length=max(p.co.z for p in arrow.data.vertices);hit=cache[35]['arrow']@Vector((0,0,length));launch=cache[32]['arrow'].translation;flight=(hit-launch).normalized();rows=[];prev=None
 rig.animation_data.action=rig.animation_data.action.copy();arrow.animation_data.action=arrow.animation_data.action.copy();bow.animation_data.action=bow.animation_data.action.copy();string.data.animation_data.action=string.data.animation_data.action.copy()
 for f in times:
  v.set_frame(sc,f);row=cache[f];am=row['arrow'];bm=row['bow'];nock=am.translation;oldq=am.to_quaternion();oldrest=bm@v.REST_LOCAL
  if f<32:
   direction=(hit-nock).normalized();target=direction.to_track_quat('Z','Y');q=oldq.slerp(target,smooth((f-9)/11));direction=q@Vector((0,0,1));linepoint=nock+direction*(oldrest-nock).dot(direction);delta=linepoint-oldrest
  else:
   q=oldq;linepoint=launch+flight*(oldrest-launch).dot(flight);delta=(linepoint-oldrest)*(1-smooth((f-35)/5)) if f<=40 else Vector((0,0,0))
  if prev is not None and prev.dot(q)<0:q.negate()
  prev=q.copy();arrow.matrix_world=matrix_at(nock,q,am.to_scale());arrow.rotation_quaternion=q
  for path in ['location','rotation_quaternion','scale']:arrow.keyframe_insert(path,frame=f)
  bow.matrix_world=bm.copy();bow.matrix_world.translation+=delta
  for path in ['location','rotation_quaternion','scale']:bow.keyframe_insert(path,frame=f)
  poses,qa=arm_ik(row['bones'],delta,rig)
  for bone in rig.pose.bones:
   if bone.name in poses:
    inv=rig.matrix_world.inverted();parent_world=poses.get(bone.parent.name,row['bones'][bone.parent.name]);bone.matrix_basis=bone.bone.convert_local_to_pose(inv@poses[bone.name],bone.bone.matrix_local,parent_matrix=inv@parent_world,parent_matrix_local=bone.parent.bone.matrix_local,invert=True);bone.rotation_mode='QUATERNION'
    for path in ['location','rotation_quaternion','scale']:bone.keyframe_insert(path,frame=f)
  if f<=40:
   tips=[bow.matrix_world@Vector((-.327,0,.924)),row['string'][1],bow.matrix_world@Vector((-.327,0,-.924))]
   # On release, the drawn nock follows the arrow until it reaches the brace.
   if f>=32:
    brace=bow.matrix_world@Vector((-.327,0,v.REST_LOCAL.z));axis=bow.matrix_world.to_quaternion()@Vector((1,0,0));tips[1]=nock if (nock-brace).dot(axis)<0 and f<35 else brace
   for p,co in zip(sp.points,tips):p.co=(*co,1);p.keyframe_insert('co',frame=f)
  rows.append({'frame':f,'wrist_shift_m':delta.length,**qa})
 for act in [rig.animation_data.action,arrow.animation_data.action,bow.animation_data.action,string.data.animation_data.action]:
  for fc in act.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 # Normalize sign sequences in all changed quaternion tracks before dense audit.
 for act in [rig.animation_data.action,arrow.animation_data.action,bow.animation_data.action]:
  groups={}
  for fc in act.fcurves:
   if fc.data_path.endswith('rotation_quaternion'):groups.setdefault(fc.data_path,{})[fc.array_index]=fc
  for fs in groups.values():
   if len(fs)!=4:continue
   prev=None
   for i in range(len(fs[0].keyframe_points)):
    q=Vector([fs[c].keyframe_points[i].co.y for c in range(4)])
    if prev is not None and prev.dot(q)<0:
     q=-q
     for c in range(4):fs[c].keyframe_points[i].co.y=q[c]
    prev=q
 audit=v.actual_audit(sc,arrow,arms);bad=[r for r in audit if r['L_triangle_intersections'] or r['R_triangle_intersections']];measure=[];dirs={}
 for f in [20,31,31.75,31.875,32,32.125,32.5,33,35,40]:
  v.set_frame(sc,f);o=arrow.matrix_world.translation;d=arrow.matrix_world.to_quaternion()@Vector((0,0,1));r=bow.matrix_world@v.REST_LOCAL;dirs[f]=d;measure.append({'frame':f,'rest_axis_miss_m':(o+d*(r-o).dot(d)-r).length})
 report={'scene':DEST.name,'changes':'Left arm IK and bow during raise9..20; fixed physical release aim; ease back35..40. Root/cameras/right hand/bear unchanged.','direction_jump_degrees':math.degrees(dirs[31.75].angle(dirs[32])),'rest_measurements':measure,'pose_qa':rows,'intersection_samples':bad};(v.OUT/'archery-aim-correction.json').write_text(json.dumps(report,indent=2));assert not bad,'Arrow intersects skin';(v.OUT/'archery-aim-clearance.json').write_text(json.dumps({'samples':audit,'intersection_samples':bad},indent=2));v.set_frame(sc,20);bpy.ops.wm.save_as_mainfile(filepath=str(DEST));print(json.dumps({'intersection_count':len(bad),'direction_jump_degrees':report['direction_jump_degrees'],'maximum_wrist_shift_m':max(r['wrist_shift_m'] for r in rows),'scene_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
