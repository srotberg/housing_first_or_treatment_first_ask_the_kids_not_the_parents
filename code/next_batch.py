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
    'multiple_of_probabilities_of_employment_if_addicted': 'sud_homeless',
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
    'smallest_rental_relative_to_lowest_income':            'h_3',
    # AND THE TOP RUNG HAD NO INSTRUMENT EITHER. largest_house_size owns the
    # share in the largest unit -- h_4 until the author's rename, h_3 now -- and
    # like the bottom rung it sat in the vector with nothing mapped to it. It is
    # only 1.7 per cent off, so this closes a hole rather than fixing a gap.
    'largest_house_size':                                  'h_2',
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
    # discount_factor IS NOT HERE ANY MORE, AND beta HAS AN OWNER ALREADY.
    # The model bisects the patient discount factor on wealth over output
    # inside every point run -- distance_discount_factor sits in the
    # calibration loop's while condition and the update is gated only on
    # re_do_simulation_with_fixed_parameters, which is zero in a point. So
    # proposing a value here was a DUPLICATE DRIVER: the search spent an arm on
    # beta, the model overrode it, and the archived VECTOR line then recorded a
    # discount factor the point did not actually run at. The vector value is
    # still passed, as the bisection's starting point, which is what BOUNDS
    # below is for.
    # w_bot's owner, and it can only move while number_of_beta_types is 2.
    # At one type it does nothing and the moment has no instrument.
    'discount_factor_impatient':                           'w_bot',
    # THE MORTALITY PENALTY IS THE PRICE OF USING, so it decides WHO is willing
    # to pay it, and a high one leaves only the most desperate -- who are the
    # poorest. That is why the model has zero use in the top two income bands
    # against 7.2 and 4.8 per cent in NSDUH. Calibrated on the income of drug
    # users on the author's instruction, rather than assigned.
    'kappa_phi_d_level':                                   'y_u',
    # gamma's instrument, freed on the author's instruction. Its measured
    # elasticity on gamma is only 0.22 and it costs h_1 at -7.32, so it is a
    # weak and coupled instrument -- but it is the only one, and h_1 now has
    # both size_homelessness and the food stamp floor holding it.
    'relative_share_of_housing':                           'gamma',
    # OPENED ON THE AUTHOR'S INSTRUCTION, both previously compile-time constants.
    #
    # increased_prob_if_homeless is the labour market cost of the street: the
    # homeless lose a job at (1+x) times the housed rate and find one at 1/(1+x)
    # times it. It owns the employed share of the homeless, and the ownership is
    # not a guess -- the steady state formula 1/(1+(1+x)**2*(s/f)), with nothing
    # in it but pi_eu and this parameter, predicts 0.9316 at the assigned 0.2
    # against 0.9252 measured. It is also the Housing First channel itself, so
    # leaving it assigned assigns the counterfactual's main result.
    'increased_prob_if_homeless':                          'emp_homeless',
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
    'relative_share_of_addiction_1':                       (0.40, 0.58),
    'mu_homeless':                                         (0.05, 1.0),
    'lambda_m':                                            (0.046, 0.500),
    'smi_onset_level':                                     (1e-5, 0.5),
    'value_of_life':                                       (1.0, 500.0),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    'probability_of_voucher_benchmark_used':               (0.0001, 0.999),
    'size_homelessness':                                   (0.01, 5.0),
    'smallest_rental_relative_to_lowest_income':            (0.005, 0.40),
    'largest_house_size':                                  (0.02, 1.00),
    'kappa_uem':                                           (1.0, 100.0),
    'max_food_cost':                                       (1e-4, 1.0),
    # a SEED for the internal bisection, not a search range: see OWN above.
    'discount_factor':                                     (0.90, 0.999),
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
BAND = {'beta': (3.0, 4.5)}
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
SKIP = {'h_3'}

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
UNSCORED = {'emp_homeless', 'sud_homeless',
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
        near = [y for x, y in g if abs(math.log(x / x_base)) < 1e-6]
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
               'gamma': ['renters'],
               # cbar CHANGED DENOMINATOR. It was total food-stamp spending over
               # model_average_labour_income, a total over a MEAN, which scaled
               # with population and printed 0.0532 against a target of 0.0042.
               # It is now total spending over total income, which is what "0.42
               # per cent of income" means. A point measured under the old label
               # carries a number thirty times larger under the same name, so
               # mixing them would walk the search away from a target it may
               # already be near. The old label said "labour income".
               'cbar': ['labour income']}


def moments(text):
    out = {}
    for n, label, m, tg in re.findall(
            r'MOMENT (\S+)\s+(.*?)model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', text):
        if any(t in label for t in STALE_LABEL.get(n, ())):
            continue
        out[n] = (float(m), float(tg))

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
                      r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', 'sud_homeless')):
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
    '6eeab9f2cc': {'57a80a45e9'},
    # 33160acfdd ADDS FIVE WRITE STATEMENTS to 80b575e3c8 and nothing else. The
    # diff, read line by line before this entry was made, is the aleph ingredient
    # block in print_all_moments: the numerator, the denominator, the worker
    # count behind it, the implied total labour income and the value of life per
    # household. Every added line is a `write(*,*)`; not one assignment, guard or
    # expression that the model computes was touched.
    #
    # This matters more than usual right now, because point_6c9629542c is the
    # FIRST point ever measured with every invariant passing and the source has
    # moved once since. Without this entry the archive is empty again and the
    # gate has nothing to interpolate from.
    '33160acfdd': {'80b575e3c8'},
    # dc8abdfbce ADDS ONLY PRINTS AND DEFAULTS-PRESERVING COORDINATES to
    # d70ad1c545, so a point measured on either is the same economy and the
    # archive must not be thrown away for it. What changed:
    #   - the by-age housing-margin DIAG block in print_all_moments, which is
    #     write statements and nothing else;
    #   - number_of_beta_types and homeless_death_risk_flat_in_age became
    #     runtime coordinates rather than compile-time parameters, and BOTH
    #     default to the value that reproduces the old behaviour exactly
    #     (one type, Baggett's mortality ratios);
    #   - freeze_beta_bisection, which defaults to 0 and gates nothing at 0.
    # A point that passes homeless_death_risk_flat_in_age=0 on dc8abdfbce is
    # therefore bit-comparable with one measured on d70ad1c545. A point that
    # passes 1 or 2 is NOT, and is a different economy by intention.
    'dc8abdfbce': {'d70ad1c545'},
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
    want = current_model_hash()
    ok = {want} | EQUIVALENT_MODELS.get(want, set())
    out, skipped = {}, 0
    for f in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        t = open(f).read()
        mh = re.search(r'^MODEL (\S*)', t, re.M)
        if not mh or mh.group(1) not in ok:
            skipped += 1
            continue
        v, m = vector(t), moments(t)
        if v and 'b' in m and 'lambda_d' in m:
            out[os.path.basename(f)[6:-4]] = (v, m)
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
    n = len(es)
    return es[n // 2] if n % 2 else 0.5 * (es[n // 2 - 1] + es[n // 2])


def main():
    A = archive()
    if not A:
        print('no archive'); return 1

    # The gate: any point with BOTH b and lambda_d inside five per cent, best by
    # worst-gap over everything else.
    opened = any(all(g in m and gap(g, m[g]) <= GATE[g] for g in GATE)
                 for _, m in A.values())
    tol = BASE_TOL if opened else GATE
    through = []
    for tag, (v, m) in A.items():
        if all(g in m and gap(g, m[g]) <= tol[g] for g in tol):
            rest = {k: gap(k, p) for k, p in m.items()
                    if k not in SKIP and k not in UNSCORED}
            through.append((max(rest.values()), tag, v, m))
    if not through:
        best = min(((max(gap('b', m['b']), gap('lambda_d', m['lambda_d'])), tag)
                    for tag, (v, m) in A.items()))
        print(f'GATE CLOSED. Best on max(|b gap|,|lambda_d gap|) is {best[1]} at '
              f'{100*best[0]:.1f} per cent; the gate is {100*GATE["b"]:.0f}.')
        print('Keep working the locus. No correction batch emitted.')
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
    lines, skipped = [], []
    for param, mom in sorted(OWN.items(), key=lambda kv: -gap(kv[1], m[kv[1]]) if kv[1] in m else 0):
        if mom not in m or gap(mom, m[mom]) <= ACCEPT:
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
            skipped.append(f'{param} (owns {mom}): no controlled pair in the archive')
            continue
        cur, tgt = m[mom]
        if br is None:
            step = DAMP * math.log(tgt / cur) / e
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
