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
from stylized import P, with_, aggregates, vsl

# THE VALUE OF LIFE, and how it was fixed.
#
# The problem: with log utility the poorest households had a NEGATIVE value of
# life. Since dying is worth zero they then preferred the extra mortality the
# disorder brings, which inverts the mechanism the model rests on. The condition
# that matters is on V1, the value at the point where v is chosen: nobody should
# be choosing to use while death is the better option. W2 alone may dip below
# zero later, when no v is being chosen.
#
# Three changes fixed it, and only the third touches aleph.
#
#   WEIGHTS THAT SUM TO ONE. Consumption is weighted by 1-gam-th rather than 1,
#   which damps log c at the bottom by a third and makes gam the housing budget
#   share proper rather than gam/(1+gam+th).
#
#   u0 STAYS. Setting it to zero was tried and reverted: it makes every route
#   into homelessness run through the disorder, and the share of the homeless
#   carrying one goes to 0.997 against a third or so in the data. Clean
#   households have to be able to lose their jobs too.
#
#   ALEPH 2.50 -> 2.80. Small, and nowhere near the 3.7 that flattens the
#   gradient by diluting the income dependence the mortality channel needs.
#
# Result: min V1 = +0.20, no household anywhere with a negative ex ante value of
# life, both headline results intact, and the share of the homeless with the
# disorder at 0.42.
#
# An income floor was also tried, at the suggestion that squeezing the bottom
# would help. It does fix the value of life, but psi*YMIN must stay under the
# small unit's rent for anyone to be at risk of the street at all, so a floor
# high enough to matter collapses homelessness and takes the moral hazard with
# it. floor_test.py is that diagnostic and is kept.
YMIN = 0.12
SIG = 0.75
YG = np.exp(np.linspace(np.log(YMIN), np.log(5.0), 30))
W = np.exp(-0.5 * ((np.log(YG) + 0.5 * SIG**2) / SIG)**2)

TARGET = dict(part=0.0513, homeless=0.00399, prog=0.332, vsl=80.0)

# ORDER MATTERS, and participation goes LAST. Every one of these parameters
# moves participation: lam makes drugs riskier, h_hl changes what is at stake in
# losing your home. So whichever bracket runs last is the one whose moment is
# actually hit, and the others are only hit to the extent the sweep has
# converged. Participation is the moment the model exists to reproduce, so b
# runs last. With b first, participation settled at 3.7 per cent against a
# target of 5.13 and stayed there however many sweeps were run.
# THETA IS SET, NOT CALIBRATED, and the reason is worth recording because the
# obvious alternative was tried and fails. The natural target is the 11 per cent
# of income that users who are not addicted spend on drugs, which is what the
# full model matches. This model cannot reach it while keeping users poor. Two
# targets pin the pair (lam, v): prog = 1 - exp(-lam v) = 0.332 fixes lam*v at
# 0.403, and a spending share of 0.11 on an average user income near 0.2 fixes
# v near 0.022, hence lam near 18. Scanning (lam, th) over that region shows the
# model is bimodal, with no interior solution:
#
#     lam    th      drug spending/income    users' income / average
#      18   0.25            0.0003                    0.375
#      18   0.35            0.3742                    3.372
#      25   0.25            0.0014                    0.287
#
# Below the threshold users are the very poor and use a hair above zero; above
# it the users are the rich and the income gradient the model exists to explain
# is gone. There is nothing in between. The economics is not subtle: what puts
# use at the bottom is that the disorder destroys a continuation value, and for
# a poor household that cost is enormous relative to the utility of the drug, so
# it uses as little as it can while still using. Low intensity use among the
# poor is the same fact as the income gradient, not an independent one. So the
# spending share is reported as an untargeted moment that the model misses, and
# theta stays set with gamma = 0.25 * (1 - theta) alongside it.
PAIRS = [('aleph', 'vsl', 0.20, 12.0),
         ('h_hl', 'homeless', 1e-5, 0.49),
         ('lam', 'prog', 10.0, 4000.0),
         ('b', 'part', 1e-5, 0.30)]

LABEL = {'part': 'drug participation rate',
         'housing_share': 'housing spending / income',
         'homeless': 'homelessness rate',
         'dshare': 'drug spending / income among users',
         'vsl': 'value of a statistical life, annual incomes',
         'prog': 'share of users who acquire the disorder'}


def stats(par):
    # GAMMA IS TIED TO THETA, not free. Housing is a quarter of non drug
    # spending in the data, so the housing weight has to move with the drug
    # weight or the three shares stop summing to one.
    par = with_(par, gam=0.25 * (1.0 - par.th))
    m = aggregates(par, YG, W)
    m['vsl'] = vsl(par)
    return m


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


def bracket_with_b(par, name, mom, lo, hi, iters=16):
    """
    Bracket one parameter on one moment, REFITTING b at every trial.

    Needed wherever the moment is a ratio that is only defined when someone
    uses, or where the parameter moves participation so hard that the stale b
    makes the moment meaningless. theta and lam are both like that: raising
    either changes how many households use, so the moment has to be read at a b
    that puts participation back on target.
    """
    tgt = TARGET[mom]
    def at(v):
        q = with_(par, **{name: v})
        if name == 'th':
            q = with_(q, gam=0.25 * (1.0 - v))
        return stats(with_(q, b=_b_for(q, iters=14)))[mom]
    rising = at(hi) > at(lo)
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if (at(mid) > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def bracket_prog(par, lo=10.0, hi=4000.0, iters=16):
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


def calibrate(par=None, sweeps=5, verbose=True):
    par = par or P()
    for s in range(sweeps):
        par = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.20, 12.0, iters=26))
        par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-5, 0.49))
        par = with_(par, lam=bracket_prog(par, 10.0, 4000.0))
        par = with_(par, b=_b_for(par, iters=30))
        if verbose:
            m = stats(par)
            worst = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
            print(f'  sweep {s+1}  worst relative gap {worst:7.3f}   '
                  f'aleph={par.aleph:.4g}  h_hl={par.h_hl:.4g}  '
                  f'lam={par.lam:.4g}  b={par.b:.4g}')
    return with_(par, gam=0.25 * (1.0 - par.th))


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
    print(f"  drug spending / income among users  : {m['dshare']:.4f}"
          "   (untargeted; see the note on theta)")
    from stylized import value1
    v1 = np.array([value1(par, y, 'HF') for y in YG])
    print(f"  minimum ex ante value of life over the grid : {v1.min():.3f}")
    return m


if __name__ == '__main__':
    import json
    par = calibrate()
    report(par)
    json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS} | {'gam': par.gam},
              open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
