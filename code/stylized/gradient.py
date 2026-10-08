"""
THE STYLIZED MODEL, STRIPPED TO THE INCOME GRADIENT IN DRUG USE.

The author, 8 October: *"isnt the point of the stylized model just to show how the mortality reverses
the income gradient?"*, *"we can leave all the rest for the quant model"*, *"then we only need stage 1"*,
*"we then also dont need a governmtn"* and *"it would be good to strip everything possible from the
model"*.  So Section 3 is this file and nothing else: no saving, no housing, no employment risk, no
government, no child.  The staged model (stages.py, stage_results.py, stylized.py) is the record of
what came before and is no longer read by the paper.

THE MODEL.  Two periods of thirty years.  Income y, fixed for life, is lognormal with dispersion sigma_y,
truncated below at y_min, and normalised to mean one.  Period 1: everyone works, c + p_v v = y, the bundle
X = c^(1-theta) (b+v)^theta, flow utility U(X) + aleph with U(X) = X^(1-sigma)/(1-sigma).  Using at all
(v > 0) gives a SUD with probability pi_d, whatever the quantity, and a SUD cuts survival into period 2
from phibar to phibar^kappa.  Period 2: no drug; the household is out of work with probability u0, or u1
with a SUD (the author, 8 October: "the unemployment risk should just happen in period 2. So everyone is
employed in period 1"), and out of work it loses its whole income and lives on y_min ("Nothing, down to
the floor"; "We should also not have ui.. Just full income loss").  So the value of period 2 is
W2(y, d) = (1 - u_d) U(X0(y)) + u_d U(X0(y_min)) + aleph, with X0(y) = y^(1-theta) b^theta.

THE DECISION IS IN CLOSED FORM.  Given that it uses, a household buys the Cobb-Douglas quantity on full
income y + p_v b, so X1 = (1-theta)^(1-theta) (theta/p_v)^theta (y + p_v b), and v > 0 only above
y_sg = (1-theta) p_v b / theta.  It uses if and only if

    D(y) = U(X1(y)) - U(X0(y)) - beta pi_d [phibar W2(y, 0) - phibar^kappa W2(y, 1)] > 0.

The first two terms are what the drug is worth, the last the expected loss from a SUD, which splits into
the mortality channel, beta pi_d (phibar - phibar^kappa) W2(y, 1), and the unemployment channel,
beta pi_d phibar (u1 - u0) [U(X0(y)) - U(X0(y_min))].  Both rise with income: dying takes old age and
aleph, unemployment takes the household down to y_min whatever it earned.  D is negative at y_sg, where
the drug is worth nothing, and at the top, so the users sit in a band.  Every moment is an integral of the
lognormal over that band, analytic, so the calibration is a smooth root-find in seconds.

THE FLOOR, y_min, and why there has to be one (the author, 8 October: "You don't need to explain the
income floor to the reader", so the paper only states it).  With sigma = 2 the value of being alive is
negative at a low enough income, and a household for which it is negative would buy a sliver of drug for
the mortality it brings (negative_value_of_life.py is the record of that defect in the old model).  The
quantitative model's safety net rules that out there; here the lowest income anyone has, in or out of
work, is y_min = 0.24 of the mean, where being alive is still worth something (it is worth nothing at
about 0.21).  What was tried on 8 October:
  - TRUNCATING at the income where being alive is worth nothing, sigma_y fitted to the bottom half's share
    after the cut: sigma_y 1.32, 44 per cent of the lognormal cut, and a sliver of spurious users just
    above the cut, whose life is worth almost nothing to lose.  Failed.
  - POOLING everyone below 0.24 at 0.24, sigma_y set on the lognormal before it: fine at the calibrated
    point, but 15 per cent of households sit at one income, and past about 1.25 times the calibrated
    mortality the band of users reaches that atom, the whole atom starts to use at once, and participation
    cannot be held for Figure 1.  Replaced, because the author wants the figure to run to twice the
    calibrated strength.
  - TRUNCATING at 0.24, sigma_y set on the lognormal before the cut (current): no atom, so as either
    channel strengthens the users slide smoothly to the bottom of the distribution.

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
# HOW FAR PAST THE CALIBRATED STRENGTH FIGURE 1 RUNS, the author, 29 September: "from nothing to twice the
# penalty", and 8 October: "No, don't cap the scan", "Just show up to 200%".
SCAN_HI = 2.0
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
# THE TWO UNEMPLOYMENT RATES, read from the quantitative model's declarations: the aggregate rate, FRED
# UNRATE averaged over 2014 to 2024, and the rate among adults aged 26 and over with a SUD, NSDUH 2024.
U0 = float(FC['unemployment_rate_data'])
U1 = float(FC['unemployment_rate_sud_data'])
FIXED = dict(beta=_P.beta, sigma=_P.sigma, phibar=_P.phi0, years=_P.years, p_v=1.0,
             pi_d=SUD_RATE / TARGET['part'], sig_y=SIG_Y, y_min=Y_FLOOR, u0=U0, u1=U1)
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


def W2(y, q, d=0):
    """The value of period 2 with SUD status d: out of work with probability u_d, on y_min."""
    u = q['u1'] if d else q['u0']
    s = q['sigma']
    return (1.0 - u) * U(X0(y, q), s) + u * U(X0(q['y_min'], q), s) + q['aleph']


def y_sg(q):
    """The income below which no positive quantity of the drug is worth buying."""
    return (1.0 - q['theta']) * q['p_v'] * q['b'] / q['theta']


def gain(y, q):
    """What the drug is worth in period-1 utility, zero below y_sg."""
    g = U(X1(y, q), q['sigma']) - U(X0(y, q), q['sigma'])
    return np.where(y > y_sg(q), g, 0.0)


def cost(y, q):
    """Expected loss from using at all: the chance of a SUD times what it takes from period 2, through
    survival and through employment."""
    return q['beta'] * q['pi_d'] * (q['phibar'] * W2(y, q, 0) - q['phibar'] ** q['kappa'] * W2(y, q, 1))


def D(y, q):
    return gain(y, q) - cost(y, q)


def y_zero(q):
    """The income at which being alive is worth nothing, W2 = 0."""
    s = q['sigma']
    xz = (q['aleph'] * (s - 1.0)) ** (-1.0 / (s - 1.0))
    return (xz / q['b'] ** q['theta']) ** (1.0 / (1.0 - q['theta']))


class Dist:
    """Lognormal with dispersion s and raw mean one, truncated below, the survivors renormalised to mean
    one, so that the lowest income is m in those units."""

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
        self.Ft, self.Pt = float(self._F(self.t)), float(self._PE(self.t))

    def _F(self, x):
        return ndtr((np.log(x) + 0.5 * self.s ** 2) / self.s)

    def _PE(self, x):
        return ndtr((np.log(x) - 0.5 * self.s ** 2) / self.s)

    def _mean(self, t):
        return (1.0 - self._PE(t)) / (1.0 - self._F(t))

    @property
    def cut_share(self):
        return self.Ft

    def F(self, y):
        """Share of households with income below y (normalised units, y at or above the bound)."""
        x = np.maximum(np.asarray(y, dtype=float) * self.M, self.t)
        return (self._F(x) - self.Ft) / (1.0 - self.Ft)

    def PE(self, y):
        """Income of households below y, as a share of total income."""
        x = np.maximum(np.asarray(y, dtype=float) * self.M, self.t)
        return (self._PE(x) - self.Pt) / (1.0 - self.Pt)

    def quantile(self, p):
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
    ew = (1.0 - pr) * W2(y, q, 0) + pr * q['phibar'] ** (q['kappa'] - 1.0) * W2(y, q, 1)
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
                bot50=float(dist.PE(dist.quantile(0.5))), cut_share=dist.cut_share, dist=dist)


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
    for step in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6):
        for sgn in (1, -1):
            l1 = l0 + sgn * step
            if f(l1) * f0 < 0:
                return math.exp(brentq(f, min(l0, l1), max(l0, l1), xtol=1e-14))
    raise ValueError('b not bracketed near %g' % b0)


def channel(q, which, x):
    """The economy with one channel at x times its calibrated strength and the other switched off."""
    k = 1.0 + x * (q['kappa'] - 1.0)
    u = q['u0'] + x * (q['u1'] - q['u0'])
    if which == 'mortality':
        return {**q, 'kappa': k, 'u1': q['u0']}
    if which == 'unemployment':
        return {**q, 'kappa': 1.0, 'u1': u}
    return {**q, 'kappa': k, 'u1': u}           # both, scaled together: the calibrated model at x = 1


def scan(q, which, n=81):
    """Figure 1: one channel scaled from nothing to SCAN_HI times its calibrated value with the other
    switched off, b refit at every point so participation stays at its calibrated level, so only who uses
    changes.  Both curves start from the same economy, the one in which a SUD has no consequences, where
    the users are everyone above y_sg and b follows in closed form; the walk goes up from there, each refit
    starting next to its neighbour's.  Every point is checked: the value of being alive positive at the
    bottom, and participation held."""
    ref = moments(q)['part']
    sc = np.linspace(0.0, SCAN_HI, n)
    g = channel(q, which, 0.0)
    ysg = Dist(g['sig_y'], g['y_min']).quantile(1.0 - ref)
    b = g['theta'] * ysg / ((1.0 - g['theta']) * g['p_v'])
    r = np.zeros(n)
    for i, x in enumerate(sc):
        g = channel(q, which, x)
        g['b'] = b = b_for_part(g, ref, b)
        m = moments(g)
        assert W2(g['y_min'], g) > 0, ('value of being alive at the bottom', which, x)
        # NOT ONE BAND EVERYWHERE: with the unemployment channel alone past about 1.6 times its strength, b falls
        # far enough that the very poorest find the drug worth buying, and unemployment takes nothing from a
        # household already on y_min, so a hair-thin band uses at the bottom.  moments() counts every band.
        assert abs(m['part'] / ref - 1.0) < 1e-8, ('participation', which, x)
        r[i] = m['r_use']
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
        (r'$y_{\min}$', 'Lowest income, over mean income', 'Set', f'${tn(q["y_min"])}$'),
        (r'$u_0$', 'Unemployment rate in period 2, no SUD', 'BLS CPS, average 2014--2024',
         f'${q["u0"]:.3f}$'),
        (r'$u_1$', 'Unemployment rate in period 2 with a SUD', 'NSDUH 2024, ages 26 and over',
         f'${tn(q["u1"])}$'),
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


def draw(curves):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10.5, 'figure.dpi': 170, 'font.family': 'serif',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': 0.18, 'grid.linestyle': '-',
                         'legend.frameon': False, 'lines.linewidth': 2.2})
    col = dict(mortality='#1F5A99', unemployment='#C0662B', both='black')
    lab = dict(mortality='Mortality risk alone', unemployment='Unemployment risk alone', both='Both')
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    top = 1.08 * max(max(r) for _, r in curves.values())
    ax.axhspan(0, 1, color='0.93', zorder=0)
    ax.text(3, 0.5, 'users poorer than average', ha='left', va='center', fontsize=8.5, color='0.45')
    ax.axhline(1.0, color='0.55', lw=0.9, zorder=1)
    ax.axvline(100, color='black', lw=0.9, ls=(0, (2, 2)), zorder=1)
    ax.text(100, top, 'calibrated ', ha='right', va='top', fontsize=8.5)
    for which in ('both', 'mortality', 'unemployment'):
        sc, r = curves[which]
        ax.plot(100 * sc, r, color=col[which], label=lab[which], zorder=3,
                lw=2.6 if which == 'both' else 2.0)
        i1 = int(np.argmin(np.abs(sc - 1.0)))
        ax.plot([100], [r[i1]], 'o', ms=5.5, color=col[which], zorder=4)
        ax.annotate(f'{r[-1]:.2f}', xy=(100 * sc[-1], r[-1]), xytext=(5, 0), textcoords='offset points',
                    fontsize=8.5, color=col[which], va='center')
    r0 = curves['mortality'][1][0]
    ax.annotate(f'{r0:.2f}', xy=(0, r0), xytext=(5, 5), textcoords='offset points', fontsize=8.5)
    ax.set_xlim(0, 100 * SCAN_HI + 14)
    ax.set_ylim(0, top)
    ax.set_xticks(np.arange(0, 100 * SCAN_HI + 1, 25))
    ax.set_xlabel('Strength of the channel, percent of its calibrated value')
    ax.set_ylabel('Mean income of users / population mean')
    ax.legend(loc='upper right', bbox_to_anchor=(1.0, 0.93), fontsize=9)
    fig.tight_layout()
    for ext in ('.pdf', '.png'):
        fig.savefig(os.path.join(FIGURES, 'stylized_who_uses' + ext), bbox_inches='tight')
    print('   wrote figures/stylized_who_uses.pdf')


def _cross(sc, r):
    """Where the users' income first falls below the population mean, by linear interpolation; None if it
    never does on the scan."""
    k = int(np.argmax(r < 1.0))
    if r[k] >= 1.0:
        return None
    return sc[k - 1] + (1.0 - r[k - 1]) * (sc[k] - sc[k - 1]) / (r[k] - r[k - 1])


def numbers(q, m, curves):
    dist = m['dist']
    (ylo, yhi), = m['intervals']
    at = lambda which, x: curves[which][1][int(np.argmin(np.abs(curves[which][0] - x)))]
    cm, cu, cb = (_cross(*curves[w]) for w in ('mortality', 'unemployment', 'both'))
    d = dict(
        g_beta=tn(q['beta']), g_beta_ann=f'{q["beta"] ** (1 / q["years"]):.3f}', g_sigma=f'{q["sigma"]:.0f}',
        g_phi0=tn(q['phibar']), g_pid=tn(q['pi_d']), g_t_sud=tn(100 * SUD_RATE), g_t_part=tn(100 * TARGET['part']),
        g_t_bot50=f'{100 * BOT50_TARGET:.1f}', g_sigy=tn(q['sig_y']), g_yfloor=tn(q['y_min']),
        g_u0_pc=f'{100 * q["u0"]:.1f}', g_u1_pc=f'{100 * q["u1"]:.1f}',
        g_t_vsl=f'{TARGET["vsl"]:.0f}', g_vsl_musd=f'{TARGET["vsl"] * MEAN_HH_INCOME_USD / 1e6:.1f}',
        g_mean_hh_usd=f'{MEAN_HH_INCOME_USD:,.0f}', g_t_dshare=f'{100 * TARGET["dshare"]:.1f}',
        g_t_ruse=tn(TARGET['r_use']),
        g_aleph=tn(q['aleph']), g_b=f'{q["b"]:.3f}', g_theta=tn(q['theta']), g_kappa=tn(q['kappa']),
        g_ysg=tn(y_sg(q)), g_pct_sg=f'{100 * float(dist.F(y_sg(q))):.0f}',
        g_r_none=tn(curves['mortality'][1][0]),
        g_rm_cal=tn(at('mortality', 1.0)), g_rm_hi=tn(at('mortality', SCAN_HI)),
        g_ru_cal=tn(at('unemployment', 1.0)), g_ru_hi=tn(at('unemployment', SCAN_HI)),
        g_scanhi_pc=f'{100 * SCAN_HI:.0f}',
        g_cross_m_pc=f'{100 * cm:.0f}' if cm is not None else '',
        g_cross_u_pc=f'{100 * cu:.0f}' if cu is not None else '',
        g_cross_b_pc=f'{100 * cb:.0f}' if cb is not None else '',
        g_rb_cal=tn(at('both', 1.0)), g_rb_hi=tn(at('both', SCAN_HI)),
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
    assert len(m['intervals']) == 1 and W2(q['y_min'], q) > 0
    print(f'  bound {q["y_min"]}: {100 * m["cut_share"]:.1f} per cent of the lognormal cut; being alive worth '
          f'nothing at {y_zero(q):.3f}; users {m["intervals"]}, y_sg {y_sg(q):.3f}')
    json.dump({k: q[k] for k in q}, open(os.path.join(HERE, 'gradient.json'), 'w'), indent=1)
    curves = {w: scan(q, w) for w in ('mortality', 'unemployment', 'both')}
    for w, (sc, r) in curves.items():
        print(f'  {w:12s}', ' '.join(f'{x:.2f}' for x in r[::4]))
    write_tables(q, m)
    draw(curves)
    d = numbers(q, m, curves)
    for k, v in sorted(d.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
