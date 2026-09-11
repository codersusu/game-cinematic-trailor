"""Short review of the three acting beats with matching soundtrack excerpts."""
from pathlib import Path
import subprocess, sys, json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import imageio_ffmpeg
folder=ROOT/'previews/v4/acting-frames'
assert all((folder/f'{f:04d}.png').is_file() for f in range(1,141))
output=ROOT/'previews/v4/Native-walk-and-expressions.mp4'
partial=output.with_name('.acting.partial.mp4')
filters=('[0:v]drawbox=x=0:y=0:w=iw:h=69:color=black:t=fill,'
         'drawbox=x=0:y=ih-69:w=iw:h=69:color=black:t=fill,'
         'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
         'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v];'
         '[1:a]atrim=start=0:end=1.5,asetpts=PTS-STARTPTS[a0];'
         '[1:a]atrim=start=4:end=6,asetpts=PTS-STARTPTS[a1];'
         '[1:a]atrim=start=12:end=14.333333333,asetpts=PTS-STARTPTS[a2];'
         '[a0][a1][a2]concat=n=3:v=0:a=1[a]')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-framerate','24','-i',str(folder/'%04d.png'),
 '-i',str(ROOT/'audio/v4/last_observatory_v4_mix.wav'),'-filter_complex',filters,'-map','[v]','-map','[a]',
 '-frames:v','140','-t',str(140/24),'-c:v','libx264','-crf','16','-preset','slow','-c:a','aac','-b:a','256k',
 '-movflags','+faststart',str(partial)],check=True)
partial.replace(output)
frames=imageio_ffmpeg.read_frames(str(output));metadata=next(frames);count=sum(1 for _ in frames)
assert count==140 and metadata['size']==(960,540)
(ROOT/'previews/v4/acting-proof-qa.json').write_text(json.dumps({'file':str(output.relative_to(ROOT)),'decoded_frames':count,'metadata':metadata,'segments':['surprise 1–36','native walking 97–144','wonder 289–344']},indent=2))
print(output)
