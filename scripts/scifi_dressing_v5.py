"""Append the portable CC0 service library without raw candidate dependencies.

Run Blender with --disable-autoexec. The four normalized meshes and their
materials match the pre-curation dressing exactly (see curation-audit.json).
"""
from pathlib import Path
import math
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'assets/v5/models'
LIBRARY = MODELS / 'service-modules.blend'
COLLECTION_NAME = 'V5 | Reused service modules'


def add_scifi_dressing():
    """Return 24 perimeter objects, their collection, sources and dependencies."""
    if bpy.data.collections.get(COLLECTION_NAME):
        raise RuntimeError(f'{COLLECTION_NAME} already exists; avoid duplicate bays')
    if not LIBRARY.is_file():
        raise FileNotFoundError(LIBRARY.relative_to(ROOT))
    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)
    objects, dependencies = [], set()
    source_names = {'wall': 'Wall1', 'locker': 'Locker1', 'pipe': 'pipe_05', 'vent': 'vent_mat'}
    with bpy.data.libraries.load(str(LIBRARY), link=False) as (source, target):
        missing = set(source_names.values()) - set(source.objects)
        if missing:
            raise RuntimeError(f'Curated service library missing meshes: {sorted(missing)}')
        target.objects = list(source_names.values())
    loaded = dict(zip(source_names, target.objects))
    meshes = {kind: obj.data for kind, obj in loaded.items()}
    # Use packed bytes and a repository-relative fallback; no original author
    # directories or raw candidate image paths are required by the saved scene.
    for mesh in meshes.values():
        for material in mesh.materials:
            for node in material.node_tree.nodes:
                if node.type != 'TEX_IMAGE' or not node.image:
                    continue
                image = node.image
                filename = Path(image.filepath).name
                source_file = MODELS / 'textures' / filename
                if not image.packed_file or not source_file.is_file():
                    raise RuntimeError(f'Incomplete curated texture: {filename}')
                image.filepath = '//' + source_file.relative_to(ROOT).as_posix()
                dependencies.add(source_file.relative_to(ROOT).as_posix())
    for obj in loaded.values():
        bpy.data.objects.remove(obj, do_unlink=True)

    def add_part(bay, kind, angle, x, y, z):
        obj = bpy.data.objects.new(f'V5 | Bay {bay:02d} | {kind}', meshes[kind])
        collection.objects.link(obj)
        # -Y is the source front; this rotation points it toward room (0, 2).
        rotation = angle - math.pi / 2
        transform = Matrix.Rotation(rotation, 4, 'Z')
        obj.location = Vector((8.5 * math.cos(angle), 2 + 8.5 * math.sin(angle), 0)) + transform @ Vector((x, y, z))
        obj.rotation_euler.z = rotation
        obj['source_asset'] = 'Irondust / CC0' if kind in ('wall', 'locker') else 'rubberduck + a52 / CC0'
        obj['source_object'] = {'wall': 'Wall1', 'locker': 'Locker1', 'pipe': 'pipe_05', 'vent': 'vent_mat'}[kind]
        objects.append(obj)
        return obj

    for bay, degree in enumerate((0, 36, 72, 108, 144, 180), 1):
        angle = math.radians(degree)
        add_part(bay, 'wall', angle, 0, 0, .14)
        add_part(bay, 'locker', angle, 1.46, 0, .14)
        add_part(bay, 'pipe', angle, -1.49, -.06, .33)
        add_part(bay, 'vent', angle, 0, -.47, .24)

    bpy.context.view_layer.update()
    return {
        'collection': collection,
        'objects': objects,
        'sources': [
            {'author': 'Irondust', 'license': 'CC0-1.0', 'url': 'https://opengameart.org/content/sci-fi-environment-pack', 'file': LIBRARY.relative_to(ROOT).as_posix(), 'objects': ['Wall1', 'Locker1']},
            {'author': 'rubberduck / a52', 'license': 'CC0-1.0', 'url': 'https://opengameart.org/content/pbr-industrial-asset-pack', 'file': LIBRARY.relative_to(ROOT).as_posix(), 'objects': ['pipe_05', 'vent_mat']},
        ],
        'dependencies': sorted(dependencies),
    }
