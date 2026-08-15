"""
A rough calibration of the stylized model. Four parameters, four targets.

    b       drug participation rate                    5.13 %
    h_hl    homelessness rate                          0.399 %
    lam     share of users who acquire the disorder    33.2 %

Three, not four. Rent used to be calibrated to the aggregate housing share and
that was a mistake: it doubled rent, because most households here take the small
unit, so a fifth of them could not afford any home while unemployed and
homelessness came out three times its target. Rent is now SET so the standard
unit costs 21.2 per cent of mean income, which is the same fact stated the way
that does not break anything.

Rough is the intention. The model is qualitative and exists to show directions,
so the calibration only has to put it in the right region. Nothing here is a fit
to be defended, there is no validation table, and the magnitudes in the paper
come from the full model.

Everything else is set: the discount factor, the interest rate, survival, the
two rental sizes, the housing weight at 0.25, the unemployment rate given the disorder (measured in
NSDUH 2024, ages 26 and above, weighted), the replacement rate, the consumption
floor, recovery and its multiplier on the street, the two mortality multipliers,
the wage penalty, and the voucher parameters.

BRACKETING, NOT A JOINT FIT. With no preference heterogeneity the aggregate is
a cliff in b: participation is one below a narrow band and zero above it. A
gradient method steps out of the band, sees a flat surface, and walks to a
corner. Each parameter is therefore bracketed on its own monotone target in
sequence, which cannot leave the band.
"""

import numpy as np
from stylized import P, with_, aggregates

# THE INCOME GRID, and a finding recorded here because it matters.
#
# The lognormal's lower tail runs to 12 per cent of average income. A household
# that poor has flow utility so negative that W2 < 0, and since dying is worth
# zero it then PREFERS the extra mortality the disorder brings: the household
# compares phi(d)*W2(a,d), and with W2 negative a lower phi is an improvement.
#
# Two fixes were tried and neither works.
#
#   RAISING ALEPH needs about 4.5 before every value of life is positive, and
#   aleph enters every household's continuation value roughly equally, so it
#   dilutes exactly the income dependence the mortality channel needs. At 3.7
#   the gradient is gone: r_use goes to 3.37 and lam collapses to its bound.
#
#   FLOORING PERMANENT INCOME at 0.30, squeezing the bottom of the
#   distribution, DOES fix the value of life completely: min W2 = +0.72 at
#   aleph = 2.5, with the disorder costly at every income. It also destroys the
#   gradient, r_use = 3.36 at every aleph tried with lam pinned at its bound.
#   The reason is the diagnosis. The use region sits at y in [0.12, 0.24],
#   which is exactly where W2 < 0, so flooring income above it removes every
#   household that used to use.
#
# What that means is worth stating rather than parameterising away: at this
# calibration the income gradient is produced in part by households for whom
# life is worth less than nothing. Fixing it properly needs a utility function
# bounded below, so W2 > 0 by construction, and then a check of whether the
# gradient survives. The grid below is the original one.
YMIN = 0.12
SIG = 0.75
YG = np.exp(np.linspace(np.log(YMIN), np.log(5.0), 30))
W = np.exp(-0.5 * ((np.log(YG) + 0.5 * SIG**2) / SIG)**2)

TARGET = dict(part=0.0513, homeless=0.00399, prog=0.332)

# ORDER MATTERS, and participation goes LAST. Every one of these parameters
# moves participation: lam makes drugs riskier, h_hl changes what is at stake in
# losing your home. So whichever bracket runs last is the one whose moment is
# actually hit, and the others are only hit to the extent the sweep has
# converged. Participation is the moment the model exists to reproduce, so b
# runs last. With b first, participation settled at 3.7 per cent against a
# target of 5.13 and stayed there however many sweeps were run.
PAIRS = [('h_hl', 'homeless', 1e-5, 0.49),
         ('lam', 'prog', 0.5, 900.0),
         ('b', 'part', 1e-5, 0.30)]

LABEL = {'part': 'drug participation rate',
         'housing_share': 'housing spending / income',
         'homeless': 'homelessness rate',
         'prog': 'share of users who acquire the disorder'}


def stats(par):
    return aggregates(par, YG, W)


def bracket(par, name, mom, lo, hi, iters=34):
    """Bisect one parameter on one monotone target."""
    tgt = TARGET[mom]
    rising = stats(with_(par, **{name: hi}))[mom] > stats(with_(par, **{name: lo}))[mom]
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if (stats(with_(par, **{name: mid}))[mom] > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def calibrate(par=None, sweeps=6, verbose=True):
    par = par or P()
    for s in range(sweeps):
        for name, mom, lo, hi in PAIRS:
            par = with_(par, **{name: bracket(par, name, mom, lo, hi)})
        if verbose:
            m = stats(par)
            worst = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
            print(f'  sweep {s+1}  worst relative gap {worst:7.3f}   '
                  + '  '.join(f'{n}={getattr(par, n):.4g}' for n, _, _, _ in PAIRS))
    return par


def report(par):
    m = stats(par)
    print('\n' + '=' * 64)
    print('STYLIZED MODEL, ROUGH CALIBRATION')
    print('=' * 64)
    print(f"{'moment':42s}{'target':>10s}{'model':>10s}")
    for _, mom, _, _ in PAIRS:
        print(f'{LABEL[mom]:42s}{TARGET[mom]:10.4f}{m[mom]:10.4f}')
    print('-' * 64)
    print('  ' + '   '.join(f'{n}={getattr(par, n):.4g}' for n, _, _, _ in PAIRS))
    print(f"\n  income of users / average : {m['r_use']:.3f}")
    print(f"  share of homeless with the disorder : {m['sud_of_homeless']:.3f}")
    return m


if __name__ == '__main__':
    import json
    par = calibrate()
    report(par)
    json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS},
              open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
