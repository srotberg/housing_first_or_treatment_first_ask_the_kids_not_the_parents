#!/usr/bin/env python3
"""The design that rebuilds a Jacobian from nothing, around the new baseline.

WHY A ONE-AT-A-TIME DESIGN AND NOT A SIMPLEX. Discarding the archive discards
the Jacobian with it: every fit in line_search.py and alternate.py reads the
measured points, and there are none on the corrected grid. What the fit needs is
a centre plus one arm per parameter -- exactly the structure jacobian.assemble
looks for -- so twenty-one points buy a full derivative matrix, and every
subsequent round can then move all twenty parameters together instead of
crawling one coordinate at a time.

THE STEP IS ONE FACTOR FOR EVERY PARAMETER, IN LOGS. A derivative wants a step
small enough to be local and large enough to clear the solver's noise, which two
runs of the same binary put at 2.5e-5 relative. A factor of 1.25 is four orders
above that and stays inside the region where the response has been linear in
every fit so far. Scaling the step to how wrong each moment is -- the old
generation rule -- probed the worst parameters hardest, which is exactly where
the response is least linear, and that is how size_homelessness crossed its
cliff in a single step.
"""
import math, re, sys
sys.path.insert(0, '.')
from converge import BOUNDS

STEP = 1.25
BASE = 'points_pregrid/point_edbaa5e630.txt'      # the pre-grid best, as a LOCATION only
SKIP = {'zeta_DI', 'housing_status_grid_expander', 'lambda_m',
        'penalty_child_addicted', 'penalty_child_homeless', 'weight_on_child'}

t = open(BASE, errors='replace').read()
vec = {k: v for k, v in (x.split('=', 1) for x in re.search(r'^VECTOR\s+(.*)$', t, re.M).group(1).split())}
lines = ['bash code/run_one_point.sh ' + ' '.join(f'{k}={vec[k]}' for k in sorted(vec))]
for p in sorted(vec):
    if p in SKIP:
        continue
    try:
        base = float(vec[p])
    except ValueError:
        continue
    if base <= 0:
        continue
    lo, hi = BOUNDS.get(p, (1e-12, 1e12))
    val = min(max(base * STEP, lo), hi)
    if abs(val - base) <= 1e-12 * max(1.0, base):     # pinned at a bound: step DOWN instead
        val = min(max(base / STEP, lo), hi)
    if abs(val - base) <= 1e-12 * max(1.0, base):
        continue
    v = dict(vec); v[p] = f'{val:.7g}'
    lines.append('bash code/run_one_point.sh ' + ' '.join(f'{k}={v[k]}' for k in sorted(v)))
open('RESTART.txt', 'w').write('\n'.join(lines) + '\n')
print(f'{len(lines)} points: 1 centre + {len(lines)-1} one-parameter arms')
