"""The old stage-1 stylized model (housing, shelter, UI, food assistance, vouchers), calibrated_stage1.json,
with saving switched off (one asset level, zero), and Figure 1's two scans: each channel 0 to 200 per cent of its
calibrated value with the other switched off, b refit to the calibrated participation. Printed, not drawn."""
import sys, time
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import numpy as np
import stages, stage_results as SR, run
from stylized import with_
from calibrate import stats
run.OTHER_CHANNEL = 'off'
base = SR.load(1)[0]
mode = sys.argv[1]
if mode == 'nosave':
    base = with_(base, na=1)
m = stats(base)
run.PART_REF = float(m['part'])
print(f'{mode}: calibrated point part={m["part"]:.4f} r_use={m["r_use"]:.3f} homeless={m["homeless"]:.4f}', flush=True)
for which in ('mortality', 'unemployment'):
    for s in (0.0, 0.5, 1.0, 1.5, 2.0):
        t = time.time()
        q = run._scaled(base, which, s)
        mm = stats(q)
        print(f'{mode} {which:12s} {100*s:4.0f}%  r_use={mm["r_use"]:.3f}  part={mm["part"]:.4f}  ({time.time()-t:.0f}s)', flush=True)
