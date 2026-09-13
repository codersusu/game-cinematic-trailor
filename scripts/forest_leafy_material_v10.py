"""Explicit green leaf shader; preserves native atlas alpha and vein detail."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fix_leafy_materials():
 mats={m for c in bpy.data.collections if c.name.startswith('V10 source | leafy grass') for o in c.objects if o.type=='MESH' for m in o.data.materials if m}
 for m in mats:
  m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();n=nt.nodes;l=nt.links
  out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.78;p.inputs['Specular IOR Level'].default_value=.2;p.inputs['Subsurface Weight'].default_value=.10
  uv=n.new('ShaderNodeTexCoord');images={}
  for role,suffix,space in [('diff','diff_2k.jpg','sRGB'),('alpha','alpha_2k.png','Non-Color'),('normal','nor_gl_2k.exr','Non-Color')]:
   t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/f'assets/v10/downloads/grass_medium_01/textures/grass_medium_01_{suffix}'),check_existing=True);t.image.colorspace_settings.name=space;l.new(uv.outputs['UV'],t.inputs['Vector']);images[role]=t
  color=n.new('ShaderNodeMixRGB');color.blend_type='MIX';color.inputs[0].default_value=.70;color.inputs[2].default_value=(.12,.30,.024,1);l.new(images['diff'].outputs['Color'],color.inputs[1]);l.new(color.outputs[0],p.inputs['Base Color']);l.new(images['alpha'].outputs['Color'],p.inputs['Alpha'])
  normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.3;l.new(images['normal'].outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs['Normal']);l.new(p.outputs['BSDF'],out.inputs['Surface']);m.surface_render_method='DITHERED';m.use_backface_culling=False;m.diffuse_color=(.12,.30,.024,1)
