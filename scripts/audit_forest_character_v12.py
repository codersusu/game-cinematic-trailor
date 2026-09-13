"""Read-only evaluated skin/terrain, heroine/bear and door collision audit."""
from pathlib import Path
import bpy,json,hashlib,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'bear-bow-forest-v12.blend'
bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);scene=bpy.context.scene
body=bpy.data.objects['V12 | FemaleAdult04 full body'];bear=bpy.data.objects.get('sm_3_0_0');ground=bpy.data.objects['V10 | Continuous forest terrain']
for m in body.modifiers:
 if m.type=='SUBSURF':m.levels=m.render_levels

def mesh(ob,tree=False):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3);mw=np.array(ev.matrix_world);pts=np.einsum('ij,kj->ik',a,mw[:3,:3])+mw[:3,3];assert np.isfinite(pts).all(),ob.name
 polys=[tuple(p.vertices) for p in me.polygons] if tree else None;ev.to_mesh_clear()
 return pts,polys

def bvh(pts,polys):return BVHTree.FromPolygons([Vector(p) for p in pts],polys)
def overlaps(a,b):return bool(np.all(a.min(0)<=b.max(0)) and np.all(b.min(0)<=a.max(0)))
assembly=bpy.data.objects.get('V5 | airlock assembly');door=list(assembly.children_recursive) if assembly else []
door=[o for o in door if o.type=='MESH' and not o.hide_render]+[o for o in scene.objects if o.type=='MESH' and o.name.startswith('V9 | vestibule') and not o.hide_render]
# Include visibly solid frame pieces parented outside the original assembly.
for o in scene.objects:
 if o.type=='MESH' and not o.hide_render and o.name.startswith('V5 | sliding airlock') and o not in door:door.append(o)
gp,gf=mesh(ground,True);gt=bvh(gp,gf);rows=[];collisions=[];penetrations=[];min_gap=(1e9,None);closest_bear=(1e9,None)
for frame in range(scene.frame_start,scene.frame_end+1):
 scene.frame_set(frame);bpy.context.view_layer.update();hp,hf=mesh(body,True);bp,bf=mesh(bear,True);hb=None
 # The route lies within the low clearing. Candidate vertices below .5 m
 # include every possible terrain penetration; cast against actual evaluated
 # terrain triangles, not only the nominal .14 m floor.
 candidates=np.flatnonzero(hp[:,2]<.5);clearances=[]
 for i in candidates:
  p=hp[i];hit,normal,idx,dist=gt.ray_cast(Vector((p[0],p[1],3)),Vector((0,0,-1)),6)
  if hit is not None:clearances.append((float(p[2]-hit.z),int(i)))
 gap,idx=min(clearances,default=(float(hp[:,2].min()-.14),None))
 if gap<min_gap[0]:min_gap=(gap,frame)
 if gap<-.003:penetrations.append({'frame':frame,'depth_m':-gap,'vertex':idx,'vertices_below_3mm':sum(c<-.003 for c,i in clearances)})
 bear_pairs=0
 bb_gap=float(np.linalg.norm(np.maximum(np.maximum(bp.min(0)-hp.max(0),hp.min(0)-bp.max(0)),0)))
 if bb_gap<closest_bear[0]:closest_bear=(bb_gap,frame)
 if overlaps(hp,bp):hb=bvh(hp,hf);bear_pairs=len(hb.overlap(bvh(bp,bf)))
 door_hits=[]
 for ob in door:
  dp,df=mesh(ob,True)
  if overlaps(hp,dp):
   if hb is None:hb=bvh(hp,hf)
   count=len(hb.overlap(bvh(dp,df)))
   if count:door_hits.append({'object':ob.name,'surface_triangle_pairs':count})
 if bear_pairs or door_hits:collisions.append({'frame':frame,'bear_surface_pairs':bear_pairs,'door':door_hits})
 rows.append({'frame':frame,'skin_vertices':len(hp),'minimum_terrain_clearance_m':gap,'terrain_candidate_vertices':len(candidates),'hero_bear_aabb_gap_m':bb_gap,'bear_surface_pairs':bear_pairs,'door_hits':door_hits})
 if frame%24==0:print('audited',frame,flush=True)
report={'scene':path.name,'scene_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':len(rows),'render_subdivision_levels_used':True,'method':'Evaluated full heroine skin at render subdivision; all candidate vertices below .5m ray-tested against actual V10 terrain. Disjoint world AABBs reject safe actor/door pairs; overlapping AABBs receive full evaluated-surface BVH overlap checks. This is sampled-frame geometry QA, not continuous swept-volume simulation.','minimum_terrain_clearance_m':min_gap[0],'minimum_clearance_frame':min_gap[1],'terrain_penetrations_over_3mm':penetrations,'actor_or_door_surface_collisions':collisions,'closest_hero_bear_aabb_gap_m':closest_bear[0],'closest_hero_bear_frame':closest_bear[1],'door_objects':[o.name for o in door],'rows':rows,'scene_modified_or_saved':False,'gpu_render':False}
out=ROOT/'previews/v12/forest-character-collision-audit.json';out.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
