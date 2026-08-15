"""
The note's tables, written straight to LaTeX so they can never drift from the
code. Run:  python3 tables.py

    tab_channels.tex   who uses, as each channel is scaled up
    tab_policy.tex     the two policy forces
"""

import json
import os
import numpy as np
from stylized import P, with_
from calibrate import bracket, stats
from run import _scaled

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'tables'))
os.makedirs(OUT, exist_ok=True)


def write(name, body):
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(body)
    print(f'   wrote {name}')


def tab_channels(base):
    """b and the income ratio, both channels, at five strengths."""
    sc = [0.0, 0.25, 0.50, 0.75, 1.0]
    rows = []
    for s in sc:
        cells = []
        for which in ('mortality', 'unemployment'):
            par = _scaled(base, which, s)
            cells += [par.b, stats(par)['r_use']]
        rows.append((s, *cells))
        print(f'   s={s:.2f}  mort b={cells[0]:.4f} r={cells[1]:.3f}   '
              f'unemp b={cells[2]:.4f} r={cells[3]:.3f}')

    L = [r'\begin{tabular}{@{}rcccc@{}}', r'\toprule',
         r'& \multicolumn{2}{c}{Mortality channel}'
         r' & \multicolumn{2}{c}{Unemployment channel} \\',
         r'\cmidrule(lr){2-3}\cmidrule(lr){4-5}',
         r'Strength of the channel & $b$ & $\bar y_u/\bar y$'
         r' & $b$ & $\bar y_u/\bar y$ \\', r'\midrule']
    for s, b1, r1, b2, r2 in rows:
        L.append(f'{100*s:.0f}\\% & {b1:.4f} & {r1:.2f} '
                 f'& {b2:.4f} & {r2:.2f} \\\\')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_channels.tex', '\n'.join(L) + '\n')
    return rows


def tab_policy(base):
    """No programme, universal Treatment First, universal Housing First."""
    p0 = 100 * stats(with_(base, pV=0.0, policy='HF'))['part']
    pt = 100 * stats(with_(base, pV=1.0, policy='TF'))['part']
    ph = 100 * stats(with_(base, pV=1.0, policy='HF'))['part']
    print(f'   none {p0:.2f}   TF {pt:.2f}   HF {ph:.2f}')

    L = [r'\begin{tabular}{@{}lcc@{}}', r'\toprule',
         r'& Participation rate & Difference \\',
         r'\midrule',
         r'\multicolumn{3}{@{}l}{\emph{Panel A. Drug use under each policy}} \\',
         f'\\quad No voucher programme ($\\pi_V=0$) & {p0:.2f}\\% & \\\\',
         f'\\quad Universal Treatment First ($\\pi_V=1$) & {pt:.2f}\\% & \\\\',
         f'\\quad Universal Housing First ($\\pi_V=1$) & {ph:.2f}\\% & \\\\',
         r'\addlinespace',
         r'\multicolumn{3}{@{}l}{\emph{Panel B. The two forces}} \\',
         r'\quad Value of life\quad(Treatment First $-$ no programme)'
         f' & & ${pt-p0:+.2f}$ pp \\\\',
         r'\quad Moral hazard\quad(Housing First $-$ Treatment First)'
         f' & & ${ph-pt:+.2f}$ pp \\\\',
         r'\addlinespace',
         r'\quad Net effect of Housing First\quad(Housing First $-$ no programme)'
         f' & & ${ph-p0:+.2f}$ pp \\\\',
         r'\bottomrule', r'\end{tabular}']
    write('tab_policy.tex', '\n'.join(L) + '\n')
    return p0, pt, ph


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('tables')
    tab_channels(base)
    tab_policy(base)
