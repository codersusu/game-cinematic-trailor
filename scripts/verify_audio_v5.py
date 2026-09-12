#!/usr/bin/env python3
"""Measure the final movie's AAC audio. This is technical QA, not listening.

The default input is the completed Astra Chamber movie in the project root.
No source audio is changed. Decoded float PCM exists only in a temporary folder.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('movie', nargs='?', type=Path,
                        default=ROOT / 'The Last Observatory - Astra Chamber.mp4')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'audio/v5/final-aac-qa.json')
    parser.add_argument('--ffmpeg', default=imageio_ffmpeg.get_ffmpeg_exe())
    return parser


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def parse_ebur128(stderr):
    # Per-frame logs also contain I/LRA values; only the last summary is final.
    if 'Summary:' not in stderr:
        raise ValueError('FFmpeg did not produce an ebur128 summary')
    summary = stderr.rsplit('Summary:', 1)[1]
    number = r'([-+]?(?:\d+(?:\.\d*)?|\.\d+)|[-+]?inf|nan)'
    patterns = {
        'integrated_loudness_lufs': rf'\bI:\s*{number}\s+LUFS',
        'loudness_range_lu': rf'\bLRA:\s*{number}\s+LU',
        'true_peak_dbtp': rf'True peak:\s*Peak:\s*{number}\s+dBFS',
    }
    values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, summary, re.IGNORECASE)
        if match is None:
            raise ValueError(f'Missing final ebur128 measurement: {key}')
        value = float(match.group(1))
        if not math.isfinite(value):
            raise ValueError(f'Non-finite final ebur128 measurement: {key}')
        values[key] = value
    return values


def verify(movie, ffmpeg):
    if not movie.is_file():
        raise FileNotFoundError(f'Completed movie does not exist: {movie}')
    version = subprocess.run([ffmpeg, '-version'], check=True, capture_output=True,
                             text=True).stdout.splitlines()[0]
    base = [ffmpeg, '-hide_banner', '-nostdin', '-i', str(movie),
            '-map', '0:a:0', '-vn', '-sn', '-dn']
    metering = subprocess.run(base + ['-af', 'ebur128=peak=true', '-f', 'null', '-'],
                             capture_output=True, text=True, check=True)
    measurements = parse_ebur128(metering.stderr)
    # Inspect the input stream declaration, before the output stream mapping.
    input_log = metering.stderr.split('Stream mapping:', 1)[0]
    codecs = re.findall(r'Stream #[^\n]*Audio:\s*([^,\s]+)', input_log)
    if not codecs:
        raise ValueError('Could not identify the movie audio codec')
    codec = codecs[0].lower()
    with tempfile.TemporaryDirectory(prefix='observatory-v5-aac-') as folder:
        pcm_path = Path(folder) / 'decoded-float.wav'
        # Do not force a sample rate or channel count: preserve what was encoded.
        subprocess.run(base + ['-v', 'error', '-c:a', 'pcm_f32le', str(pcm_path)],
                       capture_output=True, text=True, check=True)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', wavfile.WavFileWarning)
            sample_rate, samples = wavfile.read(pcm_path)
    if not np.issubdtype(samples.dtype, np.floating):
        raise ValueError('Temporary decode was not floating-point PCM')
    channels = 1 if samples.ndim == 1 else samples.shape[1]
    sample_frames = len(samples)
    duration = sample_frames / sample_rate
    finite = bool(np.isfinite(samples).all())
    # PCM saturation is never introduced by conversion to float. AAC overshoots
    # beyond full scale remain measurable here rather than being silently clipped.
    absolute_peak = float(np.max(np.abs(samples))) if finite and samples.size else None
    clipped = int(np.count_nonzero(np.abs(samples) >= 1.0))
    sample_peak_dbfs = (20 * math.log10(absolute_peak)
                        if absolute_peak is not None and absolute_peak > 0 else None)
    checks = {
        'aac_codec': codec == 'aac',
        'sample_rate_48000_hz': sample_rate == 48000,
        'stereo': channels == 2,
        'duration_within_50_ms_of_24_seconds': abs(duration - 24) <= .05,
        'finite_samples': finite,
        'no_full_scale_or_over_range_samples': clipped == 0,
        'non_silent_audio': absolute_peak is not None and absolute_peak > 1e-5,
        'integrated_loudness_within_2_lu_of_minus_18':
            abs(measurements['integrated_loudness_lufs'] + 18) <= 2,
        'true_peak_at_or_below_minus_2_dbtp': measurements['true_peak_dbtp'] <= -2,
    }
    return {
        'version': 5,
        'movie': movie.name,
        'movie_bytes': movie.stat().st_size,
        'movie_sha256': file_sha256(movie),
        'measurement_method': 'FFmpeg ebur128=peak=true on decoded AAC; unmodified-rate/channel float32 PCM sample inspection',
        'ffmpeg_version': version,
        'audio_codec': codec,
        'sample_rate_hz': int(sample_rate),
        'channels': int(channels),
        'decoded_sample_frames': sample_frames,
        'decoded_duration_seconds': duration,
        'expected_duration_seconds': 24,
        'duration_difference_seconds': duration - 24,
        'aac_padding_tolerance_seconds': .05,
        'finite_samples': finite,
        'full_scale_or_over_range_sample_count': clipped,
        'absolute_sample_peak': absolute_peak,
        'sample_peak_dbfs': sample_peak_dbfs,
        **measurements,
        'checks': checks,
        'technical_checks': 'passed' if all(checks.values()) else 'failed',
        'failed_checks': [key for key, passed in checks.items() if not passed],
        'perceptual_listening_performed': False,
    }


def main():
    args = build_parser().parse_args()
    report = verify(args.movie, args.ffmpeg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_name('.' + args.output.name + '.partial')
    partial.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    partial.replace(args.output)
    print(json.dumps(report, indent=2, allow_nan=False))
    if report['failed_checks']:
        raise SystemExit('Final AAC technical QA failed: ' + ', '.join(report['failed_checks']))


if __name__ == '__main__':
    main()
