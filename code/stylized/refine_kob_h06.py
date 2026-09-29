"""Refine the joint search's best point (kap 0.11926, b 0.0627, omega 0.0013) in finer
kap steps, omega either side: all three moments inside 2.5 per cent?"""
import json, itertools, numpy as np
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open('calibrated_stage2_h06_kob.json'))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
best = None
for kap in np.arange(0.119258, 0.1192801, 0.000002):
    q = with_(par, kap=float(kap)); cf = stats(with_(q, omega=0.0))['part']
    for om in (0.00125, 0.00130, 0.00135):
        m = stats(with_(q, omega=om))
        g = dict(part=m['part'] / 0.089 - 1, r_use=m['r_use'] / 0.74 - 1, child_gap=(cf / m['part'] - 1) / 0.1834 - 1)
        w = max(abs(x) for x in g.values())
        print(f'kap {kap:.6f} omega {om:.5f}  worst {100*w:.2f}  ' + '  '.join(f'{k} {100*x:+.2f}' for k, x in g.items()), flush=True)
        if best is None or w < best[0]: best = (w, float(kap), om, g)
w, kap, om, g = best
v.update(kap=kap, omega=om); v['_search'] = {k: round(100 * x, 2) for k, x in g.items()}
json.dump(v, open('calibrated_stage2_h06_kob2.json', 'w'), indent=1)
print(f'BEST worst {100*w:.2f} kap {kap:.6f} omega {om}', flush=True)
