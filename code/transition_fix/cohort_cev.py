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

BETA = 0.94609059720286381   # discount_factor, PARAM_HANDOVER
KAPPA_X = 0.9329             # kappa_x, PARAM_HANDOVER
CHILD_YEARS = 25

log = sys.argv[1]
curve = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(log)),
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
if 1 in wc and 1 in cev:
    print(f"check: code's CEV at t=1 {100*cev[1]:+.4f}%  this script on the same welfare {100*cev_of(wc[1]):+.4f}%")

print("\nCohort born in period b: childhood b..b+24, adult from b+25")
print("   b   lifetime       CEV      (childhood part, adult part)")
last_b = max(young) - CHILD_YEARS
for b in range(1, last_b + 1):
    if not all((b + a - 1) in by and (b + a - 1) in h for a in range(1, CHILD_YEARS + 1)):
        break
    child = sum(BETA ** (a - 1) * (by[b + a - 1][a - 1] - KAPPA_X * h[b + a - 1]) for a in range(1, CHILD_YEARS + 1))
    adult = BETA ** CHILD_YEARS * young[b + CHILD_YEARS]
    L = child + adult
    print(f"{b:4d}  {L:10.5f}  {100*cev_of(L):+8.4f}%   ({child:.4f}, {adult:.4f})")
    if b == 1:
        headline = cev_of(L)
print(f"\nTHE COHORT BORN AT THE REFORM (b = 1): CEV {100*headline:+.4f}% of consumption")
print("For comparison, the code's cross-section measure (cohort entering adulthood at t):")
for t in (1, 26):
    if t in cev:
        print(f"   t={t}: {100*cev[t]:+.4f}%")
