"""
Catch numbers that are typed into the paper instead of generated.

WHY. Every number in the prose should arrive as an @@placeholder@@ filled by
code/stylized/fill.py, which reads it from the model or, for the quantitative
model's targets, from the Fortran declaration by way of
code/paper/sync_tables.py. A number typed straight into the text is a number
that will be wrong after the next sweep, and nothing else in the pipeline
notices: LaTeX compiles a stale figure exactly as happily as a fresh one.

WHAT IT REPORTS. Any literal in the prose that equals a value one of the tables
states. It is not a proof of correctness -- a typed number that happens to
match nothing is not caught -- but it is what catches the case that actually
happens, which is a target changing in one place and not the other.

FALSE POSITIVES ARE EXPECTED and are the reason this prints rather than fails
by default. Ages, sample sizes, years, page numbers in the bibliography and
odds ratios from other papers all collide with parameter values: 1.80 is both
the rental ladder's curvature and Bassuk's odds ratio, 0.50 is both the
replacement rate and the employment rate of the homeless. Anything genuinely
new should be routed through a placeholder; anything that is a coincidence
should be added to ALLOW below with a reason.

Run:  python3 check_numbers.py [--strict]
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # writing/: these tools live in writing/tools/
SRC = os.path.join(HERE, 'housing_first_or_treatment_first.src.tex')
TAB = os.path.join(HERE, 'tables')

# (value, fragment of the sentence) pairs that are known coincidences
ALLOW = [
    # DEGENHARDT ET AL.'S POOLED SMR, 14.7, a literature estimate quoted in the
    # kappa_phi_d entry (1 October); it coincides with the model's unemployment
    # given a SUD in Table 6 and has nothing to do with it.
    ('14.7', 'standardised mortality ratio of'),
    # LITERATURE ODDS RATIOS, quoted in the prose and in the Data column of
    # tab_untargeted.tex, which calib_tables.py writes. They are estimates read
    # off the studies, not anything a model computes, and the validation table
    # moved into tables/ on 28 September, which is when the checker began to see
    # both copies. Bassuk et al. (1997); Mellentin et al. (2016), Yoon et al. (2013).
    ('1.8', 'odds ratios of'), ('2.4', 'odds ratios of'),
    ('1.8', 'in the data (Bassuk'), ('2.4', 'in the data (Bassuk'),
    # Mellentin et al. (2016) and Yoon et al. (2013); keyed without the red wrapper,
    # which comes and goes as the author clears red
    ('1.44', 'to acquire a SUD, at'), ('2.51', 'to acquire a SUD, at'),
    # Milby et al. (2005)'s weeks abstinent in the literature review; Table 2's 6.60 is the stylized model's aleph
    # (8 October), unrelated
    ('6.60', 'weeks abstinent in the arm housed'),
    # Heiberg et al. (2018)'s standardised mortality ratio; the table's 6.6 is an unrelated TEDS-A share
    ('6.6', 'Heiberg et al.\\ (2018) at'),
    # Olmstead et al. (2015)'s heroin elasticity; the table's 0.8 is an unrelated share
    ('0.8', 'elasticity for heroin at'),
    ('1.44', 'of Mellentin et al.'), ('2.51', 'of Mellentin et al.'),   # the same two, in Section 3's stage 2
    ('2.5', '(Mellentin et al.'),
    # a demand elasticity bound in the literature review; the table's 0.8 is
    # the model's share of the homeless aged 65 and over
    ('0.8', 'intensive margin is the smaller'),
    ('1.80', 'odds ratios'),          # Bassuk et al., not the ladder curvature
    ('2.41', 'odds ratios'),
    ('0.40', 'social security'),      # the retirement replacement rate
    # Milby et al. (2005)'s weeks abstinent and Nielsen et al. (2017)'s hazard ratio; the long-run
    # table's 4.48 (drug use with an elastic supply) and 2.74 (its CEV) are unrelated
    ('4.48', 'weeks against'), ('4.48', 'in the homeless, so housing'),
    ('2.74', 'opioid use disorder'),
    ('25', 'ages'), ('25', '25 to 44'), ('25', '25--34'), ('25', '25--48'),
    ('30', 'Housing costs above'), ('30', 'quadratic in age'),
    ('35', '35 to 54'), ('35', '35--44'),
    ('50', 'per cent of the way'), ('50', 'Housing costs above'),
    ('55', '55 to 64'), ('55', '55--64'), ('55', '55--68'),
    ('3.00', 'wealth over output'),
    # numbers that collide with a table cell but are a different quantity
    # the age profile of homelessness, whose 45--54 cell is 0.250 per cent. It
    # collides with zeta_DI's 0.25 replacement rate, a different quantity in a
    # different table, and the collision only appeared when eta_DI and
    # zeta_DI's rows began exporting numbers at all.
    ('0.250', 'Homelessness rate'),
    ('0.80', 'conditional elasticity'),      # Olmstead, a demand elasticity
    ('0.55', 'elasticity of demand'),        # a demand elasticity, not the job finding rate
    ('1.46', 'elasticity of supply'),        # Mace, quoted as the elasticity
    ('1.46', 'stand in the ratio'),          # the rental ladder's own ratio
    ('273.10', 'CFR'),                       # a regulation number
    ('0.35', 'times'),                       # the arithmetic behind the theta moment
    ('1.1', 'against $0.99$'),               # an untargeted earnings share
    # The SCF net worth share of the bottom 5th percentile is -0.42 per cent.
    # It collides with cbar's row in tab_eleven, where 0.42 per cent is the
    # food stamp maximum allotment over labour income -- same digits, a
    # different quantity in a different table, and opposite in sign.
    ('0.42', 'Net worth shares'),
    ('9.1', 'by band'), ('1.1', 'by band'),  # the validation table's own row
    ('0.20', 'willing to pay'),              # kappa_x quoted in its source's units
    ('13.2', 'B25042'), ('62.7', 'B25042'),  # the ACS shares, quoted at their source
    ('24.1', 'middle unit size'),            # the middle share, likewise
    ('17.2', 'poorer half'),                 # already a placeholder elsewhere
    ('0.5', 'Frisch elasticity'),            # sigma_ell in its source's units
    ('9.1', 'race adjusted'), ('1.1', 'falling to'),
    ('0.25', 'Social Security Disability'),
]


def cells():
    out = {}
    for f in sorted(os.listdir(TAB)):
        if not f.startswith('tab_'):
            continue
        s = io.open(os.path.join(TAB, f), encoding='utf-8').read()
        for m in re.finditer(r'(?<![\w.])(\d+\.\d+)(?![\w])', s):
            out.setdefault(m.group(1), f)
    return out


def main(strict=False):
    s = io.open(SRC, encoding='utf-8').read()
    from marks import drop_marks          # struck deletions and notes are not prose
    s = drop_marks(s)
    s = s[s.index(r'\section{Introduction}'):]
    s = re.sub(r'@@[a-zA-Z_0-9]+@@', '', s)
    s = re.sub(r'\\(?:label|ref|eqref|cite[a-z]*|url|href)\{[^}]*\}', '', s)
    # LAYOUT LENGTHS ARE NOT QUANTITIES. A figure's width in \textwidth and the
    # matching width passed to \notes collide with parameter values often
    # enough to bury the real hits: 0.62 is both a figure width and a cell of
    # the welfare table.
    s = re.sub(r'width\s*=\s*[\d.]+\\textwidth', '', s)
    s = re.sub(r'\\notes\{[\d.]+\\textwidth\}', r'\\notes{}', s)
    tab = cells()
    hits = []
    for m in re.finditer(r'(?<![\w.\\])(\d+\.\d+)(?![\w])', s):
        v = m.group(1)
        if v not in tab:
            continue
        ctx = re.sub(r'\s+', ' ', s[max(0, m.start() - 80):m.start() + 50])
        if any(v == a and frag in ctx for a, frag in ALLOW):
            continue
        hits.append((v, tab[v], ctx))
    if not hits:
        print('   no typed numbers that a table also states')
        return 0
    print(f'   {len(hits)} literal(s) in the prose that a table also states:')
    for v, f, ctx in hits:
        print(f'   {v:8s} also in {f:18s} ...{ctx}...')
    print('\n   route each through a placeholder, or add it to ALLOW with a reason')
    return 1 if strict else 0


if __name__ == '__main__':
    sys.exit(main('--strict' in sys.argv))
