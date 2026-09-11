# The child in the parent's flow utility

The specification settled with the author on 10 and 11 September. Approved
11 September: *"ok, i think the utility you have in mind makes sense"*.
Nothing is built.

The typeset version is `scratchpad/household_split.tex`, revision 2.

## REVISION 2 SUPERSEDES REVISION 1 OF THIS FILE

The first version specified the channel against an ADDITIVE CES aggregator in
which housing entered undeflated as a household public good. BOTH OF THOSE WERE
WRONG, and the author's question -- why should housing not be divided? -- is what
exposed it.

`calculate_flow_utility` has several branches and the live one is selected by
`include_probability_of_becoming_addicted`, which is 1. That branch is
MULTIPLICATIVE: a Cobb-Douglas bundle inside a CRRA, not a CES sum. The additive
expression revision 1 was written against is the `else` branch, and it is dead.
In the live branch housing is deflated by household size along with everything
else, through the prefactor rather than term by term. So housing IS divided, and
should be.

## Why a second channel at all

The existing death-contingent wage channel is right on every dimension that can
be checked: it penalises 5.31 per cent of newborns against 3.52-8.50 per cent of
children actually exposed; the penalty is worth 46 per cent of the child's
lifetime consumption against the stylized model's 50.86; and the eightfold death
hazard delivers it at an effective lag of about twenty-one years, EARLIER than a
childbearing-plus-26 scheme's twenty-six.

What it cannot do is price the childhood. Nilsson measures the earnings
consequence twenty years on, and nothing prices the years in between. The wage
term cannot be repurposed, because the wage impact does not exist before the
child is 26 -- which is the author's own objection, 10 September.

## Notation, with the live values

    n(a)            children under 18 at parent-age a; n(40) = 1.45
    m(a) = sqrt(1+n(a))   the equivalence scale
    s               housing size, the rung chosen
    c               non-drug consumption
    q               drug quantity
    b_bar           addiction_scalar, a shifter so q = 0 is finite
    omega_c         the parent's weight on a child; the planner's is one
    aleph           value of life, 177.77, once per household

    sigma = 2, and the live Cobb-Douglas shares are
        phi_s = 0.203 housing, phi_c = 0.527 consumption, phi_q = 0.270 drugs

They sum to one, so the bundle is homogeneous of degree one and the CRRA is well
defined.

## What the code does now

    X        = s^phi_s * c^phi_c * (b_bar + q)^phi_q
    flow(a)  = aleph + m^sigma * X^(1-sigma)/(1-sigma)
             = aleph - m^2 / X                              (sigma = 2)

THE PREFACTOR IS THE EQUIVALENCE SCALE. For any homogeneous bundle,

    m * (X/m)^(1-sigma)/(1-sigma)  ==  m^sigma * X^(1-sigma)/(1-sigma)

so multiplying by m^sigma is IDENTICAL to dividing the whole bundle by m and
summing over m members. Housing sits inside X, so housing is deflated. In every
run to date m = 1, because include_varying_household_size is 0.

## What replaces it

Everyone has the same housing and consumption, each divided by the scale.
Drugs are private to the parent. CHILDREN HAVE THE SAME UTILITY FUNCTION WITH
q = 0 -- not renormalised shares, which would put parent and child on different
scales and make adding them meaningless.

    X_P = (s/m)^phi_s * (c/m)^phi_c * (b_bar + q)^phi_q     u_P = -1/X_P
    X_K = (s/m)^phi_s * (c/m)^phi_c * b_bar^phi_q           u_K = -1/X_K

    social  W(a) = aleph + u_P +           n(a)*u_K
    parent  V(a) = aleph + u_P + omega_c * n(a)*u_K

b_bar enters the child's bundle as a constant factor, so it scales u_K and moves
no margin.

## The externality

    W - V = (1 - omega_c) * n(a) * u_K

Under Cobb-Douglas the marginal utility of consumption is phi_c/(c*X), so a
dollar of drug spending, which comes straight out of c, carries

    d(W-V)/d(drug spending) = (1 - omega_c) * n(a) * phi_c / (c * X_K)

NESTING. At omega_c = 1 and n = 0, m = 1 and the child term vanishes, leaving
W = V = aleph - 1/[ s^phi_s c^phi_c (b_bar+q)^phi_q ], the live expression
exactly. The present model is the childless, fully-internalising corner of this
one, WHICH IS THE HARD TEST ON STEP ONE OF THE BUILD.

## A household at age forty

s = 1.0, c = 1.0, q = 0.164 (the 14.1 per cent share the model already targets),
n = 1.45 so m = 1.565 and every member has s/m = c/m = 0.639.

    X_P = 0.4444    u_P = -2.250
    X_K = 0.1438    u_K = -6.955
    W = -12.335                     V = -2.250 + omega_c*(-10.084)

Raising drug spending, q 0.164 -> 0.200 and c 1.000 -> 0.964:

                        before    after    change
    parent              -2.250   -2.176    +0.074
    each child          -6.955   -7.091    -0.136
    all 1.45 children                      -0.197
    NET SOCIAL                             -0.123

## The amplification is exact, and it is 3.09

From the same consumption cut with drugs held, the parent loses 0.044 and each
child 0.136. Cobb-Douglas makes the reason exact: marginal utility is
phi_c/(c*X), and parent and child share phi_c and c, so the ratio is the ratio
of the bundles:

    (du_K/dc) / (du_P/dc) = X_P / X_K = ((b_bar + q)/b_bar)^phi_q = 3.09

The parent's bundle is larger only because it holds the drugs, and a larger
bundle has lower marginal utility. The drug partly insulates the parent from the
consumption it gives up; nothing insulates the child. THE AMPLIFICATION IS
GOVERNED ENTIRELY BY phi_q AND BY HOW MUCH THE HOUSEHOLD USES, both already
calibrated.

(Revision 1 of this file reported 4.94 from the additive form. Withdrawn.)

## Where the unemployment channel enters: nowhere new

Through c. The disorder already raises unemployment in the calibrated model --
`kappa_ued` is 0.2059 against a population 0.0503, with a separation multiplier
of 2.7 and `multiple_find_if_addicted` at 28.5 making spells long. A using
household has less income AND spends a seventh of what remains on drugs. Both
lower c, hence X_K. No extra term.

## Decisions taken, so they are not re-litigated

**CHILDREN COUNT AS WHOLE PEOPLE.** The weight is n(a), not m - 1. The square
root scale is about consumption NEEDS, not headcount. Author, 11 September:
*"Let's go with counting children as whole people."* It does not nest the code's
"equivalent adults" convention, which is the price.

**CHILDREN ARE EXOGENOUS TO THE DRUG CHOICE.** n(a) must not depend on the
addiction state, or using would remove people from the welfare sum and
mechanically raise measured welfare -- the perverse incentive that forced the
differencing of the existing child term.

**THE POPULATION PROFILE APPLIES TO EVERY HOUSEHOLD.** Measured, households with
a disorder have 0.95 times as many children overall, 0.886 composition-adjusted,
but only 0.639 at ages 35-49. Author, 11 September: *"I think we can say that
those with Sud have roughly the same number of children in the house."* So the
channel is an UPPER BOUND at the peak ages, under the reading in which the
missing children are themselves a harm rather than a reason to count fewer.

**ALEPH STAYS ON THE PARENT.** Once per household. Per child it would inflate
every welfare level by a constant without changing any margin.

## Build order

1. install the children profile and recalibrate -- ALL THE CALIBRATION RISK IS
   HERE, since m stops being 1 and every consumption-denominated moment moves.
   The n = 0 nesting test above is the check;
2. take the drugs out of the shared bundle, refitting phi_q, which must move
   because the drug goes from being deflated with everything else to entering
   the parent's bundle alone;
3. split the parent's weight from the planner's at omega_c.
