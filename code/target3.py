#!/usr/bin/env python3
"""Drive four instruments at the author's three moments, and nothing else.

THE AUTHOR'S ASSIGNMENT, 6 September, in their own words:

    "mass of bottom productivity --> share of homeless employed. 2nd bottom
    productivity ---> homelessness share. h2 ---> share of cost burdened
    households."

and, when the reply was that the three could not be had together:

    "i dont understand why we cant get all these moments that i want... we have
    so many levers now", "the mass of the bottom productivity, h1, h2,
    productivity of second lowest productivity, what else can you need? and we
    just need 3 things".

They are right that it is over-identified: four instruments, three moments. What
was missing was not a lever but a SEARCH -- every arm run on 6 September moved
one coordinate at a time off a hand-chosen base, which is how the second node's
level came to sit four per cent under a threshold for six hours without anyone
noticing. This drives all four together.

WHY IT IS SEPARATE FROM next_batch.py. That gate scores twenty-odd moments and
ranks base points on a minimax over all of them, so it anchors wherever h_1's
enormous gap is smallest and steps every instrument it owns. This is a three-
moment problem with four instruments and it wants neither behaviour: the other
moments are reported but not scored, and only these four instruments move.

THE FIT IS LOG-LINEAR AND LOCAL, and both words matter. Local because the
response is not monotone anywhere in this block -- the rung turns on h_1 below
0.020, the 30 per cent burden share turns at 0.090, and psi's effect on
emp_homeless changes SIGN between 0.7 and 0.8 -- so a global fit would average
a turning response into a slope that describes nothing. Log because every
instrument and every moment here is a positive quantity whose useful range spans
factors rather than differences.

WHAT IT WILL NOT DO. It will not report that the targets are unreachable. Six
times on 6 September a conclusion of that kind was drawn from a sweep that had
not sampled the region where the instrument acts, and five of them were wrong.
If the step is small or the fit is poor it says so and widens; the author decides
what is unreachable.
"""
import glob, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The three moments, with the author's targets. h_2 is the cost-burden headcount
# they named as "10.1% cost burdened households"; burden50 is the same idea
# measured on income inside the cheapest unit and is reported, not targeted.
TARGETS = {'h_1': 0.00399, 'h_2': 0.101, 'emp_homeless': 0.46}

# The four instruments, with the bounds the Fortran clamps them to. Exceeding a
# clamp is worse than stopping at it: the handover silently truncates and the
# point that comes back is not the point that was asked for.
INSTRUMENTS = {
    'kkk_s_deviation_bottom':                    (1.0, 6.0),
    'bottom_productivity_level':                 (0.01, 3.0),
    'smallest_rental_relative_to_lowest_income':  (0.005, 0.40),
    'size_homelessness':                         (0.0001, 0.20),
}

# Reported beside the three, never scored. gamma and the untargeted burden lines
# are how a step that fixes the three by wrecking the housing market gets caught.
WATCH = ['gamma', 'burden50', 'b', 'beta', 'pi_eu']


def model_hash():
    import hashlib
    p = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
    return hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]


def load(tag_filter=None):
    """Every archived point on the CURRENT model, as (tag, vector, moments)."""
    h = model_hash()
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, 'points', 'point_*.txt'))):
        if '.FAILED' in f:
            continue
        s = open(f, errors='replace').read()
        m = re.search(r'^MODEL (\S+)', s, re.M)
        if not m or m.group(1) != h:
            continue
        v = re.search(r'^VECTOR (.*)$', s, re.M)
        if not v:
            continue
        vec = {}
        for tok in v.group(1).split():
            if '=' in tok:
                k, val = tok.split('=', 1)
                if re.fullmatch(r'[a-z_0-9]+', k):
                    try:
                        vec[k] = float(val)
                    except ValueError:
                        pass
        mom = {}
        for name, val in re.findall(
                r'MOMENT\s+(\S+)\s+.*?model=\s*([-\dEe.+]+)', s):
            try:
                mom[name] = float(val)
            except ValueError:
                pass
        out.append((os.path.basename(f)[6:16], vec, mom))
    return out


def best(points):
    """The point closest to the three targets on the WORST relative gap.

    Minimax rather than sum of squares, and over these three only. The sum of
    squares is what made next_batch.py anchor on a wrecked corner: h_1's gap was
    so large that a point which shrank it by destroying the cost burden won on
    the total. The worst-gap rule cannot be bought that way.
    """
    scored = []
    for tag, vec, mom in points:
        if not all(k in mom for k in TARGETS):
            continue
        if not all(k in vec for k in INSTRUMENTS):
            continue
        gaps = {k: abs(mom[k] - t) / t for k, t in TARGETS.items()}
        scored.append((max(gaps.values()), tag, vec, mom, gaps))
    scored.sort(key=lambda r: r[0])
    return scored


def slopes(points, param, moment, lo=None, hi=None):
    """d log(moment) / d log(param), from pairs that differ ONLY in param.

    A CONTROLLED PAIR OR NOTHING. Regressing across points that differ in
    several coordinates gives a number that is not the derivative of anything,
    and three of 6 September's wrong directions came from exactly that. Two
    points qualify only if every other instrument matches to a relative 1e-9.
    """
    rows = []
    for i, (t1, v1, m1) in enumerate(points):
        for (t2, v2, m2) in points[i + 1:]:
            if param not in v1 or param not in v2:
                continue
            if v1[param] <= 0 or v2[param] <= 0 or v1[param] == v2[param]:
                continue
            if moment not in m1 or moment not in m2:
                continue
            if m1[moment] <= 0 or m2[moment] <= 0:
                continue
            others = [k for k in v1 if k != param]
            same = True
            for k in others:
                a, b = v1.get(k), v2.get(k)
                if a is None or b is None:
                    same = False
                    break
                if abs(a - b) > 1e-9 * max(abs(a), abs(b), 1.0):
                    same = False
                    break
            if not same:
                continue
            if lo is not None and not (lo <= v1[param] <= hi and lo <= v2[param] <= hi):
                continue
            s = (math.log(m2[moment] / m1[moment]) /
                 math.log(v2[param] / v1[param]))
            rows.append((s, t1, t2, v1[param], v2[param]))
    return rows


def main():
    pts = load()
    print(f'MODEL {model_hash()}   {len(pts)} points in this economy')
    if not pts:
        print('  nothing to fit. Seed first: a point carrying all four '
              'instruments and all three moments.')
        return 2

    scored = best(pts)
    if not scored:
        print('  no point carries all three moments AND all four instruments.')
        return 2

    worst, tag, vec, mom, gaps = scored[0]
    print(f'\nBASE point_{tag}   worst of the three = {100*worst:.1f} per cent\n')
    print(f'  {"moment":<14}{"model":>12}{"target":>12}{"gap":>10}')
    for k, t in TARGETS.items():
        print(f'  {k:<14}{mom[k]:12.5f}{t:12.5f}{100*(mom[k]-t)/t:+9.1f}%')
    print(f'\n  {"instrument":<44}{"value":>12}')
    for k in INSTRUMENTS:
        print(f'  {k:<44}{vec[k]:12.5f}')
    if WATCH:
        seen = [k for k in WATCH if k in mom]
        if seen:
            print('\n  watched, not scored: ' +
                  '  '.join(f'{k}={mom[k]:.4f}' for k in seen))

    print('\nCONTROLLED PAIRS in this economy, d log(moment) / d log(instrument):')
    any_slope = False
    for p in INSTRUMENTS:
        for q in TARGETS:
            rows = slopes(pts, p, q)
            if not rows:
                continue
            any_slope = True
            ss = sorted(r[0] for r in rows)
            med = ss[len(ss) // 2]
            turns = ' TURNS' if ss[0] * ss[-1] < 0 else ''
            print(f'  {p:<44}{q:<14}{med:+8.2f}  '
                  f'from {len(rows)} pair(s), range [{ss[0]:+.2f}, {ss[-1]:+.2f}]{turns}')
    if not any_slope:
        print('  none. Every archived point differs in more than one instrument,')
        print('  so nothing here is a derivative. Run one-coordinate arms first.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
