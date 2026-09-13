"""Fix only frames1..9: carry the bow clear of the camera, return exactly at10."""
import bpy,sys,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
from correct_aim_v13 import smooth
from refine_bow_arm_v13 import solve
SOURCE=ROOT/'bear-bow-forest-v13-before-opening-fix.blend';DEST=ROOT/'bear-bow-forest-v13-opening-test.blend'
def later_signature(objects,start=10):
 data=[]
 for ob in objects:
  owner=ob.data if ob.type=='CURVE' else ob;a=owner.animation_data.action
  data.append((ob.name,[(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points if k.co.x>=start]) for f in a.fcurves]))
 return hashlib.sha256(repr(data).encode()).hexdigest()
def camera_check(scene,cam,mesh):
 vf=cam.data.view_frame(scene=scene);lo=Vector((min(p.x for p in vf),min(p.y for p in vf),vf[0].z));hi=Vector((max(p.x for p in vf),max(p.y for p in vf),vf[0].z));ev,me=v.evaluated(mesh);me.calc_loop_triangles();bt=BVHTree.FromPolygons([ev.matrix_world@p.co for p in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear();hits=near=0
 for ix in range(21):
  for iy in range(13):
   d=cam.matrix_world.to_quaternion()@Vector((lo.x+(hi.x-lo.x)*(ix+.5)/21,lo.y+(hi.y-lo.y)*(iy+.5)/13,lo.z)).normalized();p,no,ind,dist=bt.ray_cast(cam.matrix_world.translation,d,5)
   if p is not None:hits+=1;near+=dist<.15
 return {'camera_bow_surface_distance_m':bt.find_nearest(cam.matrix_world.translation)[3],'bow_screen_ray_fraction':hits/273,'near_bow_screen_ray_fraction':near/273}
def main():
 if not SOURCE.exists():shutil.copyfile(v.DEST,SOURCE)
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);sc=bpy.context.scene;rig=bpy.data.objects['V12 | FemaleAdult04 forest rig'];arrow=bpy.data.objects['Human_Arrow'];bow=bpy.data.objects['Human_Bow'];string=bpy.data.objects['A | working bowstring'];sp=string.data.splines[0];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];cam=bpy.data.objects['V9 | First-person escape'];bm=bpy.data.objects['Human_BowMesh'];objects=[rig,arrow,bow,string,cam,bpy.data.objects['V9 | Third-person escape']];sig=later_signature(objects);cache={}
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 for i in range(144):
  f=1+i*.0625;v.set_frame(sc,f);cache[f]={'arrow':arrow.matrix_world.copy(),'bow':bow.matrix_world.copy(),'world':rig.matrix_world.copy(),'bones':{p.name:rig.matrix_world@p.matrix for p in rig.pose.bones},'string':[Vector(p.co[:3]) for p in sp.points]}
 for ob in [rig,bow,arrow]:ob.animation_data.action=ob.animation_data.action.copy()
 string.data.animation_data.action=string.data.animation_data.action.copy();poseqa=[]
 for f,row in cache.items():
  v.set_frame(sc,f);weight=1-smooth((f-8)/2);d=row['arrow'].to_quaternion()@Vector((0,0,1));rest=row['bow']@v.REST_LOCAL;wrist=row['bones']['Bip01 L Hand'].translation;F=Matrix.Translation(wrist)@Quaternion(d,math.radians(-25)*weight).to_matrix().to_4x4()@Matrix.Translation(-wrist);old_bow_q=bow.rotation_quaternion.copy();bow.matrix_world=F@row['bow']
  if old_bow_q.dot(bow.rotation_quaternion)<0:bow.rotation_quaternion.negate()
  for prop in ['location','rotation_quaternion','scale']:bow.keyframe_insert(prop,frame=f)
  nock=row['arrow'].translation.copy();new_rest=bow.matrix_world@v.REST_LOCAL;slip=.004*smooth((f-9.25)/.125)*(1-smooth((f-9.875)/.125));nock+=(new_rest-nock).normalized()*slip;arrow.matrix_world.translation=nock;arrow.keyframe_insert('location',frame=f);old_arrow_q=arrow.rotation_quaternion.copy();arrow.rotation_quaternion=(new_rest-nock).to_track_quat('Z','Y')
  if old_arrow_q.dot(arrow.rotation_quaternion)<0:arrow.rotation_quaternion.negate()
  arrow.keyframe_insert('rotation_quaternion',frame=f)
  poses,qa=solve(row['bones'],F@row['bones']['Bip01 L Hand'],0,rig);inv=row['world'].inverted()
  for bone in rig.pose.bones:
   if bone.name in poses:
    old_q=bone.rotation_quaternion.copy();parent=poses.get(bone.parent.name,row['bones'][bone.parent.name]);bone.matrix_basis=bone.bone.convert_local_to_pose(inv@poses[bone.name],bone.bone.matrix_local,parent_matrix=inv@parent,parent_matrix_local=bone.parent.bone.matrix_local,invert=True)
    if old_q.dot(bone.rotation_quaternion)<0:bone.rotation_quaternion.negate()
    for prop in ['location','rotation_quaternion','scale']:bone.keyframe_insert(prop,frame=f)
  for p,co in zip(sp.points,[F@row['string'][0],nock,F@row['string'][2]]):p.co=(*co,1);p.keyframe_insert('co',frame=f)
  bpy.context.view_layer.update();hand=rig.matrix_world@rig.pose.bones['Bip01 L Hand'].matrix;qa.update({'frame':f,'carry_cant_degrees':-25*weight,'actual_grip_error_m':(hand.translation-(F@row['bones']['Bip01 L Hand']).translation).length});poseqa.append(qa)
 for owner in [rig,bow,arrow,string.data]:
  for fc in owner.animation_data.action.fcurves:
   for k in fc.keyframe_points:
    if k.co.x<10:k.interpolation='LINEAR'
 assert later_signature(objects)==sig,'Frames10 onward changed'
 times=sorted(set([1+i*.125 for i in range(73)]+[9.9375]));clear=v.actual_audit(sc,arrow,arms,times=times);bad=[r for r in clear if r['L_triangle_intersections'] or r['R_triangle_intersections']];views=[]
 for f in times:
  v.set_frame(sc,f);views.append({'frame':f,**camera_check(sc,cam,bm)})
 report={'source_scene_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'unchanged_keyframes10_onward_hash':sig,'unchanged_keyframes10_onward':True,'pose_samples':poseqa,'clearance_samples':clear,'intersection_samples':bad,'camera_samples':views,'change':'Additional25-degree low-carry cant through8, easing out8..10;4 mm nock slip during rapid raise9.25..10. Only frames1..9.9375 keyed; frame10 and all later keys untouched. Arrow follows shifted rest during carry; no camera, bear, root, right-hand or later animation modifications.'};(v.OUT/'archery-opening-fix.json').write_text(json.dumps(report,indent=2));assert not bad;assert max(x['actual_grip_error_m'] for x in poseqa)<.0001;assert max(x['near_bow_screen_ray_fraction'] for x in views)<.05,'Bow still obstructs near camera'
 v.set_frame(sc,1);bpy.ops.wm.save_as_mainfile(filepath=str(DEST));report['scene_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest();(v.OUT/'archery-opening-fix.json').write_text(json.dumps(report,indent=2));print(json.dumps({'scene_sha256':report['scene_sha256'],'maximum_near_bow_screen_ray_fraction':max(x['near_bow_screen_ray_fraction'] for x in views),'frame1':views[0],'intersection_samples':len(bad)},indent=2),flush=True)
if __name__=='__main__':main()
