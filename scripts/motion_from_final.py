"""Refresh the two-second motion proof from the final, corrected native frames."""
from pathlib import Path
import tempfile,os,importlib.util,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('film_encoder',ROOT/'scripts/encode.py')
encoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(encoder)
with tempfile.TemporaryDirectory(prefix='observatory-motion-') as folder:
 root=Path(folder);target=root/'renders/motion-test';target.mkdir(parents=True)
 for frame in range(180,228):
  source=ROOT/'renders/frames'/f'{frame:04d}.png'
  if not source.exists():raise RuntimeError(f'Missing corrected frame {frame}')
  os.link(source,target/source.name)
 encoder.ROOT=root;sys.argv=['encode.py','test'];encoder.main()
 shutil.copy2(root/'previews/motion-test.mp4',ROOT/'previews/motion-test.mp4')
print('Updated full-resolution motion proof from corrected final frames180–227.')
