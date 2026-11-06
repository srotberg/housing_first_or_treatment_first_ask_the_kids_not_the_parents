import sys, numpy as np, pandas as pd
df = pd.read_pickle(sys.argv[1]); w = df.WGTP.astype(float).values
a = ((df.HHLDRAGEP >= 26) & (df.HHLDRAGEP <= 85)).values
bd = df.BDSP.clip(upper=5).values; rm = df.RMSP.astype(float).values
def wq(x, wt, q):
    o = np.argsort(x); c = np.cumsum(wt[o]) / wt[o].sum(); return np.interp(q, c, x[o])
for nm, c in [("{0}/{1}/{2+}", np.select([bd == 0, bd == 1], [0, 1], 2)),
              ("{0,1}/{2}/{3+}", np.select([bd <= 1, bd == 2], [0, 1], 2))]:
    med = [wq(rm[a & (c == k)], w[a & (c == k)], 0.5) for k in range(3)]
    mean = [np.average(rm[a & (c == k)], weights=w[a & (c == k)]) for k in range(3)]
    print(nm, "median rooms", med, "ratios 1 :", round(med[1]/med[0], 2), ":", round(med[2]/med[0], 2),
          "| mean rooms (9 = 9+)", [round(m, 2) for m in mean], "ratios 1 :", round(mean[1]/mean[0], 2), ":", round(mean[2]/mean[0], 2))
for b in range(6):
    s = a & (bd == b)
    print("bedrooms", b, "median rooms", wq(rm[s], w[s], 0.5), "mean", round(np.average(rm[s], weights=w[s]), 2))
