"""
A rough calibration of the stylized two period model. Seven parameters, seven
targets.

    gam     housing over non drug spending             26.8 %
    h_hl    homelessness rate                          0.399 %
    aleph   value of a statistical life                80 annual incomes
    lam     adult SUD rate, moderate or severe         4.54 %
    th      drug spending / income among users         20 %
    h_sm    share of the housed in the small unit      13.2 %
    b       drug participation rate                    10.13 %

THE STANDARD UNIT IS SET AND GAMMA IS CALIBRATED, which is the conventional
order and the third arrangement tried. h_lg = 0.40 of mean income is a market
fact quoted to the reader; the weight on housing is a preference, and a
preference is what a model is entitled to infer. Working backwards recovers the
same object, since a gamma and a grid that reproduce the share are two
descriptions of one calibration.

THE SMALL UNIT IS NO LONGER A FIXED QUARTER OF IT. h_sm used to be set at
h_lg/4, a ratio chosen in advance rather than measured, and the model then said
whatever that implied about how households sort across the two units: 45.7 per
cent of the housed in the small one against 13.2 in the data. It is bracketed
now, on that share, which is the arrangement the quantitative model already uses
for its three-way size distribution. One rental size is a market fact and the
other is inferred from how many households live in it.

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

import math
import os
import numpy as np
from stylized import (solve_child_damage, P, with_, aggregates, vsl,
                      priced_out_share)

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


# THE GRID IS 120 NODES, NOT 30, AND THE REASON IS THE DRUG DECISION.
#
# With the means test at half of median income the voucher no longer cushions the
# poor, users are poorer, and the disorder hazard lambda has to be far larger to
# convert the same fraction of them. At lambda near 450 the use decision is close
# to bang-bang, and on a 30 node grid participation moved in lumps: at lambda=455
# it ran 4.24 per cent at b=9.159e-4 and 13.83 at b=9.00e-4, so a 1.7 per cent
# change in b moved participation by nine and a half points and the 5.13 per cent
# target fell in the gap between two attainable values. The SUD rate did the same
# thing, sitting at 3.0 per cent across lambda from 435 to 475 and jumping to 5.3,
# with the 3.68 target in between. Neither moment was reachable and the sweep
# walked lambda to its ceiling.
#
# The lumps are the discretisation, not the economics: the threshold in income is
# bisected inside a node, but the housing rung a household picks is discrete, so
# several nodes can flip together. Four times the nodes cuts each lump to a
# quarter and the brackets have somewhere to land. It costs four times the solve.
# AND THE NODES ARE PLACED BY QUANTILE, NOT BY LOG INCOME, with extra density at
# the bottom. Everything the model is about happens there: who is priced out of
# housing, who uses, who acquires the disorder. At kappa = 2 sixty of the hundred
# and twenty nodes sit in the bottom quarter of the distribution and eighty four
# in the bottom half, against thirty and sixty under an even spacing.
#
# Two things fall out of doing it this way rather than by truncating log income at
# five times the mean, which is what this used to do.
#
# The mean is exactly one. Each node is the lognormal quantile at the mass midpoint
# of its interval and each weight is that interval's mass, so the discretisation
# integrates to the distribution rather than to a truncation of it.
#
# And the median comes out where the data put it. The old grid threw away the top
# tail, so sigma had to be 1.1854 to leave the bottom half with 17.2 per cent of
# earnings, and that put the median at 0.518 of the mean. Here sigma is 0.9633 and
# the median is 0.636 of the mean, against roughly 0.65 in United States household
# income. That matters for the voucher: the means test is half of median income, so
# a distribution that is too unequal makes the test tighter than HUD's rule is.
def _ndtr(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _ndtri(p, lo=-12.0, hi=12.0, iters=80):
    """The normal quantile by bisection. scipy is not installed here."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if _ndtr(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


GRID_N = 120
GRID_KAPPA = 2.0      # above one packs the nodes toward the bottom

# EVERY NODE IS THE CONDITIONAL MEAN OF THE LOGNORMAL ON ITS OWN INTERVAL, not
# the quantile at the interval's midpoint. Two things follow. The mean is one by
# construction rather than by rescaling, and the bottom interval, which runs all
# the way to zero, is represented by the mass it actually carries instead of by
# a quantile chosen arbitrarily close to the tail. The old grid truncated at the
# two tenths of a percentile and the truncation point, not the model, was what
# set how many households could not afford to rent.
#
# GRID_KAPPA PUTS THE DENSITY AT THE BOTTOM, which is where the drug, housing
# and homelessness margins all sit. At kappa = 2 two thirds of the nodes lie
# below the median.
#
# WHAT POOLING THE BOTTOM WAS TRIED FOR, AND WHY IT IS NOT HERE. A lognormal
# matching the bottom half's 17.2 per cent leaves 10.7 per cent of households
# below y = 0.20, and 0.20 is where half of income stops covering the 0.10 rent
# on the small unit. Resolved finely, every one of them is FORCED onto the
# street and h_hl has no interior solution. Pooling the bottom was measured and
# does not fix it: a pool sits at its own conditional mean, so it is either
# wholly below the affordability floor or wholly above it, and the first pool
# that clears 0.20 is the bottom 23 per cent. Pooling the bottom five per cent
# made homelessness WORSE, 1.96 per cent against 1.32, because the pool at 0.096
# cannot pay the rent even while employed. The margin is at the eleventh
# percentile, not in the tail, so no discretisation reaches it.
#
# A CONSUMPTION FLOOR WAS TRIED AND REMOVED. The quantitative model has one and
# the stylized model was given one to match, on the statutory SNAP rule and paid
# in kind so it could not cover rent. It was then ablated and it does not earn
# its place: with the bottom pooled the model passes through the 0.399 target
# without it, at h_hl near 0.00055, and the FORCED share of homelessness is
# 0.305 per cent against 0.288 with the transfer. The pool does that work, not
# the transfer, and a model whose purpose is to be easy to follow should not
# carry a parameter, a moment, a taper and an in kind restriction that change
# nothing. The quantitative model keeps its own.
def _tail_mean(sig, q):
    """E[Y 1{F(Y) < q}] for a lognormal with mean one."""
    if q <= 0.0:
        return 0.0
    if q >= 1.0:
        return 1.0
    return _ndtr(_ndtri(q) - sig)


def _cond_mean(sig, a, b):
    """E[Y | a < F(Y) < b], the value a pool of that mass sits at."""
    return (_tail_mean(sig, b) - _tail_mean(sig, a)) / (b - a)


def _trunc_level(sig, target, lo=1e-6, hi=0.90):
    """
    The raw threshold t whose TRUNCATED distribution has its lowest income at
    `target` once the survivors are renormalised to mean one.

    Truncating raises the mean of what is left, and income is normalised to mean
    one, so the two have to be solved together: dropping everyone below t leaves
    a mean M(t) = E[Y | Y > t] and a lowest income of t/M(t). One bisection in t.
    """
    def lowest(t):
        q = _ndtr((math.log(t) + 0.5 * sig * sig) / sig)
        m = (1.0 - _tail_mean(sig, q)) / max(1.0 - q, 1e-14)
        return t / m
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if lowest(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _pool(sig, floor, hi=0.60):
    """The smallest bottom pool whose conditional mean clears the floor.

    SUPERSEDED BY FLOORING, and kept only because the scans in scan_theta.py
    still import it. Read _floor_level and _grid for what the model does now,
    and the note over GRID_FLOOR for why pooling had to go.

    THE FLOOR IS THE RENT ON THE SMALLEST UNIT, and it is a real threshold
    rather than a numerical one. Food assistance is paid in kind, so rent comes
    out of the household's own income: a household whose income in a state falls
    below p_r*h_sm cannot rent at all, employed or not, and is on the street
    whatever the street is worth. In a lognormal matching the bottom half's 17.2
    per cent that is 2.5 per cent of households, which puts homelessness at 1.25
    per cent against a target of 0.399 and leaves h_hl with nothing to decide.
    Those households are an artefact of resolving the very bottom of a lognormal
    node by node: a household at the third percentile of PERMANENT income for a
    thirty year period is not a household the data contains, it is the tail of a
    functional form. Pooling the bottom into one mass point at its own
    conditional mean keeps the mean and the bottom half's share exactly, and
    puts the poorest households where the poorest households in the data are:
    able to rent, badly.
    """
    lo = 1e-9
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        if _cond_mean(sig, 0.0, mid) < floor:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


POOL_MARGIN = 1.08    # superseded by GRID_FLOOR; kept for scan_theta.py
# THE LOWEST INCOME CLEARS THE RENT BY EIGHT PER CENT. It has to clear it by
# something: a household whose income equals its rent exactly consumes nothing
# and its flow utility is minus infinity. Eight per cent puts the poorest
# household at 0.108 of mean income, where the pooled cell used to sit.
TRUNC_FLOOR = 1.08


def _grid(sig, n=GRID_N, kappa=GRID_KAPPA):
    """
    The income grid: the lognormal TRUNCATED below the rent on the smallest unit.

    THE HISTORY MATTERS HERE, because two earlier versions of this function each
    fixed one defect and created another.

    Households below the rent on the smallest unit cannot rent at all and are on
    the street whatever the street is worth, so the deep tail of a lognormal
    drives homelessness to 1.25 per cent against a target of 0.399 and leaves
    h_1 with nothing to decide. POOLING the bottom 6.68 per cent into one mass
    point at its conditional mean fixed that and left the pool WIDER THAN THE
    5.13 PER CENT PARTICIPATION TARGET, so the cell used or did not as a block
    and no b delivered the target. Integrating the drug decision over a sub grid
    inside the pool was a patch for that, and it took the MASS of users from
    incomes inside the pool while taking the DOSE from the pool's single
    representative, which is a different household: half of all users carried a
    disorder probability read off a household that was not using, and lambda ran
    to 5972 fitting that grid constant.

    FLOORING the distribution at the rent instead was better and still not
    enough. The atom is smaller, 3.08 per cent rather than 6.68, but it is still
    an atom of identical households, and measured directly it moved
    participation from 5.93 to 3.17 per cent as b crossed the value that flips
    it. The target of 5.13 sits inside that jump, so b still could not reach it.

    TRUNCATION removes the atom rather than shrinking it. The distribution is
    conditional on being able to rent, every cell carries a small mass, and
    participation is continuous in b, which is what a bracketing calibration
    needs. The economic claim is the one the pooling note always made: a
    household at the third percentile of PERMANENT income over a thirty year
    period is the tail of a functional form rather than a household the data
    contains. Truncation states that claim directly instead of stacking those
    households at a single income and pretending they are one type.
    """
    par = P()
    t = _trunc_level(sig, TRUNC_FLOOR * par.pr * par.h_sm)
    q_f = _ndtr((math.log(t) + 0.5 * sig * sig) / sig)
    u = np.arange(n + 1) / float(n)
    p = q_f + (1.0 - q_f) * u ** kappa
    p[0], p[-1] = q_f, 1.0
    w = np.diff(p)
    tv = np.array([_tail_mean(sig, q) for q in p])
    v = np.diff(tv) / w
    mean = float((w * v).sum() / w.sum())
    return v / mean, w / w.sum()


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

# THE MEANS TEST IS HALF OF MEDIAN INCOME, the HUD rule the quantitative model
# uses, and the median moves with SIG. Tying the two together here means the
# voucher rule cannot drift away from the income distribution it is applied to.
def _median_of(yg, w):
    """The median of the discretised distribution, interpolated inside the node
    the median falls in, so it does not jump from node to node."""
    c = 0.0
    for i, (yi, wi) in enumerate(zip(yg, w)):
        if c + wi >= 0.5:
            lo = yg[i - 1] if i else yi
            frac = (0.5 - c) / wi
            return float(lo + frac * (yi - lo))
        c += wi
    return float(yg[-1])


YV_HALF_MEDIAN = 0.5 * _median_of(*_grid(SIG))
assert abs(P().yV - YV_HALF_MEDIAN) < 5e-4, (
    f'yV is {P().yV} but half of median income at SIG={SIG:.4f} is '
    f'{YV_HALF_MEDIAN:.4f}; set yV in stylized.py to match')

# THE CELL EDGES AND THE TRUE CDF, handed to aggregates so the share of a cell
# inside the use region is read off the distribution rather than interpolated
# across the gap between two node values. EDGES[i] is the cumulative mass below
# cell i, so EDGES[i+1] - EDGES[i] is that cell's weight by construction.
# THE GRID'S OWN SCALE, so CDF and EDGES speak the same language. This is the
# fix for the second half of the step function bug. threshold() splits a
# boundary cell by comparing cdf(ystar) against EDGES, the cumulative masses of
# the cells, so the two have to be the same measure. They stopped being the same
# the moment the grid was truncated and renormalised: EDGES run 0 to 1 over the
# SURVIVORS, while CDF was still the raw lognormal running q_f to 1, and the
# grid's incomes had additionally been divided through by the survivors' mean.
# Comparing them put the threshold in the wrong cell, so a cell could be handed
# a fraction of a third when it should have been whole, and participation moved
# in jumps of a cell's mass with the calibration target inside one of them.
Q_F = _ndtr((math.log(_trunc_level(SIG, TRUNC_FLOOR * P().pr * P().h_sm))
             + 0.5 * SIG * SIG) / SIG)
GRID_MEAN = (1.0 - _tail_mean(SIG, Q_F)) / max(1.0 - Q_F, 1e-14)


def CDF(y):
    """
    P(income <= y) for the distribution THE GRID ACTUALLY HOLDS: the lognormal
    conditional on clearing the rent, renormalised to mean one. Returns a share
    of the surviving mass, which is what EDGES measures.
    """
    if y <= 0.0:
        return 0.0
    raw = y * GRID_MEAN
    q = _ndtr((math.log(raw) + 0.5 * SIG * SIG) / SIG)
    return min(max((q - Q_F) / max(1.0 - Q_F, 1e-14), 0.0), 1.0)


YG, W = _grid(SIG)
EDGES = np.concatenate(([0.0], np.cumsum(W)))
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
# THE TWO POPULATION RATES ARE THE SURVEY'S OWN SEVERITY SPLIT. NSDUH 2024
# adults 26 and over, from the file in data/: mild drug use disorder is 5.59 per
# cent and moderate or severe is 4.54, so any disorder is 10.13. Participation is
# the whole of that and the SUD rate is the moderate-or-severe part, which is the
# split the extraction code in data/ already uses and the one the life cycle
# model now targets. The old pair, 0.0513 and 0.0368, matched no cut of that
# variable and implied that 72 per cent of users carry a disorder where the
# survey says 45.
def _drug_targets():
    """participation, the SUD rate and the spending share, from data/.

    All three were typed and two were wrong. The population rates in use were
    the EIGHTEEN and over figures, 10.13 and 4.54 per cent, while the model's
    households are 26 and over and the note says so throughout; its own universe
    gives 8.90 and 3.68. The spending share divided 2016 spending by 2024
    PERSONAL income and got 19.7; family income is what this model's budget
    constraint spends and the two sides have to be in one year's dollars, which
    gives 16.2. See data/make_drug_spending_target.py.
    """
    import csv as _csv
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', '..', 'data', 'drug_spending_target.csv')
    with open(os.path.normpath(f)) as fh:
        return {r['quantity']: float(r['value']) for r in _csv.DictReader(fh)}


_DRUG = _drug_targets()


def _hsmall_target():
    """Sizes 1 and 2 of the ACS split, from the file the Fortran's target uses."""
    import csv as _csv
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', '..', 'data', 'us_housing_dist.csv')
    with open(os.path.normpath(f)) as fh:
        rows = {int(r['size']): float(r['share']) for r in _csv.DictReader(fh)}
    return rows[1] + rows[2]


_HSMALL = _hsmall_target()

# HOMELESSNESS IS 1.0 PER CENT AND r_use IS ADDED, author 12 September.  The
# rate moves off the 0.399 per cent point-in-time count and onto the
# quantitative model's own h_1 target of 1 per cent, so the two models are
# aimed at the same number; and the income of users, which used to be read as
# a diagnostic under the name r_use, becomes a TARGET at 0.74, the Table 7
# figure the quantitative model's y_u is aimed at: *"i think you should also
# calibrate kappa so that the average income of a user is 0.74"*.
# u1 IS CALIBRATED ON THE SUD SHARE OF THE HOMELESS, author 12 September: *"i
# mean to include the risk of unemployment with Sud to match the share of
# homeless with Sud"*.  0.217 is the quantitative model's sud_homeless target.
#
# THE DENOMINATOR IS PERIOD 2 ALONE AND THAT IS NOT A CHOICE.  Every period 1
# household in this model is CLEAN by construction -- the disorder is realised
# at the transition -- so period 1 homelessness cannot contain a single case and
# including it is pure dilution.  Measured over both periods the moment tops out
# at 10.1 per cent, less than half the target, and only there at a participation
# rate of 29 per cent; over period 2 alone it runs 0.361 at u1 = 0.05 down to
# 0.023 at 0.25 and crosses 0.217 at about u1 = 0.127, where participation and
# the income of users are both near their own targets.  So the both-period
# version is unreachable for reasons of TIMING rather than economics, and it is
# the period 2 share that is the analogue of a survey cross-section of adults
# who have had a lifetime to acquire the disorder.
#
# IT FALLS IN u1, WHICH IS THE RIGHT SIGN.  A larger unemployment risk from the
# disorder deters use, so fewer households carry it and fewer of the homeless
# have it.  bracket() reads its direction from the endpoints, so a falling
# moment is bisected correctly.
TARGET = dict(part=_DRUG['participation'], homeless=0.0100, r_use=0.74,
              # the author, 13 September: raise the lowest income until only
              # half a per cent of households cannot afford the rental
              priced_out=0.005,
              sud_of_homeless2=0.217,
              sud=_DRUG['sud_rate'], vsl=80.0,
              dshare=_DRUG['drug_spending_share'],
              housing_share=0.30, hspend=0.268,
              bot50=BOT50_TARGET,
              # AMERICAN COMMUNITY SURVEY B25042, occupied units, read from
              # data/us_housing_dist.csv, which is the same file the
              # quantitative model's three-way size distribution comes from.
              #
              # THE COLLAPSE IS TO TWO SIZES AND IT IS NOT THE SMALL BIN. This
              # model has two rentals where the quantitative model has three, so
              # its h_2 is everything below the standard family unit, not the
              # studio-and-one-bedroom bin alone. Targeting that bin, 13.2 per
              # cent, was a mistake of exactly one bin: the share is INCREASING
              # in h_sm over the whole admissible range and bottoms out near 24
              # per cent as the small unit goes to nothing, so 13.2 sits below
              # anything the model can produce and the bracket ran to its lower
              # bound. Sizes 1 and 2 together, 37.3 per cent, are what h_2
              # stands for here, and they are interior: the model gives 32.0 per
              # cent at h_sm = 0.05 and 41.7 at 0.10.
              )

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
#
# AND IT REACHES FAR UP, FOR A REASON WORTH KNOWING. The ceiling was 4000 and it
# BOUND: with b refit at every trial the adult SUD rate reaches 3.38 per cent at
# lambda = 4000 against a target of 3.68, so every trial read low, the bracket
# walked to its ceiling and reported a corner as a calibration. The rate does not
# saturate below the target, it just gets there slowly, because a household that
# faces a steeper hazard per unit BUYS FEWER UNITS: v falls roughly as 1/lambda,
# so pi(v) = 1 - exp(-lambda v) creeps rather than jumps. It crosses the target
# between 4000 and 8000 and reaches its own ceiling, prog = 1 and hence
# sud = part = 5.13 per cent, by 20000. So the bracket runs to 20000, which is
# where the moment stops responding rather than where patience ran out.
LAM_LO, LAM_HI = 0.05, 20000.0

# THETA IS SET, NOT BRACKETED, and a correction to what an earlier version of this
# comment said. It claimed the drug spending share is bimodal in theta, running
# 5.2 per cent at theta = 0.21 and jumping to 18.8 at 0.22, so that only a narrow
# window was safe to bisect on. That measurement refit b ALONE. With the whole
# model recalibrated at each theta the share is smooth and monotone:
#
#     theta   0.18    0.20    0.21    0.22    0.23
#     share  15.2%   18.4%   20.2%   21.6%   24.2%
#     r_mort  0.15    0.15    0.39    0.93    1.90
#
# The jump was lambda, gamma and the street being held at their theta = 0.23
# values while theta moved. The second row is what decides the setting: r_mort is
# what the mortality channel alone does to the income ratio of users, and it has
# to be below one for the mechanism this model exists to show. It crosses one
# between 0.22 and 0.23, so theta = 0.21 buys a spending share of about 20 per
# cent with the reversal comfortably intact, and theta = 0.23 buys 24 per cent
# with no reversal at all. frontier.py is the scan.
# THETA IS BRACKETED, which the note above already said and the list did not do.
# gamma moved onto hspend and theta never followed, so the drug spending share
# stayed an untargeted moment the model missed. It is targeted now.
# THE SMALL UNIT CANNOT OUTGROW THE GRID IT IS PART OF. _grid truncates the
# income distribution below TRUNC_FLOOR times the rent on the small unit, and it
# does so ONCE, at import, from the class value of h_sm. So a trial h_sm above
# that value prices the poorest households on the grid out of the only unit they
# could afford: they cannot rent at all, they are homeless whatever the street
# is worth, and homelessness runs from 0.4 per cent at h_sm = 0.10 to 3.0 at
# 0.15 and 20 at 0.39. None of that is the model answering a question about unit
# sizes; it is the grid and the parameter disagreeing about what the small unit
# is. Capping the bracket at the floor keeps every trial on a grid that matches
# it. The cap does not bind at the answer, which is near 0.075.
#
# THIS DOES NOT CARRY TO THE QUANTITATIVE MODEL, and it was checked there before
# this was closed. Its smallest rental is
# smallest_rental_relative_to_lowest_income, a RATIO to the lowest income on the
# grid rather than an absolute size, so the unit moves with the grid by
# construction and cannot outrun it. See TRANSITION_LESSONS.md section 7.
H_SM_HI = float(YG[0]) / (TRUNC_FLOOR * P().pr)

PAIRS = [('gam', 'hspend', 0.02, 0.70),
         ('h_hl', 'homeless', 1e-7, 0.49),
         ('aleph', 'vsl', 0.20, 24.0),
         ('lam', 'sud', LAM_LO, LAM_HI),
         ('b', 'part', 1e-5, 0.30)]

LABEL = {'part': 'drug participation rate',
         'sud': 'adult SUD rate',
         'hspend': 'housing spending / non drug spending',
         'housing_share': 'housing spending / income',
         'homeless': 'homelessness rate',
         'priced_out': 'share who cannot afford the rental',
         'dshare': 'drug spending / income among users',
         'hsmall': 'share of the housed in the small unit',
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
    # THE CHILD DAMAGE IS AN EQUILIBRIUM OBJECT AND IS SOLVED HERE, LAST.
    #
    # chdmg is V(1,0) - V(1,1), the child's loss from the parent's disorder, and
    # it depends on V1, which depends on it.  with_() clears it on any parameter
    # change, so every bracket step arrives here with it unset and every solve
    # below runs on a damage computed at THESE parameters.  Solving it anywhere
    # earlier would be solving it at the previous ones.
    par = solve_child_damage(par)
    m = aggregates(par, YG, W, edges=EDGES, cdf=CDF)
    m['vsl'] = vsl(par)
    # the grid is built from SIG, so this moment does not depend on par at
    # all; it is reported here so it passes through the same convergence
    # test and the same table generator as the moments that do.
    m['bot50'] = _bottom_half_share(SIG)
    # THE PRICED-OUT SHARE, which is the income floor's own moment.  See
    # priced_out_share in stylized.py for why homelessness cannot serve as one
    # when there is a single rental.
    m['priced_out'] = priced_out_share(par, YG, W)
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


def calibrate(par=None, sweeps=5, verbose=True, checkpoint=None, fix=(), tol=0.007):
    # fix IS HONOURED NOW, AND IT HAS TO BE. It sat in this signature unused
    # while theta was a SET parameter, where holding it was what the sweep did
    # anyway, so frontier.py could pass fix=('th',) and get what it asked for by
    # accident. Bracketing theta broke that silently and in the worst way: every
    # point of the frontier scan would have re-solved theta to the same
    # calibrated value, so the theta column would have named a number the row
    # was not computed at, every row would have been the same model, and
    # TH_BREAK -- which the paper quotes as the point past which its mechanism
    # is gone -- would have been read off a scan that never varied theta.
    par = par or P()
    fix = set(fix)
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
        if 'gam' not in fix:
            par = with_(par, gam=bracket(par, 'gam', 'hspend', 0.02, 0.70))
        # h_sm BEFORE h_hl, for the reason gamma runs before the street: both
        # move homelessness, a cheaper small unit takes households off it, and
        # whichever runs last is the one whose moment is actually hit. The
        # homelessness rate is the one that has to be, so the street runs last.
        # h_sm IS NOT BRACKETED ANY MORE.  There is one rental -- see _options in
        # stylized.py -- so the small unit is out of the choice set and the
        # share of the housed in it is not a moment the model can produce.
        if 'h_hl' not in fix:
            par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-7, 0.49))
        if 'aleph' not in fix:
            par = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.20, 24.0, iters=26))
        # THETA BEFORE THE DRUG PAIR. lam and b are bracketed on the disorder
        # rate and on participation and both move with the quantity used, so
        # theta is settled before they are chased; b still runs last, so
        # participation is still the moment that is actually hit.
        #
        # WITH b REFIT AT EVERY TRIAL, which is what bracket_with_b exists for
        # and what its docstring already named theta as needing. dshare is drug
        # spending over income AMONG USERS, so it is only defined on whoever is
        # using, and theta moves who that is: read at a stale b the bracket is
        # comparing spending shares across different populations. Wired to the
        # plain bracket it would also have made the sweep's own convergence test
        # unreachable, because b is refit LAST every sweep and would move dshare
        # off the target theta had just been set to, every sweep, forever --
        # which is the residual the note above h_hl and aleph describes, and
        # there is no reason to add a third one on purpose.

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
        # THETA IS INSIDE THE LOOP, for exactly the reason lambda is. Run once
        # ahead of it, theta was set on the drug spending share and then lambda
        # moved underneath it -- 222 to 192 to 176 over two sweeps -- and a
        # different SUD hazard changes the quantity used, so dshare came out 32
        # and then 26 per cent off the target theta had just been bracketed on.
        # The gap was closing at about a fifth a sweep, which does not reach the
        # tolerance inside the sweep budget. The three are coupled through the
        # quantity used: theta sets how much a user buys, lambda turns that
        # quantity into a disorder rate, and b decides who uses at all.
        # Alternating all three to a fixed point is what the note above already
        # prescribes for lambda and b, and b still runs LAST, so participation
        # is still the moment that is actually hit.
        for _ in range(4):
            if 'lam' not in fix:
                par = with_(par, lam=bracket_sud(par, LAM_LO, LAM_HI))
            if 'b' not in fix:
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
        # ONLY THE MOMENTS SOMETHING IS ACTUALLY BRACKETED ON. TARGET
        # also carries housing_share, which nothing calibrates: gamma is
        # bracketed on hspend, housing over spending net of drugs, while
        # housing_share is housing over income, a separate untargeted
        # moment sitting about seven per cent below its data value. A
        # convergence test that counted it reported every converged sweep
        # as seven per cent off, forever.
        m = stats(par)
        # ONLY THE MOMENTS SOMETHING IS STILL FREE TO MOVE. A held parameter's
        # moment is off by however far the hold puts it, which is the point of
        # holding it, and counting it would report every sweep of a frontier
        # point as unconverged and run all of them for nothing.
        live = [(n, mom) for n, mom, _, _ in PAIRS if n not in fix]
        # default=0.0 for the degenerate case where everything is held:
        # nothing is free to move, so there is nothing left to converge.
        worst = max((abs(m[mom] / TARGET[mom] - 1.0) for _, mom in live),
                    default=0.0)
        if verbose:
            # EVERY BRACKETED PARAMETER, and the moment that is worst. The line
            # named four of them, which predated gamma, theta and h_sm being
            # bracketed, so the three most recently added were the three a
            # reader could not see.
            wmom = max(live, key=lambda P_: abs(m[P_[1]] / TARGET[P_[1]] - 1.0),
                       default=(None, 'nothing free'))[1]
            print(f'  sweep {s+1}  worst {worst:7.3f} on {wmom:9s} '
                  f'gam={par.gam:.4g} th={par.th:.4g} h_sm={par.h_sm:.4g} '
                  f'h_hl={par.h_hl:.4g} aleph={par.aleph:.4g} '
                  f'lam={par.lam:.4g} b={par.b:.4g}', flush=True)
        # STOP WHEN EVERY TARGETED MOMENT IS HIT. Each bracket restarts from its
        # own bounds every sweep, so a converged sweep reproduces itself: the
        # remaining sweeps cost a quarter of an hour each and move nothing. The
        # test needs at least two sweeps behind it because the first sweep off a
        # seed can look converged on moments the seed already fitted while the
        # parameters that move them have not been re-solved together yet.
        # THE TOLERANCE CANNOT BE TIGHTER THAN ABOUT 0.006, and that is a
        # property of the sweep order rather than of the bisections. b runs LAST
        # so that participation is the moment actually hit, and it is: the gap
        # there is zero to four decimals. But aleph and the lambda-b loop both
        # run AFTER h_hl and both move homelessness a little, so the street is
        # fitted and then moved off by half a per cent, every sweep, forever.
        # Two successive sweeps agreed to five significant figures on lambda and
        # on b while reporting the same 0.006, which is what a structural
        # residual looks like: a tolerance below it does not buy accuracy, it
        # just runs the remaining sweeps. Reordering to put h_hl last would
        # close it and open a worse one, because h_hl moves the value of being
        # unhoused and so moves participation.
        if s >= 1 and worst < tol:
            if verbose:
                print(f'  converged: every targeted moment within '
                      f'{100 * tol:.1f} per cent', flush=True)
            break
    # GAMMA IS NOT RE-IMPOSED HERE. It used to be returned as 0.25*(1-theta),
    # which silently overwrote the value the (theta, gamma) scan chose: at
    # theta = 0.20 that is 0.200 rather than 0.2225, and the two are on opposite
    # sides of a cliff, 1.9 per cent drug spending against 13. The tie belongs
    # to the old calibration where theta was 0.11 and gamma was not a separate
    # object; it does not belong here.
    return par


def polish(par, verbose=True):
    """
    One pass over everything EXCEPT theta, at the final theta.

    The housing block is bracketed BEFORE theta and is therefore fitted to the
    theta that theta then replaces. On the last sweep there is no next sweep to
    correct that, and the model written out carries a street and a housing
    weight that belong to a different theta: after sweep one the homelessness
    rate sat 17 per cent off its target for exactly this reason. This runs the
    rest of the sweep once more with theta held where it landed, so every moment
    but the drug spending share is on target at the theta that is reported, and
    the drug spending share moves only by however much the others move it.

    h_2 IS IN THIS LIST. It was not, and it is a bracketed parameter now: left
    out, the small unit stayed at whatever the last sweep gave it while gamma
    and the street were re-fitted around it, which is the same defect this
    function exists to remove.
    """
    if verbose:
        print(f'\npolishing at theta = {par.th:.4f}')
    par = with_(par, gam=bracket(par, 'gam', 'hspend', 0.02, 0.70))
    # h_sm is out of the choice set with the second rental; see above.
    par = with_(par, h_hl=bracket(par, 'h_hl', 'homeless', 1e-7, 0.49))
    par = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.20, 24.0, iters=26))
    for _ in range(2):
        par = with_(par, lam=bracket_sud(par, LAM_LO, LAM_HI))
        par = with_(par, b=_b_for(par, iters=30))
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
          "   (untargeted; theta is set, see the note above)")
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
        # ONLY THE PARAMETERS THIS FILE CALIBRATES, which is what keep is for.
        # theta is one of them again, so it is seeded like the rest; the reason
        # the exclusion existed is that a checkpoint written while theta was
        # briefly calibrated reseeded it at 0.2236 over a class value of 0.21,
        # and that is only a hazard while theta is NOT bracketed.
        keep = {n for n, _, _, _ in PAIRS}
        kw = {k: v for k, v in json.load(open('calibrated.json')).items()
              if k in keep}
        seed = with_(P(), **kw)
        print(f'seeded from calibrated.json; theta seeded at {seed.th:.4f} '
              f'and SET there: the drug spending share is untargeted')
    par = calibrate(seed, checkpoint='calibrated.json')
    par = polish(par)
    report(par)
    json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS}
              | {'th': par.th, 'gam': par.gam},
              open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
