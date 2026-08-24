#!/usr/bin/env python3
"""Interpolate each parameter to its target, from pairs of measured points.

THE AUTHOR'S RULE, MECHANISED. If h_1 = 0.2 gives homelessness of 1 per cent
and h_1 = 0.1 gives 0.2 per cent, the value that gives 0.399 per cent is read
off the two rather than guessed at. That is a secant step, and a grid gives one
for free wherever two points differ in exactly ONE parameter: everything else
is pinned, so the pair isolates that parameter's response.

WHY LOG-LOG BY DEFAULT. These responses are not linear in the level. Total users
went 0.947, 0.759, 0.000158 across b of 0.05, 0.06, 0.12: flat, then a cliff.
Interpolating that linearly put the crossing at 0.0634 and it was nowhere near.
In logs the same three points are far better behaved, and a log reading is the
right default for a rate that spans orders of magnitude. The fallback to linear
is for pairs where either value is non positive, where logs do not exist.

WHAT IT WILL NOT DO. It suggests; it does not act. A secant through two points
of a response that is flat and then falls off a cliff can land anywhere, so
every suggestion is printed with the two points it came from and the span they
bracket, and a suggestion that extrapolates far outside that span is marked.
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# EVERY CALIBRATED PARAMETER, ITS MOMENT AND THAT MOMENT'S TARGET.
#
# A search that can only move five parameters is not a search of the space.
# Twenty four are calibrated and each owns a moment, so each gets a secant the
# moment a matched pair exists for it. The names on the left are the Fortran
# parameter names run_one_point.sh accepts; the names in the middle are what
# print_all_moments labels the moment.
OWNS = {
    'addiction_scalar_1':                    ('b',        0.0890),
    'lambda_addiction':                      ('lambda_d', 0.0368),
    'relative_share_of_addiction_1':         ('theta',    0.1620),
    'value_of_life':                         ('aleph',   80.0),
    'size_homelessness':                     ('h_1',      0.00399),
    'discount_factor':                       ('beta',     3.0),
    'relative_share_of_leisure':             ('omega_l',  0.400),
    'labor_income_tax_rate':                 ('tau_l',    0.224),
    'sd_permanent_productivity':             ('sigma_y',  0.172),
    'probability_becoming_unemployed':       ('pi_eu',    0.0485),
    'multiple_of_probabilities_of_employment_if_addicted':
                                             ('kappa_ued', 0.1625),
    'kappa_uem':                             ('kappa_uem', 0.300),
    'lambda_m':                              ('lambda_m', 0.250),
    'probability_of_voucher_benchmark_used': ('pi_V',     0.266),
    'utility_cost_of_treatment':             ('tau_u',    0.245),
    'penalty_child_addicted':                ('delta_d',  3.00),
    'penalty_child_homeless':                ('delta_h',  2.10),
    'smallest_rental_relative_to_lowest_income': ('h_2',  0.132065),
    'largest_house_size':                    ('h_4',      0.626723),
}
VEC = re.compile(r'^VECTOR\s+(.*)$', re.M)
ROW = re.compile(r'MOMENT\s+(\S+)\s+.*?model=\s*([-+0-9.eEdD]+)\s+target=\s*([-+0-9.eEdD]+)')
def _f(x):
    return float(str(x).replace('D', 'E').replace('d', 'e'))


def points():
    """(vector, moments, filename) for every measured point.

    THE VECTOR IS READ FROM THE POINT FILE, not from its name. The filename is a
    hash now, because a name that encodes nineteen parameters is unreadable and
    a name that encodes five silently drops the rest.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        txt = open(path, errors='replace').read()
        m = VEC.search(txt)
        vec = {}
        if m:
            for tok in m.group(1).split():
                if '=' in tok:
                    k, v = tok.split('=', 1)
                    try:
                        vec[k] = _f(v)
                    except ValueError:
                        pass
        else:
            # THE EARLY POINTS CARRY THEIR VECTOR ONLY IN THEIR NAME, because
            # their workers were given the recipe in a prompt and wrote no
            # header. Recover what is there so they still feed the secants.
            got = dict(re.findall(r'(b|aleph|lam|th|h)([0-9]+(?:\.[0-9]+)?)',
                                  os.path.basename(path)))
            if 'b' in got:
                vec['addiction_scalar_1'] = _f(got['b'])
            if 'aleph' in got:
                vec['value_of_life'] = _f(got['aleph'])
            vec['lambda_addiction'] = _f(got.get('lam', 1.5))
            vec['relative_share_of_addiction_1'] = _f(got.get('th', 0.38))
            vec['size_homelessness'] = _f(got.get('h', 0.42))
        mom = {}
        for r in ROW.finditer(txt):
            try:
                mom[r.group(1)] = _f(r.group(2))
            except ValueError:
                pass
        if mom and vec:
            out.append((vec, mom, os.path.basename(path)))
    return out


def interp(x1, y1, x2, y2, target):
    """The parameter value that hits target, in logs where they exist."""
    if min(x1, x2, y1, y2, target) > 0 and abs(math.log(y2) - math.log(y1)) > 1e-12:
        f = (math.log(target) - math.log(y1)) / (math.log(y2) - math.log(y1))
        return math.exp(math.log(x1) + f * (math.log(x2) - math.log(x1))), 'log-log'
    if abs(y2 - y1) < 1e-15:
        return None, None
    f = (target - y1) / (y2 - y1)
    return x1 + f * (x2 - x1), 'linear'


def main():
    pts = points()
    if len(pts) < 2:
        print(f'{len(pts)} point(s) measured; a secant needs two that differ in one '
              f'parameter')
        return 0
    print(f'{len(pts)} points measured\n')
    found = False
    for key, (moment, target) in OWNS.items():
        pairs = []
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                a, b = pts[i][0], pts[j][0]
                if key not in a or key not in b:
                    continue
                if abs(a[key] - b[key]) < 1e-15:
                    continue
                shared = set(a) & set(b)
                if any(abs(a[k] - b[k]) > 1e-15 for k in shared if k != key):
                    continue
                ya, yb = pts[i][1].get(moment), pts[j][1].get(moment)
                if ya is None or yb is None:
                    continue
                pairs.append((a[key], ya, b[key], yb, pts[i][2], pts[j][2]))
        if not pairs:
            continue
        found = True
        print(f'{key} -> {moment}, target {target:g}')
        for x1, y1, x2, y2, f1, f2 in pairs:
            sug, how = interp(x1, y1, x2, y2, target)
            if sug is None:
                print(f'   {x1:g} gave {y1:.6g}, {x2:g} gave {y2:.6g}: '
                      f'the moment did not move, no secant')
                continue
            lo, hi = min(x1, x2), max(x1, x2)
            flag = '' if lo <= sug <= hi else '   EXTRAPOLATED beyond the pair'
            print(f'   {x1:g} gave {y1:.6g}, {x2:g} gave {y2:.6g}  ->  '
                  f'suggest {key} = {sug:.6g}  ({how}){flag}')
        print()
    if not found:
        print('no pair yet differs in exactly one parameter; the grid needs a '
              'matched pair before a secant can be taken')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
