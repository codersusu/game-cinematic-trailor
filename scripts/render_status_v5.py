"""Read-only progress summary for the resumable film render."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import re,json,statistics
ROOT=Path(__file__).resolve().parents[1]
frames=sorted((ROOT/'renders/v5/frames').glob('[0-9][0-9][0-9][0-9].png'))
log=(ROOT/'renders/v5/final-render.log').read_text(errors='replace') if (ROOT/'renders/v5/final-render.log').exists() else ''
done=[(int(f),float(t)) for f,t in re.findall(r'FRAME_DONE (\d+) ([\d.]+)',log)]
last=done[-1][0] if done else 0
shot='surprise close-up' if last<=36 else 'native entrance' if last<=192 else 'turning instrument' if last<=288 else 'wonder close-up' if last<=344 else 'wide' if last<=480 else 'alignment and title'
rate=statistics.median(t for _,t in done[-8:]) if done else None
out={'completed_frames':len(frames),'total_frames':576,'percent':round(len(frames)/576*100,1),'latest_frame':last,'shot':shot,'recent_seconds_per_frame':round(rate,2) if rate else None,'movie_ready':(ROOT/'The Last Observatory - Astra Chamber.mp4').exists(),'checked_utc':datetime.now(timezone.utc).isoformat()}
print(json.dumps(out))
