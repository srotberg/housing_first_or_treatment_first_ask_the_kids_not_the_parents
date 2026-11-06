import sys, numpy as np, pandas as pd
d = pd.read_csv(sys.argv[1], usecols=["UNITSIZE", "WEIGHT", "TENURE", "INTSTATUS", "HHAGE", "BEDROOMS",
                                      "TOTROOMS", "NUMPEOPLE", "NUMYNGKIDS", "NUMOLDKIDS"], dtype=str)
for c in d.columns:
    d[c] = d[c].str.strip("'")
d["WEIGHT"] = d.WEIGHT.astype(float)
print(d.INTSTATUS.value_counts().to_dict())
o = d[d.INTSTATUS == "1"].copy()
print("occupied N(wt) =", o.WEIGHT.sum() / 1e6, "m; UNITSIZE values:",
      o.groupby("UNITSIZE").WEIGHT.sum().div(o.WEIGHT.sum()).mul(100).round(2).to_dict())
o["age"] = pd.to_numeric(o.HHAGE, errors="coerce")
o["kids"] = pd.to_numeric(o.NUMYNGKIDS, errors="coerce").fillna(0) + pd.to_numeric(o.NUMOLDKIDS, errors="coerce").fillna(0)
v = o[o.UNITSIZE.isin([str(k) for k in range(1, 10)])].copy()
v["u"] = v.UNITSIZE.astype(int)
print("reported share of occupied:", round(100 * v.WEIGHT.sum() / o.WEIGHT.sum(), 1))
def sh(m, bins):
    s = [v.WEIGHT[m & v.u.isin(b)].sum() for b in bins]; t = sum(s); return [round(100 * x / t, 1) for x in s]
all_ = v.u > 0
a2685 = (v.age >= 26) & (v.age <= 85)
kid = (v.age >= 26) & (v.age <= 50) & (v.kids > 0)
# categories: 1 <500, 2 500-749, 3 750-999, 4 1000-1499, 5 1500-1999, 6 2000-2499, 7 2500-2999, 8 3000-3999, 9 4000+
for lab, bins in [("base <500 sq ft (studio ~ 400-500): <1000 | 1000-2999 | 3000+ (log mids 2x, 5.66x of 500)", [[1, 2, 3], [4, 5, 6, 7], [8, 9]]),
                  ("rung floors at 4x and 8x of 500 sq ft: <2000 | 2000-3999 | 4000+", [[1, 2, 3, 4, 5], [6, 7, 8], [9]]),
                  ("base 750 sq ft: <1500 | 1500-3999 | 4000+ (log mids 1500, 4243)", [[1, 2, 3, 4], [5, 6, 7, 8], [9]])]:
    print(lab)
    for un, m in [("all occupied", all_), ("householder 26-85", a2685), ("26-50 with children", kid)]:
        print("   ", un, sh(m, bins))
