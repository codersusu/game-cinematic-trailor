"""Repair legacy Einar eye surfaces while preserving mesh, UVs and painted albedo.
Callable repair_eyes() edits only four eye materials. Running as a script saves
an alternate review blend and renders a small proof, never the canonical file.
"""
from pathlib import Path
import bpy,time
ROOT=Path(__file__).resolve().parents[1]

def repair_eyes():
    report=[]
    image=next((i for i in bpy.data.images if 'eyes.albedo' in i.name),None)
    if image is None:
        image=bpy.data.images.load(str(ROOT/'assets/character/einar/textures/face/eyes.albedo.tif'),check_existing=True)
    for name in ('eyes.white','eyes.iris','eyes.pupil'):
        mat=bpy.data.materials.get(name)
        if not mat:continue
        nt=mat.node_tree
        for node in list(nt.nodes):
            if node.name.startswith('Keeper eye repair'):nt.nodes.remove(node)
        uv=nt.nodes.new('ShaderNodeUVMap');uv.name='Keeper eye repair • Eyes UV';uv.uv_map='Eyes'
        tex=nt.nodes.new('ShaderNodeTexImage');tex.name='Keeper eye repair • original painted eye';tex.image=image
        surface=nt.nodes.new('ShaderNodeBsdfPrincipled');surface.name='Keeper eye repair • current surface'
        surface.inputs['Roughness'].default_value=.35
        surface.inputs['IOR'].default_value=1.4
        surface.inputs['Specular IOR Level'].default_value=.25
        surface.inputs['Subsurface Weight'].default_value=.035 if name=='eyes.white' else 0
        surface.inputs['Subsurface Scale'].default_value=.001
        nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'],surface.inputs['Base Color'])
        out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
        nt.links.new(surface.outputs['BSDF'],out.inputs['Surface'])
        report.append(name)
    mat=bpy.data.materials.get('eyes_shell')
    if mat:
        nt=mat.node_tree
        for node in list(nt.nodes):
            if node.name.startswith('Keeper eye repair'):nt.nodes.remove(node)
        glass=nt.nodes.new('ShaderNodeBsdfGlass');glass.name='Keeper eye repair • clear cornea'
        glass.inputs['Color'].default_value=(1,1,1,1);glass.inputs['Roughness'].default_value=.025;glass.inputs['IOR'].default_value=1.376
        transparent=nt.nodes.new('ShaderNodeBsdfTransparent');transparent.name='Keeper eye repair • shadow transmission'
        rays=nt.nodes.new('ShaderNodeLightPath');rays.name='Keeper eye repair • ray selection'
        mix=nt.nodes.new('ShaderNodeMixShader');mix.name='Keeper eye repair • cornea surface'
        nt.links.new(rays.outputs['Is Shadow Ray'],mix.inputs[0]);nt.links.new(glass.outputs[0],mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2])
        out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');nt.links.new(mix.outputs[0],out.inputs['Surface'])
        report.append('eyes_shell')
    print('EYE_REPAIR',report,flush=True)
    return report

if __name__=='__main__':
    repair_eyes()
    s=bpy.context.scene
    s.frame_set(145)
    # Save the review scene with its original delivery resolution/settings.
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'observatory-eyes-fixed.blend'))
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='METAL';p.metalrt='OFF';p.kernel_optimization_level='OFF';p.get_devices()
    for d in p.devices:d.use=d.type=='METAL'
    s.cycles.device='GPU';s.render.use_persistent_data=True;s.render.use_simplify=True;s.cycles.texture_limit_render='2048'
    s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False
    s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.adaptive_threshold=.03
    folder=ROOT/'preview';folder.mkdir(exist_ok=True)
    s.render.filepath=str(folder/'eyes-fixed.png')
    start=time.time();bpy.ops.render.render(write_still=True);print('EYE_PROOF_SECONDS',round(time.time()-start,2),flush=True)
