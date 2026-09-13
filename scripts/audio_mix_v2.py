#!/usr/bin/env python3
"""Version 2: synchronized walking/arrival, continuous rings, retained original score.

Writes only audio/v2/. Existing v1 sources/stems are read without modification.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,wave
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import numpy as np
from scipy.signal import find_peaks
from audio_mix import read_wav,write_wav,fade,level,filter_fft,rms,SR,N,DURATION
OUT=ROOT/'audio/v2'
RNG=np.random.default_rng(90337)

def place(canvas,clip,start):
    i=round(start*SR);a=max(0,i);b=min(N,i+len(clip))
    if b>a:canvas[a:b]+=clip[a-i:b-i]

def room_response(x,amount=.16):
    # Sparse early stone reflections followed by a diffuse, spectrally dark tail.
    y=x.copy()
    for delay,gain in [(.041,.19),(.087,.14),(.139,.11),(.213,.08),(.331,.055),(.479,.038)]:
        samples=round(delay*SR)
        y[samples:,0]+=x[:-samples,1]*gain*amount
        y[samples:,1]+=x[:-samples,0]*gain*amount
    length=round(SR*1.7);t=np.arange(length)/SR
    ir=RNG.normal(size=(length,2))*np.exp(-t[:,None]*3.7)
    ir=filter_fft(ir,180,3500);ir[:round(.055*SR)]=0
    ir/=np.sqrt(np.sum(ir*ir,axis=0))
    nfft=1<<(len(x)+length-1).bit_length()
    late=np.fft.irfft(np.fft.rfft(x,n=nfft,axis=0)*np.fft.rfft(ir,n=nfft,axis=0),n=nfft,axis=0)[:len(x)]
    return y+late*amount

def samples_from_recording(x):
    block=480
    envelope=np.sqrt(np.mean(x[:len(x)//block*block].reshape(-1,block,2)**2,axis=(1,2)))
    envelope=np.convolve(envelope,[.2,.6,.2],'same')
    peaks,_=find_peaks(envelope,distance=70,prominence=max(.0015,float(envelope.max())*.14))
    if len(peaks)<3:raise RuntimeError('Footstep recording has too few clear individual events')
    clips=[];details=[]
    for peak in peaks:
        center=int(peak*block)
        lo=max(0,center-round(.23*SR));hi=min(len(x),center+round(.44*SR))
        clip=x[lo:hi].copy()
        # Find the first meaningful heel transient, preserving the heel-to-toe shape.
        amp=np.max(np.abs(clip),axis=1)
        detected=np.flatnonzero(amp>max(.0007,float(np.max(amp))*.14))
        onset=max(0,int(detected[0])-round(.005*SR)) if len(detected) else 0
        clip=fade(clip[onset:],.003,.14)
        clip=filter_fft(clip,75,7200)
        clip=level(clip,.035)
        if np.max(np.abs(clip))>.25:clip*=.25/np.max(np.abs(clip))
        clips.append(clip)
        details.append({'source_peak_seconds':round(center/SR,3),'source_start_seconds':round((lo+onset)/SR,3),'duration_seconds':round(len(clip)/SR,3)})
    return clips,details

def continuous_gears(source,start,end):
    # Reuse the active region at two complementary speeds, with long overlapping fades.
    core=source[round(.5*SR):round(4.5*SR)]
    gears=np.zeros((N,2))
    for layer,(stretch,offset,weight) in enumerate([(1.38,0,.75),(1.83,-1.1,.25)]):
        length=round(len(core)*stretch)
        clip=np.column_stack([np.interp(np.linspace(0,len(core)-1,length),np.arange(len(core)),core[:,ch]) for ch in range(2)])
        clip=fade(clip,1.15,1.15)
        step=len(clip)/SR-1.7
        for k in range(-1,8):place(gears,clip*weight,start+offset+k*step)
    t=np.arange(N)/SR
    env=np.interp(t,[0,.8,5,8,12,18.4,20,21.0,23,24],[.18,.27,.39,.55,.75,1,.65,.40,.32,0])
    gears=level(filter_fft(gears,42,5500),.052)*env[:,None]
    return gears

def meter(ff,path):
    p=subprocess.run([ff,'-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-1.8:LRA=10:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default=str(ROOT/'tools/python/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'))
    p.add_argument('--sync',type=Path,default=OUT/'walk_sync.json');args=p.parse_args()
    sync=json.loads(args.sync.read_text())
    events=sync['foot_contacts'];arrival=sync['doorway_crossing_seconds']
    for folder in [OUT,OUT/'raw',OUT/'stems',OUT/'footstep_variants']:folder.mkdir(exist_ok=True,parents=True)
    footpath=OUT/'raw/stone_footsteps.wav'
    if not footpath.exists():
        subprocess.run([args.ffmpeg,'-v','error','-y','-i',str(OUT/'raw/stone_footsteps.mp3'),'-ar',str(SR),'-ac','2','-c:a','pcm_s16le',str(footpath)],check=True)
    footclips,footdetails=samples_from_recording(read_wav(footpath))
    for i,clip in enumerate(footclips):write_wav(OUT/'footstep_variants'/f'stone_step_{i+1:02d}.wav',clip)
    t=np.arange(N)/SR
    score=read_wav(ROOT/'audio/stems/original_underscore.wav')*3.0
    alignment=read_wav(ROOT/'audio/stems/alignment.wav')*2.65
    anticipation=read_wav(ROOT/'audio/stems/anticipation.wav')*2.45
    oldamb=read_wav(ROOT/'audio/stems/ambience.wav')
    # Tame isolated droplet spikes and reduce weather prominence for the starry v2 setting.
    ambience=level(np.tanh(oldamb/.045)*.045,.017)
    ambience*=np.interp(t,[0,arrival,arrival+1,12,20,24],[.85,.85,1,.75,.50,0])[:,None]
    mechanism=continuous_gears(read_wav(ROOT/'audio/raw/bronze_mechanism.wav'),sync.get('mechanism_start_seconds',0),24)
    footsteps=np.zeros((N,2));eventlog=[]
    for i,event in enumerate(events):
        timestamp=float(event['time_seconds']);foot=event.get('foot','left' if i%2==0 else 'right')
        if timestamp<.12:continue # The first visible support foot is already planted.
        clip=footclips[i%len(footclips)].copy()
        # Very small deterministic timbral variation prevents repeated-sample cadence.
        speed=RNG.uniform(.97,1.035);length=round(len(clip)/speed)
        clip=np.column_stack([np.interp(np.linspace(0,len(clip)-1,length),np.arange(len(clip)),clip[:,ch]) for ch in range(2)])
        clip*=RNG.uniform(.88,1.04)
        pan=(-.09 if foot=='left' else .09)+np.interp(timestamp,[0,12],[-.10,.08])
        mono=np.mean(clip,axis=1)
        clip=np.column_stack([mono*np.sqrt((1-pan)/2),mono*np.sqrt((1+pan)/2)])*1.45
        # Slight distance attenuation after entry; still audible beneath the score.
        clip*=np.interp(timestamp,[0,arrival,12],[1,.95,.82])
        place(footsteps,clip,timestamp)
        eventlog.append({'time_seconds':timestamp,'frame':event.get('frame'),'foot':foot,'variant':i%len(footclips)+1})
    footsteps=room_response(footsteps,.28)
    # Doorway arrival is a quiet change of air/room scale, not an unsupported door slam.
    air=filter_fft(RNG.normal(size=(N,2)),150,1700)
    envelope=np.exp(-((t-arrival)/.62)**2)
    doorway=level(air,.010)*envelope[:,None]
    doorway=room_response(doorway,.45)
    # Sparse upper partials support the fantastic sky; entirely original synthesis.
    sky=np.zeros((N,2))
    for start,freq,amplitude in [(7.7,587.33,.007),(12.7,880,.006),(17.2,1174.66,.004)]:
        tt=np.maximum(t-start,0);e=(1-np.exp(-tt/.75))*np.exp(-tt/3.7);e[t<start]=0
        sky+=np.column_stack([np.sin(2*np.pi*freq*t),np.sin(2*np.pi*(freq+.19)*t)])*e[:,None]*amplitude
    sky=room_response(sky,.36)
    layers={'ambience':ambience,'original_underscore':score,'continuous_mechanism':mechanism,'footsteps':footsteps,'doorway_arrival':doorway,'sky_harmonics':sky,'alignment':alignment,'anticipation':anticipation}
    mix=fade(filter_fft(sum(layers.values()),28,17000),.45,1.1)
    gain=min(1,.78/max(float(np.max(np.abs(mix))),1e-8))
    for name,x in layers.items():write_wav(OUT/'stems'/f'{name}.wav',x*gain)
    premaster=OUT/'last_observatory_v2_premaster.wav';final=OUT/'last_observatory_v2_mix.wav'
    write_wav(premaster,mix*gain)
    subprocess.run([args.ffmpeg,'-v','error','-y','-i',str(premaster),'-af','loudnorm=I=-18:TP=-1.8:LRA=10','-ar',str(SR),'-c:a','pcm_s16le',str(final)],check=True)
    measured=meter(args.ffmpeg,final);finished=read_wav(final)
    # Correct the short-program loudness offset with a final linear trim.
    trim=10**((-18.0-float(measured['input_i']))/20)
    trim=min(trim,.88/max(float(np.max(np.abs(finished))),1e-9))
    write_wav(final,finished*trim)
    measured=meter(args.ffmpeg,final);finished=read_wav(final)
    sources=[ROOT/'audio/stems'/f'{name}.wav' for name in ['original_underscore','alignment','anticipation','ambience']]+[ROOT/'audio/raw/bronze_mechanism.wav',footpath]
    qa={'version':2,'duration_seconds':len(finished)/SR,'sample_rate':SR,'channels':2,'encoding':'16-bit PCM WAV',
        'loudness_integrated_lufs':float(measured['input_i']),'true_peak_dbtp':float(measured['input_tp']),'loudness_range_lu':float(measured['input_lra']),
        'clipped_samples':int(np.sum(np.abs(finished)>=1)),'finite_values':bool(np.isfinite(finished).all()),
        'footstep_count':len(eventlog),'footstep_events':eventlog,'doorway_crossing_seconds':arrival,'alignment_seconds':20,
        'sync_status':sync.get('status','unverified'),'sync_source':str(args.sync.relative_to(ROOT)) if args.sync.is_relative_to(ROOT) else args.sync.name,
        'step_extraction':footdetails,'stems':list(layers),'sources':[{'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in sources],
        'license':'Reused and newly generated ElevenLabs SFX follow the account plan; tier unverified. Original synthesized layers created for this project. Not CC0.'}
    (OUT/'mix_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    print(json.dumps({k:qa[k] for k in ['duration_seconds','loudness_integrated_lufs','true_peak_dbtp','clipped_samples','footstep_count','sync_status']},indent=2))
if __name__=='__main__':main()
