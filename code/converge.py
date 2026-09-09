#!/usr/bin/env python3
"""One command per generation: read the points, move every parameter, emit the next batch.

WHAT A GENERATION IS. Every worker session solves the model once at one parameter
vector and commits the moments it produced. A generation is a centre plus one arm
per parameter, each arm differing from the centre in exactly ONE value, so every
arm is a matched pair with the centre and every pair is a secant.

HOW EACH PARAMETER MOVES.
  - b and the value of life move TOGETHER, by crossing two ridges
    (ridge_solve.py). They are entangled: each moves the drug margin and the
    value of life, so a secant on either alone lands off the answer.
  - Every other parameter moves on its own secant against the centre, in logs
    where both the parameter and its moment are positive, linearly otherwise.
  - A parameter with no matched pair yet keeps its value and is given an arm, so
    that the next generation has the pair it was missing.

THE STEP IS NOT TRUSTED WHOLE. A secant through a response that is flat and then
falls off a cliff can land anywhere, so a step is capped at a factor of MAX_STEP
per generation. That cap is what stops the search thrashing; it is deliberately
looser than the one-per-cent-a-loop the model's own updater uses, because here
the pairs are measured rather than guessed.
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jacobian                                          # noqa: E402
import loss_history                                      # noqa: E402
import ridge_solve                                       # noqa: E402
import score_points                                      # noqa: E402
from suggest_next import OWNS, points                    # noqa: E402

# A MOMENT THAT MUST BE READ CONDITIONALLY. lambda owns the share of users whose
# use is disordered, not the disorder rate in the population, and while the user
# rate is ten times its target the disorder rate is ten times its target too.
# Reading lambda off the raw rate sent it to 0.004; read off the share, the same
# two points say it must RISE, because 0.19 disordered out of 0.91 users is a
# share of 0.21 against a target of 0.413.
RATIO = {'lambda_addiction': ('lambda_d', 'b', 0.4130)}

# A MOMENT MEASURED OVER AN EMPTY POPULATION SAYS NOTHING. Most of these targets
# are conditional: the disordered share of users, the mental-illness share of the
# homeless, take-up among the disordered. While the conditioning population is
# far from its own target the conditional moment is noise, and calibrating
# against it moves a parameter for no reason.
#
# lambda_m is the case that made this rule. At 0.50 and at 0.90 it produced the
# SAME share of the homeless with mental illness, 0.0440, identical to seventeen
# figures against a target of 0.25 -- because homelessness in those points was
# 0.034 per cent, so the share was being read off almost nobody. The parameter
# looked saturated and untargetable; it was neither, it was ungated.
#
# Each entry is the moment that has to be near its own target first, and how far
# off it may be, as a factor, before the reading is refused.
GATE = {
    'lambda_addiction':                      ('b', 0.0890, 3.0),
    'relative_share_of_addiction_1':         ('b', 0.0890, 3.0),
    'utility_cost_of_treatment':             ('b', 0.0890, 3.0),
    'multiple_of_probabilities_of_employment_if_addicted': ('b', 0.0890, 3.0),
    # 0.00399 -> 0.01160, the Fortran's live fraction_homeless_data. The old
    # value was HUD's point-in-time household rate, which the target moved off
    # on 8 September; the gate was refusing readings against a number the model
    # had stopped aiming at. zeta_DI's adjuster is zero, so nothing was
    # mis-stepped by it, but the gate is shared machinery.
    'zeta_DI':                               ('h_1', 0.01160, 3.0),
}

# AN ARM THAT KNOCKS THE POPULATION OFF TARGET MEASURES A DIFFERENT ECONOMY.
# theta and lambda each move the TOTAL user rate as hard as b does: at the
# generation-three centre, theta 0.25 gave 0.6 per cent of the population using
# and theta 0.55 gave 85 per cent, against a target of 8.9. Their own moments
# were then read where users were ten times or a tenth of target, and the gate
# refused all of them -- correctly, and permanently, because every arm would do
# the same thing again.
#
# So an arm on one of these carries a COMPENSATING move in b, sized from the
# measured elasticity of the user rate to b, chosen to put the user rate back on
# target. The arm then differs from the centre in the parameter under test and
# in nothing that matters, which is what a secant needs.
COMPENSATE = {'lambda_addiction': 'addiction_scalar_1',
              'relative_share_of_addiction_1': 'addiction_scalar_1'}
COMPENSATED_MOMENT = 'b'
COMPENSATED_TARGET = 0.0890
B_ELASTICITY = -4.0     # d ln(users) / d ln(b), the slope every populated slice measures

# HOW MANY ARMS A GENERATION IS WORTH.
#
# Every arm is one worker session and about twenty minutes, so an arm that
# cannot teach anything is pure cost. Three rules cut a generation from
# thirty-seven arms to roughly half that without slowing the search:
#
#   A parameter already on its target gets NO arm. Five of them sit inside three
#   per cent -- b, the value of life, sigma_y, beta, the unemployment rate --
#   and re-bracketing them every round measures what is already known.
#
#   A parameter whose secant read cleanly gets ONE arm. The direction is known;
#   the centre has already moved to the predicted answer, and a single arm to one
#   side is enough to bracket the target if the prediction missed.
#
#   Everything else gets exactly ONE arm. Two-sided brackets were redundant from
#   the start: THE CENTRE IS ITSELF A MEASURED POINT, so one arm and the centre
#   already make the pair a secant needs. Bracketing both ways bought a second
#   point on a curve the centre had already anchored, at the price of a whole
#   worker session each time.
#
#   The arm's SIZE is scaled to how far the moment is: a parameter 250 per cent
#   off is probed at the full step, one 10 per cent off at a twentieth of it. A
#   fixed factor of 1.6 either barely moved the badly-wrong parameters or
#   overshot the nearly-right ones.
# WHAT THE AUTHOR HAS SET BY HAND, applied after the secants and overriding
# them. The search reads its own measurements; the author reads the economics,
# and where the two disagree this is where the author's call is recorded so it
# survives every automated round rather than being re-argued each time.
#
# lambda_addiction: raised from 1.5 on the author's instruction of 24 August.
# Its moment, the disordered share of users, sits 94 per cent low, and the three
# values measured so far (0.6, 1.5, 3.0) moved that share only between 0.028 and
# 0.032 -- but each of them also knocked the user rate off target, so none was a
# clean reading. Probed wide here, with b compensating, to settle whether lambda
# can carry the moment at all.
#
# utility_cost_of_treatment: SETTLED at 0.268 by the penalty sweep of 24 August.
# Take-up ran 0.86 at a penalty of 0.02, 0.512 at 0.15, 0.2009 at 0.3135, 0.0589
# at 1 and exactly zero at 3 and at 10, against a target of 0.245, so the answer
# interpolates between 0.15 and 0.3135. Left as an author setting rather than a
# secant because the moment is conditional on the disordered population, which
# is still moving; when lambda settles this should be re-read and released.
#
# lambda_addiction and addiction_scalar_1: SOLVED TOGETHER, 24 August, by a ridge
# that held the user rate on target while lambda moved. At lambda 9, b 0.0215
# gives 7.66 per cent using against a target of 8.9 and a disordered share of
# 0.4033 against 0.413 -- both within a few per cent at the same point, after
# five generations in which the share sat 94 per cent low. Interpolating the
# remaining gap on users, between b 0.0215 (7.66 per cent) and 0.0243 (2.89 per
# cent), gives b 0.0211 and a share near 0.42.
#
# The reading that lambda had no traction was taken entirely at lambda 1.5. The
# reading that the share flattened short of target was taken at points whose own
# user rate was two to six times off, and correcting them with an assumed
# exponent was worse than measuring them.
AUTHOR_SET = {}
# EMPTIED 25 August, on the author's instruction, after the generation six centre
# showed why it had to be.
#
# lambda 9, b 0.0211 and a treatment penalty of 0.268 were each measured cleanly
# and each pinned here by hand. Put into one point together they gave a user rate
# of 0.0175 against a target of 0.089, a disordered share 95 per cent low and a
# take-up of 0.0045 against 0.245 -- every one of them worse than before, and the
# loss up from 0.480 to 0.856.
#
# They do not compose because they move each other's moments. A higher treatment
# penalty does not only cut take-up: it means fewer households ever recover,
# which raises the expected cost of ever starting, which collapses the user rate,
# which drags the disordered share down with it. Measuring one at a time answers
# a question nobody asked -- what this parameter does while the others stay
# wrong.
#
# The Jacobian exists for exactly this. It carries the cross effects, it now has
# a full set of derivatives measured around this centre, and pinning parameters
# by hand is the one thing that takes them out of its hands. Anything set here
# again should be a value the author wants held FIXED, not a value the search is
# meant to find.
#
# utility_cost_of_treatment: probed to the model's own ceiling on the author's
# instruction of 24 August. Treatment take-up is 252 per cent high and this is
# the penalty that should push it down. The elasticity measured here, -0.030,
# was taken between 0.0125 and 0.032 and was then used to argue the parameter
# could never reach its target -- a derivative over a 2.5-fold range
# extrapolated to a claim about a 500-fold move, on a response that is flat and
# then falls off a cliff, which is the one shape this model keeps producing. The
# highest value ever run is 0.15. These probe 1, 3 and 10.
# CLEARED once both questions were answered. The lambda probes ran to 60 and the
# treatment probes to the model's ceiling of 10; both instruments turned out to
# reach their targets comfortably, so continuing to spend sessions on them buys
# nothing. Their compensation had also gone stale -- it was still proposing b
# near 0.005 for a lambda 9 arm, which puts the whole population back on drugs.
# MEASURE THE ANSWER THE ODDS FIT NAMES, rather than walk to it a capped step at
# a time. kappa_uem is the only instrument on the employment rate given serious
# mental illness and the only moment never brought inside twenty five per cent.
# Three measured points -- 1.0, 1.6 and 3.0 -- lie on a straight line in log odds
# with residuals under 0.02 and put the answer at 8.5. That is an extrapolation,
# so it is measured rather than believed: one point this generation settles
# whether the relation holds where it matters.
AUTHOR_PROBE = {'kappa_uem': [8.5]}

ON_TARGET = 0.03        # a moment this close to its target needs no arm at all
ARM_MIN, ARM_MAX = 1.15, 3.0

# A PARAMETER THE JOINT SOLVE DECLINED TO MOVE IS NOT A PARAMETER THAT IS DONE.
# The step is a compromise across twenty two moments, so it will leave a
# parameter almost where it was whenever the fit thinks moving it costs more
# elsewhere than it gains. Generation eight had five of those and their gaps were
# 27, 53, 53, 57 and 80 per cent; they were dropped from the generation and then
# printed under a heading claiming they were within three per cent of target.
# A parameter with a large gap that the fit will not move is exactly the one
# whose derivative is least trustworthy, so it gets an arm to re-measure it.
#
# The threshold is well below the gaps that produced the rule because the cost
# of an arm is one parallel session and the fleet has the slots. ON_TARGET says
# three per cent is converged, so a moment ten per cent out is a genuine miss and
# worth a measurement rather than a place on the settled list.
REFRESH_GAP = 0.10

# AND THE STEP LENGTH IS MEASURED, NOT INFERRED A ROUND LATER. The gain ratio
# compares one realised step against one prediction, so a step that overshoots
# costs a whole generation to discover. These fractions of the joint step run as
# their own points, in parallel with the arms, and the round closes knowing the
# shape of the loss along the direction it actually travelled. They move many
# parameters at once, so assemble() skips them; the regression uses them.
LINE_SEARCH = (0.4, 0.7, 1.4)

# TIGHT, on the author's instruction of 25 August, after the centre drifted from
# 0.528 to 0.856 over three rounds while the step was allowed to be a factor of
# three. A step that large lets one parameter cross a cliff -- size_homelessness
# did exactly that at generation four and took the homelessness rate to
# thirty-two times its target -- and the round after inherits the wreck.
MAX_STEP = 1.4
TRUST_FLOOR = 1.10      # never shrink the step below this
PAIRED = ('addiction_scalar_1', 'value_of_life')         # the two that must be solved together
RUNNER = os.path.join(HERE, 'run_one_point.sh')
GENFILE = os.path.join(HERE, 'GENERATION.txt')
TRUSTFILE = os.path.join(HERE, 'TRUST.txt')
ARM = 1.6               # an arm sits this factor either side of the centre

# WHAT EACH PARAMETER MAY BE. A secant knows nothing about what a number means,
# so it will happily propose a discount factor of 1.59 or a probability of 3.
# These are the bounds the model itself imposes, and an arm is clipped into them
# rather than being sent out to fail.
BOUNDS = {
    # The author lowered the floor on 29 August: b may be arbitrarily small so
    # long as it is strictly positive. Matches b_lo in the Fortran, which is now
    # 1e-30. It has never bound -- the search sits near 0.017.
    'addiction_scalar_1':                    (1e-30, 1.0),
    # NO CEILING IN THE MODEL: the handover takes lambda_addiction verbatim, and
    # the onset hazard is 1 - exp(-lambda * drug quantity), so a large enough
    # lambda drives the disordered share arbitrarily close to one. The search's
    # own cap of 20 was the only thing in the way, and it sat just below the
    # value the arithmetic points at: the share is 0.0284 at lambda 1.5, so
    # lambda * q is about 0.0288 and q about 0.019, and reaching 0.413 needs
    # lambda * q near 0.533 -- lambda around 28.
    'lambda_addiction':                      (0.01, 200.0),
    # THE CLIFF IS AT ABOUT 0.51, so the upper bound sits below it rather than at
    # 0.70. Above the cliff the model has essentially everyone using: the archive
    # puts b at 0.96 at 0.658 and 0.997 at 0.70, against a target of 0.089. An arm
    # sent up there measures a degenerate economy, scores terribly, and tells the
    # search to shrink AWAY from the band that is actually wanted. The usable
    # window is 0.47 to 0.51, across which the share of users who become
    # disordered rises from 0.03 toward the 0.41 the data needs -- so this
    # parameter, not lambda_addiction, is what lambda_d is stuck on. Simplex 4's
    # own arm for it was 0.658 and would have done exactly the wrong thing.
    #
    # THERE IS A SECOND CLIFF BELOW, AND THE LOWER BOUND NOW SITS ABOVE IT.
    # 0.01 let the search walk into a dead zone as degenerate as the one above
    # 0.51, in the other direction. Two controlled runs sharing lambda_addiction
    # 9.0 and addiction_scalar_1 0.0215 and differing only here:
    #     0.42  ->  b = 0.0086, lambda_d = 0.0010
    #     0.36  ->  b = 0.0019, lambda_d = 0.00019, and theta returns the -1
    #               sentinel because the using population it is measured over
    #               has emptied
    # against b = 0.089 in the data. So participation has already fallen by a
    # factor of ten one rung below the anchor at 0.47023, and by 0.36 there is
    # no drug block left to measure. An arm sent down there scores a gated miss
    # and pushes the simplex away from the only band that works.
    # WIDENED 29 AUGUST WITH THE AUTHOR'S APPROVAL, from (0.45, 0.51).
    #
    # THE OLD BOUND WAS 0.125 E-FOLDS WIDE AND THE SEARCH USED 100 PER CENT OF
    # IT. For scale, lambda_addiction needed 5.52 e-folds of travel to take its
    # moment from -81 per cent to +10, and probability_becoming_unemployed
    # needed 3.43. A parameter allowed forty times less room than the two that
    # actually had to move, and pressing on both ends of it every time, is not
    # being calibrated; it is being held.
    #
    # AND ITS JUSTIFICATION DIED THIS MORNING. The reasoning above cites b at
    # 0.96 for rsa_1 0.658 and a collapse below 0.36. Both come from the 566
    # points retired by the savings-grid fix, and no post-grid point exists
    # outside (0.45, 0.51) because this bound forbade one.
    #
    # SO THE NEW BOUND IS A JUDGEMENT, NOT A MEASUREMENT, and it is deliberately
    # modest: three times the old room rather than the full range, because the
    # pre-grid evidence probably had the SHAPE right -- degenerate economies at
    # both ends -- even if the grid fix moved the levels. Widening straight to
    # the old cliffs would spend solves measuring an economy where everybody
    # uses. The joint solve can find the real edges from inside.
    'relative_share_of_addiction_1':         (0.40, 0.58),
    'value_of_life':                         (1.0, 500.0),
    'size_homelessness':                     (0.01, 5.0),
    'discount_factor':                       (0.900, 0.999),
    'relative_share_of_leisure':             (0.10, 20.0),
    'labor_income_tax_rate':                 (0.05, 3.0),
    'sd_permanent_productivity':             (0.10, 3.0),
    # THE FLOOR WAS 0.001 AND THE FORTRAN'S IS 1e-6, so the search's own floor
    # was a thousand times the model's. It never bound -- the search never went
    # below 0.0164, sixteen times above its own limit -- so this is not why
    # pi_eu could not be reached. Matched to the Fortran anyway: a bound that
    # is tighter than the model's own is a constraint nobody put there on
    # purpose, and the same shape of unused headroom is what trapped
    # lambda_addiction at 4.5 to 6.9 for the whole calibration.
    'probability_becoming_unemployed':       (1e-6, 0.500),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    # THE MODEL CLAMPS THIS ONE TO [1, 40] ON THE WAY IN. Arms at 0.30 and 0.10
    # were both silently set to 1 and came back as the centre, which the round
    # then read as "no pair".
    'kappa_uem':                             (1.0, 100.0),
    # CLAMPED TO 0.5 ON THE WAY IN, and floored by the prevalence profile. Arms
    # at 0.50 and 0.90 were the SAME point, which is why they returned a share
    # identical to seventeen figures.
    'lambda_m':                              (0.046, 0.500),
    # A share, so it cannot leave the unit interval. The model clamps it there
    # too; both ends are real and neither should ever bind.
    'zeta_DI':                               (0.0, 1.0),
    # A hazard at age 26. The file's own level is 0.003306; two decades either
    # side of it is far more room than the moment should ever need.
    'smi_onset_level':                       (1e-5, 0.5),
    'probability_of_voucher_benchmark_used': (0.0005, 0.900),
    # THE MODEL ACCEPTS TEN; the search had capped itself at five for no reason
    # the model gives. The highest value ever actually run was 0.15.
    'utility_cost_of_treatment':             (0.0001, 10.0),
    'smallest_rental_relative_to_lowest_income': (0.001, 0.900),
    'largest_house_size':                    (0.005, 3.0),
    'weight_on_child':                       (0.0, 1.0),
    'max_food_cost':                         (0.0002, 0.05),
    'mu_homeless':                           (0.05, 1.0),
}


def clip(key, v):
    lo, hi = BOUNDS.get(key, (1e-12, 1e12))
    return max(lo, min(hi, v))


def runner_defaults():
    """The vector the runner currently defaults to."""
    txt = open(RUNNER).read()
    return {k: float(v) for k, v in re.findall(r'\[(\w+)\]=([-+0-9.eE]+)', txt)}


def trust_state():
    """What the last step predicted, so this one can find out if it was right."""
    state = {}
    if os.path.exists(TRUSTFILE):
        for line in open(TRUSTFILE):
            k, _, v = line.strip().partition(' ')
            try:
                state[k] = float(v)
            except ValueError:
                pass
    return state


def gain_ratio(state, residual_now):
    """How much of the promised improvement actually arrived.

    THE ONE HONEST TEST OF A DERIVATIVE. The solve predicts what the residual
    will be after the step; the next round measures what it is. Their ratio is
    the classic trust-region gain: near one the linearisation is holding and the
    step may lengthen, near zero it is not and the step must shorten. Nothing
    else here distinguishes a derivative that is wrong from a step that is long,
    and the two need opposite responses.
    """
    before = state.get('residual')
    predicted = state.get('predicted_residual')
    if before is None or predicted is None:
        return None
    promised = before - predicted
    if promised <= 1e-9:
        return None
    return (before - residual_now) / promised


def trust_step():
    """How far any parameter may move this round.

    A TRUST REGION, BECAUSE A ROUND THAT MADE THINGS WORSE IS EVIDENCE THE STEP
    WAS TOO LONG. Every parameter moves at once, and they interact: generation
    four moved h_2 by a factor of 2.6, kappa_ued by a half and the voucher
    probability by a third in one go, and came back worse than generation three
    on both the best point and the median. The secants were not wrong
    individually; the step was too long for them to hold jointly.

    So the cap halves after a generation that did not improve, and relaxes back
    toward the full step after one that did. The centre itself is already safe --
    it starts from the best measured point, so a bad round is not compounded --
    but without this the next step is just as long as the one that missed.
    """
    state = trust_state()
    held = state.get('trust')
    if held:
        return max(TRUST_FLOOR, min(MAX_STEP, held))
    best_by_gen = loss_history.by_generation()
    if len(best_by_gen) < 2:
        return MAX_STEP
    gens = sorted(best_by_gen)
    latest, previous = best_by_gen[gens[-1]], min(best_by_gen[g] for g in gens[:-1])
    if latest > previous:
        return max(TRUST_FLOOR, MAX_STEP / 2.0)
    return MAX_STEP


def best_point_moments():
    """The moments of the best measured point, for judging what is on target."""
    best, best_loss = {}, None
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        _head, mt = score_points.read(path)
        got = score_points.loss(mt)
        if got and (best_loss is None or got[0] < best_loss):
            best, best_loss = mt, got[0]
    return best


def arm_factor(gap):
    """How far to push the arm: as far as the moment is wrong, within reason."""
    if gap is None or gap != gap:
        return 1.6
    return max(ARM_MIN, min(ARM_MAX, 1.0 + abs(gap)))


def relative_gap(key, moments):
    """How far this parameter's own moment is from its target, as a fraction."""
    name = RATIO[key][0] if key in RATIO else OWNS[key][0]
    if key in RATIO:
        num, den, target = RATIO[key]
        a, b = moments.get(num), moments.get(den)
        if not a or not b or b[0] <= 0:
            return None
        return (a[0] / b[0] - target) / target
    got = moments.get(name)
    if not got or got[1] == 0 or got[0] != got[0]:
        return None
    return (got[0] - got[1]) / abs(got[1])


def centre_now():
    """Where the next generation is centred: THE BEST MEASURED POINT, not the
    vector that was sent out.

    The secants alone will not carry an improvement that a measured arm already
    demonstrates. size_homelessness is the case: an arm at 0.45 halved the
    homelessness gap against a centre of 0.2128, and its own secant was refused
    as an extrapolation, so a centre built from secants alone stayed at 0.2128
    and threw the measurement away. Starting from the best point and applying
    the secants on top keeps both -- what the search measured and what it
    inferred.
    """
    here = runner_defaults()
    best, best_loss = None, None
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        got = score_points.loss(score_points.read(path)[1])
        if got and (best_loss is None or got[0] < best_loss):
            for vec, _mom, name in points():
                if name == os.path.basename(path):
                    best, best_loss = vec, got[0]
                    break
    if best:
        for key in here:
            if key in best:
                here[key] = best[key]
    return here


def read(mom, key):
    """The moment `key` owns, conditional where it has to be read that way."""
    if key in RATIO:
        num, den, _ = RATIO[key]
        a, b = mom.get(num), mom.get(den)
        if a is None or b is None or b <= 0:
            return None
        return a / b
    return mom.get(OWNS[key][0])


def secant(key, target, pts, here):
    """The value of `key` that hits its target, from the pair that brackets it.

    THE TWO POINTS MUST DECLARE THE SAME PARAMETERS. A point that names two of
    them and a point that names nineteen cannot be differenced: the seventeen
    the first says nothing about are exactly the seventeen that might differ.

    THE PAIR SHOULD BRACKET THE TARGET. These responses are flat and then fall
    off a cliff, and a secant across two points on the flat extrapolates to
    nonsense -- generation two's points on the flat put the b that gives 0.089
    users at two hundred thousand. A pair that does not bracket is used only if
    its answer stays near the span it was measured over, and is marked with a
    star so a reading that is really an extrapolation is never mistaken for one
    that is not.
    """
    cands = []
    for vec, mom, _name in pts:
        y = read(mom, key)
        if key in vec and y is not None:
            cands.append((vec, vec[key], y, mom))
    usable = []
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i], cands[j]
            if set(a[0]) != set(b[0]) or abs(a[1] - b[1]) < 1e-15:
                continue
            if any(abs(a[0][k] - b[0][k]) > 1e-12 * max(1.0, abs(a[0][k]))
                   for k in a[0] if k != key):
                continue
            if abs(a[2] - b[2]) < 1e-15:
                continue
            brackets = (a[2] - target) * (b[2] - target) <= 0
            near = min(abs(a[1] - here), abs(b[1] - here))
            usable.append((not brackets, near, a[1], a[2], b[1], b[2], brackets,
                           a[3], b[3]))
    if not usable:
        return None, None
    _, _, x1, y1, x2, y2, brackets, m1, m2 = min(usable)
    if key in GATE:
        gm, gt, tol = GATE[key]
        for m in (m1, m2):
            got = m.get(gm)
            if got is None or got <= 0 or not (gt / tol <= got <= gt * tol):
                return None, 'gated on ' + gm
    # THE MOMENT GOES ON THE SCALE ITS RESPONSE IS STRAIGHT IN, which for a
    # share bounded by one is odds and not levels. Interpolating the employment
    # rate given serious mental illness in levels, from 0.954 and 0.895 towards
    # 0.300, reads the ceiling as a refusal to move and puts kappa_uem in the
    # thousands; in odds the same points are a straight line and the answer is
    # 8.5. See jacobian.scaled for the measurement that settled it.
    sy1, sy2 = jacobian.scaled(y1, target), jacobian.scaled(y2, target)
    st = jacobian.scaled(target, target)
    if (min(x1, x2, y1, y2, target) > 0 and None not in (sy1, sy2, st)
            and abs(sy2 - sy1) > 1e-12):
        f = (st - sy1) / (sy2 - sy1)
        # DO THE ARITHMETIC IN LOGS AND LOOK AT IT BEFORE EXPONENTIATING. A pair
        # taken across a nearly flat response gives an enormous exponent, and
        # math.exp raises OverflowError rather than returning something the span
        # check could then refuse -- which killed the round outright the first
        # time a clamped arm made two points agree.
        lg = math.log(x1) + f * math.log(x2 / x1)
        if not (-700.0 < lg < 700.0):
            return None, 'off the span'
        want, how = math.exp(lg), 'log-log'
    elif abs(y2 - y1) < 1e-15:
        return None, None
    else:
        want, how = x1 + (target - y1) / (y2 - y1) * (x2 - x1), 'linear'
    if want != want or want in (float('inf'), float('-inf')):
        return None, 'off the span'
    if not brackets:
        lo, hi = min(x1, x2), max(x1, x2)
        if not (lo / 4.0 <= want <= hi * 4.0):
            return None, 'off the span'
        how += '*'
    return want, how


def capped(key, here, want):
    """A step no larger than MAX_STEP either way, and never through zero."""
    if want is None or want != want or want <= 0 or here <= 0:
        return here
    step = trust_step()
    return clip(key, max(here / step, min(here * step, want)))


def emitted():
    """The generation that was last sent out: its centre and its arms."""
    if not os.path.exists(GENFILE):
        return None, []
    centre, arms = {}, []
    for line in open(GENFILE):
        line = line.strip()
        if line.startswith('CENTRE '):
            k, _, v = line[7:].partition('=')
            centre[k] = float(v)
        elif line.startswith('ARM '):
            # An arm may set more than one parameter: a compensated arm moves b
            # as well, and recording only the parameter under test made every
            # such point unmatchable and so permanently "missing".
            spec = {}
            for tok in line[4:].split():
                k, _, v = tok.partition('=')
                spec[k] = float(v)
            arms.append(spec)
    return centre, arms


def compensation(key, value, pts, b_centre):
    """The b that puts the user rate back on target when `key` is set to `value`.

    Read from a measured point that actually ran `key` at that value: its user
    rate says how far the arm moved the population, and the elasticity says how
    much b has to give back. Without such a point there is nothing to compensate
    from and the arm goes out plain.
    """
    # How the user rate responds to this parameter, from every point that ran it
    # at the centre's b. One exact match is rare, so the response is fitted and
    # the arm's user rate predicted from it.
    # Every point that ran this parameter counts, whatever b it ran at: its user
    # rate is first normalised to the centre's b through the same elasticity.
    # Filtering on b instead of normalising threw away every point, because the
    # centre had already moved off the b those points were measured at.
    obs = []
    for vec, mom, _n in pts:
        if key not in vec or 'addiction_scalar_1' not in vec:
            continue
        u, b = mom.get(COMPENSATED_MOMENT), vec['addiction_scalar_1']
        if not u or u <= 0 or b <= 0 or vec[key] <= 0:
            continue
        obs.append((math.log(vec[key]),
                    math.log(u) - B_ELASTICITY * (math.log(b) - math.log(b_centre))))
    obs = sorted(set(obs))
    if len(obs) < 2:
        return None
    lv = math.log(value)
    exact = [o for o in obs if abs(o[0] - lv) < 1e-9]
    if exact:
        u = math.exp(exact[0][1])
    else:
        obs.sort(key=lambda o: abs(o[0] - lv))
        (x1, y1), (x2, y2) = obs[0], obs[1]
        if abs(x2 - x1) < 1e-12:
            return None
        u = math.exp(y1 + (lv - x1) * (y2 - y1) / (x2 - x1))
    if not (1e-6 < u < 1.0):
        return None
    if abs(math.log(COMPENSATED_TARGET / u)) < 0.05:
        return None                       # the arm already sits on target
    want = b_centre * math.exp(math.log(COMPENSATED_TARGET / u) / B_ELASTICITY)
    return clip('addiction_scalar_1', want)


def coverage(pts, centre, arms):
    """Which arms actually came back.

    NINETEEN OF THIRTY WORKERS ONCE CAME BACK WITH NOTHING -- their containers
    had no clone of the repository and they sat blocked -- and the round read
    that as "no pair", which is a statement about the data and was a statement
    about the fleet. An arm that was sent and did not land has to be visible as
    a MISSING arm, not as a parameter that happens to have no secant.
    """
    landed, missing = [], []
    for spec in arms:
        want = dict(centre)
        want.update(spec)
        # SIX SIGNIFICANT DIGITS IS THE PRECISION OF THE WHOLE PIPELINE. The
        # runner writes its defaults with %.6g, so every point's vector carries
        # six digits; comparing against a ten-digit record with a 1e-9 tolerance
        # made every arm mismatch on the nine parameters it never touched, and
        # the round read a full generation as "0 of 37 came back".
        hit = any(set(v) == set(want)
                  and all(abs(v[k] - want[k]) <= 1e-5 * max(1.0, abs(want[k])) for k in want)
                  for v, _m, _n in pts)
        (landed if hit else missing).append(spec)
    return landed, missing


def main():
    pts = points()
    centre_sent, arms_sent = emitted()
    if arms_sent:
        landed, missing = coverage(pts, centre_sent, arms_sent)
        print('THE GENERATION JUST RUN: %d of %d arms came back.'
              % (len(landed), len(arms_sent)))
        if missing:
            print('These arms were sent and never landed. They are NOT parameters '
                  'without a secant; they are points that were never measured, and '
                  'the fleet has to be asked why before the round is closed:')
            for spec in missing:
                print('   MISSING  ' + ' '.join('%s=%g' % kv for kv in sorted(spec.items())))
        print()
    here = centre_now()
    data = ridge_solve.measured()
    cross, _, _, _ = ridge_solve.solve(data)

    moved, arms, settled, stale = {}, [], [], []
    simplex_owns = set()
    if os.path.exists(os.path.join(HERE, 'SIMPLEX.txt')):
        import simplex
        simplex_owns = set(simplex.BLOCK)
    best_moments = best_point_moments()

    # THE JACOBIAN LEADS WHERE IT EXISTS. Every arm measured how all twenty-two
    # moments answered one parameter; the secant used one number from each and
    # discarded the cross effects, which is what let size_homelessness take the
    # homelessness rate from 0.03 per cent to 12.9 with nothing to stop it. The
    # solve moves the whole vector together, so a parameter that would wreck
    # another moment is held back by that moment's row.
    #
    # It steps from THE GENERATION CENTRE, because that is the point the
    # derivatives were measured around. Where a parameter has no column -- no
    # arm came back for it -- the secant still answers.
    sent = emitted()[0]
    jac, jac_info = (None, None)
    if sent:
        jac, jac_info = jacobian.step(sent, jacobian.points(), trust=trust_step(),
                                      moment_cap=trust_state().get('moment_cap'))
    if jac:
        # THE STEP IS APPLIED WHERE THE SEARCH STANDS, NOT WHERE THE DERIVATIVES
        # WERE MEASURED. This used to re-anchor the centre onto the generation
        # centre, on the reasoning that a linearisation belongs at the point it
        # was taken. That silently threw away a reset: told to go back to the
        # best measured vector at 0.480, the round re-anchored onto the 0.856
        # centre the reset was undoing.
        #
        # A derivative carried a short distance is an approximation; a centre
        # quietly replaced is a lost instruction. With the step capped at 1.4 the
        # approximation is small, and the next generation's arms re-measure the
        # derivatives where the centre now is.
        here = dict(here)
        print('Jacobian: %d moments against %d parameters around %s, damping %.3g, '
              'using %.0f%% of the trust region.\n'
              % (len(jac_info['moments']), len(jac), jac_info['reference'],
                 jac_info['damping'] if isinstance(jac_info['damping'], float) else -1,
                 100 * jac_info.get('used', 0)))
    print('%d point(s) measured. Centre of the generation just run:\n' % len(pts))
    print('%-52s %12s %12s %12s %9s' % ('parameter', 'now', 'secant says', 'capped to', 'how'))
    print('-' * 102)
    for key in OWNS:
        now = here.get(key)
        if now is None:
            continue
        # TWO METHODS MAY NOT OWN ONE PARAMETER. While the simplex is running on
        # the drug block, those four are its business: a Jacobian step on them
        # would move the background the simplex measures its vertices against,
        # and the simplex has no way to see that happen -- it would go on
        # comparing losses that are no longer comparable, which is exactly the
        # error its own construction guards against.
        if key in simplex_owns:
            moved[key] = now
            print('%-52s %12.5g %12s %12.5g %9s'
                  % (key, now, '-', now, 'simplex'))
            continue
        if key in PAIRED and cross:
            want = cross[0] if key == 'addiction_scalar_1' else cross[1]
            how = 'ridges'
        else:
            want, how = secant(key, RATIO[key][2] if key in RATIO else OWNS[key][1],
                               pts, now)
            how = how or 'no pair'
        # ORDER OF EVIDENCE: an interpolation across a measured bracket beats a
        # linearisation, and a linearisation that accounts for cross effects
        # beats an extrapolated secant.
        #
        # size_homelessness is the case. Two measured points put the homelessness
        # rate at 0.03 per cent and at 12.9, with the 0.399 target between them,
        # and interpolating in logs lands on 0.345. The Jacobian, linear around
        # one of those points and held by the trust region, says 0.564 -- true to
        # the derivative and wrong about the curve, because the response is a
        # cliff. Where the bracket exists it is simply better information.
        bracketed = how in ('log-log', 'linear')
        if jac and key in jac and not bracketed:
            want = clip(key, now * math.exp(jac[key]))
            how = 'jacobian'
        new = capped(key, now, want)
        if key in AUTHOR_SET:
            new = clip(key, AUTHOR_SET[key])
            how = 'author'
        moved[key] = new
        print('%-52s %12.5g %12s %12.5g %9s'
              % (key, now, ('%.5g' % want) if want else '-', new, how))
        blind = how in ('no pair', 'off the span') or how.startswith('gated')
        gap = relative_gap(key, best_moments)
        if gap is not None and abs(gap) < ON_TARGET and not blind:
            settled.append((key, gap))          # on target and understood: no arm
        elif blind or abs(math.log(max(new, 1e-12) / max(now, 1e-12))) > 0.005:
            arms.append((key, arm_factor(gap)))
        elif gap is not None and abs(gap) >= REFRESH_GAP:
            # The fit left it where it was and its moment is a long way out.
            # That is a stale derivative, not a settled parameter.
            stale.append((key, gap))
            arms.append((key, arm_factor(gap)))
        else:
            settled.append((key, gap if gap is not None else 0.0))

    arms_emitted = []
    centre_of_generation = sent or here
    print('\nTHE NEXT GENERATION: centre, then one arm per parameter still moving.')
    print('\n  bash code/run_one_point.sh            # centre')
    for key, values in AUTHOR_PROBE.items():
        for v in values:
            v = clip(key, v)
            extra = ''
            if key in COMPENSATE:
                b = compensation(key, v, pts, moved['addiction_scalar_1'])
                if b:
                    extra = ' addiction_scalar_1=%.6g' % b
            arms_emitted.append('%s=%.6g%s' % (key, v, extra))
            print('  bash code/run_one_point.sh %s=%.6g%s' % (key, v, extra))
    for key, factor in arms:
        v = moved[key]
        # THE ARM GOES THE WAY THE CENTRE IS TRAVELLING, so the two of them
        # bracket the answer. Placing it always above meant that a parameter
        # being cut -- size_homelessness, moving 0.68 down toward 0.35 -- was
        # probed at 1.7, away from the answer and off the end of the curve, and
        # the round after it still had no bracket to interpolate across.
        falling = v < centre_of_generation.get(key, v)
        side = clip(key, v / factor) if falling else clip(key, v * factor)
        for side in (side,):
            if abs(math.log(max(side, 1e-12) / max(v, 1e-12))) < 0.02:
                side = clip(key, v / factor)
            if abs(math.log(max(side, 1e-12) / max(v, 1e-12))) < 0.02:
                continue          # both bounds pin this arm onto the centre
            extra = ''
            if key in COMPENSATE:
                b = compensation(key, side, pts, moved['addiction_scalar_1'])
                if b:
                    extra = ' addiction_scalar_1=%.6g' % b
            arms_emitted.append('%s=%.6g%s' % (key, side, extra))
            print('  bash code/run_one_point.sh %s=%.6g%s' % (key, side, extra))

    # THE LINE SEARCH. One point per fraction, every parameter the step moved,
    # scaled in logs so the fractions sit on the step itself rather than on a
    # chord across it.
    travelled = [k for k in moved
                 if abs(math.log(max(moved[k], 1e-12)
                                 / max(here.get(k, moved[k]) or moved[k], 1e-12))) > 0.005]
    if len(travelled) >= 3:
        print('\n  # along the joint step, to measure its length rather than '
              'infer it next round')
        for f in LINE_SEARCH:
            spec = []
            for key in sorted(travelled):
                base = here[key]
                v = clip(key, base * (moved[key] / base) ** f)
                if abs(math.log(max(v, 1e-12) / max(base, 1e-12))) > 0.005:
                    spec.append('%s=%.6g' % (key, v))
            if len(spec) < 3:
                continue
            spec = ' '.join(spec)
            arms_emitted.append(spec)
            print('  bash code/run_one_point.sh %s' % spec)

    if stale:
        print('\nAn arm for these because the joint solve would not move them and '
              'their moment is more than %d per cent out. Their derivative is the '
              'thing being measured, not their level.' % int(100 * REFRESH_GAP))
        for key, gap in sorted(stale, key=lambda kv: -abs(kv[1] or 0)):
            print('   stale    %-52s gap %+.1f%%' % (key, 100 * (gap or 0)))

    if simplex_owns >= set(OWNS):
        print('\nTHE SIMPLEX OWNS EVERY PARAMETER, so this round has no generation '
              'to emit. code/simplex.py drives the search; converge.py is here for '
              'the gap table, the loss history and the Jacobian, which simplex.py '
              'runs as one candidate point among its own. Nothing below is a step '
              'to take.')
    elif simplex_owns:
        print('\nHeld by the simplex (code/simplex.py), which is searching them '
              'jointly because their responses are not smooth enough to '
              'differentiate:')
        for key in sorted(simplex_owns):
            print('   simplex  %-52s %.6g' % (key, moved.get(key, float('nan'))))

    if settled:
        print('\nNo arm for these: their moment is already within %d per cent and '
              'their direction is understood.' % int(100 * ON_TARGET))
        for key, gap in sorted(settled, key=lambda kv: abs(kv[1] or 0)):
            print('   settled  %-52s gap %+.1f%%' % (key, 100 * (gap or 0)))

    # RUNNING converge TWICE GIVES TWO DIFFERENT GENERATIONS. --write re-centres
    # the runner, so a second read-only run computes a further step and arms
    # around that further centre, while the workers still start from the centre
    # --write wrote. Spawn from THIS run's own printed arms, never from a fresh
    # invocation afterwards.
    if '--write' in sys.argv:
        txt = open(RUNNER).read()
        for key, v in moved.items():
            txt = re.sub(r'(\[%s\]=)[-+0-9.eE]+' % re.escape(key), r'\g<1>%.6g' % v, txt)
        open(RUNNER, 'w').write(txt)
        # RECORD WHAT IS BEING SENT OUT, so the next round can tell an arm that
        # came back empty from an arm that was never run at all.
        new_centre = dict(here)
        new_centre.update(moved)
        with open(GENFILE, 'w') as fh:
            for key in sorted(new_centre):
                fh.write('CENTRE %s=%.6g\n' % (key, new_centre[key]))
            for spec in arms_emitted:
                fh.write('ARM %s\n' % spec)
        # RECORD WHAT THIS STEP PROMISES, so the next round can hold it to it.
        if jac_info:
            state = trust_state()
            trust, cap = trust_step(), jacobian.MOMENT_CAP
            rho = gain_ratio(state, jac_info['residual'])
            if rho is not None:
                if rho > 0.75:
                    trust, cap = min(MAX_STEP, trust * 1.5), min(3.0, cap * 1.3)
                    verdict = 'the last step delivered %.0f%% of what it promised, so both widen' % (100 * rho)
                elif rho < 0.25:
                    trust, cap = max(TRUST_FLOOR, trust / 2.0), max(1.1, cap / 1.3)
                    verdict = 'the last step delivered only %.0f%% of what it promised, so both tighten' % (100 * rho)
                else:
                    verdict = 'the last step delivered %.0f%% of what it promised, so both hold' % (100 * rho)
                print('\nGAIN: ' + verdict)
            with open(TRUSTFILE, 'w') as fh:
                fh.write('residual %.6f\n' % jac_info['residual'])
                fh.write('predicted_residual %.6f\n' % jac_info.get('predicted_residual', jac_info['residual']))
                fh.write('trust %.6f\n' % trust)
                fh.write('moment_cap %.6f\n' % cap)
        print('\nrun_one_point.sh re-centred; the generation is recorded in '
              'GENERATION.txt so the next round can check that it came back.')
    else:
        print('\n(--write to move the runner defaults to the new centre)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
