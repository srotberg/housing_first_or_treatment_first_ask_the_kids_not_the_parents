#!/usr/bin/env python3
"""Put b and lambda_d back on target after a coupled instrument has moved them.

WHY THIS EXISTS. Of the nine instruments the correction round measured, only
three move their own moment and leave the drug block alone. The other six drag b
and lambda_d with them, and four do it violently: the aleph arm moves b -85 and
lambda_d -91 per cent, theta -74 and -83, pi_eu +44 and +64, kappa_ued +42 and
+61. Those four moments therefore cannot be fixed by moving their own instrument
and stopping -- the step has to be followed by a repair, or it trades a moment
that was wrong for two that were right.

So the loop for a coupled instrument is nested, not flat:

    move the instrument by a SMALL step -> re-solve lambda_addiction and
    addiction_scalar_1 to bring b and lambda_d back -> measure -> repeat

and this computes the inner half. It refits the two-by-two drug-block Jacobian
from the archive every time rather than carrying numbers, because the surface is
curved enough that the same elasticity reads -12 and -35 in places a few
thousandths of addiction_scalar_1 apart.

SMALL STEPS ARE NOT TIMIDITY, THEY ARE WHAT MAKES THE REPAIR POSSIBLE. The fit
that closed the drug block was local and log-linear over lambda 16 to 18.5; it
cannot be trusted to undo an 85 per cent move in b. A coupled instrument should
therefore be stepped only as far as keeps b within roughly twenty per cent, which
is inside the band where the repair has actually been verified to work. That is
what --max-b-drift enforces when sizing is left to this script.

Usage:  python3 restore.py <point_tag>   -- emit the repaired vector for a point
"""
import glob
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B_TARGET, LD_TARGET = 0.089, 0.0368
FREE = ('lambda_addiction', 'addiction_scalar_1')
BOUNDS = {'lambda_addiction': (0.5, 20000.0), 'addiction_scalar_1': (1e-30, 1.0)}


def vec(t):
    m = re.search(r'^\s*VECTOR (.*)$', t, re.M)
    return dict(x.split('=', 1) for x in m.group(1).split() if '=' in x)


def mom(t, n):
    m = re.search(r'MOMENT ' + n + r'\s+\S.*?model=\s*([0-9.eE+-]+)', t)
    return float(m.group(1)) if m else None


def drug_jacobian(base_key=None, lam_lo=15.0, lam_hi=19.0):
    """Refit d ln(b, lambda_d) / d ln(lambda, as1) from the archive, locally.

    Only points that differ from one another in the two free coordinates alone
    are comparable, so the surface is selected by vector equality on everything
    else -- the same filter locus.py uses, and for the same reason: four points
    at identical lambda and addiction_scalar_1 once read b from 0.138 to 0.283
    because they also moved probability_becoming_unemployed.
    """
    groups = {}
    for f in glob.glob(os.path.join(HERE, 'points', '*.txt')):
        t = open(f).read()
        v = vec(t)
        b, d = mom(t, 'b'), mom(t, 'lambda_d')
        if not v or not b or not d or b <= 0 or d <= 0:
            continue
        lam = float(v.get('lambda_addiction', 0))
        if not (lam_lo <= lam <= lam_hi):
            continue
        key = tuple(sorted((k, val) for k, val in v.items() if k not in FREE))
        groups.setdefault(key, []).append((lam, float(v['addiction_scalar_1']), b, d))
    # PREFER THE SLICE THE BASE ACTUALLY SITS ON. Taking the largest group is
    # what made the first repair overshoot lambda_d by 2.84 times: the biggest
    # comparable set is the original lambda/addiction_scalar_1 surface, and the
    # base had since moved away from it in tau_u, h_1, mu_homeless and more, so
    # the Jacobian was measured on a different slice of the model from the one
    # it was applied to. b came back exactly -- its row is robust across slices
    # -- and lambda_d did not, which is the row whose addiction_scalar_1
    # elasticity has been seen anywhere between -9.7 and -85.
    own = groups.get(base_key) if base_key is not None else None
    if own is not None and len(own) >= 4:
        best, foreign = own, False
    else:
        best = max(groups.values(), key=len) if groups else []
        foreign = True
    if len(best) < 4:
        return None, len(best), True
    X = np.column_stack([np.ones(len(best)),
                         [math.log(p[0]) for p in best],
                         [math.log(p[1]) for p in best]])
    out = []
    for idx in (2, 3):
        y = np.array([math.log(p[idx]) for p in best])
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        out.append(c)
    return out, len(best), foreign


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    tag = sys.argv[1].replace('point_', '').replace('.txt', '')
    path = os.path.join(HERE, 'points', f'point_{tag}.txt')
    if not os.path.exists(path):
        print(f'no such point: {tag}'); return 1
    t = open(path).read()
    v = vec(t)
    b, d = mom(t, 'b'), mom(t, 'lambda_d')
    print(f'point_{tag}: b {100*(b/B_TARGET-1):+.1f}%, lambda_d {100*(d/LD_TARGET-1):+.1f}%')

    base_key = tuple(sorted((k, x) for k, x in v.items() if k not in FREE))
    (cb, cd), n, foreign = drug_jacobian(base_key)
    if cb is None:
        print('not enough comparable points to refit the drug block'); return 1
    A = np.array([[cb[1], cb[2]], [cd[1], cd[2]]])
    cond = np.linalg.cond(A)
    print(f'refit on {n} comparable points; condition number {cond:.0f}')
    print(f'  d ln b        / d ln lambda = {cb[1]:+.2f}   / d ln as1 = {cb[2]:+.1f}')
    print(f'  d ln lambda_d / d ln lambda = {cd[1]:+.2f}   / d ln as1 = {cd[2]:+.1f}')
    if cond > 500:
        print('  WARNING: instruments nearly collinear here; the repair is unreliable.')

    step = np.linalg.solve(A, np.array([math.log(B_TARGET / b), math.log(LD_TARGET / d)]))
    # A JACOBIAN FROM ANOTHER SLICE GETS A HALF STEP. When the base's own
    # comparable set is too small to fit, the numbers come from a surface the
    # base has drifted away from, and the one time that was done at full step
    # lambda_d overshot by 2.84 times -- past its target and out the other side,
    # +7.1 to -11.9 per cent. Half a step converges from either side instead of
    # oscillating, and the fit sharpens as the base's own slice fills in.
    if foreign:
        step = step * 0.5
        print(f'  base slice too small; Jacobian borrowed from {n} points '
              f'elsewhere, so the step is halved')
    nv = dict(v)
    print()
    for p, s in zip(FREE, step):
        x0 = float(v[p]); lo, hi = BOUNDS[p]
        x1 = max(lo, min(hi, x0 * math.exp(s)))
        nv[p] = f'{x1:.7g}'
        print(f'  {p:22s} {x0:12.6g} -> {x1:12.6g}  ({s:+.3f} e-folds)')
    if abs(math.log(B_TARGET / b)) > 0.25:
        print('\n  CAUTION: b is more than 25 per cent from target, which is outside the')
        print('  band this log-linear repair was verified over. Expect to iterate.')
    out = os.path.join(HERE, f'RESTORE_{tag}.txt')
    with open(out, 'w') as fh:
        fh.write('bash code/run_one_point.sh ' +
                 ' '.join(f'{k}={nv[k]}' for k in sorted(nv)) + '\n')
    print(f'\nwritten to {os.path.basename(out)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
