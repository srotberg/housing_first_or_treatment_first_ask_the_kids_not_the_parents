"""Food assistance AND the value-of-life bound on the lowest productivity, as the
quantitative model has both, and whether u1 then raises the SUD share of the homeless.

The author, 29 September: "maybe then we have to add food stamps... That bounds value of
life to be positive and still makes the lowest productivities use?", "Make sure that no
one has a negative value of life".  test_fs.py showed food stamps at the full model's
target (0.42 per cent of labour income) leave stage 1 with 2,884 negative cells, all at
productivity up to 0.21.  The quantitative model raises its lowest productivity node
while any household still prefers death (bottom_productivity_floor_rate); this does the
same: the income grid's truncation is raised in steps, sigma_y refitted to the bottom
half's 17.2 per cent, yV to half the median, and cbar (food assistance share), h1
(homelessness), kappa (users' income) and b (participation) refitted, until the strict
check finds no negative cell.  Then the band table and u1 + 0.03 with the same refit.
Log only.
usage:  STYLIZED_WORKERS=<n> python3 test_fs_bound.py stage [first TRUNC_FLOOR] [step] [psi]

psi (optional) sets the income-support replacement, the author, 29 September, on a
30-year spell of unemployment: the justifiable psi for the households at risk is about
0.15 to 0.25.  THE BOUND MAY NOT BE REACHABLE: with sigma_y refitted to keep the bottom
half's 17.2 per cent, the lowest productivity stopped rising near 0.24 in test_bottom.py.
If a step raises it by less than 0.002, or after 12 steps, the loop stops and says so.
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET
from negative_value_of_life import strict_negative_values

FS_TARGET = 0.0042
stage = int(sys.argv[1])
tf = float(sys.argv[2]) if len(sys.argv) > 2 else 2.2
step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
psi = float(sys.argv[4]) if len(sys.argv) > 4 else None


def set_grid(tf):
    C.TRUNC_FLOOR = tf
    C.SIG = C._solve_sig()
    C.YG, W0 = C._grid(C.SIG)
    C.EDGES = np.concatenate(([0.0], np.cumsum(W0)))
    C.W = W0 * len(W0)
    C.Q_F = C._ndtr((np.log(C._trunc_level(C.SIG, tf * ST.P().pr * ST.P().h2)) + 0.5 * C.SIG ** 2) / C.SIG)
    C.GRID_MEAN = (1.0 - C._tail_mean(C.SIG, C.Q_F)) / max(1.0 - C.Q_F, 1e-14)
    return 0.5 * C._median_of(C.YG, W0)


def with_b(q):
    return with_(q, b=bracket(q, 'b', 'part', 1e-5, 20.0, iters=22))


def fit(q, rounds=2):
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
    Y = np.asarray(C.YG); Wt = np.asarray(C.W) / np.sum(C.W); mid = np.cumsum(Wt) - Wt / 2
    tot = ST.aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF)
    print(f'  {tag}: u1 {q.u1:.4f}  SUD share of homeless {100*m["sud_of_homeless2"]:.2f}  '
          f'P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):.2f}  part {100*m["part"]:.2f}  '
          f'homeless {100*m["homeless"]:.3f}  r_use {m["r_use"]:.3f}  fshare {100*m["fshare"]:.3f}%', flush=True)
    for name, lo, hi in (('bottom 10%', 0, .10), ('10-25%', .10, .25), ('25-50%', .25, .50),
                         ('50-75%', .50, .75), ('top 25%', .75, 1.0)):
        mask = (mid >= lo) & (mid < hi)
        mb = ST.aggregates(q, C.YG, np.where(mask, C.W, 0.0), edges=C.EDGES, cdf=C.CDF)
        print(f'     {name:10s} y {Y[mask].min():.2f}-{Y[mask].max():.2f}  share of users '
              f'{100*mb["part"]*Wt[mask].sum()/tot["part"]:5.1f}%  use rate {100*mb["part"]:5.2f}%  '
              f'P(homeless|SUD) {100*mb["hl_sud"]/max(mb["sud"],1e-12):5.2f}%', flush=True)


par0, _ = R.load(stage)
if psi is not None:
    par0 = with_(par0, repl=psi)
    print(f'psi set to {psi}', flush=True)
q = par0
prev_bottom, steps, reached = -1.0, 0, True
while True:
    yV = set_grid(tf)
    steps += 1
    if C.YG.min() - prev_bottom < 0.002 or steps > 12:
        reached = False
        print(f'  BOUND NOT REACHABLE: the lowest productivity stopped rising at {C.YG.min():.3f} '
              f'(sigma_y {C.SIG:.4f}); continuing at this grid', flush=True)
        q = fit(with_(q, yV=yV))
        break
    prev_bottom = C.YG.min()
    print(f'TRUNC_FLOOR {tf:.2f}: lowest productivity {C.YG.min():.3f}, sigma_y {C.SIG:.4f}, '
          f'bottom-half share {100*C._bottom_half_share(C.SIG):.1f}%', flush=True)
    q = fit(with_(q, yV=yV))
    sv = strict_negative_values(ST.solve_child_damage(q))
    print(f'  STRICT value-of-life check: {sv["cells"]} negative cells; lowest {sv["lowest"]:.3f} '
          f'at {sv["where"]}', flush=True)
    if sv['cells'] == 0:
        break
    tf += step
sv0 = strict_negative_values(ST.solve_child_damage(q))
print(f'  BOUND {"REACHED" if reached else "NOT REACHED"} ({sv0["cells"]} negative cells): '
      f'lowest productivity {C.YG.min():.3f} (TRUNC_FLOOR {tf:.2f}); '
      f'PARAMS cbar {q.cbar:.6f} h1 {q.h1:.6f} kap {q.kap:.6f} b {q.b:.6f} sigma_y {C.SIG:.4f}', flush=True)
report('BASE', q)
q1 = fit(with_(q, u1=q.u1 + 0.03))
sv1 = strict_negative_values(ST.solve_child_damage(q1))
print(f'  STRICT value-of-life check at u1 + 0.03: {sv1["cells"]} negative cells', flush=True)
report('u1 + 0.03', q1)
