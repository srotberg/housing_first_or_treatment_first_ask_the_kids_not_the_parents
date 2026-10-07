"""
A CHILD UNDER 18 LIVING IN THE HOUSEHOLD, BY DRUG USE AND AGE, NSDUH 2024, weighted (ANALWT2_C).

Written 7 October for the author's question whether drug users who have had a child (NSFG: 75 against 81 percent at
40-49, nsfg_births_by_drug_use.py) still live with it. At 35-49: 67 percent of non-users have a child under 18 at home,
49 of past-month users, 42 of those with a past-year drug use disorder, 31 of past-year hard drug users. IRKI17_2 counts
any child under 18 in the household, not only the respondent's own; the unsheltered homeless and the institutionalised
are outside the survey.

Run:  python3 make_children_at_home_by_use.py NSDUH_2024_Tab.csv
"""
import sys, numpy as np, pandas as pd
F = sys.argv[1]
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'ki17': 'IRKI17+AF8-2', 'coc': 'COCYR', 'crk': 'CRKYR',
        'her': 'HERYR', 'mth': 'METHAMYR', 'illmon': 'ILLMON', 'illyr': 'ILLYR', 'sud': 'UD5ILLANY'}
hdr = open(F).readline().rstrip('\n').split('\t')
pos = {k: hdr.index(v) for k, v in COLS.items()}
rows = []
with open(F) as f:
    f.readline()
    for line in f:
        p = line.rstrip('\n').split('\t')
        rows.append([p[pos[k]] for k in COLS])
d = pd.DataFrame(rows, columns=list(COLS)).apply(pd.to_numeric, errors='coerce')
d['kid'] = (d.ki17 >= 2).astype(float)
d['hard'] = ((d.coc == 1) | (d.crk == 1) | (d.her == 1) | (d.mth == 1)).astype(int)
GROUPS = [('no illicit use, past year', d.illyr != 1), ('illicit use, past month', d.illmon == 1),
          ('hard drug, past year', d.hard == 1), ('drug use disorder, past year', d.sud == 1)]
BANDS = [('26-29', [7]), ('30-34', [8]), ('35-49', [9]), ('26-49', [7, 8, 9]), ('50-64', [10])]
print(f'{"":30s}' + ''.join(f'{b:>16s}' for b, _ in BANDS))
for name, g in GROUPS:
    out = []
    for b, a in BANDS:
        x = d[g & d.age3.isin(a)]
        out.append(f'{100*np.average(x.kid, weights=x.wt):8.1f}% n{len(x):5d}')
    print(f'{name:30s}' + ''.join(f'{o:>16s}' for o in out))
