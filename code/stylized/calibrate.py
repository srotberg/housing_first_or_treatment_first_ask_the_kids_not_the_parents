"""
A rough calibration of the stylized two period model. Five parameters, five
targets.

    aleph   value of a statistical life                80 annual incomes
    h_lg    housing over non drug spending             26.8 %
    h_hl    homelessness rate                          0.399 %
    lam     share of users who acquire a SUD           33.2 %
    b       drug participation rate                    5.13 %

THE STANDARD RENTAL UNIT IS BACK ON THE LIST, and the reason it left is worth
recording along with the reason it returned. It was calibrated to the aggregate
housing share once before and the sweep doubled the rent, so a fifth of
households could not afford any home while unemployed and homelessness came out
three times its target. It was then SET, at 21.2 per cent of mean income from the
SCF, with gamma set separately from the Consumer Expenditure Survey. That is two
external numbers aimed at one object, and nothing made the pair deliver the
survey's share in equilibrium: it came out at 16 per cent against 26.8. Setting
gamma from the survey and calibrating h_lg to realised spending removes the
double count, and the earlier failure does not repeat because the moment is now
housing over non drug SPENDING rather than over INCOME, and because h_hl is
bracketed AFTER h_lg rather than before it.

Rough is the intention. The model is qualitative and exists to show directions,
so the calibration only has to put it in the right region. Nothing here is a fit
to be defended, there is no validation table, and the magnitudes in the paper
come from the full model.

Everything else is set: the discount factor, the interest rate, survival, the
housing weight at 0.268 of non drug spending, the unemployment rate given a SUD
(measured in NSDUH 2024, ages 26 and above, weighted), the replacement rate, the
mortality multiplier, and the voucher parameters. Recovery is not on the list any
more: period 2 is terminal, so rho has nothing to name.

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

TARGET = dict(part=0.0513, homeless=0.00399, prog=0.332, vsl=80.0,
              dshare=0.11, housing_share=0.30, hspend=0.268)

# ORDER MATTERS, and participation goes LAST. Every one of these parameters
# moves participation: lam makes drugs riskier, h_hl changes what is at stake in
# losing your home. So whichever bracket runs last is the one whose moment is
# actually hit, and the others are only hit to the extent the sweep has
# converged. Participation is the moment the model exists to reproduce, so b
# runs last. With b first, participation settled at 3.7 per cent against a
# target of 5.13 and stayed there however many sweeps were run.
# THE TWO PERIOD RESTRUCTURE WAS DONE FOR THE DRUG SPENDING SHARE AND DID NOT
# DELIVER IT. The share went from 1.76 per cent in the three period model to 1.91
# here against a target of 11, and the reason is worth recording because it is
# structural rather than a matter of tuning. What a household loses by acquiring
# the SUD is, to a first approximation, kap * phi0 * (the discounted continuation),
# and the VALUE OF A STATISTICAL LIFE pins the discounted continuation directly:
# beta * E W2 / u_c * years = 80. Cutting the horizon from two continuation
# periods to one shortens the continuation, but it also raises the share of it
# that mortality destroys from the tail to ALL of it, and with aleph refitted to
# the same VSL the two effects very nearly cancel. Raising the annual discount
# factor from 0.99 to 0.995 is the same story: it lowers the aleph needed for the
# VSL, which steepens the income gradient, and leaves the spending share where it
# was.
#
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
# theta stays set with gamma = 0.268 * (1 - theta) alongside it.
# THETA AND GAMMA ARE SET, NOT BRACKETED. Freeing them was tried twice and it
# collapses: gamma couples the housing weight to the homelessness margin through
# the value of the street, the h_hl bracket loses its interior solution, and the
# sweep walks to h_hl = 0.055 with homelessness at 25 per cent. They are chosen
# instead by a scan over (theta, gamma) that refits the three below at every
# point and screens on the two things that must not break: users poorer than
# average, and no household with a negative ex ante value of life. theta = 0.20
# with gamma left at its Consumer Expenditure Survey value is the largest drug
# spending share that costs no other target. best_drug.json is the runner up.
# THE LAMBDA BRACKET REACHES FAR DOWN. In the three period model it started at
# 10 and the calibrated value was in the hundreds. Two periods put one third of
# the continuation at risk instead of two, so a household that uses loses less
# and uses more, and lambda has to be smaller to keep the same share of users
# progressing. A bracket that cannot reach a small lambda would report a corner
# rather than a calibration.
LAM_LO, LAM_HI = 0.05, 4000.0

PAIRS = [('aleph', 'vsl', 0.20, 24.0),
         ('h_lg', 'hspend', 0.08, 1.40),
         ('h_hl', 'homeless', 1e-7, 0.49),
         ('lam', 'prog', LAM_LO, LAM_HI),
         ('b', 'part', 1e-5, 0.30)]

LABEL = {'part': 'drug participation rate',
         'hspend': 'housing spending / non drug spending',
         'housing_share': 'housing spending / income',
         'homeless': 'homelessness rate',
         'dshare': 'drug spending / income among users',
         'vsl': 'value of a statistical life, annual incomes',
         'prog': 'share of users who acquire a SUD'}


def stats(par):
    # GAMMA IS FREE. Tying it to theta as 0.268(1-theta) was the mistake behind
    # the earlier claim that this model cannot reach an 11 per cent drug
    # spending share: with gamma tied, raising theta lowers gamma and the two
    # effects on the consumption weight nearly cancel, so the drug share jumps
    # from 0.001 to 0.28 with nothing in between. Freed, the pair (theta, gamma)
    # spans a region where users spend a fifth of income on drugs and are still
    # poorer than average: at theta = 0.20, gamma = 0.10 the model gives a drug
    # share of 0.20 with users at 0.29 of average income.
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
        return stats(with_(q, b=_b_for(q, iters=14)))[mom]
    rising = at(hi) > at(lo)
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if (at(mid) > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def bracket_prog(par, lo=None, hi=None, iters=16):
    """
    Bracket lam on prog, REFITTING b at every trial.

    prog is sud/part, so it is meaningless when participation is near zero.
    Evaluated on a stale b the monotonicity test reads prog = 0 at one end,
    concludes the wrong sign, and drives the parameter to a bound: that is what
    made two earlier calibrations look as though the model had broken. Refitting
    b at each trial keeps participation on target, so prog is always defined.
    """
    tgt = TARGET['prog']
    lo = LAM_LO if lo is None else lo
    hi = LAM_HI if hi is None else hi
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
        par = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.20, 24.0, iters=26))
        # THE STANDARD UNIT GOES BEFORE THE STREET, because moving it moves
        # homelessness and h_hl is what puts homelessness back. The reverse
        # order leaves the street calibrated against a unit size that has since
        # changed.
        par = with_(par, h_lg=bracket(par, 'h_lg', 'hspend', 0.08, 1.40))
        par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-7, 0.49))
        par = with_(par, lam=bracket_prog(par, LAM_LO, LAM_HI))
        par = with_(par, b=_b_for(par, iters=30))
        if verbose:
            m = stats(par)
            worst = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
            print(f'  sweep {s+1}  worst relative gap {worst:7.3f}   '
                  f'aleph={par.aleph:.4g}  h_hl={par.h_hl:.4g}  '
                  f'lam={par.lam:.4g}  b={par.b:.4g}')
    # GAMMA IS NOT RE-IMPOSED HERE. It used to be returned as 0.25*(1-theta),
    # which silently overwrote the value the (theta, gamma) scan chose: at
    # theta = 0.20 that is 0.200 rather than 0.2225, and the two are on opposite
    # sides of a cliff, 1.9 per cent drug spending against 13. The tie belongs
    # to the old calibration where theta was 0.11 and gamma was not a separate
    # object; it does not belong here.
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
    json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS}
              | {'th': par.th, 'gam': par.gam},
              open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
