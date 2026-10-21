"""
The quantitative model's transition from Housing First to Treatment First, in six panels.

usage: python3 code/paper/transition_figure.py
       reads results/transition/restart3_loop0/ (code/paper/transition_series.py writes it)
       -> writing/figures/full_transition.{pdf,png}, and the x_trf_* names in
          code/paper/results_numbers.json that the prose quotes beside the figure

The author, 30 September: "for transition you want drug use, SUD, homelessness, and CEV,
like you did the stylized model", with child homelessness and the share of parents using
drugs.  Panels (a) to (e) are years since the reform, with the Housing First benchmark as
year 0; the dashed line is the Housing First rest point and the dotted line the Treatment
First long run.  Panel (f) is the CEV of each cohort by the year it is born, against the
long-run CEV.  The path is the first iteration of a computation that has not converged;
from about year 40 its end drifts (homelessness climbs back from +4.6 to +8.2 per cent
against +5.6 in the long run, and pi_V falls below its long-run value), so years 41-59 and
the cohorts whose adult life starts in them (born in year 16 or later) are shaded.

The cohorts' CEVs are net of the no-policy run's own CEV off the benchmark's curve
(results_numbers _cev_null_share, +0.027), as the long-run x_tf_cev is (export_results.py).
The x_trf_* names are written from the same series the panels draw.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from transition_source import OUT as IN, HORIZON, UNCONVERGED_FROM, SHOWN   # the one pin
FIG = os.path.join(ROOT, 'writing', 'figures', 'full_transition')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
sys.path.insert(0, os.path.join(ROOT, 'code', 'stylized'))

BLUE, ORANGE, GREY = '#2C6FAD', '#D9822B', '0.45'


def rows(name):
    """years 1 to SHOWN only, and the cohorts born in them (21 October: the horizon's last decade is not shown,
    transition_source.SHOWN)"""
    with open(os.path.join(IN, name)) as f:
        out = [{k: float(v) for k, v in r.items() if k != 'ages'} for r in csv.DictReader(f)]
    return [r for r in out if r.get('t', r.get('born', 0)) <= SHOWN]


def main():
    S = rows('series.csv'); C = rows('cohorts.csv')
    R = json.load(open(os.path.join(IN, 'reference.json')))
    hf, tf = R['hf'], R['tf']
    import run
    plt = run.style()
    # SEVEN PANELS AND THE LEGEND IN THE EIGHTH (round 4ad85a30, the author: "can you also show the drug
    # price?"); the shading of the drifting end is gone with its note (the author: "remove")
    # FOUR ROWS OF TWO, ON A PAGE OF ITS OWN (review item 15, 7 Oct: the eight panels in two rows were too small
    # to read without zooming at the text width)
    fig, axs = plt.subplots(4, 2, figsize=(7.0, 7.6))
    t = [0] + [r['t'] for r in S]
    panels = (('b', '(a) Drug use', 'percent of households', 100),
              ('lambda_d', '(b) With a SUD', 'percent of households', 100),
              ('p_drug', '(c) Drug price', 'benchmark $=1$', 1),
              ('par_use', '(d) Parents using drugs', 'percent of parents', 100),
              ('h_1', '(e) Homeless', 'percent of households', 100),
              ('child_hl', '(f) Children in a shelter', 'percent of children', 100))
    for ax, (key, title, ylab, sc) in zip(axs.flat, panels):
        y = [sc * hf[key]] + [sc * r[key] for r in S]
        ax.axhline(sc * hf[key], color=ORANGE, ls='--', lw=1.5, label='Housing First benchmark')
        ax.axhline(sc * tf[key], color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
        ax.plot(t, y, '-', color=BLUE, lw=2.0, label='Treatment First, year by year')
        ax.plot([0], [y[0]], 'o', color=ORANGE, ms=5)
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_xlim(-1, SHOWN)
        lo, hi = min(min(y), sc * tf[key]), max(max(y), sc * hf[key])
        pad = 0.12 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
    for ax in axs[2, :]:
        ax.set_xlabel('years since the reform', fontsize=9)
    ax = axs[3, 0]
    born = [r['born'] for r in C]; cev = [r['cev_pc'] - CEV0 for r in C]
    ax.axhline(0.0, color=GREY, lw=0.8)
    ax.axhline(TF_CEV, color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
    # a line, like the other five panels (the author, 2 October: "why not give a line like in the
    # other graphs?"); it was a bar per cohort
    ax.plot(born, cev, '-', color=BLUE, lw=2.0, label='Treatment First, by year of birth')
    ax.set_title('(g) Welfare by year of birth, CEV', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of lifetime consumption', fontsize=9)
    ax.set_xlabel('year of birth, after the reform', fontsize=9)
    ax.set_xlim(0, SHOWN)
    # (h) THE SHARE BETTER OFF, YEAR BY YEAR (the author, 2 October: "an approval rate of everyone alive at the
    # beginning of the transition", "and show it across time?"), in the eighth slot; the legend goes to (a)
    # WORSE OFF, not better off (the author, 8 October: "maybe show this as percent worse off?"): the share better
    # off counts the households the reform leaves untouched as gaining (transition_series.py), the share worse off
    # does not
    Bt = rows('worse.csv')
    ax = axs[3, 1]
    ax.plot([r['t'] for r in Bt], [100 * r['all'] for r in Bt], '-', color=BLUE, lw=2.0, label='all households')
    ax.plot([r['t'] for r in Bt], [100 * r['with_sud'] for r in Bt], '--', color=BLUE, lw=1.5,
            label='households with a SUD')
    ax.set_title('(h) Worse off than under Housing First', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of households', fontsize=9)
    ax.set_xlabel('years since the reform', fontsize=9)
    ax.set_xlim(-1, SHOWN)
    ax.set_ylim(0, 105)
    # (round r327, the author: "the legend is not so well placed. can you move it to a better location"): 'center
    # right' sat on the dashed line, which runs from about 66 down to 51; above it the panel is empty
    ax.legend(fontsize=7.5, loc='upper right', frameon=False)
    axs[0, 0].legend(fontsize=7.5, loc='center right')
    fig.tight_layout()
    run.save(fig, 'full_transition')
    print(f'wrote {FIG}.pdf')
    names(S, C, R)


def names(S, C, R):
    """the x_trf_* names the prose quotes beside the figure, from the series it draws"""
    hf, tf = R['hf'], R['tf']
    col = lambda k: [r[k] for r in S]
    out = {}
    lam, b, h, ch, pu = col('lambda_d'), col('b'), col('h_1'), col('child_hl'), col('par_use')
    # drug use: the share of its long-run fall that happens in the first year
    out['x_trf_b1'] = f'{100 * b[0]:.2f}'
    out['x_trf_b1_share_pc'] = f"{100 * (hf['b'] - b[0]) / (hf['b'] - tf['b']):.0f}"
    # the SUD share: the first year by which half, and nine tenths, of its long-run fall is done
    def year(series, key, frac):
        return next(i + 1 for i, v in enumerate(series)
                    if hf[key] - v >= frac * (hf[key] - tf[key]))
    out['x_trf_sud_half_yr'] = str(year(lam, 'lambda_d', 0.5))
    out['x_trf_sud_90_yr'] = str(year(lam, 'lambda_d', 0.9))
    # homelessness and children in a shelter: the peak before the drifting end, and its year
    body = range(UNCONVERGED_FROM - 1)
    k = max(body, key=lambda i: h[i])
    out['x_trf_h_peak_pc'] = f"{100 * (h[k] / hf['h_1'] - 1):.0f}"
    out['x_trf_h_peak_yr'] = str(k + 1)
    out['x_trf_h_lr_pc'] = f"{100 * (tf['h_1'] / hf['h_1'] - 1):.0f}"
    k = max(body, key=lambda i: ch[i])
    out['x_trf_hchild_peak'] = f'{100 * ch[k]:.2f}'
    # the same peak as a rise on the benchmark, for the abstract and the introduction (the author, 9 October:
    # "childhood homelessness")
    out['x_trf_hchild_peak_pc'] = f"{100 * (ch[k] / hf['child_hl'] - 1):.0f}"
    out['x_trf_hchild_peak_yr'] = str(k + 1)
    out['x_trf_hchild_lr'] = f"{100 * tf['child_hl']:.2f}"
    out['x_trf_hchild0'] = f"{100 * hf['child_hl']:.2f}"
    # parents using drugs in the first year, against the long run
    out['x_trf_paruse1'] = f'{100 * pu[0]:.2f}'
    out['x_trf_paruse0'] = f"{100 * hf['par_use']:.2f}"
    out['x_trf_paruse_lr'] = f"{100 * tf['par_use']:.2f}"
    out['x_trf_paruse1_vs_lr'] = 'below' if pu[0] < tf['par_use'] else 'above'
    # WHY, IN THE DIRECTION THE PATH TAKES (17 October, the T = 70 re-pin: at T = 50 the share fell below its long-run
    # level in the first year and sat slightly above it after; at T = 70 it starts above it and crosses below in year
    # 11). The two sentences turn with the path instead of asserting one shape.
    if pu[0] < tf['par_use']:
        out['x_trf_paruse1_why'] = ('The share of parents who use falls below its long-run level in the first year because the '
                                    'drug price does not fall to its long-run level at once, so more potential users are deterred.')
        out['x_trf_paruse_after'] = ('From the second year on, the share of parents who use is slightly above its long-run '
                                     'level, because it counts the parents who have a SUD, whose number falls only slowly '
                                     '(panel (b)), and because the falling drug price draws some users back.')
    else:
        _kb = next((i + 1 for i, x in enumerate(pu) if x < tf['par_use']), None)
        assert _kb, 'the share of parents who use never reaches its long-run level along the path'
        out['x_trf_paruse_below_yr'] = str(_kb)
        out['x_trf_paruse1_why'] = ('It stays above its long-run level until year ' + str(_kb) + ', because it counts the '
                                    'parents who have a SUD when the reform lands, whose number falls only slowly '
                                    '(panel (b)). From then on it moves around its long-run level.')   # r347 sweep
        out['x_trf_paruse_after'] = ''
    # HOW MANY MORE CHILDREN (round 3350a58a, the author on 'while the former affects many': "(put magnitudes). how
    # many more children does the first affect relative to the second?"): the fall in the share of parents who use
    # in the first year against the largest rise in the share of children in a shelter, both in percentage points
    _du = 100 * (hf['par_use'] - pu[0])
    _dh = 100 * (max(ch[i] for i in body) - hf['child_hl'])
    out['x_trf_many'] = (f': in the first year the share of parents who use drugs falls by ${_du:.2f}$ percentage points, '
                         f'while the share of children in a shelter rises by at most ${_dh:.2f}$ points, too few '
                         f'children to reverse their gain'
                         if _du > 0 and _dh > 0 and _du > 5 * _dh else '')
    # (9 October, the referee: "Reaching 39 times as many children does not establish that benefits dominate";
    # the author: "say that the childhood homelessness increases falls on X% of children, which is way too small to
    # reverse a 2.7% welfare gain in transition"): the ratio is gone from both places, the peak rise stays
    out['x_trf_hchild_rise_pp'] = f'{_dh:.2f}'
    # (round r260, the author on 'at any time': "relative to eliminating parents' drug use for X percent of
    # children"): the first year's fall in the share of parents who use, the same _du as above
    out['x_trf_paruse_drop_pp'] = f'{_du:.2f}'
    # the same ratio alone, for Section 2 (the author, round r110: 'even in the short run the absolute increase in
    # childhood homelessness is X times smaller than the mass of children spared a parent who abuses drugs')
    out['x_trf_many_x'] = f'{round(_du, 2) / round(_dh, 2):.0f}' if _du > 0 and round(_dh, 2) > 0 else ''
    # the intuition for each panel (the author, 2 October: "Are you walking the reader through each of
    # the graphs and explaining why they come out this way?"), only where the path does what it explains
    out['x_trf_paruse_why'] = ('It is also why the share of parents who use starts below its long-run level in '
                               'panel (d): as the stock of carriers thins and the price comes down, some of '
                               'them come back.' if pu[0] < tf['par_use'] else '')
    # (round f9ac1593, the author: 'The' -> 'This happens because', 'allows' -> ', even with more households in
    # treatment,')
    out['x_trf_h_why'] = ('This happens because the households that have a SUD when the reform lands lose their '
                          'vouchers within a year. That stock shrinks only as fast as recovery allows, even with more '
                          'households in treatment (panel (b)), so revocations '
                          'are highest in the first years and fall as the stock thins.'
                          if max(h) > tf['h_1'] > hf['h_1'] else '')
    # cohorts: the first born whose CEV is within a tenth of a point of the long run's
    cev = [(int(r['born']), r['cev_pc'] - CEV0) for r in C]
    out['x_trf_cev_b1'] = f'{cev[0][1]:.1f}'
    # the first decade's cohorts on average: single cohorts are noisy on an unconverged pass
    out['x_trf_cev_dec1'] = f'{sum(c for b, c in cev[:10]) / 10:.2f}'
    # the short run against the long run, for Section 6.2 (round 4ad85a30, the author: "This is the long run
    # result, but in the short run homelessness does spike a bit")
    # keyed on the paper's long run (export_results.py's x_tf_h_dir, the omega_c = 0.085 arms) and on whether
    # the path rises above the benchmark at all; the path itself is still the old arms' until stage E lands
    _lowers = json.load(open(OUT_JSON)).get('x_tf_h_dir') == 'lowers'
    # (round c88b1dda, the author: "this should come when you talk about homelessness dropping. you need to write
    # it better")
    # (round 20b4ddb5, the author: 'the' -> 'a', 'In' -> 'However,', 'instead,' out)
    # (round f4276e76, the author: '.' -> 'because the')
    # (round r137, the author: combine it with the children's sentence before it "and add that childhood homelessness
    # rises in transition"): 'These are long-run outcomes', and children's homelessness, only where its path before
    # the drifting end rises above the benchmark (the old arms: 1.02 to a peak of 1.14 in year 6)
    _ch_up = max(ch[i] for i in body) > hf['child_hl']
    out['x_trf_h_sr'] = ('These are long-run outcomes, however. In the first years after the reform '
                         + ('both homelessness and childhood homelessness rise, ' if _ch_up else 'homelessness rises, ')
                         + 'because the households that already have a SUD lose their vouchers within a year, '
                         'while their number falls only as fast as recovery allows. I take the transition up in Section~\\ref{sec:ftrans}.'
                         if _lowers and max(h) > hf['h_1'] else
                         # (16 October, rule C, T = 50; the author on 'rise': "could rise", on 'SUD': "a SUD but decide
                         # against going to treatment and staying sober", and "even along the transition homelessness
                         # and childhood homelessness do not rise"): the path never rises above the benchmark
                         # (round r327, the author: "qualitatively reverse", "do not enter", "stay")
                         # (round r326, the author: "One concern is that....", "As I show, this concern does not
                         # materilize:", "to house themselves", "even in the first year")
                         'These are long-run outcomes, but the transition does not qualitatively reverse them. One concern is that '
                         'homelessness and childhood homelessness could rise in the first years after the reform, because the households '
                         'that already have a SUD face losing their vouchers unless they enter treatment and stay sober, '   # r347 sweep
                         'while the number with a SUD falls only as fast as recovery allows. As I show, this concern does not materialise: '
                         # (round r325, the author: "is that the reason? or is it because household use less and then
                         # it frees more resources for housing?")
                         'few households lose their vouchers, and those that stop using spend less on drugs and can '
                         'afford to house themselves, so neither rises even in the first year (Section~\\ref{sec:ftrans}).' if _lowers else '')
    out['x_trf_shade_from'] = str(UNCONVERGED_FROM)
    # (16 October, rule C, T = 50; the author on Panels (e) and (f): "you need to explain why these dont rise, and fall
    # a bit in fact", and on panel (g): "need to explain why the gains are smaller"): the path's own numbers
    _T = len(h)
    out['x_trf_norise'] = '1' if max(h) <= hf['h_1'] * (1 + 1e-3) and max(ch) <= hf['child_hl'] * (1 + 1e-3) else '0'
    out['x_trf_last_yr'] = str(_T)
    out['x_trf_h0'] = f"{100 * hf['h_1']:.2f}"
    out['x_trf_h10'] = f'{100 * h[9]:.2f}'
    out['x_trf_hlast'] = f'{100 * h[-1]:.2f}'
    out['x_trf_h_lr'] = f"{100 * tf['h_1']:.2f}"
    out['x_trf_hchild10'] = f'{100 * ch[9]:.2f}'
    out['x_trf_hchildlast'] = f'{100 * ch[-1]:.2f}'
    _ex = col('excluded')
    out['x_trf_excl_max_pc'] = f'{100 * max(_ex):.2f}'
    _pv = col('pi_v')
    out['x_trf_piv_dec1_lo'] = f'{100 * min(_pv[:10]):.2f}'
    out['x_trf_piv_dec1_hi'] = f'{100 * max(_pv[:10]):.2f}'
    out['x_trf_piv_lr'] = f"{100 * tf['pi_v']:.2f}"
    out['x_trf_piv0'] = f"{100 * hf['pi_v']:.2f}"
    out['x_trf_piv_above_hf'] = '1' if min(_pv) > hf['pi_v'] else '0'
    # (20 October, re-pinned to loop 1: pi_V is 6.55, 6.64 and 6.73 per cent in years 1-3, below Housing First's 6.75, as
    # the early treatment spending outruns the savings; loop 0's stayed above throughout) the third reason homelessness
    # does not rise, from the path, so it turns with it
    _below = [t + 1 for t, v in enumerate(_pv) if v < hf['pi_v']]
    _piv0 = f"{100 * hf['pi_v']:.2f}"
    _nw = {1: 'year', 2: 'two years', 3: 'three years', 4: 'four years', 5: 'five years', 6: 'six years'}
    if not _below:
        out['x_trf_piv_reason'] = (f'Third, $\\pi_V$ stays above its Housing First level of ${_piv0}$ percent throughout, so the '
                                   'vouchers the screen frees go to other low-income households.')
    elif _below == list(range(1, len(_below) + 1)) and len(_below) in _nw:
        out['x_trf_piv_reason'] = (f'Third, after the first {_nw[len(_below)]}, when it is as low as '
                                   f'${100 * min(_pv[:len(_below)]):.2f}$ percent, $\\pi_V$ stays above its Housing First level '
                                   f'of ${_piv0}$ percent, so the vouchers the screen frees go to other low-income households.')
    else:
        out['x_trf_piv_reason'] = (f'Third, $\\pi_V$ is above its Housing First level of ${_piv0}$ percent in all but '
                                   f'{len(_below)} years, so the vouchers the screen frees go to other low-income households.')
    out['x_trf_sud10'] = f'{100 * lam[9]:.2f}'
    out['x_trf_sud0'] = f"{100 * hf['lambda_d']:.2f}"
    out['x_trf_sud_lr'] = f"{100 * tf['lambda_d']:.2f}"
    out['x_trf_shade_born'] = str(UNCONVERGED_FROM - 25)
    # the drug price: the years it stays above its long-run level
    p = col('p_drug')
    out['x_trf_price_above_yrs'] = str(next(i for i, v in enumerate(p) if v <= tf['p_drug']))
    # adults alive at the reform: the share better off, all of them and those with a SUD
    out['x_trf_alive_better_pc'] = f"{100 * R['better_off_all']:.0f}"
    out['x_trf_alive_sud_better_pc'] = f"{100 * R['better_off_sud']:.0f}"
    out['x_trf_alive_sud_worse_pc'] = f"{100 * R['worse_off_sud']:.0f}"
    out['x_trf_alive_worse_pc'] = f"{100 * R['worse_off_all']:.0f}"
    # panel (h): the shares over the path
    Bt = rows('better.csv')
    a_all = [100 * r['all'] for r in Bt]; a_sud = [100 * r['with_sud'] for r in Bt]
    a_ent = [100 * r['entering'] for r in Bt]
    # the share WORSE off over the path (8 October): the better-off share counts households the reform leaves
    # untouched as better off, because the benchmark's value function sits slightly below the re-solve's
    Wt = rows('worse.csv')
    w_all = [100 * r['all'] for r in Wt]; w_sud = [100 * r['with_sud'] for r in Wt]
    # the entrants' share is quoted at the year before the last one shown (21 October, the author: "instead of saying
    # 99.9 percent by year 60 say by year 59")
    _ye = len(a_ent) - 1
    out['x_trf_better_sentence'] = (
        'Panel (h) repeats the comparison in every period of the path, with households in each state weighted as '
        'under Housing First. The share worse off stays '
        + (f"at about ${w_all[0]:.0f}$ percent" if round(min(w_all)) == round(max(w_all)) else
           f"between ${min(w_all):.0f}$ and ${max(w_all):.0f}$ percent")
        + f", and the share of those with a SUD who are worse off {'rises' if w_sud[-1] > w_sud[0] else 'falls'} from "
        f"${w_sud[0]:.0f}$ to ${w_sud[-1]:.0f}$ percent as the price comes down further. "
        + ('Every household entering adult life at 26 is better off throughout.' if min(a_ent) > 99.95
           and min(c for b, c in cev) > 0 else
           # (round r325, the author on 'At least 34 percent': "i thought 99.9% are better off...Are you saying that only
           # 34% entering adult life in each period of the transition are better off?"): yes, year by year; say so
           f"Of the households entering adult life at 26, ${a_ent[0]:.0f}$ percent are better off in the first year, "
           f"when $\\pi_V$ is still close to its Housing First level, and ${(f'{a_ent[_ye - 1]:.1f}' if 99.5 <= a_ent[_ye - 1] < 99.95 else f'{a_ent[_ye - 1]:.0f}')}$ percent by year "
           f"{_ye}." if a_ent[_ye - 1] > a_ent[0] else
           f"At least ${min(a_ent):.0f}$ percent of households entering adult life are better off."))
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k2, v in sorted(out.items()):
        print(f'  {k2} = {v}')


# The long-run CEV the cohorts are compared with: the paper's x_tf_cev, net of the no-policy
# run's, and that offset, which the cohorts are netted by too.
_N = json.load(open(OUT_JSON))
# the transition's own long run and no-policy run, the old arms it was solved between (export_results.py,
# STAGE D), until the T = 60 transition is re-run on the omega_c = 0.085 arms
TF_CEV, CEV0 = float(_N['x_tr_lr_cev']), float(_N['_cev_null_share_tr'])

if __name__ == '__main__':
    main()
