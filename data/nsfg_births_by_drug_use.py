"""
Do women who use drugs have as many children as women who do not? Children EVER BORN, not
children at home (the author, 30 September: "im not after the child living in the household,
but having a child at all for drug users").

NSFG 2017-2019 female respondent file (data/raw/NSFG_2017_2019_FemRespData.dat, layout read
from NSFG_2017_2019_FemRespSetup.sas), women aged 15-49, weighted by WGT2017_2019.

  PARITY      live births, multiple births counted
  HASBABES    any live birth (1 yes, 5 no)
  NUMKDHH     own, adopted, related or legal children under 18 in the household
  POT12       marijuana in the last 12 months, 1 never ... 6 daily
  COC12, CRACK12, CRYSTMTH12, INJECT12
              cocaine, crack, crystal/meth, injecting, last 12 months, 1 never ... 4 monthly+
  EVRINJECT   ever injected a non-prescription drug (1 yes, 5 no)

NSFG has no measure of a use disorder, so the heavier group is frequent use: marijuana weekly
or more, or any of the four harder drugs several times a year or more.

usage: python3 data/nsfg_births_by_drug_use.py  -> prints the tables and writes
       code/paper/nsfg_births.json
"""
import json, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DAT = os.path.join(HERE, 'raw', 'NSFG_2017_2019_FemRespData.dat')
SAS = os.path.join(HERE, 'raw', 'NSFG_2017_2019_FemRespSetup.sas')
OUT = os.path.join(HERE, '..', 'code', 'paper', 'nsfg_births.json')

sas = open(SAS, encoding='latin-1').read()
i = sas.find('\nINPUT\n'); j = sas.find(';', i)
pos = {m.group(1): (int(m.group(2)), int(m.group(3) or m.group(2)))
       for m in re.finditer(r'(\w+)\s+\$?\s*(\d+)(?:\s*-\s*(\d+))?', sas[i + 7:j])}
WANT = ['AGER', 'PARITY', 'HASBABES', 'NUMKDHH', 'POT12', 'COC12', 'CRACK12', 'CRYSTMTH12',
        'INJECT12', 'EVRINJECT', 'WGT2017_2019']
d = pd.read_fwf(DAT, colspecs=[(pos[k][0] - 1, pos[k][1]) for k in WANT], names=WANT, header=None)
d = d.apply(pd.to_numeric, errors='coerce')
assert len(d) > 6000, len(d)
HARD = ['COC12', 'CRACK12', 'CRYSTMTH12', 'INJECT12']
ok = d.POT12.between(1, 6) & d[HARD].apply(lambda c: c.between(1, 4)).all(axis=1)
d = d[ok & d.PARITY.between(0, 30)].copy()
d['hard'] = d[HARD].apply(lambda c: c.between(2, 4)).any(axis=1)
d['use'] = d.hard | d.POT12.between(2, 6)
d['heavy'] = d.POT12.between(5, 6) | d[HARD].apply(lambda c: c.between(3, 4)).any(axis=1)
d['inj'] = d.EVRINJECT == 1


def w(x, v):
    return (x.WGT2017_2019 * v).sum() / x.WGT2017_2019.sum()


GROUPS = [('no drug use in the last year', ~d.use), ('any drug use, marijuana included', d.use),
          ('a harder drug (cocaine, crack, meth, injecting)', d.hard),
          ('frequent use', d.heavy), ('ever injected', d.inj)]
out = {}
for lo, hi, tag in ((40, 49, '4049'), (35, 49, '3549'), (26, 49, '2649')):
    x = d[d.AGER.between(lo, hi)]
    print(f'\nNSFG 2017-2019, women {lo}-{hi}, n = {len(x)}')
    print(f'{"group":48s} {"n":>5s} {"births":>7s} {"any birth":>10s} {"own kids <18 at home":>21s}')
    for g, m in GROUPS:
        m = m.reindex(x.index)
        y = x[m]
        b, a, k = w(y, y.PARITY), w(y, y.PARITY > 0), w(y, y.NUMKDHH.clip(upper=9))
        print(f'{g:48s} {len(y):5d} {b:7.2f} {100 * a:9.1f}% {k:21.2f}')
        key = {'no drug use in the last year': 'nouse', 'any drug use, marijuana included': 'use',
               'a harder drug (cocaine, crack, meth, injecting)': 'hard', 'frequent use': 'heavy',
               'ever injected': 'inj'}[g]
        out[f'nsfg_births_{key}_{tag}'] = f'{b:.2f}'
        out[f'nsfg_anybirth_{key}_{tag}_pc'] = f'{100 * a:.0f}'
        out[f'nsfg_n_{key}_{tag}'] = str(len(y))
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print('\nwrote', OUT)
