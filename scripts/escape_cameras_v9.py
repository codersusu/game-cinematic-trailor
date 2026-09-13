"""Two baked review cameras for the same V9 bow/bear escape performance.

API
---
add_escape_cameras(scene, actor_rig, actor_body, path_rows) returns:
    {'third': camera_object, 'first': camera_object,
     'first_person_arms': mesh_object}

Call AFTER baking the actor's complete 144-frame / 12-fps action. path_rows may
be a list of dictionaries or a frame-keyed dictionary. Each row supplies frame,
position=(x,y,z), yaw (radians; native forward is -Y), and phase, one of shoot,
sheathe, roll, run. `pos`, `root_position` and `actor_position` are accepted
position aliases. Paths are samples, never written back to the actor.

The first-person mesh has independent geometry and retains the actor's existing
armature modifier/parent, vertex weights and arm animations. The helper never
changes the original mesh, actor action, materials or original visibility.
The arms duplicate defaults hidden for rendering. The caller must render:
  third: original body visible, first_person_arms hidden;
  first: original body hidden, first_person_arms visible.
Keep the same props, bear and environment in both renders. The cropped duplicate
is only a viewing aid; no source or licensed asset is modified on disk.

No rendering, constraints, handlers or continuous camera shake are created.
"""
import math,json
import bpy,bmesh
from mathutils import Vector,Quaternion


def _smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/max(1e-8,b-a)))
    return t*t*(3.-2.*t)


def _heading(yaw):
    return Vector((math.sin(yaw),-math.cos(yaw),0.))


def _angle(direction):
    return math.atan2(direction.x,-direction.y)


def _mix_heading(a,b,weight):
    return _heading(a+((b-a+math.pi)%(2*math.pi)-math.pi)*weight)


def _rows(rows):
    values=[]
    iterable=rows.items() if isinstance(rows,dict) else [(None,row) for row in rows]
    for key,row in iterable:
        row=dict(row)
        if key is not None:row.setdefault('frame',int(key))
        position=next((row[name] for name in ['position','pos','root_position','actor_position'] if name in row),None)
        if position is None:raise ValueError('Each path row needs position=(x,y,z)')
        values.append({'frame':int(row['frame']),'position':Vector(position),'yaw':float(row['yaw']),'phase':row['phase']})
    values.sort(key=lambda row:row['frame'])
    if not values:raise ValueError('The baked actor path must not be empty')
    if len({r['frame'] for r in values})!=len(values):raise ValueError('Duplicate path frames')
    if any(row['phase'] not in ['shoot','sheathe','roll','run'] for row in values):raise ValueError('Unrecognized escape phase')
    return values


def _smooth_vectors(values,radius=2):
    """Centered triangular filtering: stable camera, no long pursuit lag."""
    output=[]
    for index in range(len(values)):
        result=Vector();weight_sum=0
        for offset in range(-radius,radius+1):
            j=max(0,min(len(values)-1,index+offset));weight=radius+1-abs(offset)
            result+=values[j]*weight;weight_sum+=weight
        output.append(result/weight_sum)
    return output


def _arms_duplicate(scene,rig,body):
    original_data=body.data
    vertex_count=len(original_data.vertices);polygon_count=len(original_data.polygons)
    duplicate=body.copy();duplicate.data=original_data.copy()
    duplicate.name='V9 | First-person arms only';duplicate.data.name='V9 | Independent first-person arm geometry'
    # Copying the object retains its complete parent inverse and native armature
    # modifier, so evaluated arm motion exactly follows the third-person body.
    scene.collection.objects.link(duplicate)
    allowed_names={bone.name for bone in rig.data.bones if any(token in bone.name.lower() for token in ['upperarm','forearm','hand','finger','thumb','pinky']) and bone.name.startswith('B-')}
    groups={group.index for group in duplicate.vertex_groups if group.name in allowed_names}
    if not groups:raise ValueError('No deform arm/hand groups found on actor_body')
    keep={vertex.index for vertex in duplicate.data.vertices if sum(group.weight for group in vertex.groups if group.group in groups)>.12}
    mesh=bmesh.new();mesh.from_mesh(duplicate.data);mesh.verts.ensure_lookup_table()
    bmesh.ops.delete(mesh,geom=[vertex for vertex in mesh.verts if vertex.index not in keep],context='VERTS')
    mesh.to_mesh(duplicate.data);mesh.free()
    duplicate.hide_render=True
    duplicate['view_usage']='Visible only for first-person review; original body hidden in that render'
    duplicate['source_object']=body.name
    duplicate['source_vertex_count']=vertex_count
    duplicate['independent_mesh_copy']=True
    assert body.data==original_data and len(body.data.vertices)==vertex_count and len(body.data.polygons)==polygon_count
    assert duplicate.data!=body.data
    return duplicate


def add_escape_cameras(scene,actor_rig,actor_body,path_rows):
    rows=_rows(path_rows);saved_frame=scene.frame_current
    saved_camera=scene.camera;saved_body_data=actor_body.data
    saved_action=actor_rig.animation_data.action if actor_rig.animation_data else None
    old_visibility=actor_body.hide_render
    if bpy.data.objects.get('V9 | Third-person escape') or bpy.data.objects.get('V9 | First-person escape'):
        raise ValueError('V9 escape cameras already exist; call once on a clean build')
    head=actor_rig.pose.bones.get('B-head') or actor_rig.pose.bones.get('Head')
    if head is None:raise ValueError('The evaluated actor head bone is required for first-person eye height')
    roll=[row['frame'] for row in rows if row['phase']=='roll']
    run=[row['frame'] for row in rows if row['phase']=='run']
    roll_start,roll_end=(min(roll),max(roll)) if roll else (rows[-1]['frame']+1,rows[-1]['frame']+2)
    run_start=min(run) if run else rows[-1]['frame']+1
    bear=Vector((-3.8,-17.,1.3));door=Vector((-3.8,-5.8,1.55))
    eyes=[];third_positions=[];third_targets=[];first_targets=[];banks=[]
    for row in rows:
        frame=row['frame'];scene.frame_set(frame);bpy.context.view_layer.update()
        evaluated=actor_rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        bone=evaluated.pose.bones[head.name]
        # The head deformation bone starts near the neck and points through the
        # cranium. Interpolation toward its tail puts the lens near eye height.
        head_eye=evaluated.matrix_world@bone.head.lerp(bone.tail,.60)
        root=row['position'];forward=_heading(row['yaw']);threat=bear-root;threat.z=0
        if threat.length<.01:threat=forward.copy()
        threat.normalize();threat_yaw=_angle(threat)
        escape_weight=_smooth(run_start,run_start+10,frame)
        follow=_mix_heading(threat_yaw,row['yaw'],escape_weight)
        right=follow.cross(Vector((0,0,1))).normalized()
        separation=(Vector((bear.x,bear.y,root.z))-root).length
        distance=4.6+min(1.3,separation*.15)*(1-escape_weight)
        # During pursuit, move out beside the chase line so the bear cannot
        # fill the center foreground and hide the runner or airlock threshold.
        shoulder_offset=1.05+(3.20-1.05)*escape_weight
        camera_height=2.20+(2.50-2.20)*escape_weight
        desired=root-follow*distance+right*shoulder_offset+Vector((0,0,camera_height))
        combat_target=(root+Vector((0,0,1.25))).lerp(bear,.35)
        running_target=root+forward*2.+Vector((0,0,1.30))
        third_positions.append(desired);third_targets.append(combat_target.lerp(running_target,escape_weight))
        eye=head_eye+forward*.10
        if row['phase']=='roll':
            # Keep the head's trajectory but reduce the full-body tumble to a
            # readable crouched dip; the horizon is banked separately below.
            nominal=root.z+1.55;eye.z=nominal*.48+head_eye.z*.52
            eye.z=max(root.z+.74,eye.z)
        eye.z=max(root.z+.60,eye.z)
        eyes.append(eye)
        if row['phase'] in ['shoot','sheathe']:
            target=bear.copy();bank=0.
        elif row['phase']=='roll':
            turn=_smooth(roll_start,roll_start+6,frame)
            look=_mix_heading(threat_yaw,row['yaw'],turn)
            target=eye+look*6.+Vector((0,0,-.55))
            progress=(frame-roll_start)/max(1,roll_end-roll_start)
            bank=math.radians(55)*math.sin(math.pi*progress)**2
        else:
            look=forward.copy();target=eye+look*7.+Vector((0,0,-.12));bank=0.
            # Near the airlock, aim through its middle instead of up at a lintel.
            doorway_delta=Vector((door.x,door.y,root.z))-root
            if doorway_delta.length<4. and doorway_delta.dot(forward)>0:
                target=target.lerp(door,1.-_smooth(.4,4.,doorway_delta.length))
        first_targets.append(target);banks.append(bank)
    third_positions=_smooth_vectors(third_positions,2)
    third_targets=_smooth_vectors(third_targets,3)
    eyes=_smooth_vectors(eyes,1);first_targets=_smooth_vectors(first_targets,2)
    def camera(name,lens):
        data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
        data.lens=lens;data.sensor_width=36;data.clip_start=.025;data.clip_end=250;data.dof.use_dof=False
        ob.rotation_mode='QUATERNION';return ob
    third=camera('V9 | Third-person escape',28)
    first=camera('V9 | First-person escape',19)
    previous={}
    for index,row in enumerate(rows):
        frame=row['frame']
        for ob,position,target,bank in [(third,third_positions[index],third_targets[index],0.),(first,eyes[index],first_targets[index],banks[index])]:
            direction=target-position
            if direction.length<1e-5:direction=_heading(row['yaw'])
            rotation=direction.to_track_quat('-Z','Y')@Quaternion((0,0,1),bank)
            if ob.name in previous and previous[ob.name].dot(rotation)<0:rotation.negate()
            previous[ob.name]=rotation.copy();ob.location=position;ob.rotation_quaternion=rotation
            ob.keyframe_insert('location',frame=frame);ob.keyframe_insert('rotation_quaternion',frame=frame)
    for ob in [third,first]:
        for curve in ob.animation_data.action.fcurves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
        ob['baked_same_performance']=True;ob['sampled_frames']=len(rows)
    first['maximum_roll_bank_degrees']=55.
    first['stabilization']='Evaluated head eye position; centered smoothing; reduced tumble dip; no head geometry in first-person render'
    third['staging']='Over-shoulder combat follow; pursuit shifts 3.2 m sideways and rises to 2.5 m above path, keeping runner and doorway visible beside bear'
    third['combat_lateral_offset_m']=1.05;third['run_lateral_offset_m']=3.20;third['run_camera_height_m']=2.50
    arms=_arms_duplicate(scene,actor_rig,actor_body)
    scene.frame_set(saved_frame);scene.camera=saved_camera
    assert actor_body.data==saved_body_data and actor_body.hide_render==old_visibility
    assert (actor_rig.animation_data.action if actor_rig.animation_data else None)==saved_action
    scene['v9_camera_review']=json.dumps({'frames':len(rows),'roll_frames':[roll_start,roll_end],'run_start':run_start,'first_lens_mm':19,'third_lens_mm':28,'maximum_roll_bank_degrees':55,'arms_vertices':len(arms.data.vertices),'original_body_mesh_unchanged':True,'actor_action_unchanged':True,'render_visibility_switch_required':True})
    return {'third':third,'first':first,'first_person_arms':arms}
