"""Per-sign reference ranges for demo/coach.py from the train landmarks (5th to 95th percentile, with a margin)."""
import glob, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from coach import measures

ROOT = Path(__file__).resolve().parents[1]
ref = {}
for s in range(1, 6):
    ms = [m for m in (measures(np.load(f)) for f in sorted(glob.glob(str(ROOT / f'data/train/landmarks/sign_0{s}/*.npy')))) if m and m['active'] >= 3]
    a = {k: np.array([m[k] for m in ms]) for k in ('peak', 'two', 'face', 'chest', 'dur')}
    p = lambda k, q: float(np.percentile(a[k], q))
    ref[f'sign_0{s}'] = {'peak_lo': round(p('peak', 5) - .15, 3), 'peak_hi': round(p('peak', 95) + .15, 3), 'two': round(float(np.median(a['two'])), 3),
                        'face_hi': round(p('face', 95) * 1.25, 3), 'chest_hi': round(p('chest', 95) * 1.25, 3),
                        'dur_lo': round(p('dur', 5) * 0.75, 3), 'dur_hi': round(p('dur', 95) * 1.4, 3), 'n': len(ms)}
(ROOT / 'demo/static/private/coach_ref.json').write_text(json.dumps(ref, indent=1))
print(json.dumps(ref, indent=1))
