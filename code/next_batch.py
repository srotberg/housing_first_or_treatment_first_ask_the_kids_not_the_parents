#!/usr/bin/env python3
"""Wait until b and lambda_d are both within five per cent, then correct the rest.

THE AUTHOR, 30 AUGUST 02:35: "once you are 5% away from both lambda_d and b, then
automatically start spawning the algorithm to converge on the other parameters",
and earlier, "the rest i think are much easier and you can slowly converge on
them". This is that gate and that algorithm, so the engine fires it on its own
rather than waiting for someone to notice the gate has opened.

WHY A GATE AND NOT A JOINT SOLVE OVER EVERYTHING. b and lambda_d are the pair
the whole search has failed on -- lambda_d was the worst moment at 70 of 110
points -- and they are reached through two instruments whose elasticities are
enormous and curved: addiction_scalar_1 moves b with an elasticity between -12
and -26 depending where you stand. Every other moment on the list has an
instrument with an elasticity between 0.7 and 2, measured, with the target
already spanned. Those are different problems and mixing them is what produced
twenty two hours of flat loss. So the drug block is closed first, on the locus,
and only then does this open.

THE STEP IS DAMPED AND SINGLE-COORDINATE. Each line moves ONE parameter, which
keeps every point a clean arm of the Jacobian as well as a correction, so a batch
that overshoots still buys the derivative it was missing. The step is
Newton on that parameter's own measured elasticity, damped, and capped in
e-folds, because the author asked to converge slowly and because an undamped
step through an elasticity measured somewhere else is exactly how the aimed
steps missed by factors of three and five.

ELASTICITIES ARE MEASURED, NOT ASSUMED. They come from pairs of archive points
differing in ONE coordinate, nearest the winning point first. A parameter with no
such pair gets no line, and says so, rather than being moved on a guess.
"""
import glob
import hashlib
import json
import time
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# THE GATE OPENS AT FIVE PER CENT; THE BASE IS THEN CHOSEN AT TEN.
# "once you are 5% away from both lambda_d and b, then automatically start
# spawning the algorithm to converge on the other parameters" is a condition for
# STARTING the correction phase, and it has been met. Holding every subsequent
# base to five per cent as well is stricter than the author's actual rule and has
# started to block progress: the tau_u correction took the worst gap from 82 to
# 70 per cent and is the best point in the archive, but its lambda_d sits at +7
# and the five per cent test rejects it as a base, so the loop would keep
# correcting from a worse point indefinitely.
#
# So the phase opens at five and the base is then the best point by worst-gap
# among those inside TEN, which is the standard the author set for the paper. A
# base whose drug block has drifted past five still gets repaired -- a restore
# line is emitted alongside the arms -- so the drift is corrected in parallel
# rather than being allowed to accumulate.
GATE = {'b': 0.05, 'lambda_d': 0.05}     # opens the phase
BASE_TOL = {'b': 0.10, 'lambda_d': 0.10}  # admissible as a base thereafter

# THE GATE OPENS IN STAGES, NOT ALL AT ONCE.
#
# The author, 1 September: "You might want to open gates slowly... You might want
# to add h1 and h2 first after you have b and lambda d. Then open a bit more in
# the next critical moments. And so on."
#
# The first composed step of the evening moved TEN instruments at once off the
# newly pinned base. That is the same shape as the two hand-built anchors that
# failed earlier the same day, where every individual step was inside the 0.35
# e-fold cap and they still did not compose -- one took lambda_d from +1.2 to
# +815 per cent. Capping each step is not sufficient; the cross-effects compound.
#
# So a stage is a set of MOMENTS. Only instruments owning a moment in an OPEN
# stage may be stepped; everything else is held at the base. A stage opens when
# every moment in every earlier stage is inside BASE_TOL -- or when it has
# stalled, see STAGE_PATIENCE.
#
# The ordering is the author's for the first two and mine, stated, for the rest:
# after the drug block and the housing block comes the disorder and treatment
# block, which is the paper's own mechanism, and the aggregates last because they
# are the ones the model reaches most easily.
STAGES = [
    # THE AUTHOR'S SEQUENCE, 2 September, given in their own words: "calibrate
    # aleph and beta, omega_ell, sigma_y, and tau_ell. then move to b, lambda_d
    # and theta. then h1, smallest_rental_relative_to_lowest_income, and
    # newborn_endowment_scale."
    #
    # The macro block first. These five set prices, the wealth distribution and
    # the labour supply, and everything after them is measured against those --
    # so calibrating the housing block against a discount factor that later moves
    # is measuring against a base that will not hold still, which is the same
    # fault the drug gate exists to prevent one stage down.
    # pi_eu, pi_V and cbar JOIN ROUND 1 on the author's instruction, 2 September:
    # "actually you can add pi_eu, pi_V, cbar to stage 1". All three are
    # aggregates or policy levels set outside any of the blocks below, so they
    # belong with the macro round rather than in the leftover.
    # w_bot JOINS ROUND 1 with the second discount factor as its instrument. The
    # author, 2 September: "add two betas....and calibrate the impatient beta in
    # the macro stage (stage 1). half the population needs to be impatient."
    # beta_type_weight was already 0.5d0, so the half is unchanged.
    # STAGES 0, 1 AND 2 MERGED, 2 September, on the author's instruction: "You
    # need to do clear adjustments on b, lambda d and h1." Those three sat in
    # stages 1 and 2, so every instrument owning them was HELD -- the gate said
    # so itself, "size_homelessness (owns h_1): held, its stage is not open
    # yet" -- and stage 0 has never closed, so they could not open.
    #
    # That is why the headline loss did not move for a day. It is a minimax over
    # all scored moments, h_1 dominates it at +652 per cent, and h_1's
    # instrument was frozen by the staging while the fleet correctly worked
    # stage 0. size_homelessness took exactly ONE value, 0.149, across all
    # thirteen points; addiction_scalar_1 took exactly one, 0.0360.
    #
    # The author had already authorised merging the first two ("yes, merge them
    # once the borrowing arms land") and has now asked for h_1 as well. The
    # staging rationale above -- that a later block calibrated against a moving
    # base is measured against nothing -- still stands and is not repealed; it is
    # traded for reaching the moments that dominate the objective at all. The
    # per-step e-fold cap and the drug gate remain, so the protection against
    # steps that do not compose is unchanged.
    ['aleph', 'beta', 'omega_l', 'sigma_y', 'tau_l', 'pi_eu', 'pi_V', 'cbar',
     'w_bot', 'b', 'lambda_d', 'theta', 'h_1', 'emp_homeless', 'gamma',
     # h_2 JOINS THE OPEN STAGE, 3 September. It became a scored moment again
     # when the rung was pointed back at it, and a scored moment outside every
     # open stage is the worst of both: it counts against the loss and its
     # instrument is never allowed to step. That combination pinned the headline
     # number for a full day in the h_1 case and is recorded above.
     #
     # The three housing moments are now one block with one instrument each:
     #   size_homelessness                          -> h_1, the homelessness rate
     #   smallest_rental_relative_to_lowest_income   -> h_2, the cost burdened
     #   bottom_productivity_level                   -> emp_homeless
     'h_2',
     # h_share1 joins with h_2, so its instrument newborn_endowment_scale can
     # actually step. A scored moment outside every open stage counts against the
     # loss with its instrument frozen, which has cost this calibration a day
     # once already.
     'h_share1'],

    # Then the drug block, with theta joining b and lambda_d. theta was in the
    # disorder stage; the author has moved it up beside the two it is coupled to.
    # aleph RIDES ALONG IN ROUND 2, damped. The author, 2 September: "you could
    # then adjust aleph also slowly when you adjust b and lambda_d in the second
    # stage." The value of life and the drug block are the pair that fight --
    # the aleph arm moves b by -85 per cent and lambda_d by -91 -- so round 1
    # sets aleph, round 2 re-fits the drug block to it, and aleph keeps a small
    # step here to absorb what the re-fit does back to it. It is listed again so
    # it stays live even after round 1 closes.
    ['b', 'lambda_d', 'theta'],

    # Then the housing block, unchanged from where the author put it.
    # gamma JOINS THE HOUSING STAGE on the author's instruction, 2 September:
    # "also add gamma to the h1, smallest_rental_relative_to_lowest_income, and
    # newborn_endowment_scale round". Its instrument is relative_share_of_housing,
    # the weight on housing in utility, and it belongs here for the reason the
    # rung arm made plain: the utility cost of a bad dwelling is what decides
    # whether a household priced out of the cheapest unit takes the street or
    # pays, so gamma and the rung are the same decision seen from two sides. It
    # was in the leftover stage.
    # THE MOMENT h_2 TRAVELS WITH ITS PARAMETER. The author, 2 September: "wait
    # h2 is basically this: smallest_rental_relative_to_lowest_income."
    #
    # It was in the leftover round showing "(no instrument)", which is true in
    # the narrow sense -- the rung's owner slot holds emp_homeless, because the
    # author assigned it there -- and misleading in every sense that matters. One
    # parameter cannot own two moments, but the cost burden headcount is moved by
    # the rung and by nothing else, so judging it in a later round than the rung
    # means the rung is set without it and then scored against it afterwards.
    # It belongs in this round, unowned but measured, and the minimax sees it.
    # (h_1, emp_homeless and gamma moved up into the merged stage above.)

    # Then everything else. This tail is mine, not the author's, and it is
    # ordered by nothing in particular because by the time it opens the three
    # blocks above are pinned.
    # "then we can consider the rest" -- the author, 2 September. This tail is
    # NOT a considered ordering and must not be read as one; it is everything
    # left over, opened together once the three blocks above are pinned, and the
    # author has reserved the decision about it.
    # The last round, the author's own list: "then tau_u, mu_H and lambda_m in
    # the last stage." p_m is NOT in it -- see below.
    ['tau_u', 'mu_H', 'lambda_m', 'sud_homeless', 'p_m'],

    # THE LAST ROUND IS omega_c ALONE. The author, 2 September: "omega_c comes at
    # the very end in stage 5." It needs measure_child_gap=1 handed in, which is
    # a handover parameter as of the same day; until then nothing measures it and
    # the round cannot close.
    ['omega_c'],
]

# A STAGE THAT CANNOT BE SATISFIED MUST NOT DEADLOCK THE ONES BEHIND IT.
#
# emp_homeless is in stage 1 and nine controlled points say the housing block
# cannot reach it: the rung converts homelessness from chosen to involuntary --
# by-choice falls 0.99 to 0.11 -- while the employed share stays in 0.82 to 0.99.
# On a strict reading stage 2 would never open and the search would stop dead
# behind a moment the author has not yet decided about.
#
# So a stage also opens once it has gone STAGE_PATIENCE firings without its worst
# moment improving. The loop says which stages are open and WHY -- satisfied or
# stalled -- every time, so a stalled stage is visible rather than silently
# skipped, and it stays in the loss throughout.
# PATIENCE SCALES WITH THE ROUND'S SIZE. A flat three was set when a stage held
# two moments; round 1 holds NINE, and three measurements cannot fit nine
# instruments -- it was marked STALLED forty-five minutes after opening, having
# had one measurement per three instruments. The author's ordering is "get the
# first stage done, then we move to the second stage", and a threshold that
# expires before a round has been measured once per instrument defeats it.
#
# Two measurements per instrument, floored at three. Round 1 gets eighteen; a
# two-moment round still gets four. The deadlock guard is intact -- an
# unreachable round still opens the next one eventually, which is what it is for
# -- it just no longer fires before the round has been tried.
def stage_patience(st):
    n = sum(1 for q, mo in OWN.items() if mo in st)
    return max(3, 2 * n)
RESTORE_AT = 0.05                         # emit a repair line beyond this
ACCEPT = 0.10                             # the author's ten per cent rule
DAMP = 0.70                               # converge slowly, do not jump
MAX_EFOLD = 0.35                          # no single step larger than this

# Parameter -> the moment it owns. Taken from the Fortran's own adjusters, which
# is why relative_share_of_addiction_1 is paired with theta: the model updates it
# against drug_share_weighted_1 - drug_spending_share_data and clamps it between
# variables named theta_lo and theta_hi. It is NOT a free instrument for the
# disorder ratio, which is the error that flattened the loss.
OWN = {
    # BACK TO A UTILITY COST, on the author's instruction of 31 August. The
    # price of treatment is held at zero and the disutility owns tau_u again.
    # Neither is internally calibrated -- distance_money_cost_of_treatment is
    # declared and never used, and utility_cost_of_treatment_adjuster is zero --
    # so the switch is entirely in this mapping and in run_one_point's defaults.
    'utility_cost_of_treatment':                           'tau_u',
    'probability_becoming_unemployed':                     'pi_eu',
    'relative_share_of_addiction_1':                       'theta',
    'mu_homeless':                                         'mu_H',
    # lambda_m THE PARAMETER IS HELD, so that lambda_m the moment has ONE driver.
    # kappa_uem took ownership just above; leaving the recovery rate pointed at
    # the same moment would be two instruments on one target, which is the
    # duplicate-driver mistake beta was cured of. It stays in the vector, so a
    # point records it, and it moves by hand.
    # THE SECOND HALF OF THE SMI PAIR. The parameter lambda_m moves BOTH SMI
    # moments the same way -- raising it 0.067 to 0.12 took the share of the
    # homeless 0.154 to 0.105 AND the population share 0.045 to 0.028 -- so it
    # cannot fix one without breaking the other. smi_onset_level owns the
    # population share: a controlled pair moves p_m by -6 per cent for a -20 per
    # cent step while barely touching the share of the homeless, +1.25 per cent.
    # Two moments, two instruments; only one of them had ever been listed.
    # p_m IS BACK. The author said "p_m is not used" and then, minutes later,
    # asked "isn't smi_onset_level set to match the overall share of SMI?" -- it
    # is, and that is what p_m is. Restored to round 4 with its instrument.
    'smi_onset_level':                                     'p_m',
    'value_of_life':                                       'aleph',
    # RE-POINTED ON THE AUTHOR'S INSTRUCTION, from kappa_ued to the SUD share of
    # the homeless. The argument is double counting: a disorder that both takes
    # the job AND cuts the wage of a household that keeps one is charging the
    # same earnings loss twice, and the code had already reached exactly that
    # conclusion for SMI -- "rho_m has no job left that is not already
    # assigned". So the unemployment shock carries the whole channel and rho_d
    # is held at one.
    #
    # kappa_ued IS AN OUTPUT NOW, AND THAT IS THE POINT, NOT A COST.
    #
    # It was written up here as a price being paid -- a data moment at 0.1625
    # given up. The author's answer is that it is not a moment worth defending:
    # "It's ok if the unemployment rates of those with SUD and SMI are not
    # aligned with the data we have. We don't truly know what they are so we
    # calibrate them." The unemployment rate of people with a substance use
    # disorder is not measured with the confidence the HUD age profile or the CEX
    # cost-burden headcount are, so it is the right one to let float.
    #
    # So kappa_ued is reported as an untargeted OUTPUT at every point, not as a
    # miss. UNSCORED is where it belongs and nothing more is owed to it.
    #
    # A consequence for when the paper is written: the calibration table should
    # show this rate as CALIBRATED, with the SUD share of the homeless as its
    # target, rather than as an assigned number the model happens to reproduce.
    # IN ROUND 4 ON THE AUTHOR'S INSTRUCTION, 2 September: "this one should be in
    # round 4: multiple_of_probabilities_of_employment_if_addicted". It owned
    # sud_homeless while sud_homeless was UNSCORED, so it was the one parameter
    # that moved with nothing judging it. Both are in the loss now.
    'multiple_of_probabilities_of_employment_if_addicted': 'sud_homeless',
    # omega_c, THE LAST ROUND. The author, 2 September: "omega_c comes at the
    # very end in stage 5." weight_on_child was in no map at all -- it appeared
    # in gaps.py's table so the author could see it, and in next_batch nowhere,
    # so nothing would ever have stepped it. Its moment is only measured when
    # measure_child_gap is handed in as 1, which is what the final round does.
    'weight_on_child':                                     'omega_c',
    'probability_of_voucher_benchmark_used':               'pi_V',
    'size_homelessness':                                   'h_1',
    # NOT given a moment. homeless_excess_death_risk sets the LEVEL of the
    # deterrent and size_homelessness already owns h_1; giving both the same
    # moment would be the duplicate-driver mistake beta was just cured of.
    # It is in the vector so a point records it, and it moves by hand.
    # H_2 IS THE SEVERE COST BURDEN NOW, AND IT HAS AN INSTRUMENT AT LAST.
    # It used to be the share in the smallest unit, was conceded by the author
    # and sat in SKIP, and the parameter that owns it --
    # smallest_rental_relative_to_lowest_income, the SIZE of the smallest rental
    # -- was in the vector with no moment mapped to it, so nothing in the search
    # ever moved the bottom of the housing ladder. A bigger smallest unit costs
    # more rent, so it raises the share paying over half of income.
    # SWAPPED, on measured elasticities. This owned h_2 at 0.06 while
    # largest_house_size moved h_2 at 1.73 -- each grid parameter was assigned
    # to the moment it moves LEAST. smallest_rental's strongest moment is
    # actually h_1 at 2.81, but size_homelessness already owns that and the
    # food stamp floor has closed it, so it takes h_3 here. It moves h_3 at
    # -0.01, which is to say h_3 has no real instrument at all.
    # REPOINTED TO h_2 ON THE AUTHOR'S INSTRUCTION, 1 September:
    # "make the cheapest unit such that we have the right fraction of households
    # spending over 50% of their income on housing... no of total spending".
    # CORRECTED SAME DAY: the author meant over half of INCOME, not of total
    # expenditure. The moment is `rent50`, the share of RENTERS paying more than
    # half their income in rent, 0.3625 in the model against 0.175 observed --
    # not h_2, which is the headcount above half of total EXPENDITURE and reads
    # 0.0899 against 0.101 and is nearly closed already.
    #
    # It replaces h_3, which this parameter moves at -0.01 -- nothing. The
    # consequence of that mapping was not a small inefficiency: the ONE number
    # governing whether a household can be priced out of housing was assigned
    # rather than calibrated, and then pointed at a moment that could never
    # discipline it. `homeless who could afford it on INCOME ALONE` has read
    # exactly 1.0000 at every point measured, which is the same fact.
    # THE COST BURDEN ON THE SAME DENOMINATOR AS GAMMA, on the author's
    # instruction of 1 September: "keep the 26.8% for gamma. maybe use the same
    # statistic for h2 but % spending over 50% on housing?"
    #
    # h_2 is the headcount above half of total EXPENDITURE, target 0.101 from the
    # CEX. rent50 is the same headcount over INCOME, target 0.175. One parameter
    # sets both and they were pointing OPPOSITE WAYS:
    #
    #     h_2     0.0622 vs 0.101  = -38.4 per cent  -> RAISE the cheapest rung
    #     rent50  0.4599 vs 0.175  = +163 per cent   -> LOWER it
    #
    # That contradiction is what had me reporting rent50's owner with the sign
    # backwards this evening, until the author pointed out that two thirds of
    # renters sit in the TOP rung and the burden lives entirely there. On the
    # expenditure denominator the moment agrees with them and with gamma; on the
    # income one it does not, and it is the income one that is inconsistent with
    # how the Cobb-Douglas weight is defined.
    #
    # rent50 moves to UNSCORED. It stays parsed and reported at every point,
    # because it is the number the appendix quotes, and it is no longer a second
    # target competing for one instrument.
    #
    # REASSIGNED 1 September on the author's instruction: "choose h2 to match
    # it", where "it" is the employed share of the homeless. The cheapest rung
    # now owns emp_homeless, NOT the cost burden headcount.
    #
    # The reason is that emp_homeless has no other instrument, and the one it
    # had was measured not to work. At point_c947746ef0, 98.9 per cent of the
    # homeless could pay the cheapest rent out of income alone and 99.5 per cent
    # out of income plus assets, so the street is a taste margin, not a budget
    # one. increased_prob_if_homeless changes what happens to a household WHILE
    # homeless; on a taste margin that makes the employed choose a room instead
    # of holding them on the street, so it moves the LEVEL of homelessness and
    # not its composition. P(homeless|unemployed) over the working age rate
    # reads 0.258 where the data implies about 3.9 -- the SIGN of the selection
    # is backwards, not just its size.
    #
    # Raising the cheapest rung is the only thing that prices anyone out of it,
    # and the households it prices out are the low income ones, who are
    # disproportionately the unemployed. That is what turns homelessness from a
    # taste into a budget outcome and lets the composition move at all.
    #
    # THE COST BURDEN HEADCOUNT IS NOW UNOWNED. It stays scored -- the author
    # reversed its concession explicitly -- but nothing brackets on it, so it
    # will show as "(no instrument)" until it is given one or conceded. Say so
    # rather than letting it look assigned.
    # THE RUNG TARGETS THE COST BURDEN AGAIN, on the author's instruction of
    # 2-3 September. It had been pointed at emp_homeless because nothing else
    # could reach that moment; the bottom of the productivity grid now can, so
    # the rung goes back to the moment that is actually its own -- the CEX
    # severe cost burden headcount, moment h_2, target 0.101.
    'smallest_rental_relative_to_lowest_income':            'h_2',
    # THE BOTTOM PRODUCTIVITY NODE OWNS emp_homeless. The author, 3 September:
    # *"That grid point on y is the one that delivers the 46% employment of the
    # homeless."* It is the level, not the mass: y_grid_kappa stays FIXED at 3.2
    # so that one instrument faces one moment. Two dials on one target would be
    # under-identified and reachable from absurd pairs.
    #
    # THE 19.1 PER CENT IS NOT A TARGET. The author, same message: *"The 19.1%
    # average income should come out in the validation section."* Income of the
    # homeless stays UNTARGETED and unscored, which is the stronger claim -- if
    # the model lands near it without being asked to, that is evidence.
    'bottom_productivity_level':                            'emp_homeless',
    # AND THE TOP RUNG HAD NO INSTRUMENT EITHER. largest_house_size owns the
    # share in the largest unit -- h_4 until the author's rename, h_3 now -- and
    # like the bottom rung it sat in the vector with nothing mapped to it. It is
    # only 1.7 per cent off, so this closes a hole rather than fixing a gap.
    # HELD, because h_2 now belongs to the smallest rung. Keeping both pointed at
    # h_2 would be the duplicate-driver mistake the map exists to prevent, and of
    # the two this one is the wrong keeper: it is the TOP rung, so it cannot price
    # anybody out of housing however it moves. It stays in the vector, so a point
    # records it, and it moves by hand.
    #
    # What it costs to hold: largest_house_size moves h_2 at 1.427 and gamma at
    # 0.760, both measured in the seed round, so gamma loses its strongest
    # instrument. gamma's own owner, relative_share_of_housing, is separately
    # held on an h_1 elasticity of -9.567. If gamma cannot be closed by the two
    # remaining housing parameters that is an author decision, not something to
    # paper over by re-pointing a grid parameter at it.
    # 'largest_house_size':                                'h_2',
    # AND THE SAME FOR SMI. kappa_uem, the parameter, now answers to lambda_m,
    # the SMI share of the homeless, rather than to the employment rate of the
    # SMI population.
    #
    # THE EMPLOYMENT RATE OF THE SMI POPULATION IS AN OUTPUT NOW TOO, on the same
    # reasoning: not known well enough to be worth pinning, so calibrated rather
    # than assigned. It was being hit almost exactly, 0.2999 against 0.3000, and
    # it will drift. That is intended.
    #
    # ONE MEASUREMENT STILL SITS AGAINST THE PREMISE and is worth keeping in view
    # while the sweep runs. Seventy per cent of the SMI population is ALREADY out
    # of work and only thirteen per cent of the homeless have SMI, so too few
    # unemployed with SMI may not be what is holding lambda_m down. Raising
    # kappa_uem from 28.7 to 90 takes non-employment from about 0.70 to about
    # 0.90, a fifth again on a high base, where the SUD arm has far more room.
    # And SMI is a young condition here in onset AND in stock, so a lambda_m that
    # does move will move the youngest band. A measurement to make, not an
    # argument for refusing the instruction.
    'kappa_uem':                                           'lambda_m',
    # BACK, ON THE AUTHOR'S INSTRUCTION. The statutory SNAP schedule was right
    # per household and wrong by a factor of 48 in aggregate, so the programme
    # is a calibrated allotment again and cbar is a target again.
    'max_food_cost':                                       'cbar',
    # THE TWO DISCOUNT FACTORS, on the brackets the author set. The patient one
    # keeps wealth over output, which is banded rather than pointed; the
    # impatient one owns the wealth share of the bottom half, which nothing
    # could move while there was a single beta.
    # DISCOUNT_FACTOR IS BACK, AND IT SHOULD NEVER HAVE LEFT.
    #
    # It was removed on the belief -- written into this file in as many words --
    # that "the model bisects the patient discount factor on wealth over output
    # inside every point run", so proposing a value here would be a duplicate
    # driver. THAT IS NOT TRUE OF A POINT RUN, and it is now checked three ways:
    # every one of the 45 points on the current model carries the identical
    # discount_factor=0.99715, the string distance_discount_factor appears in
    # ZERO worker logs, and the one-beta point ends its run with the discount
    # factor exactly as it was handed in. The bisection lives in the full
    # calibration binary; a point does not run it.
    #
    # So beta -- wealth over output -- has had NO instrument at all, and the
    # error was invisible while there were two types: 0.99715 paired with an
    # impatient 0.95 happened to give 4.44, inside the 3.0-4.5 band, so beta
    # scored zero and nothing drew attention to it. At one type the same
    # discount factor gives 6.42 and the moment is 114 per cent out.
    #
    # This is restoring an instrument removed on a false premise, not a scope
    # change. beta is banded rather than pointed, so the step aims at the band.
    'discount_factor':                                     'beta',
    # THE IMPATIENT DISCOUNT FACTOR OWNS w_bot. It was dropped when the model went
    # to one type; the author restored the second type on 2 September because
    # w_bot is what blocks emp_homeless. The archive already brackets the target:
    # 0.0417 at an impatient factor of 0.90, 0.0506 at 0.93, 0.0061 at 0.95
    # against a target of 0.025, so the answer is between 0.90 and 0.95.
    'discount_factor_impatient':                           'w_bot',
    # AND THE SAME BUG, THREE MORE TIMES. beta was not a special case.
    #
    # A point run does not update ANY parameter internally. Eighteen parameters
    # carry a live adjuster in the source, but the block that applies them is
    # never reached -- a point ends at loop_count 2 -- and the check is direct:
    # of the parameters a run prints back, size_homelessness, discount_factor and
    # relative_share_of_leisure all come out EXACTLY as they were handed in.
    #
    # So every moment recorded as "calibrated internally" has in fact had no
    # instrument at all, and the label hid it. These three are the rest of them.
    # sd_permanent_productivity is included even though sigma_y reads -1.7 per
    # cent: it is close by luck, not by anything holding it there, and the next
    # time the economy moves it will drift with nothing pushing back.
    #
    # relative_share_of_leisure is the sharpest case. It was UNFROZEN this
    # afternoon on the author's instruction that "omega_ell should target the 0.4
    # as before", and unfreezing it did nothing whatever, because the adjuster it
    # re-enabled is in a block a point never executes. omega_l has been at -26
    # per cent since, and would have stayed there.
    'relative_share_of_leisure':                           'omega_l',
    'labor_income_tax_rate':                               'tau_l',
    'sd_permanent_productivity':                           'sigma_y',
    # SIGMA_Y HAS A SECOND INSTRUMENT AND ONLY ONE OF THEM IS EVER LIVE.
    # sd_permanent_productivity builds the quantile grid. Under
    # fixed_productivity=0 the grid is the author's KKK_process and this
    # parameter moves NOTHING; the dispersion is set by kkk_sigma_scale, the
    # common multiplier on the two innovation sds, which the Fortran now steps
    # against the same moment and the same target.
    #
    # The mapping is NOT switched here yet, deliberately. Two instruments
    # pointed at one moment is a conflict, and which of them is live is a
    # property of the POINT (its fixed_productivity), not of this table. It is
    # switched when the author picks the benchmark process; the four arms in
    # code/batch_kkk.txt are what that choice rests on. Until then a KKK point
    # carries kkk_sigma_scale explicitly in its vector.
    # 'discount_factor_impatient':                         'w_bot',
    # THE MORTALITY PENALTY IS THE PRICE OF USING, so it decides WHO is willing
    # to pay it, and a high one leaves only the most desperate -- who are the
    # poorest. That is why the model has zero use in the top two income bands
    # against 7.2 and 4.8 per cent in NSDUH. Calibrated on the income of drug
    # users on the author's instruction, rather than assigned.
    # kappa_phi_d_level IS FIXED AT 8 AND OWNS NOTHING. The author, 1 September:
    # "We can keep the mortality fixed at 8 since if it's lower the elasticity of
    # participation might be too high."
    #
    # It is the SUD excess-mortality multiplier -- kappa_phi_d_by_age is
    # 1+(kappa_phi_d_level-1)*shape_sud_profile -- and the declaration's own note
    # records that it USED to be calibrated on the drug price participation
    # elasticity, which is now an untargeted validation moment. Lowering it
    # weakens the deterrent to using and pushes that elasticity back up, so the
    # instrument cannot be spent on y_u without spending the validation moment
    # too.
    #
    # y_u is therefore UNOWNED. It stays scored, at -42 per cent and nowhere near
    # binding, and the author has put it to a robustness run at a higher income
    # rather than into the benchmark. See CALIBRATION_STATE.md.
    # gamma's instrument, freed on the author's instruction. Its measured
    # elasticity on gamma is only 0.22 and it costs h_1 at -7.32, so it is a
    # weak and coupled instrument -- but it is the only one, and h_1 now has
    # both size_homelessness and the food stamp floor holding it.
    'relative_share_of_housing':                           'gamma',
    # OPENED ON THE AUTHOR'S INSTRUCTION, both previously compile-time constants.
    #
    # increased_prob_if_homeless IS EXOGENOUS AGAIN, at 0.2 -- twenty per cent
    # each way, so the homeless lose a job at 1.2 times the housed rate and find
    # one at 1/1.2 times it. The author's instruction of 1 September: "make the
    # increased risk of being unemployed if you are homeless exogenous like it
    # was before. I think 20% each direction."
    #
    # It was opened to own emp_homeless and could not carry it. The reason is in
    # the note on smallest_rental above: the street is a taste margin in this
    # model, so a labour market penalty on it deters the employed from choosing
    # it rather than holding them there, and the instrument is spent on the level
    # of homelessness instead of its composition.
    #
    # It is not deleted from the vector. It stays handed in explicitly at 0.2 so
    # that every point records the value it ran, rather than inheriting a default
    # that could drift.
    # THE ENDOWMENT OF THE YOUNGEST IS A CALIBRATED PARAMETER NOW, on the
    # author's instruction of 1 September: "so we have one more target
    # now....the endowmenets of the youngest. and the rest is just given to the
    # government."
    #
    # It owns h_share1, the share of the homeless aged 25 to 34, and h_share1 is
    # the moment that has held this calibration open longest: 0.91 against 0.26
    # in the HUD count, moved by at most two points by any of the four
    # instruments tried against it. The reason it would not move is now measured
    # rather than guessed. Age 26 enters with wealth 0.00000 and is homeless at
    # 16.2 per cent; age 27 holds 0.229 and is homeless at 1.1 per cent, on
    # LOWER income, 0.255 against 0.289. The gap between the two ages is a
    # year's saving, not a year's earnings, so what separates them is liquidity
    # and the only instrument that acts on liquidity at birth is the endowment.
    #
    # THE LEVEL AND THE SHAPE SEPARATE CLEANLY, which is why this is not a
    # duplicate driver on size_homelessness. size_homelessness sets how much
    # homelessness there is, at every age; newborn_endowment_scale sets how much
    # of it sits in the first band. h_1 and h_share1 are the two moments and
    # these are the two instruments.
    #
    # The justification for the paper is the author's: the endowment is what
    # matches the homelessness rate of the young, and in the data a good part of
    # young households' wealth is family support that no survey observes, so the
    # SCF's own newborn distribution is a floor rather than the number.
    # UN-PARKED, 3 September. The author: *"I think we can now bring back the
    # wealth for the newborns to make their share of the homeless correct. We
    # should calibrate it"*. It replaces the note that stood here, which recorded
    # their instruction of 2 September to leave newborns untargeted while w_bot
    # was being chased.
    #
    # What changed is the size of the job. On the seventeen-node grid h_share1
    # sat at +121 per cent and the endowment had to do violence to reach it. On
    # the seven-node grid it is +24 -- 0.3223 against 0.26 -- so a small
    # endowment should do, and the w_bot cost that caused the parking is
    # correspondingly smaller.
    #
    # THE TENSION HAS NOT GONE AWAY, and it should be watched rather than
    # assumed harmless: the endowment raises w_bot, and w_bot is +16.9 per cent
    # at the point this was decided from, already above its target. If the two
    # cannot both be met, that is a real conflict between the newborn wealth
    # distribution and the bottom-half wealth share, not a search failure.
    # rho_d is the earnings penalty of a substance use disorder, switched on
    # here for the first time. It owns the SUD share of the homeless, and
    # through it the age profile: lambda_d pins the NUMBER of addicts, so the
    # only way to put more older households on the street is to make the
    # disorder impoverishing rather than more common. SMI cannot do that job --
    # its onset shape falls from 1.000 at 26 to 0.154 at 66 -- and the SUD stock
    # accumulates with age where onset does not.
    # rho_d IS HELD AT ONE and is not calibrated; see run_one_point.sh.
}
BOUNDS = {
    'utility_cost_of_treatment':                            (0.0, 8.0),
    'probability_becoming_unemployed':                     (1e-6, 0.500),
    # THE FLOOR EXCLUDED THE SOLUTION and was found by measurement, 2 September.
    # theta falls monotonically in this parameter and the target, 0.162, is
    # bracketed by two points that differ in nothing else:
    #
    #     rsa1 0.463  ->  theta 0.3050   (+88%)   point de322e4659
    #     rsa1 0.300  ->  theta 0.0585   (-64%)   point 729d412392
    #
    # so theta=0.162 sits near rsa1 0.36-0.38 -- BELOW the old floor of 0.40.
    # The gate could propose only the upper half of the bracket and could never
    # reach the target, however many rounds it ran. The Fortran clamp was never
    # the constraint: theta_lo is 0.05 and theta_hi 0.70.
    #
    # The new floor is 0.25 and not lower because rsa1=0.200 returned theta as
    # the -1 empty-population sentinel (point 460811e3cb, on an older source).
    # That defect is unresolved, so the floor keeps a margin above it rather
    # than opening the search into a region that produces sentinels.
    'relative_share_of_addiction_1':                       (0.25, 0.60),
    'mu_homeless':                                         (0.05, 1.0),
    'lambda_m':                                            (0.046, 0.500),
    'smi_onset_level':                                     (1e-5, 0.5),
    'value_of_life':                                       (1.0, 500.0),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    'probability_of_voucher_benchmark_used':               (0.0001, 0.999),
    # The Fortran's floor moved off the ratio and onto the street itself, so the
    # ratio may now go far below 0.01. Its lower bound here follows: at a rung of
    # 1.5 a street of 0.0005 is a ratio of 0.00033, and the old bound would have
    # clamped it back to thirty times that.
    'size_homelessness':                                   (1e-6, 5.0),
    'smallest_rental_relative_to_lowest_income':            (0.005, 0.40),
    # The bottom node's level, as a multiple of mean productivity. The quantile
    # construction puts it at 0.0302 unaided; the floor is well below that and
    # the ceiling is node two, since the grid must stay monotone.
    'bottom_productivity_level':                            (0.004, 0.064),
    'weight_on_child':                                     (0.0005, 0.20),
    # In units of average labour income, so 1.0 hands every newborn a year of
    # it. The upper end is deliberately generous: nothing yet says where the
    # response to newborn wealth saturates, and the one thing measured -- age 27
    # holds 0.229, which is 0.85 of a year's average income, and is barely
    # homeless -- points at the middle of this range rather than the bottom.
    'newborn_endowment_scale':                             (0.0, 3.0),
    'largest_house_size':                                  (0.02, 1.00),
    'kappa_uem':                                           (1.0, 100.0),
    'max_food_cost':                                       (1e-4, 1.0),
    # A REAL SEARCH RANGE NOW: nothing calibrates this inside a point run.
    # THE CEILING EXCLUDED THE SOLUTION, found 2 September, the same fault as
    # relative_share_of_addiction_1's floor. beta needs a discount factor ABOVE
    # ONE and the gate could not propose one, so it could never close beta
    # however many rounds it ran. Measured today, three points, one coordinate:
    #
    #     1.00200 -> beta 2.7287     point eca09faa90
    #     1.00500 -> beta 3.1277     point b8d36c0646   INSIDE the 3.0-4.5 band
    #     1.01500 -> beta 4.3665
    #
    # and w_bot sat at 0.0250/0.0251/0.0250 across all three, so the instrument
    # is near-orthogonal to the other moment it could have disturbed.
    #
    # ABOVE ONE IS ADMISSIBLE HERE and is not a modelling error: the lifetime
    # utility is a FINITE sum over life_span=60 periods solved by backward
    # induction, with no fixed point that a discount factor above one could stop
    # from converging. The author made exactly this point. The Fortran clamp has
    # always been [0.5, 1.05]; only this line was narrower.
    'discount_factor':                                     (0.90, 1.02),
    'relative_share_of_leisure':                           (0.5, 12.0),
    'labor_income_tax_rate':                               (0.30, 0.95),
    'sd_permanent_productivity':                           (0.60, 1.30),
    # The KKK grid's dispersion instrument. 1.0 is the published GKOS sds and
    # about 2.2 is what puts the bottom half's share on the SCF's 17.2 per cent,
    # so the bracket is opened well either side of that.
    'kkk_sigma_scale':                                     (0.80, 4.00),
    'discount_factor_impatient':                           (0.50, 0.995),
    # Standardised mortality ratios for opioid use disorder run 6 to 10 in the
    # literature and 8 was the assigned midpoint. The author has authorised 4 as
    # a floor if it is needed, so the bracket is opened to it rather than to the
    # literature edge.
    'kappa_phi_d_level':                                   (4.0, 10.0),
    'relative_share_of_housing':                           (0.02, 0.60),
    # Zero is no penalty at all; the ceiling is well past the 3.8 the steady
    # state formula asks for, so the bracket is not clipped before it gets there.
    'increased_prob_if_homeless':                          (0.0, 20.0),
    # One is no penalty; the floor is 0.05 rather than zero because zero
    # earnings for every addict is a corner and not a calibration.
}
# beta is banded on the author's instruction; h_3 is conceded.
BAND = {'beta': (3.0, 4.5)}   # lower edge follows wealth_to_output_data, back to 3.0 on 2 Sep
# h_3 IS CONCEDED, h_2 IS NOT. The two swapped on 31 August: "no h2 has to be
# close to 10.1%, but h3 can be off".
#
# It is the right way round. h_2 is the share of households paying more than
# half of TOTAL EXPENDITURE on housing, 10.1 per cent in the CEX -- a fact about
# the world, on the same denominator as gamma. h_3 is the share sitting in the
# largest unit the model offers, which is a fact about a grid the model chose
# rather than about the world, and its only instrument
# (smallest_rental_relative_to_lowest_income) moves it at -0.01, which is to say
# it has no instrument at all.
SKIP = {'h_3',
        # W_BOT FOLLOWS THE SECOND DISCOUNT FACTOR OUT, and this is a
        # CONSEQUENCE of the author's instruction of 1 September to go back to
        # one type rather than a separate decision -- it is one line to reverse.
        # W_BOT IS SCORED AGAIN. The impatient type is back, on the author's
        # instruction of 2 September, and it owns this moment. The reason it was
        # unscored -- "with one type nothing moves it" -- expired with that
        # decision.
        #
        # The other objection recorded here stands and the author should keep it
        # in view: the 2.5 per cent is the SCF bottom-half share of NET WORTH,
        # which is mostly home equity for those households, and
        # include_homeownership is 0, so everyone in this model rents and the
        # only asset is financial saving. The target may be measuring something
        # the model does not have. It is scored because it is the moment blocking
        # emp_homeless, not because the mapping is clean.
        }

# H_2 IS NOT CONCEDED AND MUST NOT BE PUT BACK IN SKIP. I conceded it on
# 1 September on a misreading and the author caught it.
#
# THE NAME MEANS TWO DIFFERENT THINGS. The MOMENT h_2 in this file and in the
# Fortran is "above half of spending", the CEX severe cost burden headcount with
# a target of 0.101. The PARAMETER the author calls h_2 is the cheapest rental
# rung, which in the code is smallest_rental_relative_to_lowest_income.
#
# Their instruction -- "h_2 should essentially be chosen to match the rent50
# target (that is the same as the smallest rental relative to lowest income)" --
# is about the PARAMETER: the cheapest rung is chosen to match rent50, which is
# the OWN mapping that already existed. I applied it to the MOMENT and dropped
# it, contradicting what they had said on 31 August in as many words: "no h2 has
# to be close to 10.1%, but h3 can be off."
#
# The moment reads -18.2 per cent at the best point, among the closest in the
# table. Conceding it threw away something nearly won.

# MOMENTS WITH AN INSTRUMENT THAT DO NOT GATE THE STOPPING RULE.
#
# Not the same thing as SKIP. h_3 is CONCEDED -- the author agreed it can be off
# and nothing is trying to hit it. These two are being actively driven, by
# increased_prob_if_homeless and rho_d, and are simply not what the loop stops
# on: the author chose to score the homelessness age profile itself rather than
# its proximate causes, so h_age1..h_age5 are in the minimax and these are the
# diagnostics that say WHY the profile moved.
#
# Keeping them out of the minimax also stops the loop being held open by a
# moment whose target the model may not be able to reach at all. The employed
# share needs increased_prob_if_homeless near 3.8 against an assigned 0.2, and
# what that does to h_1, pi_eu and the drug block is not yet measured.
# emp_homeless IS SCORED AGAIN, on the author's answer to D3, 1 September. The
# question put to them was whether to push the cheapest rent until the unemployed
# are priced out, accepting what that does to rent50 and gamma, or to leave the
# employed share of the homeless as a reported output. The answer -- "you'll need
# to adjust both to match the data" -- is that rent50 and gamma both stay on
# their own targets while the affordability channel is pushed, rather than being
# allowed to drift as the price of it.
#
# WHAT THAT COSTS TO BELIEVE, stated because the archive argues with it. The
# moment's owner is increased_prob_if_homeless and the one point that ever moved
# it -- 3.8, nineteen times the assigned 0.2 -- made the employed share WORSE,
# 0.961 against 0.46. That parameter changes what happens after a household is
# homeless, not who becomes homeless, and the composition is decided in the
# housing choice: 99 per cent of the model's homeless are homeless by choice.
#
# Two other things do move it, both measured today. The newborn transfer took it
# 0.956 to 0.785 across the sweep, by removing the youngest -- who are almost all
# employed -- from the street. And the affordability channel is the author's own
# instrument for it. So the moment is scored with three things acting on it and
# its nominal owner the weakest of the three, which is worth watching rather than
# pretending is clean.
# h_share1 LEFT THIS SET on 3 September; see the note beside
# newborn_endowment_scale above.
UNSCORED = {'rent50',
            # THE COST BURDEN HEADCOUNT LEAVES THE LOSS, because the author has
            # decided twice that the cheapest rung targets emp_homeless: "we
            # decided to set h2 such that 46% of the homeless are employed."
            #
            # This is forced, not a preference. The rung already HITS the cost
            # burden target where it sits -- 0.1098 against 0.101 at a rung of
            # 0.055, inside ten per cent -- and raising it to serve emp_homeless
            # takes the headcount to 0.5482 at a rung of 0.4, a gap of +443 per
            # cent. Scored, that gap dominates emp_homeless's +100 in a MINIMAX,
            # so the loss would reject every high-rung point and the rung could
            # never move. Keeping the moment in the loss makes the author's
            # instruction unexecutable.
            #
            # It stays parsed and printed with the unscored moments so the price
            # of the decision is visible in every table, and it can be restored
            # in one line if the author wants it back.
            # 'h_2' IS SCORED AGAIN, on the author's instruction of 2-3
            # September, now that the rung points at it once more. Left here
            # commented rather than deleted so the history is legible.
            # THE PROFILE IS SCORED THROUGH h_share1 ALONE, so the other four
            # shares and all five rates are reported and not scored. h_share1 is
            # the share of the homeless aged 25 to 34, 0.91 against 0.26; these
            # are how anyone sees WHERE the mass went when it moves.
            'h_age1', 'h_age2', 'h_age3', 'h_age4', 'h_age5',
            'h_share2', 'h_share3', 'h_share4', 'h_share5',
            # OUTPUTS, ON THE AUTHOR'S INSTRUCTION, and not orphans. The
            # unemployment rate of those with a substance use disorder and the
            # employment rate of the SMI population are not known well enough to
            # be worth pinning -- "we don't truly know what they are so we
            # calibrate them" -- so their parameters answer to the two
            # homelessness shares and these two are what comes out. Reported at
            # every point, never scored; a drift is information, not a miss.
            'kappa_ued', 'kappa_uem'}



FREE = ('lambda_addiction', 'addiction_scalar_1')
FREE_BOUNDS = {'lambda_addiction': (0.5, 20000.0), 'addiction_scalar_1': (1e-30, 1.0)}
# A step is compensated when its predicted drift in b exceeds this, and shrunk
# until the drift is no worse than MAX_DRIFT. Both come from the same finding:
# four of the nine instruments drag b and lambda_d with them -- value_of_life by
# -85 per cent, theta -74, pi_eu +44, kappa_ued +42 -- so moving them bare trades
# one wrong moment for two right ones.
COUPLED_AT = 0.10
# How closely a foreign slice must reproduce the base's own reading of a moment,
# at the base's own parameter value, before its bracket is trusted.
TRANSFER_TOL = 0.15
MAX_DRIFT = 0.20


def drug_jacobian(A, base_key=None):
    """d ln(b, lambda_d) / d ln(lambda_addiction, addiction_scalar_1), refit local.

    Comparable points only: identical in every coordinate except the two free
    ones. locus.py uses the same filter because four points once read b from
    0.138 to 0.283 at identical lambda and addiction_scalar_1, differing only in
    probability_becoming_unemployed.
    """
    import numpy as np
    groups = {}
    for tag, (v, m) in A.items():
        if 'b' not in m or 'lambda_d' not in m:
            continue
        b, d = m['b'][0], m['lambda_d'][0]
        lam = float(v.get('lambda_addiction', 0))
        if b <= 0 or d <= 0 or not (15.0 <= lam <= 19.0):
            continue
        key = tuple(sorted((k, x) for k, x in v.items() if k not in FREE))
        groups.setdefault(key, []).append((lam, float(v['addiction_scalar_1']), b, d))
    if not groups:
        return None, 0, True
    # PREFER THE SLICE THE BASE ACTUALLY SITS ON. Taking the largest group is
    # what made the first repair overshoot lambda_d by 2.84 times: the biggest
    # comparable set is the original lambda/addiction_scalar_1 surface, and the
    # base had since moved away from it in tau_u, h_1, mu_homeless and more, so
    # the Jacobian was measured on a different slice of the model from the one
    # it was applied to. b came back exactly -- its row is robust across slices
    # -- and lambda_d did not, which is the row whose addiction_scalar_1
    # elasticity has been seen anywhere between -9.7 and -85.
    own = groups.get(base_key) if base_key is not None else None
    if own is not None and len(own) >= 4:
        best, foreign = own, False
    else:
        best = max(groups.values(), key=len) if groups else []
        foreign = True
    if len(best) < 4:
        return None, len(best), True
    X = np.column_stack([np.ones(len(best)), [math.log(p[0]) for p in best],
                         [math.log(p[1]) for p in best]])
    rows = []
    for i in (2, 3):
        c, *_ = np.linalg.lstsq(X, np.array([math.log(p[i]) for p in best]), rcond=None)
        rows.append(c[1:])
    return np.array(rows), len(best), foreign


def coupling(A, param, base_v, base_m):
    """Per e-fold of this parameter, the log change it causes in b and lambda_d.

    Searched over ANY pair of archive points differing in this one coordinate,
    not only pairs anchored at the current base. The base moves every round --
    the gate re-opens on whichever point is best -- so a base-anchored search
    finds nothing the moment the base advances, which is exactly what happened
    the first time this was wired up: every arm came back uncoupled because the
    arms had been measured at the PREVIOUS base and the new one differed from
    them in five coordinates. Coupling is a property of the instrument, so the
    pair that measures it does not have to touch the base at all.

    The pair nearest the base in this coordinate wins, since these elasticities
    are strongly local.
    """
    best = None
    x_base = float(base_v[param]) if param in base_v else None
    items = list(A.items())
    for i in range(len(items)):
        ta, (va, ma) = items[i]
        for j in range(i + 1, len(items)):
            tb, (vb, mb) = items[j]
            if set(va) != set(vb):
                continue
            d = [k for k in va if va[k] != vb[k]]
            if d != [param]:
                continue
            if not all(k in mm for mm in (ma, mb) for k in ('b', 'lambda_d')):
                continue
            xa, xb = float(va[param]), float(vb[param])
            ya, yb = ma['b'][0], mb['b'][0]
            da, db = ma['lambda_d'][0], mb['lambda_d'][0]
            if min(xa, xb, ya, yb, da, db) <= 0 or abs(math.log(xb / xa)) < 1e-9:
                continue
            dx = math.log(xb / xa)
            cand = (math.log(yb / ya) / dx, math.log(db / da) / dx)
            dist = abs(math.log(xa / x_base)) if x_base else 0.0
            if best is None or dist < best[1]:
                best = (cand, dist)
    return best[0] if best else None



def bracket(A, param, moment, target, base_v):
    """The value of `param` that puts `moment` on target, from a straddling pair.

    GROUPED BY SLICE, NOT POOLED. Points are comparable only when they agree on
    every coordinate except this one, so they are grouped by the rest of the
    vector and a straddle is looked for INSIDE a group. Pooling across groups
    was the first version and it is wrong in a way that is easy to miss: it
    produced a bracket of [2.776, 2.776] for kappa_ued -- two points with the
    same parameter value and different moments, because they sat on different
    slices -- which interpolates to no move at all and looks like a result.

    The base's own slice is preferred; other slices are used only if it has no
    straddle, and then the nearest crossing wins. Degenerate pairs are rejected.
    """
    groups = {}
    for tag, (v, m) in A.items():
        if param not in v or moment not in m:
            continue
        x, y = float(v[param]), m[moment][0]
        if x <= 0 or y <= 0:
            continue
        key = tuple(sorted((k, val) for k, val in v.items() if k != param))
        groups.setdefault(key, []).append((x, y))
    # THE BASE'S OWN SLICE ONLY. A bracket is a LEVEL, not a slope, and levels
    # do not carry across slices. At 08:50 the fallback offered tau_u a bracket
    # of [0.1543, 0.1929] measured on an old slice, when this base's own points
    # put the crossing near 0.603 -- a factor of three and a half out, and it
    # would have read as an interpolation rather than the extrapolation it is.
    # A slope survives the move well enough to be worth damping and reusing; a
    # level does not, so with no straddle here we fall back to the Newton step.
    # A FOREIGN SLICE IS ADMISSIBLE ONLY IF IT IS SHOWN TO TRANSFER. A bracket is
    # a LEVEL, and levels do not carry across slices for free: at 08:50 the
    # fallback offered tau_u a bracket of [0.1543, 0.1929] from an old slice when
    # this base's own points put the crossing near 0.603, a factor of three and a
    # half out, dressed as an interpolation. But refusing every foreign slice is
    # too strict in the other direction -- the slice holding the good tau_u
    # bracket differs from the base in three coordinates and reads tau_u 0.32912
    # where the base reads 0.34177, which is 3.8 per cent and plainly the same
    # curve.
    #
    # So transferability is TESTED rather than assumed: a foreign slice qualifies
    # only if it contains a point at (near) the base's own value of this
    # parameter whose moment agrees with the base's to within TRANSFER_TOL. That
    # is a direct measurement of whether the two slices lie on the same curve for
    # this moment, which is exactly the question.
    base_key = tuple(sorted((k, val) for k, val in base_v.items() if k != param))
    x_base = float(base_v[param])
    y_base = None
    for tag, (v, m) in A.items():
        if tuple(sorted((k, val) for k, val in v.items() if k != param)) == base_key \
                and abs(float(v[param]) - x_base) < 1e-12 and moment in m:
            y_base = m[moment][0]
            break
    ordered = [groups[base_key]] if base_key in groups else []
    for k, g in groups.items():
        if k == base_key or y_base is None:
            continue
        # NOT A LOG RATIO HERE. x_base is this parameter's value at the base
        # point, and a parameter is allowed to sit at zero -- utility_cost_of_treatment
        # does -- so math.log(x / x_base) raises ZeroDivisionError and takes the
        # whole gate down with a traceback. It did, at 07:27 on 1 September, as
        # soon as an arm gave that parameter a second value. The group builder
        # above already drops every x <= 0, so only x_base can be zero, and the
        # `d` computation forty lines below was already guarded with
        # `if x_base > 0 else 0.0` -- this was the one site that was not.
        #
        # The absolute-or-relative form is identical to the log test whenever
        # x_base is positive, because |log(x/x_base)| < 1e-6 is |x - x_base| <
        # 1e-6 * x_base to first order, and it is well defined at zero.
        near = [y for x, y in g
                if abs(x - x_base) <= 1e-6 * max(abs(x_base), 1.0)]
        if near and abs(math.log(near[0] / y_base)) <= TRANSFER_TOL:
            ordered.append(g)
    for pts in ordered:
        pts = sorted(set(pts))
        best = None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (y0 - target) * (y1 - target) > 0:
                continue
            if abs(math.log(x1 / x0)) < 1e-9 or abs(math.log(y1 / y0)) < 1e-9:
                continue
            f = (math.log(target) - math.log(y0)) / (math.log(y1) - math.log(y0))
            x = x0 * math.exp(f * math.log(x1 / x0))
            d = abs(math.log(x / x_base)) if x_base > 0 else 0.0
            if best is None or d < best[1]:
                best = ((x, x0, x1), d)
        if best:
            return best[0]
    return None


# A NAME ADDED TO THE VECTOR AFTER POINTS WERE ALREADY MEASURED. Every point
# run before kappa_phi_d_level entered the handover solved at its declared 8.0,
# so filling it in is not a guess about those points: it is what they actually
# ran at. Without it the slice key -- which is built out of whatever names the
# VECTOR line happens to carry -- differs on a coordinate nobody moved, and the
# archive splits into a before and an after that can never bracket each other.
IMPLICIT = {'kappa_phi_d_level': '8.0'}


def vector(text):
    m = re.search(r'^\s*VECTOR (.*)$', text, re.M)
    if not m:
        return None
    v = dict(t.split('=', 1) for t in m.group(1).split() if '=' in t)
    for k, d in IMPLICIT.items():
        v.setdefault(k, d)
    return v


# h_2 NAMES TWO DIFFERENT STATISTICS IN THIS ARCHIVE, AND ONLY THE LABEL
# TELLS THEM APART. Until 30 August it was the share of housed households in
# the smallest rental unit, target 0.132065; from then it is the share paying
# more than half of income for housing, target 0.101. Every one of the 243
# points measured before the change carries the old one. Reading both as "h_2"
# would have the gate bracket a moment against points that measure something
# else entirely -- a straddle built out of two different quantities, which is
# exactly the class of error the bracket code already guards against across
# slices. The label is in the point file, so use it.
# A MOMENT WHOSE DEFINITION CHANGED IS NOT COMPARABLE WITH ITS OWN PAST.
#
# h_2 has had three definitions in a day -- the share in the smallest unit,
# then the share above half of INCOME, now the share above half of total
# SPENDING -- and gamma's object moved from rent over income to housing over
# expenditure at the same time. A point measured under an older definition
# carries a number under the same name, and mixing them silently is how a
# bracket walks away from a target it is already on. The label is what
# distinguishes them, so a stale label drops the moment and the point is simply
# re-measured when it is next asked for.
STALE_LABEL = {'h_2': ['smallest unit', 'above half of income'],
               # THE DENOMINATOR WENT BACK, so the stale label inverts with it.
               # gamma was "housing over expenditure" against 0.268, was moved to
               # "housing over income" against 0.202 this afternoon, and is back
               # to expenditure against 0.268 tonight -- because a Cobb-Douglas
               # weight IS the expenditure share, and because the ladder the
               # author wants puts every housed household above 0.202 of income,
               # making that target unreachable by construction.
               #
               # So it is the INCOME label that is stale now. Left as it was,
               # this entry would have dropped every NEW gamma row instead of
               # every old one, and gamma would have vanished from the scored set
               # without a word.
               'gamma': ['housing over income'],
}

# RESTORED after an over-wide edit deleted it on 1 September. The dict itself is
# EMPTY and should stay that way unless a target genuinely has to differ from
# what the model emits: pi_eu's entry was removed once the Fortran declared 0.139
# itself, because one number in two places is how they drift apart. The
# check below prints loudly if an entry ever disagrees with the model.
TARGET_OVERRIDE = {}
_override_checked = set()


def _check_override(name, emitted):
    """Warn once per name if an override disagrees with the model's own target."""
    if name in TARGET_OVERRIDE and name not in _override_checked:
        _override_checked.add(name)
        want = TARGET_OVERRIDE[name]
        if abs(emitted - want) > 1e-6 * max(abs(want), 1.0):
            print(f'  *** TARGET_OVERRIDE[{name!r}] is {want} but the model now '
                  f'emits {emitted}. The override is winning. If the model is '
                  f'right, delete the entry.')


def moments(text):
    out = {}
    for n, label, m, tg in re.findall(
            r'MOMENT (\S+)\s+(.*?)model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', text):
        if any(t in label for t in STALE_LABEL.get(n, ())):
            continue
        # gamma's row on a pre-change point is the income object and is dropped
        # by STALE_LABEL above. The expenditure object it should now be compared
        # against is already in those points as a DIAG line, so the row is
        # rebuilt from it rather than the point being wasted.
        _check_override(n, float(tg))
        out[n] = (float(m), TARGET_OVERRIDE.get(n, float(tg)))

    if 'gamma' not in out:
        r = re.search(r'DIAG aggregate housing / aggregate expenditure\s+=\s*([0-9.eE+-]+)', text)
        if r:
            out['gamma'] = (float(r.group(1)), 0.268)

    # THE AGE PROFILE IS SCORED, THROUGH ONE NUMBER AND NOT FIVE.
    #
    # The author's choice, and the reason for it: five bands in the minimax is
    # five constraints that no parameter owns, and the loop could never report
    # DONE while any of them was outside ten per cent -- band one was 736 per
    # cent out. One summary keeps the profile in the stopping rule without
    # making the rule a test the search cannot pass.
    #
    # THE SUMMARY IS THE SHARE, NOT THE RATE, and that matters. The rate in band
    # one confounds two things the model separates: how much homelessness there
    # is, which size_homelessness owns through h_1, and how it is spread across
    # ages, which nothing owns. The SHARE of the homeless who are 25 to 34 is
    # scale free -- it moves if and only if the composition moves -- so h_1 keeps
    # the level and h_share1 keeps the shape, with no double counting between
    # them. It reads about 0.91 against 0.26 in the HUD count.
    #
    # The other four shares and all five rates are parsed and reported, and sit
    # in UNSCORED. They are how anyone reads WHERE the mass went when h_share1
    # moves; they are simply not what the loop stops on.
    for n, m, ob in re.findall(
            r'UNTARGETED homelessness rate, band\s+(\d+)\s+model=\s*'
            r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', text):
        out['h_age' + n] = (float(m), float(ob))
    for n, m, ob in re.findall(
            r'UNTARGETED share of the homeless, band\s+(\d+)\s+model=\s*'
            r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', text):
        out['h_share' + n] = (float(m), float(ob))

    # AND THE TWO SHARES THE NEW INSTRUMENTS ANSWER TO. These are parsed so that
    # increased_prob_if_homeless and rho_d have a moment to bracket on, and they
    # are listed in UNSCORED so they do not gate the stopping rule: the author
    # chose to score the age profile itself and leave these as diagnostics.
    for pat, key in ((r'UNTARGETED employed share of the homeless\s+model=\s*'
                      r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', 'emp_homeless'),
                     (r'UNTARGETED SUD share of the homeless\s+model=\s*'
                      r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', 'sud_homeless'),
                     # THE COST BURDEN OVER INCOME, on the author's instruction of
                     # 1 September: "the cheapest rental has to be such that the
                     # right fraction of households spend over 50% of their income
                     # on it". That is THIS line and not h_2. The two are
                     # different objects and the model prints both: h_2 is over
                     # half of total EXPENDITURE, 0.0899 against 0.101, while this
                     # is over half of INCOME, 0.3625 against 0.175. Naming it
                     # rent50 so nothing can confuse it with h_2.
                     (r'UNTARGETED renters above 50 pct of income\s+model=\s*'
                      r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', 'rent50')):
        hit = re.search(pat, text)
        if hit:
            out[key] = (float(hit.group(1)), float(hit.group(2)))
    return out


def gap(name, pair):
    m, tg = pair
    if name in BAND:
        lo, hi = BAND[name]
        return 0.0 if lo <= m <= hi else min(abs(m / lo - 1), abs(m / hi - 1))
    if m <= 0 and tg > 0:
        return 1.0
    return abs(m / tg - 1)


# HASHES THAT ARE NUMERICALLY THE SAME MODEL.
#
# The stamp hashes the whole source, so a change that only renames a printed row
# produces a new hash without changing a single computed number. That happened
# when the income of drug users became MOMENT y_u: the diff is a comment, a
# parameter constant used only in that write statement, and the row's label.
# Points measured on 57a80a45e9 are therefore identical to what 6eeab9f2cc
# produces and it would be wasteful to discard them.
#
# ONLY ADD A HASH HERE AFTER READING THE DIFF AND CONFIRMING NOTHING THE MODEL
# COMPUTES CHANGED. This list is a claim about the source, not a convenience.
EQUIVALENT_MODELS = {
    # SAME ECONOMY, DIFFERENT SOURCE. Keyed by SEMANTIC hash now, so a comment
    # never appears here -- model_hash handles those.
    #
    # 31818f2e83  the current source
    # 1089e7258f  before gamma's printed object and target moved from the income
    #             denominator to the expenditure one. Nothing a household faces
    #             changed; only what is printed and what it is compared against.
    # ddde1a91e1  before the rental ladder's ratios became parameters. They
    #             DEFAULT to the 2.0 and 3.0 that were hard coded, so a point run
    #             without them is byte-for-byte the same economy.
    #
    # Both are behaviour-preserving, which is why forty points are admissible
    # across them rather than thrown away. gamma is the one row that differs, and
    # moments() reads it from the DIAG expenditure line for the older two.
    #
    # 0e0abddab7  the job finding rate became *(1-x) instead of /(1+x) on the
    #             author's instruction, so the street costs twenty per cent each
    #             way rather than twenty and sixteen and two thirds. MEASURED,
    #             not argued: the same vector was re-run under the new source in
    #             a scratch copy and compared moment by moment. The worst shift
    #             over twenty-three scored moments was kappa_ued at 0.12 per cent
    #             of its target; nineteen moved by less than 0.005 per cent, and
    #             emp_homeless -- the moment the change acts on -- went 0.96352
    #             to 0.96411. The homelessness rate did not move to five places.
    #
    # 3af48ddb51  the floor on the street moved off the RATIO and onto the street
    #             itself. At every parameter value any existing point used, the
    #             new clamp is a max() against a bound four orders of magnitude
    #             away and the rest is two write statements, so it cannot change
    #             a solve; it only opens territory none of them visited. Held
    #             here on that reading and CONFIRMED by re-running the same
    #             vector, the same way as above.
    #
    # 222bb7fd3f  rho_m went 0.55 -> 1 and gained a handover, measure_child_gap
    #             became a settable variable, and the Fortran picked up comments.
    #             All three are inert at the values every archived point ran:
    #             rho_m is raised to the power include_rho_m, which is zero, and
    #             the child gap defaults to off. MEASURED, not argued -- the same
    #             vector re-run under the new source shifts the worst of
    #             twenty-three moments by 0.129 per cent of its target, which is
    #             kappa_ued, the same moment and the same size as the two earlier
    #             equivalences.
    '222bb7fd3f': {'3af48ddb51', '0e0abddab7', '31818f2e83',
                   '1089e7258f', 'ddde1a91e1'},
    '3af48ddb51': {'0e0abddab7', '31818f2e83', '1089e7258f', 'ddde1a91e1'},
    '0e0abddab7': {'31818f2e83', '1089e7258f', 'ddde1a91e1'},
    '31818f2e83': {'1089e7258f', 'ddde1a91e1'},
}



def current_model_hash():
    """The md5 of the source the archive would be compared against."""
    src = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
    h = hashlib.md5(open(src, 'rb').read()).hexdigest()[:10]
    return h


def archive():
    """Only points measured on the CURRENT source.

    THE ARCHIVE SPANS MODELS NOW AND SCORING ACROSS THEM IS SILENTLY WRONG.
    The point tag is the md5 of the parameter vector alone, so a vector
    re-measured after a source change keeps its tag; nothing in the filename
    or the vector says which model produced it. run_one_point.sh writes a
    MODEL line for exactly this reason, and this is the consumer of it.

    A point with no MODEL line predates the stamp and belongs to an older
    source, so it is excluded rather than assumed current -- the whole point
    is to stop old elasticities being mixed into a new step. If that leaves
    too few points the caller says so; an empty batch is a better outcome
    than a batch aimed at a model that no longer exists.
    """
    # GROUP BY THE SEMANTIC HASH, not by an md5 of the whole file.
    #
    # A commit that changed ZERO non-comment lines invalidated forty points on
    # 1 September and took the loss from 162.8 per cent to "no scoreable point in
    # the current economy" -- because documentation had been written. model_hash
    # strips comments and blank lines and rebuilds the map from git history, so
    # old points whose stamp is a full-file hash are resolved exactly rather than
    # guessed at. EQUIVALENT_MODELS still applies, for revisions that differ in
    # code but are known to be the same economy.
    import model_hash as _mh
    _map = _mh.build_map()
    want = _mh.current()
    # EQUIVALENT_MODELS is keyed by SEMANTIC hash, so look it up with the
    # semantic hash. Keying the table one way and reading it the other admitted
    # exactly one point out of 260 and looked like a model change.
    ok = {want} | set(EQUIVALENT_MODELS.get(want, set()))

    # AND ONLY POINTS IN THE CURRENT ECONOMY, not merely the current source.
    #
    # number_of_beta_types is a RUNTIME value, so switching from two discount
    # factor types to one on 1 September changed the economy without changing
    # the model hash -- by design, so the archive stayed scoreable. But it also
    # meant the gate could pick a two-type point as its base and propose a step
    # carrying number_of_beta_types=2, walking the search straight back into the
    # economy the author had just abandoned. It nearly did: the best point on the
    # drug block at 20:50 was ca64c6b36b, a two-type point.
    #
    # The MODEL line cannot catch this because the source really is identical.
    # So the configuration is read from run_one_point.sh's own default -- one
    # number in one place, as ever -- and points that disagree with it are
    # skipped exactly as points from another source are.
    cfg = None
    try:
        rop = open(os.path.join(HERE, 'run_one_point.sh')).read()
        mm = re.search(r'\[number_of_beta_types\]=(\d+)', rop)
        if mm:
            cfg = mm.group(1)
    except OSError:
        pass

    out, skipped, wrong_cfg = {}, 0, 0
    for f in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        t = open(f).read()
        mh = re.search(r'^MODEL (\S*)', t, re.M)
        # resolve_for_point, not resolve -- see gaps.py and INERT_CHANGES.
        if not mh or _mh.resolve_for_point(mh.group(1), t, _map) not in ok:
            skipped += 1
            continue
        v, m = vector(t), moments(t)
        if cfg is not None and v.get('number_of_beta_types', cfg) != cfg:
            wrong_cfg += 1
            continue
        if v and 'b' in m and 'lambda_d' in m:
            out[os.path.basename(f)[6:-4]] = (v, m)
    if wrong_cfg:
        print(f'  {wrong_cfg} points skipped for running a different '
              f'number_of_beta_types than run_one_point.sh defaults to ({cfg})')
    if skipped:
        print('  %d of %d points are on a different model (%s) and were skipped'
              % (skipped, skipped + len(out), want), file=sys.stderr)
    return out


def elasticity(A, param, moment, near):
    """From archive pairs differing in ONE coordinate, the pair nearest `near`."""
    cand = []
    for a, (va, ma) in A.items():
        for b, (vb, mb) in A.items():
            if a >= b or set(va) != set(vb):
                continue
            d = [k for k in va if va[k] != vb[k]]
            if d != [param] or moment not in ma or moment not in mb:
                continue
            xa, xb = float(va[param]), float(vb[param])
            ya, yb = ma[moment][0], mb[moment][0]
            if min(xa, xb, ya, yb) <= 0 or abs(math.log(xb / xa)) < 1e-9:
                continue
            e = math.log(yb / ya) / math.log(xb / xa)
            if abs(e) < 1e-6:
                continue
            cand.append((e, abs(math.log(xb / xa))))
    if not cand:
        return None
    # THE MEDIAN OVER PAIRS, NOT THE NEAREST PAIR. Preferring the pair closest to
    # the base sounds right and is not: the nearest pair is usually the SMALLEST
    # step, which is the worst signal against the solver's own reproducibility
    # band, and one bad pair then sets the step for the whole round.
    #
    # lambda_m is the case that exposed it. Nine controlled pairs exist on that
    # parameter and eight give an elasticity between -0.65 and -1.01; one gives
    # -0.08, and that one was nearest the base, so the loop used it. On -0.08 the
    # parameter has to reach 0.035 against a floor of 0.046 and the moment is
    # unreachable -- which is what this file and two reports to the author said.
    # On the median of -0.77 it needs 0.051, comfortably inside the floor, and
    # the moment is fine. The pessimistic conclusion was an artefact of picking
    # one pair out of nine.
    #
    # A median needs no threshold, no weighting and no judgement about which pair
    # deserves trust, and it degrades gracefully: with one pair it is that pair,
    # with two it is their mean, and with nine it ignores the outlier.
    es = sorted(e for e, _ in cand)

    # A MEDIAN OVER ELASTICITIES OF BOTH SIGNS IS NOT AN ELASTICITY. The median
    # above is the right answer for a noisy monotone response; it is the wrong
    # answer, and a dangerous one, for a response that turns.
    #
    # emp_homeless in the cheapest rung is the case that forced this. The author
    # saw it before any of it was measured, 1 September: "If h2 is so large that
    # even the employed can't afford it, then the homeless would be even more of
    # the employed... No?" They are right, and it makes the response U shaped.
    # At a low rung nobody is priced out, the street is a taste margin and the
    # homeless are 92 per cent employed. Raising the rung prices out the lowest
    # income households first, who are disproportionately unemployed, so the
    # share falls. Raise it further and the employed cannot afford it either,
    # the priced-out group becomes a cross section of everyone, and the share
    # climbs back toward the population employment rate.
    #
    # Fit a log-linear slope across the turn and the two limbs cancel: the
    # median lands near zero and the instrument is declared dead at exactly the
    # value where it works best. Two instruments were already wrongly declared
    # dead on 1 September for a different reason, so this is the second way to
    # make the same mistake.
    #
    # When the pairs disagree in sign there is no slope to report. Say so, and
    # let the caller fall back on the best MEASURED point -- which is what
    # ENGINE.md asks for anyway: prefer a measured bracket to an elasticity.
    if es[0] < 0 < es[-1]:
        print(f'  {param} -> {moment}: measured slopes span both signs '
              f'({es[0]:+.3f} to {es[-1]:+.3f}), so the response turns and no '
              f'elasticity describes it. Pick the best measured point.')
        return None

    n = len(es)
    return es[n // 2] if n % 2 else 0.5 * (es[n // 2 - 1] + es[n // 2])



# WHICH PRODUCTIVITY PROCESS IS BEING CALIBRATED, and therefore which of the two
# dispersion instruments is live. Read from run_one_point.sh's own default,
# because that is what every new point inherits unless a line overrides it, so
# it IS the economy the search is stepping around.
#
# Only one of them may be in OWN at a time. sd_permanent_productivity builds the
# quantile grid and moves nothing under fixed_productivity=0; kkk_sigma_scale
# scales both innovation sds of KKK_process and moves nothing under
# fixed_productivity=1. Two instruments pointed at one moment is a conflict, and
# leaving the inert one mapped is worse than a conflict: the search would step a
# number that changes no moment and read the noise as a slope.
def _live_productivity_process():
    try:
        txt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'run_one_point.sh'), errors='replace').read()
    except OSError:
        return 1
    m = re.search(r'\[fixed_productivity\]=\s*(\d+)', txt)
    return int(m.group(1)) if m else 1


def _apply_process_mapping():
    if _live_productivity_process() == 0:
        OWN.pop('sd_permanent_productivity', None)
        OWN['kkk_sigma_scale'] = 'sigma_y'
    else:
        OWN.pop('kkk_sigma_scale', None)
        OWN.setdefault('sd_permanent_productivity', 'sigma_y')


def main():
    _apply_process_mapping()
    A = archive()
    if not A:
        print('no archive'); return 1

    # The gate: any point with BOTH b and lambda_d inside five per cent, best by
    # worst-gap over everything else.
    # THE GATE DOES NOT BIND BEFORE THE DRUG BLOCK'S OWN ROUND. The author,
    # 2 September: "i thought you could first fix the value of life and then get
    # b and lambda_d to match the drug use."
    #
    # That is the round order, and the gate was fighting it. b and lambda_d are
    # round 2's moments, but the gate demanded them inside five per cent before
    # it would admit ANY base, including in round 1 -- so an aleph step, which
    # moves b by -85 per cent and lambda_d by -91, left round 1 with nothing to
    # step from while it waited on a repair for a block round 2 exists to set.
    # The macro round was being held hostage to the round after it.
    #
    # So while the drug block's round is still HELD, the gate is advisory: a base
    # is admitted on the round's own moments and b and lambda_d are simply
    # reported. From the firing that opens their round onward the gate binds
    # exactly as before, because from then on a step really would be taken off a
    # drifted base.
    # open_stages is computed further down, after the base is chosen, so it
    # cannot be read here. Whether the drug round is open is decided from the
    # ARCHIVE instead: it opens once every moment in every earlier round is
    # inside BASE_TOL at some point, which is the same test the stage loop uses.
    # Which rounds are open, computed from the archive so it is available before
    # the base is chosen. The stage loop further down recomputes it against the
    # chosen base and prints it; this is the same test.
    _open_now = []
    for i, st in enumerate(STAGES):
        _open_now.append(i)
        if not any(all(q in mm and gap(q, mm[q]) <= BASE_TOL.get(q, ACCEPT)
                       for q in st) for _, mm in A.values()):
            break

    drug_round = next((i for i, st in enumerate(STAGES) if 'b' in st), None)
    drug_round_open = drug_round is None or drug_round == 0 or any(
        all(q in mm and gap(q, mm[q]) <= BASE_TOL.get(q, ACCEPT)
            for st in STAGES[:drug_round] for q in st)
        for _, mm in A.values())
    opened = any(all(g in m and gap(g, m[g]) <= GATE[g] for g in GATE)
                 for _, m in A.values())
    if not drug_round_open:
        tol = {}
        print('  the drug block\'s round is not open yet, so the gate is advisory: '
              'a base is admitted on the open round\'s own moments and b and '
              'lambda_d are reported, not required.')
    else:
        tol = BASE_TOL if opened else GATE
    through = []
    for tag, (v, m) in A.items():
        if all(g in m and gap(g, m[g]) <= tol[g] for g in tol):
            # THE BASE IS RANKED ON THE OPEN ROUND'S MOMENTS WHILE A ROUND IS
            # OPEN. The author, 2 September: "we need to get the first stage
            # done, then we move to the second stage."
            #
            # Ranking on ALL moments picked point_f74796c1ee, whose round-1 worst
            # is 327 per cent, over one at 94.5 -- because it looked better once
            # b and lambda_d were counted, and those belong to a round that has
            # not opened. Round 1 was then being stepped from a base chosen for
            # round 2's benefit.
            #
            # Everything outside the open rounds is still REPORTED and still in
            # the loss; it just does not decide which base the open round works
            # from. Once every round is open this is the old behaviour exactly.
            scope = {q for i in _open_now for q in STAGES[i]} if _open_now else None
            rest = {k: gap(k, p) for k, p in m.items()
                    if k not in SKIP and k not in UNSCORED
                    and (scope is None or k in scope)}
            if not rest:
                rest = {k: gap(k, p) for k, p in m.items()
                        if k not in SKIP and k not in UNSCORED}
            through.append((max(rest.values()), tag, v, m))
    if not through:
        best = min(((max(gap('b', m['b']), gap('lambda_d', m['lambda_d'])), tag)
                    for tag, (v, m) in A.items()))
        print(f'GATE CLOSED. Best on max(|b gap|,|lambda_d gap|) is {best[1]} at '
              f'{100*best[0]:.1f} per cent; the gate is {100*GATE["b"]:.0f}.')

        # THE DEADLOCK THIS BREAKS, found on 1 September after it had cost a
        # whole day. Gate shut meant "no correction batch emitted", and the
        # documented remedy was restore.py. But restore.py repairs the drug
        # block by refitting the two-by-two Jacobian FROM THE ARCHIVE, and the
        # archive held exactly one (lambda_addiction, addiction_scalar_1) pair
        # on the current model -- every point ever run had the same two values.
        # A one-point cloud has no Jacobian. So the gate stayed shut, restore.py
        # could not open it, and the loop emitted nothing, firing after firing,
        # while batches got built by hand instead.
        #
        # The escape is to emit the missing measurement rather than a step: four
        # points, each drug parameter moved alone off the best base. That both
        # closes b and gives the Jacobian its first local fit, after which the
        # ordinary machinery works.
        best_tag = best[1]
        bv = A[best_tag][0]
        pairs = {(pv.get('lambda_addiction'), pv.get('addiction_scalar_1'))
                 for pv, _ in A.values()}
        if len(pairs) < 3:
            print(f'  and the archive holds only {len(pairs)} distinct drug pair(s), '
                  f'so no local Jacobian can be fitted and restore.py cannot help.')
            lines = []
            for name in ('lambda_addiction', 'addiction_scalar_1'):
                x = float(bv[name])
                for f in (1.18, 0.85):
                    d = dict(bv); d[name] = f'{x*f:.6g}'
                    lines.append('bash code/run_one_point.sh ' +
                                 ' '.join(f'{k}={d[k]}' for k in sorted(d)))
            out = 'batch_drugfit.txt'
            with open(os.path.join(HERE, out), 'w') as fh:
                fh.write('\n'.join(lines) + '\n')
            print(f'  EMITTED {out}: the drug 2x2 off point_{best_tag}. '
                  f'Run it, then run the gate again.')
            return 0
        # THE SECOND FORM OF THE SAME DEADLOCK, found on 1 September a few hours
        # after the first. Once the drug 2x2 above had been run the archive held
        # more than three pairs, so this branch stopped emitting the 2x2 -- and
        # then fell straight through to "no correction batch emitted" again.
        # The gate was still shut, restore.py could now fit a Jacobian and step,
        # and nothing called it. Emitting nothing when a remedy exists is the
        # bug, not the caution.
        #
        # So call restore.py's own fit here and emit its step. It is emitted as
        # a BRACKET -- full, half and quarter -- because restore prints a
        # CAUTION whenever b is more than twenty-five per cent out, which is
        # exactly the case that reaches this branch, and a log-linear repair
        # that far from its verified band is a direction to be trusted rather
        # than a distance. Three points cost eighteen minutes and return a
        # measured step size instead of a guessed one.
        try:
            sys.path.insert(0, HERE)
            import importlib, math as _m
            import numpy as _np
            _r = importlib.import_module('restore')
            _t = open(os.path.join(HERE, 'points', f'point_{best_tag}.txt')).read()
            _v = _r.vec(_t)
            _b, _d = _r.mom(_t, 'b'), _r.mom(_t, 'lambda_d')
            _key = tuple(sorted((k, x) for k, x in _v.items() if k not in _r.FREE))
            (_cb, _cd), _n, _foreign = _r.drug_jacobian(_key)
            if _cb is None:
                raise RuntimeError('no comparable points')
            _A = _np.array([[_cb[1], _cb[2]], [_cd[1], _cd[2]]])
            _step = _np.linalg.solve(
                _A, _np.array([_m.log(_r.B_TARGET / _b), _m.log(_r.LD_TARGET / _d)]))
            if _foreign:
                _step = _step * 0.5
            lines = []
            for _f in (1.0, 0.5, 0.25):
                _nv = dict(_v)
                for _pname, _s in zip(_r.FREE, _step * _f):
                    _x0 = float(_v[_pname]); _lo, _hi = _r.BOUNDS[_pname]
                    _nv[_pname] = f'{max(_lo, min(_hi, _x0 * _m.exp(_s))):.7g}'
                lines.append('bash code/run_one_point.sh ' +
                             ' '.join(f'{k}={_nv[k]}' for k in sorted(_nv)))
            out = 'batch_drugfit.txt'
            with open(os.path.join(HERE, out), 'w') as fh:
                fh.write('\n'.join(lines) + '\n')
            print(f'  restore.py fits on {_n} points; EMITTED {out}: the full, half '
                  f'and quarter step off point_{best_tag}. Run it, then run the gate again.')
        except Exception as exc:
            print(f'  restore.py could not step ({exc}); no drug batch emitted.')

        # AND THE OTHER FOURTEEN MOMENTS GET WORKED WHILE THE GATE IS SHUT.
        #
        # This branch used to return here. The gate was closed for most of the
        # evening of 1 September, so every firing emitted a drug repair and
        # NOTHING ELSE, while cbar sat at -74 per cent, h_1 at -63, pi_V at +59
        # and eleven others waited for a gate that the repair alone was not
        # closing. The author asked to see progress and there was none to see,
        # because thirteen of the fleet's fourteen possible arms were never
        # emitted.
        #
        # The gate exists so that a STEP is not taken from a base whose drug
        # block has drifted, and that is right. But an ARM is a measurement, not
        # a step: moving cbar's instrument off a base with b forty five per cent
        # out still measures what cbar's instrument does to cbar. The archive
        # needs those elasticities whatever the gate says, and the compensation
        # machinery above is what turns them into steps later.
        #
        # So the arms are emitted as a bracket either side, which is what
        # ENGINE.md asks for anyway -- prefer a measured bracket to an elasticity
        # -- and they are emitted from the same base as the repair so the round
        # is internally consistent.
        # NEAR THE GATE, DO NOT SPREAD. The author's ordering, 1 September: "You
        # might need to first pin down lambda d and b and then adjust the rest."
        #
        # Emitting arms beside the repair was right when the gate was at 46 per
        # cent and might stay shut for hours -- the measurements were needed and
        # nothing else was using the fleet. It is wrong at 8.6 per cent, where
        # the gate is a round or two from opening and every worker spent on an
        # arm is a worker not spent closing it. The arms are also worth MORE
        # after the gate opens, because they are then measured off a base whose
        # drug block is pinned rather than one that will move under them.
        #
        # So inside four times the gate the round is the drug block alone.
        near = best[0] <= 4 * GATE['b']
        if near:
            print(f'  and the gate is within four times its threshold, so this '
                  f'round is the drug block ALONE. No arms: every worker spent '
                  f'on one is a worker not closing the gate, and an arm measured '
                  f'off an unpinned base has to be measured again.')
            return 0

        try:
            bv2 = A[best_tag][0]
            bm2 = A[best_tag][1]
            arms = []
            for param, mom in OWN.items():
                if param not in bv2 or mom in SKIP or mom in UNSCORED:
                    continue
                if mom not in bm2 or gap(mom, bm2[mom]) <= BASE_TOL.get(mom, 0.10):
                    continue
                x0 = float(bv2[param])
                lo, hi = BOUNDS.get(param, (x0 / 100, x0 * 100))
                for f in (0.65, 1.55):
                    x1 = max(lo, min(hi, x0 * f))
                    if abs(math.log(max(x1, 1e-300) / max(x0, 1e-300))) < 1e-4:
                        continue
                    d = dict(bv2); d[param] = f'{x1:.7g}'
                    # the street coordinate again: an arm on the rung must not
                    # drag the street, for the reason given where the steps are
                    # emitted below.
                    if param == 'smallest_rental_relative_to_lowest_income' and \
                            'size_homelessness' in d:
                        st = x0 * float(bv2['size_homelessness'])
                        rlo, rhi = BOUNDS['size_homelessness']
                        d['size_homelessness'] = f'{max(rlo, min(rhi, st / x1)):.7g}'
                    arms.append('bash code/run_one_point.sh ' +
                                ' '.join(f'{k}={d[k]}' for k in sorted(d)))
            if arms:
                with open(os.path.join(HERE, 'batch_arms.txt'), 'w') as fh:
                    fh.write('\n'.join(arms) + '\n')
                print(f'  EMITTED batch_arms.txt: {len(arms)} measurement arms off '
                      f'point_{best_tag}, a bracket either side of every out-of-target '
                      f'instrument. Run these WITH the drug repair, not after it.')
            return 0
        except Exception as exc:
            print(f'  arms could not be emitted ({exc}).')
            return 2

    through.sort()
    worst, tag, v, m = through[0]

    # THE AUTHOR'S STOPPING RULE, 30 August: "once we get below 10% for
    # everything we can stop". The concession moved from h_2 to h_3 on 31
    # August. h_3 is in SKIP, and beta scores zero inside its 3.0-4.5 band, so
    # `worst` here is
    # exactly the quantity that has to fall under ten per cent. When it does the
    # calibration is FINISHED and the loop must stop launching rather than keep
    # spending containers on a solved problem.
    if worst <= ACCEPT:
        print(f'DONE. point_{tag} meets the author\'s rule: every target inside '
              f'{100*ACCEPT:.0f} per cent except h_3, which is conceded.\n')
        gaps = sorted(((gap(k, p), k, p) for k, p in m.items()), reverse=True)
        for g, k, (mo, tg) in gaps:
            note = ('   <-- conceded' if k in SKIP else
                '   <-- driven, not scored' if k in UNSCORED else '')
            print(f'  {k:10s} {mo:11.5f} vs {tg:11.5f}  {100*(mo/tg-1):+7.1f}%{note}')
        print(f'\n  worst gap outside h_3: {100*worst:.1f} per cent')
        print('\n  STOP. Do not launch another round. Tell the author.')
        return 4
    print(f'GATE OPEN at point_{tag}: b {100*(m["b"][0]/m["b"][1]-1):+.1f}%, '
          f'lambda_d {100*(m["lambda_d"][0]/m["lambda_d"][1]-1):+.1f}%. '
          f'Worst remaining {100*worst:.0f} per cent.\n')

    base_key = tuple(sorted((k, x) for k, x in v.items() if k not in FREE))
    DJ, ndj, DJ_foreign = drug_jacobian(A, base_key)
    if DJ is not None:
        print(f'drug block refit on {ndj} comparable points, '
              f'condition {np.linalg.cond(DJ):.0f}'
              + ('  (borrowed slice, steps halved)' if DJ_foreign else '')  + '\n')
    # WHICH STAGES ARE OPEN. A stage opens when every moment in every earlier
    # stage is inside BASE_TOL, or when it has stalled for STAGE_PATIENCE
    # firings. Both cases are printed, so a stalled stage is visible.
    hist_path = os.path.join(HERE, '.stage_state')
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else {}
    open_stages, why = [], []
    for i, st in enumerate(STAGES):
        open_stages.append(i)
        worst_here = max((gap(q, m[q]) for q in st if q in m), default=0.0)
        satisfied = all(q in m and gap(q, m[q]) <= BASE_TOL.get(q, ACCEPT) for q in st)
        k = f'stage{i}'
        # A STAGE WHOSE MEMBERSHIP CHANGES GETS A FRESH PATIENCE COUNT. Stage 1
        # gained h_share1 on 2 September, and its stall had in any case been
        # counted over three firings in which the cheapest rung was frozen out of
        # the search by the elasticity guard -- so the stall measured a bug, not
        # the stage. Keying the record on the stage's contents resets it whenever
        # the author changes what a stage contains.
        sig = ','.join(st)
        rec = hist.get(k, {'best': worst_here, 'stale': 0, 'sig': sig, 'npts': -1})
        if rec.get('sig') != sig:
            rec = {'best': worst_here, 'stale': 0, 'sig': sig, 'npts': -1}
        rec['sig'] = sig
        # THE COUNTER COUNTS ROUNDS, NOT INVOCATIONS. It incremented on every
        # call, and this file is run many times inside one firing -- while
        # editing it, while checking the gate, while reporting -- so stage 1 was
        # marked STALLED within a minute of being created, having seen no new
        # points at all. A stage has only had its chance once new points have
        # LANDED, so the counter advances on the archive growing.
        # AND IT COUNTS POINTS THAT TESTED THIS ROUND, not points that happened
        # to land. Counting the whole archive marked round 1 STALLED at 01:31
        # while its own twelve points were still solving -- the counter had been
        # advanced by a ladder sweep, a fine rung sweep and a two-beta test, none
        # of which move a round-1 instrument. The round was declared stuck
        # without ever having been given a measurement, and round 2 opened behind
        # it, which is exactly the ordering the author asked to protect.
        #
        # A round has had its chance when a point lands carrying a DISTINCT value
        # of one of its own instruments. That is the measurement the round asked
        # for, and nothing else advances its patience.
        _mine = {q for q, mo in OWN.items() if mo in st}
        npts = len({tuple(sorted((q, vv.get(q)) for q in _mine))
                    for vv, _ in A.values()}) if _mine else len(A)
        if worst_here < rec['best'] - 1e-9:
            rec = {'best': worst_here, 'stale': 0, 'sig': sig, 'npts': npts}
        elif npts > rec.get('npts', -1):
            rec['stale'] = rec.get('stale', 0) + 1
            rec['npts'] = npts
        hist[k] = rec
        if satisfied:
            why.append(f'  ROUND {i+1} {st} SATISFIED, worst {100*worst_here:.1f}%')
            continue
        if rec['stale'] >= stage_patience(st):
            why.append(f'  ROUND {i+1} {st} STALLED at {100*worst_here:.1f}% for '
                       f'{rec["stale"]} of {stage_patience(st)} measurements -- '
                       f'opening the next anyway, and it '
                       f'stays in the loss')
            continue
        why.append(f'  ROUND {i+1} {st} OPEN and working, worst {100*worst_here:.1f}%')
        break
    # THE HISTORY OF THE OPENING, not just its current state. The author,
    # 2 September: "i want to see every step of the opening." A snapshot says
    # which stages are open now; it does not say WHEN each opened, what it added
    # at that moment, or how long the one before it took. That history is the
    # record of how the calibration was built and it was being thrown away every
    # firing.
    log_path = os.path.join(HERE, '.stage_log')
    slog = json.load(open(log_path)) if os.path.exists(log_path) else []
    seen = {e['stage'] for e in slog}
    inv0 = {}
    for _p, _mo in OWN.items():
        inv0.setdefault(_mo, []).append(_p)
    for i in open_stages:
        if i in seen:
            continue
        # b and lambda_d are owned by the drug pair through the GATE rather than
        # through OWN, so inv0 has nothing for them and stage 0 printed "(no
        # instrument)" -- which is false and is exactly the line the author is
        # reading to see what enters the calibration.
        # b and lambda_d are owned by the drug pair through the GATE rather than
        # through OWN, so inv0 has nothing for them. This used to be hard-coded
        # as "stage 0 is the drug gate", which was true until the author put the
        # macro block first on 2 September and then stage 0 reported the drug
        # pair as its instruments -- on the very line they are reading to see
        # what enters the calibration. Attach FREE to whichever stage holds b.
        added = [q for _mo in STAGES[i] for q in inv0.get(_mo, [])]
        if 'b' in STAGES[i] or 'lambda_d' in STAGES[i]:
            added = list(FREE) + added
        slog.append({'stage': i, 'at': time.strftime('%d %b %H:%M', time.gmtime()),
                     'moments': STAGES[i], 'added': added,
                     'reason': 'first' if i == 0 else
                               ('stalled' if any('STALLED' in x and f'stage {i-1} ' in x
                                                 for x in why) else 'satisfied'),
                     'points': len(A)})
    json.dump(slog, open(log_path, 'w'), indent=1)

    json.dump(hist, open(hist_path, 'w'), indent=1)
    print('HOW THE CALIBRATION WAS OPENED, step by step:')
    for e in slog:
        prev = 'the first round' if e['stage'] == 0 else \
               f"round {e['stage']} {e['reason']}"
        print(f"  {e['at']}  ROUND {e['stage']+1} opened ({prev}, {e['points']} points)")
        print(f"      moments  {', '.join(e['moments'])}")
        print(f"      ADDED    {', '.join(e['added']) if e['added'] else '(no instrument)'}")
    print()
    print('STAGES:'); [print(x) for x in why]
    live = {q for i in open_stages for q in STAGES[i]}

    # SHOW WHICH PARAMETERS ARE IN THE CALIBRATION AND WHICH ARE STILL HELD.
    # The author, 1 September: "you need to show me how to open the calibration
    # each time... i want to see what parameters you add to the calibration each
    # time." A list of moment NAMES does not answer that -- they asked about
    # parameters, and the mapping from one to the other is the thing they cannot
    # see from here.
    inv = {}
    for _p, _mo in OWN.items():
        inv.setdefault(_mo, []).append(_p)

    # A MOMENT CAN HAVE AN INSTRUMENT WITHOUT OWNING IT. The author, twice on
    # 2 September: "h2 is equivalent to smallest_rental_relative_to_lowest_income."
    #
    # OWN is one parameter to one moment because that is what a bracket needs --
    # the rung's owner slot holds emp_homeless, on the author's own assignment --
    # but printing "(no instrument)" beside h_2 says the cost burden headcount is
    # unreachable, and it is not: the rung IS its instrument and moves nothing
    # else. The row now names the rung and says which moment it is bracketed on,
    # so the display stops contradicting the model.
    ALSO_MOVES = {'h_2': 'smallest_rental_relative_to_lowest_income'}
    for _mo, _p in ALSO_MOVES.items():
        if _mo not in inv:
            inv[_mo] = [f'{_p} (bracketed on {OWN.get(_p, "?")})']
    print('\nWHAT IS IN THE CALIBRATION NOW:')
    for i, st in enumerate(STAGES):
        state = 'OPEN ' if i in open_stages else 'HELD '
        for _mo in st:
            ps = inv.get(_mo)
            gtxt = f'{100*gap(_mo, m[_mo]):+6.1f}%' if _mo in m else '    -  '
            if not ps:
                print(f'  {state} round {i+1}  {_mo:13} {gtxt}  (no instrument)')
            for _p in ps or []:
                print(f'  {state} round {i+1}  {_mo:13} {gtxt}  {_p} = {v.get(_p, "-")}')
    fixed = [f'{k}={v[k]}' for k in ('increased_prob_if_homeless', 'kappa_phi_d_level')
             if k in v]
    if fixed:
        print(f'  FIXED by the author, never calibrated: {", ".join(fixed)}')
    print()

    lines, skipped = [], []
    for param, mom in sorted(OWN.items(), key=lambda kv: -gap(kv[1], m[kv[1]]) if kv[1] in m else 0):
        if mom not in m or gap(mom, m[mom]) <= ACCEPT:
            continue
        # Only instruments owning a moment in an open stage may move; the rest
        # are held at the base. See STAGES.
        if mom not in live:
            skipped.append(f'{param} (owns {mom}): held, its stage is not open yet')
            continue
        # A BRACKET BEATS AN ELASTICITY. If two archive points on this
        # instrument straddle the target, interpolate between them instead of
        # stepping on a slope. tau_u is the case that forced this: its
        # elasticity has measured -0.92, -0.52, -0.86 and -3.28 at four places
        # on the same instrument, and the -0.86 step carried it from +34 per
        # cent past the target to -39. That overshoot is not a loss -- it
        # BRACKETS the target, and a log-interpolation between two measured
        # points that straddle it does not depend on the slope being right
        # anywhere.
        br = bracket(A, param, mom, m[mom][1], v)
        if br is not None:
            x1, lo_, hi_ = br
            x0 = float(v[param])
            lo, hi = BOUNDS[param]
            x1 = max(lo, min(hi, x1))
            step = math.log(x1 / x0)
            note = f'  bracket [{lo_:.4g}, {hi_:.4g}]'
            e = float('nan')
        else:
            e = elasticity(A, param, mom, v)
        if br is None and e is None:
            # A TURNING RESPONSE MUST BE EXPLORED, NOT DROPPED.
            #
            # The guard in elasticity() returns None when the measured slopes
            # span both signs, with the comment "pick the best measured point".
            # Nothing implemented that. This branch then treated None as "no
            # controlled pair" and SKIPPED the instrument -- so the cheapest rung
            # silently left the search the moment the guard fired, and three
            # rounds of stage 1 moved the street alone with the rung pinned at
            # 0.055 while the author had asked for the two together.
            #
            # The bracket path cannot rescue it either: it needs two archive
            # points STRADDLING the target, and emp_homeless has never once been
            # below 0.46, so there is nothing to interpolate between.
            #
            # When the response turns and nothing straddles, the honest move is
            # to EXPLORE: take the value of this instrument that produced the
            # best measured value of its moment, and bracket around it. That is
            # a search, not a step, and it is the only thing that can find the
            # far side of a turn.
            cand = [(gap(mom, mm[mom]), float(vv[param]))
                    for vv, mm in A.values()
                    if param in vv and mom in mm and gap(mom, mm[mom]) == gap(mom, mm[mom])]
            if not cand:
                skipped.append(f'{param} (owns {mom}): no controlled pair in the archive')
                continue
            xbest = min(cand)[1]
            lo, hi = BOUNDS.get(param, (xbest / 50, xbest * 50))

            # EXPLORE UPWARD WHERE THE AUTHOR HAS GIVEN A DIRECTION.
            #
            # "you need to move the cheapest rental up" -- 1 September, said
            # after seeing the first explore bracket go to 0.0275 and 0.11, half
            # and double around the base. Half is the direction already known to
            # fail: at a low rung nobody is priced out and the street is a pure
            # taste margin.
            #
            # A symmetric bracket is also wrong on its own terms here. "Around
            # the best measured value" picked 0.055 because the best emp_homeless
            # anywhere in the archive happens to sit at the benchmark rung, for
            # reasons that have nothing to do with the rung. Within the
            # CONTROLLED nine-point arm the best was 0.8204, at a rung of 0.30
            # with a street of 0.0005 -- five times the base and upward.
            #
            # So a parameter listed here is explored upward only. This encodes an
            # instruction, not a measurement, and it is written down as such.
            EXPLORE_UP = {'smallest_rental_relative_to_lowest_income'}
            steps = (2.0, 4.0, 8.0) if param in EXPLORE_UP else (0.5, 2.0)
            if param in EXPLORE_UP:
                xbest = max(xbest, float(v[param]))
            for fct in steps:
                x1 = max(lo, min(hi, xbest * fct))
                if abs(math.log(max(x1, 1e-300) / max(float(v[param]), 1e-300))) < 1e-4:
                    continue
                d = dict(v); d[param] = f'{x1:.7g}'
                if param == 'smallest_rental_relative_to_lowest_income' and \
                        'size_homelessness' in d:
                    st = float(v[param]) * float(v['size_homelessness'])
                    rlo, rhi = BOUNDS['size_homelessness']
                    d['size_homelessness'] = f'{max(rlo, min(rhi, st / x1)):.7g}'
                lines.append((f'EXPLORE {param}', mom, float(v[param]), x1,
                              float('nan'), 100 * (m[mom][0] / m[mom][1] - 1),
                              '  response turns; exploring around the best measured value',
                              'bash code/run_one_point.sh ' +
                              ' '.join(f'{k}={d[k]}' for k in sorted(d))))
            print(f'  {param} (owns {mom}): response turns and nothing straddles '
                  f'the target, so EXPLORING around {xbest:g}, its best measured '
                  f'value, instead of dropping it.')
            continue
        cur, tgt = m[mom]
        if br is None:
            # A MOMENT FROM AN EARLIER ROUND IS NUDGED, NOT STEPPED. The author,
            # 2 September: "in each subsequent stage, i want all the previous
            # stage's parameters to be adjusted slowly if needed if their model's
            # moments drift."
            #
            # An earlier round's moment is one the search has already brought
            # inside ten per cent. If a later round knocks it back out, the
            # instrument should recover it without undoing the round that is
            # currently being worked -- a full Newton step on aleph moves b by
            # -85 per cent, which is round 2 being wrecked to repair round 1.
            # A quarter step converges the two together instead of having them
            # chase each other across rounds.
            #
            # This generalises the aleph case, which was the first instance and
            # was hard-coded. The damping deepens the further back the moment
            # comes from: one round back is a quarter step, two is an eighth.
            _home = next((i for i, st in enumerate(STAGES) if mom in st), None)
            _work = _open_now[-1] if _open_now else 0
            back = 0 if _home is None else max(0, _work - _home)
            damp = DAMP * (1.0 if back == 0 else 0.25 ** min(back, 2))
            step = damp * math.log(tgt / cur) / e
            if back:
                note = (note + f'  earlier round ({_home+1}), nudged at '
                        f'{0.25 ** min(back, 2):.2g} step').lstrip()
            step = max(-MAX_EFOLD, min(MAX_EFOLD, step))
            x0 = float(v[param])
            lo, hi = BOUNDS[param]
            x1 = max(lo, min(hi, x0 * math.exp(step)))
            note = ''
        if abs(math.log(x1 / x0)) < 1e-4:
            skipped.append(f'{param} (owns {mom}): at a bound, cannot move')
            continue
        # COMPENSATE A COUPLED STEP INSTEAD OF EMITTING IT BARE. If this
        # instrument drags b, shrink the step until the predicted drift is
        # tolerable and fold in the lambda_addiction and addiction_scalar_1 that
        # cancel what is left. Bare, these arms trade one wrong moment for the
        # two that are finished.
        # A BRACKET STEP COUPLES JUST AS HARD AS A NEWTON STEP. The pi_eu
        # bracket asks for probability_becoming_unemployed 0.02277 -> 0.0081,
        # which at that instrument's measured coupling would roughly TRIPLE b.
        # Interpolation makes the step's effect on its OWN moment trustworthy;
        # it says nothing about what the step does to the drug block.
        cpl = coupling(A, param, v, m)
        if cpl and DJ is not None and abs(cpl[0] * step) > COUPLED_AT:
            shrink = min(1.0, abs(math.log(1 + MAX_DRIFT) / (cpl[0] * step)))
            step *= shrink
            x1 = max(lo, min(hi, x0 * math.exp(step)))
            fix = np.linalg.solve(DJ, np.array([-cpl[0] * step, -cpl[1] * step]))
            if DJ_foreign:
                fix = fix * 0.5
            note += f'  compensated, {shrink:.2f} of step, b drift {100*(math.exp(cpl[0]*step)-1):+.0f}%'
        else:
            fix = None
        nv = dict(v); nv[param] = f'{x1:.7g}'

        # THE FINAL ROUND HAS TO TURN ITS OWN MEASUREMENT ON. omega_c's moment is
        # a CHILD COUNTERFACTUAL -- the author, 2 September: "omega_c has a clear
        # target, but it's in a counterfactual" -- and it is computed only when
        # measure_child_gap is 1. The flag defaults to 0 because the
        # counterfactual costs a second solve and there is no reason to pay it in
        # the four rounds that come first. Without this line round 5 would emit
        # steps for weight_on_child against a moment that reads "not measured"
        # forever and the round could never close.
        if mom == 'omega_c':
            nv['measure_child_gap'] = '1'

        # THE SEARCH COORDINATE IS THE STREET, NOT THE RATIO.
        #
        # The author's assignment, 1 September: "H2 targets the fraction of
        # homeless employed and h1 the overall homelessness". Both of those are
        # SIZES in their head, and only one of them is a parameter. The street is
        # built at line 26238 as housing_size(0)*size_homelessness -- the rung
        # TIMES the ratio -- so the handed-in parameter is the ratio, and moving
        # the rung drags the street with it.
        #
        # That makes the two instruments the author assigned strongly coupled in
        # the wrong direction: stepping the rung to move emp_homeless also moves
        # the homelessness rate, and the arm on the ratio then has to undo it.
        # It also produced an arm whose six points made the street ABSOLUTELY
        # BETTER in five of them while the rung rose, which is the opposite of
        # what was asked for.
        #
        # So the rung's step holds the STREET fixed and rescales the ratio, and
        # the ratio's own step is read as a step in the street. After this the
        # two are as close to orthogonal as the model allows: the rung decides
        # who is priced out, the street decides how bad being priced out is.
        RUNG, RATIO = 'smallest_rental_relative_to_lowest_income', 'size_homelessness'
        if RUNG in nv and RATIO in nv:
            street0 = float(v[RUNG]) * float(v[RATIO])
            if param == RUNG:
                target_street = street0
            elif param == RATIO:
                target_street = street0 * (float(x1) / float(v[RATIO]))
            else:
                target_street = None
            if target_street is not None:
                rlo, rhi = BOUNDS[RATIO]
                r = target_street / float(nv[RUNG])
                nv[RATIO] = f'{max(rlo, min(rhi, r)):.7g}'

        if fix is not None:
            for q, z in zip(FREE, fix):
                y0 = float(v[q]); qlo, qhi = FREE_BOUNDS[q]
                nv[q] = f'{max(qlo, min(qhi, y0 * math.exp(z))):.7g}'
        lines.append((param, mom, x0, x1, e, 100 * (cur / tgt - 1), note,
                      'bash code/run_one_point.sh ' +
                      ' '.join(f'{k}={nv[k]}' for k in sorted(nv))))

    # A base whose drug block has drifted gets a repair line of its own, so the
    # arms and the restore run in the same round instead of alternating.
    drift = max(gap('b', m['b']), gap('lambda_d', m['lambda_d']))
    if drift > RESTORE_AT and DJ is not None:
        fix = np.linalg.solve(DJ, np.array([math.log(m['b'][1] / m['b'][0]),
                                            math.log(m['lambda_d'][1] / m['lambda_d'][0])]))
        if DJ_foreign:
            fix = fix * 0.5
        rv = dict(v)
        for q, z in zip(FREE, fix):
            y0 = float(v[q]); qlo, qhi = FREE_BOUNDS[q]
            rv[q] = f'{max(qlo, min(qhi, y0 * math.exp(z))):.7g}'
        lines.append(('RESTORE drug block', 'b, lambda_d', 0.0, 0.0, 0.0,
                      100 * drift, '  repairs the base itself',
                      'bash code/run_one_point.sh ' +
                      ' '.join(f'{k}={rv[k]}' for k in sorted(rv))))
    # A NARROW STAGE MUST NOT LEAVE THE FLEET IDLE.
    #
    # Staging is right and it has one cost: an open stage with two moments emits
    # one or two lines, and a dozen workers then sit through a twenty minute
    # round doing nothing. Stage 1 emitted exactly ONE line on 1 September.
    #
    # So when the open stage cannot fill a round, the NEXT stage's instruments
    # are bracketed as PRE-MEASUREMENTS. They are arms, not steps: each moves one
    # instrument off the same base and changes nothing about which stage is open
    # or what the loop will step next. The point is that when the next stage does
    # open, its brackets already exist and it can step immediately instead of
    # spending its first two firings measuring.
    #
    # This does not smuggle the ordering open. A pre-measurement can never become
    # the base -- the loop picks its base by worst-gap over the scored set, as
    # ever -- and the moments in an unopened stage stay unstepped.
    FLEET = 8
    if len(lines) < FLEET and open_stages and open_stages[-1] + 1 < len(STAGES):
        nxt = STAGES[open_stages[-1] + 1]
        pre = 0
        for param, mo in OWN.items():
            if mo not in nxt or param not in v or mo not in m:
                continue
            if gap(mo, m[mo]) <= ACCEPT:
                continue
            x0 = float(v[param]); plo, phi = BOUNDS.get(param, (x0 / 50, x0 * 50))
            for fct in (0.7, 1.4):
                x1 = max(plo, min(phi, x0 * fct))
                if abs(math.log(max(x1, 1e-300) / max(x0, 1e-300))) < 1e-4:
                    continue
                d = dict(v); d[param] = f'{x1:.7g}'
                lines.append((f'PRE {param}', mo, x0, x1, float('nan'),
                              100 * (m[mo][0] / m[mo][1] - 1),
                              '  pre-measurement for the next stage, not a step',
                              'bash code/run_one_point.sh ' +
                              ' '.join(f'{k}={d[k]}' for k in sorted(d))))
                pre += 1
                if len(lines) >= FLEET:
                    break
            if len(lines) >= FLEET:
                break
        if pre:
            print(f'  and {pre} PRE-MEASUREMENT arms for stage '
                  f'{open_stages[-1] + 1} {nxt}, so it can step the firing it '
                  f'opens instead of measuring first. These are arms, not steps.')

    # NEVER OVERWRITE A BATCH THAT IS STILL BEING CONSUMED. Workers read their
    # line out of this file and `git pull --rebase` between lines, so rewriting
    # it under them silently swaps the vectors on every line they have not
    # reached yet -- two bases mixed inside one batch, with nothing in the point
    # files to say so. This gate re-opens every firing and would have done
    # exactly that at 04:20, when it rewrote all nine arms from a new base while
    # six of the previous nine were still running. Each round gets its own file.
    # NEVER REUSE A NUMBER, even for a batch that has been deleted. The counter
    # used to take the first free slot, so deleting CORRECT_7 and _8 -- they held
    # an uncompensated step that would have tripled b -- freed the name and the
    # next round wrote a completely different CORRECT_7. Any worker still holding
    # that filename would silently run the wrong vectors. The high-water mark is
    # kept on disk so it survives deletions.
    mark = os.path.join(HERE, '.correct_seq')
    used = int(open(mark).read().strip()) if os.path.exists(mark) else 0
    for fn in os.listdir(HERE):
        mm = re.match(r'CORRECT_(\d+)\.txt$', fn)
        if mm:
            used = max(used, int(mm.group(1)))
    n = used + 1
    # AND DO NOT WRITE A ROUND THAT IS IDENTICAL TO THE LAST ONE. The gate
    # re-runs every half hour; while a round is still solving, nothing it reads
    # has changed, so it would otherwise deposit a byte-identical batch file
    # every firing and the numbering would stop meaning "round".
    body = '\n'.join(l[-1] for l in lines) + ('\n' if lines else '')
    prev = os.path.join(HERE, f'CORRECT_{n-1}.txt') if n > 1 else os.path.join(HERE, 'CORRECT.txt')
    if os.path.exists(prev) and open(prev).read() == body:
        print(f'identical to {os.path.basename(prev)}; nothing new to run.')
        return 3
    out = os.path.join(HERE, f'CORRECT_{n}.txt')
    with open(out, 'w') as fh:
        fh.write(body)
    with open(mark, 'w') as fh:
        fh.write(str(n))
    print(f'{len(lines)} correction arms written to {os.path.basename(out)}, '
          f'from point_{tag}, one coordinate each:\n')
    print(f'{"parameter":52s} {"moment":10s} {"gap":>7s} {"elast":>7s} {"from":>10s} {"to":>10s}')
    for p, mo, x0, x1, e, g, note, _ in lines:
        el = '  bracket' if e != e else f'{e:+7.2f}'
        print(f'{p:52s} {mo:10s} {g:+6.0f}% {el:>7s} {x0:10.5g} {x1:10.5g}{note}')
    for s in skipped:
        print(f'  skipped: {s}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
