"""Configure this Blender session for the renderer validated on the production Mac."""
import bpy
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL'
prefs.metalrt='OFF'
prefs.kernel_optimization_level='OFF'
prefs.get_devices()
for device in prefs.devices:device.use=device.type=='METAL'
bpy.context.scene.cycles.device='GPU'
if bpy.context.screen:
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
print('Observatory: Cycles Metal configured for this session.')
