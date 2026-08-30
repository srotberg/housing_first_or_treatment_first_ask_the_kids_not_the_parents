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

# WHAT A PARAMETER OWNS IS STATED ONCE, IN suggest_next.OWNS. This was a
# hand-copied second copy and it drifted the moment lambda_m became
# externally set: OWNS moved the SMI share of the homeless to di_takeup and
# added smi_onset_level for p_m, while this still listed lambda_m and knew
# nothing of either new parameter, so gap_table.py died on KeyError.
WHAT = {k: v[0] for k, v in OWNS.items()}
# Calibrated internally but not free: gamma is tied to theta inside the model as
# 0.28*(1-theta), so it moves when theta does and has no arm of its own.
TIED = {'relative_share_of_housing': ('gamma', 'tied to theta as 0.28*(1-theta)')}
LABEL = {
    'b': 'total drug users', 'lambda_d': 'disordered share of users',
    'theta': 'drug spending share', 'aleph': 'value of life / income',
    'h_1': 'homelessness rate', 'beta': 'wealth over output',
    'omega_l': 'labour supply / hours', 'tau_l': 'average labour income tax',
    'sigma_y': 'bottom half earnings share', 'pi_eu': 'unemployment rate',
    'kappa_ued': 'unemployment given SUD', 'kappa_uem': 'employment given SMI',
    'lambda_m': 'SMI share of the homeless', 'p_m': 'SMI share of the population', 'omega': 'use rise, child term off', 'pi_V': 'eligibles with a voucher',
    'tau_u': 'treatment take up', 'delta_d': 'child SUD ratio',
    'delta_h': 'child homelessness ratio', 'h_2': 'share in smallest unit',
    'h_3': 'share in largest unit',
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
    for key, (short, why) in TIED.items():
        if short in mom:
            tgt, got = targets.get(short, float('nan')), mom[short]
            gap = (got - tgt) / abs(tgt) if tgt else float('nan')
            rows.append((-abs(gap), key, short, vec.get(key, float('nan')),
                         tgt, got, '%+.0f%%' % (100 * gap), why))
    for _, key, short, val, tgt, got, gap, note in sorted(rows):
        print('%-52s %11.5g   %-27s %11.5g %11s %9s   %s'
              % (key, val, '%-9s %s' % (short, LABEL.get(short, '')), tgt,
                 ('%.5g' % got) if got is not None and got == got else '-', gap, note))

    got = score_points.loss(mt)
    n_int = len(rows)
    print('-' * 145)
    print('%d internally calibrated parameters shown. Loss over the %d moments '
          'this point reported: %.3f' % (n_int, got[1], got[0]))
    # GENERATED FROM THE DICT IT DESCRIBES. This sentence and the one in
    # score_points.py were both typed, and both still said 2x on three moments
    # after lambda_m became the fourth.
    by_w = {}
    for nm, w in sorted(score_points.WEIGHT.items()):
        by_w.setdefault(w, []).append(nm)
    how = ', '.join('%gx on %s' % (w, ' and '.join(ns))
                    for w, ns in sorted(by_w.items(), reverse=True))
    print('The loss is the mean absolute RELATIVE gap, weighted %s, capped at '
          '%g per moment so a ratio whose denominator empties cannot dominate '
          'it.' % (how, score_points.CAP))
    return 0


if __name__ == '__main__':
    sys.exit(main())
