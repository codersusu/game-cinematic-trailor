"""Export sequential proof images for human/model visual inspection."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
frames=[345,350,355,359,365,370,377,381,387,391,398,410,424,425,440,455,470,480]
folder=ROOT/'previews/v7/acting-frames'
missing=[f for f in frames if not (folder/f'{f-344:04d}.png').exists()]
if missing:raise SystemExit('Missing proof frames: '+str(missing))
sheet=Image.new('RGB',(1200,6*250),(12,14,17))
for i,f in enumerate(frames):
    im=Image.open(folder/f'{f-344:04d}.png').convert('RGB');im.thumbnail((400,225))
    x,y=(i%3)*400,(i//3)*250;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+231),f'{(f-1)/24:.2f}s / source {f}',fill=(220,220,210))
sheet.save(ROOT/'previews/v7/motion-review.jpg',quality=94)
print('Proof contact sheet exported for inspection.')
