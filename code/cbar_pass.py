#!/usr/bin/env python3
"""Solve max_food_cost from the run's own printed state. No search, no elasticity.

The programme is snap = max(0, cbar - tau*y), so aggregate spending is

    S(cbar) = int_0^{cbar/tau} (cbar - tau*y) f(y) dy

and the integrand vanishes at the eligibility limit, which kills the boundary
term when the integral is differentiated. What is left is exact:

    dS/dcbar = mass * recipient share

Both factors are printed every loop, so cbar is solved rather than searched.

THE UNIT TRAP, WHICH CAUGHT ME ONCE.  The recipient figure the model prints is a
SHARE and the spending figure is an unnormalised AGGREGATE, so the mass has to
multiply the share or the derivative is out by a factor of fifty. The check that
catches it is printed below: average benefit per recipient must be between zero
and cbar, because that is what a taper on a maximum allotment can pay. Reading it
without the mass gave 2.27 against a cbar of 0.087 -- twenty-six times the legal
maximum -- which is how the error was found.

S is convex in cbar, since the recipient share rises with it, so the linear step
is an upper bound and a local power law a lower one. Both are printed: it is a
measured bracket, not a point estimate.

DO NOT RUN THIS AGAINST A MOVING DISTRIBUTION. cbar is solved at one economy and
is only right for that economy -- the first pass, solved at output 61.7, drifted
to -27 per cent as the drug block moved underneath it. Wait until the moments
feeding the income distribution are still.

Usage: python3 code/cbar_pass.py <run log> [loops to average over, default 3]
"""
import re
import sys

TAPER = 0.30


def main():
    log = open(sys.argv[1], errors="ignore").read()
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    f = lambda x: float(x.replace("D", "E").replace("d", "e"))

    def series(pat):
        return [f(m.group(1)) for m in re.finditer(pat, log)]

    cbar = series(r"HANDOVER max_food_cost:.*?->\s*([-\d.eEdD+]+)") or series(
        r"(?m)^\s*max_food_cost=\s*([-\d.eEdD+]+)\s*$")
    spend = series(r"DIAG food stamps, aggregate spending\s*=\s*([-\d.eEdD+]+)")
    out = series(r"DIAG output, the denominator above\s*=\s*([-\d.eEdD+]+)")
    share = series(r"DIAG households receiving food stamps\s*=\s*([-\d.eEdD+]+)")
    mass = series(r"share with a NEGATIVE value of life.*?of\s+([-\d.eEdD+]+)")
    tgt = series(r"MOMENT cbar.*?target=\s*([-\d.eEdD+]+)")
    if not (cbar and spend and out and share and mass and tgt):
        sys.exit("a required diagnostic is missing from this log")

    # Average over a window rather than trusting one iterate: a moment print is
    # one step of the map, not an equilibrium.
    avg = lambda v: sum(v[-n:]) / len(v[-n:])
    c, S, Y, P, M, T = cbar[-1], avg(spend), avg(out), avg(share), avg(mass), tgt[-1]

    per = S / (M * P) if M * P else float("nan")
    print(f"averaged over the last {n} loops")
    print(f"  cbar                {c:.6f}")
    print(f"  spending S          {S:.6f}")
    print(f"  output Y            {Y:.4f}      ratio {S / Y:.6f}  target {T:.5f}")
    print(f"  recipient share P   {P:.6f}")
    print(f"  mass M              {M:.4f}")
    print(f"  benefit / recipient {per:.6f}  = {per / c * 100:.1f}% of cbar", end="")
    print("   OK" if 0 < per < c else "   *** OUT OF RANGE: the units are wrong ***")

    dS = M * P
    k = dS * c / S
    Sstar = T * Y
    print(f"\n  dS/dcbar = M*P      {dS:.5f}        local exponent k = {k:.4f}")
    print(f"  S must reach        {Sstar:.6f}  (x{Sstar / S:.4f})")
    lin = c + (Sstar - S) / dS
    pw = c * (Sstar / S) ** (1 / k)
    lo, hi = min(lin, pw), max(lin, pw)
    print(f"\n  cbar bracket        [{lo:.5f}, {hi:.5f}]   midpoint {(lo + hi) / 2:.5f}")
    print(f"  linear step {lin:.5f} (ignores convexity), power law {pw:.5f}")


if __name__ == "__main__":
    main()
