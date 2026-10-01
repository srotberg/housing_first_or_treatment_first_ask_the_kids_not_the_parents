"""CEV of a counterfactual against the Housing First omega_c = 0.06 curve.

Mirrors calculate_welfare_gains (source line 23028): quadratic Lagrange
interpolation of x in w over the bracketing pair and one neighbour. The curve
is anchored at x = 0 to average_welfare_of_youngest_cohort (its identity check
shifts w(0) onto that), so the target must be the counterfactual's
average_welfare_of_youngest_cohort -- the same object.
usage: python3 cev.py <target_welfare>
"""
import sys
import os
# CEV_CURVE names another benchmark's curve (stage C of OVERNIGHT_PLAN.md, the omega_c = 0.085
# benchmark); unset, the 26 September one, as before
curve = os.environ.get("CEV_CURVE", "results/reference/hf_omega_c_006/welfare_curvebaseline_benchmark.dat")
xs, ws = zip(*[tuple(map(float, l.split())) for l in open(curve) if l.strip()])
t = float(sys.argv[1])
assert all(b > a for a, b in zip(ws, ws[1:])), "curve not increasing"
assert ws[0] <= t <= ws[-1], "target off the curve"
i = next(k for k in range(1, len(ws)) if ws[k] >= t)
j = max(1, min(i, len(ws) - 2))
l0, l1, l2 = ws[j-1], ws[j], ws[j+1]
d0 = (t-l1)*(t-l2)/((l0-l1)*(l0-l2)); d1 = (t-l0)*(t-l2)/((l1-l0)*(l1-l2)); d2 = (t-l0)*(t-l1)/((l2-l0)*(l2-l1))
x = d0*xs[j-1] + d1*xs[j] + d2*xs[j+1]
print(f"target {t:.10f}  HF w(0) {ws[xs.index(0.0)]:.10f}  CEV x = {x:+.6f}  ({100*x:+.4f}% of consumption)")
