"""Blender Studio Rain walking keeper, compatible with Blender 4.5.
CC-BY 4.0 character: Blender Foundation | studio.blender.org.
No bundled Python scripts are executed. Animation authored for this film.
"""
import bpy, math
from pathlib import Path
from mathutils import Vector, Matrix
BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE/'assets/character/young_keeper/rain/Rain v3.3/rain_v3.2.blend'

def add_young_keeper(start=(-3.8,-7.6,.14), end=(-3.8,-.8,.14), start_frame=1, end_frame=240, height=1.68, cycle_frames=28):
    before=set(bpy.data.objects); old_images=set(bpy.data.images)
    with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
        dst.collections=['CH-rain']
    collection=dst.collections[0]; bpy.context.scene.collection.children.link(collection)
    objects=set(bpy.data.objects)-before
    rig=next(o for o in objects if o.type=='ARMATURE' and o.name.startswith('RIG-rain'))
    for im in set(bpy.data.images)-old_images:
        if im.filepath.startswith('//'):
            im.filepath=str(SOURCE.parent/im.filepath[2:])
    for o in objects:
        if o.animation_data and o.animation_data.action: o.animation_data.action=None
        if o.name.startswith('WGT-'): o.hide_render=True
    root=bpy.data.objects.new('Young Keeper • travel',None); collection.objects.link(root)
    for o in objects:
        if o.parent is None: o.parent=root
    # Source shoe sole and head are measured directly from authored mesh vertices.
    shoes=next(o for o in objects if o.name.startswith('GEO-rain-shoes'))
    head=next(o for o in objects if o.name.startswith('GEO-rain-head'))
    low=min((shoes.matrix_world@v.co).z for v in shoes.data.vertices)
    high=max((head.matrix_world@v.co).z for v in head.data.vertices)
    factor=height/(high-low); root.scale=(factor,)*3
    direction=Vector(end)-Vector(start); direction.z=0; direction.normalize()
    root.rotation_euler.z=math.atan2(direction.x,-direction.y)
    start,end=Vector(start),Vector(end)
    start.z-=low*factor; end.z-=low*factor
    bones=rig.pose.bones
    props=bones['Properties_IKFK']
    for side in ('left','right'):
        props['ik_arm_'+side]=0
        props['ik_leg_'+side]=1
    props['ik_stretch_legs']=0;props['ik_pole_follow_feet']=1
    cp=bones['Properties_Character_Rain'];cp['Eye_Dots']=False;cp['Dummy_Eyes']=False;cp['Quality']=1
    # Physical corneal reflection/refraction while allowing illumination of iris.
    mat=bpy.data.materials.get('MAT-rain.cornea')
    if mat and mat.use_nodes:
        nt=mat.node_tree; output=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        if output and output.inputs['Surface'].is_linked:
            original=output.inputs['Surface'].links[0].from_socket
            lp=nt.nodes.new('ShaderNodeLightPath'); trans=nt.nodes.new('ShaderNodeBsdfTransparent'); mix=nt.nodes.new('ShaderNodeMixShader')
            mix.label='Transparent shadow rays preserve iris illumination'
            nt.links.new(lp.outputs['Is Shadow Ray'],mix.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(trans.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface'])
    # Regrade original albedo/vertex-color signals; retain all authored bump/roughness.
    palette={'top':(.045,.057,.085),'jeans':(.045,.035,.025),'scarf':(.28,.17,.065),'shoes':(.055,.028,.012),'laces':(.07,.055,.035),'socks':(.035,.027,.02)}
    for suffix,color in palette.items():
        mat=bpy.data.materials.get('MAT-rain.'+suffix)
        if not mat or not mat.use_nodes: continue
        nt=mat.node_tree
        for shader in [n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']:
            socket=shader.inputs['Base Color']
            if socket.is_linked:
                original=socket.links[0].from_socket
                bw=nt.nodes.new('ShaderNodeRGBToBW');ramp=nt.nodes.new('ShaderNodeValToRGB')
                ramp.label='Observatory explorer costume grade'
                ramp.color_ramp.elements[0].color=tuple(c*.35 for c in color)+(1,)
                ramp.color_ramp.elements[1].color=tuple(color)+(1,)
                nt.links.new(original,bw.inputs[0]);nt.links.new(bw.outputs[0],ramp.inputs[0]);nt.links.new(ramp.outputs[0],socket)
            else: socket.default_value=tuple(color)+(1,)
    bpy.context.view_layer.update()
    rest={n:bones[n].matrix.copy() for n in ['MSTR-Foot.L','MSTR-Foot.R','MSTR-Hips','MSTR-Chest']}
    half=cycle_frames//2; stance=cycle_frames*.60
    speed=(end-start)/(end_frame-start_frame)
    contact_frames=list(range(start_frame+half,end_frame+1,half))
    # One final trailing-foot placement completes the halt; no impact at initial support.
    settle_frame=end_frame+12; contact_frames.append(settle_frame)
    contacts=[{'frame':f,'time_seconds':(f-1)/24,'foot':('right' if ((f-start_frame)//half)%2 else 'left')} for f in contact_frames[:-1]]
    contacts.append({'frame':settle_frame,'time_seconds':(settle_frame-1)/24,'foot':'left'})
    def path(f): return start+(end-start)*max(0,min(1,(f-start_frame)/(end_frame-start_frame)))
    def plant(f,side):
        # Stance is fixed in world space. Lead decreases as the walk reaches its stop.
        lead=max(0,min(stance/2,(end_frame-f)*.65))
        p=(start+speed*(f-start_frame) if f<start_frame else path(f))+speed*lead
        lateral=Vector((-direction.y,direction.x,0))*(rest['MSTR-Foot.'+side].translation.x*factor)
        p+=lateral; p.z+=rest['MSTR-Foot.'+side].translation.z*factor
        return p
    def pose_position(name,position,frame):
        bone=bones[name];m=rest[name].copy();m.translation=position;bone.matrix=m
        bone.keyframe_insert(data_path='location',frame=frame)
        bone.keyframe_insert(data_path='rotation_euler',frame=frame)
    for f in range(start_frame,289):
        bpy.context.scene.frame_set(f)
        root.location=path(f);root.keyframe_insert(data_path='location',frame=f)
        bpy.context.view_layer.update()
        inv=rig.matrix_world.inverted()
        amplitude=max(0,min(1,(end_frame+10-f)/22))
        phase=2*math.pi*(f-start_frame)/cycle_frames
        for side,offset in [('L',0),('R',half)]:
            last=start_frame+offset+math.floor((f-start_frame-offset)/cycle_frames)*cycle_frames
            u=f-last
            p0=plant(last,side);p1=plant(last+cycle_frames,side)
            if u<=stance: pos=p0
            else:
                q=(u-stance)/(cycle_frames-stance); blend=q*q*(3-2*q)
                pos=p0.lerp(p1,blend);pos.z+=.075*math.sin(math.pi*q)
            # Smooth trailing foot closure after final step.
            if side=='L' and f>=end_frame-3:
                q=max(0,min(1,(f-(end_frame-3))/(settle_frame-(end_frame-3))))
                pos=plant(225,side).lerp(plant(end_frame,side),q*q*(3-2*q));pos.z+=.055*math.sin(math.pi*q)
            if f>=settle_frame: pos=plant(end_frame,side)
            pose_position('MSTR-Foot.'+side,inv@pos,f)
        # Weight shifts are on body controls; the root and planted feet stay level.
        for name,mult in [('MSTR-Hips',1),('MSTR-Chest',.6)]:
            p=rest[name].translation.copy();p.x+=.012*math.sin(phase)*amplitude*mult
            p.z+=(-.038-.014*math.cos(2*phase))*amplitude
            pose_position(name,p,f)
        for side,sign in [('L',1),('R',-1)]:
            b=bones['FK-Upperarm.'+side];b.rotation_mode='XYZ'
            b.rotation_euler=(math.radians(18)*math.cos(phase)*sign*amplitude,0,math.radians(-77)*sign)
            b.keyframe_insert(data_path='rotation_euler',frame=f)
            b=bones['FK-Forearm.'+side];b.rotation_euler=(0,0,math.radians(12)*sign);b.keyframe_insert(data_path='rotation_euler',frame=f)
        b=bones['FK-Head'];b.rotation_euler=(math.radians(-3)-math.radians(3)*max(0,min(1,(f-225)/50)),math.radians(.6)*math.sin(phase)*amplitude,math.radians(-28)*max(0,min(1,(f-225)/50)))
        b.keyframe_insert(data_path='rotation_euler',frame=f)
        for name in ['FK-Hair_Ponytail1','FK-Hair_Ponytail2','FK-Hair_Ponytail3','FK-Scarf1']:
            if name in bones:
                b=bones[name];b.rotation_euler.x=math.radians({'FK-Hair_Ponytail1':-30,'FK-Hair_Ponytail2':-28,'FK-Hair_Ponytail3':-12}.get(name,0))+math.radians(2.2)*math.sin(phase-.6)*amplitude;b.keyframe_insert(data_path='rotation_euler',frame=f)
    for obj in [root,rig]:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
    bpy.context.scene.frame_set(start_frame);bpy.context.view_layer.update()
    face_target=bpy.data.objects.new('Young Keeper • face target',None);collection.objects.link(face_target)
    face_target.parent=rig;face_target.parent_type='BONE';face_target.parent_bone='FK-Head';face_target.location=(0,-.12,-.07)
    feet_targets={s:tuple(plant(start_frame,s)) for s in ('L','R')}
    return {'root':root,'rig':rig,'collection':collection,'face_target':tuple(rig.matrix_world@Vector((0,-.08,1.48))), 'face_object':face_target,'feet_targets':feet_targets,'foot_contacts':contacts,'doorway_crossing_frame':start_frame+(-5.8-start.y)/(end.y-start.y)*(end_frame-start_frame),'source':str(SOURCE),'height':height}
