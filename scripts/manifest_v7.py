"""Record the completed V7 delivery after scene, picture and AAC verification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders/v7'


def load(name):
    return json.loads((ROOT / name).read_text())


def item(name):
    p = ROOT / name
    return {'file': str(name), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


audit = load('renders/v7/scene-audit.json')
picture = load('renders/v7/movie-qa.json')
sound = load('renders/v7/audio-qa.json')
closeup = load('previews/v7/closeup-qa.json')
assert audit['status'] == 'passed' and audit['early_reuse']['safe']
assert picture['technical_checks'] == 'passed' and picture['decoded_frames'] == 576
assert sound['technical_checks'] == 'passed'
assert closeup['technical_checks'] == 'passed' and closeup['decoded_frames'] == 136
assert closeup['metadata']['size'] == [1920, 1080]
scene_sha = item('observatory-v7.blend')['sha256']
assert scene_sha == audit['candidate_sha256'] == load('renders/v7/frame-source.json')['scene_sha256']
assert item('observatory-v6.blend')['sha256'] == audit['source_sha256']
for name, record in load('renders/v7/previous-versions.json').items():
    assert item(name)['sha256'] == record['sha256'], 'Previous version changed: ' + name
artifacts = [item(p) for p in [
    'The Last Observatory - Astra Approach.mp4', 'observatory-v7.blend',
    'previews/v7/Astra-Approach-motion-proof.mp4', 'previews/v7/Astra-Approach-closeup-1080p.mp4',
    'previews/v7/final-contact-sheet.jpg', 'docs/preview-v7.png',
]]
assert artifacts[0]['sha256'] == sound['movie_sha256']
assert closeup['movie_sha256'] == next(a['sha256'] for a in artifacts if a['file'] == 'previews/v7/Astra-Approach-closeup-1080p.mp4')
frames = [OUT / 'frames' / f'{f:04d}.png' for f in range(1, 577)]
assert all(p.is_file() for p in frames)
frame_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in frames}
reused = load('renders/v7/reused-frames.json') if (OUT / 'reused-frames.json').exists() else None
if reused:
    assert reused['candidate_scene_sha256'] == scene_sha and reused['count'] == 343
    for frame in reused['frames']:
        assert frame_hashes[f"{frame['frame']:04d}.png"] == frame['sha256']
durations = [float(v) for _, v in re.findall(r'FRAME_DONE (\d+) ([\d.]+)', (OUT / 'final-render.log').read_text(errors='replace'))]
inputs = ['observatory-v6.blend', 'observatory-v5.blend', 'audio/v7/last_observatory_v7_mix.wav']
inputs += ['assets/character/heroine_v4/' + name for name in ['Female_Adult_04_facial.fbx', 'f_walk_start.max.fbx', 'f_walk_neutral_01.max.fbx', 'f_walk_stop.max.fbx', 'f_idle_breathe_01.max.fbx']]
inputs += sorted({record['path'] for record in audit['images'].values() if record['path']})
scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'scripts').glob('*v7*') if p.is_file())
scripts += ['scripts/audit_scene_v5.py', 'scripts/audit_scene_v6.py', 'scripts/verify_audio_v5.py', 'scripts/heroine_motion_v4.py', 'scripts/open_astra_approach.py', 'scripts/configure_gpu.py']
report = {
    'version': 7, 'title': 'The Last Observatory — Astra Approach',
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'movie': {'resolution': [1920, 1080], 'fps': 24, 'frames': 576, 'seconds': 24,
              'active_aspect_ratio': 2.39, 'engine': 'Blender 4.5.13 LTS / Cycles',
              'samples_max': 64, 'adaptive_threshold': .025, 'denoised': True,
              'motion_blur_shutter': .4},
    'new_animation': {'gesture': 'native second walk to the platform, followed by a right-hand reach toward Astra',
                      'first_modified_keyframe': 345, 'walk_frames': [345,424], 'close_camera_frames': [425,480],
                      'original_entrance_and_facial_animation_preserved': True,
                      'second_walk_contacts': [359,377,387,398],
                      'native_second_walk_distance_m': 2.003219814109767, 'early_frames_preserved': [1,343]},
    'artifacts': artifacts, 'build_inputs': [item(p) for p in inputs],
    'scripts': [item(p) for p in scripts],
    'frame_set': {'count': 576, 'reused_from_v6': 343 if reused else 0,
                  'aggregate_sha256': hashlib.sha256(''.join(n + ':' + h + '\n' for n, h in frame_hashes.items()).encode()).hexdigest()},
    'render_timing': {'new_frames_recorded': len(durations),
                      'total_new_frame_render_seconds': round(sum(durations), 2),
                      'median_new_frame_seconds': round(statistics.median(durations), 2) if durations else None},
    'qa': {'scene': 'renders/v7/scene-audit.json', 'picture': 'renders/v7/movie-qa.json',
           'audio': 'renders/v7/audio-qa.json', 'motion_proof': 'previews/v7/acting-proof-qa.json',
           'portable_rebuild': 'renders/v7/rebuild-qa.json', 'native_closeup': 'previews/v7/closeup-qa.json'},
    'encoded_audio': sound, 'previous_versions_unchanged': True, 'new_paid_api_requests': 0,
    'review_limit': 'Representative final images and sequential approach-proof frames inspected; no full real-time playback or perceptual listening.',
}
(OUT / 'render-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print('V7_MANIFEST_READY', artifacts[0]['sha256'])
