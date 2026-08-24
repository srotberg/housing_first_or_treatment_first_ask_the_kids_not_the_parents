#!/usr/bin/env python3
"""Decide the next generation of points from the ones already measured.

THE LOOP THE AUTHOR ASKED FOR. Score every measured point, take the secant for
each parameter from pairs that differ in it alone, form a centre from those
readings, and emit a batch: the centre itself plus one-at-a-time perturbations
of every parameter. That is a pattern search with a secant step, and the
perturbations are not decoration -- they are what GUARANTEES the next round has
a matched pair for every parameter, so the round after it can take a secant on
each. A generation of points all differing in several parameters at once
measures a surface nobody can read.

WHAT IT WILL NOT DO. It prints a batch; it does not spawn. Spawning a container
is an action with a cost, and the judgement of when a suggestion is nonsense --
a secant through a cliff can return a negative b -- belongs with someone who can
see the whole run. Suggestions outside a parameter's admissible range are
clamped and the clamp is announced.
"""
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suggest_next as S

# parameter -> (admissible low, admissible high, relative step for the pair)
RANGE = {'b': (1e-4, 0.5, 0.5), 'aleph': (1.0, 500.0, 0.4),
         'lam': (0.05, 20.0, 0.6), 'th': (0.05, 0.7, 0.25),
         'h': (0.01, 0.9, 0.4)}


def secants(pts):
    """parameter -> the suggestions its matched pairs give, interpolated."""
    out = {}
    for key, (moment, target) in S.OWNS.items():
        vals = []
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
                s, _ = S.interp(a[key], ya, b[key], yb, target)
                lo, hi = RANGE[key][0], RANGE[key][1]
                if s is not None and lo <= s <= hi:
                    vals.append(s)
        if vals:
            out[key] = statistics.median(vals)
    return out


def main():
    pts = S.points()
    if not pts:
        print('no points measured yet')
        return 0

    # the best measured point is the fallback centre, one coordinate at a time
    scored = subprocess.run([sys.executable, os.path.join(HERE, 'score_points.py')],
                            capture_output=True, text=True).stdout
    best = None
    for line in scored.splitlines():
        if line.strip().startswith('1 '):
            best = line.split()[-1]
            break
    centre = dict(pts[0][0])
    if best:
        for vec, _, name in pts:
            if name == best:
                centre = dict(vec)
    print(f'best measured point: {best}')
    print(f'  its vector: ' + '  '.join(f'{k}={v:g}' for k, v in sorted(centre.items())))

    sug = secants(pts)
    print('\nsecant readings, median over matched pairs inside the admissible range:')
    for k, v in sorted(sug.items()):
        lo, hi, _ = RANGE[k]
        c = min(max(v, lo), hi)
        flag = '' if abs(c - v) < 1e-12 else f'   CLAMPED from {v:g}'
        print(f'  {k:<6s} {centre[k]:>10g}  ->  {c:>10.5g}{flag}')
        centre[k] = c
    missing = [k for k in RANGE if k not in sug]
    if missing:
        print(f'  no matched pair yet for: {", ".join(sorted(missing))} '
              f'(kept at the best point\'s value)')

    print('\nNEXT GENERATION, as run_one_point.sh arguments (b aleph lambda theta h1):')
    batch = [tuple(centre[k] for k in ('b', 'aleph', 'lam', 'th', 'h'))]
    for k in ('b', 'aleph', 'lam', 'th', 'h'):
        lo, hi, step = RANGE[k]
        for mult in (1 - step, 1 + step):
            v = dict(centre)
            v[k] = min(max(centre[k] * mult, lo), hi)
            if abs(v[k] - centre[k]) > 1e-12:
                batch.append(tuple(v[x] for x in ('b', 'aleph', 'lam', 'th', 'h')))
    seen, out = set(), []
    for t in batch:
        key = tuple(round(x, 8) for x in t)
        if key not in seen:
            seen.add(key)
            out.append(t)
    for t in out:
        print('  bash code/run_one_point.sh ' + ' '.join(f'{x:g}' for x in t))
    print(f'\n{len(out)} points: the centre, then each parameter moved alone so the '
          f'round after this\nhas a matched pair for every one of them.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
