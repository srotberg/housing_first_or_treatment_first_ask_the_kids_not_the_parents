"""What the 2022 SCF says about young households with negative assets.

Asked by the author, 3 September: *"can you check in the s[c]f what fraction of
newborns have negative assets around 25-27 years of age, and how much debt they
have? I think we can give the bottom of the productivity distribution those
negative assets as in the data if we need to"*.

THE MEASURE. Non-housing net worth, networth - (houses - mrthel), because the
model's financial grid is non-housing wealth and the newborn holds no house.
The first measure tried here was fin - debt and it is WRONG: it charges mortgage
debt against a house that sits in nfin, and it reports 48 per cent of 25-27 year
olds as negative against the 13 per cent that is actually there.

THE DENOMINATOR is average WAGE income over all households, $83,340, because
newborn_endowment_scale multiplies model_average_labour_income.  Average total
income is $141,390 and using it would understate every figure by 41 per cent.

CELL SIZES ARE SMALL: 126 households at 25-27.  The top quintile's 0.0 per cent
negative is a small-cell artefact and Q3's -1.217 rests on a few large student
loan cases.  SCF age is the HEAD's age, so young adults living with their parents
are not separate households and the poorest young are under-covered.
"""
import pandas as pd, numpy as np, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_stata(os.path.join(HERE, 'SCF_2022.dta'), convert_categoricals=False)
d['w'] = d['wgt'] / 5.0                       # five implicates
d['nonhousing_nw'] = d['networth'] - (d['houses'] - d['mrthel'])
awi = np.average(d['wageinc'], weights=d['w'])


def wshare(df, m):
    return df.loc[m, 'w'].sum() / df['w'].sum()


def wmean(df, c, m=None):
    x = df if m is None else df[m]
    return np.average(x[c], weights=x['w'])


def wq(df, c, q):
    x = df.sort_values(c)
    cc = x['w'].cumsum() / x['w'].sum()
    return float(np.interp(q, cc, x[c]))


print(f'average wage income, all households = ${awi:,.0f}  (the denominator)')
a = d[(d['age'] >= 25) & (d['age'] <= 27)].copy()
neg = a['nonhousing_nw'] < 0
print(f'\nage 25-27, {len(a)//5} households, units of average wage income')
print(f'  share with negative non-housing net worth  {100*wshare(a, neg):.1f}%')
print(f'  mean if negative                           {wmean(a, "nonhousing_nw", neg)/awi:+.3f}')
print(f'  median if negative                         {wq(a[neg], "nonhousing_nw", 0.5)/awi:+.3f}')
print(f'  UNCONDITIONAL mean over all 25-27          {wmean(a, "nonhousing_nw")/awi:+.3f}')
print('\n  the unconditional column is the one that matters: the model gives one')
print('  endowment per productivity node, so it can only move a MEAN, and every')
print('  quintile mean including the bottom is POSITIVE.  The debt is real but it')
print('  lives in the dispersion, which a single number per node cannot carry.')

a = a.sort_values('income')
c = a['w'].cumsum() / a['w'].sum()
a['qi'] = np.searchsorted([0.2, 0.4, 0.6, 0.8], c, side='left')
print(f'\n  {"quintile":10s}{"mean income":>13}{"% negative":>12}{"mean if neg":>14}{"uncond mean":>14}')
for q in range(5):
    g = a[a['qi'] == q]
    if len(g) < 5:
        continue
    ng = g['nonhousing_nw'] < 0
    mi = wmean(g, 'nonhousing_nw', ng) / awi if ng.any() else float('nan')
    print(f'  {"Q"+str(q+1):10s}{wmean(g, "income"):>13,.0f}{100*wshare(g, ng):>11.1f}%'
          f'{mi:>14.3f}{wmean(g, "nonhousing_nw")/awi:>14.3f}')
