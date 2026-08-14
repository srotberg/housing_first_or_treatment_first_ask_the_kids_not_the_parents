"""
nsduh_gradients.py -- income and age gradients of drug use and SUD, NSDUH 2024.

These are the UNTARGETED moments that test the paper's central claim, and one of
them exposes a definitional inconsistency in the current draft.

THE INCONSISTENCY
-----------------
The paper targets drug-use PARTICIPATION at 4% of the population, built from
past-year illicit use. It then compares the model's user income ratio (41%) to
"roughly 74 percent in the NSDUH data" -- but that 74% is computed over people
with a use DISORDER, not over people who use. Reproduced exactly here: any-UD,
ages 18+, gives 0.740.

Those are different populations, and they have very different income gradients.

THE SUBSTANTIVE FINDING
-----------------------
Ages 26+, matching the model's range:

    group                    prevalence   mean income / average
    illicit use (no mj)         5.13 %           0.951
    any use disorder            8.90 %           0.761
    moderate/severe UD          3.68 %           0.687

Drug USE is barely related to income -- users earn 95% of the average. It is
the DISORDER that concentrates at the bottom, at 69%.

By income band, the contrast is sharper still:

    band        illicit use %   moderate/severe UD %
    $5,000          6.86               6.63
    $90,000         4.70               1.40

Use falls by a factor of 1.5 across the income distribution and not
monotonically. Moderate/severe UD falls by a factor of 4.7.

WHY THIS MATTERS FOR THE MODEL
------------------------------
The paper's headline is that drug use concentrates among the low-income and
that mortality risk generates this. The data support a sharper and more
demanding version: INITIATION is roughly income-neutral, and it is PROGRESSION
to disorder that is concentrated. A model with forward-looking initiation and
differential progression should reproduce exactly that pattern -- flat use
gradient, steep SUD gradient -- and it is a much stronger test than matching a
single pooled ratio.

It also means the model should NOT be calibrated to make drug users poor. It
should make users near-average and those with SUD poor.

Run:  python3 nsduh_gradients.py
"""
import numpy as np
import pandas as pd

INCOME_MID = {1: 5000, 2: 15000, 3: 25000, 4: 35000,
              5: 45000, 6: 62500, 7: 90000}
ILLICIT = ["cocydays", "herydays", "hallndayyr", "inhndayyr2", "methndayyr"]
AGE_LABEL = {7: "26-29", 8: "30-34", 9: "35-49", 10: "50-64", 11: "65+"}


def used_any(d, cols):
    """Frequency codes 1-5 mean some use in the past year; 6 means none."""
    u = np.zeros(len(d), dtype=bool)
    for c in cols:
        v = pd.to_numeric(d[c], errors="coerce").values
        u |= np.isin(v, [1, 2, 3, 4, 5])
    return u


def report(age_min, label):
    df = pd.read_stata("NSDUH_2024.dta")
    d = df[df.age3 >= age_min].copy()
    w = d.analwt2_c.values
    inc = d.irpinc3.map(INCOME_MID).values.astype(float)
    ok = ~np.isnan(inc)
    sv = pd.to_numeric(d.svyrdudany, errors="coerce").values

    use = used_any(d, ILLICIT)
    ud_any = np.isin(sv, [1, 2, 3])
    ud_ms = np.isin(sv, [2, 3])

    def rate(mask, sub=None):
        if sub is None:
            return 100 * np.sum(w[mask]) / np.sum(w)
        return 100 * np.sum(w[mask & sub]) / np.sum(w[sub])

    def winc(mask):
        m = mask & ok
        return np.sum(w[m] * inc[m]) / np.sum(w[m])

    base = winc(ok)
    print("=" * 62)
    print(label)
    print("=" * 62)
    print("  group                   prevalence   mean income / average")
    for nm, m in [("illicit use (no mj)", use), ("any use disorder", ud_any),
                  ("moderate/severe UD", ud_ms)]:
        print("  %-22s %7.2f %%          %6.3f" % (nm, rate(m), winc(m) / base))
    print()
    print("  income band    illicit use %   mod/severe UD %   pop share %")
    for k in sorted(INCOME_MID):
        sub = (d.irpinc3 == k).values
        print("   $%6s        %8.2f        %8.2f       %8.2f"
              % ("{:,}".format(INCOME_MID[k]), rate(use, sub),
                 rate(ud_ms, sub), 100 * np.sum(w[sub]) / np.sum(w)))
    print()
    if age_min >= 7:
        print("  age band       illicit use %   mod/severe UD %   pop share %")
        for k in sorted(AGE_LABEL):
            sub = (d.age3 == k).values
            print("   %-8s      %8.2f        %8.2f       %8.2f"
                  % (AGE_LABEL[k], rate(use, sub), rate(ud_ms, sub),
                     100 * np.sum(w[sub]) / np.sum(w)))
    print()


if __name__ == "__main__":
    report(4, "ages 18+  -- the paper's code; reproduces its 0.740 figure")
    report(7, "ages 26+  -- the model's range; use these")
