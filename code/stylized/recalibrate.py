"""
THE SIGMA = 2 RECALIBRATION, and the decomposition of the income gradient.

Author, 12 September: *"let's use sigma=2 to match the quant model"*, then
*"now, can you recalibrate the model this way and show what reverses the income
gradient?"* and *"examine kappa, employment risk, and omega_c to show which one
is the reason the income of users declines"*.

SEVEN PARAMETERS ON SEVEN TARGETS, exactly identified, and each one is the
quantitative model's own moment aimed at the quantitative model's own number:

    gam      housing over expenditure net of drugs        0.268
    h_hl     homelessness rate                            0.0100
    aleph    value of a statistical life / annual income  80
    th       drug spending over users' income             0.14098
    kap      users' mean income / population mean         0.74
    pi_base  adult disorder rate                          0.0368
    u1       SUD share of the homeless, period 2          0.217
    b        participation                                0.08901

SET, NOT CALIBRATED:

    h_sm = 0.10   CONCEDED.  It is judged on the share paying over half of
                  income in rent and not bracketed on it.  It CANNOT be raised
                  to reach the data's 17.5 per cent: homelessness at h_hl -> 0
                  is already 2.4 per cent at h_sm = 0.12 and 9.4 at 0.20, so
                  above about 0.10 the forced floor exceeds the 1 per cent
                  target and h_hl has nothing left to do.  At 0.10 the model
                  gives about 7 per cent.  The quantitative model, with three
                  rungs instead of one, reaches 14.8 against the same 17.5.
    omega = 0.09  the quantitative model's weight_on_child.  SET because the
                  ablation of omega_c is the experiment: an omega_c fitted
                  inside this model would not be the one the big model carries.
    h_lg = 0.40, sigma = 2, xi = sqrt(2).

BOUNDS ARE NOT DEFAULTS.  kap is bounded at 0.185 because the model has TWO
BRANCHES in it and the bracket must stay on the interior one.  Measured, at
b = 0.045, aleph = 8.3, th = 0.16, raising kap:

    kap     0.150  0.160  0.170  0.180  0.190
    r_use   0.841  0.830  0.809  0.658  0.121
    dshare  0.125  0.126  0.127  0.123  0.0009

Past about 0.185 every user goes to the corner v = 0, participation is whoever
is left, and r_use collapses to 0.12 with a drug spending share of one tenth of
one per cent.  That is a different regime, not a worse fit, and a bisection
allowed to cross into it reports a number that means nothing.  The target of
0.74 sits INSIDE the interior branch, between kap 0.17 and 0.18, but the branch
only spans r_use in [0.66, 0.85] before it falls away, so the calibration is on
a narrow ridge and the note says so rather than hiding it.
"""
import json
import numpy as np

from calibrate import stats, bracket, TARGET
from stylized import P, with_

FIXED = dict(h_sm=0.10, h_lg=0.40, omega=0.09, sigma=2.0)

# u1's BOUNDS KEEP IT ON THE INTERIOR BRANCH, like kap's.  Measured at
# b = 0.045, kap = 0.175: participation is 0.425 at u1 = 0.05, 0.170 at 0.12,
# 0.077 at 0.1625 and 0.0069 at 0.20, where r_use has already collapsed to 0.116
# and the model is on the corner branch.  0.19 is the ceiling.

# (parameter, moment, lo, hi).  Order is the sweep order and it matters: the
# housing block settles before the drug block, and b runs LAST so participation
# is the moment that is actually hit.
HOUSING = [('gam', 'hspend', 0.02, 0.70),
           ('h_hl', 'homeless', 1e-7, 0.05),
           ('aleph', 'vsl', 1.0, 40.0)]
DRUG = [('th', 'dshare', 0.05, 0.40),
        ('kap', 'r_use', 0.03, 0.185),
        ('u1', 'sud_of_homeless2', 0.06, 0.19),
        ('pi_base', 'sud', 1e-3, 0.99),
        ('b', 'part', 0.020, 0.090)]

SHOW = ['hspend', 'homeless', 'vsl', 'dshare', 'r_use', 'sud_of_homeless2',
        'sud', 'part', 'burden50', 'sud_of_homeless', 'hsmall',
        'housing_share', 'prog']


def table(par, note=''):
    m = stats(par)
    print(f'  {"moment":14s}{"model":>10}{"target":>10}{"gap %":>9}   {note}')
    for k in SHOW:
        t = TARGET.get(k)
        if t is None:
            print(f'  {k:14s}{m[k]:10.4f}{"-":>10}{"-":>9}   not targeted')
        else:
            print(f'  {k:14s}{m[k]:10.4f}{t:10.4f}{100*(m[k]-t)/t:9.1f}')
    return m


def calibrate(par, sweeps=6, verbose=True):
    for s in range(sweeps):
        for name, mom, lo, hi in HOUSING:
            par = with_(par, **{name: bracket(par, name, mom, lo, hi)})
        # The drug block is alternated to a fixed point, as the old sweep did
        # for (lam, b): theta sets how much a user buys, kap decides who is
        # willing to buy at all and therefore their income, pi_base turns use
        # into the disorder, and b decides participation.  All four move each
        # other's moments.
        for _ in range(4):
            for name, mom, lo, hi in DRUG:
                par = with_(par, **{name: bracket(par, name, mom, lo, hi)})
        m = stats(par)
        worst = max(abs(m[k] - TARGET[k]) / TARGET[k] for _, k, _, _ in HOUSING + DRUG)
        if verbose:
            print(f'  sweep {s}: worst gap {100*worst:6.2f} %   '
                  f'gam {par.gam:.4f} h_hl {par.h_hl:.2e} aleph {par.aleph:.3f} '
                  f'th {par.th:.4f} kap {par.kap:.4f} u1 {par.u1:.4f} '
                  f'pi {par.pi_base:.4f} b {par.b:.5f}')
        if worst < 0.02:
            break
    return par


if __name__ == '__main__':
    par = with_(P(), **FIXED)
    print('CALIBRATING at sigma = 2')
    par = calibrate(par)
    print()
    print('BASELINE')
    table(par)
    json.dump({k: getattr(par, k) for k in
               ('gam', 'h_hl', 'aleph', 'th', 'kap', 'u1', 'pi_base', 'b',
                'h_sm', 'h_lg', 'omega', 'sigma')},
              open('calibrated_sigma2.json', 'w'), indent=1)
    print('\nwritten to calibrated_sigma2.json')
