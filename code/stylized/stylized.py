"""
A stylised three period model of drug use, homelessness and housing policy.

WHAT IT IS FOR

Two things and nothing else:

    1  which channel decides WHO uses drugs across the income distribution
    2  how the moral hazard of unconditional housing assistance operates

It is deliberately QUALITATIVE. It shows directions, and the sign and relative
size of two opposing forces. Every magnitude in the paper comes from the full
model, which has six state variables and can be disciplined properly. There is
no validation section here and there should not be one: the calibration is rough
by design, enough to put the model in the right region and no more.

NO PREFERENCE HETEROGENEITY

Households differ in permanent income and in nothing else, so everyone at a
given income makes the same choice and the use decision is a THRESHOLD IN
INCOME rather than a probability. That sharpness is the point: the figure shows
where the threshold sits and how far it moves when a channel is switched off.

It also keeps the paper's claim intact. The introduction says the model produces
the income gradient without ex ante preference heterogeneity. An earlier version
of this file gave the taste for drugs a lognormal spread, which smoothed the
extensive margin and made calibration easy, at the cost of assuming exactly the
thing the paper says it does not need.

THE ENVIRONMENT

  period 1  income y, employed, in the large unit. Choose consumption, drug use
            v >= 0 and saving. Flow utility  log c + gam log h + th[log(b+v) - log b].
            Using gives the disorder next period with probability 1 - exp(-lam v).

  period 2  the disorder d is realised. Unemployed with probability u0, paying a
            replacement rate, with a consumption floor under the bottom.
            Earnings carry a penalty xi if d = 1.
            Choose housing and saving. Recovery from the disorder is rho.

  period 3  terminal, same risks.

  housing   a large unit, a small unit, or the street. The street is free but
            supplies only h_hl of housing services. A voucher pays part of the
            rent.

            Two rental sizes rather than one, because with a single size a
            household whose cash falls below the rent cannot be housed at all,
            and the model puts the whole bottom of the distribution on the
            street. With a small unit available they downsize instead, which is
            what happens in the data and what the full model's housing grid is
            for.

THE CHANNELS THAT SURVIVED

    MORTALITY  kap    the disorder kills you
    UNEMPLOYMENT  u1     it costs you a job, and income support cannot cover rent
               h_hl   so you may end up on the street, where housing services
                      fall from a whole unit to almost nothing

Two channels were built and then removed because, after the model was FULLY
recalibrated without them, neither result moved:

    the street raises mortality        homelessness is a third of one per cent
    recovery is harder on the street   of the population, so a channel acting
                                       only on the homeless cannot move an
                                       aggregate

Both stay in the FULL model, where mortality and welfare are the objects of
interest and the counterfactuals move the homeless population a long way. They
are absent here because this model answers two questions and they bear on
neither.

EVERY CHANNEL HERE EXISTS IN THE FULL MODEL. That is a constraint, not a
coincidence. A stylised model that rests on a shock the full model does not use
is not an introduction to it, it is a different paper. An earlier version of
this file leaned on a direct wage penalty for the disorder; the full model has
that parameter and sets it to one, which is off, because the evidence
conditional on working is contested while the robust findings are on the
employment margin. It is gone.

Which channels survive is decided by ablation, not by taste: each is removed,
the model is FULLY recalibrated, and the counterfactuals are rerun. A channel
that changes neither result after recalibration is removed. See ABLATION.txt.
"""

import numpy as np


class P:
    # preferences
    th    = 0.11      # taste for drugs
    b     = 0.009     # Stone Geary subsistence; th/b is the pull of the first unit
    gam   = 0.25      # weight on housing. CALIBRATED to the housing budget share
    beta  = 0.96
    R     = 1.03
    phi0  = 0.93      # survival over one period, clean, employed, housed
    aleph = 2.50      # flow value of being alive

    # the disorder
    lam   = 25.0      # addiction hazard per unit of use. CALIBRATED
    rho   = 0.40      # recovery when housed, over one period
    kap   = 0.45      # MORTALITY: the disorder kills you
    u1    = 0.1625    # RESOURCE: the disorder costs you a job. Measured.

    # NO WAGE PENALTY. The full model has prod_pen_d and sets it to 1.00, which
    # is off, because the evidence on a wage penalty conditional on working is
    # contested while the robust findings are on the employment margin. A
    # stylised model must not rest on a shock the model it introduces does not
    # use, so the only consequence besides mortality here is unemployment.

    # employment and the safety net
    u0    = 0.049     # unemployment probability when clean
    # LOSING YOUR JOB. Income support replaces half of what you used to earn,
    # capped at half of average income. So a household at or below the mean gets
    # half its own income, and one above the mean gets half the mean.
    #
    # This is one rule doing two jobs. For the poorest household it delivers half
    # the smallest income in the support, which is well below the rent on the
    # smallest unit, so an unemployed household there cannot house itself out of
    # income alone and needs savings or a voucher. That is what connects the
    # disorder to homelessness, and without the connection the voucher has
    # nothing to insure and the model's second result does not exist. For a
    # household above the mean the cap means unemployment is a large fall rather
    # than a proportional one, so the disorder threatens housing across the
    # distribution rather than only at the bottom.
    #
    # This is not a safety net bolted onto unemployment, it IS what unemployment
    # pays, so it is not a component to be justified separately from the
    # unemployment risk itself.
    repl  = 0.50      # replacement rate
    ycap  = 1.00      # capped at this multiple of average income

    # housing
    h_lg  = 1.00
    h_sm  = 0.50
    h_hl  = 0.05      # the street. CALIBRATED to the homelessness rate
    # RENT IS SET, NOT CALIBRATED, so that the standard unit costs the housing
    # budget share of mean income. Calibrating it to the AGGREGATE share instead
    # doubled it, because in this model most households take the small unit,
    # which is backwards relative to the data, so rent per unit had to rise to
    # make total housing spending add up. At that rent the small unit cost a
    # fifth of mean income and a fifth of all households could not afford any
    # home while unemployed, which put homelessness at 1.29 per cent against a
    # target of 0.4. Setting it here leaves 4 per cent unable to afford the
    # small unit and homelessness at 0.35 per cent.
    pr    = 0.212     # rent per unit of housing services
    pV    = 0.27      # probability a voucher arrives
    kappa_r = 0.30    # tenant's share of the rent when covered
    policy = 'HF'

    p_v   = 1.0       # price of drugs

    na    = 60
    nv    = 140


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


# ---------------------------------------------------------------------------
def _states(par, d, policy, y):
    """(probability, income level, tenant's rent multiplier) given d."""
    pu = par.u1 if d == 1 else par.u0
    covered = (policy == 'HF') or (d == 0)
    pv = par.pV if covered else 0.0
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):
        # Lose your job and income support is a FLAT guarantee, not a share of
        # what you used to earn. That is what makes the disorder threaten
        # housing across the whole distribution rather than only in the bottom
        # decile: a proportional replacement rate leaves a household at mean
        # income able to afford the small unit even while unemployed, so the
        # disorder never puts its roof at risk and the voucher has nothing to
        # insure.
        inc = y if e == 0 else par.repl * min(y, par.ycap)
        for rmul, prb in ((par.kappa_r, pv), (1.0, 1.0 - pv)):
            if pe * prb > 1e-14:
                out.append((pe * prb, inc, rmul))
    return out


def _options(par, rmul):
    """(housing services, rent, on the street) for the three choices."""
    return ((par.h_hl, 0.0, 1),
            (par.h_sm, par.pr * par.h_sm * rmul, 0),
            (par.h_lg, par.pr * par.h_lg * rmul, 0))


def solve_late(par, y, policy):
    """Periods 3 and 2 by backward induction. Returns the street share too."""
    ag = np.linspace(0.0, 1.6 * y, par.na)

    V3 = np.zeros((par.na, 2))
    for d in (0, 1):
        for p, inc, rmul in _states(par, d, policy, y):
            cash = par.R * ag + inc
            best = np.full(par.na, -np.inf)
            for h, rent, _ in _options(par, rmul):
                c = cash - rent
                best = np.maximum(best, np.where(
                    c > 1e-9, np.log(np.maximum(c, 1e-12))
                    + par.gam * np.log(h) + par.aleph, -np.inf))
            V3[:, d] += p * best

    V2 = np.zeros((par.na, 2)); H2 = np.zeros((par.na, 2))
    R2 = np.zeros((par.na, 2))            # rent actually paid, for the housing share
    for d in (0, 1):
        for p, inc, rmul in _states(par, d, policy, y):
            cash = par.R * ag[:, None] + inc
            best = np.full(par.na, -np.inf); onst = np.zeros(par.na)
            rnt = np.zeros(par.na)
            for h, rent, street in _options(par, rmul):
                r = par.rho if d else 0.0
                EV3 = (1.0 - r) * V3[:, d] + r * V3[:, 0]
                surv = par.phi0 * (1.0 - par.kap * d)
                c = cash - rent - ag[None, :]
                v = np.where(c > 1e-9,
                             np.log(np.maximum(c, 1e-12)) + par.gam * np.log(h)
                             + par.aleph + par.beta * surv * EV3[None, :],
                             -np.inf).max(axis=1)
                onst = np.where(v > best, street, onst)
                rnt = np.where(v > best, rent, rnt)
                best = np.maximum(best, v)
            V2[:, d] += p * best; H2[:, d] += p * onst; R2[:, d] += p * rnt
    return ag, V2, H2, R2


def use_choice(par, y, policy=None):
    """
    At income y: (gain from using, best v, assets if using, assets if not).
    The SIGN of the gain is the use decision, and its zero crossings in income
    bound the use region.
    """
    policy = policy or par.policy
    ag, V2, _, _ = solve_late(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * y, par.nv - 1)))
    c = (y - par.p_v * vg[:, None]) - ag[None, :]
    pid = (1.0 - np.exp(-par.lam * vg))[:, None]
    EV2 = (1.0 - pid) * V2[None, :, 0] + pid * V2[None, :, 1]
    val = np.where(c > 1e-9,
                   np.log(np.maximum(c, 1e-12)) + par.gam * np.log(par.h_lg)
                   + par.aleph + par.beta * par.phi0 * EV2, -np.inf)
    base = val.max(axis=1)
    a_by_v = ag[np.argmax(np.where(c > 1e-9, val, -np.inf), axis=1)]
    tot = base + par.th * (np.log(par.b + vg) - np.log(par.b))
    k = int(np.argmax(tot[1:])) + 1
    return float(tot[k] - tot[0]), float(vg[k]), float(a_by_v[k]), float(a_by_v[0])


def threshold(par, ygrid, policy=None):
    """
    The use region, with its boundaries resolved exactly.

    The decision is zero or one at every income, so on a grid alone the
    aggregate jumps whenever a grid point flips. Wherever the sign changes
    between neighbours the crossing is bisected and the boundary cell is given
    the fraction of itself inside the region. The decision stays sharp and the
    aggregate moves smoothly, which is what a bracketing calibration needs.
    """
    policy = policy or par.policy
    n = len(ygrid)
    g = np.empty(n); vv = np.empty(n); au = np.empty(n); an = np.empty(n)
    for i, y in enumerate(ygrid):
        g[i], vv[i], au[i], an[i] = use_choice(par, y, policy)
    frac = (g > 0.0).astype(float)
    for i in range(n - 1):
        if (g[i] > 0.0) != (g[i + 1] > 0.0):
            lo, hi, sgn = ygrid[i], ygrid[i + 1], g[i] > 0.0
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                if (use_choice(par, mid, policy)[0] > 0.0) == sgn:
                    lo = mid
                else:
                    hi = mid
            w = (0.5 * (lo + hi) - ygrid[i]) / (ygrid[i + 1] - ygrid[i])
            frac[i], frac[i + 1] = (w, 0.0) if g[i] > 0.0 else (0.0, 1.0 - w)
    return np.clip(frac, 0.0, 1.0), vv, au, an


def aggregates(par, ygrid, w, policy=None):
    policy = policy or par.policy
    use, vv, au, an = threshold(par, ygrid, policy)
    pid = use * (1.0 - np.exp(-par.lam * vv))
    ww = w / w.sum(); ybar = (ww * ygrid).sum()

    hl = hl_sud = hcost = hinc = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2, R2 = solve_late(par, y, policy)
        for m, a, d in ((ww[i] * (1.0 - use[i]), an[i], 0),
                        (ww[i] * (use[i] - pid[i]), au[i], 0),
                        (ww[i] * pid[i], au[i], 1)):
            if m <= 0.0:
                continue
            street = float(np.interp(a, ag, H2[:, d]))
            # the rent ACTUALLY paid on the unit chosen, not the small one's
            # rent regardless of choice, which understated the housing share by
            # more than half and pinned the housing weight at its bound
            hl += m * street
            hcost += m * float(np.interp(a, ag, R2[:, d]))
            if d == 1:
                hl_sud += m * street
            for p, inc, rmul in _states(par, d, policy, y):
                hinc += m * p * inc

    part = float((ww * use).sum())
    return dict(part=part, sud=float((ww * pid).sum()),
                prog=float((ww * pid).sum() / max(part, 1e-12)),
                r_use=float((ww * use * ygrid).sum() / max(part, 1e-12) / ybar),
                homeless=float(hl),
                sud_of_homeless=float(hl_sud / max(hl, 1e-12)),
                housing_share=float(hcost / max(hinc, 1e-12)),
                use=use, v=vv)
