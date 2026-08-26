"""The arm points wherever its own moment has to go.

An arm used to go UP always. That is right when the moment undershoots and
exactly wrong when it overshoots, and simplex 4 paid for it three times: pi_eu
was at 0.1062 against a target of 0.0485 and its arm raised the instrument
further; mu_H was within one per cent and its arm pushed it to 0.907 against
1.473; relative_share_of_addiction_1 went up past the cliff at 0.51 into an
economy where everyone uses.

The rule needs two facts, both known before anything spawns: which side of its
target the moment sits at the anchor, and whether raising the parameter raises
or lowers it. This file pins the four combinations and the fallbacks, because a
sign error here is invisible -- the search simply learns nothing and costs a
worker forty minutes to do it.

Run:  python3 code/test_arm_sign.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import simplex                                            # noqa: E402

CASES = [
    # the four combinations, on parameters whose response sign is unanimous
    ('probability_becoming_unemployed', {'pi_eu': 0.1062}, -1.0,
     'moment must fall, parameter raises it, so the arm goes down'),
    ('probability_becoming_unemployed', {'pi_eu': 0.0200}, +1.0,
     'moment must rise, parameter raises it, so the arm goes up'),
    ('addiction_scalar_1', {'b': 0.0727}, -1.0,
     'moment must rise, parameter lowers it, so the arm goes down'),
    ('addiction_scalar_1', {'b': 0.5000}, +1.0,
     'moment must fall, parameter lowers it, so the arm goes up'),
    # the same shape on four more, to catch a RESPONSE entry losing its sign
    ('mu_homeless', {'mu_H': 0.907}, -1.0, 'mu_H undershoots'),
    ('kappa_uem', {'kappa_uem': 0.3534}, +1.0, 'employment given SMI overshoots'),
    ('utility_cost_of_treatment', {'tau_u': 0.3486}, +1.0, 'take up overshoots'),
    ('max_food_cost', {'cbar': 0.0017}, +1.0, 'food stamps undershoot'),
    # the fallbacks, each of which must be UP rather than a guess
    ('lambda_addiction', {'lambda_d': 0.005}, +1.0,
     'its pairs split 6 to 11, so the sign is unknown and must not be guessed'),
    ('weight_on_child', {'omega': 0.2}, +1.0,
     'OWNS states no target for it, so the gap has no direction'),
    ('probability_becoming_unemployed', {}, +1.0,
     'the anchor did not report the moment'),
    ('a_parameter_that_does_not_exist', {'pi_eu': 0.9}, +1.0,
     'nothing is known about it'),
]


def main():
    bad = 0
    for key, mom, want, why in CASES:
        got = simplex.arm_sign(key, mom)
        if got != want:
            bad += 1
            print('   FAIL %-42s got %+.0f, wanted %+.0f -- %s'
                  % (key, got, want, why))
    # every RESPONSE entry must name a parameter that OWNS a moment, or its
    # sign is attached to nothing and silently never fires
    for key in simplex.RESPONSE:
        if key not in simplex.OWNS:
            bad += 1
            print('   FAIL %s has a response sign but owns no moment' % key)
    if bad:
        print('\n%d failure(s)' % bad)
        return 1
    print('   the arm takes its sign from the gap, in all %d cases' % len(CASES))
    return 0


if __name__ == '__main__':
    sys.exit(main())
