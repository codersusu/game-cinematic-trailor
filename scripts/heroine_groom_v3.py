"""Conservative hair shading refinement for the original Meshy heroine.
No procedural hairstyle or geometry changes. Call on master objects immediately
following import, before alignment/weight transfer. Rest-position masks deform
with the character rather than sliding through its animated head.
"""
import bpy
import numpy as np
MASK='heroine_hair_rest_region'


def _mix_scalar(nodes,links,name,mask,old_socket,target):
    original=old_socket.links[0].from_socket if old_socket.is_linked else None
    value=old_socket.default_value
    mix=nodes.new('ShaderNodeMixRGB');mix.name=name;mix.blend_type='MIX'
    links.new(mask,mix.inputs[0])
    if original:links.new(original,mix.inputs[1])
    else:mix.inputs[1].default_value=(value,value,value,1)
    mix.inputs[2].default_value=(target,target,target,1)
    links.new(mix.outputs[0],old_socket)
    return mix


def soften_heroine_hair(master_objects,roughness=.64,specular_level=.24):
    """Apply only to high/rear-head dark albedo; return simple audit metadata.
    Upper cap begins at88% authored body height. Front face/brows below this
    remain excluded. Rear braid mask uses positiveY (author facing−Y).
    Both gates are baked pervertex in authored rest coordinates. Albedo,
    normals, skin and outfit maps are otherwise left connected; hair alone
    becomes dielectric.
    """
    objects=list(master_objects) if not isinstance(master_objects,bpy.types.Object) else [master_objects]
    meshes=[o for o in objects if o.type=='MESH']
    if not meshes:return {'objects':0,'materials':0,'masked_vertices':0}
    bounds=[tuple(v) for o in meshes for v in o.bound_box]
    lo=min(v[2] for v in bounds);hi=max(v[2] for v in bounds);height=max(hi-lo,1e-6)
    materials=set();masked=0
    for obj in meshes:
        mesh=obj.data
        coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape((-1,3))
        normalized=(coords[:,2]-lo)/height
        top=np.clip((normalized-.88)/.045,0,1)
        rear=np.clip((normalized-.80)/.065,0,1)*np.clip((coords[:,1]/height-.009)/.023,0,1)
        region=np.maximum(top,rear).astype(np.float32)
        attr=mesh.attributes.get(MASK) or mesh.attributes.new(MASK,'FLOAT','POINT')
        attr.data.foreach_set('value',region);masked+=int(np.count_nonzero(region>.5))
        for mat in mesh.materials:
            if mat and mat.use_nodes:materials.add(mat)
    processed=0
    for mat in materials:
        nt=mat.node_tree;n=nt.nodes;l=nt.links
        if n.get('Hair refinement | authored region'):continue
        p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
        if not p:continue
        region=n.new('ShaderNodeAttribute');region.name='Hair refinement | authored region';region.attribute_name=MASK
        lum=n.new('ShaderNodeRGBToBW');lum.name='Hair refinement | albedo darkness'
        if p.inputs['Base Color'].is_linked:l.new(p.inputs['Base Color'].links[0].from_socket,lum.inputs['Color'])
        else:lum.inputs['Color'].default_value=p.inputs['Base Color'].default_value
        dark=n.new('ShaderNodeMapRange');dark.name='Hair refinement | dark albedo gate';dark.clamp=True
        dark.inputs['From Min'].default_value=.025;dark.inputs['From Max'].default_value=.18
        dark.inputs['To Min'].default_value=1;dark.inputs['To Max'].default_value=0
        l.new(lum.outputs[0],dark.inputs['Value'])
        mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';mask.name='Hair refinement | conservative combined mask'
        l.new(region.outputs['Fac'],mask.inputs[0]);l.new(dark.outputs['Result'],mask.inputs[1])
        _mix_scalar(n,l,'Hair refinement | softer broad highlight',mask.outputs[0],p.inputs['Roughness'],roughness)
        _mix_scalar(n,l,'Hair refinement | dielectric hair',mask.outputs[0],p.inputs['Metallic'],0.0)
        spec=p.inputs.get('Specular IOR Level')
        if spec:_mix_scalar(n,l,'Hair refinement | reduced plastic sheen',mask.outputs[0],spec,specular_level)
        mat['hair_refinement']='Authored rest-position upper/rear head × dark albedo; roughness/specular and dielectric hair only'
        processed+=1
    return {'objects':len(meshes),'materials':processed,'masked_vertices':masked,'attribute':MASK,'roughness_target':roughness,'specular_target':specular_level}


refine_hair_material=soften_heroine_hair
