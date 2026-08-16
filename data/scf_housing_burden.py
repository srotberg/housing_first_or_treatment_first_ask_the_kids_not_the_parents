"""
scf_housing_burden.py -- housing-cost-to-income targets from SCF 2022.

WHY THIS DIFFERS FROM THE PAPER'S TARGET
----------------------------------------
The paper targets "average rent-to-income ratio among renters = 0.33". In the
simplified model there is no homeownership, so EVERY household rents. Matching a
renters-only statistic would import the selection in who rents: renters in the
data are younger, poorer, and hold less wealth than owners. The model's renters
are the whole population, so the target has to be housing costs over ALL
households.

VALUING OWNER-OCCUPIED HOUSING
------------------------------
Two measures, and the choice matters a lot:

  cash-flow  : property tax + 12 * mortgage payment
  user cost  : 8.3% of house value (the paper's own rent-to-price ratio,
               from Garner and Verbrugge)

The cash-flow measure is wrong for this model. An outright owner with no
mortgage records almost no housing cost while consuming a lot of housing
services, and mortgage payments include principal, which is saving rather than
consumption. The model's rent is the flow price of housing services, so the
right analogue is imputed rent -- the user-cost measure.

MEAN OF RATIOS VS AGGREGATE RATIO
---------------------------------
The mean of household-level ratios is badly trim-sensitive (0.32 to 0.40
depending on where extreme ratios from near-zero incomes are cut off), so it is
a poor calibration target. The aggregate ratio -- total housing cost over total
income -- is trim-free and is what this script recommends.

Run:  python3 scf_housing_burden.py
"""
import numpy as np
import pandas as pd

RENT_PRICE_RATIO = 0.083     # paper's rent-to-house-price, Garner and Verbrugge
AGE_LO, AGE_HI = 26, 85      # the model's age range


def load():
    df = pd.read_stata("SCF_2022.dta")
    d = df[(df.age >= AGE_LO) & (df.age <= AGE_HI) & (df.income > 0)].copy()
    return d


def measures(d):
    w = d.wgt.values
    inc = d.income.values
    own = (d.hhouses == 1).values
    rent_flow = 12 * d.rent.values
    cash = d.tpay.values + 12 * d.mortpay.values
    user = RENT_PRICE_RATIO * d.houses.values
    return w, inc, own, rent_flow, cash, user


def wshare(mask, w):
    return np.sum(w[mask]) / np.sum(w)


def main():
    d = load()
    w, inc, own, rent_flow, cash, user = measures(d)

    print("SCF 2022, ages %d-%d, income > 0" % (AGE_LO, AGE_HI))
    print("households (weighted): %,.0f" .replace(",", "") % np.sum(w))
    print("homeownership rate   : %.2f %%" % (100 * wshare(own, w)))
    print()

    for name, ocost in [("cash-flow", cash), ("user cost", user)]:
        hc = np.where(own, ocost, rent_flow)
        ratio = hc / inc
        agg = np.sum(w * hc) / np.sum(w * inc)
        print("--- owner housing valued at %s" % name)
        print("  ALL households, aggregate ratio : %.4f" % agg)
        print("  ALL households, share > 30%%     : %.2f %%" % (100 * wshare(ratio > 0.30, w)))
        print("  ALL households, share > 50%%     : %.2f %%" % (100 * wshare(ratio > 0.50, w)))
        m = ~own
        print("  renters only,   mean ratio      : %.4f  (paper targets 0.33)"
              % (np.sum(w[m] * np.clip(ratio, 0, 5)[m]) / np.sum(w[m])))
        print()

    # recommended targets
    hc = np.where(own, user, rent_flow)
    ratio = hc / inc
    print("RECOMMENDED TARGETS for the all-renter model")
    print("  aggregate housing cost / income : %.4f" % (np.sum(w * hc) / np.sum(w * inc)))
    print("  share with housing cost > 50%%   : %.2f %%" % (100 * wshare(ratio > 0.50, w)))
    print()
    print("  trim sensitivity of the mean-of-ratios (why we do not target it):")
    for t in (1, 2, 3, 5, 10):
        print("    trim at %2dx income : %.4f" % (t, np.sum(w * np.clip(ratio, 0, t)) / np.sum(w)))
    print()

    print("income distribution, all households:")
    srt = np.argsort(inc)
    cw = np.cumsum(w[srt]) / np.sum(w)
    for p in (10, 25, 50, 75, 90):
        print("  p%-2d : %12.0f" % (p, inc[srt][np.searchsorted(cw, p / 100)]))
    med = inc[srt][np.searchsorted(cw, 0.5)]
    print("  mean : %12.0f   (mean/median = %.3f)"
          % (np.sum(w * inc) / np.sum(w), (np.sum(w * inc) / np.sum(w)) / med))
    print()
    print("aggregate net worth / aggregate income : %.3f"
          % (np.sum(w * d.networth.values) / np.sum(w * inc)))
    print("  NB: not directly comparable to the paper's wealth/GDP target of 3.25 --")
    print("  the denominator there is GDP, not aggregate household income.")


if __name__ == "__main__":
    main()
