"""Local eight-second native bow/bear rehearsal. No production rendering."""
from pathlib import Path
import sys, math, json
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_option_a_v8 import prepare_forest,add_archer,setup_camera,bake_archer_props
OUT=ROOT/'previews/v8/options/c';OUT.mkdir(parents=True,exist_ok=True)

def add_bear(sc):
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'assets/v8/combat/bear/source/Bear Animated.fbx'),use_anim=True)
    rig=bpy.data.objects['RigRoot'];body=bpy.data.objects['sm_3_0_0'];place=bpy.data.objects['Bear_Animated']
    sc.render.fps=12
    for tr in rig.animation_data.nla_tracks:tr.mute=True
    actions={n:bpy.data.actions[f'RigRoot|{n}|Animation Base Layer'] for n in ['Walk','Attack_StandAngry_01_Low','Hit_Stand_F01']}
    def sample(name,t):
        rig.animation_data.action=actions[name];rig.animation_data.action_slot=actions[name].slots[0]
        sc.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
        return {b.name:b.matrix_basis.copy() for b in rig.pose.bones},rig.location.copy()
    walk0=sample('Walk',1)[1];walk1=sample('Walk',52)[1]
    # Source root travel is part of the foot cycle, transferred to the top parent
    # so repeat boundaries do not snap the animal back to the clip origin.
    parent_rot=place.matrix_world.to_3x3()
    cycle=parent_rot@(walk1-walk0)
    cache={};paths={}
    for f in range(1,97):
        if f<=42:
            elapsed=(f-1)*2.5;loops=int(elapsed//51);t=1+elapsed%51
            pose,loc=sample('Walk',t)
            paths[f]=cycle*loops+parent_rot@(loc-walk0)
        elif f<63:
            pose,loc=sample('Attack_StandAngry_01_Low',1+(f-43)*2.5)
            paths[f]=paths[42].copy()
            if f<48:
                w=(f-42)/6;w=w*w*(3-2*w)
                pose={n:cache[42][n].lerp(m,w) for n,m in pose.items()}
        else:
            pose,loc=sample('Hit_Stand_F01',1+(f-63)*2.5)
            paths[f]=paths[42].copy()
            if f<66:
                w=(f-62)/4;w=w*w*(3-2*w)
                pose={n:cache[62][n].lerp(m,w) for n,m in pose.items()}
        # This older mesh exposes a long, box-shaped mouth at the source's
        # 40-degree jaw opening. Limit only its opening; retain body motion,
        # jaw translation/scale and all other facial channels.
        loc,rot,scale=pose['RigJaw'].decompose();angles=rot.to_euler('XYZ')
        angles.z=min(angles.z,math.radians(12))
        pose['RigJaw']=Matrix.LocRotScale(loc,angles.to_quaternion(),scale)
        cache[f]=pose
    rig.animation_data_clear();rig.location=walk0
    for b in rig.pose.bones:b.rotation_mode='QUATERNION'
    origin=Vector((-3.8,-13.15,.18))
    # Preserve source scale and source bone rotations. Every pose is baked so
    # loading the scene needs no callbacks, executable text, or source actions.
    floors=[]
    for f,pose in cache.items():
        sc.frame_set(f)
        for n,m in pose.items():
            b=rig.pose.bones[n];b.matrix_basis=m
            for channel in ['location','rotation_quaternion','scale']:b.keyframe_insert(channel,frame=f,group=n)
        place.location=origin+paths[f];place.keyframe_insert('location',frame=f)
        bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        low=min((ev.matrix_world@Vector(p)).z for p in ev.bound_box)
        # The central path is at .14m. Preserve the native lift but prevent the
        # source clip's small negative floor excursions passing through it.
        lift=max(0,.145-low)
        if lift:
            place.location.z+=lift;place.keyframe_insert('location',frame=f)
        floors.append(low+lift)
    rig.animation_data.action.name='C | baked native bear encounter'
    place.animation_data.action.name='C | native walk travel'
    for m in body.data.materials:
        if m and m.use_nodes:
            bs=m.node_tree.nodes.get('Principled BSDF')
            if bs:bs.inputs['Roughness'].default_value=.82
    for p in body.data.polygons:p.use_smooth=True
    for im in bpy.data.images:
        if im.packed_file and im.filepath:
            local=ROOT/'assets/v8/combat/bear/textures'/Path(im.filepath).name
            if local.exists():im.filepath=str(local)
    return dict(rig=rig,body=body,place=place,travel=list(paths[42]),floor_range=[min(floors),max(floors)])

def surface_targets(sc,actor,bear):
    sc.frame_set(63);bpy.context.view_layer.update()
    body=bear['body'];rig=bear['rig']
    # Follow the actual deformed triangle hit by the arrow, not an empty point
    # inside the animal. This also keeps the shaft attached during recoil.
    aim=rig.matrix_world@rig.pose.bones['RigSpine2'].head
    aim.x-=.2
    sc.frame_set(60);bpy.context.view_layer.update()
    start=(actor['rig'].matrix_world@actor['rig'].pose.bones['B-handProp.R'].matrix).translation.copy()
    sc.frame_set(63);bpy.context.view_layer.update()
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    verts=[ev.matrix_world@v.co for v in mesh.vertices];triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
    tree=BVHTree.FromPolygons(verts,triangles,all_triangles=True)
    hit,normal,index,distance=tree.ray_cast(start,(aim-start).normalized())
    if hit is None:raise RuntimeError('Arrow did not meet bear surface')
    ids=triangles[index];basis=[verts[i].copy() for i in ids];ev.to_mesh_clear()
    points={}
    for f in range(1,97):
        sc.frame_set(f);bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        tri=[ev.matrix_world@me.vertices[i].co for i in ids]
        points[f]=barycentric_transform(hit,*basis,*tri)
        ev.to_mesh_clear()
    return points,{'triangle':list(ids),'impact_point':list(hit),'arrow_flight_metres':distance}

def main():
    sc=prepare_forest();actor=add_archer(sc);bear=add_bear(sc);setup_camera(sc)
    wide=min(sc.timeline_markers,key=lambda m:m.frame).camera
    wide.location=(-16,-16.9,3.1)
    wide.rotation_euler=(Vector((-3.8,-16.9,1.2))-wide.location).to_track_quat('-Z','Y').to_euler()
    sc.frame_start=1;sc.frame_end=96;sc.render.fps=12
    sc['review_label']='OPTION C — BOW / REALISTIC BEAR — SOURCE ACTOR PROXY'
    for marker in sc.timeline_markers:
        marker.name=marker.name.replace('A |','C |')
        marker.camera.name=marker.camera.name.replace('A |','C |')
    points,impact_report=surface_targets(sc,actor,bear)
    bake_archer_props(sc,actor,lambda f:points[f])
    for a in bpy.data.actions:
        if a.name.startswith(('A |','C |')):
            for fc in a.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
    sc.frame_set(54);bpy.context.view_layer.update()
    for im in bpy.data.images:
        if im.filepath and not im.packed_file:im.filepath=bpy.path.abspath(im.filepath)
    path=ROOT/'option-c-bow-bear.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
    report={'option':'C — Bow versus realistic bear','scene':path.name,'frames':96,'fps':12,'duration':8,
      'actor':'Same licensed feminine bow proxy as A; final Rocketbox heroine retarget pending',
      'bear':'User-provided Bear Animated.fbx; native textured mesh and native animation',
      'timeline':['1–42 two native walk cycles toward archer','43–62 native low threat/attack anticipation','60 bow release','63 arrow contact; native standing hit reaction through96'],
      'transitions':'Five-frame walk/threat blend, three-frame threat/hit blend',
      'source_jaw_correction':'Positive local Z opening capped at12degrees to prevent exaggerated box-shaped mouth deformation',
      'native_walk_world_displacement':bear['travel'],'sampled_bear_floor_range':bear['floor_range'],
      'impact':impact_report,'licensed_source_scene_local_only':True,'heavy_render':False,
      'limitations':['Source mannequin instead of final heroine','Draft low-resolution textured bear, no groomed fur','Original uploader rig/provenance notes in asset README','No production lighting or audio'],
      'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post)}
    (OUT/'scene-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
