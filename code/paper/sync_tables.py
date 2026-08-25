"""
Push the Fortran's numbers into the two parameter tables, and export them for
the prose, so a number lives in exactly one place.

WHAT IT DOES. For every row of Tables 5 and 6 that links.py ties to a Fortran
declaration, it rewrites that row's Data cell (for internally calibrated rows,
whose Data column is the target) or its Data and Value cells (for externally
set rows, where both state the number) from the declaration, keeping the cell's
own formatting. It then writes params_numbers.json, one entry per linked row,
which fill.py merges so the prose can quote the same number as @@q_<name>@@
instead of typing it.

RED. Any cell whose number changes is wrapped in \\textcolor{red}{}, and the
placeholder for it is marked as moved, so an update shows up in the paper as an
update rather than arriving silently. The comparison is against
params_prev.json, frozen with --freeze the same way fill.py freezes its own.

WHY IN PLACE RATHER THAN REGENERATED. Regenerating the tables from a spec would
put their column widths, group headings and notes under the control of this
file, and those have been tuned by hand against real overfull boxes. Rewriting
only the numbers leaves all of that alone and cannot mangle a layout.

Run:  python3 sync_tables.py [--freeze] [--dry-run]
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fortran_consts import constants
from links import LINKS, UNITS_DIFFER

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.normpath(os.path.join(HERE, '..', '..', 'writing', 'tables'))
PREV = os.path.join(HERE, 'params_prev.json')
OUT = os.path.join(HERE, 'params_numbers.json')
FILES = ('tab_eleven.tex', 'tab_standard.tex')

RED = r'\textcolor{red}{%s}'
_RED = re.compile(r'\\textcolor\{red\}\{(.*)\}$')


def _bare(cell):
    c = cell.strip()
    m = _RED.match(c)
    return m.group(1).strip() if m else c


def _shape(cell):
    """How this cell writes a number: percent or not, and to how many places."""
    c = _bare(cell)
    m = re.fullmatch(r'\$?(\d+)\.(\d+)\$?\s*(\\%)?', c)
    if m:
        return bool(m.group(3)), len(m.group(2)), c.startswith('$')
    m = re.fullmatch(r'\$?(\d+)\$?\s*(\\%)?', c)
    if m:
        return bool(m.group(2)), 0, c.startswith('$')
    return None


def _fmt(x, shape):
    pct, dp, dollar = shape
    v = x * 100.0 if pct else x
    s = f'{v:.{dp}f}'
    if pct:
        s += r'\%'
    return f'${s}$' if dollar else s


def _key(sym):
    return re.sub(r'[^a-z0-9]+', '_', sym.lower()).strip('_') or 'x'


def run(freeze=False, dry=False):
    C = constants()
    prev = json.load(open(PREV)) if os.path.exists(PREV) else None
    nums, moved, touched = {}, [], 0
    for f in FILES:
        p = os.path.join(TAB, f)
        lines = open(p, encoding='utf-8').read().split('\n')
        for i, line in enumerate(lines):
            # A SET CELL WRAPPED IN RED IS STILL A SET CELL. Matching the
            # literal '& Int. &' made every row whose Set column carries this
            # round's mark invisible here, so a newly added parameter exported
            # nothing and its placeholder came out unfilled. fill.py's
            # _param_counts had the same blind spot and was fixed the same way.
            if r'\\' not in line:
                continue
            _set = re.search(r'&\s*(?:\\textcolor\{red\}\{)?\s*(Int|Ext)\.', line)
            if _set is None:
                continue
            cells = line.rstrip().rstrip('\\').rstrip('\\').split('&')
            if len(cells) != 7:
                continue
            sym = cells[0].strip()
            name = 'q_' + _key(_bare(sym))
            k = LINKS.get(_bare(sym))
            if not k or _bare(sym) in UNITS_DIFFER:
                # NO FORTRAN COUNTERPART, so the table cell is itself the source.
                # These are the values taken straight from a paper, and the prose
                # quotes several of them; exporting them here means the table and
                # the sentence beside it cannot disagree, which is the failure
                # this whole file exists to prevent. The linked rows below are
                # stronger, since their source is the declaration the model runs
                # on, but a shared cell beats two typed copies either way.
                lit = _bare(cells[6]) if _bare(cells[6]) not in ('n.a.', r'\textemdash') else _bare(cells[4])
                lit = re.sub(r'^\$|\$$', '', lit).replace(r'\%', '')
                if re.fullmatch(r'\d+\.?\d*', lit):
                    nums.setdefault(name, lit)
                continue
            x = C[k]
            cols = [4] if _set.group(1) == 'Int' else [4, 6]
            changed = False
            for ci in cols:
                shape = _shape(cells[ci])
                if shape is None:
                    continue
                new = _fmt(x, shape)
                if _bare(cells[ci]) != new:
                    changed = True
                cells[ci] = ' ' + (RED % new if changed else new) + ' '
            # THE VALUE CELL'S SHAPE WHEN THE DATA CELL HAS NONE. An Ext. row
            # whose Data column reads n.a. fell through to a two decimal
            # default, so lambda_m exported as 0.07 while the table beside it
            # printed 0.067, and the prose quoted the rounded one. cells[6]
            # is the Value column and states the same quantity.
            shape = _shape(cells[4]) or _shape(cells[6]) or (False, 2, False)
            nums[name] = _fmt(x, (shape[0], shape[1], False)).replace(r'\%', '')
            # A PERCENT VARIANT FOR EVERY ROW. The tenant's contribution is 0.30
            # in the table and thirty per cent in the sentence beside it, and
            # the prose quoted the table's number followed by the word percent,
            # so it read 0.30 percent. Exporting both forms means a sentence can
            # take the one it needs instead of the one the table happens to
            # print, and the mistake cannot recur silently.
            nums[name + '_pc'] = f'{100.0 * x:g}'
            if prev is not None and prev.get(name) != nums[name]:
                moved.append(name)
            if changed:
                touched += 1
                lines[i] = '&'.join(cells).rstrip() + r' \\'
        if not dry:
            open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    if freeze:
        json.dump(nums, open(PREV, 'w'), indent=1)
        print(f'   froze {len(nums)} table numbers; the next run marks what moves')
        return nums
    if not dry:
        json.dump(nums, open(OUT, 'w'), indent=1)
    print(f'   {len(nums)} table numbers exported, {touched} cell(s) rewritten and reddened')
    if prev is None:
        print('   params_prev.json missing: nothing marked as moved')
    else:
        print(f'   {len(moved)} moved: {" ".join(moved) if moved else "none"}')
    return nums


if __name__ == '__main__':
    run('--freeze' in sys.argv, '--dry-run' in sys.argv)
