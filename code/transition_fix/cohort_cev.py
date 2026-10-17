"""CEV of the cohort BORN at the reform, lifetime utility including childhood.

usage: python3 cohort_cev.py <run.log> [<welfare curve file>]

The transition prints, per period t, average_welfare_with_childhood(t): the
childhood of the cross section of households with children at t plus beta^25
times the adult value of those ENTERING adulthood (model age 1, age 26) at t.
At t = 1 that is the cohort already 26 at the reform, whose childhood was lived
before it. The author's question is the cohort BORN at the reform: its
childhood runs over periods 1..25 of the path (age a in period a) and it enters
adulthood at t = 26. This assembles that cohort's lifetime along its own life,

    L(b) = sum_{a=1..25} beta^(a-1) * (by_age(t=b+a-1, a) - kappa_x * h_1(t=b+a-1))
           + beta^25 * youngest(t=b+25)

with the same formula the model uses for a cross section (checked: it reproduces
the steady state's average_childhood_utility exactly), and reads its CEV off the
benchmark's lifetime (newborn, with childhood) welfare curve, the object the
model's own CEV uses. It does this for every birth period b the path covers.

Only the LATEST complete forward pass is used: the lines after the last
'TRANSITION INIT PARENT SHARE RESTORED' marker if that pass has reached the
periods needed, otherwise the pass before it.
"""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'paper'))
import welfare_nok as wn      # the kappa_x * H term and the benchmark's curve shift (10 October)

BETA = 0.94609059720286381   # discount_factor, PARAM_HANDOVER
KAPPA_X = 0.9342362271804227 # kappa_x, the benchmark's (KAPPA_X in the launchers; 17 October, was 0.9329, 1e-4 utils)
# EVERY LIFETIME VALUE AND CEV PRINTED HERE IS WITHOUT THE kappa_x * H TERM (10 October, the author: "compute all the
# welfare numbers without kappa_x H"): the childhood sum leaves the term out, the adult value at 26 gets the term it
# carries added back (ADULT_SENS * kappa_x * h_1 of the year the cohort enters), and the curve is shifted by the
# benchmark's own term. --with-term reproduces the earlier numbers.
WITH_TERM = '--with-term' in sys.argv
if WITH_TERM: sys.argv.remove('--with-term')
# --child-weight W (11 October): the child's childhood counted at W (the author: xi - 1, the household's own
# equivalence weight) instead of one; the curve is rebuilt from the benchmark's adult and childhood curves
CHILD_WEIGHT = wn.CHILD_WEIGHT                     # the paper's (xi - 1); --child-weight 1 gives the Fortran's
if '--child-weight' in sys.argv:
    _i = sys.argv.index('--child-weight'); CHILD_WEIGHT = float(sys.argv[_i + 1]); del sys.argv[_i:_i + 2]
CHILD_YEARS = 25

# --terminal <cf.log.gz>: the steady state the path ends in. With it, a cohort whose childhood or adult entry
# falls after the last year of the path is completed with that steady state, so every cohort born on the path
# has a CEV (the author, 2 October, of the transition figure's panel (f): "why not show 60 years too for f?")
ARGS = sys.argv[1:]
TERMINAL = None
if '--terminal' in ARGS:
    k = ARGS.index('--terminal')
    TERMINAL = ARGS[k + 1]
    del ARGS[k:k + 2]
REFS = None
if '--refs' in ARGS:
    k = ARGS.index('--refs')
    REFS = ARGS[k + 1:k + 3]
    del ARGS[k:k + 3]
log = ARGS[0]
curve = ARGS[1] if len(ARGS) > 1 else os.path.join(os.path.dirname(os.path.abspath(log)),
                                                            "welfare_curvebaseline_benchmark.dat")
lines = open(log, errors="replace").read().splitlines()


def passes(lines):
    starts = [i for i, l in enumerate(lines) if "TRANSITION INIT PARENT SHARE RESTORED" in l]
    starts.append(len(lines))
    return [lines[starts[k]:starts[k + 1]] for k in range(len(starts) - 1)]


def parse(block):
    by, h, young, wc, cev = {}, {}, {}, {}, {}
    for l in block:
        if "TRANSITION CHILDHOOD_BY_AGE t=" in l:
            f = l.split("t=")[1].split()
            by[int(f[0])] = [float(x) for x in f[1:]]
        elif "TRANSITION MECH t=" in l:
            t = int(l.split("t=")[1].split()[0]); h[t] = float(re.search(r"h_1=\s*(\S+)", l).group(1))
        elif "TRANSITION WELFARE loop=" in l and "youngest=" in l:
            t = int(re.search(r"t=\s*(\d+)", l).group(1))
            young[t] = float(re.search(r" youngest=\s*(\S+)", l).group(1))
            wc[t] = float(re.search(r"with_childhood=\s*(\S+)", l).group(1))
        elif "TRANSITION CEV t=" in l and "CEV=" in l:
            t = int(re.search(r"t=\s*(\d+)", l).group(1)); cev[t] = float(l.split("CEV=")[1].split()[0])
    return by, h, young, wc, cev


xs, ws = zip(*[tuple(map(float, l.split())) for l in open(curve) if l.strip()])
if not WITH_TERM:
    ws = tuple(w + wn.SHIFT0 for w in ws) if CHILD_WEIGHT == 1.0 else tuple(wn.curve_for_weight(CHILD_WEIGHT))


def cev_of(t):
    """quadratic Lagrange in w over the bracketing pair and a neighbour, as cev.py"""
    i = next(k for k in range(1, len(ws)) if ws[k] >= t)
    j = max(1, min(i, len(ws) - 2))
    l0, l1, l2 = ws[j - 1], ws[j], ws[j + 1]
    d0 = (t - l1) * (t - l2) / ((l0 - l1) * (l0 - l2)); d1 = (t - l0) * (t - l2) / ((l1 - l0) * (l1 - l2))
    d2 = (t - l0) * (t - l1) / ((l2 - l0) * (l2 - l1))
    return d0 * xs[j - 1] + d1 * xs[j] + d2 * xs[j + 1]


ps = passes(lines)
chosen = None
for k in range(len(ps) - 1, -1, -1):
    by, h, young, wc, cev = parse(ps[k])
    if 1 in by and CHILD_YEARS + 1 in young and all(a in by and a in h for a in range(1, CHILD_YEARS + 1)):
        chosen = k; break
if chosen is None:
    sys.exit("no forward pass in the log has reached period 26 yet")
by, h, young, wc, cev = parse(ps[chosen])
print(f"forward pass {chosen} of {len(ps) - 1} (0 = the first loop); periods in it: {min(young)}..{max(young)}")

# consistency: the code's own CEV at t=1 from its own with_childhood, through this interpolation
if 1 in wc and 1 in cev and CHILD_WEIGHT == 1.0:   # the code's own CEV counts childhood at one
    _w = (ws if WITH_TERM else tuple(w - wn.SHIFT0 for w in ws))
    _i = next(k for k in range(1, len(_w)) if _w[k] >= wc[1]); _j = max(1, min(_i, len(_w) - 2))
    _l0, _l1, _l2 = _w[_j-1], _w[_j], _w[_j+1]; _t = wc[1]
    _x = (_t-_l1)*(_t-_l2)/((_l0-_l1)*(_l0-_l2))*xs[_j-1] + (_t-_l0)*(_t-_l2)/((_l1-_l0)*(_l1-_l2))*xs[_j] + (_t-_l0)*(_t-_l1)/((_l2-_l0)*(_l2-_l1))*xs[_j+1]
    print(f"check: code's CEV at t=1 {100*cev[1]:+.4f}%  this script on the same welfare, with the term {100*_x:+.4f}%")

LAST = max(young)
if TERMINAL:
    import gzip
    by_ss = c_ss = y_ss = None
    for l in gzip.open(TERMINAL, "rt", errors="replace"):
        if "childhood_utility_by_age=" in l:
            by_ss = [float(x) for x in l.split("=")[1].split()]
        elif "average_childhood_utility=" in l:
            c_ss = float(l.split("=")[1].split()[0])
        elif "average_welfare_of_youngest_cohort=" in l:
            y_ss = float(l.split("=")[1].split()[0])
    assert by_ss and len(by_ss) == CHILD_YEARS and c_ss and y_ss, "terminal log lacks the steady-state childhood"
    # the steady state's h_1 from its own identity, average_childhood_utility = sum beta^(a-1) (by(a) - kappa_x h)
    disc = [BETA ** (a - 1) for a in range(1, CHILD_YEARS + 1)]
    h_ss = (sum(d * u for d, u in zip(disc, by_ss)) - c_ss) / (KAPPA_X * sum(disc))
    print(f"terminal steady state: h_1 {h_ss:.6f} (from its childhood identity), youngest {y_ss:.4f}; "
          f"the path's last year t={LAST}: h_1 {h[LAST]:.6f}, youngest {young[LAST]:.4f}")
    for t in range(LAST + 1, LAST + 2 * CHILD_YEARS + 2):
        by[t], h[t], young[t] = by_ss, h_ss, y_ss

print("\nCohort born in period b: childhood b..b+24, adult from b+25")
print("   b   lifetime       CEV      (childhood part, adult part)")
last_b = LAST + 1 if TERMINAL else LAST - CHILD_YEARS
for b in range(1, last_b + 1):
    if not all((b + a - 1) in by and (b + a - 1) in h for a in range(1, CHILD_YEARS + 1)):
        break
    if WITH_TERM:
        child = sum(BETA ** (a - 1) * (by[b + a - 1][a - 1] - KAPPA_X * h[b + a - 1]) for a in range(1, CHILD_YEARS + 1))
        adult = BETA ** CHILD_YEARS * young[b + CHILD_YEARS]
    else:
        child = CHILD_WEIGHT * sum(BETA ** (a - 1) * by[b + a - 1][a - 1] for a in range(1, CHILD_YEARS + 1))
        adult = BETA ** CHILD_YEARS * (young[b + CHILD_YEARS] + KAPPA_X * wn.ADULT_SENS * h[b + CHILD_YEARS])
    L = child + adult
    print(f"{b:4d}  {L:10.5f}  {100*cev_of(L):+8.4f}%   ({child:.4f}, {adult:.4f})")
    if b == 1:
        headline = cev_of(L)
print(f"\nTHE COHORT BORN AT THE REFORM (b = 1): CEV {100*headline:+.4f}% of consumption")


def steady(path):
    """last average_childhood_utility and average_welfare_with_childhood of a steady-state log"""
    import gzip
    c = w = None
    for l in gzip.open(path, "rt", errors="replace"):
        if "average_childhood_utility=" in l:
            c = float(l.split("=")[1].split()[0])
        elif "average_welfare_with_childhood=" in l:
            w = float(l.split("=")[1].split()[0])
    return c, w - c


# The same split for the steady states, childhood and discounted adult part (total minus childhood),
# so the cohort's lifetime can be read against no policy and against the long run of the same reform.
here = os.path.dirname(os.path.abspath(__file__))
refs = [("no policy", os.path.join(here, "../../results/counterfactuals_cf_fix2/null_share/cf.log.gz")),
        ("long run (TF 85)", os.path.join(here, "../../results/counterfactuals_cf_fix2/tf85/cf.log.gz"))]
# --refs <no-policy cf.log.gz> <long-run cf.log.gz>: the steady states the path was solved between, when they are
# not the old cf_fix2 arms (the T = 60 run on the 2c build, 6 October)
if REFS:
    refs = [("no policy", REFS[0]), ("long run (TF 85)", REFS[1])]
b1_child = CHILD_WEIGHT * sum(BETA ** (a - 1) * (by[a][a - 1] - KAPPA_X * h[a]) for a in range(1, CHILD_YEARS + 1))
b1_adult = BETA ** CHILD_YEARS * young[1 + CHILD_YEARS]
print("\nBorn at the reform, split into childhood (ages 1-25, discounted to age 1) and adulthood (from 26):")
print(f"   {'':18s} {'childhood':>11s} {'adulthood':>11s} {'total':>11s}")
print(f"   {'cohort b = 1':18s} {b1_child:11.4f} {b1_adult:11.4f} {b1_child + b1_adult:11.4f}")
got = {}
for name, path in refs:
    if os.path.exists(path):
        c, a = steady(path)
        c *= CHILD_WEIGHT                      # the same weight on the steady states' childhood
        got[name] = (c, a)
        print(f"   {name:18s} {c:11.4f} {a:11.4f} {c + a:11.4f}")
if "no policy" in got:
    c0, a0 = got["no policy"]
    print(f"   {'gain on no policy':18s} {b1_child - c0:+11.4f} {b1_adult - a0:+11.4f} {b1_child + b1_adult - c0 - a0:+11.4f}"
          "   (utils)")
    if "long run (TF 85)" in got:
        c1, a1 = got["long run (TF 85)"]
        print(f"   {'long-run gain':18s} {c1 - c0:+11.4f} {a1 - a0:+11.4f} {c1 + a1 - c0 - a0:+11.4f}")
print("For comparison, the code's cross-section measure (cohort entering adulthood at t):")
for t in (1, 26):
    if t in cev:
        print(f"   t={t}: {100*cev[t]:+.4f}%")
