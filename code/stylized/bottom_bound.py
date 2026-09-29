"""Raise the lowest income ONLY AS FAR AS NEEDED for no household to have a negative value
of life at the drug decision, and see whether homelessness still hits its target there.

The author, 29 September: "raise the bottom only as much as needed", after the lowest
income raised straight to 0.235 (TRUNC_FLOOR 2.4, the most the bottom half's 17.2 per
cent allows) took homelessness to 0.32 per cent against 0.6 with h1 near the top of its
range: the households who cannot pay the rent when unemployed are most of the homeless,
and raising the bottom removes them.  The requirement is the period-1 value
("What matters is what happens before the decision to use drugs"; period 2 may be
negative): period1_negative_values under both policies.

Specification as scan_u1_uninsured.py: psi 0.5, h2 0.10, h3 0.40, food stamps fitted to
0.42 per cent of labour income, no unemployment insurance with a SUD.  At every trial
bottom the full refit of that script runs (cbar, gamma, h1, u0, aleph, kappa with b
inside), warm-started from the last one.  The bottom is bisected in TRUNC_FLOOR between
1.08 (the calibrated grid, lowest income 0.108) and 2.4, four steps, after checking that
2.4 passes at all.

u1 is either held (a number) or FITTED ('fit') on the SUD share of the homeless, 21.7 per
cent, with b refit on participation at every trial, inside each round of the fit.

usage:  STYLIZED_WORKERS=<n> python3 bottom_bound.py <u1 | fit>
"""
import sys
import numpy as np
import calibrate as C
import stage_results as R
from stylized import with_
from calibrate import stats, TARGET
import scan_u1_uninsured as SC
from negative_value_of_life import period1_negative_values

mode = sys.argv[1]
FIT_U1 = mode == 'fit'


def fit_u1(q, iters=12):
    """u1 on the SUD share of the homeless, b refit at every trial; direction read off the
    endpoints, and the nearer endpoint kept, with a warning, if the target is outside."""
    def share(v):
        return stats(SC.with_b(with_(q, u1=v)))['sud_of_homeless2']
    lo, hi = q.u0 + 1e-3, 0.50
    s_lo, s_hi = share(lo), share(hi)
    tgt = TARGET['sud_of_homeless2']
    print(f'     u1 bracket: share {100*s_lo:.2f} at u1 {lo:.4f}, {100*s_hi:.2f} at {hi:.2f} '
          f'(target {100*tgt:.1f}; {"RISES" if s_hi > s_lo else "FALLS"} in u1)', flush=True)
    if (s_lo - tgt) * (s_hi - tgt) > 0:
        v = lo if abs(s_lo - tgt) < abs(s_hi - tgt) else hi
        print(f'     TARGET OUTSIDE the bracket; u1 kept at {v:.4f}', flush=True)
        return SC.with_b(with_(q, u1=v))
    rising = s_hi > s_lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if (share(mid) > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return SC.with_b(with_(q, u1=0.5 * (lo + hi)))


def full_fit(q, rounds=3):
    for r in range(rounds):
        q = SC.fit(q, rounds=1)
        if FIT_U1:
            q = SC.unemployment_u0(fit_u1(q))
            m = stats(q)
            print(f'     after u1: u1 {q.u1:.4f} u0 {q.u0:.4f} SUD share of homeless '
                  f'{100*m["sud_of_homeless2"]:.2f} homeless {100*m["homeless"]:.3f} part {100*m["part"]:.2f}',
                  flush=True)
    return q


def trial(q, tf):
    yV = SC.set_grid(tf)
    q = full_fit(with_(q, yV=yV))
    neg = sum(period1_negative_values(q, pol)['cells'] for pol in ('HF', 'TF'))
    m = stats(q)
    print(f'  TRIAL TRUNC_FLOOR {tf:.3f}: lowest income {C.YG[0]:.4f}  period-1 negative states {neg}  '
          f'homeless {100*m["homeless"]:.3f} (target {100*TARGET["homeless"]:.2f}) h1 {q.h1:.5f}  '
          f'u1 {q.u1:.4f}  SUD share of homeless {100*m["sud_of_homeless2"]:.2f}', flush=True)
    return q, neg


par0, _ = R.load(1)
q0 = with_(par0, **SC.SPEC, u1=0.10 if FIT_U1 else float(mode))
print(f'bottom bound; spec {SC.SPEC}; u1 {"FITTED on the SUD share" if FIT_U1 else mode}', flush=True)
q_lo, n_lo = trial(q0, 1.08)
if n_lo == 0:
    print('  the calibrated grid already passes; nothing to raise', flush=True)
    best, tf_best = q_lo, 1.08
else:
    q_hi, n_hi = trial(q_lo, 2.4)
    if n_hi > 0:
        print('  BOUND NOT REACHABLE: period-1 values are still negative at TRUNC_FLOOR 2.4', flush=True)
        best, tf_best = q_hi, 2.4
    else:
        lo, hi, best, tf_best = 1.08, 2.4, q_hi, 2.4
        for _ in range(4):
            mid = 0.5 * (lo + hi)
            qm, nm = trial(best, mid)
            if nm == 0:
                hi, best, tf_best = mid, qm, mid
            else:
                lo = mid
        print(f'  LOWEST BOTTOM THAT PASSES: TRUNC_FLOOR {tf_best:.3f} (fails at {lo:.3f})', flush=True)
SC.set_grid(tf_best)
print(f'--- final point, TRUNC_FLOOR {tf_best:.3f}', flush=True)
SC.report(best)
SC.gradient_check(best)
