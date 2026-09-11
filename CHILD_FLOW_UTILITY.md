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

## kappa IS SETTLED: kappa = xi - 1

Author, 11 September: *"i think you should just divide by xi inside the utility
and multiple by xi, not xi^2"*, and then *"this is how you get what i have in the
JME paper, right?"* -- yes, exactly:

    xi * u(X/xi) = xi * (X/xi)^(1-sigma)/(1-sigma) = xi^sigma * X^(1-sigma)/(1-sigma)

which with X = c^(1-gamma) h^gamma IS equation (1). Verified at sigma = 1.5, 2
and 3 and four values of xi, identical to machine precision. So the household has
xi members in total, one parent and kappa = xi - 1 children, and when q is shared
the whole thing collapses back to the published expression.

THIS REVERSES THE EARLIER "WHOLE PEOPLE" DECISION, which was taken on 11
September before the xi^sigma form had been established. Consistency with the
published specification wins.

### The consequence, recorded because it is large

The child term scales linearly with kappa, and at age forty xi - 1 = 0.565
against n = 1.45, SO THE CONTEMPORANEOUS CHANNEL IS 61 PER CENT SMALLER than
under whole people:

                       children carry   marginal: parent  children     net
    whole people, 1.45    -10.085            +0.074        -0.197    -0.123
    xi - 1 = 0.565         -3.931            +0.074        -0.077    -0.003

The per-child amplification does NOT move -- it is a ratio between two
individuals, still 3.09 -- but the aggregate externality is about two fifths of
what it was. The earlier envelope put this channel at 1.6 to 2.2 times the wage
channel; at this count it is nearer 0.6 to 0.9, COMPARABLE RATHER THAN DOMINANT.
So it is unlikely on its own to move the Housing First against Treatment First
ranking, which was the question it was built to answer.

## THE TWO CHILD TERMS ARE CONSECUTIVE, NOT ALTERNATIVES

Author, 11 September: *"in the utility we still need to include the weight on the
newborn (which we can explain is when the child actually becomes a member of
society)"*. Both terms stay, and together they cover one child's life once:

    CHILDHOOD    the contemporaneous term specified above. The child lives in
                 the household, consumes (c/xi) and (h/xi), and gets no drugs.
                 Weighted omega_c, counted kappa = xi - 1 times.

    ADULTHOOD    the existing newborn term, expected_child_value, which is the
                 child's VALUE FUNCTION at model age 1 -- its whole adult life
                 from 26 on. Weighted omega_c, collected when the parent dies,
                 which is the moment the child becomes a member of society.

NO DOUBLE COUNTING: the first is flow utility during childhood, the second is
lifetime value from adulthood. Back to back, not overlapping.

ONE omega_c MULTIPLIES BOTH, so calibrating it on the 18 per cent moment pins the
weight on childhood and on adulthood at once, and omega_c = 1 internalises both.
That is what makes the optimal SUD the optimum for the whole child life rather
than half of it.

### THE LEVEL IS TREATED OPPOSITELY IN THE TWO, AND THIS IS A TRAP

The NEWBORN term is multiplied by the probability of dying this period, so it
MUST STAY DIFFERENCED. The level version pays a household more the likelier it is
to die, measured at 0.058 utils REWARDING the disorder, which is why the
differencing at line 30158 exists.

The CONTEMPORANEOUS term carries no death probability at all, so its level is
correct and it MUST NOT BE DIFFERENCED.

Same omega_c, opposite handling. Getting it backwards would be invisible in the
output.

### A stock and a flow, which need not match

The flow-utility children are a STOCK -- xi - 1 = 0.565 equivalent children
present at age forty. The newborn is a FLOW -- exactly one replacement per death.
They are different objects and the model's demographics do not target fertility
anyway. Worth a sentence in the paper so it is not read as an inconsistency.

## WHAT THE MODEL CAN THEN SAY: THE OPTIMAL DRUG USE

Author: *"the nice thing about this paper is that i can say something about what
the optimal drug use is"*, and *"by raising omega_c=1 we know what the optimal
SUD is"*. The wedge is (1 - omega_c) times the child terms, so the social optimum
is the omega_c = 1 allocation, which the model computes directly.

CALIBRATING omega_c IS WHAT MAKES THE OPTIMUM A MEASUREMENT RATHER THAN AN
ASSUMPTION. Assume omega_c and the optimum is assumed with it; fit it to the
parent against non-parent gap and the optimum inherits that moment's discipline.
That is the argument for this calibration strategy.

On the CURRENT specification, wage channel only, omega_c = 1 gives b = 0.0732
against 0.0878 at omega_c = 0 -- the optimum is about a sixth below laissez
faire, NOT ZERO. Against that, universal Housing First takes use to 15.16 per
cent and universal Treatment First to 0.13. BOTH MISS, IN OPPOSITE DIRECTIONS,
and the optimum lies between them. The graduated clawback is the instrument that
lands between the two corners. These figures will move once the contemporaneous
channel is in, since it widens the wedge.

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
