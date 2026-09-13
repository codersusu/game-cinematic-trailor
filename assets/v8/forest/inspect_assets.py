"""Read forest mesh/texture structure in background Blender, without rendering."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
report = {'rendered': False, 'assets': {}}
for asset in ['fern_02', 'rock_moss_set_01', 'dead_tree_trunk', 'root_cluster_01']:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / asset / (asset + '_2k.gltf')))
    objects = set(bpy.data.objects) - before
    entries = []
    for o in sorted(objects, key=lambda o: o.name):
        if o.type != 'MESH':
            continue
        o.data.calc_loop_triangles()
        entries.append(dict(name=o.name, vertices=len(o.data.vertices),
                            triangles=len(o.data.loop_triangles), dimensions=list(o.dimensions),
                            materials=[m.name for m in o.data.materials if m]))
    report['assets'][asset] = entries
    for o in objects:
        bpy.data.objects.remove(o, do_unlink=True)

path = ROOT / 'fir_tree_01/fir_tree_01_2k.blend'
with bpy.data.libraries.load(str(path), link=False) as (src, dst):
    report['fir_available_collections'] = list(src.collections)
    report['fir_available_objects'] = list(src.objects)
    dst.collections = list(src.collections)

for coll in dst.collections:
    if coll:
        bpy.context.scene.collection.children.link(coll)
report['fir_collections'] = {
    c.name: {'objects': [o.name for o in c.objects], 'children': [cc.name for cc in c.children],
             'hide_render': c.hide_render, 'hide_viewport': c.hide_viewport}
    for c in dst.collections if c
}
entries = []
for o in bpy.data.objects:
    data = dict(name=o.name, type=o.type, location=list(o.location), scale=list(o.scale),
                parent=o.parent.name if o.parent else None,
                instance_collection=o.instance_collection.name if o.instance_collection else None,
                hide_render=o.hide_render, hide_viewport=o.hide_viewport,
                collections=[c.name for c in o.users_collection])
    if o.type == 'MESH':
        data['vertices'] = len(o.data.vertices)
        data['polygons'] = len(o.data.polygons)
        data['dimensions'] = list(o.dimensions)
    data['modifiers'] = []
    for m in o.modifiers:
        md = dict(name=m.name, type=m.type, show_render=m.show_render, show_viewport=m.show_viewport)
        if m.type == 'NODES':
            md['node_group'] = m.node_group.name if m.node_group else None
            md['inputs'] = {k: str(m[k]) for k in m.keys()}
            if m.node_group:
                md['interface'] = [dict(name=s.name, identifier=s.identifier, socket_type=getattr(s,'socket_type',None),
                                       default=str(getattr(s,'default_value',None)))
                                   for s in m.node_group.interface.items_tree]
        data['modifiers'].append(md)
    entries.append(data)
report['assets']['fir_tree_01'] = entries
report['images'] = []
for i in bpy.data.images:
    if i.source != 'FILE':
        continue
    path = Path(bpy.path.abspath(i.filepath)).resolve()
    report['images'].append(dict(name=i.name, path=str(path.relative_to(ROOT)),
                                 exists=path.exists(), dimensions=list(i.size)))
(ROOT / 'asset-inspection.json').write_text(json.dumps(report, indent=2) + '\n')
print('FOREST_INSPECTION_COMPLETE', len(entries))
