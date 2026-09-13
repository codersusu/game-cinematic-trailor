"""Assemble the first-person forest and single-reaction third-person room."""
from pathlib import Path
import hashlib, json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

OUT = ROOT/'previews/v12'
room_frames = list(range(37,576,2))
forest_frames = list(range(1,133))
room_source = json.loads((OUT/'room-frames/source.json').read_text())
forest_source = json.loads((OUT/'forest-frames/source.json').read_text())
for identity in (room_source,forest_source):
    assert identity['sha256']==hashlib.sha256((ROOT/identity['scene']).read_bytes()).hexdigest()
assert forest_source['view']=='first'
mapping = [('forest',f,OUT/'forest-frames'/f'{f:04d}.png') for f in forest_frames]
mapping += [('room',f,OUT/'room-frames'/f'{f:04d}.png') for f in room_frames]
assert all(path.exists() for _,_,path in mapping)
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
movie = OUT/'Forest-to-Astra-V12.mp4'
temporary = OUT/'.Forest-to-Astra-V12.partial.mp4'
writer = imageio_ffmpeg.write_frames(str(temporary),(960,604),fps=12,codec='libx264',
    pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
    output_params=['-crf','18','-movflags','+faststart'])
writer.send(None)
thumbs = []
selected = {('forest',20),('forest',35),('forest',59),('forest',132),('room',37),('room',61),('room',85),('room',125),('room',193),('room',317),('room',477),('room',575)}
rows = []
for number,(section,frame,path) in enumerate(mapping,1):
    with Image.open(path) as image:
        assert image.size==(960,540)
        canvas = Image.new('RGB',(960,604),(17,23,29))
        canvas.paste(image.convert('RGB'),(0,36))
    draw=ImageDraw.Draw(canvas)
    label='FIRST PERSON / FOREST ESCAPE' if section=='forest' else 'THIRD PERSON / ASTRA CHAMBER'
    draw.text((12,8),'V12  ·  '+label,font=font,fill=(229,237,242))
    draw.text((12,583),'Camera & performance review · same heroine / revised entrance · sound pending',font=small,fill=(180,197,205))
    writer.send(canvas.tobytes())
    rows.append({'output_frame':number,'section':section,'source_frame':frame,
                 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    if (section,frame) in selected:
        thumbs.append((section,frame,(number-1)/12,canvas.resize((384,242),Image.Resampling.LANCZOS)))
writer.close()
reader=imageio_ffmpeg.read_frames(str(temporary))
metadata=next(reader)
decoded=sum(1 for _ in reader)
assert decoded==len(mapping)==402 and metadata['size']==(960,604) and metadata['fps']==12
temporary.replace(movie)
sheet=Image.new('RGB',(1152,1068),(17,23,29));draw=ImageDraw.Draw(sheet)
for i,(section,frame,seconds,thumb) in enumerate(thumbs):
    x=(i%3)*384;y=(i//3)*267
    sheet.paste(thumb,(x,y))
    draw.text((x+8,y+246),f'{seconds:.2f}s · {section} source {frame}',font=small,fill=(190,206,215))
sheet.save(OUT/'combined-contact-sheet.jpg',quality=94)
report={'status':'encoded; visual review pending','movie':movie.name,
    'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
    'resolution':[960,604],'image_resolution':[960,540],'frames':decoded,'fps':12,
    'duration_seconds':decoded/12,'forest_to_room_cut_seconds':11,
    'forest_source':forest_source,'room_scene_sha256':room_source['sha256'],
    'room_source_range':[37,576],'first_reaction_removed':True,
    'same_heroine_in_both_scenes':True,'run_lookback_walk_entrance':True,
    'audio':'silent review','production_render':False,
    'full_decode_check':'passed','full_realtime_playback':False,
    'limitations':['Forest and room doorways have different provisional geometry.',
                  '12fps preview; final sound and production rendering pending.'],
    'frames_mapping':rows}
(OUT/'combined-movie-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(movie)
