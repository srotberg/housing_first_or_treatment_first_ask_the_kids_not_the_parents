#!/usr/bin/env python3
"""
Build data/us_wealth_shares.csv from the Federal Reserve Distributional
Financial Accounts.

Why
---
`wealth/GDP = 3` is a single aggregate, and beta is bracketed to hit it. An
aggregate cannot discipline the BOTTOM of the wealth distribution, which is
precisely where this model's homelessness margin lives: if the model's poorest
half holds far more than its data counterpart, destitution is not a real state
and the homelessness decision is being made by households that are not actually
poor. The bottom-50% share is the moment that closes that hole. It sits
alongside the aggregate, it does not replace it.

Source
------
  https://www.federalreserve.gov/releases/z1/dataviz/dfa/distribute/table/
  "Net worth levels", exported as CSV.

The DFA is the SCF interpolated to quarterly frequency and reconciled to the
Financial Accounts, so this IS the SCF -- not an alternative to it.

Levels are $ millions. Categories are TopPt1, RemainingTop1, Next9, Next40,
Bottom50, which partition the population, so shares are computed against their
own sum rather than an external total.
"""
import argparse, collections, csv, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_wealth_shares.csv")
CATS = ["Bottom50", "Next40", "Next9", "RemainingTop1", "TopPt1"]

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dfa", required=True, metavar="FILE")
    p.add_argument("--from-year", type=int, default=2015)
    p.add_argument("--to-year", type=int, default=2026)
    a = p.parse_args()

    rows = list(csv.DictReader(open(a.dfa, encoding="utf-8", errors="replace")))
    if not rows or "Net worth" not in rows[0]:
        sys.exit("ERROR: expected a 'Net worth' column. Is this the levels export?")

    by = collections.defaultdict(dict)
    for r in rows:
        try:
            by[r["Date"]][r["Category"]] = float(r["Net worth"])
        except (ValueError, KeyError):
            continue

    dates = [d for d in by if a.from_year <= int(d[:4]) <= a.to_year
             and set(CATS) <= set(by[d])]
    if not dates:
        sys.exit(f"ERROR: no complete quarters in {a.from_year}-{a.to_year}.")

    share = {c: sum(by[d][c] / sum(by[d].values()) for d in dates) / len(dates)
             for c in CATS}
    # partition check: the five groups must exhaust the population
    if abs(sum(share.values()) - 1.0) > 1e-9:
        sys.exit(f"ERROR: shares sum to {sum(share.values()):.6f}, not 1.")

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "net_worth_share", "window", "n_quarters"])
        win = f"{a.from_year}-{a.to_year}"
        for c in CATS:
            w.writerow([c, f"{share[c]:.6f}", win, len(dates)])

    print(f"  wrote {OUT}")
    print(f"  {len(dates)} quarters, {a.from_year}-{a.to_year}")
    for c in CATS:
        print(f"    {c:15s} {100*share[c]:6.2f}%")

if __name__ == "__main__":
    main()
