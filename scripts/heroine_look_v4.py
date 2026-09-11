"""Cycles materials and authored facial acting for the native Rocketbox heroine."""
from pathlib import Path
import math
import bpy
from mathutils import Vector, Matrix, Quaternion

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/character/heroine_v4'


def apply_heroine_look(objects):
    for mesh in (o for o in objects if o.type == 'MESH'):
        for polygon in mesh.data.polygons:
            polygon.use_smooth = True
        eye_groups = {g.index for g in mesh.vertex_groups if g.name in ('Bip01 LEye', 'Bip01 REye')}
        attr = mesh.data.attributes.get('v4_eye_surface') or mesh.data.attributes.new('v4_eye_surface', 'FLOAT', 'POINT')
        for vertex in mesh.data.vertices:
            attr.data[vertex.index].value = max((g.weight for g in vertex.groups if g.group in eye_groups), default=0)
        for material in mesh.data.materials:
            material.use_nodes = True
            nodes, links = material.node_tree.nodes, material.node_tree.links
            nodes.clear()
            shader = nodes.new('ShaderNodeBsdfPrincipled')
            output = nodes.new('ShaderNodeOutputMaterial')
            links.new(shader.outputs['BSDF'], output.inputs['Surface'])
            kind = 'head' if 'head' in material.name else 'opacity' if 'opacity' in material.name else 'body'
            image = nodes.new('ShaderNodeTexImage')
            image.image = bpy.data.images.load(str(ASSETS / f'f004_{kind}_color.tga'), check_existing=True)
            links.new(image.outputs['Color'], shader.inputs['Base Color'])
            shader.inputs['Roughness'].default_value = .48 if kind == 'head' else .6
            shader.inputs['Specular IOR Level'].default_value = .28
            if kind == 'opacity':
                links.new(image.outputs['Alpha'], shader.inputs['Alpha'])
                shader.inputs['Roughness'].default_value = .64
                shader.inputs['Specular IOR Level'].default_value = .22
            else:
                normal = nodes.new('ShaderNodeTexImage')
                normal.image = bpy.data.images.load(str(ASSETS / f'f004_{kind}_normal.tga'), check_existing=True)
                normal.image.colorspace_settings.name = 'Non-Color'
                mapping = nodes.new('ShaderNodeNormalMap')
                mapping.inputs['Strength'].default_value = .35 if kind == 'head' else .65
                links.new(normal.outputs['Color'], mapping.inputs['Color'])
                links.new(mapping.outputs['Normal'], shader.inputs['Normal'])
            if kind == 'head':
                shader.inputs['Subsurface Weight'].default_value = .055
                shader.inputs['Subsurface Radius'].default_value = (1, .4, .2)
                shader.inputs['Subsurface Scale'].default_value = .018
                eyes = nodes.new('ShaderNodeAttribute')
                eyes.attribute_name = 'v4_eye_surface'
                roughness = nodes.new('ShaderNodeMapRange')
                roughness.inputs['To Min'].default_value = .48
                roughness.inputs['To Max'].default_value = .16
                links.new(eyes.outputs['Fac'], roughness.inputs['Value'])
                links.new(roughness.outputs['Result'], shader.inputs['Roughness'])
        subdivision = mesh.modifiers.new('Cinematic surface smoothing', 'SUBSURF')
        subdivision.levels = 1
        subdivision.render_levels = 2


def smoothstep(value):
    t = max(0., min(1., value))
    return t * t * (3 - 2 * t)


def facial_pose(brow=0, wide=0, jaw=0, smile=0, funnel=0, up=0, cheek=0):
    return {'AK_03_BrowInnerUp': brow,
            'AK_04_BrowOuterUpLeft': brow * .72,
            'AK_05_BrowOuterUpRight': brow * .66,
            'AK_21_EyeWideLeft': wide, 'AK_22_EyeWideRight': wide * .96,
            'AK_25_JawOpen': jaw, 'AK_32_MouthFunnel': funnel,
            'AK_38_MouthPucker': funnel * (.20 / .55),
            'AK_44_MouthSmileLeft': smile, 'AK_45_MouthSmileRight': smile * .87,
            'AK_17_EyeLookUpLeft': up, 'AK_18_EyeLookUpRight': up,
            'AK_07_CheekSquintLeft': cheek, 'AK_08_CheekSquintRight': cheek}


def add_facial_performance(keeper, end_frame=576):
    meshes = [o for o in keeper['objects'] if o.type == 'MESH' and o.data.shape_keys]
    beats = [
        (1, facial_pose()), (5, facial_pose(.06, .02)),
        (15, facial_pose(.55, .32, .28)),
        (23, facial_pose(.44, .24, .20)),
        (32, facial_pose(.13, .035, .035)),
        (40, facial_pose(.06, .02)),
        (210, facial_pose(.08, .025)),
        (280, facial_pose(.11, .04, up=.025)),
        (290, facial_pose(.13, .045, up=.045)),
        (305, facial_pose(.31, .21, .16, .025, .18, .075)),
        (317, facial_pose(.36, .25, .42, .055, .55, .09)),
        (331, facial_pose(.19, .095, .09, .52, .04, .085, .12)),
        (344, facial_pose(.14, .06, .04, .19, 0, .07, .035)),
        (400, facial_pose(.10, .025, .025, .13, 0, .065)),
        (end_frame, facial_pose(.09, .02, .02, .11, 0, .06)),
    ]
    blink_frames = (34, 111, 181, 251, 339, 425, 509)
    for mesh in meshes:
        shapes = mesh.data.shape_keys
        shapes.animation_data_clear()
        keys = shapes.key_blocks
        required = set(beats[0][1]) | {'AK_09_EyeBlinkLeft', 'AK_10_EyeBlinkRight'}
        missing = required - set(keys.keys())
        if missing:
            raise ValueError(f'Missing facial controls: {sorted(missing)}')
        for key in keys:
            if key.name != 'Basis':
                key.value = 0
        for frame, values in beats:
            for name, value in values.items():
                keys[name].value = value
                keys[name].keyframe_insert('value', frame=frame)
        for name in ('AK_09_EyeBlinkLeft', 'AK_10_EyeBlinkRight'):
            for frame, value in [(1, 0), (end_frame, 0)] + [(f + offset, value) for f in blink_frames for offset, value in [(-3, 0), (-1, .65), (0, 1), (2, .24), (4, 0)]]:
                keys[name].value = value
                keys[name].keyframe_insert('value', frame=frame)
        for curve in shapes.animation_data.action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = 'BEZIER'
                point.handle_left_type = point.handle_right_type = 'AUTO_CLAMPED'
    return {'surprise_peak_frame': 15, 'wonder_peak_frame': 317,
            'smile_frame': 331, 'blink_frames': list(blink_frames),
            'animated_channels': sorted(required), 'facial_meshes': [o.name for o in meshes]}


def add_instrument_gaze(keeper):
    """Layer a restrained world-space head turn on the preserved native animation."""
    scene, rig = bpy.context.scene, keeper['rig']
    head = rig.pose.bones['Bip01 Head']
    original = []
    for frame in range(1, 577):
        scene.frame_set(frame)
        original.append(head.matrix.copy())
    for frame, matrix in enumerate(original, 1):
        scene.frame_set(frame)
        amount = smoothstep((frame - 208) / 65)
        yaw = math.radians(-42) * amount
        pitch = math.radians(14) * amount
        rotation = Quaternion((0, 0, 1), yaw)
        right = rotation @ Vector((1, 0, 0))
        rotation = Quaternion(right, pitch) @ rotation
        world = rig.matrix_world @ matrix
        pivot = world.translation.copy()
        result = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ world
        head.matrix = rig.matrix_world.inverted() @ result
        head.rotation_mode = 'QUATERNION'
        head.keyframe_insert('rotation_quaternion', frame=frame)
    scene.frame_set(1)


def face_center(keeper, frame):
    bpy.context.scene.frame_set(frame)
    rig = keeper['rig']
    eyes = [rig.matrix_world @ rig.pose.bones[name].head for name in ('Bip01 LEye', 'Bip01 REye')]
    return sum(eyes, Vector()) / 2 + Vector((0, 0, -.035))
