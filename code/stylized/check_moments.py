#!/usr/bin/env python3
"""BRUTE-FORCE CHECK OF THE MOMENTS THAT GO THROUGH threshold().

The author, 12 September: *"The only problem I think you might have is if you
have mistakes in your moment computations"*.

aggregates() does not simply sum over the income grid.  It calls threshold(),
which finds where the use decision changes sign BETWEEN grid nodes, bisects to
the crossing income, and gives the straddling cell a FRACTIONAL using weight.
That machinery is there because the use region's edge falls inside a cell, and
it is also exactly the kind of place a moment bug hides: TRANSITION_LESSONS.md
already records one there, where a cell with a crossing on each side was
written twice and the second write won.

This checks it the dumb way.  Evaluate period1 on a MUCH finer income grid,
take gain > 0 at face value with no bisection and no fractional cells, weight
by the same lognormal, and compare.  A fine enough brute-force sum and a
correct bisection must agree; if they do not, the bisection is wrong.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import stylized as S
from stylized import with_, P
import calibrate as C
from recalibrate import FIXED

V = dict(gam=0.43679, aleph=10.45448, h_hl=0.00951, b=0.10990, pi_base=0.29801,
         u0=0.04831, u1=0.05679, delta_d=0.24, kap=0.18241, th=0.20990,
         beta=1.0, omega=0.08164)
par = with_(P(), **{k: v for k, v in FIXED.items()
                    if k not in ('kap', 'gam', 'omega')}, **V)

m = C.stats(par)
print(f"aggregates():  part {m['part']:.6f}   dshare {m['dshare']:.6f}   "
      f"r_use {m['r_use']:.6f}")

# the model's own income grid and weights, then finer ones built the same way
def brute(mult):
    # THE MODEL'S OWN GRID BUILDER at a higher node count, so the brute-force
    # sum differs from aggregates() only in the BISECTION -- not in how the
    # income distribution is discretised.  Building a second grid by hand would
    # test the two grids against each other rather than the machinery.
    ys, w = C._grid(C.SIG, n=len(C.YG) * mult)[:2]
    pmass = uses = spend = uinc = 0.0
    for j, y in enumerate(ys):
        for p, gain, v, _bu, _bn, inc, _own in S.period1(par, y, None):
            pmass += w[j] * p
            if gain > 0.0:
                uses += w[j] * p
                spend += w[j] * p * par.p_v * v
                uinc += w[j] * p * inc
    return uses / pmass, (spend / uinc if uinc > 0 else 0.0), pmass

for mult in (1, 4, 8):
    part_b, dshare_b, mass = brute(mult)
    print(f"brute force x{mult:<2} ({len(C.YG)*mult:5d} incomes):  "
          f"part {part_b:.6f}   dshare {dshare_b:.6f}   mass {mass:.6f}")
