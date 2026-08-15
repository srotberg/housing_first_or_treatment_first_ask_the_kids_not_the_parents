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
    ('mortality only', dict(u1=P.u0, h_hl=P.h_sm),           '#2C6FAD', '--'),
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


# Everything the disorder does to you, switched off. Scaling a channel means
# moving its members from these values to their calibrated ones together.
OFF = dict(kap=0.0, kapH=0.0, u1=P.u0, h_hl=P.h_sm)


def _scaled(base, which, s):
    kw = dict(OFF)
    if which == 'mortality':
        kw.update(kap=s * base.kap, kapH=s * base.kapH)
    else:
        # the street's housing services belong HERE, not with mortality. An
        # earlier version had h_hl in the mortality group, which quietly put a
        # resource penalty inside the mortality curve.
        kw.update(u1=P.u0 + s * (base.u1 - P.u0),
                  h_hl=P.h_sm * (base.h_hl / P.h_sm) ** s)
    par = with_(base, **kw)
    # b is recalibrated at EVERY point, so participation is 5.13 per cent all
    # along both curves and the only thing moving is WHO uses
    return with_(par, b=bracket(par, 'b', 'part', 1e-5, 0.60, iters=22))


def fig_who_uses(base):
    """
    Figure 1: how strong does each consequence have to be to move drug use from
    the top of the income distribution to the bottom?

    An earlier version switched channels on and off and claimed only the
    mortality channel flipped the gradient. That is false in this model: with
    log utility a proportional wage penalty costs log(1 - xi) utils whatever
    your income, so it is a CONSTANT utility loss whose consumption value rises
    with income, exactly like a mortality penalty. Both channels flip it. The
    real question, and the one R1's comment 1(d) actually asks, is how MUCH of
    each is needed, and there the two are far apart.
    """
    plt = style()
    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    sc = np.linspace(0.0, 1.0, 11)
    for which, col, ls in (('mortality', '#2C6FAD', '-'),
                           ('resource', '#D9822B', '--')):
        r = [stats(_scaled(base, which, s))['r_use'] for s in sc]
        ax.plot(100 * sc, r, ls, color=col,
                label=f'{which} channel' + (': the disorder kills you' if which == 'mortality'
                      else ': it costs you a job, and\nthe home you can afford'))
    ax.axhline(1.0, color='0.35', lw=1.2)
    ax.text(2, 1.06, 'users earn the population average', fontsize=9, color='0.35')
    ax.set_yscale('log')
    ax.set_yticks([0.2, 0.5, 1.0, 2.0, 4.0])
    ax.set_yticklabels(['0.2', '0.5', '1', '2', '4'])
    ax.set_xlabel('strength of the channel, per cent of its calibrated value')
    ax.set_ylabel('income of users / population average')
    ax.set_title('What it takes to move drug use to the bottom',
                 loc='left', pad=12)
    ax.legend(loc='upper right', fontsize=9)
    fig.text(0.5, -0.075,
             'With no consequences at all, drug use sits at the TOP: users earn '
             '3.5 times the average, because drugs are a\nnormal good and a '
             'richer household gives up less utility per dollar. Both '
             'consequences flip that, but not at the\nsame price. The mortality '
             'channel crosses the line at under a fifth of its calibrated '
             'strength; the resource\nchannel needs about three fifths. The '
             'temptation parameter is recalibrated at every point, so '
             'participation is\n5.13 per cent all along both curves and the only '
             'thing moving is WHICH households use.',
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
