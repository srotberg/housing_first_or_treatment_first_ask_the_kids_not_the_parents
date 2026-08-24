#!/usr/bin/env python3
"""Does the paper's Set column say what the code actually does?

THE FAILURE THIS CATCHES. A table row says a parameter is calibrated
internally, the code holds it fixed, and nothing downstream notices: the row
reads as a result, the reader takes the target as matched, and no bracket is
moving it. delta_h was exactly that. Table 11 gives it as Int. against a child
homelessness ratio of 2.10 from Bassuk et al., the target constant
child_homeless_ratio_data = 2.10 is declared in the Fortran, and
penalty_child_homeless is a compile time PARAMETER of 0.31 that no update ever
touches. The target appeared once in the whole file, at its own declaration.

The mirror failure is a row marked Ext. that the code does calibrate, which
turns a stated assumption into a fitted number without saying so.

HOW A ROW IS JUDGED. links.py already says which Fortran constant each row's
Data column refers to. calibration_report.pairs() already says which parameter
brackets on which target, read from the distance expressions. Compose the two:
a row is Int. in the code when some parameter's distance is written against
that row's target constant AND that parameter's adjuster is not zero.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import links
import calibration_report as R

TABLES = [os.path.join(HERE, '..', '..', 'writing', 'tables', t)
          for t in ('tab_eleven.tex', 'tab_standard.tex', 'tab_internal.tex',
                    'tab_external.tex')]


def rows():
    """(symbol, set, source table) for every parameter row of the tables."""
    out = []
    for path in TABLES:
        if not os.path.exists(path):
            continue
        for line in open(path, errors='replace'):
            if not line.lstrip().startswith('$'):
                continue
            cells = [c.strip() for c in line.split('&')]
            if len(cells) < 3:
                continue
            setcol = re.sub(r'\\textcolor\{\w+\}\{([^}]*)\}', r'\1', cells[2]).strip()
            if setcol.rstrip('.') not in ('Int', 'Ext'):
                continue
            out.append((cells[0], setcol.rstrip('.'), os.path.basename(path)))
    return out


def main():
    pair = R.pairs()                      # parameter -> (model expr, target expr)
    frozen = R.zero_adjusters()
    src = open(R.FORTRAN, errors='replace').read()
    src = re.sub(r'&\s*\n\s*', '', src)

    # AN INCLUDE FLAG AT ZERO IS NOT A CALIBRATED PARAMETER, whatever its
    # adjuster says. rho_d has an adjuster of 0.05 and include_rho_d = 0, so it
    # enters as rho**(sud*include_rho), a multiplier of exactly one, and its
    # update is gated on the same flag. Reading the adjuster alone called it
    # internally calibrated and disagreed with a table that was right.
    off = {m.group(1) for m in re.finditer(
        r'integer,\s*parameter\s*::\s*include_(\w+)\s*=\s*0\b', src)}

    # AN ARRAY TARGET IS NAMED BY ELEMENT IN THE TABLE AND BY INDEX IN THE CODE.
    # links.py says housing_size_dist_data_1 for h_2, the Fortran writes
    # housing_size_dist_data(0), and stripping the index made the two fail to
    # meet: h_2 and h_4 read as external when both are bracketed every loop.
    # The suffix is the PRINT position, one more than the Fortran index.
    def keys(target):
        bare = re.sub(r'\((\d+)\)', '', target)
        m = re.search(r'\((\d+)\)', target)
        return {bare, target} | ({f'{bare}_{int(m.group(1)) + 1}'} if m else set())

    # target constant -> the parameters whose distance is written against it
    owner = {}
    for name, (_, target) in pair.items():
        for k in keys(target):
            owner.setdefault(k, []).append(name)

    bad, seen = [], set()
    print(f'{"row":26s} {"table says":11s} {"target constant":34s} code')
    print('-' * 104)
    for sym, says, table in rows():
        if sym in seen:
            continue
        seen.add(sym)
        target = links.LINKS.get(sym)
        if target is None:
            print(f'{sym:26s} {says:11s} {"(no link)":34s} not linked to a Fortran constant')
            continue
        live = [p for p in owner.get(target, [])
                if p not in frozen and p not in off]
        if live:
            code = 'Int., by ' + '+'.join(live)
        elif owner.get(target):
            why = ('its include flag is zero'
                   if any(p in off for p in owner[target])
                   else 'its adjuster is zero')
            code = f'HELD, {why}: ' + '+'.join(owner[target])
        elif re.search(r'parameter\s*::\s*\w*\s*=', src) and target in src:
            code = 'Ext., nothing brackets on it'
        else:
            code = 'Ext.'
        agree = (says == 'Int') == code.startswith('Int.')
        flag = '' if agree else '   <<< MISALIGNED'
        if not agree:
            bad.append((sym, says, code, table))
        print(f'{sym:26s} {says:11s} {target:34s} {code}{flag}')
    print('-' * 104)
    if bad:
        print(f'\n{len(bad)} row(s) where the table and the code disagree:')
        for sym, says, code, table in bad:
            print(f'  {sym:24s} {table:20s} table says {says}., code says {code}')
        return 1
    print('\nevery row agrees with the code')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
