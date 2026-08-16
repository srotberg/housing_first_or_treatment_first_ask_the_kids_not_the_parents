"""
The stylized model's two figures.

    1  WHO USES.  The gain from using, by income, with each channel
       configuration recalibrated to the same 5.13 percent participation rate.
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
from stylized import P, with_, use_prob, aggregates
from calibrate import YG, W, bracket, stats

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'figures'))

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
OFF = dict(kap=0.0, u1=P.u0, h_hl=P.h_sm)


def _scaled(base, which, s):
    kw = dict(OFF)
    if which == 'mortality':
        kw.update(kap=s * base.kap)
    else:
        # the street's housing services belong HERE, not with mortality. An
        # earlier version had h_hl in the mortality group, which quietly put an
        # unemployment consequence inside the mortality curve.
        kw.update(u1=P.u0 + s * (base.u1 - P.u0),
                  h_hl=P.h_sm * (base.h_hl / P.h_sm) ** s)
    par = with_(base, **kw)
    # b is recalibrated at EVERY point, so participation is 5.13 percent all
    # along both curves and the only thing moving is WHO uses
    return with_(par, b=bracket(par, 'b', 'part', 1e-5, 0.60, iters=22))


def fig_who_uses(base):
    """Figure 1: how strong must each channel be to move use to the bottom."""
    plt = style()
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    sc = np.linspace(0.0, 1.0, 11)
    curves = {}
    for which, col, ls, mk in (('mortality', '#2C6FAD', '-', 'o'),
                               ('unemployment', '#D9822B', '--', 's')):
        r_ = [stats(_scaled(base, which, s))['r_use'] for s in sc]
        curves[which] = r_
        ax.plot(100 * sc, r_, ls, color=col, marker=mk, ms=4.5,
                label=f'{which} channel')
    ax.axhline(1.0, color='0.3', lw=1.1)
    ax.set_yscale('log')
    # A log axis prints its own minor labels (3x10^-1 and so on) ON TOP of the
    # ticks set below, which is what made the earlier version unreadable. Both
    # the minor locator and the minor formatter have to be silenced.
    from matplotlib.ticker import NullFormatter, NullLocator, FixedLocator
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.5, 1.0, 2.0, 4.0]))
    ax.set_yticklabels(['0.1', '0.2', '0.5', '1.0', '2.0', '4.0'])
    ax.set_ylim(0.1, 6.0)
    ax.set_xlim(-3, 103)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Strength of the channel, percent of its calibrated value')
    ax.set_ylabel('Mean income of users / population mean')
    # legend OUTSIDE the plotting area, so it cannot sit on the lines
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=2,
              fontsize=9.5)
    # ABOVE the line the ratio exceeds one, so users are RICHER. An earlier
    # version had these two labels the wrong way round.
    ax.annotate('users are RICHER than average',
                xy=(0.985, 0.985), xycoords='axes fraction', ha='right',
                va='top', fontsize=8.5, color='0.4')
    ax.annotate('users are POORER than average',
                xy=(0.985, 0.015), xycoords='axes fraction', ha='right',
                va='bottom', fontsize=8.5, color='0.4')
    fig.tight_layout()
    save(fig, 'stylized_who_uses')
    return sc, curves


def fig_moral_hazard(base):
    """Figure 2: the two forces as the voucher becomes more generous."""
    plt = style()
    pVs = np.array([0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0])
    H = np.array([stats(with_(base, pV=p, policy='HF'))['part'] for p in pVs])
    T = np.array([stats(with_(base, pV=p, policy='TF'))['part'] for p in pVs])

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    # The two shaded regions must be DISJOINT or the picture is mud. An earlier
    # version shaded (TF, HF) and (TF, no programme), which overlap everywhere.
    # Here the red band is the moral hazard, the blue band above it is what
    # Housing First delivers net, and the two together are the value of life.
    ax.fill_between(pVs, 100 * T, 100 * H, color='#C0392B', alpha=0.16,
                    label='Moral hazard: Housing First $-$ Treatment First')
    ax.fill_between(pVs, 100 * H, 100 * T[0], color='#2C6FAD', alpha=0.16,
                    label='Net effect of Housing First')
    ax.plot(pVs, 100 * H, color='#C0392B', marker='o', ms=4.5,
            label='Housing First')
    ax.plot(pVs, 100 * T, color='#2C6FAD', marker='s', ms=4.5,
            label='Treatment First')
    ax.axhline(100 * T[0], color='0.45', lw=1.0, ls=':')
    ax.axvline(base.pV, color='0.45', lw=1.0, ls='--')
    ax.text(base.pV + 0.012, 100 * T[0] * 0.06, 'current programme',
            fontsize=8.5, color='0.4', rotation=90, va='bottom')
    ax.set_ylim(-0.45, 100 * T[0] * 1.22)
    ax.set_xlim(-0.02, 1.14)
    ax.text(0.02, 100 * T[0] + 0.14, 'No voucher programme', fontsize=8.5,
            color='0.4')
    # the value of life force is the WHOLE drop, so mark it as a span at the
    # right hand edge rather than as a region that overlaps the others
    xb = 1.075
    ax.annotate('', xy=(xb, 100 * T[0]), xytext=(xb, 100 * T[-1]),
                arrowprops=dict(arrowstyle='<->', color='#2C6FAD', lw=1.3))
    ax.text(xb - 0.015, 100 * (T[0] + T[-1]) / 2, 'Value of life',
            rotation=90, ha='right', va='center', fontsize=9, color='#2C6FAD')
    ax.text(0.62, 100 * (T[5] + H[5]) / 2, 'Moral hazard', fontsize=9,
            color='#C0392B', ha='center', va='center')
    ax.set_xlabel('Voucher generosity $\\pi_V$: '
                  'share of eligible households covered')
    ax.set_ylabel('Drug use participation rate, percent')
    h_, l_ = ax.get_legend_handles_labels()
    ax.legend([h_[2], h_[3]], [l_[2], l_[3]], loc='upper center',
              bbox_to_anchor=(0.46, 1.15), ncol=2, fontsize=9.5)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    fig.tight_layout()
    save(fig, 'stylized_moral_hazard')

    print('\n   participation, percent')
    print(f'     no voucher                {100*T[0]:6.2f}')
    print(f'     universal Treatment First {100*T[-1]:6.2f}'
          f'   value of life {100*(T[-1]-T[0]):+6.2f}')
    print(f'     universal Housing First   {100*H[-1]:6.2f}'
          f'   moral hazard  {100*(H[-1]-T[-1]):+6.2f}')
    print(f'     net effect of Housing First         {100*(H[-1]-H[0]):+6.2f}')
    return pVs, H, T


def fig_margins(base):
    """
    Figure 3: what the same policy dial does to the two outcomes the programme
    is actually for. Drug use is not the objective of a housing programme, and a
    reader shown only figure 2 could reasonably think Treatment First wins on
    every count. It does not.
    """
    plt = style()
    pVs = np.array([0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0])
    out = {}
    for pol in ('HF', 'TF'):
        m = [stats(with_(base, pV=p, policy=pol)) for p in pVs]
        out[pol] = dict(homeless=np.array([x['homeless'] for x in m]),
                        sud=np.array([x['sud'] for x in m]),
                        part=np.array([x['part'] for x in m]))

    out['use'] = {pol: np.array([x['part'] for x in
                                 [stats(with_(base, pV=p, policy=pol)) for p in pVs]])
                  for pol in ('HF', 'TF')}
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6))
    panels = ((axes[0], 'homeless', 'Homelessness rate, percent', '(a)'),
              (axes[1], 'part', 'Drug use, percent', '(b)'),
              (axes[2], 'sud', 'Share with a SUD, percent', '(c)'))
    for ax, key, lab, tag in panels:
        for pol, col, mk in (('HF', '#C0392B', 'o'), ('TF', '#2C6FAD', 's')):
            y = out[pol][key] if key in out[pol] else out['use'][pol]
            ax.plot(pVs, 100 * y, color=col, marker=mk, ms=4.0,
                    label='Housing First' if pol == 'HF' else 'Treatment First')
        ax.axvline(base.pV, color='0.55', lw=0.9, ls='--')
        ax.set_xlabel('Voucher generosity $\\pi_V$')
        ax.set_ylabel(lab)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(bottom=0.0)
        ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.set_title(tag, loc='left', fontsize=11, fontweight='bold')
    axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=2,
                   fontsize=9.5)
    save(fig, 'stylized_margins')

    print('\n   pi_V    homeless HF    homeless TF      disorder HF   disorder TF')
    for i, p in enumerate(pVs):
        print(f"   {p:4.2f}   {100*out['HF']['homeless'][i]:10.3f}%"
              f"   {100*out['TF']['homeless'][i]:10.3f}%"
              f"   {100*out['HF']['sud'][i]:12.3f}%"
              f"   {100*out['TF']['sud'][i]:10.3f}%")
    return pVs, out


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('figures')
    fig_who_uses(base)
    fig_moral_hazard(base)
    fig_margins(base)
