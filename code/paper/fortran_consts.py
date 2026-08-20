"""
Read the quantitative model's data targets straight out of the Fortran.

WHY THIS EXISTS. Every target the model is calibrated against is declared once
in housing_first_or_treatment_first_SR_v1.f90 as a `*_data` constant. The paper
quotes those numbers in two places, the parameter tables and the prose, and for
most of this paper's life they were typed into both. Typed numbers drift: a
target changed in the Fortran and the table kept the old one for a round, and a
table and the text disagreed about the treatment take up rate for longer than
that. Nothing here is typed. The Fortran is the source and everything else reads
from it.

Constants written as arithmetic are evaluated rather than skipped, because three
of the targets are ratios and those are exactly the ones a reader cannot check
by eye: milby_recovery_ratio_data is 6.60/4.48, child_use_gap_data is
1/0.845 - 1, and drug_supply_curvature is 1 + 1/the supply elasticity.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..',
                                    'housing_first_or_treatment_first_SR_v1.f90'))

_DECL = re.compile(
    r'^\s*(?:real\(8\)|integer)\s*(?:,\s*parameter\s*)?::\s*'
    r'([a-z_0-9]+)\s*=\s*(.+?)\s*(?:!.*)?$', re.I | re.M)


def _num(expr, seen):
    """Evaluate a Fortran literal or a small arithmetic expression."""
    e = expr.strip().rstrip('&').strip()
    # THE DOT FORM MATTERS. Fortran writes 1.d0 as well as 1.0d0, and a pattern
    # anchored on a digit before the d silently skipped every one of them,
    # which lost vsl_data, child_use_gap_data and four others.
    e = re.sub(r'([\d.])[dD]([+-]?\d+)', r'\1e\2', e)   # 1.0d0 and 1.d0
    e = re.sub(r'(?<![\w.])10\.\*\*', '10**', e)
    for name, val in seen.items():                     # substitute known names
        e = re.sub(r'(?<![\w.])%s(?![\w])' % re.escape(name), repr(val), e)
    # THE EXPONENT LETTER IS NOT A NAME. Testing the whole string for letters
    # rejected every constant written in exponent form, because 6.60d0/4.48d0
    # becomes 6.60e0/4.48e0 and the e reads as an identifier. Strip the numeric
    # literals first and test what is left.
    probe = re.sub(r'\d+\.?\d*(?:[eE][+-]?\d+)?', '', e)
    if re.search(r'[A-Za-z_]', probe):
        return None
    try:
        return float(eval(e, {'__builtins__': {}}, {}))
    except Exception:
        return None


def constants(path=SRC):
    """{name: value} for every scalar constant the file declares."""
    txt = open(path, encoding='utf-8', errors='surrogateescape').read()
    # join Fortran continuation lines so a declaration split over two lines reads
    txt = re.sub(r'&\s*\n\s*', '', txt)
    out = {}
    for m in _DECL.finditer(txt):
        name, expr = m.group(1), m.group(2)
        v = _num(expr, out)
        if v is not None:
            out.setdefault(name, v)
    return out


def targets(path=SRC):
    """Only the calibration targets, the `*_data` constants."""
    return {k: v for k, v in constants(path).items() if k.endswith('_data')}


if __name__ == '__main__':
    t = targets()
    print(f'{len(t)} data targets read from the Fortran')
    for k in sorted(t):
        print(f'   {k:44s} {t[k]:.6g}')
