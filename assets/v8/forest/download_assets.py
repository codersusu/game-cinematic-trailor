#!/usr/bin/env python3
"""Download the curated CC0 Poly Haven forest assets; verify provider MD5s.

Only asset download URLs are used after selection. Metadata snapshots preserve
the original provider manifests. Run from any directory; resumes verified files.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
SELECTED = {
    'fern_02': 'gltf',
    'rock_moss_set_01': 'gltf',
    'dead_tree_trunk': 'gltf',
    'root_cluster_01': 'gltf',
    'fir_tree_01': 'blend',
}


def md5(path):
    h = hashlib.md5()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def fetch(asset, relative, entry):
    path = ROOT / asset / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size != entry['size'] or md5(path) != entry['md5']:
        temp = path.with_name(path.name + '.part')
        req = urllib.request.Request(entry['url'], headers={'User-Agent': 'AstraTrailerAssetResearch/1.0'})
        with urllib.request.urlopen(req, timeout=120) as response, temp.open('wb') as out:
            for block in iter(lambda: response.read(1048576), b''):
                out.write(block)
        assert temp.stat().st_size == entry['size'], str(path)
        assert md5(temp) == entry['md5'], str(path)
        temp.replace(path)
    print('verified', str(path.relative_to(ROOT)), path.stat().st_size, flush=True)
    return dict(path=str(path.relative_to(ROOT)), url=entry['url'], bytes=path.stat().st_size,
                md5=entry['md5'], sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    records = []
    for asset, fmt in SELECTED.items():
        info = json.loads((ROOT / 'metadata' / (asset + '-files.json')).read_text())
        entry = info[fmt]['2k'][fmt]
        records.append(fetch(asset, entry['url'].rsplit('/', 1)[-1], entry))
        for relative, item in entry.get('include', {}).items():
            records.append(fetch(asset, relative, item))
        if asset == 'fern_02':
            entry = info['Alpha']['2k']['png']
            records.append(fetch(asset, 'textures/' + entry['url'].rsplit('/', 1)[-1], entry))
    asset = 'forest_floor'
    info = json.loads((ROOT / 'metadata' / (asset + '-files.json')).read_text())
    for channel, fmt in [('Diffuse', 'jpg'), ('nor_gl', 'jpg'), ('Rough', 'jpg'), ('Displacement', 'png')]:
        entry = info[channel]['2k'][fmt]
        records.append(fetch(asset, entry['url'].rsplit('/', 1)[-1], entry))
    report = dict(provider='Poly Haven', license='CC0-1.0',
                  license_url='https://polyhaven.com/license', files=records,
                  total_bytes=sum(r['bytes'] for r in records))
    (ROOT / 'download-manifest.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
