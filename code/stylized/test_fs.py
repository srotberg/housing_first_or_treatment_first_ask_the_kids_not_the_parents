"""Food assistance in the stylized model, as in the quantitative one, and whether u1 then
raises the SUD share of the homeless.  The author, 29 September: "maybe then we have to
add food stamps... That bounds value of life to be positive and still makes the lowest
productivities use?", "Calibrate the food stamps to match the same target in the full
model" (food_stamps_share_data = 0.0042, food stamp spending over labour income).

From the calibrated stage, cbar is fitted to fshare, h1 to homelessness, and kappa to
users' income with b refit on participation inside every kappa trial; three rounds.
Reports the negative-value-of-life share, who uses by income band, and the SUD share of
the homeless; then raises u1 by 0.03 with the same refit.  Log only.
usage:  STYLIZED_WORKERS=1 python3 test_fs.py stage
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET
from negative_value_of_life import negative_value_share

FS_TARGET = 0.0042
stage = int(sys.argv[1])
par0, _ = R.load(stage)


def with_b(q):
    return with_(q, b=bracket(q, 'b', 'part', 1e-5, 20.0, iters=22))


def fit(q, rounds=3):
    for r in range(rounds):
        q = with_(q, cbar=bracket(q, 'cbar', 'fshare', 1e-4, 0.6, iters=22, tgt=FS_TARGET))
        q = with_(q, h1=bracket(q, 'h1', 'homeless', 1e-4, 0.0999, iters=22))
        lo, hi = 0.3 * q.kap, 3.0 * q.kap
        for _ in range(18):
            mid = np.sqrt(lo * hi)
            if stats(with_b(with_(q, kap=mid)))['r_use'] > TARGET['r_use']:
                lo = mid
            else:
                hi = mid
        q = with_b(with_(q, kap=np.sqrt(lo * hi)))
        m = stats(q)
        print(f'   round {r}: cbar {q.cbar:.5f} h1 {q.h1:.5f} kap {q.kap:.5f} b {q.b:.5f}  '
              f'fshare {100*m["fshare"]:.3f}% part {100*m["part"]:.2f} homeless {100*m["homeless"]:.3f} '
              f'r_use {m["r_use"]:.3f} SUD share of homeless {100*m["sud_of_homeless2"]:.2f}', flush=True)
    return q


def report(tag, q):
    q = ST.solve_child_damage(q)
    m = stats(q)
    nv = negative_value_share(q)
    Y = np.asarray(C.YG); Wt = np.asarray(C.W) / np.sum(C.W); mid = np.cumsum(Wt) - Wt / 2
    tot = ST.aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF)
    print(f'  {tag}: u1 {q.u1:.4f}  SUD share of homeless {100*m["sud_of_homeless2"]:.2f}  '
          f'P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):.2f}  negative value of life '
          f'{100*nv["share"]:.2f}% (lowest {nv["lowest"]:.2f})  fshare {100*m["fshare"]:.3f}%', flush=True)
    for name, lo, hi in (('bottom 10%', 0, .10), ('10-25%', .10, .25), ('25-50%', .25, .50),
                         ('50-75%', .50, .75), ('top 25%', .75, 1.0)):
        mask = (mid >= lo) & (mid < hi)
        mb = ST.aggregates(q, C.YG, np.where(mask, C.W, 0.0), edges=C.EDGES, cdf=C.CDF)
        print(f'     {name:10s} y {Y[mask].min():.2f}-{Y[mask].max():.2f}  share of users '
              f'{100*mb["part"]*Wt[mask].sum()/tot["part"]:5.1f}%  use rate {100*mb["part"]:5.2f}%  '
              f'P(homeless|SUD) {100*mb["hl_sud"]/max(mb["sud"],1e-12):5.2f}%', flush=True)


print(f'stage {stage}: food assistance on, taper {par0.rho_fs}, target {100*FS_TARGET:.2f}% of labour income', flush=True)
q0 = fit(par0)
report('BASE', q0)
print(f'  PARAMS cbar {q0.cbar:.6f} h1 {q0.h1:.6f} kap {q0.kap:.6f} b {q0.b:.6f}', flush=True)
q1 = fit(with_(q0, u1=q0.u1 + 0.03), rounds=2)
report('u1 + 0.03', q1)
