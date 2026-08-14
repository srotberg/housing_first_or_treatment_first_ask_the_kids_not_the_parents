"""
The stylised THREE period model behind section 3 of the paper.

WHY THREE AND NOT TWO

Two periods makes the disorder a one off cost: you acquire it, you pay once,
the model ends. The paper's mechanism is that the disorder is PERSISTENT and
its costs compound, and that is also what makes the value of life rise steeply
in permanent income. Three periods is the smallest environment with that
property: use at 1, the disorder lands at 2, and it persists into 3 unless the
household recovers.

It also makes SAVING do something. With two periods saving is a pure
consumption smoothing device. With three, the household saves in period 1 partly
to self insure against the income drop and the homelessness risk that the
disorder brings in period 2, and Referee 1's objection to the previous appendix
was precisely that it abstracted from dynamic savings decisions.

THE ENVIRONMENT

  period 1   income y. Choose non drug consumption, drug use v >= 0 and saving.
             Everyone starts clean. Flow utility  log c + th_i [log(b+v) - log b].
             Using raises the chance of the disorder:  pi_d(v) = 1 - exp(-lam v).

  period 2   disorder d in {0,1}. Income y(1 - xi d). Homeless with probability
             pH1 if d = 1 and pH0 if not, unless a voucher covers the household.
             Homelessness costs a utility flow and raises mortality. Choose
             saving. Recover from the disorder with probability rho.

  period 3   terminal. Consume everything, with the same homelessness risk.

TWO CHANNELS, AND THE PAIRS MATTER

The disorder hurts in two ways and each has a direct and an indirect arm:

    MORTALITY   kap   it kills you       kapH  and it makes you homeless,
                                               which also kills you
    RESOURCE    xi    it makes you poor   ellH  and homelessness costs a flow

Switching a channel off means switching BOTH members of its pair. Switching kap
alone leaves the homelessness mortality penalty running in a row that is
supposed to have no mortality channel at all.

THE VOUCHER, AND WHY IT PRODUCES BOTH OF THE PAPER'S FORCES

A voucher removes the risk of homelessness. Under Housing First it arrives
whatever d is; under Treatment First only if d = 0. That single difference is

  moral hazard     under HF, generosity lowers P(homeless | disorder), so
                   acquiring the disorder costs less and use RISES
  value of life    under TF, generosity raises the value of staying clean
                   without touching the disorder branch, so use FALLS

Neither exists if the voucher is a transfer rather than insurance against a bad
state. An earlier version made that mistake and found no moral hazard at all.

NOTE ON PREFERENCES. Drugs enter ADDITIVELY, log c + th [log(b+v) - log b],
rather than as a Cobb Douglas weight. Two reasons. It keeps periods 2 and 3
independent of the taste draw, so they are solved once per income level rather
than once per household. And it means taste dispersion shifts only the drug
term, so nothing about the consumption side varies with it.
"""

import os
import numpy as np

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'figures'))


class P:
    th    = 0.050     # mean taste for drugs
    b     = 0.013     # Stone Geary subsistence; th/b is the pull of the first unit
    p_v   = 1.0       # price of drugs, the numeraire
    beta  = 0.96
    R     = 1.03
    phi0  = 0.94      # per period survival, clean and housed
    kap   = 0.45      # MORTALITY channel, direct
    kapH  = 0.35      # MORTALITY channel, through homelessness
    xi    = 0.31      # RESOURCE channel, direct
    ellH  = 0.80      # RESOURCE channel, through homelessness
    lam   = 6.00      # addiction hazard per unit of use
    rho   = 0.15      # recovery probability between period 2 and 3
    aleph = 2.50      # flow value of being alive
    pH0   = 0.02      # P(homeless) without the disorder
    pH1   = 0.35      # P(homeless) with it, absent a voucher
    pV    = 0.27      # probability of receiving a voucher
    # DRUG SUPPLY. Quantity supplied is psi * p_v ** eps_s, and psi is
    # renormalised at the benchmark so that p_v = 1 there whatever eps_s is.
    # Referee 1's comment 1(c) and Referee 3's M2d both object that the price
    # cannot be both normalised and varied. Here the normalisation is explicit
    # and confined to the benchmark, and the price is free in every experiment.
    # eps_s = 2 is the baseline: Hansen, Miller and Weber (2017) imply about
    # 0.79 for licensed marijuana, cigarettes and gasoline sit nearer 3.6.
    eps_s = 2.0
    psi   = 1.0
    sig   = 0.55      # dispersion of log taste, income independent
    nq    = 25        # Gauss Hermite nodes
    na    = 90        # asset grid
    nv    = 200       # drug use grid


def clone(**kw):
    q = P()
    for k, v in kw.items():
        setattr(q, k, v)
    return q


def fields(par):
    return {k: getattr(par, k) for k in dir(par)
            if not k.startswith('_') and not callable(getattr(par, k))}


def with_(par, **kw):
    f = fields(par); f.update(kw)
    return clone(**f)


# ----------------------------------------------------------------------------
def _ph(par, d, policy):
    """P(homeless) in state d, after the voucher."""
    covered = (policy == 'HF') or (d == 0)
    base = par.pH1 if d == 1 else par.pH0
    return base * (1.0 - (par.pV if covered else 0.0))


def _surv(par, d, policy):
    """Expected survival out of a period in state d."""
    p = _ph(par, d, policy)
    phi = par.phi0 * (1.0 - par.kap * d)
    return (1.0 - p) * phi + p * phi * (1.0 - par.kapH)


def _flow(par, c, d, policy):
    """Flow utility in state d, expected over the homelessness draw."""
    return np.log(np.maximum(c, 1e-12)) + par.aleph \
        - par.ellH * _ph(par, d, policy)


def solve_late(par, y, policy):
    """
    Backward induction over periods 3 and 2. Independent of the taste draw, so
    this is solved once per income level. Returns V2 on the asset grid, by d.
    """
    amax = 1.4 * y
    ag = np.linspace(0.0, amax, par.na)

    # period 3: consume everything
    V3 = np.empty((par.na, 2))
    for d in (0, 1):
        V3[:, d] = _flow(par, par.R * ag + y * (1.0 - par.xi * d), d, policy)

    # period 2: choose next assets
    V2 = np.empty((par.na, 2))
    for d in (0, 1):
        cash = par.R * ag[:, None] + y * (1.0 - par.xi * d)
        c    = cash - ag[None, :]
        EV3  = (1.0 - par.rho) * V3[:, d] + par.rho * V3[:, 0] if d == 1 else V3[:, 0]
        val  = np.where(c > 1e-9,
                        _flow(par, c, d, policy)
                        + par.beta * _surv(par, d, policy) * EV3[None, :],
                        -np.inf)
        V2[:, d] = val.max(axis=1)
    return ag, V2


def solve_one(par, y, policy='HF'):
    """
    Period 1. Returns (participation probability, expected use per household).

    Drugs enter additively, so the value of any (v, saving) pair splits into a
    taste independent part and th_i times a known function of v. The maximisation
    over the taste draw is therefore a single vector operation rather than a
    resolve per household.
    """
    ag, V2 = solve_late(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.55 * y, par.nv - 1)))

    cash = y - par.p_v * vg[:, None]
    c    = cash - ag[None, :]
    pid  = (1.0 - np.exp(-par.lam * vg))[:, None]
    EV2  = (1.0 - pid) * V2[None, :, 0] + pid * V2[None, :, 1]
    val  = np.where(c > 1e-9,
                    np.log(np.maximum(c, 1e-12)) + par.aleph
                    + par.beta * par.phi0 * EV2,
                    -np.inf)
    base = val.max(axis=1)                      # best over saving, for each v
    G    = np.log(par.b + vg) - np.log(par.b)   # the drug term, per unit of taste

    x, qw = np.polynomial.hermite_e.hermegauss(par.nq)
    qw = qw / qw.sum()
    th = par.th * np.exp(par.sig * x - 0.5 * par.sig**2)

    tot = base[None, :] + th[:, None] * G[None, :]      # nq by nv
    k   = np.argmax(tot, axis=1)
    best = tot[np.arange(par.nq), k]
    v_no = base[0]                                       # v = 0 is the first node
    use  = best > v_no + 1e-12
    return float((qw * use).sum()), float((qw * use * vg[k]).sum())


def profile(par, ygrid, policy='HF'):
    out = [solve_one(par, y, policy) for y in ygrid]
    return np.array([o[0] for o in out]), np.array([o[1] for o in out])


def moments(par, ygrid, w, policy='HF'):
    """
    r_use  income of users relative to the average, period 1.
    r_sud  income of households with the disorder relative to the average,
           measured in period 2 AFTER the earnings penalty, which is what NSDUH
           sees. Measuring it on pre penalty income forces the two ratios to
           move together, which is exactly what the data say they do not do.
    """
    p_use, ev = profile(par, ygrid, policy)
    vbar = np.where(p_use > 1e-9, ev / np.maximum(p_use, 1e-9), 0.0)
    pid  = p_use * (1.0 - np.exp(-par.lam * vbar))
    w    = w / w.sum()

    r_use = (w * p_use * ygrid).sum() / max((w * p_use).sum(), 1e-12) \
          / (w * ygrid).sum()
    y2    = ygrid * (1.0 - par.xi)
    ybar2 = (w * (pid * y2 + (1.0 - pid) * ygrid)).sum()
    r_sud = (w * pid * y2).sum() / max((w * pid).sum(), 1e-12) / ybar2

    ly = np.log(ygrid); ly = ly - (w * ly).sum()
    el = float((w * ly * (p_use - (w * p_use).sum())).sum() / (w * ly * ly).sum()) \
        / max((w * p_use).sum(), 1e-12)

    return dict(part=float((w * p_use).sum()), sud=float((w * pid).sum()),
                r_use=float(r_use), r_sud=float(r_sud), elast=el,
                p_use=p_use, v=vbar, ev=ev, pid=pid)


# ----------------------------------------------------------------------------
# the drug market
# ----------------------------------------------------------------------------
def demand(par, ygrid, w, policy='HF'):
    """Aggregate drug quantity demanded at the current price."""
    p_use, ev = profile(par, ygrid, policy)
    return float((w / w.sum() * ev).sum())


def normalise_supply(par, ygrid, w, policy='HF'):
    """Set psi so the benchmark clears at p_v = 1, whatever eps_s is."""
    q = with_(par, p_v=1.0)
    return demand(q, ygrid, w, policy)


def clear_price(par, ygrid, w, policy='HF', lo=0.2, hi=5.0, iters=26):
    """
    Find p_v with supply = demand. Supply slopes up and demand slopes down, so
    excess demand is decreasing in the price and a bisection is safe.
    """
    for _ in range(iters):
        p = np.sqrt(lo * hi)
        exc = demand(with_(par, p_v=p), ygrid, w, policy) - par.psi * p**par.eps_s
        if exc > 0.0:
            lo = p
        else:
            hi = p
    return float(np.sqrt(lo * hi))


def price_elasticity(par, ygrid, w, policy='HF', step=0.05):
    """
    d log(participation) / d log(p_v), holding supply fixed. This is the object
    the empirical literature estimates from tax and enforcement variation, so it
    is a DEMAND elasticity and needs no market clearing: the price is moved
    exogenously and the participation response is read off.
    """
    lo = moments(with_(par, p_v=1.0 - step), ygrid, w, policy)['part']
    hi = moments(with_(par, p_v=1.0 + step), ygrid, w, policy)['part']
    if lo <= 0.0 or hi <= 0.0:
        return 0.0
    return float((np.log(hi) - np.log(lo)) / (np.log(1.0 + step) - np.log(1.0 - step)))


def aggregates(par, ygrid, w, policy='HF'):
    """Everything the calibration targets, in one pass."""
    m = moments(par, ygrid, w, policy)
    ww = w / w.sum()
    ph0, ph1 = _ph(par, 0, policy), _ph(par, 1, policy)
    hl = (ww * ((1.0 - m['pid']) * ph0 + m['pid'] * ph1)).sum()
    hl_sud = (ww * m['pid'] * ph1).sum()
    m['homeless'] = float(hl)
    m['sud_of_homeless'] = float(hl_sud / max(hl, 1e-12))

    # value of a statistical life at mean income, in units of mean income.
    # With log utility the marginal rate of substitution between consumption
    # and survival is the continuation value times consumption.
    k = int(np.argmin(np.abs(ygrid - 1.0)))
    ag, V2 = solve_late(par, ygrid[k], policy)
    m['vsl'] = float(par.beta * par.phi0 * V2[0, 0] * ygrid[k])
    return m
