"""Drug use among food-stamp recipients, NSDUH 2024, as a stand-in for voucher holders (the author, 8 October: "let's use
food stamps as a proxy"; NSDUH 2024 has no housing-assistance variable, only IRFSTAMP, GOVTPROG and the like). Adults 26
and over (AGE3 7-11, the model's adults), weighted by ANALWT2_C. Use is the model's: any drug use disorder (SVYRDUDANY
1-3, what b is calibrated to); also moderate or severe (2-3, the model's SUD) and any illicit use in the past year
(ILLYR). Groups: everyone; someone in the family received food stamps in the past year (IRFSTAMP 1) or not (2); and
below twice the poverty line (POVERTY3 1-2), the low-income comparison, with and without food stamps.
usage: python3 data/make_use_by_food_stamps.py NSDUH_2024_Tab.csv  -> code/paper/nsduh_snap_use.json"""
import json, os, sys
import pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'paper', 'nsduh_snap_use.json')
F = sys.argv[1]
hdr = open(F).readline().rstrip('\n').split('\t')
clean = [h.replace('+AF8-', '_').upper() for h in hdr]
want = ['ANALWT2_C', 'AGE3', 'SVYRDUDANY', 'ILLYR', 'IRFSTAMP', 'POVERTY3']
idx = [clean.index(w) for w in want]
d = pd.read_csv(F, sep='\t', usecols=idx, dtype=str)
d.columns = [clean[i] for i in sorted(idx)]
d = d.apply(pd.to_numeric, errors='coerce')
x = d[d.AGE3.isin([7, 8, 9, 10, 11])]
w = x.ANALWT2_C
def rate(mask, ind):
    return 100 * (w[mask] * ind[mask]).sum() / w[mask].sum()
dud, sud, ill = x.SVYRDUDANY.isin([1, 2, 3]).astype(float), x.SVYRDUDANY.isin([2, 3]).astype(float), (x.ILLYR == 1).astype(float)
snap, nosnap, low = x.IRFSTAMP == 1, x.IRFSTAMP == 2, x.POVERTY3.isin([1, 2])
groups = {'all': x.AGE3 > 0, 'snap': snap, 'nosnap': nosnap, 'low': low, 'low_snap': low & snap, 'low_nosnap': low & nosnap}
out = {}
for g, m in groups.items():
    out[f'nsduh_{g}_dud_pc'] = f'{rate(m, dud):.1f}'
    out[f'nsduh_{g}_sud_pc'] = f'{rate(m, sud):.1f}'
    out[f'nsduh_{g}_ill_pc'] = f'{rate(m, ill):.1f}'
    out[f'_nsduh_{g}_share_pc'] = f'{100 * w[m].sum() / w.sum():.1f}'
    out[f'_nsduh_{g}_n'] = int(m.sum())
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
for g in groups:
    print(f"{g:11s} share {out[f'_nsduh_{g}_share_pc']:>5s}%  n {out[f'_nsduh_{g}_n']:6d}   any disorder {out[f'nsduh_{g}_dud_pc']:>5s}%"
          f"   moderate/severe {out[f'nsduh_{g}_sud_pc']:>5s}%   past-year use {out[f'nsduh_{g}_ill_pc']:>5s}%")
