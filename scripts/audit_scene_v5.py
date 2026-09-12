"""Read-only V4→V5 preservation, architecture and dependency audit.

Run: blender --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v5.py
Both saved scenes are loaded for comparison; neither is modified on disk.
"""
from pathlib import Path
from array import array
import hashlib
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ROOT_NAMES = ('Heroine v4 • native root motion', 'GALAXY V3 | master')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def coordinates(items, property_name, width, code='f'):
    values = array(code, [0]) * (len(items) * width)
    if values:
        items.foreach_get(property_name, values)
    return hashlib.sha256(values.tobytes()).hexdigest()


def simple(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bpy.types.ID):
        return {'id': value.name, 'type': value.bl_rna.identifier}
    try:
        return [simple(v) for v in value]
    except TypeError:
        return str(value)


def animation(owner):
    ad = getattr(owner, 'animation_data', None)
    if not ad:
        return None
    action = ad.action
    curves = []
    if action:
        for fc in action.fcurves:
            curves.append({'path': fc.data_path, 'index': fc.array_index,
                           'extrapolation': fc.extrapolation,
                           'keys': [{'co': list(k.co), 'left': list(k.handle_left), 'right': list(k.handle_right),
                                     'interpolation': k.interpolation, 'left_type': k.handle_left_type,
                                     'right_type': k.handle_right_type, 'easing': k.easing} for k in fc.keyframe_points],
                           'modifiers': [{'type': m.type, 'mute': m.mute} for m in fc.modifiers]})
    return {'action': action.name if action else None,
            'curves_sha256': digest(curves), 'fcurves': len(curves),
            'keyframes': sum(len(c['keys']) for c in curves),
            'drivers': [{'path': f.data_path, 'index': f.array_index, 'expression': f.driver.expression} for f in ad.drivers],
            'nla_tracks': len(ad.nla_tracks)}


def node_tree(tree):
    if not tree:
        return None
    return {'nodes': [{'name': n.name, 'type': n.bl_idname,
                       'image': n.image.name if hasattr(n, 'image') and n.image else None,
                       'operation': getattr(n, 'operation', None),
                       'inputs': [(s.identifier, simple(s.default_value)) for s in n.inputs if hasattr(s, 'default_value')]}
                      for n in tree.nodes],
            'links': sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in tree.links),
            'animation': animation(tree)}


def family(name):
    root = bpy.data.objects.get(name)
    if root is None:
        return []
    return [root] + list(root.children_recursive)


def snapshot():
    bpy.context.scene.frame_set(1)
    result = {}
    for root_name in ROOT_NAMES:
        entries = {}
        for obj in sorted(family(root_name), key=lambda o: o.name):
            item = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                    'basis': [list(r) for r in obj.matrix_basis], 'animation': animation(obj),
                    'hidden': [obj.hide_render, obj.hide_viewport]}
            if obj.type == 'MESH':
                mesh = obj.data
                item['mesh'] = {'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
                                'coordinates_sha256': coordinates(mesh.vertices, 'co', 3),
                                'topology_sha256': coordinates(mesh.loops, 'vertex_index', 1, 'i'),
                                'uv_sha256': [coordinates(uv.data, 'uv', 2) for uv in mesh.uv_layers]}
                if mesh.shape_keys:
                    item['shape_keys'] = {'keys': [{'name': k.name, 'coordinates_sha256': coordinates(k.data, 'co', 3),
                                                   'value_at_frame_1': k.value} for k in mesh.shape_keys.key_blocks],
                                          'animation': animation(mesh.shape_keys)}
                item['modifiers'] = [{'name': m.name, 'type': m.type, 'show_render': m.show_render,
                                      'object': m.object.name if hasattr(m, 'object') and m.object else None,
                                      'levels': getattr(m, 'levels', None), 'render_levels': getattr(m, 'render_levels', None)} for m in obj.modifiers]
                item['material_sha256'] = digest([{'name': m.name, 'tree': node_tree(m.node_tree)} if m else None for m in mesh.materials])
            elif obj.type == 'ARMATURE':
                item['bones_sha256'] = digest([{'name': b.name, 'parent': b.parent.name if b.parent else None,
                                               'matrix': [list(row) for row in b.matrix_local]} for b in obj.data.bones])
                item['bones'] = len(obj.data.bones)
            elif obj.type == 'CURVE':
                item['curve_sha256'] = digest([{'type': s.type, 'points': [list(p.co) for p in s.points],
                                                'bezier': [list(p.co) for p in s.bezier_points]} for s in obj.data.splines])
            entries[obj.name] = item
        result[root_name] = entries
    return result


def bounds(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
    if not points:
        raise RuntimeError('No evaluated geometry for bounds')
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def main():
    out = ROOT / 'renders/v5'
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'observatory-v4.blend'), use_scripts=False)
    baseline = snapshot()
    v4_objects = {o.name: o.type for o in bpy.data.objects}
    v4_sha = hashlib.sha256((ROOT / 'observatory-v4.blend').read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'observatory-v5.blend'), use_scripts=False)
    candidate = snapshot()
    scene = bpy.context.scene
    errors = []
    preservation = {}
    for root in ROOT_NAMES:
        old, new = baseline[root], candidate[root]
        changed = [n for n in old.keys() & new.keys() if old[n] != new[n]]
        record = {'baseline_count': len(old), 'candidate_count': len(new),
                  'baseline_sha256': digest(old), 'candidate_sha256': digest(new),
                  'missing_objects': sorted(old.keys() - new.keys()), 'added_objects': sorted(new.keys() - old.keys()),
                  'changed_objects': sorted(changed),
                  'changed_fields': {n: [k for k in old[n].keys() | new[n].keys() if old[n].get(k) != new[n].get(k)] for n in changed},
                  'object_fingerprints': {n: digest(v) for n, v in new.items()}}
        record['passed'] = bool(old) and old == new
        preservation[root] = record
        if not record['passed']:
            errors.append(f'Preservation mismatch: {root}')
    preserved_names = set().union(*(set(entries) for entries in candidate.values()))
    retained_legacy_meshes = sorted(o.name for o in bpy.data.objects if o.type == 'MESH' and o.name in v4_objects and o.name not in preserved_names)
    if retained_legacy_meshes:
        errors.append('Unexpected legacy environmental meshes remain')
    images, missing, outside = [], [], []
    for im in bpy.data.images:
        if im.source not in ('FILE', 'TILED'):
            continue
        packed = bool(im.packed_file or len(im.packed_files))
        path = Path(bpy.path.abspath(im.filepath)) if im.filepath else None
        relative = None
        if path:
            try:
                relative = path.resolve().relative_to(ROOT).as_posix()
            except ValueError:
                relative = path.name
                if not packed:
                    outside.append(im.name)
            if not packed and not path.is_file():
                missing.append(im.name)
        elif not packed:
            missing.append(im.name)
        images.append({'name': im.name, 'path': relative, 'packed': packed, 'dimensions': list(im.size)})
    if missing or outside:
        errors.append('Unresolved or external unpacked image dependencies')
    rig = bpy.data.objects.get('Bip01')
    face = next((o for o in family(ROOT_NAMES[0]) if o.type == 'MESH' and o.data.shape_keys and 'AK_25_JawOpen' in o.data.shape_keys.key_blocks), None)
    if not rig or not face:
        raise RuntimeError('Native V4 actor or facial mesh is missing')
    poses = {}
    for frame in (1, 15, 317, 331):
        scene.frame_set(frame)
        poses[str(frame)] = {n: round(face.data.shape_keys.key_blocks[n].value, 4) for n in ('AK_03_BrowInnerUp', 'AK_21_EyeWideLeft', 'AK_25_JawOpen', 'AK_32_MouthFunnel', 'AK_44_MouthSmileLeft')}
    face_ok = (len(rig.data.bones) == 80 and len(face.data.shape_keys.key_blocks) - 1 == 175
               and poses['15']['AK_25_JawOpen'] > poses['1']['AK_25_JawOpen'] + .1
               and poses['317']['AK_32_MouthFunnel'] > .3 and poses['331']['AK_44_MouthSmileLeft'] > .3)
    if not face_ok:
        errors.append('Native rig / facial acting checks failed')
    door_checks = {}
    for frame in (37, 82):
        scene.frame_set(frame)
        actor = bounds(family(ROOT_NAMES[0]))
        left = bounds(family('V5 | sliding airlock leaf -1'))
        right = bounds(family('V5 | sliding airlock leaf 1'))
        margins = [actor['min'][0] - left['max'][0], right['min'][0] - actor['max'][0]]
        door_checks[str(frame)] = {'actor_bounds': actor, 'left_leaf_bounds': left, 'right_leaf_bounds': right,
                                   'open_width_m': right['min'][0] - left['max'][0],
                                   'actor_horizontal_clearance_m': margins,
                                   'passed': min(margins) > .10}
        if min(margins) <= .10:
            errors.append(f'Door lateral clearance failed at frame {frame}')
    cuts = [{'frame': m.frame, 'name': m.name, 'camera': m.camera.name, 'lens_mm': m.camera.data.lens} for m in sorted(scene.timeline_markers, key=lambda m: m.frame) if m.camera]
    if [c['frame'] for c in cuts] != [1, 37, 193, 289, 345, 481]:
        errors.append('Expected six-cut schedule differs')
    rings = [o for o in bpy.data.objects if o.name.startswith('V5 | rotating precision ring ')]
    ring_checks = {o.name: animation(o) for o in rings}
    if len(rings) != 2 or any(not record or not record['fcurves'] for record in ring_checks.values()):
        errors.append('Expected two animated precision ring roots')
    source_objects = [{'name': o.name, 'source_asset': o.get('source_asset'), 'source_object': o.get('source_object')} for o in bpy.data.objects if o.get('source_asset')]
    expected_source_objects = {'Wall1', 'Locker1', 'pipe_05', 'vent_mat'}
    if len(source_objects) != 24 or {r['source_object'] for r in source_objects} != expected_source_objects:
        errors.append('Reused service model names/count differ from planned assets')
    if bpy.data.texts:
        errors.append('Saved scene contains embedded text datablocks')
    preservation_report = {'baseline_scene': 'observatory-v4.blend', 'baseline_sha256': v4_sha,
                           'candidate_scene': 'observatory-v5.blend', 'candidate_sha256': hashlib.sha256((ROOT / 'observatory-v5.blend').read_bytes()).hexdigest(),
                           'comparison': 'Meshes, topology, UVs, facial morph coordinates, bone rest matrices, object and facial fcurves, material node inputs/links, frame-1 transforms and descendant membership.',
                           'roots': preservation, 'retained_legacy_environment_meshes': retained_legacy_meshes,
                           'door_clearance': door_checks, 'status': 'passed' if not errors else 'failed', 'errors': errors}
    report = {'scene': 'observatory-v5.blend', 'sha256': preservation_report['candidate_sha256'],
              'resolution': [scene.render.resolution_x, scene.render.resolution_y], 'fps': scene.render.fps,
              'frames': [scene.frame_start, scene.frame_end], 'engine': scene.render.engine, 'samples': scene.cycles.samples,
              'object_count': len(scene.objects), 'rig_bones': len(rig.data.bones),
              'facial_shapes': len(face.data.shape_keys.key_blocks) - 1, 'source_vertices': len(face.data.vertices),
              'facial_evaluation': poses, 'camera_cuts': cuts, 'images': images,
              'missing_images': missing, 'outside_project_images': outside,
              'reused_source_objects': source_objects, 'animated_precision_rings': ring_checks,
              'preservation_audit': 'renders/v5/preservation-audit.json', 'door_clearance': door_checks,
              'retained_legacy_environment_meshes': retained_legacy_meshes, 'embedded_texts': [t.name for t in bpy.data.texts],
              'status': preservation_report['status'], 'errors': errors}
    (out / 'preservation-audit.json').write_text(json.dumps(preservation_report, indent=2) + '\n')
    (ROOT / 'docs/submission-assets-v5.json').write_text(json.dumps(report, indent=2) + '\n')
    print('V5_SCENE_AUDIT', report['status'], len(images), 'image dependencies;', len(cuts), 'cuts;', errors)
    if errors:
        raise RuntimeError('; '.join(errors))


if __name__ == '__main__':
    main()
