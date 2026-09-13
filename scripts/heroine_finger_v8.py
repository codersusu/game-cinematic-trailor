"""An anticipatory, single-index-finger reach layered over the V7 action.

Only the right finger rotation curves from frame 418 are changed. Native gait,
arm targeting, wrist, facial expressions and every earlier key are preserved.
The relaxed middle/ring/little fingers curl sequentially as the arm rises.
"""
import math
import bpy
from mathutils import Quaternion, Euler, Vector, Matrix


def _smooth(a, b, frame):
    x = max(0.0, min(1.0, (frame-a)/(b-a)))
    return x*x*(3.0-2.0*x)


def add_finger_reach_v8(scene=None, rig=None):
    scene = scene or bpy.context.scene
    rig = rig or bpy.data.objects.get('Bip01')
    if rig is None or not rig.animation_data or not rig.animation_data.action:
        raise ValueError('The animated V7 Bip01 performer is required')
    if rig.get('v8_finger_reach'):
        raise ValueError('Finger gesture already applied; start from V7')
    original = rig.animation_data.action
    current = scene.frame_current
    names = [b.name for b in rig.pose.bones if b.name.startswith('Bip01 R Finger')]
    source = {}
    for frame in range(418, 577):
        scene.frame_set(frame)
        source[frame] = {name: rig.pose.bones[name].rotation_quaternion.copy() for name in names}
    action = original.copy()
    action.name = 'V8 | Native approach and curious index-finger reach'
    rig.animation_data.action = action
    # The imported Rocketbox phalanx flexion axis is local Z. Keep a little
    # natural index curvature; use progressively deeper flexion for the smaller
    # fingers, with an open relaxed thumb rather than a tight fist.
    angles = {
        '1': (3, 5, 2),
        '2': (48, 68, 38),
        '3': (54, 74, 42),
        '4': (60, 78, 45),
    }
    previous = {}
    for frame in range(418, 577):
        scene.frame_set(frame)
        for name in names:
            suffix = name.split('Finger')[1]
            native = source[frame][name]
            digit, joint = suffix[0], int(suffix[1]) if len(suffix)>1 else 0
            if digit == '0':
                # Retain native thumb opposition; only softly fold its distal
                # joints. This leaves an air gap and avoids a clenched fist.
                target = native.copy()
                if joint:
                    target = Quaternion((0, 0, 1), math.radians(18 if joint == 1 else 12))
                weight = _smooth(427, 474, frame)
            else:
                euler = native.to_euler('XYZ')
                # Retain subtle metacarpal spread. Distal phalanges have a
                # single flexion axis and are straightened around other axes.
                spread = (euler.x*.45, euler.y*.35) if joint == 0 else (0, 0)
                target = Euler((*spread, math.radians(angles[digit][joint])), 'XYZ').to_quaternion()
                start = 421 + max(0, int(digit)-2)*3
                end = 471 + max(0, int(digit)-2)*2
                weight = _smooth(start, end, frame)
            result = native.slerp(target, weight)
            if name in previous and previous[name].dot(result)<0:
                result.negate()
            previous[name] = result.copy()
            bone = rig.pose.bones[name]
            bone.rotation_mode = 'QUATERNION'
            bone.rotation_quaternion = result
            bone.keyframe_insert('rotation_quaternion', frame=frame, group=name)
        # A small final index-base correction follows the star ray, while the
        # original arm and wrist orientation stay untouched. It is introduced
        # only late in the reach, after the fingers have clearly separated.
        align = _smooth(448, 478, frame)
        if align:
            bpy.context.view_layer.update()
            index = rig.pose.bones['Bip01 R Finger1']
            distal = rig.pose.bones['Bip01 R Finger12']
            knuckle = rig.matrix_world @ index.head
            direction = rig.matrix_world @ distal.head - knuckle
            target = Vector((0, 2, 3.7)) - knuckle
            correction = Quaternion().slerp(direction.normalized().rotation_difference(target.normalized()), align)
            location, rotation, scale = (rig.matrix_world @ index.matrix).decompose()
            old_location, old_scale = index.location.copy(), index.scale.copy()
            index.matrix = rig.matrix_world.inverted() @ Matrix.LocRotScale(location, correction @ rotation, scale)
            index.location, index.scale = old_location, old_scale
            if previous[index.name].dot(index.rotation_quaternion)<0:index.rotation_quaternion.negate()
            previous[index.name] = index.rotation_quaternion.copy()
            index.keyframe_insert('rotation_quaternion', frame=frame, group=index.name)
    paths = {rig.pose.bones[n].path_from_id('rotation_quaternion') for n in names}
    for curve in action.fcurves:
        if curve.data_path in paths:
            for key in curve.keyframe_points:
                if key.co.x >= 418:
                    key.interpolation = 'LINEAR'
    rig['v8_finger_reach'] = 'Extended index, softly curled other fingers, natural thumb'
    scene.frame_set(current)
    return {
        'base_action': original.name,
        'action': action.name,
        'modified_bones': names,
        'modified_channels': ['rotation_quaternion'],
        'preserved_frames': [1, 417],
        'gesture_transition_frames': [421, 475],
        'hold_through_frame': 576,
        'index_star_ray_alignment_frames': [448, 478],
        'finger_flexion_degrees': angles,
        'gait_arm_wrist_and_facial_animation_unchanged': True,
        'gesture': 'Right index reaches toward Astra; middle, ring and little fingers curl softly; thumb remains relaxed',
    }
