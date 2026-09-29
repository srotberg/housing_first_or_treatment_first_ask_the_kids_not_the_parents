"""Raise the bottom of the productivity distribution and ask whether u1 then raises the
SUD share of the homeless.  The author, 29 September: "maybe we need to lump the bottom
of the income distribution higher?", "if you raise the bottom productivity threshold,
then you'll have to refit h1 and b".

The grid is the lognormal truncated at TRUNC_FLOOR x the rent on the small unit (1.08,
so 0.108 of mean income).  Every income below 0.186 has a NEGATIVE value of life at some
asset level (stylized.py, y_floor note), and at the stage 2 calibration 62 per cent of
the bottom decile, 0.11-0.20, use.  Here the truncation is raised; sigma_y is refitted
to the bottom half's 17.2 per cent share, yV to half the median, and h1 (homelessness),
b (participation) and kappa (users' income) are refitted in turn.  Then u1 is raised by
0.03 with the same refit.  Stage 2 parameters as the start.  Nothing is written but the log.

usage:  STYLIZED_WORKERS=1 python3 test_bottom.py TRUNC_FLOOR
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET

tf = float(sys.argv[1])
C.TRUNC_FLOOR = tf
C.SIG = C._solve_sig()
C.YG, W0 = C._grid(C.SIG)
C.EDGES = np.concatenate(([0.0], np.cumsum(W0)))
C.W = W0 * len(W0)
C.Q_F = C._ndtr((np.log(C._trunc_level(C.SIG, tf * ST.P().pr * ST.P().h2)) + 0.5 * C.SIG ** 2) / C.SIG)
C.GRID_MEAN = (1.0 - C._tail_mean(C.SIG, C.Q_F)) / max(1.0 - C.Q_F, 1e-14)
yV = 0.5 * C._median_of(C.YG, W0)
par0, _ = R.load(2)
par0 = with_(par0, yV=yV)
print(f'TRUNC_FLOOR {tf}: bottom node {C.YG.min():.3f}, sigma_y {C.SIG:.4f}, '
      f'bottom-half share {100*C._bottom_half_share(C.SIG):.1f}, yV {yV:.4f}', flush=True)


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


def bands(q):
    q = ST.solve_child_damage(q)
    Y = np.asarray(C.YG); Wt = np.asarray(C.W) / np.sum(C.W); cum = np.cumsum(Wt)
    tot = ST.aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF)
    out = []
    for name, lo, hi in (('bottom 10%', 0, .10), ('10-25%', .10, .25), ('25-50%', .25, .50),
                         ('50-75%', .50, .75), ('top 25%', .75, 1.01)):
        mask = (cum > lo) & (cum - Wt < hi)
        m = ST.aggregates(q, C.YG, np.where(mask, C.W, 0.0), edges=C.EDGES, cdf=C.CDF)
        mass = Wt[mask].sum()
        out.append(f'     {name:10s} y {Y[mask].min():.2f}-{Y[mask].max():.2f}  users {100*m["part"]*mass/tot["part"]:5.1f}%  '
                   f'use rate {100*m["part"]:5.2f}  P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):5.2f}')
    return '\n'.join(out)


print('-- at stage 2 u1', flush=True)
q0 = fit(par0)
m0 = stats(q0)
print(f'  BASE u1 {q0.u1:.4f}: SUD share of homeless {100*m0["sud_of_homeless2"]:.2f}, '
      f'P(homeless|SUD) {100*m0["hl_sud"]/max(m0["sud"],1e-12):.2f}\n{bands(q0)}', flush=True)
print('-- u1 raised by 0.03', flush=True)
q1 = fit(with_(q0, u1=q0.u1 + 0.03), rounds=2)
m1 = stats(q1)
print(f'  HIGH u1 {q1.u1:.4f}: SUD share of homeless {100*m1["sud_of_homeless2"]:.2f}, '
      f'P(homeless|SUD) {100*m1["hl_sud"]/max(m1["sud"],1e-12):.2f}\n{bands(q1)}', flush=True)
