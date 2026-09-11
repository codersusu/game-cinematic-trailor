"""Original realistic heroine: Meshy rig/import, detail transfer, grounded film walk.
No downloaded Python is executed. Compatible with Blender4.5.
Manifest is assets/character/heroine_v3/manifest.json. Paths can be overridden.
"""
import bpy, math, json, re
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
BASE=Path(__file__).resolve().parents[1]
ASSETS=BASE/'assets/character/heroine_v3'

def _path(value):
    p=Path(value);return p if p.is_absolute() else BASE/p

def _import(path):
    path=_path(path);before=set(bpy.data.objects)
    if path.suffix.lower()=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path),use_anim=True)
    elif path.suffix.lower() in ('.glb','.gltf'):bpy.ops.import_scene.gltf(filepath=str(path))
    elif path.suffix.lower()=='.blend':
        with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
        for o in dst.objects:
            if o:bpy.context.scene.collection.objects.link(o)
    else:raise ValueError('Expected FBX, GLB, GLTF or BLEND: '+str(path))
    imported=set(bpy.data.objects)-before
    widgets={b.custom_shape for obj in imported if obj.type=='ARMATURE' for b in obj.pose.bones if b.custom_shape}
    for obj in widgets:obj.hide_render=True;obj.hide_set(True)
    return imported-widgets

def _norm(name):
    return re.sub('[^a-z0-9]','',name.lower().split(':')[-1]).replace('mixamorig','')

def _bone(rig,*names):
    lookup={_norm(b.name):b for b in rig.pose.bones}
    for n in names:
        if _norm(n) in lookup:return lookup[_norm(n)]
    raise KeyError('Missing bone '+str(names)+'; available: '+','.join(lookup))

def _geometry_bounds(objects):
    points=[o.matrix_world@Vector(v) for o in objects if o.type=='MESH' for v in o.bound_box]
    if not points:raise ValueError('Asset has no mesh')
    return Vector(tuple(min(v[k] for v in points) for k in range(3))),Vector(tuple(max(v[k] for v in points) for k in range(3)))

def _transfer_detail(master_objects,proxy_objects,rig):
    """Bind high-detail master using Blender nearest polygon interpolation.
    Requires same authored rest pose and coordinate system; fails on misalignment.
    """
    proxies=[o for o in proxy_objects if o.type=='MESH' and len(o.vertex_groups)]
    if not proxies:raise ValueError('Rig proxy has no skin weights')
    lo,hi=_geometry_bounds(proxies);ml,mh=_geometry_bounds(master_objects)
    scale=(hi.z-lo.z)/(mh.z-ml.z)
    proxy_forward=sum((rig.matrix_world.to_3x3()@(_bone(rig,side+'ToeBase',side+'Toe').bone.head_local-_bone(rig,side+'Foot').bone.head_local) for side in ('Left','Right')),Vector());proxy_forward.z=0;proxy_forward.normalize()
    angle=math.atan2(proxy_forward.y,proxy_forward.x)-math.atan2(-1,0)
    transform=Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)
    for obj in master_objects:obj.matrix_world=transform@obj.matrix_world
    ml,mh=_geometry_bounds(master_objects)
    shift=Vector(((lo.x+hi.x-ml.x-mh.x)/2,(lo.y+hi.y-ml.y-mh.y)/2,lo.z-ml.z))
    for obj in master_objects:obj.matrix_world=Matrix.Translation(shift)@obj.matrix_world
    bpy.context.view_layer.update();ml,mh=_geometry_bounds(master_objects)
    relative_error=((mh-ml)-(hi-lo)).length/max((hi-lo).length,1e-6)
    report={'uniform_scale':scale,'rotation_z':angle,'translation':list(shift),'relative_bounds_error':relative_error,'master_dimensions':list(mh-ml),'proxy_dimensions':list(hi-lo)}
    (ASSETS/'alignment-report.json').write_text(json.dumps(report,indent=2))
    if relative_error>.15:
        raise ValueError('Master/proxy pose differs after uniform alignment; see alignment-report.json')
    for obj in [o for o in master_objects if o.type=='MESH']:
        proxy=max(proxies,key=lambda p:len(p.data.vertices))
        for vg in proxy.vertex_groups:
            if vg.name not in obj.vertex_groups:obj.vertex_groups.new(name=vg.name)
        mod=obj.modifiers.new('Interpolated proxy skin weights','DATA_TRANSFER');mod.object=proxy
        mod.use_vert_data=True;mod.data_types_verts={'VGROUP_WEIGHTS'};mod.vert_mapping='POLYINTERP_NEAREST';mod.use_object_transform=True
        mod.layers_vgroup_select_src='ALL';mod.layers_vgroup_select_dst='NAME';mod.mix_mode='REPLACE'
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name);obj.select_set(False)
        arm=obj.modifiers.new('High detail deformation','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    for o in proxies:o.hide_render=True;o.hide_set(True)

def _key(bone,frame):
    bone.rotation_mode='QUATERNION'
    for field in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=field,frame=frame)

def _aim_matrix(rest_matrix,head,tail):
    old=rest_matrix.to_3x3().col[1].normalized();new=(tail-head).normalized()
    rotation=old.rotation_difference(new).to_matrix()@rest_matrix.to_3x3()
    m=rotation.to_4x4();m.translation=head;return m

def add_heroine(model_path=None,animation_path=None,detail_mesh_path=None,
                start=(-3.8,-7.6,.14),end=(-3.8,-.8,.14),start_frame=1,end_frame=240,
                height=1.72,cycle_frames=28,source_cycle=None,forward_axis=None):
    manifest=json.loads((ASSETS/'manifest.json').read_text()) if (ASSETS/'manifest.json').exists() else {}
    model_path=model_path or manifest.get('model_path')
    animation_path=animation_path or manifest.get('animation_path')
    detail_mesh_path=detail_mesh_path or manifest.get('detail_mesh_path')
    source_cycle=source_cycle or manifest.get('source_cycle')
    forward_axis=forward_axis or manifest.get('forward_axis')
    if not model_path:raise FileNotFoundError('Realistic heroine is not acquired; set model_path in '+str(ASSETS/'manifest.json'))
    objects=_import(model_path)
    rigs=[o for o in objects if o.type=='ARMATURE']
    if not rigs:raise ValueError('Heroine model is not rigged')
    rig=max(rigs,key=lambda o:len(o.data.bones))
    hips=_bone(rig,'Hips','pelvis');head=_bone(rig,'Head')
    legs={s:(_bone(rig,s+'UpLeg',s+'Thigh'),_bone(rig,s+'Leg',s+'Calf'),_bone(rig,s+'Foot'),_bone(rig,s+'ToeBase',s+'Toe')) for s in ('Left','Right')}
    # Preserve original animation on a hidden source rig before baking the target.
    if animation_path:
        animobjects=_import(animation_path);animrig=max((o for o in animobjects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
    else:
        animrig=rig.copy();animrig.data=rig.data.copy();bpy.context.scene.collection.objects.link(animrig);animobjects={animrig}
    source_action=animrig.animation_data.action if animrig.animation_data else None
    if not source_action and animrig.animation_data:
        strips=[strip for track in animrig.animation_data.nla_tracks for strip in track.strips if strip.action]
        if strips:
            source_action=strips[0].action;animrig.animation_data.action=source_action
            for track in animrig.animation_data.nla_tracks:track.mute=True
    if not source_action:raise ValueError('The supplied rig has no walking action; provide animation_path')
    source_lookup={_norm(b.name):b for b in animrig.pose.bones}
    if source_action:
        source_cycle=source_cycle or list(source_action.frame_range)
    for o in objects:
        if o.animation_data:o.animation_data_clear()
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    if detail_mesh_path:
        master=_import(detail_mesh_path)
        from heroine_groom_v3 import soften_heroine_hair
        soften_heroine_hair(master)
        _transfer_detail(master,objects,rig);objects|=master
    lo,hi=_geometry_bounds(objects);factor=height/(hi.z-lo.z)
    rig.data.pose_position='POSE'
    for b in rig.pose.bones:b.rotation_mode='QUATERNION'
    disabled_modifiers=[]
    for obj in objects:
        if obj.type=='MESH':
            for modifier in obj.modifiers:
                if modifier.type in ('ARMATURE','SUBSURF','MULTIRES'):
                    disabled_modifiers.append((modifier,modifier.show_viewport));modifier.show_viewport=False
    bpy.context.view_layer.update()
    # Infer author-facing direction from ankle-to-toe skeleton vectors.
    forward=Vector(forward_axis) if forward_axis else sum((rig.matrix_world.to_3x3()@(leg[3].bone.head_local-leg[2].bone.head_local) for leg in legs.values()),Vector())
    forward.z=0
    if forward.length<1e-5:forward=Vector((0,-1,0))
    forward.normalize();travel=Vector(end)-Vector(start);travel.z=0;travel.normalize()
    angle=math.atan2(travel.y,travel.x)-math.atan2(forward.y,forward.x)
    root=bpy.data.objects.new('Heroine v3 • travel',None);bpy.context.scene.collection.objects.link(root)
    for o in objects:
        if o.parent not in objects:
            world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
    root.scale=(factor,)*3;root.rotation_euler.z=angle
    origin=Vector((0,0,lo.z));rot=Matrix.Rotation(angle,3,'Z')
    rest={b.name:b.bone.matrix_local.copy() for b in rig.pose.bones}
    # Capture source body motion before target baking; no runtime handlers or scripts.
    samples=[]
    if source_action:
        a,z=source_cycle
        for i in range(cycle_frames):
            source_frame=a+(z-a)*i/cycle_frames
            action_start,action_end=source_action.frame_range
            source_frame=action_start+(source_frame-action_start)%(action_end-action_start)
            bpy.context.scene.frame_set(int(source_frame),subframe=source_frame%1)
            samples.append({name:b.matrix_basis.copy() for name,b in source_lookup.items()})
    # Average the walk's body pose into a relaxed arms-down stance, never A-pose.
    neutral={}
    for name in samples[0]:
        matrices=[sample[name] for sample in samples]
        trans=sum((matrix.translation for matrix in matrices),Vector())/len(matrices)
        rotation=matrices[0].to_quaternion()
        for i,matrix in enumerate(matrices[1:],2):rotation=rotation.slerp(matrix.to_quaternion(),1/i)
        neutral[name]=Matrix.LocRotScale(trans,rotation,Vector((1,1,1)))
    for o in animobjects:o.hide_render=True;o.hide_set(True)
    start,end=Vector(start),Vector(end);speed=(end-start)/(end_frame-start_frame)
    half=cycle_frames//2;stance=cycle_frames*.60;settle_frame=end_frame+12
    # Source ankle offsets are measured in world rest space prior to path motion.
    ankles={s:rig.matrix_world@leg[2].bone.head_local for s,leg in legs.items()}
    # Remove root's new scale/rotation from stored rest position by using authored matrices.
    root.scale=(1,1,1);root.rotation_euler.z=0;bpy.context.view_layer.update()
    ankles={s:rig.matrix_world@leg[2].bone.head_local for s,leg in legs.items()}
    root.scale=(factor,)*3;root.rotation_euler.z=angle
    bpy.context.view_layer.update()
    vector_inverse=rig.matrix_world.to_3x3().inverted()
    lateral=Vector((-travel.y,travel.x,0))
    def path(f):return start+(end-start)*max(0,min(1,(f-start_frame)/(end_frame-start_frame)))
    def plant(f,side):
        base=(start+speed*(f-start_frame) if f<start_frame else path(f))
        lead=max(0,min(stance/2,(end_frame-f)*.65))
        offset=ankles[side]-origin;offset-=forward*offset.dot(forward)
        return base+speed*lead+rot@offset*factor
    for f in range(start_frame,577):
        bpy.context.scene.frame_set(f)
        root.location=path(f)-rot@origin*factor;root.keyframe_insert(data_path='location',frame=f)
        phase=2*math.pi*(f-start_frame)/cycle_frames;fade=max(0,min(1,(end_frame+10-f)/22))
        for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
        if samples:
            sample=samples[(f-start_frame)%cycle_frames]
            for b in rig.pose.bones:
                key=_norm(b.name)
                if key in sample:
                    matrix=sample[key].copy()
                    if b==hips:
                        matrix.translation=Vector((0,0,0))
                    if f>end_frame:
                        trans,quat,scale=matrix.decompose();ntrans,nquat,nscale=neutral[key].decompose();quat=nquat.slerp(quat,fade);matrix=Matrix.LocRotScale(ntrans.lerp(trans,fade),quat,Vector((1,1,1)))
                    b.matrix_basis=matrix
        # Small weight shift/depression keeps realistic knee flexion at double support.
        hp=rest[hips.name].copy()
        hp.translation+=vector_inverse@(lateral*(.009*math.sin(phase)*fade)+Vector((0,0,(-.040-.013*math.cos(2*phase))*fade)))
        hips.matrix=hp;bpy.context.view_layer.update()
        inv=rig.matrix_world.inverted();local_forward=(rig.matrix_world.to_3x3().inverted()@travel).normalized()
        for side,offset in [('Left',0),('Right',half)]:
            last=start_frame+offset+math.floor((f-start_frame-offset)/cycle_frames)*cycle_frames;u=f-last
            p0,p1=plant(last,side),plant(last+cycle_frames,side)
            if u<=stance:pos=p0
            else:
                t=(u-stance)/(cycle_frames-stance);pos=p0.lerp(p1,t*t*(3-2*t));pos.z+=.068*math.sin(math.pi*t)
            if side=='Left' and f>=end_frame-3:
                t=max(0,min(1,(f-end_frame+3)/15));pos=plant(225,side).lerp(plant(end_frame,side),t*t*(3-2*t));pos.z+=.05*math.sin(math.pi*t)
            if f>=settle_frame:pos=plant(end_frame,side)
            thigh,shin,foot,toe=legs[side];h=thigh.head.copy();a=inv@pos
            axis=a-h;distance=axis.length;axis.normalize();l1=(shin.bone.head_local-thigh.bone.head_local).length;l2=(foot.bone.head_local-shin.bone.head_local).length
            distance=min(distance,(l1+l2)*.9999);along=(l1*l1-l2*l2+distance*distance)/(2*max(distance,1e-5))
            bend=local_forward-axis*local_forward.dot(axis);bend.normalize()
            knee=h+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
            thigh.matrix=_aim_matrix(rest[thigh.name],h,knee);bpy.context.view_layer.update()
            shin.matrix=_aim_matrix(rest[shin.name],knee,a);bpy.context.view_layer.update()
            fm=rest[foot.name].copy();fm.translation=a;foot.matrix=fm
            toe.matrix_basis=Matrix.Identity(4)
        # Instrument gaze after approach; retain authored facial shape and textures.
        gaze=max(0,min(1,(f-225)/50));head.rotation_mode='QUATERNION'
        head.rotation_quaternion=head.rotation_quaternion@Quaternion((0,1,0),math.radians(-25)*gaze)
        for b in rig.pose.bones:_key(b,f)
    for modifier,visible in disabled_modifiers:modifier.show_viewport=visible
    for o in animobjects:bpy.data.objects.remove(o,do_unlink=True)
    for obj in [root,rig]:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
    bpy.context.scene.frame_set(start_frame);bpy.context.view_layer.update()
    face=rig.matrix_world@head.head
    contacts=[{'frame':f,'time_seconds':(f-1)/24,'foot':'right' if ((f-start_frame)//half)%2 else 'left'} for f in range(start_frame+half,end_frame+1,half)]
    contacts.append({'frame':settle_frame,'time_seconds':(settle_frame-1)/24,'foot':'left'})
    return {'root':root,'rig':rig,'face_target':tuple(face),'feet_targets':{s:tuple(plant(start_frame,s)) for s in legs},'foot_contacts':contacts,'source':str(model_path),'objects':objects}
