#!/usr/bin/env python3
"""One new SFX request for v2; keeps existing v1 assets untouched."""
from pathlib import Path
import argparse,json,urllib.request,urllib.error
from audio_generate import key
ROOT=Path(__file__).resolve().parents[1]
PROMPT=('Foley recording of one person in soft leather walking boots taking six slow individual '
        'heel-to-toe footsteps on a hard ancient stone floor. Each footfall is separated by quiet space, '
        'with a soft heel impact, short granular sole scuff, and natural leather movement. '
        'Close dry recording, very little reverb. Deliberate cautious walking, not running, '
        'no high heels, no stomping, no background atmosphere, no music, no voices.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--env-file',type=Path,required=True);args=p.parse_args()
 out=ROOT/'audio/v2/raw/stone_footsteps.mp3'
 if out.exists() and out.stat().st_size>1000:print('Existing footsteps reused');return
 request=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128',
  data=json.dumps({'text':PROMPT,'duration_seconds':8,'prompt_influence':.65,'model_id':'eleven_text_to_sound_v2','loop':False}).encode(),
  headers={'xi-api-key':key(args.env_file),'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=180) as response:
   data=response.read();cost=response.headers.get('character-cost')
 except urllib.error.HTTPError as e:
  print('Generation failed, HTTP',e.code);raise SystemExit(1)
 if data[:1]==b'{':raise SystemExit('Unexpected non-audio response')
 out.write_bytes(data)
 manifest={'provider':'ElevenLabs','model':'eleven_text_to_sound_v2','date':'2026-09-11',
  'file':'audio/v2/raw/stone_footsteps.mp3','prompt':PROMPT,'duration_requested_seconds':8,
  'billed_characters':cost,'bytes':len(data),'subscription_tier':'unverified',
  'source':'https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert'}
 (ROOT/'audio/v2/generation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Footsteps saved',len(data),'bytes')
if __name__=='__main__':main()
