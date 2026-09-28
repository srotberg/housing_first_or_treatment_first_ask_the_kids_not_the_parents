"""bracket_seed.py <log A> <log B> <out>: each period's drug price from the two runs' loop 0.

Per period t, each run gives (p, g) with g = log(implied supply price / p). Where the gaps have
opposite signs the root is bracketed and log p* is the secant between the two points. Where they
do not, the secant would extrapolate; it is then capped at 2 per cent beyond the nearer point,
which is four loops of the 0.5 per cent cap and no more.
"""
import re, sys, math
def loop0(path):
    L = open(path, errors="replace").read().splitlines()
    loop = None; t = None; P = {}; IP = {}
    for l in L:
        m = re.search(r'TRANSITION WELFARE loop=\s*(\d+)\s+t=\s*(\d+)', l)
        if m: loop = int(m.group(1))
        if loop != 0: continue
        if 'TRANSITION MECH t=' in l:
            t = int(l.split('t=')[1].split()[0]); P[t] = float(re.search(r'p_drug=\s*(\S+)', l).group(1))
        if l.strip().startswith('implied supply price=') and t: IP[t] = float(l.split('=')[1])
    return P, IP
(PA, IA), (PB, IB) = loop0(sys.argv[1]), loop0(sys.argv[2])
T = 59
out = []; rows = []
for t in range(1, T + 1):
    pa, pb = PA[t], PB[t]; ga, gb = math.log(IA[t] / pa), math.log(IB[t] / pb)
    if abs(ga - gb) < 1e-12 or abs(math.log(pb / pa)) < 1e-9:
        x = math.log(pb) + gb / 3.15          # no slope measurable: steady-state Newton step from B
    else:
        x = math.log(pa) - ga * (math.log(pb) - math.log(pa)) / (gb - ga)
    lo, hi = min(pa, pb), max(pa, pb)
    if ga * gb > 0:                           # not bracketed: cap the extrapolation
        x = min(max(x, math.log(lo) - 0.02), math.log(hi) + 0.02)
    p = math.exp(x); out.append(p)
    rows.append((t, pa, ga, pb, gb, p, "bracketed" if ga * gb <= 0 else "extrapolated"))
open(sys.argv[3], "w").write(
    "# per-period secant between two loop-0 runs (flat seed and Newton seed), 27 Sep; see bracket_seed.py\n"
    f"# periods 1 to {T}\n" + "".join(f"{v:.15f}\n" for v in out))
for r in rows:
    if r[0] in (1, 2, 5, 10, 15, 20, 25, 30, 40, 45, 50, 59):
        print("t=%2d  A %.4f g%+.4f | B %.4f g%+.4f -> %.4f %s" % r)
