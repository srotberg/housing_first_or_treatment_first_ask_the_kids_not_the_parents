"""THE AUTHOR'S ITERATIVE SOLVER, RUN AGAINST THE MODEL.

*"you have a distance function multiplied by an adjuster. so param = param +
adjuster*(model moment - data)... adjuster small enough so that the param does not
move more than 1-2% between iterations when it is 100% off"*, and *"you should
create this for every single parameter"* -- the author, 4 September.

It is the model's own method: the Fortran carries 78 adjusters and updates, for
instance, kkk_sigma_scale by its own adjuster times (model - data), clipped to
bounds. run_one_point.sh does not iterate that loop -- a point is a single
fixed-parameter solve -- so this drives it from outside, over the handover vector.

WHY IT IS WORTH RUNNING BESIDE NELDER-MEAD. Dimension does not enter. Every
instrument updates from ONE model solve, where a simplex spends twenty-two solves
before it can take a single step. Measured on Rosenbrock at 21 parameters, no
arrangement of Nelder-Mead worked at all (best 4.42 against a 1e-3 tolerance), and
the reason is curvature in high dimension -- which a fixed point does not care
about, because it never builds a simplex.

WHAT CAN GO WRONG, and it is the only thing to be afraid of: A WRONG SIGN RUNS
AWAY FROM THE ANSWER WHILE THE TRACE LOOKS BUSY. So no sign here is reasoned. Each
is a least-squares slope over a MEASURED RAY in the archive -- points identical
except in that one parameter -- and an instrument whose ray reverses inside the
sampled range gets NO RULE AND NO UPDATE, because a constant adjuster pushes the
wrong way on one side of a reversal. On 126 points that was five of eighteen.

THE STEP. With slope D = d(moment)/d(param) and gap g = model - data, the Newton
step is -g/D. That is taken as the DIRECTION and magnitude, then capped at the
author's band: at most ADJ of the parameter's own value when the moment is 100 per
cent off, and proportionally less as the gap closes. So the cap binds far away --
where a Newton step off a secant is not to be trusted anyway -- and releases near
the answer, where it is.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

ADJ = float(os.environ.get('FP_ADJ', '0.02'))   # the author's 1-2 per cent band
ITERS = int(os.environ.get('FP_ITERS', '100000'))   # continuously, per the author
# CONVERGED means every rulable moment inside this band, not "the solver got
# bored". The author, 4 September: *"it should just have a loop that keeps going
# until convergence"*.
TOL = float(os.environ.get('FP_TOL', '0.05'))
# A PARAMETER WHOSE MOMENT IS ALREADY INSIDE THIS BAND DOES NOT MOVE.
#
# The author, 4 September: *"if can stop updating parameters that are in the 10%
# band"*, after seeing that ten of twenty-one moments were DIVERGING and that the
# divergence was not their own instruments failing -- pi_eu's parameter moved one
# part in ten thousand while its moment moved 9.2 points, so 1518 times the change
# came from the other twenty parameters.
#
# Every iteration moves all twenty-one at once, so each moment is shoved by twenty
# steps that are not its own. Holding the ones already home removes them from the
# shoving without costing anything, because they have nothing left to do. It is
# re-checked every iteration, so a moment that drifts back out resumes moving.
FREEZE_BAND = float(os.environ.get('FP_FREEZE_BAND', '0.10'))
# HYSTERESIS: A HELD PARAMETER NEEDS THIS MUCH TO START MOVING AGAIN.
#
# The author, 4 September: *"maybe the right way is to push them into the rule
# when they pass 10%, and then only start updating them again when they leave
# 15%"*, and *"so it's not so much in and out"*.
#
# With one threshold in both directions the band is a revolving door. A moment at
# 9.9 per cent is held, the next solve puts it at 10.1 and it moves again, and a
# parameter that is essentially converged keeps injecting cross-effects into the
# ones that are not. It shows in the run: fp4 held 12 of 21 at iteration 1, then
# 9, 9, 8 -- parameters were leaving the band as fast as they entered.
#
# Two thresholds make the band STICKY. A moving parameter is held once its gap is
# inside FREEZE_BAND; a held parameter only starts moving again once its gap
# exceeds RELEASE_BAND. Nothing can change state twice inside that interval.
RELEASE_BAND = float(os.environ.get('FP_RELEASE_BAND', '0.15'))


def hold(rel, was_held):
    """Is this parameter held this iteration, given its gap and its last state?

    A moving parameter is held once |rel| is inside FREEZE_BAND. A held parameter
    stays held until |rel| exceeds RELEASE_BAND. Pulled out of the loop so that
    hold_test.py can drive it directly; the loop calls nothing else.
    """
    return abs(rel) <= (RELEASE_BAND if was_held else FREEZE_BAND)
STATE = os.path.join(HERE, 'fixed_point_state.json')
LOG = os.path.join(HERE, 'fixed_point.log')
TRACE = os.path.join(HERE, 'fixed_point_trace.txt')


def say(s):
    print(s, flush=True)
    with open(LOG, 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")}  {s}\n')


# HARD-DAMPED INSTRUMENTS. Three parameters cannot take the normal step, and the
# reasons are measured, not cautious:
#
#   addiction_scalar_1  a CLIFF. 0.0368 -> lambda_d 0.038198 and 0.04048 ->
#                       0.000223: a ten per cent rise collapses the moment 99.4 per
#                       cent. The same cliff killed the Newton attempt. A normal
#                       step crosses into the dead region, where the moment stops
#                       responding -- which LOOKS like convergence.
#   lambda_addiction    ray reverses and is nearly flat, and it pulls on a
#                       population nested inside addiction_scalar_1's.
#   rr_homeless_old_level  the densest ray we have, twelve points, and it reverses
#                       above the anchor. The ruling holds near the current value
#                       only.
# PER-PARAMETER ADJUSTERS, SIZED BY ARITHMETIC. The author, 4 September: *"make
# sure that the adjusters are well calibrated so that parameters move slowly but
# not too slowly"*.
#
# One flat rate cannot be right, because the parameters do not have to travel the
# same distance: kkk_sigma_scale needs 16 per cent of its value, pi_eu's instrument
# needs 88 per cent, bottom_productivity_level needs seven hundred. At a single
# rate the first oscillates and the last never arrives.
#
# code/size_adjusters.py computes each one as D / (30 * relgap), where D is the
# MEASURED distance from the ray's crossing -- the parameter value that puts the
# moment on target -- so every instrument aims to arrive in about thirty solves,
# an hour and a half at three minutes each. Capped at 0.15 because the formula
# blows up as a gap closes and that blow-up is spurious.
#
# AND CAPPED AT 0.10 IN THE ADJUSTER ITSELF, not by a separate ceiling. The author
# set the band -- *"you can adjust up to 5% when you are 100% off"*, then *"maybe
# even 10%"* -- and then removed the step cap: *"dont cap any of the parameters...
# just let them move freely"*. With no cap, an adjuster of 0.15 moves 15 per cent
# at a 100 per cent gap, above the band they named. Putting the band in the
# adjuster satisfies both: nothing is clipped at run time, and no parameter can
# move more than ten per cent of its value in one iteration.
# WARM-START SEEDS, for instruments whose archive value is exactly zero. See the
# block in main() that applies them for why zero is a trap rather than a value.
SEED = {'homeless_job_penalty_pp': 0.05,
        # 0.017625, FROM THE FLOW BALANCE, on the author's instruction: start the
        # base from something that implies a SUD rate of 41 per cent given the
        # recovery rate of 2.5 per cent.
        #
        # In the stationary two-state distribution onset*(1-s) = recovery*s, so
        # with s = 0.0368/0.089 = 0.41348 and probability_of_stopping_addiction =
        # 0.025 (line 4116 of the Fortran), onset = 0.025*0.41348/0.58652 =
        # 0.017625.
        #
        # AND 0.134 WAS THE WRONG NUMBER, seeded here first. NSDUH's 0.134 is the
        # share of light users who CARRY a disorder -- a prevalence, a stock --
        # while the base is a per-period ONSET, a flow. Seeding the stock would
        # have overshot the hazard by about eightfold.
        'addiction_onset_base': 0.017625}   # the author, 5 September: seed delta at 5 per cent

ADJUSTERS = {
    # THE AUTHOR'S MAXIMUM, 0.10. y_h is 119 per cent out and the parameter runs
    # 0 to 0.95 with a hard ceiling, so a 2 per cent default step from 0.2 would
    # need well over a hundred solves to cross its own range. Ten per cent
    # compounding crosses it in about sixteen.
    'increased_prob_if_homeless': 0.10,
    # A PROPORTIONAL STEP CANNOT LEAVE ZERO, so delta starts at 0.05 in the
    # seed vector rather than 0 and then moves by ten per cent of itself.
    'homeless_job_penalty_pp': 0.10,
    # M MOVES 50 PER CENT AT A 100 PER CENT GAP. The author, 5 September: *"i
    # think the M var has to be adjusted much more quickly than at 10%"*, then
    # *"i think M should adjust at 50% when it's at 100%"*.
    #
    # step = f * adjuster * min(1,|rel|) * |x|, and for this parameter f is 1.0:
    # sud_homeless sits at exactly 0.0000 against 0.217, so rel is -1.0 every
    # iteration, the sign NEVER flips and the damper never halves. (An earlier
    # note here said the scale was pinned at OSC_FLOOR -- wrong; the floor is
    # only reached by flipping.) So the adjuster IS the per-iteration fraction
    # at a 100 per cent gap, and the trace confirms it exactly: M moved 4.5046
    # -> 4.5947 -> 4.6866, x1.02000 each time, on the old 0.02 default.
    #
    # 0.50 therefore gives precisely what was asked: half its own value per
    # iteration while the gap is 100 per cent, scaling down with min(1,|rel|)
    # as the gap closes.
    'multiple_of_probabilities_of_employment_if_addicted': 0.50,
    'addiction_onset_base': 0.0100,
    'bottom_productivity_level': 0.1000,
    'discount_factor': 0.0680,
    'kappa_uem': 0.1000,
    'kkk_sigma_scale': 0.0500,
    'labor_income_tax_rate': 0.0500,
    'max_food_cost': 0.0100,
    'mu_homeless': 0.0370,
    'probability_becoming_unemployed': 0.0710,
    'probability_of_voucher_benchmark_used': 0.0428,
    'relative_share_of_addiction_1': 0.0020,
    'relative_share_of_housing': 0.1000,
    'relative_share_of_leisure': 0.0748,
    'rr_homeless_old_level': 0.1000,
    # RAISED TO THE AUTHOR'S MAXIMUM 4 September on their instruction, from
    # 0.0423. The delta = 0.25 seed put h_1 at -96 per cent and this is the
    # parameter that has to climb to recover it; at 0.0423 it moved four per cent
    # an iteration. The response steepens as it climbs -- the h_1 gap closed 0.35
    # points per iteration over the first three and 8.4 at the fifth -- so bigger
    # steps risk overshooting into the region where h_1 looks discontinuous. The
    # sign-flip damping halves the adjuster the first time that happens, which is
    # what makes the larger step safe to try.
    'size_homelessness': 0.10,
    'smallest_rental_relative_to_lowest_income': 0.0148,
    'smi_onset_level': 0.1000,
    'utility_cost_of_treatment': 0.0100,
    'value_of_life': 0.0285,
    # THE ADDICTION PAIR, RESIZED. Both were sized against the WRONG MOMENTS,
    # because the mapping was crossed until 4 September: addiction_scalar_1 was
    # damped to 0.005 on the strength of a "cliff" -- 0.0368 -> lambda_d 0.038198
    # and 0.04048 -> 0.000223 -- which was not a cliff but an instrument reaching
    # its moment through two links. Against its OWN moment, the participation
    # threshold C > (phi/theta) p b, there is no reason to think it pathological,
    # so it takes the ordinary rate until a ray measured on the corrected mapping
    # says otherwise.
    # addiction_scalar_1 IS A KNIFE EDGE AND NEEDS A TINY ADJUSTER. Measured over
    # 83 archive pairs differing ONLY in it: 0.01461 -> 0.01484, a 1.5 per cent
    # change, moves the drug share 0.128 -> 0.093, which is 27 per cent; 0.01447
    # -> 0.01477 moves it 34 per cent. The elasticity is about MINUS 21.
    #
    # It was raised to 0.05 earlier tonight in a batch of "crawling instruments",
    # which was wrong for this one: at that elasticity a single step moves the
    # drug share by roughly 100 per cent and the parameter oscillates across its
    # whole usable range every iteration. The author, 5 September: *"i adjusted
    # it very slowly in the past"*, *"it has to be chosen carefully"*.
    #
    # 0.002 gives about a 4 per cent move in the drug share per iteration at a
    # 100 per cent gap, which is a step the moment can actually be steered with.
    # THE DRUG BLOCK MOVES SLOWLY, on the author's instruction 5 September:
    # *"the adjusters should be moving these parameters very slowly"*. Each is
    # sized from its MEASURED elasticity so that it moves its own moment a few
    # per cent an iteration, not across the range.
    #
    #   parameter                       measured elasticity        adjuster
    #   addiction_scalar_1              -8.74 on b                 0.002 -> 1.7%
    #   relative_share_of_addiction_1  +13.17 on b                 0.002 -> 2.6%
    #   addiction_onset_base            about 1 on lambda_d        0.010 -> 1%
    #   lambda_addiction                acts through GE, unmeasured 0.010
    #
    # The history is why this is written down: addiction_scalar_1 went 0.02 ->
    # 0.05 in a batch of "crawling instruments", which at -21 (the elasticity
    # measured then, on b alone) moved the drug share 100 per cent a step; then
    # to 0.002, which crawled; then 0.005. Sizing by elasticity rather than by
    # how far a parameter has to travel is what settles it.
    'addiction_scalar_1': 0.0020,
    'lambda_addiction': 0.0100,
}
DEFAULT_ADJ = 0.02

# NO CAP ON ANY PARAMETER'S STEP. The author, 4 September: *"dont cap any of the
# parameters....i saw that you cap some of them"*.
#
# There was a hard ceiling here -- one to two per cent, then five, then ten -- and
# it is gone. The step is the adjuster times the gap, and nothing else limits it.
# bottom_productivity_level moves 15 per cent at its 104 per cent gap and
# rr_homeless_old_level 7.5 per cent at its 50, which is what their adjusters were
# sized to do.
#
# TWO THINGS STILL BOUND A STEP, and neither is a choice I made:
#
#   the bounds     a parameter outside NB.BOUNDS is rejected by run_one_point, so
#                  the step is clipped to the box. Only discount_factor is tight
#                  enough for this to bite on one step, at gaps above about 66 per
#                  cent.
#   the gap        clamp(relgap, -1, 1) means a moment 200 per cent off steps as
#                  though it were 100 per cent off. That is the author's own
#                  framing -- "does not move more than X when it is 100 per cent
#                  off" -- and it only touches emp_homeless, at 104 per cent.

# M IS NOT FROZEN. It was, on the strength of a ray showing its slope on
# sud_homeless at -1.2e-07 across the whole range 1 to 32 -- and that ray answers
# the wrong question, because a ray HOLDS EVERYTHING ELSE FIXED.
#
# The author, 4 September: *"you cant just raise M and not touch b"*, and *"if
# raising M lowers addiction, you just have to lower b so more want to be
# addicted"*.
#
# With b held, raising M only deters: the disorder rate collapses 34-fold between
# M=4 and M=5.66 and the SUD share of the homeless falls with it. With b FREE the
# pair is a different object -- M punishes addiction, lambda_d falls, b's rule
# fires and lowers b to restore participation, and the population that comes back
# is a poorer one. That joint move is what could put substance use disorder into
# homelessness, and no single-parameter ray can see it.
#
# This only became actionable once lambda_d's sign was corrected. While b moved
# the wrong way the pair could not have worked.
# M IS FIXED AT 4, on the author's instruction 5 September: *"first fix M=4 so
# that we are aligned with the data"*. Freezing it here removes it from the rule
# map, so sud_homeless has NO instrument -- which is the honest state, because M
# does not move it in either direction. Measured over 69 archive pairs differing
# ONLY in M: sud_homeless is 0.000010 at M=1, 0.000003 at M=4 and 0.000002 at
# M=32, while b collapses from 0.234 to 0.004 across the same range. M is a
# strong deterrent on the choice to use and no handle at all on who is homeless.
# bottom_productivity_level IS EXOGENOUS from 5 September, on the author's
# instruction: *"i think the bottom productivity should be set exogenously"*.
# It owned emp_homeless and never moved it -- the moment sat at +110 to +115 per
# cent on every point of the night. Under the author's scheme M takes
# emp_homeless instead, once M is shown to have grip in the new region.
# PARAMETERS WHOSE UPPER BOUND IS ENFORCED. Everything else is floored only.
# WHERE THE FORTRAN ITSELF CLAMPS, MIRRORED HERE. This is not a cap in the
# author's sense -- their standing rule is *"dont cap any of the parameters...
# just let them move freely"* and that still holds. It is the model's own hard
# bound copied out of the handover so the walk stops spending three-minute
# solves on coordinate values the Fortran has already thrown away.
#
# homeless_job_penalty_pp: `max(min(handover_value,1.d0),0.d0)` at line 36867,
# and the comment beside it says the useful range ends EARLIER still, at
# probability_becoming_employed, because
#
#     find_mult_homeless_1 = max(0, (p_find - delta)/p_find)
#
# floors the finding rate at exactly zero from there on and delta only raises
# separations after that.
#
# WHY THIS WAS ADDED, 5 September. Chasing y_h (0.442 against 0.191 observed)
# the walk took it 0.332 -> 1.146 in sixteen iterations, past its own BOUNDS
# ceiling of 0.60, logging "above its old ceiling" eight times without effect
# because the ceiling is advisory outside CAPPED. y_h moved 0.4417 -> 0.4461,
# the WRONG WAY, and emp_homeless FELL 0.0598 -> 0.0437 -- the instrument
# destroying the moment it is needed for. Everything above 1.0 was inert.
#
# THIS DOES NOT CONCEDE ANYTHING. y_h and emp_homeless are both still scored
# and both still open; which of them gives way is the author's call and is not
# taken here.
HARD_CLAMP = {'homeless_job_penalty_pp': 1.0}

CAPPED = {'relative_share_of_addiction_1',
          # THE STREET IS CAPPED AT A TENTH OF THE CHEAPEST RENTAL, the author,
          # 5 September: *"h1 can rise to 0.1 times h2"*. size_homelessness is
          # already the street's housing service as a multiple of housing_size(0),
          # the cheapest rental, so the cap is 0.1 on the parameter itself. It sat
          # at 0.167 when the cap was set, so the ceiling binds immediately and
          # the street comes DOWN to it.
          'size_homelessness'}

# theta AND lambda ARE HELD WHILE b AND THE BASE CONVERGE. The author,
# 5 September: *"i would suggest to keep theta fixed at 0.13 and lambda at 0.05
# until at least b and the base have converged"*. Moving four drug parameters at
# once produced a point where theta hit its ceiling, the drug population emptied
# and every drug moment read zero or the -1 sentinel. Two at a time instead.
FROZEN = {'multiple_of_probabilities_of_employment_if_addicted',
          'bottom_productivity_level',
          'relative_share_of_addiction_1',
          'lambda_addiction',
          # rr_homeless_old_level IS INERT AT homeless_death_risk_flat_in_age=2,
          # which run_one_point.sh now defaults to on the author's instruction of
          # 5 September. Setting 2 takes the branch
          # kappa_phi_h_by_age = 1 + increased_risk_of_death_homeless and never
          # reads rr_homeless_profile, so the level this parameter writes into the
          # tail of that profile is not read by anything.
          #
          # IT MUST BE FROZEN RATHER THAN LEFT ALONE. An instrument that cannot
          # reach its moment does not sit still, it runs -- that is written above
          # about bottom_productivity_level and it cost eight iterations there.
          # h_share5 therefore has NO INSTRUMENT at this setting, which is
          # acceptable because setting 2 puts band 5 homelessness at 3.9e-9
          # against a target of 7.7e-4: the old are simply not homeless here, and
          # no level of a bypassed profile changes that.
          'rr_homeless_old_level'}
# NOTHING IS FROZEN, 5 September. bottom_productivity_level is released on the
# author's confirmation that it owns emp_homeless: *"We are setting the lowest
# productivity such that 46% of the homeless are employed"*.
#
# IT WAS FROZEN AT 23:05 FOR A REASON, kept here so the next runaway is recognised
# rather than rediscovered: chasing emp_homeless it MORE THAN DOUBLED in eight
# iterations, 0.004967 to 0.010646, collapsing h_1 by 84 per cent and blowing
# h_share5 to +427 while the objective went 4.03 to 20.74. An instrument that
# cannot reach its moment does not sit still, it runs.
#
# What is different now: delta acts on separation only, which is the first change
# all night that moved emp_homeless without costing something else (0.9923 ->
# 0.9637 when the finding penalty came off). So emp_homeless may become reachable
# and the parameter may settle. If it doubles again, that is the same failure and
# it should go back in this set.

# DAMPING ON OSCILLATION: HALVE THE ADJUSTER OF A PARAMETER THAT KEEPS OVERSHOOTING.
#
# MEASURED, not guessed. Ten iterations of this solver with a flat adjuster put
# rr_homeless_old_level into a clean period-two limit cycle:
#
#     it 3   2.7102    gap +237%      it 7   2.6656    gap +609%
#     it 4   2.9813    gap  -99%      it 8   2.9322    gap  -73%
#     it 5   2.6853    gap +229%      it 9   2.7167    gap +182%
#     it 6   2.9538    gap  -98%      it 10  2.9884    gap  -80%
#
# Every step is exactly ten per cent of the value -- the adjuster's maximum, since
# |rel| is clipped at one -- and every step reverses the last. The parameter is not
# converging on anything; it is bouncing between 2.68 and 2.99 forever, and each
# bounce costs a three-minute model solve. theta, size_homelessness and
# probability_becoming_unemployed show the same flip more weakly.
#
# This is the textbook failure of an undamped fixed point, and the textbook remedy:
# when the residual CHANGES SIGN the step was too big, so halve that parameter's
# adjuster; when it holds its sign the step was productive, so relax back toward
# nominal. Per parameter, because the instability is per parameter -- kappa_uem
# holds one sign for ten iterations and must keep its full step.
#
# It cannot stall the solver: the floor is an eighth of nominal, so a parameter
# that oscillates all night still moves 1.25 per cent of its value each iteration
# in the direction the gap asks for, and OSC_UP restores it the moment the sign
# settles.
OSC_DOWN = 0.5      # on a sign flip
OSC_UP = 1.5        # on a sign that held
OSC_FLOOR = 0.125   # never below an eighth of the nominal adjuster
# The gap must fall by at least this fraction to count as progress worth
# relaxing for. Model noise is about 2e-6 relative, so this is far above it.
STALL_TOL = 0.02


def damp(scale, p, rel, last):
    """The multiplier on p's adjuster, from whether its residual flipped OR STALLED.

    A SIGN THAT HOLDS IS NOT THE SAME AS PROGRESS. The first version of this rule
    relaxed the damping on any iteration whose residual kept its sign, and that is
    wrong in the case that actually occurred: rr_homeless_old_level flipped once at
    iteration 7, was halved to the floor, and then held one sign at a gap of +600
    per cent for five iterations while the rule relaxed it 1.5x each time --
    0.125, 0.19, 0.28 -- so the steps GREW, 1.25 per cent to 4.22 per cent, and the
    objective went 3.41 to 48.0. The parameter was not converging, it was walking
    away in a straight line, and the rule read the straight line as success.

    So relaxation now requires the gap to have actually SHRUNK. Three cases:

        sign flipped          the step overshot           halve
        same sign, |rel| fell the step is working         relax toward nominal
        same sign, |rel| flat the parameter has no        leave it alone
                              traction on its own moment

    The third case is the one that matters. A parameter whose moment does not
    respond is not helped by a bigger step -- rr_homeless_old_level is measured
    INERT above 3.4, where the whole ladder from 3.4 to 30 moves every moment by
    less than 0.05 per cent -- and giving it one only walks it further into the
    dead region.
    """
    prev = last.get(p)
    f = scale.get(p, 1.0)
    if prev is None:
        scale[p] = f
        return f
    if prev * rel < 0.0:
        f = max(f * OSC_DOWN, OSC_FLOOR)
    elif abs(rel) < abs(prev) * (1.0 - STALL_TOL):
        f = min(f * OSC_UP, 1.0)
    scale[p] = f
    return f



def rules(NB):
    """The author's ruling per moment: which way the PARAMETER goes when the
    MODEL MOMENT IS ABOVE TARGET.

    The author, 4 September: *"you dont need the slope to determine the adjuster
    ....you can reason it out"*, and then ruled on all twenty-one moments one at a
    time. This is the authority. The measured rays remain a CHECK -- fifteen agree,
    and the disagreements are recorded in directions_table.py rather than resolved
    silently in favour of either side.
    """
    import directions_table as D
    out = {}
    for m, (p, rule, _) in D.RULES.items():
        if p in FROZEN or p not in NB.BOUNDS:
            continue
        # 'lower' means parameter and moment move together, so to close a positive
        # gap the parameter must fall: the step carries -gap. 'raise' is the
        # opposite sign.
        out[p] = (m, -1.0 if rule == 'lower' else 1.0)
    return out


def solve(vec):
    """One model solve through run_one_point.sh, which flocks. Returns its tag."""
    cmd = ['bash', 'code/run_one_point.sh'] + [f'{k}={vec[k]}' for k in sorted(vec)]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    mm = re.search(r'point ([0-9a-f]{10})', r.stdout or '')
    if not mm:
        mm = re.search(r'([0-9a-f]{10})', r.stdout or '')
    return mm.group(1) if mm else None


def solve_tag_of(A, v):
    """The archived tag whose vector matches v on every key it carries."""
    for t, (vv, _) in A.items():
        if all(str(vv.get(k)) == str(x) for k, x in v.items()):
            return t
    return None


def main():
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    A = N.archive()
    if not A:
        say('no points on the live economy; nothing to start from')
        return 1
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    R = rules(NB)
    say(f'{len(A)} points, {len(inst)} instruments, {len(R)} with a ruling')
    for p, (m, sgn) in sorted(R.items()):
        a = ADJUSTERS.get(p, DEFAULT_ADJ)
        say(f'   {p:<44} {m:<13} '
            f'{"above -> lower" if sgn < 0 else "above -> raise"}  adj {a:.4f}')
    for p in sorted(FROZEN):
        say(f'   {p:<44} FROZEN, its instrument cannot move its moment')

    # RESUME WHERE IT WAS, NOT FROM THE BEST POINT.
    #
    # The author, 4 September: *"you should allow my method to update all the time
    # continuously"*. A fixed point is NOT a descent method -- its iterates can get
    # transiently worse while walking toward the answer, because closing one gap
    # opens another before the next update closes that. Resuming from the archive's
    # best would therefore undo every step that had temporarily cost SSR, and a
    # restart would reset the walk rather than continue it.
    #
    # So the live vector is written every iteration and read back on restart. The
    # archive's best is only the cold start, for the first run on a new economy.
    start = 1
    if os.path.exists(STATE):
        try:
            st = json.load(open(STATE))
            v, start = dict(st['v']), int(st['it']) + 1
            scale = {k: float(x) for k, x in (st.get('scale') or {}).items()}
            last = {k: float(x) for k, x in (st.get('last') or {}).items()}
            was_held = set(st.get('held') or [])
            t = solve_tag_of(A, v)
            mom = A[t][1] if t else None
            if mom is None:
                v = None
            else:
                say(f'resuming at iteration {start} from {t}, '
                    f'SSR {NM.ssr(N, mom, keys):.4f}')
        except Exception as e:
            say(f'state unreadable ({e}); cold starting')
            v = None
    else:
        v = None
    if v is None:
        # WARM START FROM THE BEST CORE POINT, not the best on all twenty-one.
        #
        # The author, 4 September: *"you might want to use some of these to
        # warm-start my method"*, of the points Nelder-Mead had just found.
        #
        # Ranking on all twenty-one picks the wrong point. sud_homeless (-100 per
        # cent) and emp_homeless (+104) contribute about 2.08 to EVERY point's SSR
        # whatever the rest does, so they swamp the comparison: NM's best,
        # 5d0160c022, is fourth on all twenty-one at 3.6107 while being far the
        # best on the twelve that respond, at 0.1739. Starting from the all-21
        # winner would begin the walk from a worse vector on every moment an
        # adjuster can actually move.
        #
        # So the START is chosen on the core twelve and the WALK still optimises
        # all twenty-one. Nothing is dropped from the objective; only the choice
        # of where to begin stops being dominated by two moments no instrument
        # reaches.
        core, _ = NM.instruments_all(N, NB, 1)
        ck = [m for _, m in core]
        pool = [(NM.ssr(N, m, ck), t) for t, (vv, m) in A.items()
                if all(k in m for k in ck)]
        tag = min(pool)[1] if pool else N.best(A, keys)[1]
        v = dict(A[tag][0])
        mom = A[tag][1]
        start = 1
        # A PROPORTIONAL STEP CANNOT LEAVE ZERO. step = adjuster * gap * |x|, so a
        # parameter warm-started at exactly 0 stays at 0 however large its gap,
        # and it reads as a converged instrument rather than a pinned one. The
        # warm start comes from the best ARCHIVE point, so restarting the loop
        # puts it straight back to zero -- which is what happened to delta at
        # 03:00 after it had been seeded in the state file.
        # The author, 5 September: *"i think you should let my method continue to
        # work, and set delta=0.25 for the warm start"*.
        for _sp, _sv in SEED.items():
            if _sp in R and abs(float(v.get(_sp, 0.0))) < 1e-12:
                v[_sp] = _sv
                say(f'   seeded {_sp} at {_sv:g}; a proportional step '
                    f'cannot leave zero')
        say(f'warm start from {tag}: core SSR {NM.ssr(N, mom, ck):.4f}, '
            f'all-21 SSR {NM.ssr(N, mom, keys):.4f}')

    # A COLD START HAS NO HISTORY, so nothing is damped on the first iteration.
    try:
        scale, last
    except NameError:
        scale, last = {}, {}
    try:
        was_held
    except NameError:
        was_held = set()
    # ONE-SHOT OVERRIDE, APPLIED ON BOTH PATHS. `code/fixed_point_override.json`
    # lets the author put a parameter somewhere specific without editing this
    # file. It is applied here, after the warm-start AND resume branches have
    # joined, and then DELETED.
    #
    # IT WAS IN THE WARM-START BRANCH FIRST AND THAT WAS WRONG. The loop RESUMES
    # from fixed_point_state.json whenever the state is fresh, so the warm-start
    # block does not run at all on a restart -- which is why kappa_uem=40, M=20
    # and the delta seed of 0.05 all appeared to be applied at 03:22 and none of
    # them reached the vector. Anything that must take effect on a restart has to
    # live below this line, not above it.
    #
    # One-shot matters too: an override that survived would reset the parameter on
    # every restart and silently undo the walk.
    _ovp = os.path.join(ROOT, 'code', 'fixed_point_override.json')
    if os.path.exists(_ovp):
        try:
            _ov = json.load(open(_ovp))
            for _op, _oval in _ov.items():
                if _op in v:
                    say(f'   override {_op}: {v[_op]} -> {_oval} (one-shot)')
                    v[_op] = _oval
                else:
                    say(f'   override {_op} IGNORED: not in the vector')
        finally:
            os.remove(_ovp)
            say('   override file consumed and removed')

    for it in range(start, start + ITERS):
        moved, held, damped, now_held = [], [], [], set()
        for p, (m, sgn) in R.items():
            if m not in mom or not mom[m][1] or p not in v:
                continue
            model, target = mom[m]
            rel = (model - target) / target
            # STICKY: it takes FREEZE_BAND to get in and RELEASE_BAND to get out.
            if hold(rel, p in was_held):
                held.append(m)
                now_held.add(p)
                continue
            lo, hi = NB.BOUNDS[p]
            x = float(v[p])
            # THE AUTHOR'S BAND: ADJ of the parameter's own value when the moment
            # is 100 per cent off, proportionally less as the gap closes.
            f = damp(scale, p, rel, last)
            last[p] = rel
            if f < 1.0:
                damped.append(f'{m} x{f:.3g}')
            frac = (f * ADJUSTERS.get(p, DEFAULT_ADJ)
                    * max(-1.0, min(1.0, rel)))
            step = sgn * frac * max(abs(x), 1e-12)
            # FREE, FLOORED AT ZERO. The author, 4 September: *"just let them move
            # freely (unless you need to cap them at 0"*. NB.BOUNDS no longer clips
            # -- a parameter may leave the box it was given, and the log SAYS SO
            # rather than clipping silently, which is the failure that hides a
            # pinned parameter as a converged one. Zero stays because a negative
            # scale, hazard or price is not a value the model can read.
            # FLOORED AT THE LOWER BOUND, FREE ABOVE. The author, 4 September,
            # first *"just let them move freely (unless you need to cap them at
            # 0"*, then named two floors explicitly: 0.05 on the addiction hazard
            # and 1e-08 on b. So the FLOOR is enforced -- it is the "cap at 0"
            # generalised to whatever the author set -- and the ceiling is not,
            # which is where the freedom was wanted.
            # THE CEILING IS ENFORCED FOR CAPPED PARAMETERS ONLY. The author's
            # standing rule is *"dont cap any of the parameters... just let them
            # move freely"*, and the floor is the exception they named. theta is
            # a second exception they named explicitly on 5 September -- *"i
            # think theta should be capped at 0.2"*, *"and below at 0.08"* --
            # because a theta that ran to 0.48 is what made drugs half the
            # Cobb-Douglas weight and flooded the model with users.
            xn = max(x + step, lo)
            if p in HARD_CLAMP and xn > HARD_CLAMP[p]:
                say(f'   {p} held at the Fortran\'s own clamp {HARD_CLAMP[p]:g}')
                xn = HARD_CLAMP[p]
            if p in CAPPED and xn > hi:
                say(f'   {p} held at its ceiling {hi:g}')
                xn = hi
            if x + step < lo:
                say(f'   {p} held at its floor {lo:g}')
            if xn > hi:
                say(f'   {p} above its old ceiling {hi:g} at {xn:.8g}')
            if abs(xn - x) > 1e-12:
                v[p] = f'{xn:.8g}'
                moved.append((p, x, xn, 100.0 * rel))
        # THREE DIFFERENT ENDINGS, and they must not be reported as one.
        gaps = {m: abs(mom[m][0] / mom[m][1] - 1.0)
                for p_, (m, _) in R.items()
                if m in mom and mom[m][1]}
        worst_m = max(gaps, key=gaps.get) if gaps else None
        if gaps and gaps[worst_m] <= TOL:
            say(f'CONVERGED at iteration {it}: every rulable moment inside '
                f'{TOL:.0%}, worst {worst_m} at {100*gaps[worst_m]:.1f}%')
            return 0
        if not moved:
            # IT DOES NOT STOP. The author, 4 September: *"the loop should be such
            # that it wont stop iterating until all parameters converged"*.
            #
            # Nothing moved means every remaining gap belongs to a parameter
            # pinned on a bound, so the NEXT SOLVE WOULD BE BIT-IDENTICAL and
            # re-running it would burn three minutes to learn nothing. So it does
            # not solve -- it waits and re-reads the archive, because the thing
            # that unpins it comes from OUTSIDE this loop: the author widening a
            # bound, or Nelder-Mead finding a better point in the same archive.
            # Then it picks up and carries on.
            at_bound = [p_ for p_ in R
                        if p_ in v and float(v[p_]) in NB.BOUNDS[p_]]
            say(f'PINNED at iteration {it}: nothing can move, {worst_m} still '
                f'{100*gaps[worst_m]:.1f}% off; on a bound: '
                + (', '.join(sorted(at_bound)) or 'none')
                + '  -- waiting for a bound to widen, not stopping')
            time.sleep(300)
            A = N.archive()
            b = N.best(A, keys)
            if b and b[1] in A and NM.ssr(N, A[b[1]][1], keys) < NM.ssr(N, mom, keys):
                v, mom = dict(A[b[1]][0]), A[b[1]][1]
                say(f'picked up a better point from the archive: {b[1]}')
            continue
        worst = max(moved, key=lambda z: abs(z[3]))
        say(f'iteration {it}: {len(moved)} moved, {len(held)} held inside '
            f'{FREEZE_BAND:.0%}/{RELEASE_BAND:.0%}, worst gap {worst[3]:+.1f}% on {worst[0]}')
        if held:
            say('   held: ' + ', '.join(sorted(held)))
        freed = sorted(was_held - now_held)
        if freed:
            say(f'   released past {RELEASE_BAND:.0%}: ' + ', '.join(freed))
        was_held = now_held
        if damped:
            say('   damped for overshooting: ' + ', '.join(sorted(damped)))
        with open(TRACE, 'a') as f:
            f.write(json.dumps({'it': it, 'moved': moved}) + '\n')
        t = solve(v)
        if not t:
            say(f'iteration {it}: solve produced no point; stopping')
            return 1
        A = N.archive()
        if t not in A:
            say(f'iteration {it}: {t} not on the live economy; stopping')
            return 1
        mom = A[t][1]
        json.dump({'it': it, 'v': v, 'tag': t, 'scale': scale, 'last': last,
                   'held': sorted(was_held)}, open(STATE, 'w'), indent=1)
        say(f'iteration {it}: {t}  SSR {NM.ssr(N, mom, keys):.4f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
