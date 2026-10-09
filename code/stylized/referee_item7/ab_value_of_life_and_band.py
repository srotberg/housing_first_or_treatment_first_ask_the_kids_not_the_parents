"""Referee item 7, claims A and B, on the model the paper's Section 3 actually reports:
code/stylized/gradient.py at code/stylized/gradient.json (fill.py reads gradient_numbers.json, the g_* names).
Read-only: nothing in the model is changed.

usage: python3 code/stylized/referee_item7/ab_value_of_life_and_band.py
"""
import json, os, sys
import numpy as np
from scipy.special import ndtr, ndtri

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gradient as G  # noqa: E402

q = json.load(open(os.path.join(os.path.dirname(HERE), 'gradient.json')))
m = G.moments(q)
dist = m['dist']
N = 400000
p = (np.arange(N) + 0.5) / N                       # equal-mass percentile nodes of the truncated lognormal
y = np.exp(dist.s * ndtri(dist.Ft + p * (1 - dist.Ft)) - 0.5 * dist.s ** 2) / dist.M
assert abs(y.mean() - 1) < 1e-3 and abs(y.min() / q['y_min'] - 1) < 1e-3, (y.mean(), y.min())

au, Vu = G.plan(y, q, True)
an, Vn = G.plan(y, q, False)
use = Vu > Vn
V1 = np.where(use, Vu, Vn)
a = np.where(use, au, an)
f = G.FA(y, q)
pi, pf, k = q['pi_d'], q['phibar'], q['kappa']

print('=== CALIBRATION CHECK (gradient.json) ===')
print({kk: round(m[kk], 6) for kk in ('part', 'r_use', 'dshare', 'vsl', 'fshare')}, 'band', m['intervals'])
print('grid participation', use.mean(), ' users mean income', y[use].mean())

print('\n=== A. VALUE OF LIFE ===')
# period 1: lifetime value at the drug decision (death before it = 0), and the period-1 flow U + aleph
flow1 = np.where(use, G._U1(y - a + f, q), G._U0(y - a + f, q)) + q['aleph']
print(f'period 1, V1 (lifetime value): share < 0 = {np.mean(V1 < 0):.6f}, min {V1.min():.4f} at y={y[np.argmin(V1)]:.4f}')
print(f'period 1, flow U+aleph:        share < 0 = {np.mean(flow1 < 0):.6f}, min {flow1.min():.4f}')
# period 2: each household's realised states, weighted by survival
rows = []  # (weight, W, flow, d, e, y)
s_clean = np.where(use, (1 - pi) * pf, pf)
s_sud = np.where(use, pi * pf ** k, 0.0)
for d, sw in ((0, s_clean), (1, s_sud)):
    u = q['u1'] if d else q['u0']
    Wd = G.W(a, y, q, d)
    fe = G._U0(y + a + f, q) + q['aleph']            # employed
    fu = G._U0(a + q['cbar'], q) + q['aleph']        # out of work
    rows.append((sw, Wd, fe, fu, u, d))
tot = sum(r[0].sum() for r in rows)
negW = sum((r[0] * (r[1] < 0)).sum() for r in rows) / tot
negF = sum((r[0] * ((1 - r[4]) * (r[2] < 0) + r[4] * (r[3] < 0))).sum() for r in rows) / tot
negFu = sum((r[0] * r[4] * (r[3] < 0)).sum() for r in rows) / tot
print(f'period 2, W(a,y,d) (value at the start of period 2, before the employment draw):'
      f' survivor-weighted share < 0 = {negW:.6f}')
for sw, Wd, fe, fu, u, d in rows:
    bad = (Wd < 0) & (sw > 0)
    if bad.any():
        print(f'   d={d}: negative W at y in [{y[bad].min():.4f}, {y[bad].max():.4f}], '
              f'percentiles [{100*p[bad].min():.2f}, {100*p[bad].max():.2f}], min W {Wd[bad].min():.4f}, '
              f'savings there {a[bad].min():.4f}-{a[bad].max():.4f}')
print(f'period 2, realised flow U+aleph (after the employment draw): survivor-weighted share < 0 = {negF:.6f}'
      f'  (of which out of work: {negFu:.6f})')
for sw, Wd, fe, fu, u, d in rows:
    for lab, fl, pr in (('employed', fe, 1 - u), ('out of work', fu, u)):
        bad = (fl < 0) & (sw > 0)
        if bad.any():
            print(f'   d={d} {lab}: negative at y in [{y[bad].min():.4f}, {y[bad].max():.4f}] '
                  f'(percentiles {100*p[bad].min():.2f}-{100*p[bad].max():.2f}); '
                  f'share of survivors {(sw*pr*bad).sum()/tot:.6f}; min {fl[bad].min():.4f}')
print(f'y_zero (consumption at which U+aleph = 0): {G.y_zero(q):.4f}; cbar = {q["cbar"]:.4f}; y_min = {q["y_min"]}')
print(f'share of ALL households alive at the start of period 1 who reach period 2 in a negative W state: '
      f'{sum((r[0]*(r[1]<0)).sum() for r in rows)/N:.6f}')

print('\n=== B. WHERE USERS SIT ===')
med = dist.quantile(0.5)
print(f'population median income / mean = {med:.4f}')
for lo, hi in m['intervals']:
    print(f'use band y in [{lo:.4f}, {hi:.4f}] = percentiles [{100*float(dist.F(lo)):.2f}, {100*float(dist.F(hi)):.2f}]')
yu = y[use]
print(f'users mean income / population mean = {yu.mean():.4f} (moments(): {m["r_use"]:.4f})')
print(f'users median income / mean = {np.median(yu):.4f}, percentile of the mean user income {100*float(dist.F(yu.mean())):.2f}')
print(f'income at the 52nd and 60th percentiles: {dist.quantile(0.52):.4f}, {dist.quantile(0.60):.4f}')
print(f'share of the income distribution truncated below y_min: {100*dist.cut_share:.2f}% of the raw lognormal')
