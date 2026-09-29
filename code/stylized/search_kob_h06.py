"""Stage 2 at 0.6 per cent homelessness: a joint grid over (kap, omega_c, b) around the
stage 2 exit, everything else held there. The omega = 0 comparison moves in steps of a
productivity node (0.5-1 point of participation), so no single parameter can put
omega_c's moment inside 2.5 per cent; this looks for the combination that puts
participation, users' income and the child gap all as close as the grid allows.
Writes the best point to calibrated_stage2_h06_kob.json."""
import json, itertools, numpy as np
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open('calibrated_stage2.json'))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
T = dict(part=0.0890, r_use=0.74, child_gap=0.1834)
best = None
for kap, b in itertools.product(np.arange(0.11916, 0.119285, 0.00001), (0.0625, 0.0626, 0.0627, 0.0628, 0.0629)):
    q = with_(par, kap=float(kap), b=float(b))
    cf = stats(with_(q, omega=0.0))['part']
    for om in np.arange(0.0008, 0.00171, 0.0001):
        m = stats(with_(q, omega=float(om)))
        g = dict(part=m['part'] / T['part'] - 1, r_use=m['r_use'] / T['r_use'] - 1,
                 child_gap=(cf / m['part'] - 1) / T['child_gap'] - 1)
        worst = max(abs(x) for x in g.values())
        if best is None or worst < best[0]:
            best = (worst, float(kap), float(b), float(om), g)
            print(f'best {100*worst:.2f}%  kap {kap:.5f} b {b:.4f} omega {om:.5f}  ' +
                  '  '.join(f'{k} {100*x:+.1f}' for k, x in g.items()), flush=True)
_, kap, b, om, g = best
v.update(kap=kap, b=b, omega=om); v['_search'] = {k: round(100 * x, 2) for k, x in g.items()}
json.dump(v, open('calibrated_stage2_h06_kob.json', 'w'), indent=1)
print('WROTE calibrated_stage2_h06_kob.json', flush=True)
