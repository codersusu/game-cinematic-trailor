"""Compare two saved V5 builds without rendering or saving them.

Default local comparison:
    blender --background --disable-autoexec --python-exit-code 1 \
        --python scripts/compare_rebuild_v5.py

Explicit scenes (paths resolve from the invoking working directory):
    blender --background --disable-autoexec --python-exit-code 1 \
        --python scripts/compare_rebuild_v5.py -- first.blend second.blend

Optional --output report.json follows the scene paths. The default report is
renders/v5/rebuild-qa.json under this script's project root. With no scene paths,
compare observatory-v5.blend with github-submission/observatory-v5.blend there.
A mismatch writes the report then raises; --python-exit-code 1 makes it fail CI.
"""
from pathlib import Path
import bpy, hashlib, json, sys, argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scene_v5 import animation, coordinates, digest

ROOT=Path(__file__).resolve().parents[1]
PROJECT_PREFIXES=(ROOT/'github-submission',ROOT)
SKIP={'rna_type','name','name_full','users','use_fake_user','tag','is_library_indirect','library','override_library','asset_data','preview','original','id_data','session_uid','filepath','filepath_raw','file_format','name_full','select','location','width','height','dimensions','show_options','show_preview','show_texture','label','hide','color','use_custom_color'}
# UI coordinates are irrelevant for nodes; physical locations/colors are recorded
# explicitly or use the generic capture without the UI exclusions.
BASE_SKIP={'rna_type','name','name_full','users','use_fake_user','tag','is_library_indirect','library','override_library','asset_data','preview','original','id_data','session_uid'}


def normalize(value):
    if isinstance(value,str):
        for prefix in sorted(PROJECT_PREFIXES,key=lambda p:len(str(p)),reverse=True):
            value=value.replace(str(prefix),'<project>')
        return value
    if value is None or isinstance(value,(bool,int,float)):
        return value
    if isinstance(value,bpy.types.ID):
        return {'id':value.name,'type':value.bl_rna.identifier}
    try:return [normalize(v) for v in value]
    except TypeError:return None


def properties(owner, skip=BASE_SKIP):
    result={}
    for prop in owner.bl_rna.properties:
        key=prop.identifier
        if key in skip or prop.is_readonly or prop.type=='COLLECTION':continue
        try:
            value=getattr(owner,key)
            if prop.type=='POINTER':
                if isinstance(value,bpy.types.ID):result[key]=normalize(value)
            else:result[key]=normalize(value)
        except (AttributeError,TypeError,ValueError):pass
    return result


def tree(nt):
    if nt is None:return None
    nodes=[]
    for n in nt.nodes:
        item={'name':n.name,'type':n.bl_idname,'properties':properties(n,SKIP),
              'inputs':[(s.identifier,normalize(s.default_value)) for s in n.inputs if hasattr(s,'default_value')],
              'outputs':[(s.identifier,normalize(s.default_value)) for s in n.outputs if hasattr(s,'default_value')]}
        if hasattr(n,'color_ramp'):
            item['ramp']={'properties':properties(n.color_ramp),'elements':[(e.position,list(e.color)) for e in n.color_ramp.elements]}
        nodes.append(item)
    return {'nodes':nodes,'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links),'animation':animation(nt)}


def geometry(data,kind):
    if kind=='MESH':
        record={'vertices':len(data.vertices),'coordinates':coordinates(data.vertices,'co',3),
                'loops':coordinates(data.loops,'vertex_index',1,'i'),'polygon_sizes':coordinates(data.polygons,'loop_total',1,'i'),
                'polygon_materials':coordinates(data.polygons,'material_index',1,'i'),
                'smooth':[p.use_smooth for p in data.polygons],
                'uvs':[(u.name,coordinates(u.data,'uv',2)) for u in data.uv_layers],
                'edges':[(list(e.vertices),e.use_seam,e.use_edge_sharp) for e in data.edges],
                'materials':[m.name if m else None for m in data.materials]}
        if data.shape_keys:
            record['shapes']={'animation':animation(data.shape_keys),'blocks':[{'name':k.name,'properties':properties(k),'coordinates':coordinates(k.data,'co',3)} for k in data.shape_keys.key_blocks]}
        return record
    record={'properties':properties(data),'animation':animation(data)}
    if kind in ('CURVE','FONT','SURFACE'):
        record['splines']=[{'properties':properties(s),'points':[(list(p.co),p.radius,p.tilt,p.weight) for p in s.points],'bezier':[(list(p.co),list(p.handle_left),list(p.handle_right),p.handle_left_type,p.handle_right_type,p.radius,p.tilt) for p in s.bezier_points]} for s in data.splines]
        record['materials']=[m.name if m else None for m in data.materials]
    if kind=='ARMATURE':
        record['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local],'properties':properties(b)} for b in data.bones]
    if hasattr(data,'node_tree'):record['node_tree']=tree(data.node_tree)
    return record


def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(1)
    objects={}
    for o in sorted(scene.objects,key=lambda o:o.name):
        entry={'type':o.type,'properties':properties(o),'matrix_basis':[list(r) for r in o.matrix_basis],
               'matrix_world':[list(r) for r in o.matrix_world],'animation':animation(o),
               'modifiers':[{'name':m.name,'type':m.type,'properties':properties(m)} for m in o.modifiers],
               'constraints':[{'name':c.name,'type':c.type,'properties':properties(c)} for c in o.constraints],
               'custom':{k:normalize(v) for k,v in o.items()},
               'collections':sorted(c.name for c in o.users_collection)}
        if o.data:entry['data']=geometry(o.data,o.type)
        if o.pose:
            entry['pose']=[{'name':b.name,'matrix_basis':[list(r) for r in b.matrix_basis],'constraints':[{'name':c.name,'type':c.type,'properties':properties(c)} for c in b.constraints]} for b in o.pose.bones]
        objects[o.name]=entry
    mats={m.name:{'properties':properties(m),'nodes':tree(m.node_tree),'animation':animation(m)} for m in bpy.data.materials if m.users}
    images={}
    for im in bpy.data.images:
        if im.source not in ('FILE','TILED'):continue
        content=im.packed_file.data if im.packed_file else Path(bpy.path.abspath(im.filepath)).read_bytes()
        images[im.name]={'content_sha256':hashlib.sha256(content).hexdigest(),'size':list(im.size),'colorspace':im.colorspace_settings.name,'alpha_mode':im.alpha_mode,'source':im.source}
    world={'properties':properties(scene.world),'nodes':tree(scene.world.node_tree),'animation':animation(scene.world)}
    render={'render':properties(scene.render),'image_settings':properties(scene.render.image_settings),'cycles':properties(scene.cycles),
            'view_settings':properties(scene.view_settings),'display_settings':properties(scene.display_settings),
            'frames':[scene.frame_start,scene.frame_end],'camera':scene.camera.name if scene.camera else None,
            'cuts':[(m.frame,m.name,m.camera.name if m.camera else None) for m in scene.timeline_markers],
            'compositor':tree(scene.node_tree)}
    # Normalize tuple/list forms for a stable structured comparison.
    return json.loads(json.dumps({'objects':objects,'materials':mats,'images':images,'world':world,'render':render}))


def differences(a,b,path='',limit=100):
    result=[]
    if a==b:return result
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(a.keys()|b.keys()):
            if k not in a:result.append({'path':path+'/'+k,'difference':'added'})
            elif k not in b:result.append({'path':path+'/'+k,'difference':'missing'})
            else:result.extend(differences(a[k],b[k],path+'/'+k,limit-len(result)))
            if len(result)>=limit:break
    elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        for i,(x,y) in enumerate(zip(a,b)):
            result.extend(differences(x,y,path+'/'+str(i),limit-len(result)))
            if len(result)>=limit:break
    else:result.append({'path':path,'root':a,'portable':b})
    return result[:limit]


def report_path(path):
    try:return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:return path.name


def main():
    global PROJECT_PREFIXES
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first_scene',nargs='?',type=Path,default=ROOT/'observatory-v5.blend')
    parser.add_argument('second_scene',nargs='?',type=Path,default=ROOT/'github-submission/observatory-v5.blend')
    parser.add_argument('--output',type=Path,default=ROOT/'renders/v5/rebuild-qa.json')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    first=args.first_scene.resolve();second=args.second_scene.resolve()
    PROJECT_PREFIXES=(first.parent,second.parent)
    root=capture(first)
    portable=capture(second)
    sections={name:{'root_sha256':digest(root[name]),'portable_sha256':digest(portable[name]),'passed':root[name]==portable[name]} for name in root}
    changed=[name for name in root['objects'].keys()&portable['objects'].keys() if root['objects'][name]!=portable['objects'][name]]
    report={'status':'passed' if root==portable else 'mismatches','root_scene':report_path(first),'portable_scene':report_path(second),
            'scope':'All scene objects: transforms, fcurves, modifiers, constraints, geometry, UVs, morphs, bones, curves, cameras/lights; used material/world/compositor nodes; render/color settings; source image content bytes. Paths normalized; serialized blend metadata ignored.',
            'object_counts':{'root':len(root['objects']),'portable':len(portable['objects'])},'sections':sections,
            'missing_objects':sorted(root['objects'].keys()-portable['objects'].keys()),'added_objects':sorted(portable['objects'].keys()-root['objects'].keys()),
            'changed_objects':sorted(changed),'differences':differences(root,portable),
            'root_object_fingerprints':{n:digest(v) for n,v in root['objects'].items()},'portable_object_fingerprints':{n:digest(v) for n,v in portable['objects'].items()}}
    output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('V5_REBUILD_QA',report['status'],report['object_counts'],{k:v['passed'] for k,v in sections.items()});print(json.dumps(report['differences'][:20]))
    if root!=portable:
        raise RuntimeError(f'Scene rebuild comparison failed; see {report_path(output)}')


if __name__=='__main__':main()
