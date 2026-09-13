import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;scene.render.resolution_percentage=50;scene.cycles.samples=24;scene.cycles.adaptive_threshold=.05
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.metalrt='OFF';prefs.kernel_optimization_level='OFF';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU'
mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys)
keys=mesh.data.shape_keys.key_blocks
for frame,name,values in [(15,'expressive-surprise',{'AK_03_BrowInnerUp':.55,'AK_21_EyeWideLeft':.32,'AK_22_EyeWideRight':.31,'AK_25_JawOpen':.28}),(317,'expressive-wonder',{'AK_03_BrowInnerUp':.36,'AK_21_EyeWideLeft':.25,'AK_22_EyeWideRight':.24,'AK_25_JawOpen':.42,'AK_32_MouthFunnel':.55,'AK_38_MouthPucker':.20}),(331,'expressive-delight',{'AK_44_MouthSmileLeft':.52,'AK_45_MouthSmileRight':.46,'AK_07_CheekSquintLeft':.12,'AK_08_CheekSquintRight':.12})]:
 scene.frame_set(frame)
 for k,v in values.items():
  keys[k].value=v;keys[k].keyframe_insert("value",frame=frame)
 scene.render.filepath=str(ROOT/'previews/v4'/f'{name}.png');bpy.ops.render.render(write_still=True)
