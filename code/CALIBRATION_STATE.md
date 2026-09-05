## 5 September, 23:12 -- THE VOUCHER BUG IS FIXED. WHAT IT DID AND DID NOT SOLVE.

provide_vouchers is 0 as of ee0a9874; the declaration carries the full reasoning.
Semantic hash is now 4346daf40c and the 1,806-point archive is orphaned.

WHAT THE FIX SOLVED. burden50 was not hard to hit, it was ARITHMETICALLY
UNREACHABLE: voucher one capped every renter's net rent at 30 per cent of income,
so no household could ever pay over half, and the moment read 0.0000 at every
configuration tried. Measured at the same ladder before and after, h2 = 0.20,
h3 = 0.60, rsl = 1.00, one coordinate changed:

    moment                          before    after   target
    burden50                        0.0000   0.1727    0.175
    gamma                           0.4630   0.2510    0.268
    burdened IN the smallest rental 0.0000   0.1890       --
    aggregate rent / income          1.084    0.233       --
    omega_l                         0.1899   0.4711    0.400
    beta                             1.835    2.647     2.25

Both dead instruments now work with the right signs. burden50 rises
monotonically in h2 -- 0.0641, 0.1727, 0.3460 at h2 = 0.13, 0.20, 0.30 -- and
h_3 FALLS in h3, 0.410 at h3 = 0.25 against 0.086 at h3 = 0.60, which is the
author's sign and the one the pre-fix model could not produce.

WHAT IT DID NOT SOLVE, and one problem it opened.

- h_1 = 0.386 against 0.0040. With free housing gone, housing has a real price
  and a third of households take the street.
- h_3 = 0.086 against 0.627, now inverted: 91 per cent are in the SMALLEST unit
  and h3 must come well below 0.25, a region never measured.
- The homeless are the wrong people: 66 to 90 per cent employed against a 0.46
  target, and ZERO with a substance use disorder against 0.217 in the data.

THE STREET CANNOT CLOSE h_1. Bracket at h2 = 0.20, h3 = 0.60, rsl = 1.00:

    street    h_1    burden50   gamma  omega_l   beta  emp|hl
    0.080   0.3855    0.1727   0.2510   0.471   2.647  0.9041
    0.020   0.2242    0.1894   0.2807   0.504   3.112  0.8604
    0.008   0.1529    0.2199   0.3017   0.515   3.320  0.8170
    0.003   0.1037    0.2556   0.3161   0.523   3.499  0.7471
    0.001   0.0721    0.2773   0.3249   0.529   3.668  0.6610

An 80x cut reaches 7.2 per cent, still 18x target, at a log-log elasticity of
about 0.38 and decaying; extrapolated, 0.4 per cent needs a street near 5e-7.
Meanwhile burden50 overshoots to 0.277 and beta runs to 3.67.

THE TENSION, AND IT IS REAL. h_1 wants h2 SMALL so everyone can afford the
cheapest rental; burden50 wants h2 LARGE so 17.5 per cent of renters pay over
half their income for it. With ssi_floor_level at 0.13 the poorest have income
about 0.13, so h2 = 0.20 costs them 154 per cent of income and the street is all
that is left. Housing them needs h2 near 0.06, at which point under 4 per cent
are burdened and burden50 collapses to about 0.03. The street is the only thing
separating the two targets and its elasticity is too low.

CANDIDATE SEPARATOR, NOT YET TESTED AND NOT MINE TO ASSIGN: an income floor
rather than the street. Raising ssi_floor_level houses the poor, cutting h_1,
AND puts them in the smallest rental paying over half their income, raising
burden50 -- the two targets move the way each needs, which nothing else does.
It would take ssi_floor_level off h_share5, so the author decides.

## 5 September, 22:22 -- CORRECTION TO THE 22:15 ENTRY BELOW. THE 0.02 BAR WAS WRONG.

The 22:15 entry said four of 31 ladder points were "valid economies" and
withdrew two claims on that basis. The bar it used was arbitrary and the entry
is wrong. MEASURED ACROSS 603 ARCHIVED WORKER LOGS:

    distance_average_labor_income   min 0.00061   p10 0.058
                                    median 0.094  p90 0.189   max 0.637
    under the model's own 1e-4 tolerance:   0 of 603  (0.0%)
    under 0.02:                             5 of 603  (0.8%)

A gap near 0.09 is the NORMAL operating condition of every point ever run here.
A single-pass point run does not drive that distance to zero and never has. If
0.02 disqualified today's ladder points it would disqualify the entire
1,906-point archive equally, so it cannot be what makes today's results special.

WHAT IS ACTUALLY SPECIAL, and this part of the 22:15 entry stands: the far-h3
sweep carries gaps of 0.38 to 0.64, four to seven times the historical median
and beyond the p90 of 0.19. Those points are outside anything this method has
run, and the h3 = 25 accounts are visibly nonsense -- total income 0.131 against
aggregate consumption 913.9 and a rent bill of 1286. So:

- WITHDRAWN AND STILL WITHDRAWN: that the sweep to h3 = 25 refutes the author's
  feasibility argument. It does not. That argument REMAINS UNTESTED.
- RESTORED: rsl = 1.00 lands omega_l on 0.3989. Its gap is 0.093, which is the
  historical median exactly, so it is as sound as anything in the archive. The
  22:15 entry withdrew it for no good reason.
- RESTORED: the normal-ladder points, gaps 0.03 to 0.14, are in the same
  condition as the whole archive and are as trustworthy as the rest of it.

THE FINDING THAT DOES NOT DEPEND ON ANY OF THIS. In every ladder point measured
today, at every gap, the smallest rental holds 4.1 to 8.7 per cent of renters
against the 37.3 per cent the h_3 target implies, and ZERO per cent of its
occupants are cost burdened while 80 to 96 per cent of the largest unit's are.
At h2 = 0.30, not being burdened means income above 0.60, which on the
productivity grid is the top 63.8 per cent of earners: the cheap unit houses the
comfortable and the expensive unit houses the strained. That is inverted from
the data and it is why burden50 reads zero. It holds across a 3.1x range of
ladder level, both voucher settings, and leisure weights from 0.05 to 1.31.

## 5 September, 22:15 -- MOST OF TODAY'S LADDER POINTS ARE NOT VALID ECONOMIES

`distance_average_labor_income` is the gap between the average labour income the
model is indexed to and the one it produces. It sits in the outer equilibrium
loop's own convergence condition with `stopping_rule_average_labor_income =
1e-4`. A point run is a SINGLE PASS -- it exits at `loop_count = 2` through the
b-sweep path -- so that distance is not driven to zero, and it measures how far
the evaluated economy is from its own scale.

OF 31 LADDER POINTS MEASURED ON 5 SEPTEMBER, FOUR COME IN UNDER 0.02:

    h2     h3     rsl    share_h2   omega_l   gamma    gap
    0.12   0.35   1.31   0.0535     0.312     0.390    0.0006
    0.40   0.80   0.60   0.0553     0.258     0.488    0.0055
    0.16   0.35   1.31   0.0485     0.306     0.389    0.0072
    0.22   0.44   1.00   0.0475     0.308     0.424    0.0171

Everything else is outside it, including the WHOLE `relative_share_of_leisure`
bracket that was used to conclude rsl = 1.00 hits omega_l = 0.40 (gap 0.093),
and the whole far-h3 sweep (gaps 0.38 to 0.64).

TWO CLAIMS MADE TODAY ARE WITHDRAWN ON THIS BASIS.

- "Raising h3 cannot price anyone out of the largest unit, refuted decisively by
  the sweep to h3 = 25." The sweep points have gaps of 0.38 to 0.64. At h3 = 25
  the model is evaluated against an income scale 250x the one it generates:
  total income 0.131, total wealth 4.34, aggregate consumption 913.9, a rent
  bill of 1286, labour supply 2e-06. That is not a refutation of anything. The
  author's feasibility argument REMAINS OPEN and has not been tested.
- "rsl = 1.00 lands omega_l on 0.3989." Measured at a gap of 0.093; re-check it.

WHAT SURVIVES. In all four valid points the share of renters in the SMALLEST
rental is 4.75 to 5.53 per cent against the 37.3 per cent the h_3 target
implies, and ZERO per cent of its occupants are cost burdened while 80 to 96 per
cent of the largest unit's are. At h2 = 0.30, not being burdened means income
above 0.60, which on the productivity grid is the top 63.8 per cent of earners:
the cheap unit houses the comfortable and the expensive unit houses the
strained. That is inverted from the data and it is why burden50 reads zero.

RULED OUT AS THE CAUSE, each by measurement rather than by reading the source:
housing vouchers (5.01 -> 5.08 per cent with them off), the fixed cost to moving
(zero), the rent charge in the value function (charged at the true
`future_housing_status_index`, `renter_to_renter_1 = tenure_1 = 1`, and
subtracted in `after_tax_wealth_net_of_expenses`), the utility form (verified as
`housing_size**((1-sigma)*relative_share_of_housing_1)`), the consumption clamp
(choice-side feasibility is strict), the accounting index (true policy index),
the choice set (open), the lump-sum transfer (zero), and phantom housing wealth
for renters (`has_house = 0` kills the term).

WHAT TO DO NEXT, and it is the author's call because it changes how points run:
re-solve each configuration so the income scale is consistent before comparing
ladders. Until then every ladder comparison is confounded by a transfer system
scaled to a different economy, and no housing calibration run on these points
means anything.

## 5 September, 20:35 -- burden50 IS A CONSTANT OF THIS ECONOMY. MY THRESHOLD THEORY WAS WRONG.

I predicted that a street below 15.1 per cent of h2 would make households stretch
rather than leave, moving the cost burden into the smallest rental. The
arithmetic was right about the CHOICE and wrong about WHO FACES IT. Tested at 10
and 5 per cent, both well below the threshold:

    street/h2   h_1          burden50   h2 burdened   h3 burdened
    10%         0.0000059    0.3869     0.126%        39.6%
    5%          0.000000     0.3869     0.126%        39.6%

Homelessness goes to exactly zero and burden50 does not move at all. The by-rung
split is identical to three decimals. The households who stop being homeless do
not move into h2 and stretch -- 97.8 per cent of renters are in h3 and can afford
it comfortably. There is no population at that margin.

burden50 ACROSS FOURTEEN CONFIGURATIONS: 0.3799, 0.3792, 0.3635, 0.3841, 0.3896,
0.3892, 0.3869, 0.3869, 0.5914, 0.7024 ... it moves only with h3, and only
because h3 changes how much housing the 95-99 per cent in the top rung buy. It is
otherwise a constant of this economy at about 0.38.

WHAT burden50 ACTUALLY MEASURES HERE, which is the author's own diagnosis: the 38
to 40 per cent of h3 renters counted as burdened are paying over half their
income for the LARGEST unit. They are not stretched poor households, they are
households buying a lot of housing. That is not cost burden, and matching it to
the SCF's 0.175 is matching the wrong object.

THE BINDING FACT, unchanged and now measured across fourteen points: DIAG
aggregate rent / aggregate income is 0.342 against 0.202 in the data, 69 per cent
too high. No rung size, street size or ladder shape changes a ratio.

WHAT IS LEFT TO TRY, neither of them in the housing block:
  - the rent level itself, pinned at the Himmelberg et al. rent_to_housing_price
    of 0.083 and therefore external data rather than a dial;
  - the income process, where pi_eu reads 4.3 per cent against 13.9 and the
    annual job-loss rate is 0.47 per cent, implying an average job of 213 years.

## 5 September, 20:30 -- CORRECTION, AND A MISLABELLED MOMENT

THE INCOME/EXPENDITURE ANOMALY RECORDED BELOW IS WITHDRAWN. It was built on the
row printed as "UNTARGETED housing over income, renters", and that row does not
measure what its label says.

    model_avg_housing_spending_renters  <-  housing_to_income_renters
    housing_to_income_renters = (rent*size) / (rent*size + consumption)

That is housing over EXPENDITURE, gross of the voucher. It is labelled "housing
over income", compared against 0.202 which is an INCOME ratio, and the Fortran's
own comment beside gamma asserts that "model_avg_housing_spending_renters is
housing over INCOME". The comment, the label and the formula all disagree, and
the target attached to it is on the wrong denominator.

Once that is seen, 0.345 gross-of-voucher against gamma's 0.268 net-of-voucher is
simply what vouchers covering about 22 per cent of rent looks like. There is no
29 per cent excess of expenditure over income, and the stationary-equilibrium
objection I raised against it does not apply.

WHAT SURVIVES, through a correctly labelled row: DIAG aggregate rent / aggregate
income reads 0.342 against 0.202 in the data, still 69 per cent too high. So the
conclusion that burden50 is driven by rent being expensive relative to income
stands; only the route to it was wrong.

TO FIX IN THE FORTRAN, and not done because it changes a printed comparison:
either relabel the row as an expenditure share and give it an expenditure target,
or compute it over total_income and keep the 0.202. The second is what the
comment and the target both assume.

## 5 September, 20:20 -- NO LADDER PARAMETER CAN PUT THE COST BURDEN IN THE SMALLEST RENTAL

The author's requirement: a high utility share on housing, cost-burdened renters
in the SMALLEST rental, and overall housing spending of 26.8 per cent. The first
and third are met. The second is not reachable from the ladder, and this is
measured rather than argued.

h2's BURDENED SHARE IS ~0.0002 IN EVERY CONFIGURATION TRIED:

    h2      0.060, 0.12, 0.16          burdened share of h2 renters 0.2%, 0.04%, 0.00%
    street  0.30, 0.5757, 0.80         unchanged
    h3      0.1864, 0.25, 0.35         0.017%, 0.016%

and raising h3 pushes households OUT of h2 rather than into it: h2's share of
renters goes 6.9 -> 5.4 per cent as h3 goes 0.25 -> 0.35, because housing is a
normal good with a weight of 0.2138 and a bigger top rung is more attractive.

WHY. To be burdened in h2 a household must choose h2 AND pay over half its income
for it. Any household in that position prefers the street: free, and costing
about 40 per cent of consumption in utility at the current sizes, against
surrendering more than half of income. So the burden never lands in h2 -- the
households who would carry it leave instead.

THE TWO INSTRUMENTS ARE COLLINEAR EVEN WHEN INDEPENDENT, measured on the
decoupled ladder:

    d burden50/d h2 = -0.164     d burden50/d h3 = 1.110
    d gamma   /d h2 = -0.359     d gamma   /d h3 = 0.602

    burden50 per unit of gamma:  via h2 +0.456, via h3 +1.845
    needed from h3 = 0.25:       +6.714

The 2x2 asks for h2 -> -0.485 and h3 -> -0.214. Infeasible, and this time it is
NOT the chaining artifact of an hour ago: the rungs are genuinely independent now.

THE BINDING FACT IS RENT RELATIVE TO INCOME, NOT THE SHAPE OF THE LADDER:

    housing / expenditure          model 0.268   data 0.268   AT TARGET
    housing / income, renters      model 0.345   data 0.202   +71 per cent

No arrangement of rung sizes can change a rent-to-income ratio; it can only move
which rung the burden sits in. And rent per unit is not free either --
rent_to_housing_price is pinned at 0.083, the Himmelberg et al. rent-to-price
ratio.

AN ANOMALY THAT SHOULD BE CHECKED BEFORE ANY MORE LADDER WORK. Those two rows
imply income/expenditure of 0.268/0.345 = 0.78 in the model against 0.268/0.202 =
1.33 in the data. The model's households spend 29 per cent MORE than their
income; the data's save 25 per cent of it. A stationary equilibrium cannot have
aggregate expenditure exceeding aggregate income by 29 per cent, so this is
either an accounting mismatch between the two moments -- the burden calculation
divides by a household's own total_income, which may exclude transfers or capital
income that fund the spending -- or a genuine fault. It would explain burden50
sitting at 0.38 to 0.70 whatever the ladder does.

## 5 September, 20:15 -- THE HOUSING LADDER, MEASURED. THREE INSTRUMENTS, THREE MOMENTS

The author's requirement: a high utility share on housing, cost-burdened renters
in the SMALLEST rental, and overall housing spending of 26.8 per cent.

MEASURED, one coordinate at a time, on model 4a12560078 with the taste pinned at
0.268 and delta held at 0.001:

    h2 (bottom rung), street ratio and h3 held
      0.060   h_1 0.000155   burden50 0.3799   gamma 0.2802   emp_homeless 0.000
      0.120   h_1 0.0575     burden50 0.3792   gamma 0.2634   emp_homeless 0.997
      0.160   h_1 0.1425     burden50 0.3635   gamma 0.2442   emp_homeless 0.998

    street ratio, at h2 = 0.12
      0.30    h_1 0.000548   burden50 0.3841
      0.5757  h_1 0.0575     burden50 0.3792

THREE THINGS THE ARCHIVE NOW SAYS.

1. h2 REACHES h_1, NOT burden50. It moved homelessness by a factor of 370 and
   burden50 by 0.2 per cent. The households it strains do not stretch to pay for
   the cheapest rental, they take the street.

2. THE STREET REACHES h_1 HARDER, and only once h2 binds. At h2 = 0.060 it was
   inert because nobody was at the margin; at 0.12 shrinking it 0.5757 -> 0.30
   cut homelessness 105-fold. The author predicted exactly this. h_1 = 0.399 per
   cent interpolates to a street ratio of about 0.40, elasticity 7.14.

3. burden50 IS INVARIANT TO BOTH. It sits at 0.38 across every h2 and every
   street size tried. It cannot be reached from the bottom of the ladder.

WHY, AND IT IS NOT SUBTLE. 95 to 99 per cent of renters are in h3, and 38 per
cent of THEM are burdened; h2 holds 0.9 to 5.1 per cent of renters and 0.0 to 0.2
per cent of them are burdened. The burden is in the TOP rung, which is what the
author diagnosed: *"those spending over 50% have to live in the smallest rental,
not the largest"*. Raising h2 does not fix it -- h2's own burdened share FALLS to
exactly zero as h2 rises, because anyone who would stretch leaves instead.

AND THE 5.7 PER CENT WHO STOPPED BEING HOMELESS when the street shrank did NOT
become burdened renters: burden50 moved 0.3792 -> 0.3841. So the marginal
homeless were never poor. At a street 58 per cent the size of the cheapest
rental and free, homelessness in this model is a GOOD DEAL taken by households
who could afford housing, not a last resort.

THE IMPLIED ASSIGNMENT, to be tested rather than assumed:

    h3, absolute      -> burden50   it decides who is pushed down into h2
    street, absolute  -> h_1        105-fold response, cleanly bracketed
    h2                -> gamma      it sets the rent level most households face

The one h3 measurement that exists agrees: moving the ladder (1.5, 2.0) ->
(2.0, 3.0) at fixed h2 took burden50 0.5947 -> 0.7192. A bracket at h3 = 0.25 and
0.35 is running.

THE STREET IS AN ABSOLUTE LEVEL NOW, on the author's instruction: *"you should
disentangle the homeless size from the smallest rental. it should be free to move
alone"*. It had been housing_size(0)*size_homelessness, so the h2 sweep above
dragged the street 0.0345 -> 0.0921 underneath itself and was never a
one-coordinate measurement. Every old vector carries 0.5757, which as an absolute
size exceeds both rungs, so run_one_point.sh now refuses an inverted ladder.

## 5 September, 19:40 -- WHY THE MODEL DIFFERS FROM THE ORIGINAL PAPER: delta

The author: *"i keep thinking there is some mistake in the code"*, *"my original
paper did not have these issues"*. They are right, and the difference is
homeless_job_penalty_pp.

    real(8) :: homeless_job_penalty_pp=0.d0        <- the declaration
    homeless_job_penalty_pp=0.19945108             <- the live vector

    housed   separation probability   0.004684   (0.47 per cent a year)
    homeless separation probability   0.204135   (20.41 per cent a year)
    MULTIPLIER                        43.6x

A homeless worker loses their job forty-four times faster than a housed one.
That is why emp_homeless reads 0.00005 against a target of 0.46: employed
households are not CHOOSING to leave the street, they are being thrown off it by
a separation hazard.

HOW IT GOT THERE, because it was nobody's mistake in particular. Early today
emp_homeless was 0.82 -- far too many of the homeless were working -- and delta
was pointed at that moment on the author's ruling that it act on separation
alone. The search drove it to 0.199 and it is marked capped. Separately, later,
relative_share_of_housing was pinned at its data value of 0.268, which pushes
working households off the street by a different route: taking the street costs
22.4 per cent of consumption at the honest taste against 7.1 at the old one.

TWO INSTRUMENTS WERE AIMED AT ONE MOMENT AT DIFFERENT TIMES AND BOTH ARE NOW
FIRING. The housing taste alone moved emp_homeless 0.818 -> 0.038 on a
one-coordinate pair, so it can carry the moment by itself. delta is redundant and
overshooting.

RECOMMENDED, NOT DONE, because delta's role is the author's ruling: put
homeless_job_penalty_pp back to 0, the declaration's own value and the original
paper's, and let the housing taste carry emp_homeless.

TWO MORE IN THE SAME CATEGORY, worth checking against the original paper:
lambda_addiction is FROZEN at 0, which is also its declaration default, and that
is why sud_homeless (0.105 against 0.217) has no instrument at all.
rr_homeless_old_level is inert because homeless_death_risk_flat_in_age=2 takes a
branch that never reads rr_homeless_profile, so h_share5 has no instrument
either.

THE STREET CANNOT CARRY THE HOMELESSNESS RATE AT AN HONEST HOUSING TASTE, and
this is measured rather than argued. The street is 0.5757 of the cheapest rental
and h_1 reads 0.000179 against 0.00399, twenty-two times too low. At the old
taste the same street cost 7.1 per cent of consumption and gave h_1 = 0.00469,
near target. To be equally attractive at the new taste the street would have to
be 0.829 of the cheapest rental -- which is not a street. The homelessness rate
has to come from the income process or the safety net, not from the size of the
street.

## 5 September, 19:36 -- THE INFEASIBILITY BELOW IS SUPERSEDED. THE AUTHOR FIXED IT.

The entry immediately below records the two-rung design as infeasible on a
measured Jacobian. That conclusion was correct about the numbers and WRONG about
the cause, and the author found the reason: *"adjust h3 independently of h2"*,
*"just adjust them independently"*.

The two knobs were MECHANICALLY chained, not economically degenerate. h3 was
rung_ratio_h3*h2 -- an overwrite added earlier the same day -- so cutting the
bottom rung cut the top rung with it and both moments fell together. The Fortran
had ALREADY been assigning housing_size(grid_size-1) = largest_house_size, an
independent absolute size; the overwrite is what destroyed it. Restricting that
overwrite to three rungs and above restores two independent levels.

MEASURED, at the SAME h2 = 0.060:

    chained     (h3 = 2.0*h2)         gamma 0.1911   -28.7 per cent
    independent (h3 = 0.1863876)      gamma 0.2726    +1.7 per cent

gamma landed on target at the author's own suggested value -- 1.5 times the
bottom rung's previous level -- with no search at all. burden50 is 0.3717 against
0.175 and now has a free instrument, because lowering h2 no longer drags gamma
down with it.

THE LIVE HOUSING BLOCK:

    smallest_rental_relative_to_lowest_income  ->  burden50  (0.175)   at 0.060
    largest_house_size                         ->  gamma     (0.268)   at 0.1863876

with relative_share_of_housing pinned at 0.268 as data, rung_ratio_h3 held, and
the ladder-inversion guard reinstated in run_one_point.sh because two independent
levels can cross again where a ratio ladder could not.

WHERE THE MODEL IS WORST, on point 95c6ecfcfc: b at 0.799 against 0.089, nine
times target and the worst number in the model; lambda_d 0.131 against 0.037;
lambda_m 0.938 against 0.25. Homelessness is 22 times too rare, 94 per cent of
the homeless carry SMI, essentially none are employed, 90 per cent are aged 26-34
and bands 4 and 5 are empty. sud_homeless reads 0.105 against 0.217 and has NO
instrument, lambda_addiction being frozen at zero.

A bracket on addiction_scalar_1 at 0.0090 and 0.0105 is in flight. The archive's
dense 182-point ray on that parameter puts the whole usable range between 0.007
and 0.010, but it was measured on model 375aed92cf and its LEVELS do not transfer:
the current phi/theta would predict b about 0.25 there against 0.799 here. The
shape transfers, the location does not.

## 5 September, 19:25 -- THE TWO-RUNG LADDER CANNOT HIT BOTH HOUSING TARGETS

MEASURED, one coordinate at a time, three points on model eebe63e443. The author's
design of an hour earlier -- *"set h2 so that the share of spending over 50% of
their income on housing is like in the data ... and choose h3 so that at the
housing spending is 26.8%"* -- is infeasible, and the reason is a Jacobian, not
a search failure.

    base   h2 0.1242584, ratio 2.0   burden50 0.5955   gamma 0.3150
    A      h2 0.060,     ratio 2.0   burden50 0.2185   gamma 0.1911
    B      h2 0.1242584, ratio 1.4   burden50 0.3402   gamma 0.2529

    d burden50 / d h2    =  5.868      d burden50 / d ratio =  0.426
    d gamma    / d h2    =  1.928      d gamma    / d ratio =  0.103
    determinant = -0.2138

BOTH INSTRUMENTS PUSH BOTH MOMENTS THE SAME WAY. Expressed as the change in
burden50 per unit change in gamma, h2 delivers +3.04 and the rung ratio +4.12.
The target, taken from point A, needs -0.57: burden50 must FALL 0.0435 while
gamma RISES 0.0769. Solving the 2x2 asks for h2 -> 0.2341 and a rung ratio of
-0.5030, and the ratio must exceed 1 for two distinct rungs to exist.

THE ECONOMICS, stated so this is not rediscovered. Both instruments work by
changing how BIG the rungs are, and enlarging housing raises aggregate housing
spending and cost burden together. They are one channel wearing two names. The
shape of the ladder cannot separate "how much housing everyone buys" from "who is
priced into paying half their income for it".

THE FRONTIER THE MODEL ACTUALLY OFFERS, which is the useful output of this:

    A   h2 0.060    gamma 0.191 (-28.7%)   burden50 0.218 (+24.8%)
    B   ratio 1.4   gamma 0.253 ( -5.6%)   burden50 0.340 (+94%)

One or the other, not both.

WHAT WOULD SEPARATE THEM is an instrument that cuts rent for the POOR without
cutting housing consumption overall. The housing voucher is exactly that: it caps
rent at 30 per cent of income, which is the cost-burden margin itself, and barely
touches the aggregate share. probability_of_voucher_benchmark_used currently owns
pi_V and sits at target. The other candidate is the lower tail of the income
distribution, kkk_sigma_scale, which owns sigma_y. Both are the author's call and
neither has been changed.

WHAT DID CLOSE, in the same round and worth keeping: beta reads 2.2335 against
its new 2.25 target (-0.7 per cent) and w_bot 0.0228 against 0.025 (-8.8), both
of them closed by pinning relative_share_of_housing at its data value of 0.268
rather than by tuning.

SOLVE TIME at two rentals, -O3, four cores: 174s with the binary cached, and 245s
when a rebuild is included. Not the 1-1.5 minutes hoped for.

## 5 September, 14:40 -- PHASE TWO: theta AND lambda_addiction RELEASED

The author: *"release lambda_addiction and let it move. Also, allow theta to
move up to 0.25. Set the death rate from homelessness to 1.6 across all ages."*

THE DEATH RATE WAS ALREADY 1.6 AT EVERY AGE. `homeless_death_risk_flat_in_age=2`
has been run_one_point.sh's default since 06:20 and takes the branch
`kappa_phi_h_by_age(j) = 1 + increased_risk_of_death_homeless` with the constant
fixed at 0.6 in the Fortran, so the multiplier is 1.6 flat. No change was needed
and none was made.

RELEASED. `relative_share_of_addiction_1` and `lambda_addiction` are out of
FROZEN. theta's ceiling goes 0.20 -> 0.25 in BOUNDS; it is in CAPPED so that
ceiling is ENFORCED. The 0.08 floor is unchanged.

lambda_addiction WAS SEEDED AT 0.2763 AND HERE IS WHY. It sat at 0.0001, and the
step is PROPORTIONAL -- `f * adjuster * min(1,|rel|) * |x|` -- so at a 1 per cent
adjuster it moves 1e-6 an iteration. Reaching a value where the hazard actually
curves would have taken of order a thousand solves, which is the proportional
step trap this file has hit before. Releasing it at 0.0001 would have satisfied
the instruction and defeated it.

THE SEED IS MEASURED, NOT GUESSED. From point f07433cffe:

    DIAG mean drug quantity, users        = 0.067437
    DIAG onset at the mean quantity       = 0.0184656
    addiction_onset_base                  = 0.0184589

so the exponential term contributes 6.7e-06 -- the hazard is the flat base and
nothing else, which is exactly why b and lambda_d moved in lockstep for eighty
iterations. Setting `1-exp(-lambda*v_bar) = base` gives lambda = 0.2763, which
puts the curvature on the same scale as the base and gives the walk gradient in
both directions:

    lambda      light user v=0.035    heavy user v=0.20
    0.0001      0.00000               0.00002
    0.2763      0.00962               0.05376
    1.0         0.03439               0.18127

Applied through `code/fixed_point_override.json`, one-shot. If the author wants
a different starting point it is one number in that file.

theta MOVES SLOWLY AND THE CEILING IS NOT THE BINDING THING. Its adjuster is
0.002 and its gap is 35 per cent, so the step is about 0.07 per cent an
iteration: 0.16 -> 0.25 is roughly six hundred solves. The author asked for slow
adjusters on 5 September and that is what this is; the raised ceiling removes a
bound that was not yet binding rather than speeding anything up.

WHAT THIS IS FOR. sud_homeless is 0.036 against 0.217 and lambda_addiction is
its only bracket. theta is 0.105 against 0.162. Both were unreachable while the
two were frozen.

## 5 September, 06:20 -- THE DEATH RATE IS WORTH 3.6x ON h_1, NOT 30x, AND THE REST IS THE EARNINGS PROCESS

The author: *"then something is very odd about the street....why does it not
raise homelessness? maybe the death rate is too high....try 60% uniform death
rate across everyone"*.

`homeless_death_risk_flat_in_age=2` IS that setting already: it bypasses
Baggett's profile and sets `kappa_phi_h = 1 + increased_risk_of_death_homeless`
with the parameter fixed at 0.6, flat at every age.

WHAT MODE 0 WAS CHARGING. Baggett's ratio divided by the SUD term
`((1-sud_share)+sud_share*kappa_phi_d)` = 1.139 at the best point:

    data age    26     35     45     55     65+
    multiplier  7.99   7.89   5.87   3.88   5.19   (held at rr_homeless_old_level)

An eightfold death hazard on a 26 year old who sleeps rough, against
`value_of_life` 45.35. Multiplying the street's housing service by five --
`size_homelessness` 0.10 -> 0.494 -- moves the HOUSING term and never touches
the MORTALITY term. That is why h_1 sat at 1.5e-4 across a fivefold range of
the street and why `emp_homeless` was identically zero.

THE ISOLATED PAIR, one coordinate, same model 375aed92cf:

    point            a1a0bf3fe6   83ab786033   target
    death mode       0 (Baggett)  2 (flat 1.6)
    h_1              0.000149     0.000543     0.00399
    lambda_m         0.884        0.342        0.25
    emp_homeless     0.0000       0.000062     0.46
    b                0.16451      0.16419      0.089
    lambda_d         0.036469     0.036405     0.0368
    theta            0.11052      0.11044      0.162
    y_u              0.93398      0.93423      0.74

3.6x on h_1, and `lambda_m` -- the worst gap in the whole table at 254 per
cent -- falls to 37. Nothing else moves. Old age homelessness goes to exactly
zero at 65 and above, so `h_share5` is solved rather than fought.

A CORRECTION THAT COST NOTHING ONLY BECAUSE IT WAS CHECKED. The four archived
mode 2 points (0f4dcaa008, 1c4b7759d4, d2e58e6afb) show h_1 at 0.0047 to
0.0161 on streets a tenth the size, which reads as 30 to 100x. They carry
theta near 0.48 and b near 0.037 -- a different drug block on an older model
hash. They were never evidence about the death rate alone. ISOLATE BEFORE
QUOTING A RATIO.

WHERE THE REMAINING FACTOR OF SEVEN IS. Homelessness rate by age band, mode 2
against the data:

    band 1   0.002152    0.003161     within 32 per cent
    band 2   0.000474    0.003378     7x low
    band 3   0.000362    0.002912     8x low
    band 4   0.0000198   0.002496     126x low
    band 5   0.0000000   0.00077      zero

The data's homelessness is nearly FLAT in age. The model's is a young
household's state and nothing else: renter wealth is 0.11 at age 27 and 0.81
by 35, and a household with savings does not take the street at ANY street
size or ANY death rate. 96 per cent of the model's homeless could pay rent out
of income alone.

SO THE BINDING CONSTRAINT IS THE EARNINGS PROCESS, and the Fortran already
says so in the block beside `persistent_income_risk` (line 28925): a Gaussian
AR(1) at rho 0.98 puts a one-in-a-hundred ten year path at 0.37 times
earnings, *"a bad decade and not a catastrophe. The rare large fall is the
thing that would put a middle-aged household with savings onto the street, and
it needs a mixture innovation rather than a normal one."* `persistent_income_risk`
is 0 in the live vector AND its branch also requires `fixed_productivity==1`,
which is 0, so the channel is off twice over.

A MIXTURE INNOVATION IS A MODEL CHANGE AND THE AUTHOR'S CALL. Not started.

WHAT CHANGES IF MODE 2 IS ADOPTED. `rr_homeless_old_level` becomes INERT --
the profile is bypassed entirely -- so it must be FROZEN, and `h_share5` loses
its instrument. `homeless_death_risk_flat_in_age` is already a CONFIG_SWITCH,
so adopting it repartitions the archive and the 20 points on 375aed92cf at
mode 0 stop being comparable.

IN FLIGHT: mode 2 with the street back at 0.10, to test whether the street
bites now that the mortality term is off it.

# Calibration state -- 5 September, 06:00

## THE SUD RATE IS HIT. point c2e94c7aa0, b = 0.007, street 0.275

    moment            model    target     gap
    lambda_d         0.0362    0.0368    -1.6 per cent   ON TARGET
    b                0.1635    0.0890    less than 2x, and bracketed
    sud_homeless     0.0098    0.2170
    h_1              0.00010   0.00399
    emp_homeless     0.0000    0.4600

lambda_d ON TARGET SETTLES THE BASE QUESTION. The author asked to raise
addiction_onset_base because too few carried the disorder; it does not need
raising at b = 0.007. It looked short at b = 0.01 only because b had crushed the
drug population there -- lambda_d ran 0.0030 to 0.0117 on the three points at
that b. At 0.007 the base at 0.01765 delivers the rate on its own.

THE USE RATE IS BRACKETED AND CLOSE. b runs 0.407 at 0.005, 0.1635 at 0.007, and
0.0118 to 0.0461 at 0.01, so 0.089 sits between 0.007 and 0.01. The three points
at 0.01 disagree with each other -- 0.046 against 0.0118 and 0.0122 -- which is
the near-discontinuity in this region rather than solver noise, so a single
reading near the crossing should not be trusted.

## h_1 IS UNRESPONSIVE TO ITS OWN INSTRUMENT, ACROSS A FACTOR OF THREE

    street          0.100   0.153   0.167   0.275
    h_1           0.00002- 0.00010 0.00010 0.00010
                  0.00029

Nearly threefold in size_homelessness and the homelessness rate does not move
off 1e-4, forty times below its 0.00399 target, with emp_homeless identically
zero on every new-model point because there is effectively nobody on the street.
The author raised the cap from 0.1 to 0.30 for exactly this and it changed
nothing.

THIS IS NOW THE BINDING PROBLEM. Two of the author's three targets are in reach
-- the SUD rate is hit and the use rate is within a factor of two -- and the
third is not responding to the only instrument pointed at it.

## THE TWO-PHASE PLAN, STILL RUNNING

Held: relative_share_of_addiction_1 = 0.16, lambda_addiction = 0.0001, M = 4,
bottom_productivity_level. Free: addiction_scalar_1, addiction_onset_base,
size_homelessness and the rest of the calibration. Phase two releases theta and
lambda once the use rate and the SUD rate are landed.

NOTE THAT THE REST OF THE MODEL IS NOT STILL. kappa_uem, value_of_life,
smi_onset_level, mu_homeless, discount_factor and a dozen others walk every
iteration, so a change between two consecutive points is not attributable to b
alone. That is why the isolated brackets were worth the wall clock.

# Calibration state -- 5 September, 05:40

## THE b BRACKET. sud_homeless IS HUMP-SHAPED IN b AND PEAKS ON TARGET

Five points, theta held at 0.16 and lambda_addiction at 0.0001 throughout, only
addiction_scalar_1 varying:

    b param    b     lambda_d  theta   sud_hl    h_1     assets_u   y_u
    target   0.089   0.0368    0.162   0.217    0.00399   0.454     0.740
    1e-06    0.968   0.158     0.131   0.046    0.00043   1.047     1.011
    1e-06    0.969   0.166     0.132   0.046    0.00063   0.964     1.010
    1e-05    0.970   0.158     0.133   0.223    0.00009   1.027     1.010
    1e-04    0.961   0.156     0.133   0.189    0.00010   0.954     0.991
    1e-03    0.830   0.140     0.132   0.096    0.00010   0.611     0.849

sud_homeless runs 0.046 -> 0.223 -> 0.189 -> 0.096 and the 0.217 target sits
between 1e-5 and 1e-4, so b is about 3e-5. THAT MOMENT WAS EXACTLY ZERO ON
ESSENTIALLY EVERY ONE OF THE 1618 POINTS BEFORE THE HAZARD CHANGE.

THE TWO 1e-06 POINTS AGREE to three figures on b and on sud_homeless, so the
readings are solid rather than solver noise.

## THREE THINGS THE BRACKET SETTLES

  1. b THE MOMENT IS NOT CONTROLLED BY b THE PARAMETER in this region. Three
     orders of magnitude move the drug share 0.97 -> 0.83 against a target of
     0.089, a gap of +979 per cent that is now the binding moment. Its handle
     has to be theta, in phase two.
  2. b TRADES sud_homeless AGAINST THE POVERTY OF USERS, and they want opposite
     ends of the range. Only 1e-3 moves assets_u toward the 0.454 benchmark
     (0.611, against about 1.0 everywhere else) and y_u toward 0.740 (0.849),
     and it costs half the SUD share of the homeless.
  3. h_1 IS 0.0001 AND emp_homeless IS EXACTLY 0 ON ALL FIVE. The street is
     empty whatever b does, so the whole bracket is composition over a
     population that barely exists. size_homelessness has to climb before any of
     these numbers mean much; it is free, not frozen, and was only idle because
     the loop was stopped for the bracket.

# Calibration state -- 5 September, 05:20

## THE AUTHOR'S TWO-PHASE PLAN FOR THE DRUG BLOCK

*"i would suggest to keep theta fixed at 0.13 and lambda at 0.05 until at least b
and the base have converged"*, then *"first, set theta to 0.16 or so, lambda to
0.0001, and just look for b and the base that give something good"*, then *"once
you have users and SUD, you can start adjusting theta and lambda"*.

PHASE ONE, live now. Held: relative_share_of_addiction_1 = 0.16,
lambda_addiction = 0.0001, M = 4, bottom_productivity_level. Free:
addiction_scalar_1 starting at 1e-6 and addiction_onset_base at 0.017625. The
search is over two parameters, not four.

PHASE TWO, once there are users and SUD: unfreeze theta and lambda and adjust
them against theta and sud_homeless.

WHY TWO PHASES. Moving four drug parameters at once produced point d13fce142f,
where theta hit its 0.200 ceiling, the drug population emptied, and b, lambda_d,
sud_homeless, mu_H, y_u, kappa_ued and tau_u ALL read exactly zero.

## THE -1 SENTINEL WAS BEING SCORED AS A VALUE

That same point returned theta = -1, the empty-population sentinel, and gap()
computed |-1 - 0.162|/0.162 and reported -717.3 per cent. With the structural
zeros beside it the LOSS read 56.8 against 74.1 on the point before, so a dead
economy looked like progress. ENGINE.md states the rule in the worker brief --
*"a MOMENT theta of -1.0 is an empty-population sentinel, not a value"* -- and
nothing in the code enforced it. gaps.load now drops it.

A dropped moment is a free pass, which is its own trap and the reason
measure_child_gap is a CONFIG_SWITCH. It is still a far smaller lie than minus
seven hundred per cent, and the zeros beside it already mark the point.

## THREE FLOORS LOWERED, ALL SILENT CLAMPS

    relative_share_of_addiction_1   0.25 -> 0.05 -> (0.08, 0.20), ceiling ENFORCED
    lambda_addiction                0.05 -> 0.001 -> 1e-6
    addiction_onset_base            new, (0.001, 0.95)

Each had been clamping an override with only a log line to say so.

## kappa_uem NOW OWNS ITS OWN MOMENT

The SMI employment rate, target 0.30, out of UNSCORED. lambda_m loses its
instrument and becomes an outcome: over 56 pairs differing only in kappa_uem,
the elasticity of lambda_m is +0.82 where h_1 is far below target and -0.07
where the street is real, with the ruled sign on 47 per cent of pairs there.

# Calibration state -- 5 September, 05:10

## THE HAZARD CHANGED. base + (1 - exp(-lambda v)), AND THE ARCHIVE RESET

Model 375aed92cf. addiction_onset_hazard is now

    v > 0 :  min(addiction_onset_base + (1 - exp(-lambda*v)), 1)
    v = 0 :  0

Both required builds pass. REGRESSION: at base=0 the new source reproduces the
old to a max relative difference of 2.5e-4 against the model's OWN run-to-run
variation of 2.4e-2 max and 1.4e-3 median on the same vector -- about 100 times
smaller, so the change is inert by default. Bit-identity was never available:
the solver is OpenMP-parallel with non-deterministic reductions.

## WHY SMI ALWAYS WORKED AND SUD NEVER DID

On 559 archived points with a REAL street (h_1 within 2x of target):

    moment                          median    target    within 20% of target
    lambda_m  SMI share of homeless  0.138     0.250     105 of 559
    sud_homeless SUD share           0.012     0.217     --

Eleven times worse relative to target, on the same points, with the same shape
of instrument. The cause is the one the author named: SMI onset is EXOGENOUS,
smi_onset_level drives p_m and nothing about the household's choices gates it,
so the mentally ill appear across the whole wealth distribution including the
bottom where homelessness happens. SUD onset required USE, use required
consumption above a threshold, and the threshold selected users from the TOP.
The baseline gives SUD the same exogenous component SMI has always had.

## THE SCHEME, ALL THE AUTHOR'S

    moment                        instrument                      direction
    lambda_d   SUD rate           addiction_onset_base            lower
    sud_homeless SUD of homeless  lambda_addiction                RAISE
    b          share who use      addiction_scalar_1              raise
    theta      drug spending      relative_share_of_addiction_1   lower
    lambda_m   SMI of homeless    kappa_uem                       lower
    h_1        homelessness       size_homelessness               lower

  * M FROZEN AT 4. Its own moment agrees: kappa_ued is 0.213 against 0.1625 at
    M=4, where it hit +390 per cent when M ran to 32.
  * bottom_productivity_level FROZEN, exogenous. emp_homeless becomes an outcome
    of the composition rather than a targeted moment.
  * lambda's direction is RAISE and it acts through GENERAL EQUILIBRIUM -- it
    moves quantity per user, which moves who uses, which moves the wealth
    distribution of users, which moves who is homeless. The sign is local.

## THE SEED IS A FLOW, NOT A STOCK

addiction_onset_base starts at 0.017625, from onset*(1-s) = recovery*s with
s = 0.0368/0.089 = 0.41348 and probability_of_stopping_addiction = 0.025. The
first seed of 0.134 was NSDUH's share of light users who CARRY a disorder -- a
prevalence -- and would have overshot the hazard about eightfold.

## THREE FLOORS CAME DOWN, ALL OF WHICH HAD BEEN BLOCKING THIS REGION SILENTLY

    relative_share_of_addiction_1   0.25 -> 0.05 -> now (0.08, 0.20) CAPPED
    lambda_addiction                0.05 -> 0.001
    addiction_onset_base            did not exist -> (0.001, 0.95)

Each clamp was silent: an override to 0.16 became 0.25 with only a log line
saying so. theta's CEILING is enforced, the one exception to the author's
free-movement rule, because a theta at 0.48 made drugs half the Cobb-Douglas
weight and flooded the model with users.

## ADJUSTERS SIZED BY MEASURED ELASTICITY, NOT BY DISTANCE

    addiction_scalar_1              -8.74 on b     0.002   about 1.7% a step
    relative_share_of_addiction_1  +13.17 on b     0.002   about 2.6%
    addiction_onset_base            ~1 on lambda_d 0.010   about 1%
    lambda_addiction                GE, unmeasured 0.010

## OPEN

  * The data force a SECOND homelessness channel. 54 per cent of the homeless
    are jobless and 21.7 per cent carry a SUD, so at least 32 points of that 54
    must be unemployed NON-SUD households. lambda selecting the disordered onto
    the street cannot deliver emp_homeless on its own.
  * y_u, the income of drug users, is the expected casualty as users get poorer.
    The author: the death penalty pinned at 8 is the lever if it collapses.
  * lambda has no independent moment of its own. Its natural target is the SUD
    rate BY USE INTENSITY, which NSDUH 2024 gives directly -- 0.134, 0.428,
    0.577, 0.717, 0.819 across the five frequency categories, hard drugs pooled
    -- but the model reports no gradient to compare against.

# Calibration state -- 5 September, 04:35

## THE LOW-b LOW-THETA COMBINATION DOES NOT PRODUCE POOR USERS

The author's hypothesis was that theta is far too large -- drugs carry 48 per
cent of the Cobb-Douglas weight in the live branch -- so any b small enough to
let the poor use floods the whole population, and that cutting BOTH would leave
only the asset-poor using. Tested at theta weight 0.1586 with b = 0.001
(point 4ffe834aed):

    b (share who use)      0.9177   target 0.0890
    theta (share spent)    0.0138   target 0.1620
    assets of users        0.8299   benchmark 0.454
    h_1                    0.00006  target 0.00399

92 PER CENT USE AND THEY SPEND 1.4 PER CENT OF CONSUMPTION ON DRUGS, and their
assets are FURTHER from the benchmark than before, not closer. The mechanism is
what (b+v)^theta gives with a tiny b: the first infinitesimal quantity carries
almost all the value, so everybody takes a sip. A small b flattens the
consumption threshold for EVERYONE equally rather than tilting it toward the
asset-poor. The low b overwhelms the low theta instead of complementing it.

CAVEAT ON THE HOMELESS STATISTICS. h_1 is 0.00001-0.0001 on every one of these
points, so "unemployed share of the homeless = 1.000" and sud_homeless are
statistics over a handful of households, not results. The street is too small in
these vectors for either number to mean anything.

## THETA AND b ARE NEARLY UNIDENTIFIED, AND THE AUTHOR SAW IT FIRST

*"i think there may be several places where theta and b give the same numbers"*.
Median elasticities from isolated archive rays:

                                     b      theta   lambda_d    y_u   sud_hl
    addiction_scalar_1            -8.74     -1.24     -11.54   -0.05   -7.23
    relative_share_of_addiction_1 +13.17    +4.11     +16.73   +0.62  +11.28

The angle between the two parameter response directions is 9.2 degrees on
(b, theta), 1.1 on (b, lambda_d), 2.3 on (b, y_u) and 1.0 on (b, sud_hl). They
are near-collinear on every scored moment, so different (theta, b) combinations
really do give the same numbers.

THEY SEPARATE ON WEALTH, which is also the author's: *"the difference is who is
using drugs -- low asset people in the low b low theta case and high asset people
in the high b high theta case"*. Along the ISO-b ridge, where the share who use
is held fixed, dln(assets of users) = -2.39 + 5.04*0.664 = +0.96 per unit
dln(addiction_scalar_1) -- an order-one response, and the only one available.

THERE IS A TARGET FOR IT. data/SUD_WEALTH.md imputes median wealth of $95,470 for
hard-drug SUD against $210,240 for all adults, a ratio of 0.454. The model runs
0.77 to 0.95. Mean-over-mean against median-based, so the levels are not strictly
comparable, but a factor of two is beyond that caveat. ADDING IT AS A SCORED
MOMENT WOULD IDENTIFY THE PAIR; that is the author's call, not a thing to do
overnight.

## TWO PARAMETERS ARE NOW EXOGENOUS

  * M frozen at 4: *"first fix M=4 so that we are aligned with the data"*, and it
    moved sud_homeless not at all over 69 isolated pairs.
  * bottom_productivity_level frozen: *"i think the bottom productivity should be
    set exogenously"*. It owned emp_homeless and never moved it -- the moment sat
    at +110 to +115 per cent on every point tonight.

emp_homeless therefore has NO instrument, pending the author's plan to give it to
M: *"we can adjust M to match the share of the homeless who are unemployed"*.
sud_homeless would then have none either, which is honest under that scheme --
it becomes an outcome of theta and b rather than a separately targeted moment.

## THETA'S FLOOR WAS HIDING THE REGION

BOUNDS was (0.25, 0.60) and an override to 0.16 was CLAMPED to 0.25 with only a
log line saying so. Lowered to (0.05, 0.60). The floor existed because theta
returns the -1 empty-population sentinel when nobody uses; that is still a live
risk at low theta and a -1 must not be scored as a value.

# Calibration state -- 5 September, 04:20

## sud_homeless CAME OFF ZERO. b IS THE KEY, AND THE AUTHOR CALLED IT.

point_d0873c90f1, addiction_scalar_1 = 0.01785, street = 0.1155, M frozen at 4:

    sud_homeless   0.31065   target 0.21700   +43.2 per cent
    b              0.85472   target 0.08900   +860.4
    lambda_d       0.49988   target 0.03680   +1258.4
    h_1            0.00011   target 0.00399   +97.2
    emp_homeless   0.00000   target 0.46000   +100.0
    loss 247.15, 6 of 23 inside ten per cent

sud_homeless has been EXACTLY ZERO on every point all night and is now above its
target. It is not structurally unreachable and no labour-market instrument was
ever going to do it: the consumption threshold in b_shifter was the whole story,
as the author said from the start.

## BUT 0.01785 LANDED ON THE WRONG SIDE OF THE CLIFF

85 per cent of the population now uses drugs. The archive holds points at
0.0147-0.0192 with b near 0.09 AND points at the same values with b near 0.95;
which side you land on depends on the rest of the vector. This one went high.

THE FIX IS SMALL, and the elasticity gives it directly: b must fall by a factor
of 9.6, ln(9.6) = 2.26, over an elasticity of -21, so the parameter rises about
11 per cent -- to roughly 0.0199. NOT back to 0.03.

h_1 at 0.00011 says the street at 0.1155 is still too small for this vector and
has to come up with it.

## WHAT THE 3 PER CENT STREET COST

Five solves, points 9-13, all degenerate at loss 3.2e20 to 4.3e20. At a street of
0.03-0.046 nobody is homeless at all, so mu_H (recovery housed over recovery
homeless) and emp_homeless both divide by zero. The walk was climbing the street
back on its own -- 0.0317, 0.0349, 0.0384, 0.0422, 0.0464 -- when the override to
0.105 finished the job.

## THE ADJUSTER, TWICE WRONG IN ONE NIGHT

0.02 -> 0.05 in a batch of "crawling instruments", which was wrong: at an
elasticity of -21 a 5 per cent step moves the drug share 100 per cent.
0.05 -> 0.002 on the measurement, which is too slow the other way: an 11 per cent
move takes 55 iterations, nearly three hours. 0.005 is the size that matches the
job -- about 10 per cent moves in the drug share, ~22 iterations.

# Calibration state -- 5 September, 04:15

## addiction_scalar_1 IS THE KNIFE EDGE, AND sud_homeless IS REACHABLE AFTER ALL

The author, 5 September: *"i remember that i actually had b being very small,
around 10^(-6)"*, *"i adjusted it very slowly in the past"*, *"it might need to
be very small"*, and then *"that would make the users also poor"*. All four are
borne out by the archive's 1618 points, whose addiction_scalar_1 spans 1e-30 to
0.25.

`b_shifter = addiction_scalar_1` (line 7392) and it enters the drug utility as
`(b + v)^theta` with v the QUANTITY consumed. A large b means a household needs a
lot of drug before using is worth anything, so only high-consumption -- rich --
households cross. That is the selection that keeps SUD households off the street.

**HOW MANY USE, AS THE PARAMETER FALLS**

    addiction_scalar_1     b = share who use     (target 0.089)
        1e-30                    0.9999
        9.2e-03                  0.73 - 0.78
        1.2e-02                  0.88
        1.47e-02 - 1.92e-02      0.08 - 0.12      <-- the workable window
        3.44e-02 (live)          0.075

SO IT CANNOT GO TO 1e-6. Below about 0.012 the whole population uses. The window
is roughly HALF the live value.

**THREE THINGS ABOUT THAT WINDOW**

  1. sud_homeless IS REACHABLE THERE. At 1.469e-02, point 0a25208049 has
     sud_homeless 0.582 with b 0.094, lambda_d 0.038 and h_1 0.0034 -- three
     moments on target at once. It is NOT a structural zero, which is what the
     earlier note left open.
  2. IT IS VIOLENTLY SENSITIVE. At the single value 1.4689e-02 the archive holds
     b = 0.0004, 0.0054, 0.029, 0.092, 0.398, 0.632 and 0.951 -- nothing to
     everyone, at the same parameter, driven by the rest of the vector. This
     parameter sets a knife edge; it does not pin the drug share.
  3. THE AUTHOR'S OBJECTION HOLDS. Income of working-age drug users is about
     0.35 against a target of 0.74 across the WHOLE window, and 1.005 at the live
     value. y_u's target sits between, so the b that gets the right NUMBER of
     users makes them all too poor.

**AND THE 3 PER CENT STREET IS PAST THE EDGE.** The two points solved at
size_homelessness 0.0317 and 0.0349 have loss 3.2e20 and 3.4e20, worst gap
1.8e21 per cent on mu_H -- recovery housed / recovery homeless, whose denominator
goes to zero when nobody chooses the street. Not a bug; the experiment saying 3
per cent is too far. The archive's good points sat at 0.105.

# Calibration state -- 5 September, 04:10

## THE AGE-80 SUD SPIKE IS max_age_to_choose_addiction, AND IT IS THE AGE-84 ARTEFACT AGAIN

`max_age_to_choose_addiction = 55` (line 491), and data age = 25 + age_index, so
index 55 is DATA AGE 80 -- exactly where the spike sits:

    SUD rate   79: 0.00104   80: 0.22376   81: 0.00184   (85ec3e553f)
               79: 0.00000   80: 0.22605   81: 0.00128   (31fafe39e7)
               79: 0.52157   80: 0.84171   81: 0.03285   (97c5e30de6)

Age 80 is the LAST age at which addiction may be chosen. The choice set changes
discontinuously at that one age and the policy function jumps there. Identical in
shape and cause to the age-84 homelessness spike, which was
max_age_to_choose_homelessness=59 and went away at 58 without relocating to 83.

IT CANNOT BE FIXED THE SAME WAY. max_age_to_choose_homelessness is a HANDOVER
variable settable per solve; max_age_to_choose_addiction is `integer, parameter`,
a compile-time constant. Changing it edits the Fortran, which ENGINE.md freezes,
so it is the author's call.

WHAT IT CONTAMINATES: lambda_d (the disorder rate) and every "users aged 65 plus"
moment take mass from a single spurious age.

## THE AUTHOR'S TWO HYPOTHESES, BOTH DISCONFIRMED

  * *"maybe you are not shocking those with SUD or SMI with unemployment"* --
    they are, and harder than the data: kappa_ued runs 0.23 to 0.80 against a
    target of 0.1625, so SUD households are MORE unemployed than in the data.
  * *"maybe you are not allowing them to actually choose homelessness"* -- the
    loop is `do future_housing_status_index = allow_to_choose_homelessness*
    lowest_housing_grid_point, largest_house_size_hhld_can_rent` at 19322 and
    21320, with lowest_housing_grid_point = -1, and
    allow_to_choose_homelessness depends ONLY on
    `age_index > max_age_to_choose_homelessness`. No dependence on the addiction
    or SMI state anywhere. The street is offered to everyone under the age cap.

# Calibration state -- 5 September, 04:05

## sud_homeless HAS NO INSTRUMENT, AND IT IS NOT FOR WANT OF LOOKING

Two isolation tests on the archive, pairs differing in ONE coordinate:

  * **M: 69 pairs.** sud_homeless is 0.000010 at M=1, 0.000003 at M=4 and
    0.000002 at M=32, while b collapses 0.234 -> 0.004 across the same range. M
    is a strong DETERRENT on the choice to use and no handle on who is homeless.
    Frozen at 4 on the author's instruction.
  * **size_homelessness: 331 pairs.** sud_homeless does not move at all --
    0.00000 -> 0.00000 from a street of 0.0425 to 0.07, 0.00000 -> 0.00004 up to
    0.22. THE EARLIER CLAIM THAT SHRINKING THE STREET RAISES IT WAS WRONG: the
    high-sud_homeless points differ from the current economy in the rental floor
    and kappa_uem as well, and the effect was attributed to the street without
    isolating it. Same mistake as the delta ray's baseline.

## WHAT IS RULED OUT AS A BUG

  * The accumulator is correct: val_homeless_sud_band uses the same
    `housing_status_index_used==lowest_housing_grid_point` test as
    val_homeless_band, and the same `unemployment_index>threshold_addiction_index`
    test as val_sud_band (~17640).
  * The printed aggregate equals sum(band share x SUD share in band) exactly on
    every point checked.
  * `can_consume_drugs` is set to 1 unconditionally at every site -- vestigial.
  * NOT mechanically disjoint. threshold_addiction_index = 3*number_of_smi_states
    = 6 splits a 12-state index into a non-disordered block 1-6 and a disordered
    block 7-12, with emp_of (1 employed, 2 nothing, 3 on UI) running WITHIN each.
    Employed-and-disordered is a real state and 20.5 per cent of SUD households
    are employed.

## WHAT IS STILL ODD

Among the 93.6 per cent of homeless aged 26-34 the SUD share is EXACTLY 0.0,
while 5-8 per cent of that age group carries the disorder. Independence would
give a small positive number.

The leading non-bug explanation is strict selection, and it is the author's own:
homelessness is chosen at one corner -- zero wealth, a particular productivity
node -- and the consumption threshold gating drug use means no disordered
household occupies it. If that is right, sud_homeless is unreachable by ANY
instrument until the threshold lets poor households use, which is
addiction_scalar_1 downward, and no labour-market parameter will ever do it.

## A PROBABLE BUG, NOT TRACED: THE AGE-80 SUD SPIKE

    SUD rate   79: 0.00104   80: 0.22376   81: 0.00184   (85ec3e553f)
               79: 0.00000   80: 0.22605   81: 0.00128   (31fafe39e7)
               79: 0.52157   80: 0.84171   81: 0.03285   (97c5e30de6)

A 200-fold spike at exactly age 80, reproducible across points and economies.
Same single-age-discontinuity shape as the age-84 homelessness spike, which was
an end-of-horizon artefact fixed by max_age_to_choose_homelessness=58.

## LATENT: emp_homeless HAS TWO TARGETS IN THE SOURCE

`employed_share_of_homeless_data=0.50` (line 1330) drives the rho_d loop at
~40020; `0.460d0` is printed on the MOMENT line at 6813 and is what gaps.py
scores. include_rho_d=1 but rho_d is pinned at 1.0 on the author's instruction,
so the 0.50 branch is not biting. A second copy of a constant, which is how
three other faults started tonight.

# Calibration state -- 5 September, 03:45

## THE ECONOMY RESTARTED AT rr_homeless_hold_age=64. FOUR POINTS, AND THE LOSS IS RISING

Like-for-like over the same 23 scored moments, in solve order:

    #  point         loss    worst   in 10%       M      rr
    1  85ec3e553f    4.81   115.7%    7/23    4.505   2.867
    2  31fafe39e7   12.34   276.8%    7/23    4.505   8.000
    3  05337a267d   14.57   283.8%    8/23    6.757   7.831
    4  8d1ce8987d   14.78   299.0%    7/23   10.131   7.667

## THE WALK ANCHORED ON THE WRONG SEED, AND THE CRITERION CANNOT SEE WHY

gaps.py ranks on the STAGE-0 set of 16 moments and picks 31fafe39e7 at 2.5879.
That point carries rr = 8.0, which drives h_share5 to exactly 0.00000 against
0.075 -- and h_share5 IS NOT IN THE STAGE-0 SET, so the ranking cannot see the
damage. On the full 23 moments 85ec3e553f (rr = 2.867) is better, 4.81 against
12.34. The loop is walking away from the better of its two seeds.

This is the same shape as every other fault tonight: a criterion evaluated over
one set while the consequence lands in another.

## M IS NOT A HARD INSTRUMENT, IT IS A SELF-DEFEATING ONE

The author asked how to make SUD households homeless, and whether M only works
once b is low enough. The four points answer both:

       M   addiction_scalar_1   lambda_d       b   kappa_ued   sud_homeless
   4.505             0.036226     0.0261  0.0695       0.277         0.0000
   6.757             0.035830     0.0011  0.0072       0.423         0.0003
  10.131             0.034183     0.0025  0.0128       0.566         0.0053
  target                          0.0368  0.0890       0.1625        0.2170

RAISING M DESTROYS THE POPULATION THE MOMENT IS A SHARE OF. b falls to a fifth,
lambda_d to a tenth, while sud_homeless creeps from 0 to 0.005 against 0.217.
Drug use is a CHOICE: make the disorder catastrophic for employment and
households stop choosing it. And M has overshot the one thing it does control --
kappa_ued 0.277 -> 0.566 against a target of 0.1625 -- so M should come DOWN.

THE AUTHOR'S READING ON b IS RIGHT AND THE MODEL SHOWS THE SELECTION. Use needs
consumption above a threshold, so users are selected RICH: band 1 users have
income 2.08 times average. Bands 2-4 users are poor, 0.40-0.46 of average, and
100 per cent of them carry the disorder -- but there are almost none. The SUD
rate by income band is 0.001-0.009 against data of 0.05-0.14, so the model has
one to two per cent of the disorder population the data has, at every income
level.

21.7 per cent of the homeless cannot carry a disorder when 0.25 per cent of the
population has one. THE LEVEL COMES FIRST -- lambda_d at -29 per cent and b at
-22 per cent, via lambda_addiction and a LOWER addiction_scalar_1, which drops
the consumption threshold and lets poor households into the user pool.
sud_homeless is a composition moment and cannot be reached before the population
exists.

## TWO THINGS PUT TO THE AUTHOR AT 03:45, BOTH OPEN

  1. Bring M down; its own moment says so.
  2. Re-anchor the walk on 85ec3e553f rather than the rr = 8.0 point.

## AND THE OLD-AGE SPIKE RELOCATED RATHER THAN CLEARING

With the hold at 64 the penalty reaches age 65 -- homelessness there falls from
0.008693 to 0.000062 -- but the mass reappears at ages 63 and 64, just below the
new boundary. The spike follows whichever age the penalty starts at. h_share5 is
now 0.0002 to 0.0000 against 0.075, so rr has overshot hard in the other
direction and 8.0 is far too high.

# Calibration state -- 5 September, 03:30

## THE PROOF: EVERY OLD HOMELESS HOUSEHOLD IS AT EXACTLY AGE 65

The author's mechanism -- *"the death penalty for the old will remove the old
from being homeless...and delta will remove the workers"* -- is right in logic
and blocked by one year of indexing. Three points at delta = 0.30 differing in
NOTHING but `rr_homeless_old_level`, age profile of the homelessness rate:

    age    rr=2.867     rr=4.0      rr=8.0
     63    0.000001    0.000001    0.000001
     64    0.000038    0.000038    0.000038
     65    0.008693    0.008693    0.008693
     66    0.000000    0.000000    0.000000
     ...
     85    0.000000    0.000000    0.000000

    f56a40b55d (2.867), 45083d5a07 (4.0), 81f55164ad (8.0)

Ages 66-85 are ALREADY EMPTY, so tripling the death hazard changes nothing at
any age to six decimals. The entire old-homeless mass is at age 65, and
`rr_homeless_hold_age=65` replaces the profile only ABOVE 65. The instrument
cannot reach its own population at any multiplier -- it is not too weak, it has
nothing left to act on.

AND THEY ARE NOT RETIREES. Retirement begins at `life_span-retirement_span+1` =
age_index 41 = data age 66, so age 65 is the LAST WORKING YEAR: no wage floor
behind it, no Social Security in front of it. The whole old-homeless population
sits in that one-year gap.

WHY THE RAY MISLEADS. y_h rising with delta is measured with rr held fixed, and
the author's objection is correct in principle -- in the joint calibration rr
should rise and clear the retirees. It cannot, for the reason above, so the ray
is measuring the mechanism with one half disabled. The ray is right about what
it measured and wrong as a guide to the mechanism.

THE FIX IS ONE INTEGER: `rr_homeless_hold_age` 65 -> 64, so the penalty covers
65+. Measured at fixed delta: band 5 0.0299 -> 0.0002, y_h 0.2614 -> 0.2458, h_1
barely moves. Cost: it is a CONFIG_SWITCH, so the 669 points measured at 65 stop
pooling and the archive restarts. THE AUTHOR'S CALL, still open.

## DELTA: THE RULING STANDS, FLOORED AT 0.01

Flipped to 'lower' on the ray and reverted the same hour -- *"no...delta is
moving in the wrong direction!"*. The ruling is the authority and the
measurement is a check; the flip broke that convention and it is restored.
Floored at 0.01 rather than 0 on the author's instruction, because a
proportional step cannot leave zero and a delta that reached it would be pinned
there whatever its gap did.

# Calibration state -- 5 September, 03:40

## THE DELTA RAY, CORRECTED -- AND A FABRICATED NUMBER IN A TABLE SHOWN TO THE AUTHOR

**The error first.** In the sorted gap table shown at 03:20 the y_h row was
printed by gaps.py as

    y_h  +275.4%  0.71707  0.19100  homeless_job_penalty_pp  0

and it was retyped by hand as `0.3025`, the LIVE TRACE value from a different and
still-unsolved vector. The best point `d0029f2b64` carries
`homeless_job_penalty_pp=0`; its moments are h_1 = 0.0035300, band 5 = 0.074176,
y_h = 0.717068. There is no point in the archive with delta = 0.25 and those
moments. The author caught it immediately: *"you showed me a delta of 0.25 with
y_h being 0.717, h1 giving 0.35% homelessness and h_share5 around 7.4%"*.

This is the rule against mixing points inside one table, broken in the smallest
possible way -- one cell -- and it made the model look as though delta did
something it has never done. A parameter value in a gap table comes from THE
POINT, never from the trace.

**The ray was also mis-built.** Its baseline was a delta=0.05 point differing from
the rest in TWELVE other coordinates. Rebuilt over six points identical in every
coordinate except delta:

    delta   tag              y_h        h_1    band1    band5
     0.00   43932f4d10    0.2614   0.004651   0.9080   0.0299
     0.05   2c40bae9b4    0.7105   0.002457   0.0120   0.0529
     0.15   a43cb9b416    0.7362   0.000299   0.1235   0.4465
     0.25   b24474cff8    0.7242   0.000153   0.0627   0.9354
     0.30   f56a40b55d    0.6892   0.000184   0.2003   0.7759
     0.55   59a64035ad    0.7250   0.000152   0.0603   0.9397
                 target   0.1910   0.003990            0.0750

The conclusion is unchanged and sharper: THE WHOLE MOVE HAPPENS BETWEEN 0 AND
0.05. y_h jumps 0.261 -> 0.711 on the first step, h_1 halves, band 1 collapses
0.908 -> 0.012. Everything above 0.05 is noise around a state already reached.

**And the death penalty cannot reach what is left.** At delta = 0.30, three points
with rr = 2.867, 4.0 and 8.0 are BIT-IDENTICAL -- y_h 0.6892, h_1 0.000184,
band 5 0.7759 (45083d5a07, f56a40b55d, 81f55164ad). `rr_homeless_hold_age=65`
puts the penalty on ages 66 AND UP while the model's old homeless are at age 65,
the last working year before Social Security starts at 66. So delta sweeps the
workers off, the remainder is unreachable, it becomes 90+ per cent of the
homeless, its income is Social Security, and y_h will not fall.

**The ruling to revisit.** The author said *"just keep the 65+ the way we have
been doing it"* after being told h_share5 was -1.1 per cent. That is true at
delta = 0 and false at every delta above it. The change is
`rr_homeless_hold_age` 65 -> 64, one integer; it is a CONFIG_SWITCH, so the 669
points measured at 65 stop pooling.

# Calibration state -- 5 September, 03:05

## y_h HAD NO LIVE INSTRUMENT AT ALL, AND THAT IS WHY IT SAT AT +275 PER CENT

Two separate faults, both silent, both now fixed.

**The two tables disagreed about which delta owns y_h.** `gaps.py` paired it with
`increased_prob_if_homeless` -- the SYMMETRIC multiplier, which the same file
declares exogenous at 0.2 four lines further down -- while `directions_table.py`
paired it with `homeless_job_penalty_pp`, the author's percentage-point,
separation-only form. `rules()` reads directions_table, so the WALK was right and
the REPORT was wrong; the table shown to the author named an instrument that owns
nothing. gaps.py now agrees with directions_table.

**A proportional step cannot leave zero.** `homeless_job_penalty_pp` was at
exactly 0 and the step is `adjuster * gap * |x|`, so it could never move however
large the gap. It read as a converged instrument rather than a pinned one -- the
same failure mode as a clipped bound, and harder to see, because the parameter
simply never appears in the trace's moved list.

Seeding it in `fixed_point_state.json` did NOT work, and the reason matters: the
loop warm-starts from the BEST ARCHIVE POINT, not from its own state file, so the
restart read `homeless_job_penalty_pp=0` straight back out of `d0029f2b64`. The
seed now lives in `fixed_point.py` as `SEED`, applied after the warm start and
only where the value is exactly zero, so it stops firing as soon as the archive
carries a real value. Confirmed live at 03:02:29:

    seeded homeless_job_penalty_pp at 0.25; a proportional step cannot leave zero
    it 1: homeless_job_penalty_pp 0.25 -> 0.275, gap +250.7%

## THE OLD AND THE WORKERS ARE CUT BY DIFFERENT INSTRUMENTS

The author's design, 5 September: *"the death penalty for the old will remove the
old from being homeless...and delta will remove the workers"*. That answers the
objection that raising delta pushes y_h UP by leaving retirees as the residual:
it only does so if the old are still there, and `rr_homeless_old_level` is what
stops that. The two are halves of one cut, not competing instruments, and y_h
falls because what is left after both is the poor.

It also means delta and `bottom_productivity_level` BOTH act on `emp_homeless`
(+109.9%, the binding moment): the productivity node owns it in the table, but
delta removes employed households from the street directly. Watch for the two
fighting.

## 65+ STAYS AS IT IS

`rr_homeless_hold_age` stays 65 on the author's instruction, *"just keep the 65+
the way we have been doing it"*. No archive partition; the 669 points measured at
65 keep pooling. At the best point `h_share5` is 0.0742 against 0.075, -1.1 per
cent, inside the band -- the 65+ share is not what is blocking the search.

The corner measurement behind that is in `directions_table.py`: at the calibrated
`rr` homelessness above age 65 is already exactly zero, so raising it removes
nothing (which is the whole of its inertness above 3.4), and dropping it to 1.0
puts 42-64 per cent of ages 66-70 on the street. It saturates below 1.5 too, so
the live region is 1.5 to 2.867.

# Calibration state — 4 September, 22:20

## h_1 IS NEAR-DISCONTINUOUS, AND THAT IS WHY THE SEARCH IS HARD

Ten points on the live economy, sorted by the homelessness rate:

         h_1   size_homelessness
    0.000407             0.41930
    0.004647             0.42224
    0.004590             0.42494
    0.000430             0.42726
    0.011550             0.43533
    0.008459             0.44371
    0.004651             0.44685
    0.004651             0.45000     target h_1 = 0.00399

h_1 is NOT MONOTONE in its own instrument and spans a factor of TWENTY-EIGHT
across a seven per cent band of it. From 0.41930 to 0.42224 -- a 0.7 per cent
parameter change -- homelessness multiplies by eleven; going UP again to 0.42726
divides it by eleven. Other parameters move between these points, so this is not a
clean ray, but no clean ray could produce a 28-fold spread over that band either.

THE CAUSE IS THE ONE ALREADY MEASURED FROM THE OTHER SIDE. Eighty-one per cent of
the model's homeless could pay rent from current income, so a mass of households
sits at indifference between the street and the cheapest rental and flips
TOGETHER on any small change. The housing choice is discrete; h_1 inherits that as
a near-discontinuity.

WHAT IT MEANS FOR THE SEARCH. The fixed point is not diverging, it is being
whipsawed: its SSR went 4.03 at the seed to 8.66 by iteration 7 while the BEST
point remained the seed, and size_homelessness is damped to half its adjuster
fighting what looks like overshoot and is actually a cliff. Damping cannot fix a
discontinuity -- no step is small enough -- which is the same conclusion reached
about rr_homeless_old_level earlier tonight, for the same underlying reason.

This is a property of the model, not of the solver, and what to do about it is the
author's call. The honest options are to accept h_1 as a moment that can only be
bracketed rather than hit, or to reduce the mass sitting at indifference -- which
means giving the street a cost that varies across households rather than one they
all face equally.

# Calibration state — 4 September, 21:50

## THE ECONOMY CHANGED TWICE TONIGHT. THE ARCHIVE IS ONE POINT.

Two model changes, both on the author's instruction, both verified as exact
no-ops at their default before anything was calibrated on them:

  max_age_to_choose_homelessness  59 -> 58, barring the street at data ages 84
                                  and 85. A config switch, so it partitions.
  homeless_job_penalty_pp         NEW. The street's labour-market penalty in
                                  PERCENTAGE POINTS: lose = pbu + delta, find =
                                  max(0, pbe - delta). Owns y_h.
  consumption_penalty_homeless    NEW, parked at 0 on the author's instruction.
  extra_job_loss_if_homeless      NEW, parked at 0; superseded by the pp form.

The live seed is 2c40bae9b4: size_homelessness 0.45, delta 0.05, cap 58.

    y_h            0.26142   target 0.191     +36.9%
    h_1            0.00465   target 0.00399   +16.6%
    emp_homeless   0.99230   target 0.46     +115.7%
    can afford     0.81343   -- was 0.995 this morning

## WHAT MOVED THE INCOME OF THE HOMELESS: size_homelessness, AND NOTHING ELSE

The separating 2x2, only two switches differing:

                              y_h   emp_hl       h_1   can afford
    size 0.343, no penalty  0.720    0.992   0.00308        0.995
    size 0.45,  no penalty  0.261    0.992   0.00465        0.813
    size 0.343, penalty A   0.714    0.996   0.00268        0.993
    size 0.45,  penalty A   0.260    0.999   0.00458        0.814

Raising the street from 0.343 to 0.45 of the cheapest rental takes the income of
the homeless from 0.720 to 0.261 and the share who could afford rent and sleep
rough anyway from 99.5 per cent to 81. The labour-market penalty on top of it
contributes 0.001.

THIS CONTRADICTS THE 04:00 FINDING, which recorded that raising size_homelessness
makes the homeless RICHER and OLDER. That was measured on the economy WITH the
age-84 spike in it and does not carry to cap 58. Do not act on it again.

## FOUR INSTRUMENTS MEASURED DEAD TONIGHT, each with a matched bracket

  rr_homeless_old_level      inert above 3.4 -- the ladder from 3.4 to 30 moves
                             every moment by under 0.05 per cent. The whole
                             old-age problem was ONE spike at data age 84, the
                             last age the street may be chosen, and it is an
                             end-of-horizon artefact: age 85 is terminal, so
                             mortality threatens a single final period. HELD at
                             the age-65 value on the author's instruction.
  increased_prob_if_homeless its two halves are a 1.3 point change in a small
                             probability and a 52 point change in a large one, a
                             forty-fold asymmetry inside one number. Raising it
                             swept the SMI and young off the street (-59 and -55
                             per cent) and moved y_h by 0.8. Back to exogenous 0.2.
  extra_job_loss_if_homeless loss side alone, 10 per cent against 20 per cent:
                             every moment moved by under 0.01 per cent.
  consumption_penalty_homeless abolishes homelessness entirely by psi = 0.3.

The common shape: every one of them DETERS someone from the street, so h_1 falls
and the composition barely moves. None of them draws anyone in. That is why the
author's prescription -- raise the penalty AND the street together -- is the only
form that can change composition rather than level.

## THE OPEN MOMENT IS emp_homeless

0.992 against 0.46, and it has not moved for any instrument tried today. The
model's homeless are low-productivity EMPLOYED households, not unemployed ones.
Its owner is bottom_productivity_level, whose own entry in directions_table says
the ray reverses, it is near-flat, and the parameter sits ON its lower bound. The
author has asked to keep it there for now. If it has not moved by morning, the
parameter is the thing to revisit, not the moment.

# Calibration state — 4 September, 20:25

## THE OLD-AGE SPIKE IS ONE AGE, AND THE FIXED POINT HAS ALREADY CLOSED IT

Homelessness by age at point_aa0c0bd2f9 (cap 59):

    age 65        0.009996
    age 66 to 83  0.000000     eighteen consecutive zeros
    age 84        0.012926
    age 85        0.000000

It was never a distribution over the retired. It is a single spike at data age
84, the last age a household may choose the street, and age 85 is terminal
(survival is exactly zero there). A household homeless at 84 is buying one final
year of saved rent against a higher chance of losing one final year of life.

THAT IS WHY MORTALITY CANNOT REACH IT. rr_homeless_old_level runs the ladder from
3.4 to 30 -- values at which death at 84 is capped at probability ONE -- and every
moment moves by less than 0.05 per cent. The prize the risk threatens is a single
terminal period, and the rent saved beats it at any multiplier.

## BARRING AGES 84 AND 85 WORKS, BUT OVERSHOOTS

Matched pair, same vector, only max_age_to_choose_homelessness differing:

              band1    band2    band3    band4    band5      h_1
    cap 59  0.00702  0.90792  0.00005  0.04804  0.03697  0.003198
    cap 58  0.00728  0.94169  0.00006  0.04983  0.00114  0.003084
    data      0.260    0.272    0.210    0.184    0.075  0.003990

The spike is gone and, CONTRARY to what the addiction cap measured earlier, it
does NOT relocate to 83: ages 66 to 85 are all zero and the mass reappears at 63
to 64. "The spike follows the cap" is true of the addiction cap and false of this
one; the note in the declaration should not be read as covering both.

But band 5 goes from -51 per cent to -98.5 per cent, so it abolishes old
homelessness rather than sizing it, and h_1 slips from -20 to -23 per cent.

And it may not be needed: at cap 59 the fixed point took band 5 from +910 per cent
to +8.4 per cent in two iterations, unaided (point_aa0c0bd2f9, 0.08128 against
0.075).

## THE COMPOSITION FAULT HAS MOVED TO BAND 2, AND IT IS NOT A MORTALITY MARGIN

Band 2 (ages 35 to 44) holds 91 per cent of the homeless against 27 in the data.
Set against Baggett's measured relative risks, which the model uses verbatim below
age 65:

     age  Baggett rr  model uses  homeless rate
      34       9.100       9.100       0.000042
      35       8.985       8.985       0.027992
      41       7.605       7.605       0.016301
      42       7.375       7.375       0.000010
   45..62   6.7 -> 3.6        same      0.000004
   75..85       1.100       2.939            0

Two things follow.

THE SPIKE SITS WHERE MORTALITY IS HIGHEST. Ages 35 to 41 carry a relative risk of
9.0 falling to 7.6 and hold nearly all the homelessness; ages 45 to 62 carry 6.7
falling to 3.6 and hold none. There is no deterrence gradient in the profile, so
RESHAPING THE DEATH RISK BY AGE IS UNLIKELY TO MOVE IT -- the same way it did
nothing at 84 -- and it would spend the one part of the calibration that is
externally identified.

THE EDGES ARE THRESHOLDS, NOT MARGINS. Homelessness goes from 0.000042 at 34 to
0.027992 at 35, a factor of 670, and from 0.016301 at 41 to 0.000010 at 42, a
factor of 1600. A smooth trade-off against mortality cannot produce that. Find
what switches at 35 and at 42 before moving the age structure.

Note also that above 65 the model already runs at 2.939 against Baggett's 1.100,
2.7 times the measured value.

# Calibration state — 4 September, 19:55

## THE AUTHOR'S METHOD HAS OVERTAKEN NELDER-MEAD, ON NELDER-MEAD'S OWN OBJECTIVE

Six iterations of the damped fixed point, with the hold rule and the oscillation
damping both live, from a start at core-12 2.4599 / all-21 112.73:

    af5640fa89   core-12 0.1429   all-21  3.83    9 of 21 inside ten per cent
    938152d1c3   core-12 0.2354   all-21  9.46    8
    1d5780203b   core-12 0.1266   all-21  3.80   10

    NM best      ce9e6d2e03   core-12 0.1338   all-21 108.01   11

`1d5780203b` is better than NM's best on the TWELVE MOMENTS NM ACTUALLY SCORES
(0.1266 against 0.1338) and twenty-eight times better on all twenty-one. Six model
solves against roughly two hundred.

The reason is not that the fixed point searches better. It is that NM's stage-1
objective is the core twelve, so nothing charges it for what it does to the other
nine, and it has run `h_share5` out to +1022 per cent. The fixed point never
scores anything, but it updates all twenty-one from the direction rules, so it
cannot buy one moment by ruining another.

**The open question for the author: is NM still worth a container?** Its own
answer is now dominated. `STAGE_MOMENTS` being 12/4/5 is their call and stands
until they rule.

## THE HOLD BAND IS NOW STICKY, AND THAT WAS THE AUTHOR'S DIAGNOSIS

They said, 4 September: *"maybe the right way is to push them into the rule when
they pass 10%, and then only start updating them again when they leave 15%"*, and
*"so it's not so much in and out"*.

They were reading the held counts, which went 12, 9, 9, 8, 10, 9 across the run --
parameters leaving the band as fast as they entered, so something essentially
converged kept moving and kept injecting cross-effects. One threshold in both
directions makes the band a revolving door.

Both searches now hold at ten per cent and release at fifteen. `hold_test.py`
(fixed point) and `hysteresis_test.py` (Nelder-Mead) each walk one gap across the
line and count state changes: eight to two, and four rebuilds to one.

THE NUMBER HELD SHOULD NOW TREND UP. If it does not over the next several
iterations, the sticky band is not enough to break the coupling and that is worth
telling the author rather than burying.

## DAMPING, AND WHY IT WAS NEEDED

Ten undamped iterations put `rr_homeless_old_level` in a period-two limit cycle:
2.7102, 2.9813, 2.6853, 2.9538, 2.6656, 2.9322, 2.7167, 2.9884 -- every step
exactly ten per cent of the value, every step reversing the last, one model solve
per bounce. Each adjuster is now scaled by whether that parameter's own residual
changed sign, halved on a flip, relaxed back on a sign that held, floored at an
eighth. Live scales at last check: `rr_homeless_old_level` 0.75,
`bottom_productivity_level` 0.5, `kappa_uem` 0.25.

## THE HOMELESSNESS BLOCK IS PARKED BY THE AUTHOR

*"those homelessness things will be fixed later"*, 4 September. `h_share5`, `h_1`,
`sud_homeless`, `emp_homeless` and `lambda_m` are all downstream of the same
composition fault -- the model's homeless are 84 per cent aged 65-plus against 7.5
per cent in the data, and 88 per cent of them could afford rent on income alone.
Do not chase any of them with the current instruments and do not read their gaps
as evidence about the search.

## RESTARTS COST MORE THAN THE CORRECTIONS THEY CARRY

Nine sessions between 17:09 and 19:52; only one ran long enough to produce more
than a couple of solves. Each restart costs about eleven minutes before the first
iteration lands. The state file and the points are pushed every iteration, so a
restart loses no TRAJECTORY -- a new session on the worker branch resumes from
`fixed_point_state.json` -- but it loses the setup time every time. Batch
corrections; do not restart to carry one.

Two failure modes seen tonight, both mine:

  - a brief that asserted a SNAPSHOT (`must print iteration 3`) went stale within
    ninety seconds because the run advanced. Assert an invariant instead
    (`it >= 3`), never a current value.
  - `create_session` does not reliably attach the repository: fp5 came up with no
    checkout at all and stalled. Pass `source_url` explicitly.

# Calibration state — 4 September, 19:35

## THE LIVE BEST, AND WHY ONE NUMBER IS NOT ENOUGH

The archive holds 215 points on the current model hash. Two searches are running
and they are best on DIFFERENT objectives, so a single "best" line would be a
lie:

    Nelder-Mead   ce9e6d2e03   core-12 SSR 0.1338   all-21 SSR 108.01   11 of 21 inside 10%
    fixed point   28e401cb4c   core-12 SSR 0.2130   all-21 SSR   3.76   11 of 21 inside 10%

NM wins the twelve moments it SCORES and loses the twenty-one by a factor of
twenty-nine, because stage 1's objective is the core twelve and nothing stops it
wrecking the other nine. It did: `h_share5` is at +1022 per cent at NM's best.
The fixed point scores none of them but updates all twenty-one from the direction
rules, and keeps them bounded. It reached the same eleven-inside in NINE model
solves against roughly two hundred.

**This is the case for opening stage 1's objective to all twenty-one moments.**
`STAGE_MOMENTS` is 12/4/5 and marked frozen as the author's call, so it stands
until they rule.

The earlier line in this file -- `point_8c42b1f32a`, SSR 2.9430, 7 of 20 -- is
superseded and kept below only for the structural finding it carries.

## pi_eu IS RESOLVED

It was never a flow. It is the unemployment RATE, u = s/(s+f), and only s is an
instrument: `probability_becoming_employed` is hard-coded at 0.55. Reaching the
old 13.9 per cent target required every SMI worker at every productivity node to
be unemployed with probability one, because `min(pbu*kappa_uem,1)` saturates at
pbu = 1/49.05. The author retargeted to U-3 at 4.9 per cent, and the moment now
reads **+1.8 per cent** at the live best, from +66 per cent this morning.

## THE HOLD BAND IS LIVE ON BOTH SEARCHES

The author, 4 September: *"every time a parameter gets into the 10%, you hold it
fixed, and do the projections, shrink, etc, based on the ones that are outside
the 10%"*.

  fixed point  a parameter whose own moment is inside ten per cent is not
               updated, and is released the moment it drifts back out.
  Nelder-Mead  `nelder.setup()` drops held instruments from the simplex,
               `scope()` seeds only the live ones, and `stage_night` rebuilds the
               moment the live set shrinks. Currently FOUR of twelve: cbar, p_m,
               sigma_y, tau_l.

`keys` stays the whole objective in both, so a live parameter cannot buy its own
moment by pushing a held one out of the band.

## THE FIXED POINT NEEDED DAMPING, AND IT IS MEASURED

Ten iterations put `rr_homeless_old_level` in a period-two limit cycle -- 2.7102,
2.9813, 2.6853, 2.9538, 2.6656, 2.9322, 2.7167, 2.9884 -- every step exactly ten
per cent of the value, every step reversing the last, three minutes of solve per
bounce. Each adjuster is now scaled by whether that parameter's own residual
changed sign: halved on a flip, relaxed back on a sign that held, floored at an
eighth. `damp_test.py` checks it against the two measured sequences.

## max_age_to_choose_homelessness IS 59 IN THE LIVE ARCHIVE

The line further down saying all 43 points carry 45 is out of date: it is a
config switch now, the live value is 59, and the current best carries 59.

# Calibration state — 4 September, 04:00

## THE STRUCTURAL FINDING OF THE NIGHT: THE LEVEL AND THE COMPOSITION FIGHT

At `point_8c42b1f32a`, SSR 2.9430, 7 of 20 inside ten per cent:

    h_1 on target (+11.6%)  requires size_homelessness 0.2925, sevenfold up
    and at that value    old band = 0.8887 of the homeless, spike at age 84

    h_1 at 30 per cent of target (size_homelessness 0.0425)
    and at that value    old band = 0.0001 of the homeless, spike at age 33

**Neither the mortality hold nor the search can resolve this.** Making the street
big enough to hit the homelessness rate makes it attractive enough for retirees
again, and the age-65 hold no longer keeps them off. The two requirements pull in
opposite directions along the one instrument that sets the level.

The reason is the one measured earlier: for a retiree, three of the four costs of
the street are structurally zero -- no job to lose, mostly no disorder to fail to
recover from, and almost no continuation value for mortality to threaten --
leaving only the foregone housing service, which `size_homelessness` is exactly
the parameter that shrinks. So raising the level to fix `h_1` necessarily buys
back old-age homelessness.

**What would resolve it** is a cost of the street that binds on a retiree: a
morbidity state, which the author has already proposed and parked. Nothing in the
current instrument set can do it, and this should not be chased further with the
existing parameters.

## THE SEARCH, AND WHY BOTH METHODS ARE ON THE SHELF

`nelder_test.py` drives the real Nelder-Mead state machine against known minima:

    quadratic bowl, 20-dim   1200 evals   1.2e-09   PASS
    Rosenbrock,      8-dim    900 evals   4.6e-14   PASS
    Rosenbrock,     20-dim   3000 evals   0.187     FAIL

The implementation is right; the method is weak at this dimension on a curved
objective. But it HAS improved: the shrink took 3.1555 to 2.9430, so it is not
stuck, and the author's call is to let it run overnight and assess in the
morning. `code/overnight.sh nm` does that -- restarts the loop if it dies and
pushes every five minutes.

`code/sweep.py` is the alternative, written and ready but NOT running: measured
coordinate brackets on all twenty instruments per round, assembled with damping
and accepted only against a measurement. Switch with `bash code/overnight.sh
sweep` after stopping the current driver. THE TWO MUST NOT RUN TOGETHER on one
container -- run_one_point.sh writes PARAM_HANDOVER.txt in `code/`, so two
solvers interleave their handovers and each measures the other's vector. That
happened once tonight and was caught within a minute.

## IN FLIGHT ON THE FLEET

- **size_homelessness 0.07 to 0.22**, to find where h_1 reaches 0.00399 from
  0.00121. Measured already: 0.0425 to 0.0560 raises h_1 by 45 per cent and
  leaves the age composition untouched, so the young dominance is NOT an
  artefact of the level -- the author's hypothesis, measured false.
- **M from 6 to 40**, testing the author's claim that a large enough SUD
  employment penalty must lift sud_homeless off zero. The penalty keys on
  d_f_1>=1, the DISORDER state rather than consumption, so the mechanism is the
  right one. Watch for sud_homeless staying at EXACTLY zero, which would mean no
  disorder-holder reaches the street by any route and no value of M helps.

Young and old composition is parked on the author's instruction: *"i think we
can deal with the young homelessness later if needed"*.

## THE MORTALITY HOLD IS LIVE AND THE AGE PROFILE HAS FLIPPED

`rr_homeless_hold_age = 65`, on the author's instruction: *"i think we can just
hold it at the 65 number.... and say that.... that would fix it"*.

**The sentence for the paper.** The model holds the relative risk of death from
sleeping rough at its age-65 value for all older ages, because beyond 65 the
observed ratio is dominated by survivor selection and does not identify the
causal effect the model needs. The homeless who reach 65 are unusually robust
and the comparison group includes the frail and institutionalised, so the
observed ratio is biased toward one; read literally Baggett's 1.1 at 65-84 says
the street PROTECTS the old, which is why the code floors it at one.

Sixty-five is where the ratio stops being USABLE, not where it stops being
measured. The 1.100 above 75 is Baggett's own 65-84 figure extended past its
band midpoint at 74.5 — an earlier note here calling it padding was wrong.

| | before (hold 70) | now (hold 65) | data |
|---|---|---|---|
| young band, share of the homeless | 0.1117 | 0.8589 | 0.2600 |
| old band, share of the homeless | 0.8821 | 0.0001 | 0.0750 |
| retired 66+ share | 88.2% | 0.0% | — |
| spike | age 80, 71.9% | age 33, 47.7% | — |

The age-80 spike is gone. It now overshoots the other way, and both errors are
large, but homelessness is at working ages where the employment deterrent
actually operates.

**THE RESPONSE SATURATES ABOVE A MULTIPLIER OF ABOUT 2.7.** Measured at one
vector: hold 70 gives an old share of 0.882, hold 65 gives 0.0003, hold 45 gives
0.00024 and hold 26 gives 0.00021. Nothing is bought by going below 65, so 65 is
the cheapest point on the plateau — the best place to sit for a number that has
to be defended.

**A moment the hold broke.** `sud_homeless` is now EXACTLY zero: no homeless
household carries the disorder. The old homeless were meeting that moment — 18.9
per cent of them had SUD — and removing them removed it. That is the worst gap in
the table at −100 per cent and the reason SSR reads 3.16 here against 1.46 on the
old economy. It is the objective correctly registering a moment that used to be
met by the wrong population.

## THE CONFIGURATION, unchanged

    number_of_beta_types  1          one beta for everyone
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor
    newborn_endowment_scale  0.0     HELD at zero by the author
    homeless_death_risk_flat_in_age  0   the Baggett age profile

Model hash **b2530947f0**, 117 points. The 22:00 cap patch (`4df7be4132`, the
street barred at `max_age_to_choose_addiction`) was **REVERTED** on the author's
instruction — *"You should revert to allow the 80 year olds to be homeless
again"* — and its points are orphaned. Any earlier section of this file that
describes that economy as live is out of date.

## THE SEARCH

**Twenty instruments**, all stages unioned. Of the 23 parameter/moment pairs in
`next_batch.OWN`, three are out and each for a different reason:

| parameter | moment | why it is out |
|---|---|---|
| `weight_on_child` | `omega_c` | held: *"since omega_c is so close, just keep it fixed for now, we can adjust it at the end"* — it reads 0.1622 against 0.1834 |
| `newborn_endowment_scale` | `h_share1` | the author holds it at 0 |
| `ssi_floor_level` | `h_share5` | the author holds the floor to the 2024 federal rate |

### Three scorer bugs found on 4 September, all fixed

1. **`sud_homeless` was never parsed.** The model prints
   `UNTARGETED SUD share of the homeless` on every point ever solved and
   `gaps.py` had no pattern for it, so its instrument
   (`multiple_of_probabilities_of_employment_if_addicted`) looked like a
   parameter with no moment and sat outside the search. It reads 0.1166 against
   Gutwinski's 0.217. Now scored retroactively on all 155 points, no model time.

2. **`omega` vs `omega_c`.** The Fortran prints `MOMENT omega`; `OWN` calls it
   `omega_c`. Even with `measure_child_gap=1` the scorer would have filed it
   under a key nothing reads. Aliased, so `omega_c` will work first time when it
   is taken up at the end.

3. **`archive()` enforced ONE config switch out of the table.**
   `homeless_death_risk_flat_in_age` was added to `CONFIG_SWITCHES` on
   4 September and had no effect at all: the two points solved with the flat 1.6
   mortality multiplier POOLED with the 150 solved on Baggett's age profile and
   were ranked against them as one economy. All switches enforced now, with a
   point predating a name falling back to the Fortran's compile-time default
   rather than the live value.

### `measure_child_gap` costs 9 per cent, not 100

Reported here first as a doubling, because the block runs a second solve and
converge. Measured on the same vector: **4m06s off, 4m30s on**. The
counterfactual starts from the converged baseline distribution. It is off again
because `omega_c` is held, and turning it off restores the archive: it is a
CONFIG SWITCH, so with it on exactly one point pooled and the simplex needed
twenty-two fresh solves to rebuild.

### The tension in `M`, worth knowing before it is spent

`multiple_of_probabilities_of_employment_if_addicted` is the SUD employment
penalty on both margins — job loss `× M`, job finding `÷ M`. Its target is
`sud_homeless`, which wants it UP. The moment it controls mechanically,
`kappa_ued`, is an untargeted OUTPUT on the author's own instruction
(*"we don't truly know what they are so we calibrate them"*) and already reads
0.2217 against 0.1625, **36 per cent high**. Closing `sud_homeless` drives
`kappa_ued` further from its data counterpart. Offered to the author on
4 September and NOT reversed: `kappa_ued` stays an output.

    simplex complete, 20 vertices
    best      827aa52172   SSR 2.1441
    worst vertex           SSR 19.0389   (the smi_onset_level fill)

## PARKED BY THE AUTHOR

- **Young and old homelessness.** *"Ignore young and old homelessness for now. We
  will fix that later."* `h_share1` and `h_share5` are UNSCORED. The best stage-0
  point puts 87.0 per cent of the homeless in retirement against 25.5 per cent of
  the population, spiking at age 80.
- **The flat 1.6× mortality multiplier** (`homeless_death_risk_flat_in_age=2`) was
  measured as a matched pair, `047afb7487` → `d2e58e6afb`: retired share 0.8 → 0.0
  per cent, SSR 3.0511 → 3.0636. **That test does not answer the question it was
  set**, because at that vector the spike was already at age 26, not 80. It would
  have to be rerun at `9a9c749a75` to learn anything.
- **The morbidity state.** *"keep calibrating the rest and we'll deal with
  morbidity later"*. Evidence scan is in `data/MORBIDITY_EVIDENCE.md`.
- **The newborn endowment double count**, two options offered, no decision taken.

### The seed only ever displaced UPWARD, and it cost `sigma_y` the whole search

Found 4 September, 14:45. `stage_night.seed()` built every vertex as `x + d`.
Across **1245 archived points, `kkk_sigma_scale` was never once measured below
its anchor value 2.20949**, against a lower bound of 0.8. The one clean matched
pair -- kkk alone, 2.20949 -> 3.09114 -- takes `sigma_y` from 0.10337 DOWN to
0.03536, and `sigma_y` has to RISE from 0.103 to 0.172. The search had never
sampled the direction the instrument needs to go, which is why the moment looked
frozen at -40 per cent through every restart.

Fixed by alternating the sign across instruments so the initial simplex straddles
the anchor. Nelder-Mead does reach both sides on its own, by making the up-vertex
the worst and reflecting through the centroid, but that costs solves and moves
every coordinate at once.

**The general lesson: a seeded simplex that is one-sided is not a simplex around
the anchor, it is a simplex in one orthant.** Check the sign coverage of any
seeding rule before trusting a moment that will not move.

### `pi_eu` is weakly handled by its own instrument

Matched pair, 4 September: `probability_becoming_unemployed` 0.0122 -> 0.0173777
(+42 per cent) moves `pi_eu` 0.08001 -> 0.08491, **+6 per cent, elasticity 0.15**
-- below the 0.27-0.51 measured earlier, so the elasticity is falling as pbu
rises. Closing a 74 per cent gap at that slope needs pbu near 0.075, six times
its value. It is inside the bounds (1e-06, 0.5) so it is reachable, but not at
this step size.

`pi_eu` is NOT structurally capped near 0.08: `6624095c1b` reaches 0.1407 and
`c35f6e74a9` reaches 0.1834. **Both are confounded** -- each carries
`discount_factor` pulled to 0.9075/0.92625 from 0.945 AND the invalid
pre-guard `rr_homeless_old_level = 0`, at SSR 53 and 164. A lead to test, not
evidence: the clean test is `discount_factor` alone at the current anchor.

### THE SEARCH WAS ON THE WRONG ECONOMY FROM 13:18 TO 15:00

`max_age_to_choose_homelessness` bars the homelessness choice above an age index:
45 is "nobody over 70 can be homeless", 59 is "nobody over 84 can be". Those are
two models of old-age homelessness. It is a HANDOVER parameter, so it moves
neither the source hash nor the semantic hash, and it was not in CONFIG_SWITCHES,
so nothing separated them and `best()` ranked all of them as one economy.

The cap-walk batches (`batch_capwalk.txt`, `batch_cw_01.txt`) carried 45. The
model change at 13:18 emptied the archive; the first points on the new hash came
from that batch; a 45-point won the pooled ranking; `stage_night` took it as the
anchor and the seed copied 45 into all eleven vertices. **The retired share
reading 0.0 per cent of the homeless was MECHANICAL, not behavioural.**

Now a CONFIG SWITCH, live 59 per the author (*"Make sure you allow homelessness
at age 84-85 still"*), PREDATE 59 (the Fortran default at line 509). This EMPTIES
the live archive: all 43 points on the current model hash carry 45.

### THE COORDINATE SCAN REPLACES THE SEEDED SIMPLEX AS THE WAY IN

The author, 4 September: *"all parameters should be sampled across many values so
they have a range to go off of"*, and on `sigma_y`: *"since share of income is too
low for bottom 50%, it means probably that sigma_y needs to be lower... Not
higher. You need to extend it from below"*.

`code/scan.py` writes one batch file per instrument, seven values spanning a wide
range inside the hard bounds, everything else at the anchor, on the 59 economy.
21 instruments, 139 points. `kkk_sigma_scale` now spans 0.8 to 4.0.

`weight_on_child` is left out: `omega_c` is held and `measure_child_gap` is off,
so its moment is not measured on these points.

**`bottom_productivity_level` cannot be scanned downward**: its anchor 0.004 IS
its lower bound, so the scan only samples up. That is a bounds question for the
author, not a scan defect.

`night_watch` takes a `code/PAUSE_NM` marker so the scan owns the CPU while the
pusher keeps committing. Remove it to resume Nelder-Mead, which should then seed
from a spanning archive rather than a one-sided simplex.

### FOUR WAYS TO SEARCH TWENTY-ONE PARAMETERS, AND NONE OF THEM WORKS

Measured 4 September with `code/stage_test.py`, Rosenbrock at 21 parameters, same
total budget, every method graded on all 21 moments at the end:

    method                                   900 evals   3000 evals   vs one-shot
    ONE SHOT, all 21 open                      7.61696      4.42097      --
    STAIRCASE 12 -> 16 -> 21 (cumulative)      9.37109      8.51109      1.93
    LADDER, block-only objective               9.86351      9.86351      2.23
    LADDER, full objective, 12/4/5 blocks      9.40621      6.28463      1.42

**The block-only ladder is unchanged to six figures between 900 and 3000
evaluations.** Not slow -- FROZEN. While block 2 is open nothing scores block 1's
moments, so block 2 wrecks them for free, block 1 undoes it, and the cycle closes
exactly. Reading the author's *"open only stage 2"* literally would have spent a
night going nowhere with a busy-looking trace.

The full-objective form -- all 21 moments always scored, only the block of
PARAMETERS allowed to move changes -- does progress, 9.41 -> 6.28. That is the
difference between a method that moves and one that is precisely stuck, and it is
the form to use if a ladder is used at all.

**But the tolerance is 1e-3 and the best of four is 4.42. Every one of them
fails.** The ranking is a ranking of failures.

### WHAT THE MEASUREMENTS ACTUALLY SUPPORT

    dimension   Rosenbrock       verdict
    4           0                PASS
    5           6.42e-14         PASS
    12          5.22e-13         PASS      -- twelve orders inside tolerance
    21          4.42             FAIL

Twelve works and is not marginal. Twenty-one does not work by ANY arrangement
tried. So: **search the twelve, measure the rest.** `expand.py` bracketed
`sigma_y` (crossing in kkk 1.5..2.2095) and `tau_l` (crossing in 0.718..0.827)
from rays alone, with no optimiser -- brackets do not care about dimension,
curvature, or the discrete choices that make the model's moments jump.

The author's premise was right and is what the evidence supports: never search
twenty-one. What the evidence adds is that the answer to *"then what searches the
other nine"* is *nothing does -- they get measured one at a time.*

**PRODUCTION IS STILL THE CUMULATIVE STAIRCASE**, which measured 1.93 times worse
than one-shot, and its stage 3 opens all 21. That has to change before stage 1
promotes. It has not been changed yet because which way to change it is the
author's call, and the choice is between the full-objective ladder and dropping
the search past stage 1 entirely in favour of brackets.

### A RAY IS A PARTIAL DERIVATIVE, AND THE PAPER'S ECONOMICS IS NOT

The author, 4 September: *"your rays are not correct because they are not based on
the economics of the paper"*. They are right, and it invalidates a day's worth of
conclusions drawn from `scan.py` and `expand.py`.

Every ray holds the other twenty parameters PINNED. In this model the parameters
are jointly identified -- `M` only means anything alongside `b`, `kkk_sigma_scale`
alongside `discount_factor` and `max_food_cost`, the housing block alongside the
income distribution. A ray freezes exactly the adjustment that constitutes the
mechanism.

**`M` IS THE PROOF.** Its ray reads slope -1.2e-07 on `sud_homeless` across the
whole range 1 to 32, which is arithmetically right and economically empty: with `b`
held, raising `M` does not punish addiction, it ABOLISHES it -- the disorder rate
collapses 34-fold between M=4 and M=5.66. With `b` free the pair is a different
object entirely. The author saw it in one line after the ray had been treated as
evidence for hours.

WHAT IT INVALIDATES, listed rather than left to surface later:

- "M is a dead instrument" -- wrong, corrected.
- "mu_homeless does nothing to sud_homeless" -- same defect.
- "bottom_productivity_level moves emp_homeless by two parts in a million" -- same.
- "rr_homeless_old_level's ray reverses" -- measured with the income distribution
  pinned, and that distribution decides who sits near the homelessness margin.
- "kkk_sigma_scale crosses sigma_y at 1.63" -- measured with beta and cbar frozen,
  both of which then broke by 20 and 13 points when kkk moved. The joint crossing
  is elsewhere.
- EVERY ADJUSTER MAGNITUDE, since size_adjusters.py derived them from ray
  crossings. The signs survive; the distances do not.

WHAT RAYS ARE STILL GOOD FOR: a sanity check on DIRECTION, and a warning when a
moment does not respond at all. Not magnitudes, and not proof that an instrument is
dead.

AND EVEN SIGNS NEED THE ECONOMICS. `b`'s sign was got wrong in both directions on
the same day: the author ruled it from the name, the measured ray disagreed, the
ray was dismissed as "a cliff, unusable", and the Fortran's own comment at line 1485
-- *"the marginal value of the first unit is theta/b, so participation FALLS in b"*
-- settled it against both. Three sources, and only the one nobody consulted was
right.

THE CONSEQUENCE FOR METHOD. The fixed point moves all twenty-one parameters from a
single solve, so its trajectory IS the joint response and it never forms a partial
derivative. Nelder-Mead likewise. That is a better argument for both than any made
earlier today.

## OPEN WITH THE AUTHOR

Nothing is blocking. The loop runs to 400 iterations and commits every twelfth.
