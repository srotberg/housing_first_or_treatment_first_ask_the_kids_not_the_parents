#!/usr/bin/env python3
"""
Build data/us_mortality_multipliers.csv: the SUD and homelessness mortality
multipliers, BY AGE.

Both were flat constants (kappa_phi_d = 6.9, kappa_phi_h = 1.6) and both are
strongly age varying in the data. They also have to be derived TOGETHER,
because the homelessness figure in the literature is measured on a population
that mostly also has SUD, so netting one out depends on the other.

SUD multiplier: shape from data, level from the literature
----------------------------------------------------------
CDC WONDER gives drug poisoning deaths by five year age group. Concentrating
them on the SUD prevalence gives the overdose hazard faced by a household with
SUD, and dividing by the all cause baseline gives the excess as a ratio:

    r(a) = q_overdose_given_SUD(a) / q_baseline(a)

That ratio is well measured and it falls by two orders of magnitude across the
age range, from about 6.3 at 30 to 0.03 at 82. What overdose does NOT capture is
the rest of SUD excess mortality, which runs through liver disease, endocarditis,
hepatitis, HIV, suicide and accidents; published all cause SMRs for opioid use
disorder are 6 to 10, of which overdose is roughly half. Rather than guess that
scale up factor, the LEVEL is anchored to the existing calibrated value at its
peak and only the SHAPE is taken from the data:

    kappa_phi_d(a) = 1 + (peak - 1) * r(a)/max(r)

This changes no level anyone previously defended, and fixes a profile that
implied a 6.9 fold SUD mortality penalty for an 80 year old.

Homelessness multiplier: net of the SUD composition, age by age
---------------------------------------------------------------
Baggett et al. (2013) give race adjusted all cause mortality rate ratios for
homeless adults of about 9.1 at 25-44, 4.5 at 45-64 and 1.1 at 65-84. Those are
TOTALS for a population of which a share s has SUD, so

    RR_total(a) = kappa_phi_h(a) * [ (1-s) + s*kappa_phi_d(a) ]

and kappa_phi_h falls out. Because kappa_phi_d now varies with age, so does the
correction: at 45-64 the SUD multiplier is much smaller than at 25-44, so more
of the observed ratio is genuine homelessness effect.

kappa_phi_h is floored at 1.0. At 65+ the arithmetic returns less than one,
which read literally says homelessness protects the old. That is survivor
selection, not causation, and the model cannot represent selection on
unobserved frailty.
"""
import argparse, csv, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "us_mortality_multipliers.csv")
AGE_LO, AGE_HI = 26, 85
OD_ROWS = {"Drug poisonings (overdose) Unintentional (X40-X44)",
           "Drug poisonings (overdose) Suicide (X60-X64)",
           "Drug poisonings (overdose) Homicide (X85)",
           "Drug poisonings (overdose) Undetermined (Y10-Y14)"}
# Baggett et al. 2013, all cause RR, homeless vs general population.
# Interpolated LINEARLY between band midpoints rather than applied as a step
# function. Their bands are twenty years wide, and stepping RR_total while
# kappa_phi_d varies smoothly puts spurious jumps in kappa_phi_h at 45 and 65 --
# it dipped to 2.6 at 46 and climbed back to 3.3 at 56, which is an artifact of
# the band edges, not a feature of the data. Kinks in a mortality hazard become
# kinks in the value function and in the housing choice, so they are worth
# avoiding.
BAGGETT = [(25, 44, 9.1), (45, 64, 4.5), (65, 84, 1.1)]
BAGGETT_MID = [((lo + hi) / 2.0, v) for lo, hi, v in BAGGETT]


def rr_at(age):
    """Piecewise linear in age through the band midpoints, flat beyond them."""
    if age <= BAGGETT_MID[0][0]:
        return BAGGETT_MID[0][1]
    if age >= BAGGETT_MID[-1][0]:
        return BAGGETT_MID[-1][1]
    for (a0, v0), (a1, v1) in zip(BAGGETT_MID, BAGGETT_MID[1:]):
        if a0 <= age <= a1:
            return v0 + (v1 - v0) * (age - a0) / (a1 - a0)
    return BAGGETT_MID[-1][1]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--overdose", required=True)
    p.add_argument("--life-table", required=True)
    p.add_argument("--sud-prevalence", type=float, default=0.0368,
                   help="moderate/severe drug UD, ages 26+ (NSDUH)")
    p.add_argument("--sud-share-homeless", type=float, default=0.217)
    p.add_argument("--peak-sud-mult", type=float, default=6.9,
                   help="level anchor: the previous flat kappa_phi_d")
    a = p.parse_args()

    lt = {int(r[0]): float(r[1])
          for r in list(csv.reader(open(a.life_table)))[1:] if r and r[0].isdigit()}

    od = {}
    for r in csv.DictReader(open(a.overdose)):
        if r["category"] not in OD_ROWS:
            continue
        lo, hi = int(r["age_lo"]), int(r["age_hi"])
        od[(lo, hi)] = od.get((lo, hi), 0.0) + float(r["q_annual"])
    if not od:
        sys.exit("ERROR: no drug-poisoning rows found in the overdose file.")

    # excess ratio r(a), by single age, from the band containing it
    def band(age):
        return next(((lo, hi) for (lo, hi) in od if lo <= age <= hi), None)

    r = {}
    for age in range(AGE_LO, AGE_HI + 1):
        b = band(age)
        if b is None or age not in lt or lt[age] <= 0:
            continue
        r[age] = (od[b] / a.sud_prevalence) / lt[age]
    if not r:
        sys.exit("ERROR: no overlap between the life table and the overdose bands.")
    rmax = max(r.values())

    s = a.sud_share_homeless
    rows = []
    for age in range(AGE_LO, AGE_HI + 1):
        kd = 1.0 + (a.peak_sud_mult - 1.0) * (r.get(age, 0.0) / rmax)
        rr = rr_at(age)
        kh = max(1.0, rr / ((1 - s) + s * kd))
        rows.append((age, kd, kh, r.get(age, float("nan"))))

    # Emit the SHAPE and the homelessness RR, not just the levels. kappa_phi_d
    # is still the second stage's instrument for the drug-price elasticity of
    # participation, so its LEVEL has to stay free; only its profile is data.
    # The model rebuilds both multipliers from these two columns whenever the
    # level moves:
    #     kappa_phi_d(a) = 1 + (level - 1) * shape(a)
    #     kappa_phi_h(a) = max(1, rr_homeless(a) / [(1-s) + s*kappa_phi_d(a)])
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age", "shape_sud", "rr_homeless", "kappa_phi_d_at_peak_level",
                    "kappa_phi_h_at_peak_level", "overdose_excess_ratio"])
        for age, kd, kh, rr in rows:
            w.writerow([age, f"{rr/rmax:.6f}", f"{rr_at(age):.6f}",
                        f"{kd:.6f}", f"{kh:.6f}", f"{rr:.6f}"])

    print(f"  wrote {OUT}   (shape + RR; the model rescales to the calibrated level)")
    print(f"  SUD prevalence {100*a.sud_prevalence:.2f}%, "
          f"SUD share of homeless {100*s:.1f}%, peak SUD multiplier {a.peak_sud_mult}")
    print(f"    {'age':>4s}{'kappa_phi_d':>13s}{'kappa_phi_h':>13s}")
    for age, kd, kh, _ in rows:
        if age % 10 == 6 or age == AGE_HI:
            print(f"    {age:>4d}{kd:>13.3f}{kh:>13.3f}")


if __name__ == "__main__":
    main()
