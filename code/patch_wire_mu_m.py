"""Wire mu_m into the eleven call sites that silently drop it.

WHAT IS BROKEN. mu_m is the SUD recovery multiplier for a household with
serious mental illness (SMI), applied in recovery_with_smi and reached from
addiction_transition through its OPTIONAL eighth argument smi_1. The
declaration says what that costs:

    ! OPTIONAL so that the twelve existing call sites stay valid while
    ! they are wired one at a time. Absent means no SMI, which is what
    ! the model was before, so leaving a site unwired is a silent
    ! omission rather than a compile error.

Four of fifteen call sites supply it and all four are in govt_revenues_calc,
the government revenue accounting. The eleven that do not are in
renter_to_renter_problem, internal_computations and
converge_to_stationary_equilibrium -- the household's value function and the
stationary distribution -- so the economy never sees mu_m and no value of it
has ever moved an equilibrium.

MEASURED, 23 September, before this patch: a frozen point identical to the
sweep's b_smi_multiple = 1.0 point except mu_m compiled at 0.10 rather than
1.0 reproduced every cell of the drug-state table to four decimals and moved
r_smi from 1.7792 to 1.7790, which is the no-op threshold this project uses.

WHY smi_of(unemployment_index) IS THE RIGHT EXPRESSION. mu_m multiplies the
recovery hazard of a household that carries SMI NOW, so the argument is the
CURRENT state. Every one of the eleven sites is enclosed by a
`do unemployment_index=` loop -- at 25265 for the seven in the value function,
and at 32597, 33103 and 33974 for the four in the distribution -- and that
variable is safe under OpenMP: the loop over it is SERIAL and the
`!$omp parallel do` inside runs over the financial index with
unemployment_index correctly in the shared clause. Ten of the eleven also sit
inside a `future_unemployment_index` loop, which is the inner one and the
WRONG variable. The four already-wired sites use smi_of(unemployment_index)
too, so this makes all fifteen consistent.

WHAT IT INVALIDATES. Every solved point, the benchmark of record and the
transition, because the recovery hazard now depends on SMI wherever mu_m is
away from one. At mu_m = 1 exactly it is a no-op by construction, which is the
control this patch is meant to be run under first.

Usage:  python3 code/patch_wire_mu_m.py [--check]

--check reports what it would do and writes nothing.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')

ADDED = 'smi_of(unemployment_index)'


def close_paren(text, start):
    """Index of the ) closing the call whose ( ends at `start`, and its arg count."""
    i, depth, args = start, 1, 1
    while i < len(text):
        c = text[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i, args
        elif c == ',' and depth == 1:
            args += 1
        i += 1
    raise RuntimeError('unbalanced parentheses after offset %d' % start)


def main(check_only):
    src = open(SRC).read()

    inserts, already, skipped = [], 0, 0
    for m in re.finditer(r'addiction_transition\(', src):
        line_start = src.rfind('\n', 0, m.start()) + 1
        head = src[line_start:m.start()]
        # A COMMENT MENTIONING THE NAME IS NOT A CALL SITE, and the first
        # attempt at this tripped over the one at line 238.
        if head.lstrip().startswith('!') or head.rstrip().endswith('function'):
            skipped += 1
            continue
        end, args = close_paren(src, m.end())
        if args >= 8:
            already += 1
            continue
        if args != 7:
            skipped += 1
            continue
        seg_start = src.rfind('\n', 0, end) + 1
        seg = src[seg_start:end]
        indent = len(seg) - len(seg.lstrip())
        pad = ' ' * max(indent, 32)
        inserts.append((end, ',&\n' + pad + ADDED))

    if already != 4:
        sys.exit('REFUSING: expected 4 already-wired call sites, found %d. '
                 'The source is not the one this patch was written against.'
                 % already)
    if len(inserts) != 11:
        sys.exit('REFUSING: expected 11 unwired call sites, found %d.'
                 % len(inserts))

    print('call sites already wired : %d' % already)
    print('call sites to wire       : %d' % len(inserts))
    print('comments and declaration : %d' % skipped)

    if check_only:
        print('\n--check: nothing written.')
        return

    for end, text in sorted(inserts, reverse=True):
        src = src[:end] + text + src[end:]
    open(SRC, 'w').write(src)
    print('\nwritten. Re-run with --check to confirm 15 wired and 0 to wire.')


if __name__ == '__main__':
    main('--check' in sys.argv)
