"""
A CHILD UNDER 18 AT HOME, USERS AGAINST NON-USERS OF THE SAME AGE, SEX, INCOME AND MARITAL STATUS. NSDUH 2024, 26-49.

The same reweighting as make_altruism_moment.py, run the other way: non-users are reweighted to the users' cells.
Past-month users 43.5 against 51.1 percent (raw non-users 60.0); a disorder of any severity 39.5 against 48.2; hard
drugs in the past year 27.6 against 44.3. Marital status may partly be an outcome of use, so the comparison without it
(income column) is the other bound.

Run:  python3 make_children_at_home_reweighted.py NSDUH_2024_Tab.csv
"""
import sys, numpy as np, pandas as pd
F = sys.argv[1]
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'ki17': 'IRKI17+AF8-2', 'coc': 'COCYR', 'crk': 'CRKYR',
        'her': 'HERYR', 'mth': 'METHAMYR', 'illmon': 'ILLMON', 'illyr': 'ILLYR', 'sud': 'UD5ILLANY',
        'sex': 'IRSEX', 'marit': 'IRMARIT', 'pinc': 'IRPINC3'}
hdr = open(F).readline().rstrip('\n').split('\t')
pos = {k: hdr.index(v) for k, v in COLS.items()}
rows = []
with open(F) as f:
    f.readline()
    for line in f:
        p = line.rstrip('\n').split('\t')
        rows.append([p[pos[k]] for k in COLS])
d = pd.DataFrame(rows, columns=list(COLS)).apply(pd.to_numeric, errors='coerce')
d = d[d.age3.isin([7, 8, 9])].copy()
d['kid'] = (d.ki17 >= 2).astype(float)
d['hard'] = ((d.coc == 1) | (d.crk == 1) | (d.her == 1) | (d.mth == 1))
non = d[d.illyr != 1]
def rw(users, cells):
    """non-users' rate reweighted to the users' distribution over the cells"""
    wu = users.groupby(cells).wt.sum()
    rn = non.groupby(cells).apply(lambda x: np.average(x.kid, weights=x.wt), include_groups=False)
    common = wu.index.intersection(rn.index)
    sh = wu.loc[common] / wu.loc[common].sum()
    return float((sh * rn.loc[common]).sum()), float(wu.loc[common].sum() / wu.sum())
print(f'{"26-49":28s} {"users":>7s} {"non-users":>10s} {"non-users like users in:":>26s}')
print(f'{"":28s} {"":7s} {"raw":>10s} {"age, sex":>12s} {"+ income":>10s} {"+ marital":>10s}')
for name, g in (('illicit use, past month', d.illmon == 1), ('drug use disorder, past yr', d.sud == 1),
                ('hard drug, past year', d.hard)):
    u = d[g]
    ru = np.average(u.kid, weights=u.wt)
    rn = np.average(non.kid, weights=non.wt)
    a, _ = rw(u, ['age3', 'sex'])
    b, _ = rw(u, ['age3', 'sex', 'pinc'])
    c, cov = rw(u, ['age3', 'sex', 'pinc', 'marit'])
    print(f'{name:28s} {100*ru:6.1f}% {100*rn:9.1f}% {100*a:11.1f}% {100*b:9.1f}% {100*c:9.1f}%  (n {len(u)}, cover {100*cov:.0f}%)')
