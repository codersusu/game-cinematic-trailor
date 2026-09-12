"""Record the final V5 outputs and source checksums after movie and audio QA."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, statistics
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'renders/v5'
def load(path): return json.loads((ROOT/path).read_text())
def item(path):
 p=ROOT/path
 return {'file':str(path),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
movie=load('renders/v5/movie-qa.json')
assert movie['technical_checks']=='passed' and movie['decoded_frames']==576
scene=load('docs/submission-assets-v5.json');assert scene['status']=='passed'
preservation=load('renders/v5/preservation-audit.json');assert preservation['status']=='passed'
source=load('renders/v5/frame-source.json');assert source['scene_sha256']==scene['sha256']==item('observatory-v5.blend')['sha256']
previous=load('renders/v5/previous-versions.json')
for name,record in previous.items():
 assert item(name)['sha256']==record['sha256'],f'Previous version changed: {name}'
artifacts=['The Last Observatory - Astra Chamber.mp4','observatory-v5.blend','renders/v5/hero-4k.png','previews/v5/Astra-Chamber-motion-proof.mp4','audio/v5/last_observatory_v5_mix.wav','previews/v5/final-contact-sheet.jpg']
inputs=['observatory-v4.blend','assets/v5/models/service-modules.blend']+sorted({im['path'] for im in scene['images'] if im['path']})
scripts=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*v5*') if p.is_file())
log=(OUT/'final-render.log').read_text(errors='replace')
durations=[float(t) for _,t in re.findall(r'FRAME_DONE (\d+) ([\d.]+)',log)]
frames=sorted((OUT/'frames').glob('[0-9][0-9][0-9][0-9].png'))
assert len(frames)==576
report={'version':5,'title':'The Last Observatory — Astra Chamber','recorded_utc':datetime.now(timezone.utc).isoformat(),
 'movie':{'resolution':[1920,1080],'fps':24,'frames':576,'seconds':24,'active_aspect_ratio':2.39,'render_engine':'Blender 4.5.13 LTS / Cycles','samples_max':64,'adaptive_threshold':.025,'denoised':True,'motion_blur_shutter':.4,'metalrt':'OFF','kernel_optimization':'OFF'},
 'hero_still':{'resolution':[3840,2160],'frame':420,'samples_max':128,'adaptive_threshold':.015},
 'artifacts':[item(p) for p in artifacts],'build_inputs':[item(p) for p in inputs], 'scripts':[item(p) for p in scripts],
 'frame_set':{'count':len(frames),'aggregate_sha256':hashlib.sha256(''.join(p.name+':'+hashlib.sha256(p.read_bytes()).hexdigest()+'\n' for p in frames).encode()).hexdigest()},
 'render_timing':{'recorded_frames':len(durations),'total_frame_render_seconds':round(sum(durations),2),'median_seconds_per_frame':round(statistics.median(durations),2)},
 'qa':{'movie':'renders/v5/movie-qa.json','preservation':'renders/v5/preservation-audit.json','portable_rebuild':'renders/v5/rebuild-qa.json','motion_proof':'previews/v5/acting-proof-qa.json','audio':'audio/v5/final-aac-qa.json'},
 'previous_versions_unchanged':True,'new_paid_api_requests':0,
 'limitations':['Pre-rendered cinematic; no interactive gameplay','Accepted Rocketbox character is an older game asset','Secondary service panel relief uses mapped detail; vent grille source is low resolution','4K output is a separate still; film is native 1080p']}
audio=load('audio/v5/final-aac-qa.json')
assert audio['technical_checks']=='passed' and audio['movie_sha256']==report['artifacts'][0]['sha256']
report['encoded_audio']=audio
(OUT/'render-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('V5_MANIFEST_READY',report['artifacts'][0]['sha256'])
