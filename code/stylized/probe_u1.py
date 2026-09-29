"""Does the SUD share of the homeless rise with u1 in the staged model?

The author, 29 September: "if you raise u1 you will have more homeless with SUD,
that is a sure thing".  The 13 September evidence that it FALLS came from the
earlier model (income floor on, sr_calibrate's driver).  This measures it on stage 1
with the floor off, refitting b at every u1 so participation stays on its target,
which is how the calibration itself would see it.  Prints, per u1: participation,
the SUD share of the homeless, homelessness, the SUD rate, and users' income ratio.

usage:  STYLIZED_WORKERS=2 python3 probe_u1.py [stage]
"""
import sys
import stage_results as R
from stylized import with_
from calibrate import stats, bracket

stage = int(sys.argv[1]) if len(sys.argv) > 1 else 1
par, _ = R.load(stage)
par = with_(par, y_floor=0.0)
print(f'stage {stage}, y_floor 0, u0 {par.u0:.4f}; b refit on participation at every u1', flush=True)
# BOTH WAYS (the author, 29 September, on the claim that the share falls: "no way!
# you have to double check this").  HELD is u1's direct effect with nothing else
# moving; REFIT keeps participation on its target, which is how the calibration
# sees it.  If the two disagree in sign, the fall is a selection effect of the refit.
grid = sorted({round(par.u0 + 0.002, 4), round(par.u1, 4), 0.108, 0.16, 0.22, 0.30})
for mode in ('HELD', 'REFIT'):
    print(f'--- b {mode} ---', flush=True)
    for u1 in grid:
        q = with_(par, u1=u1)
        if mode == 'REFIT':
            q = with_(q, b=bracket(q, 'b', 'part', 1e-5, 20.0, iters=30))
        m = stats(q)
        print(f'{mode:5s} u1 {u1:.4f}  b {q.b:.5f}  part {100*m["part"]:5.2f}  SUD of homeless '
              f'{100*m["sud_of_homeless2"]:5.2f}  homeless {100*m["homeless"]:5.2f}  '
              f'SUD {100*m["sud"]:5.3f}  users/avg {m["r_use"]:.2f}', flush=True)
