"""Does u1 raise the SUD share of the homeless once a household with a SUD that loses its
job draws no unemployment insurance?

The author, 29 September: "we need u1 to raise homelessness sud", "Make UI for those with
Sud 0", "you may need food stamps for 0 asset, 0 income case.. So keep the food stamps",
and "You can just set psi =0.5. It's ok. And go back to 0.1 and 0.4 for h2 and h3".
Specification: repl (psi) 0.5, ui_sud 0 (no insurance with a SUD), food stamps fitted to
0.42 per cent of labour income (the full model's target), h2 0.10, h3 0.40.  At each u1
the model is refitted from calibrated_stage1.json: cbar on the food stamp share, gamma on
housing spending, h1 on homelessness, u0 on the unemployment rate (4.85 per cent, the SUD households'
u1 included, as sr_calibrate.moments counts it), aleph on the value of a statistical life,
and kappa on users' income with b refit on participation inside every kappa trial; three
rounds.

THE VALUE-OF-LIFE BOUND IS ON PERIOD 1 (the author, 29 September: "no household in period
1 of life has a negative value of life. It is ok if it is negative in period 2").  The
fit runs first on the calibrated grid (lowest income 0.108).  If any period-1 state has a
negative lifetime value, the grid's lowest income is
raised as the quantitative model's bottom_productivity_floor_rate does, with sigma_y
refitted to the bottom half's 17.2 per cent, to TRUNC_FLOOR 2.4, lowest income 0.235,
which is as high as it goes with that share held (test_fs_bound.py), and the fit reruns.

THE GRADIENT CHECK, Figure 1's unemployment channel (the author: "check that raising u1
above u0 does not reverse the income gradient... even with 0 Income").  At the fitted
point the mortality penalty is switched off (kappa = 0) and u1 is set to u0, 0.10, 0.20,
0.30 and 0.50 in turn, b refitted each time to the point's participation, h1 held, as
run._scaled does.  Users' income over the average must stay above one: below one, the
unemployment channel alone has moved use to the bottom, which the paper says only the
mortality penalty does.

theta (drug spending share) is held, so this is a test, not the calibration.  Reports who uses by income band, P(homeless | SUD) by band, the SUD share
of the homeless, and both value-of-life checks: every cell (strict) and the cells
households actually occupy.  Log only.

usage:  STYLIZED_WORKERS=<n> python3 scan_u1_uninsured.py ui_sud u1 [u1 ...]
        ui_sud 0 is the rule, 1 is the model without it
needs numpy (pip install numpy scipy matplotlib in a fresh container)
"""
import sys
import numpy as np
import calibrate as C
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import stats, bracket, TARGET
from negative_value_of_life import (strict_negative_values, occupied_negative_values,
                                   period1_negative_values)

ui_sud = float(sys.argv[1]) if __name__ == '__main__' else 0.0
u1s = [float(x) for x in sys.argv[2:]] if __name__ == '__main__' else []
FS_TARGET = 0.0042
SPEC = dict(repl=0.5, ui_sud=ui_sud, cbar=0.077, h2=0.10, h3=0.40)


def set_grid(tf):
    """The income grid truncated at tf times the rent on the default small unit, sigma_y
    refitted to the bottom half's share; returns the means test, half of median income."""
    C.TRUNC_FLOOR = tf
    C.SIG = C._solve_sig()
    C.YG, W0 = C._grid(C.SIG)
    C.EDGES = np.concatenate(([0.0], np.cumsum(W0)))
    C.W = W0 * len(W0)
    C.Q_F = C._ndtr((np.log(C._trunc_level(C.SIG, tf * ST.P().pr * ST.P().h2)) + 0.5 * C.SIG ** 2) / C.SIG)
    C.GRID_MEAN = (1.0 - C._tail_mean(C.SIG, C.Q_F)) / max(1.0 - C.Q_F, 1e-14)
    return 0.5 * C._median_of(C.YG, W0)


def unemployment_u0(q):
    """u0 so that (1 - SUD) u0 + SUD u1 = 4.85 per cent, sr_calibrate's moment."""
    for _ in range(3):
        s = stats(q)['sud']
        q = with_(q, u0=max((0.0485 - s * q.u1) / max(1.0 - s, 1e-9), 0.001))
    return q


def with_b(q):
    return with_(q, b=bracket(q, 'b', 'part', 1e-5, 0.6, iters=16))


def fit(q, rounds=3):
    for r in range(rounds):
        q = with_(q, cbar=bracket(q, 'cbar', 'fshare', 1e-4, 0.6, iters=16, tgt=FS_TARGET))
        q = with_(q, gam=bracket(q, 'gam', 'hspend', 0.02, 0.70, iters=16))
        q = with_(q, h1=bracket(q, 'h1', 'homeless', 1e-6, 0.049, iters=18))
        q = unemployment_u0(q)
        q = with_(q, aleph=bracket(q, 'aleph', 'vsl', 3.0, 60.0, iters=16))
        lo, hi = 0.3 * q.kap, 3.0 * q.kap
        for _ in range(12):
            mid = np.sqrt(lo * hi)
            if stats(with_b(with_(q, kap=mid)))['r_use'] > TARGET['r_use']:
                lo = mid
            else:
                hi = mid
        q = with_b(with_(q, kap=np.sqrt(lo * hi)))
        m = stats(q)
        print(f'   round {r}: cbar {q.cbar:.4f} fshare {100*m["fshare"]:.3f}% gam {q.gam:.4f} h1 {q.h1:.6f} u0 {q.u0:.4f} aleph {q.aleph:.3f} '
              f'kap {q.kap:.4f} b {q.b:.5f} | hspend {100*m["hspend"]:.1f} homeless {100*m["homeless"]:.3f} '
              f'unemp {100*((1-m["sud"])*q.u0+m["sud"]*q.u1):.2f} vsl {m["vsl"]:.1f} r_use {m["r_use"]:.3f} '
              f'part {100*m["part"]:.2f} SUD share of homeless {100*m["sud_of_homeless2"]:.2f}', flush=True)
    return q


def report(q):
    q = ST.solve_child_damage(q)
    m = stats(q)
    Y = np.asarray(C.YG); Wt = np.asarray(C.W) / np.sum(C.W); mid = np.cumsum(Wt) - Wt / 2
    tot = ST.aggregates(q, C.YG, C.W, edges=C.EDGES, cdf=C.CDF)
    print(f'  RESULT ui_sud {q.ui_sud:g} u1 {q.u1:.3f} (u0 {q.u0:.4f}): SUD share of homeless '
          f'{100*m["sud_of_homeless2"]:.2f} (target {100*TARGET["sud_of_homeless2"]:.1f})  '
          f'P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):.2f}  homeless {100*m["homeless"]:.3f}  '
          f'part {100*m["part"]:.2f}  SUD {100*m["sud"]:.2f}  r_use {m["r_use"]:.3f}  '
          f'hsmall {100*m["hsmall"]:.1f}', flush=True)
    for name, lo, hi in (('bottom 10%', 0, .10), ('10-25%', .10, .25), ('25-50%', .25, .50),
                         ('50-75%', .50, .75), ('top 25%', .75, 1.0)):
        mask = (mid >= lo) & (mid < hi)
        mb = ST.aggregates(q, C.YG, np.where(mask, C.W, 0.0), edges=C.EDGES, cdf=C.CDF)
        print(f'     {name:10s} y {Y[mask].min():.2f}-{Y[mask].max():.2f}  share of users '
              f'{100*mb["part"]*Wt[mask].sum()/tot["part"]:5.1f}%  use rate {100*mb["part"]:5.2f}%  '
              f'P(homeless|SUD) {100*mb["hl_sud"]/max(mb["sud"],1e-12):5.2f}%', flush=True)
    print(f'  grid: lowest income {C.YG[0]:.3f}, sigma_y {C.SIG:.4f}, means test yV {q.yV:.4f}', flush=True)
    neg1 = 0
    for pol in ('HF', 'TF'):
        v1 = period1_negative_values(q, pol)
        neg1 += v1['cells']
        print(f'  PERIOD 1 value of life (the requirement), {pol}: {v1["cells"]} negative states holding '
              f'{100*v1["share"]:.3f}% of households; lowest {v1["lowest"]:.3f} at {v1["where"]}; '
              f'lowest before the draws {v1["lowest_ex_ante"]:.3f} at y {v1["lowest_ex_ante_y"]:.3f}',
              flush=True)
    sv = strict_negative_values(q)
    print(f'  period 2, every cell (information): {sv["cells"]} negative; lowest {sv["lowest"]:.3f} at {sv["where"]}',
          flush=True)
    for pol in ('HF', 'TF'):
        ov = occupied_negative_values(q, pol)
        print(f'  period 2, occupied (information), {pol}: {ov["cells"]} negative cells holding '
              f'{100*ov["share"]:.3f}% of period-2 households; lowest {ov["lowest"]:.3f} at {ov["where"]}',
              flush=True)
    print(f'  PARAMS ' + ' '.join(f'{k} {getattr(q, k):.6g}' for k in
                                  ('repl', 'ui_sud', 'cbar', 'h2', 'h3', 'gam', 'h1', 'u0', 'u1',
                                   'aleph', 'kap', 'b', 'th', 'yV')), flush=True)
    return neg1


def gradient_check(q):
    """Figure 1's unemployment channel alone: kappa 0, u1 raised, b refit, h1 held."""
    ref = stats(q)['part']
    print(f'  GRADIENT CHECK (mortality off, b refit to participation {100*ref:.2f}): '
          "users' income / average must stay above 1", flush=True)
    for u1 in (q.u0, 0.10, 0.20, 0.30, 0.50):
        g = with_(q, kap=0.0, u1=u1)
        g = with_(g, b=bracket(g, 'b', 'part', 1e-5, 20.0, iters=30, tgt=ref))
        m = stats(g)
        print(f'     u1 {u1:.3f}: users income / average {m["r_use"]:.3f} '
              f'({"REVERSED" if m["r_use"] < 1.0 else "not reversed"})  participation {100*m["part"]:.2f}  '
              f'SUD share of homeless {100*m["sud_of_homeless2"]:.2f}', flush=True)


if __name__ == '__main__':
    par0, _ = R.load(1)
    print(f'stage 1 start; set {SPEC}; u1 values {u1s}', flush=True)
    q = with_(par0, **SPEC)
    for u1 in u1s:
        print(f'--- u1 {u1}, calibrated grid', flush=True)
        set_grid(1.08)
        qa = fit(with_(q, u1=u1, yV=par0.yV))
        neg = report(qa)
        gradient_check(qa)
        if neg > 0:
            print(f'--- u1 {u1}, lowest income raised (TRUNC_FLOOR 2.4)', flush=True)
            qb = fit(with_(qa, yV=set_grid(2.4)))
            report(qb)
            gradient_check(qb)
