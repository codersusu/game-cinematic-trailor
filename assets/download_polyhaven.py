"""Download a small CC0 cinematic asset kit. Powered by Poly Haven."""
import json,subprocess,pathlib,hashlib,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parent
UA='LastObservatory/1.0 personal cinematic asset download'
def fetch(url,p):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists(): subprocess.run(['curl','-sS','-L','--fail','--retry','2','-A',UA,url,'-o',str(p)],check=True)
 return p
specs=[('monastery_stone_floor','texture'),('old_stone_wall_02','texture'),('rusty_metal_04','texture'),('stone_01','model'),('rock_face_01','model'),('kloofendal_overcast_puresky','hdri')]
jobs=[]; manifest=[]
for asset,kind in specs:
 meta=fetch('https://api.polyhaven.com/files/'+asset,ROOT/'metadata'/f'{asset}.json')
 data=json.loads(meta.read_text()); base=ROOT/kind/asset; chosen=[]
 if kind=='texture':
  for channel,fmt in [('Diffuse','jpg'),('Rough','jpg'),('nor_gl','exr'),('Displacement','png')]:
   if channel in data:
    f=data[channel]['2k'][fmt]; chosen.append((base/pathlib.Path(f['url']).name,f,channel))
 elif kind=='hdri':
  f=data['hdri']['2k']['exr']; chosen.append((base/pathlib.Path(f['url']).name,f,'environment'))
 else:
  f=data['gltf']['2k']['gltf']; chosen.append((base/pathlib.Path(f['url']).name,f,'model'))
  for rel,dep in f['include'].items(): chosen.append((base/rel,dep,'model dependency'))
 for p,f,channel in chosen:
  jobs.append((f['url'],p,f['md5']))
  manifest.append(dict(asset=asset,kind=kind,channel=channel,path=str(p.relative_to(ROOT.parent)),url=f['url'],md5=f['md5'],bytes=f['size'],license='CC0',source='https://polyhaven.com/a/'+asset))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(fetch,u,p):(p,md5) for u,p,md5 in jobs}
 for future in concurrent.futures.as_completed(futures):
  p,expected=futures[future]; future.result(); actual=hashlib.md5(p.read_bytes()).hexdigest()
  if actual != expected: raise RuntimeError('Checksum mismatch '+str(p))
  print(p.relative_to(ROOT),p.stat().st_size,flush=True)
(ROOT/'download-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Verified',len(jobs),'files;',sum(p.stat().st_size for _,p,_ in jobs),'bytes')
