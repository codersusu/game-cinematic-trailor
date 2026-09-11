"""Verify portable image dependencies and record the saved cinematic settings."""
import bpy, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
images=[];missing=[];outside=[]
for im in bpy.data.images:
    if im.source not in ('FILE','TILED'):continue
    packed=bool(im.packed_file or len(im.packed_files))
    path=Path(bpy.path.abspath(im.filepath)) if im.filepath else None
    relative=None
    if path:
        try:relative=str(path.resolve().relative_to(ROOT))
        except ValueError:
            relative=path.name
            if not packed:outside.append(im.name)
        if not packed and not path.is_file():missing.append(im.name)
    images.append({'name':im.name,'path':relative,'packed':packed,'dimensions':list(im.size)})
markers=[]
for marker in scene.timeline_markers:
    if marker.camera:markers.append({'frame':marker.frame,'name':marker.name,'camera':marker.camera.name,'lens_mm':marker.camera.data.lens})
galaxy=bpy.data.objects.get('GALAXY V3 | master')
rig=bpy.data.objects.get('Armature')
master=bpy.data.objects.get('Mesh_0')
report={'scene':'observatory-v3.blend','sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'resolution':[scene.render.resolution_x,scene.render.resolution_y],
        'fps':scene.render.fps,'frames':[scene.frame_start,scene.frame_end],
        'engine':scene.render.engine,'samples':scene.cycles.samples,
        'stars':galaxy.get('star_count') if galaxy else None,
        'rig_bones':len(rig.data.bones) if rig else None,
        'master_triangles':sum(len(p.vertices)-2 for p in master.data.polygons) if master else None,
        'cameras':markers,'images':images,'missing_images':missing,'outside_project_images':outside}
out=ROOT/'docs/submission-assets-v3.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n')
assert not missing and not outside,(missing,outside)
assert report['stars']==5456 and report['rig_bones']==24
assert report['master_triangles']==3024348
print('V3_DEPENDENCIES_VERIFIED',len(images),'images')
