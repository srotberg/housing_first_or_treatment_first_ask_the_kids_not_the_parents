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

import math
import numpy as np


class P:
    # preferences
    # SHARES THAT SUM TO ONE. The weight on consumption is 1-gam-th, so gam is
    # the housing budget share proper rather than gam/(1+gam+th). gam is set to
    # 0.268 of non drug spending, which is the share in the data.
    # THETA IS 0.20 AND NOT 0.11, and the two period model is what allows it. In
    # the three period model raising theta bought a drug spending share at the
    # cost of the income gradient: users stopped being poor. Here the mortality
    # channel is strong enough to hold the gradient while theta rises.
    #
    # THE SIX POINT SCREEN BELOW IS SUPERSEDED and is kept only as a record of
    # how far the answer moved when sigma_y was calibrated. It was run at
    # sigma_y = 0.75, a guess, and with lambda targeting the 33.2 per cent
    # conversion from use to a SUD rather than the 3.68 per cent adult rate the
    # quantitative model matches. Both were replaced, and under the new income
    # distribution the spending shares are three times larger at every theta and
    # the mortality screen fails a full point earlier. The current numbers are in
    # the block above this class attribute.
    #
    # THE CEILING MOVED WHEN THE SMR DID. With kappa derived from an SMR of 8
    # rather than 6.9 the mortality channel is stronger, so it holds the gradient
    # further. The six point screen, all at the same 5.13 per cent participation
    # rate and each fully recalibrated:
    #
    #   theta   spending    r_mort   passes
    #   0.20      3.80 %     0.187    yes
    #   0.22      6.18 %     0.161    yes
    #   0.23      6.32 %     0.449    yes
    #   0.24      4.35 %     0.967    yes, with no margin at all
    #   0.25     19.81 %     3.519    NO
    #   0.28     29.70 %     2.820    NO
    #
    # r_mort is the income gradient among users with the mortality channel alone
    # at full strength, and it has to be BELOW ONE or the model no longer says
    # what it exists to say: that mortality is what makes the poor the users.
    #
    # So 0.25 is not available, and that matters because 0.25 is where the
    # spending share finally gets near the data's 11 per cent. The 19.81 per cent
    # there is not a better calibration, it is a different regime: r_mort of 3.5
    # means the mortality channel now puts USE AT THE TOP of the income
    # distribution, and the headline result is gone.
    #
    # 0.23 is chosen. It is the largest spending share among the points that
    # pass, and it keeps real margin below one, unlike 0.24 which passes at 0.967
    # with none. The share is 6.32 per cent against 11 in the data, so the gap is
    # narrowed and not closed, and the note says so rather than claiming a fit.
    #
    # The share is NOT monotone in theta between 0.22 and 0.24, which is worth
    # knowing before anyone reads a small difference as signal: b rises smoothly
    # across the whole range, so the dip at 0.24 is the four sweep calibration
    # struggling near the boundary rather than a feature of the model.
    #
    # See scan_theta.py, which screens the channel decomposition before it reads
    # the spending share.
    # THETA = 0.21, AND THE SECOND ROW OF THIS TABLE IS WHY. Scanning theta with
    # the WHOLE model recalibrated at each point (frontier.py), the drug spending
    # share of users and what the mortality channel does on its own are:
    #
    #     theta   0.18    0.20    0.21    0.22    0.23
    #     share  15.2%   18.4%   20.2%   21.6%   24.2%
    #     r_mort  0.15    0.15    0.39    0.93    1.90
    #
    # r_mort is the average income of users over the population average when the
    # mortality channel alone is switched on at full strength. Below one, users
    # are poorer than average and mortality has reversed the income gradient by
    # itself, which is the mechanism this model exists to show. It crosses one
    # between 0.22 and 0.23, so 0.23 buys a 24 per cent spending share and loses
    # the reversal. 0.20 is the setting: a round number, a spending share of 18.4
    # per cent, and a mortality channel that drives users to a sixth of average
    # income on its own rather than to the 0.39 that 0.21 gives. The extra two
    # points of spending that 0.21 would buy are not worth the margin.
    # THETA IS SET AT 0.2334 AND NOT CALIBRATED, and the reason is a trade the
    # model cannot avoid rather than a choice about fit.
    #
    # Bracketing theta on a 20 per cent drug spending share does not converge,
    # because the share is DISCONTINUOUS in theta: it climbs to about 18.9 per
    # cent, jumps to about 29, and 20 falls in the gap. A bisection aimed into
    # that gap narrows onto the jump and reports whichever side it last
    # evaluated, which is what five sweeps of it did -- theta walked 0.197,
    # 0.206, 0.222, 0.233, 0.243, 0.249, 0.254, crossed the jump and stayed on
    # the far branch with the moment 41 per cent off.
    #
    # THE BINDING CONSTRAINT IS NOT THE GAP, IT IS THE MECHANISM. r_mort, the
    # income ratio among users with the mortality channel alone at full
    # strength, has to stay BELOW ONE or the paper no longer says that mortality
    # is what makes the poor the users. Measured at fully recalibrated points:
    #
    #   theta    dshare   r_mort
    #   0.2334    ~18%     0.322   holds, with room
    #   0.2429   18.22%    0.837   holds, barely
    #   0.2494   18.63%    1.285   FAILS
    #
    # THETA IS SET AT 0.2350, and both the value and the reason changed when the
    # data behind the target was rebuilt.
    #
    # The spending share cannot be BRACKETED on: it is discontinuous in theta,
    # climbing to about 19 per cent and jumping to 29, so a bisection aimed into
    # that gap narrows onto the jump. It is set instead, at the theta whose
    # share matches the data, and the share is reported as an untargeted moment.
    #
    # WHAT CHANGED. The target was 20 per cent, built by dividing 2016 spending
    # by 2024 PERSONAL income, and reaching it cost more theta than the
    # mortality channel could carry: r_mort, the income ratio among users with
    # mortality alone at full strength, crossed one at about theta 0.245 while
    # the share was still under 19. Correcting the target to 16.2 -- family
    # income, since that is what this model's budget constraint spends, and both
    # sides in one year's dollars -- and correcting the population rates to the
    # model's own 26-and-over universe moved the target down to meet the model
    # rather than the other way round. See data/make_drug_spending_target.py.
    #
    # MEASURED AT 0.2350, with lambda and b refit: a spending share of 16.32 per
    # cent against a target of 16.20, users at 0.218 of average income, and
    # r_mort at 0.330. r_mort runs 0.315 to 0.331 over theta 0.220 to 0.238, so
    # this sits on a plateau rather than near an edge: the mechanism is not
    # merely below its threshold of one, it is vivid.
    th    = 0.2350    # weight on drug use, SET; see above
    b     = 0.009     # Stone Geary subsistence; th/b is the pull of the first unit
    gam   = 0.2144    # CALIBRATED to the housing share. Starting value only
    # SIGMA IS 2 AND THE NESTING IS THE QUANTITATIVE MODEL'S, on the author's
    # instruction of 12 September: *"let's use sigma=2 to match the quant
    # model"*.  risk_aversion_consumption is a hard parameter there
    # (housing_first_or_treatment_first_SR_v1.f90:2785) and the three
    # Cobb-Douglas weights are built at :39177-39181 as
    #
    #     phi_h = gam*(1-th)     phi_c = (1-gam)*(1-th)     phi_q = th
    #
    # so gam is the housing share of the NON-DRUG bundle, which is exactly what
    # its target -- 26.8 per cent of expenditure net of drugs -- measures.  The
    # old weights here were (1-gam-th), gam, th, a different nesting under which
    # gam was the share of the whole bundle and the housing share of non-drug
    # spending was gam/(1-th).
    #
    # LOG WAS ASKED FOR AND MEASURED DOWN.  Under sigma = 1 the child's bundle
    # differs from the parent's only by the constant bbar^phi_q, so the pair
    # collapses to the omega_c = 0 model at theta/A and aleph/A with
    # A = 1 + omega_c*(xi-1): the contemporaneous child term is a
    # reparameterisation of two CALIBRATED parameters and its ablation row is
    # empty by construction.  omega_c_under_log.py measures it -- the drug
    # quantity ratio is flat at 1.0056 across a 25-fold range of income under
    # log and swings 1.0138 to 0.9838, crossing one, at sigma = 2.  There are no
    # derivatives anywhere in this file to trade against that: every choice is a
    # grid argmax.
    sigma = 2.0
    # THE EQUIVALENCE SCALE, xi = sqrt(household size), and a stylized household
    # is a parent and one child through period 1, so xi = sqrt(2) there and 1 in
    # period 2, where the child has grown.  That is the quantitative model's own
    # age profile collapsed to two periods: actual_household_size = 1 + n(a) with
    # n from children under 18 by age.  kappa_child = xi - 1 is settled --
    # CHILD_FLOW_UTILITY.md, approved 11 September.
    xi    = 2.0 ** 0.5
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
    # ZERO INTEREST ON SAVING, author 12 September: *"i suppose we can assume
    # that savings get 0 interest instead of negative interest"*, *"what you save
    # is just kept for the next period with no interest"*.  R was 1/0.995^30 =
    # 1.1621, a POSITIVE thirty-year return; at R = 1 a unit saved is a unit
    # carried, and beta alone drives saving.
    #
    # NOTE THE DIRECTION.  The author expected beta to come out LOWER.  Removing
    # a positive return makes saving less attractive, so beta has to work HARDER
    # for the same stock and should come out HIGHER.  Measured rather than
    # argued: see the run in the commit that made this change.
    R     = 1.0
    years = 30.0      # years in a period, used to put the VSL in annual units
    phi0  = 0.91      # survival over one period, clean: ages 26 to 55, SSA
    # THE SOURCE AND THE AGES BOTH SAID SOMETHING THE PACKAGE DOES NOT HOLD.
    # This read 'ages 25 to 55, CDC'. The table in data/ is the SSA period
    # life table 4.C6 and it starts at 26, so there is no 25 to read and no
    # CDC table behind it. Thirty years of exposure from 26 means surviving
    # ages 26 through 55, which the packaged table puts at 0.9199 rather than
    # 0.91; the gap is carried over from the source this used to name and is
    # flagged in the note rather than changed here, because moving it moves
    # every number in the stylized section.
    # SET SO THAT NO HOUSEHOLD HAS A NEGATIVE VALUE OF LIFE. When the poorest
    # household's continuation goes below zero, dying is worth more than living
    # and it then WANTS the extra mortality the disorder brings, which inverts
    # the mechanism. It is calibrated to the value of a statistical life, and
    # the level it needs is higher here than in the three period version because
    # one period of continuation has to deliver the whole of it.
    aleph = 4.00      # flow value of being alive. CALIBRATED

    # the disorder
    lam   = 25.0      # RETIRED. Kept so ablate.py and frontier.py still import,
                      # and so a robustness run can put the quantity back.
    # THE ONSET IS FLAT AND CONDITIONAL ON USING, author 12 September: *"there is
    # only a flat SUD risk when using that is independent of use"*.  This is
    # exactly the quantitative model's addiction_onset_hazard at
    # lambda_addiction = 0 (:9713-9734): the base rate if v > 0 and precisely
    # zero if v = 0, so abstainers stay clean.
    #
    # IT COSTS THE INTENSIVE-MARGIN MORAL HAZARD AND BUYS IDENTIFICATION.
    # d pi/d v is now zero, so TWO_PERIOD_SPEC.md's stated reason for two periods
    # -- *"the marginal cost of using is lambda*exp(-lambda v)*dV"* -- no longer
    # holds, and the whole mortality cost sits on the discrete decision to use at
    # all.  In exchange theta alone sets how much is used and pi_base alone sets
    # the disorder rate, where before they were jointly determined.
    pi_base = 0.40    # CALIBRATED to the disorder rate. Starting value only
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
    # RAISED FROM 6.9 TO 8.0 so the two models use the same number. The full
    # model calibrates kappa_phi_d externally at the MIDPOINT of the six to ten
    # range Hjorthoj et al. (2023) report, and citing the same source for the
    # same object while carrying two different values is exactly the
    # inconsistency the AE's letter objects to. kap is DERIVED from it, not set
    # to it: an annual ratio does not transfer to a thirty year period, so the
    # ON THE HAZARD, as in the quantitative model. smr_d is a ratio of RATES, so
    # it belongs on the hazard rather than on the death probability, and then the
    # compounding collapses: annual survival with the disorder is p**smr_d, so
    # over the thirty years of a period it is phi0**smr_d, and
    #
    #     kap = 1 - phi0**smr_d / phi0 = 1 - phi0**(smr_d - 1).
    #
    # The old form multiplied the annual death PROBABILITY by smr_d and
    # compounded that. The two agree while the annual hazard is small and this
    # one is: 0.4876 against 0.4832, nine tenths of a per cent apart. The change
    # is made for consistency with the full model rather than because it moves
    # anything here.
    # KAPPA IS CALIBRATED ON THE INCOME OF USERS, author 12 September: *"i think
    # you should also calibrate kappa so that the average income of a user is
    # 0.74"*.  0.74 is the quantitative model's own y_u target, users' mean
    # income over the population mean, from Table 7.  smr_d and the construction
    # below are kept as the STARTING VALUE and as the record of where the
    # mortality ratio came from when it was set rather than calibrated; the
    # implied SMR of whatever kap the bracket lands on is reported beside it, so
    # the calibrated mortality can be read against the literature.
    #
    # THE GRADIENT IS A TARGET IN THE BASELINE AND THAT IS DELIBERATE.  The
    # baseline matches the data on all seven moments, y_u among them, and the
    # ablations below are what decompose the reversal.  So the claim this model
    # supports is "at the mortality the data imply, channel X carries this much
    # of the gradient", not "the model produces the gradient unprompted".
    smr_d = 3.0       # the quantitative model's kappa_phi_d_level, for the start
    kap   = 1.0 - 0.91 ** (smr_d - 1.0)
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
    # THE GRID IS SET AND GAMMA IS CALIBRATED, which is the conventional order and
    # the third arrangement tried here. The two before it are worth recording.
    #
    #   BOTH SET. gamma from the expenditure survey and h_lg from an SCF housing
    #   cost to income ratio. Two external numbers aimed at one object with
    #   nothing making them agree: the model delivered a 16 per cent housing
    #   share against the survey's 26.8.
    #
    #   h_lg CALIBRATED ON THE SHARE. It hits 26.8 exactly and puts homelessness
    #   at 3.2 per cent against a target of 0.399, because the aggregate share is
    #   bounded above by h_lg and matching it needs a unit so large that the
    #   small unit prices the bottom of the distribution out of housing
    #   altogether. See the frontier below.
    #
    # So the sizes are SET and stated to the reader, and gamma is bracketed on
    # the housing share instead. That is the ordinary way round: the grid is a
    # market fact, the weight is a preference, and preferences are what a model
    # is entitled to infer. Reading it backwards recovers the same object, since
    # a gamma and a grid that reproduce the share are two descriptions of one
    # calibration.
    #
    # THE SMALL UNIT IS A QUARTER OF THE STANDARD ONE because it is the
    # affordability floor: a household whose cash falls below its rent has no
    # housed option at all and is homeless BY FORCE, which no value of h_hl
    # undoes. At a half the floor is high enough that forced homelessness alone
    # exceeds the 0.399 per cent target and the h_hl bracket loses its interior
    # solution. At a quarter, with h_lg at 0.40, the floor is 0.10 and h_hl does
    # the work it is supposed to do.
    #
    # The frontier, measured with h_sm = h_lg/2 and h_hl refitted at every point,
    # which is what rules out calibrating h_lg on the share:
    #
    #     h_lg    h_sm     h_hl     housing share   homelessness
    #     0.212   0.106   4.2e-04       0.163          0.00395
    #     0.240   0.120   7.7e-05       0.177          0.00593
    #     0.270   0.135   1.0e-07       0.195          0.00594
    #     0.340   0.170   1.0e-07       0.231          0.01091
    #     0.450   0.225   1.0e-07       0.267          0.03160
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
    h_lg  = 0.40      # SET: the standard unit, 40 per cent of mean income
    h_sm  = 0.10      # CALIBRATED, on the share of the housed in the small
                      # unit. This is the class default and calibrated.json
                      # overrides it; the comment said SET, which it has not
                      # been since the share became its moment.
    h_hl  = 0.05      # the street. CALIBRATED to the homelessness rate
    pr    = 1.00      # rent per unit of housing services: the numeraire
    # RATIONED TREATMENT FIRST reallocates the vouchers it withholds.  The
    # author, 12 September: *"Rationed tf means that only the same fraction of
    # eligible households get vouchers but those with Sud or v>0 cannot get a
    # voucher in that period"*.
    #
    # THIS IS NOT THE SAME POLICY AS 'TF'.  Under TF a household that fails the
    # sobriety condition loses its voucher and the voucher goes UNISSUED, so
    # total coverage falls and the programme spends less.  Under rationed TF the
    # SUPPLY is fixed: the same fraction of eligible households is housed, and
    # the vouchers freed by excluding users are handed to eligible non-users, so
    # coverage among the clean RISES.  That difference is the whole reason the
    # transition question is interesting -- some children gain a roof precisely
    # because other children's parents lost one.
    #
    # pv_scale is that reallocation factor and it is an EQUILIBRIUM OBJECT, not
    # a parameter: how many vouchers are freed depends on how many households
    # use, which depends on the voucher.  solve_pv_scale below finds its fixed
    # point.  At 1.0 the policy is ordinary TF.
    pv_scale = 1.0
    pV    = 0.266     # probability a voucher arrives, conditional on eligibility.
                      # HUD 2023, recipients over the income eligible population,
                      # the same 26.6 per cent the quantitative model targets. It
                      # was 0.27, the same number rounded differently.
    kV    = 0.50      # MEANS TEST, the share of MEDIAN income below which a
                      # household is eligible. This is the quantitative model's
                      # kappa_V and the paper uses the same symbol for both.
    yV    = 0.3061    # the level kV implies, kV times median income. It has moved
                      # twice with the grid: 0.2591 at 30 log spaced nodes, 0.2477
                      # at 120, and 0.3172 once the nodes were placed by quantile
                      # and the top tail stopped being truncated. The last move is
                      # the one that matters: the median is now 0.634 of the mean
                      # against 0.518 before, and roughly 0.65 in the data, so the
                      # means test is no longer tighter than HUD's rule. Eligible
                      # if current income is below HALF OF
                      # MEDIAN INCOME, which is the HUD rule the quantitative
                      # model uses. It was one times the MEAN, which is a
                      # different rule and a far looser one: the mean of this
                      # lognormal is 1 by construction and its median is
                      # exp(-sigma^2/2) = 0.518, so half of median is 0.2591.
                      # calibrate.py asserts that this equals 0.5*exp(-SIG^2/2),
                      # so it cannot drift away from SIG unnoticed.
    kappa_r = 0.30    # tenant's share of the rent when covered
    # THE CLAWBACK. The tenant's share of the rent when the household carries the
    # disorder, on the author's question of 10 September: *"instead of giving a
    # voucher up to 30% of income you can say that if you have sud it covers only
    # up to 50%"*.
    #
    # It makes conditionality a ONE PARAMETER FAMILY with both policies as
    # endpoints, rather than a switch:
    #
    #     kappa_c = kappa_r = 0.30   no penalty at all, identical to Housing First
    #     kappa_c = 1.00             the whole voucher withdrawn, identical to
    #                                Treatment First, which is why it defaults here
    #     in between                 a graduated clawback
    #
    # The point of it is that Treatment First's implicit penalty is the VALUE OF
    # THE VOUCHER rather than the value of the externality, so nothing sets its
    # strength to the damage it corrects. kappa_c can be set to the damage.
    kappa_c = 1.00
    policy = 'HF'

    p_v   = 1.0       # price of drugs

    # PARTIAL INTERNALISATION OF THE CHILD. Both are zero in the baseline, which
    # is what makes the damage to the child a pure externality. Set omega > 0
    # and the parent subtracts omega * chdmg * pi(v) from its objective, where
    # chdmg is the child's expected loss in lifetime utility from being born to
    # a parent who acquired the disorder. It depends only on v, so it acts as an
    # extra deterrent that rises with use, which is the right economics: a
    # parent who cares about the child uses less. See internalise.py.
    # OMEGA IS THE QUANTITATIVE MODEL'S weight_on_child, 0.09, and it is SET
    # rather than calibrated here: the ablation of omega_c is the experiment, and
    # an omega_c fitted inside this model would not be the one the quantitative
    # model carries.  It now acts in TWO places, as it does there:
    #
    #   the FLOW, through the child's own bundle X_K -- see _flow below;
    #   the CONTINUATION, through chdmg, the child's expected loss.
    #
    # chdmg stays zero until the child's value function is built with delta_d on
    # the SUD odds ratio of 2, which the author has asked for and which follows
    # the same order the quantitative model took: *"delta_d can be done later
    # again"*.
    omega = 0.09
    chdmg = 0.0

    # THE CHILD'S OWN INCOME, so delta_d has something to act on.  Author, 12
    # September: *"i want you to add rho=0.35 in the model like we have in the
    # quant model, and show me the odds ratio for homeless and pick delta_d to
    # match the odds ratio of the SUD"*, then *"where is delta_d?"*.
    #
    # Until now the child was a utility TERM and not an agent, so there was no
    # child SUD rate and no odds ratio to match.  It now inherits income:
    #
    #     log y_child = rho*log y_parent + (1-rho)*log ybar - delta_d * 1{parent
    #                   acquired the disorder}
    #
    # which is the quantitative model's rho_intergenerational (0.30 there) with
    # penalty_child_addicted as the shift.  delta_d is in LOG INCOME, so 0.36 --
    # the value the Fortran is pinned at -- is a 30 per cent income penalty.
    # RHO IS 0.5, THE UPPER END OF THE LITERATURE, ON THE AUTHOR'S INSTRUCTION
    # OF 13 SEPTEMBER: *"we can even set rho=0.5 to be at the upper end of the
    # literature so that delta_d is the lowest."*  It was 0.35, the quantitative
    # model's rho_intergenerational of 0.30 rounded up.
    #
    # WHY THE UPPER END HELPS.  delta_d is calibrated on the child's SUD odds
    # ratio of 2.  Income persistence and the penalty are two ways of getting a
    # child of a disordered parent to a low income, so the more of the odds
    # ratio rho delivers on its own, the less delta_d has to.  Choosing rho at
    # the top of the defensible range therefore makes the penalty the SMALLEST
    # the model can get away with, which is the conservative direction for
    # every result that runs through it.
    #
    # IT ALSO NARROWS THE CHILD'S OWN SPREAD, and that is the cost.  The
    # stationary shock is eps ~ N(0, (1-rho^2) sigma^2), so at rho = 0.5 the
    # innovation carries sqrt(0.75) = 0.866 of the parents' dispersion against
    # sqrt(0.8775) = 0.937 at 0.35.  The cross-section variance is unchanged by
    # construction; what changes is how much of a child's position is its
    # parent's.  See _child_rate for why the shock is not optional.
    rho     = 0.50
    delta_d = 0.36

    na    = 60
    nv    = 140
    y_floor = 0.0     # guaranteed minimum realised income; 0 is off.  See
                      # _states for what it is for and what value clears the
                      # negative value of life.
    v_lo  = 1e-5      # the smallest positive drug purchase, AS A FRACTION OF
                      # INCOME.  See _vgrid for why it is a fraction and why
                      # the grid above it is geometric.


_VGRID_CACHE = {}


def _vgrid(par, inc):
    """The drug quantity grid at income `inc`: abstention, then a geometric
    ladder from v_lo * inc up to half of income.

    IT WAS LINEAR AND THAT PUT A HOLE IN IT.  The grid read

        [0.0] + linspace(1e-4, 0.5 * inc, nv - 1)

    which at mean income gives 0, 0.00010, 0.00372, 0.00734, ...  So between
    SPENDING NOTHING and SPENDING 0.37 PER CENT OF INCOME the only available
    choice was 0.01 per cent: one isolated point, thirty-six times below the
    next rung, with nothing in between.

    THAT HOLE IS THE "CORNER BRANCH".  Every run of this model has alternated
    between an interior equilibrium at a drug share near 0.21 and a "corner" at
    0.0007 -- which is 0.07 per cent of income, i.e. mass sitting in exactly
    that gap, every user pinned on the lone small point because the grid gave
    them nowhere else to go.  It was read as an economic multiplicity for most
    of a day and it is a discretisation artefact.  The evidence that settled it:
    reconstructing the live vector from a printed table, to the five decimals
    the table shows, put the model on the OTHER branch from the run reporting
    it -- the two equilibria are within rounding of each other, which is what a
    grid artefact looks like and not what a genuine multiplicity looks like.

    A LADDER RATHER THAN A RULER.  Geometric spacing puts roughly eight per cent
    between neighbouring rungs everywhere, so the choice set is as well resolved
    at a tenth of a per cent of income as it is at ten per cent, and there is no
    rung that is an order of magnitude away from its neighbour.

    AND A FRACTION OF INCOME RATHER THAN AN ABSOLUTE FLOOR.  1e-4 was the same
    absolute quantity for every household, so the poorest faced a coarser grid
    in proportional terms than the richest -- and the drug, housing and
    homelessness margins all sit at the bottom of the distribution.
    """
    # BUILT ONCE AND SCALED.  geomspace is scale-equivariant --
    # geomspace(a*x, a*y, n) == a * geomspace(x, y, n) to 2e-16 -- so the ladder
    # does not depend on income at all, only the multiplier does.  It was being
    # rebuilt on every state: 1250 geomspace calls a solve at 35.6 us each,
    # against 0.6 us to scale a cached one.  Nine per cent of the solve.
    key = (par.v_lo, par.nv)
    unit = _VGRID_CACHE.get(key)
    if unit is None:
        unit = np.concatenate(([0.0], np.geomspace(par.v_lo, 0.5, par.nv - 1)))
        _VGRID_CACHE[key] = unit
    return unit * inc


def clone(**kw):
    q = P()
    for k, v in kw.items():
        setattr(q, k, v)
    return q


def fields(par):
    return {k: getattr(par, k) for k in dir(par)
            if not k.startswith('_') and not callable(getattr(par, k))}


H_RATIO = 0.25    # the small unit as a fraction of the standard one

# how finely the pooled bottom cell is swept when its use mass is added up


def with_(par, **kw):
    f = fields(par); f.update(kw)
    # THIS TIE IS DORMANT AND IT IS ALSO A TRAP. h_sm is CALIBRATED now, on the
    # share of the housed in the small unit, so a quarter of h_lg is no longer
    # what it is; nothing in the calibration, the tables, the figures or the
    # ablation moves h_lg through with_(), which is the only reason the tie has
    # not already clobbered a calibrated value with a ratio nobody measured. If
    # a diagnostic is ever written that does move h_lg, it has to pass h_sm
    # explicitly or re-bracket it, not inherit the quarter.
    if 'h_lg' in kw and 'h_sm' not in kw:
        f['h_sm'] = H_RATIO * f['h_lg']
    return clone(**f)


# ---------------------------------------------------------------------------
def _states(par, d, policy, y, used=0):
    """
    (probability, income level, tenant's rent multiplier) given d and whether
    the household used drugs in period 1.

    POLICY. Treatment First withdraws the voucher from any household that fails
    the sobriety condition IN THE PERIOD THE VOUCHER IS PAID, which is current
    use or a current disorder. Housing First withdraws it from nobody. That
    single difference is the whole experiment.

    This is called for BOTH periods, and the condition reads differently in each
    because the drug choice does not exist in both.

    In period 1 it is called at d = 0 with used = 0: the voucher is drawn on
    arrival, before v is chosen, so nobody has yet violated anything. The
    condition then bites WITHIN the period through _p1_rmul, which strips the
    voucher from a period 1 household that goes on to choose v > 0.

    IN PERIOD 2 THE CONDITION IS d = 0 AND NOTHING ELSE, because there is no
    period 2 drug choice: v is chosen once, in period 1, so v = 0 in period 2 by
    construction and a sobriety test applied to the current period cannot fail on
    it. A household that used in period 1 and did not acquire the disorder
    arrives in period 2 clean, and a rule that tests the current period must
    cover it. This is also what keeps the stylized model aligned with the
    quantitative one, where revocation is on CURRENT use and a household that
    used a decade ago and is clean today is covered; the earlier rule here
    revoked on a history of use, which is a different and much harsher policy,
    and it made Treatment First look better than the rule the paper describes.
    The `used` argument is kept because both call sites pass it and it documents
    the history at the call, but it no longer enters the condition.
    """
    pu = par.u1 if d == 1 else par.u0
    # THE RENT SHARE A COVERED HOUSEHOLD PAYS, which under a clawback depends on
    # d rather than being all or nothing. At kappa_c = 1 a household with the
    # disorder pays the market rent, the government pays nothing, and this is
    # Treatment First exactly.
    rate = par.kappa_r if ((policy == 'HF') or (d == 0)) else par.kappa_c
    out = []
    for e, pe in ((0, 1.0 - pu), (1, pu)):
        # Lose your job and income support replaces the fraction repl of what
        # you used to earn, on an earnings base capped at ycap. For the poorest
        # household that is well below the rent on the smallest unit, so the
        # disorder can put the roof at risk, which is what the voucher insures.
        inc = y if e == 0 else par.repl * min(y, par.ycap)
        # A FLOOR UNDER REALISED INCOME.  The author, 12 September: *"you need
        # to limit the lowest income from below so no one has negative value of
        # life"*.
        #
        # WHY IT IS NEEDED.  At the calibrated vector 1.43 per cent of period-2
        # states have a NEGATIVE value of life: the cheapest rental costs 0.10
        # and the poorest household earns 0.108, so it either pays the rent and
        # consumes nothing or takes the street at h = 0.0095, and with sigma = 2
        # a tiny bundle sends X^(1-sigma)/(1-sigma) to a large negative number
        # that aleph = 10.62 cannot lift.  A negative continuation makes the
        # mortality penalty a BENEFIT -- multiplying a negative number by a
        # smaller survival probability raises it -- so those households buy the
        # smallest sliver of drug the grid sells purely to acquire the disorder
        # and die sooner.  That is the whole of the "corner branch".
        #
        # MEASURED: the value of life is negative at some asset level for every
        # income below 0.18614, which is 1.86 times the rent on the small unit.
        # A floor at or above that clears it.
        #
        # DEFAULT ZERO, i.e. OFF, so that every existing result is unchanged
        # until the floor is deliberately switched on.  It is a transfer and it
        # moves homelessness, participation and the housing share, so a run with
        # it on is a different calibration and has to be re-run, not compared.
        inc = max(inc, par.y_floor)
        # MEANS TEST. A voucher can only reach a household whose income in that
        # state is below the mean. Every unemployed household passes the test;
        # employed households pass only in the bottom part of the distribution.
        pv = par.pV if (inc <= par.yV) else 0.0
        # RATIONED TF: the clean draw against a LARGER pool, because the
        # vouchers withheld from users are reissued rather than surrendered.
        # Capped at one -- a programme cannot house more than everyone.
        if policy == 'RTF':
            pv = min(pv * par.pv_scale, 1.0)
        for rmul, prb in ((rate, pv), (1.0, 1.0 - pv)):
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
    if policy == 'HF':
        return rmul
    # A household that never drew a voucher pays the market rent either way; one
    # that did keeps it at the clawback rate. At kappa_c = 1 that is the whole
    # voucher withdrawn, which is the original rule.
    if rmul >= 1.0:
        return 1.0
    return par.kappa_c


def _shares(par):
    """
    (phi_c, phi_h, phi_q), the quantitative model's nesting at
    housing_first_or_treatment_first_SR_v1.f90:39177-39181.  They sum to one, so
    gam is the housing share of the non-drug bundle and th the drug share of the
    whole.
    """
    return (1.0 - par.gam) * (1.0 - par.th), par.gam * (1.0 - par.th), par.th


def _pid(par, v):
    """
    The onset hazard.  FLAT AND CONDITIONAL ON USING, which is the quantitative
    model's addiction_onset_hazard at lambda_addiction = 0 (:9713-9734): the base
    rate at any positive quantity and exactly zero at v = 0, so an abstainer is
    never at risk.  d pi / d v is zero everywhere it is defined.
    """
    return par.pi_base * (np.asarray(v, dtype=float) > 0.0)


def _hpick(par, street, small):
    """The housing size behind a (street, small) record from _branch."""
    if street > 0.5:
        return par.h_hl
    return par.h_sm if small > 0.5 else par.h_lg


def _flow(par, c, h, q=0.0, child=True):
    """
    THE FLOW UTILITY, which is the quantitative model's, not a stylized stand-in.

    CHILD_FLOW_UTILITY.md, approved 11 September and built into the Fortran at
    :24317-24327 with aleph added at :24450:

        X_P = (c/xi)^phi_c (h/xi)^phi_h (bbar+q)^phi_q      the parent
        X_K = (c/xi)^phi_c (h/xi)^phi_h  bbar^phi_q         the child
        V   = u(X_P) + omega_c*(xi-1)*u(X_K) + aleph,   u(x) = x^(1-s)/(1-s)

    THE CHILD DOES NOT GET THE DRUG.  Its bundle carries the Stone-Geary shifter
    alone, so buying drugs reaches the child only by taking consumption out of
    the shared c.  That asymmetry is the whole of the contemporaneous channel:
    under log it would collapse into a constant multiple of the parent's bundle
    and vanish into theta and aleph, which is measured in omega_c_under_log.py
    and is why sigma is 2.

    c AND h ARE DIVIDED BY xi, q IS NOT, because children consume none of it.

    ALEPH IS ADDED ONCE, NOT PER MEMBER, matching the Fortran, where
    value_of_life is added to the assembled flow utility rather than inside the
    bracket the child weight multiplies.

    child=False is period 2, where the child has grown: xi is 1 and the second
    term is absent.
    """
    # ALGEBRAICALLY THE SAME, ONE PASS OVER THE BIG ARRAY INSTEAD OF THREE.
    #
    #   S = exp((1-s)(base + phq*log(b+q))) + w*exp((1-s)(base + phq*log(b)))
    #     = exp((1-s)*base) * [ (b+q)^((1-s)phq) + w*b^((1-s)phq) ]
    #
    # and exp((1-s)*base) is just (c/xi)^((1-s)phc) * (h/xi)^((1-s)phh).  The
    # bracket depends on q alone, which is (nv,1), while c is (nv,na): so the
    # child term costs a small array rather than a second full exponential, and
    # the parent's bundle costs ONE power rather than a log and an exp.
    #
    # _flow was 15,530 calls and forty per cent of a solve, on (140,60) arrays.
    phc, phh, phq = _shares(par)
    xi = par.xi if child else 1.0
    kch = (xi - 1.0) if child else 0.0
    s = par.sigma
    e = 1.0 - s
    big = np.maximum(c, 1e-12) / xi
    E = big ** (e * phc) * (float(h) / xi) ** (e * phh)
    bracket = (par.b + q) ** (e * phq)
    if kch > 0.0 and par.omega != 0.0:
        bracket = bracket + par.omega * kch * par.b ** (e * phq)
    return E * bracket / e + par.aleph


def _options(par, rmul):
    """(housing services, rent, on the street) for the three choices."""
    return ((par.h_hl, 0.0, 1),
            (par.h_sm, par.pr * par.h_sm * rmul, 0),
            (par.h_lg, par.pr * par.h_lg * rmul, 0))


def solve_period2(par, y, policy, used=0):
    """
    Period 2, which is terminal: assets are run down and nothing is bequeathed.

    Returns (assets grid, W2, street share, rent paid, voucher outlay, small
    unit share), each indexed by the assets grid and by the disorder d. The last
    is the share choosing the SMALLER of the two rentals, carried the same way
    the street share is: as a probability over the discrete choice, so that
    interpolating it across the assets grid stays a share rather than becoming
    an interpolated SIZE that belongs to neither option. The last of these is the
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
    S2 = np.zeros((par.na, 2))            # chose the small rental, for the size distribution
    for d in (0, 1):
        for p, inc, rmul in _states(par, d, policy, y, used):
            if p <= 1e-14:
                continue
            cash = par.R * ag + inc
            best = np.full(par.na, -np.inf); onst = np.zeros(par.na)
            rnt = np.zeros(par.na); out = np.zeros(par.na)
            sml = np.zeros(par.na)
            for h, rent, street in _options(par, rmul):
                c = cash - rent
                v = np.where(c > 1e-9, _flow(par, c, h, 0.0, child=False),
                             -np.inf)
                # what the voucher pays on this option: the rest of the market
                # rent. Zero on the street, which is free to begin with.
                s = 0.0 if street else par.pr * h * (1.0 - rmul)
                is_small = 0.0 if street else float(h == par.h_sm)
                onst = np.where(v > best, street, onst)
                rnt = np.where(v > best, rent, rnt)
                out = np.where(v > best, s, out)
                sml = np.where(v > best, is_small, sml)
                best = np.maximum(best, v)
            W2[:, d] += p * best; H2[:, d] += p * onst
            R2[:, d] += p * rnt;  G2[:, d] += p * out
            S2[:, d] += p * sml
    return ag, W2, H2, R2, G2, S2


def _branch(par, ag, inc, rmul, vg, cont):
    """
    Period 1, one branch of the drug decision: the value at each v on the grid,
    maximised over housing and saving, with the choice recorded.

    cont is the continuation E_{d'}[phi(d') W2(a',y,d')] on (v, a'), which is
    where the mortality penalty enters, INSIDE the expectation over d'.

    ONE INDEX IS CARRIED, NOT FOUR RECORDS, and the reason is that this function
    was two thirds of a calibration sweep. The option loop used to keep the
    street flag, the rent, the voucher outlay and the small-unit flag as four
    running (nv, na) arrays, updated by four np.where calls per option, so
    twelve full-array writes per call. Only one cell of each is ever read: the
    saving that wins at each v. Carrying the winning option's INDEX instead
    costs one np.where per option and the four records are gathered at the end
    from three-element lookup tables, on the n points that are actually used.

    THE TIE RULE IS UNCHANGED. The comparison is still strict, so an exact tie
    still goes to the EARLIER option, and the dead case still reports a choice
    of zero rather than option zero: where nothing is affordable the value stays
    at minus infinity and the mask below zeroes the record, which is what the
    initialised arrays did.
    """
    n = len(vg)
    cash = (inc - par.p_v * vg[:, None]) - ag[None, :]
    opts = _options(par, rmul)
    val = np.full(cash.shape, -np.inf)
    idx = np.zeros(cash.shape, dtype=np.intp)
    for o, (h, rent, street) in enumerate(opts):
        c = cash - rent
        # THE DRUG IS INSIDE THE BUNDLE NOW.  Under log it was additively
        # separable and period1 added it after the fact; at sigma = 2 it
        # multiplies, so it has to be here, where housing and saving are chosen
        # against it.
        u = np.where(c > 1e-9,
                     _flow(par, c, h, vg[:, None]) + par.beta * cont,
                     -np.inf)
        better = u > val
        idx = np.where(better, o, idx)
        val = np.where(better, u, val)

    h_o = np.array([h for h, _, _ in opts])
    rent_o = np.array([r for _, r, _ in opts])
    st_o = np.array([float(s) for _, _, s in opts])
    sb_o = np.where(st_o > 0.0, 0.0, par.pr * h_o * (1.0 - rmul))
    sm_o = np.where(st_o > 0.0, 0.0, (h_o == par.h_sm).astype(float))

    ia = np.argmax(val, axis=1)
    k = np.arange(n)
    best = val[k, ia]
    jj = idx[k, ia]
    live = np.isfinite(best)
    return (best, ag[ia],
            np.where(live, st_o[jj], 0.0),
            np.where(live, rent_o[jj], 0.0),
            np.where(live, sb_o[jj], 0.0),
            np.where(live, sm_o[jj], 0.0))


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
    ag, W2c, _, _, _, _ = solve_period2(par, y, policy, used=0)
    W2u = W2c if policy == 'HF' else solve_period2(par, y, policy, used=1)[1]
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
    cont0 = (s0 * W2c[:, 0])[None, :]

    out = []
    for p, inc, rmul in _states(par, 0, policy, y, used=0):
        vg = _vgrid(par, inc)
        pid = _pid(par, vg)[:, None]
        # SURVIVAL INSIDE THE EXPECTATION over the realised disorder. Not
        # phi * E W2: see the note at the head of this file.
        cont = (1.0 - pid) * s0 * W2u[None, :, 0] + pid * s1 * W2u[None, :, 1]
        vu, au, su, ru, gu, mu_ = _branch(par, ag, inc, _p1_rmul(par, policy, rmul),
                                     vg, cont)
        # v = 0 is solved on its own, because the household still holds the
        # voucher it drew and faces the clean continuation.
        v0, a0, s_0, r0, g0, m0_ = _branch(par, ag, inc, rmul, np.zeros(1), cont0)

        # The drug term is no longer added here: _branch carries it inside the
        # bundle.  pen is the CONTINUATION half of omega_c, the child's expected
        # loss, and is flat in v now that the hazard is.
        pen = par.omega * par.chdmg * _pid(par, vg)
        tot = vu - pen
        k = int(np.argmax(tot[1:])) + 1
        gain = float(tot[k] - v0[0])
        # V1 is the PARENT'S OWN lifetime value, which is what a planner counts
        # once and separately from the child's. The internalised term is added
        # back so that raising omega changes behaviour without double counting
        # the child.
        own = float(tot[k] + pen[k]) if gain > 0.0 else float(v0[0])
        out.append((p, gain, float(vg[k]),
                    (float(au[k]), float(su[k]), float(ru[k]), float(gu[k]),
                     float(mu_[k])),
                    (float(a0[0]), float(s_0[0]), float(r0[0]), float(g0[0]),
                     float(m0_[0])),
                    float(inc), own))
    return out


def _child_rate(par, ly, lb, w, ygrid, prob, shift):
    """
    Average a per-income probability over the CHILD's income distribution.

    THE SHOCK IS NOT OPTIONAL AND ITS ABSENCE WAS A REAL BUG.  A deterministic
    map, log y_c = rho*log y_p + (1-rho)*log ybar, collapses the child
    distribution to variance rho^2 * sigma^2 -- at rho = 0.35 that is an eighth
    of the parents' spread.  Almost no child was then poor enough to be
    homeless, so the homelessness odds ratio came out 0.000, and every child had
    nearly the same income, so the SUD odds ratio came out 0.9919 when its
    target is 2.  Both were degenerate rather than informative.
    
    The shock that keeps the cross-section stationary is eps ~ N(0, (1-rho^2)
    sigma^2), which is the standard AR(1) condition: then the child distribution
    has the SAME variance as the parents' and the odds ratios mean something.
    """
    import calibrate as _C
    sd = math.sqrt(max(1.0 - par.rho ** 2, 1e-12)) * _C.SIG
    mu = par.rho * ly + (1.0 - par.rho) * lb - shift
    lg = np.log(np.maximum(ygrid, 1e-12))
    # a lognormal kernel on the grid, per parent node, normalised across nodes
    k = np.exp(-0.5 * ((lg[None, :] - mu[:, None]) / sd) ** 2)
    k /= np.maximum(k.sum(axis=1, keepdims=True), 1e-300)
    return float((w * (k * prob[None, :]).sum(axis=1)).sum() / w.sum())


def child_sud_odds_ratio(par, ygrid, w, policy=None):
    """
    The odds ratio the author wants delta_d set on: a child's chance of the
    disorder when its parent acquired one, over the same chance when the parent
    did not.  Target 2.0, as in the quantitative model's child_sud_ratio_data.

    HOW THE CHILD GETS A CHANCE AT ALL.  It inherits income by rho and then
    faces the SAME period 1 decision this model already solves, so its disorder
    probability is use_prob at its own income times the onset rate.  Nothing new
    is assumed about the child; it is simply run through the model as an adult.

    delta_d SHIFTS ONLY THE SUD BRANCH, which is what makes the ratio respond to
    it: a clean parent's child is placed at rho*log y + (1-rho)*log ybar, a SUD
    parent's child at the same less delta_d.
    """
    ybar = float((w * ygrid).sum() / w.sum())
    ly, lb = np.log(np.maximum(ygrid, 1e-12)), np.log(max(ybar, 1e-12))
    use = np.array([use_prob(par, float(y), policy) for y in ygrid])

    def rate(shift):
        return _child_rate(par, ly, lb, w, ygrid, use, shift) * par.pi_base

    clean, sud = rate(0.0), rate(par.delta_d)
    return sud / max(clean, 1e-12)


def child_homeless_odds_ratio(par, ygrid, w, policy=None):
    """
    The same construction on HOMELESSNESS rather than the disorder.

    REPORTED, NEVER TARGETED.  delta_h is dropped -- the author, 12 September:
    *"we are not calibrating delta_h...that one is dropped"* -- which matches
    ENGINE.md's phase 3 already: delta_h = 0, the homelessness odds ratio is an
    OUTPUT, anywhere in 1.8 to 2.4 is fine, and only below 1.8 is delta_h
    reconsidered.  So this exists to be READ, and nothing is aimed at it.

    It carries delta_d, not a delta_h of its own: the child of a parent who
    acquired the disorder is poorer by delta_d, and being poorer is what makes
    it more likely to be homeless.  That is the whole channel.
    """
    ybar = float((w * ygrid).sum() / w.sum())
    ly, lb = np.log(np.maximum(ygrid, 1e-12)), np.log(max(ybar, 1e-12))
    hl = np.array([homeless_prob(par, float(y), policy) for y in ygrid])

    def rate(shift):
        return _child_rate(par, ly, lb, w, ygrid, hl, shift)

    clean, sud = rate(0.0), rate(par.delta_d)
    return sud / max(clean, 1e-12)


def use_prob(par, y, policy=None):
    """The probability a household at income y uses, over its period 1 draws."""
    return float(sum(p for p, g, *_ in period1(par, y, policy) if g > 0.0))


def homeless_prob(par, y, policy=None):
    """
    The probability a household at income y is on the street, over its period 1
    draws.

    The branch a draw lands in depends on whether it uses, so the two branches
    are weighted by that: bu is what it does if it uses and bn if it does not,
    and g > 0 says which. street is the third element of neither: the branch is
    (a', street, rent, voucher outlay), so street is index 1.
    """
    tot = 0.0
    for p, g, _v, bu, bn, *_ in period1(par, y, policy):
        tot += p * ((bu if g > 0.0 else bn)[1])
    return float(tot)


def terminal_homeless_prob(par, y, policy=None):
    """
    The probability a household at income y is on the street IN PERIOD 2, which
    is the period it dies in.

    THIS IS WHAT THE CHILD'S PENALTY KEYS ON, and getting it wrong in either
    direction breaks something. Keyed on PERIOD 1 alone, conditionality's own
    revocations could never reach a child, because the voucher is withdrawn at
    the transition into period 2. Keyed on EITHER period, which is what it used
    to be, a parent who was unhoused before the reform transmits a penalty even
    when the new programme housed it for the whole of its second period: under
    universal Housing First the initial old are housed when they die, and their
    children were still being born behind a penalty picked up under the old
    rationed programme years earlier.

    Period 2 is the right one on both counts. It is when the household dies,
    which is what equation (11) says the penalty is keyed on, and it is when
    conditionality acts, so a revocation reaches the child exactly as it should.
    """
    policy = policy or par.policy
    ag, W2c, H2c, _, _, _ = solve_period2(par, y, policy, used=0)
    if policy == 'HF':
        H2u = H2c
    else:
        _, _, H2u, _, _, _ = solve_period2(par, y, policy, used=1)
    tot = 0.0
    for p, g, v, bu, bn, *_ in period1(par, y, policy):
        uses = g > 0.0
        a = (bu if uses else bn)[0]
        pid = float(_pid(par, v)) if uses else 0.0
        Hx = H2u if uses else H2c
        tot += p * sum(pd * float(np.interp(a, ag, Hx[:, d]))
                       for d, pd in ((1, pid), (0, 1.0 - pid)))
    return float(tot)


def ever_homeless_prob(par, y, policy=None):
    """The probability a household at income y is on the street in EITHER period.

    THE CHILD'S PENALTY DOES NOT USE THIS. It keys on period 2 alone, which is
    the period the household dies in; see terminal_homeless_prob above for why
    either-period was tried and rejected. This is kept as a diagnostic, and
    verify.py asserts it is never below either single period.

    WHY IT WAS WRITTEN. The inherited penalty
    used to key on period 1 homelessness alone, on the grounds that period 1 is
    where the household's own draws are realised. For drug use that is right,
    since v is only chosen in period 1. For homelessness it is not: a household
    can lose its roof in either period, and under Treatment First the households
    that lose it are precisely the ones whose voucher is withdrawn AFTER they
    acquire the disorder, which happens at the transition into period 2. Keyed
    on period 1 alone, the homelessness that conditionality itself causes could
    never reach a child, so the channel was switched off by a timing assumption
    rather than by economics.

    The two periods are not independent, so this is computed along paths rather
    than as one minus the product of two survival probabilities: for each period
    1 draw, the household's saving and realised disorder determine the period 2
    branch it faces, and the street indicator is read there.
    """
    policy = policy or par.policy
    ag, W2c, H2c, _, _, _ = solve_period2(par, y, policy, used=0)
    if policy == 'HF':
        H2u = H2c
    else:
        _, _, H2u, _, _, _ = solve_period2(par, y, policy, used=1)
    tot = 0.0
    for p, g, v, bu, bn, *_ in period1(par, y, policy):
        uses = g > 0.0
        a, street1 = (bu if uses else bn)[0], (bu if uses else bn)[1]
        pid = float(_pid(par, v)) if uses else 0.0
        Hx = H2u if uses else H2c
        street2 = sum(pd * float(np.interp(a, ag, Hx[:, d]))
                      for d, pd in ((1, pid), (0, 1.0 - pid)))
        # homeless in period 1 OR period 2, along this path
        tot += p * (street1 + (1.0 - street1) * street2)
    return float(tot)


def value1(par, y, policy=None):
    """
    V1(y): lifetime value at the household's own optimum, which is what welfare
    has to be measured on. The household is forward looking and faces the true
    addiction hazard, so whatever v it picks is the v it wants given the policy.
    It is an expectation over the period 1 employment and voucher draws, since
    those are realised before anything is chosen.
    """
    return float(sum(p * own for p, _, _, _, _, _, own, *_
                     in period1(par, y, policy)))


# ---------------------------------------------------------------------------
# THE INCOME GRID IS SOLVED ACROSS PROCESSES, because a calibration sweep is
# about fourteen hundred model solves and each one solves the same period 1
# problem at every point of a 120 point income grid, independently. Nothing
# else in the sweep can be run in parallel: the seven parameters are bracketed
# in a fixed order because each bracket is read at the parameters the previous
# one fixed, and a bisection is sequential by construction. The grid is the one
# place where the work is genuinely independent, and it is where essentially
# all of the time goes.
#
# THE POOL IS PERSISTENT. It is built once, on first use, and reused for every
# solve after that; a pool per solve would pay the fork cost fourteen hundred
# times a sweep and lose more than it saves.
#
# WORKERS NEVER FORK AGAIN. threshold() runs inside the workers as well as in
# the parent, so the flag below marks a child and sends it down the serial path.
# Without it each worker would build a pool of its own and the process count
# would square.
#
# STYLIZED_WORKERS sets the count. Unset, it takes the smaller of four and the
# core count. Set it to 1 to turn the pool off entirely, which is what to do
# when something else on the machine wants the cores, and what the timing
# comparisons in this file were run against.
import os as _os

_IN_WORKER = False
_POOL = None


def _n_workers():
    n = _os.environ.get('STYLIZED_WORKERS')
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 0
    return n if n > 0 else min(4, _os.cpu_count() or 1)


def _mark_worker():
    global _IN_WORKER
    _IN_WORKER = True


def _close_pool():
    global _POOL
    if _POOL is not None:
        _POOL.terminate()
        _POOL = None


def _pool(n):
    global _POOL
    if _POOL is None:
        import atexit
        import multiprocessing as mp
        _POOL = mp.get_context('fork').Pool(n, initializer=_mark_worker)
        atexit.register(_close_pool)
    return _POOL


def _period1_chunk(job):
    par, ys, policy = job
    return [period1(par, y, policy) for y in ys]


def _cross_job(job):
    """One threshold crossing, bisected to the income at which the sign turns."""
    par, policy, s, lo, hi, sgn = job
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
    return 0.5 * (lo + hi)


def _map_crossings(jobs):
    """Bisect every crossing, in parallel when that is worth it.

    THE CROSSINGS ARE WHERE A CALIBRATION SPENDS ITS TIME, which is not where
    the seed spends its time and is why this was missed. At the seed no
    household sits near its use threshold, so period1 is called once per income
    and the grid is the whole cost. At a calibrated point there are crossings,
    each a 24 step bisection, and they ran sequentially in the parent: 312
    period1 calls per solve of which only the 120 on the grid were parallel. A
    pool over 38 per cent of the work caps at 1.4x however many cores it is
    given, which is what the process table showed, the parent busier than its
    four workers put together.

    Each bisection is sequential in itself, but the crossings do not depend on
    each other, so they run as concurrent chains. ONE JOB PER CROSSING rather
    than chunks of them: a chain is 24 solves against about a millisecond of
    dispatch, and equal chunks leave workers idle whenever the count of
    crossings is not a multiple of the pool.
    """
    n = _n_workers()
    if n <= 1 or _IN_WORKER or len(jobs) < 2:
        return [_cross_job(j) for j in jobs]
    return list(_pool(n).map(_cross_job, jobs))


def _map_period1(par, ygrid, policy):
    """period1 at every income on the grid, in parallel when that is worth it."""
    n = _n_workers()
    ys = list(ygrid)
    if n <= 1 or _IN_WORKER or len(ys) < 4 * n:
        return [period1(par, y, policy) for y in ys]
    # TWICE AS MANY CHUNKS AS WORKERS, so a slow chunk does not hold the whole
    # solve open while three workers sit idle.
    size = -(-len(ys) // (2 * n))
    jobs = [(par, ys[i:i + size], policy) for i in range(0, len(ys), size)]
    out = []
    for r in _pool(n).map(_period1_chunk, jobs):
        out.extend(r)
    return out


def threshold(par, ygrid, policy=None, edges=None, cdf=None):
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
    rows = _map_period1(par, ygrid, policy)
    ns = max(len(r) for r in rows)
    n = len(ygrid)
    PR = np.zeros((n, ns)); G = np.full((n, ns), np.nan); VV = np.zeros((n, ns))
    INC = np.zeros((n, ns))
    # FIVE, not four: the branch now carries the small-unit indicator alongside
    # assets, the street, rent and the voucher.
    BU = np.zeros((n, ns, 5)); BN = np.zeros((n, ns, 5))
    for i, r in enumerate(rows):
        for s, (p, g, v, bu, bn, inc, _own) in enumerate(r):
            PR[i, s] = p; G[i, s] = g; VV[i, s] = v; INC[i, s] = inc
            BU[i, s] = bu; BN[i, s] = bn
    frac = (G > 0.0).astype(float)
    # EVERY CROSSING IS FOUND FIRST, THEN ALL OF THEM ARE BISECTED, THEN THE
    # SHARES ARE APPLIED. The crossings are read straight off G, which is
    # already complete, so nothing in the search depends on a bisection and no
    # bisection depends on another; splitting the one loop into three phases is
    # what lets the middle phase run concurrently.
    #
    # THE APPLY PHASE KEEPS THE ORIGINAL ORDER, s and then increasing i, because
    # two crossings in the same state can both write the boundary cell between
    # them and the later write has to win exactly as it did when this was one
    # pass.
    cross = []
    for s in range(ns):
        for i in range(n - 1):
            if np.isnan(G[i, s]) or np.isnan(G[i + 1, s]):
                continue
            if (G[i, s] > 0.0) == (G[i + 1, s] > 0.0):
                continue
            cross.append((s, i, ygrid[i], ygrid[i + 1], bool(G[i, s] > 0.0)))

    stars = _map_crossings([(par, policy, s, lo, hi, sgn)
                            for s, _i, lo, hi, sgn in cross])

    # THE USE REGION IS BUILT ONCE PER STATE AND THEN INTEGRATED, rather than
    # each crossing writing the two cells beside it.
    #
    # WHY IT HAD TO CHANGE. Writing per crossing is correct only while no cell
    # is the boundary of two of them, and the use region is NOT always an
    # interval: at some parameter values it is the top block PLUS a single
    # isolated cell in the middle of the income distribution, where a household
    # sits on a housing rung boundary and using tips which rung it takes. That
    # cell has a crossing on each side, both write it, and the second write
    # wins, so its share was one of the two halves rather than the overlap of
    # them. As the isolated region shrank the share did not shrink with it: it
    # stayed finite until the pair of crossings vanished and then the whole cell
    # left at once.
    #
    # That is a STEP IN PARTICIPATION AS A FUNCTION OF b of about 1.25 points,
    # and it is what made two points of Figure 1's channel scan unreachable: the
    # 8.90 per cent target sat strictly inside the jump, so no b delivered it and
    # the bisection returned an endpoint. It is the same family as the bug the
    # note below records, and it survived that fix because the fix was written to
    # preserve the old later-write-wins behaviour exactly.
    #
    # WHAT IT DOES NOW. For each state the crossings are turned into a union of
    # intervals in the measure the mass is counted in, and every cell is given
    # the fraction of itself lying inside that union. One crossing gives exactly
    # what the per crossing code gave; two crossings around one cell now give
    # their overlap, which goes to zero smoothly as the region closes.
    def _pos(y):
        """Where y sits in the measure the cells are weighed in."""
        return cdf(y) if (cdf is not None and edges is not None) else y

    def _cell_edges(cell):
        if cdf is not None and edges is not None:
            return edges[cell], edges[cell + 1]
        lo_y = ygrid[cell]
        hi_y = ygrid[cell + 1] if cell + 1 < n else ygrid[cell]
        return lo_y, hi_y

    by_state = {}
    for (s, i, _lo, _hi, _sgn), ystar in zip(cross, stars):
        by_state.setdefault(s, []).append((i, float(ystar)))

    for s, items in by_state.items():
        items.sort()
        # The boundaries in measure space, forced non decreasing: a crossing
        # between cells i and i+1 cannot sit below one found earlier, and a
        # bisection landing a hair out of order must not invert an interval.
        pts = []
        for _i, ystar in items:
            q = _pos(ystar)
            pts.append(q if not pts else max(q, pts[-1]))
        # Membership alternates across the boundaries, and the segment holding
        # the lowest income is the one the lowest node's own decision names.
        inside = bool(G[0, s] > 0.0)
        lo_edge, _ = _cell_edges(0)
        _, hi_edge = _cell_edges(n - 1)
        segs = []
        left = lo_edge
        for q in pts:
            if inside and q > left:
                segs.append((left, q))
            left = q
            inside = not inside
        if inside and hi_edge > left:
            segs.append((left, hi_edge))
        for cell in range(n):
            a, b_ = _cell_edges(cell)
            width = b_ - a
            if width <= 0:
                continue
            covered = 0.0
            for u, v in segs:
                covered += max(0.0, min(b_, v) - max(a, u))
            frac[cell, s] = min(max(covered / width, 0.0), 1.0)

    # THE LOWEST CELL IS NO LONGER SPECIAL, and the sub grid that used to
    # integrate it is deleted. It took the MASS of users from incomes inside the
    # cell and the DOSE from the cell's single representative, which is a
    # different household: at the calibrated parameters the representative did
    # not use at all, so its reported dose was the smallest positive point on
    # the drug grid and half of all users carried a disorder probability of 0.45
    # that belonged to nobody. lambda had nothing left to fit but that grid
    # constant and ran to 5972, and the SUD rate moved by a factor of two when
    # the drug grid's floor moved, with every parameter held fixed.
    #
    # The grid now floors the distribution at the rent rather than pooling
    # across it, so the bottom cell is an ordinary cell of 2.5 per cent and the
    # participation margin at 5.13 per cent falls on a resolved node above it.
    # See _grid in calibrate.py. If a bottom cell ever again needs integrating,
    # integrate the WHOLE decision over the sub grid, dose included, never the
    # mass alone.

    return PR, np.clip(frac, 0.0, 1.0), VV, BU, BN, INC


def aggregates(par, ygrid, w, policy=None, edges=None, cdf=None):
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
    PR, frac, VV, BU, BN, INC = threshold(par, ygrid, policy, edges, cdf)
    ww = w / w.sum(); ybar = (ww * ygrid).sum()
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)

    part = spend = uinc = sud = 0.0
    hl = hl_sud = hcost = hinc = cost = mass = 0.0
    # PERIOD 2 HOMELESSNESS ON ITS OWN, as the denominator for the SUD share of
    # the homeless.  EVERY PERIOD 1 HOUSEHOLD IS CLEAN BY CONSTRUCTION -- the
    # disorder is realised at the transition -- so period 1 homelessness is pure
    # dilution in that ratio and carrying it makes the moment unreachable for
    # reasons of timing rather than of economics.
    hl2 = 0.0
    # THE SIZE DISTRIBUTION, over the HOUSED only. The American Community
    # Survey's universe for it is occupied units, so the street is not in the
    # denominator, exactly as in the quantitative model's counterpart.
    smallmass = housedmass = 0.0
    # RENT OVER HALF OF INCOME, the moment h_sm is JUDGED on rather than
    # calibrated to.  The author, 12 September: *"for h_sm you can set it
    # exogenously to something that gives decent % of households spending over
    # 50 per cent on rent and still be able to choose h_hl to match 1 per cent
    # homelessness rate"*.  It is the quantitative model's burden50, which sits
    # at 17.5 per cent in the data, and it is REPORTED AND NOT TARGETED: nothing
    # brackets on it.  Period 1 only and over the period 1 population, because
    # that is the age range the survey statistic is built on.
    burden = mass1 = 0.0
    # NET WORTH OVER INCOME, for beta.  Author, 12 September: *"you should also
    # calibrate beta to match a net worth to income ratio of 3"*, which is the
    # quantitative model's wealth_to_output_data.  Period 1 assets over period 1
    # income: period 2 is terminal and runs assets down to nothing, so the stock
    # a household holds is the one it chose in period 1.
    wealth = winc = 0.0
    # NON DRUG EXPENDITURE, which is what the Consumer Expenditure Survey share
    # is a share OF. In period 1 it is income less drug spending less saving; in
    # period 2, which is terminal, it is the whole of cash. Rent here is what the
    # tenant actually pays, net of any voucher, on both sides of the ratio, so
    # the object is an outlay share exactly as the survey measures it.
    hexp = 0.0
    for i, y in enumerate(ygrid):
        ag, _, H2c, R2c, G2c, S2c = solve_period2(par, y, policy, used=0)
        if policy == 'HF':
            H2u, R2u, G2u, S2u = H2c, R2c, G2c, S2c
        else:
            _, _, H2u, R2u, G2u, S2u = solve_period2(par, y, policy, used=1)
        for s in range(PR.shape[1]):
            if PR[i, s] <= 0.0:
                continue
            for uu, mm, br in ((1, ww[i] * PR[i, s] * frac[i, s], BU[i, s]),
                               (0, ww[i] * PR[i, s] * (1.0 - frac[i, s]), BN[i, s])):
                if mm <= 0.0:
                    continue
                a, street, rent, sub, small1 = br
                pid = float(_pid(par, VV[i, s])) if uu else 0.0
                if uu:
                    part += mm; spend += mm * par.p_v * VV[i, s]
                    uinc += mm * INC[i, s]; sud += mm * pid
                # period 1: everyone alive, mass one
                mass += mm
                mass1 += mm
                wealth += mm * a
                winc += mm * INC[i, s]
                if street < 0.5 and rent > 0.5 * INC[i, s]:
                    burden += mm
                hl += mm * street
                smallmass += mm * small1; housedmass += mm * (1.0 - street)
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
                    Sx = S2u if uu else S2c
                    mass += m2
                    hl += m2 * street2
                    smallmass += m2 * float(np.interp(a, ag, Sx[:, d]))
                    housedmass += m2 * (1.0 - street2)
                    hl2 += m2 * street2
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
                sud_of_homeless2=float(hl_sud / max(hl2, 1e-12)),
                # THE TWO ACCUMULATORS BEHIND THAT RATIO, exported because it
                # read exactly 0.0000 during a calibration run and a ratio of
                # zero does not say WHICH of its parts vanished.
                hl2=float(hl2), hl_sud=float(hl_sud),
                housing_share=float(hcost / max(hinc, 1e-12)),
                # SHARE OF THE HOUSED IN THE SMALLER RENTAL. The American
                # Community Survey table B25042, occupied units, puts 13.2 per
                # cent of households in a unit of no bedroom or one, which is
                # the small cell of this model's two. It is what h_sm is
                # calibrated on; h_lg stays set at its market value.
                hsmall=float(smallmass / max(housedmass, 1e-12)),
                burden50=float(burden / max(mass1, 1e-12)),
                # IN ANNUAL INCOME, NOT PER-PERIOD INCOME.  A period here is
                # thirty years, so wealth over period income is wealth over
                # thirty years of it and comes out a factor of `years` too
                # small against a target -- 3.0 -- that is stated in ANNUAL
                # income, as the quantitative model's wealth_to_output_data is.
                # Without the multiply this read 0.0293 against 3.0 and looked
                # like a factor of a hundred rather than a factor of three.
                networth=float(wealth * par.years / max(winc, 1e-12)),
                # RENT OVER NON DRUG EXPENDITURE. The frictionless Cobb-Douglas
                # benchmark for it is gam itself under the quantitative model's
                # nesting, so this is the moment that
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
    ag, W2c, _, _, _, _ = solve_period2(par, y, policy, used=0)
    W2u = W2c if policy == 'HF' else solve_period2(par, y, policy, used=1)[1]
    s0, s1 = par.phi0, par.phi0 * (1.0 - par.kap)
    tot = 0.0
    for p, inc, rmul in _states(par, 0, policy, y, used=0):
        if p <= 1e-14:
            continue
        vg = _vgrid(par, inc)
        pid = _pid(par, vg)[:, None]
        cont = (1.0 - pid) * s0 * W2u[None, :, 0] + pid * s1 * W2u[None, :, 1]
        rm = _p1_rmul(par, policy, rmul)
        val, aa, ss, rr, _, mm = _branch(par, ag, inc, rm, vg, cont)
        cont0 = np.repeat((s0 * W2c[:, 0])[None, :], 2, axis=0)
        v0, a0, ss0, r0, _, mm0 = _branch(par, ag, inc, rmul, np.zeros(2), cont0)
        tot_v = val - par.omega * par.chdmg * _pid(par, vg)
        k = int(np.argmax(tot_v[1:])) + 1
        if tot_v[k] > v0[0]:
            a, rent, pi = aa[k], rr[k], float(_pid(par, vg[k]))
            c1 = inc - rent - par.p_v * vg[k] - a
            h1, q1 = _hpick(par, ss[k], mm[k]), float(vg[k])
        else:
            a, rent, pi = a0[0], r0[0], 0.0
            c1 = inc - rent - a
            h1, q1 = _hpick(par, ss0[0], mm0[0]), 0.0
        i2 = int(np.argmin(np.abs(ag - a)))
        # d(objective)/d(phi0), which is the continuation per unit of survival
        ew = (1.0 - pi) * W2c[i2, 0] + pi * (1.0 - par.kap) * W2u[i2, 1]
        # d(flow)/dc at the chosen allocation.  With V = S/(1-sigma) + aleph and
        # S the parent's and the child's bundles each to the power 1-sigma, both
        # carry c with the same exponent phi_c, so dV/dc = phi_c * S / c.
        phc = (1.0 - par.gam) * (1.0 - par.th)
        S = (1.0 - par.sigma) * (_flow(par, c1, h1, q1) - par.aleph)
        u_c = phc * S / max(c1, 1e-12)
        tot += p * par.beta * ew / u_c * par.years
    return float(tot)
