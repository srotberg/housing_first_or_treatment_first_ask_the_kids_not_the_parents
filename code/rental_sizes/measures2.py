"""Second pass: owners' rent with PUMA fixed effects, the model's rung costs in the paper's
dollars, and the model's universe (every 26-50 household has a child)."""
import sys
import numpy as np
import pandas as pd

df = pd.read_pickle(sys.argv[1])
w = df.WGTP.astype(float)
age = df.HHLDRAGEP
a2685 = ((age >= 26) & (age <= 85)).values
a2650 = ((age >= 26) & (age <= 50)).values
a5185 = ((age >= 51) & (age <= 85)).values
ownkid = df.HUPAOC.isin([1, 2, 3]).values
renter = (df.TEN == 3).values
owner = df.TEN.isin([1, 2]).values
nocash = (df.TEN == 4).values
cr = renter & (df.GRNTP > 0).values
bd = df.BDSP.clip(upper=5)


def wq(x, wt, q):
    x = np.asarray(x, float); wt = np.asarray(wt, float)
    o = np.argsort(x)
    c = np.cumsum(wt[o]) / wt[o].sum()
    return np.interp(q, c, x[o])


def shares3(x, m, t1, t2):
    xx, ww = np.asarray(x)[m], w.values[m]
    s = np.array([ww[xx < t1].sum(), ww[(xx >= t1) & (xx < t2)].sum(), ww[xx >= t2].sum()])
    return 100 * s / s.sum()


# hedonic with PUMA fixed effects, within transformation on cash renters
X = pd.concat([pd.get_dummies(df.BDSP.clip(upper=5), prefix="bd", drop_first=True),
               pd.get_dummies(df.RMSP.clip(upper=9), prefix="rm", drop_first=True),
               pd.get_dummies(df.BLD, prefix="bld", drop_first=True),
               pd.get_dummies(df.YRBLT.clip(upper=2020), prefix="yb", drop_first=True)], axis=1).astype(float)
puma = (df.STATE.astype(str) + "_" + df.PUMA.astype(str)).values
y = np.log(df.GRNTP.where(cr).astype(float))
R = pd.DataFrame(X.values[cr], columns=X.columns)
R["y"] = y.values[cr]; R["w"] = w.values[cr]; R["g"] = puma[cr]
cols = list(X.columns) + ["y"]
wm = R[cols].mul(R.w, axis=0).groupby(R.g).sum().div(R.w.groupby(R.g).sum(), axis=0)
D = R[cols].values - wm.loc[R.g].values
sw = np.sqrt(R.w.values)
beta, *_ = np.linalg.lstsq(D[:, :-1] * sw[:, None], D[:, -1] * sw, rcond=None)
fe = wm["y"] - wm[list(X.columns)].values @ beta          # PUMA effect
xb_r = R[list(X.columns)].values @ beta + fe.loc[R.g].values
resid = R.y.values - xb_r
r2 = 1 - np.average(resid**2, weights=R.w) / np.average((R.y - np.average(R.y, weights=R.w))**2, weights=R.w)
smear = np.average(np.exp(resid), weights=R.w)
print(f"hedonic with PUMA FE: renters n={cr.sum()}, PUMAs={len(fe)}, weighted R2={r2:.3f}, smearing={smear:.3f}")
fe_all = pd.Series(puma).map(fe).fillna(np.average(fe.loc[R.g], weights=R.w)).values
pred = np.exp(X.values @ beta + fe_all) * smear
rng = np.random.default_rng(1)
draw = rng.choice(resid, size=len(df), p=R.w.values / R.w.sum())

spend = {
    "renters' gross rent + owners' hedonic rent (PUMA FE) + renter residual":
        np.where(cr, df.GRNTP, np.where(owner, pred * np.exp(draw), np.nan)),
    "renters' gross rent + owners' hedonic rent (PUMA FE), no residual":
        np.where(cr, df.GRNTP, np.where(owner, pred, np.nan)),
    "renters' gross rent + owners' value x 5%/12 (dispersion upper bound)":
        np.where(cr, df.GRNTP, np.where(owner, df.VALP * 0.05 / 12, np.nan)),
    "gross rent, cash renters only":
        np.where(cr, df.GRNTP, np.nan),
}

# the model's rung costs in dollars at the paper's own scale (export_results.py:495):
# average labour income = $9m / vsl ratio 80 = $112,500; model average labour income 1.5898
usd_per_unit = 9e6 / 80 / 1.5898179903829757
h2 = 0.040674274685127916
rung = np.array([h2, 4 * h2, 8 * h2]) * usd_per_unit / 12   # $/month
mid = np.sqrt(rung[:-1] * rung[1:])
print(f"model rungs at the paper's dollar scale: ${rung[0]:.0f}, ${rung[1]:.0f}, ${rung[2]:.0f} a month; "
      f"log midpoints ${mid[0]:.0f}, ${mid[1]:.0f}")
model_mean = (0.010549615494018028 * rung[0] + 0.13244141117438360 * rung[1] + 0.85700897333159842 * rung[2])
print(f"model mean housing spending ${model_mean:.0f} a month")
for lab, x in spend.items():
    m = a2685 & ~np.isnan(x) & (np.nan_to_num(x) > 0)
    s_mid = shares3(x, m, mid[0], mid[1])
    s_flr = shares3(x, m, rung[1], rung[2])
    p10 = wq(x[m], w.values[m], 0.10)
    s_p10 = shares3(x, m, 2 * p10, np.sqrt(32) * p10)
    q = [wq(x[m], w.values[m], p) for p in (0.10, 0.5, 0.9)]
    mean = np.average(x[m], weights=w.values[m])
    print(f"\n{lab}  (householder 26-85, N={w.values[m].sum()/1e6:.1f}m)")
    print(f"   p10 {q[0]:.0f}  p50 {q[1]:.0f}  p90 {q[2]:.0f}  mean {mean:.0f};  p50/p10 {q[1]/q[0]:.2f}, p90/p10 {q[2]/q[0]:.2f}")
    print(f"   paper-dollar rungs, log-midpoint bins  : {s_mid[0]:5.1f} {s_mid[1]:5.1f} {s_mid[2]:5.1f}")
    print(f"   paper-dollar rungs, rung-floor bins    : {s_flr[0]:5.1f} {s_flr[1]:5.1f} {s_flr[2]:5.1f}")
    print(f"   base = data p10 (${p10:.0f}), log midpoints: {s_p10[0]:5.1f} {s_p10[1]:5.1f} {s_p10[2]:5.1f}")
    # same paper-dollar bins, model universe: 26-50 with own child + 51-85
    mu = m & ((a2650 & ownkid) | a5185)
    s_mu = shares3(x, mu, mid[0], mid[1])
    print(f"   paper-dollar rungs, log-mid, 26-50 with own child + 51-85: {s_mu[0]:5.1f} {s_mu[1]:5.1f} {s_mu[2]:5.1f}")

# the model's universe re-weighted to the data's age distribution of householders 26-85:
# at each age 26-50 the bedroom distribution of householders with own children, at 51-85 of all
cut = np.select([bd <= 1, bd == 2], [0, 1], 2)
cut2 = np.select([bd == 0, bd == 1], [0, 1], 2)
for nm, c in [("{0,1}/{2}/{3+}", cut), ("{0}/{1}/{2+}", cut2)]:
    tot = np.zeros(3)
    for a in range(26, 86):
        at = (age == a).values
        mass = w.values[at].sum()
        sel = at & ownkid if a <= 50 else at
        d = np.array([w.values[sel & (c == k)].sum() for k in range(3)])
        tot += mass * d / d.sum()
    tot = 100 * tot / tot.sum()
    print(f"\nmodel universe re-weighted by age (26-50 all with own child <18, 51-85 all), {nm}: "
          f"{tot[0]:.1f} {tot[1]:.1f} {tot[2]:.1f}")

# no-cash renters, for the record
print(f"\nno-cash-rent occupied units, share of 26-85: {100*w.values[nocash & a2685].sum()/w.values[a2685].sum():.2f}%")

print("\n=== scale sensitivity, PUMA-FE + residual measure, householder 26-85")
x = spend["renters' gross rent + owners' hedonic rent (PUMA FE) + renter residual"]
m = a2685 & ~np.isnan(x) & (np.nan_to_num(x) > 0)
q143 = wq(x[m], w.values[m], 1 - 0.85700897333159842)
need = q143 / mid[1]
print(f"14.3th percentile ${q143:.0f}/month; the model's top share needs a dollar scale x{need:.3f} of the paper's,"
      f" i.e. average labour income ${need*112500:,.0f}")
for ali in (need * 112500, 82149, 112500, 128857):
    k = ali / 112500
    s = shares3(x, m, mid[0] * k, mid[1] * k)
    print(f"   average labour income ${ali:>9,.0f}: rungs ${rung[0]*k:.0f}/{rung[1]*k:.0f}/{rung[2]*k:.0f}, shares {s[0]:.1f} {s[1]:.1f} {s[2]:.1f}")

print("\n=== scale at which the model's mean housing spending equals the data mean")
for lab in ["renters' gross rent + owners' hedonic rent (PUMA FE) + renter residual",
            "renters' gross rent + owners' hedonic rent (PUMA FE), no residual",
            "renters' gross rent + owners' value x 5%/12 (dispersion upper bound)"]:
    x = spend[lab]; m = a2685 & ~np.isnan(x) & (np.nan_to_num(x) > 0)
    k = np.average(x[m], weights=w.values[m]) / model_mean
    s = shares3(x, m, mid[0] * k, mid[1] * k)
    print(f"   {lab[:70]}: scale x{k:.3f} (average labour income ${112500*k:,.0f}), shares {s[0]:.1f} {s[1]:.1f} {s[2]:.1f}")
