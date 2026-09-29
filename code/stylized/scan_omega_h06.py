"""Stage 2 at 0.6 per cent homelessness: omega_c's moment on a fine grid between the
two values the proportional rule bounced between (0.00177 at -18 per cent, 0.00186 at
+31 per cent), everything else held at the checkpoint. child_gap is participation at
omega = 0 over participation at omega, less one (sr_calibrate's definition); the
omega = 0 side does not depend on omega, so it is solved once."""
import json, numpy as np
import stages, sr_calibrate as S
from stylized import P, with_
from calibrate import stats
v = json.load(open('calibrated_stage2_h06_hold_osc.json'))
par = with_(P(), **{k: x for k, x in v.items() if not k.startswith('_')})
cf = stats(with_(par, omega=0.0))
print(f"omega = 0: part {100*cf['part']:.3f}", flush=True)
for om in np.linspace(0.00170, 0.00195, 11):
    m = stats(with_(par, omega=float(om)))
    gap = cf['part'] / m['part'] - 1.0 if m['part'] > 0 else float('nan')
    print(f"omega {om:.6f}  part {100*m['part']:.3f}  dshare {m['dshare']:.4f}  child_gap {gap:.4f}  "
          f"(target 0.1834, {100*(gap/0.1834-1):+.1f} per cent)", flush=True)
