# Ensure render settings for the eye refraction.

import bpy

# Render Settings required for Rain
eevee = bpy.context.scene.eevee
if hasattr(eevee, 'use_ssr'):
	eevee.use_ssr = True
	eevee.use_ssr_refraction = True
elif hasattr(eevee, 'use_raytracing'):
	# Blender 4.2 and beyond
	eevee.use_raytracing = True
	eevee.use_fast_gi = True
	eevee.ray_tracing_options.trace_max_roughness = 0.05