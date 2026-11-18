#!/usr/bin/env python3
"""fill_slides.py -- the deck's numbers, read from the paper, never typed.

    python3 presentation/latex/fill_slides.py        (build.sh runs it first)

slides.src.tex -> slides.tex. Every @@name@@ is filled from

  * the paper's own names, loaded exactly as code/paper/splice.py loads them for the paper and printed at the paper's
    text precision (fill.text_precision), so a slide says what the paper says;
  * the deck's own names (DECK below), for the few numbers the paper prints only in a table or inside a generated
    sentence. Each is read off a cell of the table the paper prints (writing/tables) or out of the sentence with a
    pattern; a cell is checked against the paper's own name where one exists, and the build stops if the paper
    rewords a sentence, rather than print a stale number.

@@name@@ prints a negative value with a typeset minus ($-$1.19), for text; @@=name@@ prints the bare number (-1.19), for
pgfplots coordinates and maths. A direction the deck types in words ("falls", "loses", "gains") is asserted in
DIRECTIONS below, so a number that changes sign stops the build instead of contradicting the word beside it.

It also writes the tables the deck shows in part, from the paper's own table files:
  gen_params.tex      selected rows of Table 3 (writing/tables/tab_eleven.tex)
  gen_untargeted.tex  selected rows of Table 4 (writing/tables/tab_untargeted.tex)
  gen_alttrans.tex    Table 7's tabular (writing/tables/tab_alttrans.tex)
Table 5, the weight-of-one table and the stylized model's two tables are bare tabulars, which the deck inputs directly.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
TAB = os.path.join(ROOT, 'writing', 'tables')
sys.path.insert(0, os.path.join(ROOT, 'code', 'paper'))
sys.path.insert(0, os.path.join(ROOT, 'code', 'stylized'))
import fill     # noqa: E402
import splice   # noqa: E402

N = splice.load([os.path.join(ROOT, f) for f in splice.FILES])


def paper(k):
    """a name of the paper, as the paper prints it"""
    return str(fill.text_precision(k, N[k]))


def num(s):
    return float(s.replace('$-$', '-').replace('$', '').replace('{,}', '').replace('\\%', '').strip())


def signed(x, d=0):
    s = f'{x:.{d}f}'
    return s[1:] if re.fullmatch(r'-0(\.0+)?', s) else s


def clean(s):
    """a cell without the marks the paper's tables may carry"""
    for _ in range(3):
        s = re.sub(r'\\(?:new|updnum|tocheck)\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', s)
    return s.strip()


def lines(path):
    return [re.sub(r'(?<!\\)%.*', '', l).rstrip() for l in open(path)]


def cells(line):
    return [clean(c) for c in line[:-2].split('&')]


def rows(path):
    """the body rows of a generated tabular, by their first cell"""
    return {cells(l)[0]: cells(l) for l in lines(path) if '&' in l and l.endswith('\\\\')}


def grab(name, pattern):
    """numbers out of one of the paper's generated sentences; stops the build if the paper reworded it"""
    m = re.search(pattern, str(N[name]))
    assert m, f'{name} no longer reads as the deck expects ({pattern}): reread it and fix the deck'
    return m.groups()


def words_to_int(w):
    units = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen ' \
            'seventeen eighteen nineteen'.split()
    tens = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
    total = 0
    for p in w.lower().split():
        total += tens[p] if p in tens else units.index(p)
    return str(total)


# ------------------------------------------------------------------------------------------------- Table 5, long run
T5 = rows(os.path.join(TAB, 'tab_longrun.tex'))
CEV = 'CEV of a newborn, percent of lifetime consumption'
PIV = 'Voucher probability $\\pi_V$'


def t5(label, col):
    return T5[label][col]


def change(label, col, base, mag=None):
    """the percent change of a Table 5 row from column base to column col, signed. With mag, the size is the paper's own
    (computed at full precision) and the printed cells only give its sign and check it."""
    v = 100 * (num(t5(label, col)) / num(t5(label, base)) - 1)
    if mag is None:
        return signed(v)
    m = float(mag)
    assert abs(abs(v) - m) <= 1, f'{label}, column {col}: the table gives {v:.1f}, the paper {m}'
    return signed(math.copysign(m, v))


def cev(col, name):
    c = signed(num(t5(CEV, col)), 2)
    assert abs(abs(float(c)) - float(paper(name))) < 1e-9, f'Table 5 CEV column {col} is {c}, {name} is {paper(name)}'
    return c


DECK = {}

# Experiment 1, no externalities: columns 2 to 5 against column 1
DECK.update(d_x1_use_held=change('Drug use', 2, 1, paper('x_pe_b_pc')),
            d_x1_use_pvc=change('Drug use', 3, 1, paper('x_fx_b_pc')),
            d_x1_use_prc=change('Drug use', 4, 1),
            d_x1_use_both=change('Drug use', 5, 1, paper('x_nc_b_pc')),
            d_x1_cev_held=cev(2, 'x_pe_newborn_cev'), d_x1_cev_pvc=cev(3, 'x_fx_newborn_cev'),
            d_x1_cev_prc=signed(num(t5(CEV, 4)), 2), d_x1_cev_both=cev(5, 'x_nc_newborn_cev'))
DECK['d_x1_use_upto'] = signed(max(abs(float(DECK[k])) for k in DECK if k.startswith('d_x1_use_')))

# Experiment 2, with the externalities: columns 7, 8 and 10 against column 6
DECK.update(d_x2_use_held=change('Drug use', 7, 6, paper('x_dc_b_b_pc')),
            d_x2_use_pvc=change('Drug use', 8, 6, paper('x_dc_p_b_pc')),
            d_x2_use_both=change('Drug use', 10, 6, paper('x_tf_b_pc')),
            d_x2_hl_held=change('Homelessness', 7, 6, grab('x_dcb_h', r'^falls by \$(\d+)\$ percent$')[0]),
            d_x2_hl_pvc=change('Homelessness', 8, 6, grab('x_dcp_h', r'^falls by \$(\d+)\$ percent$')[0]),
            d_x2_hl_both=change('Homelessness', 10, 6, paper('x_tf_h_pc')),
            d_x2_piv_bench=t5(PIV, 6), d_x2_piv_held=t5(PIV, 7), d_x2_piv_pvc=t5(PIV, 8), d_x2_piv_both=t5(PIV, 10))
for k, n in (('d_x2_piv_pvc', 'x_dc_p_piv_pc'), ('d_x2_piv_both', 'x_tf_piv1_pc'), ('d_x2_piv_bench', 'x_tf_piv0_pc')):
    assert DECK[k] == paper(n), f'{k} {DECK[k]} against {n} {paper(n)}'

# the main experiment, the last column
DECK.update(d_m_use=DECK['d_x2_use_both'], d_m_sud=change('Carrying a SUD', 10, 6, paper('x_tf_sud_pc')),
            d_m_hl=DECK['d_x2_hl_both'], d_m_hchild=change('In a shelter', 10, 6, paper('x_tf_hchild_pc')),
            d_m_paruse=change('Living with a parent who uses drugs', 10, 6),
            d_m_parsud=change('Living with a parent who has a SUD', 10, 6),
            d_m_hl0=t5('Homelessness', 6), d_m_hl1=t5('Homelessness', 10),
            d_m_hchild0=t5('In a shelter', 6), d_m_hchild1=t5('In a shelter', 10),
            d_m_treat0=t5('In treatment, of those with a SUD', 6), d_m_treat1=t5('In treatment, of those with a SUD', 10),
            d_sud_better=t5('Households with a SUD better off', 10))
DECK['d_kids_hl'] = grab('x_lr_children_hl', r'homelessness also falls by \$(\d+)\$ percent')[0]
DECK['d_nb_better'] = grab('x_lr_approve', r'\$([\d.]+)\$ percent are better off')[0]

# robustness: the detection rate at half and at a quarter
DECK['d_h10_use'], DECK['d_h10_hl'] = grab('x_h10_clause', r'^cuts drug use by \$(\d+)\$ and homelessness by \$(\d+)\$ percent$')
DECK['d_h05_use'], DECK['d_h05_hl'] = grab('x_h05_clause', r'^cuts drug use by \$(\d+)\$ and homelessness by \$(\d+)\$ percent$')

# validation: the middle of the income distribution
DECK['d_ui_mlo'], DECK['d_ui_mhi'], DECK['d_ui_dlo'], DECK['d_ui_dhi'] = grab(
    'x_ui_sentence', r'flatter and lower than in the data, \$([\d.]+)\$ to \$([\d.]+)\$ percent against \$([\d.]+)\$ to \$([\d.]+)\$')

# the announced screen
DECK['d_ann_cut'] = grab('x_at_ann_par', r'in anticipation of a screen that will catch every user, by \$(\d+)\$ percent')[0]

# the parameter counts, which the paper writes in words
for k in ('n_all', 'n_ext', 'n_int', 'n_main', 'n_std'):
    DECK['d_' + k] = words_to_int(N[k])

# ------------------------------------------------------------------------------------- Table 7, alternative transitions
T7 = {}
group = None
for l in lines(os.path.join(TAB, 'tab_alttrans.tex')):
    m = re.search(r'\\multicolumn\{7\}\{@\{\}l\}\{(.*)\}', l)
    if m:
        group = {'No': 'ne', 'Announced': 'an', 'Sobriety': 'gr'}[m.group(1).split()[0]]
    elif '&' in l and l.endswith('\\\\') and re.match(r'\s*\d+$', cells(l)[1]):
        c = cells(l)
        key = 'main' if c[0] == 'Main transition' else f'{group}{c[1]}'
        T7[key] = c
assert sorted(T7) == ['an100', 'an20', 'gr100', 'gr20', 'main', 'ne100', 'ne20'], sorted(T7)
for k, c in T7.items():
    DECK[f'd_at_h_{k}'] = '0' if c[2] == 'none' else c[2].split()[0]
    DECK[f'd_at_cev_{k}'] = c[6]
assert DECK['d_at_cev_main'] == paper('x_tr_cev_b1_2') and DECK['d_at_cev_ne100'] == paper('x_at_ne100_cev')
DECK['d_ax_at_h'] = signed(1.18 * max(float(DECK[f'd_at_h_{k}']) for k in T7))
DECK['d_ax_at_cev'] = signed(1.2 * max(float(DECK[f'd_at_cev_{k}']) for k in T7), 1)

# axis ranges of the bar charts, so a bar that grows is not cut off
DECK['d_ax_x1_use'] = signed(1.3 * min(float(DECK[k]) for k in DECK if k.startswith('d_x1_use_') and k != 'd_x1_use_upto'))
DECK['d_ax_x1_cev'] = signed(1.2 * min(float(DECK[k]) for k in DECK if k.startswith('d_x1_cev_')), 1)
DECK['d_ax_main'] = signed(1.2 * min(float(DECK[k]) for k in ('d_m_use', 'd_m_sud', 'd_m_hl', 'd_m_hchild', 'd_m_paruse', 'd_m_parsud')))

# --------------------------------------------------------------- the directions the deck states in words, checked
f = lambda k: float(DECK[k]) if k in DECK else float(paper(k))
DIRECTIONS = [
    ('a newborn loses in every case without the externalities', all(f(k) < 0 for k in DECK if k.startswith('d_x1_cev_'))),
    ('drug use falls in every case without the externalities', all(f(k) < 0 for k in ('d_x1_use_held', 'd_x1_use_pvc', 'd_x1_use_prc', 'd_x1_use_both'))),
    ('every step of experiment 2 gains', all(f(k) > 0 for k in ('x_dc_b_cev', 'x_dc_p_cev', 'x_tf_cev'))),
    ('every outcome falls in the main experiment', all(f(k) < 0 for k in ('d_m_use', 'd_m_sud', 'd_m_hl', 'd_m_hchild', 'd_m_paruse', 'd_m_parsud'))),
    ('parents gain too in the main experiment', f('x_wd_P_tf') > 0),
    ('the drug price falls in the main experiment', num(t5('Drug price, benchmark $=1$', 10)) < num(t5('Drug price, benchmark $=1$', 6))),
    ('pi_V rises in the main experiment', f('x_tf_piv1_pc') > f('x_tf_piv0_pc')),
    ('with a weight of one, a newborn gains with prices held', f('x_om1_tot_held') > 0 and N['x_om1_tot_dir_held'] == 'gains'),
    ('with a weight of one, every parent loses with prices held', N['x_om1_parents_held'] == 'every parent loses' and f('x_om1_P_held') < 0),
    ('with a weight of one, a newborn gains when both clear', f('x_om1_tot_tf') > 0),
    ('half and quarter rates: the stop shares are inside the military range',
     N['x_ws_half_where'] == 'inside' and N['x_ws_quarter_where'] == 'inside'),
    ('half and quarter rates: a newborn still gains', f('x_h10_cev') > 0 and N['x_h05_dir'] == 'better'),
    ('universal vouchers: Treatment First raises welfare', N['x_univ_dir'] == 'raises'),
    ('the exemption in treatment beats the main transition for newborns', f('d_at_cev_gr20') > f('d_at_cev_main')),
    ('the main transition never raises homelessness', DECK['d_at_h_main'] == '0'),
    ('universal Housing First beats rationed Housing First', N['x_univ_hf_cev_dir'] == 'raise'),
]
bad = [d for d, ok in DIRECTIONS if not ok]
assert not bad, 'a direction the deck states in words no longer holds: ' + '; '.join(bad)

# ------------------------------------------------------------------------------------- the tables the deck shows in part
T3 = rows(os.path.join(TAB, 'tab_eleven.tex'))
PARAMS = [('$b$', "first unit's marginal utility"), ('$\\pi_d$', 'chance use leads to a SUD'),
          ('$\\kappa_{\\phi d}$', 'mortality with a SUD'), ('$\\aleph$', 'value of being alive'),
          ('$h_1$', 'service flow of homelessness'), ('$\\pi_V$', 'chance of drawing a voucher'),
          ('$\\mu_H$', 'recovery when homeless'), ('$\\bar\\tau^{u}$', 'utility cost of treatment'),
          ('$\\omega_c$', "parent's weight on its child"), ('$\\delta_d$', "child's earnings loss"),
          ('$\\varepsilon_s$', 'supply elasticity')]
out = ['% Written by fill_slides.py from writing/tables/tab_eleven.tex. Do not edit.',
       '\\begin{tabular}{@{}llrrr@{}}', '\\toprule', 'Parameter & Moment and source & Data & Model & Value\\\\', '\\midrule']
for sym, lab in PARAMS:
    c = T3[sym]
    out.append(f'{sym}, {lab} & {c[3]} & {c[4]} & {c[5]} & {c[6]}\\\\')
out += ['\\bottomrule', '\\end{tabular}']
open(os.path.join(HERE, 'gen_params.tex'), 'w').write('\n'.join(out) + '\n')

T4 = {re.sub(r'\$\^\{[a-z]\}\$', '', k): v for k, v in rows(os.path.join(TAB, 'tab_untargeted.tex')).items()}
UNTARGETED = [('Abstinence, contingent over unconditional housing, ratio', None),
              ('Three-year mortality, households with SMI put on the street, pp', None),
              ('Child of a SUD parent acquires a SUD, odds ratio', None),
              ('Children living with a parent with a SUD, \\%', None),
              ('Unemployment given a SUD', 'Unemployment given a SUD, \\%'),
              ('Drug use with SMI over without, ratio', None),
              ('Drug deaths as a share of deaths, 26--44', 'Drug deaths as a share of deaths, ages 26--44, \\%'),
              ('Participation (extensive margin)', 'Participation price elasticity'),
              ('Intensive margin (users)', 'Intensive price elasticity, users'),
              ('Homeless adult had a homeless parent, odds ratio', None),
              ('Employed share of the homeless', 'Employed share of the homeless, \\%')]
out = ['% Written by fill_slides.py from writing/tables/tab_untargeted.tex. Do not edit.',
       '\\begin{tabular}{@{}lrrl@{}}', '\\toprule', 'Moment & Data & Model & Source\\\\', '\\midrule']
for lab, show in UNTARGETED:
    c = T4[lab]
    out.append(f'{show or lab} & {c[1]} & {c[2]} & {c[3]}\\\\')
out += ['\\bottomrule', '\\end{tabular}']
open(os.path.join(HERE, 'gen_untargeted.tex'), 'w').write('\n'.join(out) + '\n')

t7 = open(os.path.join(TAB, 'tab_alttrans.tex')).read()
t7 = t7[t7.index('\\begin{tabular}'):t7.index('\\end{tabular}') + len('\\end{tabular}')]
open(os.path.join(HERE, 'gen_alttrans.tex'), 'w').write(
    '% Written by fill_slides.py from writing/tables/tab_alttrans.tex. Do not edit.\n' + clean(t7) + '\n')

# ------------------------------------------------------------------------------------------------------- the fill
src = open(os.path.join(HERE, 'slides.src.tex')).read()


def value(k):
    if k in DECK:
        return DECK[k]
    assert k in N, f'@@{k}@@: no such name in the paper or the deck'
    return paper(k)


def fill_raw(m):
    return value(m.group(1))


def fill_text(m):
    v = value(m.group(1))
    return '$-$' + v[1:] if re.match(r'-\d', v) else v


out = re.sub(r'@@=([A-Za-z0-9_]+)@@', fill_raw, src)
out = re.sub(r'@@([A-Za-z0-9_]+)@@', fill_text, out)
assert '@@' not in out, 'an unfilled @@ is left in the deck'
used = sorted(set(re.findall(r'@@=?([A-Za-z0-9_]+)@@', src)))
open(os.path.join(HERE, 'slides.tex'), 'w').write(
    '% Written by fill_slides.py from slides.src.tex, with the paper\'s own numbers. Edit slides.src.tex, not this file.\n'
    + out)
print(f'slides.tex: {len(used)} names filled, {sum(1 for k in used if k in DECK)} of them the deck\'s own')
