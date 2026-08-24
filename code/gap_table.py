#!/usr/bin/env python3
"""The whole calibration on one page: parameter, value, moment, target, gap.

Every internally calibrated parameter appears, with the value it was run at, the
moment it owns, what the data says that moment should be, what the model
produced, and the gap as a percentage of the target. Nothing is left out and
nothing is summarised away: a parameter whose moment could not be measured says
so, rather than being dropped from the table.

By default it reads the best-scoring point on disk. Give it a filename to read
that one instead.
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from converge import GATE, RATIO, read                     # noqa: E402
from suggest_next import OWNS, points                      # noqa: E402
import score_points                                        # noqa: E402

WHAT = {
    'addiction_scalar_1': 'b', 'lambda_addiction': 'lambda_d',
    'relative_share_of_addiction_1': 'theta', 'value_of_life': 'aleph',
    'size_homelessness': 'h_1', 'discount_factor': 'beta',
    'relative_share_of_leisure': 'omega_l', 'labor_income_tax_rate': 'tau_l',
    'sd_permanent_productivity': 'sigma_y', 'probability_becoming_unemployed': 'pi_eu',
    'multiple_of_probabilities_of_employment_if_addicted': 'kappa_ued',
    'kappa_uem': 'kappa_uem', 'lambda_m': 'lambda_m',
    'probability_of_voucher_benchmark_used': 'pi_V',
    'utility_cost_of_treatment': 'tau_u', 'penalty_child_addicted': 'delta_d',
    'penalty_child_homeless': 'delta_h',
    'smallest_rental_relative_to_lowest_income': 'h_2',
    'largest_house_size': 'h_4',
}
LABEL = {
    'b': 'total drug users', 'lambda_d': 'disordered share of users',
    'theta': 'drug spending share', 'aleph': 'value of life / income',
    'h_1': 'homelessness rate', 'beta': 'wealth over output',
    'omega_l': 'labour supply / hours', 'tau_l': 'average labour income tax',
    'sigma_y': 'bottom half earnings share', 'pi_eu': 'unemployment rate',
    'kappa_ued': 'unemployment given SUD', 'kappa_uem': 'employment given SMI',
    'lambda_m': 'SMI share of the homeless', 'pi_V': 'eligibles with a voucher',
    'tau_u': 'treatment take up', 'delta_d': 'child SUD ratio',
    'delta_h': 'child homelessness ratio', 'h_2': 'share in smallest unit',
    'h_4': 'share in largest unit',
}


def main():
    by_name = {v[2]: v for v in points()}
    paths = sorted(glob.glob(os.path.join(HERE, 'points', '*.txt')))
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        want = os.path.basename(sys.argv[1])
        paths = [p for p in paths if os.path.basename(p) == want]
        if not paths:
            print('no such point: %s' % want)
            return 1
        path = paths[0]
    else:
        scored = []
        for p in paths:
            _head, mt = score_points.read(p)
            got = score_points.loss(mt)
            if got:
                scored.append((got[0], p))
        if not scored:
            print('no points measured yet')
            return 1
        scored.sort()
        path = scored[0][1]

    name = os.path.basename(path)
    _head, mt = score_points.read(path)
    targets = {k: v[1] for k, v in mt.items()}
    mom = {k: v[0] for k, v in mt.items()}
    if name not in by_name:
        print('point %s carries no vector' % name)
        return 1
    vec = by_name[name][0]

    print('point %s\n' % name)
    print('%-52s %11s   %-27s %11s %11s %9s   %s'
          % ('parameter', 'value', 'moment it owns', 'target', 'model', 'gap', 'note'))
    print('-' * 145)
    rows = []
    for key, short in WHAT.items():
        if key not in vec:
            continue
        tgt = RATIO[key][2] if key in RATIO else targets.get(short, OWNS[key][1])
        got = read(mom, key)
        note = ''
        if key in GATE:
            gm, gt, tol = GATE[key]
            g = mom.get(gm)
            if g is None or g <= 0 or not (gt / tol <= g <= gt * tol):
                note = 'not readable yet: %s is %s' % (
                    gm, ('%.3g' % g) if g is not None else 'missing')
        if got is None or got != got:
            rows.append((9e9, key, short, vec[key], tgt, got, 'no model value', note))
            continue
        gap = (got - tgt) / abs(tgt) if tgt else float('nan')
        rows.append((-abs(gap), key, short, vec[key], tgt, got, '%+.0f%%' % (100 * gap), note))
    for _, key, short, val, tgt, got, gap, note in sorted(rows):
        print('%-52s %11.5g   %-27s %11.5g %11s %9s   %s'
              % (key, val, '%-9s %s' % (short, LABEL.get(short, '')), tgt,
                 ('%.5g' % got) if got is not None and got == got else '-', gap, note))
    return 0


if __name__ == '__main__':
    sys.exit(main())
