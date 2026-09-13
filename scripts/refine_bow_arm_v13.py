"""Natural nearly extended bow arm and canted bow; CPU only, no camera changes."""
import bpy,sys,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
from correct_aim_v13 import smooth,matrix_at
SOURCE=ROOT/'bear-bow-forest-v13-before-arm-staging.blend';DEST=ROOT/'bear-bow-forest-v13-arm-test.blend'
def solve(world,hand_goal,weight,rig):
 u,e,h=['Bip01 L '+n for n in ['UpperArm','Forearm','Hand']];a,b,c=[world[n].translation.copy() for n in [u,e,h]];wrist=hand_goal.translation;l1=(b-a).length;l2=(c-b).length;dist=(wrist-a).length;axis=(wrist-a).normalized();assert dist<l1+l2+.0001;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));native=b-a-axis*(b-a).dot(axis);native.normalize();down=Vector((0,0,-1));down-=axis*down.dot(axis);down.normalize();turn=native.rotation_difference(down);pole=Quaternion().slerp(turn,weight)@native;elbow=a+axis*along+pole*height
 qu=(b-a).normalized().rotation_difference((elbow-a).normalized())@world[u].to_quaternion();qe=(c-b).normalized().rotation_difference((wrist-elbow).normalized())@world[e].to_quaternion();out={u:matrix_at(a,qu,world[u].to_scale()),e:matrix_at(elbow,qe,world[e].to_scale()),h:hand_goal};change=hand_goal@world[h].inverted()
 for bone in rig.data.bones:
  if any(p.name==h for p in bone.parent_recursive):out[bone.name]=change@world[bone.name]
 return out,{'elbow_angle_degrees':math.degrees((a-elbow).angle(wrist-elbow)),'reach_ratio':dist/(l1+l2),'upper_length_error_m':abs((elbow-a).length-l1),'forearm_length_error_m':abs((wrist-elbow).length-l2)}
def main():
 if not SOURCE.exists():shutil.copyfile(v.DEST,SOURCE)
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);sc=bpy.context.scene;arrow=bpy.data.objects['Human_Arrow'];bow=bpy.data.objects['Human_Bow'];rig=bpy.data.objects['V12 | FemaleAdult04 forest rig'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];string=bpy.data.objects['A | working bowstring'];sp=string.data.splines[0]
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 times=sorted(set([1+i*.25 for i in range(157)]+[32+i*.125 for i in range(25)]+list(range(41,145))));cache={}
 for f in times:
  v.set_frame(sc,f);cache[f]={'arrow':arrow.matrix_world.copy(),'bow':bow.matrix_world.copy(),'bones':{p.name:rig.matrix_world@p.matrix for p in rig.pose.bones},'rigworld':rig.matrix_world.copy(),'string':[Vector(p.co[:3]) for p in sp.points]}
 flight=cache[32]['arrow'].to_quaternion()@Vector((0,0,1));rig.animation_data.action=rig.animation_data.action.copy();bow.animation_data.action=bow.animation_data.action.copy();string.data.animation_data.action=string.data.animation_data.action.copy();qa=[]
 for f in times:
  v.set_frame(sc,f);row=cache[f];weight=smooth((f-9)/11)*(1-smooth((f-35)/5));bm=row['bow'];rest=bm@v.REST_LOCAL;direction=row['arrow'].to_quaternion()@Vector((0,0,1)) if f<32 else flight;q=Quaternion(direction,math.radians(-25)*weight);wr=row['bones']['Bip01 L Hand'].translation;sh=row['bones']['Bip01 L UpperArm'].translation;el=row['bones']['Bip01 L Forearm'].translation;length=(el-sh).length+(wr-el).length;rotated=rest+q@(wr-rest);relative=rotated-sh;bb=relative.dot(direction);distance=-bb+math.sqrt(max(0,bb*bb+(length*.97)**2-relative.length_squared));extension=max(0,min(.085,distance))*weight;newrest=rest+direction*extension;F=Matrix.Translation(newrest)@q.to_matrix().to_4x4()@Matrix.Translation(-rest);bow.matrix_world=F@bm
  for prop in ['location','rotation_quaternion','scale']:bow.keyframe_insert(prop,frame=f)
  poses,metrics=solve(row['bones'],F@row['bones']['Bip01 L Hand'],weight,rig);inv=row['rigworld'].inverted()
  for bone in rig.pose.bones:
   if bone.name in poses:
    parent=poses.get(bone.parent.name,row['bones'][bone.parent.name]);bone.matrix_basis=bone.bone.convert_local_to_pose(inv@poses[bone.name],bone.bone.matrix_local,parent_matrix=inv@parent,parent_matrix_local=bone.parent.bone.matrix_local,invert=True);bone.rotation_mode='QUATERNION'
    for prop in ['location','rotation_quaternion','scale']:bone.keyframe_insert(prop,frame=f)
  if f<=40:
   nock=row['arrow'].translation;mid=row['string'][1];held=(mid-nock).length<.00001;points=[F@row['string'][0],mid if held else F@mid,F@row['string'][2]]
   for p,co in zip(sp.points,points):p.co=(*co,1);p.keyframe_insert('co',frame=f)
  bpy.context.view_layer.update();actual={n:rig.matrix_world@rig.pose.bones[n].matrix for n in poses};ah=actual['Bip01 L Hand'];expected=F@row['bones']['Bip01 L Hand'];grip=(ah.translation-expected.translation).length;u,e,h=[actual['Bip01 L '+part].translation for part in ['UpperArm','Forearm','Hand']]
  qa.append({'frame':f,'extension_m':extension,'bow_cant_degrees':-25*weight,'actual_grip_position_error_m':grip,'actual_upper_length_error_m':abs((e-u).length-(el-sh).length),'actual_forearm_length_error_m':abs((h-e).length-(wr-el).length),**metrics})
 for act in [rig.animation_data.action,bow.animation_data.action,string.data.animation_data.action]:
  for fc in act.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 for act in [rig.animation_data.action,bow.animation_data.action]:
  tracks={}
  for fc in act.fcurves:
   if fc.data_path.endswith('rotation_quaternion'):tracks.setdefault(fc.data_path,{})[fc.array_index]=fc
  for fs in tracks.values():
   if len(fs)!=4:continue
   prev=None
   for i in range(len(fs[0].keyframe_points)):
    q=Vector([fs[c].keyframe_points[i].co.y for c in range(4)])
    if prev is not None and prev.dot(q)<0:
     q=-q
     for c in range(4):fs[c].keyframe_points[i].co.y=q[c]
    prev=q
 audit=v.actual_audit(sc,arrow,arms);bad=[r for r in audit if r['L_triangle_intersections'] or r['R_triangle_intersections']];report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pose_samples':qa,'intersection_samples':bad,'note':'Extend bow along unchanged arrow line;25-degree outward cant around arrow axis; downward elbow pole. Blend9..20 and35..40; arrow action/root/cameras/right hand/run/roll unchanged.'};(v.OUT/'archery-arm-staging.json').write_text(json.dumps(report,indent=2));(v.OUT/'archery-arm-staging-clearance.json').write_text(json.dumps({'samples':audit,'intersection_samples':bad},indent=2));assert not bad,'Arrow/skin intersections';assert max(r['actual_grip_position_error_m'] for r in qa)<.0001
 v.set_frame(sc,20);bpy.ops.wm.save_as_mainfile(filepath=str(DEST));report['scene_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest();(v.OUT/'archery-arm-staging.json').write_text(json.dumps(report,indent=2));print(json.dumps({'scene':DEST.name,'scene_sha256':report['scene_sha256'],'frame20':next(x for x in qa if x['frame']==20),'intersection_frames':len(bad)},indent=2),flush=True)
if __name__=='__main__':main()
