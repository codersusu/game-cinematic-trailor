"""Append the CC-BY Blender Studio Einar rig and author the keeper performance.
Usage inside Blender: info=add_keeper(location=(-2.8,-.3,.2),rotation_z=0,height=1.8)
Required attribution: Einar Rig (CC-BY) Blender Foundation | studio.blender.org
"""
from pathlib import Path
import math,re
import bpy
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'einar/einar_release_v1.blend'

def _curves(action):
    try:return list(action.fcurves)
    except Exception:
        return [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]

def _pose_values(action):
    result={}
    if not action:return result
    for fc in _curves(action):
        if re.match(r'pose\.bones\["[^"]+"\]\.(location|rotation_euler|rotation_quaternion|scale)$',fc.data_path):
            result[(fc.data_path,fc.array_index)]=fc.evaluate(1)
    return result

def add_keeper(location=(-2.8,-.3,.2),rotation_z=0.0,height=1.8,animate=True,quality=1):
    before=set(bpy.data.objects)
    images_before=set(bpy.data.images)
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
        dst.collections=['CH-einar']
        dst.actions=[n for n in src.actions if n in ['Face_default','Face_eyes_closed','Face_scared','Face_content']]
    col=dst.collections[0];bpy.context.scene.collection.children.link(col)
    objs=set(bpy.data.objects)-before
    # Resolve images against the original archive, including source-relative UDIM paths.
    imported_images=set(bpy.data.images)-images_before
    for image in imported_images:
        if image.filepath.startswith('//textures/'):
            image.filepath=str(SOURCE.parent/image.filepath[2:])
    # Replace absent optional wrench texture references with packed neutral images.
    for image in list(imported_images):
        path=Path(bpy.path.abspath(image.filepath)) if image.filepath else None
        if image.source=='FILE' and path and not path.exists():
            neutral=bpy.data.images.new('Keeper neutral '+image.name,width=4,height=4)
            neutral.generated_color=(.5,.5,1,1) if 'normal' in image.name else (.12,.09,.055,1)
            neutral.pack();image.user_remap(neutral)
    # Source helper drivers reference a source camera and obsolete geometry-node sockets.
    for obj in objs:
        if obj.animation_data:
            for fc in list(obj.animation_data.drivers):
                invalid=False
                try:obj.path_resolve(fc.data_path)
                except (ValueError,KeyError):invalid=True
                if invalid or 'depsgraph.scene.camera' in fc.driver.expression:
                    obj.driver_remove(fc.data_path,fc.array_index)
    # Rebuild the skin surface with its original painted albedo and authored normals.
    # This avoids 3.5-to-4/5 Principled conversion changing the old layered skin shader.
    skin=bpy.data.materials.get('einar.skin')
    if skin and skin.use_nodes:
        nt=skin.node_tree;albedo=nt.nodes.get('Image Texture.005');normal=nt.nodes.get('Reroute')
        surface=nt.nodes.new('ShaderNodeBsdfPrincipled');surface.name='Keeper skin • current Cycles'
        surface.inputs['Roughness'].default_value=.48
        surface.inputs['Subsurface Weight'].default_value=.16
        surface.inputs['Subsurface Scale'].default_value=.004
        surface.inputs['Subsurface Radius'].default_value=(1,.4,.2)
        surface.inputs['IOR'].default_value=1.42
        if albedo:nt.links.new(albedo.outputs['Color'],surface.inputs['Base Color'])
        if normal:nt.links.new(normal.outputs[0],surface.inputs['Normal'])
        nt.links.new(surface.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
    # Current eye surfaces preserve the original Eyes UV and painted albedo.
    # Cornea transmits shadow rays so disabled caustics do not black out the eye.
    import importlib.util
    eye_fix_path=HERE.parents[1]/'scripts'/'fix_eyes.py'
    eye_spec=importlib.util.spec_from_file_location('keeper_eye_repair',eye_fix_path)
    eye_module=importlib.util.module_from_spec(eye_spec);eye_spec.loader.exec_module(eye_module)
    eye_module.repair_eyes()
    root=bpy.data.objects.new('Keeper • placement',None);col.objects.link(root)
    for obj in objs:
        if not obj.parent:
            obj.parent=root
    rig=next(o for o in objs if o.type=='ARMATURE' and o.name.startswith('RIG-einar'))
    rig.animation_data_create();rig.animation_data.action=None
    props=rig.pose.bones['Properties_Character_Einar']
    props['Quality']=quality
    props['Viewport Bump']=1
    props['Distress Stage']=0.0
    props['Satchel']=0
    # Original helper collections contain alternate proxies, controls and blood states.
    # Retain source visibility flags and disable unneeded satchel/tool props explicitly.
    for obj in objs:
        if any(x in obj.name.lower() for x in ['pipe_wrench','blow_dart']):obj.hide_render=True
        if obj.name.startswith('META-'):obj.hide_render=True;obj.hide_set(True)
        if obj.type=='MESH':
            for mod in obj.modifiers:
                if mod.type=='SUBSURF':mod.render_levels=min(mod.render_levels,2)
    # Parent transforms preserve the source 1.8m-scale character and front direction (-Y).
    factor=height/1.8
    root.scale=(factor,)*3;root.rotation_euler.z=rotation_z;root.location=location
    # Set arms to FK with a weighted, relaxed stance.
    switches=rig.pose.bones['Properties']
    switches['ik_left_upperarm']=0.0;switches['ik_right_upperarm']=0.0
    for side,sign in [('L',1),('R',-1)]:
        b=rig.pose.bones.get('FK-UpperArm.'+side)
        if b:
            b.rotation_mode='XYZ';b.rotation_euler=(0,0,math.radians(sign*66))
        b=rig.pose.bones.get('FK-Forearm.'+side)
        if b:
            b.rotation_mode='XYZ';b.rotation_euler=(math.radians(-12),0,0)
    # The facial pose library supplies physically authored eyelid closure, not guessed offsets.
    closed=_pose_values(bpy.data.actions.get('Face_eyes_closed'))
    default=_pose_values(bpy.data.actions.get('Face_default'))
    if animate:
        for (path,index),closed_value in closed.items():
            if 'Blink.' not in path:continue
            arr=rig.path_resolve(path);base=default.get((path,index),float(arr[index]))
            for frame,weight in [(1,0),(145,0),(188,0),(191,1),(194,0),(258,0),(261,1),(264,0),(576,0)]:
                arr[index]=base+(closed_value-base)*weight
                rig.keyframe_insert(data_path=path,index=index,frame=frame,group='Keeper blink')
        head=rig.pose.bones['FK-Head'];head.rotation_mode='XYZ'
        for frame,angles in [(1,(-2,0,-4)),(145,(-2,0,-4)),(180,(-1,0,-2)),(228,(5,0,5)),(288,(7,0,8)),(576,(7,0,8))]:
            head.rotation_euler=tuple(math.radians(a) for a in angles);head.keyframe_insert('rotation_euler',frame=frame,group='Keeper reaction')
        for name in ['ACT-Eyebrow_Inner.L','ACT-Eyebrow_Inner.R']:
            b=rig.pose.bones[name]
            for frame,v in [(1,0),(145,0),(190,0),(238,.002),(288,.0015),(576,.0015)]:
                b.location.y=v;b.keyframe_insert('location',frame=frame,group='Keeper brow')
        chest=rig.pose.bones['FK-Chest'];chest.rotation_mode='XYZ'
        for frame in range(1,578,24):
            chest.rotation_euler.x=math.radians(.3*math.sin(frame/24*math.pi*.45))
            chest.keyframe_insert('rotation_euler',frame=frame,group='Keeper breath')
    bpy.context.view_layer.update()
    face=root.matrix_world@Vector((0,-.12,1.665))
    print('KEEPER_ADDED',len(objs),'objects; face target',tuple(face))
    return {'root':root,'rig':rig,'collection':col,'face_target':tuple(face),'source':str(SOURCE)}
