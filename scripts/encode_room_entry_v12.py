"""Export the changed entrance alone for convenient performance review."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
from PIL import Image
folder=ROOT/'previews/v12'
movie=folder/'Room-entry-run-look-back-walk.mp4'
frames=list(range(37,192,2))
writer=imageio_ffmpeg.write_frames(str(movie),(960,540),fps=12,codec='libx264',
    pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=1,
    output_params=['-crf','18','-movflags','+faststart'])
writer.send(None)
for frame in frames:
    with Image.open(folder/'room-frames'/f'{frame:04d}.png') as image:
        assert image.size==(960,540)
        writer.send(image.convert('RGB').tobytes())
writer.close()
reader=imageio_ffmpeg.read_frames(str(movie));meta=next(reader);count=sum(1 for _ in reader)
assert count==78 and meta['size']==(960,540) and meta['fps']==12
(folder/'room-entry-movie-qa.json').write_text(json.dumps({'frames':count,'fps':12,
    'duration_seconds':count/12,'source_range':[37,192],'decode_check':'passed',
    'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
    'visual_review':'Native frames45,79,101,147 inspected','full_realtime_playback':False},indent=2)+'\n')
print(movie)
