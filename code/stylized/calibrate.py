"""
Calibrating the stylised model, and checking that it is identified.

The point of calibrating a stylised model is not to claim it fits the data. It
is so that the comparative statics in run.py are read off a point that is in the
right region of the parameter space, and so that the one moment the model is NOT
fitted to becomes a genuine out of sample check.

SEVEN PARAMETERS, SEVEN TARGETS

    b        drug participation                          5.13 %
    lam      P(disorder | used)                          71.7 %
    kap      price elasticity of participation           -0.45
    xi       income with the disorder / average          0.687
    pH1      share of the homeless with the disorder     21.7 %
    pH0      homelessness rate                           0.399 %
    aleph    value of a statistical life, in mean incomes  107

HELD OUT, AND THIS IS THE POINT

    r_use    income of USERS / average                   0.951 in the data

The income gradient of USE is never targeted. It is what the paper's mechanism
is supposed to explain, so fitting it would make the exercise circular. Everything
that identifies the mortality channel comes from the price elasticity instead,
exactly as in the full model.

The targets are the same objects, from the same sources, as the full model's:
NSDUH 2024 ages 26 and above for the drug moments, HUD point in time converted
to households for the homelessness rate, Gutwinski et al. for the composition of
the homeless population, and the standard 7.5 million dollar value of a
statistical life against mean household income near 70,000.
"""

import numpy as np
from stylized import P, with_, fields, aggregates, price_elasticity, moments

YG = np.exp(np.linspace(np.log(0.15), np.log(5.0), 40))
W  = np.exp(-0.5 * ((np.log(YG) + 0.5 * 0.75**2) / 0.75)**2)

TARGET = dict(part=0.0513, prog=0.717, elast_p=-0.45, r_sud=0.687,
              sud_of_homeless=0.217, homeless=0.00399, vsl=107.0)

# parameter, moment, bracket, and the sign of d(moment)/d(parameter)
BLOCKS = [
    ('b',     'part',            1e-5, 3.0,  -1),
    ('lam',   'prog',            0.05, 200.0, +1),
    ('kap',   'elast_p',         0.02, 0.95, +1),   # bigger kap, LESS elastic
    ('xi',    'r_sud',           0.01, 0.90, -1),
    ('pH1',   'sud_of_homeless', 1e-4, 0.95, +1),
    ('pH0',   'homeless',        1e-6, 0.30, +1),
    ('aleph', 'vsl',             0.10, 400.0, +1),
]


def stats(par):
    m = aggregates(par, YG, W)
    m['prog'] = m['sud'] / max(m['part'], 1e-12)
    m['elast_p'] = price_elasticity(par, YG, W)
    return m


def bisect(par, name, mom, lo, hi, sign, iters=13):
    tgt = TARGET[mom]
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        val = stats(with_(par, **{name: mid}))[mom]
        # sign = +1 means the moment RISES in the parameter
        if (val > tgt) == (sign > 0):
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def loss(par):
    """Sum of squared relative gaps. The price elasticity is a level rather than
    a ratio, so it is scaled by its own target's magnitude like the rest."""
    m = stats(par)
    return sum((m[k] / TARGET[k] - 1.0)**2 for k in TARGET)


def calibrate(par=None, verbose=True, maxiter=900):
    """
    Joint minimisation rather than one bisection per parameter.

    Coordinate bisection assumes each parameter dominates one moment. The
    Jacobian below says that is FALSE here, and in an instructive way. Raising
    the addiction hazard lam RAISES the disorder rate mechanically but LOWERS it
    in equilibrium, because households respond by using less: the partial and
    the total derivative have opposite signs. A bisection that assumes the
    partial sign walks the parameter to its bound, which is what happened, and
    from there the price elasticity collapses to zero and every other bracket
    loses its signal too.

    So the calibration is a joint fit. Parameters are searched in logs, which
    keeps them positive and makes the step sizes scale free.
    """
    from scipy.optimize import minimize
    par = par or P()
    names = [b[0] for b in BLOCKS]
    lo = np.array([np.log(b[2]) for b in BLOCKS])
    hi = np.array([np.log(b[3]) for b in BLOCKS])
    x0 = np.clip(np.array([np.log(getattr(par, n)) for n in names]),
                 lo + 1e-6, hi - 1e-6)

    hist = {'n': 0}

    def f(x):
        x = np.clip(x, lo, hi)
        q = with_(par, **{n: float(np.exp(v)) for n, v in zip(names, x)})
        L = loss(q)
        hist['n'] += 1
        if verbose and hist['n'] % 60 == 0:
            print(f'    {hist["n"]:5d} evaluations, loss {L:10.5f}')
        return L

    res = minimize(f, x0, method='Nelder-Mead',
                   options=dict(maxfev=maxiter, xatol=1e-4, fatol=1e-7))
    x = np.clip(res.x, lo, hi)
    return with_(par, **{n: float(np.exp(v)) for n, v in zip(names, x)})


def report(par):
    m = stats(par)
    print('\n' + '=' * 74)
    print('CALIBRATION OF THE STYLISED MODEL')
    print('=' * 74)
    print(f"{'moment':38s}{'target':>11s}{'model':>11s}{'gap':>11s}")
    order = ['part', 'prog', 'elast_p', 'r_sud', 'sud_of_homeless',
             'homeless', 'vsl']
    label = {'part': 'drug participation', 'prog': 'P(disorder | used)',
             'elast_p': 'price elasticity of participation',
             'r_sud': 'income with disorder / average',
             'sud_of_homeless': 'share of homeless with disorder',
             'homeless': 'homelessness rate',
             'vsl': 'value of a statistical life / income'}
    for k in order:
        print(f'{label[k]:38s}{TARGET[k]:11.4f}{m[k]:11.4f}'
              f'{m[k]-TARGET[k]:11.4f}')
    print('-' * 74)
    print(f"{'HELD OUT: income of users / average':38s}{0.951:11.4f}"
          f"{m['r_use']:11.4f}{m['r_use']-0.951:11.4f}")
    print('-' * 74)
    print('parameters')
    for name, _, _, _, _ in BLOCKS:
        print(f'   {name:8s}{getattr(par, name):12.5f}')
    return m


def jacobian(par, rel=0.10):
    """
    Sensitivity of every moment to every parameter, in elasticities. This is the
    numerical identification evidence Referee 1 asks for in his comment 2(f),
    done here on the small model where it can be read at a glance.
    """
    names = [b[0] for b in BLOCKS]
    moms = ['part', 'prog', 'elast_p', 'r_sud', 'sud_of_homeless',
            'homeless', 'vsl', 'r_use']
    base = stats(par)
    print('\n' + '=' * 92)
    print('IDENTIFICATION: elasticity of each moment to each parameter')
    print('   a near diagonal matrix is what a triangular calibration needs')
    print('=' * 92)
    print(f"{'':9s}" + ''.join(f'{m[:15]:>10s}' for m in moms))
    J = np.zeros((len(names), len(moms)))
    for i, n in enumerate(names):
        v = getattr(par, n)
        hi = stats(with_(par, **{n: v * (1 + rel)}))
        lo = stats(with_(par, **{n: v * (1 - rel)}))
        row = ''
        for j, mm in enumerate(moms):
            d = (hi[mm] - lo[mm]) / max(abs(base[mm]), 1e-12) / (2 * rel)
            J[i, j] = d
            row += f'{d:10.2f}'
        print(f'{n:9s}' + row)
    return J


if __name__ == '__main__':
    print('calibrating')
    par = calibrate()
    m = report(par)
    jacobian(par)
    print('\nparameter block for stylized.py:')
    for n, _, _, _, _ in BLOCKS:
        print(f'    {n:6s}= {getattr(par, n):.6f}')
