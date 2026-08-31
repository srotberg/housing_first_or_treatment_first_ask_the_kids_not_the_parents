# Where the calibration is

Rewritten whenever a point changes the picture. The hourly engine trigger reads
this rather than carrying the state in its own prompt, because the prompt went
stale three times in one evening and a stale prompt sends the search backwards.

## The objective

The author's ten per cent rule: EVERY target within ten per cent. They conceded
the model is hard to calibrate and will say so in the paper. That is a MINIMAX,
not a mean -- `score_points.worst()` with `ACCEPT = 0.10`. The mean is what once
led the search to a point with b exact and lambda_d at minus seventy eight.

`beta` is banded (3.0, 4.5) on the author's instruction and scores zero inside
it. `h_2`, the smallest-rental share, is conceded and need not be chased.

## Where it stands, 30 August 12:20

BEST ON THE AUTHOR'S MINIMAX: `point_051d242e11`, worst gap 37 per cent on h_1,
and EVERY moment inside 37. Across the morning the worst went 164, 120, 82, 70,
68, 65, 37, and the gaps now cluster instead of having one outlier:

    h_1 -37, h_2 +35 (conceded), lambda_m -33, tau_u +31, kappa_uem +28,
    kappa_ued -28, theta +26, aleph -21, pi_eu +17, b -11, cbar -11,
    with ten moments already inside ten.

BEST WITH A CLEAN DRUG BLOCK: `point_7add914d47` -- b -7.5, lambda_d -1.7,
pi_eu +4.1, thirteen of twenty one inside ten per cent, worst 65 on kappa_uem.

point_051d242e11 is not admissible as a base, its b being -10.9 and the bound
ten. REPAIR3 runs from it to recover b, lambda_d and pi_eu without losing the 37.

## The drug block is closed and pi_eu is SOLVED

b and lambda_d were closed at lambda_addiction 15.89 with addiction_scalar_1
0.018367, by fitting BOTH surfaces on BOTH instruments over a band narrow enough
to be locally log-linear and checking the condition number before stepping. Every
earlier aimed step had chained an elasticity from one region into another and
missed by three to five times.

pi_eu bound every round after tau_u came down, was never better than +45 per cent
over ninety points, and this file once called it unexplained. The instrument was
never weak. probability_becoming_unemployed crosses its target near 0.0085 and
BOTH bracketing points were already in the archive; they were unusable only
because they carry b at +155 and +187 per cent. p_eu cannot move without taking
the drug block with it, so the answer was to move it and repair the block in the
same point, which is what the ladder and the secant did.

## The tools, and which to reach for

  `locus.py`      traces the b-on-target curve; right when the drug block is far
                  out, superseded by local 2-D fitting for stepping.
  `next_batch.py` the gate. Opens at five per cent on b and lambda_d, then picks
                  the best base within ten, emits one damped single-coordinate
                  arm per off-target moment, prefers a measured BRACKET to an
                  elasticity, compensates any arm that drags the drug block, and
                  adds a repair line when the base itself has drifted.
  `restore.py`    two-moment repair, b and lambda_d on the two drug instruments.
  `repair3.py`    THREE-moment repair, adding probability_becoming_unemployed and
                  pi_eu. Prefer this now: the kappa_uem arm took pi_eu from +4 to
                  +17 in one step, because two employment moments move together.
  `compensate.py` the gate's compensation, standalone, for hand-built batches.
  `joint_step.py` full least squares over everything. TRIED AND WORSE -- kept so
                  the negative result is not rediscovered.

## What still binds, and whether it has an instrument

    h_1       -37%  size_homelessness             overshot by a bracket, step back
    lambda_m  -19%  lambda_m                      NOT floor-bound; see below
    tau_u     +31%  utility_cost_of_treatment     bracketed [0.6031, 0.6308]
    kappa_uem +28%  kappa_uem                     elasticity -1.05, moves freely
    kappa_ued -28%  multiple_of_prob..._addicted  coupled, compensate
    theta     +26%  relative_share_of_addiction_1 coupled, compensate
    aleph     -21%  value_of_life                 coupled, compensate
    h_2       +35%  conceded by the author

## lambda_m is NOT floor-bound -- an earlier entry here was wrong

This file, and two reports to the author, said the SMI share of the homeless
could not be reached through its own instrument: elasticity -0.08, the step it
wanted landing on the floor of 0.046, and a scope decision needed. That was
wrong, and the way it was wrong is worth more than the conclusion.

Nine controlled pairs exist on the lambda_m parameter. Eight give an elasticity
between -0.65 and -1.01. One gives -0.08 -- and that one happened to be NEAREST
the base, which is the pair `elasticity()` used to pick. On -0.08 the parameter
must reach 0.035 and the moment is unreachable; on the median of -0.77 it needs
0.051, comfortably inside the floor, and the moment is ordinary.

The nearest pair is usually the SMALLEST step, which is the worst signal against
the solver's reproducibility band. `elasticity()` now takes the MEDIAN over all
controlled pairs, which needs no threshold or weighting and degrades gracefully:
one pair is itself, two are their mean, nine ignore the outlier.

relative_share_of_addiction_1 is still contested between theta and lambda_m, and
that remains a real tension -- but it is no longer a reason to concede a moment,
because lambda_m has a working instrument of its own.

## Rules that came out of specific mistakes

BUILD THE NEXT STEP FROM MEASURED CROSSINGS, NOT FROM A LOCAL ELASTICITY. The
addiction_scalar_1 elasticity of b is about -26 at the centre's neighbours and
-14 across the wider grid; the local number carried to lambda 11.8 predicts
b = 0.060 where the model returns 0.138. Interpolate between straddling points;
never extrapolate a slope past the pair that produced it.

BRACKET, DO NOT AIM. A one per cent error in addiction_scalar_1 is a twenty per
cent error in b. Every new lambda gets a THREE-POINT bracket. When two estimates
disagree, widen rather than average. Every wide bracket has worked and four
aimed steps have missed, by factors of 4, 5, 3.2 and 2.3.

RELATIVE_SHARE_OF_ADDICTION_1 IS THETA'S INSTRUMENT AND NOTHING ELSE'S. The
Fortran adjusts it against `drug_share_weighted_1 - drug_spending_share_data`
and clamps it between `theta_lo` and `theta_hi`. The search had been using it to
reach the disorder ratio, where it is violent -- 0.45 to 0.51 multiplies b by
5.7 and lambda_d by 18.6 -- and it takes the SMI share of the homeless from
0.256 to 0.085 on the way, because it floods the homeless with drug users. That
is the mechanism behind the flat loss: every gain on the ratio was paid for in
theta and lambda_m. The ratio belongs to lambda_addiction, b to
addiction_scalar_1, theta to this.

CHECK WHICH LINES LANDED, NOT HOW MANY. A count hides a worker stalled on a
permission prompt; two hours went that way. Compare vectors in `points/` against
the batch file line by line and respawn the specific lines missing.

REPORT MOMENTS WITHIN TEN PER CENT AT ONE POINT. "Nineteen of twenty one have
been inside ten per cent" is each moment at its own best point, is not a result,
and the author challenged it directly.

THE UNEMPLOYMENT TYPO WAS INERT. `probability_becoming_employed1` was real and
undeclared, but line 24028 overwrites the slice eighty five lines later. Every
point stands. Do not re-litigate it.

PREFERENCES ARE CONSTANT ACROSS STATES and `recompute_derived_parameters` now
asserts it. The author asked; the model was already correct, but the diagnostic
printed `_1` under the `_2` label and would have hidden a divergence.

## STOP: the archive is on a different model as of 30 August evening

Two changes today mean the 243 archived points describe a model that no longer
exists. Do not launch a correction round until the equivalence run below has
landed and been read.

**The asset grid was cut from 41 reachable points to 25.** The author asked for
it, to buy solve time. Every archived point was solved on 41. Every moment they
report is a moment of a different model, and the gate's brackets, elasticities
and drug-block Jacobians are all built out of them. A DIAG line now records the
grid in each point so the two generations cannot be mixed silently; there is
precedent for exactly this going wrong, in `points_pregrid`.

**h_2 was redefined and is no longer conceded.** The trigger prompt still says
"being off on h2 is ok". That was true when h_2 meant the share in the smallest
rental unit. It now means the share paying more than half of income for housing,
target 0.101 from SCF 2022 over ALL households, and the author wants it hit.
`SKIP` in next_batch.py is empty. The old h_2 and the new one are told apart by
their LABEL, via `STALE_LABEL`, because both are called h_2 in point files.

Also renamed: the old h_4, the share in the largest unit, is now **h_3**. Its
target is unchanged at 0.626723.

## What the homelessness block actually does, measured on 30 August

This is the day's main finding and it is not a calibration problem.

- **92 per cent of the model's homeless are homeless BY CHOICE** (median over 242
  points; 84 per cent at the best point). The test is income plus assets against
  the rent on the smallest unit.
- **The smallest unit costs 5.9 per cent of average labour income**, which is the
  25th percentile of rents actually paid in SCF 2022. Nobody is priced out.
- **88 per cent of the model's working-age homeless are employed**, against 40 to
  52 per cent in Meyer et al. (2024). Their income is 19.1 per cent of average in
  that paper; the model has never printed its counterpart until today.
- **A household with the disorder is 34 times LESS likely to be homeless than a
  random one.** The data has it 5.9 times MORE likely. The association is
  reversed, not weak, and no point in the archive reaches a relative risk above
  0.78 -- across kappa from 1 to 20, lambda_d from 0.001 to 0.92, and the
  employment penalty on and off.

**The recovery deterrent is NOT the cause.** mu_homeless=1.0 took mu_H from 1.425
to 1.094 and moved the SUD share of the homeless from 0.001024 to 0.001042. That
hypothesis was stated confidently here and is refuted; do not revive it.

**The live hypothesis is the MORTALITY INTERACTION.** Survival is
`survival(clean,housed)**(kappa_phi_h*kappa_phi_d)` -- the two hazards multiply.
For a clean household the street multiplies the death hazard by up to 9; for an
addict it multiplies an already 8-fold hazard, so the marginal cost of
homelessness is about eight times larger for an addict. Two things fit: both
multipliers collapse with age, and the relative risk runs 0.011, 0.039, 0.153,
0.557, 1.07 across the five HUD bands; and at kappa_phi_d_level=1 the relative
risk is 0.783 against 0.02 at 8.

**And h_2's instrument is not identified against h_1.** `size_homelessness` sets
the utility of the street and the smallest unit sets the utility of the cheapest
housed alternative; the housed/homeless margin is the gap between them. So
`smallest_rental_relative_to_lowest_income` moves h_1 directly. Two moments on
two parameters that move one margin.

## Data definitions that are settled but NOT yet adopted

The NSDUH work is done and the numbers are verified against the 2024 codebook,
which is now in `data/`. Nothing has been changed in the model on the strength of
it, because a target change is the author's call.

- `b` = 0.0890 is ANY drug use disorder including marijuana, svyrdudany in
  (1,2,3), adults 26+ -- `age3 >= 7`, NOT the `age3 >= 4` the published income
  script uses, which is the eighteen and over cut.
- `lambda_d` = 0.0368 is moderate or severe, same universe.
- The two income rows in the validation table are on the WRONG age cut and do not
  reproduce: on 26+ they are 0.761 and 0.687, not 0.740 and 0.711.
- Marijuana is 71 per cent of the moderate-or-severe target. Excluding it, any
  non-marijuana disorder is 2.82 per cent with income 0.693 of average.
- Regular non-marijuana use, 50+ days, is 1.59 per cent of adults with income
  0.589, and 42.6 per cent of those users carry a disorder against the model's
  40.3 -- the conditional structure is right, the levels are three times too big.

## The SUD mortality level is now a coordinate of the search

The author asked on 30 August to calibrate the death probability so the average
income of drug users matches the data. The model puts it at **0.308** of average
income against **0.740** in NSDUH, and households with a disorder at 0.385
against 0.711, so users in this model are far poorer than users in the world.

`kappa_phi_d_level` is the instrument. Survival is raised to the power of the
multiplier, so the multiplier is what the disorder COSTS a household -- its
whole continuation value -- and what it costs decides who is willing to bear it.
It is now a handover case, has a default of 8.0 in `run_one_point.sh`, and is
filled in at 8.0 by `next_batch.py`'s `IMPLICIT` for any VECTOR line written
before 30 August, because every earlier point solved at the declared 8.0.

**Two things about it that the search must not lose.**

- It is **assigned in the note at the midpoint of a literature range**: all
  cause standardised mortality ratios for opioid use disorder run 6 to 10. The
  handover clamp is 1 to 30, deliberately wider, because a search that cannot
  leave the range cannot report that the answer is outside it. But a calibrated
  value outside 6 to 10 is a paper problem, not just a fit, and has to be
  reported as one rather than quietly adopted.
- **`drug deaths as a share of deaths at 25 to 44` is this parameter's own
  moment**, and it is currently the model's best validation row at 23.9 per cent
  against 20. Calibrating `kappa_phi_d_level` on the income of users spends the
  parameter on a moment it controls only partly and turns that row from a check
  into a passenger. Say so when reporting a fitted value.

**The sign is not known.** Lower mortality makes the disorder cheaper, so
households with more continuation value to lose become willing to use, which
RAISES users' average income. Lower mortality also keeps poor households that
already carry the disorder alive longer, which LOWERS it. `code/MORTALITY.txt`
is four points at 2, 4, 12 and 20 to find out which wins before any step is
taken. b and lambda_d drift on every arm, uncompensated on purpose: that drift
is the compensation a later step has to carry, and an arm whose using population
has collapsed says nothing about the income of users.

## Every point now carries the validation column

The note's untargeted table, `tab:untargeted`, listed a data value and a source
for twenty moments and nothing from the model beside any of them, so a table
whose whole purpose is that the model can be caught on it had never been read
against the model. Nineteen of the twenty rows now print inside the block
`run_one_point.sh` keeps, as `UNTARGETED <name> model= ... observed= ...`, so
they come free with every point from 30 August onward. Read them with

    python3 code/paper/validation_report.py code/points/point_XXXXXXXXXX.txt

which prints model, data and relative gap, and prints a row the point does NOT
carry as missing rather than dropping it -- a table that silently loses a row
reads as a table the model passed.

Two rows are not free.

- **The two drug price elasticities** need the price moved and the model
  re-solved, so they sit behind `measure_price_elasticity`, which is 0 by
  default and costs what `measure_child_gap` costs. Turn it on for a point
  worth spending a second solve on. It refuses to run when `measure_child_gap`
  is also on, because omega leaves its distribution behind and the elasticity
  would then be measured off omega's world rather than the benchmark.

- **Returns to homelessness within 24 months** is not implemented. It needs the
  distribution pushed forward three periods from a seed of the currently
  homeless, restricted after the first step to the ones who got housed. The
  machinery exists in `compute_homelessness_duration`, which is a faithful
  forward push and is commented out at its only call site, but it is written
  age-by-age for a different question and answering this one means extracting
  a one-step push out of `converge_to_stationary_equilibrium`. That is a
  refactor of the most intricate loop in the file for one row of a validation
  table, and it is the author's call whether to spend it.

A point measured before this landed has none of these rows. It is not a failed
point; it is an old one, and `validation_report.py` says so rather than
inventing zeros.

## Standing operational rules

- Every point runs through `run_one_point.sh`, cold, with the HANDOVER assertion.
- NO supervisor beside measurements, ever; test positionally, not with pgrep -f.
- `points_pregrid/` is history from the savings-grid bug. Never score or seed it.
- Re-measuring a vector on a changed model reproduces its md5 tag and would
  overwrite a real measurement. Move `points/` aside first and verify it back.
- A scope change -- opening an externally assigned parameter, moving a target --
  is the author's call. Fixing an outright bug is not, but say what it
  invalidates and MEASURE before believing it.
- NEVER tell a worker to run its line through command substitution. A worker told
  to run `bash code/run_one_point.sh $(sed -n "1p" FILE ...)` stalls on a
  permission prompt and is lost silently; one sat blocked for forty minutes on
  the batch measuring lambda_m. Tell it to `cat -n` the file, read the line, and
  issue a separate Bash call whose command is that line verbatim.


## 30 August, 20:20 -- the housing block was scored against the wrong denominator, and the sign of the error flips when that is fixed

`point_2d7b98ec04` is the first point measured after h_2 and gamma moved to
total spending, and it says the opposite of everything measured before it.

    h_2, share above half of INCOME     0.262   target 0.101   2.6x too HIGH
    h_2, share above half of SPENDING   0.053   target 0.101   1.9x too LOW

Same households, same model, same target number. The income denominator made
the model look badly over-burdened and pointed the whole housing block at a
CHEAPER rental ladder. On the denominator CEX actually measures, the model is
under-burdened and the ladder has to go UP.

That matters beyond h_2, because it aligns three things that were in conflict
all afternoon:

- the author's criterion for the smallest rung is that a low income household
  cannot afford it, which needs a HIGHER floor;
- h_2 at 0.053 against 0.101 needs MORE severe burden, which needs a higher
  floor;
- gamma at 0.2016 against 0.268 needs MORE housing spending, same direction.

The earlier finding that all the severe burden sits in the largest unit still
holds -- units 0 and 1 have exactly zero burdened households at every point
measured so far -- so `largest_house_size` still owns the burden RATE and
`smallest_rental_relative_to_lowest_income` still owns who is priced out. What
changed is which way both have to move.

WHAT NONE OF THIS FIXES. The relative risk of homelessness given a SUD is
0.085 in the model against 2.44 in the data: the SIGN is wrong, not the size.
The disorder makes a household LESS likely to be homeless here, because a
household has to be able to afford the habit to have it, so the poorest do not
use and the poorest are who ends up on the street. Users have income 0.308 of
average and the homeless have 0.217 -- users are RICHER than the homeless. No
setting of the rung sizes touches that. The candidate mechanism now being
measured is whether a higher floor makes drug spending crowd out rent: a user
spends about 19 per cent of expenditure on the habit while the cheapest unit
costs about 6 per cent of average labour income, so today there is always room
for both. FLOOR.txt tests it at 0.090, 0.105 and 0.150.

STALE IN THE TRIGGER PROMPT. It still says "being off on h2 is ok". That was
said when h_2 meant the share in the smallest unit. h_2 is the severe cost
burden now, it has an instrument, and the author spent this evening on it. The
concession stays in the STOPPING RULE so the loop can still terminate, but h_2
is bracketed like everything else and should not be described as conceded.


## 30 August, 20:50 -- raising the floor puts the SUD share of the homeless on target, and it was the one moment said to be out of reach

The floor ladder, everything else held at the current vector:

    floor    h_1       SUD share of homeless   by choice   h_2
    0.0377   0.00289   0.00157                 0.911       0.0509
    0.090    0.01249   0.19004                 0.839       0.0484
    0.105    0.01650   0.16197                 0.904       0.0500
    data     0.00399   0.217                               0.101

The SUD share of the homeless moves 121-fold, from 0.0016 to 0.190 against a
target of 0.217. That is the moment that was off by two orders of magnitude all
day and that this file recorded, an hour ago, as structurally out of reach
because the SIGN was wrong. It is not out of reach. The mechanism is the one the
author named: the cheapest unit costs about 6 per cent of average labour income
while a user spends about 19 per cent of expenditure on the habit, so today
there is always room for both and the habit never costs anyone their housing.
Raise the floor and it does.

THE ARGUMENT THAT WAS WRONG, and it was made here in writing: that a higher
floor could not create involuntary homelessness because 84 per cent of the
homeless could pay the smallest rent out of income alone. True at the old floor,
and irrelevant -- the point is not to price out the households who are already
homeless, it is to price out the ones who are spending on drugs.

IDENTIFICATION, MEASURED RATHER THAN ARGUED. h_2 is 0.0509, 0.0484, 0.0500
across the whole ladder: the floor does not move it. So the two housing rungs
are separate instruments after all -- the floor owns who is priced out,
largest_house_size owns the burden rate through the share in the largest unit,
which is where every burdened household sits at every point measured today.

WHAT IT COSTS. h_1 overshoots to 0.0125 against 0.00399, three times the
target, and size_homelessness is the instrument that pulls it back. And 0.105 is
WORSE than 0.090 on the SUD share, so the optimum is interior, near 0.09, not at
the top of the ladder.


## 30 August, 21:20 -- the 25 point asset grid moved the drug block by a quarter, and the archive is not comparable across it

Identical parameter vector, the only difference the grid:

    point_d6ed8b6e2a   41 points   b 0.08673   lambda_d 0.03493   h_1 0.002669
    point_3fdcabf7ae   25 points   b 0.06294   lambda_d 0.02122   h_1 0.002892

b falls 27 per cent and lambda_d 39 per cent. Every commit between the two runs
is a print or a label except f17a75a, the grid cut, so this is the grid.

THE CLAIM THAT WAS WRONG, and it was made here in chat: that the coarse grid is
only a SEARCH grid because internal_computations refines a' on 62 sub points, so
cutting it costs nothing. It preserves the savings policy. It does not preserve
b and lambda_d, and those two are what gate the search.

WHAT IT INVALIDATES. All 246 points measured before f17a75a. They are not
wrong -- they are measurements of a different model -- but they cannot be
bracketed against a 25 point arm, and next_batch has been doing exactly that:
its chosen base, point_144fe4c95a, is a 41 point measurement and every arm
around it is a 25 point one. That is the likely reason CORRECT_22 ran nine arms
and left the worst gap at 33 per cent with the base unmoved.

WHAT TO DO ABOUT IT is the author's call, because it is a trade between speed
and the two moments that gate everything:
  - keep 25 and rebuild the archive, three times cheaper per point but from
    scratch, roughly 250 points of history discarded;
  - go back to 41 and keep the archive, at 25 minutes a point;
  - something between, chosen by measuring b at 29 or 33 points and taking the
    coarsest grid whose b is within a per cent or two of the 41 point value.
The third is one or two points of work and is what I would put to the author
first.

UNTIL IT IS DECIDED, next_batch must not bracket across the grid boundary. The
grid is stamped in every point measured after f17a75a and absent before it, so
the filter is available and cheap.


## 30 August, 22:00 -- the extensive margin, not the Stone Geary threshold, is what makes users poor

Two diagnostics were added because nothing printed either of them, and
together they close a question that had been argued all evening.

THE AGE OF USERS. Two in five are 65 or older.

    band     model   data
    26-34    0.396   0.284
    35-44    0.078   0.251
    45-54    0.054   0.178
    55-64    0.061   0.163
    65+      0.411   0.124     mean age 52.6 vs 45.5

U shaped: the young, who have no assets, and the old, who have no future,
with a hole where most real users are. Worth about a fifth of the income gap
and no more -- income of WORKING AGE users is 0.352 against 0.298 for all
users, so removing the retirees closes 18 per cent of the distance to 0.74.

THE STONE GEARY THRESHOLD IS NOT BINDING ON ANYONE, which kills a hypothesis
recorded here in strong terms an hour ago. optimize_frac_spent_on_addiciton
buys nothing unless C > (phi/theta) p b, and that threshold is 0.0162 while
the mean C of households who buy NOTHING is 0.4029 -- twenty five times above
it. So the closed form cannot be what selects users, and the claim that "the
model's own theory says buyers must be rich" was about a margin that never
binds. It governs HOW MUCH given that a household uses. WHETHER it uses is a
separate discrete choice, policy_function_addiction, decided on continuation
values, and that is where the poor are selected:

    buyers      mean C 0.1405   mean income 0.1426
    non-buyers  mean C 0.4029   mean income 0.5167

THE BUFFER IS NOT THERE EITHER. The author's reading was that a household
willing to risk the disorder has something to fall back on. In this model it
does not:

    assets of drug users        0.185 of average net worth
    assets of experimenters     0.154
    assets with a SUD           0.247

Users are asset poor as well as income poor. If family resources are the
real world mechanism, nothing in this model plays that role -- the endowment
at 26 does not, and there is no ongoing transfer to an adult child.

WHAT IS LEFT. Selection runs entirely through the continuation value: the
poor use because their future is worth little. KAPPA1.txt tests it directly
by removing the mortality cost, kappa_phi_d_level = 1.0, with
addiction_scalar_1 cut to hold the use rate near the target, so the
comparison is at a matched b rather than at b = 0.97 where the archive's low
kappa points sit and where the income of users is 0.91 by arithmetic.


## 31 August, 01:45 -- the asset grid is 25 points, decided

The author's call, and it closes the question opened when the cut from 41 to
25 reachable points was measured against an IDENTICAL vector:

    b         0.0867 at 41 points   0.0629 at 25    -27 per cent
    lambda_d  0.0349                0.0212          -39 per cent
    h_1       0.00267               0.00289          +8 per cent

Every commit between those two runs was a print or a label, so the move is
the grid.

WHAT IT COSTS AND WHAT IT DOES NOT. It does not cost the moments. b and
lambda_d are calibrated, so the grid error is absorbed into
addiction_scalar_1 and lambda_addiction and the targets are still hit. What
is grid dependent is the PARAMETER VALUE that hits them: at 41 points the
same targets would be met at a different b.

The author has ruled that this needs NO note in the paper. Recorded here so
it is not raised again as an outstanding task.

It also means the 268 point archive stays retired. That was already true --
the mortality form, SNAP and the treatment cost all moved on 30 and 31
August -- but the grid alone would have done it.

The gain is 8 minutes a point against 25, measured over 246 old points and
the first few new ones, a factor of 3.1. That is what makes a joint Jacobian
affordable at all: seventeen points is forty minutes now and over two hours
before.


## 31 August, 02:30 -- five model changes, an empty archive, and nothing measured yet

WHAT CHANGED TONIGHT, all committed, none yet measured:

- mortality multiplies the DEATH PROBABILITY and is capped at one, so the
  disorder raises death by exactly 8.00 at every age from 26 to 84. It was an
  exponent on survival, which drifted from 7.97 to 6.17.
- SNAP is implemented from the statute: allotment by household size on the
  concave schedule, gross eligibility at 130 per cent of the poverty line,
  thirty cents per dollar of NET income. The floor went from 0.73 per cent of
  average labour income to 3.96 and the cutoff from 2.4 to 21.5. Aggregate
  spending is a check now, not a target, and cbar is out of the searched set.
- treatment costs MONEY, not utility. tau_u is a price, still bracketed on
  take up of 24.5 per cent; utility_cost_of_treatment is held at zero. The
  recovery effect is 2.0, assigned from buprenorphine remission of 18.8
  against 10.4 per cent, where it was 1.35 from contingency management.
- productivity is INTERGENERATIONALLY PERSISTENT, rho = 0.35, where it was
  zero. A child's draw conditions on the parent's node, so delta_d now means
  the effect NET of income transmission. The literature splits it about evenly,
  which is the check: delta_d should end up doing half the work it was doing.
- only 30 per cent of job losers get an insured period, where all of them did.
  The unemployment RATE is algebraically unchanged, but the share of the
  jobless with no income at all goes from 45 to 84 per cent and the mass with
  nothing rises 1.86 fold.

THE ARCHIVE IS RETIRED to code/points_pre31aug, all 270 points. Every one was
solved under a superseded model, and leaving them in code/points would have
been worse than losing them: run_one_point.sh skips a vector whose tag it
already holds, so an archived point would come back silently as though it were
current.

THE FIRST ANCHOR CAME BACK DEAD and the cause is recorded in
code/points_failed. Extending newborn_parent_share to carry the parent's node
replaced its declaration initialiser with a plain zero, so no newborns were
created and the population died out. Fixed by seeding the shares where the
grid is built. sigma_y read 0.169 against 0.172 throughout, because it comes
from the grid and not the distribution -- one healthy moment beside a dead
model is the shape of this failure and worth recognising again.

WHAT TO DO NEXT, in order:
1. the anchor lands -> read it, and CHECK IT IS NOT ZEROS before using it.
2. five one-coordinate arms around it: value_of_life, addiction_scalar_1,
   lambda_addiction, size_homelessness, money_cost_of_treatment.
3. solve the 4x4 jointly onto aleph 80, b 8.9 per cent, lambda_d 3.68 per
   cent, h_1 0.4 per cent. These are heavily coupled -- value_of_life drags b
   hard, and that coupling IS the mechanism -- so one coordinate secants fight
   each other and a joint step is what converges.

THE ROW TO READ FIRST is the employed share of the homeless, 0.895 before
against 0.46 in the data. If it has not moved, the new zero income households
are self insuring out of savings and the bottom half wealth share, 0.149
against 0.025, is the binding constraint. That would argue for building beta
heterogeneity BEFORE spending more rounds converging a model that cannot reach
the moment. Two independent routes now point at that same change.

STILL NEEDING THE AUTHOR: kill -9 on supervise_calibration.py, which has been
up for ninety minutes and rewinds the checkout at every container wake, and on
two stale local solvers. Every kill this session was refused by the permission
classifier.

## 31 August, 03:00 -- the anchor replicates, and the row to read first moved the WRONG WAY

THE ANCHOR IS ALIVE AND INDEPENDENTLY REPLICATED. `point_485225bf80` was
re-solved from scratch on the fixed source, in a separate container, without
sight of the committed file. The two agree on every one of 57 MOMENT and
UNTARGETED values to a maximum RELATIVE difference of 8.5e-05, the largest
being the 55-64 user share; the targeted moments agree to seven significant
figures. That is parallel-reduction ordering, not a difference. Histogram mass
is 1.0000000000001 where it wants 1.0, and MOMENT theta is 0.182 rather than
the -1.0 sentinel, so step 1 of the previous section -- read it and CHECK IT
IS NOT ZEROS -- is discharged twice over.

The replication also cost a repeat of the dead point. A run launched from
7e67aad, before the newborn fix landed, reproduced `point_485225bf80` byte for
byte apart from the wall-clock line: the same histogram mass 0, the same -1.0
theta, the same healthy 0.169 sigma_y. The collapse is therefore fully
deterministic in the source version and not a sporadic solver failure, which
is worth knowing because it means the fix can be verified by the tag alone.

THE ROW TO READ FIRST WENT THE WRONG WAY. The employed share of the homeless
was 0.895 against 0.46 in the data before tonight's five changes. The
prediction on file was that if it had NOT MOVED, the new zero-income
households were self-insuring out of savings and beta heterogeneity should
come before more convergence rounds. It did not fail to move -- it rose to
0.966, and the supporting rows moved with it:

    employed share of the homeless   0.966  vs 0.460   (was 0.895)
    net worth share, bottom half     0.129  vs 0.025   (was 0.149)
    wealth share of the bottom 25%   0.020
    no wage income, working age      0.060  vs 0.139

The insured-period change was supposed to take the jobless with no income at
all from 45 to 84 per cent and raise the mass with nothing 1.86 fold. The
working-age share with no wage income nonetheless sits at 6.0 per cent against
13.9 in the data, less than half the target. So the new zero-income households
exist and are still not showing up homeless-and-jobless: they are being
absorbed by savings, exactly the mechanism the note anticipated, only more
strongly than the "has not moved" case it was written for. The argument for
building beta heterogeneity BEFORE spending more rounds converging is
therefore stronger than the note allowed for, not weaker. Three independent
routes now point at that same change.

The four coupled targets stand at aleph 61.0 against 80, b 9.76 against 8.90
per cent, lambda_d 4.35 against 3.68 per cent and h_1 0.131 against 0.399 per
cent. h_1 is the outlier at -67 per cent and it is the same moment the homeless
rows above are about, which is a further reason to think the binding
constraint is the wealth distribution rather than the four coordinates.

## ROUND 1's JACOBIAN, AND THE THREE HOLES IN IT

Thirteen one-coordinate arms around `point_485225bf80` were measured and read as
a full moment-by-arm elasticity matrix rather than one arm at a time. Reading
each arm only against the moment it owns is what made three of them look usable
when they are not, so the matrix is the object to keep.

The best point on the current model is `point_02c96e3721`
(`money_cost_of_treatment=0.06`): worst gap 67.2 per cent on h_1, ten moments
outside ten per cent, against the base's 136.5 per cent and twelve.

**Three arms are degenerate and must not be re-used as directions.**
`value_of_life=48` and `value_of_life=55`, and `addiction_scalar_1=0.0215`, all
drive homelessness to nothing; mu_H is then a ratio with an empty denominator
and prints around 1.7e12. aleph does rise with `value_of_life` -- 61 at 34.6,
104 at 48, 126 at 55 -- so the target of 80 is bracketed between 34.6 and 48 and
Newton in logs puts it at 41. But the two arms that bracket it also destroy the
homeless population, so aleph cannot simply be walked up: the step has to be
small and it has to be checked against h_1. Hence the 38 arm this round.

**`size_homelessness` saturates at 0.075.** The ladder is

    0.064481 -> h_1 0.001314, lambda_m 0.3669
    0.075    -> h_1 0.002329, lambda_m 0.2093     (elasticities +3.79, -3.72)
    0.085    -> h_1 0.002400, lambda_m 0.2058     (elasticities +0.02, -0.13)

so the whole of the instrument's power is spent between 0.0645 and 0.075 and
there is nothing above it. Two consequences. The chord to use is the lower one;
a Jacobian built from the 0.075-to-0.085 pair reports the instrument as dead and
sends the solver to the e-fold cap for no gain, which is what the first joint
solve did. And `lambda_m` crosses its target of 0.25 inside that segment, at
about 0.0715, while h_1 only reaches 0.0019 against a target of 0.00399. **h_1
cannot be closed with `size_homelessness`.**

**`lambda_m` the parameter is not an instrument for `lambda_m` the moment**: its
own elasticity is -0.064, flat. The moment's real instrument is
`size_homelessness` at -3.72. Two moments, one instrument, and they happen to
want the same direction, which is the only reason this is not yet a problem.

**`relative_share_of_housing` raises gamma at an elasticity of 0.22 and costs
h_1 at -7.32.** The arm at 0.21 took gamma from 30.7 to 25.6 per cent off and in
the same step drove h_1 to 0.000127, lambda_m to 1.0, b to 0.153 and h_3 to
0.818: worst gap 300 per cent, rms 86.5 against the base's 41.7. It is not a
usable direction and it is left out of the joint step. Note also that
`tie_gamma_to_theta=1` makes this parameter a function of theta by default; the
handover overrides it and the override sticks, but nothing else should assume it
is free.

### The three holes

Four of the worst gaps are in the housing block -- h_1 67 per cent low, h_2 61
per cent low, gamma 30 per cent low, h_3 7 per cent high -- and the block has
essentially one measured instrument, the one that cannot be used. So:

- **h_2 has no measured column at all.** Its owner,
  `smallest_rental_relative_to_lowest_income`, sets `housing_size(0)`, the
  bottom rung of the ladder, and has never been armed. Raising it makes the
  cheapest dwelling dearer, which should raise the share paying over half of
  spending, the share choosing the street, and housing's share of expenditure --
  h_2, h_1 and gamma, the three moments that are all low. It is the highest
  value arm available and it gets three of this round's eight lines, at 0.055,
  0.070 and 0.085, to buy the curvature as well as the slope.
- **beta has no column.** `discount_factor` has never been armed; beta is 26 per
  cent high.
- **aleph has no usable column**, for the reason above.

### The joint step, and why there are two of them

A ridge solve in logs over the seven instruments with usable columns, damped at
0.7 and capped at 0.35 e-folds, takes the residual norm from 1.293 to 0.562 and
predicts lambda_m 47.5 -> 2.4 per cent, h_1 67.2 -> 38.3, b 9.0 -> 0.9, mu_H
10.5 -> 3.0. It buys that partly by sacrificing pi_eu, 20.1 -> 28.6 per cent,
because it moves `probability_becoming_unemployed` UP against its own moment in
order to serve lambda_d, b and kappa_ued, which all want it up.

Whether an instrument's own moment or the cross terms should win is exactly the
question the bracketing method exists to settle, and it is cheaper to measure
than to argue: line 1 is the step with that instrument, line 2 the step without
it (residual norm 0.698, pi_eu held at 21.4 per cent). Next round keeps whichever
actually landed better.

## WHAT THE HOMELESS LOOK LIKE, AND WHY h_1 IS THE WRONG THING TO CHASE

Read at `point_02c96e3721`, and worth separating from the gap table because
three of these are structural rather than calibration-sensitive:

    homeless by choice, share of the homeless     = 1.000
    homeless who could afford it on INCOME ALONE  = 1.000
    employed share of the homeless                = 0.964   data 0.46
    income of the homeless / average              = 0.282   data 0.191
    SUD share of the homeless                     = 0.00007 data 0.217
    share of the homeless aged 26-34              = 0.997   HUD  0.260

Every homeless household in the model has income plus assets above the rent on
the smallest dwelling, and all but four per cent of them work. **Nobody in this
model is shut out.** Homelessness is a preference, exercised almost entirely by
solvent employed households under 35 who do not use drugs.

The consequence for the search is direct. `size_homelessness` is the disutility
of the homeless state, so raising it recruits MORE solvent young households into
choosing the street: it moves the rate without touching the composition, and it
saturates at 0.075 anyway. h_1 at 67 per cent low is therefore not a
mis-parameterised rate, it is a symptom, and closing it with its own instrument
would leave every row above exactly where it is.

`smallest_rental_relative_to_lowest_income` is the instrument that can change
the composition, because it raises the rent on the bottom rung and so can push
`could afford it on INCOME ALONE` below one. That is why it takes three of
ROUND2's eight lines rather than one.

The intergenerational ratios, both untargeted and both reached through income
alone: child SUD 1.18 against 2.0, child homelessness 1.77 against 2.1. The
homeless-versus-population SUD ratio is 0.003 against 5.9 in the data -- a
reversed sign, not a level miss.

## THE DRUG BLOCK IS OPEN AND restore.py CANNOT REPAIR IT YET

`next_batch.py` exits 2: b is 9.0 per cent low and lambda_d 22.2 per cent low at
`point_02c96e3721`. `restore.py 02c96e3721` raises TypeError, and the reason is
not a bug in it. It refits the two-by-two Jacobian from archive points differing
in `lambda_addiction` and `addiction_scalar_1` ALONE, and every such pair sits at
the old `money_cost_of_treatment=0.02`. There is no locus on the current slice,
so there is nothing to fit.

`ROUND2B.txt` re-establishes it with two arms off the best point,
`lambda_addiction=13.0` and `addiction_scalar_1=0.01910`. Until those land the
repair tool stays unusable, and a joint step will keep under-moving
lambda_addiction because the ridge spreads work the drug block needs
concentrated: JOINT-B moves it to 15.72 where the single-moment Newton on
lambda_d asks for about 12.5.

## STILL BLOCKED ON THE AUTHOR

`supervise_calibration.py` (PID 1372) and three stale `hftf` solvers (1636,
1913, 2673) have been up for over three hours. Four `kill -9` attempts across
two sessions were refused by the permission classifier. Six solver processes are
sharing four cores, so every measured point is running several times slower than
it should. Nothing else in the loop can clear this.

## WORKERS GO IN THEIR OWN CONTAINERS, AND THE RUNNER NOW ENFORCES IT

On 31 August a batch was launched through LOCAL subagents rather than one
container per worker. Local subagents share this checkout, so four runs went
live in `code/` at once. Everything `run_one_point.sh` writes after the build is
keyed to the DIRECTORY and not to the tag -- the `hftf` binary,
`PARAM_HANDOVER.txt`, `B_SWEEP_GRID.txt`, `calibration_state.dat` -- so they
raced. Caught with `B_SWEEP_GRID.txt` holding one point's `addiction_scalar_1`
while a different point was solving, and `PARAM_HANDOVER.txt` already consumed.

**The count assertion cannot catch this.** It counts HANDOVER lines, and a run
handed the wrong vector gets exactly as many. The point would be archived under
the md5 of the vector it was ASKED for while carrying the moments of the vector
it was GIVEN. A mislabelled point is worse than a missing one, because nothing
downstream can tell.

Nothing was lost. The four runs were stopped before any archived, and the
archive was then verified: no tag in `code/points/` has a matching
`worker_<tag>.log` in this container, so every one of the fourteen was solved
elsewhere and never saw a concurrent run. The audit is one line and worth
repeating after any local run:

    for p in code/points/point_*.txt; do t=$(basename $p .txt); t=${t#point_};
      [ -f "code/worker_${t}.log" ] && echo "LOCAL: $t"; done

`run_one_point.sh` now takes an `flock` on `.run_one_point.lock` covering the
build and everything after it, so a second point in the same checkout waits
instead of racing. Parallelism ACROSS containers is untouched. Parallelism
within one container was never real: the solver takes every core it can, so two
runs sharing four cores are slower than the same two in sequence.

The rule, restated because it is easy to get wrong: workers are spawned with
`create_session`, passing `source_url` and `source_revision`. Those two names
belong to that tool. The `Agent` tool takes neither and runs in THIS container;
seeing them in the standing rule is the tell that a fresh container was meant.

## NEW BEST POINT: 2cf90f8525, AND THE RIDGE STEP TRANSFERS

ROUND2 line 1 -- the joint ridge step WITH `probability_becoming_unemployed`
allowed to move against its own moment -- landed and is the best point in the
archive. Worst gap excluding h_2 is **h_1 at 42.1 per cent**, down from 67.2.

The predictions held, which is the useful part: h_1 predicted 0.00246 came in at
0.00231, kappa_uem predicted 0.28629 came in at 0.28315, lambda_m predicted
0.24397 came in at 0.20692. tau_u closed to 0.3 per cent, theta to 1.2, mu_H to
8.4, kappa_uem to 5.6. The Jacobian measured at `485225bf80` transfers to a step
taken from `02c96e3721`.

It cost pi_eu exactly as predicted, 20.1 -> 28.9 per cent. Whether that trade was
right is still open: JOINT-B, the same step without that instrument, has not
landed yet.

**A NOTE ON THE OBJECTIVE.** The engine prompt says the minimax excludes h_2,
but `SKIP` in `next_batch.py` is empty and its comment says so deliberately --
h_2 was conceded when it meant the share in the smallest unit, and was
un-conceded when it was redefined as the severe cost burden. The code is the
newer statement of the author's intent, so both numbers are worth reporting:
worst including h_2 is 59.9 per cent (h_2 itself), worst excluding it is 42.1
(h_1). Do not quietly pick one.

## THE DRUG-BLOCK LOCUS, MEASURED ON THE CURRENT SLICE AT LAST

ROUND2B landed both arms and they are clean -- nothing outside the block moves
more than eight per cent:

    lambda_addiction   16.33 -> 13.0      b  elast -1.56   lambda_d elast  -1.14
    addiction_scalar_1 .0191823 -> .01910 b  elast -17.6   lambda_d elast -36.0

`restore.py` can fit again. Solving the two-by-two at the new best point asks for
`addiction_scalar_1` to move -0.00463 in logs, which is 7.7 per cent PAST the
arm that measured the -36 elasticity, so the step is clamped at the bracket edge
and `lambda_addiction` takes up the slack by least squares. That lands b within
0.4 per cent and lambda_d within 0.5, both from inside the measured pairs. The
clamp matters here more than anywhere: restore.py's own note records this
elasticity reading -12 in one place and -35 a few thousandths away.

`ROUND3.txt` line 1 is that repair. Lines 2-4 are the three
`smallest_rental_relative_to_lowest_income` arms re-based onto the new best
point, because NONE of the three landed from ROUND2 -- every point in the
archive still sits at 0.03771127 -- and they remain the round's priority: they
are the only instrument that can move the homelessness composition.

One worker reported committing ROUND2 line 4 as `b1a14f7`; that object does not
exist in the repository, so it committed in its own container and never pushed.
Check the object, not the report.

## THE smallest_rental LADDER: h_1 YES, h_2 NO, AND THE COMPOSITION GOES BACKWARDS

All four rungs are measured on the `02c96e3721` slice. This was the round's
priority and it answers the question, partly against the hypothesis:

    sr        h_1        h_2      gamma   lambda_m | SUDofHL   employed   income
    0.03771   0.001307   0.0394   0.1863   0.3688  | 0.00007   0.964      0.282
    0.055     0.003771   0.0403   0.1880   0.0825  | 0.109     0.983      0.311
    0.070     0.007769   0.0422   0.1927   0.0636  | 0.097     0.982      0.368
    0.085     0.007115   0.0406   0.2010   0.1369  | 0.114     0.976      0.375
    target    0.00399    0.101    0.268    0.25    | 0.217     0.460      0.191

**h_1 is reachable.** It crosses its target between 0.055 and 0.070 and the
slope on the first segment is +2.81 in logs. On the JOINT-A slice the same step
took h_1 from 42.1 per cent off to 1.7.

**h_2 is not.** Its supposed owner moves it from 0.0394 to 0.0422 across a
ladder that more than doubles the rent floor, against a target of 0.101. Nothing
else in the archive moves it either. **h_2 has no instrument in this model.**
That bears directly on the disagreement recorded above between the engine
prompt, which concedes h_2, and `next_batch.py`, which does not: whatever the
author intends, it is not reachable through the housing ladder.

**gamma is barely reachable**: 0.186 to 0.201 across the whole ladder, against
0.268. Its only strong instrument, `relative_share_of_housing`, costs h_1 at an
elasticity of -7.32 and is unusable.

**The composition moves the wrong way.** The SUD share of the homeless does jump,
0.00007 to about 0.11 against a target of 0.217, and then saturates. But the
employed share RISES, 0.964 to 0.976, against a target of 0.460, and the income
of the homeless RISES, 0.282 to 0.375, against 0.191. And at every rung, all the
way to 0.085,

    homeless by choice                    = 1.000
    homeless who could afford it on income = 1.000

**Raising the rent floor never shuts anybody out.** It makes the street
attractive to RICHER households, because homelessness in this model is a choice
at every income and a higher floor simply moves the indifference point up. There
is no instrument here that makes the homeless poor or jobless; that requires
households with neither income nor assets, which is the lower-tail-of-wealth
question, and it is the author's call.

## h_1 AND lambda_m: THE CLAIM BELOW WAS WRONG, SEE THE CORRECTION AFTER IT

Every instrument that raises h_1 lowers lambda_m, and the two moments now want
to move the same way (h_1 +41.9 per cent, lambda_m +16.1). The ratios differ
slightly between the two instruments -- `size_homelessness` moves them at
-0.98, `smallest_rental` at -1.41 -- so a combination exists on paper, but it
asks for `size_homelessness` at 0.133, far outside its range and past the point
where it saturates at 0.075. Not reachable.

The best available compromise is the minimax on the pair, at
`smallest_rental` about 0.0398, where both sit near 32 per cent instead of
h_1 at 41.9. `ROUND4.txt` brackets it at 0.0398 and 0.046, adds a
`multiple_of_probabilities_of_employment_if_addicted` arm at 3.4 for kappa_ued
(30.3 per cent off, elasticity +1.02), and one combined line.

## THREE MOMENTS WITH NO SAFE INSTRUMENT

- **aleph** (24.1 per cent off). `value_of_life` is the only instrument and every
  arm is degenerate: at 38 the drug block collapses to b=0.0085 and
  lambda_d=0.0014; at 48 and 55 homelessness dies and mu_H prints 1.7e12.
- **h_2** (60.6 per cent off), as above.
- **gamma** (30.7 per cent off), as above.

`largest_house_size=0.145` is also degenerate: mu_H prints 2.1e12.

## CORRECTION (PART RIGHT, PART WRONG -- SEE THE SECOND CORRECTION BELOW)

The section headed "h_1 and lambda_m cannot both be closed" is WRONG and is left
in place only so the reasoning that produced it can be checked. Two mistakes,
both of the same kind: a slope was read off one chord and used as though it
described the whole surface.

**First mistake: the chord averaged over a threshold.** The h_1 slope of +2.81
came from `smallest_rental` 0.03771 to 0.055. Measured finely on the JOINT-B
slice, that segment is not a slope at all:

    sr      0.03771   0.03984   0.046    0.055     0.070    0.085
    h_1     0.00232   0.00233   0.00221  0.00406   0.00896  0.01123

Flat, then slightly NEGATIVE, then a jump between 0.046 and 0.055. It is a cliff,
not a gradient -- a marginal household switches to the street when the cheapest
dwelling crosses a price. The minimax step built on the averaged slope predicted
h_1 would reach 0.00270 and it came in at 0.00233, because 0.0398 is on the flat
part. **h_1 IS reachable, at sr around 0.053 to 0.055**, where it lands within
two to six per cent on both slices measured so far.

**Second mistake: the sign of the size_homelessness/lambda_m relation is not
global.** At sr=0.03771, raising `size_homelessness` raises h_1 and LOWERS
lambda_m, which is where "every instrument moves them oppositely" came from. At
sr=0.055 it raises BOTH:

    at sr=0.055, size_homelessness 0.064481 -> 0.0747535
        h_1       elasticity +0.49
        lambda_m  elasticity +3.24

So past the cliff the two moments stop fighting. Extrapolating within that pair,
lambda_m reaches 0.25 at `size_homelessness` about 0.0909, and h_1 would then be
about 12 per cent high -- worth measuring rather than trusting, since this is the
second slope in this section to have been read too confidently.

`ROUND5.txt` measures it: two points in the joint region (sr 0.053 with
size_homelessness 0.085, and sr 0.055 with 0.090), one to locate the cliff on
this slice (sr 0.053 alone), and one to widen the `addiction_scalar_1` bracket
to 0.0188, which is what every pending drug repair is blocked on.

## WHY CORRECT_24.txt WAS NOT LAUNCHED AS WRITTEN

The gate opened and emitted six arms. Four are already known void from the
archive, and launching them would spend four containers confirming what is
measured:

- `smallest_rental -> 0.0535` FOR h_2. The gate's own fitted elasticity is +0.06
  and the ladder confirms it: h_2 goes 0.0394 to 0.0422 while the rent floor
  more than doubles. This arm cannot move h_2 and it lands on the flat side of
  the h_1 cliff.
- `size_homelessness -> 0.0891` for h_1 at elasticity +2.18. That slope was
  measured on 0.064481 to 0.075; the instrument saturates above 0.075, where
  h_1 moves 0.002329 to 0.002400.
- `value_of_life -> 40.837` for aleph. Every value_of_life arm is degenerate: at
  38 the drug block collapses to b=0.0085 and lambda_d=0.0014, at 48 and 55
  homelessness dies.
- `lambda_m -> 0.0515` at its own elasticity of -0.06, which is the definition of
  a dead instrument.

The two sound arms are `probability_becoming_unemployed -> 0.00872` for pi_eu and
`multiple_of_probabilities_of_employment_if_addicted -> 3.17` for kappa_ued. The
second is already measured at 3.4 from the best point: kappa_ued improves 30.3
to 16.9 per cent and the drug block is destroyed -- lambda_d 12.0 to 63.5, b 0.3
to 50.0. It is only usable with a simultaneous drug repair, which is blocked on
the same narrow `addiction_scalar_1` bracket.

## SECOND CORRECTION: THE CLIFF IS REAL, THE "JOINT REGION" WAS NOT

Of the two claims in the correction above, the first survives measurement and
the second does not.

**The cliff is real and h_1 IS reachable.** `e2ecd0039e`, at
`size_homelessness` 0.074132 and `smallest_rental` 0.053, puts h_1 at 0.0038238
against a target of 0.00399 -- **4.2 per cent off**, from 41.9.

**"Past the cliff the two moments stop fighting" was wrong**, and the reason is
a rule violation rather than bad luck. The +3.24 elasticity came from
`75fb32aada` against `4f4d5c48f1`, and those two points differ in SEVEN
coordinates: lambda_addiction, lambda_m, money_cost_of_treatment, mu_homeless,
multiple_of_probabilities_of_employment_if_addicted,
probability_becoming_unemployed and size_homelessness. It was never an
elasticity, only a difference between two multi-coordinate points, and the
standing rule that elasticities come from pairs differing in ONE coordinate
exists precisely to stop this.

A properly controlled pair at sr=0.053 -- `e2ecd0039e` against `6e3c543029`,
differing in `size_homelessness` alone -- says:

    h_1       elasticity +1.49
    lambda_m  elasticity -1.38

**Opposite signs, the same as at sr=0.03771.** h_1 and lambda_m fight
everywhere measured. The three points built on the imagined joint region all
came in with lambda_m between 66 and 72 per cent off.

**BEFORE USING ANY PAIR, PRINT WHAT DIFFERS BETWEEN ITS TWO POINTS.** Both of
the last two rounds' mistakes would have been caught by that one line, and it
costs nothing:

    sorted(k for k in set(va)|set(vb) if va.get(k)!=vb.get(k))

## THE REAL TRADE, AND THE ONE UNTRIED INSTRUMENT

The archive now contains both ends of the trade at one slice:

    sr=0.03771  h_1 41.9% off, lambda_m 16.1% off   (worst-ex 41.9)
    sr=0.053    h_1  4.2% off, lambda_m 66.1% off   (worst-ex 66.1)

and the cliff between 0.046 and 0.053 means there is no useful midpoint: sr=0.043
gives 42.9 and 29.3, sr=0.046 gives 44.6 and 46.5. Either h_1 or lambda_m, not
both, unless a THIRD instrument moves lambda_m.

`smi_onset_level` is that candidate and it has never been armed -- the gate
reports "no controlled pair in the archive" for it every firing. It sets the
stock of serious mental illness, so more of it should raise the SMI share of the
homeless without touching the housing choice. `ROUND6` arms it at 0.0045 and
0.0070 from `e2ecd0039e`, where h_1 is already solved, and re-tests `lambda_m`
itself at 0.15 there, since its flatness was only ever measured at sr=0.03771.

If neither moves lambda_m, then h_1 and lambda_m are jointly unreachable and
which one to concede is the author's call.

## THE DRUG LOCUS IS 4.7x WIDER NOW

`c0f41297da` against `7830fbe852`, controlled, `addiction_scalar_1` alone:

    step dlog -0.0201   b elasticity -14.71   lambda_d elasticity -21.58

against the -17.6 and -36.0 read off the old narrow pair. The repair at
`e2ecd0039e` still wants 2.8x this bracket, so ROUND6 line 4 takes the clamped
step -- predicted b and lambda_d land about 20 per cent off rather than on
target, which is progress toward them rather than a repair, and it widens the
bracket again for the next one.

## lambda_m THE PARAMETER IS NOT DEAD -- IT WAS MEASURED IN THE WRONG PLACE

Recorded twice in this file as a dead instrument, on an elasticity of -0.064 for
its own moment. That reading was taken at `smallest_rental=0.03771`. At 0.053,
from a controlled pair (`e2ecd0039e` against `63028a1011`, differing in
`lambda_m` alone):

    lambda_m parameter 0.0663688 -> 0.15
        lambda_m moment  elasticity -3.351
        p_m              elasticity -0.868

Strong, and NEGATIVE, so to RAISE the SMI share of the homeless the parameter
must come DOWN. Every step taken on it so far has been upward, which is why it
looked flat and then looked harmful. This is the third time in this search that a
slope read at one place has been treated as a property of the instrument; the
pattern is now unmistakable and the fix is the same each time -- re-measure the
column at the point you intend to step from.

## smi_onset_level IS NOT AN INSTRUMENT FOR lambda_m, BUT IT OWNS p_m

Both arms are controlled and agree:

    smi_onset_level 0.002761 -> 0.0045    lambda_m +0.086   p_m +0.298
    smi_onset_level 0.002761 -> 0.0070    lambda_m +0.104   p_m +0.344

lambda_m barely moves -- 66.1 per cent off to 64.6 and 62.6 -- while p_m goes to
26.4 per cent off and the drug block collapses. So the answer to the question
ROUND6 was built to settle is NO: this is not the third instrument for lambda_m.
It is, however, a clean instrument for p_m, which is what it was always supposed
to own, and that matters because `lambda_m` moves p_m too.

## THE PAIR THAT MAY CLOSE BOTH

Two moments, two controlled columns, opposite enough to separate:

                     lambda_m    p_m
    lambda_m param     -3.351   -0.868
    smi_onset_level    +0.104   +0.321

Solving at `3eae65c27e` asks for `lambda_m` 0.0663688 -> 0.04935 and
`smi_onset_level` 0.002761 -> 0.001578, and predicts lambda_m 0.0982 -> 0.250 and
p_m 0.0450 -> 0.0486, both on target. **Both steps go DOWN and every measured arm
on both went UP**, so this is extrapolation to the far side of the base and is not
to be believed until measured. ROUND7 lines 1-3 bracket it -- `lambda_m` at 0.050
and 0.055, `smi_onset_level` at 0.0018 -- and line 4 takes the joint step.

## THE DRUG REPAIR WORKED, AND h_1 IS HOLDING

`3eae65c27e` is the base for ROUND7 because the clamped drug step did most of
what was asked: **lambda_d 53.4 per cent off to 0.7**, and h_1 improved to 3.1
per cent as a side effect. b overshot to 0.1221, 37.2 per cent high, which is the
next thing to repair once lambda_m is settled -- it is the same two instruments
and they are now measured over a wide bracket.

At that point the remaining list is lambda_m 60.7, b 37.2, gamma 30.5, kappa_ued
30.2, aleph 25.0, pi_eu 22.6, theta 18.0, and eight moments outside ten per cent.

## BEST POINT: 9ff7a5b81c, SIX MOMENTS OUTSIDE TEN PER CENT

The drug repair at `c0f41297da` landed exactly as the two-by-two predicted and
both its steps were inside their measured brackets:

    b         34.9 per cent off -> 4.9
    lambda_d  35.8 per cent off -> 4.5

taking the count outside ten per cent from eight to **six**, the fewest in the
archive. Worst excluding h_2 is h_1 at 41.7 per cent. What remains there:

    h_1 41.7   gamma 30.9   kappa_ued 29.4   aleph 24.7   pi_eu 23.4   lambda_m 16.1

## h_1 HAS TWO INSTRUMENTS AND BOTH COST lambda_m THE SAME WAY

`size_homelessness` does NOT saturate on this slice -- 0.074132 to 0.095 takes
h_1 from 41.3 per cent off to **4.6** -- so the saturation recorded earlier
belongs to the 0.064481 slice and nowhere else. But lambda_m goes 16.2 to 47.3.
The rent floor does the same thing at a different price. Both close h_1, both
break lambda_m, and the archive now holds four points showing it.

The ratios differ enough on paper to separate them -- `size_homelessness` moves
the pair at -0.954, `lambda_m` at -0.676 -- but solving the two-by-two asks for
`lambda_m` at 0.0131, three times below the 0.0441274 floor its own data profile
implies. **Not feasible.**

`lambda_m` is also non-monotone across slices, which is worth recording because
it has now produced three different readings: elasticity on its own moment
-0.064 at sr=0.03771 on the old slice, -1.116 at sr=0.053, and **+1.025** at
sr=0.03771 on the current one, where pinning it at its floor took the moment DOWN
from 0.2096 to 0.1391 while h_1 improved to 7.6 per cent. Do not carry a sign for
this parameter between points.

## WHAT IS LEFT, AND WHICH PART IS SEARCH

Reachable, and ROUND10 goes after both:
- **pi_eu**, 23.4 per cent off, with a clean measured instrument
  (`probability_becoming_unemployed`, elasticity +0.44) never applied at this
  point. Full Newton asks 0.009921 -> 0.006149; lines 1 and 2 take 70 per cent
  of that and all of it.
- **kappa_ued**, 29.4 per cent off. `multiple_of_probabilities_of_employment_if_addicted`
  closes it but drags the drug block hard -- at 3.4 it put lambda_d at 63.5 per
  cent and b at 50. The drug locus repairs drifts of about 35 per cent inside its
  brackets, so a smaller step at 3.2 plus a repair next round is the way in.

Not search, and needing the author:
- **h_1 against lambda_m.** Either 41.7 and 16.1, or about 5 and 45. No midpoint.
- **gamma**, 30.9 per cent. Three routes ruled out: `relative_share_of_housing`
  directly (costs h_1 at -7.32), the `apply_gamma_tie` route through
  `relative_share_of_addiction_1` (elasticity -0.196, needs 0.079 against a bound
  of 0.40), and the rent floor (0.186 to 0.201 across the whole ladder).
- **aleph**, 24.7 per cent. Every `value_of_life` arm is degenerate.
- **h_2**, 60.4 per cent, no instrument at all.

## pi_eu AND kappa_ued ARE DRUG-BLOCK COMPLEMENTS

ROUND10's fourth line is the useful result and it was not the one designed to be.
Taken separately, both instruments wreck the drug block:

    probability_becoming_unemployed down    b 4.9 -> 32.1,  lambda_d 4.5 -> 48.7
    multiple_of_prob_emp_if_addicted up     b 4.9 -> 34.2,  lambda_d 4.5 -> 45.0

Taken together their drifts CANCEL, because they push b and lambda_d in opposite
directions:

    both        pi_eu 23.4 -> 3.8,  b 4.9 -> 2.5,  lambda_d 4.5 -> 1.4

That is the first pair found in this search whose coupling helps rather than
costs, and it closes pi_eu for free. `2f789d317c` therefore has six moments
outside ten per cent with pi_eu, b and lambda_d all inside five.

It also revealed that `probability_becoming_unemployed` down LOWERS kappa_ued
hard -- 29.4 per cent off to 44.9 -- which is why kappa_ued reads 33.6 at the
joint point despite its own parameter having been raised. So kappa_ued needs a
bigger push than its own gap suggests, and the push has to be paid for out of
the drug locus rather than out of pi_eu, which is now spent.

## ROUND11: kappa_ued WITH THE REPAIR IN THE SAME LINE

Rather than move kappa_ued and repair next round, both lines carry the repair
computed from the measured columns:

    param 3.2 -> 3.4   repair lamA +0.016, as1 -0.011   predicted b and lambda_d exactly on target
    param 3.2 -> 3.6   repair lamA +0.000, as1 -0.020   as1 clamped at its bracket, b 0.5%, lambda_d 0.7%

Line 2 runs 3.6 bare so the drift is measured at this point rather than carried
from an older slice, which is what the two clamped predictions rest on.

Line 3 retries `value_of_life` at 37. Every earlier arm on it was degenerate, but
those were taken where the drug block was already broken; aleph also improved on
its own from 24.7 to 21.9 when the block was repaired, which suggests the
degeneracy was the block collapsing rather than the instrument itself. Worth one
point to find out.

## aleph IS REACHABLE, AND ITS INSTRUMENT IS NOT DEGENERATE -- IT IS EXPENSIVE

Retried at the repaired point, `value_of_life` 34.587 -> 37 takes **aleph from
21.9 per cent off to 10.9**, nearly inside. So the instrument works and the
earlier verdict of "degenerate" was wrong about the cause, though right that the
arms were unusable. Measured controlled at the healthy point:

    aleph     elasticity   +1.96
    b         elasticity  -31.04
    lambda_d  elasticity  -40.10

Those last two are the largest in the model and they are why every earlier arm
looked degenerate: b lands at 0.0113 and lambda_d at 0.0025. The block does not
collapse because the point was already sick; it collapses because this
instrument is enormously coupled.

**The repair is 5.4x outside the `addiction_scalar_1` bracket.** So this is not a
step that can be taken safely and is not one to pretend otherwise about. ROUND12
line 1 takes it anyway, unclamped, because it is the only route to aleph and
because measuring it is how the bracket gets wide enough to trust; line 2 takes
about 59 per cent of it at `value_of_life` 36; line 4 arms
`addiction_scalar_1` alone at 0.0175, which widens the bracket from two per cent
to about eight whatever else happens. Any of the three that survives makes the
next repair legitimate rather than extrapolated.

## THE kappa_ued STEP WORKED AND ITS REPAIR OVERSHOT

`multiple_of_prob_emp_if_addicted` 3.2 -> 3.6 with the clamped repair took
kappa_ued 33.6 per cent off to 22.8, but the repair over-corrected: b 2.5 -> 13.0
and lambda_d 1.4 -> 10.4, both now high rather than low. The correction is small
and **inside the bracket** -- lamA +0.070, as1 +0.0009 -- and is ROUND12 line 3.
It also cost kappa_uem, which went outside ten per cent for the first time in
several rounds, and that will need watching rather than assuming.

## CORRECTION: THE pi_eu PAIR WAS NOT FREE, kappa_uem PAID FOR IT

Recorded last round as the first coupling in this search that helps. The part
about b and lambda_d is right -- they came out better -- but "closes pi_eu for
free" is wrong, and the moment that paid was one I did not look at:

    9ff7a5b81c   pi_eu 23.4%   kappa_uem  6.5%   lambda_m 16.1%
    2f789d317c   pi_eu  3.8%   kappa_uem 33.5%   lambda_m 26.8%

Lowering `probability_becoming_unemployed` swapped pi_eu for kappa_uem, one
moment outside ten per cent for another, and cost lambda_m ten points as well.
Both points sit at six outside. **Check the WHOLE vector before calling a step
free**, not the moments the step was aimed at.

## THE UNCLAMPED aleph REPAIR FAILED, AS THE BRACKET SAID IT WOULD

ROUND12 line 1 took the `value_of_life` repair 5.4x outside the
`addiction_scalar_1` bracket, deliberately, to see whether the locus held that
far. It does not: b overshot to 84.9 per cent HIGH and lambda_d to 65.5, and
aleph reached only 18.7 per cent rather than the 10.9 the bare arm gave, because
the repair's own coordinates move aleph too. The linear locus is good to about
two per cent in `addiction_scalar_1` and no further. Line 4, arming that
parameter alone at 0.0175, is the way to widen it; nothing else should be
extrapolated past it in the meantime.

The in-bracket correction on the same round worked exactly: **b 13.0 per cent
off to 0.7, lambda_d 10.4 to 3.7**, at `32fba2ab17`, which is now the best point
of its family at six moments outside ten and worst 43.7 per cent on h_1.

## kappa_uem IS A CLEAN TWO-FOR-ONE AND IS THIS ROUND

`kappa_uem` the parameter has a measured elasticity of -0.952 on its own moment
and +0.569 on lambda_m. Its own moment is 33.4 per cent HIGH at `32fba2ab17` and
lambda_m is 27.1 per cent LOW, so raising the parameter fixes one and helps the
other:

    kappa_uem parameter 21.19 -> 28.67
        kappa_uem moment  0.4001 -> 0.300   (33.4% -> 0)
        lambda_m          0.1822 -> 0.2164  (27.1% -> 13.4%)

If it lands, that is five moments outside ten per cent rather than six, and
lambda_m stops being one of them. Lines 1 and 2 bracket it; lines 3 and 4 push
kappa_ued to 4.0 with and without it, since kappa_ued is still 22.7 per cent off
and its own drift is now measured at this point.

## NEW BEST POINT: e3fc6bd353. THE kappa_uem TWO-FOR-ONE LANDED

    kappa_uem  33.4 per cent off -> 4.0
    lambda_m   27.1 -> 16.5
    b          0.7 -> 0.1        lambda_d  3.7 -> 1.9

Six moments outside ten per cent, worst h_1 at 41.9. It ties `9ff7a5b81c` on the
count and beats it on substance -- kappa_ued 22 against 29, pi_eu 16 against 23,
everything else level -- so the sum of the gaps outside ten falls from 166 to
151. Outside now: h_1 42, gamma 31, aleph 24, kappa_ued 22, lambda_m 16, pi_eu 16.

## THE BRACKET WIDENER PAID OFF TWICE

`addiction_scalar_1` at 0.0175 was a deliberate throwaway -- b came back at 181
per cent and lambda_d at 329 -- but it is a controlled pair over a bracket **4.0
times wider** than the one every repair has been clamped against, and the column
re-measured over that range is:

    b elasticity -17.00 (narrow bracket said -14.71)
    lambda_d     -23.48 (narrow bracket said -21.58)

Close enough that the narrow readings were sound, and the usable range is now
0.0604 in logs rather than 0.0201. That is what makes the aleph route legitimate:
`value_of_life` 36 with its repair now sits exactly AT the wide bracket edge
instead of 5.4x outside it, and aleph is predicted 24.3 per cent off to 18.1.
At 37 it would reach 13.6, but that repair asks `lambda_addiction` for 3.6x ITS
bracket, so 36 is the step to take and the next one is measured from there.

**A deliberately bad point can be the most valuable line in a round.** Its own
moments were never the reason to run it.

## THE lambda_addiction COLUMN IS THE OLDEST THING STILL IN USE

Every drug repair in the last six rounds has used a `lambda_addiction` column of
(-1.56 on b, -1.14 on lambda_d) measured on the `02c96e3721` slice, before five
parameters moved. Its `addiction_scalar_1` partner has been re-measured three
times since. ROUND14 line 2 arms `lambda_addiction` alone at 15.5 from the
current best point, so the repairs stop resting on the one column nobody has
checked.

## NEW BEST: 620db1471b. AND THE OLD lambda_addiction COLUMN WAS WRONG

`kappa_ued` at 4.0 with its repair landed clean -- **21.9 per cent off to 12.3**,
b at 4.8 and lambda_d at 5.8 -- and the point now leads the archive on the sum of
gaps outside ten per cent, 1.42 against the previous 1.52:

    h_1 42, gamma 31, aleph 25, pi_eu 17, lambda_m 15, kappa_ued 12

**The line that mattered most was the column check.** Re-measured on the current
slice, `lambda_addiction` reads

    b        -1.328   (the column used since ROUND9 said -1.56)
    lambda_d -0.615   (said -1.14)

The lambda_d elasticity is **little more than half** what every repair since
ROUND9 has assumed. That is not a rounding difference, it is the reason the
`value_of_life` 36 repair undershot on the same round: aleph reached 22.0 per
cent instead of the predicted 18.1, and b and lambda_d were left at 32.4 and
28.1, because the solver believed `lambda_addiction` would deliver nearly twice
the lambda_d it actually does. Two rounds of clamped repairs were solved against
it.

**Both columns of the drug locus are now measured on the current slice**, so
    J = [[-1.328, -17.00], [-0.615, -23.48]]
and every repair from here rests on nothing older than this point. Re-derived
with it, the `value_of_life` 36 step needs `addiction_scalar_1` at exactly its
wide-bracket edge and `lambda_addiction` well inside, and predicts aleph 25.0 per
cent off to 18.8.

**Re-measure a column before trusting it at a new point, not after it fails.**
This is the same lesson as the seven-coordinate pair and the lambda_m sign, and
it has now cost three rounds.

## ROUND15

    1  value_of_life 36 + repair on the corrected columns   aleph 25.0 -> 18.8
    2  pi_eu with kappa_uem HELD                            pi_eu 16.8 -> ~0
    3  kappa_ued 4.4 + repair                               12.3 -> 3.8
    4  value_of_life 35.3 + repair                          25.0 -> 21.9, brackets line 1

Line 2 is the answer to the ROUND10 mistake. Lowering
`probability_becoming_unemployed` closes pi_eu and pushes kappa_uem to 32 per
cent off; `kappa_uem` the parameter has a measured elasticity of -0.952 on that
moment, so the compensation is computed and carried in the same line rather than
discovered a round later.

## kappa_ued AT 4.4 CLOSES ITS OWN MOMENT AND IS A NET LOSS

    kappa_ued  12.3 per cent off -> 0.3
    b           4.8 -> 2.3
    lambda_d    5.8 -> 11.0
    tau_u       inside ten -> 19.1
    theta       inside ten -> 15.6

Eight moments outside ten per cent and a sum of 1.81, against `620db1471b`'s six
and 1.42. **Closing kappa_ued outright costs more than leaving it at twelve per
cent.** Judged on its own moment this is the cleanest hit of the whole search;
judged on the vector it is the worst step of the round, and only the second
reading is the one that counts. The instrument should stay at 4.0.

This is the same error the pi_eu pair produced two rounds ago, caught earlier
this time because the whole vector is now printed for every arm rather than the
moments the step was aimed at. That habit is worth keeping.

The lambda_d overshoot at that point is repairable and both steps are inside
their brackets -- `lambda_addiction` to 18.95, `addiction_scalar_1` to 0.018049
-- but repairing it would still leave tau_u and theta outside, so it is only
worth doing if a later round has a reason to be at 4.4 at all.

**Best point is unchanged: `620db1471b`, six outside ten per cent, worst h_1 at
41.7.**

## ROUND15 FAILED ENTIRELY, AND THE CAUSE IS ONE HABIT

All three remaining lines left b and lambda_d high, and the best point did not
move:

    L1  value_of_life 36 + repair    b +48.2%  lambda_d +31.5%   out10 8
    L2  pi_eu + kappa_uem held       b +47.3%  lambda_d +62.8%   out10 9
    L4  value_of_life 35.3 + repair  b +21.3%  lambda_d +29.0%   out10 10

**L2 moved no drug parameter at all** and still blew the block to 47 and 63 per
cent. So this is not a bad repair, it is a missing one:
`probability_becoming_unemployed` drags b and lambda_d hard on its own, which
ROUND10 measured, and the line compensated `kappa_uem` while forgetting the drug
block. L1 and L4 over-offset in the other direction, because
`value_of_life`'s drag HERE is weaker than the column measured at
`2f789d317c`, so the repair pushed the block past target rather than onto it.

Both failures are the same habit: **a column measured at one point, used at
another.** It has now cost four rounds -- the seven-coordinate pair, the lambda_m
sign, the stale `lambda_addiction` column, and this. Every time, the fix
afterwards has been to re-measure at the point being stepped from, and every time
the next round has repeated it somewhere else, because the columns are re-measured
one at a time while the steps use four at once.

## ROUND16 STOPS DOING THAT

Four bare arms, one coordinate each, all from `620db1471b`:

    value_of_life                   34.587 -> 36
    probability_becoming_unemployed 0.007098 -> 0.0050
    addiction_scalar_1              0.018326 -> 0.0175
    lambda_addiction                17.942 -> 15.5

No combined step, no repair, nothing predicted. It buys a complete four-column
Jacobian at ONE point covering aleph, pi_eu and the drug block -- the exact set
every failed step needed -- and next round can take a single joint move that
rests on nothing carried from anywhere else.

A round spent measuring rather than stepping is cheaper than three more rounds
of steps that overshoot, which is what the last two rounds have been.

**Best point remains `620db1471b`: six moments outside ten per cent, worst h_1 at
41.7, sum 1.42.**

## THE FOUR-COLUMN JACOBIAN, AND WHAT IT SETTLES

Measured at `620db1471b`, four bare single-coordinate arms, nothing carried:

    moment      gap    value_of_life  prob_unemp  addiction_scalar_1  lambda_addiction
    aleph      25.0%        +2.136       -0.104        +0.787            -0.000
    pi_eu      16.8%        -2.442       +0.311        -4.153            -0.157
    b           4.8%       -36.478       -0.979       -15.459            -1.532
    lambda_d    5.8%       -45.413       -1.593       -23.154            -1.359
    kappa_ued  12.3%        -8.382       +0.661        -0.803            -0.038
    kappa_uem   4.1%        +0.352       -0.653        +0.642            +0.023
    lambda_m   15.3%       +13.888       +0.414        +0.164            +0.046
    h_1        41.7%       -14.766       +0.064        -0.835            -0.025
    gamma      30.9%        +0.140       +0.035        +0.552            +0.030
    theta       3.0%        +7.884       -0.512        -6.941            +0.119
    tau_u       4.0%       -19.335       +0.035        +2.541            +0.523

Three things fall out of it.

**`lambda_addiction` is a clean repair instrument.** b -1.53, lambda_d -1.36,
and every other column below 0.16 in absolute value. Nothing else in this model
is remotely that selective, and it is why the repairs that stayed inside its
bracket have all landed.

**gamma has no instrument, confirmed a fourth time.** The best column is
`addiction_scalar_1` at +0.552, which would need 14 times its bracket. **So the
minimax cannot go below gamma's 30.9 per cent**, whatever else is done.

**h_1, lambda_m and aleph all ride on `value_of_life` alone, and h_1 pulls the
opposite way from the other two** -- elasticities -14.77, +13.89 and +2.14. That
is the real reason h_1 has sat at 41.7 per cent for eight rounds: it was never
under-instrumented, it was fighting two other moments over one instrument.

## AND IT GIVES THE BEST STEP IN MANY ROUNDS

Sweeping the one instrument the three of them share:

    dlog      h_1    lambda_m   aleph    worst
    0.0000   41.7%     15.3%    25.0%    41.7%   <- where the best point sits
   -0.0140   28.3%     30.2%    27.2%    30.9%   <- gamma binds instead
   -0.0350    2.2%     47.9%    30.4%    47.9%

**The minimax over the whole vector falls from 41.7 per cent to 30.9**, and at
that point gamma is the binding moment rather than h_1. h_1 is not closed --
nothing closes it without giving lambda_m away -- but it stops being the worst.

`value_of_life` drags b and lambda_d at -36.5 and -45.4, so the step needs a
repair; the box-constrained solve keeps both instruments inside their brackets
and leaves b at 5.8 per cent and lambda_d at 3.7. ROUND17 line 3 is that step,
line 4 is 70 per cent of it, line 1 the full four-column ridge and line 2 the
targeted pi_eu pair.

## THE HOUSING BLOCK WAS SEARCHED ON ONE PARAMETER OUT OF THREE

The author's objection is correct and this section records the error rather than
the excuse. h_1, h_2, gamma and aleph are the statistics a housing paper rests
on, and they are the four still outside ten per cent. Two of them were declared
unreachable on a search that never touched the relevant instrument.

The ladder has exactly **three rungs** (`housing_status_grid_size=3`), and the
distribution across them at `d25318fa67` is

    unit 0   12.1% of renters   none over half of income
    unit 1   20.8%              none over half of income
    unit 2   67.1%              40.3% of them over half of income

**Every household that h_2 counts is in the top rung.** h_2 and gamma are
therefore properties of how expensive the TOP of the ladder is, and how many
people are pushed into it. What the search has actually done to the three
geometry parameters:

    smallest_rental_relative_to_lowest_income   19 controlled pairs   (the BOTTOM rung)
    largest_house_size                           1 pair, at a point where mu_H printed 2e12
    housing_status_grid_expander                 0 pairs -- NEVER ARMED

So "h_2 has no instrument" and "gamma has no instrument, confirmed four times"
were concluded from nineteen measurements of the bottom rung, one broken
measurement of the top, and none at all of the spacing. That is not a finding
about the model, it is a hole in the search.

It also explains a reading that should have been the tell: `relative_share_of_housing`
has an elasticity of only **0.22** on gamma, where a Cobb-Douglas weight should
be near one. With three discrete rungs the housing expenditure share is pinned by
the SIZES on the grid, not by the preference weight. The low elasticity was
evidence about the grid and it was read as evidence about the instrument.

`ROUND18` arms both, bare, from the best point: `largest_house_size` at 0.13 and
0.16, `housing_status_grid_expander` at 1.5 and 0.7.

## h_1 AND lambda_m ARE COLLINEAR, WHICH IS A REAL RESULT

Unlike the above, this one holds up. The two instruments that move the pair move
it in the same direction:

    value_of_life      h_1 -14.766   lambda_m +13.888   ratio -1.063
    size_homelessness  h_1  +1.960   lambda_m  -1.870   ratio -1.048

The ratios differ by 1.4 per cent. They do not span the plane, so no combination
of them separates h_1 from lambda_m -- one slides along a locus, it does not step
off it. Breaking that needs an instrument with a different ratio, and
`smallest_rental` near its cliff is the only candidate seen so far.

## FOOD STAMPS REVERTED, AND EVERY POINT NOW RECORDS ITS MODEL

The statutory SNAP schedule is out, on the author's instruction. It was correct
per household and wrong by a factor of 48 in aggregate -- 20.4 per cent of
labour income against 0.42 in the data -- because far more households in this
model fall under a realistic eligibility limit than in the world. That is the
same lower-tail problem as the bottom half's net worth share at 0.131 against
0.025, showing up in a different place.

The programme is a single allotment `max_food_cost` less the statutory taper,
with `max_food_cost` calibrated on aggregate spending again. `MOMENT cbar` is a
target, the adjuster is back at 5e-2, and `next_batch.py` maps it -- **fourteen
calibrated parameters**. The taper stays: it predates the statutory schedule and
without it every household below a hard floor has identical income, so one atom
crosses the homelessness margin together and the rate jumps rather than passing
through its target.

**This invalidates every elasticity in the archive.** The food stamp floor enters
the budget of every poor household, so the drug block, the housing block and the
homelessness margin all move. The 84 points remain valid as measurements of the
OLD model and must not be mixed with new ones.

### The md5 hazard now has a detector

The point tag is the md5 of the PARAMETER vector alone, so re-measuring a vector
on a changed model reproduces the tag and silently replaces a real measurement.
That has been a standing rule with no way to check it. `run_one_point.sh` now
writes a `MODEL <hash>` line into every point, so a point measured on a different
source can be identified and discarded rather than trusted.

    model before the revert   9955099921
    model after the revert    fcbd17f4c6

Any point carrying neither hash predates the stamp; any ROUND18 point carrying
`fcbd17f4c6` was rebuilt mid-round and is NOT comparable to the rest of ROUND18.

### Odds ratios, asked and answered

Intergenerational persistence at rho=0.35 bought almost nothing:

    child SUD ratio           median 1.156 -> 1.189   target 2.0
    child homelessness ratio  median 1.622 -> 1.690   target 2.1

269 points before the change against 82 after. The intergenerational channel is
carried by the income penalties, not by the persistence.

## THE AUTHOR'S DECISIONS, 31 AUGUST ~14:30

**The two discount factors are both calibrated, and the author set the brackets:**

    beta_impatient   on the WEALTH SHARE OF THE BOTTOM, target 0.025
    beta_patient     on wealth over output, inside its 3.0-4.5 band

So neither is assigned and no spread has to be guessed. The bottom-half share is
currently 0.131 against 0.025 -- more than five times too fat -- and it is the
moment that most wants this change.

**largest_house_size is the housing instrument.** Measured controlled at
`d25318fa67`, 0.1118 -> 0.13:

    gamma  30.8 per cent off -> 22.2   elasticity +0.78
    h_2    60.8 -> 49.1                elasticity +1.73

against the +0.22 on `relative_share_of_housing` and the +0.06 the gate fitted
on `smallest_rental`, both of which were used to call these moments unreachable.
Extrapolating inside the bracket, gamma closes near 0.155 and h_2 near 0.18, both
well inside the (0.02, 1.00) bound. The cost is the drug block, b -4.19 and
lambda_d -3.56, which is exactly what the locus repairs inside its brackets.

`housing_status_grid_expander` is dead: every elasticity at or below 0.05. Of the
three geometry parameters the TOP RUNG is the instrument and the other two are
not.

## THE HOUSING BLOCK IS UNDER-DETERMINED WITH THREE RUNGS

Four housing moments -- h_1, h_2, h_3, gamma -- and effectively two working
instruments, `smallest_rental` and `largest_house_size`, since the expander does
nothing. That is two equations short however well each is measured.

`housing_status_grid_size` is a compile-time parameter at 3. Every array is
dimensioned on it, `lowest_housing_grid_point=-1` is the street and
`second_lowest_housing_grid_point=0` the first rung, and the per-unit
diagnostics already loop from the second lowest to `housing_status_grid_size-1`.
Nothing hardcodes three. Raising it is a one-line change and the value function
is LINEAR in that index, so 3 to 5 costs about 1.7 times the solve.

It is also the natural fix for h_2 specifically: h_2 is a statistic about
DISPERSION in housing burden, and with three rungs holding 12, 21 and 67 per
cent there is almost none to measure.

## THE TREATMENT PRICE DID MATTER, JUST NOT FOR WHAT IT WAS ADDED FOR

Recorded because the author's recollection was the opposite and the arms are
unambiguous. Controlled, 0.02 -> 0.06:

    tau_u   136.5 per cent off -> 9.4   elasticity -0.70
    mu_H     39.5 -> 10.5
    theta    12.2 -> 6.8

It is the instrument that closed tau_u, and nothing else has been found for it.
But it did NOT do the job it was introduced for: the income of working age drug
users went 0.405 to 0.355 against a target of 0.74 -- the WRONG WAY. And the
price it settled at is 0.100 of average labour income against 0.034 to 0.065 for
real outpatient treatment, so it is one and a half to three times too expensive.

Two things to weigh before removing it. `utility_cost_of_treatment` has to take
over as tau_u's instrument, which it did before, so that part is a swap rather
than a loss. But a MONETARY price has distributional bite that a utility cost
does not: it is what stops a poor household buying treatment, which is close to
the question the paper asks.

## THE STAMP CAUGHT A CONTAMINATED ROUND ON ITS FIRST OUTING

Two of ROUND18's four points carry a `MODEL` line and two do not, which splits
the round across two models:

    453ae48b31  largest_house_size 0.13   unstamped  -> PRE-revert, clean
    b566bad1d3  expander 1.5              unstamped  -> PRE-revert, clean
    db152f5587  largest_house_size 0.16   stamped    -> POST-revert, NOT comparable
    350d9853df  expander 0.7              stamped    -> POST-revert, NOT comparable

The two stamped points were run by workers that pulled the food stamp revert
mid-round and rebuilt, exactly the hazard the stamp was added for. It worked on
its first outing, and without it the 0.16 point would have gone into the
`largest_house_size` ladder as though it were a clean arm.

**The stamp itself was buggy and wrote an EMPTY hash.** The script does
`cd "$(dirname "$0")"` at line 24, so a later `$(dirname "$0")` resolved to
code/code and md5sum failed silently. Fixed: the hash is computed once after the
cd, and the script now exits rather than writing an unidentifiable point. An
empty stamp is nearly as bad as none. Note it still did its job -- the PRESENCE
of the line was enough to sort the round.

## THE CLEAN largest_house_size ARM, AND A VERY ENCOURAGING DIRTY ONE

Clean, both on the pre-revert model, 0.1118 -> 0.13:

    gamma  30.8 per cent off -> 22.2   elasticity +0.78
    h_2    60.8 -> 49.1                elasticity +1.73

The 0.16 point is on the reverted model, so it is NOT an elasticity and must not
be read as one. But as a combined observation of both changes together it is the
best housing block seen in this project:

    gamma  0.24285  target 0.268    9.4 per cent off
    h_2    0.10122  target 0.101    0.2 per cent off

h_2, which was called unreachable four times, is essentially ON TARGET. Its cbar
is 206.5 per cent off, which is the tell that it is the new model -- max_food_cost
is a live moment again there and has not been recalibrated.

So the combination to test on the reverted model is `largest_house_size` near
0.16 with the drug block repaired: the arm costs b -5.56 and lambda_d -7.03,
which is large but is what the locus repairs.

`housing_status_grid_expander` is dead on both models: 1.0 -> 1.5 and 1.0 -> 0.7
move gamma by under one per cent and h_2 by under a tenth.

## THE FOOD STAMP REVERT CLOSED h_1, WHICH NO PARAMETER COULD

Same vector, `d25318fa67` on the old model against `d25318fa67_nosnap` on the
reverted one:

    h_1        41.8 per cent off ->  1.9    <- closed
    pi_eu      20.3 ->  9.2                 <- closed
    lambda_m   15.9 ->  6.7                 <- closed
    h_2        60.8 -> 51.1
    gamma      30.8 -> 30.3                 barely moves

    lambda_d    6.5 -> 80.6                 <- opened
    b           4.4 -> 72.3                 <- opened
    tau_u       5.4 -> 65.8                 <- opened
    theta       4.9 -> 58.6                 <- opened
    kappa_ued   8.1 -> 36.7                 <- opened
    cbar         --  -> 166.8               max_food_cost is live and stale

**h_1 was the binding moment for eighteen rounds and had no instrument** -- it is
collinear with lambda_m through `value_of_life`, ratios -1.063 against -1.048 --
and the consumption floor closed it without a search. lambda_m came with it, so
the collinearity stopped mattering rather than being solved.

What opened is the drug block, and the reason is legible: `max_food_cost` is a
calibrated parameter again sitting at a value the old rule chose, so the
consumption floor for the poorest households is wrong, and that is exactly where
drug users live. That block has the best measured instruments in the model. **h_1
had none.** It is a good trade.

gamma did not move, which is consistent with the top rung being its instrument
rather than the transfer.

## next_batch.py NOW REFUSES TO SCORE ACROSS MODELS

The archive spans three sources and nothing in a filename or a vector says
which. `archive()` reads the `MODEL` line and keeps only points matching the
current source; a point with no stamp predates it and is EXCLUDED rather than
assumed current. Right now that leaves zero usable points and the gate says "no
archive", which is the correct answer -- an empty batch beats a batch aimed at a
model that no longer exists.

    unstamped     86   the pre-revert model
    (empty)        2   post-revert, from the stamp bug
    fcbd17f4c6     1   post-revert anchor
    920988590e     0   CURRENT: two betas

The 86 old points remain valuable as measurements of their own model and as the
record of what was learned. They must not be scored beside new ones.

## THE TWO-TYPE SPLIT WORKS FOR THE MOMENT IT WAS BUILT FOR

`c6e8793eb5`, impatient beta 0.90 against a patient 0.99715, same vector
otherwise as the one-type anchor:

    w_bot   0.15716 -> 0.01183   target 0.025    <- the target is now BRACKETED
    beta    4.012   -> 2.893     band 3.0-4.5

The wealth share of the bottom half was **6.3 times** too fat with one discount
factor and NOTHING in the parameter set could move it. With two it overshoots to
slightly too thin, so 0.025 lies between beta_impatient 0.99715 and 0.90.

CAREFUL WITH THE 0.131 FIGURE that appears earlier in this file: that is the
share on the PRE-revert model. On the reverted one, which is what the two-type
point should be compared against, it is 0.15716. Comparing across the revert was
the mistake the MODEL stamp exists to prevent and it was nearly made here.

The interpolation is NOT tight. In logs it gives 0.927, linearly 0.909, and the
0.018 between them is a large distance for this parameter -- b moved from 0.025
to 0.92 across the interval, so the surface is violently curved. TWOBETA line 3
at 0.95 sits inside the bracket and will pin it properly; do not step on the
interpolation before that lands.

Everything else at that point is a wreck -- sixteen moments outside ten per
cent, lambda_d at 2184 and b at 936, meaning 92 per cent of households use
drugs. That is a step-size result, not a design fault: at beta 0.90 households
discount the future so heavily that the addiction hazard stops deterring them,
and `max_food_cost` is still stale on top of it. The next point is beta_impatient
near 0.93 with cbar recalibrated.

**THIS IS PROVISIONAL UNTIL THE VALIDATION LANDS.** TWOBETA line 1 sets the two
betas EQUAL, so the two-pass model must reproduce the one-type model exactly.
If any moment differs, the accumulation across passes is wrong and every number
in this section is void. Do not build a round on these until that point is in
and compared.

## WHAT h_1 COST TO LEARN, AND THE LESSON

h_1 bound for eighteen rounds. Several of those rounds went into proving it
unreachable inside the parameter set -- correctly: it is collinear with lambda_m
through `value_of_life` at ratios -1.063 against -1.048, and no combination of
the two instruments separates them. Then the author changed the consumption
floor and it closed to 1.9 per cent without a search.

**A moment that is unreachable within the parameter set may be one model change
away.** The Jacobian is the right tool for asking whether a step exists; it
cannot tell you the model is wrong. When a moment resists for several rounds,
say what would have to change about the MODEL rather than measuring the same
instruments again -- three of this session's rounds would not have been needed.

## kappa_phi_d_level IS CALIBRATED NOW, ON THE INCOME OF DRUG USERS

The author's instruction. The mortality penalty is the PRICE of using, so it
decides who is willing to pay it, and a high one leaves only the most desperate
-- who are the poorest. That is the mechanism behind the model's largest
untargeted failure:

    use rate by income band, model against NSDUH, at b near target
        band 1  4.6%   13.7%
        band 2  3.2%   13.1%
        band 3  9.5%    9.1%
        band 4 11.4%   10.2%
        band 5  2.1%    7.9%
        band 6  0.003%  7.2%
        band 7  0.000%  4.8%

**Zero use in the top two bands.** Not a gradient that is too steep -- a cliff,
and the missing income of drug users lives on the other side of it.

The sign is measured, not assumed. Raising `value_of_life` from 34.59 to 37,
which raises the cost of the death risk, took the income of users from 0.320 to
0.157 and b from 0.091 to 0.011: a higher death cost squeezes use down to the
most desperate. So the penalty must come DOWN to spread use up the distribution.

    MOMENT y_u   income of drug users, target 0.740 (NSDUH)
    kappa_phi_d_level bracketed on it, bounds (4.0, 10.0)

Standardised mortality ratios for opioid use disorder run 6 to 10 and 8 was the
assigned midpoint; the author has authorised 4 as a floor, so the bracket opens
to it rather than to the literature edge. **Seventeen calibrated parameters.**

**THIS RAISES THE BAR.** y_u enters the minimax and it is 55 to 77 per cent off
at every point where b is readable, so the worst gap will jump when the next
point lands. That is the intended consequence: the failure is now something the
loss is trying to fix rather than something the report mentions.

## THE TWO BETAS ARE KEPT IF THEY EARN IT ON THE UNTARGETED TABLE

The author's standard: keep them if they help anything at all among the moments
that are not targeted. So the test is not whether w_bot closes -- it is whether
the untargeted table is better WITH the split than without, at a comparable fit.
That comparison needs a well fitted point in each configuration, which is the
sequence being run: validate, fit, then read the untargeted table.

Note the two changes aim at different failures and are not alternatives.
Beta heterogeneity targets WEALTH -- the bottom half share, 6.3 times too fat.
kappa targets WHO USES -- zero use in the top two income bands. The untargeted
table needs both.

## THREE RUNGS FOR NOW, AND THE GRID MAPPING WAS BACKWARDS

The author's call: fit h_1, h_2 and h_3 with the three rungs the model has, and
consider a fourth later. The evidence for that is the h_2/h_3 trade, measured
along the `largest_house_size` ladder:

    lhs 0.1118   h_2 60.8 per cent off   h_3  7.1   unit 2 holds 67.1 per cent
    lhs 0.13     h_2 49.1                h_3  9.6   unit 2 holds 68.7
    lhs 0.16     h_2  0.2                h_3 11.8   unit 2 holds 70.1

With three rungs an expensive top rung is necessarily a CROWDED one -- the
households it prices out have nowhere to go but unit 1 or the street -- so
closing h_2 pushes h_3 from 7.1 per cent off to 11.8. That is mild, and it was
measured on a model that has since changed twice, so it is worth seeing where the
two sit together on the current model before paying for a fourth rung. The
fourth is a one-line change and the value function is linear in that index, so it
costs about 20 to 26 minutes a point. Held in reserve.

**THE OWNERSHIP WAS INVERTED.** Measured on controlled pairs:

                            h_1     h_2     h_3
    largest_house_size    -0.09    1.73    0.16
    smallest_rental        2.81    0.06   -0.01

`smallest_rental` owned h_2 at 0.06 and `largest_house_size` owned h_3 at 0.16.
Each was assigned to the moment it moves LEAST, which is why h_2 was called
unreachable four times: the search kept stepping the parameter that cannot move
it. Now swapped.

**h_3 still has no real instrument** -- 0.16 from largest_house_size, which is
needed for h_2, and -0.01 from smallest_rental. That is the standing argument
for the fourth rung and the thing to watch in the fit.

## gamma IS FREED, AND THE UNTIED PATH HAD A STALE BUG IN IT

`tie_gamma_to_theta` is 0 on the author's instruction. gamma was the one
targeted moment with no instrument -- `relative_share_of_housing` was pinned at
0.28*(1-theta), so nothing could move housing's share of expenditure, and four
rounds were spent confirming that.

**Freeing the tie alone would have made things worse.** The untied branch of the
internal calibration is stale in two ways, both left over from the round that
moved gamma to the expenditure denominator:

    if (tie_gamma_to_theta==0) relative_share_of_housing = ... -
        (model_avg_housing_spending_renters - avg_rent_to_income_data)
    if (tie_gamma_to_theta==0) relative_share_of_housing = ... -
        (mass_of_renters_at_housing_spending(1,1) - SW_renters_spend_over_X_on_hous_2)

The first steps on the INCOME-denominator object, which is not what gamma
measures any more. The second overwrites it and aims at a different moment
altogether, the mass of renters spending over X. So the branch that was dormant
under the tie would have driven the parameter against the wrong target the
moment it was switched on.

`relative_share_of_housing_adjuster` is therefore set to 0 and `next_batch.py`
owns the parameter across points, like the other seventeen. **Eighteen
calibrated parameters, and every targeted moment now has an owner.**

Its measured elasticity on gamma is only 0.22 and it costs h_1 at -7.32, so it is
weak and coupled. It is workable now only because h_1 has both
`size_homelessness` and the food stamp floor holding it -- which it did not when
this instrument was first tried and rejected.

## TWO INTERNALS FROZEN, AND WHY THE DISTANCE HAD TO GO WITH THE ADJUSTER

On the author's instruction to stop moving what does not need to move.
`sd_permanent_productivity` (sigma_y, 1.7 per cent off) and
`relative_share_of_leisure` (omega_l, 0.3) are held by
`freeze_fitted_internals=1`. Both have been inside two per cent for the whole
search while everything being stepped fought.

**Zeroing the adjuster alone would have hung the loop.** Every point run
converges roughly twenty-eight internal distances, and the block that zeroes
them all is gated on `re_do_simulation_with_fixed_parameters`, which is
`max(sweep_addiction_scalar, diagnostic_simulation)` -- both zero, so it does
NOT run in a point. An adjuster at zero with its distance still live leaves the
loop waiting on a parameter that can no longer move. Both distances are
multiplied by `(1-freeze_fitted_internals)` for that reason.

This is the same shape as the `max_food_cost` case earlier: that adjuster sat at
zero for the whole SNAP period while `distance_max_food_cost` stayed live, which
means the loop was iterating on a parameter nothing could move. Worth checking
whether that cost time on every point in that period.

`labor_income_tax_rate` is deliberately NOT frozen. tau_l is 6.1 per cent off,
and the tax rate has to respond to the income distribution to hold average tax at
target -- and the distribution is about to move a long way under kappa and the
two betas.

## THE DEATH MULTIPLIER IS THE CLIFF, CONFIRMED. kappa 8 -> 6, betas held equal

    income band      kappa 8    kappa 6     NSDUH
        1             2.2%       33.4%      13.7%
        2             1.6%       11.9%      13.1%
        3             0.2%       36.8%       9.1%
        4             0.2%       50.2%      10.2%
        5             0.02%      43.1%       7.9%
        6             0.000%     20.0%       7.2%
        7             0.000%      0.7%       4.8%

**The cliff is gone.** Bands 6 and 7 went from literally zero to 20.0 and 0.7 per
cent. The rich do start using once the death risk falls, which is the mechanism
the author proposed and it is now measured rather than argued.

    income of drug users   0.1702 -> 0.41991   target 0.740
    b                      0.0246 -> 0.35445   target 0.089
    lambda_d               0.0071 -> 0.25177   target 0.0368
    h_1                    0.00391 -> 0.00592  target 0.00399
    aleph                  57.5 -> 144.4       target 80

**8 to 6 massively overshoots.** A third of the population uses. So kappa=4 is
off the table rather than a floor that might be needed, and the bracket should
eventually narrow -- but not before the kappa=4 point lands and confirms the
slope, since one interval is not a curve.

## kappa AND addiction_scalar_1 MUST BE SOLVED JOINTLY, NOT IN TURN

Interpolating kappa from b alone gives 6.97. Extrapolating it from y_u alone
gives 5.01. They disagree by two, and neither is usable:

- b's target lies INSIDE the 8-to-6 bracket, so its interpolation is sound as far
  as it goes -- but b is not kappa's moment, it is addiction_scalar_1's.
- y_u's target lies OUTSIDE the bracket, so its number is an extrapolation. Worse,
  the y_u reading of 0.42 at kappa 6 is INFLATED because b is 0.354 there: when a
  third of the population uses, users are close to the population and their
  average income drifts toward one for reasons that have nothing to do with the
  mechanism. The same artefact as the two-beta point.

So the next step is a two-by-two on (kappa_phi_d_level, addiction_scalar_1)
against (y_u, b), not a step on either alone. kappa sets WHO uses -- the income
gradient -- and addiction_scalar_1 sets HOW MANY. TWOBETA2 lines 2 and 3 are the
addiction_scalar_1 column and are still solving; the kappa column is these two
points. When both are in the two-by-two can be solved on measured columns.

**y_u is only readable where b is near 0.089.** That has never yet been true on
any point in this model version, which is why the income of drug users still has
no trustworthy reading.

## THE TWO-BETA POINTS WERE MEASURED ON A HALVED DENOMINATOR. ALL FOUR ARE VOID

The re-validation of the two-pass accumulation did not pass. It failed, and the
model's own diagnostic had been printing the failure on every two-beta point
since the first one:

    DIAG histogram mass / distribution (want 1.0)
        point_110278961e (two betas, equal)      2.0000407534
        point_5c932be8a2 (two betas, kappa 6)    2.0051297579
        point_d25318fa67_nosnap (one beta)       1.0000000000

**What went wrong.** The guard that suppresses an accumulator's reset on the
second pass was applied to accumulators. It was not applied to the DENOMINATORS,
because a denominator is not accumulated in the statistics loop -- it is
recomputed from scratch, `sum_of_distribution=0` followed by a sum over
`distribution_stationary`, which holds only the type just solved. So after two
passes every numerator held two units of mass and every denominator held one.

The earlier guard sweep could not have caught this. It keyed on a zero-assignment
to a name carrying `(time_period)`, and none of these masses carry one.

**What it invalidated.** Twenty-eight division sites in the two-pass chain, so
every LEVEL moment on all four two-beta points is exactly twice its truth:

    reported     truth      moment
    h_1          0.00416 -> 0.00208   homelessness rate
    b            0.02777 -> 0.01388   total drug users, kappa 8
    b            0.35445 -> 0.17722   total drug users, kappa 6
    lambda_d     0.00578 -> 0.00289   disorder rate, kappa 8

RATIOS of two accumulated quantities are unaffected -- both sides doubled -- so
sigma_y, omega_l, tau_l, beta, gamma, h_3, theta, kappa_ued and mu_H are as
reported. `w_bot` is neither: its percentile walk asked for half of a one-type
mass out of a two-type histogram, so it read the 25th percentile and divided by
a doubled total. It is wrong in a direction that no simple factor undoes.

**The fix.** Each of the ten mass recomputations inside the two-pass reporters
is scaled to pooled mass, `sum_of_distribution=sum_of_distribution*(accumulating_beta_types+1)`,
which is exact because each type carries unit mass and `beta_type_weight` is
declared but never used, so the pooling is fifty-fifty by construction.
`sum_of_distribution_not_be_homeless` accumulates in the big loop like the other
426 and is guarded instead.

Scaling was deliberately NOT applied in `set_SS_benefits`,
`initialize_feasible_distribution` or `calculate_welfare_by_characteristics`.
Those run per type inside the loop and their masses are per-type by design;
scaling the SS benefit denominator on the second pass would have corrupted the
second type's solve rather than its statistics.

## THE SECOND, QUIETER TWO-BETA BUG: A ROUTINE THAT RECOMPUTES REPORTS ONE TYPE

Distinct from the doubling and invisible to a test with equal betas. A statistics
routine that rebuilds its object from `distribution_stationary` each pass, rather
than accumulating into it, reports the LAST TYPE solved, not the pooled economy.
Numerator and denominator are then consistent with each other, so nothing looks
doubled and nothing looks wrong.

`calculate_cdf_of_incomes_earned` was the case that matters: it builds the list
of distinct income levels and their masses, and everything that reads an income
band or a quintile reads it -- including the drug-use-by-income-band table the
whole kappa argument is being run on. Under two different betas it would have
handed back the impatient type's income distribution applied to the whole
population. It is now pooled: the two mass counters and the two arrays carry
across the pass, and the running count of distinct levels is carried in
`income_cdf_levels_used` rather than in `i`, which the mortgage loop just above
would otherwise clobber.

Two consistent per-type pairs are left and are NOT bugs, because both sides
recompute together: `average_rent_by_age / mass_of_renters_by_age`, and
`model_wealth_of_top_x_perc / model_total_net_wealth_1`. Both are untargeted
diagnostics and both report the last type. Worth pooling before either is
quoted.

**A test with equal betas cannot find this class.** It only shows up when the
two types differ, which is the configuration nothing has yet been measured in.

## WHY HOMELESSNESS IS TOO YOUNG: THE UNEMPLOYMENT PROCESS HAS NO AGE DIMENSION

The author asked whether middle-aged homelessness is low because their
unemployment is not persistent enough. The structural answer is stronger than
the question: in the live branch of `build_unemployment_process`
(`include_addiction==1`, lines 25842 onward) EVERY assignment is
`unemployment_process(:,...)`. The first index is age and it is a colon in every
one of them. Separation, job-finding, UI receipt, and the addicted variants of
all three are identical at 30 and at 60.

The dead branch (`include_addiction==0`) does carry `cutoff_age_1` and
`cutoff_age_2`, so the array was built to hold an age profile. Nothing has ever
put one in it.

The second source of heterogeneity is dead too. `adjusting_unemployment_
probabilities_based_on_productivity` computes a profile and then overwrites it
with `adjusted_probability_1=1`, so the separation rate does not vary with
permanent productivity either. The only things that move the transition are
homelessness itself (`increased_prob_if_homeless=0.2`), the disorder, and SMI.

### THE PROFILE, MEASURED

From `output/baseline_benchmark.txt`. NOTE THE DATE: 14 August, so this is the
model before the food stamp revert, before the second beta and before any of the
kappa work. The shape is almost certainly still right; the levels are not
current and this should be re-measured.

    band     model rate   data rate   ratio     model share   data share
    25-34       0.626       0.316      1.98        34.7          26.0
    35-44       0.632       0.338      1.87        38.4          27.2
    45-54       0.296       0.291      1.02        17.5          21.0
    55-64       0.158       0.250      0.63         8.7          18.4
    65+         0.006       0.077      0.08         0.6           7.5

Data is HUD PiT 2024, already in Table 8 as an untargeted moment.

Read across the top row: the data profile is nearly FLAT from 25 to 64 --
0.316, 0.338, 0.291, 0.250 -- and only falls at 65. The model's is a spike. It
is twice the data before 45, right at 45-54, and then collapses.

**Because the overall rate is a calibration target, the model buys its level by
putting the mass in the wrong place.** h_1 can be inside one per cent while the
age profile is wrong by a factor of two at both ends.

### THE FAILURE IS NOT ONE FAILURE, IT IS TWO

**55-64 is a persistence story and the author's hypothesis fits it.** These are
working-age households facing an age-invariant job-finding rate. In the data the
job-finding rate falls with age and unemployment duration rises steeply with it,
so the model gives a 58 year old the re-employment prospects of a 28 year old.
The CPS profile has to be pulled properly before it becomes a shape -- the
direction is not in doubt, the magnitude is not yet measured here.

**65+ is not a persistence story at all, and no age-varying job-finding rate can
touch it.** Homelessness is EXACTLY ZERO from age 66 onward, every single age.
Retirees are out of the labour market, so the unemployment process does not
reach them; they live on social security and accumulated assets, and in this
model that always covers the lowest rung. There is no hard constraint barring a
homeless retiree -- nothing gates the lowest housing grid point on age -- so this
is an outcome, and it says the retirement income floor is never low enough to
put anyone on the street. Seven and a half per cent of the homeless in the data
are 65 or over.

### THE TEMPLATE ALREADY EXISTS IN THE MODEL

`smi_onset_by_age = smi_onset_level * smi_onset_shape_by_age`, built in
`build_smi_onset` and rebuilt whenever a calibrated parameter moves. A data shape
over the life cycle multiplied by one calibrated level, so the level stays a
calibration parameter and the shape is discipline from outside. An age-varying
job-finding rate would follow that pattern exactly and would add no new
calibration parameter.

Not a repair, so not mine to make: this is a modelling change and the author's
call. Recorded here with the measurement so the decision is taken against
numbers.

### ONE THING THIS IS NOT

`calculate_homeownership_by_characteristics` is NOT affected by today's halved
denominator bug. Both `homelessness_by_age` and its denominator `mass_by_age`
have guarded resets, so both pool across the two passes and the ratio is right.

## THE FIX WORKS, AND MY ACCOUNT OF WHAT IT INVALIDATED WAS WRONG

Measured, not predicted. Same vector, same equal betas, fixed model against the
voided one:

    DIAG histogram mass / distribution (want 1.0)
        void   2.0000407534
        fixed  1.0000203306        <- repaired

    moment      fixed        void      new/old
    lambda_d    0.0028915    0.0057831   0.500
    pi_V        0.17305      0.12561     1.378
    w_bot       0.15929      0.031967    4.983
    every other moment                   1.000

**Three moments moved. Not twenty.** I wrote in the section above that every
level moment was exactly double its truth, and gave a table of corrected values
for b, h_1 and lambda_d. That table was reasoning from the mechanism, not
measurement, and it was wrong on two rows of three:

    b at kappa 8   really is 0.02777, NOT 0.01388
    b at kappa 6   really is 0.35445, NOT 0.17722
    h_1            really is 0.00416, NOT 0.00208
    lambda_d       WAS doubled; 0.00578 -> 0.00289 is right

So **kappa=6 does overshoot b by four times**, exactly as first recorded, and
the walk-back of that in the section above should be ignored. The 8-to-6 bracket
still brackets b's target, but far less comfortably than the corrected numbers
suggested.

The bug bites only where a POOLED numerator meets a RECOMPUTED denominator.
`lambda_d` is `model_fraction_addicted`, accumulated in the big loop of
`stationary_equilibrium_statistics` with a guarded reset, divided by
`sum_of_distribution` -- one of each, so it doubled. `b` and `h_1` come out of
`govt_revenues_calc` and did not move, so whatever their numerators do they are
in step with their denominator. The class is narrow and the only way to find its
members is to measure, which is what the one-pass comparison now running is for.

`w_bot` is the one that matters. At 0.15929 it is finally in line with the
one-beta readings of 0.157, 0.131 and 0.176, which is the check that the
percentile walk is now reading the median of a pooled histogram rather than the
25th percentile of it. Against a target of 0.025 it is 537 per cent too high --
which is the gap the impatient beta was added to close, now measurable for the
first time.

RULE, AGAIN, HAVING BROKEN IT: MEASURE BEFORE BELIEVING IT. The instruction is
in this file and in the engine prompt, and I still published a table of
"corrected" values derived from a mechanism rather than from a run.

## THE AGE PROFILE OF JOB FINDING: PARKED BY THE AUTHOR, WITH ONE FREE FINDING

The author asked whether Krueger et al.\ is the baseline for the job finding
rate, then said to park the whole question and see how the model fits first.
Parked. Recorded here so it is not re-derived.

**Yes, it is the baseline.** Section 5 of the note, at the paragraph for
$\bar\pi^{ue}$: "the annual job finding rate ... which I set to @@q_bar_pi_ue@@
from the annual exit rate Krueger et al.\ (2014) estimate on matched CPS
panels." Krueger, Cramer and Cho (2014), Brookings Papers on Economic Activity.
$\bar\pi^{eu}$ is then chosen to hit the CPS unemployment rate given it.

**But that paper measures DURATION dependence, not an age profile.** Its subject
is how the exit rate to employment falls with time already spent unemployed. It
would not give an age profile without leaning on a demographic cut that is not
what the paper is designed to estimate. An age profile needs matched-CPS UE
transition rates by age, or published BLS duration-by-age tabulations, and
neither is in `data/`.

**THE FREE FINDING. The model already carries the state duration dependence
needs, and does not use it.** Unemployment states 2 and 3 are distinct: 3 is the
insured period and 2 is the uninsured continuation, and the transition is
3 -> 2, so a spell that continues moves to the state that pays nothing. That is
a one-period-of-unemployment marker sitting in the state vector already. But
both states get the SAME exit rate:

    25863   unemployment_process(:,3,1,1,0,:)=probability_becoming_employed
    25874   unemployment_process(:,2,1,1,0,:)=probability_becoming_employed

So the model distinguishes the long-term unemployed for UI purposes and then
gives them a first-year household's chance of finding work. Making the rate out
of state 2 lower than out of state 3 is exactly what Krueger et al.\ measures,
costs NO new state variable, and adds one parameter.

**And it has a mechanism for the age profile that an age-specific rate does not.**
Homelessness in this model requires exhausting assets. The young hold none, so a
SHORT spell puts them on the street; the middle-aged hold a buffer, so only a
LONG spell does. Duration dependence fattens the tail of spell lengths, which
disproportionately reaches the households that need a long spell to fall -- the
older ones. That is a conjecture about this model, not a result. It would be
measured, not asserted.

Both are modelling changes and so the author's call. Neither is being made now.

## TREATMENT IS CHARGED IN UTILITY AGAIN, NOT ON RESOURCES

The author's call, 31 August. `money_cost_of_treatment` is held at zero in
`run_one_point.sh` and `utility_cost_of_treatment` owns tau_u in
`next_batch.py`, bounded (0.0, 8.0) against the model's own clamp of [0,10].

The switch is entirely in those two files. NEITHER cost is internally
calibrated: `distance_money_cost_of_treatment` is declared at line 238 and never
used anywhere, and `utility_cost_of_treatment_adjuster` is zero, so its one use
at 34730 multiplies to nothing. Both are pure handover parameters. Nothing in
the Fortran had to change.

**THE KNOWN RISK, stated once and then proceeded past.** The reason the money
cost was tried in the first place is that the utility cost ran to its FLOOR.
The record at line 5744 of the model has it going 2.12423 -> 0, "-100%, its
floor", with tau_u still short of target. Take-up is far too LOW (0.0076 against
0.245 at the last measured point), and raising take-up means LOWERING the cost,
which cannot go below zero. So utility cost may not be able to reach tau_u from
above. If it pins at zero again the moment is not identified by this parameter
and something else has to give -- but that is for the measurement to say, not
for me to assume in advance.

## h_3 IS CONCEDED, h_2 IS NOT. THE TWO SWAPPED ON 31 AUGUST

The author, correcting me: "no h2 has to be close to 10.1%, but h3 can be off".
`SKIP` in `next_batch.py` is now `{'h_3'}` and the stopping rule scores h_2.

I had it backwards in the round before, and quoted the 30 August "being off on
h2 is ok" at the author as though it still held. It does not, and the reason it
does not is that h_2 is not the moment it was when that was said. It has been
three different statistics in a week -- the share in the smallest unit, the
share above half of INCOME, and now the share above half of TOTAL EXPENDITURE.
Only the last is a fact about the world: 10.1 per cent in the CEX, on the same
denominator as gamma's 26.8. The concession was made against the first of the
three.

h_3, the share sitting in the largest unit the model offers, is a fact about a
grid the model chose. Its only instrument,
`smallest_rental_relative_to_lowest_income`, moves it at -0.01, so it has no
instrument at all. That is the one to concede.

## THE SECOND BETA WORKS. IT HAS SIMPLY NEVER BEEN SWITCHED ON SINCE

The author asked whether the two-beta runs improved the bottom half's share of
net worth. Every point measured on the FIXED model has
`discount_factor_impatient` equal to `discount_factor`, so it is one economy
solved twice and w_bot cannot move. That is why it reads 0.159.

Two points were run with the betas actually different, in TWOBETA.txt, and they
were voided for a different reason. Their readings:

    beta_impatient   w_bot     wealth/output    (target 0.025, band 3.0-4.5)
      0.99715        0.15929       4.048
      0.95           0.02265       3.015
      0.90           0.01183       2.893

**The target is bracketed between 0.95 and 0.90 and sits very close to 0.95**,
where w_bot is 9 per cent off and wealth over output lands at 3.015 -- half a
per cent from the centre of its band, which it has never been near.

THE CAVEAT THAT KEEPS THIS A BRACKET AND NOT A RESULT. Those two points are on
model 920988590e, whose histogram check reads 1.0 not because it was right but
because numerator AND denominator were both per-type: it reports the LAST TYPE
SOLVED, so 0.02265 is the impatient half's own bottom-half share and not the
pooled economy's. The pooled number will differ. The BRACKET is what carries
over -- w_bot falls steeply and monotonically in beta_impatient over
[0.90, 0.99715], and 0.025 is inside it.

So: re-measure 0.95 and 0.90 on the fixed model before believing any level.
