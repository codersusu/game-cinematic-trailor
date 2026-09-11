"""Selective optical bloom for stellar emission, preserving stone contrast."""
def configure_compositor(scene):
    scene.use_nodes=True
    for layer in scene.view_layers:layer.use_pass_emit=True
    nt=scene.node_tree;nt.nodes.clear()
    render=nt.nodes.new('CompositorNodeRLayers')
    subtle=nt.nodes.new('CompositorNodeGlare');subtle.name='Restrained optical highlights'
    subtle.glare_type='FOG_GLOW';subtle.quality='HIGH';subtle.threshold=2;subtle.mix=-.87
    bloom=nt.nodes.new('CompositorNodeGlare');bloom.name='Stellar emission halo'
    bloom.glare_type='FOG_GLOW';bloom.quality='HIGH';bloom.threshold=.6;bloom.size=8;bloom.mix=1
    add=nt.nodes.new('CompositorNodeMixRGB');add.name='Add stellar halo';add.blend_type='ADD';add.inputs[0].default_value=.5
    output=nt.nodes.new('CompositorNodeComposite')
    nt.links.new(render.outputs['Image'],subtle.inputs['Image'])
    nt.links.new(render.outputs['Emit'],bloom.inputs['Image'])
    nt.links.new(subtle.outputs['Image'],add.inputs[1]);nt.links.new(bloom.outputs['Image'],add.inputs[2])
    nt.links.new(add.outputs['Image'],output.inputs['Image'])
