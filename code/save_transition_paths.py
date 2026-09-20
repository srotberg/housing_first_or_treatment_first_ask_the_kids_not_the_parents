#!/usr/bin/env python3
"""save_transition_paths.py <run.log> [--out DIR] [--loop N] [--tag NAME]

Harvest a transition run's per-period PATHS out of its log and write them as
seed files, so that a run which is killed, or a new run at the same horizon,
starts from where the last one got to instead of from the linear ramp.

WHAT IS AN INSTRUMENT AND WHAT IS NOT. Only two quantities in the transition
are iterated per period, and only those two can be seeded:

    price_of_addictive_good_path   clears the drug market   -> drug_price_path_seed.txt
    probability_of_voucher_path    clears the govt budget   -> pi_v_path_seed.txt

Homelessness is NOT an instrument. h_1 is an outcome of the distribution, so
there is nothing to hand a new run: it is written out as h1_path_reference.txt,
which is a TARGET to score a restart against, not an input. The object that
would really warm-start homelessness is the distribution path itself, and that
is 73 MB per period, not a vector.

WHICH LINE EACH VALUE COMES FROM, because they are not interchangeable:

    TRANSITION MECH t= .. h_1= .. b= .. lambda_d= .. p_drug= .. pi_v= ..
        printed BEFORE that period's update. Its pi_v is last loop's.
    TRANSITION PI_V loop= .. t= .. pi_v= .. budget_residual= ..
        printed AFTER the update, and is the authoritative pi_v.

So pi_v is taken from the PI_V lines when they exist and from MECH only as a
fallback, and the header of the file written says which was used. The PI_V
lines do not exist at loop 0, because the update is gated on
loop_count > start_updating_at_loop_number.

THE PRICE WRITTEN IS THE PRICE FACED, not a Newton step onto the measured gap.
A restart that re-faces the same price re-measures the same gap and carries on;
transition_trace.py --seed is the tool for stepping it, and the run's own
per-period secant in previous_price_of_addictive_good_path is better than both
while the run is up.
"""
import sys, os, re, argparse, collections

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--out", default=".", help="directory to write the seed files into")
ap.add_argument("--loop", type=int, default=None, help="loop to harvest; default the deepest complete one")
ap.add_argument("--tag", default=None, help="suffix for the filenames, e.g. t60_gf")
ap.add_argument("--force", action="store_true",
                help="write even when the path is poisoned (NaN, or pi_v on a bound)")
ap.add_argument("--fill", action="store_true",
                help="take the deepest value available PER PERIOD, splicing across loops; "
                     "the files record which loop each period came from")
a = ap.parse_args()

NUM = r"(?:[-+0-9.EDed]+|NaN|[-+]?Infinity)"
mech_re = re.compile(
    r"TRANSITION MECH t=\s*(\d+)\s+h_1=\s*(%s)\s+b=\s*(%s)\s+lambda_d=\s*(%s)\s+p_drug=\s*(%s)\s+pi_v=\s*(%s)" % ((NUM,)*5))
piv_re = re.compile(
    r"TRANSITION PI_V loop=\s*(\d+)\s+t=\s*(\d+)\s+pi_v=\s*(%s)\s+budget_residual=\s*(%s)" % (NUM, NUM))
welf_re = re.compile(r"TRANSITION WELFARE loop=\s*(\d+)\s+t=\s*(\d+)")

def f(s):
    return float(s.replace("D", "E").replace("d", "e"))

# MECH carries no loop number, so the loop is tracked from the WELFARE line
# that precedes each period's block.
mech = collections.defaultdict(dict)   # loop -> t -> (h1,b,ld,p)
piv  = collections.defaultdict(dict)   # loop -> t -> pi_v
cur_loop = 0
with open(a.log, errors="replace") as fh:
    for line in fh:
        m = welf_re.search(line)
        if m:
            cur_loop = int(m.group(1)); continue
        m = mech_re.search(line)
        if m:
            t = int(m.group(1))
            mech[cur_loop][t] = (f(m.group(2)), f(m.group(3)), f(m.group(4)), f(m.group(5)), f(m.group(6)))
            continue
        m = piv_re.search(line)
        if m:
            piv[int(m.group(1))][int(m.group(2))] = f(m.group(3))

if not mech:
    sys.exit("no TRANSITION MECH lines in %s -- this log predates the diagnostic" % a.log)

# THE DEEPEST LOOP IS USUALLY THE INCOMPLETE ONE. A run is killed, or is still
# going, part way through its newest loop, so max(mech) can be a three-period
# fragment of a thirty-period horizon. Taking it silently would hand a T=30
# restart three periods of seed and twenty-seven of linear ramp, which is worse
# than the complete older loop it passed over. Default to the deepest loop that
# covers the whole horizon seen anywhere in the log, and say what was skipped.
horizon = max(max(d) for d in mech.values())
full = [L for L in sorted(mech) if len(mech[L]) == horizon and max(mech[L]) == horizon]

if a.loop is not None:
    loop = a.loop
    if loop not in mech:
        sys.exit("loop %d not in the log; loops present: %s" % (loop, sorted(mech)))
elif a.fill:
    loop = max(mech)
elif full:
    loop = full[-1]
    if loop != max(mech):
        print("NOTE: loop %d is deeper but covers only %d of %d periods; taking loop %d, "
              "which is complete. --fill splices the deeper values in per period."
              % (max(mech), len(mech[max(mech)]), horizon, loop))
else:
    loop = max(mech)
    print("WARNING: no loop in this log covers all %d periods. Taking loop %d with %d."
          % (horizon, loop, len(mech[loop])))

if a.fill:
    # Deepest available value PER PERIOD. This is a SPLICE across loops, not an
    # iterate of the map, and the header of every file written says so period by
    # period. It is the right thing for a restart seed -- use the best
    # information you have about each period -- and the wrong thing to quote as
    # a path.
    src = {}
    for t in range(1, horizon + 1):
        for L in sorted(mech, reverse=True):
            if t in mech[L]:
                src[t] = L
                break
    periods = sorted(src)
    spliced = sorted(set(src.values()))
    print("SPLICED across loops %s: %s" % (spliced,
          ", ".join("t%d<-L%d" % (t, src[t]) for t in periods[:6]) + (" ..." if len(periods) > 6 else "")))
else:
    src = {t: loop for t in mech[loop]}
    periods = sorted(mech[loop])
# A POISONED LOOP IS INDISTINGUISHABLE FROM A GOOD ONE ONCE IT IS A COLUMN OF
# NUMBERS, and that is the whole risk of seeding from a file. Two failures have
# actually happened in this model and both are caught here rather than left for
# a T=60 restart to inherit:
#
#   NaN in any period        -- the run had already diverged
#   pi_v at a bound          -- 1e-5 is the floor and 1.0 the ceiling in
#                               probability_of_voucher_path; sitting on either
#                               is the voucher programme abolished or universal,
#                               which is the collapse the step clip was added to
#                               stop, not an equilibrium.
PI_V_FLOOR, PI_V_CEIL = 1.0e-5, 1.0
bad = []
for t in periods:
    h1, b, ld, pr, pv_mech = mech[src[t]][t]
    pv = piv[src[t]].get(t, pv_mech)
    for name, v in (("h_1", h1), ("b", b), ("lambda_d", ld), ("p_drug", pr), ("pi_v", pv)):
        if v != v or v in (float("inf"), float("-inf")):
            bad.append("t=%d %s is %s (loop %d)" % (t, name, v, src[t]))
    if abs(pv - PI_V_FLOOR) <= 1e-12 or abs(pv - PI_V_CEIL) <= 1e-12:
        bad.append("t=%d pi_v is pinned at the bound %.1e (loop %d)" % (t, pv, src[t]))

if bad:
    print("REFUSING TO WRITE. This path is poisoned, not converged:")
    for x in bad[:12]:
        print("   " + x)
    if len(bad) > 12:
        print("   ... and %d more" % (len(bad) - 12))
    if not a.force:
        sys.exit("re-run with --force only if you have read the log and want it anyway")
    print("--force given; writing it anyway.")

tag = ("_" + a.tag) if a.tag else ""
os.makedirs(a.out, exist_ok=True)

piv_src = "TRANSITION PI_V (post-update)" if any(piv.get(L) for L in set(src.values())) else \
          "TRANSITION MECH (PRE-update; no PI_V lines at these loops, so this is the value they FACED)"

def write(name, header, values):
    p = os.path.join(a.out, name)
    with open(p, "w") as g:
        for h in header:
            g.write("# %s\n" % h)
        for v in values:
            g.write("%.15f\n" % v)
    print("wrote %s  (%d periods)" % (p, len(values)))

write("drug_price_path_seed%s.txt" % tag,
      ["price_of_addictive_good_path, the price FACED at loop %d of %s" % (loop, os.path.basename(a.log)),
       "periods %d..%d" % (periods[0], periods[-1]),
       "not a Newton step: a restart re-faces this price and re-measures the gap"],
      [mech[src[t]][t][3] for t in periods])

write("pi_v_path_seed%s.txt" % tag,
      ["probability_of_voucher_path at loop %d of %s" % (loop, os.path.basename(a.log)),
       "source: %s" % piv_src,
       "periods %d..%d" % (periods[0], periods[-1])],
      [piv[src[t]].get(t, mech[src[t]][t][4]) for t in periods])

write("h1_path_reference%s.txt" % tag,
      ["h_1 at loop %d of %s -- A REFERENCE, NOT AN INPUT." % (loop, os.path.basename(a.log)),
       "homelessness is an outcome of the distribution; nothing reads this file.",
       "score a restart against it; it cannot seed one.",
       "periods %d..%d" % (periods[0], periods[-1])],
      [mech[src[t]][t][0] for t in periods])

print("loop harvested: %d of %s" % (loop, sorted(mech)))
print("pi_v source   : %s" % piv_src)
