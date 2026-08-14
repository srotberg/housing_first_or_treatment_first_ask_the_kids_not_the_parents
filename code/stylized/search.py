"""
Find where in parameter space the stylised model reproduces the two income
ratios the full model targets, and check the analytics while doing it.

THE CONDITION BEING CHECKED

At v -> 0 the household uses if and only if, in CONSUMPTION units,

    (th/b) * c/(1-th)     >     p_v  +  beta * lam * VSL(y)
    -----------------           ------------------------------
    marginal willingness        price plus the mortality cost
    to pay, RISES like y        of the marginal unit

with  VSL(y) = phi0 kap c [ log W + aleph/(1-th) ].

VSL/y therefore rises in y through the log term, so the right side grows
SUPERLINEARLY while the left grows linearly. That is the whole mechanism, and it
says the sign flip is a race the mortality channel wins only if lam is large
enough and aleph is not so large that it swamps the log term.

Both of those are checkable, and this searches for them.
"""

import numpy as np
from stylized import P, clone, solve_one, V2


def moments(par, ygrid, w=None):
    """Participation, the two income ratios, and the intensity gradient."""
    if w is None:
        w = np.ones_like(ygrid)
    w = w / w.sum()
    v = np.array([solve_one(par, y)[0] for y in ygrid])
    use = v > 1e-3
    pid = 1.0 - np.exp(-par.lam * v)

    ybar = (w * ygrid).sum()
    mu = w * use
    ms = w * pid
    r_use = (mu * ygrid).sum() / max(mu.sum(), 1e-12) / ybar
    r_sud = (ms * ygrid).sum() / max(ms.sum(), 1e-12) / ybar

    x = np.log(ygrid); x = x - x.mean()
    slope = float((x * (v - v.mean())).sum() / (x * x).sum())
    return dict(part=float(mu.sum()), r_use=float(r_use), r_sud=float(r_sud),
                slope=slope, v=v, pid=pid, use=use)


def vsl(par, ygrid):
    """VSL in consumption units at zero saving, and its elasticity in y."""
    out = []
    for y in ygrid:
        d0 = V2(par, y, 0.0, 0, 'HF')
        d1 = V2(par, y, 0.0, 1, 'HF')
        c = y
        out.append((d0 - d1) * c / (1.0 - par.th))
    out = np.array(out)
    x = np.log(ygrid); yv = np.log(np.maximum(out, 1e-12))
    e = np.polyfit(x, yv, 1)[0]
    return out, float(e)


if __name__ == '__main__':
    # a lognormal income grid, so the ratios mean what they mean in the data
    ygrid = np.exp(np.linspace(np.log(0.18), np.log(4.0), 40))
    w = np.exp(-0.5 * ((np.log(ygrid) + 0.5 * 0.7**2) / 0.7)**2)

    print('=' * 78)
    print('IS THE VALUE OF LIFE SUPERLINEAR IN INCOME? (elasticity > 1 is needed)')
    print('=' * 78)
    print(f"{'aleph':>8s}{'VSL elasticity in y':>24s}{'min V2 (clean)':>18s}")
    for al in [0.0, 1.0, 2.0, 3.0, 5.0, 8.0]:
        par = clone(aleph=al)
        _, e = vsl(par, ygrid)
        mn = min(V2(par, y, 0.0, 0, 'HF') for y in ygrid)
        print(f'{al:8.1f}{e:24.3f}{mn:18.3f}')
    print('\n  aleph enters the bracket as a constant, so a LARGER aleph makes the')
    print('  log term a smaller share of it and pushes the elasticity toward 1.')
    print('  A SMALLER aleph steepens the mechanism but drives the continuation')
    print('  value negative at low income, where the mortality penalty then')
    print('  becomes a mortality benefit. The calibration is squeezed from both')
    print('  sides, and that is a real result rather than a nuisance.')

    print('\n' + '=' * 78)
    print('SEARCH: where does the model deliver use near income neutral and')
    print('        disorder concentrated at the bottom? (data: 0.95 and 0.69)')
    print('=' * 78)
    print(f"{'lam':>6s}{'b':>8s}{'aleph':>7s}{'part':>8s}"
          f"{'r_use':>8s}{'r_sud':>8s}{'slope':>9s}")
    best, bestloss = None, np.inf
    for lam in [1.0, 2.0, 4.0, 6.0, 9.0]:
        for b in [0.004, 0.008, 0.015, 0.030]:
            for al in [2.0, 3.0, 5.0]:
                par = clone(lam=lam, b=b, aleph=al)
                m = moments(par, ygrid, w)
                if m['part'] < 0.005:
                    continue
                loss = (m['r_use'] - 0.951)**2 + (m['r_sud'] - 0.687)**2
                print(f'{lam:6.1f}{b:8.3f}{al:7.1f}{m["part"]:8.3f}'
                      f'{m["r_use"]:8.3f}{m["r_sud"]:8.3f}{m["slope"]:9.4f}')
                if loss < bestloss:
                    bestloss, best = loss, (lam, b, al, m)
    if best:
        lam, b, al, m = best
        print(f'\n  closest: lam={lam}, b={b}, aleph={al}  ->  '
              f'r_use={m["r_use"]:.3f}, r_sud={m["r_sud"]:.3f}, '
              f'participation={m["part"]:.3f}')
