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
