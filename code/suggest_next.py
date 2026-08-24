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

# parameter in the point's tag -> the moment it owns, and that moment's target
OWNS = {
    'b':     ('b',        0.0890),
    'lam':   ('lambda_d', 0.0368),
    'th':    ('theta',    0.1620),
    'aleph': ('aleph',   80.0),
    'h':     ('h_1',      0.00399),
}
TAG = re.compile(r'point\s+b([0-9.eE+-]+)_aleph([0-9.eE+-]+)_lam([0-9.eE+-]+)'
                 r'_th([0-9.eE+-]+)_h([0-9.eE+-]+)')
ROW = re.compile(r'MOMENT\s+(\S+)\s+.*?model=\s*([-+0-9.eEdD]+)\s+target=\s*([-+0-9.eEdD]+)')


def _f(x):
    return float(str(x).replace('D', 'E').replace('d', 'e'))


def points():
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        txt = open(path, errors='replace').read()
        m = TAG.search(txt)
        if not m:
            continue
        vec = dict(zip(('b', 'aleph', 'lam', 'th', 'h'), (_f(g) for g in m.groups())))
        mom = {}
        for r in ROW.finditer(txt):
            try:
                mom[r.group(1)] = _f(r.group(2))
            except ValueError:
                pass
        if mom:
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
                if abs(a[key] - b[key]) < 1e-15:
                    continue
                if any(abs(a[k] - b[k]) > 1e-15 for k in a if k != key):
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
