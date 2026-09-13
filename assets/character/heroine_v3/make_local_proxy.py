import bpy,sys,json,time
from pathlib import Path
BASE=Path.cwd();sys.path.insert(0,str(BASE/'scripts'))
from heroine_v3 import _import,_geometry_bounds
bpy.ops.wm.read_factory_settings(use_empty=True)
t0=time.monotonic();objects=_import('assets/character/heroine_v3/master.glb')
meshes=[o for o in objects if o.type=='MESH'];original=sum(len(o.data.polygons) for o in meshes);target=200000
print('START',original,'triangles',flush=True)
for o in meshes:
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 mod=o.modifiers.new('Upload-only 200K rig proxy','DECIMATE');mod.decimate_type='COLLAPSE';mod.ratio=min(1,target/original);mod.use_collapse_triangulate=True
 bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 print('DECIMATED',o.name,len(o.data.polygons),'elapsed',time.monotonic()-t0,flush=True)
for im in bpy.data.images:
 if im.size[0]>2048 or im.size[1]>2048:
  factor=2048/max(im.size);im.scale(round(im.size[0]*factor),round(im.size[1]*factor));im.pack()
 bpy.context.view_layer.update()
path=BASE/'assets/character/heroine_v3/local-rig-proxy.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_image_format='JPEG',export_jpeg_quality=90,export_yup=True,export_animations=False)
lo,hi=_geometry_bounds(meshes)
report={'source':'master.glb','output':str(path),'triangles':sum(len(o.data.polygons) for o in meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'original_triangles':original,'dimensions':list(hi-lo),'seconds':time.monotonic()-t0,'size_bytes':path.stat().st_size,'purpose':'Upload-only rig proxy; original visual master and8Ktexture files untouched'}
(BASE/'assets/character/heroine_v3/local-rig-proxy-stats.json').write_text(json.dumps(report,indent=2));print('PROXY_COMPLETE',json.dumps(report),flush=True)
