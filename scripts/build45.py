"""Reproducible cinematic environment. Blender --background --python scripts/build_scene.py"""
import bpy, math, random, sys, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
random.seed(41)
TAU=math.tau
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.cycles.use_denoising=True
scene.cycles.adaptive_threshold=.025
scene.cycles.max_bounces=8
scene.cycles.diffuse_bounces=3
scene.cycles.glossy_bounces=4
scene.cycles.transmission_bounces=6
scene.cycles.volume_bounces=1
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=576
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False
scene.render.use_persistent_data=True
scene.view_settings.view_transform='AgX'
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
scene.view_settings.exposure=-.55
scene.render.use_motion_blur=True
scene.render.motion_blur_shutter=.4
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences
 prefs.compute_device_type='METAL';prefs.get_devices()
 for d in prefs.devices: d.use=d.type=='METAL'
 scene.cycles.device='GPU'
 print('RENDER_DEVICES',[(d.name,d.type,d.use) for d in prefs.devices])
except Exception as e: print('CPU_FALLBACK',str(e));scene.cycles.device='CPU'

def material(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m

def noise_surface(m,scale=5,strength=.12,distance=.05):
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 tex=n.new('ShaderNodeTexNoise');coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector']);tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance
 l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 return tex

def scanned(name,asset,scale=1):
 m=material(name,(.2,.2,.2));n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=scale
 l.new(coord.outputs['Object'],mapping.inputs[0])
 for channel,ext,socket in [('diff','jpg','Base Color'),('rough','jpg','Roughness'),('disp','png',None)]:
  path=ROOT/'assets/texture'/asset/f'{asset}_{channel}_2k.{ext}'
  if not path.exists(): continue
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.projection='BOX';t.projection_blend=.25
  if channel!='diff':t.image.colorspace_settings.name='Non-Color'
  l.new(mapping.outputs['Vector'],t.inputs['Vector'])
  if socket:l.new(t.outputs['Color'],p.inputs[socket])
  else:
   norm=n.new('ShaderNodeBump');norm.inputs['Strength'].default_value=.4;norm.inputs['Distance'].default_value=.025;l.new(t.outputs['Color'],norm.inputs['Height']);l.new(norm.outputs['Normal'],p.inputs['Normal'])
 return m
stone=scanned('Limestone • scanned weathering','old_stone_wall_02',.48)
floor=scanned('Slate • rain worn','monastery_stone_floor',.56)
# Scattered damp patches alter reflectivity without covering the scanned surface.
fn=floor.node_tree.nodes;fl=floor.node_tree.links;fp=fn.get('Principled BSDF')
wet=fn.new('ShaderNodeTexNoise');wet.inputs['Scale'].default_value=.64;wet.inputs['Detail'].default_value=3
wr=fn.new('ShaderNodeValToRGB');wr.color_ramp.elements[0].position=.36;wr.color_ramp.elements[0].color=(.12,.12,.12,1);wr.color_ramp.elements[1].position=.59;wr.color_ramp.elements[1].color=(.85,.85,.85,1)
fl.new(wet.outputs['Fac'],wr.inputs[0]);fl.new(wr.outputs[0],fp.inputs['Roughness']);fp.inputs['Coat Weight'].default_value=.18
shaft=material('Monolithic pale limestone',(.21,.22,.20),0,.76)
st=noise_surface(shaft,6,.3,.045);sn=shaft.node_tree.nodes;sl=shaft.node_tree.links;sr=sn.new('ShaderNodeValToRGB');sr.color_ramp.elements[0].color=(.09,.105,.1,1);sr.color_ramp.elements[1].color=(.32,.32,.28,1);sl.new(st.outputs['Fac'],sr.inputs[0]);sl.new(sr.outputs[0],sn.get('Principled BSDF').inputs['Base Color'])
bronze=material('Bronze • centuries of patina',(.23,.105,.033),.78,.33)
n=bronze.node_tree.nodes;l=bronze.node_tree.links;p=n.get('Principled BSDF')
tex=noise_surface(bronze,26,.12,.002)
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.26;ramp.color_ramp.elements[0].color=(.028,.06,.046,1);ramp.color_ramp.elements[1].position=.68;ramp.color_ramp.elements[1].color=(.34,.17,.055,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
gold=material('Worn brass edges',(.49,.29,.095),.82,.28);noise_surface(gold,110,.12,.008)
dark=material('Blackened iron',(.025,.031,.034),.7,.37);noise_surface(dark,43,.1,.014)
obsidian=material('Polished black basalt',(.018,.026,.027),.15,.22);noise_surface(obsidian,17,.15,.018)
cloth=material('Faded indigo canvas',(.022,.039,.047),0,.87);noise_surface(cloth,190,.16,.002)
water=material('Rain water',(.17,.24,.24),.08,.09);water.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.65

COL=bpy.context.collection

def mesh_obj(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o)
 if mat:me.materials.append(mat)
 return o

def bevel(o,width=.04,segments=2):
 mod=o.modifiers.new('Rounded worn edges','BEVEL');mod.width=width;mod.segments=segments
 return o

def cube(name,loc,scale,mat,edge=.02):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 if edge:bevel(o,edge)
 return o

def cyl(name,loc,r,depth,mat,vertices=64):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);bevel(o,.025)
 return o

def line(name,points,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=2
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);COL.objects.link(o);c.materials.append(mat);return o

def wedge(name,r1,r2,a1,a2,z,h,mat,steps=4):
 vs=[]
 for zz in [z,z+h]:
  for r in [r1,r2]:
   for j in range(steps+1):
    a=a1+(a2-a1)*j/steps;vs.append((r*math.cos(a),r*math.sin(a)+2,zz))
 N=steps+1;fs=[]
 for j in range(steps):
  fs.extend([(j,j+1,N+j+1,N+j),(2*N+j,3*N+j,3*N+j+1,2*N+j+1),(j,2*N+j,2*N+j+1,j+1),(N+j,N+j+1,3*N+j+1,3*N+j)])
 fs.extend([(0,N,3*N,2*N),(N-1,2*N-1,4*N-1,3*N-1)])
 return bevel(mesh_obj(name,vs,fs,mat),.018)

# Set foundation and many independently edged radial floor stones.
cyl('Chamber foundation',(0,2,-.28),10,.5,dark,128)
for ring in range(8):
 r1=.8+ring*1.1;r2=r1+1.085;count=12+ring*6
 for j in range(count):
  a=TAU*(j+.5*(ring%2))/count
  wedge('Radial floor voussoir',r1,r2,a+.006,a+TAU/count-.006,-.03+random.uniform(-.008,.008),.16,floor)
for rr in [2.0,4.2,6.4,8.6]:
 wedge('Inlaid brass meridian',rr,rr+.022,0,TAU,.136,.008,gold,192)
for a in range(0,360,30):
 ar=math.radians(a)
 line('Meridian floor seam',[(r*math.cos(ar),r*math.sin(ar)+2,.141) for r in [2,8.7]],.009,gold)
# Dark stepped pedestal with layered bronze collars.
for r,z,d,mat in [(2.75,.16,.25,stone),(2.48,.36,.18,obsidian),(2.15,.54,.2,stone),(1.62,.7,.16,bronze),(1.37,.88,.24,obsidian)]:cyl('Orrery dais',(0,2,z),r,d,mat,96)
# Twelve colossal piers with capitals and high semicircular arches, framing the open south side.
for i in range(12):
 a=TAU*i/12; x=8.4*math.cos(a);y=2+8.4*math.sin(a)
 if i in [8,9,10]:continue
 for radius,z,dep,mat in [(.72,.25,.32,stone),(.58,.49,.16,obsidian),(.45,3.25,5.4,shaft),(.55,5.95,.23,stone),(.72,6.16,.21,stone)]:
  cyl('Observatory pier',(x,y,z),radius,dep,mat,24)
 # fluting and metal restraint rings
 for zz in [1.1,4.9]:cyl('Pier iron restraint',(x,y,zz),.463,.1,dark,32)
 for k in range(10):
  aa=k*TAU/10
  line('Carved pier flute',[(x+.445*math.cos(aa),y+.445*math.sin(aa),z) for z in [.9,5.5]],.018,shaft)
# Arches built as individual stone blocks.
for i in range(12):
 if i in [7,8,9,10]:continue
 a1=TAU*i/12;a2=TAU*(i+1)/12
 p1=Vector((8.4*math.cos(a1),2+8.4*math.sin(a1),6.18));p2=Vector((8.4*math.cos(a2),2+8.4*math.sin(a2),6.18))
 mid=(p1+p2)*.5;axis=(p2-p1).normalized();rad=(p2-p1).length/2
 normal=Vector((-axis.y,axis.x,0))
 for j in range(17):
  aa=j*math.pi/17+.009;bb=(j+1)*math.pi/17-.009;vs=[]
  for dep in [-.37,.37]:
   for rr in [rad,rad+.46]:
    for angle in [aa,bb]:
     q=mid+axis*(rr*math.cos(angle))+Vector((0,0,rr*math.sin(angle)))+normal*dep;vs.append(tuple(q))
  bevel(mesh_obj('Individual arch keystone',vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],stone),.025)
 # low parapet back wall
 ang=(a1+a2)/2
 wall=cube('Weathered parapet',(8.6*math.cos(ang),2+8.6*math.sin(ang),1.45),(4.05,.7,2.5),stone,.055);wall.rotation_euler.z=ang+math.pi/2
# Surviving dome ribs, incomplete panels, broken crown ring.
for i in range(16):
 a=TAU*i/16
 pts=[]
 for k in range(12 if i in [2,5,8,11,14] else 22):
  t=(math.pi/2)*k/25
  r=8.9*math.cos(t);z=7.8+4.3*math.sin(t)
  pts.append((r*math.cos(a),2+r*math.sin(a),z))
 line('Exposed dome rib',pts,.075,bronze)
 if i in [0,1,2,3,4,5,6,7]:
  # broken dome skin near outer edge
  verts=[]
  for k in range(6):
   t=.04+k*.10
   for side in [0,1]:
    an=a+side*TAU/16;r=8.9*math.cos(t);verts.append((r*math.cos(an),2+r*math.sin(an),7.8+4.3*math.sin(t)))
  mesh_obj('Surviving dome plate',verts,[(k*2,k*2+1,k*2+3,k*2+2) for k in range(5)],dark)
for z,r in [(7.8,8.9),(8.1,8.87)]:line('Dome structural collar',[(r*math.cos(j*TAU/192),2+r*math.sin(j*TAU/192),z) for j in range(193)],.1,bronze)
# A few hanging banners with modeled folds.
for a in [.38,2.65]:
 x=7.8*math.cos(a);y=2+7.8*math.sin(a);verts=[];faces=[]
 for j in range(19):
  for k in range(9):
   u=k/8;v=j/18;verts.append((x+(u-.5)*1.1,y+.1*math.sin(u*math.pi*6+v*2),6.4-v*3.1+.07*math.sin(u*19)*v**5))
 for j in range(18):
  for k in range(8):n=j*9+k;faces.append((n,n+1,n+10,n+9))
 o=mesh_obj('Keeper banners • folded cloth',verts,faces,cloth)
 for p in o.data.polygons:p.use_smooth=True
# Rock scans scattered in clusters; cliffs beyond arches.
for asset,count,rad in [('stone_01',65,7.6),('rock_face_01',7,19)]:
 path=ROOT/'assets/model'/asset/f'{asset}_2k.gltf'
 if not path.exists():continue
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 for base in imported:
  base.hide_render=True;base.hide_viewport=True
  for i in range(count):
   a=random.uniform(0,math.pi) if asset=='rock_face_01' else random.uniform(0,TAU);r=random.uniform(27,32) if asset=='rock_face_01' else random.uniform(rad-2,rad+2);o=base.copy();o.data=base.data;COL.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.name='Scanned cliff backdrop' if asset=='rock_face_01' else 'Scanned floor gravel'
   o.location=(r*math.cos(a),2+r*math.sin(a),.13 if asset=='stone_01' else -2)
   s=random.uniform(.5,2.8) if asset=='stone_01' else random.uniform(.6,1.0)
   o.scale=tuple(c*s for c in base.scale);o.rotation_euler.z=a
# Telescope with brass barrel, support and finder.
tele_root=bpy.data.objects.new('Antique survey telescope',None);COL.objects.link(tele_root);tele_root.location=(4.8,2,.15)
for z,r,d in [(1,.065,2),(1.75,.22,.12)]:
 o=cyl('Telescope mounting',(0,0,z),r,d,bronze);o.parent=tele_root
for a in [0,TAU/3,2*TAU/3]:
 o=line('Telescope tripod',[(0,0,1.55),(.7*math.cos(a),.7*math.sin(a),0)],.045,dark);o.parent=tele_root
for j,(r,depth) in enumerate([(.16,1.6),(.19,.12),(.19,.12)]):
 o=cyl('Optical brass barrel',(0,(j-1)*.65,1.9),r,depth,bronze);o.rotation_euler.x=math.pi/2;o.parent=tele_root
try:
 from ruins import add_ruin_details
 add_ruin_details(stone_mat=shaft)
except ImportError:pass
# Tiny suspended dust catches the light, sparse rather than fogging image.
verts=[];faces=[]
for i in range(200):
 x=random.uniform(-5,5);y=random.uniform(-3,7);z=random.uniform(.5,7);r=random.uniform(.002,.007);n=len(verts)
 verts.extend([(x-r,y,z),(x+r,y,z),(x,y,z+r*2)]);faces.append((n,n+1,n+2))
mesh_obj('Airborne illuminated dust',verts,faces,gold)
# Restrained room atmosphere.
fog=bpy.data.materials.new('Thin mountain haze');fog.use_nodes=True;nodes=fog.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');v=nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.003;v.inputs['Color'].default_value=(.43,.54,.63,1);v.inputs['Anisotropy'].default_value=.25;fog.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
cube('Atmosphere volume',(0,2,5),(27,27,16),fog,0)
# Machine generated in a separate reusable module.
try:
 from armillary import build_armillary
 machine=build_armillary(center=(0,2,3.7),bronze_mat=bronze,dark_mat=dark,accent_mat=gold)
except ImportError:
 machine={};print('MACHINE_MODULE_PENDING')
# Fine luminous inlays reveal the machine awakening without a featureless glowing orb.
lens_inlay=material('Celestial gold • awakening inlay',(.32,.17,.035),.68,.26)
lp=lens_inlay.node_tree.nodes.get('Principled BSDF');lp.inputs['Emission Color'].default_value=(1,.48,.09,1)
for f,e in [(1,0),(400,0),(455,.25),(480,4),(500,2.8),(576,2.3)]:
 lp.inputs['Emission Strength'].default_value=e;lp.inputs['Emission Strength'].keyframe_insert('default_value',frame=f)
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('Celestial globe') and any(t in o.name for t in ['meridians','constellation','stars']):
  o.data.materials.clear();o.data.materials.append(lens_inlay)
# Keeper appended with studio materials/rig preserved.
keeper={}
path=ROOT/'assets/character/integrate.py'
if path.exists():
 import importlib.util
 spec=importlib.util.spec_from_file_location('keeper_integration',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 keeper=mod.add_keeper(location=(-2.8,-.3,.14))
 print('KEEPER_INFO',str(keeper))
# Lighting: cold broken skylight, warm grazing illumination, soft portrait key.
world=bpy.data.worlds.new('Storm sky');scene.world=world;world.use_nodes=True
wn=world.node_tree.nodes;wl=world.node_tree.links
hdri=ROOT/'assets/hdri/kloofendal_overcast_puresky/kloofendal_overcast_puresky_2k.exr'
if hdri.exists():
 t=wn.new('ShaderNodeTexEnvironment');t.image=bpy.data.images.load(str(hdri));wl.new(t.outputs['Color'],wn.get('Background').inputs['Color'])
wn.get('Background').inputs['Strength'].default_value=.035

def light(name,kind,loc,energy,color,size=1,target=(0,2,2)):
 d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=color
 if kind=='AREA':d.shape='DISK';d.size=size
 elif kind=='POINT':d.shadow_soft_size=size
 o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
light('Moon through ruined dome','AREA',(2,5,11),1500,(.46,.67,1),5)
light('Amber rake across bronze','AREA',(-4,-2,7),1700,(1,.59,.28),5)
light('Cool arch rim','AREA',(5,8,5),900,(.35,.57,1),4)
light('Portrait softbox','AREA',(-4.5,-4,4.3),200,(1,.88,.72),2,target=(-2.8,-.3,1.6))
light('Keeper edge','AREA',(-3,2,3),230,(.4,.66,1),2,target=(-2.8,-.3,1.6))
shaft_light=light('Narrow moon shaft','SPOT',(-3,3,11),5200,(.60,.76,1),.1,target=(0,2,1.1))
shaft_light.data.spot_size=math.radians(28);shaft_light.data.spot_blend=.35
core=light('Awakening lens bounce','POINT',(0,.6,3.7),20,(1,.42,.1),.2)
for f,e in [(1,2),(380,4),(460,60),(480,180),(510,90),(576,70)]:core.data.energy=e;core.data.keyframe_insert('energy',frame=f)
light('Keeper eye catchlight','AREA',(-2.8,-2.1,2.1),15,(.8,.88,1),.6,target=(-2.8,-.3,1.8))
# Cameras share 2.39:1 composition via final editorial crop.
def camera(name,start,end,target1,target2,lens,f1,f2,fstop=4):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);COL.objects.link(o);d.lens=lens;d.sensor_width=36;d.clip_end=300;d.dof.use_dof=True;d.dof.aperture_fstop=fstop
 focus=bpy.data.objects.new(name+' focus',None);COL.objects.link(focus);d.dof.focus_object=focus
 for f,pos,target in [(f1,start,target1),(f2,end,target2)]:
  o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f);focus.location=target;focus.keyframe_insert('location',frame=f)
 marker=scene.timeline_markers.new(name,frame=f1);marker.camera=o
 return o
camera('01 • The sleeping instrument',(-3.8,-1.9,5.9),(-3.0,-1.5,5.6),(-1.2,2,5.3),(-.8,2,5.15),65,1,144,3.2)
face=keeper.get('face_target',(-2.8,-.3,1.78)) if isinstance(keeper,dict) else (-2.8,-.3,1.78)
face=tuple(face)
camera('02 • The keeper',(-3.45,-2.1,face[2]+.06),(-3.25,-1.83,face[2]+.03),face,face,65,145,288,3.5)
wide=camera('03 • The last observatory',(7.6,-12,3.3),(5.7,-10.5,2.9),(0,2,3.5),(0,2,3.6),32,289,480,7.1)
camera('04 • Alignment',(1.2,-12.4,3.9),(.6,-11.8,4.2),(0,2,3.65),(0,2,3.8),34,481,576,6.3)
scene.camera=wide
# Blender 4.5 classic compositor; restrained fog-glow highlights.
scene.use_nodes=True
nt=scene.node_tree
nt.nodes.clear()
rl=nt.nodes.new('CompositorNodeRLayers')
gl=nt.nodes.new('CompositorNodeGlare')
gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2.0;gl.mix=-.87
out=nt.nodes.new('CompositorNodeComposite')
nt.links.new(rl.outputs['Image'],gl.inputs['Image'])
nt.links.new(gl.outputs['Image'],out.inputs['Image'])
scene.frame_set(390)
# Keep the final project independent of the source rig's optional UI scripts.
for textblock in list(bpy.data.texts):bpy.data.texts.remove(textblock)
# Store all asset paths relative to project for portability.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'observatory45.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'observatory45.blend'))
print('SCENE_READY',len(bpy.data.objects),'objects')
