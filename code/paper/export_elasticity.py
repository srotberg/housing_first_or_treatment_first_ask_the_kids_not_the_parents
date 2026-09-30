"""
The benchmark's drug price elasticities, as x_ names for the prose, merged into
results_numbers.json beside export_results.py's.

usage: python3 code/paper/export_elasticity.py

Source: code/ELASTICITY_RESULT_BENCH.txt, worker run 3 of 29 September (PASSED on all
four checks: the paper's 12 moment blocks, the base line equal to the last block, the
save reached, the CEV null), a +10 per cent price measured once after the loop.

THE INTENSIVE MARGIN IS OVER ALL USERS (the author, 30 September: "the intensive margin
should be based on all users not just addicted"): the per-USER line, -0.63, not the
Fortran's UNTARGETED intensive line, which is per ADDICT (-1.01).

The direction words compare the model with the most elastic end of the range the prose
quotes from the literature: participation -0.3 to -0.9 (Saffer and Chaloupka 1999;
Grossman and Chaloupka 1998), intensive -0.3 to -0.8 (Grossman and Chaloupka 1998;
Olmstead et al. 2015).  They are typed there, so they are typed here once, beside it.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'ELASTICITY_RESULT_BENCH.txt')
OUT = os.path.join(HERE, 'results_numbers.json')
LIT = {'part': (-0.3, -0.9), 'int': (-0.3, -0.8)}

txt = open(SRC).read()
assert 'VERDICT: PASSED' in txt, 'the elasticity run did not pass its checks'
part = float(re.search(r'UNTARGETED price elasticity, participation\s+model=\s*(-?[\d.]+)', txt).group(1))
user = float(re.search(r'DIAG elasticity, quantity per USER \(mixed\)\s*=\s*(-?[\d.]+)', txt).group(1))


def where(x, lo_hi):
    lo, hi = lo_hi
    if abs(x) > abs(hi):
        return 'higher than'
    if abs(x) < abs(lo):
        return 'lower than'
    return 'within'


# THE PRICE CHANGE the elasticities are measured at (the author asked, twice): the run
# raises the price once, from its base to the new level, holding the distribution
base_p = float(re.findall(r'ELASTICITY_DIAG base price=\s*([-+.\dEe]+)\s', txt)[-1])
new_p = float(re.findall(r'ELASTICITY_DIAG new price=\s*([-+.\dEe]+)\s', txt)[-1])

out = json.load(open(OUT))
out['x_el_dp_pc'] = f'{100 * (new_p / base_p - 1):.0f}'
out['x_el_part'] = f'{part:.2f}'
out['x_el_int'] = f'{user:.2f}'
out['x_el_part_where'] = where(part, LIT['part'])
out['x_el_int_where'] = where(user, LIT['int'])
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print({k: out[k] for k in ('x_el_part', 'x_el_int', 'x_el_part_where', 'x_el_int_where')})
