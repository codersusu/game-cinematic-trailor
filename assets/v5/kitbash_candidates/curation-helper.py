from pathlib import Path
import bpy, sys, json, hashlib, shutil
from mathutils import Matrix
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from scifi_dressing_v5 import add_scifi_dressing
from audit_scene_v5 import coordinates, node_tree, digest
bpy.ops.wm.read_factory_settings(use_empty=True)
result=add_scifi_dressing()
entries={}
for o in result['objects']:
 m=o.data
 entries[o.name]={'matrix':[list(row) for row in o.matrix_world], 'vertices':coordinates(m.vertices,'co',3),'topology':coordinates(m.loops,'vertex_index',1,'i'),'uv':[coordinates(u.data,'uv',2) for u in m.uv_layers], 'polygon_materials':[p.material_index for p in m.polygons], 'smooth':[p.use_smooth for p in m.polygons], 'materials':[{'name':mat.name,'nodes':node_tree(mat.node_tree)} for mat in m.materials]}
images={i.name:{'sha256':hashlib.sha256(i.packed_file.data).hexdigest(),'colorspace':i.colorspace_settings.name,'size':list(i.size)} for i in bpy.data.images if i.packed_file}
mode='curate' if '--curate' in sys.argv else 'verify'
proof=json.loads(json.dumps({'objects':entries,'images':images,'fingerprint':digest({'objects':entries,'images':images})}));entries=proof['objects']
out=ROOT/'assets/v5/kitbash_candidates'
(out/f'dressing-{mode}-fingerprint.json').write_text(json.dumps(proof,indent=2)+'\n')
if mode=='curate':
 target=ROOT/'assets/v5/models'
 for dep in result['dependencies']:
  source=ROOT/dep;shutil.copy2(source,target/'textures'/source.name)
 for image in bpy.data.images:
  if image.packed_file:image.filepath='//textures/'+Path(image.filepath).name
 prototypes=set()
 for kind, name in [('wall','Wall1'),('locker','Locker1'),('pipe','pipe_05'),('vent','vent_mat')]:
  src=next(o for o in result['objects'] if o.name==f'V5 | Bay 01 | {kind}')
  obj=bpy.data.objects.new(name,src.data);obj.matrix_world=Matrix.Identity(4);obj['source_object']=name;prototypes.add(obj)
 bpy.data.libraries.write(str(target/'service-modules.blend'),prototypes,path_remap='RELATIVE',fake_user=False,compress=True)
 print('CURATED_LIBRARY_READY',len(prototypes),len(images),proof['fingerprint'])
else:
 baseline=json.loads((out/'dressing-curate-fingerprint.json').read_text())
 differences=[n for n in entries if entries[n]!=baseline['objects'].get(n)]
 report={'status':'passed' if proof==baseline else 'failed','baseline_fingerprint':baseline['fingerprint'],'curated_fingerprint':proof['fingerprint'],'object_count':len(entries),'changed_objects':differences,'packed_image_bytes_identical':images==baseline['images']}
 (ROOT/'assets/v5/models/curation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('CURATION_COMPARISON',json.dumps(report))
 assert proof==baseline
