"""NASA catalog-derived star sky with an art-directed galactic orientation.
Source/terms: docs/sky-v2.md. Does not synthesize or scatter extra stars.
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector,Matrix,Euler
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MAP=ROOT/'assets/hdri/stars/starmap_2020_8k_gal.exr'


def galactic_mapping_rotation(azimuth_deg=0,elevation_deg=25,band_tilt_deg=35):
    """World-to-texture XYZ Euler: north=+Y, east=+X, elevation above horizon.
    The galactic map center is UV(.5,.5), Blender environment direction +X.
    Positive band tilt rises to image-right when looking toward the center.
    """
    az,el,tilt=map(math.radians,(azimuth_deg,elevation_deg,band_tilt_deg))
    center=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
    right=Vector((math.cos(az),-math.sin(az),0))
    up=right.cross(center).normalized()
    y_axis=-(right*math.cos(tilt)+up*math.sin(tilt))
    z_axis=center.cross(y_axis).normalized()
    texture_to_world=Matrix((center,y_axis,z_axis)).transposed()
    return texture_to_world.transposed().to_euler('XYZ')


def build_star_world(map_path=None,azimuth_deg=0,elevation_deg=25,band_tilt_deg=35,
                     rotation_deg=None,star_strength=.85,ambient_strength=.045,
                     base_color=(.00025,.0005,.0015),ambient_color=(.16,.24,.40)):
    """Return and assign a World using unmodified NASA 8192x4096 EXR pixels.
    Camera/glossy/transmission rays see stars; diffuse rays get dim blue ambient.
    rotation_deg optionally overrides the derived Mapping Euler rotation.
    No renderer simplification or texture-resolution setting is changed here.
    """
    path=Path(map_path) if map_path else DEFAULT_MAP
    if not path.exists():raise FileNotFoundError(str(path))
    world=bpy.data.worlds.new('V2 | NASA catalog Milky Way')
    world.use_nodes=True
    nt=world.node_tree;nodes=nt.nodes;links=nt.links;nodes.clear()
    coord=nodes.new('ShaderNodeTexCoord');coord.location=(-900,200)
    mapping=nodes.new('ShaderNodeMapping');mapping.name='Milky Way orientation';mapping.label='North +Y / elevation / band tilt';mapping.vector_type='VECTOR';mapping.location=(-680,200)
    rotation=Euler(tuple(math.radians(v) for v in rotation_deg),'XYZ') if rotation_deg is not None else galactic_mapping_rotation(azimuth_deg,elevation_deg,band_tilt_deg)
    mapping.inputs['Rotation'].default_value=rotation
    links.new(coord.outputs['Generated'],mapping.inputs['Vector'])
    # World-generated coordinates are world ray directions in Blender.
    env=nodes.new('ShaderNodeTexEnvironment');env.name='NASA 2020 Galactic Stars • 8K';env.location=(-440,200);env.projection='EQUIRECTANGULAR';env.interpolation='Linear'
    env.image=bpy.data.images.load(str(path),check_existing=True)
    env.image.colorspace_settings.name='Linear Rec.709'
    links.new(mapping.outputs['Vector'],env.inputs['Vector'])
    tint=nodes.new('ShaderNodeVectorMath');tint.operation='ADD';tint.name='Dim blue sky floor';tint.location=(-210,200);tint.inputs[1].default_value=base_color;links.new(env.outputs['Color'],tint.inputs[0])
    visible=nodes.new('ShaderNodeBackground');visible.name='Visible star exposure';visible.location=(0,200);visible.inputs['Strength'].default_value=star_strength;links.new(tint.outputs['Vector'],visible.inputs['Color'])
    ambient=nodes.new('ShaderNodeBackground');ambient.name='Low diffuse ambient';ambient.location=(0,-20);ambient.inputs['Color'].default_value=(*ambient_color,1);ambient.inputs['Strength'].default_value=ambient_strength
    pathnode=nodes.new('ShaderNodeLightPath');pathnode.location=(-430,-150)
    camera_glossy=nodes.new('ShaderNodeMath');camera_glossy.operation='MAXIMUM';camera_glossy.location=(-210,-100)
    links.new(pathnode.outputs['Is Camera Ray'],camera_glossy.inputs[0]);links.new(pathnode.outputs['Is Glossy Ray'],camera_glossy.inputs[1])
    visible_rays=nodes.new('ShaderNodeMath');visible_rays.operation='MAXIMUM';visible_rays.location=(0,-190)
    links.new(camera_glossy.outputs[0],visible_rays.inputs[0]);links.new(pathnode.outputs['Is Transmission Ray'],visible_rays.inputs[1])
    mix=nodes.new('ShaderNodeMixShader');mix.location=(250,140)
    links.new(visible_rays.outputs[0],mix.inputs[0]);links.new(ambient.outputs[0],mix.inputs[1]);links.new(visible.outputs[0],mix.inputs[2])
    out=nodes.new('ShaderNodeOutputWorld');out.location=(450,140);links.new(mix.outputs[0],out.inputs['Surface'])
    world['source']='https://svs.gsfc.nasa.gov/4851/'
    world['sky_credit']='NASA/Goddard Space Flight Center Scientific Visualization Studio; Gaia DR2: ESA/Gaia/DPAC'
    world['galactic_center_azimuth_deg']=azimuth_deg;world['galactic_center_elevation_deg']=elevation_deg;world['band_tilt_deg']=band_tilt_deg
    world['texture_resolution_note']='Keep Cycles texture_limit_render at 8192 or OFF; never globally downsample this star panorama.'
    bpy.context.scene.world=world
    return world
