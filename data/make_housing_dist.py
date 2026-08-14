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
    Pull the bedroom counts out of a data.census.gov xlsx export.

    B25042 is NESTED: a Total row, then an "Owner occupied:" header followed by
    its six bedroom rows, then "Renter occupied:" followed by its six. The
    bedroom labels REPEAT across the two blocks, so a flat label->value dict
    silently keeps only the renter numbers. Track which tenure block we are in
    and accumulate separately.

    B25041 is flat -- one block, no tenure header -- and falls out of the same
    loop with everything landing in 'all'.
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
    blocks = {"owner": {}, "renter": {}, "all": {}}
    total = None
    cur = "all"

    for r in ws.iter_rows(values_only=True):
        if not r or r[0] is None:
            continue
        label = str(r[0]).strip().rstrip(":").lower()
        est = next((parse_num(c) for c in r[1:] if parse_num(c) is not None), None)

        if label.startswith("owner occupied"):
            cur = "owner"; continue
        if label.startswith("renter occupied"):
            cur = "renter"; continue
        if label == "total":
            total = est; continue
        if est is None:
            continue
        for cat in CATS:
            if label == cat:
                blocks[cur][cat] = est

    return table_id, universe, blocks, total


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--xlsx", required=True, metavar="FILE")
    p.add_argument("--bins", default="0112", choices=sorted(BINS),
                   help="0112 = {0,1}{2}{3+} (default); 0113 = {0,1}{2,3}{4+}")
    p.add_argument("--tenure", default="all", choices=["all", "owner", "renter"],
                   help="which households. 'all' is the model-consistent choice: "
                        "there is no homeownership in the model, so every housed "
                        "household maps to an occupied unit regardless of tenure.")
    a = p.parse_args()

    table_id, universe, blocks, total_row = read_acs(a.xlsx)

    if "B25041" in table_id:
        print(f"  WARNING: {table_id} has universe '{universe}', which includes "
              f"VACANT units.\n"
              f"           About 10% of the stock, skewed small and rental, so "
              f"this overstates\n"
              f"           the small end. B25042 (occupied units) is the right "
              f"table.", file=sys.stderr)

    if a.tenure == "all":
        counts = [blocks["owner"].get(c, 0.0) + blocks["renter"].get(c, 0.0)
                  + blocks["all"].get(c, 0.0) for c in CATS]
    else:
        counts = [blocks[a.tenure].get(c, 0.0) for c in CATS]

    if sum(counts) <= 0:
        sys.exit(f"ERROR: no '{a.tenure}' bedroom rows found in {a.xlsx}.\n"
                 f"       Blocks seen: "
                 f"{ {k: len(v) for k, v in blocks.items()} }")

    total = sum(counts)
    # cross-check against the table's own Total row when we took everything
    if a.tenure == "all" and total_row and abs(total - total_row) > 0.005 * total_row:
        sys.exit(f"ERROR: the bedroom rows sum to {total:,.0f} but the table's "
                 f"Total row says {total_row:,.0f}. Nesting misread?")

    edges = BINS[a.bins]
    shares = [sum(counts[lo:hi]) / total for lo, hi in edges]

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["size", "share", "source", "universe", "tenure"])
        for k, (name, sh) in enumerate(zip(["small", "medium", "large"], shares), 1):
            w.writerow([k, f"{sh:.6f}", table_id, universe, a.tenure])

    print(f"  wrote {OUT}")
    print(f"  table {table_id}, universe: {universe}, tenure: {a.tenure}")
    print(f"  households: {total:,.0f}"
          + (f"   (Total row: {total_row:,.0f})" if total_row else ""))
    for cat, c in zip(CATS, counts):
        print(f"    {cat:20s} {c:14,.0f}  {100*c/total:6.2f}%")
    print(f"  collapsed with --bins {a.bins}:")
    for name, sh in zip(["small", "medium", "large"], shares):
        print(f"    {name:8s} {100*sh:6.2f}%")


if __name__ == "__main__":
    main()
