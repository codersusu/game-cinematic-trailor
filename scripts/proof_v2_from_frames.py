"""Make a two-second native motion proof from final frames49–96 and synced audio."""
from pathlib import Path
import sys,subprocess,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image
from encode_v2 import CREDIT
folder=ROOT/'renders/v2/frames'
for f in range(49,97):
 with Image.open(folder/f'{f:04d}.png') as im:
  assert im.size==(1920,1080)
  im.verify()
out=ROOT/'previews/v2/Arrival-motion-1080p.mp4'
bar=round((1080-1920/2.39)/2)
filters=f'drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-framerate','24','-start_number','49','-i',str(folder/'%04d.png'),'-ss','2','-i',str(ROOT/'audio/v2/last_observatory_v2_mix.wav'),'-vf',filters,'-map','0:v:0','-map','1:a:0','-t','2','-frames:v','48','-c:v','libx264','-preset','slow','-crf','16','-c:a','aac','-b:a','256k','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-metadata',f'comment={CREDIT}','-movflags','+faststart',str(out)],check=True)
gen=imageio_ffmpeg.read_frames(str(out));meta=next(gen);count=sum(1 for _ in gen)
assert count==48 and meta['size']==(1920,1080) and meta['fps']==24
(ROOT/'previews/v2/motion-qa.json').write_text(json.dumps({'source_frames':[49,96],'decoded_frames':count,'metadata':meta,'audio_start_seconds':2,'output':str(out)},indent=2))
print(out)
