"""Explicit Meshy task operations. Credentials stay in the supplied env file.

Task responses (temporary signed download URLs) remain in renders/v3/service-tasks.
"""
import argparse, base64, json, os, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TASKS=ROOT/'renders/v3/service-tasks'
def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['submit','status','download'])
 p.add_argument('name');p.add_argument('--endpoint');p.add_argument('--payload',type=Path)
 p.add_argument('--image',type=Path);p.add_argument('--env-file',type=Path)
 p.add_argument('--field',default='model_urls.glb');p.add_argument('--output',type=Path)
 a=p.parse_args();TASKS.mkdir(parents=True,exist_ok=True);path=TASKS/(a.name+'.json')
 if a.operation=='download':
  d=json.loads(path.read_text())['response']
  for field in a.field.split('.'):d=d[field]
  a.output.parent.mkdir(parents=True,exist_ok=True)
  partial=a.output.with_name('.'+a.output.name+'.partial')
  urllib.request.urlretrieve(d,partial)
  partial.replace(a.output)
  print('DOWNLOADED',str(a.output),a.output.stat().st_size);return
 key=os.environ.get('MESHY_API_KEY')
 if a.env_file:
  key=next((l.split('=',1)[1].strip().strip('"').strip("'") for l in a.env_file.read_text().splitlines() if l.startswith('MESHY_API_KEY=')),key)
 if not key:raise SystemExit('Meshy API key unavailable')
 if a.operation=='submit':
  if path.exists():raise SystemExit('Task name already exists; retrieve its status instead')
  payload=json.loads(a.payload.read_text()) if a.payload else {}
  if a.image:payload['image_url']='data:image/png;base64,'+base64.b64encode(a.image.read_bytes()).decode()
  endpoint=a.endpoint;url='https://api.meshy.ai'+endpoint
  req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 else:
  previous=json.loads(path.read_text());endpoint=previous['endpoint'];task_id=previous['id']
  req=urllib.request.Request('https://api.meshy.ai'+endpoint+'/'+task_id,headers={'Authorization':'Bearer '+key})
 try:
  with urllib.request.urlopen(req,timeout=120) as r:response=json.load(r)
 except urllib.error.HTTPError as e:
  print('MESHY_ERROR',e.code,e.read().decode()[:1200]);raise SystemExit(1)
 if a.operation=='submit':
  result={'endpoint':endpoint,'id':response['result'],'response':response}
 else:result={**previous,'response':response}
 path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:response.get(k) for k in ('status','progress','consumed_credits','task_error') if k in response}) if a.operation=='status' else 'SUBMITTED '+a.name)
if __name__=='__main__':main()
