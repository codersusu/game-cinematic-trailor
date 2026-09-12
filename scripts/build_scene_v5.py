"""Build Astra Chamber around the unchanged baked V4 heroine and stellar galaxy."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
OUT=ROOT/'renders/v5';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'observatory-v4.blend'))
scene=bpy.context.scene
# Preserve the reviewed animation, facial keys, galaxy, cameras and focus targets.
roots={'Heroine v4 • native root motion','GALAXY V3 | master'}
def preserve(o):
 if o.type=='CAMERA' or o.name.endswith(' focus'):return True
 a=o
 while a:
  if a.name in roots:return True
  a=a.parent
 return False
for o in list(bpy.data.objects):
 if not preserve(o):bpy.data.objects.remove(o,do_unlink=True)
for coll in list(bpy.data.collections):
 if not coll.objects and not coll.children:bpy.data.collections.remove(coll)
COL=bpy.data.collections.new('V5 | Astra Chamber');scene.collection.children.link(COL)
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);return o

def mat(name,color,metal=0,rough=.4,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m

def finish(name,asset,color,metal,rough_low,rough_high):
 m=mat(name,color,metal);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 folder=ROOT/'assets/v5/materials'/asset;files=list(folder.glob('*_Color.jpg'));prefix=files[0].name.removesuffix('_Color.jpg')
 coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1.5;l.new(coord.outputs['Object'],mapping.inputs[0])
 for channel in ['Color','Roughness','Displacement']:
  path=folder/(prefix+'_'+channel+'.jpg');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True);tex.projection='BOX';tex.projection_blend=.15
  if channel!='Color':tex.image.colorspace_settings.name='Non-Color'
  l.new(mapping.outputs['Vector'],tex.inputs['Vector'])
  if channel=='Color':
   mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*color,1);l.new(tex.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
  elif channel=='Roughness':
   remap=n.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=rough_low;remap.inputs['To Max'].default_value=rough_high;l.new(tex.outputs['Color'],remap.inputs['Value']);l.new(remap.outputs[0],p.inputs['Roughness'])
  else:
   bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.0002;l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
 return m
alloy=finish('V5 | satin structural alloy','Metal032',(.46,.55,.64),.85,.24,.4)
polished=finish('V5 | polished machined edges','Metal050A',(.68,.74,.8),.95,.16,.27)
shell=finish('V5 | pale manufactured shells','Plastic010',(.67,.71,.74),.05,.28,.4)
deck=finish('V5 | charcoal satin deck','Metal032',(.095,.13,.18),.55,.3,.47)
black=mat('V5 | dark gasket and recess',(.009,.015,.023),.2,.46)
copper=mat('V5 | restrained copper fittings',(.43,.235,.10),.8,.25)
warm=mat('V5 | warm guide light',(1,.63,.28),0,.3,4)
cool=mat('V5 | instrument ceramic light',(.45,.78,1),0,.3,4.5)
screen=mat('V5 | instrument display',(.012,.07,.12),.15,.2,.8)
signal=mat('V5 | display fine marks',(.18,.68,1),0,.25,2)
# Anti-reflective thin glazing; small reflection contribution keeps stars readable.
glass=bpy.data.materials.new('V5 | optical anti-reflection glazing');glass.use_nodes=True
n=glass.node_tree.nodes;l=glass.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.035
trans=n.new('ShaderNodeBsdfTransparent');g=n.new('ShaderNodeBsdfGlass');g.inputs['Color'].default_value=(.84,.93,1,1);g.inputs['Roughness'].default_value=.035;g.inputs['IOR'].default_value=1.45
l.new(trans.outputs[0],mix.inputs[1]);l.new(g.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])

def bevel(o,width=.025,segments=3):
 mod=o.modifiers.new('Manufactured edge radii','BEVEL');mod.width=width;mod.segments=segments
 if o.type=='MESH':
  mod=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return o

def cube(name,loc,size,material,edge=.025,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=link(bpy.context.object);o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material)
 if edge:bevel(o,edge)
 if parent:o.parent=parent
 return o

def cylinder(name,loc,r,depth,material,vertices=96,parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=link(bpy.context.object);o.name=name;o.data.materials.append(material);bevel(o,.015)
 if parent:o.parent=parent
 return o

def mesh(name,verts,faces,material,parent=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o);me.materials.append(material)
 if parent:o.parent=parent
 return o

def line(name,points,r,material,parent=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(material)
 if parent:o.parent=parent
 return o

def annulus(name,r1,r2,z,depth,material,center=(0,2),a1=0,a2=math.tau,parent=None,steps=192):
 verts=[]
 for zz in [z-depth/2,z+depth/2]:
  for r in [r1,r2]:
   for j in range(steps+1):
    a=a1+(a2-a1)*j/steps;verts.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),zz))
 N=steps+1;faces=[]
 for j in range(steps):faces.extend([(j,j+1,N+j+1,N+j),(2*N+j,3*N+j,3*N+j+1,2*N+j+1),(j,2*N+j,2*N+j+1,j+1),(N+j,N+j+1,3*N+j+1,3*N+j)])
 faces.extend([(0,N,3*N,2*N),(N-1,2*N-1,4*N-1,3*N-1)])
 return bevel(mesh(name,verts,faces,material,parent),.008,2)

def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);COL.objects.link(o);o.location=loc;o.parent=parent;return o

def light(name,loc,power,color,size,target,shape='DISK',size_y=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape=shape;d.size=size
 if size_y is not None:d.size_y=size_y
 o=bpy.data.objects.new(name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

# Continuous ground at the exact native sole-contact height, with inlaid seams.
cube('V5 | continuous chamber and transept deck',(0,0,.04),(23,28,.2),deck,.015)
for r in [3.1,4.8,7.2,9.9]:
 annulus('V5 | deck recessed ring',r,r+.027,.142,.004,black)
for r in [3.25,9.5]:annulus('V5 | floor guidance ring',r,r+.023,.147,.008,warm)
for i in range(32):
 a=i*math.tau/32
 line('V5 | radial deck joint',[(r*math.cos(a),2+r*math.sin(a),.142) for r in [3.35,9.6]],.007,black)
# Dark anti-slip inserts along the actual arrival route.
rubber=mat('V5 | rubber walking inserts',(.025,.03,.034),0,.7)
n=rubber.node_tree.nodes;l=rubber.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');vm=n.new('ShaderNodeVectorMath');vm.operation='SCALE';vm.inputs[3].default_value=.5;l.new(tc.outputs['Object'],vm.inputs[0])
for chan,socket in [('diff','Base Color'),('rough','Roughness')]:
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/f'assets/v5/materials/rubber_tiles/rubber_tiles_{chan}_2k.jpg'),check_existing=True);t.projection='BOX';t.projection_blend=.15
 if chan=='rough':t.image.colorspace_settings.name='Non-Color'
 l.new(vm.outputs[0],t.inputs[0]);l.new(t.outputs['Color'],p.inputs[socket])
for j in range(9):
 y=-8.5+j*.82
 cube('V5 | flush anti-slip insert',(-3.8,y,.132),(1.34,.79,.024),rubber,.007)
 for side in [-1,1]:
  o=cube('V5 | awakening path segment',(-3.8+side*.82,y,.15),(.025,.56,.013),warm,.004)
  m=warm.copy();m.name='V5 | sequenced path light';o.data.materials[0]=m;socket=m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength']
  start=28+j*13
  for f,v in [(1,.08),(start,.08),(start+10,4),(576,4)]:socket.default_value=v;socket.keyframe_insert('default_value',frame=f)
# Rear and side window bays: open front connects to a broad interior transept.
angles=[math.radians(-30+i*20) for i in range(13)]
for a in angles:
 x=9.15*math.cos(a);y=2+9.15*math.sin(a)
 o=cube('V5 | structural titanium mullion',(x,y,4.65),(.24,.34,9.0),alloy,.055);o.rotation_euler.z=a
 for z in [.42,2.75,8.8]:
  o=cube('V5 | mullion locking collar',(x,y,z),(.34,.46,.22),polished,.03);o.rotation_euler.z=a
 # Full dome ribs follow engineered arcs to central crown.
 pts=[]
 for j in range(41):
  t=j*math.pi/2/40;r=9.15*math.cos(t);pts.append((r*math.cos(a),2+r*math.sin(a),9.1+3.5*math.sin(t)))
 line('V5 | overhead titanium rib',pts,.09,alloy)
for a,b in zip(angles[:-1],angles[1:]):
 mid=(a+b)/2;width=2*9.15*math.sin((b-a)/2)
 for z,h in [(1.35,2.42),(8.90,.38)]:
  o=cube('V5 | manufactured perimeter shell',(9.35*math.cos(mid),2+9.35*math.sin(mid),z),(width,.25,h),shell,.045);o.rotation_euler.z=mid+math.pi/2
 # Curved thin optical glazing, behind all dressing.
 verts=[]
 for z in [2.8,8.7]:
  for j in range(13):
   aa=a+(b-a)*j/12;verts.append((9.25*math.cos(aa),2+9.25*math.sin(aa),z))
 mesh('V5 | panoramic glass bay',verts,[(j,j+1,14+j,13+j) for j in range(12)],glass)
 # matching roof glass strips.
 verts=[]
 for j in range(21):
  t=j*math.pi/2/20;r=9.25*math.cos(t)
  for aa in [a,b]:verts.append((r*math.cos(aa),2+r*math.sin(aa),9.12+3.5*math.sin(t)))
 mesh('V5 | optical roof glazing',verts,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(20)],glass)
 for z in [.3,2.68,8.7]:
  pts=[(9.06*math.cos(a+(b-a)*j/20),2+9.06*math.sin(a+(b-a)*j/20),z) for j in range(21)]
  line('V5 | perimeter cove light',pts,.025,warm)
annulus('V5 | dome collar',9.02,9.28,9.10,.16,alloy,a1=angles[0],a2=angles[-1])
annulus('V5 | crown fitting',.65,.88,12.55,.16,polished)

# Sliding airlock, outside the heroine's route until it is fully open.
portal=empty('V5 | airlock assembly',(-3.8,-5.8,.14))
for side in [-1,1]:
 cube('V5 | airlock structural jamb',(side*1.86,0,1.74),(.38,.60,3.48),alloy,.075,portal)
 cube('V5 | airlock pale casing',(side*2.12,.07,1.75),(.17,.78,3.50),shell,.05,portal)
 cube('V5 | warm airlock rim',(side*1.64,.32,1.76),(.045,.045,3.19),warm,.016,portal)
 cube('V5 | portal equipment wing',(side*3.35,0,1.65),(2.1,.4,3.3),shell,.06,portal)
 for z in [.38,2.9]:cube('V5 | wing dark recess',(side*3.35,.215,z),(1.72,.027,.12),black,.015,portal)
 leaf=empty('V5 | sliding airlock leaf '+str(side),(side*.8,0,0),portal)
 cube('V5 | solid door leaf',(0,0,1.65),(1.58,.2,3.22),alloy,.055,leaf)
 cube('V5 | inset ceramic door panel',(0,.12,1.66),(1.29,.06,2.79),shell,.045,leaf)
 cube('V5 | door status strip',(-side*.48,.166,1.7),(.045,.018,1.38),cool,.008,leaf)
 for z in [.39,2.91]:cube('V5 | machined door seam',(0,.16,z),(1.13,.024,.07),black,.01,leaf)
 for f,x in [(1,side*.8),(7,side*.8),(34,side*2.60),(576,side*2.60)]:leaf.location.x=x;leaf.keyframe_insert('location',frame=f)
 for fc in leaf.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
cube('V5 | airlock lintel',(0,0,3.53),(4.6,.84,.32),alloy,.065,portal)
cube('V5 | lintel illuminated inset',(0,.44,3.49),(3.2,.025,.035),warm,.008,portal)
cube('V5 | flush threshold',(0,0,-.007),(3.23,.65,.024),polished,.01,portal)
# Behind the portrait, a quiet approach corridor gives a tangible interior backdrop.
for side in [-1,1]:
 cube('V5 | approach sidewall',(-3.8+side*2.32,-9.3,1.8),(.22,5.9,3.6),shell,.04)
 cube('V5 | approach floor cove',(-3.8+side*2.17,-9.3,.25),(.035,5.7,.035),warm,.008)
cube('V5 | approach back wall',(-3.8,-12.15,1.8),(4.85,.2,3.6),alloy,.04)
for x in [-5.65,-4.45,-3.15,-1.95]:cube('V5 | approach back inlay',(x,-12.035,1.8),(.035,.025,2.6),warm,.005)

# Original precision apparatus wraps the unmodified Astra stellar geometry.
for r,z,d,m in [(2.72,.25,.22,alloy),(2.48,.44,.16,shell),(2.17,.60,.16,black),(1.75,.74,.17,alloy),(1.32,.92,.2,polished)]:
 cylinder('V5 | instrument platform',(0,2,z),r,d,m,160)
for r,z in [(2.46,.53),(1.76,.83)]:annulus('V5 | platform luminous inlay',r-.02,r+.02,z,.022,cool)
for k in range(12):
 a=k*math.tau/12
 ob=cube('V5 | platform access cassette',(2.2*math.cos(a),2+2.2*math.sin(a),.47),(.24,.48,.16),alloy,.025);ob.rotation_euler.z=a
 for s in [-1,1]:
  cylinder('V5 | base captive bolt',(2.2*math.cos(a)-s*.16*math.sin(a),2+2.2*math.sin(a)+s*.16*math.cos(a),.565),.025,.019,polished,12)
center=(0,2,3.7)
ring_roots=[]
for idx,(radius,tilt,turn) in enumerate([(2.45,(90,0,0),125),(2.20,(76,23,47),-150)]):
 tiltroot=empty('V5 | gimbal orientation '+str(idx),center);tiltroot.rotation_euler=tuple(math.radians(x) for x in tilt)
 spin=empty('V5 | rotating precision ring '+str(idx),parent=tiltroot);ring_roots.append(spin)
 for f in range(1,577,8):spin.rotation_euler.z=math.radians(turn)*(f-1)/575;spin.keyframe_insert('rotation_euler',frame=f)
 spin.rotation_euler.z=math.radians(turn);spin.keyframe_insert('rotation_euler',frame=576)
 annulus('V5 | gimbal structural hoop',radius-.085,radius+.085,0,.16,alloy,center=(0,0),parent=spin)
 for z in [-.089,.089]:annulus('V5 | gimbal polished rail',radius-.065,radius+.065,z,.015,polished,center=(0,0),parent=spin)
 for k in range(12):
  a=k*math.tau/12
  annulus('V5 | ring ceramic segment',radius-.069,radius+.069,.112,.027,shell,center=(0,0),a1=a+.07,a2=a+.29,parent=spin,steps=10)
  annulus('V5 | ring illuminated index',radius-.026,radius+.026,-.111,.025,cool,center=(0,0),a1=a+.07,a2=a+.24,parent=spin,steps=10)
  for off in [.015,.34]:
   bolt=cylinder('V5 | ring captive fastener',(radius*math.cos(a+off),radius*math.sin(a+off),-.105),.028,.022,copper,12,spin)
  # Deep radial clamps provide true parallax rather than only texture lines.
  if k%3==0:
   ob=cube('V5 | gimbal radial clamp',(radius*math.cos(a),radius*math.sin(a),0),(.25,.18,.29),black,.028,spin);ob.rotation_euler.z=a
for side in [-1,1]:
 pod=cylinder('V5 | magnetic bearing',(side*2.45,2,3.7),.18,.3,copper,64);pod.rotation_euler.y=math.pi/2
 cube('V5 | bearing upright',(side*2.50,2,2.12),(.19,.34,2.98),alloy,.05)
 cube('V5 | upright illuminated channel',(side*2.50,1.81,2.24),(.035,.022,2.34),cool,.008)
# Low consoles with modeled controls and original thin orbital graphics.
for index,(x,y) in enumerate([(5.2,3.8),(6.5,4.8)]):
 root=empty('V5 | observation console '+str(index),(x,y,.14));root.rotation_euler.z=math.radians(-28)
 cube('V5 | console plinth',(0,0,.14),(1.45,.95,.28),alloy,.075,root)
 cube('V5 | console pedestal',(0,.15,.56),(.93,.70,.70),black,.05,root)
 top=cube('V5 | console sloped head',(0,0,1.01),(1.50,.93,.18),shell,.065,root);top.rotation_euler.x=math.radians(19)
 display=empty('V5 | console display plane',(0,-.005,1.12),root);display.rotation_euler.x=math.radians(19)
 cube('V5 | console optical display',(0,0,0),(1.25,.70,.025),screen,.026,display)
 for rr in [.12,.21,.27]:line('V5 | screen orbit',[(rr*math.cos(j*math.tau/72)-.21,rr*math.sin(j*math.tau/72),.016) for j in range(73)],.002,signal,display)
 for j in range(6):cube('V5 | console data line',(.36,-.23+j*.075,.018),(.30-(j%3)*.06,.009,.006),signal,.002,display)
 for j in range(4):cylinder('V5 | console tactile key',(-.46+j*.14,-.29,.034),.024,.02,polished,16,display)

from scifi_dressing_v5 import add_scifi_dressing
dressing=add_scifi_dressing()
(OUT/'reused-assets.json').write_text(json.dumps({'sources':dressing['sources'],'dependencies':dressing['dependencies']},indent=2))
# Portrait camera stays on the approach side of the closing door.
cam=bpy.data.objects['00 • A breath at the threshold'];focus=cam.data.dof.focus_object
cam.animation_data_clear();cam.data.lens=58
for f,delta in [(1,(.32,1.6,.07)),(36,(.24,1.53,.055))]:
 scene.frame_set(f);target=focus.location.copy();cam.location=target+Vector(delta);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
# Frame the new architecture from inside the airlock and look through the ring apertures.
def reframe(name,start,end,target1,target2,lens,f1,f2):
 cam=bpy.data.objects[name];focus=cam.data.dof.focus_object
 cam.animation_data_clear();focus.animation_data_clear();cam.data.lens=lens
 for f,loc,target in [(f1,start,target1),(f2,end,target2)]:
  cam.location=loc;focus.location=target;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);focus.keyframe_insert('location',frame=f)
reframe('02 • The turning heavens',(1.2,-3.6,3.05),(.45,-3.0,3.25),(0,2,3.85),(0,2,3.85),44,193,288)
reframe('03 • Under a billion stars',(5.5,-4.7,3.8),(4.8,-4.3,3.8),(0,2,3.05),(0,2,3.1),18,345,480)
reframe('04 • The stars remember',(1.2,-4.8,3.5),(.6,-4.3,3.8),(0,2,3.2),(0,2,3.35),17,481,576)
# Lighting is supported by visible architectural strips and soft overhead sources.
light('V5 | broad ceiling key',(-2,-.5,9),1250,(.78,.87,1),6,(0,2,1.5))
light('V5 | warm architectural bounce',(-5,-3,5.5),850,(1,.72,.46),4,(0,2,2))
light('V5 | cool window-side fill',(6,6,7),900,(.38,.60,1),5,(0,2,3))
light('V5 | front room fill',(1,-7,5),500,(.69,.81,1),5,(0,2,3))
light('V5 | warm approach key',(-4.8,-6.2,2.7),65,(1,.74,.50),1.4,(-3.8,-7.6,1.6))
light('V5 | soft approach fill',(-2.3,-6.7,2.5),35,(.61,.77,1),1.4,(-3.8,-7.6,1.6))
light('V5 | entry overhead',(-3.8,-4.8,3.8),130,(1,.78,.55),2,(-3.8,-4,.5))
light('V5 | reaction soft key',(-2.5,1.3,2.4),35,(.57,.79,1),1.2,(-3.8,-.8,1.55))
light('V5 | reaction warm rim',(-5.5,-1.5,2.6),35,(1,.72,.45),1.5,(-3.8,-.8,1.55))
light('V5 | stellar bounce',(0,1.7,3.7),65,(.37,.64,1),1.3,(-3.8,-.8,1.2))
# Reuse catalog sky, dim enough that the smaller foreground galaxy remains dominant.
scene.world.node_tree.nodes['Visible star exposure'].inputs['Strength'].default_value=.7
fog=bpy.data.materials.new('V5 | restrained chamber atmosphere');fog.use_nodes=True;n=fog.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.0014;v.inputs['Color'].default_value=(.48,.59,.70,1);v.inputs['Anisotropy'].default_value=.2;fog.node_tree.links.new(v.outputs['Volume'],o.inputs['Volume'])
cube('V5 | atmosphere',(0,1,5),(30,36,17),fog,0)
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.adaptive_threshold=.025;scene.cycles.use_denoising=True
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.fps=24
scene.render.use_motion_blur=True;scene.render.motion_blur_shutter=.4
# Remove all unused legacy material/image datablocks, leaving only portable dependencies.
for _ in range(3):
 for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.images):
  for block in list(datablocks):
   if block.users==0:datablocks.remove(block)
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
scene['version']='V5 Astra Chamber';scene['galaxy_preserved']=True;scene['character_performance']='Unchanged baked V4 body and facial keys'
scene.frame_set(420)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'observatory-v5.blend'),compress=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'observatory-v5.blend'),compress=True)
print('V5_SCENE_READY',len(scene.objects),flush=True)
