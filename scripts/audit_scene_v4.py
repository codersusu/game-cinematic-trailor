"""Audit the saved native actor, facial keys, cameras and portable image assets."""
from pathlib import Path
import hashlib, json
import bpy
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
images=[];missing=[];outside=[]
for image in bpy.data.images:
    if image.source not in ('FILE','TILED'):continue
    packed=bool(image.packed_file or len(image.packed_files))
    path=Path(bpy.path.abspath(image.filepath)) if image.filepath else None
    relative=None
    if path:
        try:relative=str(path.resolve().relative_to(ROOT))
        except ValueError:
            relative=path.name
            if not packed:outside.append(image.name)
        if not packed and not path.is_file():missing.append(image.name)
    images.append({'name':image.name,'path':relative,'packed':packed,'dimensions':list(image.size)})
rig=bpy.data.objects.get('Bip01')
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys and 'AK_25_JawOpen' in o.data.shape_keys.key_blocks)
poses={}
for frame in (1,15,317,331):
    scene.frame_set(frame)
    poses[str(frame)]={name:round(mesh.data.shape_keys.key_blocks[name].value,4) for name in ('AK_03_BrowInnerUp','AK_21_EyeWideLeft','AK_25_JawOpen','AK_32_MouthFunnel','AK_44_MouthSmileLeft')}
assert poses['15']['AK_25_JawOpen']>poses['1']['AK_25_JawOpen']+.1
assert poses['317']['AK_32_MouthFunnel']>.3
assert poses['331']['AK_44_MouthSmileLeft']>.3
assert len(rig.data.bones)==80 and len(mesh.data.shape_keys.key_blocks)-1==175
assert not missing and not outside,(missing,outside)
report={'scene':'observatory-v4.blend','sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'resolution':[scene.render.resolution_x,scene.render.resolution_y],'fps':scene.render.fps,'frames':[scene.frame_start,scene.frame_end],
        'engine':scene.render.engine,'samples':scene.cycles.samples,'rig_bones':len(rig.data.bones),
        'facial_shapes':len(mesh.data.shape_keys.key_blocks)-1,'source_vertices':len(mesh.data.vertices),
        'facial_evaluation':poses,
        'camera_cuts':[{'frame':m.frame,'name':m.name,'camera':m.camera.name,'lens_mm':m.camera.data.lens} for m in sorted(scene.timeline_markers,key=lambda m:m.frame) if m.camera],
        'images':images,'missing_images':missing,'outside_project_images':outside,'status':'passed'}
(ROOT/'docs/submission-assets-v4.json').write_text(json.dumps(report,indent=2)+'\n')
print('V4_SCENE_VERIFIED',len(images),'image dependencies;',len(report['camera_cuts']),'camera cuts; native rig and facial acting passed')
