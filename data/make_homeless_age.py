#!/usr/bin/env python3
"""
Build data/us_homeless_by_age.csv from the HUD PIT counts.

This is an UNTARGETED moment and a good one. The model runs 60 single ages and
produces an age profile of homelessness endogenously; nothing in the calibration
fits that profile, so comparing it is a genuine out of sample test of the
life cycle mechanism rather than a check that a fitted parameter did its job.

National, from the PIT file already in raw/. No separate download exists or is
needed: the by state workbook carries "Overall Homeless - Age X to Y" columns
and the Total row aggregates them.

Population denominators come from the CDC WONDER export in raw/, which reports
population by five year age group alongside deaths. Using one source for both
keeps the vintages aligned.

Bands are the PIT bands: 25 to 34, 35 to 44, 45 to 54, 55 to 64. Under 18 and
18 to 24 are outside the model's range and are reported but not used. There is
no 65 plus column in the PIT age breakdown, so the profile stops at 64.
"""
import argparse, csv, os, re, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_homeless_by_age.csv")
# The 65+ column is named "Over 64", not "65+" -- easy to miss and the reason
# the first version of this file stopped at 64.
BANDS = {"Age 25 to 34": (25, 34), "Age 35 to 44": (35, 44),
         "Age 45 to 54": (45, 54), "Age 55 to 64": (55, 64),
         "Over 64": (65, 84)}

def wonder_pop(path):
    """Population by five year group, deduplicated across cause rows."""
    pop = {}
    for r in csv.reader(open(path, encoding="utf-8", errors="replace"), delimiter="\t"):
        if len(r) < 7:
            continue
        m = re.match(r'"?(\d+)-(\d+)', r[1].strip())
        if not m:
            continue
        try:
            pop[(int(m.group(1)), int(m.group(2)))] = int(r[6])
        except ValueError:
            continue
    return pop

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pit", required=True, help="HUD PIT counts by state, .xlsb")
    p.add_argument("--wonder", required=True, help="CDC WONDER export, for population")
    p.add_argument("--year", default="2024")
    a = p.parse_args()

    from pyxlsb import open_workbook
    with open_workbook(a.pit) as wb:
        with wb.get_sheet(a.year) as sh:
            rows = [[c.v for c in r] for r in sh.rows()]
    hdr = [str(h) if h is not None else "" for h in rows[0]]
    tot = next((r for r in rows if r and str(r[0]).strip() == "Total"), None)
    if tot is None:
        sys.exit("ERROR: no Total row in the PIT sheet.")

    pop5 = wonder_pop(a.wonder)
    out = []
    for band, (lo, hi) in BANDS.items():
        i = next((k for k, h in enumerate(hdr) if h.strip() == f"Overall Homeless - {band}"), None)
        if i is None:
            sys.exit(f"ERROR: column 'Overall Homeless - {band}' not found.")
        pop = sum(v for (a0, a1), v in pop5.items() if a0 >= lo and a1 <= hi)
        if pop == 0:
            sys.exit(f"ERROR: no population for {band}. Age groups seen: {sorted(pop5)}")
        out.append((lo, hi, int(tot[i]), pop, tot[i] / pop))

    T = sum(o[2] for o in out)
    P = sum(o[3] for o in out)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age_lo", "age_hi", "homeless", "population", "rate", "share_of_homeless"])
        for lo, hi, c, pop, rate in out:
            w.writerow([lo, hi, c, pop, f"{rate:.8f}", f"{c/T:.6f}"])

    print(f"  wrote {OUT}   (PIT {a.year}, ages 25-84)")
    print(f"    {'band':9s}{'homeless':>10s}{'population':>13s}{'rate %':>9s}{'share %':>9s}")
    for lo, hi, c, pop, rate in out:
        print(f"    {str(lo)+'-'+str(hi):9s}{c:>10,d}{pop:>13,d}{100*rate:>9.4f}{100*c/T:>9.1f}")
    print(f"    {'TOTAL':9s}{T:>10,.0f}{P:>13,d}{100*T/P:>9.4f}{100.0:>9.1f}")

if __name__ == "__main__":
    main()
