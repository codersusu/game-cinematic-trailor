"""Read-only V6→V7 preservation and physical approach measurements.
Compares early body/camera evaluation before permitting cached frames1–343.
Measures actual deformed boots, authored platform geometry, and body/hand paths.
No rendering, scene edits, or scene saves. Report: renders/v7/scene-audit.json.
"""
from pathlib import Path
import sys,json,math
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_scene_v6 import (sha,digest,primitives,static_snapshot,matrix_values,sample_time,numeric_comparison,mapping_comparison,WORLD_MATRIX_TOLERANCE)
RIG='Bip01';ROOT_OBJECT='Heroine v4 • native root motion';GALAXY=Vector((0,2,3.7));FLOOR_Z=.14
EARLY_TIMES=list(range(1,344))+[343.5]
PHYSICAL_TIMES=list(range(344,577))
TRANSFORMS={'location','rotation_euler','rotation_quaternion','rotation_axis_angle','rotation_mode','scale','delta_location','delta_rotation_euler','delta_rotation_quaternion','delta_scale'}

def animation_structure(record):
 if record is None:return None
 return {k:v for k,v in record.items() if k!='curves'}

def normalized_static():
 snap=static_snapshot()
 camera_names={o.name for o in bpy.data.objects if o.type=='CAMERA'}
 camera_helpers={o.data.dof.focus_object.name for o in bpy.data.objects if o.type=='CAMERA' and o.data.dof.focus_object}
 snap['camera_objects']={n:snap['objects'][n] for n in camera_names|camera_helpers}
 snap['objects']={n:r for n,r in snap['objects'].items() if n not in camera_names|camera_helpers}
 for name in (RIG,ROOT_OBJECT):
  record=snap['objects'][name];record['animation']=animation_structure(record['animation']);record.pop('matrix_basis',None)
  record['properties']={k:v for k,v in record['properties'].items() if k not in TRANSFORMS}
  record['custom_properties']={k:v for k,v in record['custom_properties'].items() if not k.startswith('v7_')}
 return snap

def camera_evaluation():
 cam=bpy.context.scene.camera;d=cam.data;focus=d.dof.focus_object
 return {'name':cam.name,'matrix':matrix_values(cam.matrix_world),'data':primitives(d),'dof':primitives(d.dof),'focus':matrix_values(focus.matrix_world) if focus else None}

def early_evaluation():
 s=bpy.context.scene;rig=bpy.data.objects[RIG];result={}
 for time in EARLY_TIMES:
  sample_time(s,time);rw=rig.matrix_world.copy()
  result[str(time)]={'bones':{b.name:matrix_values(rw@b.matrix) for b in rig.pose.bones},'rig':matrix_values(rw),'root':matrix_values(bpy.data.objects[ROOT_OBJECT].matrix_world),'camera':camera_evaluation()}
 return result

def trajectories():
 s=bpy.context.scene;rig=bpy.data.objects[RIG];rows={}
 for frame in range(1,577):
  s.frame_set(frame);rw=rig.matrix_world
  points={label:list(rw@rig.pose.bones[bone].head) for label,bone in [('pelvis','Bip01 Pelvis'),('wrist','Bip01 R Hand'),('shoulder','Bip01 R UpperArm'),('head','Bip01 Head'),('left_ankle','Bip01 L Foot'),('right_ankle','Bip01 R Foot')]}
  rows[str(frame)]=points
 return rows

def platform_geometry():
 s=bpy.context.scene;s.frame_set(344);dg=bpy.context.evaluated_depsgraph_get();tiers=[]
 for ob in bpy.data.objects:
  if not ob.name.startswith('V5 | instrument platform') or ob.type!='MESH':continue
  eo=ob.evaluated_get(dg);me=eo.to_mesh();verts=[eo.matrix_world@v.co for v in me.vertices];polys=[list(p.vertices) for p in me.polygons];coords=np.array([list(v) for v in verts]);center=np.array([0.,2.]);radius=float(np.sqrt(((coords[:,:2]-center)**2).sum(axis=1)).max())
  tiers.append({'name':ob.name,'radius_m':radius,'z_min':float(coords[:,2].min()),'z_max':float(coords[:,2].max()),'bvh':BVHTree.FromPolygons(verts,polys,all_triangles=False)})
  eo.to_mesh_clear()
 return tiers

def deformed_geometry_measurements():
 s=bpy.context.scene;root=bpy.data.objects[ROOT_OBJECT];meshes=[o for o in root.children_recursive if o.type=='MESH' and not o.hide_render];tiers=platform_geometry();membership={};rows=[];intersections=[]
 # Actual evaluated vertex membership retains boot weights after subdivision.
 for frame in PHYSICAL_TIMES:
  s.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();boots={'left':[],'right':[]};actor=[]
  for ob in meshes:
   eo=ob.evaluated_get(dg);me=eo.to_mesh();values=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',values);values=values.reshape(-1,3);mw=np.array(eo.matrix_world)
   if not np.isfinite(values).all() or not np.isfinite(mw).all():raise RuntimeError(f'Nonfinite evaluated geometry/transform: {ob.name} frame{frame}')
   world=values[:,0,None]*mw[:3,0]+values[:,1,None]*mw[:3,1]+values[:,2,None]*mw[:3,2]+mw[:3,3]
   if not np.isfinite(world).all():raise RuntimeError(f'Nonfinite world geometry: {ob.name} frame{frame}')
   actor.append(world)
   cache_key=(ob.name,len(me.vertices))
   if cache_key not in membership:
    names={g.index:g.name for g in ob.vertex_groups};masks={side:[] for side in ['left','right']}
    for v in me.vertices:
     for side,letter in [('left','L'),('right','R')]:
      if sum(g.weight for g in v.groups if names.get(g.group) in [f'Bip01 {letter} Foot',f'Bip01 {letter} Toe0'])>.60:masks[side].append(v.index)
    membership[cache_key]=masks
   for side in boots:
    idx=membership[cache_key][side]
    if idx:boots[side].append(world[idx])
   eo.to_mesh_clear()
  if not actor or any(not boots[side] for side in boots):raise RuntimeError('Evaluated character/boot geometry is missing')
  all_points=np.concatenate(actor);foot_record={}
  for side in boots:
   points=np.concatenate(boots[side]);lowest=float(points[:,2].min());sole=points[points[:,2]<=lowest+.004]
   foot_record[side]={'sole_clearance_m':lowest-FLOOR_Z,'low_sole_center_xyz':list(map(float,sole.mean(axis=0)))}
  tier_records=[]
  for tier in tiers:
   vertical=all_points[(all_points[:,2]>=tier['z_min']-1e-6)&(all_points[:,2]<=tier['z_max']+1e-6)]
   if not len(vertical):continue
   radial=np.sqrt(vertical[:,0]**2+(vertical[:,1]-2)**2);margin=radial-tier['radius_m'];possible=vertical[margin<0]
   max_depth=0.;inside=0
   for pt in possible:
    nearest,normal,_,distance=tier['bvh'].find_nearest(Vector(pt))
    if nearest is not None and (Vector(pt)-nearest).dot(normal)<-1e-6:
     inside+=1;max_depth=max(max_depth,float(distance))
   tier_records.append({'name':tier['name'],'minimum_cylinder_margin_m':float(margin.min()),'inside_evaluated_platform_vertices':inside,'maximum_actual_penetration_m':max_depth})
   if max_depth>.003:intersections.append({'frame':frame,'tier':tier['name'],'maximum_penetration_m':max_depth,'inside_vertices':inside})
  rows.append({'frame':frame,'feet':foot_record,'platform_tiers':tier_records})
 contacts=[]
 for side in ['left','right']:
  was_airborne=False;previous=-99
  for row in rows:
   clearance=row['feet'][side]['sole_clearance_m']
   if clearance>.025:was_airborne=True
   if was_airborne and clearance<.012 and row['frame']-previous>7:
    previous=row['frame'];contacts.append({'frame':previous,'time_seconds':(previous-1)/24,'foot':side,'sole_clearance_m':clearance});was_airborne=False
 contacts.sort(key=lambda c:c['frame'])
 support=[min(row['feet'][side]['sole_clearance_m'] for side in ['left','right']) for row in rows]
 return {'method':'World-space evaluated boot vertices identified by native foot/toe skin weights; convex-platform candidate points tested against actual beveled platform BVHs. This reports vertex penetration, not a full swept-volume collision proof.','contact_event_definition':'A descending boot enters the12mm floor band after lifting above25mm; this is an approximate contact cue, not an exact collision timestamp.','all_evaluated_vertices_finite':True,'floor_z_m':FLOOR_Z,'sample_frames':[344,576],'platforms':[{k:v for k,v in t.items() if k!='bvh'} for t in tiers],'contacts':contacts,'support_clearance_range_m':[min(support),max(support)],'maximum_positive_support_gap_m':max(support),'platform_penetrations_over_3mm':intersections,'frames':rows}

def trajectory_summary(baseline,current):
 start=current['343'];finish=current['576'];steps=[];baseline_steps=[];hand_steps=[]
 for f in range(2,577):
  step=(Vector(current[str(f)]['pelvis'])-Vector(current[str(f-1)]['pelvis'])).length
  if f>=344:
   steps.append((step,f));hand_steps.append(((Vector(current[str(f)]['wrist'])-Vector(current[str(f-1)]['wrist'])).length,f))
  if 38<=f<=217:baseline_steps.append((Vector(baseline[str(f)]['pelvis'])-Vector(baseline[str(f-1)]['pelvis'])).length)
 def radius(p):return math.hypot(p[0],p[1]-2)
 body_gain=radius(start['pelvis'])-radius(finish['pelvis'])
 initial_hand_distance=(Vector(start['wrist'])-GALAXY).length
 baseline_best=min((Vector(baseline[str(f)]['wrist'])-GALAXY).length for f in range(344,577))
 candidate_best=min(((Vector(current[str(f)]['wrist'])-GALAXY).length,f) for f in range(344,577))
 direct_distance=(Vector(finish['pelvis'])-Vector(start['pelvis'])).length
 baseline_peak=max(baseline_steps)
 return {'start_frame':343,'end_frame':576,'start_pelvis_xyz':start['pelvis'],'end_pelvis_xyz':finish['pelvis'],'initial_horizontal_distance_to_astra_m':radius(start['pelvis']),'final_horizontal_distance_to_astra_m':radius(finish['pelvis']),'horizontal_distance_reduction_m':body_gain,'direct_body_displacement_m':direct_distance,'pelvis_path_length_m':sum(x[0] for x in steps),'maximum_adjacent_pelvis_displacement_m':max(steps)[0],'maximum_adjacent_pelvis_displacement_frame':max(steps)[1],'native_first_walk_maximum_adjacent_pelvis_displacement_m':baseline_peak,'teleport_guardrail_m':baseline_peak*3,'maximum_adjacent_wrist_displacement_m':max(hand_steps)[0],'maximum_adjacent_wrist_displacement_frame':max(hand_steps)[1],'initial_hand_distance_to_astra_m':initial_hand_distance,'baseline_v6_best_hand_distance_to_astra_m':baseline_best,'v7_best_hand_distance_to_astra_m':candidate_best[0],'v7_best_hand_frame':candidate_best[1],'hand_distance_improvement_vs_v6_m':baseline_best-candidate_best[0]}

def main():
 out=ROOT/'renders/v7';out.mkdir(parents=True,exist_ok=True);source=ROOT/'observatory-v6.blend';candidate=ROOT/'observatory-v7.blend';report={'source_scene':source.name,'candidate_scene':candidate.name,'status':'failed','errors':[]};errors=report['errors']
 try:
  report.update(source_sha256=sha(source),candidate_sha256=sha(candidate))
  bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);old=normalized_static();old_early=early_evaluation();old_paths=trajectories()
  bpy.ops.wm.open_mainfile(filepath=str(candidate),use_scripts=False);new=normalized_static();new_early=early_evaluation();new_paths=trajectories()
  checks={key:mapping_comparison(old[key],new[key]) for key in ['objects','meshes','materials','node_groups','images']}
  checks['render_world_compositor']={'passed':old['settings']==new['settings'],'baseline_sha256':digest(old['settings']),'candidate_sha256':digest(new['settings']),'changed_sections':[k for k in old['settings'] if old['settings'][k]!=new['settings'][k]]}
  checks['early_body_root_and_cameras']=numeric_comparison(old_early,new_early,WORLD_MATRIX_TOLERANCE)
  old_early_markers=[m for m in old['markers'] if m['frame']<344];new_early_markers=[m for m in new['markers'] if m['frame']<344]
  checks['early_camera_cuts']={'passed':old_early_markers==new_early_markers,'baseline':old_early_markers,'candidate':new_early_markers}
  for key,check in checks.items():
   if not check['passed']:errors.append('Failed preservation check: '+key)
  errors.extend(new['dependency_errors'])
  if new['embedded_texts']:errors.append('Candidate contains embedded text/scripts')
  motion=trajectory_summary(old_paths,new_paths);geometry=deformed_geometry_measurements()
  physical_checks={
   'meaningful_body_approach':{'passed':motion['horizontal_distance_reduction_m']>.5,'measured_reduction_m':motion['horizontal_distance_reduction_m'],'required_reduction_m':.5},
   'no_significant_root_teleport':{'passed':motion['maximum_adjacent_pelvis_displacement_m']<motion['teleport_guardrail_m'],'largest_step_m':motion['maximum_adjacent_pelvis_displacement_m'],'native_first_walk_scaled_guardrail_m':motion['teleport_guardrail_m']},
   'hand_closer_than_v6':{'passed':motion['hand_distance_improvement_vs_v6_m']>.25,'measured_improvement_m':motion['hand_distance_improvement_vs_v6_m'],'required_improvement_m':.25},
   'new_walking_contacts':{'passed':len(geometry['contacts'])>=2,'contacts':geometry['contacts']},
   'boots_above_floor':{'passed':geometry['support_clearance_range_m'][0]>=-.01,'minimum_clearance_m':geometry['support_clearance_range_m'][0],'penetration_allowance_m':.01},
   'walking_stays_supported':{'passed':geometry['maximum_positive_support_gap_m']<.035,'maximum_support_gap_m':geometry['maximum_positive_support_gap_m'],'allowed_gap_m':.035},
   'no_platform_vertex_penetration_over_3mm':{'passed':not geometry['platform_penetrations_over_3mm'],'intersections':geometry['platform_penetrations_over_3mm']}}
  for key,check in physical_checks.items():
   if not check['passed']:errors.append('Failed measured approach requirement: '+key)
  if sha(source)!=report['source_sha256'] or sha(candidate)!=report['candidate_sha256']:errors.append('A saved scene changed during the read-only audit')
  report.update(checks=checks,physical_checks=physical_checks,motion=motion,deformed_geometry=geometry,camera_cuts=new['markers'],camera_changes={'removed':sorted(old['camera_objects'].keys()-new['camera_objects'].keys()),'added':sorted(new['camera_objects'].keys()-old['camera_objects'].keys())},images=new['images'],dependency_errors=new['dependency_errors'],early_reuse={'frames':[1,343],'additional_motion_blur_sample':343.5,'all_rig_bones':len(bpy.data.objects[RIG].pose.bones),'early_samples':len(EARLY_TIMES),'safe':all(c['passed'] for c in checks.values()) and not new['dependency_errors']},status='passed' if not errors else 'failed')
 except Exception as exc:errors.append(type(exc).__name__+': '+str(exc))
 finally:(out/'scene-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('V7_SCENE_AUDIT',report['status'],errors)
 if errors:raise RuntimeError('; '.join(errors))

if __name__=='__main__':main()
