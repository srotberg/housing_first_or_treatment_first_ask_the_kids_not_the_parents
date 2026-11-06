import sys, numpy as np, pandas as pd
d = pd.read_stata(sys.argv[1], columns=["wgt", "age", "wageinc", "income"])
m = (d.age >= 26) & (d.age <= 65) & (d.wageinc > 0)
print("SCF 2022 summary extract, households 26-65 with wage income > 0:",
      "mean wageinc", round(np.average(d.wageinc[m], weights=d.wgt[m])),
      "| N(wt) m", round(d.wgt[m].sum() / 1e6, 1))
o = np.argsort(d.wageinc[m].values); c = np.cumsum(d.wgt[m].values[o]) / d.wgt[m].sum()
print("median wageinc", round(np.interp(0.5, c, d.wageinc[m].values[o])))
