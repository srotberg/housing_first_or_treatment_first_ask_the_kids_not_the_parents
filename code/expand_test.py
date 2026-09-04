"""Adversarial checks on expand.py's direction call, run without the model.

The whole value of expand.py is getting the DIRECTION right, and a sign error
there is worse than no tool at all: it would spend hours sampling away from the
answer while reporting that coverage was being fixed. So the direction logic is
tested against hand-built rays, including the two real ones this was written for.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import expand as E

fails = []


def ray(xs, ys, key='m'):
    return [(x, f't{i}', {key: (y, 0.0)}) for i, (x, y) in enumerate(zip(xs, ys))]


def check(name, got, want):
    if got != want:
        fails.append(f'{name}: got {got}, want {want}')
    print(f'  {"ok  " if got == want else "FAIL"} {name:<52} {got}')


# THE REAL sigma_y CASE. kkk_sigma_scale 2.20949 -> 3.09114 sends the bottom
# half's income share 0.10337 -> 0.03536, and the target 0.172 is ABOVE both.
# The slope is negative, so the parameter has to come DOWN. The author said the
# same thing in words on 4 September; if this test ever says UP, the tool is
# lying about the one case it was built for.
v, d = E.direction(ray([2.20949, 2.6, 3.09114], [0.10337, 0.070, 0.03536]), 'm', 0.172)
check('sigma_y: target above a falling ray -> DOWN', v, 'DOWN')

v, _ = E.direction(ray([1.0, 2.0, 3.0], [0.10, 0.15, 0.20]), 'm', 0.30)
check('target above a rising ray -> UP', v, 'UP')

v, _ = E.direction(ray([1.0, 2.0, 3.0], [0.10, 0.15, 0.20]), 'm', 0.05)
check('target below a rising ray -> DOWN', v, 'DOWN')

v, _ = E.direction(ray([1.0, 2.0, 3.0], [0.20, 0.15, 0.10]), 'm', 0.05)
check('target below a falling ray -> UP', v, 'UP')

v, d = E.direction(ray([1.0, 2.0, 3.0], [0.10, 0.15, 0.20]), 'm', 0.16)
check('target inside the ray -> BRACKETED', v, 'BRACKETED')
check('  and the crossing interval is the right one', (d['x0'], d['x1']), (2.0, 3.0))

v, _ = E.direction(ray([1.0, 2.0], [0.1, 0.2]), 'm', 0.9)
check('two points is not a ray -> THIN', v, 'THIN')

# A NON-MONOTONE RAY MUST BE FLAGGED, not averaged. The measured kkk points near
# 2.21-2.26 rise while the clean pair to 3.09 falls, so this shape is real.
v, d = E.direction(ray([1.0, 2.0, 3.0, 4.0], [0.10, 0.18, 0.12, 0.05]), 'm', 0.30)
check('non-monotone ray -> flagged', d['monotone'], False)

# EXTENSION STOPS AT THE BOUND rather than inventing points outside it.
check('extend at the upper bound is empty', E.extend(4.0, 0.8, 4.0, True), [])
check('extend at the lower bound is empty', E.extend(0.8, 0.8, 4.0, False), [])
x = E.extend(2.20949, 0.8, 4.0, False)
check('extend down stays inside the bounds', all(0.8 <= t < 2.20949 for t in x), True)
check('  and reaches the bound', abs(min(x) - 0.8) < 1e-9, True)
x = E.extend(0.0122, 1e-06, 0.5, True)
check('extend up from a small value reaches its bound',
      abs(max(x) - 0.5) < 1e-9, True)

print()
if fails:
    print('FAILURES:')
    for f in fails:
        print('  ' + f)
    raise SystemExit(1)
print('  all direction checks pass')
