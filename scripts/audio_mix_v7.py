#!/usr/bin/env python3
"""Add measured final-approach deck contacts to the existing V5 soundtrack.

Writes audio/v7 only. Contact times must come from the native animation report;
no defaults invent footsteps. Requires NumPy and imageio-ffmpeg, no API key.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import numpy as np
import imageio_ffmpeg

OUT = ROOT / 'audio/v7'
SR = 48000
FPS = 24
DURATION = 24


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portable(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return path.name


def read_wav(path):
    with wave.open(str(path), 'rb') as audio:
        if (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) != (SR, 2, 2):
            raise ValueError(f'Expected 48 kHz stereo 16-bit PCM: {path.name}')
        return np.frombuffer(audio.readframes(audio.getnframes()), '<i2').astype(np.float64).reshape(-1, 2) / 32768


def write_wav(path, samples):
    if not np.isfinite(samples).all() or np.max(np.abs(samples)) >= 1:
        raise ValueError('Refusing to write non-finite or clipped audio')
    with wave.open(str(path), 'wb') as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SR)
        audio.writeframes((samples * 32767).astype('<i2').tobytes())


def read_contacts(path):
    report = json.loads(path.read_text())
    if report.get('fps', FPS) != FPS:
        raise ValueError('The contact report must use 24 film frames per second')
    rows = report.get('foot_contacts')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Contact report needs a nonempty foot_contacts array')
    events = []
    for row in rows:
        frame = float(row['frame'])
        # This revision adds only the later approach, after the original entrance.
        if not math.isfinite(frame) or not 240 < frame <= 576:
            raise ValueError(f'Contact is outside the later approach: {frame}')
        side = {'l': 'left', 'r': 'right'}.get(str(row['foot']).lower(), str(row['foot']).lower())
        if side not in ('left', 'right'):
            raise ValueError('Each contact needs an explicit left/right foot')
        seconds = (frame - 1) / FPS
        if 'time_seconds' in row and abs(float(row['time_seconds']) - seconds) > 1e-5:
            raise ValueError('Contact seconds must use frame 1 at time zero')
        events.append({'frame': int(frame) if frame.is_integer() else frame,
                       'foot': side, 'time_seconds': seconds})
    if events != sorted(events, key=lambda event: event['frame']):
        raise ValueError('Measured contacts must be sorted by frame')
    if len({(event['frame'], event['foot']) for event in events}) != len(events):
        raise ValueError('Duplicate measured contact')
    return events


def meter(ffmpeg, path):
    run = subprocess.run([ffmpeg, '-hide_banner', '-nostdin', '-i', str(path),
                          '-af', 'loudnorm=I=-18:TP=-2.5:LRA=10:print_format=json',
                          '-f', 'null', '-'], capture_output=True, text=True, check=True)
    values = json.loads(run.stderr[run.stderr.rfind('{'):run.stderr.rfind('}') + 1])
    return {key: float(values[key]) for key in ('input_i', 'input_tp', 'input_lra')}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contacts', type=Path, default=ROOT / 'renders/v7/approach-performance.json')
    parser.add_argument('--ffmpeg', default=imageio_ffmpeg.get_ffmpeg_exe())
    return parser


def main():
    args = build_parser().parse_args()
    events = read_contacts(args.contacts)
    source = ROOT / 'audio/v5/last_observatory_v5_mix.wav'
    base = read_wav(source)
    if len(base) != SR * DURATION:
        raise ValueError('The source soundtrack must be exactly 24 seconds')
    variant_paths = sorted((ROOT / 'audio/v5/footstep_variants').glob('deck_step_*.wav'))
    if not variant_paths:
        raise FileNotFoundError('No existing V5 deck contact variants found')
    additions = np.zeros_like(base)
    rng = np.random.default_rng(70090337)
    for index, event in enumerate(events):
        path = variant_paths[index % len(variant_paths)]
        clip = read_wav(path)
        mono = clip.mean(axis=1)
        pan = -.065 if event['foot'] == 'left' else .065
        clip = np.column_stack([mono * np.sqrt((1 - pan) / 2),
                                mono * np.sqrt((1 + pan) / 2)])
        clip *= .055 * rng.uniform(.94, 1.04) / max(float(np.max(np.abs(clip))), 1e-9)
        onset = round(event['time_seconds'] * SR)
        stop = min(len(additions), onset + len(clip))
        additions[onset:stop] += clip[:stop - onset]
        event['variant_source'] = portable(path)
    # Small, damped early reflections fit the chamber and preserve heel onsets.
    dry = additions.copy()
    for seconds, gain in [(.026, .085), (.064, .048), (.117, .021)]:
        delay = round(seconds * SR)
        additions[delay:] += dry[:-delay, ::-1] * gain
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'stems').mkdir(exist_ok=True)
    premaster = OUT / 'last_observatory_v7_premaster.wav'
    master = OUT / 'last_observatory_v7_mix.wav'
    write_wav(premaster, base + additions)
    measured = meter(args.ffmpeg, premaster)
    # One transparent overall gain retains the V5 score and cue relationships.
    gain_db = min(-18 - measured['input_i'], -2.6 - measured['input_tp'])
    gain = 10 ** (gain_db / 20)
    write_wav(master, (base + additions) * gain)
    write_wav(OUT / 'stems/v5_program.wav', base * gain)
    write_wav(OUT / 'stems/approach_footsteps.wav', additions * gain)
    finished = read_wav(master)
    measured = meter(args.ffmpeg, master)
    peak = float(np.max(np.abs(finished)))
    checks = {
        'exactly_24_seconds': len(finished) == SR * DURATION,
        'finite_samples': bool(np.isfinite(finished).all()),
        'no_clipping': peak < 1,
        'loudness_within_half_lu_of_minus_18': abs(measured['input_i'] + 18) <= .5,
        'true_peak_at_or_below_minus_2_5_dbtp': measured['input_tp'] <= -2.5,
    }
    sources = [source, args.contacts, *variant_paths]
    report = {
        'version': 7,
        'master': portable(master), 'master_sha256': sha256(master),
        'duration_seconds': len(finished) / SR, 'sample_rate_hz': SR,
        'channels': 2, 'encoding': '16-bit PCM WAV',
        'integrated_loudness_lufs': measured['input_i'],
        'true_peak_dbtp': measured['input_tp'], 'loudness_range_lu': measured['input_lra'],
        'absolute_sample_peak': peak,
        'full_scale_or_over_range_sample_count': int(np.count_nonzero(np.abs(finished) >= 1)),
        'overall_linear_trim_db': gain_db,
        'added_footstep_count': len(events), 'added_footstep_events': events,
        'original_entrance_contacts_unchanged': True,
        'doorway_crossing_seconds': 3.4054740275,
        'source_files': [{'file': portable(path), 'sha256': sha256(path)} for path in sources],
        'script': 'scripts/audio_mix_v7.py', 'script_sha256': sha256(Path(__file__)),
        'new_paid_api_requests': 0, 'dialogue': False,
        'checks': checks, 'technical_checks': 'passed' if all(checks.values()) else 'failed',
        'perceptual_listening_performed': False,
        'rights': 'Reuses V5 score and effects, including processed V2 ElevenLabs footfall source; original source terms apply. Additional mix creates no new service requests.',
    }
    (OUT / 'mix_qa.json').write_text(json.dumps(report, indent=2) + '\n')
    (OUT / 'walk_sync.json').write_text(json.dumps({
        'fps': FPS, 'source': portable(args.contacts),
        'source_sha256': sha256(args.contacts), 'foot_contacts': events,
    }, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if not all(checks.values()):
        raise SystemExit('V7 soundtrack failed technical QA; see audio/v7/mix_qa.json')


if __name__ == '__main__':
    main()
