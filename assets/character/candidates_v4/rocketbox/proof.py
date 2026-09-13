import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'Female_Adult_04_facial.fbx'))
mesh=next(o for o in bpy.data.objects if o.type=='MESH')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rig.animation_data_clear()
for poly in mesh.data.polygons:poly.use_smooth=True
for m in mesh.data.materials:
 m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 p=n.new('ShaderNodeBsdfPrincipled');o=n.new('ShaderNodeOutputMaterial');l.new(p.outputs['BSDF'],o.inputs['Surface'])
 kind='head' if 'head' in m.name else 'opacity' if 'opacity' in m.name else 'body'
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/f'f004_{kind}_color.tga'),check_existing=True);l.new(t.outputs['Color'],p.inputs['Base Color'])
 p.inputs['Roughness'].default_value=.5 if kind=='head' else .57
 p.inputs['Specular IOR Level'].default_value=.3
 if kind=='head':p.inputs['Subsurface Weight'].default_value=.07;p.inputs['Subsurface Radius'].default_value=(1,.4,.2);p.inputs['Subsurface Scale'].default_value=.025
 if kind=='opacity':l.new(t.outputs['Alpha'],p.inputs['Alpha'])
 else:
  norm=n.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(R/f'f004_{kind}_normal.tga'),check_existing=True);norm.image.colorspace_settings.name='Non-Color'
  nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.45;l.new(norm.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],p.inputs['Normal'])
# Subdivision softens the early-generation facial silhouette without replacing its facial controls.
sub=mesh.modifiers.new('Portrait surface smoothing','SUBSURF');sub.levels=1;sub.render_levels=1
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,pos,power,color,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;aim(o,target)
bpy.ops.object.camera_add(location=(.06,-.95,1.65));cam=bpy.context.object;aim(cam,(0,0,1.60));cam.data.lens=70;bpy.context.scene.camera=cam
area('Warm window',(-1.1,-1.6,2.4),70,(1,.82,.68),1.3,(0,0,1.5))
area('Cool fill',(.9,-.7,1.8),22,(.6,.77,1),1,(0,0,1.5))
area('Rim',(.5,.7,2.2),60,(.6,.8,1),1,(0,0,1.5))
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('World');scene.world.color=(.045,.045,.045);scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
if hasattr(prefs,'use_metalrt'):prefs.use_metalrt=False
scene.cycles.device='GPU';scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.25
keys=mesh.data.shape_keys.key_blocks
poses={
 'neutral':{},
 'surprise':{'AK_03_BrowInnerUp':.32,'AK_04_BrowOuterUpLeft':.28,'AK_05_BrowOuterUpRight':.28,'AK_21_EyeWideLeft':.35,'AK_22_EyeWideRight':.35,'AK_25_JawOpen':.23},
 'wonder':{'AK_03_BrowInnerUp':.15,'AK_04_BrowOuterUpLeft':.16,'AK_05_BrowOuterUpRight':.14,'AK_21_EyeWideLeft':.16,'AK_22_EyeWideRight':.16,'AK_25_JawOpen':.28,'AK_32_MouthFunnel':.14,'AK_44_MouthSmileLeft':.12,'AK_45_MouthSmileRight':.1}}
for f,(label,vals) in enumerate(poses.items(),1):
 scene.frame_set(f)
 for k in keys:k.value=vals.get(k.name,0)
 for k in keys:
  if k.name!='Basis':k.keyframe_insert(data_path='value',frame=f)
 scene.render.filepath=str(R/f'portrait-{label}.png');bpy.ops.render.render(write_still=True)
scene.frame_start=1;scene.frame_end=3
bpy.ops.wm.save_as_mainfile(filepath=str(R/'portrait-proof.blend'),compress=True)
(R/'facial-proof.json').write_text(json.dumps({'mesh_vertices':len(mesh.data.vertices),'bones':len(rig.data.bones),'shape_keys':len(keys)-1,'poses':poses},indent=2))
