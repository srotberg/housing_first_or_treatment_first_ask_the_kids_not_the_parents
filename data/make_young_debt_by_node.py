"""Young households with negative assets, bracketed on the MODEL's productivity grid.

The author, 3 September: *"for each income bracket, look at the fraction of 25-27
year olds with debt and compute what that debt is and show me a table of the
fraction by income and the debt conditional on having debt.  Make the income
consistent with the productivity grid when you analyze the data"*.

THE BRACKETS ARE THE MODEL'S OWN.  The Fortran cuts the productivity CDF at
p_edge(i) = ((i-1)/7)**y_grid_kappa with y_grid_kappa=3.2 (line 28316), so the
node masses are 0.20, 1.62, 4.83, 10.04, 17.39, 26.99 and 38.94 per cent.  A
newborn's node is a draw from that stationary distribution, so within a single
birth cohort the node shares ARE those masses -- which is why households are
ranked WITHIN the age band here rather than against the whole population.

WHY TOTAL INCOME AND NOT WAGE INCOME.  Ranking on wageinc puts every zero-earner
at the bottom and the bottom three nodes then have mean wage income of exactly
zero, so the assignment among the tied zeros is arbitrary.  The model has ~100 per
cent participation and no zero-earners, so total income is the closer analogue.
The wage-income ranking is printed underneath as a cross-check.

CELL SIZES DECIDE WHAT IS READABLE.  Node 1 is 0.20 per cent of the distribution,
which is a QUARTER OF ONE HOUSEHOLD in the 126-household 25-27 cell, and node 2 is
two.  Nothing about nodes 1-2 can be read at 25-27 and little at 25-34.  N is
printed on every row for that reason; rows with N below about 20 are indicative
at best.

The measure is non-housing net worth, networth - (houses - mrthel), because the
model's financial grid is non-housing wealth.  The denominator is average WAGE
income over all households because newborn_endowment_scale multiplies
model_average_labour_income.
"""
import pandas as pd, numpy as np, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_stata(os.path.join(HERE, 'SCF_2022.dta'), convert_categoricals=False)
d['w'] = d['wgt'] / 5.0
d['nonhousing_nw'] = d['networth'] - (d['houses'] - d['mrthel'])
AWI = np.average(d['wageinc'], weights=d['w'])
N, KAPPA = 7, 3.2
EDGE = [(i / N) ** KAPPA for i in range(N + 1)]
EDGE[0], EDGE[-1] = 0.0, 1.0


def wsh(df, m):
    return df.loc[m, 'w'].sum() / df['w'].sum() if df['w'].sum() > 0 else np.nan


def wmn(df, c, m=None):
    x = df if m is None else df[m]
    return np.average(x[c], weights=x['w']) if len(x) and x['w'].sum() > 0 else np.nan


def wqt(df, c, q):
    if len(df) == 0:
        return np.nan
    x = df.sort_values(c)
    cc = x['w'].cumsum() / x['w'].sum()
    return float(np.interp(q, cc, x[c]))


def table(a, label, rank_col):
    a = a.sort_values(rank_col).copy()
    c = a['w'].cumsum() / a['w'].sum()
    a['node'] = np.clip(np.searchsorted(EDGE[1:-1], c, side='left') + 1, 1, N)
    print(f'\n=== {label} ===')
    print(f"{'node':>4}{'mass':>7}{'N':>5}{'mean inc':>11}{'% negative':>12}"
          f"{'mean if neg':>13}{'med if neg':>12}{'% any debt':>12}{'med debt':>10}")
    for i in range(1, N + 1):
        g = a[a['node'] == i]
        n_hh = len(g) // 5
        mass = f'{100*(EDGE[i]-EDGE[i-1]):.2f}%'
        if n_hh == 0:
            print(f'{i:>4}{mass:>7}{n_hh:>5}{"-- no observations --":>58}')
            continue
        ng = g['nonhousing_nw'] < 0
        ad = g['debt'] > 0
        mi = wmn(g, 'nonhousing_nw', ng) / AWI if ng.any() else np.nan
        md = wqt(g[ng], 'nonhousing_nw', 0.5) / AWI if ng.any() else np.nan
        gd = wqt(g[ad], 'debt', 0.5) / AWI if ad.any() else np.nan
        print(f'{i:>4}{mass:>7}{n_hh:>5}{wmn(g, "income"):>11,.0f}{100*wsh(g, ng):>11.1f}%'
              f'{mi:>13.3f}{md:>12.3f}{100*wsh(g, ad):>11.1f}%{gd:>10.3f}')


print(f'denominator: average wage income, all households = ${AWI:,.0f}')
print('net worth and debt columns are in units of that, matching newborn_endowment_scale')
print(f'node masses from ((i-1)/7)**3.2: '
      + ', '.join(f'{100*(EDGE[i]-EDGE[i-1]):.2f}%' for i in range(1, N + 1)))
for lo, hi in [(25, 27), (25, 29), (25, 34)]:
    a = d[(d['age'] >= lo) & (d['age'] <= hi)]
    table(a, f'age {lo}-{hi}, ranked on TOTAL income ({len(a)//5} households)', 'income')
print('\n\nCROSS-CHECK: the same brackets ranked on WAGE income.  The bottom nodes')
print('fill with zero-earners and their mean wage income is exactly zero, so the')
print('assignment among the ties is arbitrary -- this is why total income is used above.')
for lo, hi in [(25, 27), (25, 34)]:
    a = d[(d['age'] >= lo) & (d['age'] <= hi)]
    table(a, f'age {lo}-{hi}, ranked on WAGE income ({len(a)//5} households)', 'wageinc')
