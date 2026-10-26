"""
Drug use by income relative to the mean, the Housing First benchmark against NSDUH 2024 (Section 5.3, Block 2).

usage: python3 code/paper/use_by_income_figure.py [--from-log CF_LOG]
       reads  results/use_by_income/benchmark_useinc.txt (the model) and data/NSDUH_2024.dta (the data)
       writes writing/figures/use_by_income.{pdf,png} and the x_ui_* names in code/paper/results_numbers.json
       --from-log first rewrites the results file from the LAST 'DIAG USEINC' block of a benchmark run's cf.log

The author, 26 October: "So for each income to average income showing the use rate. Data and model", then "This is
fantastic and should be in the validation". The calibration targets only the users' average income (kappa_phi_d, 0.74 of
the mean); this shows the whole profile.

THE DATA. Adults aged 26 and over in NSDUH 2024, weighted (analwt2_c); a user is anyone with a drug use disorder of any
severity (svyrdudany 1-3), the definition behind the participation target b (Section 5.1); income is total personal
income in its seven bands (irpinc3), each placed at its midpoint ($90,000 for the open top band), relative to the
weighted mean of those midpoints.

THE MODEL. The benchmark (the corrected Housing First, results/decomp_2c_shares_Cu/arm_tf/null, re-solved with a
print-only diagnostic, code/paper/use_by_income/patch_useinc.py): every household's mass and interest-inclusive income
(income_2, the y_u numerator's concept) in 400 bins of width 0.025, and the users under the y_u guard, character for
character. The bins are grouped into the data's seven bands, each edge taken relative to the data's mean, so the two
lines share their bands; a band's use rate is its users over its households.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'use_by_income', 'benchmark_useinc.txt')
DTA = os.path.join(ROOT, 'data', 'NSDUH_2024.dta')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
sys.path.insert(0, os.path.join(ROOT, 'code', 'stylized'))

MID = {1: 5000, 2: 15000, 3: 25000, 4: 35000, 5: 45000, 6: 62500, 7: 90000}
EDGE = [0, 10000, 20000, 30000, 40000, 50000, 75000, np.inf]
BLUE, ORANGE = '#2C6FAD', '#D9822B'


def from_log(log):
    """the last DIAG USEINC block of a run's log, to the results file, with its source"""
    L = open(log, errors='replace').read().splitlines()
    end = max(i for i, l in enumerate(L) if 'DIAG USEINC END' in l)
    beg = max(i for i, l in enumerate(L[:end]) if 'DIAG USEINC BEGIN' in l)
    rows = [l.split()[2:] for l in L[beg + 1:end] if l.strip().startswith('DIAG USEINC')]
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, 'w') as f:
        f.write(f'# the Housing First benchmark by income, from the last DIAG USEINC block of {log}\n')
        f.write('# bin (width 0.025 from -1)  households  users  households x income  users x income\n')
        for r in rows:
            f.write(' '.join(r) + '\n')


def model():
    M = np.loadtxt(RES)
    return M[:, 1], M[:, 2], M[:, 3], M[:, 4]


def data():
    df = pd.read_stata(DTA, columns=['age3', 'analwt2_c', 'irpinc3', 'svyrdudany'])
    d = df[df.age3 >= 7]
    w = d.analwt2_c.values.astype(float)
    x = d.irpinc3.map(MID).values.astype(float)
    sud = np.isin(pd.to_numeric(d.svyrdudany, errors='coerce').values, [1, 2, 3])
    mean = np.sum(w * x) / np.sum(w)
    rate = [100 * np.sum(w[(d.irpinc3 == k).values & sud]) / np.sum(w[(d.irpinc3 == k).values]) for k in sorted(MID)]
    return rate, mean, np.sum(w[sud] * x[sud]) / np.sum(w[sud]) / mean


def main():
    if '--from-log' in sys.argv:
        from_log(sys.argv[sys.argv.index('--from-log') + 1])
    dy, dmean, d_yu = data()
    mass, users, inc, uinc = model()
    mmean = inc.sum() / mass.sum()
    rel = inc / np.maximum(mass, 1e-300) / mmean
    edges = [e / dmean for e in EDGE]
    my = []
    for a, b in zip(edges[:-1], edges[1:]):
        s = (rel >= a) & (rel < b) if a > 0 else (rel < b)
        my.append(100 * users[s].sum() / mass[s].sum())
    m_yu = uinc.sum() / users.sum() / mmean
    print(f'data: users\' income / mean {d_yu:.3f}; model {m_yu:.3f}, users {100 * users.sum() / mass.sum():.2f} per cent')
    for i in range(7):
        print(f'  band {i + 1}: data {dy[i]:5.2f}  model {my[i]:5.2f}')

    import run
    plt = run.style()
    lab = [f'under {edges[1]:.2f}'] + [f'{edges[i]:.2f}–{edges[i + 1]:.2f}' for i in range(1, 6)] + \
          [f'{edges[6]:.2f} and over']
    X = np.arange(7)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(X, dy, '-o', color=ORANGE, lw=2.0, ms=7, mec='white', mew=1.2, label='NSDUH 2024')
    ax.plot(X, my, '-s', color=BLUE, lw=2.0, ms=7, mec='white', mew=1.2, label='Model')
    ax.set_xticks(X)
    ax.set_xticklabels(lab, fontsize=8.5)
    ax.set_xlabel('income relative to the mean', fontsize=9.5)
    ax.set_ylabel('percent using drugs', fontsize=9.5)
    ax.set_ylim(0, max(max(dy), max(my)) * 1.15)
    ax.legend(fontsize=9, loc='upper right')
    fig.tight_layout()
    run.save(fig, 'use_by_income')

    # THE SENTENCE TURNS WITH THE NUMBERS (writing/NUMBERS.md): each claim is printed only where the bands bear it out
    f1 = lambda v: f'{v:.1f}'
    mid = range(2, 6)
    out = {'x_ui_m_bot': f1(my[0]), 'x_ui_d_bot': f1(dy[0]), 'x_ui_m_top': f1(my[6]), 'x_ui_d_top': f1(dy[6]),
           'x_ui_lo': f'{edges[1]:.2f}', 'x_ui_hi': f'{edges[6]:.2f}', 'x_ui_mid_lo': f'{edges[2]:.2f}'}
    ends = (my[0] == max(my) and dy[0] == max(dy) and my[6] == min(my) and dy[6] == min(dy))
    s = ('As in the data, use is highest at the bottom of the income distribution and lowest at the top: '
         f'${f1(my[0])}$ percent of households with less than ${edges[1]:.2f}$ of the mean income use drugs, against '
         f'${f1(dy[0])}$ percent in NSDUH 2024, and ${f1(my[6])}$ percent of those with more than ${edges[6]:.2f}$ times '
         f'the mean, against ${f1(dy[6])}$ percent.' if ends else
         f'${f1(my[0])}$ percent of households with less than ${edges[1]:.2f}$ of the mean income use drugs, against '
         f'${f1(dy[0])}$ percent in NSDUH 2024, and ${f1(my[6])}$ percent of those with more than ${edges[6]:.2f}$ times '
         f'the mean, against ${f1(dy[6])}$ percent.')
    m_lo, m_hi = min(my[i] for i in mid), max(my[i] for i in mid)
    d_lo, d_hi = min(dy[i] for i in mid), max(dy[i] for i in mid)
    if m_hi < d_lo:
        s += (f' Between ${edges[2]:.2f}$ and ${edges[6]:.2f}$ times the mean, use in the model is '
              + ('flatter and ' if m_hi - m_lo < d_hi - d_lo else '')
              + f'lower than in the data, ${f1(m_lo)}$ to ${f1(m_hi)}$ percent against ${f1(d_lo)}$ to ${f1(d_hi)}$.')
        if my[0] > dy[0] and m_yu < d_yu:
            s += (' Both differences lower the average income of users in the model, which is why it falls short of its '
                  'target in Table~\\ref{tab:eleven}.')
    out['x_ui_sentence'] = s
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print('use_by_income:', s)


if __name__ == '__main__':
    main()
