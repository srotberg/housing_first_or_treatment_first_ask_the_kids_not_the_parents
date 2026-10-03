"""
The benchmark's drug price elasticities, as x_ names for the prose, merged into
results_numbers.json beside export_results.py's.

usage: python3 code/paper/export_elasticity.py

Source now: results/elast_points/w0.txt, ten points from -50 to +50 by ten (see SRC below).
History: code/ELASTICITY_RESULT_MULTI.txt, the worker run of 30 September: the paper's 12
moment blocks, then the price raised from the saved benchmark state by each of 1, 2, 5,
10, 20 and 50 per cent, and the six elasticities AVERAGED (the author, 30 September: "you
should check 1%, 2%, 5%, 10%, 20%, 50% and average them out. same for the intensive
margin").  Its four standard checks passed; the fifth, that its 10 per cent line
reproduces run 3's (ELASTICITY_RESULT_BENCH.txt), holds at two decimals, not four.  Two
things the file records and the prose does not repeat: five of the six measurements
started from a voucher income threshold 4.8e-4 higher than the saved state's (the
restore does not reset median_income), and at 1-2 per cent the response is a few
households crossing grid points, so the per-user elasticity is +0.50 at 2 per cent.

THE 2 PER CENT STEP IS DROPPED (the author, 30 September: "i think you should throw away the
2% price increase, something there seems odd").  Its participation elasticity, -4.20, is
nearly twice its neighbours', and its per-user one is the only positive entry.  The averages
are over the other five steps, computed here from the per-step lines rather than read off
the run's own average line, which includes it: participation -2.37 -> -2.00, per user
-0.29 -> -0.45.

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
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
# THE TEN POINTS, -50 TO +50 BY TEN (2 October; the author: "we can wait for the numbers for table 6"):
# results/elast_points/w0.txt, a worker that re-solved the omega_c = 0.085 benchmark and then moved the
# price from its saved state down and up by each of 10 to 50 per cent. Replaces ELASTICITY_RESULT_2C.txt
# (1, 5, 10, 20 and 50 per cent up, the 2 per cent step dropped: -2.14 and -0.49). Two checks, here
# rather than in a note: every last-block moment of the re-solve within 1e-3 of the reference
# benchmark's, and the null re-solve at the base price moving users by under 1e-4.
SRC = os.path.join(ROOT, 'results', 'elast_points', 'w0.txt')
SRC_LOG = os.path.join(ROOT, 'results', 'elast_points', 'w0.bench.log.gz')
REF_LOG = os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085', 'bench.log.gz')
OUT = os.path.join(HERE, 'results_numbers.json')
LIT = {'part': (-0.3, -0.9), 'int': (-0.3, -0.8)}
EDGE = 0.10
DROP = ()                             # price steps, per cent, left out of the averages

txt = open(SRC).read()
assert 'solve exited 0' in txt, 'the elasticity worker did not finish'


def moments(path):
    d = {}
    for l in gzip.open(path, 'rt', errors='replace'):
        m = re.match(r'^ MOMENT (\S+).*model=\s*(\S+)', l)
        if m:
            d[m.group(1)] = float(m.group(2))
    return d


_a, _b = moments(SRC_LOG), moments(REF_LOG)
_gap = {k: abs(_a[k] / _b[k] - 1) for k in _b if k in _a and _b[k]}
assert len(_gap) >= 27 and max(_gap.values()) < 1e-3, \
    f'the re-solved benchmark is not the reference: {max(_gap.items(), key=lambda x: x[1])}'
_null = re.findall(r'ELASTICITY_NULL dp=0 users=.*rel gaps\s+(\S+)', txt)[-1]
assert abs(float(_null)) < 1e-4, f'the null re-solve moves users by {_null}'
rows = {}
for dp, pa, us in re.findall(r'^ ELASTICITY_MULTI dp=\s*(-?[\d.]+)\s+participation=\s*(\S+)\s+per_user=\s*(\S+)',
                             txt, re.M):
    rows[float(dp)] = (float(pa), float(us))
assert sorted(rows) == [-50.0, -40.0, -30.0, -20.0, -10.0, 10.0, 20.0, 30.0, 40.0, 50.0], \
    f'expected ten price changes, found {sorted(rows)}'
# the per-step lines reproduce the run's own average
m = re.findall(r'ELASTICITY_MULTI average participation=\s*(\S+)\s+per_user=\s*(\S+)', txt)[-1]
assert abs(sum(r[0] for r in rows.values()) / len(rows) - float(m[0])) < 1e-9
assert abs(sum(r[1] for r in rows.values()) / len(rows) - float(m[1])) < 1e-9
steps = [dp for dp in sorted(rows) if dp not in DROP]
part = sum(rows[dp][0] for dp in steps) / len(steps)
user = sum(rows[dp][1] for dp in steps) / len(steps)


def where(x, lo_hi):
    lo, hi = (abs(v) for v in lo_hi)
    a = abs(x)
    if abs(a - lo) <= EDGE * lo:
        return 'at the less elastic end of'
    if abs(a - hi) <= EDGE * hi:
        return 'at the more elastic end of'
    # 'larger in absolute value than' (review, 3 October): -1.61 is not higher than -0.3 to -0.9
    if a > hi:
        return 'larger in absolute value than'
    if a < lo:
        return 'smaller in absolute value than'
    # the author, 30 September: 'is in the middle of'
    return 'in the middle of'


def so_int(w):
    if w == 'larger in absolute value than':
        return "so each user's purchases respond more to the drug price in the model than in the data"
    if w == 'smaller in absolute value than':
        return "so each user's purchases respond less to the drug price in the model than in the data"
    return "so the model matches how much each user's purchases respond to the drug price"


def listing(xs):
    xs = [f'{x:.0f}' for x in xs]
    return ', '.join(xs[:-1]) + ' and ' + xs[-1]


out = json.load(open(OUT))
out.pop('x_el_dp_pc', None)          # the single 10 per cent step this replaced
# the sizes once, and whether the price was moved both ways
_sizes = sorted({abs(dp) for dp in steps})
out['x_el_dp_list'] = listing(_sizes)
out['x_el_dp_how'] = 'Raising and lowering' if min(steps) < 0 < max(steps) else 'Raising'
out['x_el_n_word'] = {4: 'four', 5: 'five', 6: 'six', 10: 'ten'}[len(steps)]
out['x_el_part'] = f'{part:.2f}'
out['x_el_int'] = f'{user:.2f}'
out['x_el_part_where'] = where(part, LIT['part'])
out['x_el_int_where'] = where(user, LIT['int'])
out['x_el_int_so'] = so_int(out['x_el_int_where'])
# THE LITERATURE'S ENDS AS NAMES, so the validation paragraph and Table 6 quote the range
# the direction words are measured against rather than typing it a second time
for k, (lo, hi) in LIT.items():
    out[f'x_el_{k}_lo'] = f'{lo:.1f}'
    out[f'x_el_{k}_hi'] = f'{hi:.1f}'
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print({k: out[k] for k in ('x_el_part', 'x_el_int', 'x_el_part_where', 'x_el_int_where', 'x_el_dp_list')})
