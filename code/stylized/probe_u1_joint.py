"""Does the SUD share of the homeless rise with u1 when the CALIBRATION's other
instruments move with it?

The author, 29 September (second time): "there is too few homeless with SUD in the
stage 2 calibration, which says that u1 has to rise....and if drug use is too low,
then you need to let b drop further!"  probe_u1.py refit b alone and held kap, so
users' income ran from 0.15 to 0.95 of the average along its u1 grid: it read the
share off economies whose users were a different slice of the income distribution.
The calibration holds that slice too -- kap is bracketed on users' income at 0.74 --
so this refits kap on r_use, with b refit on participation inside every kap trial,
and reads the share at each u1.

usage:  STYLIZED_WORKERS=1 python3 probe_u1_joint.py [stage] [u1 ...]
"""
import sys
import numpy as np
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET

stage = int(sys.argv[1]) if len(sys.argv) > 1 else 2
par, _ = R.load(stage)
grid = [float(x) for x in sys.argv[2:]] or [par.u0 + 1e-4, 0.055, 0.065, 0.0765, 0.09, 0.11]
print(f'stage {stage}: u0 {par.u0:.5f}, calibrated u1 {par.u1:.5f} kap {par.kap:.5f} b {par.b:.5f}; '
      f'kap refit on r_use {TARGET["r_use"]}, b refit on participation inside it', flush=True)


def with_b(q):
    return with_(q, b=bracket(q, 'b', 'part', 1e-5, 20.0, iters=22))


for u1 in grid:
    q0 = with_(par, u1=u1)
    lo, hi = 0.5 * par.kap, 2.0 * par.kap
    for _ in range(18):
        mid = np.sqrt(lo * hi)
        # r_use FALLS in kap (mortality pushes use to the bottom)
        if stats(with_b(with_(q0, kap=mid)))['r_use'] > TARGET['r_use']:
            lo = mid
        else:
            hi = mid
    for k in (lo, hi):
        q = with_b(with_(q0, kap=k))
        m = stats(q)
        print(f'u1 {u1:.4f}  kap {k:.5f}  b {q.b:.5f}  part {100*m["part"]:5.2f}  r_use {m["r_use"]:.3f}  '
              f'SUD of homeless {100*m["sud_of_homeless2"]:5.2f}  homeless {100*m["homeless"]:5.3f}  '
              f'SUD {100*m["sud"]:5.3f}', flush=True)
