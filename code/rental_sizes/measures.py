"""Candidate data counterparts to the model's three rental rungs, 2023 ACS 1-year PUMS.

Model: h_2, h_3 = 4 h_2, h_4 = 8 h_2, all rented at one price per unit, shares
1.06 / 13.24 / 85.70 of housed households aged 26 to 85.
"""
import sys
import numpy as np
import pandas as pd

df = pd.read_pickle(sys.argv[1])
w = df.WGTP.astype(float)
R3, R4 = 4.0, 8.0                       # benchmark rung ratios (PARAM_HANDOVER.bench.txt)
LO, HI = np.sqrt(R3), np.sqrt(R3 * R4)  # log midpoints between rungs: 2 and 5.66


def wq(x, wt, q):
    o = np.argsort(x.values)
    xs, ws = x.values[o], wt.values[o]
    c = np.cumsum(ws) / ws.sum()
    return np.interp(q, c, xs)


def shares(cat, wt):
    s = wt.groupby(cat).sum()
    s = s / s.sum() * 100
    return [s.get(k, 0.0) for k in (0, 1, 2)]


def show(label, cat, mask=None):
    m = np.ones(len(df), bool) if mask is None else mask
    s = shares(cat[m], w[m])
    print(f"{label:<78s} {s[0]:6.1f} {s[1]:6.1f} {s[2]:6.1f}   N={w[m].sum()/1e6:6.1f}m")
    return s


age = df.HHLDRAGEP
a2685 = ((age >= 26) & (age <= 85)).values
a2650 = ((age >= 26) & (age <= 50)).values
a5185 = ((age >= 51) & (age <= 85)).values
ownkid = df.HUPAOC.isin([1, 2, 3]).values      # own children under 18 present
single_parent = df.HHT2.isin([6, 10]).values    # householder, no spouse/partner, own kids <18
alone = df.HHT2.isin([5, 9]).values
np_le2 = (df.NP <= 2).values
renter = (df.TEN == 3).values
owner = df.TEN.isin([1, 2]).values

bd = df.BDSP.clip(upper=5)
print("=== A. Bedrooms, ordinal cuts")
cut_0112 = pd.Series(np.select([bd <= 1, bd == 2], [0, 1], 2), index=df.index)
cut_0_1_2 = pd.Series(np.select([bd == 0, bd == 1], [0, 1], 2), index=df.index)
cut_0113 = pd.Series(np.select([bd <= 1, bd <= 3], [0, 1], 2), index=df.index)
cut_01_2_3 = pd.Series(np.select([bd <= 1, bd <= 2, bd == 3], [0, 1, 2], 3), index=df.index)
show("{0,1}/{2}/{3+}  all occupied units (B25042 replication)", cut_0112)
show("{0,1}/{2}/{3+}  householder 26-85", cut_0112, a2685)
show("{0,1}/{2}/{3+}  renters only", cut_0112, renter)
show("{0,1}/{2,3}/{4+} all occupied", cut_0113)
show("{0}/{1}/{2+}    all occupied", cut_0_1_2)
show("{0}/{1}/{2+}    householder 26-85", cut_0_1_2, a2685)
show("{0}/{1}/{2+}    renters only", cut_0_1_2, renter)
bshare = w.groupby(bd).sum() / w.sum() * 100
print("bedroom shares, all occupied:", {int(k): round(v, 2) for k, v in bshare.items()})
bshare = w[a2685].groupby(bd[a2685]).sum() / w[a2685].sum() * 100
print("bedroom shares, householder 26-85:", {int(k): round(v, 2) for k, v in bshare.items()})

print("\n=== C. Universe: the model's household (bedrooms {0,1}/{2}/{3+} and {0}/{1}/{2+})")
for lab, m in [("householder 26-50, own child <18", a2650 & ownkid),
               ("householder 26-50, single parent with own child <18", a2650 & single_parent),
               ("householder 26-50, any", a2650),
               ("householder 51-85, any", a5185),
               ("householder 51-85, living alone", a5185 & alone),
               ("householder 26-85, 1 or 2 persons", a2685 & np_le2)]:
    show("{0,1}/{2}/{3+}  " + lab, cut_0112, m)
    show("{0}/{1}/{2+}    " + lab, cut_0_1_2, m)
# model-like composition: 26-50 single parent + 51-85 alone, each weighted by its
# data mass (the model weights by survival, not reported here)
ml = (a2650 & single_parent) | (a5185 & alone)
show("{0,1}/{2}/{3+}  model-like: 26-50 single parent + 51-85 living alone", cut_0112, ml)
show("{0}/{1}/{2+}    model-like: 26-50 single parent + 51-85 living alone", cut_0_1_2, ml)

print("\n=== B. Rooms, binned at the model's own ratios")
rm = df.RMSP.astype(float)
base_rooms = wq(rm[bd == 0], w[bd == 0], 0.5)
p10_rooms = wq(rm, w, 0.10)
print(f"median rooms of a no-bedroom unit = {base_rooms}, p10 rooms all occupied = {p10_rooms}, "
      f"median rooms all = {wq(rm, w, 0.5)}")
print("rooms distribution (all occupied, %):",
      {int(k): round(v, 2) for k, v in (w.groupby(rm.clip(upper=9)).sum() / w.sum() * 100).items()})
for base, lab in [(base_rooms, "studio median"), (2.0, "2 rooms")]:
    cmid = pd.Series(np.select([rm < LO * base, rm < HI * base], [0, 1], 2), index=df.index)
    cfloor = pd.Series(np.select([rm < R3 * base, rm < R4 * base], [0, 1], 2), index=df.index)
    show(f"rooms, base={base:g} ({lab}), log-midpoint bins <{LO*base:.2f}, <{HI*base:.2f}", cmid, a2685)
    show(f"rooms, base={base:g} ({lab}), rung-floor bins <{R3*base:g}, <{R4*base:g}", cfloor, a2685)
# rooms per sqrt(persons), the model's equivalence scale
eq = rm / np.sqrt(df.NP)
b = wq(eq[a2685], w[a2685], 0.10)
ceq = pd.Series(np.select([eq < LO * b, eq < HI * b], [0, 1], 2), index=df.index)
show(f"rooms/sqrt(persons), base = p10 = {b:.2f}, log-midpoint bins", ceq, a2685)

print("\n=== D. Housing services in dollars")
# hedonic rent equation on cash renters, used to impute owners' rental equivalence
cr = renter & (df.GRNTP > 0).values
def dummies(d):
    X = [pd.get_dummies(d.BDSP.clip(upper=5), prefix="bd", drop_first=True),
         pd.get_dummies(d.RMSP.clip(upper=9), prefix="rm", drop_first=True),
         pd.get_dummies(d.BLD, prefix="bld", drop_first=True),
         pd.get_dummies(d.YRBLT.clip(upper=2020), prefix="yb", drop_first=True)]
    return pd.concat(X, axis=1).astype(float)
Xall = dummies(df)
St = pd.get_dummies(df.STATE, prefix="st", drop_first=True).astype(float)
Xs = pd.concat([Xall, St], axis=1)
Xs.insert(0, "const", 1.0)
y = np.log(df.GRNTP[cr].astype(float))
sw = np.sqrt(w[cr].values)
beta, *_ = np.linalg.lstsq(Xs[cr].values * sw[:, None], y.values * sw, rcond=None)
resid = y.values - Xs[cr].values @ beta
r2 = 1 - np.average(resid**2, weights=w[cr]) / np.average((y - np.average(y, weights=w[cr]))**2, weights=w[cr])
smear = np.average(np.exp(resid), weights=w[cr])
print(f"hedonic log gross rent: n={cr.sum()}, weighted R2={r2:.3f}, smearing={smear:.3f}")
pred_state = np.exp(Xs.values @ beta) * smear
# national-price quantity index: same coefficients, location set to the renter-weighted mean state effect
st_eff = St.values @ beta[-St.shape[1]:]
mean_st = np.average(st_eff[cr], weights=w[cr])
pred_nat = np.exp(Xs.values @ beta - st_eff + mean_st) * smear

rng = np.random.default_rng(0)
own_resid = rng.choice(resid, size=len(df), p=w[cr].values / w[cr].sum())

meas = {
    "gross rent, cash renters only": (df.GRNTP.where(cr).astype(float), cr),
    "renters' gross rent + owners' hedonic rent (state prices) + renter residual":
        (pd.Series(np.where(cr, df.GRNTP, np.where(owner, pred_state * np.exp(own_resid), np.nan)), index=df.index), cr | owner),
    "hedonic rent for all (state prices), no residual":
        (pd.Series(np.where(cr | owner, pred_state, np.nan), index=df.index), cr | owner),
    "hedonic rent for all at NATIONAL prices (a quantity index), no residual":
        (pd.Series(np.where(cr | owner, pred_nat, np.nan), index=df.index), cr | owner),
    "renters' gross rent + owners' value x 5%/12":
        (pd.Series(np.where(cr, df.GRNTP, np.where(owner, df.VALP * 0.05 / 12, np.nan)), index=df.index), cr | owner),
}
studio_rent = wq(df.GRNTP[cr & (bd == 0).values].astype(float), w[cr & (bd == 0).values], 0.5)
p10_rent = wq(df.GRNTP[cr].astype(float), w[cr], 0.10)
print(f"median gross rent of a cash-rented studio = {studio_rent:.0f}, p10 cash gross rent = {p10_rent:.0f}, "
      f"median cash gross rent = {wq(df.GRNTP[cr].astype(float), w[cr], 0.5):.0f}")
out = {}
for lab, (x, ok) in meas.items():
    m = ok & a2685 & x.notna().values & (x > 0).values
    xx = x.fillna(0)
    for bname, base in [("studio median rent", studio_rent if "NATIONAL" not in lab and "no residual" not in lab
                          else wq(x[m & (bd == 0).values], w[m & (bd == 0).values], 0.5)),
                         ("p10 of the measure", wq(x[m], w[m], 0.10))]:
        c = pd.Series(np.select([xx < LO * base, xx < HI * base], [0, 1], 2), index=df.index)
        s = show(f"{lab[:52]:<52s} base {bname[:12]} ${base:5.0f}", c, m)
        out[(lab, bname)] = s
    q = [wq(x[m], w[m], p) for p in (0.10, 0.5, 0.9)]
    print(f"    p10, p50, p90 = {q[0]:.0f}, {q[1]:.0f}, {q[2]:.0f}; p50/p10 = {q[1]/q[0]:.2f}, p90/p10 = {q[2]/q[0]:.2f}")
    # implied ratios: median of the measure within the bedroom bins {0,1},{2},{3+}
    med = [wq(x[m & (cut_0112 == k).values], w[m & (cut_0112 == k).values], 0.5) for k in (0, 1, 2)]
    med2 = [wq(x[m & (cut_0_1_2 == k).values], w[m & (cut_0_1_2 == k).values], 0.5) for k in (0, 1, 2)]
    print(f"    median within {{0,1}}/{{2}}/{{3+}} BR: {med[0]:.0f} {med[1]:.0f} {med[2]:.0f}  ratios 1 : {med[1]/med[0]:.2f} : {med[2]/med[0]:.2f}")
    print(f"    median within {{0}}/{{1}}/{{2+}} BR:   {med2[0]:.0f} {med2[1]:.0f} {med2[2]:.0f}  ratios 1 : {med2[1]/med2[0]:.2f} : {med2[2]/med2[0]:.2f}")

print("\n=== E. Share at or above 8x and 4x the cheapest, and what the model's shares would need")
x, ok = meas["renters' gross rent + owners' hedonic rent (state prices) + renter residual"]
m = ok & a2685 & (x > 0).values
for p in (0.0106, 0.1430):
    print(f"   quantile {p:.4f} of housing spending, 26-85: ${wq(x[m], w[m], p):.0f}/month")
print(f"   ratio of the 14.3th percentile to the 1.06th: {wq(x[m], w[m], 0.143)/wq(x[m], w[m], 0.0106):.2f}")
r = rm[a2685]
print(f"   rooms: 1.06th pct {wq(r, w[a2685], 0.0106)}, 14.3th pct {wq(r, w[a2685], 0.143)}")
