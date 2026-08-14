"""
The stylised three period model behind the note.

WHAT IT HAS TO CONTAIN

The small model earns its place only if it carries the full model's mechanism.
That means four links, and it has all four:

    homelessness raises mortality                   kapH
    homelessness makes it harder to get clean       rho_mult_hl < 1
    the disorder raises mortality                   kap
    the disorder raises unemployment                u1 > u0

and one policy: a voucher that removes the risk of homelessness, given
unconditionally under Housing First and only to the clean under Treatment First.

WHY THREE PERIODS

Two periods make the disorder a one off cost: acquire it, pay once, the model
ends. The paper's mechanism is that it PERSISTS and its costs compound, which is
also what makes the value of life rise steeply in permanent income. Three is the
smallest number with that property, and it makes saving do something beyond
smoothing: the household saves in period 1 partly to self insure against the
unemployment and homelessness risk the disorder brings in period 2.

THE ENVIRONMENT

  period 1   income y, employed and housed. Choose consumption, drug use v and
             saving. Flow utility  log c + th_i [log(b+v) - log b].
             Using gives the disorder next period with probability
             pi_d(v) = 1 - exp(-lam v).

  period 2   the disorder d is realised. Unemployed with probability u0, or u1
             if d = 1, and unemployment pays a replacement rate omega. Earnings
             carry a further penalty xi if d = 1. Homeless with a probability
             that rises with the disorder and with unemployment, unless a
             voucher covers the household; homelessness costs a utility flow
             ellH and raises mortality by kapH. Choose saving. Recovery is rho
             if housed and rho * rho_mult_hl if homeless.

  period 3   terminal, with the same employment and homelessness risks.

THE TWO CHANNELS, AND WHY THEY MOVE IN GROUPS

The disorder hurts in two ways and each has a direct and an indirect arm:

    MORTALITY   kap   it kills you        kapH  it makes you homeless,
                                                which also kills you
    RESOURCE    u1    it costs you a job  ellH  homelessness costs a flow
                xi    and a wage

Switching a channel off means switching every member of its group. Switching kap
alone leaves the homelessness mortality penalty running in a row that is supposed
to have no mortality channel at all.

THE PRICE OF DRUGS IS AN EQUILIBRIUM OBJECT

Quantity supplied is psi * p_v ** eps_s and psi is renormalised so the benchmark
clears at p_v = 1 whatever eps_s is. R1's comment 1(c) and R3's M2d both object
that a price cannot be normalised and varied at the same time; here the
normalisation is explicit, confined to the benchmark, and the price is free in
every experiment.
"""

import os
import numpy as np

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'writing', 'figures'))


class P:
    # preferences and technology
    th    = 0.050     # mean taste for drugs
    sig   = 0.55      # dispersion of log taste, INDEPENDENT of income
    b     = 0.010     # Stone Geary subsistence; th/b is the pull of the first unit
    beta  = 0.96
    R     = 1.03
    phi0  = 0.94      # per period survival, clean, employed, housed
    aleph = 2.50      # flow value of being alive

    # the disorder
    lam   = 6.00      # addiction hazard per unit of use
    rho   = 0.25      # recovery probability when HOUSED
    rho_mult_hl = 0.40   # recovery multiplier when homeless: harder to get clean
    kap   = 0.45      # MORTALITY, direct
    xi    = 0.20      # RESOURCE, direct wage penalty
    u1    = 0.16      # RESOURCE, unemployment probability with the disorder

    # employment
    u0    = 0.049     # unemployment probability without the disorder
    omega = 0.40      # replacement rate when unemployed

    # HOUSING. One rental unit at price pr, or the street.
    #
    # Homelessness is a CHOICE, not a hazard. A household compares living in the
    # unit, which costs pr, against the street, which is free but costs dis_hl in
    # flow utility, raises mortality by kapH, and lowers the recovery
    # probability. Households with low cash choose the street. This is the
    # trade off the whole literature is built on, and modelling it as an
    # exogenous probability, as an earlier version of this file did, hides it:
    # the voucher then works by shrinking a lottery rather than by relaxing a
    # budget constraint, which is not how the policy operates.
    pr    = 0.21      # rent, as a share of mean income
    dis_hl = 0.80     # RESOURCE, flow utility cost of the street
    kapH  = 0.35      # MORTALITY, extra death risk on the street

    # policy: a voucher cuts the tenant's rent to kappa_r * pr
    pV    = 0.27      # probability a voucher arrives
    kappa_r = 0.30    # tenant contribution rate
    policy = 'HF'

    # the drug market
    p_v   = 1.0
    eps_s = 2.0       # supply elasticity; 0.79 licensed marijuana, 3.6 cigarettes
    psi   = 1.0

    # numerics
    nq    = 21        # taste nodes
    na    = 70        # asset grid
    nv    = 160       # drug use grid


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
def _states(par, d, policy):
    """
    (probability, income multiplier, rent actually payable) for disorder status
    d. Housing is no longer here: it is chosen inside the value function.

    A voucher cuts the tenant's rent to kappa_r * pr. Under Housing First it
    arrives whatever d is; under Treatment First only if the household is clean.
    """
    pu = par.u1 if d == 1 else par.u0
    covered = (policy == 'HF') or (d == 0)
    pv = par.pV if covered else 0.0
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):                  # e = 1 unemployed
        inc = (par.omega if e else 1.0) * (1.0 - par.xi * d)
        for rent, prb in ((par.kappa_r * par.pr, pv), (par.pr, 1.0 - pv)):
            if pe * prb > 1e-14:
                out.append((pe * prb, inc, rent))
    return out


def _surv(par, d, h):
    """h = 1 on the street."""
    return par.phi0 * (1.0 - par.kap * d) * (1.0 - par.kapH * h)


def solve_late(par, y, policy):
    """Backward induction over periods 3 and 2. Independent of the taste draw."""
    ag = np.linspace(0.0, 1.4 * y, par.na)

    V3 = np.zeros((par.na, 2))
    H3 = np.zeros((par.na, 2))          # share choosing the street, for reporting
    for d in (0, 1):
        for p, inc, rent in _states(par, d, policy):
            cash = par.R * ag + inc * y
            v_ho = np.where(cash - rent > 1e-9,
                            np.log(np.maximum(cash - rent, 1e-12)) + par.aleph,
                            -np.inf)
            v_hl = np.log(np.maximum(cash, 1e-12)) - par.dis_hl + par.aleph
            street = v_hl > v_ho
            V3[:, d] += p * np.where(street, v_hl, v_ho)
            H3[:, d] += p * street

    V2 = np.zeros((par.na, 2))
    H2 = np.zeros((par.na, 2))
    for d in (0, 1):
        for p, inc, rent in _states(par, d, policy):
            cash = par.R * ag[:, None] + inc * y
            best = None
            for h in (0, 1):                       # h = 1 is the street
                c = cash - (rent if h == 0 else 0.0) - ag[None, :]
                r = par.rho * (par.rho_mult_hl if h else 1.0) if d == 1 else 0.0
                EV3 = (1.0 - r) * V3[:, d] + r * V3[:, 0]
                val = np.where(c > 1e-9,
                               np.log(np.maximum(c, 1e-12))
                               - (par.dis_hl if h else 0.0) + par.aleph
                               + par.beta * _surv(par, d, h) * EV3[None, :],
                               -np.inf).max(axis=1)
                best = val if best is None else np.maximum(best, val)
                if h == 0:
                    v_ho = val
            V2[:, d] += p * best
            H2[:, d] += p * (best > v_ho + 1e-12)
    return ag, V2, H2


def solve_one(par, y, policy=None):
    """
    Period 1. Returns (participation, expected use, assets carried into period 2
    by users, assets carried by abstainers).

    The period 2 assets are needed because homelessness is now a CHOICE made at
    a given cash position, so the homelessness rate cannot be read off a
    parameter: it has to be evaluated at the asset the household actually saved.
    """
    policy = policy or par.policy
    ag, V2, _ = solve_late(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.55 * y, par.nv - 1)))

    c = (y - par.p_v * vg[:, None]) - ag[None, :]
    pid = (1.0 - np.exp(-par.lam * vg))[:, None]
    EV2 = (1.0 - pid) * V2[None, :, 0] + pid * V2[None, :, 1]
    val = np.where(c > 1e-9,
                   np.log(np.maximum(c, 1e-12)) + par.aleph
                   + par.beta * par.phi0 * EV2, -np.inf)
    base = val.max(axis=1)
    G = np.log(par.b + vg) - np.log(par.b)

    x, qw = np.polynomial.hermite_e.hermegauss(par.nq)
    qw = qw / qw.sum()
    th = par.th * np.exp(par.sig * x - 0.5 * par.sig**2)
    tot = base[None, :] + th[:, None] * G[None, :]
    k = np.argmax(tot, axis=1)
    use = tot[np.arange(par.nq), k] > base[0] + 1e-12
    a_by_v = ag[np.argmax(np.where(c > 1e-9, val, -np.inf), axis=1)]
    pu = float((qw * use).sum())
    a_use = float((qw * use * a_by_v[k]).sum() / max(pu, 1e-12))
    return pu, float((qw * use * vg[k]).sum()), a_use, float(a_by_v[0])


def profile(par, ygrid, policy=None):
    out = [solve_one(par, y, policy) for y in ygrid]
    return tuple(np.array([o[i] for o in out]) for i in range(4))


# ----------------------------------------------------------------------------
def aggregates(par, ygrid, w, policy=None):
    policy = policy or par.policy
    p_use, ev, a_use, a_no = profile(par, ygrid, policy)
    vbar = np.where(p_use > 1e-9, ev / np.maximum(p_use, 1e-9), 0.0)
    pid = p_use * (1.0 - np.exp(-par.lam * vbar))
    ww = w / w.sum()
    ybar = (ww * ygrid).sum()

    hl = hl_sud = inc_sud = m_sud = inc_all = hcost = hinc = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2 = solve_late(par, y, policy)
        # three groups arrive in period 2: abstainers, users who stayed clean,
        # and users who acquired the disorder, each at their own asset position
        groups = ((ww[i] * (1.0 - p_use[i]),        a_no[i],  0),
                  (ww[i] * (p_use[i] - pid[i]),     a_use[i], 0),
                  (ww[i] * pid[i],                  a_use[i], 1))
        for m, a, d in groups:
            if m <= 0.0:
                continue
            street = float(np.interp(a, ag, H2[:, d]))
            hl += m * street
            if d == 1:
                hl_sud += m * street
                m_sud += m
            for p, inc, rent in _states(par, d, policy):
                inc_all += m * p * inc * y
                if d == 1:
                    inc_sud += m * p * inc * y
                hcost += m * p * (1.0 - street) * rent
                hinc  += m * p * inc * y

    spend = float((ww * p_use * par.p_v * vbar).sum()
                  / max((ww * p_use * ygrid).sum(), 1e-12))
    return dict(
        spend=spend,
        part=float((ww * p_use).sum()), sud=float((ww * pid).sum()),
        r_use=float((ww * p_use * ygrid).sum()
                    / max((ww * p_use).sum(), 1e-12) / ybar),
        homeless=float(hl),
        sud_of_homeless=float(hl_sud / max(hl, 1e-12)),
        unemp_sud=float(par.u1),
        housing_share=float(hcost / max(hinc, 1e-12)),
        r_sud=float(inc_sud / max(m_sud, 1e-12) / max(inc_all, 1e-12)),
        vsl=_vsl(par, ygrid, policy),
        p_use=p_use, v=vbar, pid=pid)


def _vsl(par, ygrid, policy):
    """Value of a statistical life at mean income, in units of mean income.
    With log utility the marginal rate of substitution between consumption and
    survival is the continuation value times consumption."""
    k = int(np.argmin(np.abs(ygrid - 1.0)))
    _, V2, _ = solve_late(par, ygrid[k], policy)
    return float(par.beta * par.phi0 * V2[0, 0] * ygrid[k])


def price_elasticity(par, ygrid, w, policy=None, step=0.06):
    """
    d log(participation) / d log(p_v) at fixed supply. This is what the
    empirical literature estimates from tax and enforcement variation, so it is
    a DEMAND elasticity and needs no market clearing: move the price, read off
    the participation response.
    """
    lo = aggregates(with_(par, p_v=1.0 - step), ygrid, w, policy)['part']
    hi = aggregates(with_(par, p_v=1.0 + step), ygrid, w, policy)['part']
    if lo <= 1e-9 or hi <= 1e-9:
        return 0.0
    return float((np.log(hi) - np.log(lo))
                 / (np.log(1.0 + step) - np.log(1.0 - step)))


def demand(par, ygrid, w, policy=None):
    ev = profile(par, ygrid, policy)[1]
    return float((w / w.sum() * ev).sum())


def clear_price(par, ygrid, w, policy=None, lo=0.25, hi=4.0, iters=22):
    """Supply slopes up and demand down, so excess demand is monotone in p."""
    for _ in range(iters):
        p = np.sqrt(lo * hi)
        if demand(with_(par, p_v=p), ygrid, w, policy) - par.psi * p**par.eps_s > 0:
            lo = p
        else:
            hi = p
    return float(np.sqrt(lo * hi))
