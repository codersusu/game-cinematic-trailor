"""Copy audited project sources/assets/video to the existing Git checkout.

Never deletes local production files. Git staging/push and verified cleanup are
separate operations. Third-party redistribution rules are explicit inputs.
"""
from pathlib import Path
import fnmatch
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'github-submission'
rules = json.loads((ROOT / 'docs/v13/redistribution-rules.json').read_text())
restricted = [p for group in rules['required_exclusions'] + rules['research_image_exclusions']
              for p in group['patterns']]
video_extensions = {'.mp4', '.mov', '.mkv', '.webm', '.avi'}
source_folders = ['scripts', 'assets', 'audio', 'docs', 'previews', 'renders', 'preview']

def exclusion(p):
    name = p.relative_to(ROOT).as_posix()
    if name == 'docs/v13/upload-manifest.json':
        return 'Manifest generated after copying; excludes itself'
    if any(fnmatch.fnmatch(name, pat) for pat in restricted):
        return 'License restriction or signed source response; see redistribution rules'
    if any(part in {'__pycache__', '__MACOSX', '.git'} for part in p.parts) or p.name.startswith('._'):
        return 'Generated runtime/archive metadata'
    if p.name == '.DS_Store' or p.suffix in {'.pyc', '.log', '.blend1', '.blend2'}:
        return 'Cache, log or automatic backup'
    if p.name.startswith('.env') or p.suffix.lower() == '.html' or name.startswith('assets/reference/'):
        return 'Private configuration or unlicensed research page/reference'
    if p.is_symlink():
        return 'Symlink; not followed into external locations'
    if name.startswith(('previews/', 'renders/', 'preview/')):
        if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.exr'}:
            if p.stem.isdigit() or p.stem.startswith('.') or 'frame' in p.parent.name:
                return 'Regenerable individual render frame'
        if p.suffix.lower() == '.blend':
            return 'Intermediate render/probe scene; source scenes and scripts retained'
    return None

paths = [p for folder in source_folders for p in (ROOT / folder).rglob('*') if p.is_file()]
paths += [p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in
          {'.blend', '.md', '.command', '.mp4', '.mov'}]
included, omitted = [], []
for p in sorted(set(paths)):
    rel = p.relative_to(ROOT)
    reason = exclusion(p)
    if reason:
        omitted.append({'path':rel.as_posix(), 'reason':reason})
        continue
    target = DEST / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
        shutil.copy2(p, target)
    included.append({'path':rel.as_posix(), 'bytes':p.stat().st_size, 'sha256':sha})

manifest = {'version':13, 'files':included, 'exclusions':omitted,
            'file_count':len(included), 'bytes':sum(r['bytes'] for r in included),
            'scope':'All project code and redistributable source assets; licensed archer data, credentials, runtimes and regenerable frame caches excluded',
            'latest_movie':'previews/v13/Forest-to-Astra-V13-1080p.mp4'}
for parent in [ROOT, DEST]:
    (parent / 'docs/v13/upload-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps({'files':manifest['file_count'], 'bytes':manifest['bytes'], 'excluded':len(omitted)}))
