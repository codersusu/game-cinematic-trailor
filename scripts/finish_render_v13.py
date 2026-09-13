"""Resume the approved V13 renders sequentially, then encode the scored film."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
bundled = ROOT / 'tools/Blender4.5.app/Contents/MacOS/Blender'
BLENDER = os.environ.get('BLENDER_BIN', str(bundled) if bundled.exists() else 'blender')
SCENES = {
    'forest': ('bear-bow-forest-v13.blend', '9b39cf38ebb29f738b8e074e6cdb548d23054572633cc4746e859447c4bfb93a'),
    'room': ('observatory-v12-run-entry.blend', 'f9b081ad2459c3171d968bfe839a83e3f8923d008049bd9fa1ebee9842f1b23d'),
}
for section, (scene, expected) in SCENES.items():
    assert hashlib.sha256((ROOT / scene).read_bytes()).hexdigest() == expected
    assert not (ROOT / 'previews/v13/pause-render').exists(), 'Render paused'
    command = [str(BLENDER), '--background', '--disable-autoexec', str(ROOT / scene),
               '--python-exit-code', '1', '--python', str(ROOT / 'scripts/render_review_v13.py'),
               '--', section, 'motion']
    if section == 'room':
        command += ['37', '575']
    log = ROOT / 'renders/v13/logs' / f'{section}-final-motion.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    print(f'Rendering {section}: {log}', flush=True)
    with log.open('w') as stream:
        subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    assert f'V13_RENDER_COMPLETE {section} motion' in log.read_text(), 'Render incomplete or paused'
    print(f'Completed {section}', flush=True)
subprocess.run([sys.executable, str(ROOT / 'scripts/encode_review_v13.py')], cwd=ROOT, check=True)
print('V13_RENDER_AND_ENCODE_COMPLETE', flush=True)
