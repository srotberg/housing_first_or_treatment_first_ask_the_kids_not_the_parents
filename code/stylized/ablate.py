"""
Which pieces of the stylised model earn their place?

The model exists to make exactly two points:

  POINT 1   which channel decides WHO uses drugs across the income distribution
  POINT 2   how the moral hazard of unconditional housing assistance operates

So the test for keeping a piece is not whether it is realistic. It is whether
removing it changes one of those two numbers. Anything that changes neither is
detail the reader has to carry for nothing, and it gets cut.

For each piece this switches it off, REFITS the taste, the subsistence parameter
and the mortality penalty to the same three moments, so the comparison is
between two models that agree on participation, spending and the price
elasticity, and then reports:

    r_use          income of users / average, the gradient       POINT 1
    moral hazard   participation at universal HF against none    POINT 2

A piece is worth keeping if it moves one of them by more than a couple of
points. Everything else is decoration.
"""

import json
import numpy as np
from stylized import P, with_
from calibrate import stats, fit, TARGET, BRACKETS, YG, W


CORE = {'part': TARGET['part'], 'spend': TARGET['spend'],
        'elast_p': TARGET['elast_p']}
REFIT = [f for f in BRACKETS if f[0] in ('b', 'th', 'kap')]


def headline(par, refit=True):
    if refit:
        par = fit(par, targets=CORE, free=REFIT, maxfev=450, verbose=False)
    m0 = stats(with_(par, pV=0.0, policy='HF'))
    m1 = stats(with_(par, pV=1.0, policy='HF'))
    mt = stats(with_(par, pV=1.0, policy='TF'))
    mh = 100.0 * (m1['part'] / max(m0['part'], 1e-12) - 1.0)
    tf = 100.0 * (mt['part'] / max(m0['part'], 1e-12) - 1.0)
    return stats(par)['r_use'], mh, tf, par


ABLATIONS = [
    ('none: the model as calibrated', {}),
    ('homelessness does not impede recovery', dict(rho_mult_hl=1.0)),
    ('homelessness does not raise mortality', dict(kapH=0.0)),
    ('the disorder is absorbing (no recovery)', dict(rho=0.0)),
    ('nobody is unemployed when clean', dict(u0=0.0)),
    ('unemployment pays nothing', dict(omega=0.02)),
    ('drug price fixed, no market clearing', dict(eps_s=1e6)),
    ('no taste dispersion to speak of', dict(sig=0.15)),
]


if __name__ == '__main__':
    try:
        cal = json.load(open('calibrated.json'))
    except FileNotFoundError:
        raise SystemExit('run calibrate.py first')
    base = with_(P(), **cal)

    print('=' * 78)
    print('DOES EACH PIECE EARN ITS PLACE?')
    print('   every row is refitted to the same participation, spending and')
    print('   price elasticity, so the rows differ only in the mechanism')
    print('=' * 78)
    print(f"{'switched off':42s}{'r_use':>9s}{'HF moral':>10s}{'TF':>8s}")
    print(f"{'':42s}{'':>9s}{'hazard %':>10s}{'%':>8s}")
    ref = None
    for name, kw in ABLATIONS:
        r, mh, tf, _ = headline(with_(base, **kw))
        if ref is None:
            ref = (r, mh, tf)
            flag = ''
        else:
            moved = abs(r - ref[0]) > 0.02 or abs(mh - ref[1]) > 2.0
            flag = '   KEEP' if moved else '   cut?'
        print(f'{name:42s}{r:9.3f}{mh:10.2f}{tf:8.2f}{flag}')
    print('-' * 78)
    print('   r_use below one is the paper\'s central fact: drug use sits at the')
    print('   bottom of the income distribution. A positive HF moral hazard is')
    print('   the second: unconditional housing assistance raises use.')
