"""
Expose EVERY Fortran constant to the prose as @@f_<name>@@.

WHY THIS EXISTS. sync_tables.py links 36 constants, one per row of Tables 5 and
6, because those are the rows it has to rewrite. But the quantitative model's
prose quotes far more than its tables state: targets, shares, elasticities and
ratios that are declared in the Fortran and then typed again into the text. A
survey of Section 4 onward found 86 typed decimals against 28 placeholders, and
among them were the participation rate of 0.0513 and the SUD rate of 0.0368,
which are the model's own calibration targets written out by hand.

A number typed into prose is a number that will be wrong after the next sweep,
and nothing notices. This writes every parsed declaration to
fortran_numbers.json under the name f_<constant>, so any sentence can read the
declaration instead of repeating it.

BOTH A RAW AND A PERCENT FORM are written, f_x and f_x_pc, because the Fortran
holds fractions and the prose usually wants percentages, and converting by hand
in the text is how "0.30 percent of market rent" came to describe a parameter
equal to 0.30 as a fraction.

Run:  python3 export_consts.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fortran_consts import constants

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'fortran_numbers.json')


def _fmt(x):
    """The declaration's own value, trimmed of trailing zeros."""
    if x == int(x):
        return str(int(x))
    s = f'{x:.6f}'.rstrip('0').rstrip('.')
    return s


def main():
    c = constants()
    out = {}
    for name, v in c.items():
        try:
            x = float(v)
        except (TypeError, ValueError):
            continue
        out[f'f_{name}'] = _fmt(x)
        out[f'f_{name}_pc'] = _fmt(100.0 * x)
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f'   wrote fortran_numbers.json, {len(c)} constants '
          f'({len(out)} placeholders including percent forms)')


if __name__ == '__main__':
    main()
