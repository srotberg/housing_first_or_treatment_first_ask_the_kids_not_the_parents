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
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ridge_solve                                       # noqa: E402
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
    'penalty_child_addicted':                ('b', 0.0890, 3.0),
    'multiple_of_probabilities_of_employment_if_addicted': ('b', 0.0890, 3.0),
    'lambda_m':                              ('h_1', 0.00399, 3.0),
    'penalty_child_homeless':                ('h_1', 0.00399, 3.0),
}

MAX_STEP = 3.0          # no parameter may move by more than this factor in one generation
PAIRED = ('addiction_scalar_1', 'value_of_life')         # the two that must be solved together
RUNNER = os.path.join(HERE, 'run_one_point.sh')
GENFILE = os.path.join(HERE, 'GENERATION.txt')
ARM = 1.6               # an arm sits this factor either side of the centre

# WHAT EACH PARAMETER MAY BE. A secant knows nothing about what a number means,
# so it will happily propose a discount factor of 1.59 or a probability of 3.
# These are the bounds the model itself imposes, and an arm is clipped into them
# rather than being sent out to fail.
BOUNDS = {
    'addiction_scalar_1':                    (1e-10, 1.0),
    'lambda_addiction':                      (0.01, 20.0),
    'relative_share_of_addiction_1':         (0.01, 0.70),
    'value_of_life':                         (1.0, 500.0),
    'size_homelessness':                     (0.01, 5.0),
    'discount_factor':                       (0.900, 0.999),
    'relative_share_of_leisure':             (0.10, 20.0),
    'labor_income_tax_rate':                 (0.05, 3.0),
    'sd_permanent_productivity':             (0.10, 3.0),
    'probability_becoming_unemployed':       (0.001, 0.500),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    # THE MODEL CLAMPS THIS ONE TO [1, 40] ON THE WAY IN. Arms at 0.30 and 0.10
    # were both silently set to 1 and came back as the centre, which the round
    # then read as "no pair".
    'kappa_uem':                             (1.0, 40.0),
    # CLAMPED TO 0.5 ON THE WAY IN, and floored by the prevalence profile. Arms
    # at 0.50 and 0.90 were the SAME point, which is why they returned a share
    # identical to seventeen figures.
    'lambda_m':                              (0.046, 0.500),
    'probability_of_voucher_benchmark_used': (0.0005, 0.900),
    'utility_cost_of_treatment':             (0.0001, 5.0),
    'penalty_child_addicted':                (0.001, 5.0),
    'penalty_child_homeless':                (0.001, 5.0),
    'smallest_rental_relative_to_lowest_income': (0.001, 0.900),
    'largest_house_size':                    (0.005, 3.0),
    'weight_on_child':                       (0.0, 1.0),
    'max_food_cost':                         (0.0002, 0.05),
    'mu_homeless':                           (0.05, 1.0),
}


def clip(key, v):
    lo, hi = BOUNDS.get(key, (1e-12, 1e12))
    return max(lo, min(hi, v))


def centre_now():
    """The vector the runner currently defaults to: the centre of this generation."""
    txt = open(RUNNER).read()
    return {k: float(v) for k, v in re.findall(r'\[(\w+)\]=([-+0-9.eE]+)', txt)}


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
    if min(x1, x2, y1, y2, target) > 0 and abs(math.log(y2 / y1)) > 1e-12:
        f = math.log(target / y1) / math.log(y2 / y1)
        want, how = math.exp(math.log(x1) + f * math.log(x2 / x1)), 'log-log'
    elif abs(y2 - y1) < 1e-15:
        return None, None
    else:
        want, how = x1 + (target - y1) / (y2 - y1) * (x2 - x1), 'linear'
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
    return clip(key, max(here / MAX_STEP, min(here * MAX_STEP, want)))


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
            k, _, v = line[4:].partition('=')
            arms.append((k, float(v)))
    return centre, arms


def coverage(pts, centre, arms):
    """Which arms actually came back.

    NINETEEN OF THIRTY WORKERS ONCE CAME BACK WITH NOTHING -- their containers
    had no clone of the repository and they sat blocked -- and the round read
    that as "no pair", which is a statement about the data and was a statement
    about the fleet. An arm that was sent and did not land has to be visible as
    a MISSING arm, not as a parameter that happens to have no secant.
    """
    landed, missing = [], []
    for key, value in arms:
        want = dict(centre)
        want[key] = value
        hit = any(set(v) == set(want)
                  and all(abs(v[k] - want[k]) <= 1e-9 * max(1.0, abs(want[k])) for k in want)
                  for v, _m, _n in pts)
        (landed if hit else missing).append((key, value))
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
            for key, value in missing:
                print('   MISSING  %s=%g' % (key, value))
        print()
    here = centre_now()
    data = ridge_solve.measured()
    cross, _, _, _ = ridge_solve.solve(data)

    moved, arms = {}, []
    print('%d point(s) measured. Centre of the generation just run:\n' % len(pts))
    print('%-52s %12s %12s %12s %9s' % ('parameter', 'now', 'secant says', 'capped to', 'how'))
    print('-' * 102)
    for key in OWNS:
        now = here.get(key)
        if now is None:
            continue
        if key in PAIRED and cross:
            want = cross[0] if key == 'addiction_scalar_1' else cross[1]
            how = 'ridges'
        else:
            want, how = secant(key, RATIO[key][2] if key in RATIO else OWNS[key][1],
                               pts, now)
            how = how or 'no pair'
        new = capped(key, now, want)
        moved[key] = new
        print('%-52s %12.5g %12s %12.5g %9s'
              % (key, now, ('%.5g' % want) if want else '-', new, how))
        if how in ('no pair', 'off the span') or how.startswith('gated') \
                or abs(math.log(max(new, 1e-12) / max(now, 1e-12))) > 0.05:
            arms.append(key)

    print('\nTHE NEXT GENERATION: centre, then one arm per parameter still moving.')
    print('\n  bash code/run_one_point.sh            # centre')
    for key in arms:
        v = moved[key]
        for side in (clip(key, v * ARM), clip(key, v / ARM)):
            if abs(math.log(max(side, 1e-12) / max(v, 1e-12))) < 0.02:
                continue          # the bound has pinned this arm onto the centre
            print('  bash code/run_one_point.sh %s=%.6g' % (key, side))

    if '--write' in sys.argv:
        txt = open(RUNNER).read()
        for key, v in moved.items():
            txt = re.sub(r'(\[%s\]=)[-+0-9.eE]+' % re.escape(key), r'\g<1>%.6g' % v, txt)
        open(RUNNER, 'w').write(txt)
        # RECORD WHAT IS BEING SENT OUT, so the next round can tell an arm that
        # came back empty from an arm that was never run at all.
        new_centre = dict(centre_now())
        new_centre.update(moved)
        with open(GENFILE, 'w') as fh:
            for key in sorted(new_centre):
                fh.write('CENTRE %s=%.10g\n' % (key, new_centre[key]))
            for key in arms:
                v = moved[key]
                for side in (clip(key, v * ARM), clip(key, v / ARM)):
                    if abs(math.log(max(side, 1e-12) / max(v, 1e-12))) < 0.02:
                        continue
                    fh.write('ARM %s=%.10g\n' % (key, side))
        print('\nrun_one_point.sh re-centred; the generation is recorded in '
              'GENERATION.txt so the next round can check that it came back.')
    else:
        print('\n(--write to move the runner defaults to the new centre)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
