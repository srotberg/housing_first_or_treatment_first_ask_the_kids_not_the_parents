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
parameters that range from 1e-4 (h1) to 15 (aleph).  It is the same rule with
the scale factored out.
"""
import math
import numpy as np

import calibrate as C
from calibrate import stats
from stylized import solve_child_damage, P, with_, child_sud_odds_ratio, child_homeless_odds_ratio

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
    # GAMMA IS CALIBRATED AGAIN, ON THE HOUSING SHARE.  The author, 13
    # September: *"ok, then maybe you need to rental sizes...one is 0.1 and one
    # 0.4"*, *"and choose gamma to match 26.8% spending on housing"*.
    #
    # It was SET at 0.268 earlier today, for the good reason that with a single
    # fixed-size rental a household cannot choose how much housing to buy, so
    # the expenditure share carried no information about the preference weight
    # and gam ran to its bound.  With two sizes the household chooses BETWEEN
    # them, the share responds to the weight again, and gam is identified.
    # aleph WAS DROPPED FROM THIS LIST BY A BAD EDIT AND IS RESTORED.  A
    # replacement that ran from the gamma comment to the h3 line swallowed the
    # aleph entry that sat between them, so the two-rental run calibrated NINE
    # parameters and left the value of life untargeted for its whole length.  It
    # showed up as the vsl column vanishing from the gap table, which is exactly
    # what a reporter that silently drops rows would have hidden -- and this one
    # did not hide it, it was simply not read.
    ('aleph',   'vsl',             80.0,     +1, 0.30, 3.0,  60.0),
    ('gam',     'hspend',           0.268,   +1, 0.40, 0.05,  0.60),
    # h2 = 0.4 AND h1_rental = 0.1 ARE SET, on the author's instruction.  Neither
    # carries a moment: gam has the housing share and h1 has homelessness.
    # y_floor IS SET, NOT BRACKETED.  It was put on the priced-out share when
    # there was one rental and that share was the binding margin.  With a 0.1
    # unit available the floor already covers the cheapest rent, so the priced-
    # out share is near zero at any floor and has nothing left to identify.  It
    # goes back to its own job, clearing the negative value of life, and is
    # reported on every table.
    # AND h1 MATCHES HOMELESSNESS ON WHAT IS LEFT.  The author, 13 September:
    # *"you need to put the lowest income such that it cannot afford h2, but the
    # rest can, and then choose h1 to match the homelessness rate"*.
    #
    # That is the separation the last two runs lacked.  Once the floor has cut
    # the priced-out group to half a per cent, everyone else CAN pay the rent,
    # so whoever is still on the street is there by CHOICE -- and choice is the
    # one margin street quality governs.  h1 was powerless before only because
    # it was being asked to move a population that had no choice to make.
    #
    # THE LOWER BOUND IS 0.001 AND NOT 1e-7.  The author: *"raise h1 to be above
    # 0"*, *"because when it is 0 you cannot adjust it"*.  They are right twice
    # over: a bracket sitting on a bound has stopped being a parameter, and at
    # exactly zero the flow utility raises 0 to a negative power and the solve
    # dies -- which is how the last scan crashed.
    ('h1',    'homeless',         0.0100,  +1, 0.40, 0.001, 0.05),
    # b's CEILING IS 1.0, author 12 September: *"i think you need to have a very
    # high b"*.  At theta = 0.25 the model starts with 72 to 86 per cent of
    # households using, and b is the only thing that brings that down: measured
    # in the earlier run, b = 0.25338 gave participation 0.1053, so the old
    # ceiling of 0.30 was roughly where the target sits and b would have arrived
    # PINNED against it with nothing left to give.  A bound a parameter reaches
    # is not a calibration, it is a constraint.
    ('b',       'part',             0.08901, -1, 0.30, 0.005, 1.00),
    # pi_base IS NOT CALIBRATED.  IT IS 0.0368/0.089 BY CONSTRUCTION.
    #
    # The author, 13 September: *"shouldnt pi_base just be 0.0368/0.089?"*  Yes.
    # Onset is a FLAT rate on anyone who buys -- stylized.py:872 is
    # `par.pi_base * (v > 0)` and nothing else -- so
    #
    #     sud = part * pi_base     identically
    #
    # and the log confirms it to the printed digits: at iterations 450, 550 and
    # 600 the model's sud/part read 0.3723, 0.3695 and 0.3750 against pi_base of
    # 0.37212, 0.36911 and 0.37501.
    #
    # So with participation at its target of 0.089, the disorder rate of 0.0368
    # pins pi_base at 0.41348 exactly and there is nothing to search for.
    #
    # AND SEARCHING FOR IT WAS DOING HARM, because the identity makes the sud
    # bracket read b's error rather than pi_base's.  Iteration 600: part -7.4
    # per cent and sud -16.0, so pi_base was being pushed down to repair a
    # shortfall b had caused.  Iteration 650: part -10.4 and sud -15.5, the same
    # thing again.  Two brackets pulling on one identity.
    #
    # sud is now a CHECK rather than a target: it is on target whenever
    # participation is, and if it ever is not, the identity above is broken and
    # something else is wrong.  The bracket is retired with its distance retired
    # with it, which is the standing rule.
    # ('pi_base', 'sud',              0.0368,  +1, 0.40, 1e-3,  0.99),
    ('u0',      'unemployment',     0.0485,  +1, 0.40, 0.005, 0.30),
    # THE SIGN IS POSITIVE NOW, AND THE NEGATIVE ONE WAS THE BUG.  The author,
    # 13 September: *"if you raise u1 and push b down, then youll have enough
    # users with sud"*, *"you are measuring it wrong"*, *"because you are not
    # adjusting b"*.
    #
    # THE EARLIER MEASUREMENT HELD b FIXED AND IS WORTHLESS.  Sweeping u1 alone,
    # the SUD share of the homeless falls 0.198 -> 0.121 -- but only because the
    # population SUD rate collapses from 3.70 to 0.16 per cent, so the ratio is
    # being read off an economy with no users left.  That is not the calibration's
    # experiment: b is bracketed on participation and re-fits at every u1, which
    # holds the using population at 8.9 per cent while the disorder gets more
    # costly.  The record's own note that the ratio 'FALLS in u1' rests on the
    # same fixed-b reading.
    #
    # WITH THE NEGATIVE SIGN THE DRIVER DROVE u1 TO ITS LOWER BOUND and parked
    # it: the moment sat 8.3 per cent below target for nine hundred iterations
    # with u1 at 0.04860 against u0 at 0.04850, so the disorder cost no job at
    # all, which cannot be right.  A parameter on its bound is not calibrated.
    ('u1',      'sud_of_homeless2', 0.217,   +1, 0.20, 0.0486, 0.50),
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
    # THE UPPER BOUND IS 0.0125 AND IT IS MEASURED, and it is a BOUND rather than
    # a pin so the bracket stays live and child_gap keeps reporting its gap.
    #
    # child_gap is NOT monotone in omega and it is not single-peaked either.  It
    # has a local maximum near 0.0088 at 0.1230, a cliff, a second maximum near
    # 0.0123 at 0.1315, and beyond that the omega = 0 counterfactual crosses onto
    # the other drug branch and the moment cannot be measured at all.  Swept at
    # nv = 560:
    #
    #   omega    0.0040  0.0060  0.0080  0.0088  0.0100  0.0123  0.0140  0.0800
    #   gap      0.0458  0.0737  0.1073  0.1230  0.0677  0.1315   HELD    HELD
    #   target                           0.1834
    #
    # The target is above every one of those, so the bracket pushes omega up for
    # ever.  Unbounded it did exactly that on 13 September: omega crossed the
    # cliff at about iteration 1300 and eight of the next nineteen sampled passes
    # were on the corner branch, with participation and the disorder rate being
    # adjusted on readings from an economy with no drug use.  By iteration 2500
    # participation read -42.6 per cent.
    #
    # AND THE CEILING IS NOT A PROPERTY OF THIS VECTOR.  Every thirty per cent
    # perturbation of b, th or kap either drops the maximum by an order of
    # magnitude or makes the moment unmeasurable, and xi = 1.70 -- which nearly
    # doubles the child's weight (xi-1) and so scales the whole child channel up
    # -- gives 0.0812, LOWER than the calibrated point's 0.1315.
    #
    # So omega is SET at the maximum of its own moment, not identified by it, and
    # the table will go on showing child_gap about -28 per cent.  That is the
    # honest reading and it is why this is a bound and not a retirement: hiding
    # the gap would be worse than showing one that cannot close.
    # THE BOUND IS 0.0088, BELOW THE CLIFF, NOT 0.0125 ABOVE IT.  The first
    # attempt bounded omega at 0.0125 because that is where its moment reaches
    # its largest measurable value, 0.1315.  That was the wrong side.  The cliff
    # is at about 0.0089: below it the model is on the INTERIOR drug branch,
    # above it a block of households flips and the economy sits on the corner,
    # where dshare, r_use and child_gap are all artefacts and three brackets go
    # HELD.  Bounded at 0.0125 the run went to the corner and stayed: iterations
    # 500 and 600 both read drug share 0.0000, and the runaway detector froze
    # omega at 0.01042, correctly but on the far side, leaving the other ten
    # brackets nothing to work with.
    #
    # So the bound is the last omega on the interior side.  child_gap will read
    # about 0.123 against 0.1834, a gap near -33 per cent, permanently.  That is
    # the honest number: every value of this moment that reaches the target is a
    # comparison between two DIFFERENT economies, the baseline on the corner and
    # the counterfactual on the interior branch, which is the artefact the branch
    # guard exists to reject and which once read 1.4984 against the same target.
    # THE BOUND IS BACK OFF.  It was put at 0.0125 and then 0.0088 to keep omega
    # on the interior side of its cliff, and the justification was the branch
    # test above, which does not survive.  Crossing the cliff is a real response.
    # The step is 0.05 per cent a pass, on the author's instruction of 13
    # September -- *"you just have to move omega_c maybe by 0.05% each
    # iteration"* -- and it was already there; the bound was what stopped it, not
    # the step.  What protects the run now is the right thing: the moment is held
    # only when the BASELINE is degenerate, and the corner escape then steps th
    # up until the baseline is a drug economy again.
    # THE LOWER BOUND COMES DOWN TO 1e-6, on the author's instruction of 13
    # September: *"lower the bound on omega_c and let it go further down"*.  At
    # 0.001 it was a bound the run was heading for rather than a range: the
    # child gap read +788 per cent with omega already at 0.0076 and falling,
    # because Delta(y) is of order 5 and participation is a threshold, so even a
    # tiny weight removes a lot of marginal users.  A parameter sitting on its
    # bound has stopped being calibrated.
    ('omega',   'child_gap',        0.1834,  +1, 0.30, 1e-6,  1.00),
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
    # UNPINNED AGAIN, 12 September, and calibrated at the SLOWEST rate in the
    # model.  The author: *"But I also want you to calibrate delta d now to
    # match the odds ratio of 2, but update it very very slowly..."*.
    #
    # It was pinned at 0.24 a few hours ago because it wandered by a factor of
    # two -- 0.36, 0.46, 0.59, 0.72, 0.57, 0.55, 0.56, 0.62, 0.55 -- against a
    # noisy moment, while fighting kappa over the same margin.  Two things have
    # changed since: kappa, b and pi_base are all at 0.1 per cent a pass now
    # rather than 0.5, so the margin is no longer being yanked from the other
    # side; and 0.24 leaves the odds ratio at 1.26 to 1.42 against a target of
    # 2, so the pin was not delivering the moment either.
    #
    # 0.05 PER CENT A PASS, half the slowest of the others, which is what "very
    # very slowly" has to mean if it is to mean anything beyond what th, kap, b
    # and pi_base already do.  From 0.24 to the 0.55-0.6 region earlier runs
    # found is about 1700 passes; the budget is 50000.
    #
    # SIGN IS POSITIVE: a bigger income penalty makes the child poorer, poorer
    # children use more, so the odds ratio RISES in delta_d.
    # THE UPPER BOUND IS 1.0 AND IT IS IN LOG INCOME, NOT PER CENT.  The author,
    # 13 September: *"Delta d cannot be over 100%!!"*, seeing delta_d read 1.45
    # in the tables.  The parameter is a shift in LOG income --
    # log y_child = rho*log y_p + (1-rho)*log ybar - delta_d*1{parent SUD} --
    # so the value is not a percentage and 1.45 is a cut of 76.5 per cent, not
    # 145.  A cut of 100 per cent is delta_d = infinity, which is why a bound of
    # 2.0 never caught anything.  The bound is now 1.0, a cut of 63.2 per cent,
    # and the table prints the implied percentage beside the value so the unit
    # cannot be misread again.  For scale: the author's own pin of 0.24 is a cut
    # of 21.3 per cent and Nilsson (2017) is 24 per cent, i.e. delta_d = 0.274.
    ('delta_d', 'child_sud_or',      2.0,     +1, 0.30, 0.01,  1.00),
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
# h1 ALSO GETS A FASTER STEP.  It is the parameter with the furthest to travel
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
# SLOWER ON omega, delta_d AND th, on the author's instruction of 13
# September: *"maybe slower updates on omegac, deltad, and theta"*.
# omega 0.25 -> 0.05 per cent a pass, th 0.1 -> 0.03, delta_d 0.05 ->
# 0.02.  These are the three that were not converging from their start:
# omega fell 0.00905 to 0.00163 and delta_d climbed 0.57 to 1.45 over
# nineteen hundred passes, neither settling.
# h1 IS 0.005, WAS 0.02, on the author's instruction of 13 September: *"h1
# should get also 0.5%"* -- the same cap u1 runs at.  At 0.02 it was the fastest
# instrument in the spec, twenty times b's, which is why homelessness snapped to
# target within fifty iterations while every other moment crawled.  A single
# instrument moving that much faster than the rest lands its own moment and then
# keeps re-landing it on top of everyone else's adjustments.
# b IS 0.02 NOW, WAS 0.001, on the author's instruction of 13 September: *"it
# should move very fast"*.  It is the instrument that has to hold participation
# while u1 climbs, and at 0.001 against u1's 0.005 it was five times too slow to
# do it: over three hundred and fifty iterations u1 went 0.0800 -> 0.4584, a
# rise of 473 per cent, while b managed 0.0514 -> 0.0396, a fall of 23, and
# participation drifted from +4 per cent to -32.  Every one of those iterations
# was spent in a thinned-out economy, which is the fixed-b regime the author
# ruled out as a way of measuring this.
# u1 AT 0.1 PER CENT AND b AT 0.25, on the author's instruction of 13 September:
# *"reset u1, update it at 0.1% and update b at 0.25%"*.  b is now two and a
# half times FASTER than u1, which is the ratio the experiment needs: b has to
# hold participation while u1 climbs, so the instrument doing the holding must
# outrun the one doing the pushing.
#
# IT WAS THE OTHER WAY ROUND AND THAT IS WHAT BROKE THE TEST.  u1 ran at 0.5 per
# cent and b at 0.1, five times slower.  Over three hundred and fifty iterations
# u1 rose 473 per cent while b fell 23, and participation drifted from +4 to -32
# per cent -- so every iteration was spent in a thinned-out economy, which is
# the fixed-b regime the author had already ruled out as a way of measuring
# this.  The sweep was reproducing a bad experiment slowly.
PER_PARAM_STEP = {'omega': 0.0005, 'th': 0.0003, 'h1': 0.005, 'kap': 0.001,
                  'u1': 0.001, 'b': 0.0025, 'pi_base': 0.001, 'delta_d': 0.0002}
DAMP = 0.5                   # halve the adjuster when the gap flips sign
GROW = 1.2                   # grow it back while the sign holds
ADJ_FLOOR = 1e-3
CHILD_GAP_FLOOR = 0.1        # of the participation target, as the Fortran uses


_SLOW_EVERY = 5      # iterations between the expensive child evaluations
_slow_cache = {}


def moments(par, it=0):
    """Every moment the spec needs, including the two that are not in aggregates.

    THE CHILD DAMAGE IS SOLVED ONCE, HERE, AND EVERYTHING BELOW USES THE SOLVED
    par.  chdmg is V(1,0) - V(1,1) and it depends on every other parameter, so
    with_() clears it on any change and stylized raises rather than defaulting
    to zero.  stats() solves it for its own use, but the odds ratios and the
    child gap below call period1 DIRECTLY, so they need a par that carries it.
    Solving here rather than in each of them also means one fixed point per
    loop rather than four.
    """
    par = solve_child_damage(par)
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
            # THE TEST IS ON THE BASELINE ALONE.  The author, 13 September:
            # *"i dont understand why moving omegac=0 and keeping everything
            # else constant measures a different economy that is not suitable
            # for comparison?"*  They are right and the old test could not be
            # defended.
            #
            # Setting omega to zero with everything else held IS the comparative
            # static this moment is defined as.  If the economy answers by a
            # block of households flipping onto the other drug branch, that is
            # omega_c's effect -- large and discontinuous, but the model's real
            # answer.  "The response was big" is not a reason to throw the
            # measurement away, and the old test threw away every such case by
            # requiring the two sides to have drug shares within a factor of two
            # of each other.
            #
            # WHAT IS ACTUALLY INVALID is a degenerate BASELINE: when the
            # baseline sits on the corner, its "users" are buying the smallest
            # grid quantity purely to shorten their lives, so baseline
            # participation is not measuring drug use and the ratio has a
            # meaningless denominator.  That is the one case that was ever
            # verified -- at omega 0.05 the baseline drug share was 0.0000 and
            # the raw gap read 0.4436 -- and it is a statement about the
            # baseline, not about the two sides resembling each other.
            #
            # The corner test below already holds child_gap whenever the
            # baseline is on the corner, so this is the same rule stated once.
            ok = m['dshare'] > CORNER and m['part'] > 0
            _slow_cache['child_gap'] = (cf['part'] / m['part'] - 1.0
                                        if ok else None)
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
        # AND THE CHILD GAP GOES WITH THEM.  Its own guard compares the
        # baseline's drug share with the omega = 0 counterfactual's and holds
        # when they are on different branches -- but when BOTH sit on the
        # corner that test passes and the gap is read anyway.  It passed 18 of
        # 33 tables that way in sr_run_231918.log and drove omega from 0.01105
        # to 0.07837, a factor of seven, on the difference between two corner
        # economies.  omega_c's effect on drug use is not defined where nobody
        # is choosing a drug quantity.
        m['child_gap'] = None
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

        # A PARAMETER THAT MOVES ONE WAY WHILE ITS GAP WIDENS IS NOT CONVERGING
        # SLOWLY, IT IS RUNNING AWAY, AND NOTHING USED TO NOTICE.
        #
        # The author, 13 September: *"That should not diverge...."*.  They are
        # right, and the case that produced this is exact.  delta_d's sign in
        # SPEC is +1, which is correct: with no income floor the odds ratio is
        # smooth and monotone in it, 1.13 at 0.10 rising to 3.11 at 1.00, and
        # 0.56972 hits the target of 2.0000 to four decimals.  WITH the floor
        # the same scan runs the other way, 0.837 down to 0.124, so the true
        # sign is -1.  The bracket then pushed delta_d up every pass, the ratio
        # fell, the gap widened, and it pushed harder: 0.57 to 1.45 over
        # nineteen hundred passes with only the bound to stop it, dragging omega
        # and the rest of the vector along.
        #
        # So: count consecutive moves in one direction, and if the gap has not
        # shrunk over a long run of them, the bracket's sign is wrong for the
        # configuration it is in.  Freeze the adjuster and SAY SO on the table.
        # Freezing rather than flipping the sign is deliberate -- a sign that is
        # wrong in one configuration and right in another is a fact about the
        # model that the author has to see, not something for the search to
        # paper over.
        runs = state.setdefault('_runaway', {})
        d = runs.setdefault(name, {'n': 0, 'dir': 0, 'rel0': abs(rel)})
        mv = 1 if new > old else (-1 if new < old else 0)
        if mv != 0 and mv == d['dir']:
            d['n'] += 1
        else:
            d['dir'], d['n'], d['rel0'] = mv, 1, abs(rel)
        # AND THE TRIP IS A SUSPICION, NOT A VERDICT.  MEASURE BEFORE FREEZING.
        #
        # The counter above cannot tell "this parameter's sign is wrong" from
        # "another parameter moved the moment away while this one walked
        # correctly towards it", and it froze delta_d on the second.  Measured
        # at the vector it froze at, with the income floor on, child_sud_or is
        # MONOTONE RISING in delta_d -- 1.04 at 0.10, 1.25 at 0.40, 1.50 at
        # 0.70, 1.67 at 0.8598, 1.96 at 1.00 -- so the sign of +1 was right and
        # the bracket only needed to reach its bound.  It was frozen at 0.8598
        # with a gap of -16.7 per cent, and 1500 further passes changed nothing.
        # What tripped the counter was rel0 being captured at +0.4 per cent, the
        # pass the direction last changed, after which the gap crossed zero and
        # grew the other way as the rest of the vector moved: |rel| >= 0.98*|rel0|
        # is then true for any gap at all.
        #
        # So when the counter trips, probe: move the parameter a VISIBLE step in
        # the direction the bracket wants, re-solve, and see whether the gap
        # shrinks.  One extra solve, once, at the moment of firing.  If it
        # shrinks the sign is right and the run counter resets; if it does not,
        # freeze, and say the freeze was measured.  A parameter pinned at a
        # bound is not running away and is never frozen.
        if d['n'] >= RUNAWAY_PASSES and abs(rel) >= 0.98 * d['rel0']:
            direction = -sgn * (1.0 if rel > 0 else -1.0)
            probe = max(min(old * (1.0 + direction * 0.15), hi), lo)
            if abs(probe - old) <= 1e-12 * max(abs(old), 1.0):
                # At a bound. It cannot run anywhere.
                d['n'] = 0
            else:
                v2 = moments(with_(par, **{name: probe})).get(mom)
                if v2 is None:
                    # The moment is held at the probe, so nothing was measured.
                    d['n'] = 0
                else:
                    rel2 = (v2 - tgt) / tgt
                    if abs(rel2) < abs(rel):
                        print(f'  RUNAWAY SUSPECTED on {name} after {d["n"]} passes '
                              f'({100 * d["rel0"]:+.1f} % to {100 * rel:+.1f} %), '
                              f'and MEASURED CLEAR: moving it to {probe:.5f} takes '
                              f'{mom} to {v2:.4f}, a gap of {100 * rel2:+.1f} %.  '
                              f'The sign is right; the counter is reset and the '
                              f'bracket keeps going.')
                        # rel0 is refreshed too, or the next four hundred passes
                        # trip on the same stale baseline.
                        d['n'], d['rel0'] = 0, abs(rel)
                    else:
                        state[name + '_adj'] = 0.0
                        state.setdefault('_frozen', set()).add(name)
                        print(f'  RUNAWAY {name} has moved '
                              f'{"up" if mv > 0 else "down"} for {d["n"]} passes '
                              f'and its gap has not shrunk '
                              f'({100 * d["rel0"]:+.1f} % to {100 * rel:+.1f} %).  '
                              f'MEASURED: moving it to {probe:.5f} takes {mom} to '
                              f'{v2:.4f}, a gap of {100 * rel2:+.1f} %, which is no '
                              f'better.  Its sign is wrong for this configuration.  '
                              f'Adjuster set to zero; the gap is still reported.')
                        d['n'] = 0

    # THE ESCAPE FROM THE CORNER HAS TO BE EXPLICIT, BECAUSE HOLDING ALONE
    # PARKS THE RUN THERE.  This was learned by breaking it.  At CORNER = 0.02
    # the passes at a drug share of 0.037 to 0.043 were scored as interior and
    # fed about -74 per cent into th and kap.  That was a garbage signal -- and
    # it was ALSO the only thing that ever pulled the model back onto the
    # interior branch, which it did five times in the 12 September run.
    # Raising the threshold to 0.10 removed the noise AND the escape with it:
    # sr_run_231918.log then sat at a drug share of 0.0482, unchanged to four
    # decimals, from iteration 1050 to 1600, with the other eight brackets
    # converging onto an economy whose drug block was dead.
    #
    # So the escape is now a rule rather than a side effect.  th is what moves
    # the model across the branch -- measured, every sweep in the 12 September
    # logs: th 0.2045 gives a drug share of 0.0000 and th 0.2100 gives 0.2181 --
    # so while the drug share is held, th steps UP by its cap and nothing else
    # about the pass changes.  This is not the branch guard the author had
    # removed: that one refused to move the WHOLE vector and froze the search.
    # This moves exactly one parameter, in a direction that is measured, and
    # only while the moment that would otherwise set it cannot be read.
    if m.get('dshare') is None:
        room = PER_PARAM_STEP.get('th', MAX_REL_STEP)
        th_hi = next(r[6] for r in SPEC if r[0] == 'th')   # its own upper bound
        th_old = kw.get('th', par.th)
        kw['th'] = min(th_old * (1.0 + room), th_hi)
        moved.append(('th', th_old, kw['th'], float('nan')))

    return with_(par, **kw), moved


# THE THRESHOLD IS MEASURED, NOT CHOSEN.  It was 0.02, and at 0.02 it
# misclassified four of the sixty-eight tables the 12 September run produced.
# Every drug spending share that run reported, sorted:
#
#   corner    0.0000 (x16)  0.0196 0.0198 0.0199 0.0200 0.0202
#             0.0367 0.0383 0.0397 0.0432
#                    <-- nothing at all between 0.0432 and 0.1381 -->
#   interior  0.1381 0.1409 0.1473 ... 0.2071 0.2147
#
# The two branches were separated by an interval 0.095 wide with nothing in it,
# so any threshold inside it classified all sixty-eight correctly and 0.10 is
# the middle of it.
#
# THE INTERVAL IS SPARSE, NOT EMPTY, and it took fifty passes of the next run to
# show it: iteration 50 of sr_run_231918.log reads a drug share of 0.0546, with
# the income of users at 0.2229, which is the corner branch beyond any doubt.
# So do not read the gap as a property of the model -- it is where the corner
# branch is merely RARE -- and do not narrow the threshold back toward it on the
# strength of a finite sample.  0.10 holds that pass correctly; 0.05 would not
# have.  At 0.02 the four passes at 0.0367 to 0.0432 read as interior
# and fed about -74 per cent into BOTH th and kap -- iteration 3300 is one, and
# iterations 2200 and 2400 are two more.  That is the single largest source of
# the +/- 28 point swing r_use showed over the run, and it is exactly the cost
# the comment in moments() describes: the corner does not merely waste
# iterations, it undoes converged ones.
CORNER = 0.10   # drug spending share below this is the corner branch

# HOW LONG A ONE-WAY RUN HAS TO BE BEFORE IT COUNTS AS A RUNAWAY.  Long enough
# that a genuinely slow bracket is never caught: at the slowest step in
# PER_PARAM_STEP, 0.02 per cent a pass, 400 passes moves a parameter by 8 per
# cent, and any bracket whose gap is closing will have shrunk it measurably over
# that.  delta_d's actual runaway ran for nineteen hundred.
RUNAWAY_PASSES = 400


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
    # THE FLOOR AND WHAT IT HAS LEFT BEHIND, ON EVERY TABLE.  The author asked
    # for the floor to rise until no household has a negative value of life, so
    # the table has to say where the floor is and whether the condition is met
    # -- otherwise the rule is invisible and there is no way to see it working
    # or stalling.
    from negative_value_of_life import negative_value_share
    _nv = negative_value_share(par)
    print(f'  FLOOR   y_floor {par.y_floor:.4f}   negative value of life '
          f'{100 * _nv["share"]:.2f} %   lowest V {_nv["lowest"]:.2f}')
    # THE HOMELESSNESS ODDS RATIO IS REPORTED AND NEVER TARGETED, author:
    # *"i also want a report of the homelessness odds ratio"* and *"we are not
    # calibrating delta_h...that one is dropped"*.  ENGINE.md's phase 3 agrees:
    # anywhere in 1.8 to 2.4 is fine, only below 1.8 is delta_h reopened.
    # BOTH ODDS RATIOS ARE REPORTED AND NEITHER IS TARGETED NOW.  delta_h was
    # dropped by the author on 12 September and delta_d pinned at 0.24 the same
    # day, so this line is how the pin is judged: if the SUD ratio sits far from
    # 2 at delta_d = 0.24, that is the thing to look at, and it will be visible
    # rather than buried in a bracket that was quietly chasing it.
    print(f'  PENALTY delta_d {par.delta_d:.4f} in log income, which is a child'
          f' income cut of {100 * (1 - math.exp(-par.delta_d)):.1f} per cent')
    print(f'  ODDS    child homeless {m["child_hl_or"]:.3f}'
          f'   child SUD {m["child_sud_or"]:.3f}  at delta_d {par.delta_d:.2f}'
          f'   (both reported only)')
    return max(gs)


if __name__ == '__main__':
    from recalibrate import FIXED, START
    from negative_value_of_life import negative_value_share
    # BETA IS EXOGENOUS AT 0.995 ANNUAL, WHICH IS 0.995**30 = 0.86038 OVER A
    # THIRTY-YEAR PERIOD.  Author, 13 September: *"ok, use beta=0.995."*  It was
    # exogenous at 1.0 on their earlier instruction of 12 September -- *"ok, i
    # think we can just set beta=1"*, *"exogenous, not calibration"*,
    # *"beta=1.47 is not believable"* -- so this is a change of an exogenous
    # value, NOT a parameter coming off a bound.  It was never calibrated here.
    #
    # WHY IT WAS 1 AND WHY THAT REASONING STILL HOLDS.  Calibrating beta on a net
    # worth to income ratio of 3 drove it to 1.477 at the old positive interest
    # rate and to 1.62 once interest was set to zero -- a household valuing a
    # period thirty years away MORE than the present.  That is why networth is an
    # OUTPUT and not a target, and it stays one.  Expect networth to fall further
    # below 3 at the lower beta; it is reported, not aimed at.
    #
    # THE COST IS MEASURED AND IT IS NOT SMALL.  Substituting 0.86038 into the
    # 13 September calibrated vector with every other parameter held puts
    # participation at 0.324 against 0.089 and users' income at 1.78 of average
    # -- above one, which is the corner branch recalibrate.py records a failed
    # sweep on.  The direction is the model's own logic, since a less patient
    # household weighs a thirty-year consequence less and uses more, but it means
    # this calibration MUST start from the interior-branch point and not from the
    # beta = 1 vector.  See recalibrate.py's START for why the start picks the
    # branch.
    #
    # AND THE DIRECTION CONFIRMS WHAT WAS FLAGGED: removing a positive return
    # made saving less attractive, so beta rose rather than fell.
    # SEEDED FROM ITERATION 3400 of sr_run_224426.log, the best point that run
    # reached: median gap 1.8 per cent, ten of eleven brackets inside ten, with
    # the income of users at +8.3 and the drug spending share at +5.8 TOGETHER,
    # and the child SUD odds ratio exact at 2.0023.  The one row outside ten is
    # the child gap at -36.2, which is what this run is for.  Seeding is not
    # putting a thumb on the answer -- every start on the interior branch has
    # reached the same region -- it is starting this run where the last one got
    # to instead of walking the same three thousand passes again.
    SEED = dict(gam=0.43813, aleph=10.98104, h1=0.00969, b=0.06063,
                pi_base=0.41372, u0=0.04824, u1=0.05508, omega=0.00905,
                # delta_d SOLVED, not guessed.  The author, 13 September:
                # *"you should scan the incomes and see which ones give an odds
                # ratio of 2 and pick that"*.  Scanned on this vector with no
                # floor: 0.10 gives 1.1331, 0.24 gives 1.3500, 0.40 gives
                # 1.6414, 0.55 gives 1.9558, 0.66 gives 2.2103, 1.00 gives
                # 3.1083 -- smooth and monotone throughout -- and bisecting on
                # it lands at 0.56972, which returns 2.0000 to four decimals.
                # That is a child income cut of 43.4 per cent.
                delta_d=0.56972, kap=0.10589, th=0.15242)
    # RESEED FROM THE BANKED PRE-CLIFF POINT, sr_run_002132.log iteration 1200:
    # median gap 0.3 per cent with ten of eleven brackets inside ten and all ten
    # of those inside 3.1.  omega there is 0.00853, below the cliff, so the run
    # starts on the right side of it and the new bound keeps it there.
    # gam IS NOT SEEDED.  It is SET at its data value of 0.268 -- see the note in
    # SPEC -- and SEED is applied LAST, so leaving it here would put 0.437 back
    # and silently undo the decision.
    # RESEEDED FROM ITERATION 900 of the two-rental run at rho = 0.35, which is
    # the best fit of the session: eight of ten moments inside ten per cent,
    # seven of them exact, median gap 0.1 per cent, nothing held, and r_use at
    # 0.7373 against 0.74 on the interior branch.
    #
    # omega STARTS AT 0.003 AND IS STILL CALIBRATED, on the author's instruction
    # of 13 September: *"you can make it 0.003"*, then *"i mean, calibrate it
    # but start it from 0.003"*.  Measured at the iteration-900 vector, the
    # child gap crosses its 0.1834 target between omega 0.003 (0.1605) and 0.004
    # (0.2341), so this starts the bracket AT the crossing instead of a long way
    # above it.
    #
    # WHY IT COULD NOT GET THERE ON ITS OWN.  From 0.00853 the bracket crawled to
    # 0.0070 over nine hundred iterations while delta_d climbed 0.5697 -> 0.6606
    # closing its own moment.  A larger delta_d is a larger Delta(y), which is a
    # larger deterrent at ANY omega, so the gap bottomed at +592 per cent near
    # iteration 550 and then ROSE every table to +624: delta_d was widening it
    # faster than omega could narrow it.  Starting omega at the crossing gives it
    # a chance to settle before delta_d moves much further.
    # u1 IS RESET to 0.04860, where the experiment began, rather than left at the
    # 0.4584 it drifted to: that vector records the speed mismatch, not the
    # mechanism.  Everything else is the point where eight of ten moments were
    # inside ten per cent.
    # RESEEDED FROM ITERATION 900, which is where the previous run converged:
    # eight of ten moments inside ten per cent, median gap 0.3, nothing held,
    # VSL exactly 80.0000 and the housing share exactly 0.2680.  It had stopped
    # moving -- u1 frozen at 0.0725 since iteration 450 and omega at 0.0020 --
    # with the two composition moments capped.
    #
    # omega STARTS AT 0.0005, on the author's instruction of 13 September:
    # *"maybe move omega_c=0.0005?"*.  At 0.0020 the child gap sat at 0.5144
    # against a target of 0.1834 and would not move: omega's step cap is 0.05
    # per cent, the slowest in the spec, so closing a gap that size from there
    # takes thousands of iterations.  Starting below the crossing lets the
    # bracket approach it from the other side instead.
    SEED = dict(aleph=12.4055, gam=0.4429, h1=0.01010, b=0.05310,
                # 0.0368/0.089, the value the identity sets, not a start
                pi_base=0.0368 / 0.089, u0=0.04760, u1=0.07250, omega=0.0005,
                delta_d=0.79370, kap=0.11060, th=0.14930)
    _start = {**{k: v for k, v in FIXED.items() if k != 'kap'},
              **{**START, "th": 0.25, "beta": 0.995 ** 30, "kap": 1.0 - 0.91 ** 2,
                   # A STARTING VALUE AGAIN, not a pin: delta_d is back in SPEC
                   # and is stepped, from the 0.24 the author pinned it at.
                   "delta_d": 0.24,
                   # THE INCOME FLOOR IS OFF, and the reason is that it and the
                   # author's own instruction cannot both stand.  They asked for
                   # a floor "so no one has negative value of life", and then
                   # for the child's SUD penalty to be calibrated to the odds
                   # ratio.  Measured, the floor makes the second impossible:
                   #
                   #   delta_d   OR, no floor   OR, floor 0.19
                   #      0.24         1.3600           0.6184
                   #      0.60         2.0967           0.2795
                   #      2.00         6.2929           0.0059
                   #
                   # The floor does not merely blunt delta_d, it REVERSES ITS
                   # SIGN.  A child pushed down by the penalty lands on the
                   # floor, and at 0.19 it is housed and fed, which is a
                   # lower-use state than being just above the floor paying rent
                   # out of a thin income.  So the harder the penalty pushes the
                   # more protected the child becomes, and a ratio of 2 is
                   # unreachable at any delta_d.  The live run demonstrated it:
                   # delta_d walked to 1.249, past the 0.57 the target needs,
                   # with the ratio down at 0.718 and still falling.
                   #
                   # It also killed two other brackets outright -- homelessness
                   # went to zero because the floor is what lets the priced-out
                   # afford the cheapest unit, and sud_of_homeless2 had no
                   # homeless population to form a ratio from.
                   #
                   # The negative value of life therefore stands at 1.43 per
                   # cent of period-2 states, which is the same order as the
                   # quantitative model's 0.45 per cent, and that model runs
                   # with it rather than eliminating it.
                   "y_floor": 0.0,
                   # STARTING VALUES MATTER WHEN THE STEP IS RELATIVE.  The
                   # author, 12 September: *"this is why the model cannot
                   # converge"*.  h1 started at 1e-4 and lands near 1e-2 -- a
                   # factor of a HUNDRED, which at 0.5 per cent a pass is about
                   # 920 iterations before homelessness can respond at all.
                   # Measured, it was doing exactly that: h1 climbing 0.00010,
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
                 "h1": 0.005, "b": 0.07}}
    _start.update(SEED)                       # SEED WINS: it is applied last
    par = with_(P(), **_start)
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
    # THE INCOME FLOOR RISES UNTIL NOBODY HAS A NEGATIVE VALUE OF LIFE.
    #
    # The author, 12 September: *"You need to keep raising the lowest income
    # then until no household has negative value of life."*  So it is a RULE,
    # not a pinned number.  A fixed floor would be wrong twice over: the share
    # with a negative value depends on the whole vector, which moves every pass,
    # and a floor set once can be undone later by aleph or kappa drifting.
    #
    # The rule is one-directional, which is what "keep raising" means: raise
    # while any household has a negative value of life, stop when none does,
    # never lower.  It therefore converges to the SMALLEST floor that clears the
    # condition on the vector the search actually ends at, and re-raises if a
    # later pass re-opens it.
    #
    # THE STEP IS ABSOLUTE, NOT RELATIVE, because the floor starts at zero and a
    # relative step from zero never moves.
    #
    # WHAT THIS COSTS, MEASURED, AND THE AUTHOR HAS BEEN TOLD.  Imposing a floor
    # on the vector calibrated WITHOUT one takes homelessness to zero at 0.12
    # and above, and sud_of_homeless2 with it, and at 0.19 it reverses delta_d's
    # sign on the child SUD odds ratio.  Those tests held every other parameter
    # fixed.  Here the brackets are free to answer -- h1 is exactly the
    # instrument for homelessness -- and whether they do is the open question
    # this run settles.
    FLOOR_STEP = 0.002
    # THE FLOOR IS OFF FOR THIS RUN, and the reason is measured, not preferred.
    # With it at 0.182 the odds ratio of 2 the author asked to hit is out of
    # reach at EVERY penalty -- scanned, the ratio runs 0.837 down to 0.124 --
    # because the floor removes thirty-four of the forty-three using income
    # levels and every one of them is poor.  Without it the same scan is smooth
    # and monotone and 0.56972 returns 2.0000.  The author asked to solve the
    # penalty for the ratio and then to calibrate, and only one configuration
    # admits both.  The negative value of life therefore stands at 1.56 per cent
    # of period-2 states and the FLOOR line on every table reports it.
    # THE FLOOR IS ON, ON THE AUTHOR'S INSTRUCTION OF 13 SEPTEMBER: *"turn on
    # y_floor and start the full calibration."*  It was off, for the reasons
    # measured above, and those reasons have NOT gone away -- they are restated
    # here so the run is read with them in view rather than discovered again.
    #
    # WHY IT WAS ASKED FOR.  chdmg is now solved rather than held at zero, and
    # switching that channel on at the old vector took the drug share to 0.00001
    # and users' mean income to 0.13: it deterred every genuine user and left
    # only the households whose value of life is negative, which buy the
    # smallest sliver the grid sells purely to acquire the disorder and die
    # sooner.  The floor is the existing instrument for exactly that.
    #
    # THE START IS 0.18614, NOT 0.15, because 0.18614 is the MEASURED value that
    # clears the negative value of life -- see _states in stylized.py, where it
    # is 1.86 times the rent on the small unit -- and the whole point of turning
    # the floor on is to clear it.  Starting below it and stepping up leaves the
    # pathology live for the early loops, which are the ones that pick the
    # branch.
    #
    # AND THE CONFLICT IS UNRESOLVED AND IS THE WHOLE RISK OF THIS RUN.  The
    # floor that clears the pathology and the floor that breaks the child SUD
    # odds ratio are the SAME FLOOR.  At 0.19 the measured scan has delta_d's
    # sign REVERSED -- a child pushed down by the penalty lands on the floor,
    # where it is housed and fed, which is a lower-use state than being just
    # above the floor paying rent out of a thin income -- so the ratio of 2 is
    # unreachable at any penalty and delta_d walks away to 1.249 with the ratio
    # at 0.718 and falling.  0.18614 is not meaningfully below 0.19.
    #
    # WHAT IS GENUINELY OPEN, and it is why this run is worth making rather than
    # refusing.  Every one of those measurements HELD THE OTHER PARAMETERS
    # FIXED.  Here the brackets are free: h1 is exactly the instrument for
    # homelessness, and whether the free brackets can answer the floor is the
    # question this run settles.  If the child SUD odds ratio walks away from 2
    # while delta_d climbs past 0.6, that is the reversal and the run should be
    # stopped rather than left to grind.
    FLOOR_ON = True
    if FLOOR_ON:
        # 0.099, NOT 0.18614.  The author, 13 September: *"the lowest income
        # should be such that 0.5% cannot afford to rent h2"*.  Measured with
        # the priced-out share keyed on h2, the cheapest rental: at a floor of
        # 0.099 it is 0.00357, which is the half a per cent asked for; at 0.12
        # and above it is exactly zero and nobody can be unhoused for want of
        # money at all.
        #
        # AND IT CHANGES WHICH WAY h1 HAS TO MOVE.  At this floor 0.36 per cent
        # are priced out and 6.6 per cent are homeless, so the other 6.3 per
        # cent are CHOOSING the street.  h1 has to fall from 0.0371 to thin them
        # out, not rise.  The earlier reading that h1 had to rise came from a
        # priced-out measure keyed on h3, the LARGE unit, where being priced out
        # means renting the small one rather than being unhoused.
        #
        # THE COST IS THE PATHOLOGY, and it is reported rather than hidden: at a
        # floor near 0.10 the negative value of life runs about 0.4 per cent,
        # against 0.00 at 0.186.  The author asked for no negative value of life
        # AND for half a per cent priced out, and those two want the floor on
        # opposite sides of 0.12.  The FLOOR line on every table carries it.
        par = with_(par, y_floor=0.099)
    for it in range(50000):
        m = moments(par, it)
        if FLOOR_ON and it % 10 == 0:
            nv = negative_value_share(par)['share']
            # THE FLOOR MAY NEVER REACH THE RENT, AND THE LAST RUN SHOWS WHY.
            #
            # The step fires whenever any negative value of life remains, and
            # over six hundred iterations it walked y_floor from 0.186 to 0.274
            # while the rent sat at 0.266.  Once the floor passes the rent EVERY
            # household can afford the unit, homelessness is identically zero,
            # and its instrument loses all grip: the gap sat at -100 per cent
            # from iteration 500 to the end while the floor kept climbing.  The
            # pathology was still 1.00 per cent, so it would have climbed for
            # ever.
            #
            # Capped just below the rent, the floor can still clear the poorest
            # households' negative value of life -- which is what it is for --
            # but it can never house the whole distribution, so homelessness
            # stays a live margin.  If the pathology survives at the cap, that
            # is a fact to report rather than something to outrun.
            # THE AUTO-STEP IS OFF: y_floor IS BRACKETED NOW.
            #
            # It is in SPEC, on homelessness, so a stepper that also moved it
            # every ten iterations would be a second controller fighting the
            # first -- and the step is blind, which is how the previous run
            # walked the floor past the rent and killed homelessness outright.
            # The pathology is still REPORTED on every table, and if it survives
            # at the floor the bracket chooses, that is a fact to report rather
            # than something to outrun.
            pass
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
