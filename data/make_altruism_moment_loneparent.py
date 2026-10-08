"""Run:  python3 make_altruism_moment_loneparent.py NSDUH_2024_Tab.csv

Writes code/paper/nsduh_loneparent.json: how much more the non-parents use in the past month, lowest and highest over
personal or family income held equal and each group's weights -- nsduh_lp_unm_lo_pc/hi_pc against unmarried two-adult
households (also matched on marital status), nsduh_lp_mar_lo/hi against married couples -- and the lone parents' count.

Two-person households, NSDUH 2024, 26+: a lone parent with one child under 18 against a married couple with no child,
and against an unmarried adult living with one other adult (partner, roommate or relative; the public file has no
cohabitation flag). Drug use matched on age, sex and income, reweighting each way."""
import json, os, sys, numpy as np, pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'paper', 'nsduh_loneparent.json')
F = sys.argv[1]
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'sex': 'IRSEX', 'marit': 'IRMARIT', 'ki17': 'IRKI17+AF8-2',
        'nrch': 'NRCH17+AF8-2', 'pinc': 'IRPINC3', 'finc': 'IRFAMIN3', 'hh': 'IRHHSIZ2',
        'illmon': 'ILLMON', 'illyr': 'ILLYR', 'sud': 'UD5ILLANY'}
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
print('NRCH17_2 against IRKI17_2 among 2-person households:\n', pd.crosstab(d[d.hh == 2].nrch, d[d.hh == 2].ki17))
lone = d[(d.hh == 2) & (d.ki17 == 2) & (d.marit != 1)]
couple = d[(d.hh == 2) & (d.ki17 == 1) & (d.marit == 1)]
other = d[(d.hh == 2) & (d.ki17 == 1) & (d.marit != 1)]
def rate(x, o): return float(np.average(x[o], weights=x.wt))
def matched(a, b, cells, o):
    """b reweighted to a's cells: (a's rate, b's rate as if b had a's mix, cover of a)"""
    wa = a.groupby(cells).wt.sum()
    ra = a.groupby(cells).apply(lambda g: rate(g, o), include_groups=False)
    rb = b.groupby(cells).apply(lambda g: rate(g, o), include_groups=False)
    c = ra.index.intersection(rb.index)
    sh = wa.loc[c] / wa.loc[c].sum()
    return float((sh * ra.loc[c]).sum()), float((sh * rb.loc[c]).sum()), float(wa.loc[c].sum() / wa.sum())
for nm, x in (('lone parent + 1 child', lone), ('married couple, no child', couple), ('unmarried, 2 adults, no child', other)):
    print(f'{nm:30s} n {len(x):5d}  women {100*rate(x.assign(f=(x.sex==2).astype(float)), "f"):4.0f}%  '
          f'past month {100*rate(x,"illmon"):5.1f}%  past year {100*rate(x,"illyr"):5.1f}%  disorder {100*rate(x,"sud"):5.1f}%')
for o in ('illmon', 'illyr', 'sud'):
    print(f'\n{o}:')
    for cname, comp in (('married couple', couple), ('unmarried 2 adults', other)):
        for cells in (['age3', 'sex', 'pinc'], ['age3', 'sex', 'finc'], ['age3', 'sex', 'pinc', 'finc']):
            a, b, cov = matched(lone, comp, cells, o)
            b2, a2, cov2 = matched(comp, lone, cells, o)
            print(f'  vs {cname:18s} on {"+".join(cells):18s}: lone parents {100*a:5.1f} vs {100*b:5.1f} '
                  f'(non-parents use {100*(b/a-1):+6.1f}%, cover {100*cov:.0f}%)  |  other way: {100*a2:5.1f} vs {100*b2:5.1f} '
                  f'({100*(b2/a2-1):+6.1f}%, cover {100*cov2:.0f}%)')

print('\nunmarried on both sides, also matched on marital status (never married, divorced or separated, widowed):')
for o in ('illmon', 'illyr', 'sud'):
    for cells in (['age3', 'sex', 'marit', 'pinc'], ['age3', 'sex', 'marit', 'finc']):
        a, b, cov = matched(lone, other, cells, o)
        b2, a2, cov2 = matched(other, lone, cells, o)
        print(f'  {o:6s} on {"+".join(cells):20s}: lone parents {100*a:5.1f} vs {100*b:5.1f} ({100*(b/a-1):+6.1f}%, cover {100*cov:.0f}%)'
              f'  |  other way: {100*a2:5.1f} vs {100*b2:5.1f} ({100*(b2/a2-1):+6.1f}%, cover {100*cov2:.0f}%)')

# THE NUMBERS THE PAPER QUOTES (Section 5, the omega_c item): past-month use, personal or family income, each weighting
def _gaps(comp, extra):
    out = []
    for inc in ('pinc', 'finc'):
        cells = ['age3', 'sex'] + extra + [inc]
        a, b, _ = matched(lone, comp, cells, 'illmon')
        out.append(100 * (b / a - 1))
        b2, a2, _ = matched(comp, lone, cells, 'illmon')
        out.append(100 * (b2 / a2 - 1))
    return out
unm, mar = _gaps(other, ['marit']), _gaps(couple, [])
# THE MOMENT THAT IDENTIFIES omega_c (the author, 8 October: "unmarried two person household vs lone parent with child,
# that identifies omegac exactly"): family income held equal, which with two people in each household is income per
# person, and lone parents reweighted to the non-parents' cells, the convention of make_altruism_moment.py
# PAST-YEAR USE (the author, 8 October: "use the past year use....17.5% that is good enough", "and it's exact too"):
# the model's period is a year, and past-month use gave 19.5. On any drug use disorder, the model's participation
# definition, the gap is 59 with only 76 lone parents who have one; not used.
cells_id = ['age3', 'sex', 'marit', 'finc']
b2, a2, cov_id = matched(other, lone, cells_id, 'illyr')
ident = b2 / a2 - 1
for _o in ('illmon', 'illyr', 'sud'):
    _b, _a, _ = matched(other, lone, cells_id, _o)
    print(f'  identifying cells, {_o}: {100*(_b/_a-1):+.1f}%')
print(f'IDENTIFYING MOMENT (past-year use): unmarried two-adult households use {100*ident:.2f}% more than lone parents (cover {100*cov_id:.0f}%)')
res = {'nsduh_lp_id_value': f'{ident:.4f}', 'nsduh_lp_id_pc': f'{100 * ident:.1f}',
       'nsduh_lp_unm_lo_pc': f'{min(unm):.0f}', 'nsduh_lp_unm_hi_pc': f'{max(unm):.0f}',
       'nsduh_lp_mar_lo': f'{min(mar):.0f}', 'nsduh_lp_mar_hi': f'{max(mar):.0f}', 'nsduh_lp_n': f'{len(lone):,}'}
json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
print('wrote', OUT, res)
