#!/usr/bin/env python3
"""Generate three original SFX requests. Secrets are read privately from external env."""
import argparse,json,re,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOBS=[
 ('rain_chamber',12,True,'Quiet steady rain falling through a broken dome onto ancient stone and shallow puddles inside a large abandoned observatory. Intimate detailed individual water droplets, distant soft mountain wind, spacious natural stone chamber acoustics. Consistent ambience only, no thunder, no music, no voices.'),
 ('bronze_mechanism',10,False,'An enormous ancient bronze astronomical clockwork mechanism slowly awakens: deep heavy metal groans, stone bearing rumble, deliberate ratchet ticks, large interlocking gears grinding and rotating with tremendous weight, accelerating gently then settling. Cinematic realistic mechanical sound design in a vast stone hall. No modern motors, no music, no voices.'),
 ('alignment',6,False,'One monumental bronze astronomical ring clicks firmly into alignment, followed by a deep warm resonant metallic bell tone blooming and decaying through a vast ancient stone observatory. Restrained majestic mysterious cinematic sound. Single event near the start with a long beautiful reverberant tail. No speech, no music, no explosions.')]
def key(path):
 values={}
 for line in path.read_text().splitlines():
  if '=' in line and not line.lstrip().startswith('#'):
   a,b=line.split('=',1);values[a.strip().removeprefix('export ')]=b.strip().strip('\"\'')
 for name in ('ELEVEN_LABS_API_KEY','ELEVENLABS_API_KEY','XI_API_KEY'):
  if len(values.get(name,''))>20:return values[name]
 raise SystemExit('Credential not found')
def main():
 p=argparse.ArgumentParser();p.add_argument('--env-file',type=Path,required=True);args=p.parse_args();secret=key(args.env_file)
 manifest={'provider':'ElevenLabs','model':'eleven_text_to_sound_v2','endpoint':'https://api.elevenlabs.io/v1/sound-generation','docs':'https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert','date':'2026-09-11','requests':[]}
 try:
  req=urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription',headers={'xi-api-key':secret})
  with urllib.request.urlopen(req,timeout=30) as r:
   sub=json.load(r)
  manifest['subscription_tier']=sub.get('tier','unknown')
  print('Subscription tier:',manifest['subscription_tier'])
 except Exception:manifest['subscription_tier']='unverified'
 for name,duration,loop,prompt in JOBS:
  out=ROOT/'audio/raw'/f'{name}.mp3'
  entry={'file':str(out.relative_to(ROOT)),'duration_requested_seconds':duration,'loop':loop,'prompt':prompt}
  if out.exists() and out.stat().st_size>1000:
   entry['status']='existing';manifest['requests'].append(entry);continue
  payload={'text':prompt,'duration_seconds':duration,'loop':loop,'model_id':'eleven_text_to_sound_v2','prompt_influence':0.55}
  req=urllib.request.Request(manifest['endpoint']+'?output_format=mp3_44100_128',data=json.dumps(payload).encode(),headers={'xi-api-key':secret,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=180) as r:
    data=r.read();entry['billed_characters']=r.headers.get('character-cost');entry['request_id']=r.headers.get('request-id')
   if data[:1]==b'{':raise ValueError('Unexpected JSON response')
   out.write_bytes(data);entry['status']='generated';entry['bytes']=len(data);print(name,'saved',len(data),'bytes',flush=True)
  except urllib.error.HTTPError as e:
   entry['status']='failed';entry['http_status']=e.code
   print(name,'HTTP failure',e.code,flush=True)
   manifest['requests'].append(entry);break
  manifest['requests'].append(entry)
  (ROOT/'audio/generation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (ROOT/'audio/generation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
