"""
Does flooring permanent income break the income gradient, or only break the
calibration routine?

The sweep that flooded lam to its lower bound is not evidence that the gradient
is gone: the same degeneracy appears whenever the bracketing lands on a branch
where nobody acquires the disorder, and then prog is 0/0 and every bracket is
meaningless. This isolates the economics by HOLDING lam and h1 at their
baseline values and bracketing only b on participation, so the only thing the
floor can do is move who uses.

Run:  python3 floor_test.py
"""

import json
import numpy as np
from math import erf
from stylized import P, with_, aggregates, solve_period2

BASE = with_(P(), **json.load(open('calibrated.json')))
SIG = 0.75
TARGET_PART = 0.0513


def grid(ymin, n=30):
    """Lognormal on [ymin, 5], with the sub floor mass piled on the first node
    and income rescaled so the mean stays at one."""
    yg = np.exp(np.linspace(np.log(ymin), np.log(5.0), n))
    z = (np.log(yg) + 0.5 * SIG**2) / SIG
    w = np.exp(-0.5 * z**2)
    below = 0.5 * (1.0 + erf(z[0] / np.sqrt(2.0)))
    w = w.copy()
    w[0] += below * w.sum() / max(1.0 - below, 1e-9)
    yg = yg / float((w / w.sum() * yg).sum())
    return yg, w


def bracket_b(par, yg, w, lo=1e-5, hi=0.60, iters=26):
    f = lambda x: aggregates(with_(par, b=x), yg, w)['part']
    rising = f(hi) > f(lo)
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if (f(mid) > TARGET_PART) == rising:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


if __name__ == '__main__':
    # THE TWO CONSTRAINTS PULL OPPOSITE WAYS.
    #   value of life  needs the floor HIGH, so the poorest are not destitute
    #   homelessness   needs it LOW, since a household that can afford the small
    #                  unit on income support is never homeless, and psi*ymin
    #                  must stay below h_S = 0.106 for anyone to be at risk
    # A floor alone cannot satisfy both. A floor plus a modest aleph can: the
    # floor does most of the lifting and aleph finishes it, well short of the
    # level that dilutes the gradient.
    print('%-7s %-7s %-8s %-8s %-10s %-11s %-9s' %
          ('ymin', 'aleph', 'part', 'r_use', 'homeless', 'min phi*W2', 'life ok'))
    for ymin in (0.16, 0.18, 0.20, 0.22):
        yg, w = grid(ymin)
        for al in (2.8, 3.1, 3.4):
            base = with_(BASE, aleph=al)
            par = with_(base, b=bracket_b(base, yg, w))
            m = aggregates(par, yg, w)
            s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
            worst, ok = 1e9, True
            for y in yg[::2]:
                _, V2, _, _, _, _ = solve_period2(par, y, 'HF')
                worst = min(worst, s0 * V2[0, 0])
                ok = ok and (s1 * V2[0, 1] < s0 * V2[0, 0])
            print('%-7.2f %-7.1f %-8.4f %-8.3f %-10.5f %-11.3f %-9s' %
                  (ymin, al, m['part'], m['r_use'], m['homeless'], worst, ok))
