#!/usr/bin/env python3
"""transition_trace.py <run.log> [--loop N] [--seed out.txt]

Pulls a transition run's per-period trace out of its log and prints it as a
table, one row per period, newest loop by default.

WHY A SCRIPT. The log is hundreds of megabytes and the quantities that matter
are on four different line shapes, printed once per period per loop. Reading
them by eye is how a loop-0 number gets quoted as a loop-3 one.

    TRANSITION MECH t= <t> h_1= b= lambda_d= p_drug= pi_v=
    drug quantity V=
    distance_drug_market=            (this is |gap|; the SIGN is not in the log)
    TRANSITION WELFARE ...

THE SIGN OF THE DRUG GAP IS RECONSTRUCTED, NOT READ. clear_drug_market prints
abs(gap), so the log cannot say which way the price must move. It is recovered
from the quantity and the BENCHMARK's own shifter, exactly as
CALIBRATION_RECIPE.md section 6a does it:

    implied = shifter * V**(1/eps_s)        gap = implied - price

which reproduces the printed distance_drug_market and is therefore a
reconstruction rather than a guess -- the script CHECKS that and says so.

--seed writes a next-loop price path seed by a one-step Newton on the measured
gap, using the slope measured in the same period (d(implied)/dp = -2.25 at t=1,
falling to about -7.8 by t=28, from results/transition_t30/RESEED_CONTROL.md):

    p* = p + gap / (1 - d(implied)/dp)

It is for RESTARTING a run that was interrupted. A run that stays up does not
need it: clear_drug_market already carries a per-period secant across loops in
previous_price_of_addictive_good_path, so the built-in iteration is the better
instrument and an external reseed throws its history away.
"""
import sys, re, argparse

EPS_S   = 1.4600000381469727
SHIFTER = 1.62001478993009917495     # the committed benchmark's, held fixed

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--loop", type=int, default=None, help="loop number; default the last complete one")
ap.add_argument("--seed", default=None, help="write a Newton-step price path seed here")
a = ap.parse_args()

def slope(t):
    # LINEAR IN t BETWEEN THE TWO MEASURED POINTS, and flat outside them.
    # Measured on the T=30 arm-3 path: -2.25 at t=1, -7.8 at t=28. It is used
    # for ONE Newton step and nothing else; do not read it as a structural
    # object, and never extrapolate it past t=28.
    if t <= 1:  return -2.25
    if t >= 28: return -7.8
    return -2.25 + (-7.8 + 2.25) * (t - 1) / 27.0

mech = re.compile(r"TRANSITION MECH t=\s*(\d+)\s+h_1=\s*(\S+)\s+b=\s*(\S+)\s+"
                  r"lambda_d=\s*(\S+)\s+p_drug=\s*(\S+)\s+pi_v=\s*(\S+)")
qty  = re.compile(r"drug quantity V=\s*(\S+)")
dist = re.compile(r"distance_drug_market=\s*(\S+)")
lc   = re.compile(r"^\s*loop_count=\s*(\d+)")

loops, cur, pend_v, pend_d = [], {}, None, None
with open(a.log, "rb") as fh:
    for raw in fh:
        line = raw.decode("utf-8", "replace")
        m = lc.match(line)
        if m:
            if cur: loops.append(cur); cur = {}
            continue
        m = mech.search(line)
        if m:
            t = int(m.group(1))
            cur[t] = dict(t=t, h1=float(m.group(2)), b=float(m.group(3)),
                          lam=float(m.group(4)), p=float(m.group(5)),
                          piv=float(m.group(6)), V=None, d=None)
            pend_v = t
            continue
        m = qty.search(line)
        if m and pend_v in cur and cur[pend_v]["V"] is None:
            cur[pend_v]["V"] = float(m.group(1)); pend_d = pend_v; continue
        m = dist.search(line)
        if m and pend_d in cur and cur[pend_d]["d"] is None:
            cur[pend_d]["d"] = float(m.group(1)); continue
if cur: loops.append(cur)
if not loops:
    print("no TRANSITION MECH lines in %s" % a.log); sys.exit(1)

idx = a.loop if a.loop is not None else len(loops) - 1
if not 0 <= idx < len(loops):
    print("loop %d not in the log (0..%d)" % (idx, len(loops) - 1)); sys.exit(1)
L = loops[idx]

print("%s: %d loop block(s) found, showing block %d (%d periods)"
      % (a.log, len(loops), idx, len(L)))
print("  t   h_1        b          lambda_d   p_faced    p_implied  gap        |gap| log  chk")
rows, bad = [], 0
for t in sorted(L):
    r = L[t]
    if r["V"] is None:
        print("%3d  INCOMPLETE -- no quantity printed for this period" % t); continue
    implied = SHIFTER * r["V"] ** (1.0 / EPS_S)
    gap = implied - r["p"]
    chk = "" if r["d"] is None else ("ok" if abs(abs(gap) - r["d"]) < 1e-6 else "MISMATCH")
    if chk == "MISMATCH": bad += 1
    print("%3d  %-10.6f %-10.6f %-10.6f %-10.6f %-10.6f %+10.6f %-9s  %s"
          % (t, r["h1"], r["b"], r["lam"], r["p"], implied, gap,
             "-" if r["d"] is None else "%.6f" % r["d"], chk))
    rows.append((t, r["p"], gap))

if rows:
    g = [abs(x[2]) for x in rows]
    print("\nmean |gap| %.6f   max %.6f at t=%d   rule 5e-3, periods inside: %d of %d"
          % (sum(g)/len(g), max(g), rows[g.index(max(g))][0],
             sum(1 for x in g if x <= 5e-3), len(g)))
if bad:
    print("\n%d period(s) MISMATCH the printed distance_drug_market. The sign"
          " reconstruction is NOT valid on this log -- do not seed from it." % bad)
    sys.exit(2)

if a.seed:
    with open(a.seed, "w") as out:
        for t, p, gap in rows:
            out.write("%.15f\n" % (p + gap / (1.0 - slope(t))))
    print("\nNewton-step seed for %d periods written to %s" % (len(rows), a.seed))
    print("  Only for restarting an interrupted run: a live run's own per-period")
    print("  secant is the better instrument and this discards its history.")
