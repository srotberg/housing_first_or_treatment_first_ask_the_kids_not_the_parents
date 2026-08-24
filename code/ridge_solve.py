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
    """(b, aleph, users, vsl) for every point on disk."""
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
        b = vec.get('addiction_scalar_1')
        a = vec.get('value_of_life')
        if b is None or a is None:            # older points name the pair instead
            n = NAME.search(os.path.basename(path))
            if not n:
                continue
            b, a = float(n.group(1)), float(n.group(2))
        out.append((b, a, mom['b'][0], mom['aleph'][0]))
    return out


def _fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
    return k, my - k * mx


def solve(data, target_users=0.0890, target_vsl=80.0, fallback_slope=-3.49):
    """Where the users ridge and the value-of-life ridge cross."""
    alephs = sorted({a for _, a, _, _ in data})
    bs = sorted({b for b, _, _, _ in data})

    users_ridge = []
    for a in alephs:
        s = sorted((b, u) for b, aa, u, _ in data if aa == a and u > 0)
        if not s:
            continue
        b2, u2 = s[-1]
        if len(s) >= 2:
            b1, u1 = s[-2]
            k = (math.log(u2) - math.log(u1)) / (math.log(b2) - math.log(b1))
        else:
            k = fallback_slope          # the slope the well-populated slice measured
        users_ridge.append((a, math.exp(math.log(b2) + (math.log(target_users) - math.log(u2)) / k), k))

    vsl_ridge = []
    for b in bs:
        s = sorted((a, v) for bb, a, _, v in data if bb == b and v == v)
        if len(s) < 2:
            continue
        (a1, v1), (a2, v2) = s[0], s[1]
        if v2 == v1:
            continue
        k = (v2 - v1) / (a2 - a1)
        vsl_ridge.append((b, a1 + (target_vsl - v1) / k, k))

    if len(users_ridge) < 2 or len(vsl_ridge) < 2:
        return None, users_ridge, vsl_ridge
    k1, c1 = _fit([math.log(a) for a, _, _ in users_ridge], [math.log(b) for _, b, _ in users_ridge])
    k2, c2 = _fit([math.log(b) for b, _, _ in vsl_ridge], [math.log(a) for _, a, _ in vsl_ridge])
    if abs(1 - k1 * k2) < 1e-9:
        return None, users_ridge, vsl_ridge
    x = (c1 + k1 * c2) / (1 - k1 * k2)
    return (math.exp(x), math.exp(c2 + k2 * x)), users_ridge, vsl_ridge


if __name__ == '__main__':
    data = measured()
    cross, u_ridge, v_ridge = solve(data)
    print('%d point(s) carry both a drug margin and a value of life.' % len(data))
    print('\nusers ridge: the b that gives 0.089 total users')
    for a, b, k in u_ridge:
        print('   aleph %7.2f   slope %7.2f   b     -> %.5f' % (a, k, b))
    print('\nvalue-of-life ridge: the aleph that gives a value of life of 80')
    for b, a, k in v_ridge:
        print('   b     %7.4f   slope %7.2f   aleph -> %.2f' % (b, k, a))
    if cross:
        print('\nTHE TWO RIDGES CROSS AT   b = %.5f   aleph = %.2f' % cross)
    else:
        print('\nNot enough matched points yet to cross the ridges.')
