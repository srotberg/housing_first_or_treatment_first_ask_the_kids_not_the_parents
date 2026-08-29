#!/usr/bin/env python3
"""Solve b and lambda_d alone, on two instruments, with everything else frozen.

THE AUTHOR'S DESIGN, 29 AUGUST: fix all the other parameters, find the pair that
puts b and lambda_d on their targets, and only then go back and adjust the rest.
This file is the first half. alternate.py phase B is the second.

WHY A TWO PARAMETER SOLVE IS THE RIGHT SHAPE HERE, AND THE TWENTY PARAMETER ONE
WAS NOT. Five cycles of the alternating search moved lambda_d from -81 per cent
to -78. The reason was never the optimiser: lambda_addiction was confined to
4.51 to 6.93, and the disordered share of users does not move inside that window
at all. Outside it the moment moves immediately -- at lambda 30 the share is
0.434 against 0.414 in the data, on target at the first try. So this is not a
hard search problem, it is a two dimensional root find that was being attempted
with the wrong bracket.

THE SYSTEM. Two targets, two instruments, and they are triangular:

    lambda_addiction  ->  the RATIO lambda_d/b     (corr +0.19; and -0.36 on b)
    discount_factor   ->  b                        (corr -0.94; only +0.18 on the ratio)

Lambda sets the ratio and knocks b down as a side effect; the discount factor
puts b back without undoing the ratio. Solving on (ratio, b) rather than on
(lambda_d, b) is deliberate: it is the pair the instruments are diagonal in, so
the 2x2 is nearly triangular and Newton behaves.

WHY 1-beta AND NOT beta. The discount factor lives at 0.999 and the interesting
range runs to about 0.97, so log(beta) spans 0.001 -- three digits of nothing,
and the regression is singular in it. The discount RATE 1-beta spans 0.001 to
0.03, a factor of thirty, and that is also the quantity the household's problem
actually turns on. So the coordinate is log(1-beta) and the step is taken there.

WHAT IT WILL NOT DO. It does not touch the loss. Every other moment is free to
drift, and at lambda 30 several of them will: this is the same bargain phase A
makes, and it is only honest because phase B follows. Nothing here should be
read as an improvement until the repair has run.
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

TARGET_B = 0.089
TARGET_LD = 0.0368
TARGET_RATIO = TARGET_LD / TARGET_B

RATIO_PARAM = 'lambda_addiction'
# THE b INSTRUMENT IS addiction_scalar_1, WHICH IS THE MODEL'S OWN b.
#
# The author pointed this out on 29 August and the Fortran confirms it: the
# declaration of addiction_scalar_1 calls it "b_1 in the written model", says
# "participation is a threshold function of b", and the file carries a raise_b
# flag that sets it. It is the Stone Geary shifter on the addictive good, and it
# is the same object the stylized model calibrates as b -- there against the
# participation rate, with lam against the SUD rate. That is the pairing:
#
#     addiction_scalar_1  ->  b, the user share
#     lambda_addiction    ->  lambda_d, the disorder rate
#
# TWO WRONG INSTRUMENTS WERE TRIED FIRST AND BOTH FAILED FOR REASONS WORTH
# KEEPING. The discount factor looked ideal over the archive at lambda near 6
# -- correlation -0.94 with b, only +0.18 with the ratio -- and at lambda 30 it
# dilutes the ratio by a quarter while buying only 2.3x on b. Then
# relative_share_of_addiction_1 did far better, 3.8x on b with the ratio rising,
# but the Newton step asked for 0.534 and its bound is 0.51, so it cannot carry
# the move. addiction_scalar_1 has neither problem: it is bounded (1e-10, 1.0)
# against a current value of 0.017, so the range is not a constraint at all.
#
# ITS OWN HAZARD, FROM THE COMMENT BESIDE IT: participation is a THRESHOLD
# function of it, and the declaration records a run where it climbed eleven
# iterations through participation of 87 to 96 per cent before entering the
# right decade. Short steps here, and read the b that comes back rather than
# trusting the linearisation.
B_PARAM = 'addiction_scalar_1'

# A point belongs to this experiment only if every OTHER coordinate matches the
# centre. The whole premise is that the rest is frozen, so a point that drifted
# elsewhere is measuring a different question and would bias the two slopes with
# variation they did not cause.
FROZEN_TOL = 1e-6

# Newton on a 2x2 fitted from measurements is trustworthy over the range those
# measurements span and nowhere else. The step is capped in e-folds of each
# instrument's own coordinate.
MAX_STEP = {RATIO_PARAM: 0.90, B_PARAM: 0.70}


# The 1-beta transform existed because the discount factor lives at 0.999 and is
# singular in logs. rsa_1 lives near 0.45 to 0.51 and is perfectly well behaved
# in logs, so these are now the identity and the step is taken in log rsa_1.
# They are kept rather than inlined so that swapping B_PARAM back to the
# discount factor is a one line change and not a rewrite.
def rate(x):
    return max(x, 1e-6)


def unrate(r):
    return r


def points():
    """(vector, moments, name) for every scored point that has both moments."""
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
        if not mt or 'b' not in mt or 'lambda_d' not in mt:
            continue
        if mt['b'][0] <= 0 or mt['lambda_d'][0] <= 0:
            continue
        vec = {}
        for tok in m.group(1).split():
            k, v = tok.split('=', 1)
            vec[k] = float(v)
        out.append((vec, mt, fn))
    return out


def family(centre, pts):
    """The points that differ from the centre ONLY in the two instruments."""
    keep = []
    for vec, mt, name in pts:
        if set(vec) != set(centre):
            continue
        ok = True
        for k in centre:
            if k in (RATIO_PARAM, B_PARAM):
                continue
            a, c = vec[k], centre[k]
            if abs(a - c) > FROZEN_TOL * max(1.0, abs(c)):
                ok = False
                break
        if ok and vec[RATIO_PARAM] > 0 and 0 < vec[B_PARAM] < 1:
            keep.append((vec, mt, name))
    return keep


def fit(fam):
    """Regress log b and log(ratio) on log lambda and log(1-beta).

    Returns (J, f0, x0) with J the 2x2 of d(log moment)/d(log instrument),
    f0 the fitted logs at the centre of the design, x0 the design centre.
    """
    X, Yb, Yr = [], [], []
    for vec, mt, _n in fam:
        b, ld = mt['b'][0], mt['lambda_d'][0]
        X.append([math.log(vec[RATIO_PARAM]), math.log(rate(vec[B_PARAM]))])
        Yb.append(math.log(b))
        Yr.append(math.log(ld / b))
    X = np.array(X)
    if len(X) < 3:
        return None
    # Both instruments must actually vary, or the column is noise and the
    # solve reads a slope off nothing. This is the failure that killed the
    # regression Jacobian in jacobian.py, and it is checked here rather than
    # discovered later.
    for j, nm in ((0, RATIO_PARAM), (1, B_PARAM)):
        if np.ptp(X[:, j]) < 1e-6:
            print(f'  {nm} does not vary in this family; cannot solve on it')
            return None
    A = np.column_stack([np.ones(len(X)), X])
    cb, *_ = np.linalg.lstsq(A, np.array(Yb), rcond=None)
    cr, *_ = np.linalg.lstsq(A, np.array(Yr), rcond=None)
    J = np.array([[cb[1], cb[2]], [cr[1], cr[2]]])
    x0 = X.mean(axis=0)
    f0 = np.array([cb[0] + cb[1] * x0[0] + cb[2] * x0[1],
                   cr[0] + cr[1] * x0[0] + cr[2] * x0[1]])
    resid = float(np.linalg.norm(A @ cb - np.array(Yb)) +
                  np.linalg.norm(A @ cr - np.array(Yr)))
    return J, f0, x0, resid


def solve(centre, verbose=True):
    pts = points()
    fam = family(centre, pts)
    if verbose:
        print(f'family: {len(fam)} of {len(pts)} points share the frozen coordinates')
        print(f"{'lambda':>9} {'discount':>9} {'b':>8} {'lambda_d':>9} {'ratio':>7}  point")
        for vec, mt, name in sorted(fam, key=lambda t: t[0][RATIO_PARAM]):
            b, ld = mt['b'][0], mt['lambda_d'][0]
            print(f'{vec[RATIO_PARAM]:9.3f} {vec[B_PARAM]:9.5f} {b:8.4f} '
                  f'{ld:9.5f} {ld/b:7.4f}  {name[6:16]}')
    got = fit(fam)
    if got is None:
        print('cannot fit: need at least three points with BOTH instruments varying')
        return None
    J, f0, x0, resid = got
    if verbose:
        print(f'\nfitted elasticities (residual {resid:.4f}):')
        print(f'  d log b     / d log lambda   = {J[0,0]:+.3f}')
        print(f'  d log b     / d log(1-beta)  = {J[0,1]:+.3f}')
        print(f'  d log ratio / d log lambda   = {J[1,0]:+.3f}')
        print(f'  d log ratio / d log(1-beta)  = {J[1,1]:+.3f}')
    want = np.array([math.log(TARGET_B), math.log(TARGET_RATIO)])
    try:
        step = np.linalg.solve(J, want - f0)
    except np.linalg.LinAlgError:
        print('the 2x2 is singular; the two instruments are not separating')
        return None
    x = x0 + step
    raw = {RATIO_PARAM: math.exp(x[0]), B_PARAM: unrate(math.exp(x[1]))}
    out = dict(centre)
    for k, v in raw.items():
        cur = centre[k]
        c = math.log(rate(v) / rate(cur)) if k == B_PARAM else math.log(v / cur)
        c = max(-MAX_STEP[k], min(MAX_STEP[k], c))
        v = unrate(rate(cur) * math.exp(c)) if k == B_PARAM else cur * math.exp(c)
        lo, hi = BOUNDS.get(k, (1e-12, 1e12))
        out[k] = min(max(v, lo), hi)
    if verbose:
        print(f'\nunconstrained solution: {RATIO_PARAM}={raw[RATIO_PARAM]:.4g}  '
              f'{B_PARAM}={raw[B_PARAM]:.6f}')
        print(f'after trust region and bounds: {RATIO_PARAM}={out[RATIO_PARAM]:.4g}  '
              f'{B_PARAM}={out[B_PARAM]:.6f}')
        for k in (RATIO_PARAM, B_PARAM):
            if abs(out[k] - raw[k]) > 1e-9 * max(1.0, abs(raw[k])):
                print(f'  NOTE {k} was cut back; this is one step of several, not the answer')
    return out


def emit(vec):
    return 'bash code/run_one_point.sh ' + ' '.join(
        f'{k}={vec[k]:.7g}' for k in sorted(vec))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--centre', default='point_56bb8e81a5.txt',
                    help='the point whose frozen coordinates define the family')
    ap.add_argument('--out', default='BL_SOLVE.txt')
    a = ap.parse_args()
    p = os.path.join(HERE, 'points', a.centre)
    txt = open(p, errors='replace').read()
    m = re.search(r'^VECTOR (.*)$', txt, re.M)
    centre = {}
    for tok in m.group(1).split():
        k, v = tok.split('=', 1)
        centre[k] = float(v)
    _h, mt = score_points.read(p)
    print(f'centre {a.centre}: b={mt["b"][0]:.4f} lambda_d={mt["lambda_d"][0]:.5f} '
          f'ratio={mt["lambda_d"][0]/mt["b"][0]:.4f}')
    print(f'targets:            b={TARGET_B:.4f} lambda_d={TARGET_LD:.5f} '
          f'ratio={TARGET_RATIO:.4f}\n')
    nxt = solve(centre)
    if nxt is None:
        return 1
    with open(os.path.join(HERE, a.out), 'w') as f:
        f.write(emit(nxt) + '\n')
    print(f'\nwrote 1 point to {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
