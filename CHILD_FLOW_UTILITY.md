# The child in the parent's flow utility

Specification only; nothing is built. Approved 11 September: *"ok, i think this
is correct now"*. The typeset version is `scratchpad/scaling.tex`, one page, in
the notation of Rotberg and Steinberg (2024).

## The published specification is the starting point

Equation (1) of the JME paper:

    u_j(c,h) = xi_j^sigma * (c^(1-gamma) h^gamma)^(1-sigma) / (1-sigma)

with `xi_j` the equivalence scale -- the square root of average household size at
age j, from AHS 2017. **THE SCALE IS A PREFACTOR, NOT A DIVISOR ON THE
ARGUMENTS**, and `scaled_household_size` in the Fortran is exactly `xi_j^sigma`.

## What the prefactor already means

With `X = c^(1-gamma) h^gamma` and `u(x) = x^(1-sigma)/(1-sigma)`,

    xi^sigma * u-numerator(X)  ==  xi * u(X / xi)
                                   ^^         ^^
                                 members    scale

because X is homogeneous of degree one. So the published form is ALREADY a
household: xi members, each consuming X/xi, added up. The scale and the count are
both present, collapsed into one power of xi.

## Adding drugs, which the parent does not share

Let q be drugs with share phi_q, children consuming none, and b_bar a shifter
keeping q = 0 finite. The members now hold DIFFERENT bundles:

    X_P = (c/xi)^phi_c (h/xi)^phi_h (b_bar + q)^phi_q
    X_K = (c/xi)^phi_c (h/xi)^phi_h  b_bar^phi_q

There is no single X, so the collapse is unavailable and the members must be
written out:

    W = u(X_P) + kappa   * u(X_K)                  planner
    V = u(X_P) + omega_c * kappa * u(X_K)          parent; enters the Bellman

    W - V = (1 - omega_c) * kappa * u(X_K)         the externality

## WHY DIVIDING BY xi AND MULTIPLYING BY N IS NOT THE SAME THING

The author asked this directly. With N = xi^2 the number of people:

    divide by xi, multiply by xi:   xi * u(X/xi) = xi^sigma     * u-num(X)
    divide by xi, multiply by N :    N * u(X/xi) = xi^(sigma+1) * u-num(X)

The second is the first times an extra xi, for EVERY sigma and every N --
verified numerically at sigma = 2 and 3 and several N, ratio exactly xi each
time. And xi varies with age, so that factor does not merely rescale utility, it
REWEIGHTS IT ACROSS THE LIFE CYCLE. The scale and the count must be the same xi
for the published form to survive.

## The one decision still open: kappa

    kappa = xi - 1    household has xi members in total, and the whole thing
                      collapses back to xi^sigma u(X) when q is shared.
                      NESTS THE PUBLISHED FORM.

    kappa = n         whole children, household has 1 + n members. Defensible --
                      a child is a person and xi is about needs, not headcount --
                      but a departure that does not nest.

The author chose whole people on 11 September, BEFORE it was established that the
published specification is the xi^sigma form. The two are in tension and the
choice is worth revisiting. My recommendation is kappa = xi - 1, for consistency
with the JME paper, unless the departure is wanted deliberately.

## Decisions already taken

**CHILDREN ARE EXOGENOUS TO THE DRUG CHOICE.** n must not depend on the addiction
state, or using would remove people from the welfare sum and mechanically raise
measured welfare -- the trap that forced the differencing of the existing child
term.

**THE POPULATION PROFILE APPLIES TO EVERY HOUSEHOLD.** Households with a disorder
have 0.95 times as many children overall, 0.886 composition-adjusted, but only
0.639 at ages 35-49. Author: *"I think we can say that those with Sud have
roughly the same number of children in the house."* So the channel is an UPPER
BOUND at the peak ages.

**THE VALUE OF LIFE STAYS WITH THE PARENT**, once per household. Per child it
would move every welfare level by a constant without moving any margin.

**THE CHILDREN PROFILE IS CHILDREN UNDER 18 BY AGE**, not household size, built
in `data/make_children_by_age.py`: the SCF single-year shape rescaled to the
NSDUH under-18 levels, peaking at 1.45 children around age 40.

## Where the unemployment channel enters: nowhere new

Through c. The disorder already raises unemployment in the calibrated model --
`kappa_ued` is 0.2059 against a population 0.0503, with a separation multiplier
of 2.7 and long spells. A using household has less income AND spends a seventh of
what remains on drugs. Both lower c, hence X_K.

## Build order

1. install the children profile and recalibrate with drugs still shared. ALL THE
   CALIBRATION RISK IS HERE, since xi stops being 1 and every
   consumption-denominated moment moves. The household is still made of identical
   members at this stage, so the published prefactor form still holds and the
   code need not be restructured. The check is that omega_c = 1 with no children
   must reproduce the current benchmark exactly;
2. take the drugs out of the shared bundle. This is the step that breaks the
   collapse and forces the explicit sum, and it needs phi_q refitted;
3. split the parent's weight from the planner's at omega_c.

## Superseded

Revisions 1 and 2 of this file specified the channel against an ADDITIVE CES
aggregator, revision 1 with housing undeflated. Both were wrong: the live branch
is multiplicative, and housing is deflated with everything else. Revision 2's
amplification figure of 3.09 and revision 1's 4.94 were computed under the
"whole people" count and will move if kappa changes.
