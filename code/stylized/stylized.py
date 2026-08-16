"""
A stylized two period model of drug use, homelessness and housing policy.

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

Households differ in permanent income and in nothing else. They also differ in
the employment and voucher draws of period 1, which are the same lotteries every
household faces, so within a draw the use decision is a THRESHOLD IN INCOME
rather than a probability. That sharpness is the point: the figure shows where
the threshold sits and how far it moves when a channel is switched off.

It also keeps the paper's claim intact. The introduction says the model produces
the income gradient without ex ante preference heterogeneity. An earlier version
of this file gave the taste for drugs a lognormal spread, which smoothed the
extensive margin and made calibration easy, at the cost of assuming exactly the
thing the paper says it does not need.

THE ENVIRONMENT

  period 1  income y. Employment is drawn with the unemployment probability u0,
            and an income eligible household draws a voucher with probability
            pV. The household is clean. It then chooses consumption, housing,
            drug use v >= 0 and saving. Flow utility
                (1-gam-th) log c + gam log h + th[log(b+v) - log b] + aleph.
            Using gives the disorder at the TRANSITION with probability
            1 - exp(-lam v), so the household internalises that using MORE is
            riskier.

  the       the disorder d' is realised, and survival into period 2 is
  transition  phi(d') = phi0 (1 - kap d'). The mortality penalty applies here
            and only here.

  period 2  terminal. Employment is drawn again, with u0 if clean and the
            higher u1 if d' = 1, the voucher is drawn again subject to the
            policy rule, housing is chosen, assets are run down and nothing is
            bequeathed.

  housing   a large unit, a small unit, or the street. The street is free but
            supplies only h_hl of housing services. A voucher is means tested at
            yV, arrives with probability pV, and cuts the tenant's rent to
            kappa_r of the market rent.

            Two rental sizes rather than one, because with a single size a
            household whose cash falls below the rent cannot be housed at all.
            Collapsing h_sm into h_lg takes homelessness far above its target
            and NO value of h_hl brings it back: making the street arbitrarily
            bad does not help a household that cannot afford the rent at any
            level of misery. That row of the ablation is a model that failed to
            calibrate, not a recalibrated model, which is the strongest case any
            component here has.

WHY TWO PERIODS AND WHERE THE DISORDER IS REALISED

Mortality is a tax on a continuation value, so the disorder can only cost
anything if there is a future left when it is carried. That does NOT require a
third period, it requires the disorder to be realised at a TRANSITION rather
than inside the terminal period. Here it is drawn on the way from period 1 to
period 2 and survival over that transition depends on it, so acquiring it
destroys the whole of period 2.

An earlier two period attempt, in the deleted two_period.py, realised the
disorder IN the final period, where death costs nothing because nothing follows
it. Its moral hazard collapsed from +2.55 to +0.24 and it was correctly
rejected. That is a verdict on where the draw sits, not on how many periods
there are, and it is the reason this file puts the draw in the transition.

A PERIOD IS THIRTY YEARS, so the two of them span ages twenty five to eighty
five, and every parameter with an annual counterpart is compounded to that
length rather than used raw.

SURVIVAL GOES INSIDE THE EXPECTATION

The period 1 continuation is

    E_{d'} [ phi(d') W2(a', y, d') ]     and NOT     phi * E_{d'} W2 .

Survival depends on the realised disorder, so it belongs inside. Writing it
outside is the value of life pathology in another form: wherever W2 is negative,
lower survival RAISES the expected continuation and the disorder becomes
something the household wants.

THE CHANNELS THAT SURVIVED

    MORTALITY  kap    the disorder kills you
    UNEMPLOYMENT  u1     it costs you a job, and income support cannot cover rent
               h_hl   so you may end up on the street, where housing services
                      fall from a whole unit to almost nothing

Two channels were built and then removed because, after the model was FULLY
recalibrated without them, neither result moved:

    the street raises mortality        homelessness is a fraction of one per
    recovery is harder on the street   cent of the population, so a channel
                                       acting only on the homeless cannot move
                                       an aggregate

Recovery has since gone entirely, and not because it was small: with a terminal
period 2 there is no period to recover into, so rho has nothing to name. It
stays in the FULL model, where treatment is a choice and rho is the parameter
its whole effect runs through.

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
    # SHARES THAT SUM TO ONE. The weight on consumption is 1-gam-th, so gam is
    # the housing budget share proper rather than gam/(1+gam+th). gam is set to
    # 0.268 of non drug spending, which is the share in the data.
    # THETA IS 0.20 AND NOT 0.11, and the two period model is what allows it. In
    # the three period model raising theta bought a drug spending share at the
    # cost of the income gradient: users stopped being poor. Here the mortality
    # channel is strong enough to hold the gradient while theta rises, and the
    # spending share goes from 1.9 per cent to 4.9. The ceiling is real and it is
    # close: theta = 0.22 still passes, theta = 0.24 does not, and by 0.28 users
    # are RICHER than average and the model has changed regime. 0.20 is chosen
    # over 0.22 because it buys the same spending share with room to spare.
    # See scan_theta.py, which screens the channel decomposition before it reads
    # the spending share.
    th    = 0.20      # weight on drug use
    b     = 0.009     # Stone Geary subsistence; th/b is the pull of the first unit
    gam   = 0.2144    # weight on housing = 0.268 * (1 - th)
    # A PERIOD IS THIRTY YEARS, so the discount factor and the interest rate are
    # the annual values COMPOUNDED, not the annual values used raw. The interest
    # rate is set to 1/beta so that beta*R = 1 and nothing in the results comes
    # from a wedge between the two.
    #
    # THE ANNUAL FACTOR IS 0.995 AND NOT 0.99, and over thirty years that is the
    # difference between 0.740 and 0.860. It is not a free choice of units. The
    # value of a statistical life pins the DISCOUNTED continuation, beta*W2, so
    # raising beta lowers the aleph needed to deliver it. A smaller aleph is a
    # continuation that depends more on the household's own consumption and less
    # on a constant, which is exactly the part of the continuation that scales
    # with permanent income. So a patient household has a mortality penalty that
    # bites harder at the top and less hard at the bottom, which steepens the
    # income gradient in who uses and, by lowering what a poor household stands
    # to lose, raises how much a user uses. Both of those move the model towards
    # the data at once.
    # THE ANNUAL FACTOR IS 0.995, so a thirty year period discounts at 0.86. It
    # is high on purpose: the consequences of using arrive a FULL THIRTY YEARS
    # after the decision, and at an annual 0.99 they would arrive weighted 0.74,
    # which asks the household to weigh a distant death against an immediate
    # pleasure with the scales already tipped by impatience. The interest rate is
    # 1/beta so that beta*R = 1 and nothing comes from a wedge between the two.
    #
    # BETA = 1 WAS TRIED AND REJECTED, and it is worth recording why, because the
    # argument for it is a good one: over a thirty year gap, why discount at all?
    # Two things happen, and they run the wrong way.
    #
    #   The drug spending share FALLS, from 4.8 per cent to 3.2. A household that
    #   weighs the thirty year consequence in full finds the SUD more costly and
    #   uses less, so patience and the spending share pull against each other in
    #   exactly the way mortality and the spending share do.
    #
    #   The minimum ex ante value of life goes NEGATIVE, to -0.02. The VSL pins
    #   the discounted continuation beta * E W2, so a larger beta buys a smaller
    #   aleph, and aleph is the part of the continuation that does not shrink
    #   when consumption does. Shrink it far enough and the poorest household
    #   prefers death, which inverts the mechanism the model rests on.
    #
    # 0.995 is as patient as the model can be while every household still values
    # its own life.
    beta_ann = 0.995
    beta  = 0.995 ** 30
    R     = 1.0 / (0.995 ** 30)
    years = 30.0      # years in a period, used to put the VSL in annual units
    phi0  = 0.91      # survival over one period, clean: ages 25 to 55, CDC
    # SET SO THAT NO HOUSEHOLD HAS A NEGATIVE VALUE OF LIFE. When the poorest
    # household's continuation goes below zero, dying is worth more than living
    # and it then WANTS the extra mortality the disorder brings, which inverts
    # the mechanism. It is calibrated to the value of a statistical life, and
    # the level it needs is higher here than in the three period version because
    # one period of continuation has to deliver the whole of it.
    aleph = 4.00      # flow value of being alive. CALIBRATED

    # the disorder
    lam   = 25.0      # SUD hazard per unit of use. CALIBRATED
    # MORTALITY: the SUD kills you. kap is the proportional fall in survival over
    # a THIRTY YEAR period, and it is derived from the annual mortality rate
    # ratio rather than assumed, because a period this long is not forgiving
    # about the difference. The full model multiplies the ANNUAL death
    # probability by 6.9, so the right construction compounds that annual hazard
    # over thirty years:
    #
    #     annual survival, clean       p_a  = phi0 ** (1/30)      = 0.99686
    #     annual survival with a SUD   p_d  = 1 - smr*(1 - p_a)   = 0.97834
    #     kap                               = 1 - p_d**30 / phi0  = 0.4326
    #
    # Applying the 6.9 to the THIRTY YEAR death probability instead would give
    # kap = 0.58, which is the same arithmetic error as using an annual discount
    # factor for a thirty year period. The number it replaces, a flat 0.45, was
    # carried over from the twenty year version, where it implied a rate ratio of
    # 9.2; at thirty years it implies 7.4. Both sit inside Hjorthoj et al.'s
    # range, so this is a correction of construction rather than of magnitude,
    # and it moves the penalty DOWN very slightly.
    smr_d = 6.9       # mortality rate ratio with a SUD. Hjorthoj et al. (2023)
    kap   = 1.0 - (1.0 - 6.9 * (1.0 - 0.91 ** (1.0 / 30.0))) ** 30 / 0.91
    u1    = 0.1625    # RESOURCE: the disorder costs you a job. Measured.

    # NO RECOVERY PARAMETER. rho needed a period to recover INTO and there is
    # none: period 2 is terminal. It belongs to the full model, where treatment
    # is a choice and rho is what its effect runs through.

    # NO WAGE PENALTY. The full model has prod_pen_d and sets it to 1.00, which
    # is off, because the evidence on a wage penalty conditional on working is
    # contested while the robust findings are on the employment margin. A
    # stylized model must not rest on a shock the model it introduces does not
    # use, so the only consequence besides mortality here is unemployment.

    # employment and the safety net
    # u0 IS NOT DECORATION. Setting it to zero makes every route into
    # homelessness run through the disorder, and the share of the homeless
    # carrying one then goes to 0.997. The data say the opposite: most homeless
    # people do not have a substance use disorder, roughly a third do. A clean
    # household therefore has to be able to lose its job too, in BOTH periods:
    # period 1 draws employment on the same lottery as period 2.
    # FRED series UNRATE, the headline civilian unemployment rate, monthly and
    # seasonally adjusted, averaged over 2014 to 2024: 4.852 per cent. The file is
    # data/raw/FRED_UNRATE_monthly_1948_2024.xlsx.
    #
    # ONE CAVEAT ON THE UNIVERSE. UNRATE is ages 16 and over, while u1 is NSDUH
    # ages 26 and over, so the two are not on the same age base. The headline rate
    # is HIGHER than a 25+ rate, because young workers carry more unemployment, so
    # this choice overstates u0 and understates the gap u1 - u0 that the whole
    # unemployment channel runs on. It is conservative in the direction that
    # matters, which is why it is acceptable rather than merely convenient.
    u0    = 0.0485    # unemployment probability when clean
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
    # leaves the baseline calibration and BOTH policy forces nearly identical,
    # so ablate.py votes to cut it. That verdict is wrong, because ablate.py
    # only ever looks at the baseline. Without the cap, income support is
    # exactly proportional to income, and a penalty proportional to income
    # cannot move a gradient generated by income: the unemployment curve in
    # figure 1 becomes flat by construction. With the cap it falls, so the
    # channel does something and still fails to reverse the gradient, which is
    # the honest version of the result and the one a referee cannot dismiss as a
    # knife edge. Real income support is capped too.
    repl  = 0.50      # replacement rate
    ycap  = 1.00      # earnings base capped at this multiple of average income

    # HOUSING. Rent per unit of housing services is the NUMERAIRE, p_r = 1, so
    # a unit size and its rent are the same number.
    #
    # THE STANDARD UNIT IS DERIVED FROM GAMMA, and the change is worth recording
    # because the previous version double counted. It used to be fixed at 21.2
    # per cent of average income, the housing cost to income ratio in the SCF,
    # while gamma was fixed separately at the Consumer Expenditure Survey share.
    # Those are two external numbers aimed at the same object and nothing made
    # them agree. Now there is only ONE number, 0.268, and the unit is what it
    # implies: the dwelling a household at mean income would occupy if housing
    # were continuously choosable, h_lg = gam/(1-th) * ybar. The small unit is a
    # QUARTER of it and the street is what the homelessness rate identifies.
    #
    # A QUARTER RATHER THAN A HALF, and the reason is the homelessness margin.
    # The small unit is the affordability floor: a household whose cash falls
    # below its rent has no housed option at all and is homeless BY FORCE, which
    # no value of h_hl undoes. At half of a 0.262 unit that floor sits at 0.131
    # and forced homelessness alone runs above the 0.399 per cent target, so the
    # h_hl bracket loses its interior solution. At a quarter the floor is 0.0655,
    # the target is reachable, and h_hl does the work it is supposed to do.
    #
    # CALIBRATING h_lg ON THE REALISED HOUSING SHARE WAS TRIED AND FAILS, and the
    # reason is structural rather than a matter of tuning. Every household
    # consumes at most ONE standard unit however rich it is, so the aggregate
    # share is bounded above by h_lg in units of mean income and the rich drag it
    # down. Matching 26.8 per cent needs h_lg near 0.45, hence a small unit at
    # 0.225, and every household whose cash falls below that is homeless BY
    # FORCE, which no value of h_hl undoes. That sweep hit the share exactly and
    # put homelessness at 3.2 per cent against a target of 0.399, with h_hl
    # pinned at its lower bound and the SUD share of the homeless down at 8 per
    # cent. The frontier, with h_hl refitted at every point:
    #
    #     h_lg    h_sm     h_hl     housing share   homelessness
    #     0.212   0.106   4.2e-04       0.163          0.00395   <- on target
    #     0.240   0.120   7.7e-05       0.177          0.00593
    #     0.270   0.135   1.0e-07       0.195          0.00594
    #     0.340   0.170   1.0e-07       0.231          0.01091
    #     0.450   0.225   1.0e-07       0.267          0.03160
    #
    # So the realised share is an untargeted moment this model misses, for the
    # same kind of reason it misses the drug spending share, and it is reported
    # as one.
    h_lg  = 0.2620    # = gam/(1-th) * ybar. DERIVED, see above
    h_sm  = 0.0655    # tied to H_RATIO * h_lg in with_()
    h_hl  = 0.05      # the street. CALIBRATED to the homelessness rate
    pr    = 1.00      # rent per unit of housing services: the numeraire
    pV    = 0.27      # probability a voucher arrives, conditional on eligibility
    yV    = 1.00      # MEANS TEST: eligible if current income is below the mean
    kappa_r = 0.30    # tenant's share of the rent when covered
    policy = 'HF'

    p_v   = 1.0       # price of drugs

    # PARTIAL INTERNALISATION OF THE CHILD. Both are zero in the baseline, which
    # is what makes the damage to the child a pure externality. Set omega > 0
    # and the parent subtracts omega * chdmg * pi(v) from its objective, where
    # chdmg is the child's expected loss in lifetime utility from being born to
    # a parent who acquired the disorder. It depends only on v, so it acts as an
    # extra deterrent that rises with use, which is the right economics: a
    # parent who cares about the child uses less. See internalise.py.
    omega = 0.0
    chdmg = 0.0

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


H_RATIO = 0.25    # the small unit as a fraction of the standard one


def with_(par, **kw):
    f = fields(par); f.update(kw)
    # THE SMALL UNIT IS A QUARTER OF THE STANDARD ONE, always, and it is tied
    # here rather than at the call sites so that a bracket on h_lg cannot forget
    # it and silently calibrate one size against a stale other.
    if 'h_lg' in kw and 'h_sm' not in kw:
        f['h_sm'] = H_RATIO * f['h_lg']
    return clone(**f)


# ---------------------------------------------------------------------------
def _states(par, d, policy, y, used=0):
    """
    (probability, income level, tenant's rent multiplier) given d and whether
    the household used drugs in period 1.

    POLICY. Treatment First withdraws the voucher from any household that
    violates the sobriety condition, which is v > 0 OR d = 1, and not only from
    those that went on to acquire the disorder. That is exactly the rule in the
    full model, where voucher receipt is revoked with certainty whenever v > 0.
    Housing First withdraws it from nobody. That single difference is the whole
    experiment.

    This is called for BOTH periods. In period 1 it is called at d = 0 with
    used = 0, because the voucher is drawn on arrival, before v is chosen, so
    nobody has yet violated anything; the condition then bites within the period
    through _p1_rmul, which strips the voucher from a period 1 household that
    goes on to choose v > 0.
    """
    pu = par.u1 if d == 1 else par.u0
    covered = (policy == 'HF') or (d == 0 and not used)
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):
        # Lose your job and income support replaces the fraction repl of what
        # you used to earn, on an earnings base capped at ycap. For the poorest
        # household that is well below the rent on the smallest unit, so the
        # disorder can put the roof at risk, which is what the voucher insures.
        inc = y if e == 0 else par.repl * min(y, par.ycap)
        # MEANS TEST. A voucher can only reach a household whose income in that
        # state is below the mean. Every unemployed household passes the test;
        # employed households pass only in the bottom part of the distribution.
        pv = par.pV if (covered and inc <= par.yV) else 0.0
        for rmul, prb in ((par.kappa_r, pv), (1.0, 1.0 - pv)):
            out.append((pe * prb, inc, rmul))
    return out


def _p1_rmul(par, policy, rmul):
    """
    The rent multiplier a period 1 household faces once it has chosen v > 0.

    Under Treatment First the sobriety condition applies to the voucher in every
    period in which it is held, period 1 included, so a household that uses
    loses it immediately and pays the market rent. Under Housing First it keeps
    what it drew. The period 1 voucher is drawn BEFORE v is chosen, since the
    household is clean on arrival, so conditionality operates here as a
    consequence of the drug decision rather than as a screen on entry.
    """
    return rmul if policy == 'HF' else 1.0


def _options(par, rmul):
    """(housing services, rent, on the street) for the three choices."""
    return ((par.h_hl, 0.0, 1),
            (par.h_sm, par.pr * par.h_sm * rmul, 0),
            (par.h_lg, par.pr * par.h_lg * rmul, 0))


def solve_period2(par, y, policy, used=0):
    """
    Period 2, which is terminal: assets are run down and nothing is bequeathed.

    Returns (assets grid, W2, street share, rent paid, voucher outlay), each
    indexed by the assets grid and by the disorder d. The last of these is the
    government's expected spending on this household in period 2. It is pure
    accounting: nothing in the household's problem depends on it, and the
    household never pays for it. It exists so that the two policies can be
    compared at equal COST as well as at equal generosity, which is the only
    comparison in this model under which Treatment First can win.
    """
    ag = np.linspace(0.0, 1.6 * y, par.na)

    W2 = np.zeros((par.na, 2)); H2 = np.zeros((par.na, 2))
    R2 = np.zeros((par.na, 2))            # rent actually paid, for the housing share
    G2 = np.zeros((par.na, 2))            # voucher outlay in period 2
    for d in (0, 1):
        for p, inc, rmul in _states(par, d, policy, y, used):
            if p <= 1e-14:
                continue
            cash = par.R * ag + inc
            best = np.full(par.na, -np.inf); onst = np.zeros(par.na)
            rnt = np.zeros(par.na); out = np.zeros(par.na)
            for h, rent, street in _options(par, rmul):
                c = cash - rent
                v = np.where(c > 1e-9,
                             (1.0 - par.gam - par.th) * np.log(np.maximum(c, 1e-12))
                             + par.gam * np.log(h) + par.aleph, -np.inf)
                # what the voucher pays on this option: the rest of the market
                # rent. Zero on the street, which is free to begin with.
                s = 0.0 if street else par.pr * h * (1.0 - rmul)
                onst = np.where(v > best, street, onst)
                rnt = np.where(v > best, rent, rnt)
                out = np.where(v > best, s, out)
                best = np.maximum(best, v)
            W2[:, d] += p * best; H2[:, d] += p * onst
            R2[:, d] += p * rnt;  G2[:, d] += p * out
    return ag, W2, H2, R2, G2


def _branch(par, ag, inc, rmul, vg, cont):
    """
    Period 1, one branch of the drug decision: the value at each v on the grid,
    maximised over housing and saving, with the choice recorded.

    cont is the continuation E_{d'}[phi(d') W2(a',y,d')] on (v, a'), which is
    where the mortality penalty enters, INSIDE the expectation over d'.
    """
    n = len(vg)
    cash = (inc - par.p_v * vg[:, None]) - ag[None, :]
    val = np.full(cash.shape, -np.inf)
    st = np.zeros(cash.shape); rn = np.zeros(cash.shape); sb = np.zeros(cash.shape)
    for h, rent, street in _options(par, rmul):
        c = cash - rent
        u = np.where(c > 1e-9,
                     (1.0 - par.gam - par.th) * np.log(np.maximum(c, 1e-12))
                     + par.gam * np.log(h) + par.aleph + par.beta * cont,
                     -np.inf)
        s = 0.0 if street else par.pr * h * (1.0 - rmul)
        st = np.where(u > val, street, st)
        rn = np.where(u > val, rent, rn)
        sb = np.where(u > val, s, sb)
        val = np.maximum(val, u)
    ia = np.argmax(val, axis=1)
    k = np.arange(n)
    return val[k, ia], ag[ia], st[k, ia], rn[k, ia], sb[k, ia]


def period1(par, y, policy=None):
    """
    The period 1 problem at income y, state by state.

    The household draws employment and, if income eligible, a voucher, and only
    then chooses housing, drug use and saving. So the use decision is a
    threshold in income WITHIN a draw, and participation at a given income is
    the probability of drawing a state in which the household uses.

    Returns a list, one entry per period 1 state, of

        (probability, gain from using, best v,
         (a', street, rent, voucher outlay)  if it uses,
         (a', street, rent, voucher outlay)  if it does not,
         income in the state, lifetime value at the household's own optimum)

    The SIGN of the gain is the use decision, and its zero crossings in income
    bound the use region. States of zero probability are RETAINED rather than
    dropped, so that the list is the same length at every income: the employed
    household's voucher state has probability zero above the means test, and
    dropping it there would shift every later index and break the bisection in
    threshold().
    """
    policy = policy or par.policy
    # TWO CONTINUATIONS, not one. Treatment First revokes the voucher from any
    # household that used, so period 2 is worth less after v > 0 even before the
    # disorder is realised. Under Housing First the two coincide and the second
    # solve is skipped.
    ag, W2c, _, _, _ = solve_period2(par, y, policy, used=0)
    W2u = W2c if policy == 'HF' else solve_period2(par, y, policy, used=1)[1]
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
    cont0 = (s0 * W2c[:, 0])[None, :]

    out = []
    for p, inc, rmul in _states(par, 0, policy, y, used=0):
        vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * inc, par.nv - 1)))
        pid = (1.0 - np.exp(-par.lam * vg))[:, None]
        # SURVIVAL INSIDE THE EXPECTATION over the realised disorder. Not
        # phi * E W2: see the note at the head of this file.
        cont = (1.0 - pid) * s0 * W2u[None, :, 0] + pid * s1 * W2u[None, :, 1]
        vu, au, su, ru, gu = _branch(par, ag, inc, _p1_rmul(par, policy, rmul),
                                     vg, cont)
        # v = 0 is solved on its own, because the household still holds the
        # voucher it drew and faces the clean continuation.
        v0, a0, s_0, r0, g0 = _branch(par, ag, inc, rmul, np.zeros(1), cont0)

        pen = par.omega * par.chdmg * (1.0 - np.exp(-par.lam * vg))
        tot = vu + par.th * (np.log(par.b + vg) - np.log(par.b)) - pen
        k = int(np.argmax(tot[1:])) + 1
        gain = float(tot[k] - v0[0])
        # V1 is the PARENT'S OWN lifetime value, which is what a planner counts
        # once and separately from the child's. The internalised term is added
        # back so that raising omega changes behaviour without double counting
        # the child.
        own = float(tot[k] + pen[k]) if gain > 0.0 else float(v0[0])
        out.append((p, gain, float(vg[k]),
                    (float(au[k]), float(su[k]), float(ru[k]), float(gu[k])),
                    (float(a0[0]), float(s_0[0]), float(r0[0]), float(g0[0])),
                    float(inc), own))
    return out


def use_prob(par, y, policy=None):
    """The probability a household at income y uses, over its period 1 draws."""
    return float(sum(p for p, g, *_ in period1(par, y, policy) if g > 0.0))


def value1(par, y, policy=None):
    """
    V1(y): lifetime value at the household's own optimum, which is what welfare
    has to be measured on. The household is forward looking and faces the true
    addiction hazard, so whatever v it picks is the v it wants given the policy.
    It is an expectation over the period 1 employment and voucher draws, since
    those are realised before anything is chosen.
    """
    return float(sum(p * own for p, _, _, _, _, _, own
                     in period1(par, y, policy)))


def threshold(par, ygrid, policy=None):
    """
    The use region, with its boundaries resolved exactly.

    Within a period 1 draw the decision is zero or one at every income, so on a
    grid alone the aggregate jumps whenever a grid point flips. Wherever the
    sign changes between neighbours the crossing is bisected and the boundary
    cell is given the fraction of itself inside the region. The decision stays
    sharp and the aggregate moves smoothly, which is what a bracketing
    calibration needs.

    Returns, per income and per period 1 state, the state probability, the
    fraction of the cell inside the use region, the chosen v, and the two
    branches of (a', street, rent, voucher outlay), plus the state's income.
    """
    policy = policy or par.policy
    rows = [period1(par, y, policy) for y in ygrid]
    ns = max(len(r) for r in rows)
    n = len(ygrid)
    PR = np.zeros((n, ns)); G = np.full((n, ns), np.nan); VV = np.zeros((n, ns))
    INC = np.zeros((n, ns))
    BU = np.zeros((n, ns, 4)); BN = np.zeros((n, ns, 4))
    for i, r in enumerate(rows):
        for s, (p, g, v, bu, bn, inc, _own) in enumerate(r):
            PR[i, s] = p; G[i, s] = g; VV[i, s] = v; INC[i, s] = inc
            BU[i, s] = bu; BN[i, s] = bn
    frac = (G > 0.0).astype(float)
    for s in range(ns):
        for i in range(n - 1):
            if np.isnan(G[i, s]) or np.isnan(G[i + 1, s]):
                continue
            if (G[i, s] > 0.0) == (G[i + 1, s] > 0.0):
                continue
            lo, hi, sgn = ygrid[i], ygrid[i + 1], G[i, s] > 0.0
            for _ in range(24):
                mid = 0.5 * (lo + hi)
                r = period1(par, mid, policy)
                gm = r[s][1] if s < len(r) else np.nan
                if np.isnan(gm):
                    break
                if (gm > 0.0) == sgn:
                    lo = mid
                else:
                    hi = mid
            w = (0.5 * (lo + hi) - ygrid[i]) / (ygrid[i + 1] - ygrid[i])
            frac[i, s], frac[i + 1, s] = ((w, 0.0) if G[i, s] > 0.0
                                          else (0.0, 1.0 - w))
    return PR, np.clip(frac, 0.0, 1.0), VV, BU, BN, INC


def aggregates(par, ygrid, w, policy=None):
    """
    Everything the calibration and the note read off the model.

    Aggregates that describe a stock, homelessness and the housing share, are
    taken over BOTH periods, weighted by the mass alive: one unit in period 1
    and phi(d') in period 2. Period 1 now carries unemployment, so a period 1
    household can be on the street too, and counting only period 2 would
    understate homelessness and overstate the share of the homeless who carry
    the disorder. Aggregates that describe the drug decision, participation and
    the disorder rate, are period 1 objects, since that is where v is chosen.
    """
    policy = policy or par.policy
    PR, frac, VV, BU, BN, INC = threshold(par, ygrid, policy)
    ww = w / w.sum(); ybar = (ww * ygrid).sum()
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)

    part = spend = uinc = sud = 0.0
    hl = hl_sud = hcost = hinc = cost = mass = 0.0
    # NON DRUG EXPENDITURE, which is what the Consumer Expenditure Survey share
    # is a share OF. In period 1 it is income less drug spending less saving; in
    # period 2, which is terminal, it is the whole of cash. Rent here is what the
    # tenant actually pays, net of any voucher, on both sides of the ratio, so
    # the object is an outlay share exactly as the survey measures it.
    hexp = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2c, R2c, G2c = solve_period2(par, y, policy, used=0)
        if policy == 'HF':
            H2u, R2u, G2u = H2c, R2c, G2c
        else:
            _, _, H2u, R2u, G2u = solve_period2(par, y, policy, used=1)
        for s in range(PR.shape[1]):
            if PR[i, s] <= 0.0:
                continue
            for uu, mm, br in ((1, ww[i] * PR[i, s] * frac[i, s], BU[i, s]),
                               (0, ww[i] * PR[i, s] * (1.0 - frac[i, s]), BN[i, s])):
                if mm <= 0.0:
                    continue
                a, street, rent, sub = br
                pid = (1.0 - np.exp(-par.lam * VV[i, s])) if uu else 0.0
                if uu:
                    part += mm; spend += mm * par.p_v * VV[i, s]
                    uinc += mm * INC[i, s]; sud += mm * pid
                # period 1: everyone alive, mass one
                mass += mm
                hl += mm * street
                hcost += mm * rent; hinc += mm * INC[i, s]; cost += mm * sub
                hexp += mm * (INC[i, s] - (par.p_v * VV[i, s] if uu else 0.0) - a)
                # period 2: the disorder is drawn at the transition and survival
                # depends on it
                Hx, Rx, Gx = (H2u, R2u, G2u) if uu else (H2c, R2c, G2c)
                for d, pd, surv in ((0, 1.0 - pid, s0), (1, pid, s1)):
                    m2 = mm * pd * surv
                    if m2 <= 0.0:
                        continue
                    street2 = float(np.interp(a, ag, Hx[:, d]))
                    mass += m2
                    hl += m2 * street2
                    if d == 1:
                        hl_sud += m2 * street2
                    hcost += m2 * float(np.interp(a, ag, Rx[:, d]))
                    cost += m2 * float(np.interp(a, ag, Gx[:, d])) / par.R
                    hexp += m2 * par.R * a
                    for p2, inc2, _ in _states(par, d, policy, y, uu):
                        hinc += m2 * p2 * inc2
                        hexp += m2 * p2 * inc2

    use = (PR * frac).sum(axis=1)
    return dict(part=float(part), sud=float(sud),
                # DRUG SPENDING OVER INCOME AMONG USERS, the moment that would
                # identify theta if it were targeted. Aggregate spending over
                # aggregate income of users, not the average of the ratios, so a
                # handful of very poor users cannot drive it.
                dshare=float(spend / max(uinc, 1e-12)),
                prog=float(sud / max(part, 1e-12)),
                r_use=float((ww * use * ygrid).sum() / max(part, 1e-12) / ybar),
                homeless=float(hl / max(mass, 1e-12)),
                sud_of_homeless=float(hl_sud / max(hl, 1e-12)),
                housing_share=float(hcost / max(hinc, 1e-12)),
                # RENT OVER NON DRUG EXPENDITURE. The frictionless Cobb-Douglas
                # benchmark for it is gam/(1-th), so this is the moment that
                # says whether the discrete housing grid, the street and the
                # voucher deliver the survey share the weight was set from. It
                # is what h_lg is calibrated on.
                hspend=float(hcost / max(hexp, 1e-12)),
                cost=float(cost),
                use=use, v=(PR * frac * VV).sum(axis=1) / np.maximum(use, 1e-12))


def vsl(par, y=1.0, policy=None):
    """
    The value of a statistical life, in multiples of average ANNUAL income.

    A household at income y in period 1 would pay, in period 1 consumption, an
    amount beta * E_{d'}[(1 - kap d') W2] for a marginal increase in phi0, its
    probability of surviving into period 2. That is the standard VSL: the
    marginal rate of substitution between consumption and mortality risk. It
    comes out in units of one PERIOD's mean income, so it is multiplied by the
    number of years in a period to put it in the annual units the empirical
    estimates use.

    This is what pins aleph. Raising aleph raises every continuation value and
    therefore the willingness to pay for survival, one for one.
    """
    policy = policy or par.policy
    ag, W2c, _, _, _ = solve_period2(par, y, policy, used=0)
    W2u = W2c if policy == 'HF' else solve_period2(par, y, policy, used=1)[1]
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
    tot = 0.0
    for p, inc, rmul in _states(par, 0, policy, y, used=0):
        if p <= 1e-14:
            continue
        vg = np.concatenate(([0.0], np.linspace(1e-4, 0.5 * inc, par.nv - 1)))
        pid = (1.0 - np.exp(-par.lam * vg))[:, None]
        cont = (1.0 - pid) * s0 * W2u[None, :, 0] + pid * s1 * W2u[None, :, 1]
        rm = _p1_rmul(par, policy, rmul)
        val, aa, _, rr, _ = _branch(par, ag, inc, rm, vg, cont)
        cont0 = np.repeat((s0 * W2c[:, 0])[None, :], 2, axis=0)
        v0, a0, _, r0, _ = _branch(par, ag, inc, rmul, np.zeros(2), cont0)
        tot_v = (val + par.th * (np.log(par.b + vg) - np.log(par.b))
                 - par.omega * par.chdmg * (1.0 - np.exp(-par.lam * vg)))
        k = int(np.argmax(tot_v[1:])) + 1
        if tot_v[k] > v0[0]:
            a, rent, pi = aa[k], rr[k], float(1.0 - np.exp(-par.lam * vg[k]))
            c1 = inc - rent - par.p_v * vg[k] - a
        else:
            a, rent, pi = a0[0], r0[0], 0.0
            c1 = inc - rent - a
        i2 = int(np.argmin(np.abs(ag - a)))
        # d(objective)/d(phi0), which is the continuation per unit of survival
        ew = (1.0 - pi) * W2c[i2, 0] + pi * (1.0 - par.kap) * W2u[i2, 1]
        u_c = (1.0 - par.gam - par.th) / max(c1, 1e-12)
        tot += p * par.beta * ew / u_c * par.years
    return float(tot)
