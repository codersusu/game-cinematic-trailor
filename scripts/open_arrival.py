"""Open the editable scene using an installed Blender; no bundled application needed."""
from pathlib import Path
import os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
candidates=[os.environ.get('BLENDER_BIN'),shutil.which('blender'),'/Applications/Blender.app/Contents/MacOS/Blender',str(ROOT/'tools/Blender4.5.app/Contents/MacOS/Blender')]
blender=next((x for x in candidates if x and Path(x).is_file()),None)
if not blender:raise SystemExit('Install Blender 4.5 LTS and put blender on PATH, or set BLENDER_BIN to its executable.')
subprocess.Popen([blender,str(ROOT/'observatory-v2.blend')],cwd=ROOT)
