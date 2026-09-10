"""
Clawback sweep, using the PAPER'S OWN accounting (children.verdict): priv and
per_case are both mass-weighted means of node-by-node CEVs, so their ratio is
like for like, and gain = dsud * per_case.
"""
import json, sys
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats
from welfare import cev
from children import child_grid, shifted, DEL_D

WW = W / W.sum()
base = with_(P(), **json.load(open('calibrated.json')))
GRID = [0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.45, 0.50, 0.60, 0.70, 0.85, 1.00]


def sweep(pV, lab):
    v1h, _ = child_grid(base, 'HF', pV)
    ly = np.log(YG)
    v_pen = np.interp(ly + np.log(1.0 - DEL_D), ly, v1h, left=v1h[0], right=v1h[-1])
    per_case = float((WW * cev(base, v1h - v_pen)).sum())
    dlt = shifted(v1h, 0.0) - shifted(v1h, DEL_D)
    sh = stats(with_(base, pV=pV, policy='HF'))
    print(f'\n{"="*78}\n{lab}: pi_V = {pV:.3f}\n{"="*78}')
    print(f'   per-case value to the child = {100*per_case:.2f}%  '
          f'(income-only bound {100*(1/(1-DEL_D)-1):.2f}%)   DELTA = {dlt:.6f}')
    print('\n   -- the excess: internalising the child under Housing First, b held --')
    ex = {}
    for w in (0.0, 1.0):
        m = stats(with_(base, omega=w, chdmg=dlt, policy='HF', pV=pV))
        ex[w] = (100*m['part'], 100*m['sud'])
        print(f'      omega={w:.2f}   use {100*m["part"]:8.4f}%   disorder {100*m["sud"]:8.4f}%')
    print(f'      EXCESS = {ex[0.0][0]-ex[1.0][0]:.4f} pp use, '
          f'{ex[0.0][1]-ex[1.0][1]:.4f} pp disorder')
    print(f'\n   {"clawback":>9s}{"kappa_c":>9s}{"use":>10s}{"disorder":>11s}'
          f'{"private":>10s}{"extern":>10s}{"TOTAL":>10s}')
    rows = []
    for kc in GRID:
        q = with_(base, kappa_c=kc)
        v1c, _ = child_grid(q, 'TF', pV)
        priv = float((WW * cev(base, v1h - v1c)).sum())
        m = stats(with_(q, pV=pV, policy='TF'))
        gain = (sh['sud'] - m['sud']) * per_case
        rows.append((kc, 100*m['part'], 100*m['sud'], 100*priv, 100*gain,
                     100*(gain-priv)))
        print(f'   {100*(kc-0.30):8.0f}pp{kc:9.2f}{100*m["part"]:9.4f}%'
              f'{100*m["sud"]:10.4f}%{100*priv:9.4f}%{100*gain:9.4f}%'
              f'{100*(gain-priv):9.4f}%')
    b = max(rows, key=lambda r: r[5])
    print(f'\n   OPTIMUM kappa_c = {b[0]:.2f} ({100*(b[0]-0.30):.0f}pp)  '
          f'TOTAL {b[5]:.4f}%   use left {b[1]:.4f}%   '
          f'social optimum use {ex[1.0][0]:.4f}%')
    return rows


sweep(1.0, 'UNIVERSAL')
sweep(base.pV, 'RATIONED')
