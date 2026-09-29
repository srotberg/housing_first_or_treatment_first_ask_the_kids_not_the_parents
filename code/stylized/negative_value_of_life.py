#!/usr/bin/env python3
"""WHY THE POOREST HOUSEHOLDS BUY AN INFINITESIMAL AMOUNT OF DRUG.

The author asked what the optimal SUD rate is at omega_c = 1 and expected it to
be near zero.  The model says 3.1 per cent.  This is why, and the answer is a
defect rather than economics.

THE MEASUREMENT, instrumenting period1's own call to _branch rather than
reconstructing it -- a reconstruction was tried first and disagreed with
period1 on all 408 states, so nothing built on it could be trusted:

    state inc = 0.10804, a' = 0, pi(floor) = 0.4183

      v = 0      flow -32.266474 + continuation -8.749330
      v = floor  flow -32.266604 + continuation -8.335905

The flow is IDENTICAL to five decimals -- buying 1e-6 of income changes nothing
a household can taste.  The CONTINUATION is better by 0.41.  Backing the
period-2 values out of the continuation array that period1 actually passed:

      s0 * W2_clean-but-used  = -8.749330   s0 = 0.9100   W2 = -9.6146
      s1 * W2_disordered      = -7.760914   s1 = 0.8034   W2 = -9.6606

BOTH VALUES ARE NEGATIVE.  Being alive in period 2 is worth less than not
being, for this household.  The disorder makes the STATE slightly worse, -9.66
against -9.61, exactly as intended -- and it cuts survival from 0.91 to 0.80,
and multiplying a NEGATIVE number by a SMALLER survival probability makes it
LESS NEGATIVE.  Acquiring the disorder is therefore worth +0.99.

So the household buys the smallest sliver of drug the grid sells, not for the
drug, but to purchase a 41.8 per cent chance of dying sooner.  aleph, the value
of life, is 10.62 per period and is what should prevent this; on the street at
h = 0.0095 with income 0.108 it is not nearly enough.

WHAT THIS EXPLAINS.  The "corner branch" that has dominated a day of
calibration is this mechanism at scale: it is why the drug share collapses to
the grid floor EXACTLY, why participation survives while the quantity vanishes,
and why the corner arrives precisely as omega_c rises -- a larger child term
makes the flow more negative and pushes more households below zero.

AND IT CORRECTS AN EARLIER CLAIM IN THIS REPOSITORY'S RECORD.  These households
were described as "choosing a dominated infinitesimal".  They are not choosing
a dominated action: given a negative continuation the choice is strictly
optimal.  What is wrong is the negative continuation.

THE QUANTITATIVE MODEL HAS THE SAME DEFECT AND ALREADY WATCHES FOR IT.  It
prints DIAG share with a NEGATIVE value of life every loop.  Measured in the
archive: 0.45 per cent in worker_6344102474, a healthy run, with the lowest
value of a period of life at -34,108 against an aleph of 203.8; and 89.04 per
cent in worker_e12c3d0657, the run whose labour income tax was set to zero,
where the lowest reads -1.6e10.  The stylized model had no such diagnostic,
which is the only reason this took a day to find.  This script is that
diagnostic.
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import stylized as S
from stylized import with_, P
from recalibrate import FIXED
import calibrate as C


def negative_value_share(par):
    """Share of period-2 states, by population mass, whose value is negative,
    with the worst value and the population mean beside it."""
    neg = tot = acc = 0.0
    lo = float('inf')
    for j, y in enumerate(C.YG):
        _, W2c, *_ = S.solve_period2(par, y, None, used=0)
        for p, inc, rmul in S._states(par, 0, None, y, used=0):
            if p <= 1e-14:
                continue
            w = W2c[:, 0]
            m = C.W[j] * p
            tot += m
            neg += m * float((w < 0).mean())
            acc += m * float(w.mean())
            lo = min(lo, float(w.min()))
    return dict(share=neg / tot, lowest=lo, mean=acc / tot)



def strict_negative_values(par, policies=('HF', 'TF')):
    """THE STRICT CHECK, the author, 29 September: "Make sure that no one has a negative
    value of life".  negative_value_share above looks at clean households' period-2
    values only.  This looks at every income node, every asset level, with and without
    the disorder (d = 0, 1), after using or not in period 1 (the used argument), under
    each policy.  Returns the number of negative (node, asset, d, used, policy) cells,
    the worst value and where it is.  Zero cells is the requirement."""
    n = 0
    worst = (float('inf'), None)
    for pol in policies:
        for used in (0, 1):
            for y in C.YG:
                ag, W2, *_ = S.solve_period2(par, float(y), pol, used=used)
                for d in (0, 1):
                    w = W2[:, d]
                    n += int((w < 0).sum())
                    k = int(np.argmin(w))
                    if w[k] < worst[0]:
                        worst = (float(w[k]), dict(y=float(y), a=float(ag[k]), d=d, used=used, policy=pol))
    return dict(cells=n, lowest=worst[0], where=worst[1])


def occupied_negative_values(par, policy='HF'):
    """THE OCCUPIED CHECK: the strict check restricted to period-2 states households
    actually reach.  Each period-1 state's own choice (use or not, a') is followed into
    period 2, with d drawn from the onset hazard and survival applied, so a cell counts
    only if it carries mass.  The strict check also counts cells nobody is in, such as
    a SUD at an income where nobody uses, or zero assets where every user saves; with
    no unemployment insurance under a SUD, an unemployed household at zero assets has
    nothing to consume and its value is minus infinity there.  Returns the number of
    occupied negative cells, their share of period-2 households, and the worst one."""
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
    tot = neg = 0.0
    n = 0
    worst = (float('inf'), None)
    for j, y in enumerate(C.YG):
        ag, W2c, *_ = S.solve_period2(par, float(y), policy, used=0)
        W2u = W2c if policy == 'HF' else S.solve_period2(par, float(y), policy, used=1)[1]
        for p, gain, v, ru, rn, inc, own in S.period1(par, float(y), policy):
            if p <= 1e-14:
                continue
            if gain > 0.0:
                pid = float(S._pid(par, v))
                k = int(np.argmin(np.abs(ag - ru[0])))
                cells = ((W2u[k, 1], p * pid * s1, 1, 1), (W2u[k, 0], p * (1.0 - pid) * s0, 0, 1))
            else:
                k = int(np.argmin(np.abs(ag - rn[0])))
                cells = ((W2c[k, 0], p * s0, 0, 0),)
            for w, m, d, used in cells:
                m *= C.W[j]
                if m <= 0.0:
                    continue
                tot += m
                if w < 0.0:
                    neg += m
                    n += 1
                    if w < worst[0]:
                        worst = (float(w), dict(y=float(y), a=float(ag[k]), d=d, used=used, inc=float(inc)))
    return dict(cells=n, share=neg / max(tot, 1e-300), lowest=worst[0], where=worst[1])

if __name__ == '__main__':
    d = json.load(open('best_vector_it1800.json'))
    kw = {k: v for k, v in FIXED.items()
          if k not in ('kap', 'gam', 'omega', 'sigma')}
    kw.update(d['_held_not_calibrated']); kw.update(d['parameters'])
    base = with_(P(), **kw)
    r = negative_value_share(base)
    print(f"share of period-2 states with a NEGATIVE value of life: "
          f"{100*r['share']:.2f} per cent")
    print(f"lowest value of a period of life: {r['lowest']:.4f}")
    print(f"population mean:                  {r['mean']:.4f}")
    print(f"aleph, for scale:                 {base.aleph:.4f}")
    print("\nThe quantitative model's counterpart, DIAG share with a NEGATIVE")
    print("value of life, reads 0.45 per cent on a healthy run and 89.04 on the")
    print("run whose labour income tax was zeroed.")
