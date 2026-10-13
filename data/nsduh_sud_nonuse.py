"""nsduh_sud_nonuse.py -- how many adults with a SUD did not use in the past month, and in the past year (NSDUH 2024).

The question (the author, 13 Oct): the model has about 4.5 per cent of households with a SUD spending nothing on the drug
under Housing First, at a budget corner; does that line up with the data? SUD is the model's: a moderate or severe drug
use disorder (SVYRDUDANY 2 or 3), adults 26 and over (AGE3 7-11), weighted by ANALWT2_C. ILLMON and ILLYR are any illicit
drug use in the past month and past year; POVERTY3 is income relative to the poverty line.

Result (13 Oct): no illicit use in the past month 16.5 per cent (below poverty 17.2, 100-199% 20.5, 200%+ 13.9); in the
past year 5.2 per cent. The model's period is a year, so its 4.5 per cent sits between the two; but in the model the
zeros are concentrated among the poorest, while in the data they are not concentrated by income.
"""
import os, zipfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
Z = os.path.join(HERE, 'raw', 'NSDUH_2024_public_use_file_tab_delimited.zip')
with zipfile.ZipFile(Z) as z:
    name = z.namelist()[0]
    head = z.open(name).readline().decode('latin-1').rstrip('\r\n').split('\t')
    clean = [h.replace('+AF8-', '_').upper() for h in head]
    want = ['ANALWT2_C', 'AGE3', 'SVYRDUDANY', 'ILLYR', 'ILLMON', 'POVERTY3']
    idx = [clean.index(x) for x in want]
    d = pd.read_csv(z.open(name), sep='\t', usecols=idx, dtype=str, encoding='latin-1')
d.columns = [clean[i] for i in sorted(idx)]
for c in d.columns:
    d[c] = pd.to_numeric(d[c], errors='coerce')
w = d.ANALWT2_C
base = d.AGE3.isin([7, 8, 9, 10, 11]) & d.SVYRDUDANY.isin([2, 3])


def share(var, mask=True):
    m = base & mask
    return 100 * w[m & (d[var] == 0)].sum() / w[m].sum(), int(m.sum())


print('adults 26+ with a moderate or severe drug use disorder:')
print('  no illicit use in the past month: %.1f%% (n=%d)' % share('ILLMON'))
for k, lab in ((1, 'below poverty'), (2, '100-199% of poverty'), (3, '200%+ of poverty')):
    print('    %s: %.1f%% (n=%d)' % ((lab,) + share('ILLMON', d.POVERTY3 == k)))
print('  no illicit use in the past year: %.1f%% (n=%d)' % share('ILLYR'))
