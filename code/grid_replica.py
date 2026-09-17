import math
from math import erf, sqrt, exp, log

LIFE, RET = 60, 20
NW = LIFE - RET           # 40 working ages
RHO_F, SD_F = 0.5, 0.309
RHO_S, SD_S = 0.9, 0.20
TARGET_SHARE = 0.172

def Phi(x): return 0.5*(1.0+erf(x/sqrt(2.0)))

def build(n, s_b, s_t, kkk, bpl, merge_lo, merge_hi):
    sf, ss = kkk*SD_F, kkk*SD_S
    var_fix = sf**2/(1-RHO_F**2); var_eta = ss**2
    var = [0.0]*(NW+1); var[1] = var_eta+var_fix
    for i in range(2, NW+1): var[i] = RHO_S**2*var[i-1]+var_eta
    sd = [0.0]+[sqrt(var[i]) for i in range(1, NW+1)]
    z = {}; w = {}
    for i in range(1, NW+1):
        w[i] = (s_b+s_t)*sd[i]/(n-1)
        z[i] = [-s_b*sd[i]+w[i]*(j) for j in range(n)]
    # age-1 masses, Tauchen midpoints
    m = [0.0]*n
    m[0] = Phi((z[1][0]+0.5*w[1])/sd[1])
    for j in range(1, n-1):
        m[j] = Phi((z[1][j]+0.5*w[1])/sd[1])-Phi((z[1][j]-0.5*w[1])/sd[1])
    m[n-1] = 1-Phi((z[1][n-1]-0.5*w[1])/sd[1])
    tot = sum(m); m = [x/tot for x in m]
    # mean normalisation on the age-1 grid, same constant at every age
    mean1 = sum(m[j]*exp(z[1][j]) for j in range(n))
    shift = log(mean1)
    g = {i: [exp(z[i][j]-shift) for j in range(n)] for i in range(1, NW+1)}
    # bottom override, per age
    if bpl > 0:
        lo = max(1, min(int(merge_lo+0.5), n-1)) - 1      # 0-based
        hi = max(lo+1, min(int(merge_hi+0.5), n-1)) - 1
        hi = max(lo, hi)
        bmass = sum(m[lo:hi+1])
        for i in range(1, NW+1):
            bold = sum(m[j]*g[i][j] for j in range(lo, hi+1))/bmass
            low = sum(m[j]*g[i][j] for j in range(0, lo))
            resc = (1-low-bmass*bpl)/(1-low-bmass*bold)
            for j in range(lo, hi+1): g[i][j] = bpl
            for j in range(hi+1, n): g[i][j] *= resc
    # pooled bottom-half share
    pool = sorted((g[i][j], m[j]/NW) for i in range(1, NW+1) for j in range(n))
    total = sum(y*mm for y, mm in pool)
    acc = 0.0; cum = 0.0
    for y, mm in pool:
        if cum+mm <= 0.5: acc += y*mm; cum += mm
        else: acc += y*(0.5-cum); break
    return m, g[1], acc/total

n, s_t, kkk = 7, 3.0, 1.9506
m, g1, share = build(n, 3.4113, s_t, kkk, 0.95008064760720046, 2.0, 2.0)
print("REPLICA of the live run (s_b=3.4113, kkk=1.9506)")
print("  masses  :", " ".join("%.6f" % x for x in m))
print("  grid a1 :", " ".join("%.6f" % x for x in g1))
print("  bottom-half share = %.5f   (log says 0.20131)" % share)
print("  bottom node mass  = %.5f   (log says 0.0020072)" % m[0])

def bisect(f, lo, hi, tgt, it=80):
    for _ in range(it):
        mid = 0.5*(lo+hi)
        if (f(lo)-tgt)*(f(mid)-tgt) <= 0: hi = mid
        else: lo = mid
    return 0.5*(lo+hi)

mass_of = lambda sb: build(n, sb, s_t, kkk, 0.95008064760720046, 2.0, 2.0)[0][0]
print("\nBOTTOM NODE MASS vs kkk_s_deviation_bottom (7 nodes, everything else held)")
for tgt in (0.0040, 0.0055, 0.0070, 0.0085, 0.0100):
    sb = bisect(mass_of, 2.5, 3.6, tgt)
    mm, gg, sh = build(n, sb, s_t, kkk, 0.95008064760720046, 2.0, 2.0)
    print("   mass %.4f -> s_b = %.4f   node1 level %.5f   bottom-half share %.5f" % (tgt, sb, gg[0], sh))

SB = bisect(mass_of, 2.5, 3.6, 0.0070)
share_of = lambda k: build(n, SB, s_t, k, 0.95008064760720046, 2.0, 2.0)[2]
KK = bisect(share_of, 1.5, 2.6, 0.20131)
mm, gg, sh = build(n, SB, s_t, KK, 0.95008064760720046, 2.0, 2.0)
print("\nHOLDING THE SHARE AT 0.20131 while the bottom node carries 0.70 per cent:")
print("   kkk_s_deviation_bottom = %.4f   kkk_sigma_scale = %.4f" % (SB, KK))
print("   masses :", " ".join("%.6f" % x for x in mm))
print("   grid a1:", " ".join("%.6f" % x for x in gg))
print("   bottom-half share = %.5f   bottom node mass = %.5f" % (sh, mm[0]))

print("\n--- IF THE GRID GOES TO 15 NODES ---")
n15 = 15
mass15 = lambda sb: build(n15, sb, s_t, kkk, 0.0, 1.0, 1.0)[0][0]
SB15 = bisect(mass15, 2.4, 3.8, 0.0070)
mm0, gg0, _ = build(n15, SB15, s_t, kkk, 0.0, 1.0, 1.0)
cum = 0.0
print("   s_b = %.4f  (bottom node 0.70 pc).  no override, levels and cumulative mass:" % SB15)
for j in range(8):
    cum += mm0[j]
    print("      node %2d  level %.5f   mass %.5f   cum %.5f" % (j+1, gg0[j], mm0[j], cum))
# lift nodes 2..k so only node 1 is left below the priced-out threshold
k = max(j+1 for j in range(n15) if gg0[j] < 0.20)
share15 = lambda kk2: build(n15, SB15, s_t, kk2, 0.95008064760720046, 2.0, float(k))[2]
KK15 = bisect(share15, 1.5, 2.8, 0.20131)
mm1, gg1, sh1 = build(n15, SB15, s_t, KK15, 0.95008064760720046, 2.0, float(k))
print("   merge nodes 2..%d (all below 0.20), kkk_sigma_scale = %.4f holds the share" % (k, KK15))
print("   masses :", " ".join("%.5f" % x for x in mm1[:8]))
print("   grid a1:", " ".join("%.5f" % x for x in gg1[:8]))
print("   bottom-half share = %.5f   bottom node mass = %.5f   lifted mass = %.5f" %
      (sh1, mm1[0], sum(mm1[1:k])))
