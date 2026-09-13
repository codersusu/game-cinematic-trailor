"""Encode the inexpensive gesture rehearsal and a labeled pose strip."""
from pathlib import Path
import subprocess,json,hashlib,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
out=ROOT/'previews/v8/finger'
movie=out/'Astra-index-finger-workbench.mp4'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg,'-y','-v','error','-framerate','12','-i',str(out/'motion-frames/%04d.png'),
 '-vf','tpad=stop_mode=clone:stop_duration=1','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
frames=[1,9,17,25,31]
sheet=Image.new('RGB',(600*len(frames),540),(12,16,22));draw=ImageDraw.Draw(sheet)
for column,index in enumerate(frames):
    picture=Image.open(out/f'motion-frames/{index:04d}.png').convert('RGB')
    sheet.paste(picture,(column*600,40));draw.text((column*600+20,15),f'Frame {418+(index-1)*2}',fill='white')
sheet.save(out/'finger-motion-strip.jpg',quality=93)
stream=imageio_ffmpeg.read_frames(str(movie));meta=next(stream);count=sum(1 for _ in stream)
report={'status':'passed' if count==43 else 'failed','frames':count,'fps':meta['fps'],'size':list(meta['size']),
 'source_frames':[418,478],'source_stride':2,'playback_fps':12,'final_pose_hold_seconds':1,
 'preview_only':True,'renderer':'BLENDER_WORKBENCH','production_lighting':False,'audio':False,
 'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
 'pose_strip_source_frames':[418+(index-1)*2 for index in frames],
 'visual_review':'pending_pose_strip_inspection','full_realtime_playback':False}
(out/'motion-qa.json').write_text(json.dumps(report,indent=2)+'\n')
assert count==43
print(json.dumps(report,indent=2))
