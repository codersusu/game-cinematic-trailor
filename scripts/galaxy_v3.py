"""Aster: a deterministic, three-dimensional stellar spiral for Cycles 4.5.
Authored point geometry inspired by the supplied Astra reference, without text.
The module changes no camera, world, compositor or renderer setting.
"""
import bpy
import math
import random
from mathutils import Vector


def _empty(name,parent=None):
    ob=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(ob);ob.parent=parent
    return ob


def _turn(ob,angle_deg):
    for frame in sorted(set(range(1,577,4))|{576}):
        ob.rotation_euler.z=math.radians(angle_deg)*(frame-1)/575
        ob.keyframe_insert('rotation_euler',frame=frame)


def _star_material(name,color,strength):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nt=mat.node_tree;nt.nodes.clear()
    emission=nt.nodes.new('ShaderNodeEmission');emission.name='Stellar radiance'
    emission.inputs['Color'].default_value=(*color,1)
    emission.inputs['Strength'].default_value=strength
    out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(emission.outputs[0],out.inputs['Surface'])
    if hasattr(mat,'cycles') and hasattr(mat.cycles,'emission_sampling'):
        mat.cycles.emission_sampling='NONE'
    return mat


# Normalized icosahedron makes a rounded point silhouette at macro distances.
_PHI=(1+math.sqrt(5))/2
_ICO=[Vector(p).normalized() for p in [(-1,_PHI,0),(1,_PHI,0),(-1,-_PHI,0),(1,-_PHI,0),(0,-1,_PHI),(0,1,_PHI),(0,-1,-_PHI),(0,1,-_PHI),(_PHI,0,-1),(_PHI,0,1),(-_PHI,0,-1),(-_PHI,0,1)]]
_FACES=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]


def build_galaxy(center=(0,2,3.7),radius=1.72,seed=601,brightness=1.0,rotation_degrees=165,
                 tilt_degrees=(78,-12,-15),star_count=4700):
    """Return root/spin/layers/focus_points; all geometry is local to center.
    Radius excludes only tiny star radii. Most stars are sub-centimetre points;
    rare large stars punctuate the spiral, and there is no solid central orb.
    brightness scales emission; compositor glare should be subtle, not broad.
    """
    rng=random.Random(seed)
    root=_empty('GALAXY V3 | master');root.location=center
    tilt=_empty('Galaxy | inclined stellar disk',root)
    tilt.rotation_euler=tuple(math.radians(x) for x in tilt_degrees)
    spin=_empty('Galaxy | main orbital rotation',tilt);_turn(spin,rotation_degrees)
    colors=[(.24,.54,1.0),(.58,.78,1.0),(.94,.97,1.0),(1.0,.55,.22),(1.0,.83,.56)]
    strengths=[.85,5.0,24.0]
    mats=[_star_material('Galaxy | %s %s'%(tier,c),rgb,strength*brightness) for tier,strength in enumerate(strengths) for c,rgb in enumerate(colors)]
    buckets=[[] for _ in range(8)]
    def add(point,size,tier,color):
        r=math.hypot(point[0],point[1]);bucket=min(7,int(r/radius*8))
        buckets[bucket].append((point,size,tier*len(colors)+color))
    # The image's clean winding '6' gesture comes from one dominant spiral.
    # Two close, fine filaments create a star-rich arm without solid ribbons.
    for i in range(star_count):
        t=rng.random()
        arm=0 if i<int(star_count*.84) else 1
        r=.10+(radius-.10)*(t**.84)
        theta=-.3+math.pi*2.95*t+(0 if arm==0 else 1.48)
        # Secondary material fades strongly near the outer part of the disk.
        if arm==1:r*=.82
        width=.008+.024*(r/radius)
        filament=(.012 if i%3 else -.017)*(.4+r/radius)
        rr=r+rng.gauss(0,width)+filament
        theta+=rng.gauss(0,.015)
        z=rng.gauss(0,.016+.018*(1-r/radius))
        p=(rr*math.cos(theta),rr*math.sin(theta),z)
        q=rng.random()
        if q<.026:
            size=rng.uniform(.007,.0135);tier=2
        elif q<.22:
            size=rng.uniform(.0026,.0052);tier=1
        else:
            size=rng.uniform(.0009,.0026);tier=0
        color=rng.choices(range(5),weights=[.24,.31,.30,.09,.06])[0]
        add(p,size,tier,color)
    # Thin outlying stars preserve depth and irregularity without filling the
    # important dark gaps between spiral turns.
    for i in range(260):
        r=radius*(rng.random()**.55);theta=rng.uniform(0,math.tau)
        add((r*math.cos(theta),r*math.sin(theta),rng.gauss(0,.075)),rng.uniform(.0008,.0024),0,rng.randrange(3))
    # Compact resolved stellar nucleus: many small stars, never a solid sphere.
    for i in range(480):
        spread=.035 if i<330 else .095
        p=(rng.gauss(0,spread),rng.gauss(0,spread),rng.gauss(0,spread*.46))
        add(p,rng.uniform(.0011,.0033),1 if i%8 else 2,2 if i%6 else 4)
    for i in range(16):
        p=(rng.gauss(0,.018),rng.gauss(0,.018),rng.gauss(0,.012))
        add(p,rng.uniform(.009,.015),2,2)
    layers=[]
    for index,stars in enumerate(buckets):
        pivot=_empty('Galaxy | differential shell %d'%index,spin)
        _turn(pivot,12-24*(index+.5)/8)
        verts=[];faces=[];material_indices=[]
        for p,size,mi in stars:
            offset=len(verts);v=Vector(p)
            verts.extend(tuple(v+q*size) for q in _ICO)
            faces.extend(tuple(offset+j for j in f) for f in _FACES)
            material_indices.extend([mi]*len(_FACES))
        mesh=bpy.data.meshes.new('Stellar points | shell %d'%index)
        mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('Galaxy | resolved stars %d'%index,mesh);bpy.context.collection.objects.link(obj);obj.parent=pivot
        for mat in mats:mesh.materials.append(mat)
        for poly,mi in zip(mesh.polygons,material_indices):poly.material_index=mi;poly.use_smooth=True
        # Tiny opaque stars need not cast expensive, invisible micro-shadows.
        obj.visible_shadow=False
        layers.append(pivot)
    root['star_count']=sum(len(b) for b in buckets)
    root['main_rotation_degrees']=rotation_degrees
    root['visual_note']='Resolved stellar points; no solid curves, nucleus sphere, volumes or logos.'
    bpy.context.scene.frame_set(1)
    return {'root':root,'spin':spin,'layers':layers,'center':tuple(center),'radius':radius,
            'star_count':root['star_count'],'focus_points':{'center':tuple(center)}}


if __name__=='__main__':
    result=build_galaxy()
    print('GALAXY_READY',result['star_count'])
