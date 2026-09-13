"""Build and CPU-audit the revised room entrance; never renders."""
from pathlib import Path
import bpy,sys,json,hashlib,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from heroine_entry_v12 import add_room_entry_v12
source=ROOT/'observatory-v11-single-reaction.blend';dest=ROOT/'observatory-v12-run-entry.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
s=bpy.context.scene;r=bpy.data.objects['Bip01'];out=ROOT/'previews/v12';out.mkdir(parents=True,exist_ok=True)
auditframes=[225,226,250,288,289,317,344,345,385,424,425,478,510,575,576]
def sample():
 data={}
 for f in auditframes:
  s.frame_set(f);bpy.context.view_layer.update()
  marker=max((m for m in s.timeline_markers if m.camera and m.frame<=f),key=lambda m:m.frame)
  data[f]={'objects':{o.name:o.matrix_world.copy() for o in s.objects},'bones':{b.name:b.matrix.copy() for b in r.pose.bones},'camera':marker.camera.name,'camera_matrix':marker.camera.matrix_world.copy(),'shapes':{o.name:{k.name:k.value for k in o.data.shape_keys.key_blocks} for o in s.objects if o.type=='MESH' and o.data.shape_keys}}
 return data
before=sample();objects_before=set(bpy.data.objects);shape_actions={o.name:o.data.shape_keys.animation_data.action for o in s.objects if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.animation_data}
report=add_room_entry_v12(s,r)
# Camera sits inside the room and sees her run in, check the doorway over her
# right shoulder, then walk inward. Every existing later cut stays unchanged.
data=bpy.data.cameras.new('V12 | Run through threshold and check behind');camera=bpy.data.objects.new(data.name,data);s.collection.objects.link(camera)
data.lens=28;data.clip_end=250;data.dof.use_dof=False;camera.rotation_mode='QUATERNION';previous=None
for frame,pos,target in [(37,(-1.0,-3.7,1.9),(-3.8,-7.1,1.03)),(77,(-.8,-1.3,1.8),(-3.8,-4.9,1.1)),(108,(-.8,-.5,1.8),(-3.8,-4.3,1.15)),(192,(-.4,2.4,1.8),(-3.8,-1.2,1.12))]:
 camera.location=pos;q=(Vector(target)-camera.location).to_track_quat('-Z','Y')
 if previous is not None and previous.dot(q)<0:q.negate()
 previous=q.copy();camera.rotation_quaternion=q;camera.keyframe_insert('location',frame=frame);camera.keyframe_insert('rotation_quaternion',frame=frame)
for curve in camera.animation_data.action.fcurves:
 for point in curve.keyframe_points:point.interpolation='BEZIER';point.handle_left_type=point.handle_right_type='AUTO_CLAMPED'
next(m for m in s.timeline_markers if m.frame==37).camera=camera
s.frame_start=37;s.frame_end=576;s['v12_entry_note']='Runs inside, checks doorway over shoulder, settles and walks; one later wonder reaction.'
after=sample();rows=[];maxerror=0
for frame in auditframes:
 a,b=before[frame],after[frame];errors=[]
 for name,old in a['objects'].items():
  if name not in b['objects']:raise AssertionError('Original object missing '+name)
  errors.extend(abs(v) for row in (old-b['objects'][name]) for v in row)
 for name,old in a['bones'].items():errors.extend(abs(v) for row in (old-b['bones'][name]) for v in row)
 maximum=max(errors);maxerror=max(maxerror,maximum)
 assert a['camera']==b['camera'] and a['shapes']==b['shapes']
 rows.append({'frame':frame,'maximum_object_and_bone_matrix_difference':maximum,'camera':b['camera'],'facial_shapes_exact':True})
assert maxerror<1e-6,maxerror
for name,action in shape_actions.items():assert bpy.data.objects[name].data.shape_keys.animation_data.action==action
# Sampling source clearance near the doorway proves the running body passes
# between the jambs; camera/render review still judges silhouette and appeal.
mesh=bpy.data.objects.get('f004_hipoly_81_bones_opacity');doorrows=[]
for f in range(37,77):
 s.frame_set(f);ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();points=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 slab=[p for p in points if -6.15<p.y<-5.45]
 if slab:doorrows.append({'frame':f,'minimum_x':min(p.x for p in slab),'maximum_x':max(p.x for p in slab),'maximum_z':max(p.z for p in slab)})
from mathutils.bvhtree import BVHTree
portal=bpy.data.objects['V5 | airlock assembly'];structural=[o for o in portal.children_recursive if o.type=='MESH' and any(n in o.name for n in ['solid door leaf','structural jamb','lintel'])]
door_collisions=[]
for f in range(37,77):
 s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get()
 def tree(ob):
  ev=ob.evaluated_get(deps);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];ps=[list(p.vertices) for p in me.polygons];t=BVHTree.FromPolygons(vs,ps);ev.to_mesh_clear();return t
 actor_tree=tree(mesh)
 for ob in structural:
  pairs=actor_tree.overlap(tree(ob))
  if pairs:door_collisions.append({'frame':f,'object':ob.name,'triangle_pairs':len(pairs)})
assert not door_collisions,door_collisions
s.frame_set(77);s.camera=camera
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert sha(source)==source_sha
report.update({'source_scene':source.name,'source_sha256':source_sha,'scene':dest.name,'scene_sha256':sha(dest),'source_scene_unchanged':True,'new_camera':camera.name,'later_camera_cuts_unchanged':True})
(out/'room-entry-report.json').write_text(json.dumps(report,indent=2)+'\n')
audit={'status':'passed','source_scene':source.name,'source_sha256':source_sha,'scene':dest.name,'scene_sha256':sha(dest),'modified_frame_range':[37,224],'preserved_frame_range':[225,576],'preserved_from_frame':225,'maximum_later_pose_difference':maxerror,'samples':rows,'doorway_body_bounds':doorrows,'doorway_structural_collision_frames':door_collisions,'doorway_collision_check_frames':[37,76],'minimum_boot_clearance_m':min(x['minimum_boot_clearance_m'] for x in report['frames']),'maximum_boot_clearance_m':max(x['minimum_boot_clearance_m'] for x in report['frames']),'facial_animation_actions_unchanged':True,'new_running_asset_provenance':'assets/character/heroine_v12/acquisition.json','production_render_performed':False,'visual_review_pending':True}
(out/'room-entry-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('V12_ROOM_READY',json.dumps({k:v for k,v in audit.items() if k not in ['samples','doorway_body_bounds']}))
