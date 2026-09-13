"""Make a public environment/bear copy; never overwrite the production film scene.
Removes all human/archer rig data and derived motion, then reopens to verify.
Run with Blender 4.5 --background --python scripts/package_forest_environment_v13.py.
"""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'bear-bow-forest-v13.blend'
DEST=ROOT/'forest-environment-v13.blend'
OUT=ROOT/'docs/v13/forest-environment-redistribution.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def action_rows(a):
 return [(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for f in a.fcurves] if a else []
def action_hashes():
 return {o.name:hashlib.sha256(repr(action_rows(o.animation_data.action)).encode()).hexdigest() for o in bpy.data.objects if o.animation_data and o.animation_data.action}
def state_hash():
 rows=[]
 for f in range(1,145):
  bpy.context.scene.frame_set(f)
  for n in ['RigRoot','Bear_Animated','V9 | First-person escape','V9 | Third-person escape']:
   o=bpy.data.objects[n];rows.append((f,n,[list(r) for r in o.matrix_world]))
   if o.type=='ARMATURE':rows.append([(b.name,[list(r) for r in b.matrix]) for b in o.pose.bones])
 return hashlib.sha256(repr(rows).encode()).hexdigest()
source_sha=sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
before=state_hash();actions_before=action_hashes()
remove=set()
for o in bpy.data.objects:
 n=o.name.lower()
 if (o.type=='ARMATURE' and o.name!='RigRoot') or (o.type!='CAMERA' and any(t in n for t in ['human','archer','bowstring','femaleadult04','physical arrow rest'])) or n.startswith(('wgt-','cs-')):
  remove.add(o)
changed=True
while changed:
 changed=False
 for o in bpy.data.objects:
  if o not in remove and (o.parent in remove or any(getattr(m,'object',None) in remove for m in o.modifiers)):
   remove.add(o);changed=True
removed=sorted(o.name for o in remove)
for o in remove:bpy.data.objects.remove(o,do_unlink=True)
# Only documented bear, cameras, procedural vegetation wind, and door animations survive.
allowed=[]
for o in bpy.data.objects:
 if o.animation_data:
  if o.name in ['RigRoot','Bear_Animated'] or o.type=='CAMERA' or o.name.startswith(('V10 |','V5 | sliding airlock leaf')):
   if o.animation_data.action:allowed.append(o.animation_data.action)
   for track in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(track)
  else:o.animation_data_clear()
for a in list(bpy.data.actions):
 if a not in allowed:bpy.data.actions.remove(a,do_unlink=True)
# Discard orphan meshes/materials/images/shape keys, even when source files set fake users.
for prop in bpy.data.bl_rna.properties:
 if prop.type=='COLLECTION':
  for data in getattr(bpy.data,prop.identifier):
   if hasattr(data,'use_fake_user'):data.use_fake_user=False
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
for collection in list(bpy.data.collections):
 if any(t in collection.name.lower() for t in ['archer','heroine','femaleadult04']) and not collection.all_objects:bpy.data.collections.remove(collection)
for sc in bpy.data.scenes:
 for key in list(sc.keys()):del sc[key]
 sc['public_copy']='Environment, bear and cameras only. Human/archer/derived motion removed. See docs/v13/redistribution-audit.md.'
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath:
  image.filepath=bpy.path.relpath(bpy.path.abspath(image.filepath),start=str(ROOT))
assert state_hash()==before,'Bear/cameras changed during stripping'
for n,h in action_hashes().items():assert actions_before[n]==h,n
bpy.context.scene.frame_set(20)
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(DEST),use_scripts=False)
assert sha(SOURCE)==source_sha,'Source production scene changed'
assert state_hash()==before,'Saved bear/camera evaluation changed'
violations=[]
for prop in ['objects','meshes','armatures','actions','materials','images','curves','shape_keys']:
 for data in getattr(bpy.data,prop):
  if any(s in data.name.lower() for s in ['human_','humanf','humanm','archer','retargeted','bowstring','shoot stow','femaleadult04 shoot']):violations.append(prop+':'+data.name)
for arm in bpy.data.armatures:
 for b in arm.bones:
  if b.name.startswith(('B-','Bip01')):violations.append('bone:'+b.name)
assert not violations,violations
assert [o.name for o in bpy.data.objects if o.type=='ARMATURE']==['RigRoot']
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
assert not missing,missing
report={'source':SOURCE.name,'source_sha256':source_sha,'destination':DEST.name,'sha256':sha(DEST),'bytes':DEST.stat().st_size,'removed_objects':removed,'remaining_armatures':[o.name for o in bpy.data.objects if o.type=='ARMATURE'],'remaining_object_count':len(bpy.data.objects),'remaining_action_count':len(bpy.data.actions),'retained_animation_classes':['CC-BY bear performance/path','project camera animation','project vegetation wind','project airlock door'], 'source_unchanged':sha(SOURCE)==source_sha,'bear_and_camera_evaluation_identical_all144':True,'retained_action_curves_identical':True,'known_licensed_datablock_or_bone_markers':violations,'missing_external_images':missing,'images':[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images],'texture_portability':'External image paths are relative to repository root; ship assets with this scene.','no_gpu_render':True}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['images','removed_objects']},indent=2))
