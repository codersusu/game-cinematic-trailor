#!/usr/bin/env python3
"""Compose 'Beyond the Threshold', an original 33.5-second cinematic score.

Original notes, orchestration, dynamics and synthesis; CC0 VSCO2 instrument
recordings perform the parts. No existing music, dialogue, footsteps, surprise
stingers, service API or private project data is used. All output is audio/v13.
"""
from pathlib import Path
from fractions import Fraction
import json,hashlib,math,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/python'))
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt,fftconvolve,resample_poly
import imageio_ffmpeg
SR=48000;DURATION=33.5;COUNT=int(SR*DURATION);OUT=ROOT/'audio/v13'
RNG=np.random.default_rng(130913)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rms(audio):return float(np.sqrt(np.mean(audio*audio)))
def envelope(audio,attack=.012,release=.18):
 audio=audio.copy();a=min(len(audio),int(attack*SR));z=min(len(audio),int(release*SR))
 if a:audio[:a]*=np.sin(np.linspace(0,np.pi/2,a))[:,None]**2
 if z:audio[-z:]*=np.cos(np.linspace(0,np.pi/2,z))[:,None]**2
 return audio

def filt(audio,lo=40,hi=14000):
 audio=sosfilt(butter(2,lo,btype='highpass',fs=SR,output='sos'),audio,axis=0)
 return sosfilt(butter(2,hi,btype='lowpass',fs=SR,output='sos'),audio,axis=0)

def stereo(audio,pan,width=.65):
 mono=audio.mean(axis=1);side=(audio[:,0]-audio[:,1])*.5*width
 left=mono*math.sqrt((1-pan)/2)*math.sqrt(2)+side
 right=mono*math.sqrt((1+pan)/2)*math.sqrt(2)-side
 return np.column_stack([left,right])


def hall_ir(seconds,seed):
 rng=np.random.default_rng(seed);n=int(SR*seconds);t=np.arange(n)/SR
 result=rng.normal(size=(n,2))*np.exp(-t[:,None]*5.4/seconds)
 result=filt(result,160,5700)
 result[:int(.032*SR)]=0
 # A few broad early reflections, followed by a dense decorrelated tail.
 for delay,gain in [(.047,.9),(.079,.6),(.113,.38),(.173,.25)]:
  start=int(delay*SR);result[start:start+50]+=np.hanning(50)[:,None]*gain
 result/=np.sqrt(np.sum(result*result,axis=0))
 return result


def meter(path):
 command=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-nostdin','-i',str(path),'-af','loudnorm=I=-18:TP=-2.5:LRA=11:print_format=json','-f','null','-']
 run=subprocess.run(command,capture_output=True,text=True,check=True)
 row=json.loads(run.stderr[run.stderr.rfind('{'):run.stderr.rfind('}')+1])
 return {k:float(row[k]) for k in ['input_i','input_tp','input_lra']}


def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'stems').mkdir(exist_ok=True)
 manifest=json.loads((OUT/'sources/acquisition.json').read_text())
 bank={};sample_info=[]
 notes={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
 for row in manifest['files']:
  path=ROOT/row['file'];assert sha(path)==row['sha256']
  audio,sample_rate=sf.read(path,always_2d=True,dtype='float64');audio=audio[:,:2]
  if audio.shape[1]==1:audio=np.repeat(audio,2,axis=1)
  if sample_rate!=SR:audio=resample_poly(audio,SR//math.gcd(SR,sample_rate),sample_rate//math.gcd(SR,sample_rate),axis=0)
  instrument=row['instrument'];match=re.search(r'_([A-G]#?)(\d)(?=_|\.)',path.name)
  # VSCO wind/string files use C3=middle C, while this harp recording uses
  # scientific C4=middle C. These offsets were checked against sample spectra.
  base=None
  if match:
   base=12*(int(match.group(2))+1)+notes[match.group(1)]+(0 if instrument=='harp' else 12)
  if instrument=='timpani':base=41.45
  mono=audio.mean(axis=1);window=max(1,int(.008*SR));energy=np.convolve(abs(mono[:min(len(mono),int(.8*SR))]),np.ones(window)/window,mode='same')
  positions=np.flatnonzero(energy>max(float(np.max(energy))*.035,.00001))
  if len(positions):audio=audio[max(0,int(positions[0]) - int(.006*SR)):]
  audio=filt(audio,30 if instrument in ['bassdrum','timpani','cello_sustain'] else 60,14000 if instrument in ['cymbal','glock'] else 11000)
  peak=float(np.max(abs(audio)))
  audio/=max(peak,.001)
  bank.setdefault(instrument,[]).append({'audio':audio,'midi':base,'file':row['file']})
  sample_info.append({'file':row['file'],'instrument':instrument,'root_midi':base,'duration_after_trim_seconds':len(audio)/SR,'source_sha256':row['sha256']})
 stems={name:np.zeros((COUNT,2),dtype=np.float64) for name in ['low_strings_and_pulse','orchestral_harmony','melodic_winds','harp_and_starlight','orchestral_percussion','subtle_synth_support']}
 events=[];pitched_cache={};rr={}
 def put(stem,audio,start,gain=1):
  i=round(start*SR);end=min(COUNT,i+len(audio));begin=max(0,i)
  if end>begin:stems[stem][begin:end]+=audio[begin-i:end-i]*gain
 def play(instrument,midi,start,duration,gain,stem,pan=0,attack=.025,release=.35,variation=True):
  choices=bank[instrument]
  if midi is None:source=choices[0];semitones=0
  else:
   distance=min(abs(midi-sample['midi']) for sample in choices)
   candidates=[sample for sample in choices if abs(midi-sample['midi'])<distance+.001]
   number=rr.get(instrument,0);source=candidates[number%len(candidates)];rr[instrument]=number+1
   semitones=midi-source['midi']
  key=(source['file'],midi)
  if key not in pitched_cache:
   if abs(semitones)<.0001:pitched=source['audio']
   else:
    ratio=Fraction(2**(-semitones/12)).limit_denominator(1200)
    pitched=resample_poly(source['audio'],ratio.numerator,ratio.denominator,axis=0)
   pitched_cache[key]=pitched
  audio=pitched_cache[key];length=min(len(audio),round((duration+release)*SR));audio=audio[:length].copy()
  audio=envelope(audio,attack,release)
  if instrument in ['cello_sustain','violin_sustain','horn','flute']:
   t=np.arange(len(audio))/SR
   breath=.77+.23*np.sin(np.minimum(t/max(duration,.01),1)*np.pi*.8)
   audio*=breath[:,None]
  audio=stereo(audio,pan,.7)
  human_gain=RNG.uniform(.94,1.04) if variation else 1.
  put(stem,audio,start,gain*human_gain)
  events.append({'instrument':instrument,'midi':midi,'start_seconds':round(start,4),'duration_seconds':duration,'release_seconds':release,'gain':round(gain*human_gain,5),'pan':pan,'stem':stem,'source':source['file']})
 def chord(start,duration,notes_,gain=.07,kind='violin_sustain',stem='orchestral_harmony'):
  for j,midi in enumerate(notes_):play('cello_sustain' if kind=='violin_sustain' and midi<55 else kind,midi,start+j*.014,duration,gain,stem,pan=(-.32+j*.18),attack=.28,release=.8)
 # Forest: low bowed eighth notes, breathing brass, and irregular heavy drum
 # punctuation. The rhythm is musical and intentionally independent of feet.
 patterns=[[50,57,62,64,50,57,60,57],[46,53,58,62,46,53,60,58],[50,57,62,65,50,57,64,60],[45,52,57,58,45,52,62,58]]
 for i,start in enumerate(np.arange(.10,10.80,.3125)):
  bar=min(3,int(start/2.5));note=patterns[bar][i%8]
  emphasis=1.0 if i%4==0 else .68 if i%2==0 else .53
  energy=.66+.34*min(start/8.8,1)
  play('cello_spic',note,start+RNG.uniform(-.006,.006),.20,.092*emphasis*energy,'low_strings_and_pulse',pan=-.24,attack=.008,release=.23)
 for start,root,bassgain in [(0,38,.072),(2.5,34,.067),(5,38,.078),(7.5,33,.083),(10,38,.063)]:
  play('cello_sustain',root,start,2.30,.060,'low_strings_and_pulse',pan=.16,attack=.2,release=.5)
  play('horn',root+12,start+.03,1.72,.048,'orchestral_harmony',pan=.22,attack=.24,release=.65)
 for start,gain in [(.08,.19),(2.55,.17),(4.42,.10),(5.03,.20),(6.90,.12),(7.54,.20),(8.78,.11),(9.40,.09),(10.06,.15)]:
  play('bassdrum',None,start,1.8,gain,'orchestral_percussion',pan=.02,attack=.002,release=.5)
 for start,note,gain in [(1.36,38,.073),(3.80,41,.065),(5.97,38,.067),(7.08,45,.08),(8.20,45,.074),(9.73,38,.085)]:
  play('timpani',note,start,1.15,gain,'orchestral_percussion',pan=.28,attack=.003,release=.5)
 # One restrained repeating upper figure gives the tension an identifiable motif.
 for start,note,length,gain in [(1.0,62,1.,.039),(2.10,65,.7,.032),(4.0,64,1.3,.036),(6.15,62,.8,.042),(7.1,65,1.,.047),(9.0,61,1.2,.048)]:
  play('violin_sustain',note,start,length,gain,'orchestral_harmony',pan=-.3,attack=.20,release=.5)
 # Suspended cymbal swell leads into the11-second doorway cut; it is a score
 # transition, not a reused impact or sound-effect asset.
 cymbal=bank['cymbal'][0]['audio'];reverse=envelope(cymbal[:int(2.15*SR)][::-1],.8,.13)
 put('orchestral_percussion',stereo(reverse,.1,.85),8.78,.027)
 # Quiet vigilance: thinner orchestration, held open fifth, spaced plucked notes.
 chord(11.02,3.5,[50,57],.030,kind='cello_sustain',stem='low_strings_and_pulse')
 for start,note in [(11.24,62),(12.75,69),(14.25,64),(15.15,69),(16.0,74),(16.8,76)]:
  play('harp',note,start,1.20,.045 if start<15 else .055,'harp_and_starlight',pan=-.10,attack=.008,release=.7)
 for start,note in [(12.05,50),(13.30,57),(14.55,52),(15.80,57)]:play('cello_spic',note,start,.25,.030,'low_strings_and_pulse',pan=-.18,attack=.012,release=.35)
 chord(15.10,2.55,[57,64,69],.031)
 # Astra reveals: parallel D major opens the color, widening strings, lyrical
 # flute and a soft horn line. Harmonic rhythm and dynamics build with the shots.
 harmonic_plan=[(17.50,2.65,[50,57,62,66,76],.052),(20.0,2.95,[47,55,62,66,69],.055),(22.70,2.80,[47,54,62,66,69],.067),(25.20,2.95,[45,57,62,64,69],.062),(27.70,2.2,[50,57,64,66,73],.061),(29.30,3.05,[50,57,62,66,71,76],.070)]
 for start,dur,notes_,gain in harmonic_plan:
  play('cello_sustain',notes_[0]-12,start,dur,.061,'low_strings_and_pulse',pan=.17,attack=.25,release=.9)
  chord(start,dur,notes_[1:],gain)
  for j,note in enumerate([notes_[1]+12,notes_[2]+12,notes_[-1],notes_[-2]+12]):
   play('harp',note,start+.11+j*.23,1.5,.071 if start==29.3 else .047,'harp_and_starlight',pan=-.28+j*.13,attack=.008,release=.8)
 # A four-note idea rises with the revelation, then answers and resolves.
 melody=[(17.65,74,.72,.075),(18.49,76,.72,.078),(19.32,78,1.18,.083),(20.65,81,1.75,.081),(22.74,78,.86,.094),(23.72,76,.75,.080),(24.58,74,1.45,.078),(26.28,73,.86,.074),(27.30,76,1.5,.075),(29.33,78,.78,.084),(30.27,76,.65,.067),(31.08,74,1.22,.060)]
 for start,note,dur,gain in melody:play('flute',note,start,dur,gain,'melodic_winds',pan=.19,attack=.13,release=.35)
 for start,note,dur,gain in [(17.55,50,2.10,.048),(20.15,55,2.10,.055),(22.72,54,2.0,.060),(25.28,57,2.10,.052),(29.30,62,2.55,.052)]:
  play('horn',note,start,dur,gain,'melodic_winds',pan=-.09,attack=.34,release=.7)
 # Gentle timbral accents at the expressive reveal and finger moment.
 for start,note,gain in [(17.55,86,.022),(22.75,90,.028),(29.30,86,.063),(29.77,93,.022),(30.23,90,.020),(30.69,88,.016)]:
  play('glock',note,start,2.,gain,'harp_and_starlight',pan=.05 if note==86 else .3,attack=.004,release=.85)
 for start,gain in [(17.50,.055),(22.70,.077),(29.30,.052)]:
  play('bassdrum',None,start,1.7,gain,'orchestral_percussion',pan=0,attack=.005,release=.6)
  play('cymbal',None,start,2.7,gain*.26,'orchestral_percussion',pan=-.08,attack=.22,release=1.)
 # Quiet synthetic fundamentals support scale without replacing instrumentation.
 timeline=np.arange(COUNT)/SR
 for start,stop,midi,amp in [(0,10.8,26,.013),(11.,16.9,26,.008),(17.5,20.,26,.012),(20.,22.7,23,.011),(22.7,25.2,23,.012),(25.2,27.7,21,.011),(27.7,33.5,26,.010)]:
  t=np.arange(round((stop-start)*SR))/SR;freq=440*2**((midi-69)/12)
  sig=(np.sin(2*np.pi*freq*t)+.28*np.sin(2*np.pi*freq*2*t))[:,None]
  sig=np.repeat(sig,2,axis=1);sig=envelope(sig,.3,.75);put('subtle_synth_support',sig,start,amp)
 # Two concert-hall depths keep articulation in front and melodic atmosphere
 # behind it. Only rendered original parts feed these algorithmic reverbs.
 irs={'short':hall_ir(1.45,9131),'long':hall_ir(3.15,9132)}
 wet={'low_strings_and_pulse':(.12,'short'),'orchestral_harmony':(.23,'long'),'melodic_winds':(.21,'long'),'harp_and_starlight':(.26,'long'),'orchestral_percussion':(.13,'short'),'subtle_synth_support':(.02,'short')}
 for name,audio in stems.items():
  amount,kind=wet[name];verb=np.column_stack([fftconvolve(audio[:,ch],irs[kind][:,ch],mode='full')[:COUNT] for ch in range(2)])
  audio+=verb*amount
  # Finishing fades apply equally to all stems; the final chord is allowed to
  # ring under a long release instead of abruptly ending the last note.
  stems[name]=envelope(filt(audio,28,16500),.12,1.45)
 mix=sum(stems.values());peak=float(np.max(abs(mix)))
 # Keep the floating premaster within headroom before the transparent gain pass.
 preliminary=min(1.,.72/max(peak,1e-9));mix*=preliminary
 for name in stems:stems[name]*=preliminary
 premaster=OUT/'Beyond the Threshold - premaster.wav';sf.write(premaster,mix,SR,subtype='PCM_24')
 measured=meter(premaster);gain_db=min(-18.-measured['input_i'],-2.6-measured['input_tp']);gain=10**(gain_db/20)
 mix*=gain
 master=OUT/'forest_to_astra_music.wav';sf.write(master,mix,SR,subtype='PCM_24')
 for name,audio in stems.items():sf.write(OUT/'stems'/f'{name}.wav',audio*gain,SR,subtype='PCM_24')
 mp3=OUT/'forest_to_astra_music.mp3'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(master),'-codec:a','libmp3lame','-b:a','256k',str(mp3)],check=True)
 (OUT/'score-events.json').write_text(json.dumps({'title':'Beyond the Threshold','duration_seconds':DURATION,'seed':130913,'original_composition':True,'harmonic_plan':harmonic_plan,'events':events,'sample_map':sample_info},indent=2)+'\n')
 written,sr=sf.read(master,always_2d=True,dtype='float64');measure=meter(master)
 windows=[]
 for a,b,label in [(0,11,'forest tension'),(11,15,'doorway vigilance'),(15,17.5,'curiosity builds'),(17.5,22.7,'Astra atmosphere'),(22.7,29.3,'expressive revelation'),(29.3,33.5,'finger and resolve')]:
  block=written[round(a*SR):round(b*SR)];windows.append({'start_seconds':a,'end_seconds':b,'cue':label,'rms_dbfs':round(20*np.log10(max(rms(block),1e-12)),2)})
 checks={'exact_33_5_seconds':len(written)==COUNT,'sample_rate_48000':sr==SR,'stereo':written.shape[1]==2,'finite':bool(np.isfinite(written).all()),'no_clipped_samples':bool(np.max(abs(written))<1),'true_peak_below_minus_2_5':measure['input_tp']<=-2.5,'loudness_between_minus_20_and_minus_17':-20<=measure['input_i']<=-17,'ends_near_silence':bool(np.max(abs(written[-48:]))<.0003)}
 qa={'status':'passed' if all(checks.values()) else 'failed','title':'Beyond the Threshold','file':str(master.relative_to(ROOT)),'master_sha256':sha(master),'preview_mp3':str(mp3.relative_to(ROOT)),'preview_sha256':sha(mp3),'duration_seconds':len(written)/sr,'sample_rate_hz':sr,'channels':2,'encoding':'24-bit PCM WAV','integrated_loudness_lufs':measure['input_i'],'true_peak_dbtp':measure['input_tp'],'loudness_range_lu':measure['input_lra'],'sample_peak_dbfs':20*np.log10(float(np.max(abs(written)))),'clipped_sample_count':int(np.count_nonzero(abs(written)>=1)),'original_note_event_count':len(events),'instrument_recording_count':len(sample_info),'transparent_master_gain_db':gain_db,'checks':checks,'cue_levels':windows,'stems':list(stems),'script':'scripts/music_v13.py','script_sha256':sha(Path(__file__)),'source_manifest':'audio/v13/sources/acquisition.json','sample_license':'CC0-1.0','production_apis_used':False,'dialogue_or_vocals':False,'old_footsteps_or_surprise_cues_used':False,'perceptual_listening_performed':False}
 (OUT/'music-qa.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
 assert all(checks.values()),'Music technical QA failed'

if __name__=='__main__':main()
