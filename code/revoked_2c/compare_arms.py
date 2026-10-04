#!/usr/bin/env python3
"""compare_arms.py <mine_null> <accepted_null> <mine_fixboth> <accepted_fixboth>: worst relative difference of the
re-solved arms' headline statistics against the accepted runs (finalstats.py outputs)."""
import re, sys
def lv(p):
    out = {}
    for l in open(p, errors='replace'):
        m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
        if m:
            try: out[m.group(1).strip()] = float(m.group(2))
            except ValueError: pass
    return out
keys = ('drug price', 'pi_V (voucher probability)', 'drug use b', 'SUD lambda_d', 'homelessness h_1',
        'share of households holding a voucher', 'welfare (with childhood)')
for mine, acc, name in ((sys.argv[1], sys.argv[2], 'null'), (sys.argv[3], sys.argv[4], 'fixboth')):
    x, y = lv(mine), lv(acc)
    d = {k: abs(x[k] / y[k] - 1) for k in keys if k in x and y.get(k)}
    w = max(d, key=d.get) if d else None
    print(f'{name}: worst relative difference {d[w]:.1e} ({w}) over {len(d)} statistics' if w else f'{name}: nothing to compare')
