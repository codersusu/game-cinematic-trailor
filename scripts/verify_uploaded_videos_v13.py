"""Verify every archived video from a separately fetched GitHub LFS checkout."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
fresh = Path(sys.argv[1]).resolve()
plan = json.loads((ROOT / 'docs/v13/video-cleanup-plan.json').read_text())
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=fresh).decode().strip()
assert commit == plan['requires_remote_commit']
rows = []
for row in plan['videos']:
    oid = row['sha256']
    obj = fresh / '.git/lfs/objects' / oid[:2] / oid[2:4] / oid
    assert obj.stat().st_size == row['bytes'], row['path']
    assert hashlib.sha256(obj.read_bytes()).hexdigest() == oid, row['path']
    pointer = subprocess.check_output(['git', 'show', 'HEAD:' + row['path']], cwd=fresh).decode()
    assert f'oid sha256:{oid}' in pointer and f'size {row["bytes"]}' in pointer
    rows.append(row)
report = {'status':'passed', 'remote':'https://github.com/codersusu/game-cinematic-trailor',
          'commit':commit, 'method':'Fresh remote Git clone and independent LFS fetch; all video bytes SHA256 checked',
          'videos':rows, 'count':len(rows), 'bytes':sum(x['bytes'] for x in rows)}
(ROOT / 'docs/v13/videos-remote-verification.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'videos'}))
