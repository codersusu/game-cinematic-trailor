"""Read-only actual arrow versus full heroine mesh check after impact."""
from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import fix_archery_v13 as v
bpy.ops.wm.open_mainfile(filepath=str(v.DEST),use_scripts=False);sc=bpy.context.scene;body=bpy.data.objects['V12 | FemaleAdult04 full body'];arrow=bpy.data.objects['Human_Arrow']
for mod in body.modifiers:
 if mod.type=='SUBSURF':mod.levels=mod.render_levels
rows=[]
for f in [123]+[x for x in range(35,145) if x!=123]:
 v.set_frame(sc,f);ae,am=v.evaluated(arrow);am.calc_loop_triangles();ap=[ae.matrix_world@x.co for x in am.vertices];af=[tuple(x.vertices) for x in am.loop_triangles];ae.to_mesh_clear();be,bm=v.evaluated(body);bp=[be.matrix_world@x.co for x in bm.vertices];alo=Vector([min(x[k] for x in ap) for k in range(3)]);ahi=Vector([max(x[k] for x in ap) for k in range(3)]);blo=Vector([min(x[k] for x in bp) for k in range(3)]);bhi=Vector([max(x[k] for x in bp) for k in range(3)]);gap=max(max(blo[k]-ahi[k],alo[k]-bhi[k]) for k in range(3));hits=[];nearest=None
 if gap<=0:
  bm.calc_loop_triangles();bf=[tuple(x.vertices) for x in bm.loop_triangles];abt=BVHTree.FromPolygons(ap,af,all_triangles=True);bbt=BVHTree.FromPolygons(bp,bf,all_triangles=True);hits=abt.overlap(bbt);nearest=min(bbt.find_nearest(p)[3] for p in ap)
 be.to_mesh_clear();row={'frame':f,'aabb_separation_m':gap,'arrow_heroine_triangle_intersections':len(hits),'nearest_arrow_vertex_to_skin_m':nearest};rows.append(row)
 if f==123 or hits or len(rows)%20==0:print(json.dumps(row),flush=True)
rows.sort(key=lambda r:r['frame']);bad=[r for r in rows if r['arrow_heroine_triangle_intersections']];report={'scene_sha256':hashlib.sha256(v.DEST.read_bytes()).hexdigest(),'method':'all integer frames35..144 at12fps; evaluated full heroine at render subdivision2, complete actual arrow mesh; exact triangle-BVH overlap after bounding-box rejection; no scene mutation or rendering','samples':rows,'intersection_samples':bad};(v.OUT/'archery-pursuit-full-body-audit.json').write_text(json.dumps(report,indent=2));print('COMPLETE',json.dumps({'frames':len(rows),'intersection_frames':len(bad),'scene_sha256':report['scene_sha256']}),flush=True)
