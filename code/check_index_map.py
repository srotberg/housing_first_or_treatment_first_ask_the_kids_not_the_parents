"""
Catch index tests that would break when mental illness is switched on.

WHY THIS EXISTS

The unemployment index folds employment, the SUD and mental illness together:

    index = 3*number_of_smi_states*d + 3*m + e,   e in 1..3, m,d in 0..1

with the SUD OUTERMOST. Two consequences, and this script enforces the second.

    SAFE FOREVER.  index >  threshold_addiction_index   means "has a SUD"
                   index <= threshold_addiction_index   means "is clean"
                   loops 1..threshold and threshold+1..grid_size
    Those stay correct at either grid size, because the SUD block is contiguous.

    WRONG THE MOMENT THE GRID GROWS.  Anything finer: index == threshold+1,
    index == grid_size, index == 1, index > threshold+1. At six states
    index == threshold+1 is "employed with a SUD"; at twelve it is "employed
    with a SUD and no mental illness", and the mentally ill are silently
    dropped from whatever the test was gating.

Those finer tests were rewritten through emp_of and sud_of. Two of them were
missed the first time, because they were written as index==(threshold+1) with
brackets the regex did not expect, and they gated the labour supply solve. The
compiler cannot catch that and neither can the run time verifier, which only
checks that the helpers agree with the thresholds, not that every site uses
them. So it is checked here.

Run:  python3 check_index_map.py
Exit code 1 if anything needs attention.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')

# the two coarse forms, which are correct at any grid size
SAFE = [
    re.compile(r'unemployment_index(?:_1)?\s*>\s*threshold_addiction_index\s*(?![+\d])'),
    re.compile(r'unemployment_index(?:_1)?\s*<=\s*threshold_addiction_index\s*(?![+\d])'),
]

# anything comparing the index to the threshold or to the top of the grid
SUSPECT = re.compile(
    r'[A-Za-z_0-9]+\s*(?:<=|>=|==|<|>|/=)\s*\(?\s*'
    r'(?:threshold_addiction_index|unemployment_grid_size)\s*(?:[+-]\s*\d+)?\s*\)?')

# the run time verifier is allowed to compare the two forms: that is its job
EXEMPT_ROUTINE = 'verify_index_map'


def scan(path=SRC):
    bad = []
    routine = '?'
    for n, line in enumerate(open(path, errors='replace'), 1):
        stripped = line.strip()
        if stripped.startswith('subroutine ') or stripped.startswith('integer function') \
                or stripped.startswith('real(8) function'):
            routine = stripped.split('(')[0].split()[-1]
        if stripped.startswith('!') or 'write' in line or 'parameter ::' in line:
            continue
        if routine == EXEMPT_ROUTINE:
            continue
        rest = line
        for safe in SAFE:
            rest = safe.sub('', rest)
        for m in SUSPECT.finditer(rest):
            # loop bounds are ranges, not tests, and are safe by contiguity
            if re.match(r'^\s*do\s', stripped):
                continue
            bad.append((n, routine, m.group(0).strip()))
    return bad


if __name__ == '__main__':
    bad = scan()
    if not bad:
        print('index map: every fine grained test goes through emp_of and sud_of')
        sys.exit(0)
    print(f'index map: {len(bad)} site(s) compare the index directly and will be')
    print('wrong once number_of_smi_states is 2. Rewrite them through emp_of and')
    print('sud_of, then re-run this.\n')
    for n, r, t in bad:
        print(f'  line {n:6d}  in {r:44s}  {t}')
    sys.exit(1)
