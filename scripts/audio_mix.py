#!/usr/bin/env python3
"""Deterministic original underscore plus generated SFX; produces 24-second PCM stems."""
from pathlib import Path
import argparse,json,math,subprocess,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SR=48000; DURATION=24; N=SR*DURATION
RNG=np.random.default_rng(80241)

def read_wav(path):
 with wave.open(str(path),'rb') as w:
  assert w.getsampwidth()==2 and w.getframerate()==SR
  x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float64)/32768
  return x.reshape(-1,w.getnchannels())
def write_wav(path,x):
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
def fade(x,fi=.2,fo=.4):
 x=x.copy();a=min(int(fi*SR),len(x));b=min(int(fo*SR),len(x))
 if a:x[:a]*=np.sin(np.linspace(0,np.pi/2,a))[:,None]**2
 if b:x[-b:]*=np.cos(np.linspace(0,np.pi/2,b))[:,None]**2
 return x

def rms(x):return float(np.sqrt(np.mean(x*x)))
def level(x,target):return x*target/max(rms(x),1e-7)
def at(x,start):
 y=np.zeros((N,2));i=int(start*SR);count=min(len(x),N-i);y[i:i+count]+=x[:count];return y

def filter_fft(x,low,high):
 f=np.fft.rfftfreq(len(x),1/SR);gain=1/(1+(low/np.maximum(f,.01))**6)/(1+(f/high)**6)
 return np.fft.irfft(np.fft.rfft(x,axis=0)*gain[:,None],n=len(x),axis=0)

def reverb(x,wet=.25,seconds=3):
 L=int(SR*seconds);t=np.arange(L)/SR;h=RNG.normal(size=(L,2))*np.exp(-t[:,None]*3.8/seconds)
 h=filter_fft(h,90,4200);h[:int(.027*SR)]=0;h/=np.sqrt(np.sum(h*h,axis=0));nfft=1<<(len(x)+L-1).bit_length()
 tail=np.fft.irfft(np.fft.rfft(x,n=nfft,axis=0)*np.fft.rfft(h,n=nfft,axis=0),n=nfft,axis=0)[:len(x)]
 return x+tail*wet

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ffmpeg',required=True);args=parser.parse_args()
 for name in ('rain_chamber','bronze_mechanism','alignment'):
  subprocess.run([args.ffmpeg,'-v','error','-y','-i',str(ROOT/'audio/raw'/f'{name}.mp3'),'-ar',str(SR),'-ac','2','-c:a','pcm_s16le',str(ROOT/'audio/raw'/f'{name}.wav')],check=True)
 rain=read_wav(ROOT/'audio/raw/rain_chamber.wav');mech=read_wav(ROOT/'audio/raw/bronze_mechanism.wav');align=read_wav(ROOT/'audio/raw/alignment.wav')
 # Seamless repeating ambience, with a 0.5-second equal-gain overlap.
 step=len(rain)-int(.5*SR);amb=np.zeros((N,2))
 for i in range(-step,N,step):
  r=fade(rain,.5,.5);a=max(i,0);b=min(i+len(r),N)
  if b>a:amb[a:b]+=r[a-i:b-i]
 amb=level(filter_fft(amb,60,8500),.027)
 t=np.arange(N)/SR
 amb*=np.interp(t,[0,5,7,17,20,23,24],[1.25,1.15,.8,.7,.55,.45,0])[:,None]
 # A restrained, original D-based harmonic texture: no sampled music or melody.
 score=np.zeros((N,2));env=np.interp(t,[0,2.7,6,12,17.5,19.8,20,24],[0,0,.15,.5,.85,1,.45,0])
 for frequency,amp in [(36.708,.55),(73.416,.32),(110,.18),(146.832,.12),(220,.08),(293.665,.045)]:
  for ch,detune in [(0,-.035),(1,.035)]:
   phase=2*np.pi*(frequency+detune)*t+.004*np.sin(2*np.pi*.13*t)
   score[:,ch]+=amp*np.sin(phase)*(1+.12*np.sin(2*np.pi*.19*t+ch))
 score=level(score,.065)*env[:,None]
 # Airy bowed harmonics breathe in at the reveal; a slight beating adds life.
 for start,freq,amp in [(7,293.665,.014),(12,440,.017),(16,587.33,.014)]:
  tt=np.maximum(t-start,0);e=(1-np.exp(-tt/2))*np.exp(-tt/11);e[t<start]=0
  score+=np.column_stack([np.sin(2*np.pi*freq*t),np.sin(2*np.pi*(freq+.22)*t)])*e[:,None]*amp
 score=reverb(score,.2,3.5);score=fade(score,3,2)
 # The generated mechanism has a long quiet tail: stretch active motion to the shot.
 mech=mech[:int(5.5*SR)]
 mech=np.column_stack([np.interp(np.linspace(0,len(mech)-1,int(8.8*SR)),np.arange(len(mech)),mech[:,ch]) for ch in range(2)])
 mechanism=at(fade(level(mech,.065),.6,1.3),10.8)
 # Locate the audible alignment event rather than trusting generated leading silence.
 energy=np.max(np.abs(align),axis=1);first=np.flatnonzero(energy>.12)[0]
 align=align[max(0,first-int(.01*SR)):]
 impact=at(fade(level(align,.075),.003,1.3),20)
 # Original quiet anticipatory air swell, terminating exactly at the alignment.
 swell=RNG.normal(size=(N,2));swell=filter_fft(swell,220,1900)
 se=np.clip((t-17.4)/2.6,0,1)**2;se[t>=20]=0
 swell=level(swell,.032)*se[:,None];swell=fade(swell,0,.1)
 # Subsonic-style cinematic hit kept above 30 Hz, giving a sense of scale.
 ht=np.maximum(t-20,0);hit=np.sin(2*np.pi*(42*ht+13*(1-np.exp(-ht*5))/5))*np.exp(-ht*1.35)*(1-np.exp(-ht*60))
 hit[t<20]=0;impact+=hit[:,None]*.12
 layers={'ambience':amb,'original_underscore':score,'mechanism':mechanism,'alignment':impact,'anticipation':swell}
 mix=sum(layers.values());mix=filter_fft(mix,27,18000);mix=fade(mix,.5,1.2)
 # Gentle saturation only catches outlying transients; shared gain preserves stems.
 peak=float(np.max(np.abs(mix)));gain=min(1.35,.83/max(peak,1e-9));mix*=gain
 for name,x in layers.items():write_wav(ROOT/'audio/stems'/f'{name}.wav',x*gain)
 write_wav(ROOT/'audio/last_observatory_premaster.wav',mix)
 mastering=subprocess.run([args.ffmpeg,'-hide_banner','-y','-i',str(ROOT/'audio/last_observatory_premaster.wav'),'-af','loudnorm=I=-18:TP=-1.8:LRA=11:print_format=json','-ar',str(SR),'-c:a','pcm_s16le',str(ROOT/'audio/last_observatory_mix.wav')],check=True,capture_output=True,text=True)
 meter=json.loads(mastering.stderr[mastering.stderr.rfind('{'):mastering.stderr.rfind('}')+1])
 mix=read_wav(ROOT/'audio/last_observatory_mix.wav')
 verify=subprocess.run([args.ffmpeg,'-hide_banner','-i',str(ROOT/'audio/last_observatory_mix.wav'),'-af','loudnorm=I=-18:TP=-1.8:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
 meter=json.loads(verify.stderr[verify.stderr.rfind('{'):verify.stderr.rfind('}')+1])
 qa={'duration_seconds':DURATION,'sample_rate':SR,'channels':2,'encoding':'PCM signed 16-bit','sample_peak_dbfs':round(20*np.log10(np.max(np.abs(mix))),2),'rms_dbfs':round(20*np.log10(rms(mix)),2),'clipped_samples':int(np.sum(np.abs(mix)>=1)),'loudness_integrated_lufs':float(meter['input_i']),'true_peak_dbtp':float(meter['input_tp']),'loudness_range_lu':float(meter['input_lra']),'original_score_seed':80241,'alignment_seconds':20,'stems':list(layers),'license_status':'ElevenLabs subscription lookup returned HTTP 401, though sound generation succeeded; tier unverified; generated SFX usage follows account plan. Original synthesized underscore and anticipation are made for this project.'}
 (ROOT/'audio/mix_qa.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
if __name__=='__main__':main()
