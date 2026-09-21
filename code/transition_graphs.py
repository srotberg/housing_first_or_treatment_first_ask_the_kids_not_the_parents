#!/usr/bin/env python3
"""transition_graphs.py <run.log> [--loop N] [--out FILE.png]

The series the author asked for on 21 September, over the transition's periods:
per cent change in homelessness, in drug use and in SUD; the drug price p_drug
and the voucher probability pi_v, which are the model's TWO equilibrium objects;
lifetime CEV including childhood by cohort; and the distance each equilibrium
object still has to travel, against its own stopping rule.

FIVE PANELS, NOT ONE CHART, and never a second y-axis. The three per-cent
changes share units and belong together -- reading them against each other IS
the economics, since drug use falls while homelessness rises. p_drug is a level
near 0.9, pi_v a level near 0.07, the CEV a percentage near 3, and the distances
span orders of magnitude and want a log axis; putting any of those on a shared
scale would flatten the others into noise.

THE DISTANCE PANEL IS THE ONE THAT SAYS WHETHER TO BELIEVE THE REST. Its two
series are the only things the transition actually solves for, and until both
sit under their dashed rules every other panel is an iterate, not a result.

Reference values are read from the steady-state dumps in the run directory, not
typed, so the per cent changes cannot silently drift from the benchmark they
claim to be against.
"""
import sys, os, re, argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--loop", type=int, default=None)
ap.add_argument("--out", default=None)
a = ap.parse_args()

RUNDIR = os.path.dirname(os.path.abspath(a.log)) or "."

def from_dump(fname, key):
    """Read one scalar out of a steady-state dump, by exact key."""
    path = os.path.join(RUNDIR, fname)
    with open(path, errors="replace") as fh:
        for ln in fh:
            k, _, v = ln.partition(",")
            if k.strip() == key:
                return float(v.split()[0].replace("D", "E"))
    raise KeyError("%s not found in %s" % (key, fname))

B  = "baseline_benchmark.txt"
TF = "counter_TF.txt"
ref = {
    "h1_b":  from_dump(B,  "model_fraction_homeless"),
    "b_b":   from_dump(B,  "model_exprimenters+model_fraction_addicted"),
    "ld_b":  from_dump(B,  "model_fraction_addicted"),
    "piv_b": from_dump(B,  "probability_of_voucher_benchmark"),
    "h1_t":  from_dump(TF, "model_fraction_homeless"),
    "b_t":   from_dump(TF, "model_exprimenters+model_fraction_addicted"),
    "ld_t":  from_dump(TF, "model_fraction_addicted"),
    "piv_t": from_dump(TF, "probability_of_voucher_benchmark"),
}

NUM = r"(?:[-+0-9.EDed]+|NaN)"
mech = re.compile(r"TRANSITION MECH t=\s*(\d+)\s+h_1=\s*(%s)\s+b=\s*(%s)\s+lambda_d=\s*(%s)\s+p_drug=\s*(%s)\s+pi_v=\s*(%s)" % ((NUM,)*5))
cev  = re.compile(r"TRANSITION CEV t=\s*(\d+)\s+CEV=\s*(%s)" % NUM)
welf = re.compile(r"TRANSITION WELFARE loop=\s*(\d+)\s+t=\s*(\d+)")
# The drug-market distance carries NO period tag -- it is printed once per
# period, between that period's MECH line and its BUDGET line. So it is keyed
# on the MECH line that most recently went past, which is why last_t is tracked.
dist = re.compile(r"distance_drug_market=\s*(%s)" % NUM)
budg = re.compile(r"TRANSITION BUDGET loop=\s*(\d+)\s+t=\s*(\d+).*?residual=\s*(%s)" % NUM)
f    = lambda s: float(s.replace("D", "E").replace("d", "e"))

M, C, D, R, loop, last_t = {}, {}, {}, {}, 0, None
for ln in open(a.log, errors="replace"):
    m = welf.search(ln)
    if m: loop = int(m.group(1)); continue
    m = mech.search(ln)
    if m:
        M.setdefault(loop, {})[int(m.group(1))] = tuple(f(m.group(i)) for i in (2,3,4,6,5))
        last_t = int(m.group(1))
        continue
    m = cev.search(ln)
    if m: C.setdefault(loop, {})[int(m.group(1))] = f(m.group(2)); continue
    m = budg.search(ln)
    if m: R.setdefault(int(m.group(1)), {})[int(m.group(2))] = abs(f(m.group(3))); continue
    m = dist.search(ln)
    if m and last_t is not None: D.setdefault(loop, {})[last_t] = abs(f(m.group(1)))

if not M: sys.exit("no TRANSITION MECH lines in %s" % a.log)
L = a.loop if a.loop is not None else max(M)
if L not in M: sys.exit("loop %d absent; present: %s" % (L, sorted(M)))
T = sorted(M[L])
print("loop %d, periods %d..%d (%d of them)" % (L, T[0], T[-1], len(T)))

pct   = lambda v, base: 100.0*(v/base - 1.0)
h1    = [pct(M[L][t][0], ref["h1_b"]) for t in T]
bb    = [pct(M[L][t][1], ref["b_b"])  for t in T]
ld    = [pct(M[L][t][2], ref["ld_b"]) for t in T]
piv   = [M[L][t][3] for t in T]
pdr   = [M[L][t][4] for t in T]
Td    = [t for t in T if t in D.get(L, {})];  dd = [D[L][t] for t in Td]
Tr    = [t for t in T if t in R.get(L, {})];  rr = [R[L][t] for t in Tr]
# The transition doubles the steady state's rules; both are maxima over periods.
RULE_DRUG, RULE_BUDGET = 1.0e-2, 5.0e-2
Tc    = [t for t in T if t in C.get(L, {})]
cevs  = [100.0*C[L][t] for t in Tc]

INK, MUTE, GRID = "#0b0b0b", "#52514e", "#dcdbd6"
S1, S2, S3      = "#2a78d6", "#eb6834", "#1baf7a"   # validated slots 1-3
REFC            = "#9a9892"

fig, ax = plt.subplots(5, 1, figsize=(9.5, 17.5), sharex=True,
                       gridspec_kw={"height_ratios": [1.3, 1, 1, 1, 1.15], "hspace": 0.26})
fig.patch.set_facecolor("#fcfcfb")

def dress(x, ylab):
    x.xaxis.set_major_locator(MaxNLocator(integer=True))
    x.set_facecolor("#fcfcfb")
    x.grid(True, color=GRID, linewidth=0.6, alpha=0.9)
    x.set_axisbelow(True)
    for s in ("top", "right"): x.spines[s].set_visible(False)
    for s in ("left", "bottom"): x.spines[s].set_color(GRID)
    x.tick_params(colors=MUTE, labelsize=9, length=0)
    x.set_ylabel(ylab, color=MUTE, fontsize=10)

def label_end(x, ts, ys, text, colour):
    """Direct label at the right end. The relief rule: aqua is under 3:1 on
    this surface, so every series carries a visible label, not colour alone."""
    x.annotate(text, xy=(ts[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
               color=INK, fontsize=9.5, va="center")

# --- panel 1: the three per-cent changes, one shared unit -------------------
dress(ax[0], "per cent vs benchmark")
ax[0].axhline(0, color=REFC, linewidth=1.0)
for ys, colour, name, tf in ((h1, S1, "homelessness", pct(ref["h1_t"], ref["h1_b"])),
                             (bb, S2, "drug use",     pct(ref["b_t"],  ref["b_b"])),
                             (ld, S3, "SUD",          pct(ref["ld_t"], ref["ld_b"]))):
    ax[0].plot(T, ys, color=colour, linewidth=2.0, solid_capstyle="round", label=name)
    ax[0].axhline(tf, color=colour, linewidth=1.0, linestyle=(0, (4, 3)), alpha=0.55)
    label_end(ax[0], T, ys, name, colour)
ax[0].set_title("Transition against the benchmark, loop %d" % L,
                color=INK, fontsize=13, fontweight="bold", loc="left", pad=26)
ax[0].legend(frameon=False, fontsize=9, labelcolor=MUTE, ncol=4,
             loc="lower left", bbox_to_anchor=(0, 1.005), handlelength=1.6,
             columnspacing=1.6, borderaxespad=0)
ax[0].annotate("dashed line: that series' long-run TF steady state",
               xy=(0, 1.005), xycoords="axes fraction", xytext=(300, 2),
               textcoords="offset points", color=MUTE, fontsize=8.5, va="bottom")

# --- panel 2: p_drug, EQUILIBRIUM OBJECT ONE, a level ----------------------
dress(ax[1], "drug price p_drug")
ax[1].plot(T, pdr, color=S1, linewidth=2.0, solid_capstyle="round")
ax[1].axhline(pdr[-1], color=REFC, linewidth=1.0, linestyle=(0, (4, 3)))
ax[1].annotate("t=%d  %.6f" % (T[-1], pdr[-1]), xy=(T[-1], pdr[-1]), xytext=(6, 0),
               textcoords="offset points", color=MUTE, fontsize=8.5, va="center")
ax[1].annotate("EQUILIBRIUM OBJECT 1 of 2 -- cleared against the drug market",
               xy=(0, 1.04), xycoords="axes fraction", color=MUTE, fontsize=8.5, va="bottom")

# --- panel 3: pi_v, EQUILIBRIUM OBJECT TWO, a level ------------------------
dress(ax[2], "voucher probability pi_v")
ax[2].plot(T, piv, color=S2, linewidth=2.0, solid_capstyle="round")
for v, txt in ((ref["piv_b"], "benchmark"), (ref["piv_t"], "long-run TF")):
    ax[2].axhline(v, color=REFC, linewidth=1.0, linestyle=(0, (4, 3)))
    ax[2].annotate("%s  %.6f" % (txt, v), xy=(T[-1], v), xytext=(6, 0),
                   textcoords="offset points", color=MUTE, fontsize=8.5, va="center")
ax[2].annotate("EQUILIBRIUM OBJECT 2 of 2 -- cleared against the budget residual",
               xy=(0, 1.04), xycoords="axes fraction", color=MUTE, fontsize=8.5, va="bottom")

# --- panel 4: CEV by cohort -------------------------------------------------
dress(ax[3], "lifetime CEV incl. childhood, %")
if Tc:
    ax[3].axhline(0, color=REFC, linewidth=1.0)
    ax[3].plot(Tc, cevs, color=S2, linewidth=2.0, solid_capstyle="round")
    ax[3].annotate("%+.3f%% at t=%d" % (cevs[0], Tc[0]), xy=(Tc[0], cevs[0]),
                   xytext=(6, -14), textcoords="offset points", color=INK, fontsize=9.5)
else:
    ax[3].annotate("no CEV printed at this loop", xy=(0.5, 0.5), xycoords="axes fraction",
                   ha="center", color=MUTE, fontsize=10)

# --- panel 5: HOW FAR EACH OBJECT STILL HAS TO GO ---------------------------
# Log axis: these span orders of magnitude within one loop, and the thing worth
# seeing is distance-to-rule, which is a ratio.
dress(ax[4], "distance remaining (log)")
ax[4].set_xlabel("period of the transition", color=MUTE, fontsize=10)
ax[4].set_yscale("log")
drew = False
for ts, ys, colour, name, rule in ((Td, dd, S1, "drug market", RULE_DRUG),
                                   (Tr, rr, S2, "budget residual", RULE_BUDGET)):
    if not ts: continue
    drew = True
    ax[4].plot(ts, ys, color=colour, linewidth=2.0, solid_capstyle="round", label=name)
    ax[4].axhline(rule, color=colour, linewidth=1.0, linestyle=(0, (4, 3)), alpha=0.7)
    label_end(ax[4], ts, ys, name, colour)
    worst = max(ys)
    print("  %-16s max %.4g over %d periods, rule %.3g -> %s (%.1fx)"
          % (name, worst, len(ts), rule,
             "INSIDE" if worst <= rule else "outside", worst/rule))
if drew:
    ax[4].legend(frameon=False, fontsize=9, labelcolor=MUTE, ncol=2,
                 loc="lower left", bbox_to_anchor=(0, 1.005), handlelength=1.6,
                 columnspacing=1.6, borderaxespad=0)
    ax[4].annotate("dashed line: that object's stopping rule. Both must be under it, in EVERY period.",
                   xy=(0, 1.005), xycoords="axes fraction", xytext=(190, 2),
                   textcoords="offset points", color=MUTE, fontsize=8.5, va="bottom")
else:
    ax[4].annotate("no distances printed at this loop", xy=(0.5, 0.5), xycoords="axes fraction",
                   ha="center", color=MUTE, fontsize=10)

span = max(T[-1] - T[0], 1)
for x in ax:
    x.set_xlim(T[0] - 0.02*span, T[-1] + 0.14*span)

out = a.out or os.path.join(RUNDIR, "transition_loop%d.png" % L)
fig.savefig(out, dpi=170, bbox_inches="tight", facecolor=fig.get_facecolor())
print("wrote", out)
for nm, v in (("h_1", h1), ("b", bb), ("lambda_d", ld)):
    print("  %-9s t=%d %+7.2f%%   t=%d %+7.2f%%" % (nm, T[0], v[0], T[-1], v[-1]))
if Tc: print("  CEV       t=%d %+7.3f%%   t=%d %+7.3f%%" % (Tc[0], cevs[0], Tc[-1], cevs[-1]))
