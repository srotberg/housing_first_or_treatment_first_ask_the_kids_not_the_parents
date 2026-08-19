"""
A rough calibration of the stylized two period model. Five parameters, five
targets.

    gam     housing over non drug spending             26.8 %
    h_hl    homelessness rate                          0.399 %
    aleph   value of a statistical life                80 annual incomes
    lam     share of users who acquire a SUD           33.2 %
    b       drug participation rate                    5.13 %

THE RENTAL SIZES ARE SET AND GAMMA IS CALIBRATED, which is the conventional order
and the third arrangement tried. The grid is a market fact quoted to the reader,
h_lg = 0.40 of mean income and h_sm a quarter of that; the weight on housing is a
preference, and a preference is what a model is entitled to infer. Working
backwards recovers the same object, since a gamma and a grid that reproduce the
share are two descriptions of one calibration.

WHAT WAS TRIED BEFORE, both of which failed. Setting BOTH, gamma from the
expenditure survey and h_lg from an SCF housing cost to income ratio, aims two
external numbers at one object with nothing making them agree, and the model
delivered a 16 per cent share against the survey's 26.8. Calibrating h_lg on the
share instead hits 26.8 exactly and puts homelessness at 3.2 per cent, because
the aggregate share is bounded above by h_lg and matching it needs a unit so
large that the small unit prices the bottom of the distribution out of housing.
The frontier is tabulated in stylized.py.

FREEING GAMMA HAS ITS OWN HISTORY AND IT IS A BAD ONE, so this arrangement is on
probation until the sweep is read. Twice before, gamma was freed jointly with
theta in a scan, and it collapsed both times: gamma couples the housing weight to
the homelessness margin through the value of the street, the h_hl bracket lost
its interior solution, and the sweep walked to h_hl = 0.055 with homelessness at
25 per cent. Two things differ now. theta stays SET, so only one preference is
moving. And the rental sizes are SET, so the affordability floor cannot drift
while gamma moves, which is what removed h_hl's interior solution before. If the
h_hl bracket corners again, this arrangement is wrong too and the note should say
so rather than report a corner as a calibration.

THE VALUE OF LIFE IS BRACKETED AFTER THE STREET. aleph is additive in flow
utility so it barely touches the housing choice, whereas h_hl moves the
continuation and hence the VSL, so the dependence runs one way. With aleph first
the sweep reported a VSL of 129 against a target of 80.

Rough is the intention. The model is qualitative and exists to show directions,
so the calibration only has to put it in the right region. Nothing here is a fit
to be defended, there is no validation table, and the magnitudes in the paper
come from the full model.

Everything else is set: the discount factor, the interest rate, survival, the two
rental sizes, the weight on drugs, the unemployment rate given a SUD
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
# SIG IS CALIBRATED, NOT SET. It is chosen so that the bottom half of the income
# distribution holds the share of earnings it holds in the data: 17.2 percent, in
# the SCF 2022, among households aged 26 to 65 with positive wage and salary
# income. The life cycle model is calibrated to the same moment, so the two
# models carry the same income dispersion by construction rather than by
# coincidence, which is what lets the stylized model stand in for the other one.
#
# It is solved here rather than in the sweep below because the mapping from SIG
# to the share involves nothing else in the model: the grid and its weights are
# built before any parameter is chosen, and the share falls monotonically in SIG.
# Bisection on one number is exact and costs nothing, where putting it in the
# sweep would make every other bracket chase a moving grid.
#
# What it replaced: 0.75, which was a guess and was too equal. It gave the bottom
# half 19.3 percent against 17.2, a ratio of the ninetieth to the tenth percentile
# of 6.6 against 10.0 in the data, and a top tenth share of 29.2 against 41.1.
BOT50_TARGET = 0.172


def _grid(sig):
    yg = np.exp(np.linspace(np.log(YMIN), np.log(5.0), 30))
    w = np.exp(-0.5 * ((np.log(yg) + 0.5 * sig**2) / sig)**2)
    return yg, w / w.sum()


def _bottom_half_share(sig):
    """Share of income held by the poorer half, with the node the median falls
    inside split at the median rather than assigned whole, so the share moves
    smoothly in sig instead of jumping from node to node."""
    yg, w = _grid(sig)
    mean = float((w * yg).sum())
    acc = tot = 0.0
    for yi, wi in zip(yg, w):
        if acc + wi <= 0.5:
            tot += yi * wi
            acc += wi
        else:
            tot += yi * (0.5 - acc)
            break
    return tot / mean


def _solve_sig(lo=0.30, hi=2.50, iters=60):
    # the share FALLS in sig, so a share above target means too equal and sig rises
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if _bottom_half_share(mid) > BOT50_TARGET:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


SIG = _solve_sig()
YG, W = _grid(SIG)
W = W * len(W)  # calibrate.py uses W unnormalised elsewhere; scale is irrelevant

# LAMBDA TARGETS THE SAME MOMENT AS THE LIFE CYCLE MODEL. It used to target
# prog, the 33.2 per cent of users who acquire a SUD, while the life cycle model
# targets the ADULT SUD RATE of 3.68 per cent from NSDUH 2024. Those two are not
# the same claim: with participation at 5.13 per cent, a prog of 0.332 implies a
# population SUD rate of 0.0513 * 0.332 = 1.70 per cent, less than half of 3.68,
# so the two models were calibrated to inconsistent numbers for the same object.
#
# sud is also the better behaved moment. prog is sud/part, a ratio of two
# endogenous objects, and it is very nearly a step function in lam: with b refit
# at every point it runs 0.065 at lam = 60, 0.221 at 121 and 0.9998 at 250. The
# population rate is bounded by participation and moves smoothly.
TARGET = dict(part=0.0513, homeless=0.00399, sud=0.0368, vsl=80.0,
              dshare=0.20, housing_share=0.30, hspend=0.268,
              bot50=BOT50_TARGET)

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
# SUPERSEDED, and left because the arithmetic in it is still the reason the
# target is 20 per cent rather than the 34.7 in the data.
# THETA WAS SET, NOT CALIBRATED, and the reason is worth recording because the
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
# SUPERSEDED: THETA AND GAMMA ARE BOTH BRACKETED NOW. gamma has been on hspend
# for some time, and theta joined it on the drug spending share once the target
# moved from 11 per cent to 20. The paragraph below records why freeing them
# failed when gamma was TIED to theta as 0.268(1-theta), which is the version
# that collapsed, and it is kept because the tie is the thing not to reinstate.
# THETA AND GAMMA WERE SET, NOT BRACKETED. Freeing them was tried twice and it
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

# THETA'S WINDOW, and a correction to what an earlier version of this comment
# said. It claimed the drug spending share is bimodal in theta, running 5.2 per
# cent at theta = 0.21 and jumping to 18.8 at 0.22, so that only a narrow window
# was safe to bisect on. That measurement refit b ALONE. With the whole model
# recalibrated at each theta, which is what a bracket inside the sweep actually
# does, the share is smooth and monotone:
#
#     theta   0.18    0.20    0.21    0.22    0.23
#     share  15.2%   18.4%   20.2%   21.6%   24.2%
#
# The jump was lambda, gamma and the street being held at their theta = 0.23
# values while theta moved, which is a different model at every point rather
# than the same model at a different theta. The window is wide enough to hold
# the answer and no wider, and the sweep warns if theta arrives at either end.
TH_LO, TH_HI = 0.150, 0.280

PAIRS = [('th', 'dshare', TH_LO, TH_HI),
         ('gam', 'hspend', 0.02, 0.70),
         ('h_hl', 'homeless', 1e-7, 0.49),
         ('aleph', 'vsl', 0.20, 24.0),
         ('lam', 'sud', LAM_LO, LAM_HI),
         ('b', 'part', 1e-5, 0.30)]

LABEL = {'part': 'drug participation rate',
         'sud': 'adult SUD rate',
         'hspend': 'housing spending / non drug spending',
         'housing_share': 'housing spending / income',
         'homeless': 'homelessness rate',
         'dshare': 'drug spending / income among users',
         'vsl': 'value of a statistical life, annual incomes',
         'prog': 'share of users who acquire a SUD',
         'bot50': "bottom half's share of earnings"}


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
    # the grid is built from SIG, so this moment does not depend on par at
    # all; it is reported here so it passes through the same convergence
    # test and the same table generator as the moments that do.
    m['bot50'] = _bottom_half_share(SIG)
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


def bracket_sud(par, lo=None, hi=None, iters=16):
    """
    Bracket lam on the adult SUD rate, REFITTING b at every trial.

    prog is sud/part, so it is meaningless when participation is near zero.
    Evaluated on a stale b the monotonicity test reads prog = 0 at one end,
    concludes the wrong sign, and drives the parameter to a bound: that is what
    made two earlier calibrations look as though the model had broken. Refitting
    b at each trial keeps participation on target, so prog is always defined.
    """
    tgt = TARGET['sud']
    lo = LAM_LO if lo is None else lo
    hi = LAM_HI if hi is None else hi
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        q = with_(par, lam=mid)
        q = with_(q, b=_b_for(q))
        if stats(q)['sud'] > tgt:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def calibrate(par=None, sweeps=5, verbose=True, checkpoint=None, fix=()):
    par = par or P()
    for s in range(sweeps):
        # HOUSING FIRST, THEN THE VALUE OF LIFE. aleph used to run first and the
        # calibration reported a VSL of 129 against a target of 80: aleph was on
        # target when it was set and the street moved underneath it afterwards.
        # aleph is additive in flow utility, so it barely touches the housing
        # choice, while the rent moves the continuation and hence the VSL a lot.
        # The dependence runs one way, so the housing block goes first.
        # GAMMA FIRST, then the street. Both move homelessness, so whichever runs
        # last is the one whose moment is actually hit, and homelessness is the
        # one that has to be.
        par = with_(par, gam=bracket(par, 'gam', 'hspend', 0.02, 0.70))
        par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-7, 0.49))
        par = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.20, 24.0, iters=26))
        # LAM AND B ARE SOLVED JOINTLY, not once each. prog is very nearly a
        # step function in lam at the calibrated dispersion: with b refit at
        # every trial it runs 0.065 at lam = 60, 0.221 at 121 and 0.9998 at 250,
        # so the whole target range sits inside a factor of two. bracket_prog
        # refits b inside itself, but the b that survives the sweep is the one
        # set AFTERWARDS, on participation, and on a curve that steep even a
        # small move in b throws prog off by more than the moment's tolerance.
        # That is what left prog at 0.247 against a target of 0.332 while lam
        # sat at 121, nowhere near its bounds, and looked like a model that
        # could not reach the moment. Alternating the two to a fixed point fixes
        # it: b still runs last, so participation is still the moment that is
        # actually hit, but lam is re-solved against the b that will survive.
        for _ in range(4):
            par = with_(par, lam=bracket_sud(par, LAM_LO, LAM_HI))
            par = with_(par, b=_b_for(par, iters=30))
        # THETA GOES LAST BUT ONE, AND THE FIRST VERSION HAD IT FIRST. calibrate()
        # starts from the class defaults, where lambda is 25 against a calibrated
        # 161 and the street is 0.05 against 0.00028, so a theta bracketed before
        # anything else has been refit is bracketed on a model that does not
        # exist: it ran to the top of its window on sweep one and reported that
        # the drug spending share could not be reached. The share depends on
        # lambda above all, since lambda is what makes using risky, so theta has
        # to be read at a lambda that is on target.
        #
        # b is refit inside bracket_with_b at every trial and AGAIN below, so
        # participation is still the moment that is hit exactly, which is the
        # rule the rest of this ordering follows.
        if 'th' not in fix:
            par = with_(par, th=bracket_with_b(par, 'th', 'dshare',
                                               TH_LO, TH_HI))
            if par.th <= TH_LO * 1.001 or par.th >= TH_HI * 0.999:
                print(f'   WARNING: theta arrived at a bound, {par.th:.4f} in '
                      f'[{TH_LO}, {TH_HI}]; the drug spending share is not hit')
            par = with_(par, b=_b_for(par, iters=30))
        # CHECKPOINT EVERY SWEEP. This process has been killed mid run four
        # times by the container reclaiming background work, and each time the
        # whole calibration was lost because the only write was at the end. Now
        # each sweep leaves a checkpoint on disk, so a kill costs one sweep
        # rather than all of them, and the next run can be seeded from it.
        #
        # THE CHECKPOINT IS NOT calibrated.json, AND THAT MATTERS. It used to be,
        # and calibrate() is called by scan_theta.py as well as by this file, so
        # four theta scans running in parallel each overwrote the canonical
        # calibration every sweep with a point from their own scan. Everything
        # read off the model while they ran, including a diagnosis of the
        # mortality channel, was computed at whichever theta had checkpointed
        # last. The file the note is built from is written in one place only, by
        # this file's __main__, and every other caller checkpoints under its own
        # name.
        import json as _json
        _json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS} | {'th': par.th, 'gam': par.gam},
                   open(checkpoint or f'checkpoint_th_{par.th:.2f}.json', 'w'),
                   indent=1)
        if verbose:
            m = stats(par)
            # ONLY THE MOMENTS SOMETHING IS ACTUALLY BRACKETED ON. TARGET
            # also carries housing_share, which nothing calibrates: gamma is
            # bracketed on hspend, housing over spending net of drugs, while
            # housing_share is housing over income, a separate untargeted
            # moment sitting about seven per cent below its data value. A
            # convergence test that counted it reported every converged sweep
            # as seven per cent off, forever.
            worst = max(abs(m[mom] / TARGET[mom] - 1.0)
                        for _, mom, _, _ in PAIRS)
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
    print(f"  income of the poorest household / average : "
          f"{float(YG.min() / (W / W.sum() @ YG)):.3f}")
    from stylized import value1
    v1 = np.array([value1(par, y, 'HF') for y in YG])
    print(f"  minimum ex ante value of life over the grid : {v1.min():.3f}")
    return m


if __name__ == '__main__':
    import json
    # SEEDED FROM THE EXISTING CALIBRATION when there is one. A cold start from
    # the class defaults is the more honest test of path independence, and it is
    # what this used to do, but it costs a sweep or two of every bracket working
    # on a model that is nowhere near calibrated. Delete calibrated.json to cold
    # start deliberately.
    import os
    seed = None
    if os.path.exists('calibrated.json'):
        seed = with_(P(), **json.load(open('calibrated.json')))
        print(f'seeded from calibrated.json at theta = {seed.th:.4f}')
    par = calibrate(seed, checkpoint='calibrated.json')
    report(par)
    json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS}
              | {'th': par.th, 'gam': par.gam},
              open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
