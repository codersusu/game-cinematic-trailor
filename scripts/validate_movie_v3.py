"""Decode the delivered movie, verify timing, and export a review contact sheet."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image,ImageOps,ImageDraw
movie=ROOT/'The Last Observatory - Celestial.mp4'
(ROOT/'previews/v3').mkdir(parents=True,exist_ok=True)
(ROOT/'renders/v3').mkdir(parents=True,exist_ok=True)
gen=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24')
meta=next(gen);w,h=meta['size'];count=0;selected={32,80,144,224,336,420,492,540};thumbs=[]
for frame in gen:
 count+=1
 if count in selected:
  im=Image.frombytes('RGB',(w,h),frame);im.thumbnail((640,360))
  tile=Image.new('RGB',(640,390),(12,14,17));tile.paste(im,(0,0))
  ImageDraw.Draw(tile).text((12,369),f'{(count-1)/24:.2f}s  /  frame {count}',fill=(200,203,206));thumbs.append(tile)
assert count==576,(count,'Expected 576 decoded frames')
assert tuple(meta['size'])==(1920,1080),meta
assert abs(meta['fps']-24)<.001,meta
assert abs(meta['duration']-24)<.1,meta
sheet=Image.new('RGB',(1280,390*4),(12,14,17))
for i,tile in enumerate(thumbs):sheet.paste(tile,((i%2)*640,(i//2)*390))
sheet.save(ROOT/'previews/v3/final-contact-sheet.jpg',quality=94)
report={'movie':movie.name,'decoded_frames':count,'metadata':meta,'technical_checks':'passed','visual_review':'contact sheet exported for inspection'}
(ROOT/'renders/v3/movie-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
