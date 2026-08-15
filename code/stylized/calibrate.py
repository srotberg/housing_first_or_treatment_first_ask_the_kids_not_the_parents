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

# A FLOOR ON PERMANENT INCOME, and the reason it is here.
#
# The raw lognormal's lower tail runs to 12 per cent of average income. A
# household that poor has flow utility so negative that W2 < 0, and since dying
# is worth zero it then PREFERS the extra mortality the disorder brings: what it
# compares is phi(d)*W2(a,d), so with W2 negative a lower phi is an improvement.
# That inverts the mechanism the whole model rests on, and it bites exactly
# where the drug users are.
#
# Raising aleph does not fix it. Aleph enters every household's continuation
# value roughly equally, so it dilutes precisely the income dependence the
# mortality channel needs; it takes about 4.5 to make every value of life
# positive, and by 3.7 the gradient is already gone.
#
# THE VALUE OF LIFE PROBLEM, AND WHERE THE SEARCH FOR A FIX GOT TO.
#
# The raw lognormal's lower tail runs to 12 per cent of average income, and a
# household that poor has W2 < 0. Since dying is worth zero it then PREFERS the
# extra mortality the disorder brings: what it compares is phi(d)*W2(a,d), so
# with W2 negative a lower phi is an improvement. That inverts the mechanism,
# and it bites over roughly y in [0.12, 0.24], which is exactly where the users
# are. floor_test.py is the diagnostic.
#
# THREE REQUIREMENTS, and no point yet found that meets all three.
#
#   1  every value of life positive     needs the income floor HIGH, or aleph
#                                       high, or both
#   2  the income gradient              survives a floor easily; r_use is 0.21
#                                       at YMIN = 0.20 and 0.44 at 0.30. Dies if
#                                       aleph alone is pushed past about 3.7,
#                                       which dilutes the income dependence the
#                                       mortality channel needs
#   3  a non zero moral hazard          needs the floor LOW: a household that
#                                       can afford the small unit on income
#                                       support is never at risk, so psi*YMIN
#                                       must stay under h_S = 0.106
#
# YMIN = 0.20 with aleph = 3.1 satisfies 1 and 2: min phi*W2 = +0.567, the
# disorder is costly at every income, r_use = 0.207. But the progression moment
# then has to be carried by theta rather than lam, since with the disorder that
# costly users pick a v so small that lam cannot lift prog past 0.09 even pinned
# at 900. At the theta this requires, roughly 0.38, the policy experiment
# collapses: participation with no voucher is 20.6 per cent and universal cover
# drives BOTH policies to zero, so the moral hazard is exactly zero and result 2
# is gone.
#
# So the three pull against each other and this is unresolved. The grid and
# parameters below are the WORKING configuration, which has results 1 and 2 but
# the negative value of life at the bottom. Nothing here is silently changed.
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
# THETA, NOT LAM, IS THE INSTRUMENT FOR PROGRESSION. lam is the hazard per unit
# used and theta is how much a user uses, and with the income floor in place the
# disorder is costly enough everywhere that users choose a very small v: lam then
# cannot lift prog past 0.09 even pinned at 900. theta moves it directly, since
# raising the weight on drugs raises the quantity and the quantity is what
# carries the risk. lam is set externally at 97 instead.
PAIRS = [('h_hl', 'homeless', 1e-5, 0.49),
         ('lam', 'prog', 10.0, 900.0),
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


def _b_for(par, iters=16):
    """Refit b so participation is on target at the given parameters."""
    return bracket(par, 'b', 'part', 1e-5, 0.60, iters=iters)


def bracket_prog(par, lo=10.0, hi=900.0, iters=14):
    """
    Bracket lam on prog, REFITTING b at every trial.

    prog is sud/part, so it is meaningless when participation is near zero.
    Evaluated on a stale b the monotonicity test reads prog = 0 at one end,
    concludes the wrong sign, and drives the parameter to a bound: that is what
    made two earlier calibrations look as though the model had broken. Refitting
    b at each trial keeps participation on target, so prog is always defined.
    """
    tgt = TARGET['prog']
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        q = with_(par, lam=mid)
        q = with_(q, b=_b_for(q))
        if stats(q)['prog'] > tgt:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def calibrate(par=None, sweeps=4, verbose=True):
    par = par or P()
    for s in range(sweeps):
        par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-5, 0.49))
        par = with_(par, lam=bracket_prog(par, 10.0, 900.0))
        par = with_(par, b=_b_for(par, iters=30))
        if verbose:
            m = stats(par)
            worst = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
            print(f'  sweep {s+1}  worst relative gap {worst:7.3f}   '
                  + f'h_hl={par.h_hl:.4g}  th={par.th:.4g}  b={par.b:.4g}')
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
