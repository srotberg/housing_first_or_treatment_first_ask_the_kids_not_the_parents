"""omega_c onto child_gap 0.1834 at a stage 2 checkpoint (argv[1]), everything else held.
Scans for a bracket first (the moment is not smooth everywhere), then bisects it."""
import json, sys, numpy as np
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open(sys.argv[1]))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
base = stats(with_(par, omega=0.0))['part']
T = 0.1834
def gap(om):
    return base / stats(with_(par, omega=om))['part'] - 1.0
grid = np.linspace(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else np.linspace(0.0014, 0.0022, 17)
vals = [(float(o), gap(float(o))) for o in grid]
for o, g in vals:
    print(f'omega {o:.5f}  child_gap {g:.4f}  ({100*(g/T-1):+.1f})', flush=True)
br = [(a, b) for (a, ga), (b, gb) in zip(vals, vals[1:]) if (ga - T) * (gb - T) <= 0]
print('brackets:', [(round(a, 5), round(b, 5)) for a, b in br], flush=True)
if not br:
    sys.exit('no crossing of the target on the grid')
lo, hi = br[0]; glo = gap(lo)
for _ in range(14):
    mid = 0.5 * (lo + hi); g = gap(mid)
    if (g - T) * (glo - T) > 0: lo, glo = mid, g
    else: hi = mid
    print(f'  omega {mid:.7f}  child_gap {g:.4f}  ({100*(g/T-1):+.2f})', flush=True)
print(f'OMEGA {0.5*(lo+hi):.7f}', flush=True)
