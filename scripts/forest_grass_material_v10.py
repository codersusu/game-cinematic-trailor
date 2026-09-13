"""Direct alpha-cutout Bermuda grass material for merged/instanced V10 patches.

Call fix_grass_materials() after loading/building the V10 scene, before saving.
No geometry, cameras, lighting, animation or texture files are modified.
"""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[1]
TEXTURES=ROOT/'assets/v10/downloads/grass_bermuda_01/textures'

def fix_grass_materials():
 objects=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V10 | grass colony')]
 materials={m for o in objects for m in o.data.materials if m}
 if not materials:materials={m for m in bpy.data.materials if m.name.startswith('grass_bermuda_01') and 'sphere' not in m.name}
 report={'objects':[o.name for o in objects],'materials':[],'geometry_changed':False,'textures_changed':False,'rendered':False}
 for m in sorted(materials,key=lambda x:x.name):
  m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();nodes=nt.nodes;links=nt.links
  out=nodes.new('ShaderNodeOutputMaterial');out.location=(1040,160)
  uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap';uv.location=(-900,100)
  textures={}
  for index,(role,suffix,space) in enumerate([('Diffuse','diff_2k.jpg','sRGB'),('Alpha','alpha_2k.png','Non-Color'),('Roughness','rough_2k.exr','Non-Color'),('Normal','nor_gl_2k.exr','Non-Color')]):
   p=TEXTURES/f'grass_bermuda_01_{suffix}';assert p.is_file(),p
   t=nodes.new('ShaderNodeTexImage');t.label=f'Native {role}';t.name=f'V10 | grass {role}';t.location=(-650,440-index*270);t.image=bpy.data.images.load(str(p),check_existing=True);t.image.colorspace_settings.name=space;t.interpolation='Linear';t.extension='CLIP';links.new(uv.outputs['UV'],t.inputs['Vector']);textures[role]=t
  # Modest exposure lifting of the dark native olive albedo. The texture retains
  # its leaf veins and color variation; there is no emissive lighting shortcut.
  gamma=nodes.new('ShaderNodeGamma');gamma.label='Lift dark leaf albedo';gamma.inputs['Gamma'].default_value=.8;gamma.location=(-360,420);links.new(textures['Diffuse'].outputs['Color'],gamma.inputs['Color'])
  hsv=nodes.new('ShaderNodeHueSaturation');hsv.label='Living grass albedo';hsv.inputs['Hue'].default_value=.5;hsv.inputs['Saturation'].default_value=1.08;hsv.inputs['Value'].default_value=1.3;hsv.location=(-140,420);links.new(gamma.outputs['Color'],hsv.inputs['Color'])
  normal=nodes.new('ShaderNodeNormalMap');normal.uv_map='UVMap';normal.inputs['Strength'].default_value=.55;normal.location=(-100,-180);links.new(textures['Normal'].outputs['Color'],normal.inputs['Color'])
  principled=nodes.new('ShaderNodeBsdfPrincipled');principled.label='Native grass PBR';principled.location=(120,380);principled.inputs['Metallic'].default_value=0;principled.inputs['Specular IOR Level'].default_value=.28;principled.inputs['Roughness'].default_value=.72
  links.new(hsv.outputs['Color'],principled.inputs['Base Color']);links.new(textures['Roughness'].outputs['Color'],principled.inputs['Roughness']);links.new(normal.outputs['Normal'],principled.inputs['Normal'])
  translucent=nodes.new('ShaderNodeBsdfTranslucent');translucent.label='Leaf backlighting';translucent.location=(170,-60);links.new(hsv.outputs['Color'],translucent.inputs['Color']);links.new(normal.outputs['Normal'],translucent.inputs['Normal'])
  leaf=nodes.new('ShaderNodeMixShader');leaf.label='25 percent leaf translucency';leaf.inputs[0].default_value=.25;leaf.location=(470,250);links.new(principled.outputs['BSDF'],leaf.inputs[1]);links.new(translucent.outputs['BSDF'],leaf.inputs[2])
  transparent=nodes.new('ShaderNodeBsdfTransparent');transparent.location=(470,-50)
  cutout=nodes.new('ShaderNodeMixShader');cutout.label='White mask = visible leaf';cutout.location=(780,180);links.new(textures['Alpha'].outputs['Color'],cutout.inputs[0]);links.new(transparent.outputs['BSDF'],cutout.inputs[1]);links.new(leaf.outputs['Shader'],cutout.inputs[2]);links.new(cutout.outputs['Shader'],out.inputs['Surface'])
  if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
  m.use_backface_culling=False
  if hasattr(m,'use_transparent_shadow'):m.use_transparent_shadow=True
  m.diffuse_color=(.14,.25,.045,1);m['v10_grass_fix']='Explicit native UV/PBR/alpha, 25 percent translucency, albedo gamma .8 value1.3, no emission'
  report['materials'].append({'name':m.name,'textures':{k:v.image.filepath for k,v in textures.items()},'alpha_polarity':'white visible / black transparent','normal_strength':.55,'translucency':.25,'albedo_gamma':.8,'albedo_value':1.3,'surface_method':getattr(m,'surface_render_method',None)})
 report['uv_checks']=[{'object':o.name,'uv_layers':[u.name for u in o.data.uv_layers],'loop_count':len(o.data.loops),'uv_count':len(o.data.uv_layers['UVMap'].data) if 'UVMap' in o.data.uv_layers else 0} for o in objects]
 for row in report['uv_checks']:assert row['loop_count']==row['uv_count'],row
 out=ROOT/'renders/v10/grass-material-fix.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
 p=ROOT/'bear-bow-forest-v10.blend';bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);print(json.dumps(fix_grass_materials(),indent=2))
 # Standalone execution is inspection only; caller owns saving the scene.
