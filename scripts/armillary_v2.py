"""V2 visibly moving, mechanically nested astronomical instrument.
No external dependencies beyond Blender. Geometry uses metres, Z up.
"""
import bpy
import math
import random
from mathutils import Vector
from math import sin, cos, pi


def _material(name, color, metal=0.8, rough=0.3):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m


def _mesh(name, verts, faces, mat, parent, bevel=0, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.parent = parent
    if mat: me.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if bevel:
        b = ob.modifiers.new('Hand softened edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
    return ob


class Batch:
    def __init__(self): self.v, self.f = [], []
    def box(self, center, size, angle=0):
        start = len(self.v)
        for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            x,y,z = x*size[0]/2,y*size[1]/2,z*size[2]/2
            self.v.append((center[0]+x*cos(angle)-y*sin(angle),center[1]+x*sin(angle)+y*cos(angle),center[2]+z))
        self.f.extend(tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def cylinder(self, a, b, radius, segments=12):
        a,b = Vector(a),Vector(b)
        d = (b-a).normalized()
        u = d.cross(Vector((0,0,1)))
        if u.length < .01: u = d.cross(Vector((0,1,0)))
        u.normalize(); w = d.cross(u).normalized(); start=len(self.v)
        for pt in (a,b):
            for i in range(segments):
                t=2*pi*i/segments
                self.v.append(tuple(pt+radius*(u*cos(t)+w*sin(t))))
        self.f.extend([tuple(start+i for i in range(segments-1,-1,-1)),tuple(start+segments+i for i in range(segments))])
        for i in range(segments):
            j=(i+1)%segments
            self.f.append((start+i,start+j,start+segments+j,start+segments+i))
    def sphere(self, center, radius, rings=6, segments=10):
        start=len(self.v)
        for j in range(rings+1):
            ph=pi*j/rings
            for i in range(segments):
                t=2*pi*i/segments
                self.v.append((center[0]+radius*sin(ph)*cos(t),center[1]+radius*sin(ph)*sin(t),center[2]+radius*cos(ph)))
        for j in range(rings):
            for i in range(segments):
                k=j*segments+i; n=j*segments+(i+1)%segments
                self.f.append((start+k,start+n,start+n+segments,start+k+segments))
    def finish(self,name,mat,parent,bevel=0,smooth=False):
        return _mesh(name,self.v,self.f,mat,parent,bevel,smooth)


def _empty(name,parent=None):
    ob=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(ob)
    ob.parent=parent
    return ob


def _annulus(name,radius,width,depth,mat,parent,z=0,segments=192,bevel=.006):
    v=[]; f=[]
    for r,h in [(radius-width/2,z-depth/2),(radius+width/2,z-depth/2),(radius-width/2,z+depth/2),(radius+width/2,z+depth/2)]:
        for i in range(segments):
            a=2*pi*i/segments; v.append((r*cos(a),r*sin(a),h))
    for i in range(segments):
        j=(i+1)%segments
        f.extend([(i,j,segments+j,segments+i),(2*segments+i,3*segments+i,3*segments+j,2*segments+j),(i,2*segments+i,2*segments+j,j),(segments+i,segments+j,3*segments+j,3*segments+i)])
    ob=_mesh(name,v,f,mat,parent,bevel)
    for idx,p in enumerate(ob.data.polygons): p.use_smooth=idx%4 in (2,3)
    return ob


def _text(name,string,location,size,mat,parent,rotation=(0,0,0)):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=string
    cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'
    cu.extrude=.0008; cu.bevel_depth=.0003; cu.bevel_resolution=1
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob)
    ob.parent=parent; ob.location=location; ob.rotation_euler=rotation
    cu.materials.append(mat)
    return ob


def _animate(ob,start,end):
    """Constant mechanical speed, baked every four frames for portability."""
    for frame in sorted(set(list(range(1,577,4))+[576])):
        t=(frame-1)/575
        ob.rotation_euler=tuple(a+(b-a)*t for a,b in zip(start,end))
        ob.keyframe_insert(data_path='rotation_euler',frame=frame)


def build_armillary(center=(0,2,3.7),bronze_mat=None,dark_mat=None,accent_mat=None):
    """Build a ~5m antique armillary; return root, pivots and world focus points.
    bronze_mat is the structural metal; dark_mat recessed bronze; accent_mat
    restrained warm engravings. Nothing emits light. Rings turn continuously
    through 24 seconds on nested, mechanically shared bearing axes.
    """
    bronze=bronze_mat or _material('Armillary | aged gunmetal bronze',(.29,.145,.048),.88,.3)
    dark=dark_mat or _material('Armillary | oxidised recess',(.021,.043,.039),.55,.43)
    gold=accent_mat or _material('Armillary | polished engraving',(.51,.31,.1),.8,.24)
    root=_empty('ARMILLARY | master'); root.location=center
    # Pure water: true transmission and physical refractive index. Droplets
    # are batched into two meshes and partially embedded into the ring faces.
    rain=bpy.data.materials.get('Armillary | condensed rain') or bpy.data.materials.new('Armillary | condensed rain')
    rain.use_nodes=True
    rain_shader=rain.node_tree.nodes.get('Principled BSDF')
    rain_shader.inputs['Base Color'].default_value=(.97,.99,1,1)
    rain_shader.inputs['Metallic'].default_value=0
    rain_shader.inputs['Roughness'].default_value=.055
    rain_shader.inputs['IOR'].default_value=1.333
    rain_shader.inputs['Transmission Weight'].default_value=1
    rain_rng=random.Random(1907)
    pivots=[]
    # Outer vertical meridian yaws on the pedestal's central thrust bearing.
    # Subsequent rings rotate in their parent's local frame about alternating
    # X/Y/X axes. This is a true nested gimbal, not a floating arrangement.
    deg=math.radians
    settings=[(2.42,.185,.15,(pi/2,0,deg(-12)),(pi/2,0,deg(66))),
              (2.155,.145,.105,(deg(25),0,0),(deg(205),0,0)),
              (1.87,.135,.10,(0,deg(-30),0),(0,deg(-240),0)),
              (1.58,.105,.085,(deg(35),0,0),(deg(275),0,0))]
    romans=['XII','I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
    for n,(r,width,depth,start,end) in enumerate(settings):
        pivot=_empty('Ring %d | balanced pivot'%(n+1),root if n==0 else pivots[-1]); pivots.append(pivot)
        _animate(pivot,start,end)
        _annulus('Ring %d | bronze band'%(n+1),r,width,depth,bronze,pivot)
        # Double turned beads frame a dark recessed graduated face.
        _annulus('Ring %d | recessed scale'%(n+1),r,width*.80,.009,dark,pivot,z=depth/2+.001,bevel=.002)
        for edge in (-1,1):
            _annulus('Ring %d | moulded lip %d'%(n+1,edge),r+edge*width*.43,.016,.017,gold,pivot,z=depth/2+.008,bevel=.004)
        marks=Batch(); bolts=Batch(); gear=Batch()
        divisions=180 if n<3 else 120
        for i in range(divisions):
            a=2*pi*i/divisions
            long=i%5==0
            length=width*(.24 if long else .115)
            rr=r+width*.24
            marks.box((rr*cos(a),rr*sin(a),depth/2+.007),(length,.009 if long else .0045,.003),a)
        for i in range(24):
            a=2*pi*i/24; rr=r-width*.30
            bolts.sphere((rr*cos(a),rr*sin(a),depth/2+.010),.009,4,8)
        if n in (0,1):
            for i in range(120):
                a=2*pi*i/120
                gear.box(((r+width*.60)*cos(a),(r+width*.60)*sin(a),-.015),(.05,.027,depth*.68),a)
            gear.finish('Ring %d | cut gear teeth'%(n+1),bronze,pivot,.003)
        marks.finish('Ring %d | engraved divisions'%(n+1),gold,pivot)
        bolts.finish('Ring %d | hammered rivets'%(n+1),bronze,pivot,smooth=True)
        for i,roman in enumerate(romans):
            a=pi/2-i*2*pi/12
            _text('Ring %d | numeral %s'%(n+1,roman),roman,(r*cos(a),r*sin(a),depth/2+.011),width*.30,gold,pivot,(0,0,a-pi/2))
        if n in (0,1):
            beads=Batch()
            for i in range(48 if n==0 else 29):
                # Sparse upper arc, with a handful of larger collected beads.
                a=rain_rng.uniform(.37,2.92)
                rr=r+rain_rng.uniform(-width*.28,width*.30)
                radius=rain_rng.uniform(.0025,.0065)
                if i%13==0:radius=rain_rng.uniform(.009,.012)
                center_drop=Vector((rr*cos(a),rr*sin(a),depth/2+.0068))
                start_vertex=len(beads.v)
                beads.sphere(center_drop,radius,8,12)
                for k in range(start_vertex,len(beads.v)):
                    q=Vector(beads.v[k])-center_drop
                    # Attached beads flatten against metal and elongate
                    # slightly with gravity, rather than floating spheres.
                    q.y*=1.22
                    q.z*=.62
                    beads.v[k]=tuple(center_drop+q)
            beads.finish('Ring %d | fine rain beads'%(n+1),rain,pivot,smooth=True)
        # Each axis has paired turned bearing caps, with inset screws.
        caps=Batch(); screws=Batch()
        for s in (-1,1):
            bx,by=(0,s*r) if n==2 else (s*r,0)
            caps.cylinder((bx,by,-depth*.85),(bx,by,depth*.85),.079,24)
            caps.cylinder((bx,by,depth*.85),(bx,by,depth*1.1),.052,24)
            screws.box((bx,by,depth*1.11),(.059,.009,.003))
        caps.finish('Ring %d | trunnion bearings'%(n+1),bronze,pivot,.004,True)
        screws.finish('Ring %d | screw slots'%(n+1),dark,pivot)

    # The hinge direction is invariant under the inner ring's rotation.
    # Parent each spindle to the outer ring: both ends remain on the two bands
    # exactly, including when their planes coincide. No cross-product normals,
    # quaternion flips, numerical singularities, drivers or handlers are used.
    for pair in range(3):
        outer,inner=pivots[pair],pivots[pair+1]
        ro,ri=settings[pair][0],settings[pair+1][0]
        span=ro-ri
        axis=Vector((0,1,0)) if pair==1 else Vector((1,0,0))
        for sign in (-1,1):
            holder=_empty('Gimbal bridge %d %s | shared hinge'%(pair+1,sign),outer)
            d=axis*sign
            holder.location=d*ri
            holder.rotation_mode='QUATERNION'
            holder.rotation_quaternion=d.to_track_quat('Z','Y')
            shaft=Batch();shaft.cylinder((0,0,-.035),(0,0,span+.035),.031,16)
            for zz in [0,span]:
                shaft.sphere((0,0,zz),.065,8,14)
                shaft.cylinder((0,0,zz-.044),(0,0,zz+.044),.048,20)
            shaft.finish('Gimbal bridge %d | turned spindle'%pair,bronze,holder,.003,True)
    bpy.context.scene.frame_set(1)

    # Central celestial globe with turned meridians, studded constellations,
    # and a real mechanical polar spindle instead of a floating centre.
    globe_root=_empty('Celestial globe | polar axis',pivots[-1])
    globe_root.rotation_euler=(pi/2,0,0)
    globe_spin=_empty('Celestial globe | rotating shell',globe_root)
    _animate(globe_spin,(0,0,deg(-10)),(0,0,deg(170)))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=48,radius=.79)
    globe=bpy.context.object; globe.name='Celestial globe | dark engraved bronze'
    globe.parent=globe_spin; globe.location=(0,0,0); globe.data.materials.append(dark)
    for p in globe.data.polygons:p.use_smooth=True
    lines=Batch()
    def wire(points,radius=.004):
        for a,b in zip(points,points[1:]): lines.cylinder(a,b,radius,6)
    for lat in [-60,-30,0,30,60]:
        ph=math.radians(lat); rr=.798*cos(ph); zz=.798*sin(ph)
        wire([(rr*cos(2*pi*i/120),rr*sin(2*pi*i/120),zz) for i in range(121)],.006 if lat==0 else .003)
    for lon in range(0,180,30):
        a=math.radians(lon)
        wire([(.799*sin(2*pi*i/120)*cos(a),.799*sin(2*pi*i/120)*sin(a),.799*cos(2*pi*i/120)) for i in range(121)],.003)
    lines.finish('Celestial globe | brass meridians',gold,globe_spin,smooth=True)
    # Deterministic ornamental constellation network on the visible hemisphere.
    stars=Batch(); links=Batch()
    constellations=[[(.18,.44),(.34,.30),(.45,.07),(.26,-.06),(.09,-.02)],
                   [(-.17,.51),(-.34,.38),(-.51,.22),(-.41,.03)],
                   [(-.45,-.24),(-.28,-.38),(-.06,-.49),(.13,-.34)]]
    for chain in constellations:
        pts=[]
        for x,z in chain:
            p=(x,-math.sqrt(.805**2-x*x-z*z),z);pts.append(p);stars.sphere(p,.014,6,10)
        for a,b in zip(pts,pts[1:]):
            # Raised engraving follows the sphere, never a chord through it.
            arc=[(Vector(a).lerp(Vector(b),j/10)).normalized()*.808 for j in range(11)]
            for u,v in zip(arc,arc[1:]): links.cylinder(u,v,.0035,6)
    stars.finish('Celestial globe | constellation studs',gold,globe_spin,smooth=True)
    links.finish('Celestial globe | constellation lines',gold,globe_spin,smooth=True)
    spindle=Batch()
    spindle.cylinder((0,0,-1.62),(0,0,1.62),.039,24)
    for z in [-1.42,-.88,.88,1.42]:
        spindle.cylinder((0,0,z-.055),(0,0,z+.055),.075,24)
        spindle.sphere((0,0,z),.078,8,16)
    spindle.finish('Polar spindle | brass collars',bronze,globe_root,.004,True)

    # Wide structural cradle, bearing pedestal and a decorative calibration
    # wheel. Pedestal ends about 0.22m above the default floor for a stone base.
    base=Batch()
    for z,r,h in [(-3.40,.72,.14),(-3.25,.56,.13),(-3.10,.35,.20),(-2.80,.24,.45),(-2.50,.38,.15)]:
        base.cylinder((0,0,z-h/2),(0,0,z+h/2),r,48)
    base.finish('Armillary | fixed cast pedestal',bronze,root,.012,True)
    cradle=_empty('Armillary | yaw bearing cradle',root)
    _animate(cradle,(0,0,deg(-12)),(0,0,deg(66)))
    base=Batch()
    base.cylinder((0,0,-2.59),(0,0,-2.43),.31,48)
    base.cylinder((-.55,0,-2.49),(.55,0,-2.49),.11,24)
    for s in (-1,1):
        base.cylinder((s*.46,0,-2.49),(s*1.53,0,-1.90),.085,20)
        base.sphere((s*1.53,0,-1.90),.15,10,16)
    base.finish('Armillary | rotating cast cradle',bronze,cradle,.012,True)
    # Three reinforcing scroll ribs share one efficient mesh.
    ribs=Batch()
    for angle in [0,2*pi/3,4*pi/3]:
        path=[]
        for i in range(33):
            t=i/32
            r=.25+.40*sin(pi*t)
            path.append((r*cos(angle),r*sin(angle),-3.35+t*.89))
        for a,b in zip(path,path[1:]):ribs.cylinder(a,b,.045,10)
    ribs.finish('Pedestal | curved structural ribs',bronze,root,smooth=True)
    wheel=_empty('Calibration wheel | front',root);wheel.location=(0,-.40,-2.90);wheel.rotation_euler=(pi/2,0,0)
    _annulus('Calibration wheel | rim',.23,.038,.043,bronze,wheel,segments=64,bevel=.008)
    spokes=Batch()
    for i in range(8):
        a=i*2*pi/8;spokes.cylinder((0,0,0),(.22*cos(a),.22*sin(a),0),.014,8)
    spokes.cylinder((0,0,-.055),(0,0,.055),.052,20)
    spokes.finish('Calibration wheel | spokes',gold,wheel,.002,True)
    plaque=Batch();plaque.box((0,-.567,-3.26),(.50,.045,.12))
    plaque.finish('Maker plate | cast brass',dark,root,.007)
    _text('Maker plate | inscription','TEMPUS  •  MDCLXXXIV',(0,-.594,-3.265),.031,gold,root,(pi/2,0,0))
    bpy.context.scene.frame_set(1)
    c=Vector(center)
    return {'root':root,'pivots':pivots,'globe':globe,
            'focus_points':{'center':tuple(c),'globe':tuple(c),'engraving':tuple(c+Vector((0,-.09,2.42))),'pedestal':tuple(c+Vector((0,-.5,-3.05)))},
            'center':tuple(c),'radius':2.58}


if __name__=='__main__':
    build_armillary()
    print('Armillary created:',len(bpy.context.scene.objects),'objects')
