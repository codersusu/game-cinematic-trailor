"""Inspect the user supplied bear rig without rendering or changing the asset."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'assets/v8/combat/bear'
OUT = ROOT / 'renders/v8/combat/bear-inspection.json'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 24
bpy.ops.import_scene.fbx(filepath=str(ASSET / 'source/Bear Animated.fbx'), use_anim=True)
scene = bpy.context.scene

def bounds(ob, evaluated=False):
    if evaluated:
        ob = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    points = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return {'min': [min(p[a] for p in points) for a in range(3)],
            'max': [max(p[a] for p in points) for a in range(3)]}

objects=[]
for o in bpy.data.objects:
    entry={'name':o.name,'type':o.type,'location':list(o.location),'rotation_euler':list(o.rotation_euler),
           'scale':list(o.scale),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None,
           'modifiers':[{'name':m.name,'type':m.type,'object':m.object.name if m.type=='ARMATURE' and m.object else None} for m in o.modifiers]}
    if o.type=='MESH':
        o.data.calc_loop_triangles()
        sums=[sum(g.weight for g in v.groups) for v in o.data.vertices]
        entry.update(vertices=len(o.data.vertices),triangles=len(o.data.loop_triangles),bounds=bounds(o),
                     materials=[m.name if m else None for m in o.data.materials],
                     unweighted_vertices=sum(w<1e-8 for w in sums),weight_sum_range=[min(sums),max(sums)])
    elif o.type=='ARMATURE':
        entry['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),
                         'tail':list(b.tail_local),'length':b.length} for b in o.data.bones]
    objects.append(entry)
actions=[{'name':a.name,'frame_range':list(a.frame_range),'fcurves':len(a.fcurves),'groups':len(a.groups)} for a in bpy.data.actions]
images=[{'name':i.name,'source_basename':Path(i.filepath).name,'packed':bool(i.packed_file),'size':list(i.size),
         'local_texture':'assets/v8/combat/bear/textures/'+Path(i.filepath).name,
         'local_texture_exists':(ASSET/'textures'/Path(i.filepath).name).exists()} for i in bpy.data.images]
materials=[]
for m in bpy.data.materials:
    materials.append({'name':m.name,'diffuse_color':list(m.diffuse_color),'nodes':[
        {'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.use_nodes else []})
sampled={}
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
for action in bpy.data.actions:
    if any(key in action.name.lower() for key in ['attack_run_01_attackf','attack_standangry_01_low','hit_stand_f01','|run|','|walk|','trans_stand_to_run']):
        rig.animation_data_create()
        for track in rig.animation_data.nla_tracks:
            track.mute=True
        rig.animation_data.action=action
        if action.slots:
            rig.animation_data.action_slot=action.slots[0]
        rows=[]
        start,end=action.frame_range
        for i in range(5):
            frame=start+(end-start)*i/4
            scene.frame_set(int(frame),subframe=frame-int(frame))
            rows.append({'frame':frame,'meshes':{o.name:bounds(o,True) for o in bpy.data.objects if o.type=='MESH'},
                         'rig_location':list(rig.location),'root_pose_heads':{b.name:list(rig.matrix_world@b.head) for b in rig.pose.bones if b.parent is None},
                         'selected_bones':{b.name:list(rig.matrix_world@b.head) for b in rig.pose.bones if b.name in ['RigHead','RigLFLegDigit11','RigRFLegDigit11','RigLBLegDigit11','RigRBLegDigit11']}})
        sampled[action.name]=rows
sample_metrics={}
for name,rows in sampled.items():
    samples=[r['meshes']['sm_3_0_0'] for r in rows]
    sample_metrics[name]={'minimum_sampled_floor_z':min(b['min'][2] for b in samples),
                          'maximum_sampled_height':max(b['max'][2]-b['min'][2] for b in samples),
                          'world_pelvis_travel':(Vector(rows[-1]['root_pose_heads']['RigPelvis'])-Vector(rows[0]['root_pose_heads']['RigPelvis'])).length,
                          'all_bounds_finite':all(math.isfinite(v) for b in samples for ext in b.values() for v in ext)}
report={'status':'CPU inspection complete; no rendered visual QA','scene_fps':scene.render.fps,'scene_fps_base':scene.render.fps_base,
        'objects':objects,'actions':actions,'images':images,'materials':materials,'sampled_actions':sampled,'sample_metrics':sample_metrics,
        'integration':{'container':'Bear_Animated','armature':'RigRoot','mesh':'sm_3_0_0','forward_world_axis':'-Y',
                       'root_motion_channel':'RigRoot object local location Z, transformed into world -Y by parent',
                       'action_binding':'Assign action and its first action_slot explicitly; mute NLA tracks.',
                       'texture_binding':'All five images are packed; rewrite their paths to local_texture for portable saving.',
                       'normalization':'Keep source hierarchy; place/scale/rotate its top Bear_Animated empty.'},
        'limitations':['Five poses per selected action, not a full deformation or collision audit.',
                       'Native root-motion clips require staging or removal of object translation to avoid double movement.',
                       'Sampled floor penetration reaches about 8cm in the run transition; correct character elevation before preview.',
                       'Creator warns this older release has known rigging problems; sampled bounds are finite but visual QA remains required.']}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+'\n')
print('BEAR_INSPECTION',len(objects),'objects',len(actions),'actions',len(images),'images',scene.render.fps)
for o in objects:print(o['name'],o['type'],o.get('dimensions'),len(o.get('bones',[])))
for a in actions:print(a['name'],a['frame_range'])
