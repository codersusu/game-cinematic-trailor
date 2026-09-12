#!/usr/bin/env python3
"""Version 5: modern observatory airlock, instrument hum and muted deck footfalls.

Writes only audio/v5/. Existing v1/v2 recordings are read without modification.
No generated dialogue or new paid service requests are used.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,wave
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import numpy as np
import imageio_ffmpeg
from scipy.signal import find_peaks
from audio_mix import read_wav,write_wav,fade,level,filter_fft,rms,SR,N,DURATION
OUT=ROOT/'audio/v5'
RNG=np.random.default_rng(90337)

def place(canvas,clip,start):
    i=round(start*SR);a=max(0,i);b=min(N,i+len(clip))
    if b>a:canvas[a:b]+=clip[a-i:b-i]

def room_response(x,amount=.16):
    # Short, damped instrument-room reflections; no long stone-chamber echo.
    y=x.copy()
    for delay,gain in [(.023,.13),(.048,.09),(.091,.055),(.153,.03)]:
        samples=round(delay*SR)
        y[samples:,0]+=x[:-samples,1]*gain*amount
        y[samples:,1]+=x[:-samples,0]*gain*amount
    length=round(SR*.65);t=np.arange(length)/SR
    ir=RNG.normal(size=(length,2))*np.exp(-t[:,None]*7.0)
    ir=filter_fft(ir,180,2400);ir[:round(.055*SR)]=0
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

def muted_deck_contact(clip,index):
    # Keep real heel/toe timing but suppress grit, then add damped metal-panel modes.
    t=np.arange(len(clip))/SR
    body=filter_fft(clip,65,1350)
    body*=np.exp(-t[:,None]/.24)
    body=level(body,.019)
    resonant=np.zeros(len(clip))
    for freq,gain,decay in [(143,.011,.095),(237,.006,.066),(389,.003,.043)]:
        resonant+=gain*np.sin(2*np.pi*freq*(1+.007*index)*t)*np.exp(-t/decay)*(1-np.exp(-t/.0018))
    rubber=.009*np.sin(2*np.pi*(76*t-24*t*t))*np.exp(-t/.046)*(1-np.exp(-t/.002))
    return fade(body+(resonant+rubber)[:,None],.002,.10)

def modern_room(t,arrival):
    ventilation=filter_fft(RNG.normal(size=(N,2)),60,1150)
    ventilation=level(ventilation,.0055)
    ventilation*=np.interp(t,[0,arrival,arrival+.8,20,23,24],[.6,.6,1,.8,.5,0])[:,None]
    instrument=np.zeros((N,2))
    for freq,amp in [(55,.0075),(110,.0036),(220,.0018),(440,.00065)]:
        phase=2*np.pi*freq*t+.025*np.sin(2*np.pi*.08*t)
        instrument[:,0]+=amp*np.sin(phase)
        instrument[:,1]+=amp*np.sin(phase+.12)
    breath=.92+.08*np.sin(2*np.pi*.075*t)
    envelope=np.interp(t,[0,1.5,7.8,12,18.5,20,23,24],[.35,.45,.65,.85,1,.7,.35,0])
    instrument*= (breath*envelope)[:,None]
    return ventilation,fade(instrument,.3,.7)

def sliding_airlock(t):
    # Rubber-sealed electric track: soft acceleration, steady slide, deceleration.
    env=np.interp(t,[0,.07,.23,1.08,1.30,1.45,24],[0,.45,1,.85,.32,0,0])
    frequency=np.interp(t,[0,.2,1.04,1.45,24],[120,192,192,92,92])
    phase=2*np.pi*np.cumsum(frequency)/SR
    motor=(np.sin(phase)+.22*np.sin(2*phase)+.06*np.sin(4*phase))*.010
    rail=level(filter_fft(RNG.normal(size=(N,2)),110,1900),.0065)
    airlock=(motor[:,None]+rail)*env[:,None]
    return fade(airlock,.03,.1)

def instrument_alignment(t):
    # Retain the score's 20-second event, now a clean resonant instrument lock.
    tt=np.maximum(t-20,0);envelope=(1-np.exp(-tt/.012))*np.exp(-tt/1.3)
    envelope[t<20]=0
    chord=np.zeros((N,2))
    for freq,amp in [(73.416,.060),(146.832,.027),(293.665,.009),(587.33,.003)]:
        chord[:,0]+=amp*np.sin(2*np.pi*freq*tt)*envelope
        chord[:,1]+=amp*np.sin(2*np.pi*(freq+.08)*tt)*envelope
    return room_response(chord,.12)

def meter(ff,path):
    p=subprocess.run([ff,'-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-2.5:LRA=10:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default=imageio_ffmpeg.get_ffmpeg_exe())
    p.add_argument('--sync',type=Path,default=OUT/'walk_sync.json');args=p.parse_args()
    sync=json.loads(args.sync.read_text())
    events=sync['foot_contacts'];arrival=sync['doorway_crossing_seconds']
    if sync.get('fps') != 24 or arrival is None or not 0 < float(arrival) < DURATION:
        raise ValueError('A measured doorway crossing and 24 fps contact schedule are required')
    if any(abs(float(e['time_seconds'])-(float(e['frame'])-1)/24) > 1e-6 for e in events):
        raise ValueError('Contact timestamps must use frame 1 at time zero')
    for folder in [OUT,OUT/'stems',OUT/'footstep_variants']:folder.mkdir(exist_ok=True,parents=True)
    footpath=ROOT/'audio/v2/raw/stone_footsteps.wav'
    if not footpath.exists():
        raise FileNotFoundError(f'Required existing recording is missing: {footpath}')
    footclips,footdetails=samples_from_recording(read_wav(footpath))
    footclips=[muted_deck_contact(clip,i) for i,clip in enumerate(footclips)]
    for i,clip in enumerate(footclips):write_wav(OUT/'footstep_variants'/f'deck_step_{i+1:02d}.wav',clip)
    t=np.arange(N)/SR
    score=read_wav(ROOT/'audio/stems/original_underscore.wav')*3.0
    alignment=instrument_alignment(t)
    anticipation=read_wav(ROOT/'audio/stems/anticipation.wav')*2.45
    ambience,mechanism=modern_room(t,arrival)
    airlock=sliding_airlock(t)
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
    footsteps=room_response(footsteps,.12)
    # Doorway arrival is a quiet change of air/room scale, not an unsupported door slam.
    air=filter_fft(RNG.normal(size=(N,2)),150,1700)
    envelope=np.exp(-((t-arrival)/.62)**2)
    doorway=level(air,.005)*envelope[:,None]
    doorway=room_response(doorway,.10)
    # Sparse upper partials support the fantastic sky; entirely original synthesis.
    sky=np.zeros((N,2))
    for start,freq,amplitude in [(7.7,587.33,.007),(12.7,880,.006),(17.2,1174.66,.004)]:
        tt=np.maximum(t-start,0);e=(1-np.exp(-tt/.75))*np.exp(-tt/3.7);e[t<start]=0
        sky+=np.column_stack([np.sin(2*np.pi*freq*t),np.sin(2*np.pi*(freq+.19)*t)])*e[:,None]*amplitude
    sky=room_response(sky,.18)
    layers={'ventilation':ambience,'original_underscore':score,'instrument_hum':mechanism,'sliding_airlock':airlock,'footsteps':footsteps,'doorway_arrival':doorway,'sky_harmonics':sky,'alignment':alignment,'anticipation':anticipation}
    mix=fade(filter_fft(sum(layers.values()),28,17000),.45,1.1)
    gain=min(1,.78/max(float(np.max(np.abs(mix))),1e-8))
    for name,x in layers.items():write_wav(OUT/'stems'/f'{name}.wav',x*gain)
    premaster=OUT/'last_observatory_v5_premaster.wav';final=OUT/'last_observatory_v5_mix.wav'
    write_wav(premaster,mix*gain)
    subprocess.run([args.ffmpeg,'-v','error','-y','-i',str(premaster),'-af','loudnorm=I=-18:TP=-2.5:LRA=10','-ar',str(SR),'-c:a','pcm_s16le',str(final)],check=True)
    measured=meter(args.ffmpeg,final);finished=read_wav(final)
    # Correct the short-program loudness offset with a final linear trim.
    trim=10**((-18.0-float(measured['input_i']))/20)
    trim=min(trim,10**((-2.3-float(measured['input_tp']))/20))
    write_wav(final,finished*trim)
    measured=meter(args.ffmpeg,final);finished=read_wav(final)
    sources=[ROOT/'audio/stems'/f'{name}.wav' for name in ['original_underscore','anticipation']]+[footpath]
    qa={'version':5,'duration_seconds':len(finished)/SR,'sample_rate':SR,'channels':2,'encoding':'16-bit PCM WAV',
        'loudness_integrated_lufs':float(measured['input_i']),'true_peak_dbtp':float(measured['input_tp']),'loudness_range_lu':float(measured['input_lra']),
        'clipped_samples':int(np.sum(np.abs(finished)>=1)),'finite_values':bool(np.isfinite(finished).all()),
        'footstep_count':len(eventlog),'footstep_events':eventlog,'doorway_crossing_seconds':arrival,'alignment_seconds':20,
        'sync_status':sync.get('status','unverified'),'sync_source':str(args.sync.relative_to(ROOT)) if args.sync.is_relative_to(ROOT) else args.sync.name,
        'step_extraction':footdetails,'stems':list(layers),'sources':[{'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in sources],
        'dialogue':False,'new_paid_api_requests':0,'airlock_seconds':[0,1.45],
        'synthesis':['muted metal/rubber footfall resonances','sliding electric airlock','ventilation','instrument hum','instrument alignment','doorway air','sky harmonics'],
        'license':'Existing ElevenLabs SFX reused from v1/v2 follow the original account plan; tier unverified. Original synthesized layers created for this project. Not CC0.'}
    (OUT/'mix_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    manifest={'version':5,'new_paid_api_requests':0,'master_file':str(final.relative_to(ROOT)),
        'master_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
        'mix_script':'scripts/audio_mix_v5.py','mix_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'sync_file':qa['sync_source'],'source_files':qa['sources'],'synthesis':qa['synthesis'],
        'source_footfall_manifest':'audio/v2/generation_manifest.json','dialogue':False}
    (OUT/'generation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:qa[k] for k in ['duration_seconds','loudness_integrated_lufs','true_peak_dbtp','clipped_samples','footstep_count','sync_status']},indent=2))
if __name__=='__main__':main()
