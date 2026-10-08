"""
THE STYLIZED MODEL, STRIPPED TO THE INCOME GRADIENT IN DRUG USE.

The author, 8 October: *"isnt the point of the stylized model just to show how the mortality reverses
the income gradient?"*, *"we can leave all the rest for the quant model"*, *"then we only need stage 1"*,
*"we then also dont need a governmtn"* and *"it would be good to strip everything possible from the
model"*.  So Section 3 is this file and nothing else: no saving, no housing, no employment risk, no
government, no child.  The staged model (stages.py, stage_results.py, stylized.py) is the record of
what came before and is no longer read by the paper.

THE MODEL.  Two periods of thirty years.  Income y, fixed for life, is lognormal with dispersion sigma_y,
raised to a floor y_min where it falls below it, and normalised to mean one.  Period 1: c + p_v v = y, the
bundle X = c^(1-theta) (b+v)^theta, flow utility U(X) + aleph with U(X) = X^(1-sigma)/(1-sigma).  Using at
all (v > 0) gives a SUD with probability pi_d, whatever the quantity, and a SUD cuts survival into period
2 from phibar to phibar^kappa.  Period 2: c = y and no drug, so its value is W2(y) = U(X0(y)) + aleph with
X0(y) = y^(1-theta) b^theta.

THE DECISION IS IN CLOSED FORM.  Given that it uses, a household buys the Cobb-Douglas quantity on full
income y + p_v b, so X1 = (1-theta)^(1-theta) (theta/p_v)^theta (y + p_v b), and v > 0 only above
y_sg = (1-theta) p_v b / theta.  It uses if and only if

    D(y) = U(X1(y)) - U(X0(y)) - beta pi_d (phibar - phibar^kappa) W2(y) > 0.

The first two terms are what the drug is worth, the last is the expected loss of the life still to be
lived.  D is negative at y_sg, where the drug is worth nothing, and tends to -beta pi_d (phibar -
phibar^kappa) aleph at the top, so the users sit in a band [y_lo, y_hi].  Every moment is an integral of
the lognormal over that band, analytic, so the calibration is a smooth root-find in seconds.

THE FLOOR, and why there has to be one.  With sigma = 2 the value of being alive, W2, is negative at low
enough income, and a household for which being alive is worth less than nothing would buy a sliver of drug
for the mortality it brings (negative_value_of_life.py is the record of that defect in the old model).
The quantitative model's safety net rules that out there; here, with no government, incomes are bounded
below.  Two ways of doing it were tried on 8 October and one failed:
  - TRUNCATING at the income where W2 = 0, renormalised: matching the bottom half's share then needs
    sigma_y = 1.32 and cuts 44 per cent of the lognormal, and households just above the cut, with a life
    worth almost nothing to lose, use: a sliver of spurious users at the bottom.
  - A FLOOR at 0.24 of mean income, the old model's, with sigma_y set on the lognormal before it: the
    value of being alive is positive at the floor (it is zero at about 0.21), nobody at the floor uses,
    and the users are one band.  Anywhere between about 0.21 and the bottom of the users' band gives the
    same users; the floor decides only how many households sit at it.

usage:  python3 gradient.py      -> gradient.json (the calibration), gradient_numbers.json (g_* names
                                    for fill.py), writing/tables/tab_external.tex and tab_internal.tex,
                                    writing/figures/stylized_who_uses.pdf
"""
import csv
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq, least_squares
from scipy.special import ndtr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'code', 'paper'))
from fortran_consts import constants as _fc  # noqa: E402

from stylized import P  # noqa: E402  (beta, sigma, phibar and the period length, as before)
from calibrate import BOT50_TARGET  # noqa: E402

FC = _fc()
TABLES = os.path.join(ROOT, 'writing', 'tables')
FIGURES = os.path.join(ROOT, 'writing', 'figures')

# MEAN HOUSEHOLD INCOME, the dollar anchor for the VSL sentence in Section 3: CPS ASEC mean household
# income, in the dollars the text quotes.  Moved here from stage_results.py, which now reads it from here.
MEAN_HH_INCOME_USD = 113000.0
# HOW FAR PAST THE CALIBRATED STRENGTH FIGURE 1 RUNS.  It was twice (the author, 29 September: "from
# nothing to twice the penalty") in the old model; in this one the band of users slides down the income
# distribution so fast as the risk strengthens that at about 1.25 times the calibrated strength it reaches
# the floor, the households there start to use, and with 15 per cent of households at that one income
# participation can no longer be held at its target.  So the figure stops at 1.2, the last point where the
# floor is inert, which scan() asserts at every point.
SCAN_HI = 1.2
# THE INCOME FLOOR, as a share of mean income: see the head of this file.
Y_FLOOR = 0.24


def _drug_data():
    with open(os.path.join(ROOT, 'data', 'drug_spending_target.csv')) as fh:
        return {r['quantity']: float(r['value']) for r in csv.DictReader(fh)}


_D = _drug_data()
# THE FOUR TARGETS, each read from where it already lives: the NSDUH participation rate from data/, the
# drug spending share, the users' income and the VSL from the quantitative model's declarations, so the two
# models aim at one number.
TARGET = dict(vsl=float(FC['vsl_data']),
              part=_D['participation'],
              dshare=float(FC['drug_spending_share_data']),
              r_use=float(FC['drug_user_income_data']))
SUD_RATE = _D['sud_rate']
# sigma_y IS SET OUTSIDE THE MODEL: a lognormal's bottom half holds Phi(-sigma_y) of the total, so the SCF's
# 17.2 per cent pins it exactly, before the floor.
SIG_Y = brentq(lambda s: ndtr(-s) - BOT50_TARGET, 0.05, 4.0)

_P = P()
FIXED = dict(beta=_P.beta, sigma=_P.sigma, phibar=_P.phi0, years=_P.years, p_v=1.0,
             pi_d=SUD_RATE / TARGET['part'], sig_y=SIG_Y, y_min=Y_FLOOR)
FREE = ('aleph', 'b', 'theta', 'kappa')
MOMENT_OF = dict(aleph='vsl', b='part', theta='dshare', kappa='r_use')


# ---------------------------------------------------------------------------------------------------
def U(X, s):
    return np.log(X) if s == 1.0 else X ** (1.0 - s) / (1.0 - s)


def X0(y, q):
    return y ** (1.0 - q['theta']) * q['b'] ** q['theta']


def X1(y, q):
    th, p = q['theta'], q['p_v']
    return (1.0 - th) ** (1.0 - th) * (th / p) ** th * (y + p * q['b'])


def W2(y, q):
    return U(X0(y, q), q['sigma']) + q['aleph']


def y_sg(q):
    """The income below which no positive quantity of the drug is worth buying."""
    return (1.0 - q['theta']) * q['p_v'] * q['b'] / q['theta']


def gain(y, q):
    """What the drug is worth in period-1 utility, zero below y_sg."""
    g = U(X1(y, q), q['sigma']) - U(X0(y, q), q['sigma'])
    return np.where(y > y_sg(q), g, 0.0)


def mort_cost(y, q):
    """Expected loss of the life still to be lived, from using at all."""
    return q['beta'] * q['pi_d'] * (q['phibar'] - q['phibar'] ** q['kappa']) * W2(y, q)


def D(y, q):
    return gain(y, q) - mort_cost(y, q)


def y_zero(q):
    """The income at which being alive is worth nothing, W2 = 0."""
    s = q['sigma']
    xz = (q['aleph'] * (s - 1.0)) ** (-1.0 / (s - 1.0))
    return (xz / q['b'] ** q['theta']) ** (1.0 / (1.0 - q['theta']))


class Dist:
    """Lognormal with dispersion s and raw mean one, incomes below the floor raised to it, everything then
    divided by the new mean so that mean income is one and the floor is m in those units."""

    def __init__(self, s, m):
        self.s, self.m = s, m
        lo, hi = 1e-9, 0.99
        for _ in range(200):
            t = 0.5 * (lo + hi)
            if t / self._mean(t) < m:
                lo = t
            else:
                hi = t
        self.t = 0.5 * (lo + hi)
        self.M = self._mean(self.t)

    def _F(self, x):
        return ndtr((np.log(x) + 0.5 * self.s ** 2) / self.s)

    def _PE(self, x):
        return ndtr((np.log(x) - 0.5 * self.s ** 2) / self.s)

    def _mean(self, t):
        return t * self._F(t) + 1.0 - self._PE(t)

    @property
    def floor_share(self):
        return float(self._F(self.t))

    def F(self, y):
        """Share of households with income at or below y (y above the floor, normalised units)."""
        return self._F(np.asarray(y, dtype=float) * self.M)

    def PE(self, y):
        """Income of households at or below y, as a share of total income (y above the floor)."""
        x = np.asarray(y, dtype=float) * self.M
        return (self.t * self._F(self.t) + self._PE(x) - self._PE(self.t)) / self.M

    def quantile(self, p):
        if p <= self.floor_share:
            return self.m
        return brentq(lambda y: float(self.F(y)) - p, self.m, 1e3)


def full(free, fixed=FIXED):
    q = dict(fixed)
    q.update(dict(zip(FREE, free)))
    return q


def use_set(q):
    """The intervals of income on which the household uses, above the floor."""
    lo = max(y_sg(q), q['y_min']) * (1.0 + 1e-9)
    grid = np.exp(np.linspace(np.log(lo), np.log(80.0), 4000))
    d = D(grid, q)
    out, start = [], None
    for i in range(len(grid)):
        if d[i] > 0 and start is None:
            start = grid[0] if i == 0 else brentq(lambda y: float(D(y, q)), grid[i - 1], grid[i])
        if d[i] <= 0 and start is not None:
            out.append((start, brentq(lambda y: float(D(y, q)), grid[i - 1], grid[i])))
            start = None
    if start is not None:
        out.append((start, grid[-1]))
    return out


def vsl(q, y=1.0):
    """The VSL of a household at mean income, in annual incomes: what it would pay in period-1
    consumption for survival, beta times the expected period-2 value per unit of survival over the
    marginal utility of consumption, times the years in a period, as stylized.vsl computes it."""
    s, th, p = q['sigma'], q['theta'], q['p_v']
    if float(D(y, q)) > 0:
        X, c, pr = X1(y, q), (1.0 - th) * (y + p * q['b']), q['pi_d']
    else:
        X, c, pr = X0(y, q), y, 0.0
    ew = ((1.0 - pr) + pr * q['phibar'] ** (q['kappa'] - 1.0)) * W2(y, q)
    u_c = (1.0 - th) * X ** (1.0 - s) / c
    return float(q['beta'] * ew / u_c * q['years'])


def moments(q):
    dist = Dist(q['sig_y'], q['y_min'])
    iv = use_set(q)
    part = sum(float(dist.F(b) - dist.F(a)) for a, b in iv)
    inc = sum(float(dist.PE(b) - dist.PE(a)) for a, b in iv)
    p, th, b = q['p_v'], q['theta'], q['b']
    spend = th * (inc + p * b * part) - p * b * part
    return dict(part=part, r_use=inc / part if part > 0 else float('nan'),
                dshare=spend / inc if inc > 0 else float('nan'), vsl=vsl(q), intervals=iv,
                bot50=float(dist.PE(dist.quantile(0.5))), floor_share=dist.floor_share, dist=dist)


def kappa_for_part(q, part):
    """kappa that puts participation at `part`, everything else held.  Participation falls in kappa at
    every income, since the mortality cost rises and the drug's worth does not move."""
    def f(lk):
        return moments({**q, 'kappa': 1.0 + math.exp(lk)})['part'] - part
    lo, hi = math.log(1e-4), math.log(50.0)
    assert f(lo) > 0 > f(hi), 'participation not bracketed in kappa'
    return 1.0 + math.exp(brentq(f, lo, hi, xtol=1e-14))


def _resid(z, fixed):
    """vsl, dshare and r_use on (aleph, b, theta); kappa solved inside on participation, which keeps
    the band of users from vanishing at a trial point and leaving the fit on a flat surface."""
    al, b, th = np.exp(z)
    q = full([al, b, th, 2.0], fixed)
    try:
        q['kappa'] = kappa_for_part(q, TARGET['part'])
    except (AssertionError, ValueError):
        return np.full(3, 10.0)
    m = moments(q)
    return np.array([m[k] / TARGET[k] - 1.0 for k in ('vsl', 'dshare', 'r_use')])


def calibrate(start=None, fixed=FIXED):
    """aleph on the VSL, theta on the spending share, b and kappa on participation and the users'
    income, the last two jointly: b moves where the band of users sits, kappa how wide it is."""
    s = start or dict(aleph=6.44, b=0.0554, theta=0.218)
    r = least_squares(_resid, np.log([s['aleph'], s['b'], s['theta']]), args=(fixed,),
                      xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=2000)
    al, b, th = np.exp(r.x)
    q = full([al, b, th, 2.0], fixed)
    q['kappa'] = kappa_for_part(q, TARGET['part'])
    return q


def b_for_part(q, part, b0):
    """b that puts participation at `part`, everything else held, found next to b0 (participation is not
    monotone in b over its whole range, so the bracket is grown outwards from a neighbour's value)."""
    def f(lb):
        return moments({**q, 'b': math.exp(lb)})['part'] - part
    l0 = math.log(b0)
    f0 = f(l0)
    if f0 == 0:
        return b0
    for step in (0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8):
        for sgn in (1, -1):
            l1 = l0 + sgn * step
            if f(l1) * f0 < 0:
                return math.exp(brentq(f, min(l0, l1), max(l0, l1), xtol=1e-14))
    raise ValueError('b not bracketed near %g' % b0)


def scan(q, n=49):
    """Figure 1: kappa - 1 scaled from nothing to SCAN_HI times its calibrated value, b refit at every
    point so participation stays at its calibrated level, walking out from the calibrated point so each
    refit starts next to its neighbour's.  Every point is checked for the two things the floor is there
    to guarantee, and for a single band of users."""
    ref = moments(q)['part']
    sc = np.linspace(0.0, SCAN_HI, n)
    i1 = int(np.argmin(np.abs(sc - 1.0)))
    r, bs = np.zeros(n), np.zeros(n)
    for order in (range(i1, -1, -1), range(i1, n)):
        b = q['b']
        for i in order:
            g = {**q, 'kappa': 1.0 + sc[i] * (q['kappa'] - 1.0)}
            g['b'] = b = b_for_part(g, ref, b)
            m = moments(g)
            assert W2(g['y_min'], g) > 0 and float(D(g['y_min'], g)) <= 0, ('floor', sc[i])
            assert len(m['intervals']) == 1, ('bands', sc[i], m['intervals'])
            r[i], bs[i] = m['r_use'], b
    return sc, r


# ---------------------------------------------------------------------------------------------------
def tn(x, nd=2):
    return f'{x:.{nd}f}'


def write_tables(q, m):
    ext = [
        (r'$\beta$', 'Discount factor over a thirty-year period',
         f'${q["beta"] ** (1 / q["years"]):.3f}$ annually, compounded', f'${tn(q["beta"])}$'),
        (r'$\sigma$', 'Risk aversion', 'Standard; Attanasio and Weber (2010)', f'${q["sigma"]:.0f}$'),
        (r'$\bar\phi$', 'Survival over a period, no SUD',
         'US life table 2010, Arias (2014), ages 26--55', f'${tn(q["phibar"])}$'),
        (r'$\pi_d$', 'Chance that use starts a SUD', 'NSDUH 2024: SUD rate over participation',
         f'${tn(q["pi_d"])}$'),
        (r'$\sigma_y$', 'Dispersion of log income',
         f'SCF 2022: bottom half holds {100 * BOT50_TARGET:.1f}\\% of earnings', f'${tn(q["sig_y"])}$'),
        (r'$y_{\min}$', 'Income floor, over mean income', 'Every household values being alive',
         f'${tn(q["y_min"])}$'),
        (r'$p_v$', 'Price of a unit of drugs', 'Normalisation', f'${tn(q["p_v"])}$'),
    ]
    T = TARGET
    intl = [
        (r'$\aleph$', 'VSL over income', f'{T["vsl"]:.0f}', f'{m["vsl"]:.1f}', tn(q['aleph'])),
        (r'$b$', 'Drug participation, NSDUH 2024', f'{100 * T["part"]:.1f}\\%',
         f'{100 * m["part"]:.1f}\\%', f'{q["b"]:.3f}'),
        (r'$\theta$', "Drug spending over users' income", f'{100 * T["dshare"]:.1f}\\%',
         f'{100 * m["dshare"]:.1f}\\%', tn(q['theta'])),
        (r'$\kappa_{\phi d}$', "Users' income over the average, NSDUH 2024", tn(T['r_use']),
         tn(m['r_use']), tn(q['kappa'])),
    ]
    head = '% Generated by code/stylized/gradient.py.\n\\footnotesize\n'
    with open(os.path.join(TABLES, 'tab_external.tex'), 'w') as f:
        f.write(head + '\\begin{tabular}{@{}lllr@{}}\n\\toprule\n'
                'Parameter & Description & Source or rationale & Value \\\\\n\\midrule\n')
        f.writelines(' & '.join(r) + ' \\\\\n' for r in ext)
        f.write('\\bottomrule\n\\end{tabular}\n')
    with open(os.path.join(TABLES, 'tab_internal.tex'), 'w') as f:
        f.write(head + '\\begin{tabular}{@{}llrrr@{}}\n\\toprule\n'
                'Parameter & Target moment & Data & Model & Value \\\\\n\\midrule\n')
        f.writelines(' & '.join(r) + ' \\\\\n' for r in intl)
        f.write('\\bottomrule\n\\end{tabular}\n')
    print('   wrote tables/tab_external.tex, tables/tab_internal.tex')


def draw(sc, r):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 11, 'figure.dpi': 170,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': 0.22, 'lines.linewidth': 2.4})
    fig, ax = plt.subplots(figsize=(7.0, 4.3))
    ax.plot(100 * sc, r, color='#2C6FAD')
    ax.axhline(1.0, color='0.45', lw=1.0)
    ax.axvline(100, color='black', lw=1.0, ls=':')
    top = max(r) * 1.04
    ax.set_ylim(0, top)
    ax.annotate('calibrated', xy=(100, 0.97 * top), ha='center', va='top', fontsize=8,
                bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='none'))
    i1 = int(np.argmin(np.abs(sc - 1.0)))
    ax.plot([100], [r[i1]], 'o', ms=9, mfc='none', mec='black', mew=1.4, zorder=5)
    for x, y, dx, dy in ((0, r[0], 4, 4), (100 * sc[-1], r[-1], 4, -2)):
        ax.annotate(f'{y:.2f}', xy=(x, y), xytext=(dx, dy), textcoords='offset points',
                    fontsize=8.5, color='#2C6FAD', fontweight='bold', va='center')
    ax.set_xlabel('Strength of the mortality risk of a SUD, percent of its calibrated value')
    ax.set_ylabel('Mean income of users / population mean')
    ax.set_xlim(-3, 100 * SCAN_HI + 11)
    fig.tight_layout()
    for ext in ('.pdf', '.png'):
        fig.savefig(os.path.join(FIGURES, 'stylized_who_uses' + ext), bbox_inches='tight')
    print('   wrote figures/stylized_who_uses.pdf')


def numbers(q, m, sc, r):
    dist = m['dist']
    (ylo, yhi), = m['intervals']
    # where users' income crosses the population mean, by linear interpolation on the scan
    k = int(np.argmax(r < 1.0))
    cross = sc[k - 1] + (1.0 - r[k - 1]) * (sc[k] - sc[k - 1]) / (r[k] - r[k - 1])
    d = dict(
        g_beta=tn(q['beta']), g_beta_ann=f'{q["beta"] ** (1 / q["years"]):.3f}', g_sigma=f'{q["sigma"]:.0f}',
        g_phi0=tn(q['phibar']), g_pid=tn(q['pi_d']), g_t_sud=tn(100 * SUD_RATE), g_t_part=tn(100 * TARGET['part']),
        g_t_bot50=f'{100 * BOT50_TARGET:.1f}', g_sigy=tn(q['sig_y']), g_yfloor=tn(q['y_min']),
        g_floor_share_pc=f'{100 * m["floor_share"]:.0f}', g_yzero=tn(y_zero(q)),
        g_t_vsl=f'{TARGET["vsl"]:.0f}', g_vsl_musd=f'{TARGET["vsl"] * MEAN_HH_INCOME_USD / 1e6:.1f}',
        g_mean_hh_usd=f'{MEAN_HH_INCOME_USD:,.0f}', g_t_dshare=f'{100 * TARGET["dshare"]:.1f}',
        g_t_ruse=tn(TARGET['r_use']),
        g_aleph=tn(q['aleph']), g_b=f'{q["b"]:.3f}', g_theta=tn(q['theta']), g_kappa=tn(q['kappa']),
        g_ysg=tn(y_sg(q)), g_ylo=tn(ylo), g_yhi=tn(yhi),
        g_pct_lo=f'{100 * float(dist.F(ylo)):.0f}', g_pct_hi=f'{100 * float(dist.F(yhi)):.0f}',
        g_pct_sg=f'{100 * float(dist.F(y_sg(q))):.0f}',
        g_r_none=tn(r[0]), g_r_cal=tn(r[int(np.argmin(np.abs(sc - 1.0)))]), g_r_hi=tn(r[-1]),
        g_scanhi_pc=f'{100 * SCAN_HI:.0f}', g_cross_pc=f'{100 * cross:.0f}',
    )
    json.dump(d, open(os.path.join(HERE, 'gradient_numbers.json'), 'w'), indent=1, sort_keys=True)
    return d


def main():
    q = calibrate()
    m = moments(q)
    print('  calibrated:', ', '.join(f'{k}={q[k]:.5g}' for k in FREE))
    print('  moments:   ', ', '.join(f'{MOMENT_OF[k]}={m[MOMENT_OF[k]]:.5g} ({TARGET[MOMENT_OF[k]]:.5g})'
                                     for k in FREE))
    for k in FREE:
        assert abs(m[MOMENT_OF[k]] / TARGET[MOMENT_OF[k]] - 1.0) < 1e-6, k
    assert len(m['intervals']) == 1 and W2(q['y_min'], q) > 0 and float(D(q['y_min'], q)) <= 0
    json.dump({k: q[k] for k in q}, open(os.path.join(HERE, 'gradient.json'), 'w'), indent=1)
    sc, r = scan(q)
    write_tables(q, m)
    draw(sc, r)
    d = numbers(q, m, sc, r)
    for k, v in sorted(d.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
