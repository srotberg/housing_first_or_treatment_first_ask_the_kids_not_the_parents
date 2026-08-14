"""
The stylised model's four results, and three figures built to be read.

Each result maps to a rung of the channel shutdown ladder in section 7 of the
paper. The small model is not a preview of the answer. Its job is to say which
parameter is responsible for which fact, so that when the ladder moves a number
in the calibrated model the reader already knows what it is evidence about.
"""

import os
import numpy as np
from stylized import P, with_, profile, moments, solve_late, OUT

# a lognormal income distribution, so the ratios mean what they mean in the data
YG = np.exp(np.linspace(np.log(0.15), np.log(5.0), 46))
W  = np.exp(-0.5 * ((np.log(YG) + 0.5 * 0.75**2) / 0.75)**2)

# The four channel configurations. MORTALITY is {kap, kapH} and RESOURCE is
# {xi, ellH}, because the disorder kills you directly and by making you homeless,
# and impoverishes you directly and through the cost of homelessness. Switching
# one member of a pair leaves the other running.
CASES = [('both channels', dict()),
         ('mortality only', dict(xi=0.0, ellH=0.0)),
         ('resource only',  dict(kap=0.0, kapH=0.0)),
         ('neither',        dict(kap=0.0, kapH=0.0, xi=0.0, ellH=0.0))]


def bcal(par, target=0.0513, lo=1e-4, hi=3.0, iters=17):
    """b is identified by the participation RATE, so bisect on it, in logs."""
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if moments(with_(par, b=mid), YG, W)['part'] > target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


# ---------------------------------------------------------------------------
def exp1():
    print('\n' + '=' * 78)
    print('1. WHICH CHANNEL PUTS DRUG USE AT THE BOTTOM OF THE DISTRIBUTION')
    print('   b is RECALIBRATED to a 5.13 per cent participation rate in every')
    print('   row, so the rows differ only in which channel is switched on and')
    print('   the LEVEL of use is held fixed across them.')
    print('=' * 78)
    print(f"{'channels on':18s}{'b':>9s}{'r_use':>9s}{'r_sud':>9s}"
          f"{'elasticity':>13s}")
    rows = {}
    for name, kw in CASES:
        par = with_(P(), **kw)
        b = bcal(par)
        m = moments(with_(par, b=b), YG, W)
        print(f'{name:18s}{b:9.4f}{m["r_use"]:9.3f}{m["r_sud"]:9.3f}'
              f'{m["elast"]:13.3f}')
        rows[name] = (b, m)
    print(f"\n   {'data (NSDUH 26+)':18s}{'':6s}{0.951:9.3f}{0.687:9.3f}")
    return rows


def exp2():
    print('\n' + '=' * 78)
    print('2. THE LEVEL AND THE GRADIENT ARE IDENTIFIED BY DIFFERENT MOMENTS')
    print('=' * 78)
    print(f"{'b':>9s}{'participation':>15s}{'r_use':>9s}"
          f"{'r_use, no mortality':>22s}")
    rows = []
    for b in [0.0015, 0.003, 0.005, 0.008, 0.012, 0.018, 0.026]:
        m1 = moments(with_(P(), b=b), YG, W)
        m0 = moments(with_(P(), b=b, kap=0.0, kapH=0.0), YG, W)
        # an income ratio computed over an empty set of users is 0/0, so rows
        # where nobody uses are reported as blank rather than as a number
        f1 = f'{m1["r_use"]:9.3f}' if m1['part'] > 5e-3 else f'{"--":>9s}'
        f0 = f'{m0["r_use"]:22.3f}' if m0['part'] > 5e-3 else f'{"--":>22s}'
        print(f'{b:9.4f}{m1["part"]:15.3f}{f1}{f0}')
        rows.append((b, m1['part'], m1['r_use'] if m1['part'] > 5e-3 else np.nan,
                     m0['r_use'] if m0['part'] > 5e-3 else np.nan))
    return rows


def exp3():
    print('\n' + '=' * 78)
    print('3. THE VALUE OF LIFE CONSTANT CANNOT BE IDENTIFIED BY A GRADIENT')
    print('=' * 78)
    print(f"{'aleph':>8s}{'share with V<0':>17s}{'r_use':>9s}"
          f"{'b for 5.13%':>14s}")
    rows = []
    for al in [0.0, 0.5, 1.0, 2.0, 2.5, 4.0, 8.0]:
        par = with_(P(), aleph=al)
        neg = 0.0
        for y, wi in zip(YG, W / W.sum()):
            _, V2 = solve_late(par, y, 'HF')
            if V2[0, 0] < 0:
                neg += wi
        b = bcal(par)
        m = moments(with_(par, b=b), YG, W)
        print(f'{al:8.1f}{neg:17.3f}{m["r_use"]:9.3f}{b:14.4f}')
        rows.append((al, neg, m['r_use']))
    return rows


def exp4():
    print('\n' + '=' * 78)
    print('4. THE TWO FORCES: MORAL HAZARD AND THE VALUE OF LIFE')
    print('   A voucher removes the risk of homelessness. Under Housing First it')
    print('   arrives whatever the disorder status, under Treatment First only if')
    print('   the household is clean, so the only thing HF adds to TF is cover in')
    print('   the disorder state. The two columns are therefore the decomposition.')
    print('=' * 78)
    b = bcal(P())
    pVs = np.array([0.0, 0.10, 0.20, 0.30, 0.45, 0.60, 0.75, 0.90, 1.00])
    H, T = [], []
    for pv in pVs:
        par = with_(P(), b=b, pV=pv)
        H.append(moments(par, YG, W, 'HF')['part'])
        T.append(moments(par, YG, W, 'TF')['part'])
    H, T = np.array(H), np.array(T)
    print(f"{'pV':>7s}{'use, HF':>11s}{'use, TF':>11s}"
          f"{'value of life':>16s}{'moral hazard':>15s}{'net, HF':>11s}")
    for k, pv in enumerate(pVs):
        print(f'{pv:7.2f}{H[k]:11.4f}{T[k]:11.4f}'
              f'{100*(T[k]/T[0]-1):15.2f}%{100*(H[k]/T[k]-1):14.2f}%'
              f'{100*(H[k]/H[0]-1):10.2f}%')
    return pVs, H, T, b


# ---------------------------------------------------------------------------
# figures, one idea each
# ---------------------------------------------------------------------------
def _style():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.size': 11, 'figure.dpi': 170,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': True, 'grid.alpha': 0.25, 'grid.linewidth': 0.6,
        'legend.frameon': False, 'axes.labelsize': 11,
        'axes.titlesize': 12, 'lines.linewidth': 2.2})
    return plt


def _save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p + '.pdf', bbox_inches='tight')
    fig.savefig(p + '.png', bbox_inches='tight')
    print(f'   wrote {name}.pdf')


def fig_gradient(r1):
    """The result: participation by income, one line per channel configuration."""
    plt = _style()
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    style = {'neither':        ('#B4405A', ':',  'no penalty at all'),
             'resource only':  ('#D9822B', '--', 'resource channel only'),
             'mortality only': ('#2C6FAD', '-',  'mortality channel only'),
             'both channels':  ('#1B3B5F', '-',  'both channels')}
    for name in ['neither', 'resource only', 'mortality only', 'both channels']:
        col, ls, lab = style[name]
        _, m = r1[name]
        ax.plot(YG, 100.0 * m['p_use'], ls, color=col, label=lab,
                lw=2.8 if name == 'both channels' else 2.1)
    ax.set_xscale('log')
    ax.set_xticks([0.2, 0.5, 1.0, 2.0, 5.0])
    ax.set_xticklabels(['0.2', '0.5', '1', '2', '5'])
    ax.set_xlabel('permanent income, population mean $= 1$')
    ax.set_ylabel('drug use participation rate, per cent')
    ax.set_title('Only the mortality channel puts drug use at the bottom',
                 loc='left', pad=12)
    ax.legend(loc='best', fontsize=9.5)
    fig.text(0.5, -0.05,
             'The Stone Geary parameter $b$ is recalibrated to a 5.13 per cent '
             'participation rate in every case, so the four\nlines differ only in '
             'which channel operates, not in the level of use. The resource '
             'channel does not flip the gradient.',
             ha='center', fontsize=8.5, color='0.35')
    _save(fig, 'stylized_gradient')


def fig_decomposition(cross):
    """The two forces, with the gap between them shaded."""
    plt = _style()
    pVs, H, T, _ = cross
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.fill_between(pVs, 100 * T, 100 * H, color='#C0392B', alpha=0.15,
                    label='moral hazard, cover extended to the disorder state')
    ax.fill_between(pVs, 100 * T, 100 * T[0], color='#2C6FAD', alpha=0.15,
                    label='value of life, cover conditional on staying clean')
    ax.plot(pVs, 100 * H, '-', color='#C0392B', label='Housing First')
    ax.plot(pVs, 100 * T, '-', color='#2C6FAD', label='Treatment First')
    ax.axhline(100 * T[0], color='0.55', lw=1.0, ls=':')
    ax.text(0.015, 100 * T[0], ' no voucher', va='bottom', fontsize=9, color='0.4')
    ax.axvline(0.27, color='0.7', lw=1.0, ls='--')
    ax.text(0.285, ax.get_ylim()[0], ' current US rationing', fontsize=8.5,
            color='0.45', rotation=90, va='bottom')
    ax.set_xlabel('voucher generosity $\\pi_V$, share of eligible households covered')
    ax.set_ylabel('drug use participation rate, per cent')
    ax.set_title('Two forces, opposite signs, and both grow with generosity',
                 loc='left', pad=12)
    ax.legend(loc='best', fontsize=9)
    fig.text(0.5, -0.05,
             'Under Housing First a voucher arrives whatever the disorder status; '
             'under Treatment First only if the household is\nclean. The only '
             'thing the first adds to the second is cover in the disorder state, '
             'so the red band IS the moral hazard.',
             ha='center', fontsize=8.5, color='0.35')
    _save(fig, 'stylized_decomposition')


def fig_identification(r2, r3):
    """Level against gradient, and why the value of life needs a level target."""
    plt = _style()
    fig, ax = plt.subplots(1, 2, figsize=(11.4, 4.4))

    bs = np.array([r[0] for r in r2])
    ax[0].plot(bs, 100 * np.array([r[1] for r in r2]), 'o-', color='#1B3B5F',
               label='participation rate (left)')
    ax[0].set_xscale('log')
    ax[0].set_xlabel('Stone Geary parameter $b$')
    ax[0].set_ylabel('participation rate, per cent')
    a2 = ax[0].twinx()
    a2.plot(bs, [r[2] for r in r2], 's--', color='#2C6FAD', ms=5,
            label='income ratio, mortality ON (right)')
    a2.plot(bs, [r[3] for r in r2], '^:', color='#D9822B', ms=5,
            label='income ratio, mortality OFF (right)')
    a2.axhline(1.0, color='0.6', lw=1.0)
    a2.set_ylabel('income of users / population average')
    a2.grid(False); a2.spines['top'].set_visible(False)
    ax[0].set_title('(a) $b$ moves the level; the mortality channel\n'
                    'decides which side of one the gradient is on',
                    loc='left', fontsize=11)
    h1, l1 = ax[0].get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    ax[0].legend(h1 + h2, l1 + l2, loc='center right', fontsize=8.5)

    al = np.array([r[0] for r in r3])
    ax[1].plot(al, 100 * np.array([r[1] for r in r3]), 'o-', color='#C0392B',
               label='households who would rather be dead (left)')
    ax[1].set_xlabel('value of life constant $\\aleph$')
    ax[1].set_ylabel('share with negative continuation value, per cent')
    b2 = ax[1].twinx()
    b2.plot(al, [r[2] for r in r3], 's--', color='#2C6FAD', ms=5,
            label='income of users / average (right)')
    b2.axhline(1.0, color='0.6', lw=1.0)
    b2.set_ylabel('income of users / population average')
    b2.grid(False); b2.spines['top'].set_visible(False)
    ax[1].set_title('(b) the gradient barely moves across the range\n'
                    'where the model silently breaks', loc='left', fontsize=11)
    h1, l1 = ax[1].get_legend_handles_labels()
    h2, l2 = b2.get_legend_handles_labels()
    ax[1].legend(h1 + h2, l1 + l2, loc='center right', fontsize=8.5)

    fig.tight_layout()
    _save(fig, 'stylized_identification')


if __name__ == '__main__':
    r1 = exp1()
    r2 = exp2()
    r3 = exp3()
    cr = exp4()
    print('\nfigures')
    fig_gradient(r1)
    fig_decomposition(cr)
    fig_identification(r2, r3)
