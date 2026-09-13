#!/usr/bin/env python3
"""Apply the final picture edit to the existing score, preserving originals."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/python'))
sys.path.insert(0, str(ROOT / 'scripts'))
import numpy as np
import soundfile as sf
import imageio_ffmpeg
from music_v13 import meter

OUT = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = OUT / 'forest_to_astra_music.wav'
    original_mp3 = OUT / 'forest_to_astra_music.mp3'
    before = {p.name: sha(p) for p in (source, original_mp3)}
    assert before[source.name] == '3f6d515c1147259351a5ef501c6ac0ab32d75b643d4704a28a8c60ea56fb64b3'
    audio, sr = sf.read(source, dtype='float64', always_2d=True)
    assert sr == 48000 and audio.shape == (1608000, 2)
    trim, fade = 36000, 5760
    edited = audio[trim:].copy()
    edited[:fade] *= np.sin(np.linspace(0, np.pi / 2, fade))[:, None] ** 2
    master = OUT / 'forest_to_astra_music_final.wav'
    preview = OUT / 'forest_to_astra_music_final.mp3'
    sf.write(master, edited, sr, subtype='PCM_24')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg, '-y', '-v', 'error', '-i', str(master),
                    '-codec:a', 'libmp3lame', '-b:a', '256k', str(preview)], check=True)
    final, final_sr = sf.read(master, dtype='float64', always_2d=True)
    decoded_bytes = subprocess.run([ffmpeg, '-v', 'error', '-i', str(preview),
                                   '-f', 'f64le', '-acodec', 'pcm_f64le', '-'],
                                  capture_output=True, check=True).stdout
    decoded = np.frombuffer(decoded_bytes, dtype='<f8').reshape(-1, 2)
    measures = meter(master)
    preview_measures = meter(preview)
    unchanged = {p.name: sha(p) == before[p.name] for p in (source, original_mp3)}
    exact_tail = np.array_equal(final[fade:], audio[trim + fade:])
    checks = {
        'original_wav_and_mp3_unchanged': all(unchanged.values()),
        'exact_1572000_stereo_frames': final.shape == (1572000, 2),
        'sample_rate_48000': final_sr == 48000,
        'pcm_24': sf.info(master).subtype == 'PCM_24',
        'finite': bool(np.isfinite(final).all()),
        'no_clipped_samples': bool(np.max(np.abs(final)) < 1),
        'true_peak_below_minus_2': measures['input_tp'] < -2,
        'integrated_loudness_minus_19_to_minus_16': -19 <= measures['input_i'] <= -16,
        'first_sample_zero': bool(np.all(final[0] == 0)),
        'tail_after_fade_exact_original_samples': exact_tail,
        'final_fade_preserved': np.array_equal(final[-48000:], audio[-48000:]),
        'mp3_decodes_to_exact_duration': decoded.shape == (1572000, 2),
        'mp3_no_clipping': bool(np.max(np.abs(decoded)) < 1),
    }
    report = {
        'status': 'passed' if all(checks.values()) else 'failed',
        'edit': 'Remove forest source frames 1–9 at 12 fps; final picture begins at frame 10.',
        'source_duration_seconds': 33.5, 'trim_start_seconds': 0.75,
        'trim_start_samples': trim, 'fade_in_seconds': 0.12,
        'fade_in_samples': fade, 'fade_curve': 'sin squared, zero to unity',
        'duration_seconds': len(final) / final_sr, 'sample_frames': len(final),
        'sample_rate_hz': final_sr, 'channels': 2, 'encoding': '24-bit PCM WAV',
        'master_file': str(master.relative_to(ROOT)), 'master_sha256': sha(master),
        'mp3_file': str(preview.relative_to(ROOT)), 'mp3_sha256': sha(preview),
        'source_hashes': before, 'source_preservation': unchanged,
        'integrated_loudness_lufs': measures['input_i'],
        'true_peak_dbtp': measures['input_tp'], 'loudness_range_lu': measures['input_lra'],
        'sample_peak_dbfs': float(20 * np.log10(np.max(np.abs(final)))),
        'clipped_sample_count': int(np.count_nonzero(np.abs(final) >= 1)),
        'mp3_measurements': preview_measures, 'checks': checks,
        'final_cues_seconds': {
            'forest': [0, 10.25], 'doorway': 10.25, 'vigilance': [10.25, 14.25],
            'curiosity': [14.25, 16.75], 'astra_atmosphere': 16.75,
            'expressive_reveal': 21.95, 'fingertip': 28.55, 'resolve': [30.25, 32.75]},
        'composition_regenerated': False, 'gain_renormalization': False,
        'stems_and_score_events': 'Preserved at original 33.5-second timeline.',
        'perceptual_listening_performed': False,
    }
    (OUT / 'final-edit-qa.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()
