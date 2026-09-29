"""Where does the omega = 0 comparison land as kap moves, everything else at the stage 2
exit? The child-gap target is reachable, with participation inside 2.5 per cent, when
omega = 0 participation is in [10.27, 10.79] per cent; omega then closes the moment."""
import json, numpy as np
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open('calibrated_stage2.json'))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
for kap in np.linspace(0.1188, 0.1206, 19):
    q = with_(par, kap=float(kap))
    c = stats(with_(q, omega=0.0)); m = stats(q)
    ok = 10.27 <= 100 * c['part'] <= 10.79
    print(f"kap {kap:.5f}  omega=0 part {100*c['part']:.3f}  base part {100*m['part']:.3f}  r_use {m['r_use']:.4f}  {'IN WINDOW' if ok else ''}", flush=True)
