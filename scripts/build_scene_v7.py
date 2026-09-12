"""Bring the existing performer close to Astra, then reach; preserve V6."""
from pathlib import Path
import sys,hashlib,json
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
source=ROOT/'observatory-v6.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
scene=bpy.context.scene
study='--camera-study' in sys.argv
if not study:
    from heroine_approach_v7 import add_approach_v7
    report=add_approach_v7(scene=scene,endpoint=(-3.0,1.05,.14))
else: report={}
for marker in list(scene.timeline_markers):
    if marker.frame in (345,385):scene.timeline_markers.remove(marker)
for name in ['V6 | The first reach','V6 | The first reach focus']:
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)

def camera(name,cut,lens,keys):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
    focus=bpy.data.objects.new(name+' focus',None);scene.collection.objects.link(focus)
    data.lens=lens;data.sensor_width=36;data.clip_end=300
    data.dof.use_dof=True;data.dof.aperture_fstop=7.1;data.dof.focus_object=focus
    ob.rotation_mode='QUATERNION';previous=None
    for f,pos,target in keys:
        ob.location=pos;q=(Vector(target)-ob.location).to_track_quat('-Z','Y')
        if previous is not None and q.dot(previous)<0:q.negate()
        ob.rotation_quaternion=q;previous=q.copy()
        ob.keyframe_insert('location',frame=f);ob.keyframe_insert('rotation_quaternion',frame=f)
        focus.location=target;focus.keyframe_insert('location',frame=f)
    marker=scene.timeline_markers.new(name,frame=cut);marker.camera=ob
    return ob
camera('V7 | Approach Astra',345,20,[
    (345,(-6.8,-5.0,2.5),(-1.8,1.0,1.8)),
    (424,(-6.4,-4.3,2.55),(-1.7,1.25,1.9)),
])
camera('V7 | Beside Astra',425,24,[
    (425,(-5.0,4.5,2.0),(-1.2,2.0,2.3)),
    (480,(-4.8,4.3,2.05),(-1.1,2.0,2.35)),
])
scene.frame_set(472)
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
bpy.ops.file.make_paths_relative()
dest=ROOT/('observatory-v7-camera-study.blend' if study else 'observatory-v7.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
if not study:
    report.update({'source_scene':source.name,'source_sha256':source_sha,'scene':dest.name,'scene_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'camera_cuts':[345,425],'duration_seconds':24,'previous_version_unchanged':True})
    (ROOT/'renders/v7/approach-performance.json').write_text(json.dumps(report,indent=2)+'\n')
print('V7_SCENE_READY',dest.name)
