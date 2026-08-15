"""
The stylised model's two figures.

    1  WHO USES.  The gain from using, by income, with each channel
       configuration recalibrated to the same 5.13 per cent participation rate.
       Where the line is above zero the household uses. Only the mortality
       channel puts that region at the bottom of the income distribution.

    2  THE MORAL HAZARD.  Drug use under Housing First and under Treatment
       First as the voucher becomes more generous. The gap between them is the
       moral hazard: the effect of extending cover to households that already
       have the disorder.

Nothing else. The model is qualitative and these are the two things it is for.
"""

import json
import os
import numpy as np
from stylized import P, with_, use_choice, aggregates
from calibrate import YG, W, bracket, stats

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'figures'))

# The two channels move in GROUPS. The disorder kills you directly and by
# putting you on the street; it impoverishes you through unemployment, a wage
# penalty, and the housing it forces you down to. Switching one member of a
# group leaves the other running.
CONFIGS = [
    ('both channels',  {},                                   '#1B3B5F', '-'),
    ('mortality only', dict(xi=0.0, u1=P.u0),                '#2C6FAD', '--'),
    ('resource only',  dict(kap=0.0, kapH=0.0),              '#D9822B', ':'),
]


def style():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 11, 'figure.dpi': 170,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': 0.22,
                         'legend.frameon': False, 'lines.linewidth': 2.4})
    return plt


def save(fig, name):
    for ext in ('.pdf', '.png'):
        fig.savefig(os.path.join(OUT, name + ext), bbox_inches='tight')
    print(f'   wrote {name}.pdf')


def fig_who_uses(base):
    """Figure 1: the gain from using, by income, per channel configuration."""
    plt = style()
    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    ys = np.exp(np.linspace(np.log(0.15), np.log(4.0), 44))

    for name, kw, col, ls in CONFIGS:
        par = with_(base, **kw)
        # recalibrate the temptation parameter so every configuration has the
        # SAME participation rate; only then is the difference about mechanism
        par = with_(par, b=bracket(par, 'b', 'part', 1e-5, 0.30))
        g = np.array([use_choice(par, y)[0] for y in ys])
        ax.plot(ys, g, ls, color=col, label=name)
        pos = g > 0
        if pos.any():
            ax.plot(ys[pos], g[pos], ls, color=col, lw=4.0, alpha=0.30)

    ax.axhline(0.0, color='0.35', lw=1.2)
    ax.set_xscale('log')
    ax.set_xticks([0.2, 0.5, 1.0, 2.0, 4.0])
    ax.set_xticklabels(['0.2', '0.5', '1', '2', '4'])
    ax.set_xlabel('permanent income, population mean $=1$')
    ax.set_ylabel('gain from using drugs')
    ax.set_title('Who uses: only the mortality channel puts use at the bottom',
                 loc='left', pad=12)
    ax.legend(loc='best', fontsize=10)
    fig.text(0.5, -0.06,
             'Above the line the household uses; the thick segment is the use '
             'region. Every configuration is recalibrated to the\nsame 5.13 per '
             'cent participation rate, so the lines differ in WHICH households '
             'use, not how many. With only the\nresource channel the region '
             'sits at the top: a richer household gives up less utility per '
             'dollar of drugs, and a\npenalty proportional to income cannot '
             'outrun that. A mortality penalty can, because it destroys a '
             'continuation\nvalue that rises with income.',
             ha='center', fontsize=8.6, color='0.35')
    save(fig, 'stylized_who_uses')


def fig_moral_hazard(base):
    """Figure 2: the two policy forces as generosity rises."""
    plt = style()
    pVs = np.array([0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0])
    H = np.array([stats(with_(base, pV=p, policy='HF'))['part'] for p in pVs])
    T = np.array([stats(with_(base, pV=p, policy='TF'))['part'] for p in pVs])

    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    ax.fill_between(pVs, 100 * T, 100 * H, color='#C0392B', alpha=0.16,
                    label='moral hazard: cover extended to the disorder state')
    ax.fill_between(pVs, 100 * T, 100 * T[0], color='#2C6FAD', alpha=0.16,
                    label='value of life: cover conditional on staying clean')
    ax.plot(pVs, 100 * H, color='#C0392B', label='Housing First')
    ax.plot(pVs, 100 * T, color='#2C6FAD', label='Treatment First')
    ax.axhline(100 * T[0], color='0.5', lw=1.0, ls=':')
    ax.text(0.012, 100 * T[0], ' no voucher', va='bottom', fontsize=9,
            color='0.4')
    ax.axvline(0.27, color='0.7', lw=1.0, ls='--')
    ax.text(0.285, ax.get_ylim()[0], ' US rationing', rotation=90, va='bottom',
            fontsize=8.6, color='0.45')
    ax.set_xlabel('voucher generosity: share of eligible households covered')
    ax.set_ylabel('drug use participation rate, per cent')
    ax.set_title('The moral hazard is the gap between the two policies',
                 loc='left', pad=12)
    ax.legend(loc='best', fontsize=9.5)
    fig.text(0.5, -0.06,
             'Under Housing First a voucher arrives whatever the disorder '
             'status; under Treatment First only if the household is\nclean. '
             'The only thing the first adds to the second is cover in the '
             'disorder state, so the red band IS the moral\nhazard. Both forces '
             'grow with generosity and they work in opposite directions, which '
             'is why the net effect of\nhousing assistance on drug use is not '
             'signed by theory.',
             ha='center', fontsize=8.6, color='0.35')
    save(fig, 'stylized_moral_hazard')

    # in percentage POINTS, not ratios: under universal Treatment First nobody
    # uses at all, so a ratio is undefined. That is the sharpness of a model
    # with no preference heterogeneity, and it is the honest way to report it.
    print(f"\n   at universal provision, participation in percentage points")
    print(f"     no voucher                {100*T[0]:6.2f}")
    print(f"     Treatment First           {100*T[-1]:6.2f}"
          f"   value of life {100*(T[-1]-T[0]):+6.2f} pp")
    print(f"     Housing First             {100*H[-1]:6.2f}"
          f"   moral hazard  {100*(H[-1]-T[-1]):+6.2f} pp")
    print(f"     net effect of Housing First          "
          f"{100*(H[-1]-H[0]):+6.2f} pp")


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('figures')
    fig_who_uses(base)
    fig_moral_hazard(base)
