"""
Do drug users have as many children as those who do not use? Children EVER BORN or ever
fathered, not children at home (the author, 30 September: "im not after the child living in
the household, but having a child at all for drug users"; "like on average across all users
not just females?").

NSFG 2017-2019 female and male respondent files (data/raw/NSFG_2017_2019_{FemResp,Male}Data.dat,
layouts read from the matching *Setup.sas), ages 15-49, weighted by WGT2017_2019. The weights
are population weights for each sex, so the two files pool by stacking them.

  PARITY      women: live births, multiple births counted
  BIOKIDS     men: biological children ever fathered
  NUMKDHH     own, adopted, related or legal children under 18 in the household
  POT12       marijuana in the last 12 months, 1 never ... 6 daily
  COC12, CRACK12, CRYSTMTH12, INJECT12
              cocaine, crack, crystal/meth, injecting, last 12 months, 1 never ... 4 monthly+

NSFG has no measure of a use disorder, so the heavier group is frequent use: marijuana weekly
or more, or any of the four harder drugs several times a year or more. Men under-report
children they have fathered, most for children they do not live with, which if anything
lowers the users' figure.

usage: python3 data/nsfg_births_by_drug_use.py  -> prints the tables and writes
       code/paper/nsfg_births.json
"""
import json, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
OUT = os.path.join(HERE, '..', 'code', 'paper', 'nsfg_births.json')
HARD = ['COC12', 'CRACK12', 'CRYSTMTH12', 'INJECT12']


def read(stem, kids):
    sas = open(os.path.join(RAW, f'NSFG_2017_2019_{stem}Setup.sas'), encoding='latin-1').read()
    i = sas.find('\nINPUT\n'); j = sas.find(';', i)
    pos = {m.group(1): (int(m.group(2)), int(m.group(3) or m.group(2)))
           for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s*-\s*(\d+))?', sas[i + 7:j])}
    want = ['AGER', kids, 'NUMKDHH', 'POT12'] + HARD + ['WGT2017_2019']
    d = pd.read_fwf(os.path.join(RAW, f'NSFG_2017_2019_{stem}Data.dat'),
                    colspecs=[(pos[k][0] - 1, pos[k][1]) for k in want], names=want, header=None)
    d = d.apply(pd.to_numeric, errors='coerce').rename(columns={kids: 'KIDS'})
    assert len(d) > 4000, len(d)
    ok = d.POT12.between(1, 6) & d[HARD].apply(lambda c: c.between(1, 4)).all(axis=1)
    d = d[ok & d.KIDS.between(0, 30)].copy()
    d['hard'] = d[HARD].apply(lambda c: c.between(2, 4)).any(axis=1)
    d['use'] = d.hard | d.POT12.between(2, 6)
    d['heavy'] = d.POT12.between(5, 6) | d[HARD].apply(lambda c: c.between(3, 4)).any(axis=1)
    return d


W, M = read('FemResp', 'PARITY'), read('Male', 'BIOKIDS')
SEXES = {'women': W, 'men': M, 'all': pd.concat([W, M], ignore_index=True)}
TAG = {'women': '', 'men': 'm_', 'all': 'all_'}


def w(x, v):
    return (x.WGT2017_2019 * v).sum() / x.WGT2017_2019.sum()


GROUPS = [('nouse', 'no drug use in the last year'), ('use', 'any drug use, marijuana included'),
          ('hard', 'a harder drug (cocaine, crack, meth, injecting)'), ('heavy', 'frequent use')]
out = {}
for sex, d in SEXES.items():
    for lo, hi, tag in ((40, 49, '4049'), (35, 49, '3549')):
        x = d[d.AGER.between(lo, hi)]
        print(f'\nNSFG 2017-2019, {sex} {lo}-{hi}, n = {len(x)}')
        print(f'{"group":48s} {"n":>5s} {"children":>9s} {"any child":>10s} {"own kids <18 at home":>21s}')
        for key, g in GROUPS:
            y = x[~x.use] if key == 'nouse' else x[x[key]]
            b, a, k = w(y, y.KIDS), w(y, y.KIDS > 0), w(y, y.NUMKDHH.clip(upper=9))
            print(f'{g:48s} {len(y):5d} {b:9.2f} {100 * a:9.1f}% {k:21.2f}')
            out[f'nsfg_{TAG[sex]}births_{key}_{tag}'] = f'{b:.2f}'
            out[f'nsfg_{TAG[sex]}anybirth_{key}_{tag}_pc'] = f'{100 * a:.0f}'
            out[f'nsfg_{TAG[sex]}n_{key}_{tag}'] = str(len(y))
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print('\nwrote', OUT)
