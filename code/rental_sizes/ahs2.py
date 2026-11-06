import sys, pandas as pd
d = pd.read_csv(sys.argv[1], usecols=["UNITSIZE", "WEIGHT", "INTSTATUS", "BEDROOMS"], dtype=str)
for c in d.columns: d[c] = d[c].str.strip("'")
d = d[(d.INTSTATUS == "1") & d.UNITSIZE.isin([str(k) for k in range(1, 10)])]
d["WEIGHT"] = d.WEIGHT.astype(float)
for b in ["0", "1", "2", "3", "4"]:
    s = d[d.BEDROOMS == b]
    print("bedrooms", b, s.groupby("UNITSIZE").WEIGHT.sum().div(s.WEIGHT.sum()).mul(100).round(1).to_dict())
