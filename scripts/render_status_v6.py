"""Read-only status for the revised ending and final export."""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'renders/v6'
frames = list((folder / 'frames').glob('[0-9][0-9][0-9][0-9].png'))
log = (folder / 'final-render.log').read_text(errors='replace') if (folder / 'final-render.log').exists() else ''
done = [(int(f), float(t)) for f, t in re.findall(r'FRAME_DONE (\d+) ([\d.]+)', log)]
latest = done[-1][0] if done else None
rate = statistics.median(t for _, t in done[-8:]) if done else None
print(json.dumps({
    'completed_frames': len(frames), 'total_frames': 576,
    'reused_frames': 359 if (folder / 'reused-frames.json').exists() else 0,
    'new_frames_completed': len(done), 'latest_frame': latest,
    'shot': 'wide anticipation' if latest and latest < 385 else 'hand reach' if latest and latest < 481 else 'closing' if latest else 'preparing',
    'recent_seconds_per_frame': round(rate, 2) if rate else None,
    'estimated_remaining_render_seconds': round((576-len(frames))*rate) if rate else None,
    'movie_ready': (ROOT / 'The Last Observatory - Astra Reach.mp4').exists(),
    'checked_utc': datetime.now(timezone.utc).isoformat(),
}))
