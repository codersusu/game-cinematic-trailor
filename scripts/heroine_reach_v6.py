"""Bake a restrained standing right-hand reach onto the delivered V5 performer.

Only torso, right clavicle/arm/hand/finger rotations after frame 360 are changed.
The original action is copied; feet, pelvis, root, facial morphs and early keys
remain intact. No IK constraints, handlers or external targets are retained.
Run this file in Blender against V5 for a CPU-only JSON probe; it never saves V5.
"""
from pathlib import Path
import math, json, hashlib
import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT=Path(__file__).resolve().parents[1]
GALAXY=Vector((0,2,3.7))


def smooth(a,b,f):
    t=max(0.,min(1.,(f-a)/(b-a)))
    return t*t*(3-2*t)


def curves(action, before=None, exclude=()):
    data=[]
    for fc in action.fcurves:
        if fc.data_path in exclude:continue
        data.append((fc.data_path,fc.array_index,[(tuple(k.co),None if k.interpolation=='LINEAR' else tuple(k.handle_left),None if k.interpolation=='LINEAR' else tuple(k.handle_right),k.interpolation) for k in fc.keyframe_points if before is None or k.co.x<=before]))
    return hashlib.sha256(repr(data).encode()).hexdigest()


def layer_reach(scene=None, rig=None, probe_path=None):
    scene=scene or bpy.context.scene
    rig=rig or bpy.data.objects.get('Bip01')
    if rig is None or rig.type!='ARMATURE':raise ValueError('The baked V5 Bip01 rig is required')
    if rig.get('v6_reach_layer'):raise ValueError('Reach already layered; build again from V5')
    bones=rig.pose.bones
    # Rocketbox thighs are parented to the lowest Spine: do not rotate it.
    torso=['Bip01 Spine1','Bip01 Spine2']
    chain=['Bip01 R Clavicle','Bip01 R UpperArm','Bip01 R Forearm','Bip01 R Hand']
    fingers=[b.name for b in bones if b.name.startswith('Bip01 R Finger')]
    names=torso+chain+fingers
    for name in names:
        if name not in bones:raise ValueError('Missing bone: '+name)
    if not rig.animation_data or not rig.animation_data.action:raise ValueError('Native baked action required')
    previous_frame=scene.frame_current
    original=rig.animation_data.action
    rotation_paths={bones[n].path_from_id('rotation_quaternion') for n in names}
    prefix_before=curves(original,360)
    unaffected_before=curves(original,exclude=rotation_paths)
    # Snapshot native rotations before adding any keys; breathing remains beneath
    # the layer, and the per-frame native locomotion data is never resampled away.
    native={}
    for f in range(361,577):
        scene.frame_set(f)
        native[f]={n:(bones[n].rotation_quaternion.copy(),bones[n].location.copy(),bones[n].scale.copy()) for n in names}
    action=original.copy();action.name='V6 | Native performance with standing reach'
    rig.animation_data.action=action

    def point(name):return rig.matrix_world@bones[name].head

    def world_rotate(name,q):
        bone=bones[name]
        location=bone.location.copy();scale=bone.scale.copy()
        world=rig.matrix_world@bone.matrix
        pos,rot,size=world.decompose()
        bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(pos,q@rot,size)
        bone.location=location;bone.scale=scale
        bpy.context.view_layer.update()

    def aim_segment(name,child,desired):
        current=point(child)-point(name)
        if current.length>1e-7 and desired.length>1e-7:
            world_rotate(name,current.normalized().rotation_difference(desired.normalized()))

    ik_errors=[]
    for f in range(361,577):
        scene.frame_set(f)
        for name,(q,loc,scale) in native[f].items():
            b=bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=q;b.location=loc;b.scale=scale
        bpy.context.view_layer.update()
        anticipate=smooth(360,385,f)
        rise=smooth(375,448,f)
        settle=smooth(510,576,f)
        # A tiny breathing-like hesitation at the top, not a reaching loop.
        hesitation=math.sin(math.pi*smooth(434,460,f))*.008 if 434<f<460 else 0
        weight=rise*(1-.09*settle)
        turn=anticipate*(.3+.7*weight)
        direction=(GALAXY-point('Bip01 Spine2'));direction.z=0;direction.normalize()
        lean_axis=Vector((0,0,1)).cross(direction).normalized()
        for name,yaw,lean in [('Bip01 Spine1',-4.,1.3),('Bip01 Spine2',-6.,1.3)]:
            q=Quaternion(Vector((0,0,1)),math.radians(yaw)*turn)
            q=Quaternion(lean_axis,math.radians(lean)*weight)@q
            world_rotate(name,q)
        world_rotate('Bip01 R Clavicle',Quaternion(Vector((0,1,0)),math.radians(-3.2)*weight))
        shoulder=point('Bip01 R UpperArm');old_elbow=point('Bip01 R Forearm');old_wrist=point('Bip01 R Hand')
        upper=(old_elbow-shoulder).length;lower=(old_wrist-old_elbow).length
        start=(old_wrist-shoulder);start_dir=start.normalized()
        towards=(GALAXY-shoulder).normalized()
        # Travel along an outward arc rather than pulling the wrist through the
        # chest. End at ~91% arm reach, leaving a clearly bent elbow.
        travel=start_dir.rotation_difference(towards)
        ray=Quaternion().slerp(travel,weight)@start_dir
        distance=start.length*(1-weight)+(upper+lower)*(.915-hesitation-.02*settle)*weight
        distance=min(distance,(upper+lower)*.995)
        wrist=shoulder+ray*distance
        original_pole=old_elbow-shoulder-start_dir*(old_elbow-shoulder).dot(start_dir)
        if original_pole.length<1e-6:original_pole=Vector((.4,-.6,-.2))
        pole=original_pole.normalized().lerp(Vector((.75,-.35,-.75)).normalized(),smooth(360,432,f))
        pole-=ray*pole.dot(ray)
        if pole.length<1e-5:pole=ray.cross(Vector((0,0,1)))
        pole.normalize()
        along=(upper*upper-lower*lower+distance*distance)/(2*distance)
        offset=math.sqrt(max(0.,upper*upper-along*along))
        elbow=shoulder+ray*along+pole*offset
        aim_segment('Bip01 R UpperArm','Bip01 R Forearm',elbow-shoulder)
        actual_elbow=point('Bip01 R Forearm')
        aim_segment('Bip01 R Forearm','Bip01 R Hand',wrist-actual_elbow)
        actual_wrist=point('Bip01 R Hand')
        ik_errors.append((actual_wrist-wrist).length)
        # Fingers follow the starward line, with a softly cupped/upward palm.
        # Use knuckle geometry because FBX display-bone tails are not the limb
        # axes. Limit the roll to avoid excessive wrist pronation.
        longitudinal=point('Bip01 R Finger2')-actual_wrist
        hand_direction=longitudinal.normalized().lerp(towards,weight*.88).normalized()
        world_rotate('Bip01 R Hand',longitudinal.normalized().rotation_difference(hand_direction))
        long_axis=(point('Bip01 R Finger2')-point('Bip01 R Hand')).normalized()
        across=point('Bip01 R Finger4')-point('Bip01 R Finger1')
        normal=long_axis.cross(across).normalized()
        desired=Vector((0,0,1));desired-=long_axis*desired.dot(long_axis)
        if desired.length>.001:
            desired.normalize()
            angle=math.atan2(long_axis.dot(normal.cross(desired)),normal.dot(desired))
            angle=max(math.radians(-55),min(math.radians(55),angle))*weight
            world_rotate('Bip01 R Hand',Quaternion(long_axis,angle))
        relax=smooth(392,460,f)*(1-.12*settle)
        for name in fingers:
            suffix=name.split('Finger')[1]
            source=native[f][name][0]
            if suffix.startswith('0'):
                target=source.slerp(Quaternion(),.22)
            elif len(suffix)==1:
                # Preserve the original individual knuckle spread.
                target=source.slerp(Quaternion((0,0,1),.06+int(suffix)*.012),.48)
            else:
                target=Quaternion((0,0,1),.10 if suffix.endswith('1') else .065)
            bones[name].rotation_quaternion=source.slerp(target,relax)
        for name in names:
            bone=bones[name]
            # Keep quaternion signs continuous for scalar fcurve interpolation.
            oldq=native[f][name][0]
            if bone.rotation_quaternion.dot(oldq)<0:bone.rotation_quaternion.negate()
            bone.keyframe_insert('rotation_quaternion',frame=f,group=name)
    for fc in action.fcurves:
        if fc.data_path in rotation_paths:
            for key in fc.keyframe_points:
                if key.co.x>360:key.interpolation='LINEAR'
    assert curves(action,360)==prefix_before,'Early animation keys changed'
    assert curves(action,exclude=rotation_paths)==unaffected_before,'Root/legs or other native channels changed'
    rig['v6_reach_layer']='Standing, baked only after frame 360'
    report={'strategy':'World-space analytical two-link reach using joint heads; subtle torso/clavicle rotation; finger relaxation; original native action copied',
            'changed_bones':names,'first_modified_frame':361,'visible_anticipation_start':360,'rise_frames':[375,448],
            'hold_through':510,'galaxy_center':list(GALAXY),'pose':'standing','contact_claim':'Attempt toward distant stars; no physical contact',
            'early_animation_keys_identical':True,'non_reach_animation_channels_identical':True,'facial_shapes_modified':False,
            'max_wrist_ik_error_m':max(ik_errors),'keyframes':{}}
    keeper=bpy.data.objects.get('Heroine v4 • native root motion')
    meshes=[o for o in keeper.children_recursive if o.type=='MESH'] if keeper else []
    for f in (345,360,385,408,434,448,472,510,550,576):
        scene.frame_set(f);bpy.context.view_layer.update()
        record={label:list(point(name)) for label,name in [('shoulder','Bip01 R UpperArm'),('elbow','Bip01 R Forearm'),('wrist','Bip01 R Hand'),('middle_knuckle','Bip01 R Finger2'),('head','Bip01 Head'),('left_foot','Bip01 L Foot'),('right_foot','Bip01 R Foot')]}
        verts=[]
        for obj in meshes:
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
            verts.extend(evaluated.matrix_world@v.co for v in mesh.vertices);evaluated.to_mesh_clear()
        if verts:record['body_bounds']={'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]}
        shoulder,elbow,wrist=(Vector(record[k]) for k in ('shoulder','elbow','wrist'))
        record['elbow_inner_angle_degrees']=math.degrees((shoulder-elbow).angle(wrist-elbow))
        record['wrist_distance_to_galaxy_m']=(GALAXY-wrist).length
        report['keyframes'][str(f)]=record
    if probe_path:
        p=Path(probe_path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n')
    scene.frame_set(previous_frame)
    return report


if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'observatory-v5.blend'),use_scripts=False)
    result=layer_reach(probe_path=ROOT/'renders/v6/reach-rig-probe.json')
    print('REACH_LAYER_READY',result['max_wrist_ik_error_m'],result['keyframes']['448'])
