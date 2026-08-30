#!/usr/bin/env python3
"""One damped step on ALL instruments at once, using the measured cross-effects.

WHY THIS AND NOT NINE MORE ARMS. The correction round measured nine
single-coordinate arms at one base and eight of nine moved their own moment the
right way, but the gate banks only the single arm that lowers the worst gap, so
coordinate descent spends nine containers to buy one improvement. Every arm
carries a full moment vector, though, which is a measured Jacobian: nine columns
by every moment the model reports. This solves with it.

WHY IT IS NOT JUST "APPLY ALL THE ARMS". Two of the nine are violently coupled
into the drug block that took all night to close -- the kappa_ued arm moves b
+42 and lambda_d +61 per cent, the theta arm moves them -74 and -83 -- so summing
the diagonal steps would undo it. But their signs are OPPOSITE, and that is
usable: a least squares solve over the whole matrix can trade one against the
other and keep b and lambda_d where they are while still moving theta and
kappa_ued. That is what the coupling is FOR, once it is measured rather than
feared.

b AND lambda_d ARE CARRIED AS HEAVILY WEIGHTED MOMENTS, NOT DROPPED. They are on
target and the point of the step is to keep them there; giving them a large
weight makes the solver spend its freedom protecting them first.

THE STEP IS DAMPED AND CAPPED for the same reason the arms were: the Jacobian is
local, several of these elasticities have already been shown to change sign
across the surface, and the author asked to converge slowly.
"""
import glob
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'point_1855f8103d'
OWN = {
    'utility_cost_of_treatment': 'tau_u',
    'size_homelessness': 'h_1',
    'probability_becoming_unemployed': 'pi_eu',
    'lambda_m': 'lambda_m',
    'mu_homeless': 'mu_H',
    'value_of_life': 'aleph',
    'multiple_of_probabilities_of_employment_if_addicted': 'kappa_ued',
    'relative_share_of_addiction_1': 'theta',
    'probability_of_voucher_benchmark_used': 'pi_V',
}
BOUNDS = {
    'utility_cost_of_treatment': (0.0001, 10.0),
    'size_homelessness': (0.01, 5.0),
    'probability_becoming_unemployed': (1e-6, 0.500),
    'lambda_m': (0.046, 0.500),
    'mu_homeless': (0.05, 1.0),
    'value_of_life': (1.0, 500.0),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    'relative_share_of_addiction_1': (0.40, 0.58),
    'probability_of_voucher_benchmark_used': (0.0001, 0.999),
}
# The two that are already on target and must stay there.
PROTECT = {'b': 12.0, 'lambda_d': 12.0}
MOMENTS = ['tau_u', 'h_1', 'pi_eu', 'lambda_m', 'mu_H', 'aleph',
           'kappa_ued', 'theta', 'pi_V', 'b', 'lambda_d']
DAMP = 0.60
MAX_EFOLD = 0.30
RIDGE = 0.02


def vec(t):
    m = re.search(r'^\s*VECTOR (.*)$', t, re.M)
    return dict(x.split('=', 1) for x in m.group(1).split() if '=' in x)


def mom(t, n):
    m = re.search(r'MOMENT ' + n + r'\s+\S.*?model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', t)
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def main():
    base = open(os.path.join(HERE, 'points', BASE + '.txt')).read()
    bv = vec(base)
    arms = {}
    for f in glob.glob(os.path.join(HERE, 'points', '*.txt')):
        t = open(f).read()
        v = vec(t)
        if set(v) != set(bv):
            continue
        d = [k for k in v if v[k] != bv[k]]
        if len(d) == 1 and d[0] in OWN:
            arms[d[0]] = (t, float(v[d[0]]))
    params = [p for p in OWN if p in arms]
    missing = [p for p in OWN if p not in arms]
    if missing:
        print('no arm yet for:', ', '.join(missing))
    if len(params) < 4:
        print('too few arms to solve jointly'); return 1

    # Jacobian: d ln(moment) / d ln(parameter), each column a controlled arm.
    J, resid, w = [], [], []
    for m in MOMENTS:
        y0, tg = mom(base, m)
        if y0 is None or y0 <= 0:
            continue
        row = []
        ok = True
        for p in params:
            t, x1 = arms[p]
            y1, _ = mom(t, m)
            x0 = float(bv[p])
            if y1 is None or y1 <= 0 or x0 <= 0 or x1 <= 0:
                ok = False; break
            row.append(math.log(y1 / y0) / math.log(x1 / x0))
        if not ok:
            continue
        J.append(row)
        resid.append(math.log(tg / y0))
        w.append(PROTECT.get(m, 1.0))
    J = np.array(J); r = np.array(resid); W = np.diag(w)
    A = J.T @ W @ J + RIDGE * np.eye(len(params))
    step = np.linalg.solve(A, J.T @ W @ r) * DAMP
    step = np.clip(step, -MAX_EFOLD, MAX_EFOLD)

    print(f'\nJacobian {J.shape[0]} moments x {J.shape[1]} instruments, '
          f'condition number {np.linalg.cond(J):.0f}\n')
    print(f"{'parameter':52s} {'from':>10s} {'to':>10s} {'e-folds':>8s}")
    nv = dict(bv)
    for p, s in zip(params, step):
        x0 = float(bv[p]); lo, hi = BOUNDS[p]
        x1 = max(lo, min(hi, x0 * math.exp(s)))
        nv[p] = f'{x1:.7g}'
        print(f'{p:52s} {x0:10.5g} {x1:10.5g} {s:+8.3f}'
              + ('   AT BOUND' if abs(x1 - lo) < 1e-12 or abs(x1 - hi) < 1e-12 else ''))
    pred = J @ step
    print(f"\n{'moment':10s} {'now':>9s} {'predicted after':>16s}")
    k = 0
    for m in MOMENTS:
        y0, tg = mom(base, m)
        if y0 is None or y0 <= 0:
            continue
        print(f'{m:10s} {100*(y0/tg-1):+8.0f}% {100*(math.exp(math.log(y0)+pred[k])/tg-1):+15.0f}%')
        k += 1
    out = os.path.join(HERE, 'JOINT.txt')
    with open(out, 'w') as fh:
        fh.write('bash code/run_one_point.sh ' +
                 ' '.join(f'{k}={nv[k]}' for k in sorted(nv)) + '\n')
    print(f'\nwritten to {os.path.basename(out)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
