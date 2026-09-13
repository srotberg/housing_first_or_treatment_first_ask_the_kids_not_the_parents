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


from tablered import mark as _mark_changes_body


def write(name, body):
    body = _mark_changes_body(name, body)
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
         'SSA period life table, ages 26--55', '{:.2f}'),
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
        ('repl', r'\psi_{ui}', 'UI replacement rate',
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
        # rather than in model units, and Table 2 quotes h_2 the same way. The
        # division is a no-op while average income is exactly one, which is what
        # the calibrated grid gives today, so 0.40 is both; it stops being a
        # no-op the moment the grid moves off that normalisation, which is the
        # only reason to keep it. It was written when average income was 0.978
        # and the table printed 0.40 beside a source line saying 0.41.
        ('h3', r'h_3', 'Standard rental unit', 'Set', '{:.2f}'),
        # h_2 IS NOT HERE ANY MORE. It used to be Set, at exactly a quarter of
        # h_3, and printed as the ratio rather than as a decimal so that a
        # reader could not multiply 0.10 by four, get 0.40 against h_3's 0.41,
        # and conclude the table was wrong. It is now bracketed on the share of
        # the housed in the smaller of the two units, so it is an internally
        # calibrated parameter and its row is in Table 2 with the others. The
        # quarter is gone with it: the ratio the calibration picks is whatever
        # reproduces the size distribution, not a number chosen in advance.
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
    # THETA IS AN INTERNALLY CALIBRATED ROW, reported against the moment it is
    # chosen to match like every other row here. It is found by a SCAN rather
    # than a bisection, and that is a fact about the moment rather than about
    # the parameter: the drug spending share is discontinuous in theta, climbing
    # to about 19 per cent and jumping to 29, so a bisection aimed between those
    # branches narrows onto the jump instead of converging. Scanning theta for
    # the value whose share matches the data is what calibrating on a moment
    # means; only the method of search differs.
    #
    # FOUR FIGURES BECAUSE THE THIRD ONE MATTERS: the mortality channel gives
    # out near 0.245 and this sits at 0.2350.
    # THE SOURCE LINE NAMES RAND ONLY, and it has to. This column is a plain l
    # so no row can wrap, and the note at the head of tab_internal warns that
    # widening any description overflows the text block: at 63 characters this
    # cell put the table 64pt over, against a previous longest of 52. The full
    # construction, which also needs NSDUH for the denominator, is in the prose
    # where theta is presented.
    ('th', r'\theta', 'Weight on drugs in utility',
     'Drug spending over income among users, RAND 2016',
     'dshare', '{:.1%}', '{:.4f}'),
    ('h1', 'h_1', 'Service flow of homelessness', 'Homelessness rate, HUD 2023',
     'homeless', '{:.3%}', '{:.5f}'),
    # h_2 IS CALIBRATED, NOT SET, and its target is the same American Community
    # Survey size distribution the quantitative model matches: B25042, occupied
    # units, collapsed to this model's two rentals, so 13.2 per cent of
    # households are in a unit of no bedroom or one. h_3 stays at its market
    # value and h_2 is bracketed on the share, which is the arrangement the
    # quantitative model uses and the reason the fixed quarter was dropped.
    ('h2', r'h_2', 'Small rental unit',
     'Share of the housed in the small unit, ACS 2023', 'hsmall',
     '{:.1%}', '{:.3f}'),
    # THE MOMENT IS THE ADULT SUD RATE, not the share of users who progress, and
    # it is the MODERATE OR SEVERE rate on the model's own universe: NSDUH 2024,
    # AGE3 >= 7 for 26 and over, svyrdudany in (2,3), 3.68 per cent, with
    # participation the whole of any severity at 8.90. Both come from the same
    # variable and the same universe, which two earlier pairs did not: 5.13 and
    # 3.68 matched no single cut, and 10.13 and 4.54 were the EIGHTEEN and over
    # figures while the note said 26 and over throughout.
    ('lam', r'\lambda_d', 'SUD hazard per unit used',
     'Adult SUD rate, NSDUH 2024', 'sud', '{:.2%}', '{:.1f}'),
]


def tab_external(base):
    L = [r'\footnotesize', r'\begin{tabular}{@{}lL{7.3cm}L{5.0cm}r@{}}',
         r'\toprule',
         r'Parameter & Description & Source or rationale & Value \\',
         r'\midrule']
    from calibrate import YG, W
    ww = W / W.sum(); ybar = float((ww * YG).sum())
    PER_YBAR = {'h3'}             # quoted as a multiple of average income
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
    from calibrate import YG, W
    ww = W / W.sum(); ybar = float((ww * YG).sum())
    # QUOTED AS A MULTIPLE OF AVERAGE INCOME, exactly as h_3 is in Table 1.
    # h_2 is a housing service flow and the only other one the reader sees is
    # scaled that way, so leaving this in model units would put 0.10 beside a
    # 0.41 that is measured differently.
    PER_YBAR = {'h2'}
    for attr, sym, desc, mom, key, mfmt, vfmt in INTERNAL:
        val = SIG if attr is None else getattr(base, attr)
        if attr in PER_YBAR:
            val = val / ybar
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
