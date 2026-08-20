"""
Turn the two hand written parameter tables into a spec, once.

The spec is then the only place a row lives: params.py generates the tables
from it and exports every value in it as a placeholder the prose can quote, so
a number appears in the paper exactly once and comes from the model or from
the Fortran declaration that sets it.

Each Data cell is linked to a Fortran `*_data` constant by matching its value,
which is how the link is made without transcribing fifty four rows by hand.
Cells that match nothing keep their literal and are reported, so the ones that
still need a source are visible rather than silently frozen.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fortran_consts import constants

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.normpath(os.path.join(HERE, '..', '..', 'writing', 'tables'))

CONST = constants()


def _val(cell):
    """The numeric value a Data cell states, if it states one."""
    c = re.sub(r'\\textcolor\{red\}\{|\}|\$|\\%|,', '', cell).strip()
    m = re.fullmatch(r'(\d+\.?\d*)\s*%?', c)
    if not m:
        return None, None
    x = float(m.group(1))
    return (x / 100.0, 'pct') if '%' in c else (x, 'raw')


def _link(x):
    """The Fortran constant whose value is this cell's, if there is one."""
    if x is None:
        return None
    for k, v in CONST.items():
        if k.endswith('_data') and abs(v - x) <= max(1e-9, 5e-4 * abs(x)):
            return k
    return None


def parse(fname, table):
    rows, group = [], None
    for line in open(os.path.join(TAB, fname), encoding='utf-8'):
        g = re.search(r'\\multicolumn\{7\}\{@\{\}l\}\{\\emph\{([^}]*)\}\}', line)
        if g:
            group = g.group(1)
            continue
        if r'\\' not in line or ('& Int. &' not in line and '& Ext. &' not in line):
            continue
        cells = [c.strip() for c in line.rstrip().rstrip('\\\\').split('&')]
        if len(cells) != 7:
            continue
        sym, desc, setby, moment, data, model, value = cells
        x, kind = _val(data)
        src = _link(x)
        rows.append(dict(table=table, group=group, sym=sym, desc=desc, set=setby,
                         moment=moment, data_src=src, data_kind=kind,
                         data_lit=None if src else data, model=model, value=value))
    return rows


if __name__ == '__main__':
    rows = parse('tab_eleven.tex', 'main') + parse('tab_standard.tex', 'standard')
    linked = [r for r in rows if r['data_src']]
    open(os.path.join(HERE, 'params_spec.json'), 'w').write(json.dumps(rows, indent=1))
    print(f'{len(rows)} rows, {len(linked)} linked to a Fortran constant')
    print('\nlinked:')
    for r in linked:
        print(f"   {r['sym']:24s} {r['data_src']}")
    print('\nnot linked, still literal:')
    for r in rows:
        if not r['data_src']:
            print(f"   {r['sym']:24s} {r['data_lit']}")
