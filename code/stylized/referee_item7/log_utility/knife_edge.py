"""How close to indifference the calibrated households are: D(y), the gain from using, over income, at both
calibrations, scaled by the period-1 flow utility of mean income (dU per 1 % of consumption at y = 1).

usage: python3 code/stylized/referee_item7/log_utility/knife_edge.py
"""
import json
import os
import numpy as np
from common import G, BENCH, OUT, load_log

y = np.array([0.24, 0.3, 0.5, 0.675, 0.74, 1.0, 2.0, 5.0, 10.0])
out = {}
for name, q in (('bench', BENCH), ('log', load_log())):
    d = G.D(y, q)
    a = float(G.plan(1.0, q, False)[0][0])
    du1pc = 0.01 * (1.0 - a) * float(G._U0p(1.0 - a + float(G.FA(1.0, q)), q))   # utility of 1 % more consumption at y = 1
    out[name] = dict(y=y.tolist(), D=d.tolist(), D_in_pct_cons=(d / du1pc).tolist())
    print(name, 'D/(1% of consumption at mean income):', np.round(d / du1pc, 2))
json.dump(out, open(os.path.join(OUT, 'knife_edge.json'), 'w'), indent=1)
