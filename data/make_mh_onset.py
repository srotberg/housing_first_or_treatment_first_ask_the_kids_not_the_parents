#!/usr/bin/env python3
"""
Build data/us_mh_onset_shape.csv: the age PROFILE of serious mental illness
onset.

The problem
-----------
mh_onset is a scalar, calibrated to hit 5.5% SMI prevalence. A constant onset
hazard against a constant recovery hazard drives prevalence toward a steady
state from below, so the model produces a profile that RISES with age. NSDUH
says it falls by a factor of eight:

    26-29  11.0%      45-49   5.6%
    30-34  10.3%      50-54   4.5%
    35-39   6.9%      55-59   3.0%
    40-44   6.0%      60-64   2.7%     65+  1.4%

So the model hits the average and gets the shape backwards. SMI feeds
employment, homelessness and mortality, so that misplaces the whole mental
health channel across the life cycle.

The fix, same as for the mortality multipliers
-----------------------------------------------
Take the SHAPE from data and leave the LEVEL calibrated, so the existing
identification (mh_onset -> SMI prevalence) is untouched.

Onset is backed out of the prevalence profile and the recovery hazard. For a two
state chain with onset lambda(a) and recovery mu,

    p(a+1) = p(a)*(1-mu) + (1-p(a))*lambda(a)
    lambda(a) = [ p(a+1) - p(a)*(1-mu) ] / (1 - p(a))

This is approximate in two ways worth stating. It ignores differential mortality,
which removes SMI households faster and so understates the onset needed to
sustain a given prevalence, increasingly at older ages. And it ignores
mh_onset_sud, which raises onset for households with SUD. Both affect the level
more than the shape, and the level is calibrated anyway.

Negative implied onset is clamped to zero: where prevalence falls faster than
recovery alone can explain, the residual is mortality and selection, not
negative incidence.
"""
import argparse, csv, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_mh_onset_shape.csv")
AGE_LO, AGE_HI = 26, 85
# NSDUH 2023 Table 6.4B, serious mental illness in the past year, total
PREV = [(27.5, 0.110), (32.0, 0.103), (37.0, 0.069), (42.0, 0.060),
        (47.0, 0.056), (52.0, 0.045), (57.0, 0.030), (62.0, 0.027), (72.0, 0.014)]


# Prevalence is fitted LOG-LINEARLY in age, not interpolated piecewise.
# Differencing a piecewise linear curve turns every kink into a spike: the first
# attempt produced an onset profile that was 1.00 at 26, 0.01 at 32, 0.35 at 38
# and exactly 0.00 at 56 and 68. Those zeros are artifacts of the interpolation,
# not incidence that vanishes and reappears. A single exponential through the
# NSDUH points gives a smooth, monotone profile and its slope is what the onset
# formula actually needs.
import math

def fit_loglinear():
    n = len(PREV)
    xs = [a for a, _ in PREV]
    ys = [math.log(p) for _, p in PREV]
    mx, my = sum(xs)/n, sum(ys)/n
    beta = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
    alpha = my - beta*mx
    ss_tot = sum((y-my)**2 for y in ys)
    ss_res = sum((y-(alpha+beta*x))**2 for x, y in zip(xs, ys))
    return alpha, beta, 1.0 - ss_res/ss_tot

ALPHA, BETA, R2 = fit_loglinear()

def interp(age):
    return math.exp(ALPHA + BETA*age)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recover", type=float, default=0.067, help="mh_recover")
    a = ap.parse_args()

    lam = {}
    for age in range(AGE_LO, AGE_HI + 1):
        p0, p1 = interp(age), interp(age + 1)
        lam[age] = max(0.0, (p1 - p0 * (1.0 - a.recover)) / max(1e-9, 1.0 - p0))
    peak = max(lam.values())
    if peak <= 0:
        raise SystemExit("ERROR: implied onset is zero everywhere; check --recover.")

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age", "shape_mh_onset", "implied_onset", "smi_prevalence"])
        for age in range(AGE_LO, AGE_HI + 1):
            w.writerow([age, f"{lam[age]/peak:.6f}", f"{lam[age]:.8f}",
                        f"{interp(age):.6f}"])

    print(f"  wrote {OUT}   (recovery hazard {a.recover})")
    print(f"  log-linear prevalence fit: {100*math.exp(ALPHA+BETA*26):.2f}% at 26, "
          f"decaying {100*(1-math.exp(BETA)):.2f}%/yr,  R2 = {R2:.3f}")
    print(f"    {'age':>4s}{'SMI prev':>10s}{'implied onset':>15s}{'shape':>8s}")
    for age in range(AGE_LO, AGE_HI + 1, 6):
        print(f"    {age:>4d}{100*interp(age):>9.2f}%{lam[age]:>15.5f}{lam[age]/peak:>8.3f}")


if __name__ == "__main__":
    main()
