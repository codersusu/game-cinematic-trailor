"""Distance-based preview LODs; full-resolution source meshes remain untouched.

Call optimize_forest_lods(bpy.context.scene) after V10 environment placement.
This only reassigns selected vegetation collection instances. It neither saves
the scene nor renders. Distances use XY paths at every integer animation frame.
"""
import time

import bpy
from mathutils import Vector


def optimize_forest_lods(scene, sapling_distance=8.0, tree_distance=45.0,
                         sapling_ratio=.22, tree_ratio=.20):
    started = time.monotonic()
    original_frame = scene.frame_current
    original_subframe = scene.frame_subframe
    samples = []
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        for name in ('V9 | First-person escape', 'V9 | Third-person escape'):
            obj = bpy.data.objects.get(name)
            if obj:
                p = obj.matrix_world.translation
                samples.append(Vector((p.x, p.y)))
        for name, bone in (('Rig', 'B-hips'), ('RigRoot', 'RigSpine2')):
            obj = bpy.data.objects.get(name)
            if obj and obj.pose and bone in obj.pose.bones:
                p = obj.matrix_world @ obj.pose.bones[bone].head
                samples.append(Vector((p.x, p.y)))
    scene.frame_set(original_frame, subframe=original_subframe)
    if not samples:
        raise ValueError('No actor/camera path samples; refusing distance LOD assignment')

    selected = []
    eligible = {'sapling': 0, 'far_tree': 0}
    for obj in list(scene.objects):
        if obj.hide_render or obj.instance_type != 'COLLECTION' or not obj.instance_collection:
            continue
        if obj.name.startswith('V10 | Understory conifer |'):
            kind, threshold, ratio = 'sapling', sapling_distance, sapling_ratio
        elif obj.name.startswith(('V10 | Wooded background |', 'V10 | Far treeline |')):
            kind, threshold, ratio = 'far_tree', tree_distance, tree_ratio
        else:
            continue
        eligible[kind] += 1
        # Existing optimized instances are left alone on repeated calls.
        if obj.instance_collection.get('v10_preview_lod'):
            continue
        p = obj.matrix_world.translation
        distance = min((Vector((p.x, p.y)) - q).length for q in samples)
        if distance > threshold:
            selected.append((obj, kind, ratio, distance))

    staging = bpy.data.collections.new('V10 LOD temporary CPU evaluation')
    scene.collection.children.link(staging)
    variants, counts, source_records = {}, {'sapling': 0, 'far_tree': 0}, []
    instance_before = instance_after = 0
    try:
        for obj, kind, ratio, distance in selected:
            source = obj.instance_collection
            key = (source.name, ratio)
            if key not in variants:
                collection = bpy.data.collections.new(source.name + ' | preview LOD')
                collection.instance_offset = source.instance_offset.copy()
                collection['v10_preview_lod'] = True
                collection['source_collection'] = source.name
                before = after = 0
                for original in source.all_objects:
                    if original.type != 'MESH':
                        continue
                    copy = original.copy()
                    copy.data = original.data.copy()
                    copy.animation_data_clear()
                    copy.parent = None
                    copy.matrix_world = original.matrix_world.copy()
                    copy.name = original.name + ' | preview LOD'
                    staging.objects.link(copy)
                    copy.data.calc_loop_triangles()
                    source_triangles = len(copy.data.loop_triangles)
                    before += source_triangles
                    # Collapse preserves UV layers/material indices; triangulating
                    # its result avoids accidental n-gon tessellation changes.
                    modifier = copy.modifiers.new('Distance preview reduction', 'DECIMATE')
                    modifier.decimate_type = 'COLLAPSE'
                    modifier.ratio = ratio
                    modifier.use_collapse_triangulate = True
                    bpy.context.view_layer.update()
                    evaluated = copy.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    reduced = bpy.data.meshes.new_from_object(
                        evaluated, preserve_all_data_layers=True,
                        depsgraph=bpy.context.evaluated_depsgraph_get())
                    reduced.name = original.data.name + ' | preview LOD'
                    old_copy_mesh = copy.data
                    copy.modifiers.clear()
                    copy.data = reduced
                    reduced.calc_loop_triangles()
                    after += len(reduced.loop_triangles)
                    collection.objects.link(copy)
                    staging.objects.unlink(copy)
                    if old_copy_mesh.users == 0:
                        bpy.data.meshes.remove(old_copy_mesh)
                    if not reduced.uv_layers and original.data.uv_layers:
                        raise RuntimeError('LOD lost UV layers: ' + original.name)
                variants[key] = (collection, before, after)
                source_records.append({'source_collection': source.name,
                    'lod_collection': collection.name, 'ratio': ratio,
                    'original_triangles': before, 'lod_triangles': after})
            collection, before, after = variants[key]
            obj.instance_collection = collection
            obj['v10_lod_min_path_distance_m'] = distance
            counts[kind] += 1
            instance_before += before
            instance_after += after
    finally:
        bpy.data.collections.remove(staging)
        scene.frame_set(original_frame, subframe=original_subframe)
    return {'gpu_rendered': False, 'elapsed_seconds': time.monotonic() - started,
        'distance_method': 'Minimum XY distance to both cameras, human hips and bear spine at every integer frame',
        'sapling_distance_m': sapling_distance, 'tree_distance_m': tree_distance,
        'eligible_instances': eligible, 'reassigned_instances': counts,
        'modified_instance_triangles_before': instance_before,
        'modified_instance_triangles_after': instance_after,
        'triangle_reduction_fraction': 1 - instance_after / instance_before if instance_before else 0,
        'source_variants': source_records, 'full_source_meshes_unchanged': True,
        'limitations': ['Distant alpha foliage silhouettes require a preview image check.',
                       'Reduced instance triangle counts are not a GPU memory or render-time benchmark.']}
