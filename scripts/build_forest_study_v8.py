"""Asset-backed forest staging study. No production rendering is started.

Preserves V7 and reuses its native entrance performance at the same scale/speed.
This is a discovery layout; the combat and final threshold crossing are separate
action studies until their source animations have been reviewed.
"""
from pathlib import Path
import bpy, math, random, json, hashlib
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/v8'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'observatory-v7.blend'
original_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), use_scripts=False)
scene = bpy.context.scene
actor_root = bpy.data.objects['Heroine v4 • native root motion']
portal = bpy.data.objects['V5 | airlock assembly']
keep = {actor_root, portal, *actor_root.children_recursive, *portal.children_recursive}
for ob in list(scene.objects):
    if ob not in keep:
        bpy.data.objects.remove(ob, do_unlink=True)
for m in list(scene.timeline_markers):
    scene.timeline_markers.remove(m)
scene.frame_end = 288
scene.frame_set(1)
forest = bpy.data.collections.new('V8 | Forest discovery study')
scene.collection.children.link(forest)


def empty(name, location=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    forest.objects.link(ob)
    ob.location = location
    return ob


offset = empty('V8 | Preserve native gait, place on forest trail', (0, -9, 0))
actor_root.parent = offset
# The discovery occurs before the door opens in the existing interior sequence.
for ob in portal.children_recursive:
    if ob.name.startswith('V5 | sliding airlock leaf'):
        ob.animation_data_clear()
        side = -1 if ob.name.endswith('-1') else 1
        ob.location.x = side * .8


def material(name, color, rough=.7, metal=0, emission=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    m.diffuse_color = (*color, 1)
    return m


soil = material('V8 | leaf litter earth', (.09, .065, .032))
nodes, links = soil.node_tree.nodes, soil.node_tree.links
p = nodes.get('Principled BSDF')
uv = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeVectorMath')
mapping.operation = 'SCALE'
mapping.inputs[3].default_value = .35
links.new(uv.outputs['Object'], mapping.inputs[0])
ground_folder = ROOT / 'assets/v8/forest/forest_floor'
for suffix, socket in [('diff', 'Base Color'), ('rough', 'Roughness')]:
    path = ground_folder / f'forest_floor_{suffix}_2k.jpg'
    if path.exists():
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(path), check_existing=True)
        if suffix != 'diff': tex.image.colorspace_settings.name = 'Non-Color'
        links.new(mapping.outputs[0], tex.inputs['Vector'])
        if suffix == 'diff':
            tint = nodes.new('ShaderNodeMixRGB'); tint.blend_type = 'MULTIPLY'
            tint.inputs[0].default_value = 1
            tint.inputs[2].default_value = (.45, .50, .42, 1)
            links.new(tex.outputs['Color'], tint.inputs[1]); links.new(tint.outputs[0], p.inputs[socket])
        else: links.new(tex.outputs['Color'], p.inputs[socket])


def height(x, y):
    # A clear flat path preserves the already validated native foot contact.
    side = max(0, min(1, (abs(x + 3.8) - 1.3) / 4))
    return .14 + side * (.24 + .28 * math.sin(x * .61) * math.cos(y * .37))


verts, faces = [], []
N = 96
for j in range(N + 1):
    y = -100 + j * 120 / N
    for i in range(N + 1):
        x = -90 + i * 170 / N
        verts.append((x, y, height(x, y)))
for j in range(N):
    for i in range(N):
        a = j * (N + 1) + i
        faces.append((a, a + 1, a + N + 2, a + N + 1))
mesh = bpy.data.meshes.new('V8 | gently banked trail terrain')
mesh.from_pydata(verts, [], faces)
mesh.update()
ground = bpy.data.objects.new(mesh.name, mesh)
forest.objects.link(ground)
mesh.materials.append(soil)
for poly in mesh.polygons: poly.use_smooth = True

sources = {}
asset_rows = []


def import_gltf(key, path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = set(bpy.data.objects) - before
    coll = bpy.data.collections.new('V8 source | ' + key)
    for ob in objects:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        coll.objects.link(ob)
    # Collection is intentionally unlinked; instances render its source objects.
    deps = bpy.context.evaluated_depsgraph_get()
    points = [ob.matrix_world @ Vector(v) for ob in objects if ob.type == 'MESH' for v in ob.bound_box]
    lo = Vector([min(v[i] for v in points) for i in range(3)])
    hi = Vector([max(v[i] for v in points) for i in range(3)])
    sources[key] = (coll, lo, hi)
    if key == 'moss':
        # The download is a display layout of six stones, not one natural pile.
        # Normalize separate meshes so each placed stone has a controlled footprint.
        for i, ob in enumerate(sorted((o for o in objects if o.type == 'MESH'), key=lambda o: o.name)):
            stone = ob.copy(); stone.data = ob.data.copy()
            stone.matrix_world = ob.matrix_world.copy()
            sub = bpy.data.collections.new('V8 source | individual moss stone ' + str(i)); sub.objects.link(stone)
            points2 = [stone.matrix_world @ Vector(v) for v in stone.bound_box]
            lower = Vector([min(v[j] for v in points2) for j in range(3)])
            upper = Vector([max(v[j] for v in points2) for j in range(3)])
            center = (lower + upper) / 2; center.z = lower.z
            stone.location -= center
            sources['stone' + str(i)] = (sub, lower - center, upper - center)
    asset_rows.append({'asset': key, 'path': str(path.relative_to(ROOT)),
                       'bounds_m': [list(lo), list(hi)],
                       'mesh_vertices': sum(len(o.data.vertices) for o in objects if o.type == 'MESH')})
    if key == 'fern':
        alpha = bpy.data.images.load(str(ROOT / 'assets/v8/forest/fern_02/textures/fern_02_alpha_2k.png'), check_existing=True)
        alpha.colorspace_settings.name = 'Non-Color'
        for ob in objects:
            if ob.type != 'MESH': continue
            for mat in ob.data.materials:
                if not mat or not mat.use_nodes: continue
                principal = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if principal:
                    t = mat.node_tree.nodes.new('ShaderNodeTexImage'); t.image = alpha
                    mat.node_tree.links.new(t.outputs['Color'], principal.inputs['Alpha'])
    return coll


base = ROOT / 'assets/v8/forest'
for key, asset in [('fern', 'fern_02'), ('moss', 'rock_moss_set_01'), ('trunk', 'dead_tree_trunk'), ('roots', 'root_cluster_01')]:
    import_gltf(key, base / asset / f'{asset}_2k.gltf')
import_gltf('cliff', ROOT / 'assets/model/rock_face_01/rock_face_01_2k.gltf')


def instance(key, name, pos, scale=1, yaw=0):
    coll, lo, hi = sources[key]
    ob = empty(name, pos)
    ob.instance_type = 'COLLECTION'
    ob.instance_collection = coll
    ob.scale = (scale,) * 3 if isinstance(scale, (float, int)) else scale
    ob.rotation_euler.z = yaw
    ob.location.z -= lo.z * ob.scale.z
    return ob


rng = random.Random(801)
for i in range(90):
    y = rng.uniform(-29, -5)
    side = -1 if i % 2 else 1
    x = -3.8 + side * rng.uniform(1.75, 9)
    instance('fern', f'V8 | fern bank {i:03d}', (x, y, height(x, y)), rng.uniform(.65, 1.35), rng.uniform(0, math.tau))
for i in range(14):
    x = -3.8 + (-1 if i % 2 else 1) * rng.uniform(2.5, 11)
    y = rng.uniform(-27, -7)
    if -20 < y < -9 and -11 < x < -5.1: x -= 6
    stone_keys = [key for key in sources if key.startswith('stone')]
    instance(stone_keys[i % len(stone_keys)], f'V8 | moss stone {i:02d}', (x, y, height(x, y)), rng.uniform(.6, 1.0), rng.uniform(0, math.tau))
instance('trunk', 'V8 | fallen timber foreground', (-9, -19, .12), 1.1, .5)
instance('roots', 'V8 | exposed roots near the threshold', (-7.5, -8, .13), 1.1, .4)
# Fractured scanned stone forms the cliff around an intentionally clear doorway.
for i, (x, y, z, scale, yaw) in enumerate([
    (-11.92, -4.5, .1, (2.1, 1.5, 2.7), 0),
    (2.88, -4.0, .1, (2.1, 1.7, 3.0), 0),
    (-4.0, -4.2, 4.0, (1.8, 1.6, 1.4), 0),
    (-14.5, -2.5, .1, (2.7, 2.4, 3.4), .1),
    (7.2, -2.0, .1, (2.5, 2.5, 3.3), -.3),
]): instance('cliff', f'V8 | cliff entrance scan {i}', (x, y, z), scale, yaw)

# Baked LOD1 variants preserve needle cards without importing all authoring LODs.
fir_path = base / 'fir_tree_01/fir_tree_01_2k.blend'
if fir_path.exists():
    selected = ['fir_tree_01_b_LOD1', 'fir_tree_01_c_LOD1']
    with bpy.data.libraries.load(str(fir_path), link=False) as (available, imported):
        imported.objects = selected
    for i, ob in enumerate(imported.objects):
        assert ob is not None, selected[i]
        ob.location = (0, 0, 0)
        coll = bpy.data.collections.new('V8 source | fir variant ' + str(i))
        coll.objects.link(ob)
        sources['fir' + str(i)] = (coll, Vector((0, 0, 0)), Vector((0, 0, 15)))
    for i in range(24):
        x = -3.8 + (-1 if i % 2 else 1) * rng.uniform(4, 22)
        y = rng.uniform(-31, 2)
        # Keep the second camera's foreground clear of full trunk occlusion.
        if -20 < y < -7 and -10 < x < -6: x -= 4
        instance('fir' + str(i % 2), f'V8 | linked fir {i:02d}', (x, y, height(x, y)), rng.uniform(.7, 1.05), rng.uniform(0, math.tau))
    for i in range(48):
        x = rng.uniform(-27, 21); y = rng.uniform(-39, -27)
        instance('fir' + str(i % 2), f'V8 | distant forest {i:02d}', (x, y, .14), rng.uniform(.48, 1.05), rng.uniform(0, math.tau))
    asset_rows.append({'asset': 'fir', 'path': str(fir_path.relative_to(ROOT)), 'source_objects': [o.name for o in imported.objects], 'instances': 72})


def camera(name, cut, lens, keys):
    data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.new(name, data); forest.objects.link(ob)
    data.lens = lens; data.clip_end = 250
    ob.rotation_mode = 'QUATERNION'
    previous = None
    for frame, pos, target in keys:
        ob.location = pos
        q = (Vector(target) - ob.location).to_track_quat('-Z', 'Y')
        if previous is not None and previous.dot(q) < 0: q.negate()
        previous = q.copy(); ob.rotation_quaternion = q
        ob.keyframe_insert('location', frame=frame)
        ob.keyframe_insert('rotation_quaternion', frame=frame)
    marker = scene.timeline_markers.new(name, frame=cut); marker.camera = ob
    return ob


camera('V8 | Trail exploration', 1, 32, [
    (1, (-9.0, -15.0, 1.6), (-3.8, -17.0, 1.1)),
    (96, (-9.0, -10.3, 1.8), (-3.8, -13.4, 1.2)),
])
camera('V8 | Clearing discovery', 97, 26, [
    (97, (-7.0, -17.5, 3.0), (-3.3, -7.4, 2.2)),
    (216, (-6.8, -14.8, 2.8), (-3.2, -6.3, 2.2)),
])
camera('V8 | Concealed door', 217, 42, [
    (217, (-5.4, -14.2, 1.85), (-3.8, -5.5, 1.9)),
    (252, (-5.1, -13.7, 1.85), (-3.8, -5.5, 1.9)),
])
camera('V8 | A sound behind her', 253, 65, [
    (253, (-6.0, -7.4, 1.72), (-3.8, -9.8, 1.52)),
    (288, (-5.8, -7.5, 1.72), (-3.8, -9.8, 1.52)),
])

world = bpy.data.worlds.new('V8 | blue hour forest sky'); world.use_nodes = True
scene.world = world
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18, .28, .46, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35

# A small volume softens distant trees without hiding the action or doorway.
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3.8, -27, 6))
mist = bpy.context.object; mist.name = 'V8 | forest air depth study'
mist.scale = (85, 100, 18)
fog = bpy.data.materials.new('V8 | thin blue forest haze'); fog.use_nodes = True
fog.node_tree.nodes.clear()
volume = fog.node_tree.nodes.new('ShaderNodeVolumePrincipled')
volume.inputs['Density'].default_value = .012
volume.inputs['Color'].default_value = (.40, .53, .65, 1)
volume.inputs['Anisotropy'].default_value = .25
output = fog.node_tree.nodes.new('ShaderNodeOutputMaterial')
fog.node_tree.links.new(volume.outputs['Volume'], output.inputs['Volume'])
mist.data.materials.append(fog); mist.display_type = 'WIRE'


def light(name, kind, pos, energy, color, target, size=5):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == 'AREA': d.shape = 'DISK'; d.size = size
    if kind == 'SUN': d.angle = math.radians(8)
    ob = bpy.data.objects.new(name, d); forest.objects.link(ob); ob.location = pos
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()


light('V8 | last light through canopy', 'SUN', (-15, -2, 18), 1.2, (.58, .73, 1), (-3, -14, 0))
light('V8 | open sky bounce', 'AREA', (-4, -15, 9), 1100, (.45, .65, 1), (-3.8, -15, 0), 12)
light('V8 | door spill', 'AREA', (-3.8, -6.3, 2.3), 160, (1, .66, .32), (-3.8, -11, .8), 2)
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 960; scene.render.resolution_y = 540; scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.use_compositing = False
scene.render.use_sequencer = False
scene.render.film_transparent = False
scene.render.use_simplify = True
scene.render.simplify_subdivision = 1
scene.frame_set(160)
scene.camera = bpy.data.objects['V8 | Clearing discovery']
for text in list(bpy.data.texts): bpy.data.texts.remove(text)
bpy.ops.file.make_paths_relative()
destination = ROOT / 'forest-v8-layout.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == original_hash
(OUT / 'forest-layout.json').write_text(json.dumps({
    'status': 'asset and camera staging study, not a finished cinematic',
    'scene': destination.name, 'source_scene_unchanged': True,
    'source_sha256': original_hash, 'fps': 24, 'frames': 288,
    'native_motion': 'Original V7 entrance action, static forest translation only; native scale and timing unchanged',
    'assets': asset_rows, 'heavy_render_started': False,
    'pending_actions': ['Combat selection and retargeting', 'Forest-to-airlock final crossing', 'Forest-specific gaze and reaction', 'Wind and sound'],
}, indent=2) + '\n')
print('V8_FOREST_LAYOUT_READY', destination.name)
