"""
Does the model need three periods, or will two do?

THE QUESTION

Period 3 exists so that the disorder, realised at the start of period 2, has a
future to destroy: survival from 2 to 3 is phi(d) = phi0(1 - kap*d), and that is
the mortality channel. Delete period 3 and mortality has nothing to act on.

So a two period model cannot simply drop the last period. It has to move the
timing: the disorder is realised at the END of period 1, survival from 1 to 2
depends on it, and period 2 is terminal.

    period 1  employed, clean, income y. Choose consumption, housing, drug use
              v >= 0 and saving. The disorder arrives with probability
              pi(v) = 1 - exp(-lam v), and survival into period 2 is phi(d).

    period 2  terminal. The disorder is known. Unemployed with probability u_d,
              income support, voucher, housing choice, consume everything.

WHAT IS LOST

Recovery. rho needs at least two post disorder periods to mean anything, and
with a terminal period 2 there is nowhere for it to act. The ablation already
said rho does not move either result, and it was retained only so that the name
"Treatment First" had content: a household could get clean and become eligible
again. In two periods that story is gone, though the policy contrast itself is
untouched, since it is still exactly whether the voucher is withdrawn at d = 1.

WHAT IS KEPT

Everything the two results rest on: the drug decision, the use dependent
addiction hazard, mortality, unemployment, the three point housing grid,
homelessness, income support, saving, the means test, and both policies.

Run:  python3 two_period.py
"""

import numpy as np
from stylized import P, with_, _options


def _states2(par, d, policy, y):
    """(probability, income, tenant's rent multiplier) in the terminal period."""
    pu = par.u1 if d == 1 else par.u0
    covered = (policy == 'HF') or (d == 0)
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):
        inc = y if e == 0 else par.repl * min(y, par.ycap)
        pv = par.pV if (covered and inc <= par.yV) else 0.0
        for rmul, prb in ((par.kappa_r, pv), (1.0, 1.0 - pv)):
            if pe * prb > 1e-14:
                out.append((pe * prb, inc, rmul))
    return out


def solve_last(par, y, policy):
    """The terminal period. Returns assets grid, W2 by disorder, street share."""
    ag = np.linspace(0.0, 1.6 * y, par.na)
    W2 = np.zeros((par.na, 2)); H2 = np.zeros((par.na, 2))
    for d in (0, 1):
        for p, inc, rmul in _states2(par, d, policy, y):
            cash = par.R * ag + inc
            best = np.full(par.na, -np.inf); onst = np.zeros(par.na)
            for h, rent, street in _options(par, rmul):
                c = cash - rent
                v = np.where(c > 1e-9, np.log(np.maximum(c, 1e-12))
                             + par.gam * np.log(h) + par.aleph, -np.inf)
                onst = np.where(v > best, street, onst)
                best = np.maximum(best, v)
            W2[:, d] += p * best
            H2[:, d] += p * onst
    return ag, W2, H2


def use_choice2(par, y, policy=None):
    """(gain from using, best v, assets if using, assets if not)."""
    policy = policy or par.policy
    ag, W2, _ = solve_last(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * y, par.nv - 1)))
    cash = (y - par.p_v * vg[:, None]) - ag[None, :]
    pid = (1.0 - np.exp(-par.lam * vg))[:, None]
    # MORTALITY NOW SITS BETWEEN PERIOD 1 AND PERIOD 2, and it depends on the
    # disorder, so acquiring it costs the household twice: a lower chance of
    # reaching period 2 at all, and a worse period 2 if it gets there.
    s0 = par.phi0
    s1 = par.phi0 * (1.0 - par.kap)
    EW = (1.0 - pid) * s0 * W2[None, :, 0] + pid * s1 * W2[None, :, 1]
    val = np.full(cash.shape, -np.inf)
    for h, rent, _ in _options(par, 1.0):
        c = cash - rent
        val = np.maximum(val, np.where(
            c > 1e-9,
            np.log(np.maximum(c, 1e-12)) + par.gam * np.log(h)
            + par.aleph + par.beta * EW, -np.inf))
    base = val.max(axis=1)
    a_by_v = ag[np.argmax(val, axis=1)]
    tot = base + par.th * (np.log(par.b + vg) - np.log(par.b))
    k = int(np.argmax(tot[1:])) + 1
    return float(tot[k] - tot[0]), float(vg[k]), float(a_by_v[k]), float(a_by_v[0])


def threshold2(par, ygrid, policy=None):
    policy = policy or par.policy
    n = len(ygrid)
    g = np.empty(n); vv = np.empty(n); au = np.empty(n); an = np.empty(n)
    for i, y in enumerate(ygrid):
        g[i], vv[i], au[i], an[i] = use_choice2(par, y, policy)
    frac = (g > 0.0).astype(float)
    for i in range(n - 1):
        if (g[i] > 0.0) != (g[i + 1] > 0.0):
            lo, hi, sgn = ygrid[i], ygrid[i + 1], g[i] > 0.0
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                if (use_choice2(par, mid, policy)[0] > 0.0) == sgn:
                    lo = mid
                else:
                    hi = mid
            w = (0.5 * (lo + hi) - ygrid[i]) / (ygrid[i + 1] - ygrid[i])
            frac[i], frac[i + 1] = (w, 0.0) if g[i] > 0.0 else (0.0, 1.0 - w)
    return np.clip(frac, 0.0, 1.0), vv, au, an


def aggregates2(par, ygrid, w, policy=None):
    policy = policy or par.policy
    use, vv, au, an = threshold2(par, ygrid, policy)
    pid = use * (1.0 - np.exp(-par.lam * vv))
    ww = w / w.sum(); ybar = (ww * ygrid).sum()

    hl = hl_sud = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2 = solve_last(par, y, policy)
        for m, a, d in ((ww[i] * (1.0 - use[i]), an[i], 0),
                        (ww[i] * (use[i] - pid[i]), au[i], 0),
                        (ww[i] * pid[i], au[i], 1)):
            if m <= 0.0:
                continue
            street = float(np.interp(a, ag, H2[:, d]))
            hl += m * street
            if d == 1:
                hl_sud += m * street

    part = float((ww * use).sum())
    return dict(part=part, sud=float((ww * pid).sum()),
                prog=float((ww * pid).sum() / max(part, 1e-12)),
                r_use=float((ww * use * ygrid).sum() / max(part, 1e-12) / ybar),
                homeless=float(hl),
                sud_of_homeless=float(hl_sud / max(hl, 1e-12)),
                use=use, v=vv)


# ---------------------------------------------------------------------------
from calibrate import YG, W, TARGET, PAIRS


def stats2(par):
    return aggregates2(par, YG, W)


def bracket2(par, name, mom, lo, hi, iters=32):
    tgt = TARGET[mom]
    rising = stats2(with_(par, **{name: hi}))[mom] > stats2(with_(par, **{name: lo}))[mom]
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        if (stats2(with_(par, **{name: mid}))[mom] > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def calibrate2(par=None, sweeps=6, verbose=True):
    par = par or P()
    for s in range(sweeps):
        for name, mom, lo, hi in PAIRS:
            par = with_(par, **{name: bracket2(par, name, mom, lo, hi)})
        if verbose:
            m = stats2(par)
            worst = max(abs(m[k] / TARGET[k] - 1.0) for k in TARGET)
            print(f'  sweep {s+1}  worst gap {worst:7.3f}   '
                  + '  '.join(f'{n}={getattr(par, n):.4g}' for n, _, _, _ in PAIRS))
    return par


def channel_scan(par):
    """Result 1: does mortality still reverse the gradient and unemployment not?"""
    OFF = dict(kap=0.0, u1=P.u0, h_hl=P.h_sm)
    out = {}
    for which in ('mortality', 'unemployment'):
        row = []
        for s in (0.0, 0.5, 1.0):
            kw = dict(OFF)
            if which == 'mortality':
                kw.update(kap=s * par.kap)
            else:
                kw.update(u1=P.u0 + s * (par.u1 - P.u0),
                          h_hl=P.h_sm * (par.h_hl / P.h_sm) ** s)
            q = with_(par, **kw)
            q = with_(q, b=bracket2(q, 'b', 'part', 1e-5, 0.60, iters=20))
            row.append((s, q.b, stats2(q)['r_use']))
        out[which] = row
    return out


if __name__ == '__main__':
    print('=' * 70)
    print('TWO PERIOD MODEL')
    print('=' * 70)
    par = calibrate2(P(), sweeps=6)
    m = stats2(par)
    print(f"\n  participation {m['part']:.4f}  (target 0.0513)")
    print(f"  homelessness  {m['homeless']:.5f}  (target 0.00399)")
    print(f"  prog          {m['prog']:.4f}  (target 0.332)")
    print(f"  income of users / average : {m['r_use']:.3f}")
    print(f"  b={par.b:.5g}  h_hl={par.h_hl:.5g}  lam={par.lam:.5g}")

    print('\n  RESULT 1, does mortality still reverse the gradient?')
    for which, row in channel_scan(par).items():
        cells = '   '.join(f's={s:.1f}: r={r:.3f}' for s, _, r in row)
        print(f'    {which:14s} {cells}')

    print('\n  RESULT 2, the two policy forces')
    p0 = stats2(with_(par, pV=0.0, policy='HF'))['part']
    ph = stats2(with_(par, pV=1.0, policy='HF'))['part']
    pt = stats2(with_(par, pV=1.0, policy='TF'))['part']
    print(f'    no voucher {100*p0:6.2f}   universal TF {100*pt:6.2f}'
          f'   universal HF {100*ph:6.2f}')
    print(f'    value of life {100*(pt-p0):+6.2f}   moral hazard {100*(ph-pt):+6.2f}')

    print('\n  THE CONTINUATION VALUE AT THE BOTTOM')
    for y in (0.12, 0.18, 0.30, 1.00):
        ag, W2, H2 = solve_last(par, y, 'HF')
        print(f'    y {y:.2f}   W2(0,d=0) {W2[0,0]:7.3f}   W2(0,d=1) {W2[0,1]:7.3f}'
              f'   d=1 worse? {W2[0,1] < W2[0,0]}')
