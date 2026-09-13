#!/usr/bin/env python3
"""Fetch curated Poly Haven CC0 vegetation assets and verify provider hashes."""
from pathlib import Path
import json,hashlib,urllib.request
R=Path(__file__).resolve().parent
SELECTED={'grass_bermuda_01':'blend','fir_sapling':'gltf','grass_medium_01':'blend'}
def download(asset,path,info):
 p=R/asset/path;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists() or hashlib.md5(p.read_bytes()).hexdigest()!=info['md5']:
  req=urllib.request.Request(info['url'],headers={'User-Agent':'AstraTrailerResearch/1.0'})
  b=urllib.request.urlopen(req,timeout=120).read();assert len(b)==info['size'];assert hashlib.md5(b).hexdigest()==info['md5'];p.write_bytes(b)
 return {'path':str(p.relative_to(R)),'source_url':info['url'],'bytes':p.stat().st_size,'md5':info['md5'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
if __name__=='__main__':
 rows=[]
 for asset,fmt in SELECTED.items():
  d=json.loads((R/'metadata'/(asset+'-files.json')).read_text());e=d[fmt]['2k'][fmt]
  rows.append(download(asset,e['url'].rsplit('/',1)[-1],e))
  for path,item in e.get('include',{}).items():rows.append(download(asset,path,item))
  if asset=='fir_sapling':
   for channel in d:
    if 'alpha' in channel.lower():
     e=d[channel]['2k']['png'];rows.append(download(asset,'textures/'+e['url'].rsplit('/',1)[-1],e))
  print('VERIFIED',asset,flush=True)
 catalog=json.loads((R/'metadata/candidates.json').read_text())
 report={'provider':'Poly Haven','license':'CC0-1.0','license_url':'https://polyhaven.com/license','assets':{k:{'source':'https://polyhaven.com/a/'+k,'authors':catalog[k]['authors']} for k in SELECTED},'files':rows,'total_bytes':sum(r['bytes'] for r in rows)}
 (R/'download-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
