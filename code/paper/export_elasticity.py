"""
The benchmark's drug price elasticities, as x_ names for the prose, merged into
results_numbers.json beside export_results.py's.

usage: python3 code/paper/export_elasticity.py

Source: code/ELASTICITY_RESULT_MULTI.txt, the worker run of 30 September: the paper's 12
moment blocks, then the price raised from the saved benchmark state by each of 1, 2, 5,
10, 20 and 50 per cent, and the six elasticities AVERAGED (the author, 30 September: "you
should check 1%, 2%, 5%, 10%, 20%, 50% and average them out. same for the intensive
margin").  Its four standard checks passed; the fifth, that its 10 per cent line
reproduces run 3's (ELASTICITY_RESULT_BENCH.txt), holds at two decimals, not four.  Two
things the file records and the prose does not repeat: five of the six measurements
started from a voucher income threshold 4.8e-4 higher than the saved state's (the
restore does not reset median_income), and at 1-2 per cent the response is a few
households crossing grid points, so the per-user elasticity is +0.50 at 2 per cent and
the average over all six, -0.29, would be -0.45 without it.

THE INTENSIVE MARGIN IS OVER ALL USERS (the author, 30 September: "the intensive margin
should be based on all users not just addicted"): the per-USER column, not the per-ADDICT
one (-1.01).

The direction words compare the model with the range the prose quotes from the
literature: participation -0.3 to -0.9 (Saffer and Chaloupka 1999; Grossman and
Chaloupka 1998), intensive -0.3 to -0.8 (Grossman and Chaloupka 1998; Olmstead et al.
2015).  They are typed there, so they are typed here once, beside it.  A value within a
tenth of either end, in proportion, is AT that end rather than outside it: -0.29 against
a range starting at -0.3 is at its less elastic end, and 'lower than' would overstate
the difference.  The clause that follows the word is generated with it.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'ELASTICITY_RESULT_MULTI.txt')
OUT = os.path.join(HERE, 'results_numbers.json')
LIT = {'part': (-0.3, -0.9), 'int': (-0.3, -0.8)}
EDGE = 0.10

txt = open(SRC).read()
assert 'THE FOUR STANDARD CHECKS PASSED' in txt, 'the elasticity run did not pass its checks'
m = re.findall(r'ELASTICITY_MULTI average participation=\s*(\S+)\s+per_user=\s*(\S+)\s+per_addict=\s*(\S+)', txt)
part, user = float(m[-1][0]), float(m[-1][1])
steps = []
for s in re.findall(r'ELASTICITY_MULTI dp=\s*([\d.]+)\s+participation=', txt):
    if float(s) not in steps:
        steps.append(float(s))
assert len(steps) == 6, f'expected six price changes, found {steps}'


def where(x, lo_hi):
    lo, hi = (abs(v) for v in lo_hi)
    a = abs(x)
    if abs(a - lo) <= EDGE * lo:
        return 'at the less elastic end of'
    if abs(a - hi) <= EDGE * hi:
        return 'at the more elastic end of'
    if a > hi:
        return 'higher than'
    if a < lo:
        return 'lower than'
    return 'within'


def so_int(w):
    if w == 'higher than':
        return "so each user's purchases respond more to the drug price in the model than in the data"
    if w == 'lower than':
        return "so each user's purchases respond less to the drug price in the model than in the data"
    return "so the model matches how much each user's purchases respond to the drug price"


def listing(xs):
    xs = [f'{x:.0f}' for x in xs]
    return ', '.join(xs[:-1]) + ' and ' + xs[-1]


out = json.load(open(OUT))
out.pop('x_el_dp_pc', None)          # the single 10 per cent step this replaced
out['x_el_dp_list'] = listing(steps)
out['x_el_part'] = f'{part:.2f}'
out['x_el_int'] = f'{user:.2f}'
out['x_el_part_where'] = where(part, LIT['part'])
out['x_el_int_where'] = where(user, LIT['int'])
out['x_el_int_so'] = so_int(out['x_el_int_where'])
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print({k: out[k] for k in ('x_el_part', 'x_el_int', 'x_el_part_where', 'x_el_int_where', 'x_el_dp_list')})
