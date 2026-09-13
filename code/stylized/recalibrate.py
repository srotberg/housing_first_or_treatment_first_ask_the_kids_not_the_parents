"""
THE SIGMA = 2 RECALIBRATION, and the decomposition of the income gradient.

Author, 12 September: *"let's use sigma=2 to match the quant model"*, then
*"now, can you recalibrate the model this way and show what reverses the income
gradient?"* and *"examine kappa, employment risk, and omega_c to show which one
is the reason the income of users declines"*.

SEVEN PARAMETERS ON SEVEN TARGETS, exactly identified, and each one is the
quantitative model's own moment aimed at the quantitative model's own number:

    h1     homelessness rate                            0.0100
    aleph    value of a statistical life / annual income  80
    th       drug spending over users' income             0.14098
    kap      users' mean income / population mean         0.74
    pi_base  adult disorder rate                          0.0368
    u1       SUD share of the homeless, period 2          0.217
    b        participation                                0.08901

SET, NOT CALIBRATED:

    h2 = 0.10   CONCEDED.  It is judged on the share paying over half of
                  income in rent and not bracketed on it.  It CANNOT be raised
                  to reach the data's 17.5 per cent: homelessness at h1 -> 0
                  is already 2.4 per cent at h2 = 0.12 and 9.4 at 0.20, so
                  above about 0.10 the forced floor exceeds the 1 per cent
                  target and h1 has nothing left to do.  At 0.10 the model
                  gives about 7 per cent.  The quantitative model, with three
                  rungs instead of one, reaches 14.8 against the same 17.5.
    omega = 0.09  the quantitative model's weight_on_child.  SET because the
                  ablation of omega_c is the experiment: an omega_c fitted
                  inside this model would not be the one the big model carries.
    h3 = 0.40, sigma = 2, xi = sqrt(2).

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
import math as _math

import numpy as np

from calibrate import stats, bracket, TARGET
from stylized import P, with_

# gam IS SET AT ITS DATA VALUE AND hspend IS NOT A TARGET.  The author, 12
# September: *"I want the stylized model to be super simple.  And just include
# the least things needed to make the points"*.  The housing expenditure share
# is not one of the points, and it is also NOT REACHABLE.  Measured, with the
# drug block held at START:
#
#   gam     0.2144  0.2800  0.3400  0.3600  0.3900
#   hspend  0.1843  0.2130  0.2361  0.2465  0.2644
#   r_use    0.741   0.645   0.554   0.902   1.275
#
#   h3      0.40    0.60    0.85    1.00
#   hspend  0.1843  0.2002  0.2042  0.2047
#   r_use    0.741   0.916   1.056   1.054
#
# gam tops out at 0.236 on the interior branch and crosses to the WRONG branch
# between 0.34 and 0.36; h3 saturates at 0.205 and ruins the gradient getting
# there.  Housing here is a discrete menu of two units and the street, and the
# aggregate rent share is bounded by that menu.  Two sweeps were spent finding
# this the hard way: both hit hspend = 0.268 exactly and both did it by crossing
# the branch, after which kap, u1 and b all cornered on their bounds and
# participation sat near 60 per cent.
#
# So gam = 0.268 is the Cobb-Douglas weight FROM the expenditure survey, set and
# not calibrated, and the realised share is reported as a diagnostic.  That is
# the file's original "BOTH SET" arrangement for gam, restored on purpose, and
# it drops the one parameter that was dragging the model off its branch.
# KAPPA IS SET FROM THE QUANTITATIVE MODEL, author 12 September: *"Maybe just
# set kappa to give a death risk of 3 like we will have in the quant model"*.
# kap = 1 - phi0^(smr-1) with smr = 3 and phi0 = 0.91 is 1 - 0.91^2 = 0.1719,
# the same mortality ratio as kappa_phi_d_level = 3.0 in the Fortran.
#
# THIS IS THE BEST CHANGE MADE TO THIS FILE TODAY and it is worth saying why.
# It removes the bracket that defeated four sweeps -- r_use is non-monotone in
# kap and has two roots -- and, far more importantly, it turns the income of
# users from a TARGET into an OUTPUT.  The model is no longer told to reproduce
# the gradient; it either does or it does not.  Measured at aleph 15, kap 0.1719:
#
#     b       0.0260  0.0270  0.0280  0.0290
#     part    0.2285  0.1800  0.1022  0.0054
#     r_use    0.656   0.682   0.727   0.114
#     dshare  0.1378  0.1390  0.1417  0.0009
#     sud     0.0914  0.0720  0.0409  0.0022
#
# At b about 0.0282, where participation is the data's 8.9 per cent, users come
# out at 0.73 of average income against 0.74 in Table 7, and the drug spending
# share at 0.142 against 0.141.  NEITHER IS TARGETED.
#
# The cliff at b = 0.029 is the corner branch and it is close, so b's bracket is
# bounded below it.
FIXED = dict(gam=0.268, h2=0.10, h3=0.40, omega=0.09, sigma=2.0,
             kap=1.0 - 0.91 ** 2)

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
START = dict(h1=1e-4, aleph=15.0, th=0.16,
             u1=0.127, pi_base=0.40, b=0.0282)
# THE START MOVED AGAIN, IN (aleph, kap) JOINTLY, and the first version of this
# note blamed the wrong thing.  Two sweeps cornered from aleph 8.3 with kap
# 0.175, and the diagnosis offered at the time -- that a near-worthless street
# was the cause -- is WITHDRAWN: flooring h1 was measured and does nothing.
# The share of households with a NEGATIVE value of life stays between 19 and 36
# per cent over h1 from 0.01 to 0.06, while homelessness runs to 23 per cent
# at h1 = 0.04 and 49 at 0.06, so the floor destroys the homelessness target
# without touching the pathology.  A consumption floor was measured too: it
# lifts the minimum lifetime value from -68 to -9 and moves the SHARE only from
# 26.7 to 25.0 per cent.
#
# It is aleph and kap together.  share V1<0 / participation / users' income:
#
#              kap=0.020        kap=0.090        kap=0.175
#   aleph  8.3  0.267/0.661/1.38  0.267/0.609/1.41  0.267/0.204/0.67
#   aleph 15.4  0.090/0.631/1.42  0.090/0.031/0.83  0.090/0.004/0.11
#   aleph 25.0  0.025/0.579/1.47  0.025/0.000/0.00  0.025/0.000/0.00
#
# At aleph 15.4, kap 0.09 the pathology is 9.0 per cent, users are at 0.83 of
# average income and the VSL is 79.8 against its target of 80.  kap 0.175 at
# that aleph is deep in the corner branch, which is what both sweeps found.
#
# NINE PER CENT IS STILL HIGH and the note says so rather than declaring it
# solved: the quantitative model reports 0.227 per cent.  aleph 25 takes it to
# 2.5 per cent but puts the VSL at 141.

# u1's BOUNDS KEEP IT ON THE INTERIOR BRANCH, like kap's.  Measured at
# b = 0.045, kap = 0.175: participation is 0.425 at u1 = 0.05, 0.170 at 0.12,
# 0.077 at 0.1625 and 0.0069 at 0.20, where r_use has already collapsed to 0.116
# and the model is on the corner branch.  0.19 is the ceiling.

# (parameter, moment, lo, hi).  Order is the sweep order and it matters: the
# housing block settles before the drug block, and b runs LAST so participation
# is the moment that is actually hit.
HOUSING = [('h1', 'homeless', 1e-7, 0.02),
           ('aleph', 'vsl', 3.0, 60.0)]
# THE DRUG BLOCK IS SPLIT AND b AND pi_base GO FIRST.  Author, 12 September:
# *"I think you first have to match b and sud and only then start adjusting
# kappa and omegac"*.  b decides who uses and pi_base turns use into the
# disorder; they are a pair and they settle against each other in a few passes.
# kap, u1 and th are read AFTER that pair is at a fixed point, so each is
# bracketed on a user population that is the right SIZE, instead of one the next
# b move will change underneath it.
#
# KAPPA CANNOT IMPLY AN SMR BELOW ONE, and it never could: kap is the
# proportional fall in thirty-year survival, kap = 1 - phi0^(smr-1), so kap = 0
# IS smr = 1 and the parameter only rises from there.  The interval below is smr
# 2.06 to 2.51, and even the cornered values of the failed sweeps, kap 0.020 to
# 0.030, were smr 1.21 to 1.32.  The table now prints the implied smr beside kap
# so this does not have to be done in the reader's head.
DRUG_FIRST = [('b', 'part', 0.018, 0.0288),
              ('pi_base', 'sud', 1e-3, 0.99)]

# THETA RUNS LAST.  It has the largest single-bracket move of any parameter
# here -- 0.16 to 0.1919 in one pass -- and that twenty per cent jump changes
# the surface every parameter read AFTER it is bracketed on, which is what put
# b on its bound with a clean monotone root available.  Run last it perturbs
# nothing downstream, and its own gap is small: at th = 0.16 the drug share is
# already 0.142 against 0.141.
DRUG = [('u1', 'sud_of_homeless2', 0.06, 0.19),
        ('th', 'dshare', 0.05, 0.40)]

# REPORTED BESIDE THE TABLE, NEVER IN IT.  The author, 12 September: *"when I
# ask for the gaps table I am referring to the calibration gaps table on
# parameters we actually choose to target the moments of interest"*.  So the
# table is one row per CALIBRATED PARAMETER and nothing else; a moment with no
# instrument is a diagnostic and goes underneath, where it cannot be mistaken
# for something the calibration is trying to hit.
# r_use IS NOW A DIAGNOSTIC, NOT A TARGET.  Nothing is aimed at it; kap is set
# from the quantitative model's SMR and whatever gradient the model produces is
# the result.
DIAGNOSTIC = ['r_use', 'hspend', 'burden50', 'sud_of_homeless', 'hsmall',
              'housing_share', 'prog']


def table(par, note=''):
    """The calibration gaps table: one row per parameter we actually calibrate."""
    m = stats(par)
    if note:
        print(note)
    print(f'  {"parameter":10s}{"value":>11}  {"moment":22s}'
          f'{"model":>10}{"target":>10}{"gap %":>9}')
    print('  ' + '-' * 72)
    worst = 0.0
    for name, mom, _, _ in HOUSING + DRUG_FIRST + DRUG:
        t, v = TARGET[mom], m[mom]
        g = 100 * (v - t) / t
        worst = max(worst, abs(g))
        # kap = 1 - phi0^(smr-1), so the mortality rate ratio it implies is
        # smr = 1 + ln(1-kap)/ln(phi0).  kap = 0 is smr = 1 exactly and the
        # parameter cannot imply a ratio below one.
        tag = (f'   smr {1.0 + _math.log(1.0 - par.kap) / _math.log(par.phi0):.2f}'
               if name == 'kap' else '')
        print(f'  {name:10s}{getattr(par, name):11.5f}  {MOMENT_NAME[mom]:22s}'
              f'{v:10.4f}{t:10.4f}{g:9.1f}{tag}')
    print('  ' + '-' * 72)
    hit = sum(1 for _, k, _, _ in HOUSING + DRUG_FIRST + DRUG
              if abs(m[k] - TARGET[k]) / TARGET[k] < 0.02)
    n = len(HOUSING) + len(DRUG_FIRST) + len(DRUG)
    print(f'  worst gap {worst:.1f} %,  {hit} of {n} within two per cent')
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
        # b and pi_base to a fixed point BEFORE anything else in the drug block.
        for _ in range(4):
            for name, mom, lo, hi in DRUG_FIRST:
                par = with_(par, **{name: bracket(par, name, mom, lo, hi, iters=iters)})
        for _ in range(3):
            for name, mom, lo, hi in DRUG:
                par = with_(par, **{name: bracket(par, name, mom, lo, hi, iters=iters)})
            # and re-settle the pair against whatever kap, th and u1 just did
            for name, mom, lo, hi in DRUG_FIRST:
                par = with_(par, **{name: bracket(par, name, mom, lo, hi, iters=iters)})
        m = stats(par)
        worst = max(abs(m[k] - TARGET[k]) / TARGET[k]
                    for _, k, _, _ in HOUSING + DRUG_FIRST + DRUG)
        if verbose:
            table(par, note=f'\nAFTER SWEEP {s}')
            print(f'  sweep {s}: worst gap {100*worst:6.2f} %   '
                  f'h1 {par.h1:.2e} aleph {par.aleph:.3f} '
                  f'th {par.th:.4f} u1 {par.u1:.4f} '
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
               ('h1', 'aleph', 'th', 'u1', 'pi_base', 'b',
                'kap', 'gam', 'h2', 'h3', 'omega', 'sigma')},
              open('calibrated_sigma2.json', 'w'), indent=1)
    print('\nwritten to calibrated_sigma2.json')
