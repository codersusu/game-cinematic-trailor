"""Encode the inexpensive choice rehearsal with consistent honest labels."""
from pathlib import Path
import sys, json, hashlib
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

option = sys.argv[1] if len(sys.argv) > 1 else ''
titles = {'a': 'A — BOW vs FOREST GUARDIAN', 'b': 'B — SWORD vs FOREST GUARDIAN', 'c': 'C — BOW vs BEAR'}
if option not in titles: raise ValueError('Choose a, b or c')
folder = ROOT / f'previews/v8/options/{option}'
source = json.loads((folder / 'frames/source.json').read_text())
frames = sorted((folder / 'frames').glob('[0-9][0-9][0-9][0-9].png'))
assert len(frames) == 96, (len(frames), 'Expected 8 seconds at12fps')
assert [p.stem for p in frames] == [f'{f:04d}' for f in range(1,97)]
width, height = source['resolution']
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
if not Path(font_path).exists():
    font = ImageFont.load_default(size=20); small = ImageFont.load_default(size=14)
else:
    font = ImageFont.truetype(font_path, 20); small = ImageFont.truetype(font_path, 14)
movie = folder / f'Option-{option.upper()}-draft.mp4'
encoded_height = height + 64
writer = imageio_ffmpeg.write_frames(str(movie), (width,encoded_height), fps=12, codec='libx264', pix_fmt_in='rgb24', pix_fmt_out='yuv420p', macro_block_size=1, output_params=['-crf','18','-movflags','+faststart'])
writer.send(None)
thumbs=[]
for n,path in enumerate(frames,1):
    im=Image.open(path).convert('RGB'); assert im.size==(width,height)
    canvas=Image.new('RGB',(width,encoded_height),(19,25,31));canvas.paste(im,(0,36))
    draw=ImageDraw.Draw(canvas);draw.text((12,7),titles[option],font=font,fill=(235,242,247))
    draw.text((12,height+43),'Draft choreography · source stand-ins · final heroine and lighting pending',font=small,fill=(182,198,211))
    writer.send(canvas.tobytes())
    if n in [1,18,36,54,72,96]:
        thumb=canvas.copy();thumb.thumbnail((384,248));thumbs.append((n,thumb))
writer.close()
sheet=Image.new('RGB',(768,3*272),(19,25,31));d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(thumbs):
    x=(i%2)*384;y=(i//2)*272;sheet.paste(im,(x,y));d.text((x+10,y+251),f'Frame {n} · {(n-1)/12:.2f}s',font=small,fill=(184,202,215))
sheet.save(folder/'contact-sheet.jpg',quality=94)
g=imageio_ffmpeg.read_frames(str(movie));meta=next(g);count=sum(1 for _ in g)
assert count==96 and meta['size']==(width,encoded_height) and abs(meta['fps']-12)<.01
qa={'option':option,'title':titles[option],'technical_checks':'passed','frames':count,'fps':12,'seconds':8,'size':list(meta['size']),'audio':False,'source_scene':source,'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'contact_sheet_frames':[1,18,36,54,72,96],'visual_review':'exported awaiting inspection','full_realtime_playback':False,'heavy_render':False}
(folder/'movie-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print('OPTION_DRAFT_READY',str(movie))
