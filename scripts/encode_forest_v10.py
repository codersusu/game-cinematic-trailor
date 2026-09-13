"""Encode and decode-verify both12second camera studies with honest draft labels."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
view=sys.argv[1];assert view in ['third','first'];folder=ROOT/'previews/v10'/view;source=json.loads((folder/'frames/source.json').read_text());frames=sorted((folder/'frames').glob('[0-9][0-9][0-9][0-9].png'));assert len(frames)==144
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
movie=folder/('Forest-Escape-'+view+'-person.mp4');writer=imageio_ffmpeg.write_frames(str(movie),(960,604),fps=12,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,output_params=['-crf','18','-movflags','+faststart']);writer.send(None);thumbs=[]
for f,p in enumerate(frames,1):
 assert p.stem==f'{f:04d}';im=Image.open(p).convert('RGB');assert im.size==(960,540);canvas=Image.new('RGB',(960,604),(19,25,31));canvas.paste(im,(0,36));d=ImageDraw.Draw(canvas);d.text((12,7),f'{view.upper()} PERSON — DENSE FOREST / ESCAPE',font=font,fill=(236,243,247));d.text((12,583),'Environment review · temporary heroine · final character and sound pending',font=small,fill=(181,199,211));writer.send(canvas.tobytes())
 if f in [20,35,55,64,96,140]:thumb=canvas.resize((384,248));thumbs.append((f,thumb))
writer.close();sheet=Image.new('RGB',(768,816),(19,25,31));d=ImageDraw.Draw(sheet)
for i,(f,im) in enumerate(thumbs):
 x=i%2*384;y=i//2*272;sheet.paste(im,(x,y));d.text((x+10,y+251),f'Frame {f} · {(f-1)/12:.2f}s',font=small,fill=(185,203,216))
sheet.save(folder/'contact-sheet.jpg',quality=94);reader=imageio_ffmpeg.read_frames(str(movie));meta=next(reader);count=sum(1 for _ in reader);assert count==144 and meta['size']==(960,604) and meta['fps']==12
qa={'view':view,'technical_checks':'passed','frames':count,'fps':12,'duration_seconds':12,'source':source,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'visual_review':'awaiting contact sheet and key-frame review','full_realtime_playback':False,'heavy_render':False};(folder/'movie-qa.json').write_text(json.dumps(qa,indent=2)+'\n');print(movie)
