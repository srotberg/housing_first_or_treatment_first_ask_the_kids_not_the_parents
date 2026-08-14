#!/usr/bin/env python3
"""
Build data/us_overdose_mortality.csv from a CDC WONDER mortality export.

Why
---
The model's SUD mortality channel is the paper's central mechanism, and it is
currently INFERRED: aleph is calibrated to hit a $7.5m VSL and the excess
hazard falls out. Measuring it makes the mechanism an input. That is a
materially stronger answer to Referee 1's rival hypothesis -- that the
SUD-to-employment channel does the work -- than a calibrated parameter is.

The query to run
----------------
CDC WONDER, Provisional Mortality Statistics:
  https://wonder.cdc.gov/mcd.html

  Group by:  Five-Year Age Groups
  AND        MCD - Drug/Alcohol Induced Causes      <-- NOT the 113 Cause List
  Export as tab-delimited.

The 113 Cause List is the wrong grouping and this script says so if it sees
one. Its nearest category, "Accidental poisoning and exposure to noxious
substances (X40-X49)", is UNINTENTIONAL poisoning only: it misses drug
poisonings coded as suicide (X60-X64), homicide (X85) and undetermined intent
(Y10-Y14), together roughly 8-12% of overdose deaths, while also sweeping in
alcohol (X45) and non-drug poisonings (X46-X49). The Drug/Alcohol Induced
grouping separates all of these cleanly and additionally reports "all other
drug-induced causes", which is part of the non-overdose excess mortality that
overdose figures alone understate.

Output
------
    age_lo,age_hi,deaths,population,rate_per_100k,q_annual,category

one row per age group per retained category.
"""

import argparse
import csv
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "us_overdose_mortality.csv")

# categories worth keeping, in the Drug/Alcohol Induced grouping
KEEP = re.compile(r'drug poisoning|alcohol poisoning|drug.induced|alcohol.induced', re.I)
# "All other drug-induced causes" (D9) is NOT usable as non-overdose SUD
# mortality. CDC's drug-induced list carries a long tail of THERAPEUTIC adverse
# effects -- drug-induced anaemia, thyroiditis, polyneuropathy, osteoporosis --
# which have nothing to do with substance use disorder and which dominate at
# older ages: D9 runs 600 per 100,000 at 80-84 against 6 for overdose. At prime
# ages it is largely F11-F19, mental and behavioural disorders due to
# psychoactive substance use, and there it IS informative. Flagged, never summed
# into the overdose total.
CONTAMINATED = re.compile(r'All other drug.induced', re.I)
# the 113-list fallback, flagged loudly
FALLBACK = re.compile(r'Accidental poisoning and exposure to noxious', re.I)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wonder", required=True, metavar="FILE",
                   help="tab-delimited CDC WONDER export")
    a = p.parse_args()

    rows = list(csv.reader(open(a.wonder, encoding='utf-8', errors='replace'),
                           delimiter='\t'))
    if not rows:
        sys.exit("ERROR: empty file")
    hdr = [h.strip().strip('"') for h in rows[0]]

    def col(pat):
        for i, h in enumerate(hdr):
            if re.search(pat, h, re.I):
                return i
        return None

    i_age = col(r'Five-Year Age Groups$')
    i_cause = col(r'Drug/Alcohol Induced') or col(r'113 Cause List$')
    i_d = col(r'^Deaths$')
    i_p = col(r'^Population$')
    if None in (i_age, i_cause, i_d, i_p):
        sys.exit(f"ERROR: could not find the needed columns.\n  saw: {hdr}")

    is_fallback = '113' in hdr[i_cause]
    if is_fallback:
        print("  WARNING: this export is grouped by the ICD-10 113 Cause List.\n"
              "           Its poisoning category is X40-X49, UNINTENTIONAL only:\n"
              "           it misses drug poisonings coded as suicide (X60-X64),\n"
              "           homicide (X85) and undetermined intent (Y10-Y14), and it\n"
              "           includes alcohol (X45) and non-drug poisonings (X46-X49).\n"
              "           Re-run grouped by 'MCD - Drug/Alcohol Induced Causes'.",
              file=sys.stderr)

    out, seen = [], set()
    for r in rows[1:]:
        if len(r) <= max(i_age, i_cause, i_d, i_p):
            continue
        age = r[i_age].strip().strip('"')
        cause = r[i_cause].strip().strip('"')
        if not age or not cause:
            continue
        m = re.match(r'(\d+)-(\d+)', age)
        if not m:
            continue
        if is_fallback:
            if not FALLBACK.search(cause):
                continue
        elif not KEEP.search(cause):
            continue
        try:
            deaths = int(r[i_d]); pop = int(r[i_p])
        except ValueError:
            continue
        if pop <= 0:
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        key = (lo, cause)
        if key in seen:
            continue
        seen.add(key)
        out.append((lo, hi, deaths, pop, 1e5 * deaths / pop, deaths / pop, cause))

    if not out:
        sys.exit("ERROR: no usable rows. Check the grouping variables.")

    out.sort()
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age_lo", "age_hi", "deaths", "population",
                    "rate_per_100k", "q_annual", "category"])
        for lo, hi, d, pop, rate, q, c in out:
            w.writerow([lo, hi, d, pop, f"{rate:.4f}", f"{q:.8f}", c])

    print(f"  wrote {OUT}")
    print(f"  {len(out)} rows, {len({c for *_, c in out})} categories")
    if any(CONTAMINATED.search(c) for *_, c in out):
        print("  NOTE: 'All other drug-induced causes' is retained but must NOT be\n"
              "        read as non-overdose SUD mortality -- it is dominated by\n"
              "        therapeutic adverse effects at older ages. Overdose is the\n"
              "        sum of the four 'Drug poisonings' rows only.", file=sys.stderr)
    for c in sorted({c for *_, c in out}):
        sub = [(lo, rate) for lo, hi, d, pop, rate, q, cc in out if cc == c]
        pk = max(sub, key=lambda x: x[1])
        print(f"    {c[:58]:58s} peak {pk[1]:6.1f}/100k at {pk[0]}")


if __name__ == "__main__":
    main()
