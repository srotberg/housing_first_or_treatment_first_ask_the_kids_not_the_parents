"""
THE AUTHOR'S CALIBRATION METHOD, which is the quantitative model's.

    parameter <- parameter - adjuster * (moment - target)     for EVERY parameter
    re-solve ONCE
    repeat

WHY THIS REPLACES THE BRACKETING SWEEP.  Author, 12 September: *"but if you used
my method it should run very very fast!"*, *"you just adjust the parameters based
on my method"*, *"you just need to set up the updates correctly"*.  They are
right on both counts and the old sweep was wrong on both.

    bisection : 18 solves to move ONE parameter, every other one frozen,
                22 brackets a sweep = 396 solves, about 6.4 minutes
    this      : 2 solves to move ALL NINE (the second is omega_c's
                counterfactual), about 2 seconds

AND THE NON-MONOTONICITY THAT WRECKED FOUR SWEEPS WAS AN ARTIFACT OF BISECTION.
r_use is non-monotone in kap, participation looked non-monotone in b -- but
bisection REQUIRES monotonicity and finds the wrong root or a bound without it,
while this rule needs only the SIGN of each response, which is fixed and known.
The surface was never the problem; the solver was.

THE ASSIGNMENT, in the author's own words, 12 September:

    *"gamma rises when spending on rent to income ratio is below 26.8%, beta
    rises when it is below target, unemployment with SUD should rise if too few
    homeless with SUD, kappa is set to 3, h1 need to rise if homelessness is
    below 1%, h2 is just set to some exogenous number to give a decent renters
    spending over 50% on rent, omega_c needs to match the child gap, and it
    should rise if the child gap is too small, theta is held at 0.16, b needs to
    match the user rate, and should decline if user rate is too low, onset should
    match share of SUD and should rise if the SUD rate is too low"*,

    *"pi_eu should be chosen to match an unemployment rate of 4.85% as in the
    quant model"* and *"you raise pi_eu if the unemployment rate is below the
    data"*, and *"you also need aleph to match the value of life ... and you
    raise it if the value of life is too low"*.

EVERY SIGN IS +1 EXCEPT b.  "b should DECLINE if the user rate is too LOW" is
the opposite of the rule's default, and it is the economics rather than a slip:
b is the Stone-Geary shifter, so a SMALLER b makes abstaining costlier and pulls
MORE households into use.  A mechanical reading would have got this one backwards.

THE STEP IS RELATIVE, not absolute.  The Fortran carries the scale in each
parameter's own adjuster because each has been tuned by hand over months.  Here
the gap is divided by the target first, so one adjuster is meaningful across
parameters that range from 1e-4 (h_hl) to 15 (aleph).  It is the same rule with
the scale factored out.
"""
import math
import numpy as np

import calibrate as C
from calibrate import stats
from stylized import P, with_, child_sud_odds_ratio, child_homeless_odds_ratio

# (name, moment, target, sign, adjuster, lo, hi)
# (name, moment, target, sign, adjuster, lo, hi).  SEVEN CALIBRATED.
#
# beta AND u1 ARE SET, not calibrated, and both for reasons measured today.
#   beta = 1, author: *"exogenous, not calibration"*, *"beta=1.47 is not
#     believable"*.  Calibrated on net worth over income of 3 it went to 1.477,
#     and to 1.621 at zero interest.  networth becomes an OUTPUT.
#   u1 = 0.1625, its MEASURED value.  It was never a free parameter -- the
#     declaration reads "RESOURCE: the disorder costs you a job. Measured." --
#     and aiming it at the SUD share of the homeless was a sign error: the ratio
#     FALLS in u1, because a bigger job-loss penalty deters use so hard the
#     disorder disappears and the numerator goes to zero.  sud_of_homeless2
#     becomes an OUTPUT; its ceiling is 0.084 against a target of 0.217.
# (name, moment, target, sign, adjuster, lo, hi).  EIGHT CALIBRATED.
#
# beta IS SET AT 1, not calibrated.  Author: *"exogenous, not calibration"*,
# *"beta=1.47 is not believable"*.  On net worth over income of 3 it went to
# 1.477, and 1.621 at zero interest -- a household valuing a period thirty years
# out MORE than the present.  networth becomes an OUTPUT.
#
# u1's SIGN IS NEGATIVE, and it took two measurements to get right.  The rule
# said "unemployment with SUD should rise if too few homeless with SUD", but the
# SUD share of the homeless FALLS in u1.  The author supplied the mechanism --
# *"when u1 rises, b has to fall"*, *"if b is low enough people will eventually
# use"* -- and the numbers show it, with b refit at every u1 to hold
# participation at 8.9 per cent:
#
#   u1       b*       r_use    hl_sud     ratio
#   0.0485  0.02695   0.300   0.000704   0.2394
#   0.0550  0.02674   0.379   0.000656   0.2158
#   0.1625  0.02351   0.751   0.000079   0.0252
#   0.8000  0.01175   0.774   0.000000   0.0000
#
# b falls to hold participation, so use is recruited from the TOP of the
# distribution -- r_use runs 0.300 to 0.774 -- and rich users do not sleep rough.
# The target of 0.217 sits at u1 about 0.0545, just above u0.
# (name, moment, target, sign, adjuster, lo, hi).  EIGHT CALIBRATED.
#
# beta IS SET AT 1.  Author: *"exogenous, not calibration"*, *"beta=1.47 is not
# believable"*.  On net worth over income of 3 it went to 1.477, and 1.621 at
# zero interest -- a household valuing a period thirty years out MORE than the
# present.  networth becomes an OUTPUT.
#
# u1's SIGN IS NEGATIVE, and it took two measurements to get right.  The spec
# said "unemployment with SUD should rise if too few homeless with SUD", but the
# share FALLS in u1.  The author supplied the mechanism -- *"when u1 rises, b has
# to fall"*, *"if b is low enough people will eventually use"* -- and the numbers
# show it, with b refit at every u1 to hold participation at 8.9 per cent:
#
#   u1       b*       r_use    hl_sud     ratio
#   0.0485  0.02695   0.300   0.000704   0.2394
#   0.0550  0.02674   0.379   0.000656   0.2158
#   0.1625  0.02351   0.751   0.000079   0.0252
#   0.8000  0.01175   0.774   0.000000   0.0000
#
# b falls to hold participation, so use is recruited from the TOP of the
# distribution -- r_use runs 0.300 to 0.774 -- and rich users do not sleep rough.
# 0.217 sits at u1 about 0.0545, just above u0.  NOTE THE TENSION this creates:
# at that u1 users sit at 0.38 of average income against the data's 0.74.
SPEC = [
    ('gam',     'hspend',           0.268,   +1, 0.40, 0.05,  0.60),
    ('aleph',   'vsl',             80.0,     +1, 0.30, 3.0,  60.0),
    ('h_hl',    'homeless',         0.0100,  +1, 0.40, 1e-7,  0.05),
    # b's CEILING IS 1.0, author 12 September: *"i think you need to have a very
    # high b"*.  At theta = 0.25 the model starts with 72 to 86 per cent of
    # households using, and b is the only thing that brings that down: measured
    # in the earlier run, b = 0.25338 gave participation 0.1053, so the old
    # ceiling of 0.30 was roughly where the target sits and b would have arrived
    # PINNED against it with nothing left to give.  A bound a parameter reaches
    # is not a calibration, it is a constraint.
    ('b',       'part',             0.08901, -1, 0.30, 0.005, 1.00),
    ('pi_base', 'sud',              0.0368,  +1, 0.40, 1e-3,  0.99),
    ('u0',      'unemployment',     0.0485,  +1, 0.40, 0.005, 0.30),
    ('u1',      'sud_of_homeless2', 0.217,   -1, 0.20, 0.0486, 0.50),
    # omega_c IS BOUNDED TO [0.01, 0.14], author 12 September: *"try omega_c only
    # between 0.01-0.14"*.  It had run to 0.242 on the negative child gap the
    # corner branch produces -- see the guard above, which now stops that at
    # source -- and 0.14 keeps it in a range the quantitative model's 0.09 sits
    # inside.  The floor of 0.01 keeps it strictly positive, so the child
    # counterfactual stays defined.
    # LOWER BOUND 0.001, NOT 0.01, on the author's suggestion of 12 September:
    # *"You can allow omega_c to have a lower bound at 0.001 if that helps"*.
    #
    # It is insurance rather than a fix, and it is not binding today -- omega_c
    # has sat between 0.081 and 0.090 all run.  It matters because a CLAMPED
    # parameter with a LIVE DISTANCE cannot converge, which is ENGINE.md's rule
    # for retiring a bracket read the other way round: the rule keeps proposing
    # a move the clamp keeps refusing, the gap never closes, and the table shows
    # a parameter sitting exactly on a round number with a large gap beside it.
    # Earlier runs did drive omega_c down to 0.0146, within a factor of 1.5 of
    # the old floor, so the clamp was close to binding and nothing was gained by
    # its being where it was.
    ('omega',   'child_gap',        0.1834,  +1, 0.30, 0.001, 1.00),
    # delta_d ON THE CHILD SUD ODDS RATIO OF 2, asked for twice.  Sign standard:
    # a bigger income penalty makes the child poorer, poorer children use more,
    # so the ratio RISES in delta_d.
    # DELTA_D IS PINNED AT 0.24 AND IS NO LONGER A BRACKET.  The author, 12
    # September: *"Maybe set delta d to 0.24 and pin it?"*, *"I think it is
    # creating some problems"*.
    #
    # It was.  Over the 2500-cap run it went 0.36, 0.46, 0.59, 0.72, 0.57, 0.55,
    # 0.56, 0.62, 0.55 -- a factor of two, wandering, and never settling, while
    # its moment is a ratio of two conditional disorder rates that is noisy in
    # its own right.  Worse, it is the SAME ECONOMICS as the income gradient:
    # the child odds ratio exceeds one only when poorer people use more, which
    # is what r_use measures, so delta_d and kappa were pulling on one margin
    # from two directions.  Retiring it removes one of the two.
    #
    # ENGINE.md's rule for turning a bracket off is to zero its DISTANCE as
    # well, because a zero adjuster with a live distance cannot converge.  Here
    # the spec IS the distance -- worst, median and the count inside ten are all
    # built from SPEC in table() -- so removing the row retires the term too,
    # and nothing is left scoring a parameter that cannot move.
    #
    # The odds ratio is still COMPUTED and still REPORTED, on the ODDS line
    # beside the homelessness one, because it is the number the pin has to be
    # judged by.  It is just no longer targeted.
    # kappa IS FREED AGAIN, on users' income.  Author, 12 September: *"maybe then
    # you have to pick kappa as well to push the income down"*, *"maybe 3
    # multiples is not enough"*.  It was SET at SMR 3 earlier today, which made
    # the gradient an OUTPUT -- and the output came out wrong: r_use 1.02 at the
    # start and 2.66 by iteration 45, against 0.74 in the data.
    #
    # SIGN IS NEGATIVE: more mortality makes users poorer, so r_use FALLS in kap
    # and kap must RISE when r_use is above target.
    #
    # CEILING IS SMR 15.6.  kap = 1 - phi0^(smr-1), so 0.75 is smr 15.6 and 0.05
    # is smr 1.54.  The table prints the implied smr beside kap, which is the
    # number to judge -- the author's question is exactly whether 3 is enough.
    ('kap',     'r_use',            0.74,    -1, 0.30, 0.05,  0.75),
    # THETA IS FREED AGAIN, at 0.1 per cent a pass.  Author, 12 September: *"now
    # that you update parameters slowly, you can add theta, and calibrate it too,
    # and allow it to move at most 0.1% between iterations"*.
    #
    # IT FAILED THE FIRST TIME AT 5 PER CENT: the rule drove it 0.16 -> 0.199
    # while the drug spending share stayed pinned at 0.0007, the corner value,
    # and the worst gap swung 449, 46, 55, 207, 45, 38, 188, 162 with no trend.
    # The diagnosis then was that theta and b both act on one margin.  That is
    # still true, but two things have changed since: the branch guard now refuses
    # any step that leaves the interior branch, and the global step is 0.5 per
    # cent rather than 5.  Both of those attack exactly the failure that was
    # observed, so it is worth another go -- at a tenth the speed of everything
    # else, since it is the parameter that moved the model between branches.
    ('th',      'dshare',           0.14098, +1, 0.30, 0.05,  0.45),
    # THETA IS NOT CALIBRATED.  It was freed on the author's instruction when
    # the eight-parameter run left the drug spending share at 0.052 against
    # 0.141 -- and freeing it FAILED, which is worth recording because the
    # reasoning for freeing it was sound.
    #
    # With theta free the rule drove it 0.16 -> 0.199 while the share stayed
    # pinned at 0.0007, the CORNER value: every user sitting on the smallest
    # positive point of the v-grid, buying essentially nothing.  theta cannot
    # lift it there, because on that branch the drug's marginal value is below
    # the threshold at any theta in range.  The worst gap swung 449, 46, 55,
    # 207, 45, 38, 188, 162 per cent with no trend over 110 iterations, against
    # a median of 0.1 per cent for the eight-parameter run.
    #
    # THE CAUSE IS THAT THETA AND b BOTH ACT ON ONE MARGIN.  Both decide how
    # much a household uses; giving the rule two instruments for it is what put
    # the model on the corner branch and kept it there.  Author's resolution,
    # 12 September: *"can you fix theta to 0.25 and try to calibrate the rest?"*
]

# 0.5 PER CENT A PASS, author 12 September over four messages: *"i think maybe
# you are updating parameters too fast"*, *"maybe they need to be updated only
# 0.1% at most"*, *"you can try 1% updates, or 0.5% updates"*, *"5% is too much"*.
#
# THE ARITHMETIC THAT PICKED 0.5.  b travels from 0.028 to about 0.25, a factor
# of nine: roughly 45 iterations at 5 per cent, 440 at 0.5, 2,200 at 0.1 -- four
# minutes, a quarter of an hour, three hours.  0.5 buys most of the stability at
# a fifteenth of the cost.
#
# WHY 5 WAS TOO MUCH, diagnosed correctly by the author: b swung 0.087 -> 0.168
# -> 0.039 -> 0.101 on consecutive passes, and every fall into the corner branch
# followed a large step.
MAX_REL_STEP = 0.005

# omega_c GETS HALF AGAIN, author: *"maybe omega_c should be even slower? maybe
# 0.05%?"*.  It is the parameter that misbehaved most -- it ran to every ceiling
# it was given, 0.14, 0.25, 0.305 -- and the only one whose moment costs a
# SECOND SOLVE, so its gap is the noisiest of the nine.  A slower step on the
# noisiest signal is the right asymmetry, and it is the same device the Fortran
# uses for theta and omega_c: one parameter gets its own rate.
# h_hl ALSO GETS A FASTER STEP.  It is the parameter with the furthest to travel
# in relative terms and the one whose moment is least coupled to the others, so
# it can afford to move faster than the block that fights over the drug margin.
# KAPPA AT 0.1 PER CENT, on the author's instruction of 12 September.  It had
# NO entry here, so it ran at the global 0.5 -- five times theta's rate and
# twice omega_c's -- for no reason beyond having been overlooked when those two
# were slowed.  Measured before the change, its mean net move was 0.043 per cent
# an iteration, already inside the new cap, because the sign-flip ratchet keeps
# halving its adjuster toward the floor while r_use alternates.  So this binds
# only on the occasional large step and is not expected to stop kappa's drift:
# the correlation over 28 interior-branch tables puts kap NINTH of eleven on
# r_use and with the WRONG SIGN, +0.108 where the mechanism says negative, with
# pi_base at -0.726 and b at +0.566.  What it does buy is a readable table --
# r_use has been swinging plus or minus 32 points reading to reading.
# b AND pi_base TO 0.1 PER CENT, the last two substantive parameters still
# running at the global 0.5.  Every parameter the author has asked to be slowed
# is at 0.1 to 0.25, and these two were simply never named.
#
# THEY ARE THE PAIR YOU WOULD EXPECT TO RING.  b is bracketed on participation
# and pi_base on the disorder rate, but BOTH move BOTH -- either can deliver a
# given SUD rate -- so they can trade a large amount of parameter space against
# each other while their own moments still look reasonable.  Measured over the
# 50000 run, peak-to-peak as a share of the mean:
#
#                iters ~2650-3000   iters ~3050-3400
#     b                 21.6%             39.4%
#     pi_base           34.1%             50.2%
#     omega             22.7%             33.1%
#     th                 5.0%             10.1%
#
# Widening, not damping, and at iteration 3500 the swing carried participation
# to -52.3 per cent, the worst since iteration 200, with b at 0.0669 against
# 0.0942 one block earlier.
#
# theta is the evidence that slowing works: it went from +50 per cent and
# swinging to +5.4 per cent once it was capped at 0.1 and given the iterations.
PER_PARAM_STEP = {'omega': 0.0025, 'th': 0.001, 'h_hl': 0.02, 'kap': 0.001,
                  'b': 0.001, 'pi_base': 0.001}
DAMP = 0.5                   # halve the adjuster when the gap flips sign
GROW = 1.2                   # grow it back while the sign holds
ADJ_FLOOR = 1e-3
CHILD_GAP_FLOOR = 0.1        # of the participation target, as the Fortran uses


_SLOW_EVERY = 5      # iterations between the expensive child evaluations
_slow_cache = {}


def moments(par, it=0):
    """Every moment the spec needs, including the two that are not in aggregates."""
    m = dict(stats(par))
    # pi_eu's moment.  Employment is an i.i.d. draw, so the realised rate is u0
    # among the clean and u1 among those with the disorder.  Exact, no extra solve.
    m['unemployment'] = (1.0 - m['sud']) * par.u0 + m['sud'] * par.u1
    # delta_d's moment, and the homelessness odds ratio the author asked to have
    # REPORTED beside it.  Both run the child through the model as an adult at
    # its inherited income, so neither costs a new solve.

    # omega_c's moment: use with the child term OFF against use with it on.  This
    # is the second solve, and it is what the Fortran spends a third of a loop on.
    # HELD when either population is too small for the ratio to mean anything --
    # the same guard, and the same reason: at a using mass near zero the ratio is
    # a statement about the denominator, not about internalisation.
    # THE GUARD IS ON THE DRUG SHARE, NOT ON PARTICIPATION.  It was on
    # participation alone and that was the wrong quantity: participation counts
    # anyone with v > 0, including the CORNER branch where a "user" buys 0.07 per
    # cent of income.  There the child gap goes NEGATIVE -- use LOWER with the
    # child term off, which is backwards, since the term deters use -- and a
    # negative gap reads as "far below target", so the rule pushes omega_c UP.
    # Measured, iterations 165 to 185 of the theta = 0.25 run:
    #
    #   iter   omega  child_gap  drug share   part
    #    165  0.18053    0.1549      0.2355  0.1618   interior, gap sensible
    #    175  0.14838   -0.0088      0.0007  0.0596   corner, gap negative
    #    185  0.24170   -0.0329      0.0007  0.0637   omega climbing on noise
    #
    # That is the whole of why omega_c reached 0.24 against the quantitative
    # model's 0.09.  The Fortran's own guard has the right idea -- "one of the
    # two is too small for the gap to mean anything" -- this one just measured
    # the wrong thing.  0.02 sits an order of magnitude above the corner's 0.0007
    # and an order below any interior value.
    # THE THREE EXPENSIVE QUANTITIES ARE REFRESHED EVERY FIFTH ITERATION.
    # Timed on this grid: stats() 1.03 s, the omega_c counterfactual another
    # 1.03 s because it is a SECOND FULL SOLVE, and the two odds ratios 0.71 s
    # between them.  That put an iteration at about 3.8 seconds where the model
    # solve alone is 1.0.
    #
    # They can be stale because they MOVE SLOWLY: omega_c steps at 0.25 per cent
    # a pass and delta_d at 0.5, so their moments cannot change materially in
    # five iterations.  The cheap moments -- participation, the disorder rate,
    # homelessness, the housing share -- are recomputed every single iteration
    # as before, and those are the ones that move fast.
    fresh = (it % _SLOW_EVERY == 0) or ('child_gap' not in _slow_cache)
    if fresh:
        if par.omega > 0.0 and m['part'] > CHILD_GAP_FLOOR * 0.08901 \
                and m['dshare'] > 0.02:
            cf = stats(with_(par, omega=0.0))
            # THE COUNTERFACTUAL HAS TO BE ON THE SAME BRANCH AS THE BASELINE.
            # Guarding the baseline's drug share alone was half a guard.  At
            # iteration 200 the baseline had drug share 0.1028 and users at 0.278
            # of mean income, while the omega = 0 counterfactual had 0.2177 and
            # 1.298 -- users flipped from poor to RICH.  The reported child gap
            # of 1.4984 against a target of 0.1834 was not omega_c's marginal
            # effect on use; it was the difference between two equilibria.
            #
            # A factor of two in the drug spending share is far more than a
            # weight of 0.11 can do at the margin, so it is the branch test.
            same = 0.5 < cf['dshare'] / max(m['dshare'], 1e-12) < 2.0
            _slow_cache['child_gap'] = (cf['part'] / m['part'] - 1.0
                                        if same and m['part'] > 0 else None)
        else:
            _slow_cache['child_gap'] = None
        _slow_cache['child_sud_or'] = child_sud_odds_ratio(par, C.YG, C.W)
        _slow_cache['child_hl_or'] = child_homeless_odds_ratio(par, C.YG, C.W)
    m['child_gap'] = _slow_cache['child_gap']
    m['child_sud_or'] = _slow_cache['child_sud_or']
    m['child_hl_or'] = _slow_cache['child_hl_or']

    # IN THE CORNER, dshare AND r_use ARE ARTEFACTS AND ARE HELD.
    #
    # This is a hold on a MEASUREMENT, not a guard on a step.  The branch guard
    # that was removed today blocked the whole vector from moving and froze the
    # search; this blocks nothing.  Eight brackets step exactly as before.  Two
    # decline to step on a reading that has been measured to carry no
    # information, the same way child_gap already declines.
    #
    # THE EVIDENCE.  drug_grid_floor_test.py sweeps the grid's smallest positive
    # point over three orders of magnitude and gets dshare / v_lo = 1.000 at
    # every one: in the corner every user sits exactly on the floor, so the drug
    # share is a property of the grid.  Move the floor and the "moment" moves
    # with it one for one.  r_use sits at 0.142 to 0.147 across every corner
    # table on record regardless of what kappa is doing.
    #
    # WHAT IT COSTS TO LEAVE THEM IN.  Iteration 1300 of the 50000 run: median
    # 0.6 per cent, eight of ten inside ten, the child gap at -0.2 and the
    # disorder rate at -0.1.  Iteration 1400, one block later and in the corner:
    # theta walked 0.20847 to 0.20217 on a constant -100 per cent signal and
    # kappa's implied SMR fell 2.77 to 2.66 on a constant -80 per cent one, the
    # largest single move it made all day.  The corner does not merely waste
    # iterations, it undoes converged ones.
    #
    # The raw values are kept for the OUTPUT line, because the drug share is how
    # the branch is READ even when it cannot be targeted.
    m['dshare_raw'], m['r_use_raw'] = m['dshare'], m['r_use']
    if m['dshare'] <= CORNER:
        m['dshare'] = None
        m['r_use'] = None
    return m


def step(par, m, state):
    """
    One pass of the author's rule over every parameter at once.

    WITH THE SIGN-FLIP RATCHET, which the first version left out and which is
    half the method.  Without it b swung 0.087 -> 0.168 -> 0.039 -> 0.101 and the
    child gap 0.894 -> 0.120 -> 1.125 across ten passes: the step overshoots, the
    gap changes sign, and the next step overshoots back.  The Fortran damps
    exactly this in damp_on_flip -- halve the adjuster when the gap flips, grow
    it back while the sign holds -- and every oscillating parameter here is one
    the Fortran already damps.
    """
    kw, moved = {}, []
    for name, mom, tgt, sgn, adj0, lo, hi in SPEC:
        v = m.get(mom)
        if v is None:                      # moment held this pass
            continue
        old = getattr(par, name)
        rel = (v - tgt) / tgt              # relative gap, so one adjuster fits all scales
        prev = state.get(name)
        adj = state.setdefault(name + '_adj', adj0)
        if prev is not None:
            adj = max(adj * DAMP, ADJ_FLOOR) if prev * rel < 0 else min(adj * GROW, adj0)
            state[name + '_adj'] = adj
        state[name] = rel
        new = old * (1.0 - sgn * adj * rel)
        room = PER_PARAM_STEP.get(name, MAX_REL_STEP) * abs(old)
        new = max(min(new, old + room), old - room)
        new = max(min(new, hi), lo)
        kw[name] = new
        moved.append((name, old, new, 100 * rel))
    return with_(par, **kw), moved


CORNER = 0.02   # drug spending share below this is the corner branch


def step_on_branch(par, m, state):
    """
    One step of the author's rule, BACKED OFF IF IT LEAVES THE INTERIOR BRANCH.

    THE CORNER IS WHAT HAS BEEN STOPPING THIS MODEL CALIBRATING.  Every run so
    far has walked into it: the drug spending share collapses from ~0.20 to
    0.0007, every "user" sits on the smallest positive point of the v-grid, the
    child gap turns to noise, and b then falls chasing participation from the
    wrong branch.  The best run reached participation 0.0830 against 0.0890 and
    a child gap of 0.1864 against 0.1834 at iteration 50 -- essentially hit --
    and was in the corner ten iterations later with b dragged from 0.268 to
    0.065.

    The rule itself is unchanged.  What is added is a line search on the STEP
    LENGTH: take the full step, and if the model has left the interior branch,
    halve the step and try again.  Four halvings, then accept whatever the
    smallest step gives rather than stall.  It costs at most four extra solves
    on the iterations that would have fallen in, and nothing at all on the rest.

    This does not force a result.  If the interior branch genuinely does not
    contain the targets the search still fails -- it just fails without the
    corner's meaningless numbers mixed into the record.
    """
    full, _ = step(par, m, state)
    if m.get('dshare', 0.0) <= CORNER:
        return full          # already in the corner: let the rule climb out
    # THE SKIP WAS THE BUG, AND ITS PREMISE WAS MEASURED FALSE.
    #
    # It read: "a 0.5 per cent step cannot take the drug share from 0.20 to the
    # corner's 0.0007, so the verification solve is only worth its second when
    # the share is within striking distance", and skipped the check above
    # 5 * CORNER = 0.10.  That premise assumes the drug share moves CONTINUOUSLY
    # in the parameters.  It does not: the two branches are separated by a jump,
    # and the model steps across it in one pass from the far side of the skip.
    #
    # MEASURED at the iteration 1300 vector, sweeping omega_c alone with every
    # other parameter at its calibrated value:
    #
    #     omega      dshare      child gap    cf/base dshare
    #     0.01463    0.0007        0.4174        306.4        corner
    #     0.00500    0.2105        0.0551          1.03       interior
    #     0.00100    0.2135        0.0160          1.01       interior
    #     0.00010    0.2158        0.0015          1.00       interior
    #
    # So the branch boundary in omega_c sits between 0.005 and 0.0146, and the
    # share on either side of it is 0.21 or 0.0007 with nothing in between.  A
    # step that begins at 0.21 -- comfortably above the skip -- lands in the
    # corner, and the check that would have caught it was skipped precisely
    # because the share was healthy.
    #
    # WHAT IT COST: a limit cycle.  Every other printed table from iteration 450
    # to 1300 reads dshare 0.0007, worst 99.5 per cent, median about 15, and the
    # ones between read dshare 0.21 with the worst gap falling 449, 317, 286,
    # 167, 248, 109, 110, 54.6, 54.0, 48.0.  The interior branch was converging
    # the whole time and half the record is the corner.
    #
    # The check now runs on every step.  It costs a second an iteration, which
    # is what the skip was buying, and the second is worth it.
    for _ in range(4):
        if stats(full)['dshare'] > CORNER:
            return full
        # halve every parameter's move back toward where we are
        full = with_(par, **{n: 0.5 * (getattr(par, n) + getattr(full, n))
                             for n, _, _, _, _, _, _ in SPEC})
    # A SIXTEENTH OF THE STEP STILL LEAVES THE BRANCH: TAKE NONE OF IT, AND
    # SHRINK THE ADJUSTERS SO THE NEXT PASS PROPOSES A SMALLER ONE.
    #
    # The refusal used to "accept whatever the smallest step gives rather than
    # stall", which is how the corner was entered even on iterations where the
    # check ran.  Refusing is right.  Refusing ALONE is a deterministic freeze,
    # and it was one: iterations 200, 250 and 300 of the 50000 run came out
    # byte-identical, every parameter and every moment, for a hundred passes.
    #
    # The reasoning that shipped it said the search could not stall "because the
    # step is recomputed next pass from a fresh solve and the sign-flip ratchet
    # shrinks the adjusters meanwhile".  That is wrong, and wrong in a way worth
    # keeping: if the parameters do not move, the moments do not move, the gaps
    # do not change, the sign never flips, so the ratchet NEVER FIRES and the
    # identical step is proposed and refused forever.  The ratchet is driven by
    # the gap changing sign, and a frozen model is precisely one whose gaps have
    # stopped changing.  A guard that depends on the system evolving cannot be
    # relied on to rescue a state in which the system has stopped evolving.
    #
    # So the refusal damps the adjusters itself rather than waiting for a
    # mechanism that cannot fire.  Each refused pass halves every adjuster, so
    # the proposed step shrinks geometrically and either finds a size that stays
    # on the branch or converges onto the boundary -- which is a result, and the
    # gap table then says so in the open instead of alternating between two
    # economies every fifty iterations.
    for name, *_ in SPEC:
        k = name + '_adj'
        if k in state:
            state[k] = max(state[k] * DAMP, ADJ_FLOOR)
    return par


def table(par, m, it):
    print(f'\n  ITERATION {it}')
    print(f'  {"param":9}{"value":>11}  {"moment":20}{"model":>10}{"target":>9}{"gap %":>8}')
    print('  ' + '-' * 70)
    gs = []
    for name, mom, tgt, *_ in SPEC:
        v = m.get(mom)
        if v is None:
            print(f'  {name:9}{getattr(par,name):11.5f}  {mom:20}{"HELD":>10}{tgt:9.4f}{"--":>8}')
            continue
        g = 100 * (v - tgt) / tgt
        gs.append(abs(g))
        tag = ('  smr %.2f' % (1.0 + math.log(1.0 - par.kap) / math.log(par.phi0))
               ) if name == 'kap' else ''
        print(f'  {name:9}{getattr(par,name):11.5f}  {mom:20}{v:10.4f}{tgt:9.4f}{g:8.1f}{tag}')
    print('  ' + '-' * 70)
    print(f'  worst {max(gs):.1f} %   median {sorted(gs)[len(gs)//2]:.1f} %   '
          f'{sum(1 for g in gs if g < 10)} of {len(gs)} inside ten')
    print(f'  OUTPUT  users income/mean {m["r_use_raw"]:.4f}  drug share {m["dshare_raw"]:.4f}'
          f'  networth {m["networth"]:.3f}  SUD of homeless {m["sud_of_homeless2"]:.4f}'
          f'  burden50 {m["burden50"]:.4f}')
    # THE HOMELESSNESS ODDS RATIO IS REPORTED AND NEVER TARGETED, author:
    # *"i also want a report of the homelessness odds ratio"* and *"we are not
    # calibrating delta_h...that one is dropped"*.  ENGINE.md's phase 3 agrees:
    # anywhere in 1.8 to 2.4 is fine, only below 1.8 is delta_h reopened.
    # BOTH ODDS RATIOS ARE REPORTED AND NEITHER IS TARGETED NOW.  delta_h was
    # dropped by the author on 12 September and delta_d pinned at 0.24 the same
    # day, so this line is how the pin is judged: if the SUD ratio sits far from
    # 2 at delta_d = 0.24, that is the thing to look at, and it will be visible
    # rather than buried in a bracket that was quietly chasing it.
    print(f'  ODDS    child homeless {m["child_hl_or"]:.3f}'
          f'   child SUD {m["child_sud_or"]:.3f}  at delta_d {par.delta_d:.2f}'
          f'   (both reported only)')
    return max(gs)


if __name__ == '__main__':
    from recalibrate import FIXED, START
    # BETA IS EXOGENOUS AT 1, author 12 September: *"ok, i think we can just set
    # beta=1"*, *"exogenous, not calibration"*, *"beta=1.47 is not believable"*.
    # They are right: calibrating beta on a net worth to income ratio of 3 drove
    # it to 1.477 at the old positive interest rate and to 1.62 once interest was
    # set to zero -- a household that values a period thirty years away MORE than
    # the present.  networth leaves the target set with it and is reported.
    #
    # AND THE DIRECTION CONFIRMS WHAT WAS FLAGGED: removing a positive return
    # made saving less attractive, so beta rose rather than fell.
    par = with_(P(), **{k: v for k, v in FIXED.items() if k != 'kap'},
                **{**START, "th": 0.25, "beta": 1.0, "kap": 1.0 - 0.91 ** 2,
                   # PINNED, not a starting value: delta_d is out of SPEC, so
                   # nothing steps it and it holds here for the whole run.
                   "delta_d": 0.24,
                   # STARTING VALUES MATTER WHEN THE STEP IS RELATIVE.  The
                   # author, 12 September: *"this is why the model cannot
                   # converge"*.  h_hl started at 1e-4 and lands near 1e-2 -- a
                   # factor of a HUNDRED, which at 0.5 per cent a pass is about
                   # 920 iterations before homelessness can respond at all.
                   # Measured, it was doing exactly that: h_hl climbing 0.00010,
                   # 0.00016, 0.00027, 0.00045 over 300 iterations while the
                   # homelessness gap sat at -72 per cent throughout.  Not
                   # stuck -- crawling.
                   #
                   # b had the same problem more mildly, starting at 0.028 and
                   # landing near 0.076, a factor of three.
                   #
                   # Both now start where earlier runs found them.  This is not
                   # putting a thumb on the answer: any start on the interior
                   # branch reaches the same place, it just reaches it in this
                   # run rather than the next one.
                   "h_hl": 0.005, "b": 0.07})
    smr = 1 + math.log(1 - par.kap) / math.log(par.phi0)
    print(f"THE AUTHOR'S METHOD, sigma = 2, kappa SET at SMR {smr:.2f}")
    state = {}
    # A FROZEN RUN MUST ANNOUNCE ITSELF.  The branch guard's refusal path can
    # return the vector unchanged, and when it fired every pass the run printed
    # iterations 200, 250 and 300 byte-identical -- every parameter, every
    # moment -- for a hundred passes.  Nothing in the output said so: a table
    # that has not moved looks exactly like a table that is converging slowly,
    # and it was caught only by someone noticing two tables were the same.
    # That is not a thing to leave to eyesight at fifty-iteration intervals.
    frozen = 0
    prev_vec = None
    for it in range(50000):
        m = moments(par, it)
        if it % 50 == 0 or it == 49999:
            w = table(par, m, it)
            if w < 2.0:
                print('\n  every gap inside two per cent, stopping')
                break
        # THE BRANCH GUARD IS OFF, on the author's instruction of 12 September:
        # *"yes, remove the guard and use 4 workers"*.
        #
        # It was built this afternoon to keep the search off the corner branch,
        # and by the end of the day it was the thing stopping the search.  The
        # log says so plainly: the corner never appeared in this run -- the drug
        # share sat between 0.17 and 0.23 throughout -- while FROZEN fired at 25
        # and then 50 consecutive passes with the vector refusing to move,
        # because the guard rejected every proposed step and the damping shrank
        # the adjusters toward the floor.  A guard against a hazard that is not
        # occurring, which blocks the search that is.
        #
        # The moments were checked before the guard was blamed: check_moments.py
        # puts aggregates() within 1.6 per cent of a brute-force sum over 960
        # incomes with no bisection at all, converged.  So the machinery below
        # the guard is sound and it was the guard on top that was the problem.
        #
        # step() is the author's rule with nothing wrapped round it, which is
        # how this ran before the guard existed.  The freeze detector stays --
        # it costs nothing and it is what caught the guard in the first place.
        par, _ = step(par, m, state)
        vec = tuple(round(getattr(par, n), 12) for n, *_ in SPEC)
        frozen = frozen + 1 if vec == prev_vec else 0
        prev_vec = vec
        if frozen and frozen % 25 == 0:
            print(f'  FROZEN: the parameter vector has not moved in {frozen} '
                  f'passes.  The branch guard is refusing every step, so every '
                  f'proposed move leaves the interior branch.  Adjusters are '
                  f'being damped each refusal; if this does not clear, the '
                  f'search is against a boundary and the vector is the answer.')
        if frozen >= 500:
            print(f'\n  STOPPING: frozen for {frozen} passes at iteration {it}.')
            table(par, moments(par), f'{it} frozen')
            break
    print('\nFINAL')
    table(par, moments(par), 'final')
