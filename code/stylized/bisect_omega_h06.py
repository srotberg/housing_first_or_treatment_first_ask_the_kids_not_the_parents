"""omega_c onto its target (child_gap 0.1834) with everything else held at the stage 2
checkpoint, by bisection: the moment is monotone on the scanned interval."""
import json
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open('calibrated_stage2_h06_hold_osc.json'))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
base = stats(with_(par, omega=0.0))['part']
def gap(om):
    return base / stats(with_(par, omega=om))['part'] - 1.0
lo, hi = 0.00195, 0.00240
glo, ghi = gap(lo), gap(hi)
print(f'lo {lo:.6f} {glo:.4f}   hi {hi:.6f} {ghi:.4f}', flush=True)
assert glo < 0.1834 < ghi, 'target not bracketed'
for _ in range(14):
    mid = 0.5 * (lo + hi); g = gap(mid)
    print(f'omega {mid:.7f}  child_gap {g:.4f}  ({100*(g/0.1834-1):+.2f} per cent)', flush=True)
    if g < 0.1834: lo = mid
    else: hi = mid
print(f'OMEGA {0.5*(lo+hi):.7f}', flush=True)
