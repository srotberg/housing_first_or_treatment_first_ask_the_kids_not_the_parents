import sys, numpy as np, pandas as pd
df = pd.read_pickle(sys.argv[1]); w = df.WGTP.astype(float).values; age = df.HHLDRAGEP.values
bd = df.BDSP.clip(upper=5).values; ownkid = df.HUPAOC.isin([1, 2, 3]).values
c = np.select([bd == 0, bd <= 2], [0, 1], 2)
def sh(m):
    s = np.array([w[m & (c == k)].sum() for k in range(3)]); return 100 * s / s.sum()
print("{0}/{1,2}/{3+} householder 26-85:", np.round(sh((age >= 26) & (age <= 85)), 1))
print("{0}/{1,2}/{3+} 26-50 own child:", np.round(sh((age >= 26) & (age <= 50) & ownkid), 1))
tot = np.zeros(3)
for a in range(26, 86):
    at = age == a; mass = w[at].sum(); sel = at & ownkid if a <= 50 else at
    tot += mass * sh(sel) / 100
print("{0}/{1,2}/{3+} model universe age-reweighted:", np.round(100 * tot / tot.sum(), 1))
