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
from transition_source import OUT as IN   # the one pin
FIG = os.path.join(ROOT, 'writing', 'figures', 'full_transition')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
sys.path.insert(0, os.path.join(ROOT, 'code', 'stylized'))

UNCONVERGED_FROM = 41          # the drifting end of the T = 60 path (see the docstring)
BLUE, ORANGE, GREY = '#2C6FAD', '#D9822B', '0.45'


def rows(name):
    with open(os.path.join(IN, name)) as f:
        return [{k: float(v) for k, v in r.items() if k != 'ages'} for r in csv.DictReader(f)]


def main():
    S = rows('series.csv'); C = rows('cohorts.csv')
    R = json.load(open(os.path.join(IN, 'reference.json')))
    hf, tf = R['hf'], R['tf']
    import run
    plt = run.style()
    # SEVEN PANELS AND THE LEGEND IN THE EIGHTH (round 4ad85a30, the author: "can you also show the drug
    # price?"); the shading of the drifting end is gone with its note (the author: "remove")
    fig, axs = plt.subplots(2, 4, figsize=(13.2, 6.0))
    t = [0] + [r['t'] for r in S]
    panels = (('b', '(a) Drug use', 'percent of adults', 100),
              ('lambda_d', '(b) Carrying a SUD', 'percent of adults', 100),
              ('p_drug', '(c) Drug price', 'benchmark $=1$', 1),
              ('par_use', '(d) Parents using drugs', 'percent of parents', 100),
              ('h_1', '(e) Homeless', 'percent of households', 100),
              ('child_hl', '(f) Children in a shelter', 'percent of children', 100))
    for ax, (key, title, ylab, sc) in zip(axs.flat, panels):
        y = [sc * hf[key]] + [sc * r[key] for r in S]
        ax.axhline(sc * hf[key], color=ORANGE, ls='--', lw=1.5, label='Housing First rest point')
        ax.axhline(sc * tf[key], color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
        ax.plot(t, y, '-', color=BLUE, lw=2.0, label='Treatment First, year by year')
        ax.plot([0], [y[0]], 'o', color=ORANGE, ms=5)
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_xlim(-1, 60)
        lo, hi = min(min(y), sc * tf[key]), max(max(y), sc * hf[key])
        pad = 0.12 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
    for ax in axs[1, :2]:
        ax.set_xlabel('years since the reform', fontsize=9)
    ax = axs[1, 2]
    born = [r['born'] for r in C]; cev = [r['cev_pc'] - CEV0 for r in C]
    ax.axhline(0.0, color=GREY, lw=0.8)
    ax.axhline(TF_CEV, color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
    # a line, like the other five panels (the author, 2 October: "why not give a line like in the
    # other graphs?"); it was a bar per cohort
    ax.plot(born, cev, '-', color=BLUE, lw=2.0, label='Treatment First, by year of birth')
    ax.set_title('(g) Welfare by year of birth, CEV', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of lifetime consumption', fontsize=9)
    ax.set_xlabel('year of birth, after the reform', fontsize=9)
    ax.set_xlim(0, max(born) + 1)
    # (h) THE SHARE BETTER OFF, YEAR BY YEAR (the author, 2 October: "an approval rate of everyone alive at the
    # beginning of the transition", "and show it across time?"), in the eighth slot; the legend goes to (a)
    Bt = rows('better.csv')
    ax = axs[1, 3]
    ax.plot([r['t'] for r in Bt], [100 * r['all'] for r in Bt], '-', color=BLUE, lw=2.0, label='all households')
    ax.plot([r['t'] for r in Bt], [100 * r['with_sud'] for r in Bt], '--', color=BLUE, lw=1.5,
            label='households with a SUD')
    ax.set_title('(h) Better off than under Housing First', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of households', fontsize=9)
    ax.set_xlabel('years since the reform', fontsize=9)
    ax.set_xlim(-1, 60)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=7.5, loc='center right', frameon=False)
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
    out['x_trf_hchild_peak_yr'] = str(k + 1)
    out['x_trf_hchild_lr'] = f"{100 * tf['child_hl']:.2f}"
    out['x_trf_hchild0'] = f"{100 * hf['child_hl']:.2f}"
    # parents using drugs in the first year, against the long run
    out['x_trf_paruse1'] = f'{100 * pu[0]:.2f}'
    out['x_trf_paruse0'] = f"{100 * hf['par_use']:.2f}"
    out['x_trf_paruse_lr'] = f"{100 * tf['par_use']:.2f}"
    out['x_trf_paruse1_vs_lr'] = 'below' if pu[0] < tf['par_use'] else 'above'
    # the intuition for each panel (the author, 2 October: "Are you walking the reader through each of
    # the graphs and explaining why they come out this way?"), only where the path does what it explains
    out['x_trf_paruse_why'] = ('It is also why the share of parents who use starts below its long-run level in '
                               'panel (d): as the stock of carriers thins and the price comes down, some of '
                               'them come back.' if pu[0] < tf['par_use'] else '')
    out['x_trf_h_why'] = ('The households that carry a SUD when the reform lands lose their vouchers at once, '
                          'and that stock shrinks only as fast as recovery allows (panel (b)), so revocations '
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
    out['x_trf_h_sr'] = ('That is a long-run outcome. However, in the first years after the reform homelessness rises, '
                         'because the households that already carry a SUD lose their vouchers at once, '
                         'while their number falls only as fast as recovery allows (Section~\\ref{sec:ftrans}).'
                         if _lowers and max(h) > hf['h_1'] else '')
    out['x_trf_shade_from'] = str(UNCONVERGED_FROM)
    out['x_trf_shade_born'] = str(UNCONVERGED_FROM - 25)
    # the drug price: the years it stays above its long-run level
    p = col('p_drug')
    out['x_trf_price_above_yrs'] = str(next(i for i, v in enumerate(p) if v <= tf['p_drug']))
    # adults alive at the reform: the share better off, all of them and those carrying a SUD
    out['x_trf_alive_better_pc'] = f"{100 * R['better_off_all']:.0f}"
    out['x_trf_alive_sud_better_pc'] = f"{100 * R['better_off_sud']:.0f}"
    # panel (h): the shares over the path
    Bt = rows('better.csv')
    a_all = [100 * r['all'] for r in Bt]; a_sud = [100 * r['with_sud'] for r in Bt]
    a_ent = [100 * r['entering'] for r in Bt]
    out['x_trf_better_sentence'] = (
        'Panel (h) repeats the comparison in every year of the path, for a household in each state weighted as '
        'under Housing First: the share better off stays '
        + (f"at about ${a_all[0]:.0f}$ percent" if round(min(a_all)) == round(max(a_all)) else
           f"between ${min(a_all):.0f}$ and ${max(a_all):.0f}$ percent")
        + f", the share among those with a SUD {'rises' if a_sud[-1] > a_sud[0] else 'falls'} from "
        f"${a_sud[0]:.0f}$ to ${a_sud[-1]:.0f}$ percent as the price comes down, and "
        + ('every household entering adult life is better off throughout.' if min(a_ent) > 99.95 else
           f"at least ${min(a_ent):.0f}$ percent of households entering adult life are better off."))
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
