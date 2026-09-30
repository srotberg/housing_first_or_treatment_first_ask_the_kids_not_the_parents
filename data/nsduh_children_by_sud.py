"""
Do adults with a drug use disorder have as many children at home as adults without one?
NSDUH 2024 public-use file, respondents aged 26 to 49 (AGE3 7-9, the years a child is at home
in the model), weighted by ANALWT2_C.

  NRCH17_2   the respondent's OWN children under 18 in the household, 0, 1, 2, 3 = 3 or more
  SVYRDUDANY drug use disorder severity among past-year users: 1 mild, 2 moderate, 3 severe
             (the model's participation is any severity, its SUD moderate or severe)
  ILLYR      any illicit drug use in the past year

usage: python3 data/nsduh_children_by_sud.py   -> prints the table and writes
       code/paper/nsduh_children.json (names the paper quotes)
"""
import json, os, zipfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
Z = os.path.join(HERE, 'raw', 'NSDUH_2024_public_use_file_tab_delimited.zip')
OUT = os.path.join(HERE, '..', 'code', 'paper', 'nsduh_children.json')
with zipfile.ZipFile(Z) as z:
    name = z.namelist()[0]
    head = z.open(name).readline().decode('latin-1').rstrip('\r\n').split('\t')
    clean = [h.replace('+AF8-', '_').upper() for h in head]
    want = ['ANALWT2_C', 'AGE3', 'NRCH17_2', 'SVYRDUDANY', 'ILLYR']
    idx = [clean.index(w) for w in want]
    d = pd.read_csv(z.open(name), sep='\t', usecols=idx, dtype=str, encoding='latin-1')
d.columns = [clean[i] for i in sorted(idx)]
for c in d.columns:
    d[c] = pd.to_numeric(d[c], errors='coerce')
d = d[d.AGE3.isin([7, 8, 9]) & d.NRCH17_2.between(0, 3)]
w = d.ANALWT2_C
groups = {
    'no drug use disorder': ~d.SVYRDUDANY.isin([1, 2, 3]),
    'drug use disorder, any severity': d.SVYRDUDANY.isin([1, 2, 3]),
    'moderate or severe (SUD)': d.SVYRDUDANY.isin([2, 3]),
    'no illicit use in the past year': d.ILLYR == 0,
    'illicit use in the past year': d.ILLYR == 1,
}
rows = {}
print(f'NSDUH 2024, ages 26-49, n = {len(d)}')
print(f'{"group":36s} {"n":>6s} {"mean own children <18":>22s} {"share with any":>15s}')
for g, m in groups.items():
    ww = w[m]; k = d.NRCH17_2[m]
    mean = (ww * k).sum() / ww.sum(); anyc = (ww * (k > 0)).sum() / ww.sum()
    rows[g] = (int(m.sum()), mean, anyc)
    print(f'{g:36s} {m.sum():6d} {mean:22.2f} {100 * anyc:14.1f}%')
out = {
    'n_kids_nodud': f"{rows['no drug use disorder'][1]:.2f}",
    'n_kids_dud': f"{rows['drug use disorder, any severity'][1]:.2f}",
    'n_kids_sud': f"{rows['moderate or severe (SUD)'][1]:.2f}",
    'n_kids_nouse': f"{rows['no illicit use in the past year'][1]:.2f}",
    'n_kids_use': f"{rows['illicit use in the past year'][1]:.2f}",
}
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(out)
