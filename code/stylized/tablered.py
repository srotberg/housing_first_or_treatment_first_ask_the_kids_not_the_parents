"""
Mark the cells of the stylized tables that have moved since the last version out.

WHY THIS EXISTS. fill.py already reds a number in the PROSE when it moves, and
sync_tables.py does the same for the Fortran's two tables. The four stylized
tables had nothing, so a round that changed every target and every model value
in Table 2 rendered entirely black and the author had to take the changes on
trust.

THE BASELINE IS THE SAME ONE THE PROSE USES. tables_prev.json holds the cells as
they stood at the version last sent out, alongside fill.py's numbers_prev.json,
so red here and red in the prose mean one thing: moved since you last read it.
Refresh the two together or they will disagree about what is new.

A ROW THE BASELINE DOES NOT HAVE IS ALL NEW, and every cell of it is marked.
That is how theta's row appears when it moves from Table 1 to Table 2.

ONLY CELLS THAT ARE NUMBERS ARE MARKED. A digit is not enough of a test: source
lines carry years, so "Drug spending over income among users, RAND 2016 and
NSDUH 2024" was being reddened as though a value had moved. A cell counts as a
number when it holds no letters beyond a unit suffix, which leaves 16.2\%,
$0.2350$ and 9.489 pp in and every description and source line out.
"""

import json
import os
import re

_PREV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tables_prev.json')
_BASE = json.load(open(_PREV)) if os.path.exists(_PREV) else {}


# A cell is a number when it carries no letters except a unit suffix. Years in a
# source line are digits but not values, and marking them says a number moved
# when none did.
_NUMERIC = re.compile(r'^[^A-Za-z]*(?:pp|percent)?[^A-Za-z]*$')


def _is_number(cell):
    return bool(cell) and bool(_NUMERIC.match(cell))


def mark(name, body):
    """Wrap every cell of `body` whose value moved since the baseline in red."""
    base = _BASE.get(name)
    if not base:
        return body
    out = []
    for line in body.split('\n'):
        s = line.strip()
        if not s.endswith(r'\\') or s.startswith(r'\multicolumn') or '&' not in s:
            out.append(line)
            continue
        cells = [c.strip() for c in s[:-2].split('&')]
        was = base.get(cells[0])
        if was is None:
            # A NEW ROW IS STILL ONLY MARKED ON ITS NUMBERS. Reddening its
            # description and its source line as well says "new" twice and
            # makes the numbers harder to pick out, which is the opposite of
            # what the mark is for.
            rest = [(r'\textcolor{red}{%s}' % c
                     if _is_number(c) else c) for c in cells[1:]]
        else:
            rest = []
            for k, c in enumerate(cells[1:]):
                old = was[k] if k < len(was) else None
                moved = (old is not None and c != old and _is_number(c))
                rest.append(r'\textcolor{red}{%s}' % c if moved else c)
        out.append(cells[0] + ' & ' + ' & '.join(rest) + r' \\')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# FREEZING THE BASELINE. The three red markers are refreshed together at the
# start of a comment round -- fill.py --freeze, sync_tables.py --freeze and this
# -- so that red means one thing across the whole note: moved since the version
# the author last read. This was being done by hand, which is how the four
# stylized tables came back red for changes the author had already seen.
#
# It reads the BUILT tables rather than regenerating them, so it freezes exactly
# what was sent out. Run it before applying a round's comments, never after.
_FILES = ('tab_internal.tex', 'tab_external.tex', 'tab_welfare.tex',
          'tab_children.tex')


def _cells(path):
    rows = {}
    for line in open(path):
        s = line.strip()
        if not s.endswith(r'\\') or s.startswith(r'\multicolumn') or '&' not in s:
            continue
        cells = [_bare(c.strip()) for c in s[:-2].split('&')]
        rows[cells[0]] = cells[1:]
    return rows


def _bare(cell):
    """The cell as it reads without this round's mark, so a frozen baseline
    never carries a wrapper into the next comparison."""
    m = re.fullmatch(r'\\textcolor\{red\}\{(.*)\}', cell)
    return m.group(1).strip() if m else cell


def freeze():
    tab = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '..', '..', 'writing', 'tables'))
    out = {}
    for f in _FILES:
        p = os.path.join(tab, f)
        if os.path.exists(p):
            out[f] = _cells(p)
    json.dump(out, open(_PREV, 'w'), indent=1)
    n = sum(len(v) for v in out.values())
    print(f'   froze {n} rows across {len(out)} stylized tables into '
          'tables_prev.json; the next build marks what moves from here')


if __name__ == '__main__':
    freeze()
