"""Run:  python3 make_altruism_moment_hhsize.py NSDUH_2024_Tab.csv

The parent/non-parent gap in past-month use (NSDUH 2024, 26+) with parents and non-parents in households of the
SAME SIZE (IRHHSIZ2, 6 = six or more): the data's counterpart of the omega_c = 0 experiment, which keeps the household
and removes only the concern. Parents are reweighted to the non-parents' cells, as in make_altruism_moment.py."""
import sys, numpy as np, pandas as pd
F = sys.argv[1]
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'sex': 'IRSEX', 'marit': 'IRMARIT', 'ki17': 'IRKI17+AF8-2',
        'pinc': 'IRPINC3', 'finc': 'IRFAMIN3', 'hh': 'IRHHSIZ2', 'illmon': 'ILLMON', 'illyr': 'ILLYR'}
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
def gap(cells, x, outcome='illmon'):
    p, n = x[x.kid == 1], x[x.kid == 0]
    w0 = n.groupby(cells).wt.sum()
    u1 = p.groupby(cells).apply(lambda g: np.average(g[outcome], weights=g.wt), include_groups=False)
    u0 = n.groupby(cells).apply(lambda g: np.average(g[outcome], weights=g.wt), include_groups=False)
    c = u0.index.intersection(u1.index)
    sh = w0.loc[c] / w0.loc[c].sum()
    a, b = float((sh * u1.loc[c]).sum()), float((sh * u0.loc[c]).sum())
    return a, b, float(w0.loc[c].sum() / w0.sum())
two = d[d.hh >= 2]
print('non-parents by household size (weighted share):',
      {int(k): round(float(v), 3) for k, v in (d[d.kid == 0].groupby('hh').wt.sum() / d[d.kid == 0].wt.sum()).items()})
print('parents by household size:', {int(k): round(float(v), 3) for k, v in (d[d.kid == 1].groupby('hh').wt.sum() / d[d.kid == 1].wt.sum()).items()})
for label, cells, x in (('paper: age, sex, marital, personal income', ['age3', 'pinc', 'sex', 'marit'], d),
                        ('+ household size', ['age3', 'pinc', 'sex', 'marit', 'hh'], d),
                        ('age, sex, marital, hh size, family income', ['age3', 'finc', 'sex', 'marit', 'hh'], d),
                        ('age, sex, marital, hh size, both incomes', ['age3', 'pinc', 'finc', 'sex', 'marit', 'hh'], d),
                        ('age, sex, marital, hh size (no income)', ['age3', 'sex', 'marit', 'hh'], d)):
    a, b, cov = gap(cells, x)
    print(f'{label:44s} parents {100*a:5.2f}%  non-parents {100*b:5.2f}%  ratio {a/b:.3f}  non-parents use {100*(b/a-1):+5.1f}%  (cover {100*cov:.0f}%)')
for label, cells in (('+ household size, past-YEAR use', ['age3', 'pinc', 'sex', 'marit', 'hh']),):
    a, b, cov = gap(cells, d, 'illyr')
    print(f'{label:44s} parents {100*a:5.2f}%  non-parents {100*b:5.2f}%  ratio {a/b:.3f}  non-parents use {100*(b/a-1):+5.1f}%  (cover {100*cov:.0f}%)')

print('\nTHE OTHER DIRECTION: non-parents reweighted to the PARENTS\' cells (cover is of parents)')
def gap_att(cells, x, outcome='illmon'):
    p, n = x[x.kid == 1], x[x.kid == 0]
    w1 = p.groupby(cells).wt.sum()
    u1 = p.groupby(cells).apply(lambda g: np.average(g[outcome], weights=g.wt), include_groups=False)
    u0 = n.groupby(cells).apply(lambda g: np.average(g[outcome], weights=g.wt), include_groups=False)
    c = u1.index.intersection(u0.index)
    sh = w1.loc[c] / w1.loc[c].sum()
    a, b = float((sh * u1.loc[c]).sum()), float((sh * u0.loc[c]).sum())
    return a, b, float(w1.loc[c].sum() / w1.sum())
for label, cells in (('paper cells', ['age3', 'pinc', 'sex', 'marit']),
                     ('+ household size', ['age3', 'pinc', 'sex', 'marit', 'hh']),
                     ('hh size, family income', ['age3', 'finc', 'sex', 'marit', 'hh'])):
    a, b, cov = gap_att(cells, d)
    print(f'{label:44s} parents {100*a:5.2f}%  non-parents {100*b:5.2f}%  ratio {a/b:.3f}  non-parents use {100*(b/a-1):+5.1f}%  (cover {100*cov:.0f}%)')
print('\nby household size, paper cells within each size (parents reweighted to non-parents):')
for h in range(2, 7):
    a, b, cov = gap(['age3', 'pinc', 'sex', 'marit'], d[d.hh == h])
    n1 = int((d[(d.hh == h)].kid == 1).sum()); n0 = int((d[(d.hh == h)].kid == 0).sum())
    print(f'  size {h}: ratio {a/b:.3f}  non-parents use {100*(b/a-1):+5.1f}%  (parents n {n1}, non-parents n {n0}, cover {100*cov:.0f}%)')
