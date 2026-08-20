"""
The note's tables, written straight to LaTeX so they can never drift from the
code. Run:  python3 tables.py

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
         'ANN', '{:.3f}'),
        ('R', 'R', 'Interest rate over a thirty year period',
         r'Set to $1/\beta$', '{:.3f}'),
        ('phi0', r'\bar\phi', 'Survival over a period, no SUD',
         'SSA period life table, ages 25--55', '{:.2f}'),
        ('th', r'\theta', 'Weight on drugs in utility',
         r'Set; see the text', '{:.2f}'),
    ]),
    ('The SUD', [
        ('kap', r'\kappa_{\phi d}', 'Fall in survival with a SUD, over a thirty year period',
         'Hjorth\\o j et al.\\ (2023), age 26+', '{:.2f}'),
        ('u0', 'u_0', 'Unemployment probability, no SUD',
         'BLS CPS via FRED, 2014 to 2024', '{:.4f}'),
        ('u1', 'u_1', 'Unemployment probability, with a SUD',
         'NSDUH 2024, age 26+', '{:.4f}'),
    ]),
    ('Income support', [
        ('repl', r'\psi', 'UI replacement rate',
         'DOL, statutory UI rates', '{:.2f}'),
        ('ycap', r'\bar y', 'Cap on the earnings base',
         'DOL, state benefit maxima', '{:.2f}'),
    ]),
    ('Housing, drugs and the voucher', [
        ('pr', 'p_r', 'Rent per unit of housing services', 'Normalisation',
         '{:.2f}'),
        ('p_v', 'p_v', 'Price of a unit of drugs',
         'Normalisation', '{:.2f}'),
        # QUOTED AS A MULTIPLE OF AVERAGE INCOME, like the two rows above them,
        # rather than in model units. The model's numeraire makes h_lg 0.40 and
        # average income 0.978, so the same object is 0.41 of average income; a
        # table that printed 0.40 next to a source line saying 0.41 was asking
        # the reader to reconcile two numbers for one parameter.
        ('h_lg', r'h_3', 'Standard rental unit', 'Set', '{:.2f}'),
        # The ratio is stated in the TEXT and not here. Printing "a quarter of
        # the standard unit" beside 0.10 next to a 0.41 invites the reader to
        # multiply by four, get 0.40, and conclude the table is wrong. It is not:
        # h_sm is exactly h_lg/4 and both are correctly rounded. But a table
        # should not set a check it fails.
        # THE VALUE IS THE RATIO, not a rounded decimal. h_sm is exactly a
        # quarter of h_lg, and printing 0.10 beside the standard unit's 0.41
        # invited the reader to multiply by four and find 0.40. Writing the
        # relation itself is exact and there is nothing left to check.
        ('h_sm', r'h_2', 'Small rental unit', 'Set', r'0.25\times h_3'),
        ('kappa_r', r'\kappa_r', "Tenant's share of the rent",
         'HUD voucher rules', '{:.2f}'),
        ('kV', r'\kappa_V', 'Voucher means test',
         'HUD income limits', '{:.2f}'),
        ('pV', r'\pi_V', 'Chance of drawing a voucher',
         'HUD 2023, recipients over eligible', '{:.3f}'),
    ]),
]

# SIGMA_Y IS FIRST AND ITS ATTRIBUTE IS None. It is calibrated, on the bottom
# half's share of earnings, but it is not carried on the parameter object: the
# income grid is built from it before any parameter is chosen, so it lives in
# calibrate.SIG. None means "read SIG", and the row is otherwise an ordinary
# internally calibrated one.
INTERNAL = [
    (None, r'\sigma_y', 'Dispersion of productivity',
     "Bottom half's share of earnings, SCF 2022", 'bot50', '{:.1%}', '{:.3f}'),
    ('gam', r'\gamma', 'Weight on housing services',
     'Housing over expenditure net of drugs, CEX 2024', 'hspend', '{:.1%}',
     '{:.3f}'),
    ('aleph', r'\aleph', 'Flow value of being alive',
     'Value of a statistical life, Viscusi and Aldy (2003)', 'vsl', '{:.1f}', '{:.3f}'),
    ('b', 'b', 'Whether a household uses', 'Drug participation, NSDUH 2024',
     'part', '{:.2%}', '{:.5f}'),
    ('h_hl', 'h_1', 'Service flow of homelessness', 'Homelessness rate, HUD 2023',
     'homeless', '{:.3%}', '{:.5f}'),
    # THE MOMENT IS THE ADULT SUD RATE, not the share of users who progress.
    # The life cycle model targets 3.68 per cent from NSDUH 2024 and this model
    # used to target a progression rate of 33.2 per cent, which at a
    # participation rate of 5.13 implies a population rate of 1.70: the two
    # models were calibrated to inconsistent numbers for the same object.
    ('lam', r'\lambda', 'SUD hazard per unit used',
     'Adult SUD rate, NSDUH 2024', 'sud', '{:.2%}', '{:.1f}'),
]


def tab_external(base):
    L = [r'\footnotesize', r'\begin{tabular}{@{}lL{7.3cm}L{5.0cm}r@{}}',
         r'\toprule',
         r'Parameter & Description & Source or rationale & Value \\',
         r'\midrule']
    from calibrate import YG, W
    ww = W / W.sum(); ybar = float((ww * YG).sum())
    PER_YBAR = {'h_lg'}             # quoted as a multiple of average income
    for k, (head, rows) in enumerate(EXTERNAL):
        if k:
            L.append(r'\addlinespace')
        L.append(r'\multicolumn{4}{@{}l}{\emph{%s}} \\' % head)
        for attr, sym, desc, src, fmt in rows:
            # the annual rate is the model's, not a number typed into the table
            if src == 'ANN':
                src = f'${base.beta_ann:.3f}$ annually, compounded'
            raw = None if attr is None else getattr(base, attr)
            if attr in PER_YBAR:
                raw = raw / ybar
            # a format string with no field is a literal, printed as written
            val = (fmt if attr is None or '{:' not in fmt
                   else fmt.format(raw))
            L.append(f'${sym}$ & {desc} & {src} & ${val}$ \\\\')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_external.tex', '\n'.join(L) + '\n')


def tab_internal(base):
    from calibrate import TARGET, SIG
    m = stats(base)
    L = [r'% Generated by code/stylized/tables.py. Do not edit by hand: it is',
         r'% overwritten on every calibration, and hand edits have been lost here',
         r'% before.',
         r'\footnotesize\setlength{\tabcolsep}{4pt}',
         r'% Plain l columns, not L{}, so no row can wrap. At \footnotesize the six',
         r'% columns of content plus five 4pt gaps of \tabcolsep fit inside the',
         r'% 469.8pt text block; widening any description will overflow it.',
         r'\begin{tabular}{@{}lllrrr@{}}',
         r'\toprule',
         r'Parameter & Description & Target moment & Data & Model & Value \\',
         r'\midrule']
    for attr, sym, desc, mom, key, mfmt, vfmt in INTERNAL:
        val = SIG if attr is None else getattr(base, attr)
        L.append(f'${sym}$ & {desc} & {mom} & '
                 f'{mfmt.format(TARGET[key]).replace("%", chr(92) + "%")} & '
                 f'{mfmt.format(m[key]).replace("%", chr(92) + "%")} & '
                 f'${vfmt.format(val)}$ \\\\')
        print(f'   {attr or "sig":6s}: target {TARGET[key]:.5f}  '
              f'model {m[key]:.5f}  value {val:.6g}')
    L += [r'\bottomrule', r'\end{tabular}']
    write('tab_internal.tex', '\n'.join(L) + '\n')


def tab_channels(base):
    """b and the income ratio, both channels, at five strengths."""
    sc = [0.0, 0.25, 0.50, 0.75, 1.0, 1.25]
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
    tab_external(base)
    tab_internal(base)
