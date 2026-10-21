#!/usr/bin/env python3
"""Every parameter in the prose is in a table, and every table row is in the prose.

WHY THIS EXISTS. The note's parameter tables and its identification prose drifted
apart three separate ways at once, and none of them announced itself:

  - varsigma was marked Int. in the table while the prose said it is set rather
    than calibrated, and code/paper/params_spec.json agreed with the prose. The
    table file had simply not been regenerated;
  - lambda_m was still marked Int. against the SMI share of the homeless after it
    had become an assigned parameter and that moment had passed to eta_DI;
  - omega_m and eta_DI were live calibrated parameters in the Fortran, with
    entries in the prose, and appeared in no table at all.

sync_tables.py syncs NUMBERS into the table files. It does not add rows and does
not touch the Set column, so a structural change is invisible to it. This closes
that gap: it compares the SYMBOLS and the SET column against the prose.

WHAT IT CHECKS
  1. every \\item[$sym$, ...] in the identification prose has a table row;
  2. every table row has an \\item entry;
  3. the Set column agrees with the prose. "set externally" or "set to" in an
     entry means Ext.; "calibrated internally" or "calibrated to" means Int.

WHAT IT DOES NOT CHECK, said here so nobody assumes it does: whether an Int. row
brackets on the RIGHT model quantity. code/paper/check_alignment.py judges the
Set column against the Fortran; this one judges it against the prose. A row can
pass both and still target the wrong moment.

Run:  python3 check_params.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # writing/: these tools live in writing/tools/
SRC = os.path.join(HERE, 'housing_first_or_treatment_first.src.tex')
TABLES = ('tab_eleven.tex', 'tab_standard.tex')

# Rows that describe an object rather than a parameter with an entry of its own.
EXEMPT_ROWS = {r'\varepsilon(j)', r'\bar\phi(j)', r'\bar y', r's_m(j)',
               r'\varsigma_m(j)'}
# Entries for objects that are deliberately not tabulated.
EXEMPT_ITEMS = set()


def strip_red(t):
    """Unwrap \\textcolor{red}{...} even when the contents carry braces.

    A one-level regex missed every red row whose symbol is itself braced, which
    is most of them: $\\eta_{DI}$ inside \\textcolor{red}{} looked to the checker
    like no row at all, so a freshly added row read as missing.
    """
    key = '\\textcolor{red}{'
    while True:
        i = t.find(key)
        if i < 0:
            return t
        j = i + len(key)
        depth, k = 1, j
        while k < len(t) and depth:
            if t[k] == '{':
                depth += 1
            elif t[k] == '}':
                depth -= 1
            k += 1
        if depth:
            return t
        t = t[:i] + t[j:k - 1] + t[k:]


def strip_new(t):
    """Unwrap \\new{...}, so a red-marked \\item symbol still parses."""
    key = '\\new{'
    while True:
        i = t.find(key)
        if i < 0:
            return t
        j = i + len(key)
        depth, k = 1, j
        while k < len(t) and depth:
            if t[k] == '{':
                depth += 1
            elif t[k] == '}':
                depth -= 1
            k += 1
        if depth:
            return t
        t = t[:i] + t[j:k - 1] + t[k:]


def norm(sym):
    return re.sub(r'\s+', '', sym.strip().strip('$'))


def table_rows():
    out = {}
    for fn in TABLES:
        p = os.path.join(HERE, 'tables', fn)
        if not os.path.exists(p):
            continue
        group = None
        for line in open(p):
            line = strip_red(line)
            g = re.search(r'\\multicolumn\{\d+\}\{[^}]*\}\{\\emph\{([^}]*)\}\}', line)
            if g:
                group = g.group(1)
            if '&' not in line or line.lstrip().startswith('%'):
                continue
            cells = [c.strip() for c in line.split('&')]
            m = re.match(r'^\$(.+?)\$$', cells[0])
            if not m or len(cells) < 3:
                continue
            st = re.match(r'^(Int|Ext)\.', cells[2])
            if not st:
                continue
            out[norm(m.group(1))] = (st.group(1), fn, group, len(out))
    return out


def prose_items():
    body = strip_new(strip_red(open(SRC).read()))
    out = {}
    # AN ENTRY MAY COVER TWO PARAMETERS. "\\item[$\\kappa_V$ and $\\kappa_r$, the
    # voucher rules.]" is one entry and two rows, and reading it as a single
    # symbol named "kappa_V and kappa_r" reported both as missing.
    for m in re.finditer(r'\\item\[((?:\$[^$]+\$(?:\s+and\s+)?)+)', body):
        syms = re.findall(r'\$([^$]+)\$', m.group(1))
        tail = body[m.end():m.end() + 1400]
        tail = tail.split(r'\item[')[0]
        # WHICHEVER CLAIM COMES FIRST IS THE ONE ABOUT THIS PARAMETER. An entry
        # routinely mentions its neighbours -- pi^eu's says it is chosen given
        # "the job finding rate set externally below", and eta_DI's says the
        # replacement rate beside it is fixed from outside -- so a search that
        # simply looks for either phrase reads the neighbour's status as this
        # one's. Taking the earliest match is not clever, but it is right
        # whenever the entry opens by saying what the parameter is, which is the
        # convention here.
        low = tail.lower()
        ext = re.search(r'set externally|is set to|set rather than calibrated|'
                        r'assigned|which i set to', low)
        internal = re.search(r'calibrated internally|calibrated to|is calibrated|'
                             r'chosen to reproduce|chosen to match', low)
        said = None
        if ext and internal:
            said = 'Ext' if ext.start() < internal.start() else 'Int'
        elif ext:
            said = 'Ext'
        elif internal:
            said = 'Int'
        for sym in syms:
            out[norm(sym)] = (said, len(out))
    return out


def order_report(rows, items):
    """Where the prose runs the parameters in a different order from the table.

    THE TABLE IS THE ORDER. A reader goes down Table 11 and looks each row up in
    the text, so an entry that appears three parameters early is one the reader
    has to hunt for. Nothing checked this and it drifted twice: eta_DI's entry
    sat in the housing block while its row was in the mental illness chain, and
    omega_m came before lambda_m in the prose and after it in the table.

    Reported as the LONGEST COMMON SUBSEQUENCE against the table's order, so the
    output names the entries that are out of place rather than every entry after
    the first displaced one.
    """
    shared = [s for s in rows if s in items]
    shared.sort(key=lambda s: rows[s][3])
    seq = [items[s][1] for s in shared]
    n = len(seq)
    best = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            if seq[j] < seq[i] and best[j] + 1 > best[i]:
                best[i], prev[i] = best[j] + 1, j
    keep = set()
    if n:
        i = max(range(n), key=lambda k: best[k])
        while i >= 0:
            keep.add(i)
            i = prev[i]
    return [shared[i] for i in range(n) if i not in keep]


def main():
    rows, items = table_rows(), prose_items()
    bad = []
    for sym, (said, _) in sorted(items.items()):
        if sym in EXEMPT_ITEMS:
            continue
        if sym not in rows:
            bad.append('  in the prose, in no table:      $%s$' % sym)
        elif said and rows[sym][0] != said:
            bad.append('  the table says %s., the prose says %s.:  $%s$'
                       % (rows[sym][0], said, sym))
    for sym, (st, fn, group, _) in sorted(rows.items()):
        if sym in EXEMPT_ROWS or sym in items:
            continue
        bad.append('  in %-16s in no prose entry:  $%s$' % (fn + ',', sym))
    for sym in order_report(rows, items):
        bad.append('  out of the table\'s order in the prose:  $%s$   (%s)'
                   % (sym, rows[sym][2] or 'no group'))
    if bad:
        print('parameters: text and tables disagree\n')
        print('\n'.join(bad))
        print('\n%d disagreement(s). Fix the table row or the prose entry; '
              'they are the same claim written twice.' % len(bad))
        return 1
    print('   %d parameters: every prose entry has a table row, every table row '
          'has a prose entry, and the Set column agrees with both'
          % len(set(items) | set(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
