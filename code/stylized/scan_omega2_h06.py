"""omega_c's moment over a wider range at a stage 2 checkpoint (argv[1]), everything
else held: where it jumps, and whether a smooth stretch crosses the target 0.1834."""
import json, sys, numpy as np
import stages
from stylized import P, with_
from calibrate import stats
v = json.load(open(sys.argv[1]))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
base = stats(with_(par, omega=0.0))['part']
print(f'{sys.argv[1]}: omega = 0 participation {100*base:.3f}', flush=True)
for om in np.linspace(0.0015, 0.0025, 21):
    m = stats(with_(par, omega=float(om)))
    g = base / m['part'] - 1.0
    print(f'omega {om:.5f}  part {100*m["part"]:.3f}  child_gap {g:.4f}  ({100*(g/0.1834-1):+.1f})', flush=True)
