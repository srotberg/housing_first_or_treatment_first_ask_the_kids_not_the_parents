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

MAX_STEP = 3.0          # no parameter may move by more than this factor in one generation
PAIRED = ('addiction_scalar_1', 'value_of_life')         # the two that must be solved together
RUNNER = os.path.join(HERE, 'run_one_point.sh')
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
    'kappa_uem':                             (0.01, 5.0),
    'lambda_m':                              (0.001, 0.990),
    'probability_of_voucher_benchmark_used': (0.0005, 0.900),
    'utility_cost_of_treatment':             (0.0001, 5.0),
    'penalty_child_addicted':                (0.001, 5.0),
    'penalty_child_homeless':                (0.001, 5.0),
    'smallest_rental_relative_to_lowest_income': (0.001, 0.900),
    'largest_house_size':                    (0.005, 3.0),
}


def clip(key, v):
    lo, hi = BOUNDS.get(key, (1e-12, 1e12))
    return max(lo, min(hi, v))


def centre_now():
    """The vector the runner currently defaults to: the centre of this generation."""
    txt = open(RUNNER).read()
    return {k: float(v) for k, v in re.findall(r'\[(\w+)\]=([-+0-9.eE]+)', txt)}


def secant(key, target, pts, here):
    """The value of `key` that hits its target, from the two measured points
    nearest the centre that differ in `key` alone."""
    moment = OWNS[key][0]
    pairs = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i][0], pts[j][0]
            if key not in a or key not in b or abs(a[key] - b[key]) < 1e-15:
                continue
            shared = set(a) & set(b)
            if any(abs(a[k] - b[k]) > 1e-15 for k in shared if k != key):
                continue
            ya, yb = pts[i][1].get(moment), pts[j][1].get(moment)
            if ya is None or yb is None or abs(ya - yb) < 1e-15:
                continue
            near = min(abs(math.log(max(a[key], 1e-12) / max(here, 1e-12))),
                       abs(math.log(max(b[key], 1e-12) / max(here, 1e-12))))
            pairs.append((near, a[key], ya, b[key], yb))
    if not pairs:
        return None, None
    _, x1, y1, x2, y2 = min(pairs)
    if min(x1, x2, y1, y2, target) > 0 and abs(math.log(y2 / y1)) > 1e-12:
        f = math.log(target / y1) / math.log(y2 / y1)
        return math.exp(math.log(x1) + f * math.log(x2 / x1)), 'log-log'
    if abs(y2 - y1) < 1e-15:
        return None, None
    return x1 + (target - y1) / (y2 - y1) * (x2 - x1), 'linear'


def capped(key, here, want):
    """A step no larger than MAX_STEP either way, and never through zero."""
    if want is None or want != want or want <= 0 or here <= 0:
        return here
    return clip(key, max(here / MAX_STEP, min(here * MAX_STEP, want)))


def main():
    pts = points()
    here = centre_now()
    data = ridge_solve.measured()
    cross, _, _ = ridge_solve.solve(data)

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
            want, how = secant(key, OWNS[key][1], pts, now)
            how = how or 'no pair'
        new = capped(key, now, want)
        moved[key] = new
        print('%-52s %12.5g %12s %12.5g %9s'
              % (key, now, ('%.5g' % want) if want else '-', new, how))
        if how == 'no pair' or abs(math.log(max(new, 1e-12) / max(now, 1e-12))) > 0.05:
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
        print('\nrun_one_point.sh re-centred.')
    else:
        print('\n(--write to move the runner defaults to the new centre)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
