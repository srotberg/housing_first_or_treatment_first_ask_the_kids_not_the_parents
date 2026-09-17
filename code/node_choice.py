exec(open('grid_replica.py').read().split('print("REPLICA')[0])
def bis(f, lo, hi, t, it=90):
    for _ in range(it):
        m = 0.5*(lo+hi)
        if (f(lo)-t)*(f(m)-t) <= 0: hi = m
        else: lo = m
    return 0.5*(lo+hi)
K = 1.9506                       # held, so the comparison is grid shape only
print("bottom node held at 0.700 pc of the population; kkk_sigma_scale held at 1.9506")
print()
print("   n   s_b     step    node1     next rung   mass to lift (<0.15)   blocks vs 7")
print("   " + "-"*74)
for n in (7, 9, 11, 13, 15, 17):
    sb = bis(lambda s: build(n, s, 3.0, K, 0.0, 1.0, 1.0)[0][0], 2.2, 3.8, 0.0070)
    m0, g0, _ = build(n, sb, 3.0, K, 0.0, 1.0, 1.0)
    step = g0[1]/g0[0] - 1.0
    lift = sum(m0[j] for j in range(1, n) if g0[j] < 0.15)
    print("  %2d  %.4f  %4.0f pc  %.5f   %5.2f pc     %5.2f pc              %.2f - %.2f" %
          (n, sb, 100*step, g0[0], 100*(m0[0]+m0[1]), 100*lift, n/7.0, (n/7.0)**2))
