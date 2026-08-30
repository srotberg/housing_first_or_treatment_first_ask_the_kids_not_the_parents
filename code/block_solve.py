#!/usr/bin/env python3
"""Solve the whole coupled block at once: nine moments on eight instruments.

THE AUTHOR, 29 AUGUST 23:00: "You need to then optimize all of these params
together. Like 7-8 of them and keep the rest constant. Because if you do a few
at a time you can't get them all at once."

THE MEASUREMENT THAT PROVED IT. A point launched purely to diagnose
unemployment -- probability_becoming_unemployed from 0.0228 to 0.001, nothing
else touched -- moved lambda_d by +289 per cent, to within 15 of its target and
the second best it has ever been, and b by +145, tau_u by +229, kappa_uem by
+182, kappa_ued by -91, lambda_m by -81. The separation rate is not a repair to
apply after the drug block is set; it is one of the largest instruments ON it,
because unemployment is what makes drug use affordable.

So the two-stage plan cannot hold, and neither can any pairwise one. Every
two-parameter solve today succeeded on its own pair and was undone by the
coordinate it was holding fixed:

    lambda and addiction_scalar_1 alone   -> b and lambda_d bracketed, but
                                             tau_u went to +205
    discount factor for b                 -> diluted the ratio by a quarter
    p_eu alone                            -> fixed pi_eu, moved lambda_d 289

THE BLOCK. Eight parameters, nine moments, everything else frozen:

    lambda_addiction                        -> lambda_d
    addiction_scalar_1                      -> b
    probability_becoming_unemployed         -> pi_eu
    utility_cost_of_treatment               -> tau_u
    relative_share_of_addiction_1           -> theta
    size_homelessness                       -> h_1
    kappa_uem                               -> kappa_uem (employment given SMI)
    multiple_of_probabilities_of_employment_if_addicted -> kappa_ued
                                            -> aleph rides along, overidentified

The arrows are a reading aid, not the method: the whole 9x8 is solved at once
in least squares, because the pairing is exactly the assumption that has failed
all day.

WHY LEAST SQUARES AND NOT A SQUARE SOLVE. Nine moments on eight instruments is
overidentified by one, which is deliberate -- aleph has no instrument of its own
here and the fit should be told about it rather than left to discover it. The
residual on aleph after a solve is then a diagnostic: large means the block
cannot hold it and value_of_life has to come in as a ninth.

THE STEP IS BOUNDED HARD AND FOR A REASON. Every aimed step today missed --
a b interpolation by a factor of four, a ratio by five, a b prediction at
lambda 21.4 by 3.2 -- while every wide bracket worked. An eight dimensional
Newton step from a first-order fit of a model whose elasticities change SIGN
between regions is not to be trusted far. MAX_EFOLD caps each coordinate's
move, and the design measures a LADDER along the solved direction rather than
its endpoint, so the step length is chosen by measurement rather than by faith
in the linearisation.
"""
import argparse
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_points                                      # noqa: E402
from converge import BOUNDS                              # noqa: E402

PARAMS = [
    'lambda_addiction',
    'addiction_scalar_1',
    'probability_becoming_unemployed',
    'utility_cost_of_treatment',
    'relative_share_of_addiction_1',
    'size_homelessness',
    'kappa_uem',
    'multiple_of_probabilities_of_employment_if_addicted',
]
MOMENTS = ['b', 'lambda_d', 'pi_eu', 'tau_u', 'theta',
           'h_1', 'kappa_uem', 'kappa_ued', 'aleph']

# Which instrument the model's own comments say owns which moment. Used ONLY to
# label the diagnostic; the solve uses the whole matrix and assumes no pairing.
OWN = {'lambda_addiction': 'lambda_d',
       'addiction_scalar_1': 'b',
       'probability_becoming_unemployed': 'pi_eu',
       'utility_cost_of_treatment': 'tau_u',
       'relative_share_of_addiction_1': 'theta',
       'size_homelessness': 'h_1',
       'kappa_uem': 'kappa_uem',
       'multiple_of_probabilities_of_employment_if_addicted': 'kappa_ued'}

# Weight the three that have blocked the calibration all day. This is not the
# paper's loss -- it is the direction chooser, and it should spend its
# conditioning on the moments that have never come right.
WEIGHT = {'lambda_d': 3.0, 'b': 3.0, 'pi_eu': 3.0, 'tau_u': 2.0, 'theta': 2.0}

# A point is in the fit if it is within this many e-folds of the centre in
# every varying coordinate. Beyond that the model is a different animal: the
# ratio's elasticity in b changes sign between lambda 11.8 and lambda 30.
BANDWIDTH = 1.2
RIDGE = 0.05
MAX_EFOLD = 1.10
LADDER = (0.10, 0.28, 0.55, 1.00)


def points():
    out = []
    for fn in sorted(os.listdir(os.path.join(HERE, 'points'))):
        if not fn.startswith('point_') or fn.endswith('.FAILED.txt'):
            continue
        p = os.path.join(HERE, 'points', fn)
        txt = open(p, errors='replace').read()
        m = re.search(r'^VECTOR (.*)$', txt, re.M)
        if not m:
            continue
        _h, mt = score_points.read(p)
        if not mt or not all(k in mt for k in MOMENTS):
            continue
        # theta returns -1 when the using population is empty. That is a
        # sentinel, not a measurement, and fitting it as a value would tell the
        # regression that drug spending goes negative.
        if mt['theta'][0] < 0 or mt['b'][0] <= 0:
            continue
        vec = {}
        for tok in m.group(1).split():
            k, v = tok.split('=', 1)
            vec[k] = float(v)
        if any(vec.get(k, 0) <= 0 for k in PARAMS):
            continue
        out.append((vec, mt, fn))
    return out


def local(centre, pts):
    """The DESIGN ONLY: the centre, and points differing from it in ONE coordinate.

    THIS WAS A BANDWIDTH FILTER AND THE BANDWIDTH WAS NOT THE PROBLEM. Fitting
    every archive point within 1.2 e-folds put roughly a hundred points into the
    regression, and in every one of them all twenty-odd parameters differ at
    once. That is the same confounding that has produced five wrong answers
    today -- lambda's sign, addiction_scalar_1's sign, the discount factor's
    effect on the ratio, pi_eu's elasticity at 0.125 against a true 0.78, and an
    SMI decomposition that reconstructed a moment exactly and predicted nothing.

    It showed up here as a flat contradiction. The single clean arm on
    utility_cost_of_treatment -- one coordinate, 0.4 e-folds, everything else
    identical -- measures d log tau_u / d log cost = -1.344. The pooled local
    fit over the same neighbourhood returned -0.009, an instrument that looks
    dead. The arm is right and the pool is confounded, and a solve that believed
    the pool would have concluded tau_u had no instrument and spent its step
    elsewhere.

    So the fit uses the design and nothing else. That is what the design is FOR:
    each arm moves one coordinate, so each column of the Jacobian is identified
    by construction rather than by hoping the archive happens to span it. It
    costs statistical power -- twelve points for eight columns -- and buys the
    only thing that matters here, which is that the columns mean what they say.
    """
    keep = []
    for vec, mt, name in pts:
        if any(k not in vec for k in PARAMS):
            continue
        moved = [k for k in centre
                 if k in vec and abs(vec[k] - centre[k]) > 1e-12 * max(1.0, abs(centre[k]))]
        if len(moved) <= 1:
            d = max([abs(math.log(vec[k] / centre[k])) for k in PARAMS] + [0.0])
            keep.append((vec, mt, name, d))
    return keep


def fit(centre, fam):
    """Weighted log-log regression of every block moment on every instrument."""
    X, Y = [], []
    for vec, mt, _n, _d in fam:
        X.append([math.log(vec[k] / centre[k]) for k in PARAMS])
        Y.append([math.log(mt[k][0]) for k in MOMENTS])
    X, Y = np.array(X), np.array(Y)
    if len(X) < len(PARAMS) + 1:
        return None, f'need {len(PARAMS)+1} points near the centre, have {len(X)}'
    dead = [PARAMS[j] for j in range(len(PARAMS)) if np.ptp(X[:, j]) < 1e-9]
    if dead:
        return None, 'these do not vary in the family: ' + ', '.join(dead)
    A = np.column_stack([np.ones(len(X)), X])
    J, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return (J[0], J[1:].T), None       # intercepts, and d log moment / d log param


def solve(centre, mt0, fam, verbose=True):
    got, why = fit(centre, fam)
    if got is None:
        print('cannot fit:', why)
        return None
    f0, Jm = got
    want = np.array([math.log(mt0[k][1]) for k in MOMENTS])
    have = np.array([math.log(mt0[k][0]) for k in MOMENTS])
    w = np.array([WEIGHT.get(k, 1.0) for k in MOMENTS])
    W = np.diag(w)
    # Gauss-Newton on the residual AT THE CENTRE, not at the fit's intercept:
    # the fit is a local approximation and the centre is measured, so anchoring
    # on the measurement is strictly better information.
    r = want - have
    d = np.linalg.solve(Jm.T @ W @ Jm + RIDGE * np.eye(len(PARAMS)), Jm.T @ W @ r)
    if verbose:
        print(f'fit over {len(fam)} points within {BANDWIDTH} e-folds\n')
        # PAIR BY NAME, NOT BY POSITION. MOMENTS and PARAMS are not in the
        # same order -- b belongs to addiction_scalar_1 and lambda_d to
        # lambda_addiction, which are the first two of each list crossed over --
        # so zipping them by index printed cross elasticities under the
        # heading "own". The fit and the solve were always right; the label was
        # not, and a mislabelled diagnostic is worse than none.
        print('  own-instrument elasticities, paired by name:')
        for par, mom in OWN.items():
            if par in PARAMS and mom in MOMENTS:
                print(f'    d log {mom:10} / d log {par[:34]:34} = '
                      f'{Jm[MOMENTS.index(mom), PARAMS.index(par)]:+.3f}')
        print(f'\n  residual to close, in logs, weighted:')
        for i, k in enumerate(MOMENTS):
            print(f'    {k:11} {100*(math.exp(r[i])-1):+7.0f}%   weight {w[i]:.0f}')
        n = float(np.max(np.abs(d)))
        print(f'\n  raw step, largest coordinate {n:.3f} e-folds:')
        for j, k in enumerate(PARAMS):
            print(f'    {k[:38]:38} x{math.exp(d[j]):.4f}')
    return d


def emit(centre, d, out):
    lines = []
    n = float(np.max(np.abs(d)))
    u = d / n if n > 0 else d
    for t in LADDER:
        v = dict(centre)
        for j, k in enumerate(PARAMS):
            x = centre[k] * math.exp(t * MAX_EFOLD * u[j])
            lo, hi = BOUNDS.get(k, (1e-30, 1e30))
            v[k] = min(max(x, lo), hi)
        lines.append('bash code/run_one_point.sh ' +
                     ' '.join(f'{k}={v[k]:.7g}' for k in sorted(v)))
    open(os.path.join(HERE, out), 'w').write('\n'.join(lines) + '\n')
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--centre', required=True)
    ap.add_argument('--out', default='BLOCK.txt')
    ap.add_argument('--design', action='store_true',
                    help='emit a one-arm-per-parameter design instead of a step')
    a = ap.parse_args()
    p = os.path.join(HERE, 'points', a.centre)
    txt = open(p, errors='replace').read()
    centre = {}
    for tok in re.search(r'^VECTOR (.*)$', txt, re.M).group(1).split():
        k, v = tok.split('=', 1)
        centre[k] = float(v)
    _h, mt0 = score_points.read(p)
    print(f'centre {a.centre}')
    for k in MOMENTS:
        m, t = mt0[k]
        print(f'   {k:11} {m:11.5f}  target {t:9.4f}   {100*(m-t)/t:+6.0f}%')
    print()

    if a.design:
        # ONE ARM PER PARAMETER, both directions on the three that have blocked
        # everything. A Jacobian over eight instruments needs nine points to be
        # determined and is worthless at exactly nine, so this is eleven.
        two_sided = {'lambda_addiction', 'addiction_scalar_1',
                     'probability_becoming_unemployed'}
        lines = []
        for k in PARAMS:
            for s in ((+1, -1) if k in two_sided else (+1,)):
                v = dict(centre)
                x = centre[k] * math.exp(s * 0.40)
                lo, hi = BOUNDS.get(k, (1e-30, 1e30))
                v[k] = min(max(x, lo), hi)
                if abs(v[k] - centre[k]) < 1e-12 * max(1.0, centre[k]):
                    print(f'   {k} pinned at a bound in the {"+" if s>0 else "-"} direction, arm dropped')
                    continue
                lines.append('bash code/run_one_point.sh ' +
                             ' '.join(f'{kk}={v[kk]:.7g}' for kk in sorted(v)))
        open(os.path.join(HERE, a.out), 'w').write('\n'.join(lines) + '\n')
        print(f'wrote {len(lines)} design points to {a.out}')
        return 0

    pts = points()
    fam = local(centre, pts)
    d = solve(centre, mt0, fam)
    if d is None:
        return 1
    lines = emit(centre, d, a.out)
    print(f'\nwrote {len(lines)} points to {a.out} '
          f'-- a LADDER along the solved direction, not its endpoint')
    return 0


if __name__ == '__main__':
    sys.exit(main())
