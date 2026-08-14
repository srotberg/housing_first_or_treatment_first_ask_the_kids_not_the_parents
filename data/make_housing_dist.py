#!/usr/bin/env python3
"""
Build data/us_housing_dist.csv -- the distribution of HOUSEHOLDS across unit
sizes -- from an ACS bedrooms table.

Why this exists
---------------
The housing grid's geometric spread, varsigma (h_spread in params.f90), is
currently identified from the share of households spending more than 30% of
income on housing. That is identification from a budget CONSEQUENCE of the
grid rather than from the grid itself, and it makes varsigma absorb anything
else that moves the housing-cost distribution. Targeting the size distribution
directly is cleaner.

Which ACS table
---------------
Use B25042, "Tenure by Bedrooms", universe OCCUPIED HOUSING UNITS. Its total
column is all households by bedrooms, which is the right universe: the model
has no homeownership, every housed household pays p_rent*h, so the model's
housed population maps to all occupied units rather than to renters alone.

Do NOT use B25041. Its universe is "Housing units", which includes VACANT
units -- about 10% of the stock, skewed small and rental -- so it overstates
the small end. The script accepts it with a warning so an interim number is
possible, but it is the wrong universe.

  B25042: https://data.census.gov/table/ACSDT1Y2023.B25042
  API:    https://api.census.gov/data/2023/acs/acs1?get=group(B25042)&for=us:*

Mapping to the model
--------------------
The model has NH = 4 housing states: state 1 is homelessness, states 2-4 are
three housed sizes. Six bedroom categories collapse to three by --bins:

  small   : no bedroom + 1 bedroom
  medium  : 2 bedrooms
  large   : 3, 4, 5+ bedrooms

That is the default. It is not the only defensible cut -- {0-1}, {2-3}, {4+}
is the obvious alternative and is available as --bins 0113 -- and the choice
matters, so it is a flag rather than a constant buried in the code.

Usage
-----
    python3 make_housing_dist.py --xlsx ACSDT1Y2023.B25042.xlsx
    python3 make_housing_dist.py --xlsx B25041.xlsx --bins 0113
"""

import argparse
import csv
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_housing_dist.csv")

# the six ACS bedroom categories, in order
CATS = ["no bedroom", "1 bedroom", "2 bedrooms", "3 bedrooms", "4 bedrooms",
        "5 or more bedrooms"]

BINS = {
    "0112": [(0, 2), (2, 3), (3, 6)],   # {0,1} {2} {3,4,5+}   -- default
    "0113": [(0, 2), (2, 4), (4, 6)],   # {0,1} {2,3} {4,5+}
}


def parse_num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = re.sub(r"[^\d.\-]", "", str(x))
    try:
        return float(s)
    except ValueError:
        return None


def read_acs(path):
    """
    Pull (label, estimate) pairs out of a data.census.gov xlsx export. The
    export puts the table in a 'Data' sheet with a Label column and an Estimate
    column; the table id and universe live in an 'Information' sheet.
    """
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)

    table_id, universe = "?", "?"
    if "Information" in wb.sheetnames:
        for r in wb["Information"].iter_rows(values_only=True):
            cells = [str(c) for c in r if c is not None]
            if len(cells) >= 2 and cells[0].startswith("TABLE ID"):
                table_id = cells[1]
            if len(cells) >= 2 and cells[0].startswith("UNIVERSE"):
                universe = cells[1]

    ws = wb["Data"] if "Data" in wb.sheetnames else wb.worksheets[0]
    rows = []
    for r in ws.iter_rows(values_only=True):
        if not r or r[0] is None:
            continue
        label = str(r[0]).strip().strip(":").lower()
        # the estimate is the first numeric-looking cell after the label
        est = next((parse_num(c) for c in r[1:] if parse_num(c) is not None), None)
        if est is not None:
            rows.append((label, est))
    return table_id, universe, rows


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--xlsx", required=True, metavar="FILE")
    p.add_argument("--bins", default="0112", choices=sorted(BINS),
                   help="0112 = {0,1}{2}{3+} (default); 0113 = {0,1}{2,3}{4+}")
    a = p.parse_args()

    table_id, universe, rows = read_acs(a.xlsx)

    if "B25041" in table_id:
        print(f"  WARNING: {table_id} has universe '{universe}', which includes "
              f"VACANT units.\n"
              f"           About 10% of the stock, skewed small and rental, so "
              f"this overstates\n"
              f"           the small end. B25042 (occupied units) is the right "
              f"table.", file=sys.stderr)

    # match the six categories against the label column
    counts = []
    for cat in CATS:
        hit = next((v for lab, v in rows if lab.startswith(cat.split()[0])
                    and cat.split()[0] != "5" or lab.startswith("5")), None)
        # explicit match is safer than the prefix trick above
        hit = next((v for lab, v in rows if lab == cat), hit)
        if hit is None:
            sys.exit(f"ERROR: could not find the '{cat}' row in {a.xlsx}.\n"
                     f"       Labels seen: {[l for l,_ in rows][:10]}")
        counts.append(hit)

    total = next((v for lab, v in rows if lab == "total"), sum(counts))
    if abs(sum(counts) - total) > 0.01 * total:
        sys.exit(f"ERROR: the six categories sum to {sum(counts):,.0f} but the "
                 f"total row says {total:,.0f}. Wrong columns?")

    edges = BINS[a.bins]
    shares = [sum(counts[lo:hi]) / total for lo, hi in edges]

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["size", "share", "source", "universe"])
        for k, (name, sh) in enumerate(zip(["small", "medium", "large"], shares), 1):
            w.writerow([k, f"{sh:.6f}", table_id, universe])

    print(f"  wrote {OUT}")
    print(f"  table {table_id}, universe: {universe}")
    print(f"  total households: {total:,.0f}")
    for cat, c in zip(CATS, counts):
        print(f"    {cat:20s} {c:14,.0f}  {100*c/total:6.2f}%")
    print(f"  collapsed with --bins {a.bins}:")
    for name, sh in zip(["small", "medium", "large"], shares):
        print(f"    {name:8s} {100*sh:6.2f}%")


if __name__ == "__main__":
    main()
