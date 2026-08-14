#!/usr/bin/env python3
"""
Build data/us_life_table.csv from whatever life table you managed to download.

The Fortran model wants exactly two columns, ages 26-85, one record per line:

    age,qx

where qx is the probability of dying within one year at that exact age, for the
TOTAL population. params.f90::load_life_table() reads it, maps age 26 to model
age 1, and ignores anything outside 26-85. A missing file is not fatal -- the
model warns and falls back to a smooth exponential hazard -- so this script is
the difference between "fitted to nothing" and an actual data source, which is
what Referee 3's M1b asks for.

Three input formats are handled, because three different sites are plausible
depending on which one is reachable:

  --hmd    Human Mortality Database, USA, "Life tables (period 1x1)", both
           sexes. Whitespace-delimited, a two-line header, columns
           Year Age mx qx ax lx dx Lx Tx ex. Already combined-sex, so nothing
           has to be averaged. This is the cleanest input.

  --ssa    SSA Actuarial Life Table (oact/STATS/table4c6.html), saved as HTML
           or copied to text. Male and female appear as separate column blocks
           on one row, so the two qx are averaged. That average is crude --
           it weights the sexes equally rather than by population -- and it is
           still far better than the placeholder. Pass --sex-weights to change
           it.

  --csv    Any two-column file that already has age and qx, in either order of
           rows, with or without a header.

Usage
-----
    python3 make_life_table.py --hmd USA_bltper_1x1.txt --year 2021
    python3 make_life_table.py --ssa table4c6.html
    python3 make_life_table.py --csv whatever.csv

Writes data/us_life_table.csv next to this script and prints what it did.
"""

import argparse
import csv
import os
import re
import sys

AGE_LO, AGE_HI = 26, 85
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_life_table.csv")


def from_hmd(path, year):
    """HMD period life table, 1x1, both sexes."""
    rows = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                yr = int(parts[0])
            except ValueError:
                continue  # header
            age_tok = parts[1].replace("+", "")
            try:
                age = int(age_tok)
                qx = float(parts[3])
            except ValueError:
                continue
            if year is not None and yr != year:
                continue
            if AGE_LO <= age <= AGE_HI:
                rows[age] = qx
    if year is None and rows:
        print("  note: no --year given, so the LAST year in the file was used")
    return rows


def from_ssa(path, w_male):
    """
    SSA table4c6: one row per age, male block then female block. Strip any HTML,
    then take the first numeric token as the age, the second as male qx and the
    (first token of the female block) as female qx. The table has 7 numeric
    columns per row: age, m_qx, m_lx, m_ex, f_qx, f_lx, f_ex.
    """
    text = open(path, encoding="utf-8", errors="replace").read()
    text = re.sub(r"<[^>]+>", " ", text)          # drop tags
    text = text.replace(",", "")                   # 100,000 -> 100000
    rows = {}
    for line in text.splitlines():
        toks = re.findall(r"-?\d+\.?\d*", line)
        if len(toks) < 7:
            continue
        try:
            age = int(float(toks[0]))
            m_qx = float(toks[1])
            f_qx = float(toks[4])
        except ValueError:
            continue
        if not (AGE_LO <= age <= AGE_HI):
            continue
        if not (0.0 <= m_qx < 1.0 and 0.0 <= f_qx < 1.0):
            continue
        rows[age] = w_male * m_qx + (1.0 - w_male) * f_qx
    return rows


def from_ssa_xlsx(path):
    """
    SSA table4c6 saved as .xlsx. Seven numeric columns per data row:

        age, m_qx, m_lx, m_ex, f_qx, f_lx, f_ex

    The lx columns are what make this the best of the SSA routes. Averaging
    male and female qx with equal weights is wrong -- by the mid-eighties the
    survivor populations differ by a wide margin, so the sexes do not contribute
    equally to deaths at that age. The correct both-sexes hazard is the ratio of
    total deaths to total survivors,

        q(x) = ( lM(x)*qM(x) + lF(x)*qF(x) ) / ( lM(x) + lF(x) ),

    which is what this does. Both sexes carry a radix of 100,000, so this
    assumes an equal sex ratio at birth; the true ratio is about 1.05 male per
    female, an error far smaller than the equal-weight one it replaces.
    """
    import openpyxl
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = {}
    for rec in ws.iter_rows(values_only=True):
        nums = [c for c in rec if isinstance(c, (int, float))]
        if len(nums) < 7:
            continue
        age, m_qx, m_lx, _m_ex, f_qx, f_lx = nums[0], nums[1], nums[2], nums[3], nums[4], nums[5]
        if age != int(age):
            continue
        age = int(age)
        if not (AGE_LO <= age <= AGE_HI):
            continue
        denom = m_lx + f_lx
        if denom <= 0:
            continue
        rows[age] = (m_lx * m_qx + f_lx * f_qx) / denom
    return rows


def from_csv(path):
    rows = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for rec in csv.reader(fh):
            if len(rec) < 2:
                continue
            try:
                age = int(float(rec[0]))
                qx = float(rec[1])
            except ValueError:
                continue  # header
            if AGE_LO <= age <= AGE_HI:
                rows[age] = qx
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--hmd", metavar="FILE")
    g.add_argument("--ssa", metavar="FILE")
    g.add_argument("--ssa-xlsx", metavar="FILE",
                   help="SSA table4c6 as .xlsx; combines the sexes by lx weight")
    g.add_argument("--csv", metavar="FILE")
    p.add_argument("--year", type=int, default=None,
                   help="HMD only: which calendar year to take")
    p.add_argument("--sex-weights", type=float, default=0.5, metavar="W_MALE",
                   help="SSA only: weight on male qx (default 0.5)")
    a = p.parse_args()

    if a.hmd:
        rows, src = from_hmd(a.hmd, a.year), f"HMD {a.hmd}"
    elif a.ssa:
        rows, src = from_ssa(a.ssa, a.sex_weights), f"SSA {a.ssa}"
    elif a.ssa_xlsx:
        rows, src = from_ssa_xlsx(a.ssa_xlsx), f"SSA xlsx {a.ssa_xlsx} (lx-weighted)"
    else:
        rows, src = from_csv(a.csv), f"CSV {a.csv}"

    if not rows:
        sys.exit(f"ERROR: no usable (age, qx) records found in {src}.\n"
                 f"       Expected ages {AGE_LO}-{AGE_HI}. Check the format.")

    missing = [j for j in range(AGE_LO, AGE_HI + 1) if j not in rows]
    bad = {j: q for j, q in rows.items() if not (0.0 <= q < 1.0)}
    if bad:
        sys.exit(f"ERROR: qx outside [0,1) at ages {sorted(bad)[:5]} -- "
                 f"is the column a RATE per 100,000 rather than a probability?")

    # qx must rise with age over this range; a fall means columns were misread
    seq = [rows[j] for j in sorted(rows)]
    drops = sum(1 for i in range(1, len(seq)) if seq[i] < seq[i - 1] * 0.9)
    if drops > 3:
        print(f"  WARNING: qx falls with age at {drops} points. That is not a "
              f"US life table shape -- check the column mapping.", file=sys.stderr)

    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["age", "qx"])
        for j in sorted(rows):
            w.writerow([j, f"{rows[j]:.8f}"])

    print(f"  wrote {OUT}")
    print(f"  source: {src}")
    print(f"  ages {min(rows)}-{max(rows)}, {len(rows)} records")
    print(f"  qx at 26: {rows.get(26, float('nan')):.6f}"
          f"   at 65: {rows.get(65, float('nan')):.6f}"
          f"   at 85: {rows.get(85, float('nan')):.6f}")
    if missing:
        print(f"  NOTE: {len(missing)} ages missing ({missing[:8]}...); the model "
              f"keeps its fallback hazard for those")


if __name__ == "__main__":
    main()
