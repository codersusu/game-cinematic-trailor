"""Small masonry debris dressing, kept outside the instrument and portrait."""
import bpy,random,math

def add_ruin_details(stone_mat=None):
    rng=random.Random(731)
    if stone_mat is None:
        stone_mat=bpy.data.materials.get('Limestone • scanned weathering')
    root=bpy.data.objects.new('Ruin dressing | fallen masonry',None)
    bpy.context.collection.objects.link(root)
    # Deliberate clusters under rear/side piers, no south camera corridor.
    centers=[(6.8,4.6),(-6.7,4.9),(3.2,8.8),(-3.6,8.6),(7.3,1.2)]
    chunks=[]
    for i in range(15):
        cx,cy=centers[i//3]
        sx=rng.uniform(.30,.80);sy=rng.uniform(.25,.55);sz=rng.uniform(.19,.46)
        verts=[]
        for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            verts.append((x*sx/2+rng.uniform(-.055,.055),y*sy/2+rng.uniform(-.035,.035),z*sz/2+rng.uniform(-.025,.025)))
        # Three faces triangulated with inset chipped vertices; angular
        # silhouette remains architectural rather than rounded fieldstone.
        faces=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6),(4,6,7)]
        me=bpy.data.meshes.new('Fractured limestone block');me.from_pydata(verts,[],faces);me.update()
        ob=bpy.data.objects.new('Fallen voussoir %02d'%i,me);bpy.context.collection.objects.link(ob);ob.parent=root
        ob.location=(cx+rng.uniform(-.65,.65),cy+rng.uniform(-.65,.65),.145+sz/2)
        ob.rotation_euler=(rng.uniform(-.10,.10),rng.uniform(-.10,.10),rng.uniform(0,math.tau))
        if stone_mat:me.materials.append(stone_mat)
        bevel=ob.modifiers.new('Weathered fracture edges','BEVEL');bevel.width=.012;bevel.segments=2
        chunks.append(ob)
    return {'root':root,'chunks':chunks}
