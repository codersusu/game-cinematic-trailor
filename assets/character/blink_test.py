import bpy,json
from pathlib import Path
r=bpy.data.objects['RIG-einar']
p=Path(__file__).resolve().parent
report={}
for frame in [145,191,194,228,261,288]:
 bpy.context.scene.frame_set(frame)
 report[frame]={n:list(r.pose.bones[n].location) for n in ['Blink.L','Blink.R']}
 report[frame]['head']=list(r.pose.bones['FK-Head'].rotation_euler)
(p/'animation-check.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;s.frame_set(191);s.render.resolution_x=600;s.render.resolution_y=600;s.cycles.samples=16
s.render.filepath=str(p/'keeper-blink.png');bpy.ops.render.render(write_still=True)
