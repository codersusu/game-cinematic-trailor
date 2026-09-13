"""Lightweight exact-curve audit for the isolated V8 finger layer."""
from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'observatory-v7.blend'
study=ROOT/'observatory-v8-finger-study.blend'
bpy.ops.wm.open_mainfile(filepath=str(study),use_scripts=False)
s=bpy.context.scene;r=bpy.data.objects['Bip01'];after=r.animation_data.action
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
    loaded.actions=[name for name in available.actions if name=='V7 | Native second approach and nearby reach']
before=loaded.actions[0]
def allowed(path):return path.startswith('pose.bones["Bip01 R Finger') and path.endswith('rotation_quaternion')
errors=[];unchanged=0;maximum_early_difference=0
for old in before.fcurves:
    new=after.fcurves.find(old.data_path,index=old.array_index)
    if new is None:errors.append('Missing curve '+old.data_path);continue
    if not allowed(old.data_path):
        a=[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in old.keyframe_points]
        b=[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in new.keyframe_points]
        if a!=b:errors.append('Unexpected change '+old.data_path)
        unchanged+=1
    else:
        for frame in [x/2 for x in range(2,835)]:
            maximum_early_difference=max(maximum_early_difference,abs(old.evaluate(frame)-new.evaluate(frame)))
if maximum_early_difference>1e-7:errors.append('Earlier finger animation changed')
rows=[]
for frame in [418,421,438,456,478,510,576]:
    s.frame_set(frame)
    def p(n):return r.matrix_world@r.pose.bones[n].head
    index=p('Bip01 R Finger1');distal=p('Bip01 R Finger12')
    direction=(distal-index).normalized()
    angle=math.degrees(direction.angle(Vector((0,2,3.7))-index))
    rows.append({'frame':frame,'index_ray_error_degrees':angle,'index_knuckle':list(index),'index_distal_joint':list(distal)})
report={'status':'passed' if not errors else 'failed','errors':errors,'unchanged_nonfinger_curves':unchanged,
 'maximum_finger_curve_difference_through_417':maximum_early_difference,
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'study_sha256':hashlib.sha256(study.read_bytes()).hexdigest(),
 'rows':rows,'visual_review':{'status':'three_workbench_views_inspected','frame':478,'views':['palm','back','side'],
 'observations':['Index finger is extended; other three fingers are individually curled with open space toward palm.','Thumb remains relaxed beside the index.','Original mesh topology limits knuckle detail in this magnified diagnostic view.'],
 'production_render_performed':False}}
(ROOT/'previews/v8/finger/gesture-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not errors
