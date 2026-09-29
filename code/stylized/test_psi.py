"""A lower income-support replacement psi, with b recalibrated, and whether u1 then raises
the SUD share of the homeless.  No food stamps (the author, 29 September: "I rather not have
the food stamps if it's not critical. I want to make the model simple").

The author: "Is there a way to justify a lower psi? Because unemployment benefits pay only
during the first 6-9 months", and on the scan that held b fixed: "But if drug use falls, you
have to calibrate b to match use".  From the calibrated stage, psi is set, then h1
(homelessness), and kappa (users' income) with b refit on participation inside every kappa
trial, over three rounds.  Reports who uses by income band, the strict value-of-life check,
the SUD share of the homeless, then u1 + 0.03 with the same refit.  Log only.
usage:  STYLIZED_WORKERS=<n> python3 test_psi.py stage psi
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET
from negative_value_of_life import strict_negative_values

stage, psi = int(sys.argv[1]), float(sys.argv[2])
par0, _ = R.load(stage)


def with_b(q):
    return with_(q, b=bracket(q, 'b', 'part', 1e-5, 20.0, iters=22))


def fit(q, rounds=3):
    for r in range(rounds):
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
        print(f'   round {r}: h1 {q.h1:.5f} kap {q.kap:.5f} b {q.b:.5f}  part {100*m["part"]:.2f} '
              f'homeless {100*m["homeless"]:.3f} r_use {m["r_use"]:.3f} '
              f'SUD share of homeless {100*m["sud_of_homeless2"]:.2f}', flush=True)
    return q


def report(tag, q):
    q = ST.solve_child_damage(q)
    m = stats(q)
    sv = strict_negative_values(q)
    Y = np.asarray(C.YG); Wt = np.asarray(C.W) / np.sum(C.W); mid = np.cumsum(Wt) - Wt / 2
    tot = ST.aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF)
    print(f'  {tag}: psi {q.repl:.2f} u1 {q.u1:.4f}  SUD share of homeless {100*m["sud_of_homeless2"]:.2f}  '
          f'P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):.2f}  part {100*m["part"]:.2f}  '
          f'homeless {100*m["homeless"]:.3f}  r_use {m["r_use"]:.3f}', flush=True)
    print(f'  STRICT value-of-life check: {sv["cells"]} negative cells; lowest {sv["lowest"]:.3f} '
          f'at {sv["where"]}', flush=True)
    for name, lo, hi in (('bottom 10%', 0, .10), ('10-25%', .10, .25), ('25-50%', .25, .50),
                         ('50-75%', .50, .75), ('top 25%', .75, 1.0)):
        mask = (mid >= lo) & (mid < hi)
        mb = ST.aggregates(q, C.YG, np.where(mask, C.W, 0.0), edges=C.EDGES, cdf=C.CDF)
        print(f'     {name:10s} y {Y[mask].min():.2f}-{Y[mask].max():.2f}  share of users '
              f'{100*mb["part"]*Wt[mask].sum()/tot["part"]:5.1f}%  use rate {100*mb["part"]:5.2f}%  '
              f'P(homeless|SUD) {100*mb["hl_sud"]/max(mb["sud"],1e-12):5.2f}%', flush=True)


print(f'stage {stage}: psi {psi} (from {par0.repl}), no food stamps', flush=True)
q0 = fit(with_(par0, repl=psi))
report('BASE', q0)
print(f'  PARAMS h1 {q0.h1:.6f} kap {q0.kap:.6f} b {q0.b:.6f}', flush=True)
q1 = fit(with_(q0, u1=q0.u1 + 0.03), rounds=2)
report('u1 + 0.03', q1)
