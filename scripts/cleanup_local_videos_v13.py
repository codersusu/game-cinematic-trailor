"""Remove only remotely verified video exports; retain editable project data.

Default is a dry run. --execute also replaces Git checkout video contents with
their committed LFS pointers and evicts only their verified local cache objects.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / 'github-submission'
plan = json.loads((ROOT / 'docs/v13/video-cleanup-plan.json').read_text())
proof = json.loads((ROOT / 'docs/v13/videos-remote-verification.json').read_text())
assert proof['status'] == 'passed' and proof['commit'] == plan['requires_remote_commit']
assert proof['videos'] == plan['videos']
assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO).decode().strip() == proof['commit']
prepared = []
for row in proof['videos']:
    rel = Path(row['path'])
    assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix.lower() == '.mp4'
    original, checkout = ROOT / rel, REPO / rel
    pointer = subprocess.check_output(['git','show','HEAD:' + row['path']], cwd=REPO)
    assert f'oid sha256:{row["sha256"]}'.encode() in pointer
    for p in [original, checkout]:
        assert p.is_file() and not p.is_symlink(), str(p)
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], str(p)
    prepared.append((row, original, checkout, pointer))

# Do not evict a cache object that also belongs to a non-video asset.
video_paths = {r['path'] for r in proof['videos']}
shared = set()
listing = json.loads(subprocess.check_output(['git','lfs','ls-files','--json'], cwd=REPO))
for item in listing['files']:
    if item['name'] not in video_paths:
        shared.add(item['oid'])

if '--execute' not in sys.argv:
    print(json.dumps({'dry_run':True, 'verified_production_videos':len(prepared),
                      'production_video_bytes':sum(r['bytes'] for r, *_ in prepared)}))
    raise SystemExit(0)

report = {'status':'in progress', 'remote_commit':proof['commit'], 'deleted_production_videos':[],
          'checkout_lfs_placeholders':[], 'evicted_video_cache_objects':[],
          'preserved':'All editable scenes, source assets, music, code and individual render frames'}
out = ROOT / 'docs/v13/video-cleanup-result.json'
seen = set()
for row, original, checkout, pointer in prepared:
    original.unlink()
    report['deleted_production_videos'].append(row)
    checkout.write_bytes(pointer)
    report['checkout_lfs_placeholders'].append(row['path'])
    oid = row['sha256']
    obj = REPO / '.git/lfs/objects' / oid[:2] / oid[2:4] / oid
    if oid not in seen and oid not in shared and obj.exists():
        assert hashlib.sha256(obj.read_bytes()).hexdigest() == oid
        obj.unlink()
        report['evicted_video_cache_objects'].append({'sha256':oid, 'bytes':row['bytes']})
    seen.add(oid)
    out.write_text(json.dumps(report, indent=2)+'\n')
report['status'] = 'complete'
video_names = [r['path'] for r in proof['videos']]
subprocess.run(['git','add','-f','--',*video_names], cwd=REPO, check=True)
subprocess.run(['git','diff','--cached','--exit-code','--',*video_names], cwd=REPO, check=True)
report['production_video_bytes_removed'] = sum(x['bytes'] for x in report['deleted_production_videos'])
report['restore_command'] = 'git lfs pull --include="*.mp4"'
out.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'status':'complete','production_videos_removed':len(prepared),
                  'production_video_bytes_removed':report['production_video_bytes_removed'],
                  'checkout_videos_replaced_with_pointers':len(prepared),
                  'video_cache_objects_evicted':len(report['evicted_video_cache_objects'])}))
