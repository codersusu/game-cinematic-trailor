"""Encode the native1080p film with its new original instrumental score."""
from pathlib import Path
import hashlib,json,sys,subprocess,wave
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont

OUT=ROOT/'previews/v13'
room=json.loads((OUT/'room-frames/source.json').read_text())
forest=json.loads((OUT/'forest-frames/source.json').read_text())
for identity in (room,forest):
    assert identity['resolution']==[1920,1080]
    assert hashlib.sha256((ROOT/identity['scene']).read_bytes()).hexdigest()==identity['sha256']
assert forest['view']=='first'
mapping=[('forest',f,OUT/'forest-frames'/f'{f:04d}.png') for f in range(10,133)]
mapping += [('room',f,OUT/'room-frames'/f'{f:04d}.png') for f in range(37,576,2)]
assert len(mapping)==393 and all(path.exists() for _,_,path in mapping)
music=ROOT/'audio/v13/forest_to_astra_music_final.wav'
assert music.exists()
with wave.open(str(music),'rb') as audio:
    assert audio.getnchannels()==2 and audio.getframerate()==48000
    assert audio.getnframes()==1572000, 'Music must match the32.75-second final edit'
silent=OUT/'.Forest-to-Astra-V13.video-only.mp4'
movie=OUT/'Forest-to-Astra-V13-1080p.mp4'
partial=OUT/'.Forest-to-Astra-V13-1080p.partial.mp4'
writer=imageio_ffmpeg.write_frames(str(silent),(1920,1080),fps=12,codec='libx264',
    pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
    output_params=['-crf','17','-movflags','+faststart'])
writer.send(None);rows=[];thumbs=[]
selected={('forest',20),('forest',31),('forest',35),('forest',59),('forest',132),
          ('room',45),('room',79),('room',147),('room',193),('room',317),('room',477),('room',575)}
for number,(section,frame,path) in enumerate(mapping,1):
    with Image.open(path) as image:
        assert image.size==(1920,1080),'Only genuine1080p frames are accepted'
        rgb=image.convert('RGB');writer.send(rgb.tobytes())
        if (section,frame) in selected:thumbs.append((section,frame,(number-1)/12,rgb.resize((480,270),Image.Resampling.LANCZOS)))
    rows.append({'output_frame':number,'section':section,'source_frame':frame,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
writer.close()
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(music),
    '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000',
    '-t','32.75','-movflags','+faststart','-metadata','title=The Last Observatory — Forest to Astra',
    '-metadata','comment=Original score; see accompanying V13 credits and source manifests.',str(partial)],check=True)
reader=imageio_ffmpeg.read_frames(str(partial));meta=next(reader);count=sum(1 for _ in reader)
assert count==393 and meta['size']==(1920,1080) and meta['fps']==12
subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(partial),'-map','0:a:0','-f','null','-'],check=True)
partial.replace(movie)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
sheet=Image.new('RGB',(1440,1200),(17,23,29));draw=ImageDraw.Draw(sheet)
for i,(section,frame,seconds,thumbnail) in enumerate(thumbs):
    x=(i%3)*480;y=(i//3)*300;sheet.paste(thumbnail,(x,y))
    draw.text((x+10,y+276),f'{seconds:.2f}s · {section} {frame}',font=font,fill=(200,213,220))
sheet.save(OUT/'combined-contact-sheet.jpg',quality=95)
qa={'status':'encoded; representative visual review pending','movie':movie.name,
    'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'resolution':[1920,1080],
    'native_render_resolution':True,'frames':393,'fps':12,'duration_seconds':32.75,
    'opening_edit':'Omit inherited obstructed idle frames1..9; start on clean bow raise10',
    'video_decode':'passed','audio_decode':'passed','forest_source':forest,'room_source':room,
    'music':str(music.relative_to(ROOT)),'music_sha256':hashlib.sha256(music.read_bytes()).hexdigest(),
    'music_codec':'AAC320kbps stereo48kHz','review_bands_removed':True,
    'full_realtime_playback':False,'frames_mapping':rows}
(OUT/'combined-movie-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print(movie)
