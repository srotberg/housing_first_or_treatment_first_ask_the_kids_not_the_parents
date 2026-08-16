"""
ROBUSTNESS: what if parents already care about the child?

The baseline treats the damage to the child as a pure externality: the parent
puts no weight on it at all. That is the assumption the whole reversal in
Section 6.2 rests on, so it deserves a check rather than an assertion.

THE EXPERIMENT

Give the parent a weight omega on the child's lifetime value. Since the only
thing the parent's choice of v does to the child is raise the probability that
the child is born to a household with the disorder, the extra term in the
parent's period 1 objective is

    - omega * pi(v) * DELTA,    DELTA = E[V1(y_base)] - E[V1(y_base(1-del_d))]

which is a deterrent rising in v. DELTA is the child's expected loss in lifetime
UTILITY from the income penalty, computed once at the baseline programme, and
held fixed across policies. Holding it fixed is a simplification: a full
treatment would be a fixed point across generations, since the policy changes
the child's world too. It is the same simplification children.py already makes.

WHAT IS AND IS NOT COUNTED

The planner counts the parent's own lifetime value once and the child's once.
The parent counts its own in full and the child's at omega. So the wedge, the
part that is genuinely external, is (1 - omega) of the damage. value1 therefore
returns the parent's OWN value, with the internalised term added back after the
choice of v is made, so that raising omega changes behaviour without moving the
parent's welfare by accounting alone.

Only the disorder penalty del_d is internalised here, not the homelessness
penalty del_h. That is the margin that decides Housing First against Treatment
First: both policies drive homelessness to zero at universal cover, so del_h
prices the programme against no programme and does not enter this comparison.

Run:  python3 internalise.py
"""

import json
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats, bracket
from welfare import cev, PV_INCOME
from children import child_grid, shifted, DEL_D

WW = W / W.sum()


def delta_utility(par):
    """The child's expected loss in lifetime UTILITY from the income penalty."""
    v1, _ = child_grid(par, 'HF', par.pV)
    return shifted(v1, 0.0) - shifted(v1, DEL_D)


def row(par, omega, dlt, pV=1.0):
    """
    One row of the robustness table, at internalisation weight omega.

    b IS RECALIBRATED AT EVERY omega, exactly as in figure 1. Internalisation is
    a powerful deterrent on its own: left at the baseline b, a weight of 0.10
    takes drug use from 5.13 per cent to 2.80 and a weight of 0.25 takes it to
    1.01, so without a refit the table would be comparing economies with
    different amounts of drug use and would answer a different question. Holding
    participation at its target isolates what internalisation does to the POLICY
    COMPARISON rather than to the level of use.
    """
    q = with_(par, omega=omega, chdmg=dlt)
    q = with_(q, b=bracket(q, 'b', 'part', 1e-6, 0.60, iters=26))
    vh = np.array([value1(with_(q, policy='HF', pV=pV), y, 'HF') for y in YG])
    vt = np.array([value1(with_(q, policy='TF', pV=pV), y, 'TF') for y in YG])
    priv = float((WW * cev(q, vh - vt)).sum()) * PV_INCOME
    mh = stats(with_(q, pV=pV, policy='HF'))
    mt = stats(with_(q, pV=pV, policy='TF'))
    dsud = mh['sud'] - mt['sud']
    # the child's damage per case, in units of one lifetime income, and only
    # the (1 - omega) share of it is still external
    v1u, _ = child_grid(q, 'HF', pV)
    per_case = cev(q, shifted(v1u, 0.0) - shifted(v1u, DEL_D)) * PV_INCOME
    gain = (1.0 - omega) * dsud * per_case
    base = stats(with_(q, pV=par.pV, policy='HF'))
    return dict(omega=omega, part=base['part'], b=q.b, sud_h=mh['sud'],
                sud_t=mt['sud'], dsud=dsud, priv=priv, gain=gain,
                ratio=gain / max(priv, 1e-12))


def tab_internalise(par, dlt, omegas=(0.0, 0.10, 0.25, 0.50)):
    import os
    from tables import OUT
    # every model output in this table moved with the recalibration
    RED = lambda x: '' + x + ''
    rows = [row(par, w, dlt) for w in omegas]
    L = [r'\small', r'\begin{tabular}{@{}lcccccc@{}}', r'\toprule',
         r'Weight on & Refitted & \multicolumn{2}{c}{Disorder at $\pi_V=1$}'
         r' & Private & External & Gain over \\',
         r'\cmidrule(lr){3-4}',
         r'the child $\omega$ & $b$ & HF & TF & loss & gain & loss \\',
         r'\midrule']
    for r in rows:
        lab = f'{r["omega"]:.2f}'
        if abs(r['omega']) < 1e-9:
            lab += r'\ \ (baseline)'
        b_, sh, st = r["b"], 100*r["sud_h"], 100*r["sud_t"]
        pr, gn, ra = 100*r["priv"], 100*r["gain"], r["ratio"]
        L.append(f'{lab} & {RED(f"{b_:.5f}")} & {RED(f"{sh:.3f}")}\\% '
                 f'& {RED(f"{st:.3f}")}\\% & {RED(f"{pr:.3f}")}\\% '
                 f'& {RED(f"{gn:.3f}")}\\% & {RED(f"{ra:.1f}")} \\\\')
    L += [r'\bottomrule', r'\end{tabular}']
    with open(os.path.join(OUT, 'tab_internalise.tex'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('   wrote tab_internalise.tex')
    return rows


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('=' * 76)
    print('ROBUSTNESS: PARTIAL INTERNALISATION OF THE CHILD')
    print('=' * 76)
    dlt = delta_utility(base)
    print(f'\n   DELTA, the child\'s loss in lifetime utility : {dlt:.4f}')
    print(f'   for comparison, V1 at mean income          : '
          f'{value1(base, 1.0, "HF"):.4f}')
    print('\n   b is recalibrated at every omega so that participation stays '
          'at 5.13 per cent')
    print(f'\n   {"omega":>7s}{"use, baseline":>16s}{"disorder HF":>14s}'
          f'{"disorder TF":>14s}{"private loss":>15s}{"external gain":>16s}'
          f'{"ratio":>9s}')
    for r in tab_internalise(base, dlt):
        print(f'   {r["omega"]:7.2f}{100*r["part"]:15.2f}%{100*r["sud_h"]:13.3f}%'
              f'{100*r["sud_t"]:13.3f}%{100*r["priv"]:14.3f}%'
              f'{100*r["gain"]:15.3f}%{r["ratio"]:9.1f}')
