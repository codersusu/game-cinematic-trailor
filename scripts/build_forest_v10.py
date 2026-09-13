"""Dress the accepted V9 motion with a dense, reusable-asset forest."""
from pathlib import Path
import bpy,math,random,json,hashlib,sys
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'previews/v10';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from forest_grass_material_v10 import fix_grass_materials
from forest_lod_v10 import optimize_forest_lods
from forest_leafy_material_v10 import fix_leafy_materials
RNG=random.Random(10107)

def distance(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/max(1e-9,v.length_squared)));return (p-(a+v*t)).length

def main():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'bear-bow-escape-v9.blend'),use_scripts=False);sc=bpy.context.scene
 def motion_hash():
  names=['Rig','RigRoot','Human_Bow','Human_Arrow','A | archer placement','Bear_Animated','V9 | Third-person escape','V9 | First-person escape']
  data=[]
  for name in names:
   o=bpy.data.objects[name];a=o.animation_data.action if o.animation_data else None
   data.append([name,[(fc.data_path,fc.array_index,[(list(k.co),k.interpolation) for k in fc.keyframe_points]) for fc in a.fcurves] if a else None])
  return hashlib.sha256(json.dumps(data).encode()).hexdigest()
 before=motion_hash();people=[];bears=[];eyes=[];rays=[]
 for f in range(1,145,3):
  sc.frame_set(f);bpy.context.view_layer.update();human=bpy.data.objects['Rig'];bear=bpy.data.objects['RigRoot']
  hp=human.matrix_world@human.pose.bones['B-hips'].head;bp=bear.matrix_world@bear.pose.bones['RigSpine2'].head
  people.append(Vector((hp.x,hp.y)));bears.append(Vector((bp.x,bp.y)))
  for name in ['V9 | Third-person escape','V9 | First-person escape']:
   cam=bpy.data.objects[name];cp=Vector((cam.location.x,cam.location.y));eyes.append(cp)
   rays.extend([(cp,Vector((hp.x,hp.y))),(cp,Vector((bp.x,bp.y)))])
 sc.frame_set(1)
 def path_clear(x,y,kind='tree'):
  p=Vector((x,y));dh=min((p-q).length for q in people);db=min((p-q).length for q in bears);dc=min((p-q).length for q in eyes)
  if kind=='tree':
   return dh>2.0 and db>2.5 and dc>1.6 and min(distance(p,a,b) for a,b in rays)>1.0
  if kind=='sapling':return dh>1.35 and db>1.9 and dc>1.15 and min(distance(p,a,b) for a,b in rays)>.65
  if kind=='fern':return dh>.75 and db>1.15 and dc>.55
  return dh>.34 and db>.65
 def h(x,y):
  edge=max(max(-12-x,x-1,0),max(-29-y,y-0,0));w=min(1,edge/18)
  return .14+w*(.45+1.15*math.sin(x*.051)*math.cos(y*.046)+.4*math.sin(y*.12))
 # Keep every existing performance and gate object; replace only background dressing.
 for ob in sc.objects:
  if ob.instance_type=='COLLECTION' and ob.name.startswith('V8 |') and 'cliff entrance' not in ob.name:ob.hide_render=True
  if ob.name=='V8 | gently banked trail terrain':ob.hide_render=True
 col=bpy.data.collections.new('V10 | Dense forest environment');sc.collection.children.link(col)
 counts={}
 def instance(c,name,x,y,scale=1,yaw=0,z=None,wind=0):
  o=bpy.data.objects.new(name,None);col.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=c;o.location=(x,y,h(x,y) if z is None else z);o.scale=(scale,)*3 if isinstance(scale,(float,int)) else scale;o.rotation_euler.z=yaw
  if wind:
   phase=RNG.uniform(0,math.tau)
   for f in [1,25,49,73,97,121,145]:
    o.rotation_euler.x=math.radians(wind)*math.sin(f*.04+phase);o.rotation_euler.y=math.radians(wind*.6)*math.sin(f*.037+phase+1);o.keyframe_insert('rotation_euler',frame=f)
  counts[name.split(' | ')[1]]=counts.get(name.split(' | ')[1],0)+1
  return o
 def standalone(src,name):
  c=bpy.data.collections.new(name);ob=src.copy();ob.data=src.data;ob.animation_data_clear();ob.parent=None;ob.location=(0,0,0);ob.rotation_euler=(0,0,0);ob.scale=(1,1,1);c.objects.link(ob)
  lo=min(v.co.z for v in ob.data.vertices);ob.location.z=-lo
  return c
 # Extend ground beyond all camera horizons, retaining the validated flat clearing.
 verts=[];faces=[];steps=130
 for j in range(steps+1):
  y=-160+j*280/steps
  for i in range(steps+1):
   x=-160+i*300/steps;verts.append((x,y,h(x,y)))
 for j in range(steps):
  for i in range(steps):a=j*(steps+1)+i;faces.append((a,a+1,a+steps+2,a+steps+1))
 mesh=bpy.data.meshes.new('V10 | Continuous forest terrain');mesh.from_pydata(verts,[],faces);mesh.update();ground=bpy.data.objects.new(mesh.name,mesh);col.objects.link(ground)
 soil=bpy.data.materials['V8 | leaf litter earth'].copy();soil.name='V10 | damp forest floor';mesh.materials.append(soil)
 nodes=soil.node_tree.nodes;links=soil.node_tree.links;bs=nodes.get('Principled BSDF');mapping=next(n for n in nodes if n.type=='VECT_MATH')
 norm=nodes.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(ROOT/'assets/v8/forest/forest_floor/forest_floor_nor_gl_2k.jpg'),check_existing=True);norm.image.colorspace_settings.name='Non-Color';links.new(mapping.outputs[0],norm.inputs['Vector']);nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;links.new(norm.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 for poly in mesh.polygons:poly.use_smooth=True
 # Full-sized canopy: near mature firs, overlapping midground, and distant ranks.
 firfile=ROOT/'assets/v8/forest/fir_tree_01/fir_tree_01_2k.blend'
 with bpy.data.libraries.load(str(firfile),link=False) as (src,dst):dst.objects=['fir_tree_01_a_LOD2','fir_tree_01_c_LOD2']
 far=[standalone(o,'V10 source | far fir '+str(i)) for i,o in enumerate(dst.objects)]
 near=[bpy.data.collections['V8 source | fir variant 0'],bpy.data.collections['V8 source | fir variant 1']]
 centers=[]
 for layer,target,bounds,spacing in [('Near canopy',100,(-32,24,-49,14),2.7),('Wooded background',170,(-74,66,-92,59),4.3),('Far treeline',95,(-120,113,-135,94),6.8)]:
  made=0
  for trial in range(target*100):
   if made>=target:break
   x=RNG.uniform(bounds[0],bounds[1]);y=RNG.uniform(bounds[2],bounds[3])
   if layer!='Near canopy' and -30<x<23 and -48<y<13:continue
   if -9.0<x<2 and -6<y<3:continue
   if not path_clear(x,y) or any((x-a)**2+(y-b)**2<spacing**2 for a,b in centers):continue
   c=RNG.choice(near if layer=='Near canopy' else far);size=RNG.uniform(.75,1.3) if layer=='Near canopy' else RNG.uniform(.95,1.65)
   instance(c,f'V10 | {layer} | {made:03}',x,y,size,RNG.uniform(0,math.tau));centers.append((x,y));made+=1
 # Decompose fern display layout into individual variants before planting.
 ferns=[standalone(o,'V10 source | fern '+str(i)) for i,o in enumerate(bpy.data.collections['V8 source | fern'].objects) if o.type=='MESH']
 # Newly acquired low conifers fill the otherwise empty space under tall trunks.
 before_objects=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/v10/downloads/fir_sapling/fir_sapling_2k.gltf'))
 imported=set(bpy.data.objects)-before_objects;saplings=[]
 for o in imported:
  if o.type!='MESH':continue
  for m in o.data.materials:
   if m and m.use_nodes and 'twigs' in m.name:
    p=m.node_tree.nodes.get('Principled BSDF');t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/v10/downloads/fir_sapling/textures/fir_sapling_twigs_alpha_2k.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';m.node_tree.links.new(t.outputs['Color'],p.inputs['Alpha'])
  saplings.append(standalone(o,'V10 source | '+o.name))
 for o in imported:bpy.data.objects.remove(o,do_unlink=True)
 for i in range(280):
  x=RNG.uniform(-28,18);y=RNG.uniform(-43,7)
  if not path_clear(x,y,'sapling') or (-9<x<1 and -6<y<3):continue
  instance(RNG.choice(saplings),f'V10 | Understory conifer | {i:03}',x,y,RNG.uniform(.65,1.7),RNG.uniform(0,math.tau),wind=.7)
 # Fern colonies follow the sides of the worn route, breaking up uniform spacing.
 for i in range(1350):
  x=RNG.uniform(-23,15);y=RNG.uniform(-39,4)
  if not path_clear(x,y,'fern') or (-8<x<.2 and -6<y<2):continue
  patch=math.sin(x*.73+y*.24)*math.cos(y*.54-x*.15)
  if patch<-.25:continue
  instance(RNG.choice(ferns),f'V10 | Fern colony | {i:04}',x,y,RNG.uniform(.65,1.9),RNG.uniform(0,math.tau),wind=1.6)
 # Native alpha-textured grass blades combined into reusable, irregular clumps.
 grassfile=ROOT/'assets/v10/downloads/grass_bermuda_01/grass_bermuda_01_2k.blend'
 with bpy.data.libraries.load(str(grassfile),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('grass_bermuda_01_medium_') or n.startswith('grass_bermuda_01_seedling_')]
 grasses=[o for o in dst.objects if o and o.type=='MESH'];patches=[]
 for k in range(10):
  vs=[];fs=[];uvs=[];mis=[];mats=[]
  for i in range(36):
   src=RNG.choice(grasses);me=src.data;angle=RNG.uniform(0,math.tau);r=math.sqrt(RNG.random())*.55;x=math.cos(angle)*r;y=math.sin(angle)*r
   transform=Matrix.Translation((x,y,0))@Matrix.Rotation(RNG.uniform(0,math.tau),4,'Z')@Matrix.Diagonal((RNG.uniform(2.1,4.3),RNG.uniform(2.1,4.3),RNG.uniform(1.3,2.8),1))
   offset=len(vs);vs.extend([transform@v.co for v in me.vertices]);uv=me.uv_layers.active
   for p in me.polygons:
    fs.append(tuple(offset+v for v in p.vertices));uvs.extend([tuple(uv.data[l].uv) if uv else (0,0) for l in p.loop_indices]);material=me.materials[p.material_index]
    if material not in mats:mats.append(material)
    mis.append(mats.index(material))
  me=bpy.data.meshes.new('V10 | grass colony '+str(k));me.from_pydata(vs,[],fs);me.update();uv=me.uv_layers.new(name='UVMap')
  for l,co in zip(uv.data,uvs):l.uv=co
  for m in mats:me.materials.append(m)
  for p,mi in zip(me.polygons,mis):p.material_index=mi;p.use_smooth=True
  ob=bpy.data.objects.new(me.name,me);c=bpy.data.collections.new('V10 source | grass colony '+str(k));c.objects.link(ob);patches.append(c)
 for i in range(4100):
  if i%6:continue
  x=RNG.uniform(-28,20);y=RNG.uniform(-48,7)
  if -8<x<.2 and -6<y<2:continue
  clear=path_clear(x,y,'grass')
  # Short sparse tufts remain on the path; surrounding banks are densely grown.
  if not clear and RNG.random()>.12:continue
  scale=RNG.uniform(.65,1.3) if clear else RNG.uniform(.12,.26)
  instance(RNG.choice(patches),f'V10 | Grass bank | {i:04}',x,y,scale,RNG.uniform(0,math.tau),wind=1.8 if clear and i%3==0 else 0)
 # Broader leafy clumps form the main carpet; Bermuda remains fine edge detail.
 mediumfile=ROOT/'assets/v10/downloads/grass_medium_01/grass_medium_01_2k.blend'
 with bpy.data.libraries.load(str(mediumfile),link=False) as (src,dst):dst.objects=[f'grass_medium_01_large_{v}_LOD2' for v in 'abc']
 leafy=[];fixed=set()
 def fix_weight(tree):
  if tree in fixed:return
  fixed.add(tree)
  for node in tree.nodes:
   if node.type in ['BSDF_PRINCIPLED','BSDF_TRANSLUCENT'] and 'Weight' in node.inputs and not node.inputs['Weight'].is_linked:node.inputs['Weight'].default_value=1
   if node.type=='GROUP' and node.node_tree:fix_weight(node.node_tree)
 for i,o in enumerate(dst.objects):
  for m in o.data.materials:
   if m and m.use_nodes:fix_weight(m.node_tree)
  leafy.append(standalone(o,'V10 source | leafy grass '+str(i)))
 for i in range(3200):
  x=RNG.uniform(-28,20);y=RNG.uniform(-48,7)
  if -8<x<.2 and -6<y<2:continue
  clear=path_clear(x,y,'grass')
  if not clear and RNG.random()>.06:continue
  width=RNG.uniform(2.0,3.6) if clear else RNG.uniform(.25,.65)
  height=RNG.uniform(1.25,2.5) if clear else .3
  instance(RNG.choice(leafy),f'V10 | Leafy grass carpet | {i:04}',x,y,(width,width,height),RNG.uniform(0,math.tau),wind=1.1 if i%4==0 else 0)
 # Scanned mossy rocks, fallen timber and roots tie the green ground to the gate.
 stones=[c for c in bpy.data.collections if c.name.startswith('V8 source | individual moss stone')]
 for i in range(65):
  x=RNG.uniform(-25,15);y=RNG.uniform(-38,5)
  if not path_clear(x,y,'tree') or (-9<x<1 and -6<y<3):continue
  instance(RNG.choice(stones),f'V10 | Mossy outcrop | {i:03}',x,y,RNG.uniform(.25,.75),RNG.uniform(0,math.tau))
 cliff=bpy.data.collections['V8 source | cliff']
 for i,(x,y,z,size,rot) in enumerate([(-8.6,-3.5,.12,(1.2,1,1.35),.04),(.8,-3.5,.12,(1.1,1,1.45),-.08),(-3.8,-2.0,3.8,(1.4,1,1),.15)]):instance(cliff,f'V10 | Rock around entrance | {i}',x,y,size,rot,z=z)
 # Weather the static equipment wings; moving door geometry is preserved.
 alloy=bpy.data.materials.new('V10 | weathered entry alloy');alloy.use_nodes=True;p=alloy.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.065,.11,.12,1);p.inputs['Metallic'].default_value=.7;p.inputs['Roughness'].default_value=.53
 noise=alloy.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;noise.inputs['Detail'].default_value=2;bump=alloy.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.007;alloy.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);alloy.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 for ob in sc.objects:
  if ob.name.startswith('V5 | portal equipment wing'):ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(alloy)
 # Soft dawn canopy lighting: legible green detail, warm edge light, cool depth.
 for ob in sc.objects:
  if ob.type=='LIGHT' and ob.name=='V8 | last light through canopy':ob.data.color=(1,.83,.61);ob.data.energy=1.55;ob.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-32));ob.data.angle=math.radians(9)
  if ob.type=='LIGHT' and ob.name=='V8 | open sky bounce':ob.data.color=(.64,.8,1);ob.data.energy=1450;ob.data.size=13
 sc.view_settings.exposure=.15
 world=sc.world;bg=world.node_tree.nodes.get('Background');sky=world.node_tree.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(28);sky.sun_rotation=math.radians(130);sky.sun_disc=False;sky.altitude=.15;bg.inputs['Strength'].default_value=.10;world.node_tree.links.new(sky.outputs['Color'],bg.inputs['Color'])
 fogmat=bpy.data.materials.new('V10 | Thin woodland haze');fogmat.use_nodes=True;n=fogmat.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Density'].default_value=.008;vol.inputs['Color'].default_value=(.62,.74,.78,1);vol.inputs['Anisotropy'].default_value=.3;fogmat.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
 bpy.ops.mesh.primitive_cube_add(size=1,location=(-3,-15,17));fog=bpy.context.object;fog.name='V10 | Woodland atmosphere';fog.scale=(270,265,40);fog.data.materials.append(fogmat)
 for i,pos in enumerate([(10,-20,6),(-20,-16,7)]):
  data=bpy.data.lights.new('V10 | soft sky through trees '+str(i),'AREA');ob=bpy.data.objects.new(data.name,data);col.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((-4,-17,.3))-ob.location).to_track_quat('-Z','Y').to_euler();data.energy=1000;data.size=15;data.color=(.70,.84,.86)
 fix_grass_materials();fix_leafy_materials();lod_report=optimize_forest_lods(sc)
 (OUT/'lod-report.json').write_text(json.dumps(lod_report,indent=2)+'\n')
 sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.render.fps=12;sc.frame_start=1;sc.frame_end=144
 sc.eevee.volumetric_tile_size='16';sc.eevee.volumetric_samples=32
 sc['environment_version']='V10 — dense forest, grass colonies, understory and atmosphere';sc.frame_set(20);bpy.context.view_layer.update();assert motion_hash()==before,'Original action or camera animation changed'
 for image in bpy.data.images:
  if image.filepath and not image.packed_file:image.filepath=bpy.path.abspath(image.filepath)
 dest=ROOT/'bear-bow-forest-v10.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
 report={'scene':dest.name,'source_scene':'bear-bow-escape-v9.blend','unchanged_motion_and_camera_hash':before,'instances':counts,'total_environment_instances':sum(counts.values()),'assets':'Existing PolyHaven fir, fern, moss stones and rock face plus CC0 Grass Bermuda01, Grass Medium01 and Fir Sapling','design':'Dense layered conifer forest around a narrow worn escape route; overlapping wooded background, low conifers, fern/grass banks, softly lit haze','heavy_render':False,'retargeted_final_heroine':False,'frames':144,'fps':12,'resolution':[960,540],'samples':16}
 (OUT/'environment-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
