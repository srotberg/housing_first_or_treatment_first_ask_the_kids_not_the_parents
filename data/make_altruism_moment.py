"""
The moment that identifies parental altruism.

WHY THIS MOMENT AND NOT A BORROWED PARAMETER

omega is the weight a parent puts on its child's lifetime value. In this model
the only thing it does is make a parent use fewer drugs than an otherwise
identical household without a child, because using raises the chance of a
disorder and the disorder lowers the child's permanent income. So the moment
that identifies it is exactly that: the difference in drug use between adults
with and without a child in the household, holding everything else fixed.

That is a revealed behavioural moment from the survey the paper already uses for
the participation rate and for u_1, rather than an altruism parameter borrowed
from a transfer literature whose model is not this one. Two alternatives were
considered and rejected:

    THE TRANSFER FLOW. Calibrate omega so the model reproduces the observed
    flow of bequests and inter vivos transfers. It does not work here, because
    estates in this model accrue to the government rather than to children, so
    omega does not move saving at all and the transfer flow does not identify
    it. Restoring bequests to children only to identify omega would undo a
    change made for a different reason.

    A GENERATIONAL DISCOUNT. beta^30 = 0.74 at an annual 0.99. It is an anchor
    for the order of magnitude, not an estimate, and it is not disciplined by
    anything about drugs.

WHAT THE RAW COMPARISON GETS WRONG

Unadjusted, adults with a child in the household use almost exactly as much as
those without: 16.34 against 16.63 per cent past month. That is composition.
Parents are older, richer and far more likely to be married, and all three lower
drug use on their own. Reweighting parents to the joint age by income by sex by
marital distribution of non parents opens a gap of 2.6 percentage points, from
16.71 to 14.11 per cent, a ratio of 0.845.

The age pattern is what makes this credible rather than mechanical: the gap is
widest at 35 to 49, ratio 0.60, and at 30 to 34, ratio 0.71, which is the child
rearing window, and it narrows at 50 to 64 when children have left.

THE CAVEAT, AND WHY IT MAKES THIS AN UPPER BOUND

Selection runs the wrong way and cannot be signed away. Heavy users lose custody,
so some of the gap is children being absent from users' households rather than
users cutting down for their children. The measured gap is therefore an UPPER
bound on what altruism explains, and zero is the lower bound. omega is reported
across that range with the threshold at which any conclusion changes, which is
the same discipline the other externality parameters are held to.

HOW IT MAPS INTO THE MODEL

Every household in the model has a child, so there is no parent and non parent
comparison to run directly. The mapping is the counterfactual instead: omega is
the entire reason a household in this model uses less than it otherwise would,
so switching altruism off at the calibrated parameters must raise drug use by
1/0.845 - 1 = 18.3 per cent. That is the calibration condition.

Run:  python3 make_altruism_moment.py
"""

import os
import numpy as np
import pandas as pd

# The full NSDUH 2024 public use file, tab delimited. Only these columns are
# read: the file is 390 MB and about 2,800 columns wide.
COLS = {'wt': 'ANALWT2+AF8-C', 'age3': 'AGE3', 'sex': 'IRSEX',
        'marit': 'IRMARIT', 'ki17': 'IRKI17+AF8-2', 'pinc': 'IRPINC3',
        'illyr': 'ILLYR', 'illmon': 'ILLMON'}

# AGE3 categories. The model's population is 26 and over, which is 7 and up.
AGE_LABEL = {7: '26-29', 8: '30-34', 9: '35-49', 10: '50-64', 11: '65+'}
CELLS = ['age3', 'pinc', 'sex', 'marit']


def load(path):
    with open(path) as f:
        hdr = f.readline().rstrip('\n').split('\t')
    pos = {k: hdr.index(v) for k, v in COLS.items()}
    keys = list(pos)
    rows = []
    with open(path) as f:
        f.readline()
        for line in f:
            p = line.rstrip('\n').split('\t')
            rows.append([p[pos[k]] for k in keys])
    d = pd.DataFrame(rows, columns=keys).apply(pd.to_numeric, errors='coerce')
    d = d[d.age3 >= 7].copy()
    # IRKI17_2 is a recode: 1 is no children under 18 in the household, 2, 3
    # and 4 are one, two, and three or more.
    d['kid'] = (d.ki17 >= 2).astype(int)
    return d


def wmean(g, c):
    return float(np.average(g[c], weights=g.wt))


def gap(d, outcome='illmon'):
    """Raw and composition adjusted parent minus non parent difference."""
    p, n = d[d.kid == 1], d[d.kid == 0]
    raw = (wmean(p, outcome), wmean(n, outcome))

    # Reweight parents to the NON PARENTS' joint distribution over the cells,
    # so the comparison is within age, income, sex and marital status rather
    # than across them. Doing it one variable at a time leaves most of the
    # composition in: parents are older AND richer AND married.
    w0 = n.groupby(CELLS).wt.sum()
    u1 = p.groupby(CELLS).apply(lambda x: wmean(x, outcome), include_groups=False)
    u0 = n.groupby(CELLS).apply(lambda x: wmean(x, outcome), include_groups=False)
    common = u0.index.intersection(u1.index)
    sh = w0.loc[common] / w0.loc[common].sum()
    adj = (float((sh * u1.loc[common]).sum()), float((sh * u0.loc[common]).sum()))
    cover = float(w0.loc[common].sum() / w0.sum())
    return raw, adj, cover, len(common)


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'NSDUH_2024_Tab.csv'
    d = load(path)
    print('=' * 72)
    print('PARENTAL ALTRUISM: the drug use gap between adults with and without')
    print('a child in the household, NSDUH 2024, ages 26 and over, weighted')
    print('=' * 72)
    for outcome, name in (('illmon', 'past month'), ('illyr', 'past year')):
        raw, adj, cover, ncell = gap(d, outcome)
        print(f'\n{name} illicit drug use')
        print(f'   raw          with a child {100*raw[0]:6.2f}%   '
              f'without {100*raw[1]:6.2f}%   ratio {raw[0]/raw[1]:.3f}')
        print(f'   reweighted   with a child {100*adj[0]:6.2f}%   '
              f'without {100*adj[1]:6.2f}%   ratio {adj[0]/adj[1]:.3f}')
        print(f'   implied rise in use with altruism off : '
              f'{100*(adj[1]/adj[0]-1):.1f}%')
        print(f'   {ncell} cells, {100*cover:.1f}% of non parent weight')

    print('\nby age band, past month, unadjusted within band')
    for a, g in d.groupby('age3'):
        p, n = g[g.kid == 1], g[g.kid == 0]
        if len(p) > 50 and len(n) > 50:
            print(f'   {AGE_LABEL.get(a, a):6s} without {100*wmean(n,"illmon"):6.2f}%'
                  f'   with {100*wmean(p,"illmon"):6.2f}%'
                  f'   ratio {wmean(p,"illmon")/wmean(n,"illmon"):.3f}')
