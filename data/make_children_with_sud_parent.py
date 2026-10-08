"""Children living with a parent who has a drug use disorder, NSDUH 2024 (the review's point that the model's share is
never checked; SAMHSA's older figure, about 3 per cent, was on the earlier diagnostic definition). Respondents aged 26 and over
(AGE3 7-11; the author, 8 October: "it should be 26+"), each weighted by ANALWT2_C times NRCH17_2, their own children under
18 in the household (3 = three or more): the share of those children whose parent has a moderate or severe drug use
disorder (SVYRDUDANY 2 or 3, the model's SUD), and any severity: per parent (the one surveyed), and either parent, the
other parent of a married respondent taking the child-weighted rate of married parents of the other sex, independently
(an upper bound if partners' disorders go together); the model's household is one adult.
usage: python3 data/make_children_with_sud_parent.py NSDUH_2024_Tab.csv  -> code/paper/nsduh_kids_sud.json"""
import json, os, sys
import pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'paper', 'nsduh_kids_sud.json')
F = sys.argv[1]
hdr = open(F).readline().rstrip('\n').split('\t')
clean = [h.replace('+AF8-', '_').upper() for h in hdr]
want = ['ANALWT2_C', 'AGE3', 'NRCH17_2', 'SVYRDUDANY', 'IRMARIT', 'IRSEX']
idx = [clean.index(w) for w in want]
d = pd.read_csv(F, sep='\t', usecols=idx, dtype=str)
d.columns = [clean[i] for i in sorted(idx)]
d = d.apply(pd.to_numeric, errors='coerce')
x = d[d.AGE3.isin([7, 8, 9, 10, 11]) & d.NRCH17_2.between(0, 3)]
kw = x.ANALWT2_C * x.NRCH17_2
mar = x.IRMARIT == 1
def shares(ind):
    v = ind.astype(float)
    p = {sx: (kw[mar & (x.IRSEX == sx)] * v[mar & (x.IRSEX == sx)]).sum() / kw[mar & (x.IRSEX == sx)].sum() for sx in (1, 2)}
    other = x.IRSEX.map({1: p[2], 2: p[1]})
    either = v.where(~mar, 1 - (1 - v) * (1 - other))
    return 100 * (kw * v).sum() / kw.sum(), 100 * (kw * either).sum() / kw.sum()
s1, s2 = shares(x.SVYRDUDANY.isin([2, 3])); d1, d2 = shares(x.SVYRDUDANY.isin([1, 2, 3]))
out = {'nsduh_kids_sud_pc': f"{s1:.1f}", 'nsduh_kids_sud_hh_pc': f"{s2:.1f}",
       'nsduh_kids_dud_pc': f"{d1:.1f}", 'nsduh_kids_dud_hh_pc': f"{d2:.1f}"}
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(out)
