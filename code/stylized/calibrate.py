"""
Calibrating the stylised model.

WHAT IS TARGETED, AND WHAT IS DELIBERATELY NOT

    b        drug participation rate                     5.13 %
    kap      price elasticity of participation          -0.45
    lam      share of users who acquire the disorder    71.7 %
    xi       income with the disorder / average          0.687
    pr       housing spending / income                    21.2 %
    dis_hl   homelessness rate                           0.399 %
    aleph    value of a statistical life / PERIOD income  5.36

    HELD OUT  income of USERS / average                  0.951
    HELD OUT  share of the homeless with the disorder    21.7 %

The income gradient of USE is never targeted. It is the fact the mechanism is
supposed to explain, so fitting it would make the exercise circular. Everything
that identifies the mortality channel comes from the PRICE ELASTICITY instead,
exactly as in the full model, which leaves the gradient as an out of sample check.

The unemployment rate given the disorder is set externally to the measured 16.25
per cent rather than calibrated, because it IS a moment: NSDUH 2024 microdata,
ages 26 and above, weighted.

WHY A JOINT FIT AND NOT ONE BISECTION PER PARAMETER

Coordinate bisection assumes each parameter dominates one moment. That is false
here, in an instructive way. Raising the addiction hazard lam raises the disorder
rate MECHANICALLY but lowers it in EQUILIBRIUM, because households respond by
using less. The partial and the total derivative have opposite signs, so a
bracket built on the partial sign walks lam to its bound; from there participation
saturates, the price elasticity collapses to zero, and every other bracket loses
its signal too. That is what happened on the first attempt. The Jacobian below
reports it rather than hiding it, and it is a caution that applies to the full
model's calibration as well.
"""

import numpy as np
from stylized import P, with_, aggregates, price_elasticity

YG = np.exp(np.linspace(np.log(0.15), np.log(5.0), 34))
W  = np.exp(-0.5 * ((np.log(YG) + 0.5 * 0.75**2) / 0.75)**2)

# THE VALUE OF LIFE TARGET IS IN PERIOD INCOMES, NOT ANNUAL ONES.
# A 7.5 million dollar VSL against 70,000 of annual income is 107 ANNUAL
# incomes. Three periods span roughly ages 26 to 85, so a period is about 20
# years and period income is 20 annual incomes: the target is 107/20 = 5.36.
# Targeting 107 asks for a value of life twenty times too large, which makes the
# marginal mortality cost of drug use so big that nobody uses anywhere in the
# parameter space, and the fit dies with participation at zero.
# The progression target is a TRANSITION rate, not the cross sectional ratio.
#
# NSDUH gives 5.13 per cent using and 3.68 per cent with a disorder, and 3.68 /
# 5.13 = 0.717 is tempting. It is the wrong object here: those are stocks
# measured in one cross section, while this model's period 1 households use and
# its period 2 households carry the disorder, so the model analogue is a flow
# over one period. Targeting 0.717 asks the model to convert 72 per cent of
# users within a single period, which needs an addiction hazard so high that
# nobody uses enough to be exposed to it, and the fit stalls with progression at
# 8 per cent. The full model's annual hazard given any use is 2 per cent, so
# over a twenty year period 1 - 0.98^20 = 0.332.
TARGET = dict(part=0.0513, spend=0.11, elast_p=-0.45, prog=0.332, r_sud=0.687,
              homeless=0.00399, housing_share=0.212, vsl=5.36)

FREE = [('b',     1e-5, 3.0),
        ('th',    2e-3, 4.00),
        ('kap',   0.02, 0.95),
        ('lam',   0.20, 400.0),
        ('xi',      0.01, 0.85),
        ('pr',      0.02, 0.60),
        ('dis_hl',  0.02, 6.00),
        ('aleph',   0.20, 400.0)]

LABEL = {'part': 'drug participation rate',
         'elast_p': 'price elasticity of participation',
         'prog': 'share of users who acquire the disorder',
         'r_sud': 'income with the disorder / average',
         'homeless': 'homelessness rate',
         'sud_of_homeless': 'share of homeless with the disorder',
         'vsl': 'value of a statistical life / mean income',
         'spend': 'drug spending / income, among users',
         'housing_share': 'housing spending / income'}


def stats(par, ygrid=None, w=None):
    ygrid = YG if ygrid is None else ygrid
    w = W if w is None else w
    m = aggregates(par, ygrid, w)
    m['prog'] = m['sud'] / max(m['part'], 1e-12)
    m['elast_p'] = price_elasticity(par, ygrid, w)
    return m


def loss(par, targets=None, free=None):
    """
    Squared LOG ratio, not squared relative gap.

    A relative gap saturates: a moment 27 times too small and a moment 30 per
    cent too small both contribute about one, so the optimiser cannot tell which
    to fix and drifts. In logs, being 27 times out costs (log 27)^2 = 10.9
    against 0.13 for 30 per cent, which is the ordering the fit needs.
    """
    t = targets or TARGET
    m = stats(par)
    tot = 0.0
    for k in t:
        a, b_ = m[k], t[k]
        if a * b_ <= 0.0:            # wrong sign, or dead: penalise hard
            tot += 25.0
        else:
            tot += np.log(abs(a) / abs(b_))**2
    return tot


def fit(par=None, targets=None, free=None, maxfev=2600, verbose=True, tag=''):
    """Joint Nelder Mead over the free parameters, searched in logs."""
    from scipy.optimize import minimize
    par = par or P()
    t = targets or TARGET
    fr = free or FREE
    names = [f[0] for f in fr]
    lo = np.array([np.log(f[1]) for f in fr])
    hi = np.array([np.log(f[2]) for f in fr])
    x0 = np.clip([np.log(getattr(par, n)) for n in names], lo + 1e-6, hi - 1e-6)
    n = {'k': 0}

    def f(x):
        x = np.clip(x, lo, hi)
        q = with_(par, **{k: float(np.exp(v)) for k, v in zip(names, x)})
        L = loss(q, t)
        n['k'] += 1
        if verbose and n['k'] % 150 == 0:
            print(f'    {tag}{n["k"]:5d} evals, loss {L:9.5f}')
        return L

    # two restarts: Nelder Mead collapses its simplex and a restart from the
    # incumbent is the cheapest way to let it re expand
    x = x0
    for _ in range(3):
        r = minimize(f, x, method='Nelder-Mead',
                     options=dict(maxfev=maxfev // 3, xatol=2e-4, fatol=1e-9))
        x = np.clip(r.x, lo, hi)
    return with_(par, **{k: float(np.exp(v)) for k, v in zip(names, x)})


def report(par):
    m = stats(par)
    print('\n' + '=' * 72)
    print('CALIBRATION OF THE STYLISED MODEL')
    print('=' * 72)
    print(f"{'moment':41s}{'target':>10s}{'model':>10s}{'gap':>10s}")
    for k in ['part', 'spend', 'elast_p', 'prog', 'r_sud', 'housing_share',
              'homeless', 'vsl']:
        print(f'{LABEL[k]:41s}{TARGET[k]:10.4f}{m[k]:10.4f}{m[k]-TARGET[k]:10.4f}')
    print('-' * 72)
    print(f"{'HELD OUT income of users / average':41s}{0.951:10.4f}"
          f"{m['r_use']:10.4f}{m['r_use']-0.951:10.4f}")
    print(f"{'HELD OUT share of homeless w/ disorder':41s}{0.217:10.4f}"
          f"{m['sud_of_homeless']:10.4f}{m['sud_of_homeless']-0.217:10.4f}")
    print('-' * 72)
    print('  ' + '   '.join(f'{n}={getattr(par,n):.4g}' for n, _, _ in FREE))
    return m


def jacobian(par, rel=0.08):
    """Elasticity of each moment to each parameter. R1's comment 2(f), on the
    small model where it fits on one screen."""
    names = [f[0] for f in FREE]
    moms = ['part', 'spend', 'elast_p', 'prog', 'r_sud', 'housing_share',
            'homeless', 'vsl', 'r_use', 'sud_of_homeless']
    base = stats(par)
    print('\n' + '=' * 86)
    print('IDENTIFICATION: elasticity of each moment to each parameter')
    print('=' * 86)
    print(f"{'':8s}" + ''.join(f'{m[:9]:>9s}' for m in moms))
    for n in names:
        v = getattr(par, n)
        hi = stats(with_(par, **{n: v * (1 + rel)}))
        lo = stats(with_(par, **{n: v * (1 - rel)}))
        row = ''.join(f'{(hi[m]-lo[m])/max(abs(base[m]),1e-12)/(2*rel):9.2f}'
                      for m in moms)
        print(f'{n:8s}' + row)


# ---------------------------------------------------------------------------
# the channel configurations, EACH recalibrated to the same two moments
# ---------------------------------------------------------------------------
# The comparison is only fair if every configuration matches the same facts. So
# in each one, b is refitted to the participation rate and the ACTIVE penalty is
# refitted to the price elasticity: the mortality penalty where there is one,
# the wage penalty where there is not. Then the income gradient is the only thing
# left free to differ, and it differs because of the mechanism rather than
# because one configuration was allowed a better fit.
CONFIGS = [
    ('both channels',  {},                                   ['b', 'th', 'kap']),
    ('mortality only', dict(xi=0.0, u1=P.u0, dis_hl=0.02),    ['b', 'th', 'kap']),
    ('resource only',  dict(kap=0.0, kapH=0.0),               ['b', 'th', 'xi']),
]


def fit_config(base, kw, free_names, maxfev=400):
    par = with_(base, **kw)
    fr = [f for f in FREE if f[0] in free_names]
    t = {'part': TARGET['part'], 'elast_p': TARGET['elast_p'],
         'spend': TARGET['spend']}
    return fit(par, targets=t, free=fr, maxfev=maxfev, verbose=False)


if __name__ == '__main__':
    import json, sys
    print('calibrating the benchmark')
    # start in the region the moments point to: a high taste with a high
    # subsistence gives few users who each spend a lot, which is what a 5 per
    # cent participation rate alongside 11 per cent spending requires
    par = fit(P())
    m = report(par)
    jacobian(par)
    out = {n: getattr(par, n) for n, _, _ in FREE}
    json.dump(out, open('calibrated.json', 'w'), indent=1)
    print('\nwrote calibrated.json')
