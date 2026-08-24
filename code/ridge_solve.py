#!/usr/bin/env python3
"""Solve TWO entangled parameters at once, instead of one at a time.

WHY THIS EXISTS. b and the value of life both move the drug margin AND the value
of life, so a secant on either alone lands off the answer. Ten measured points
showed it plainly: the b that gives 0.089 total users is 0.0277 at aleph 30 and
0.0098 at aleph 120, and the aleph that gives a value of life of 80 is 37.1 at
b = 0.02 and 27.3 at b = 0.06. Each ridge is a straight line in logs; the answer
is where they cross, and it is not on either ridge taken by itself.

The generation-two centre was built by reading b off the aleph = 120 slice and
aleph off the b = 0.04 slice, which is exactly the mistake this file exists to
stop.
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = re.compile(r'MOMENT\s+(\S+)\s+.*?model=\s*([-+0-9.eEdD]+|NaN)\s+target=\s*([-+0-9.eEdD]+)')
VEC = re.compile(r'^VECTOR\s+(.*)$', re.M)
NAME = re.compile(r'b([0-9.]+)_aleph([0-9.]+)')


def _f(x):
    try:
        return float(x.replace('D', 'E').replace('d', 'e'))
    except ValueError:
        return float('nan')


def measured():
    """(vector, users, vsl, name) for every point on disk.

    THE WHOLE VECTOR, not just the pair. Two points may be compared only if
    everything other than the parameter under test agrees, and that cannot be
    checked from a pair of numbers. The first version of this returned four
    numbers and so lumped three different values of lambda into one slice.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        txt = open(path, errors='replace').read()
        mom = {m.group(1): (_f(m.group(2)), _f(m.group(3))) for m in ROW.finditer(txt)}
        if 'b' not in mom or 'aleph' not in mom:
            continue
        vec = {}
        m = VEC.search(txt)
        if m:
            for tok in m.group(1).split():
                k, _, v = tok.partition('=')
                vec[k] = _f(v)
        else:                                 # older points name the pair instead
            n = NAME.search(os.path.basename(path))
            if not n:
                continue
            vec = {'addiction_scalar_1': float(n.group(1)),
                   'value_of_life': float(n.group(2))}
        out.append((vec, mom['b'][0], mom['aleph'][0], os.path.basename(path)))
    return out


def comparable(a, b, key):
    """May these two points be differenced on `key`?

    They must DECLARE THE SAME PARAMETERS and agree on all of them but this one.
    Requiring the same key set is what keeps a legacy point, which declares two
    parameters, from being paired with a modern one that declares nineteen: the
    seventeen it says nothing about are exactly the seventeen that might differ.
    """
    if set(a) != set(b) or key not in a:
        return False
    if abs(a[key] - b[key]) < 1e-15:
        return False
    return all(abs(a[k] - b[k]) <= 1e-12 * max(1.0, abs(a[k])) for k in a if k != key)


def _bracket(cands, target):
    """The pair that brackets the target, else the two nearest it.

    A SECANT ACROSS A BRACKET INTERPOLATES; ANYTHING ELSE EXTRAPOLATES. These
    responses are flat and then fall off a cliff, so an extrapolation from two
    points on the flat can land anywhere: the drug margin's own history has a
    secant from the flat part putting the crossing at 0.0634 when it was near
    0.0093.
    """
    below = [c for c in cands if c[1] <= target]
    above = [c for c in cands if c[1] > target]
    if below and above:
        return max(below, key=lambda c: c[1]), min(above, key=lambda c: c[1]), True
    s = sorted(cands, key=lambda c: abs(math.log(max(c[1], 1e-12) / target))
               if target > 0 else abs(c[1] - target))
    return s[0], s[1], False


EXTRAPOLATION_LIMIT = 4.0


def _keep(value, x1, x2, bracketed):
    """Refuse a secant that has run away off the flat.

    A slice whose measured points all sit far from the target says almost
    nothing about where the target is. Generation two measured total users of
    0.85, 0.91 and 0.98 across a threefold range of b — a slope of -0.14, which
    put the b that gives 0.089 at two hundred thousand. An answer like that is
    not a weak reading to be down-weighted, it is no reading at all.
    """
    if value != value or value <= 0:
        return False
    if bracketed:
        return True
    lo, hi = min(x1, x2), max(x1, x2)
    return lo / EXTRAPOLATION_LIMIT <= value <= hi * EXTRAPOLATION_LIMIT


def _fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
    return k, my - k * mx


def solve(data, target_users=0.0890, target_vsl=80.0):
    """Where the users ridge and the value-of-life ridge cross.

    Each ridge is built only from pairs that differ in ONE parameter, and each
    pair is chosen to bracket its target where the measured points allow it.
    """
    users_ridge, discarded = [], []
    seen = set()
    for i, (va, ua, _, _) in enumerate(data):
        cands = [(vb['addiction_scalar_1'], ub) for vb, ub, _, _ in data
                 if comparable(va, vb, 'addiction_scalar_1') and ub > 0]
        if ua <= 0 or not cands:
            continue
        cands.append((va['addiction_scalar_1'], ua))
        key = tuple(sorted((k, round(v, 12)) for k, v in va.items()
                           if k != 'addiction_scalar_1'))
        if key in seen:
            continue
        seen.add(key)
        (b1, u1), (b2, u2), bracketed = _bracket(cands, target_users)
        if abs(math.log(u2 / u1)) < 1e-12:
            continue
        k = (math.log(u2) - math.log(u1)) / (math.log(b2) - math.log(b1))
        want = math.exp(math.log(b2) + (math.log(target_users) - math.log(u2)) / k)
        if not _keep(want, b1, b2, bracketed):
            discarded.append(('users', va['value_of_life'], want, k))
            continue
        users_ridge.append((va['value_of_life'], want, k))

    vsl_ridge = []
    seen = set()
    for i, (va, _, wa, _) in enumerate(data):
        cands = [(vb['value_of_life'], wb) for vb, _, wb, _ in data
                 if comparable(va, vb, 'value_of_life') and wb == wb]
        if wa != wa or not cands:
            continue
        cands.append((va['value_of_life'], wa))
        key = tuple(sorted((k, round(v, 12)) for k, v in va.items() if k != 'value_of_life'))
        if key in seen:
            continue
        seen.add(key)
        (a1, v1), (a2, v2), bracketed = _bracket(cands, target_vsl)
        if abs(v2 - v1) < 1e-12:
            continue
        k = (v2 - v1) / (a2 - a1)
        want = a1 + (target_vsl - v1) / k
        if not _keep(want, a1, a2, bracketed):
            discarded.append(('value of life', va['addiction_scalar_1'], want, k))
            continue
        vsl_ridge.append((va['addiction_scalar_1'], want, k))

    if len(users_ridge) < 2 or len(vsl_ridge) < 2:
        return None, users_ridge, vsl_ridge, discarded
    k1, c1 = _fit([math.log(a) for a, _, _ in users_ridge], [math.log(b) for _, b, _ in users_ridge])
    k2, c2 = _fit([math.log(b) for b, _, _ in vsl_ridge], [math.log(a) for _, a, _ in vsl_ridge])
    if abs(1 - k1 * k2) < 1e-9:
        return None, users_ridge, vsl_ridge, discarded
    x = (c1 + k1 * c2) / (1 - k1 * k2)
    return (math.exp(x), math.exp(c2 + k2 * x)), users_ridge, vsl_ridge, discarded


if __name__ == '__main__':
    data = measured()
    cross, u_ridge, v_ridge, dropped = solve(data)
    print('%d point(s) carry both a drug margin and a value of life.' % len(data))
    print('\nusers ridge: the b that gives 0.089 total users')
    for a, b, k in u_ridge:
        print('   aleph %7.2f   slope %7.2f   b     -> %.5f' % (a, k, b))
    print('\nvalue-of-life ridge: the aleph that gives a value of life of 80')
    for b, a, k in v_ridge:
        print('   b     %7.4f   slope %7.2f   aleph -> %.2f' % (b, k, a))
    for which, at, want, k in dropped:
        print('   DISCARDED on the %s ridge at %.4g: slope %.2f puts it at %.4g, '
              'off the measured span' % (which, at, k, want))
    if cross:
        print('\nTHE TWO RIDGES CROSS AT   b = %.5f   aleph = %.2f' % cross)
    else:
        print('\nNot enough matched points yet to cross the ridges.')
