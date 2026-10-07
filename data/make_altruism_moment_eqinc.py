"""Run:  python3 make_altruism_moment_eqinc.py NSDUH_2024_Tab.csv

The parent/non-parent gap in past-month use (NSDUH 2024, 26+), matched on personal income (the paper's moment)
against matched on family income PER EFFECTIVE PERSON, which is what the omega_c = 0 experiment holds fixed."""
import sys, numpy as np, pandas as pd
F = sys.argv[1]
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'sex': 'IRSEX', 'marit': 'IRMARIT', 'ki17': 'IRKI17+AF8-2',
        'pinc': 'IRPINC3', 'finc': 'IRFAMIN3', 'hh': 'IRHHSIZ2', 'pov': 'POVERTY3', 'illmon': 'ILLMON'}
hdr = open(F).readline().rstrip('\n').split('\t')
pos = {k: hdr.index(v) for k, v in COLS.items()}
rows = []
with open(F) as f:
    f.readline()
    for line in f:
        p = line.rstrip('\n').split('\t')
        rows.append([p[pos[k]] for k in COLS])
d = pd.DataFrame(rows, columns=list(COLS)).apply(pd.to_numeric, errors='coerce')
d = d[d.age3 >= 7].copy()
d['kid'] = (d.ki17 >= 2).astype(int)
MID = {1: 5, 2: 15, 3: 25, 4: 35, 5: 45, 6: 62.5, 7: 100}
d['eqi'] = d.finc.map(MID) / np.sqrt(d.hh.clip(1, 6))
# seven bins at the weighted septiles of income per effective person
o = d.sort_values('eqi'); cw = o.wt.cumsum() / o.wt.sum()
cuts = [o.eqi[cw >= q].iloc[0] for q in np.arange(1, 7) / 7]
d['eqbin'] = np.searchsorted(np.unique(cuts), d.eqi, side='right')
def gap(cells, sub=None):
    x = d if sub is None else d[sub]
    p, n = x[x.kid == 1], x[x.kid == 0]
    w0 = n.groupby(cells).wt.sum()
    u1 = p.groupby(cells).apply(lambda g: np.average(g.illmon, weights=g.wt), include_groups=False)
    u0 = n.groupby(cells).apply(lambda g: np.average(g.illmon, weights=g.wt), include_groups=False)
    c = u0.index.intersection(u1.index)
    sh = w0.loc[c] / w0.loc[c].sum()
    a, b = float((sh * u1.loc[c]).sum()), float((sh * u0.loc[c]).sum())
    return a, b, float(w0.loc[c].sum() / w0.sum())
for label, cells in (('personal income (paper)', ['age3', 'pinc', 'sex', 'marit']),
                     ('family income per eff. person', ['age3', 'eqbin', 'sex', 'marit']),
                     ('poverty level (family size)', ['age3', 'pov', 'sex', 'marit']),
                     ('personal x family per person', ['age3', 'pinc', 'eqbin', 'sex', 'marit'])):
    a, b, cov = gap(cells)
    print(f'{label:32s} parents {100*a:5.2f}%  non-parents {100*b:5.2f}%  ratio {a/b:.3f}  non-parents use {100*(b/a-1):+.1f}%  (cover {100*cov:.0f}%)')
print('\nby age, matched on family income per effective person:')
for ag, lab in ((7, '26-29'), (8, '30-34'), (9, '35-49'), (10, '50-64')):
    a, b, _ = gap(['eqbin', 'sex', 'marit'], d.age3 == ag)
    print(f'  {lab}  ratio {a/b:.3f}')
