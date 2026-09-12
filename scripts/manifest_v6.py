"""Record the completed V6 delivery after scene, picture and AAC verification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/v6'


def load(name):
    return json.loads((ROOT / name).read_text())


def item(name):
    p = ROOT / name
    return {'file': str(name), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


audit = load('renders/v6/scene-audit.json')
picture = load('renders/v6/movie-qa.json')
sound = load('renders/v6/audio-qa.json')
assert audit['status'] == 'passed' and audit['early_reuse']['safe']
assert picture['technical_checks'] == 'passed' and picture['decoded_frames'] == 576
assert sound['technical_checks'] == 'passed'
scene_sha = item('observatory-v6.blend')['sha256']
assert scene_sha == audit['candidate_sha256'] == load('renders/v6/frame-source.json')['scene_sha256']
assert item('observatory-v5.blend')['sha256'] == audit['source_sha256']
for name, record in load('renders/v6/previous-versions.json').items():
    assert item(name)['sha256'] == record['sha256'], 'Previous version changed: ' + name
artifacts = [item(p) for p in [
    'The Last Observatory - Astra Reach.mp4', 'observatory-v6.blend',
    'previews/v6/Astra-Reach-motion-proof.mp4',
    'previews/v6/final-contact-sheet.jpg', 'docs/preview-v6.png',
]]
assert artifacts[0]['sha256'] == sound['movie_sha256']
frames = [OUT / 'frames' / f'{f:04d}.png' for f in range(1, 577)]
assert all(p.is_file() for p in frames)
frame_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in frames}
reused = load('renders/v6/reused-frames.json') if (OUT / 'reused-frames.json').exists() else None
if reused:
    assert reused['candidate_scene_sha256'] == scene_sha and reused['count'] == 359
    for frame in reused['frames']:
        assert frame_hashes[f"{frame['frame']:04d}.png"] == frame['sha256']
durations = [float(v) for _, v in re.findall(r'FRAME_DONE (\d+) ([\d.]+)', (OUT / 'final-render.log').read_text(errors='replace'))]
inputs = ['observatory-v5.blend', 'audio/v5/last_observatory_v5_mix.wav']
inputs += sorted({record['path'] for record in audit['images'].values() if record['path']})
scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts').glob('*v6*') if p.is_file())
scripts += ['scripts/audit_scene_v5.py', 'scripts/verify_audio_v5.py', 'scripts/open_astra_reach.py', 'scripts/configure_gpu.py']
report = {
    'version': 6, 'title': 'The Last Observatory — Astra Reach',
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'movie': {'resolution': [1920, 1080], 'fps': 24, 'frames': 576, 'seconds': 24,
              'active_aspect_ratio': 2.39, 'engine': 'Blender 4.5.13 LTS / Cycles',
              'samples_max': 64, 'adaptive_threshold': .025, 'denoised': True,
              'motion_blur_shutter': .4},
    'new_animation': {'gesture': 'standing right-hand reach toward the distant Astra galaxy',
                      'first_modified_keyframe': 361, 'close_camera_frames': [385, 480],
                      'native_walk_and_facial_animation_preserved': True,
                      'root_and_lower_body_preserved': True},
    'artifacts': artifacts, 'build_inputs': [item(p) for p in inputs],
    'scripts': [item(p) for p in scripts],
    'frame_set': {'count': 576, 'reused_from_v5': 359 if reused else 0,
                  'aggregate_sha256': hashlib.sha256(''.join(n + ':' + h + '\n' for n, h in frame_hashes.items()).encode()).hexdigest()},
    'render_timing': {'new_frames_recorded': len(durations),
                      'total_new_frame_render_seconds': round(sum(durations), 2),
                      'median_new_frame_seconds': round(statistics.median(durations), 2) if durations else None},
    'qa': {'scene': 'renders/v6/scene-audit.json', 'picture': 'renders/v6/movie-qa.json',
           'audio': 'renders/v6/audio-qa.json', 'motion_proof': 'previews/v6/acting-proof-qa.json',
           'portable_rebuild': 'renders/v6/rebuild-qa.json'},
    'encoded_audio': sound, 'previous_versions_unchanged': True, 'new_paid_api_requests': 0,
    'review_limit': 'Representative final images and sequential motion-proof frames inspected; no full real-time playback or perceptual listening.',
}
(OUT / 'render-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print('V6_MANIFEST_READY', artifacts[0]['sha256'])
