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
from calibrate import YG, W, bracket, stats, TARGET


# HOW FAR PAST THE CALIBRATED STRENGTH THE CHANNEL SCAN RUNS. Figure 2's
# horizontal axis ends here and three sentences in Section 3.4 quote it, so it
# is a constant rather than a literal inside the scan: fill.py exports it as
# @@scanhi_pc@@ and the prose reads it from there.
SCAN_HI = 2.0     # the author, 29 September: from nothing to twice the penalty

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
# READ OFF THE BASE, NOT OFF THE CLASS DEFAULT. The small unit is now tied to a
# calibrated standard unit, so P.h2 is a stale starting value rather than the
# size the model was solved at, and taking the endpoint from it would put the
# street somewhere other than "as good as the small unit".
def _off(base):
    return dict(kap=0.0, u1=base.u0, h1=base.h2)


def _scaled(base, which, s):
    kw = _off(base)
    if which == 'mortality':
        kw.update(kap=s * base.kap)
    else:
        # the street's housing services belong HERE, not with mortality. An
        # earlier version had h1 in the mortality group, which quietly put an
        # unemployment consequence inside the mortality curve.
        kw.update(u1=base.u0 + s * (base.u1 - base.u0),
                  h1=base.h2 * (base.h1 / base.h2) ** s)
    par = with_(base, **kw)
    # b is recalibrated at EVERY point, so participation is 5.13 percent all
    # along both curves and the only thing moving is WHO uses.
    #
    # THE CEILING USED TO BE 0.60 AND IT BOUND. With the consequences switched
    # off drugs are a pure luxury, so it takes a very large Stone-Geary
    # endowment to hold participation down to 5.13 percent: the answer is b =
    # 1.15, and at a ceiling of 0.60 the bisection returned the ceiling and left
    # participation at 15.15 percent. Both curves therefore started from a point
    # with three times the drug use of every other point on them, while the note
    # said the amount of use was identical throughout. Raising the ceiling to 20
    # makes the claim true where it can be made true.
    q = with_(par, b=bracket(par, 'b', 'part', 1e-5, 20.0, iters=30))
    # AND WHERE IT CANNOT, SAY SO. Participation is a step function of b at the
    # far end of the mortality curve, jumping from 4.1 to 6.2 percent with
    # nothing in between, so no b delivers 5.13 there. That is a fact about the
    # model rather than a failure of the bisection, and it is printed rather
    # than passed over, because a point that misses the target is not comparable
    # with the points that hit it.
    got = stats(q)['part']
    if abs(got - TARGET['part']) > 5e-4:
        print(f'   NOTE: {which} at {s:.2f}: participation {100*got:.2f} percent, '
              f'not {100*TARGET["part"]:.2f}; no b delivers the target here')
    return q


def fig_who_uses(base):
    """Figure 1: how strong must each channel be to move use to the bottom."""
    # PAST THE CALIBRATED VALUE, to SCAN_HI. Stopping at 100 leaves the
    # reader unable to tell a channel that has just crossed the line from one
    # that is still falling hard, and it leaves the unemployment channel's
    # failure looking like it might be about to turn. It is not. The grid keeps
    # its step of an eighth of the calibrated value whatever SCAN_HI is.
    sc = np.linspace(0.0, SCAN_HI, int(round(8 * SCAN_HI)) + 1)
    curves, parts = {}, {}
    for which in ('mortality', 'unemployment'):
        m_ = [stats(_scaled(base, which, s)) for s in sc]
        curves[which] = [x['r_use'] for x in m_]
        parts[which] = [x['part'] for x in m_]
    draw_who_uses(sc, curves)
    return sc, curves, parts


def draw_who_uses(sc, curves):
    """Figure 1's drawing, apart from its computation, so it can be redrawn from
    the curves stage_numbers.json keeps (stage_results.py 1 --replot)."""
    plt = style()
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    sc = np.asarray(sc)
    for which, col, ls, mk in (('mortality', '#2C6FAD', '-', 'o'),
                               ('unemployment', '#D9822B', '--', 's')):
        ax.plot(100 * sc, curves[which], ls, color=col, marker=mk, ms=4.5,
                label=f'{which} channel')
    ax.axhline(1.0, color='0.3', lw=1.1)
    # A LINEAR AXIS (the author, 29 September: "it does not look to scale"). The
    # log axis spaced 0.1, 0.2, 0.5, 1, 2, 3, 5 unevenly, so 0.53 and 3.88 did not
    # read as the distances they are.
    hi = max(max(curves['mortality']), max(curves['unemployment']))
    top = 0.5 * np.ceil(hi / 0.5 + 0.4)
    ax.set_ylim(0.0, top)
    ax.set_yticks(np.arange(0.0, top + 1e-9, 0.5))
    ax.grid(axis='y', which='major', color='0.88', lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xticks(list(range(0, int(round(100 * SCAN_HI)) + 1, 25)))
    # the calibrated point, so the extrapolation past it reads as extrapolation
    ax.axvline(100, color='black', lw=0.9, ls=':')
    ax.annotate('calibrated', xy=(100, 0.04 * top), ha='center', va='bottom',
                fontsize=8, color='black',
                bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='none'))
    ax.set_xlabel('Strength of the channel, percent of its calibrated value')
    ax.set_ylabel('Mean income of users / population mean')
    # legend OUTSIDE the plotting area, so it cannot sit on the lines
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=2,
              fontsize=9.5)
    # NO "users are RICHER / POORER than average" labels: the author, 29
    # September, asked for them off; the line at one says it.
    # THE TWO ENDPOINTS, PRINTED ON THE CURVE, so the prose's numbers can be
    # checked against the figure without interpolating.
    for which, col in (('mortality', '#2C6FAD'), ('unemployment', '#D9822B')):
        y_end = curves[which][-1]
        ax.annotate(f'{y_end:.2f}', xy=(100 * sc[-1], y_end),
                    xytext=(4, -2), textcoords='offset points',
                    fontsize=8.5, color=col, fontweight='bold', va='center')
    y0 = curves['mortality'][0]
    ax.annotate(f'{y0:.2f}', xy=(0, y0), xytext=(2, 6),
                textcoords='offset points', fontsize=8.5, color='0.25',
                fontweight='bold')
    ax.set_xlim(-3, 100 * SCAN_HI + 11)
    fig.tight_layout()
    save(fig, 'stylized_who_uses')


def fig_moral_hazard(base):
    """Figure 2: the two forces as the voucher becomes more generous."""
    plt = style()
    pVs = np.array([0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0])
    # THE WHOLE MOMENT DICT AT EVERY POINT, not just participation. The prose
    # quotes homelessness, the SUD rate and the voucher outlay at the two ends
    # of this figure, and it used to recompute them in fill.py. Two computations
    # of the same number are two numbers, and they drifted: the note went to
    # press quoting an income ratio the figure beside it did not show.
    mH = [stats(with_(base, pV=p, policy='HF')) for p in pVs]
    mT = [stats(with_(base, pV=p, policy='TF')) for p in pVs]
    H = np.array([m['part'] for m in mH])
    T = np.array([m['part'] for m in mT])

    # THE CEILING IS THE HIGHEST CURVE, not the no programme rate. It used to be
    # 1.22 times T[0], which worked only while Housing First stayed below the no
    # programme line. On the rebuilt calibration Housing First RISES above it,
    # to 9.21 per cent against 4.34, so the red curve ran clean off the top of
    # the axis and the figure showed a moral hazard band with no curve bounding
    # it. Any limit written in terms of one series will break the first time the
    # ranking of the series changes.
    top = 100 * max(H.max(), T.max(), T[0]) * 1.16

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
    ax.text(base.pV + 0.012, top * 0.04, 'current programme',
            fontsize=8.5, color='0.4', rotation=90, va='bottom')
    ax.set_ylim(-0.45, top)
    ax.set_xlim(-0.02, 1.14)
    ax.text(0.02, 100 * T[0] + top * 0.02, 'No voucher programme', fontsize=8.5,
            color='0.4')
    # the value of life force is the WHOLE drop, so mark it as a span at the
    # right hand edge rather than as a region that overlaps the others
    xb = 1.075
    ax.annotate('', xy=(xb, 100 * T[0]), xytext=(xb, 100 * T[-1]),
                arrowprops=dict(arrowstyle='<->', color='#2C6FAD', lw=1.3))
    ax.text(xb - 0.015, 100 * (T[0] + T[-1]) / 2, 'Value of life',
            rotation=90, ha='right', va='center', fontsize=9, color='#2C6FAD')
    ax.text(0.62, 100 * (T[5] + H[5]) / 2 + top * 0.03, 'Moral hazard', fontsize=9,
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
    return pVs, H, T, mH, mT


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

    # NO SECOND PASS FOR PARTICIPATION. There used to be an out['use'] here that
    # solved the whole grid again under both policies to get a series out[pol]
    # already carried, and the panel loop never reached it: eighteen solves that
    # produced a number nothing read.
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6))
    panels = ((axes[0], 'homeless', 'Homelessness rate, percent', '(a)'),
              (axes[1], 'part', 'Drug use, percent', '(b)'),
              (axes[2], 'sud', 'Share with a SUD, percent', '(c)'))
    for ax, key, lab, tag in panels:
        for pol, col, mk in (('HF', '#C0392B', 'o'), ('TF', '#2C6FAD', 's')):
            y = out[pol][key]
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


# THE WORDS FOR A FRACTION OF THE CHANNEL, so the sentence that says over how
# much of it the reversal happens follows the curve instead of being typed. It
# was typed, it said "the last quarter", and the curve said half.
_FRACTION = ((1.0, 'whole'), (0.75, 'three quarters'), (2.0 / 3.0, 'two thirds'),
             (0.5, 'half'), (1.0 / 3.0, 'third'), (0.25, 'quarter'),
             (0.125, 'eighth'))


def _fraction_word(x):
    return min(_FRACTION, key=lambda fw: abs(fw[0] - x))[1]


# Small counts as words, so a sentence can say "two of twenty two" without the
# number being typed into it.
_WORDS = ('no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
          'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
          'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty',
          'twenty one', 'twenty two', 'twenty three', 'twenty four')


def figure_numbers(base):
    """
    Every number the prose quotes off a figure, written from the figure itself.

    WHY THIS EXISTS. fill.py used to recompute these, so the note and the plot
    beside it were two independent calculations of the same object. They
    disagreed in print: the text quoted an income ratio of 3.33 at half strength
    against 2.62 with the channel off, which is not "unchanged" and was not what
    the figure showed. Anything that appears on a figure is now computed once,
    here, and read from this file by fill.py.
    """
    sc, curves, parts = fig_who_uses(base)
    pVs, H, T, mH, mT = fig_moral_hazard(base)
    fig_margins(base)

    mort = np.asarray(curves['mortality'])
    unem = np.asarray(curves['unemployment'])

    def at(curve, s):
        i = int(np.argmin(np.abs(sc - s)))
        return float(curve[i])

    d = {'r_off': f'{at(mort, 0.0):.2f}',
         'r_mort': f'{at(mort, 1.0):.2f}',
         'r_mort_half': f'{at(mort, 0.5):.2f}',
         'r_mort125': f'{at(mort, SCAN_HI):.2f}',
         'r_unemp': f'{at(unem, 1.0):.2f}',
         'r_unemp125': f'{at(unem, SCAN_HI):.2f}',
         'scanhi_pc': f'{100.0 * SCAN_HI:.0f}'}

    # STILL ABOVE ONE is a claim, and the contrast with the mortality channel
    # rests on it, so the word comes from the number.
    hi = at(unem, SCAN_HI)
    d['runemphidir'] = 'above' if hi > 1.0 else ('below' if hi < 1.0 else 'at')

    # OVER HOW MUCH OF THE CHANNEL THE REVERSAL HAPPENS. The last grid point at
    # or below the calibrated strength where the ratio is still within five per
    # cent of its value with the channel off is where the fall begins, so the
    # reversal occupies what is left of the channel.
    off = at(mort, 0.0)
    start = 0.0
    for s_, r_ in zip(sc, mort):
        if s_ <= 1.0 + 1e-9 and abs(r_ - off) <= 0.05 * abs(off):
            start = float(s_)
    d['revfrac'] = _fraction_word(max(1.0 - start, 0.0))

    # WHETHER b ACTUALLY HELD PARTICIPATION at every point of Figure 1, and
    # WHERE IT CANNOT. Ten of twenty two points missed under the pooled bottom
    # cell and flooring the grid removed those, so the note was allowed to
    # promise the target at every point and verify.py failed the build on any
    # miss. Two points on the mortality curve miss anyway, and they are not a
    # bisection failure: participation is a STEP function of b there, falling
    # 9.34 to 8.09 per cent across one step at 0.75 of the calibrated mortality
    # and 9.15 to 7.68 at 1.125, with the 8.90 target strictly inside the jump.
    # A whole interval of incomes changes its housing rung at once, and the
    # value of using changes with it, so the set of users is not continuous in
    # b. No value of b delivers the target at those two points and none exists
    # to be found.
    #
    # BOTH ARE REACHABLE AGAIN, so the note promises the target at every point
    # with no hedge and verify.py fails the build on any miss. What made them
    # unreachable was threshold() writing boundary cells per crossing: where the
    # use region is the top block plus one isolated interior cell, that cell is
    # the boundary of two crossings and the second write overwrote the first, so
    # its share never shrank to zero and the whole cell left at once.
    d['_part_misses'] = sum(1 for which in ('mortality', 'unemployment')
                            for pp in parts[which]
                            if abs(pp - TARGET['part']) > 5e-4)
    d['_part_worst'] = max(abs(pp - TARGET['part'])
                           for which in ('mortality', 'unemployment')
                           for pp in parts[which])

    # THE ENDS OF FIGURE 2, which the policy paragraph reads off directly.
    m0, mt, mh = mT[0], mT[-1], mH[-1]
    d['p0'] = f'{100 * m0["part"]:.2f}'
    d['pt'] = f'{100 * mt["part"]:.2f}'
    d['ph'] = f'{100 * mh["part"]:.2f}'
    d['vol'] = f'{100 * (mt["part"] - m0["part"]):+.2f}'
    d['mh'] = f'{100 * (mh["part"] - mt["part"]):+.2f}'
    d['net'] = f'{100 * (mh["part"] - m0["part"]):+.2f}'
    d['hl0'] = f'{100 * m0["homeless"]:.2f}'
    d['sudh'] = f'{100 * mh["sud"]:.3f}'
    d['sudt'] = f'{100 * mt["sud"]:.3f}'
    # HOW PANEL (b) AND PANEL (c) CAN MOVE IN OPPOSITE DIRECTIONS. Housing First
    # takes participation DOWN relative to no programme and the share with a
    # disorder UP, which reads as a contradiction until the intensive margin is
    # named: fewer households use, and each one that does uses much more,
    # because it keeps its voucher and the drug is a luxury. The hazard is
    # 1-exp(-lambda v), so it is the dose that converts a user into a case.
    # These are the conversion rates among USERS at the two ends.
    d['sud0'] = f'{100 * m0["sud"]:.3f}'
    d['conv0'] = f'{100 * m0["sud"] / m0["part"]:.1f}'
    d['convh'] = f'{100 * mh["sud"] / mh["part"]:.1f}'
    d['costh'] = f'{mh["cost"]:.4f}'
    d['costt'] = f'{mt["cost"]:.4f}'
    d['costdir'] = ('more' if mt['cost'] > mh['cost']
                    else 'less' if mt['cost'] < mh['cost'] else 'no more')
    d['costgap'] = f'{abs(mt["cost"] - mh["cost"]):.4f}'
    # NO ARTICLE. The prose reads "ends up slightly @@costdearer@@", so the
    # word supplies the comparative alone.
    d['costdearer'] = ('dearer' if mt['cost'] > mh['cost']
                       else 'cheaper' if mt['cost'] < mh['cost']
                       else 'no dearer')
    d['costeffect'] = 'first' if mt['cost'] > mh['cost'] else 'second'
    # HOW CLOSE THE TWO OUTLAYS ARE, which Section 4 leans on when it says the
    # stylized comparison is unaffected by the budget. That is a result about
    # this calibration, not an identity, so the phrase follows the numbers.
    _rel = abs(mt['cost'] - mh['cost']) / max(mh['cost'], 1e-12)
    d['costclose'] = ('happen to cost very nearly the same' if _rel < 0.02
                      else f'differ in cost by {100 * _rel:.1f} percent')

    # WHETHER CONDITIONALITY DETERS EVERYONE, which Section 4 contrasts the
    # quantitative model against. It used to say "Treatment First deters everyone
    # and nobody is thrown off the rolls", which was true only while the period 2
    # condition revoked on a history of use: once it tests the current period, a
    # few households use anyway and are revoked, and the contrast has to say so.
    if mt['part'] < 5e-5:
        d['tfdeter'] = ('Treatment First deters everyone, so nobody is ever '
                        'thrown off the rolls')
    else:
        d['tfdeter'] = ('Treatment First deters all but '
                        f'{100 * mt["part"]:.2f} percent of households, and that '
                        'remainder is what conditionality actually revokes')

    # PANEL (a) OF FIGURE 3, whose two claims in the prose are both orderings and
    # so both have to follow the curves. That the two policies end at zero
    # homelessness is a result, not an identity, and which of them runs lower on
    # the way there is a result the conditional policy could lose.
    hlH = np.array([m['homeless'] for m in mH])
    hlT = np.array([m['homeless'] for m in mT])
    top = max(float(hlH[-1]), float(hlT[-1]))
    d['hluniv'] = 'zero' if top < 5e-5 else f'{100 * top:.2f} percent'
    interior = slice(1, -1)
    gap = float(np.mean(hlT[interior] - hlH[interior]))
    d['hltfdir'] = ('below' if gap < -1e-7 else
                    'above' if gap > 1e-7 else 'on top of')

    # THE RAW VALUES TOO, under a key the placeholder filler ignores. fill.py
    # needs the SUD rates at full precision to form the externality's gain, and
    # reading them back out of a rounded string would put a third version of the
    # same number into circulation.
    d['_raw'] = {'sudh': float(mh['sud']), 'sudt': float(mt['sud']),
                 'costh': float(mh['cost']), 'costt': float(mt['cost']),
                 'parth': float(mh['part']), 'partt': float(mt['part']),
                 'part0': float(m0['part'])}

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'figure_numbers.json'), 'w') as f:
        json.dump(d, f, indent=1)
    print('\n   wrote figure_numbers.json')
    for k, v in d.items():
        if not k.startswith('_'):
            print(f'      {k:12s} {v}')
    return d


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    print('figures')
    figure_numbers(base)
