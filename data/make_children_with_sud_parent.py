"""Children living with a parent who has a drug use disorder, NSDUH 2024 (the review's point that the model's share is
never checked; SAMHSA's older figure, about 3 per cent, was on the earlier diagnostic definition). Respondents aged 26-49
(AGE3 7-9, the ages a child is at home in the model), each weighted by ANALWT2_C times NRCH17_2, their own children under
18 in the household (3 = three or more): the share of those children whose parent has a moderate or severe drug use
disorder (SVYRDUDANY 2 or 3, the model's SUD), and any severity. A child with two parents in the sample's terms is
counted once per parent, which is the model's one-adult household.
usage: python3 data/make_children_with_sud_parent.py NSDUH_2024_Tab.csv  -> code/paper/nsduh_kids_sud.json"""
import json, os, sys
import pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'paper', 'nsduh_kids_sud.json')
F = sys.argv[1]
hdr = open(F).readline().rstrip('\n').split('\t')
clean = [h.replace('+AF8-', '_').upper() for h in hdr]
want = ['ANALWT2_C', 'AGE3', 'NRCH17_2', 'SVYRDUDANY']
idx = [clean.index(w) for w in want]
d = pd.read_csv(F, sep='\t', usecols=idx, dtype=str)
d.columns = [clean[i] for i in sorted(idx)]
d = d.apply(pd.to_numeric, errors='coerce')
x = d[d.AGE3.isin([7, 8, 9]) & d.NRCH17_2.between(0, 3)]
kw = x.ANALWT2_C * x.NRCH17_2
out = {'nsduh_kids_sud_pc': f"{100 * (kw * x.SVYRDUDANY.isin([2, 3])).sum() / kw.sum():.1f}",
       'nsduh_kids_dud_pc': f"{100 * (kw * x.SVYRDUDANY.isin([1, 2, 3])).sum() / kw.sum():.1f}"}
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(out)
