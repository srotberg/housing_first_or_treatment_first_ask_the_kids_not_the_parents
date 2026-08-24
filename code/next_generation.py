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

# parameter -> (admissible low, admissible high, relative step for the pair).
# The bounds are the Fortran's own clamps where it has them, so a suggestion
# that is clamped here would have been clamped there anyway, silently.
RANGE = {
    'addiction_scalar_1':                    (1e-4,   0.5,   0.5),
    'value_of_life':                         (1.0,    500.0, 0.4),
    'lambda_addiction':                      (0.05,   20.0,  0.6),
    'relative_share_of_addiction_1':         (0.05,   0.70,  0.25),
    'size_homelessness':                     (0.01,   0.90,  0.4),
    'discount_factor':                       (0.90,   1.02,  0.01),
    'relative_share_of_leisure':             (0.5,    20.0,  0.2),
    'labor_income_tax_rate':                 (0.1,    2.0,   0.2),
    'sd_permanent_productivity':             (0.3,    3.0,   0.15),
    'probability_becoming_unemployed':       (1e-4,   0.5,   0.5),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 20.0, 0.4),
    'kappa_uem':                             (1.0,    40.0,  0.5),
    'lambda_m':                              (1e-3,   0.5,   0.5),
    'probability_of_voucher_benchmark_used': (1e-4,   1.0,   0.5),
    'utility_cost_of_treatment':             (0.0,    10.0,  0.5),
    'penalty_child_addicted':                (0.0,    0.40,  0.3),
    'penalty_child_homeless':                (0.0,    0.40,  0.3),
    'smallest_rental_relative_to_lowest_income': (5e-4, 10.0, 0.4),
    'largest_house_size':                    (0.02,   1.0,   0.3),
}
ORDER = list(RANGE)


def secants(pts):
    """parameter -> the suggestions its matched pairs give, interpolated."""
    out = {}
    for key, (moment, target) in S.OWNS.items():
        vals = []
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                a, b = pts[i][0], pts[j][0]
                # ONLY KEYS BOTH POINTS DEFINE. The early points carry a
                # partial vector, recovered from their filename, and demanding
                # equality on a key one of them never recorded dropped every
                # pair they were in.
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

    print('\nNEXT GENERATION, as run_one_point.sh command lines:')
    keys = [k for k in ORDER if k in centre]
    batch = [tuple(centre[k] for k in keys)]
    for k in keys:
        lo, hi, step = RANGE[k]
        for mult in (1 - step, 1 + step):
            v = dict(centre)
            v[k] = min(max(centre[k] * mult, lo), hi)
            if abs(v[k] - centre[k]) > 1e-12:
                batch.append(tuple(v[x] for x in keys))
    seen, out = set(), []
    for t in batch:
        key = tuple(round(x, 8) for x in t)
        if key not in seen:
            seen.add(key)
            out.append(t)
    for t in out:
        print('  bash code/run_one_point.sh ' +
              ' '.join(f'{k}={x:g}' for k, x in zip(keys, t)))
    print(f'\n{len(out)} points: the centre, then each parameter moved alone so the '
          f'round after this\nhas a matched pair for every one of them.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
