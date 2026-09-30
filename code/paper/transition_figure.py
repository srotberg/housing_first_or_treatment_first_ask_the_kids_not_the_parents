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
IN = os.path.join(ROOT, 'results', 'transition', 'restart3_loop0')
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
    fig, axs = plt.subplots(2, 3, figsize=(10.6, 6.2))
    t = [0] + [r['t'] for r in S]
    panels = (('b', '(a) Drug use', 'percent of adults'),
              ('lambda_d', '(b) Carrying a SUD', 'percent of adults'),
              ('h_1', '(c) Homeless', 'percent of households'),
              ('child_hl', '(d) Children in a shelter', 'percent of children'),
              ('par_use', '(e) Parents using drugs', 'percent of parents'))
    for ax, (key, title, ylab) in zip(axs.flat, panels):
        y = [100 * hf[key]] + [100 * r[key] for r in S]
        ax.axvspan(UNCONVERGED_FROM - 0.5, 59.5, color='0.92', lw=0, zorder=0)
        ax.axhline(100 * hf[key], color=ORANGE, ls='--', lw=1.5, label='Housing First rest point')
        ax.axhline(100 * tf[key], color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
        ax.plot(t, y, '-', color=BLUE, lw=2.0, label='Treatment First, year by year')
        ax.plot([0], [y[0]], 'o', color=ORANGE, ms=5)
        ax.set_title(title, fontsize=10.5, loc='left')
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_xlim(-1, 60)
        lo, hi = min(min(y), 100 * tf[key]), max(max(y), 100 * hf[key])
        pad = 0.12 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
    for ax in axs[1, :2]:
        ax.set_xlabel('years since the reform', fontsize=9)
    axs[0, 0].legend(fontsize=7.5, loc='center right')
    ax = axs[1, 2]
    born = [r['born'] for r in C]; cev = [r['cev_pc'] - CEV0 for r in C]
    ax.axvspan(UNCONVERGED_FROM - 25 - 0.5, max(born) + 0.5, color='0.92', lw=0, zorder=0)
    ax.axhline(0.0, color=GREY, lw=0.8)
    ax.axhline(TF_CEV, color=BLUE, ls=':', lw=1.5, label='Treatment First long run')
    ax.bar(born, cev, color=BLUE, width=0.7)
    ax.set_title('(f) Welfare by year of birth, CEV', fontsize=10.5, loc='left')
    ax.set_ylabel('percent of lifetime consumption', fontsize=9)
    ax.set_xlabel('year of birth, after the reform', fontsize=9)
    ax.set_xlim(0, max(born) + 1)
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
    # cohorts: the first born whose CEV is within a tenth of a point of the long run's
    cev = [(int(r['born']), r['cev_pc'] - CEV0) for r in C]
    out['x_trf_cev_b1'] = f'{cev[0][1]:.1f}'
    out['x_trf_cev_b10'] = f'{cev[9][1]:.1f}'
    # the drug price: the years it stays above its long-run level
    p = col('p_drug')
    out['x_trf_price_above_yrs'] = str(next(i for i, v in enumerate(p) if v <= tf['p_drug']))
    # adults alive at the reform: the share better off, all of them and those carrying a SUD
    out['x_trf_alive_better_pc'] = f"{100 * R['better_off_all']:.0f}"
    out['x_trf_alive_sud_better_pc'] = f"{100 * R['better_off_sud']:.0f}"
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k2, v in sorted(out.items()):
        print(f'  {k2} = {v}')


# The long-run CEV the cohorts are compared with: the paper's x_tf_cev, net of the no-policy
# run's, and that offset, which the cohorts are netted by too.
_N = json.load(open(OUT_JSON))
TF_CEV, CEV0 = float(_N['x_tf_cev']), float(_N['_cev_null_share'])

if __name__ == '__main__':
    main()
