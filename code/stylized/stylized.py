"""
A stylized three period model of drug use, homelessness and housing policy.

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

  period 1  income y, employed, in the large unit, which is NOT a choice here,
            so y is income net of that rent. Choose consumption, drug use v >= 0
            and saving. Flow utility
                log c + gam log h + th[log(b+v) - log b] + aleph.
            Using gives the disorder next period with probability 1 - exp(-lam v),
            so the household internalises that using MORE is riskier.

  period 2  the disorder d is realised, but only for households that used.
            Unemployed with probability u0, or the higher u1 if d = 1. Income
            support replaces repl of previous earnings on a base capped at ycap.
            Choose consumption, housing and saving. Recovery from the disorder
            is rho. There is NO wage penalty: see below.

  period 3  terminal. Same employment, income support and housing as period 2,
            no drug use decision, assets run down, nothing bequeathed.

  housing   a large unit, a small unit, or the street. The street is free but
            supplies only h_hl of housing services. A voucher is means tested at
            yV, arrives with probability pV, and cuts the tenant's rent to
            kappa_r of the market rent.

            Two rental sizes rather than one, because with a single size a
            household whose cash falls below the rent cannot be housed at all.
            Collapsing h_sm into h_lg takes homelessness from 0.42 per cent to
            3.41 against a target of 0.399, and NO value of h_hl brings it back:
            making the street arbitrarily bad does not help a household that
            cannot afford the rent at any level of misery. That row of the
            ablation is a model that failed to calibrate, not a recalibrated
            model, which is the strongest case any component here has.

THE CHANNELS THAT SURVIVED

    MORTALITY  kap    the disorder kills you
    UNEMPLOYMENT  u1     it costs you a job, and income support cannot cover rent
               h_hl   so you may end up on the street, where housing services
                      fall from a whole unit to almost nothing

Two channels were built and then removed because, after the model was FULLY
recalibrated without them, neither result moved:

    the street raises mortality        homelessness is four tenths of one per
    recovery is harder on the street   cent of the population, so a channel
                                       acting only on the homeless cannot move
                                       an aggregate

Both stay in the FULL model, where mortality and welfare are the objects of
interest and the counterfactuals move the homeless population a long way. They
are absent here because this model answers two questions and they bear on
neither.

EVERY CHANNEL HERE EXISTS IN THE FULL MODEL. That is a constraint, not a
coincidence. A stylized model that rests on a shock the full model does not use
is not an introduction to it, it is a different paper. An earlier version of
this file leaned on a direct wage penalty for the disorder; the full model has
that parameter and sets it to one, which is off, because the evidence
conditional on working is contested while the robust findings are on the
employment margin. It is gone.

Which channels survive is decided by ablation, not by taste: each is removed,
the model is FULLY recalibrated, and the counterfactuals are rerun. A channel
that changes neither result after recalibration is removed. See ABLATION.txt.

That test is NECESSARY BUT NOT SUFFICIENT, and ycap is the counterexample. It
reads as removable in ABLATION.txt because the table only looks at the baseline,
where users are poor and the cap never binds. In figure 1 the unemployment
channel is scaled up alone, users are rich, and the cap is the only thing making
the resource penalty less than proportional to income; uncapped, that curve is
flat by construction. A component has to be tested where the figures put it.
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
    # stylized model must not rest on a shock the model it introduces does not
    # use, so the only consequence besides mortality here is unemployment.

    # employment and the safety net
    u0    = 0.049     # unemployment probability when clean
    # LOSING YOUR JOB. Income support replaces the fraction repl of what you used
    # to earn, on an earnings base capped at ycap. A household at or below the
    # mean therefore gets half its own income; one above the mean gets half the
    # mean, so the largest benefit anyone can draw is 0.5.
    #
    # The LEVEL is what connects the disorder to homelessness. For the poorest
    # household half its income is well below the rent on the smallest unit, so
    # an unemployed household there cannot house itself out of current income
    # alone and needs savings or a voucher. Set income support above the small
    # unit's rent and everyone is always housed, the voucher has nothing to
    # insure, and the moral hazard is exactly zero.
    #
    # This is not a safety net bolted onto unemployment, it IS what unemployment
    # pays, so it is not a component to be justified separately from the
    # unemployment risk itself.
    #
    # THE CAP EARNS ITS PLACE, and it took a second look to see it. Removing it
    # leaves the baseline calibration and BOTH policy forces identical to four
    # decimals, so ablate.py votes to cut it. That verdict is wrong, because
    # ablate.py only ever looks at the baseline. Without the cap, income support
    # is exactly proportional to income, and a penalty proportional to income
    # cannot move a gradient generated by income: the unemployment curve in
    # figure 1 becomes flat at 3.37 by construction. With the cap it falls to
    # 1.96, so the channel does something and still fails to reverse the
    # gradient, which is the honest version of the result and the one a referee
    # cannot dismiss as a knife edge. Real income support is capped too.
    repl  = 0.50      # replacement rate
    ycap  = 1.00      # earnings base capped at this multiple of average income

    # HOUSING. Rent per unit of housing services is the NUMERAIRE, p_r = 1, so
    # a unit size and its rent are the same number. The standard unit is set to
    # the housing budget share in the data, 21.2 per cent of average income, and
    # the small unit is half of it.
    h_lg  = 0.212
    h_sm  = 0.106
    h_hl  = 0.05      # the street. CALIBRATED to the homelessness rate
    pr    = 1.00      # rent per unit of housing services: the numeraire
    # FINANCING. A proportional tax on all income, in every period, set so that
    # revenue covers the voucher outlay. Zero by default: the calibration and the
    # two headline results are all computed without it, and it is switched on
    # only in welfare.py, to ask whether making households pay for the programme
    # changes which policy they prefer.
    tau   = 0.00
    pV    = 0.27      # probability a voucher arrives, conditional on eligibility
    yV    = 1.00      # MEANS TEST: eligible if current income is below the mean
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
    # POLICY. Treatment First withdraws the voucher on acquiring the disorder,
    # Housing First does not. That single difference is the whole experiment.
    covered = (policy == 'HF') or (d == 0)
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):
        # Lose your job and income support replaces the fraction repl of what
        # you used to earn, on an earnings base capped at ycap. For the poorest
        # household that is well below the rent on the smallest unit, so the
        # disorder can put the roof at risk, which is what the voucher insures.
        gross = y if e == 0 else par.repl * min(y, par.ycap)
        inc = (1.0 - par.tau) * gross
        # MEANS TEST. A voucher can only reach a household whose income in that
        # state is below the mean. Every unemployed household passes the test;
        # employed households pass only in the bottom part of the distribution.
        pv = par.pV if (covered and inc <= par.yV) else 0.0
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
    """
    Periods 3 and 2 by backward induction.

    Returns (assets grid, V2, street share, rent paid, voucher outlay). The last
    of these is the government's expected spending on this household from
    period 2 on, discounted at the market rate and weighted by survival. It is
    pure accounting: nothing in the household's problem depends on it, and the
    household never pays for it. It exists so that the two policies can be
    compared at equal COST as well as at equal generosity, which is the only
    comparison in this model under which Treatment First can win.
    """
    ag = np.linspace(0.0, 1.6 * y, par.na)

    V3 = np.zeros((par.na, 2))
    G3 = np.zeros((par.na, 2))
    Y3 = np.zeros(2)                      # pre tax income, for the tax base
    for d in (0, 1):
        for p, inc, rmul in _states(par, d, policy, y):
            Y3[d] += p * inc / max(1.0 - par.tau, 1e-9)
            cash = par.R * ag + inc
            best = np.full(par.na, -np.inf); sub = np.zeros(par.na)
            for h, rent, street in _options(par, rmul):
                c = cash - rent
                v = np.where(c > 1e-9, np.log(np.maximum(c, 1e-12))
                             + par.gam * np.log(h) + par.aleph, -np.inf)
                # what the voucher pays on this option: the rest of the market
                # rent. Zero on the street, which is free to begin with.
                s = 0.0 if street else par.pr * h * (1.0 - rmul)
                sub = np.where(v > best, s, sub)
                best = np.maximum(best, v)
            V3[:, d] += p * best
            G3[:, d] += p * sub

    V2 = np.zeros((par.na, 2)); H2 = np.zeros((par.na, 2))
    R2 = np.zeros((par.na, 2))            # rent actually paid, for the housing share
    G2 = np.zeros((par.na, 2))            # voucher outlay, periods 2 and 3
    Y2 = np.zeros(2)                      # pre tax income, periods 2 and 3
    for d in (0, 1):
        surv_d = par.phi0 * (1.0 - par.kap * d)
        r_d = par.rho if d else 0.0
        Y2[d] = ((1.0 - r_d) * Y3[d] + r_d * Y3[0]) * surv_d / par.R
        for p, inc, rmul in _states(par, d, policy, y):
            Y2[d] += p * inc / max(1.0 - par.tau, 1e-9)
            cash = par.R * ag[:, None] + inc
            best = np.full(par.na, -np.inf); onst = np.zeros(par.na)
            rnt = np.zeros(par.na); out = np.zeros(par.na)
            r = par.rho if d else 0.0
            EV3 = (1.0 - r) * V3[:, d] + r * V3[:, 0]
            EG3 = (1.0 - r) * G3[:, d] + r * G3[:, 0]
            surv = par.phi0 * (1.0 - par.kap * d)
            for h, rent, street in _options(par, rmul):
                c = cash - rent - ag[None, :]
                obj = np.where(c > 1e-9,
                               np.log(np.maximum(c, 1e-12)) + par.gam * np.log(h)
                               + par.aleph + par.beta * surv * EV3[None, :],
                               -np.inf)
                ia = np.argmax(obj, axis=1)
                v = obj[np.arange(par.na), ia]
                s = 0.0 if street else par.pr * h * (1.0 - rmul)
                g = s + surv * EG3[ia] / par.R
                onst = np.where(v > best, street, onst)
                rnt = np.where(v > best, rent, rnt)
                out = np.where(v > best, g, out)
                best = np.maximum(best, v)
            V2[:, d] += p * best; H2[:, d] += p * onst
            R2[:, d] += p * rnt;  G2[:, d] += p * out
    return ag, V2, H2, R2, G2, Y2


def use_choice(par, y, policy=None):
    """
    At income y: (gain from using, best v, assets if using, assets if not).
    The SIGN of the gain is the use decision, and its zero crossings in income
    bound the use region.
    """
    policy = policy or par.policy
    ag, V2, _, _, _, _ = solve_late(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * y, par.nv - 1)))
    cash = ((1.0 - par.tau) * y - par.p_v * vg[:, None]) - ag[None, :]
    pid = (1.0 - np.exp(-par.lam * vg))[:, None]
    EV2 = (1.0 - pid) * V2[None, :, 0] + pid * V2[None, :, 1]
    # HOUSING IS A CHOICE IN EVERY PERIOD, period 1 included. The household is
    # employed and clean here, but it still picks among the same three options
    # and pays for the one it picks, so y is income and not income net of some
    # assumed rent. Vouchers are the one thing that does not operate yet: the
    # programme starts in period 2. That costs the policy comparison nothing,
    # because every period 1 household is clean, so Housing First and Treatment
    # First would cover exactly the same households on exactly the same terms.
    val = np.full(cash.shape, -np.inf)
    for h, rent, _ in _options(par, 1.0):
        c = cash - rent
        val = np.maximum(val, np.where(
            c > 1e-9,
            np.log(np.maximum(c, 1e-12)) + par.gam * np.log(h)
            + par.aleph + par.beta * par.phi0 * EV2, -np.inf))
    base = val.max(axis=1)
    a_by_v = ag[np.argmax(val, axis=1)]
    tot = base + par.th * (np.log(par.b + vg) - np.log(par.b))
    k = int(np.argmax(tot[1:])) + 1
    return float(tot[k] - tot[0]), float(vg[k]), float(a_by_v[k]), float(a_by_v[0])


def value1(par, y, policy=None):
    """
    V1(y): lifetime value at the household's own optimum, which is what welfare
    has to be measured on. The household is forward looking and faces the true
    addiction hazard, so whatever v it picks is the v it wants given the policy.
    """
    policy = policy or par.policy
    ag, V2, _, _, _, _ = solve_late(par, y, policy)
    vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * y, par.nv - 1)))
    c = ((1.0 - par.tau) * y - par.p_v * vg[:, None]) - ag[None, :]
    pid = (1.0 - np.exp(-par.lam * vg))[:, None]
    EV2 = (1.0 - pid) * V2[None, :, 0] + pid * V2[None, :, 1]
    val = np.full(c.shape, -np.inf)
    for h, rent, _ in _options(par, 1.0):
        cc = c - rent
        val = np.maximum(val, np.where(
            cc > 1e-9,
            np.log(np.maximum(cc, 1e-12)) + par.gam * np.log(h)
            + par.aleph + par.beta * par.phi0 * EV2, -np.inf))
    tot = val.max(axis=1) + par.th * (np.log(par.b + vg) - np.log(par.b))
    return float(tot.max())


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

    hl = hl_sud = hcost = hinc = cost = base_y = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2, R2, G2, Y2 = solve_late(par, y, policy)
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
            cost += m * float(np.interp(a, ag, G2[:, d]))
            # the tax base: period 1 earnings plus the present value of income
            # from period 2 on, all pre tax
            base_y += m * (y + par.phi0 * Y2[d] / par.R)
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
                cost=float(cost), tax_base=float(base_y),
                use=use, v=vv)
