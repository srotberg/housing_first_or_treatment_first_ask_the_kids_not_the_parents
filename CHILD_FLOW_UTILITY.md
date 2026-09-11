# The child in the parent's flow utility

The design settled with the author on 10 and 11 September, after the
death-contingent wage channel was audited and found correct but incapable of
carrying a contemporaneous harm. This file is the specification; nothing is built.

## Why a second channel at all

The existing channel is right on every dimension that can be checked:

    count   5.31% of newborns penalised   against 3.52-8.50% of children exposed
    size    46% of lifetime consumption   against the stylized model's 50.86%
    date    about 21 years out            against 26 for a childbearing scheme

What it cannot do is price the CHILDHOOD. A child living with an addicted parent
suffers now, and Nilsson measures only the earnings consequence twenty years
later. The author, 10 September: *"How would you capture contemporaneous
childhood harm? Like less resources consumed that the parent does value as
much?"* -- and *"it's not just that the drugs take resources away, but they also
cause unemployment which takes more resources away"*.

## The symbols, with the file's own values

    sigma = 2, rho = 1.25, eta = 1.07    ->  power_1 = 0.2, power_2 = -5,
                                             power_3 = 0.144
    phi_c = (1 - 0.278)(1 - 0.27) = 0.527     relative_share_of_consumption
    phi_a = 0.27                              relative_share_of_addiction
    aleph = 177.77                            value_of_life

    n(a)   children under 18 at parent-age a, the profile in
           data/make_children_by_age.py; n(40) = 1.45
    m(a)   = sqrt(1 + n(a))                   equivalence scale, NEEDS
    c      non-drug consumption
    q      drug quantity, frac_spent * C / price
    H      housing utility, a household PUBLIC good, already undeflated

## What the code does now

    flow(a) = aleph - m * [ H + phi_c*(c/m)^0.2 + phi_a*(q/m)^0.144 ]^(-5)

m identical people each consuming c/m AND q/m: the household shares the drugs.
And m = 1 today, because include_varying_household_size is 0.

## What replaces it

    A    = H + phi_c*(c/m)^0.2                 shared bundle, everyone gets this
    u_P  = -[ A + phi_a*q^0.144 ]^(-5)         parent, drugs UNDIVIDED
    u_K  = -[ A ]^(-5)                         child: consumption and housing only

    social  W(a) = aleph + u_P +          n(a)*u_K
    parent  V(a) = aleph + u_P + omega_c * n(a)*u_K

THE EXTERNALITY IS ONE LINE:

    W - V = (1 - omega_c) * n(a) * u_K

and the marginal externality of a dollar spent on drugs, which comes out of c:

    d(W-V)/d(drug spending) = (1-omega_c) * n(a) * phi_c * A^(-6) * c^(-0.8) * m^(-0.2)

THREE CHANGES AND NO MORE: q loses its /m; the children become a separate
additive term; m = sqrt(1+n(a)) replaces m = 1.

NESTING. At omega_c = 1 and n = 0, m = 1 and W = V = today's expression exactly.
The current model is the childless, fully-internalising corner.

## Decisions taken, so they are not re-litigated

**CHILDREN COUNT AS WHOLE PEOPLE.** The weight is n(a), not m - 1. The square
root scale is a statement about consumption NEEDS, not about how many people
there are. Author, 11 September: *"Let's go with counting children as whole
people."* This does NOT nest the current code's "equivalent adults" convention,
which is the price.

**CHILDREN ARE EXOGENOUS TO THE DRUG CHOICE.** n(a) does not depend on the
addiction state. Making it depend would mean using REMOVES people from the social
welfare sum and mechanically raises measured welfare -- the same perverse
incentive that forced the child-value differencing at line 30158, where the level
version "REWARDED the disorder".

**THE POPULATION PROFILE IS USED FOR EVERYONE.** Measured, households with a
disorder have 0.95 times as many children overall and 0.886 composition-adjusted,
but only 0.639 at ages 35-49, the peak child-rearing years. Author, 11 September:
*"I think we can say that those with Sud have roughly the same number of children
in the house. It is not a big difference."* SO THE CHANNEL IS AN UPPER BOUND AT
THE PEAK AGES, and this is the reading in which the missing children are
themselves a harm -- removal -- rather than a reason to count fewer of them.

**ALEPH STAYS ON THE PARENT.** value_of_life is added once per household, not per
person. Adding it per child would inflate every welfare level by a constant
without changing any margin.

## Where the unemployment channel enters: nowhere new

Through c. The disorder already raises unemployment in the calibrated model --
`kappa_ued` is 0.2059 against a population rate of 0.0503, with a separation
multiplier of 2.7 and `multiple_find_if_addicted` at 28.5 making spells long. So
a using household has less income AND spends 14 per cent of what remains on
drugs. Both lower c, both lower A, both lower u_K. No extra term.

## Size, as an envelope

Combined diversion takes c down about 22 per cent:

    (c/m)^0.2 falls by 1 - 0.78^0.2                        4.9%
    if the consumption term is ~60% of A, A falls          2.9%
    u_K = -A^(-5), so |u_K| rises by 1.029^5 - 1          15.9%

carried by n(a) = 1.45 children at age 40, of which the parent internalises
omega_c. Against the wage channel's 24.3 utils this is of the order of 1.6 to 2.2
times as large, which would put the omega_c matching the parent against non-parent
moment nearer 0.3-0.4 than the 1.06 it takes today. THIS IS AN ENVELOPE.

## Build order, when it is built

1. install the children profile and recalibrate, drugs still shared -- ALL THE
   CALIBRATION RISK IS HERE, since m stops being 1 and every consumption
   denominated moment moves;
2. take the /m off the drug term, and refit relative_share_of_addiction, which
   must move because the drug now enters one bracket at q instead of m brackets
   at q/m;
3. split the parent's weight from the planner's at omega_c.

Each step is separately checkable.
