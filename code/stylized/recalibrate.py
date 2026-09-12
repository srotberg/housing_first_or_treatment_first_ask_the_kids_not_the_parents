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

# THE STARTING POINT IS NOT A DETAIL, IT PICKS THE BRANCH.  Started from the log
# model's calibrated values the first sweep failed outright: the housing block
# runs first, it was bracketed at drug parameters that put every household on
# drugs, so gam and aleph were fitted to a nonsense economy and the whole model
# came to rest on the WRONG BRANCH -- participation 66 per cent, users RICHER
# than average at r_use 1.36 -- with four of the eight parameters cornered on
# their bounds trying to climb back.  Worst gap 645 per cent.
#
# These values come from the scans in the commit that built this file and they
# are on the interior branch: r_use 0.7406 against 0.740 and the SUD share of
# the homeless 0.2150 against 0.217 before a single bracket has run, with
# participation, the disorder rate, the housing share and the VSL the four that
# still need closing.
START = dict(gam=0.2144, h_hl=1e-4, aleph=8.3, th=0.16,
             kap=0.175, u1=0.127, pi_base=0.40, b=0.045)

# u1's BOUNDS KEEP IT ON THE INTERIOR BRANCH, like kap's.  Measured at
# b = 0.045, kap = 0.175: participation is 0.425 at u1 = 0.05, 0.170 at 0.12,
# 0.077 at 0.1625 and 0.0069 at 0.20, where r_use has already collapsed to 0.116
# and the model is on the corner branch.  0.19 is the ceiling.

# (parameter, moment, lo, hi).  Order is the sweep order and it matters: the
# housing block settles before the drug block, and b runs LAST so participation
# is the moment that is actually hit.
HOUSING = [('gam', 'hspend', 0.05, 0.60),
           ('h_hl', 'homeless', 1e-7, 0.02),
           ('aleph', 'vsl', 3.0, 60.0)]
DRUG = [('th', 'dshare', 0.05, 0.40),
        ('kap', 'r_use', 0.03, 0.185),
        ('u1', 'sud_of_homeless2', 0.06, 0.19),
        ('pi_base', 'sud', 1e-3, 0.99),
        ('b', 'part', 0.020, 0.090)]

# REPORTED BESIDE THE TABLE, NEVER IN IT.  The author, 12 September: *"when I
# ask for the gaps table I am referring to the calibration gaps table on
# parameters we actually choose to target the moments of interest"*.  So the
# table is one row per CALIBRATED PARAMETER and nothing else; a moment with no
# instrument is a diagnostic and goes underneath, where it cannot be mistaken
# for something the calibration is trying to hit.
DIAGNOSTIC = ['burden50', 'sud_of_homeless', 'hsmall', 'housing_share', 'prog']


def table(par, note=''):
    """The calibration gaps table: one row per parameter we actually calibrate."""
    m = stats(par)
    if note:
        print(note)
    print(f'  {"parameter":10s}{"value":>11}  {"moment":22s}'
          f'{"model":>10}{"target":>10}{"gap %":>9}')
    print('  ' + '-' * 72)
    worst = 0.0
    for name, mom, _, _ in HOUSING + DRUG:
        t, v = TARGET[mom], m[mom]
        g = 100 * (v - t) / t
        worst = max(worst, abs(g))
        print(f'  {name:10s}{getattr(par, name):11.5f}  {MOMENT_NAME[mom]:22s}'
              f'{v:10.4f}{t:10.4f}{g:9.1f}')
    print('  ' + '-' * 72)
    hit = sum(1 for _, k, _, _ in HOUSING + DRUG
              if abs(m[k] - TARGET[k]) / TARGET[k] < 0.02)
    print(f'  worst gap {worst:.1f} %,  {hit} of {len(HOUSING) + len(DRUG)}'
          f' within two per cent')
    print('\n  not targeted, reported only:')
    for k in DIAGNOSTIC:
        print(f'  {"":10s}{"":11s}  {MOMENT_NAME.get(k, k):22s}{m[k]:10.4f}')
    return m


MOMENT_NAME = {
    'hspend': 'housing / expenditure', 'homeless': 'homelessness rate',
    'vsl': 'VSL / annual income', 'dshare': 'drug spending share',
    'r_use': "users' income / mean", 'sud_of_homeless2': 'SUD share of homeless',
    'sud': 'disorder rate', 'part': 'participation',
    'burden50': 'rent over half income', 'sud_of_homeless': 'SUD of homeless, both',
    'hsmall': 'housed in small unit', 'housing_share': 'housing / income',
    'prog': 'use that becomes SUD'}


def calibrate(par, sweeps=8, verbose=True, iters=16):
    # 16 BISECTIONS, NOT 34.  Geometric bisection narrows the interval by 2^n, so
    # 16 is a factor of 65536 on every bracket, far finer than any moment's
    # tolerance, and it halves the wall clock of a sweep.  34 was inherited and
    # was buying nothing.
    for s in range(sweeps):
        for name, mom, lo, hi in HOUSING:
            par = with_(par, **{name: bracket(par, name, mom, lo, hi, iters=iters)})
        # The drug block is alternated to a fixed point, as the old sweep did
        # for (lam, b): theta sets how much a user buys, kap decides who is
        # willing to buy at all and therefore their income, pi_base turns use
        # into the disorder, and b decides participation.  All four move each
        # other's moments.
        for _ in range(4):
            for name, mom, lo, hi in DRUG:
                par = with_(par, **{name: bracket(par, name, mom, lo, hi, iters=iters)})
        m = stats(par)
        worst = max(abs(m[k] - TARGET[k]) / TARGET[k] for _, k, _, _ in HOUSING + DRUG)
        if verbose:
            table(par, note=f'\nAFTER SWEEP {s}')
            print(f'  sweep {s}: worst gap {100*worst:6.2f} %   '
                  f'gam {par.gam:.4f} h_hl {par.h_hl:.2e} aleph {par.aleph:.3f} '
                  f'th {par.th:.4f} kap {par.kap:.4f} u1 {par.u1:.4f} '
                  f'pi {par.pi_base:.4f} b {par.b:.5f}')
        if worst < 0.02:
            break
    return par


if __name__ == '__main__':
    par = with_(P(), **FIXED, **START)
    print('CALIBRATING at sigma = 2, from the interior-branch start')
    par = calibrate(par)
    print()
    print('BASELINE')
    table(par)
    json.dump({k: getattr(par, k) for k in
               ('gam', 'h_hl', 'aleph', 'th', 'kap', 'u1', 'pi_base', 'b',
                'h_sm', 'h_lg', 'omega', 'sigma')},
              open('calibrated_sigma2.json', 'w'), indent=1)
    print('\nwritten to calibrated_sigma2.json')
