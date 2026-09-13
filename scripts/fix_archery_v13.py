"""V13 physical arrow-rest/nock correction; never edit prior-version scenes.
CPU geometry solving and collision audits only. Root owns GPU previews.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'bear-bow-forest-v12.blend';DEST=ROOT/'bear-bow-forest-v13.blend';OUT=ROOT/'previews/v13';OUT.mkdir(exist_ok=True,parents=True)
RADIUS=.00370
REST_LOCAL=Vector((0,-.06,.11))

def set_frame(scene,f):scene.frame_set(math.floor(f),subframe=f%1);bpy.context.view_layer.update()
def evaluated(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();return ev,me

def hand_trees(arms):
 ev,me=evaluated(arms);points=[ev.matrix_world@v.co for v in me.vertices];groups={g.index:g.name for g in arms.vertex_groups};trees={};polys={};me.calc_loop_triangles()
 for side in 'LR':
  allowed={i for i,n in groups.items() if n.startswith(f'Bip01 {side} ') and any(t in n for t in [' Hand',' Finger',' Forearm'])}
  finger={i for i,n in groups.items() if n.startswith(f'Bip01 {side} Finger')}
  weights=[sum(g.weight for g in v.groups if g.group in allowed)>.08 for v in me.vertices];fw=[sum(g.weight for g in v.groups if g.group in finger)>.15 for v in me.vertices]
  faces=[tuple(t.vertices) for t in me.loop_triangles if all(weights[i] for i in t.vertices)];ff=[tuple(t.vertices) for t in me.loop_triangles if all(fw[i] for i in t.vertices)]
  trees[side]=BVHTree.FromPolygons(points,faces,all_triangles=True);trees[side+'f']=BVHTree.FromPolygons(points,ff,all_triangles=True);polys[side]=faces
 ev.to_mesh_clear();return trees,points,polys

def shaft_clearance(tree,origin,direction,radius=RADIUS,step=.003,start=.04,end=.89):
 minimum=1e9;at=None
 for i in range(math.ceil((end-start)/step)+1):
  t=min(end,start+i*step);p=origin+direction*t;hit,normal,idx,d=tree.find_nearest(p)
  if hit is None:continue
  c=d-radius
  if .04<=t<=.185:c-=.008
  # Distance is unsigned on these open wrist subsets; explicit ray/triangle
  # tests below detect crossings without mistaking the back of a sleeve.
  
  if c<minimum:minimum=c;at=t
 hit,normal,idx,dist=tree.ray_cast(origin+direction*start,direction,end-start)
 if hit is not None:minimum=min(minimum,-radius)
 return minimum,at

def solve_nock(bowmat,old_nock,trees,previous=None):
 rest=bowmat@REST_LOCAL;up=bowmat.to_3x3()@Vector((0,0,1));up.normalize();side=bowmat.to_3x3()@Vector((0,1,0));side.normalize();candidates=[]
 # A fixed support above and on the archer's left of the riser. Ray hits on
 # actual draw-hand fingers select a real nocking contact, not a proxy palm.
 for z in [.055,.04,.07,.025,.085,.01,-.01]:
  for x in [0,.02,-.02,.04,-.04]:
   nominal=old_nock+up*z+side*x;ray=(nominal-rest).normalized();hit,normal,idx,dist=trees['Rf'].ray_cast(rest,ray,1.5)
   if hit is None:
    near,nn,ni,nd=trees['Rf'].find_nearest(nominal)
    if near is not None:
     ray=(near-nn*.003-rest).normalized();hit,normal,idx,dist=trees['Rf'].ray_cast(rest,ray,1.8)
   if hit is None:continue
   direction=(rest-hit).normalized();origin=hit+direction*.008
   lc,lt=shaft_clearance(trees['L'],origin,direction,step=.008);rc,rt=shaft_clearance(trees['R'],origin,direction,step=.008,start=0)
   score=(origin-(previous if previous is not None else old_nock+up*.045)).length
   if min(lc,rc)<.001:score+=100+max(0,.001-min(lc,rc))*1000
   candidates.append((score,origin,direction,{'left_clearance':lc,'left_axis_at':lt,'right_clearance':rc,'right_axis_at':rt,'finger_contact':list(hit),'nock_skin_gap':.008}))
 if not candidates:raise RuntimeError('No real draw-finger contact found')
 best=min(candidates,key=lambda x:x[0]);return best[1],best[2],rest,best[3]

def _geometry(arrow):
 # Source game arrow has a14.7mm shaft and vanes beginning at its zero/nock
 # point. Use a7.3mm shaft, keep arrow length, and leave room for drawing fingers.
 arrow.data=arrow.data.copy()
 for v in arrow.data.vertices:
  v.co.x*=.5;v.co.y*=.5
  if v.index>=58:v.co.z=.04+v.co.z
 bm=bmesh.new();bm.from_mesh(arrow.data);result=bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=12,radius1=RADIUS,radius2=RADIUS,depth=.061,matrix=Matrix.Translation((0,0,.0305)));bm.to_mesh(arrow.data);bm.free()
 arrow['v13_shaft_diameter_m']=RADIUS*2;arrow['v13_fletching_start_m']=.04

def _rest_object(bow):
 # A small physical arrow shelf extends from the riser under the new shaft.
 bpy.ops.mesh.primitive_cube_add(size=1);shelf=bpy.context.object;shelf.name='V13 | Physical arrow rest';shelf.parent=bow;shelf.matrix_parent_inverse=Matrix.Identity(4);shelf.location=(0,REST_LOCAL.y/2,REST_LOCAL.z-(RADIUS+.0015)/.85);shelf.scale=(.028,abs(REST_LOCAL.y)+.024,.003)
 m=bpy.data.materials.new('V13 | arrow rest dark leather');m.diffuse_color=(.065,.033,.018,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.68;shelf.data.materials.append(m);return shelf

def protected_hash():
 rows=[]
 for o in bpy.data.objects:
  if o.name in ['Human_Arrow','A | working bowstring']:continue
  a=o.animation_data.action if o.animation_data else None
  if a:rows.append((o.name,[(f.data_path,f.array_index,[tuple(k.co) for k in f.keyframe_points]) for f in a.fcurves]))
 return hashlib.sha256(repr(rows).encode()).hexdigest()

def actual_audit(scene,arrow,arms,times=None):
 rows=[]
 if times is None:times=sorted(set([1+i*.25 for i in range(157)]+[30+i*.0625 for i in range(81)]))
 for f in times:
  set_frame(scene,f);trees,points,polys=hand_trees(arms);ev,me=evaluated(arrow);me.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(t.vertices) for t in me.loop_triangles];abt=BVHTree.FromPolygons(verts,faces,all_triangles=True);ev.to_mesh_clear()
  n=arrow.matrix_world.translation;d=arrow.matrix_world.to_quaternion()@Vector((0,0,1));row={'frame':f}
  for side in 'LR':
   row[side+'_triangle_intersections']=len(abt.overlap(trees[side]));row[side+'_shaft_clearance']=shaft_clearance(trees[side],n,d,step=.002,start=.006)[0]
  row['nock_to_string_m']=(n-Vector(bpy.data.objects['A | working bowstring'].data.splines[0].points[1].co[:3])).length
  rows.append(row)
  if len(rows)%40==0:print('audit',f,flush=True)
 return rows

def diagnostic_camera(scene,bow):
 set_frame(scene,20);rest=bow.matrix_world@REST_LOCAL;data=bpy.data.cameras.new('V13 | Arrow rest diagnostic');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
 cam.location=rest+Vector((.75,-.75,.25));target=rest+Vector((0,-.25,-.015));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=52;data.clip_start=.02;cam['diagnostic_only']=True
 return cam.name

def contact_audit_saved():
 bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False);scene=bpy.context.scene;arrow=bpy.data.objects['Human_Arrow'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];rows=[]
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 for f in [1,8.5,9,11.75,13,20,25,31,31.875,32]:
  set_frame(scene,f);trees,_,_=hand_trees(arms);mw=arrow.matrix_world;nearest=1e3;near=None
  # Sample the actual added nock cylinder surface (including rear cap).
  samples=[Vector((RADIUS*math.cos(a*math.tau/64),RADIUS*math.sin(a*math.tau/64),z*.001)) for a in range(64) for z in range(31)]
  samples += [Vector((RADIUS*r/10*math.cos(a*math.tau/64),RADIUS*r/10*math.sin(a*math.tau/64),0)) for a in range(64) for r in range(11)]
  for p in samples:
   w=mw@p;hit,normal,idx,d=trees['Rf'].find_nearest(w)
   if d<nearest:nearest=d;near=(list(w),list(hit))
  rows.append({'frame':f,'nock_surface_to_finger_m':nearest,'nearest_world_points':near})
 report={'scene_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'method':'actual 7.4 mm nock cylinder surface sampled at 64 azimuths, 1 mm axial intervals over rear 30 mm, plus filled rear cap; nearest evaluated render-subdivision finger triangle','samples':rows};(OUT/'archery-nock-contact.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

def string_audit_saved():
 bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False);scene=bpy.context.scene;string=bpy.data.objects['A | working bowstring'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];rows=[]
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 for f in [20,31]:
  set_frame(scene,f);trees,_,_=hand_trees(arms);points=[string.matrix_world@Vector(p.co[:3]) for p in string.data.splines[0].points];radius=string.data.bevel_depth*max(string.matrix_world.to_scale());best=(1e9,None,None)
  for endpoint in [points[0],points[2]]:
   n=points[1];d=(endpoint-n).normalized();limit=min((endpoint-n).length,.25)
   for i in range(math.ceil(limit/.00025)+1):
    at=min(limit,i*.00025);p=n+d*at;hit,normal,idx,dist=trees['Rf'].find_nearest(p)
    if dist<best[0]:best=(dist,list(p),list(hit))
  ev,me=evaluated(string);me.calc_loop_triangles();bt=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True);overlap=len(bt.overlap(trees['Rf']));ev.to_mesh_clear()
  rows.append({'frame':f,'string_radius_m':radius,'centerline_to_finger_m':best[0],'string_surface_to_finger_m':best[0]-radius,'closest_world_points':[best[1],best[2]],'actual_tube_finger_triangle_intersections':overlap})
 report={'scene_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'method':'string centerline sampled every 0.25 mm within 25 cm of nock on each segment; subtract actual curve bevel radius; evaluated full tube triangle overlap against drawing fingers','samples':rows};(OUT/'archery-string-contact.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

def finalize_saved():
 bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False);scene=bpy.context.scene;arrow=bpy.data.objects['Human_Arrow'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];body=bpy.data.objects['V12 | FemaleAdult04 full body']
 # Equivalent quaternion signs must remain continuous between keyed matrices.
 fs={f.array_index:f for f in arrow.animation_data.action.fcurves if f.data_path=='rotation_quaternion'};previous=None;corrected=[]
 from mathutils import Quaternion
 for i in range(len(fs[0].keyframe_points)):
  q=Quaternion([fs[c].keyframe_points[i].co.y for c in range(4)])
  if previous is not None and q.dot(previous)<0:
   q.negate();corrected.append(fs[0].keyframe_points[i].co.x)
   for c in range(4):fs[c].keyframe_points[i].co.y=q[c]
  previous=q.copy()
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 rows=actual_audit(scene,arrow,arms)
 for m in body.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 bodyrows=actual_audit(scene,arrow,body,times=[1,8.5,11.75,20,31,31.875,32,32.125,33,35,40])
 bad=[r for r in rows+bodyrows if r['L_triangle_intersections'] or r['R_triangle_intersections']]
 report=json.loads((OUT/'archery-build.json').read_text());report['intersection_sample_count']=len(bad);report['quaternion_sign_keys_corrected']=corrected;report['protected_actions_hash_final']=protected_hash();assert report['protected_actions_hash']==report['protected_actions_hash_final']
 assert not bad,'Arrow still intersects hands'
 set_frame(scene,20);bpy.ops.wm.save_as_mainfile(filepath=str(DEST));report['scene_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest()
 (OUT/'archery-build.json').write_text(json.dumps(report,indent=2));(OUT/'archery-clearance.json').write_text(json.dumps({'sampling':'quarter-frame 1..40 plus sixteenth-frame 30..35; render subdivision; complete actual arrow triangle intersections against skinned hand/finger/forearm/sleeve triangles; sampled radial shaft envelope includes fletching allowance. Open wrist boundary uses unsigned distance plus explicit axis ray intersection.','samples':rows,'full_body_samples':bodyrows,'intersection_samples':bad},indent=2))
 print(json.dumps({'scene_sha256':report['scene_sha256'],'intersection_samples':len(bad),'quaternion_keys_corrected':len(corrected)},indent=2),flush=True)
 assert not bad,'Arrow still intersects hands'

def main():
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False);sc=bpy.context.scene;arrow=bpy.data.objects['Human_Arrow'];bow=bpy.data.objects['Human_Bow'];arms=bpy.data.objects['V12 | FemaleAdult04 first-person arms'];string=bpy.data.objects['A | working bowstring'];sp=string.data.splines[0];before=protected_hash()
 for m in arms.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels
 original={}
 for f in range(1,145):
  set_frame(sc,f);original[f]={'matrix':arrow.matrix_world.copy(),'tip':arrow.matrix_world@Vector((0,0,max(v.co.z for v in arrow.data.vertices))),'string':[p.co.copy() for p in sp.points]}
 set_frame(sc,20);trees,_,_=hand_trees(arms);old=arrow.matrix_world;before_clear={s:shaft_clearance(trees[s],old.translation,old.to_quaternion()@Vector((0,0,1)),radius=.007334,start=.059)[0] for s in 'LR'}
 if '--study' in sys.argv:
  
  print('before',before_clear,flush=True)
  for f in [1,9,13,20,31]:
   set_frame(sc,f);trees,_,_=hand_trees(arms);old=arrow.matrix_world.copy()
   for yy in [-.06,-.035,0]:
    for zz in [.11,.145]:
     globals()['REST_LOCAL']=Vector((0,yy,zz));n,d,r,qa=solve_nock(bow.matrix_world,old.translation,trees);print(json.dumps({'frame':f,'local':list(REST_LOCAL),'nock':list(n),'rest':list(r),'qa':qa}),flush=True)
  return
 _geometry(arrow);rest_obj=_rest_object(bow);maxz=max(v.co.z for v in arrow.data.vertices);arrow.animation_data_clear();arrow.rotation_mode='QUATERNION';string.data.animation_data_clear();solutions={};qa_rows=[];previous=None
 for i in range(125):
  f=1+i*.25;set_frame(sc,f);trees,_,_=hand_trees(arms)
  # Before the source release, the old nock is the original source draw hand.
  rig=bpy.data.objects['Rig'];old_nock=(rig.matrix_world@rig.pose.bones['B-handProp.R'].matrix).translation
  n,d,r,qa=solve_nock(bow.matrix_world,old_nock,trees,previous);previous=n;solutions[f]=(n,d,r);qa_rows.append({'frame':f,**qa})
  if i%24==0:print('solved loaded',f,flush=True)
 launch=solutions[32][0];hit=original[35]['tip'];flight_q=(hit-launch).to_track_quat('Z','Y');first_tip=launch+flight_q@Vector((0,0,maxz));old_q35=original[35]['matrix'].to_quaternion();detach=None
 times=sorted(set([1+i*.25 for i in range(125)]+[32+i*.125 for i in range(25)]+[float(f) for f in range(36,145)]))
 prev_q=None
 for f in times:
  set_frame(sc,f)
  if f<32:n,d,rest=solutions[f];q=d.to_track_quat('Z','Y')
  elif f<35:q=flight_q;tip=first_tip.lerp(hit,(f-32)/3);n=tip-q@Vector((0,0,maxz))
  else:
   row=original[int(f)];q=row['matrix'].to_quaternion()@old_q35.inverted()@flight_q;n=row['tip']-q@Vector((0,0,maxz))
  if prev_q is not None and prev_q.dot(q)<0:q.negate()
  prev_q=q.copy()
  arrow.matrix_world=Matrix.Translation(n)@q.to_matrix().to_4x4();arrow.rotation_quaternion=q;arrow.keyframe_insert('location',frame=f);arrow.keyframe_insert('rotation_quaternion',frame=f);arrow.keyframe_insert('scale',frame=f)
  if f<=32:nock=n
  elif f<35:
   brace=bow.matrix_world@Vector((-.327,0,REST_LOCAL.z));axis=bow.matrix_world.to_quaternion()@Vector((1,0,0));held=(n-brace).dot(axis)<0
   nock=n if held else brace
   if not held and detach is None:detach=f
  else:nock=bow.matrix_world@Vector((-.327,0,REST_LOCAL.z if f<=40 else 0))
  if f<=40:
   tips=[bow.matrix_world@Vector((-.327,0,.924)),nock,bow.matrix_world@Vector((-.327,0,-.924))]
  else:tips=[Vector(p[:3]) for p in original[int(f)]['string']]
  for p,co in zip(sp.points,tips):p.co=(*co,1);p.keyframe_insert('co',frame=f)
 for action in [arrow.animation_data.action,string.data.animation_data.action]:
  for fc in action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 assert before==protected_hash(),'Unrelated action changed';diagnostic=diagnostic_camera(sc,bow);audit=actual_audit(sc,arrow,arms);(OUT/'archery-clearance.json').write_text(json.dumps({'samples':audit,'intersection_samples':[r for r in audit if r['L_triangle_intersections'] or r['R_triangle_intersections']]},indent=2));assert not any(r['L_triangle_intersections'] or r['R_triangle_intersections'] for r in audit),'Arrow still intersects hands';set_frame(sc,20);bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
 report={'scene':DEST.name,'scene_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_actions_hash':before,'old_shaft_radius_m':.007334,'new_shaft_radius_m':RADIUS,'physical_rest_bow_local':list(REST_LOCAL),'arrow_tip_impact_frame':35,'bear_tip_positions_preserved_frames':[35,144],'string_detaches_from_arrow_frame':detach,'before_frame20_shaft_clearance':before_clear,'loaded_solver_samples':qa_rows,'gpu_render':False,'final_audit_pending':False,'diagnostic_camera':diagnostic,'intersection_sample_count':sum(bool(r['L_triangle_intersections'] or r['R_triangle_intersections']) for r in audit)};(OUT/'archery-build.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='loaded_solver_samples'},indent=2))
if __name__=='__main__':
 if '--string-audit' in sys.argv:string_audit_saved()
 elif '--contact-audit' in sys.argv:contact_audit_saved()
 elif '--finalize' in sys.argv:finalize_saved()
 else:main()
