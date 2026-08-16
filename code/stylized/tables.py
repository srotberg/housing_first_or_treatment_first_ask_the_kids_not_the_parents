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


# Every externally set parameter, with the attribute it is read from so the
# note can never quote a value the model does not use.
EXTERNAL = [
    ('Preferences and demographics', [
        ('beta', r'\beta', 'Discount factor over a thirty year period',
         r'$0.99$ annually, compounded', '{:.3f}'),
        ('R', 'R', 'Gross interest rate over a thirty year period',
         r'Set to $1/\beta$', '{:.3f}'),
        (None, r'\sigma', 'Dispersion of log permanent income',
         'Heathcote et al.\\ (2010)', '0.75'),
        ('phi0', r'\phi_0', 'Survival over a period, no SUD',
         'SSA period life table, ages 25--55', '{:.2f}'),
        ('th', r'\theta', 'Weight on drug use',
         r'Set; see the text', '{:.2f}'),
    ]),
    ('The SUD', [
        ('kap', r'\kappa', 'Proportional fall in survival with a SUD',
         'Hjorth\\o j et al.\\ (2023), age 26+, \\textcolor{red}{over 30 years}', '{:.2f}'),
        ('u0', 'u_0', 'Unemployment probability, no SUD',
         '\\textcolor{red}{BLS CPS, series UNRATE via FRED, 2014 to 2024}', '{:.4f}'),
        ('u1', 'u_1', 'Unemployment probability, with a SUD',
         'NSDUH 2024, age 26+', '{:.4f}'),
    ]),
    ('Income support', [
        ('repl', r'\psi', 'Replacement rate while unemployed',
         'DOL, statutory UI rates', '{:.2f}'),
        ('ycap', r'\bar y',
         'Cap on the earnings base, multiple of average income',
         'DOL, state benefit maxima', '{:.2f}'),
    ]),
    ('Housing, drugs and the voucher', [
        ('pr', 'p_r', 'Rent per unit of housing services', 'Normalisation',
         '{:.2f}'),
        ('p_v', 'p_v', 'Price of a unit of drugs',
         'Normalisation', '{:.2f}'),
        ('h_lg', 'h_L', 'Standard rental unit',
         '\\textcolor{red}{Set; $0.41$ of mean income}', '{:.2f}'),
        ('h_sm', 'h_S', 'Small rental unit',
         '\\textcolor{red}{Set; a quarter of the standard unit}', '{:.2f}'),
        ('kappa_r', r'\kappa_r', "Tenant's share of the rent when covered",
         'HUD voucher rules', '{:.2f}'),
        ('yV', 'y_V', 'Voucher means test, multiple of average income',
         'HUD income limits', '{:.2f}'),
        ('pV', r'\pi_V', 'Voucher generosity in the baseline',
         'HUD 2023, assisted eligible share', '{:.2f}'),
    ]),
]

INTERNAL = [
    ('gam', r'\gamma', '\\textcolor{red}{Weight on housing services}',
     '\\textcolor{red}{Housing over non drug spending}', 'hspend', '{:.2%}',
     '{:.3f}'),
    ('aleph', r'\aleph', 'Flow value of being alive',
     'Value of a statistical life', 'vsl', '{:.1f}', '{:.3f}'),
    ('b', 'b', 'Pull of the first unit of drugs', 'Drug participation rate',
     'part', '{:.2%}', '{:.5f}'),
    ('h_hl', 'h_0', 'Housing services when homeless', 'Homelessness rate',
     'homeless', '{:.2%}', '{:.5f}'),
    ('lam', r'\lambda', 'Addiction hazard per unit of use',
     'Share of users who acquire a SUD', 'prog', '{:.1%}', '{:.1f}'),
]


def tab_external(base):
    L = [r'\footnotesize', r'\begin{tabular}{@{}cL{6.9cm}L{4.5cm}r@{}}',
         r'\toprule',
         r'Parameter & Description & Source or rationale & Value \\',
         r'\midrule']
    for k, (head, rows) in enumerate(EXTERNAL):
        if k:
            L.append(r'\addlinespace')
        L.append(r'\multicolumn{4}{@{}l}{\emph{%s}} \\' % head)
        for attr, sym, desc, src, fmt in rows:
            val = fmt if attr is None else fmt.format(getattr(base, attr))
            L.append(f'${sym}$ & {desc} & {src} & ${val}$ \\\\')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_external.tex', '\n'.join(L) + '\n')


def tab_internal(base):
    from calibrate import TARGET
    m = stats(base)
    L = [r'\footnotesize', r'\begin{tabular}{@{}cL{4.6cm}L{4.6cm}rrr@{}}',
         r'\toprule',
         r'Parameter & Description & Target moment & Data & Model & Value \\',
         r'\midrule']
    # THE MODEL AND VALUE COLUMNS ARE RED because every one of them moved with
    # the recalibration. The Data column is a target and did not move.
    red = lambda x: '\\textcolor{red}{' + x + '}'
    for attr, sym, desc, mom, key, mfmt, vfmt in INTERNAL:
        L.append(f'${sym}$ & {desc} & {mom} & '
                 f'{mfmt.format(TARGET[key]).replace("%", chr(92) + "%")} & '
                 f'{red(mfmt.format(m[key]).replace("%", chr(92) + "%"))} & '
                 f'{red("$" + vfmt.format(getattr(base, attr)) + "$")} \\\\')
        print(f'   {attr}: target {TARGET[key]:.5f}  model {m[key]:.5f}  '
              f'value {getattr(base, attr):.6g}')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_internal.tex', '\n'.join(L) + '\n')


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
    # every cell here is a model output and every one of them moved
    red = lambda x: '\\textcolor{red}{' + x + '}'
    for s, b1, r1, b2, r2 in rows:
        L.append(f'{100*s:.0f}\\% & {red(f"{b1:.4f}")} & {red(f"{r1:.2f}")} '
                 f'& {red(f"{b2:.4f}")} & {red(f"{r2:.2f}")} \\\\')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_channels.tex', '\n'.join(L) + '\n')
    return rows


def tab_policy(base):
    """No programme, universal Treatment First, universal Housing First."""
    p0 = 100 * stats(with_(base, pV=0.0, policy='HF'))['part']
    pt = 100 * stats(with_(base, pV=1.0, policy='TF'))['part']
    ph = 100 * stats(with_(base, pV=1.0, policy='HF'))['part']
    print(f'   none {p0:.2f}   TF {pt:.2f}   HF {ph:.2f}')
    R = lambda x: '\\textcolor{red}{' + x + '}'

    L = [r'\begin{tabular}{@{}lcc@{}}', r'\toprule',
         r'& Participation rate & Difference \\',
         r'\midrule',
         r'\multicolumn{3}{@{}l}{\emph{Panel A. Drug use under each policy}} \\',
         f'\\quad No voucher programme ($\\pi_V=0$) & {R(f"{p0:.2f}")}\\% & \\\\',
         f'\\quad Universal Treatment First ($\\pi_V=1$) & {R(f"{pt:.2f}")}\\% & \\\\',
         f'\\quad Universal Housing First ($\\pi_V=1$) & {R(f"{ph:.2f}")}\\% & \\\\',
         r'\addlinespace',
         r'\multicolumn{3}{@{}l}{\emph{Panel B. The two forces}} \\',
         r'\quad Value of life\quad(Treatment First $-$ no programme)'
         f' & & {R(f"${pt-p0:+.2f}$")} pp \\\\',
         r'\quad Moral hazard\quad(Housing First $-$ Treatment First)'
         f' & & {R(f"${ph-pt:+.2f}$")} pp \\\\',
         r'\addlinespace',
         r'\quad Net effect of Housing First\quad(Housing First $-$ no programme)'
         f' & & {R(f"${ph-p0:+.2f}$")} pp \\\\',
         r'\bottomrule', r'\end{tabular}']
    write('tab_policy.tex', '\n'.join(L) + '\n')
    return p0, pt, ph


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('tables')
    tab_external(base)
    tab_internal(base)
    tab_channels(base)
    tab_policy(base)
