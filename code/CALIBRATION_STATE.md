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

## LIVE STATE, 1 September 20:15 -- ONE BETA, DEATH PENALTY OWNS y_u

The author's two decisions of the last half hour, and what each settles.

**ONE DISCOUNT FACTOR TYPE.** "Go back having just one." number_of_beta_types is
a runtime value with a handover case, so the model hash does NOT change and every
archived point stays scoreable. run_one_point.sh defaults to 1.

The second type existed for w_bot and the measurement condemned it: closing w_bot
needs an impatient beta near 0.27, and even at the search bound of 0.50 the moment
only reaches 0.053 against a target of 0.025. w_bot is therefore in SKIP -- a
CONSEQUENCE of the instruction, one line to reverse, and flagged as such. Note
also that the 2.5 per cent is the SCF bottom-half share of NET WORTH, mostly home
equity, while include_homeownership is 0 and the only asset here is financial
saving; retargeting it to a financial-wealth concept is a different fix.

**THE DEATH PENALTY OWNS THE INCOME OF USERS.** "Adjust the death penalty to get
the right average income." kappa_phi_d_level -> y_u was already the OWN mapping
and the measurement says it is the right one:

    kappa_phi_d_level    elasticity -0.637. 8 -> 5.64 takes y_u 0.5325 -> 0.6652
                         against 0.7400, closing 64 per cent of the gap in ONE
                         step. Solves near 4.8, inside the authorised (4.0, 10.0).
    discount_factor_imp  elasticity -0.14. Would need beta near 0.09.

Four and a half times the instrument, and in a range the author has already
sanctioned. The mechanism is why: the mortality penalty is the PRICE of using, so
lowering it lets households who are not desperate afford the risk, which is
exactly the composition change y_u measures.

`code/batch_yu.txt` runs kappa_phi_d_level=4.8 at one beta and pairs against
batch_onebeta line 1, the same vector at 8.0, so the value is measured rather
than extrapolated past the pair that produced it.

EXPECT THE DRUG BLOCK TO OPEN WHEN IT LANDS. 8 -> 5.64 took lambda_d from +1 to
+132 per cent and b from +22 to +151. That is the nested loop restore.py exists
for: small step on the coupled instrument, then re-close b and lambda_d on
lambda_addiction and addiction_scalar_1. batch_onebeta lines 2-5 are that 2x2 at
one beta, which is what gives the repair a Jacobian.

### h_2 IS NOT CONCEDED. SKIP IS {h_3, w_bot}.

I put the moment h_2 in SKIP on 1 September on a misreading and the author caught
it. THE NAME MEANS TWO THINGS: the MOMENT h_2 is the CEX severe cost burden
headcount, target 0.101, reading -18.2 per cent and among the closest in the
table; the PARAMETER the author calls h_2 is the cheapest rental rung, which here
is smallest_rental_relative_to_lowest_income. Their instruction was about the
parameter. The same trap exists for h_3: the MOMENT h_3 is the share in the
largest unit, the author's h_3 is the middle rung at twice the cheapest.

The ladder is as the author specified and confirmed in the code: h_1 street,
h_2 = housing_size(0) = 0.055 calibrated on rent50, h_3 = 2*h_2 = 0.110 assigned,
h_4 = 3*h_2 = 0.165 assigned.

### What is still in flight, and what was cancelled

Running: batch_onebeta (5 points, one beta -- the re-solved best point and the
drug 2x2 there), batch_yu (1 point), batch_recal5 (8 points).

CANCELLED: the impatient beta bracket at 0.85/0.75/0.65, and the drug 2x2 at TWO
betas. Both were measuring an economy that no longer exists. batch_recal5 is left
to finish because slopes partly transfer even though levels do not.

### The gate deadlock, fixed

next_batch would not step unless b AND lambda_d were inside five per cent, and the
documented remedy, restore.py, refits its Jacobian from an archive that held ONE
drug pair. Gate shut, repair impossible, nothing emitted -- for a whole day, while
batches were built by hand. next_batch now emits batch_drugfit.txt itself when the
gate is shut and fewer than three drug pairs exist.

## SUPERSEDED, 1 September 18:25


### STOP BUILDING MULTI-PARAMETER ANCHORS. THIS IS THE SECOND FAILURE.

recal1 moved seven parameters at once and broke four moments that were fine.
recal3 moved TWELVE and was worse still: lambda_d +815 per cent from +1.2, b
+363 from +21.9, tau_u to exactly zero, h_share1 to -97.9, and pi_eu to +101 --
in the WRONG DIRECTION, after a step that should have cut the unemployment rate.
Every individual step was inside the 0.35 e-fold cap and inside a measured
bracket. They still did not compose.

The rule the archive now supports: an anchor moves ONE parameter, or at most a
pair shown orthogonal by measurement. Capping each step is not sufficient. I
wrote this down after recal1 and then did it again in recal3, which is why it is
at the top of the file in these words.

### The best points are recal2's, and w_bot binds at nearly all of them

Ranked on the author's minimax over the scored set, the whole current-model
archive is still bad -- best worst-gap 378.6 per cent. But the MEDIAN gap tells
the real story: recal1's points sit at 54 per cent, recal2's at 32 to 42.
4969e74993 is the best on median at 32.5, ca84c51275 next at 33.3, and
ca84c51275 is where lambda_d is +1.2 per cent.

At fourteen of the nineteen points the binding moment is w_bot or h_1.

### w_bot CANNOT REACH ITS TARGET, and the reason is a fixed constant

discount_factor_impatient does move it -- elasticity +1.809 measured across
0.95 -> 0.70, where w_bot goes 0.156 -> 0.0898. My earlier "no instrument" call
was wrong and came from a step too small to leave the flat region.

But extrapolating to the parameter's own lower bound of 0.50 gives w_bot 0.049
against a target of 0.025, still ninety-six per cent out. The instrument works
and cannot get there.

**`beta_type_weight` is the missing instrument and it is a compile-time constant
at 0.5.** Line 2378: `real(8), parameter :: beta_type_weight=0.5d0`. It is the
SHARE of households that are impatient, fixed at half, and it acts on w_bot
through a different channel from the discount factor itself -- how many
households are in the impatient type rather than how impatient that type is.
Raising it puts more of the population in the type that does not accumulate, so
the bottom half's wealth share falls.

OPENING IT IS A SCOPE CHANGE AND THEREFORE THE AUTHOR'S CALL. It is not done and
must not be done without them. It is recorded here because w_bot is the binding
moment at most points in the archive and the ten per cent rule cannot be met
while it stays shut.

## SUPERSEDED, 1 September 17:25 -- recal2 launched

`code/batch_recal2.txt` is the live round. The gate ran and refused to emit:
"GATE CLOSED. Best on max(|b gap|,|lambda_d gap|) is 30cbdc5ac4 at 80.6 per
cent." The drug block is open again and it is my doing -- see below.

### THE RECAL1 ANCHOR OVERSHOT, AND IT IS THE SAME MISTAKE THE RULES ALREADY NAME

Seven parameters moved at once, each inside the 0.35 e-fold cap, and the errors
compounded exactly as the two failed joint points said they would. What it won:

    pi_eu   -0.3%   (was -40.5)   the measured 0.0564 landed on 13.9 exactly
    cbar   +11.6%   (was +146)
    aleph  -19.5%   (was +127)
    mu_H    +2.2%   (was  +34)
    p_m     -9.0%   sigma_y -1.7%

What it broke, three of which were FINE before:

    lambda_d -95.0% (was -18.5)   the drug block, from cutting theta's weight
    b        -64.5% (was -10.8)   same cause
    tau_u    -93.5% (was  +33)    overshot through zero
    lambda_m -63.0% (was  +80)    overshot through zero
    y_u      -41.9% (was  +1.6)
    h_1     +414.6% (was  -85)    relative_share_of_housing, elasticity -9.567
    beta      5.452 (was 4.332)   now OUTSIDE the 3.0-4.5 band

The lesson is not new and that is the point: a multi-parameter step is only safe
where the moments are separable, and theta's weight is not separable from the
drug block. Single arms next time, or pairs that have been shown orthogonal.

### THREE MOMENTS HAVE NO WORKING INSTRUMENT, NOW MEASURED AT THIS MODEL

Not argued -- these are matched pairs off one anchor, one parameter each.

**w_bot.** discount_factor_impatient 0.95 -> 0.90 moved w_bot from 0.10505 to
0.10520. Elasticity -0.033. It is the owner in OWN and it does nothing. w_bot is
320 per cent out and there is nothing pointed at it that moves it.

**emp_homeless.** increased_prob_if_homeless 0.2 -> 1.0, a fivefold rise, moved
the employed share of the homeless from 0.97661 to 0.98470 -- elasticity +0.01,
and in the WRONG DIRECTION. This confirms at the current model what the lone
x=3.8 point suggested on the old one. The parameter changes what happens AFTER a
household is homeless; the composition is decided in the housing choice.

**rent50.** smallest_rental 0.12 -> 0.085 gives elasticity +0.57, so closing a
283 per cent gap needs the cheapest rental at 0.0113 -- a NINETY per cent cut,
six times the 0.35 e-fold cap. And that runs directly against D3, where the
author asked for the cheapest unit to be pushed UP until the unemployed are
priced out. Both cannot be had from one parameter. THIS IS A QUESTION FOR THE
AUTHOR, not something to resolve by choosing one and not saying.

### What recal2 does

Anchor: nine steps, every one either inside a measured bracket or capped at 0.35
e-folds, with the drug block repaired first -- relative_share_of_addiction_1 back
to 0.463, which sits inside the 0.42/0.5057 bracket that produced theta -50 and
theta +87.

Arms: the gamma/h_1 tension measured here rather than borrowed; a DELIBERATELY
large step on discount_factor_impatient (0.75) and on increased_prob_if_homeless
(5.0) to settle whether those two moments have any instrument at all; rent50
extended to 0.055; the endowment bracketed at 2.30 because h_share1 needs 2.00;
a second drug-block bracket point; and kappa_phi_d_level for y_u.

## SUPERSEDED, 1 September 16:50 -- the archive was empty against 7de893e588

SEED, DO NOT RUN THE GATE. `code/batch_recal1.txt`, eight points, all launched
16:47-16:49. Line 1 is the new anchor; lines 2-8 are one arm each off it.

### The four decisions the author made this afternoon, and what each did

**D1. omega_l is calibrated again.** "omega_ell should target the 0.4 as
before." `freeze_fitted_internals` is split into
`freeze_sd_permanent_productivity` (still 1) and
`freeze_relative_share_of_leisure` (now 0). The freeze was applied when BOTH
internals were fitted; sigma_y rode every change since and still reads -1.7 per
cent, omega_l drifted to -55 and was frozen at a value fitting a model that no
longer exists. A frozen parameter whose moment has drifted is worse than a held
one, because the moment is still scored.

**D2. h_2 is in SKIP.** "h_2 should essentially be chosen to match the rent50
target (that is the same as the smallest rental relative to lowest income)."
One cost burden read two ways, one parameter setting both. It was never
orphaned in the sense reported -- it never needed its own instrument. THE
TRIGGER PROMPTS SAID THE OPPOSITE and both were corrected at 16:52.

**D3. emp_homeless is scored again.** "you'll need to adjust both to match the
data" -- rent50 and gamma stay on their own targets while the affordability
channel is pushed, rather than drifting as its price.

**D4. NO CHANGE. The top of the asset grid is fine.** "as long as less than 0.1%
of households are at the top grid point, it is ok." The model already prints it:
`DIAG mass ON the top savings grid point` reads 0.0036 to 0.0072 per cent at
every point measured, on BOTH grids. The prepared change to
max_times_labour_income_saved was dropped. The 2.47 per cent figure in the older
notes predates the fix to the grid endpoint and is not true of this model.

### Two things the six-point endowment sweep settled

**The endowment works, but as a CLIFF.** h_share1 reads 0.894, 0.886, 0.884,
0.866, 0.884 across scale 0 to 0.75 and then 0.402 at 1.00; age 26 homelessness
is 14.9 per cent at zero and EXACTLY zero at 1.00. Do not interpolate across it.
The anchor sits past it at 1.25 and the arm is 1.60.

**The drug block closed itself.** b -10.8 per cent and lambda_d -18.5 at scale
1.00, against -80 and -96 on the old grid, with y_u at +1.6. Nothing was aimed at
them; recurving the asset grid did it. The planned drug-block re-solve may not be
needed -- CHECK before spending a round on it.

Also measured: the endowment does not touch rent50 (0.6338 to 0.6395) or gamma
(0.4370 to 0.4338), so their instruments can work without fighting it.

### The one structural doubt to put to the author

gamma is 115 per cent out and its instrument is weak and coupled: elasticity
0.22 on gamma, -9.567 on h_1. Closing gamma on relative_share_of_housing alone
needs a 97 per cent cut, which would destroy h_1. The anchor cuts it 20 per cent,
which is what h_1 needs and does almost nothing for gamma. If the arms confirm
this, gamma does not close on this instrument at any step h_1 survives, and that
is a scope question rather than a search failure.

## SUPERSEDED, 1 September 16:20 -- the archive was empty against 8ced112a69 too

MODEL 8ced112a69. Points on that hash: **ZERO**. The gate is NOT to be run this
firing or any firing until a seed lands -- `next_batch.py` scores only points on
the current hash, so with nothing to interpolate from any batch it wrote would be
a guess dressed as a step. Seed first. That rule is in the trigger prompt and it
applies now.

Four changes, all the author's, made within an hour of each other:

1. **The newborn endowment is a first-period transfer, not an initial asset
   holding.** Newborns start at zero assets and receive `newborn_endowment_scale`
   times average labour income as cash in hand at age 26, carried as
   `newborn_age_transfer` and added at the nine sites that already add a transfer
   to resources, outside the productivity scaling because it is flat. Why it had
   to change: endowing the distribution placed every newborn ON an asset grid
   point, and the snap takes the smallest point STRICTLY above the target, so the
   instrument was a four-step staircase that could not be bisected and a scale of
   zero delivered 0.0840 rather than nothing.

2. **`newborn_endowment_scale` is a calibrated parameter and owns `h_share1`.**
   That is the moment which has held this calibration open longest -- 0.91
   against 0.26, moved at most two points by any of four instruments through four
   channels. It does not duplicate `size_homelessness`: that one sets the LEVEL
   and answers to `h_1`, this one sets the SHAPE.

3. **The residual bequest goes to the government.** `model_total_inheritance`
   accumulates the newborn transfer and the government collects `model_bequests -
   value_of_initial_assets - model_total_inheritance`, with the second term now
   zero. The lump sum that used to be spread over all sixty ages is gone and its
   fixed point with it, at both sites that iterated it.

4. **`financial_grid_expander_positive` is settable, default 3.0.** Five grid
   rungs below a year's rent instead of one. This is not only about the
   instrument: it is the grid every household's SAVING decision is made on, and
   one rung between zero wealth and a year's rent is an artifact sitting exactly
   on the margin the model measures. The cost is at the top, where the last gap
   widens from 0.611 to 1.184 and mass had already been found piling against the
   edge -- so read wealth over output and the wealth share of the bottom half
   carefully on the first points back, rather than assuming they held.

### The seed round in flight

`code/batch_transfer.txt`, six points, scale 0 / 0.15 / 0.30 / 0.50 / 0.75 /
1.00, delivering 0 to 0.6372 in cash at age 26, which is zero to 5.31 years of
rent on the cheapest unit. Scale 0.15 delivers 0.0956, within a rounding error of
the 0.0960 the SCF distribution was handing newborns on average, so it is the
no-change point. All six carry expander 3.0 and share one model hash.

Two more workers are still running `code/batch_endowment.txt` lines 5 and 6,
bracketing `pi_eu` at 0.05 and 0.09 because the anchor's 0.01546 was calibrated
to the retired 4.85 per cent target and the new one is 13.9. **Those two are on
the OLD model hash** and are kept only as a rough read on the pi_eu-to-
unemployment mapping, which is about the employment transition chain rather than
the asset grid. They are not admissible as an anchor and must not be scored.

The four endowment-sweep workers on the old snapped mechanism were stopped: they
answered a question that no longer exists.

### THE FIRST POINT BACK CONTRADICTS MY DIAGNOSIS, AND IT IS NOT A SMALL MISS

`point_2dfee07d2e`, pi_eu=0.09, MODEL a693849dcb. Against the anchor
`point_2af18641a4`:

| band | anchor | pi_eu=0.09 | observed |
|---|---|---|---|
| 1 | 0.9093 | **0.4726** | 0.260 |
| 2 | 0.0262 | 0.2459 | 0.272 |
| 3 | 0.0115 | 0.0804 | 0.210 |
| 4 | 0.0230 | 0.1158 | 0.184 |
| 5 | 0.0300 | 0.0853 | 0.075 |

`h_share1` moved FORTY-FOUR POINTS. Four instruments through four channels had
moved it by at most two. Bands 2 and 5 land almost exactly on the data. That is
the moment this calibration has been blocked on all week, and something just
moved it most of the way.

**BUT THE ATTRIBUTION IS NOT MADE, AND MUST NOT BE CLAIMED.** These two points
differ in TWO things, not one: pi_eu went 0.01546 to 0.09, AND the endowment
mechanism changed from the SCF distribution, mean 0.0960, to a uniform snapped
0.6721. By the liquidity hypothesis the second alone would move band 1 hard. So
this point does not establish that unemployment is the cause; it establishes that
ONE of the two is, and that the age profile is reachable at all, which was in
doubt.

The two clean reads are already in flight:
- `pi_eu` at 0.05 versus 0.09, same model, same endowment -- isolates pi_eu;
- the six-point transfer sweep on the new model at fixed pi_eu -- isolates the
  endowment.

What is NOT supported by this point: that more unemployment makes the homeless
less employed. The employed share of the homeless went 0.9077 to 0.9223 -- the
wrong way, and by almost nothing -- while the unemployment rate went 0.0833 to
0.1813. `increased_prob_if_homeless` owns that moment and nothing else does.

What this point costs elsewhere: `h_1` fell 0.00346 to 0.00124 against a target
of 0.00399, so the LEVEL of homelessness is now less than a third of the data,
and `w_bot` went 0.0297 to 0.1083 against 0.025. Both are scored. The level has
an owner in `size_homelessness`; w_bot is the top-of-grid problem below.

### THE TOP OF THE ASSET GRID HAS TO REPRESENT MORE WEALTH

The author, on being told that concentrating the grid at the bottom spreads it
at the top: "if there are too many people at the top grid point, you have to
make the top grid point represent more wealth."

That is `max_times_labour_income_saved`, 3.2 times the top labour income, and it
is the diagnosis the code itself already reached once: "a truncated top
understates total wealth, and every share read off that total is inflated --
which is most of why the bottom half appeared to hold 16.9 per cent of net worth
against 2.52 in the data." `w_bot` reads 0.1083 against 0.025 at the point above,
which is that symptom exactly.

It is only used in the grid endpoint and in printouts, no parameter expressions,
so it can be made settable exactly as the expander was. **HELD until the six seed
points land**, because they are all on hash 8ced112a69 and changing the source
now would leave the seed round unable to anchor the next gate run. It is a
prepared change, not a pending decision.

### What to do when the seed lands

Compare the six by `h_share1` and by `h_1`. The prediction on record, so it can
be scored rather than reconstructed later: age 27 holds 0.2287 and is homeless at
1.13 per cent where age 26 holds 0.0960 and is homeless at 13.35 per cent, on
HIGHER income, so a transfer near 0.23 -- scale 0.36 -- is where the age profile
should break if liquidity is really what separates the two ages. **If h_share1
does not move over a sweep that takes newborn cash from zero to five years of
rent, liquidity is not the mechanism and the diagnosis has to be rebuilt from
scratch.** That is the point of including scale 0 and scale 1.00 in the same
round.

## Where it stood, 30 August 12:20 (BEFORE the changes above)

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
is scaled to pooled mass, `sum_of_distribution=sum_of_distribution*(accumulating_beta_types+1)`.

**CORRECTED 1 September, on a measurement.** This paragraph used to say the
scaling "is exact because each type carries unit mass and `beta_type_weight` is
declared but never used, so the pooling is fifty-fifty by construction". That is
true of the INITIAL mass and false of the pooled statistics, and it sits where it
reads as describing the latter. A worker measuring `point_76be6ca8af` reported
the masses directly:

```
mass by beta type:  patient 50.243405   impatient 33.263490   ratio 1.510467
pooled mass 83.506895               one-type equivalent 50.243405
```

Both types do start at unit mass -- the age 26 row reads 2.000000 for the pair --
so the divergence is accumulated differential mortality, not a weighting fault:
the impatient type carries far more of the disorder and `kappa_phi_d_level` is
8.0. The `*(accumulating_beta_types+1)` scaling is therefore NOT exact, which is
precisely why `pooled_mass_all` and `mass_by_beta_type` were introduced later in
the session and why the two histogram invariants moved from 1.19 to exactly 1.0
once they were. The sentence is corrected rather than deleted so the reasoning
that was wrong stays visible.
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

## THE TWO-PASS PATH FAILS ITS OWN EQUAL-BETA TEST. ONE BETA IS THE LIVE MODEL

`code/VALIDATION_RESULT.md`. Same 28-parameter vector, both discount factors
equal, `number_of_beta_types` 2 against 1. With the betas equal the two-type
population is two identical copies of the one-type population, so every moment
must reproduce to machine precision. **23 of 46 MOMENT fields do not.**

    moment      two-pass    one-pass   one/two    target
    tau_l        0.1181      0.2376     2.012      0.224
    pi_eu        0.0270      0.0530     1.963      0.0485
    lambda_d     0.00289     0.00715    2.472      0.0368
    aleph        162.0       57.5       0.355      80
    kappa_ued    0.4294      0.1028     0.239      0.1625
    tau_u        0.00758     0.0838    11.062      0.245
    y_u          0.3359      0.1702     0.507      0.740
    w_bot        0.15929     0.15716    0.987      0.025

**READ THE ONE-PASS COLUMN AGAINST THE TARGETS.** tau_l is 6 per cent off at one
type and 47 at two. pi_eu is 9 against 44. aleph is 28 against 103. kappa_ued is
37 against 164. The one-type economy is not slightly better, it is a different
and far better fitted model, and every round spent on the two-pass path was
spent on numbers that were not measuring the model.

**WHY IT PROPAGATES.** tau_l and pi_eu are INTERNAL ADJUSTER targets. About
twenty-eight distances converge inside every point run. Feed an adjuster a
statistic that is out by a factor of two and it drives its parameter to the
wrong place, and then the tax rate and the separation rate are genuinely
different and every other moment moves with them. That is why the disagreement
is not confined to a clean family of doublings: tau_u differs by ELEVEN times,
which no accumulator error produces directly.

**WHAT IS NOT WRONG.** `w_bot` agrees to 1.3 per cent between the two runs, so
today's pooled-denominator fix is right and the wealth histogram is being read
correctly. The three `want 1.0` checks pass in both.

**WHAT THE STATIC AUDIT FINDS AND DOES NOT.** Every simple normalisation
`X = X / Y` in the two-pass chain now has matching guard status on both sides:
zero mismatches across 410 pooled names. What it does find is the top-x-per-cent
searches -- `pop_of_top_wealth_x_perc` and `pop_of_top_income_x_perc` are
per-type counts divided by a pooled `sum_of_distribution`, at six sites, and
those feed `distance_` variables that are convergence criteria, so the cutoff
search itself converges to the wrong percentile. Real, and not enough on its own
to explain tau_l.

### number_of_beta_types IS A VECTOR COORDINATE NOW

It was `integer, parameter :: number_of_beta_types=2`, with exactly two uses: the
declaration and the driver's loop bound. Nothing dimensions on it. It is now
`integer :: number_of_beta_types=1` with a handover case, so:

- the one-type economy, which works, is the DEFAULT and needs no source edit;
- the two-type economy is reachable by passing 2, so repair attempts can be
  measured without rebuilding;
- both live on ONE model hash in ONE archive, instead of forking it in two.

`run_one_point.sh` carries `[number_of_beta_types]=1`. Every point tag changes,
because the tag is the md5 of the whole sorted vector and the vector has a new
coordinate. That cost is paid now rather than later, and it is cheap today
because only two points exist on the current hash.

`discount_factor_impatient` still owns `w_bot` in `next_batch.py`, and at one
type it does nothing, so **w_bot has no instrument until the two-pass path is
repaired**. That is the one thing the author asked for that this does not
deliver.

## THE VALIDATION FAILURE WAS THE TEST, NOT THE MODEL. beta DOES NOT STAY EQUAL

I reported the two-pass path as broken. That is not established, and the
evidence I gave for it does not support it.

**`discount_factor` is INTERNALLY CALIBRATED and `discount_factor_impatient` is
NOT.** The patient beta is bisected on wealth over output inside every point
run -- `distance_discount_factor` sits in the calibration loop's while
condition, and the update at line 33905 is
`discount_factor=0.5*(discount_factor_lo+discount_factor_hi)`, gated only on
`re_do_simulation_with_fixed_parameters==1`, which is ZERO in a point run.
`distance_discount_factor_impatient` and `discount_factor_impatient_adjuster`
are both declared and never used anywhere.

So a run that STARTS with the two equal does not KEEP them equal. The patient
one bisects away from 0.99715 while the impatient one sits where the handover
left it. **The two-pass "equal beta" run was a genuine two-type economy**, and a
two-type economy has no obligation to reproduce a one-type one. The 23
disagreeing moments are what two different economies look like, not what a
pooling bug looks like. tau_l's ratio of 2.012 is a coincidence of magnitude.

The pooling may still be wrong. It is now UNTESTED, which is a different and
weaker statement than the one I made.

### freeze_beta_bisection MAKES THE TEST MEAN WHAT IT CLAIMS

`integer, parameter :: freeze_beta_bisection=0`, beside `freeze_fitted_internals`.
At 1 it zeroes `distance_discount_factor` and gates all three sites that write
`discount_factor` in the update block, so beta stays exactly where the vector
puts it. `code/VALIDATE2.txt` is the re-test: two lines, identical but for
`number_of_beta_types=1` and `=2`, to be run with the flag at 1. Because the
type count is a vector coordinate now, the two lines have different tags and
neither collides with anything.

### AND A REAL IDENTIFICATION POINT, SEPARATE FROM THE BUG

Patient beta is calibrated internally on wealth over output; impatient beta is
set externally on w_bot. That is a coherent two-parameter, two-moment
assignment. But the bisection sets the patient beta from a POOLED moment while
only half the population carries it, so pushing pooled wealth over output to
target moves the patient beta about twice as far as it would at one type -- and
the further it goes, the more the two types differ. Ill-conditioned rather than
wrong, and worth knowing before reading a fitted two-type point.

## beta HAS ONE DRIVER NOW, NOT TWO

`discount_factor` is out of `next_batch.py`'s OWN map on the author's
instruction. The model bisects it on wealth over output inside every point run,
so proposing a value externally was a duplicate driver with three costs: the
search spent an arm on a moment that already had an owner, the model silently
overrode the proposal, and the archived VECTOR line then recorded a discount
factor the point did not run at -- which makes the point irreproducible from
its own vector in that coordinate, and quietly poisons any bracket or
elasticity read off the beta column.

Its BOUNDS entry stays, annotated. `run_one_point.sh` still passes
`discount_factor`, because the bisection needs a starting point and a vector
that omitted it would leave the seed riding in on whatever
`calibration_state.dat` happened to hold -- the under-specified-point failure
this file already records for two other parameters.

`discount_factor_impatient` is untouched and still owns `w_bot`. It is NOT
internally calibrated: `distance_discount_factor_impatient` and
`discount_factor_impatient_adjuster` are declared and used nowhere, so the
external assignment is the only thing driving it and there is no duplicate to
remove. The two-parameter, two-moment split the author asked for -- patient
beta on wealth over output, impatient beta on the bottom half's wealth share --
is now exactly what the code does.

Fifteen parameters are searched externally, down from sixteen.

## THE ARCHIVE IS EMPTY ON THE CURRENT MODEL, SO THE GATE IS SEEDED, NOT RUN

Model `d70ad1c545` carries the pooled-denominator fix, the income cdf pooling,
`number_of_beta_types` as a vector coordinate, the utility treatment cost, and
`freeze_beta_bisection`. ZERO points score on it, so `next_batch.py` has nothing
to interpolate from and a batch built off it would be a guess dressed as a step.
The gate was deliberately not run this firing.

`ANCHOR1B.txt` seeds it with three lines, all at `number_of_beta_types=1` --
the configuration that is validated and much better fitted -- taken from the
one-pass vector, with the treatment price at zero and the utility cost
bracketed at 0, 0.05 and 0.5.

Three lines rather than one because the utility cost is the coordinate that just
changed hands and its behaviour on this model is unmeasured. Seeding and
bracketing the new instrument in the same round costs nothing extra: the archive
needs points either way. A BRACKET BEATS AN ELASTICITY, and tau_u is the moment
that forced that rule, its measured elasticity having come out at -0.92, -0.52,
-0.86 and -3.28 at four places on the same instrument.

Expected: take-up rises as the cost falls, so line 1 should give the HIGHEST
tau_u. If tau_u at a utility cost of zero is still below 0.245, the moment is
not reachable from this instrument and that is the finding, recorded rather than
worked around.

## KAPPA COLUMN RE-MEASURED ON THE FIXED DENOMINATOR

The two points of `code/KAPPA_REDO.txt`, solved on model `ab22a2f5ba` -- the
source as it stood immediately after `b87a441`, the commit that scaled the
two-pass masses to pooled mass. Both handed over 28 of 28 parameters and both
closed with `END OF MOMENTS`, so both are measurements of the vector they were
given.

| | line 1 | line 2 |
|---|---|---|
| `kappa_phi_d_level` | 6 | 7.0 |
| tag | `5c932be8a2` | `ed5b9fe138` |
| file | `points/point_5c932be8a2.txt` | `points/point_ed5b9fe138.txt` |
| solve time | 27 min | 25 min |


### Every targeted moment, both points

`target` is shown once where the two points share it; the two that differ are
marked. All twenty-three targeted moments are listed.

| moment | what it is | kappa 6 | kappa 7 | target |
|---|---|---|---|---|
| `sigma_y` | bottom half earnings share | 0.16905002140174125 | 0.16905002140174125 | 0.172 |
| `tau_l` | average labour income tax | 0.11442914447442246 | 0.1167514189782618 | 0.2240000069141388 |
| `omega_l` | labour supply / total hours | 0.40383530014564456 | 0.4033126901715104 | 0.4000000059604645 |
| `beta` | wealth over output | 3.9690743327438036 | 4.013257577919592 | 3.0 |
| `h_2` | above half of spending | 0.08054490001734889 | 0.059898611956434096 | 0.101 |
| `h_3` | share in the largest unit | 0.6744297716959058 | 0.684812806847286 | 0.626723 |
| `gamma` | housing over expenditure | 0.18723776812442583 | 0.1920012250460057 | 0.2680000066757202 |
| `h_1` | homelessness rate | 0.005918915001538732 | 0.0050959584796382825 | 0.0039900001138448715 |
| `b` | total drug users | 0.3544728441695787 | 0.14226821821056154 | 0.08900000154972076 |
| `lambda_d` | disorder rate | 0.1258953181943336 | 0.03421332862142739 | 0.03680000081658363 |
| `theta` | drug spending share | 0.2751468050212041 | 0.19583038526270236 | 0.16200000047683716 |
| `aleph` | value of life / income | 144.44286034226735 | 157.92187936659454 | 80.0 |
| `pi_eu` | unemployment rate | 0.04912738478728769 | 0.03284130204904531 | 0.048500001430511475 |
| `kappa_ued` | unemployment given SUD | 0.1662437548607938 | 0.19184957407612943 | 0.16249999403953552 |
| `kappa_uem` | employment given SMI | 0.27164468610016695 | 0.2935120453239533 | 0.30000001192092896 |
| `p_m` | SMI population share | 0.050247230956804015 | 0.04572837424734653 | 0.050716882618654986 (k6) / 0.04892764961416063 (k7) |
| `lambda_m` | SMI share of the homeless | 0.16848968637103492 | 0.18286001093074977 | 0.25 |
| `pi_V` | eligibles with a voucher | 0.163555741937361 | 0.1738935087488769 | 0.26600000262260437 |
| `cbar` | food stamps / labour income | 0.02560339832356143 | 0.01875429916397353 | 0.00419999985024333 |
| `tau_u` | treatment take up | 0.20793996433365705 | 0.2274431835124974 | 0.24500000476837158 |
| `mu_H` | recovery housed / homeless | 1.5582118318046048 | 1.6651877503782861 | 1.4732142857142856 |
| `w_bot` | net worth share, bottom half | 0.1508205427270792 | 0.15739998644348707 | 0.025 |
| `y_u` | income of drug users | 0.8398040361534324 | 0.6772915062602598 | 0.74 |

### The three `want 1.0` diagnostics

| DIAG | kappa 6 | kappa 7 |
|---|---|---|
| income histogram mass / distribution | 1.0025696551268057 | 1.0001326204170609 |
| histogram mass / distribution | 1.0025696551268173 | 1.0001326204170731 |
| histogram wealth / total wealth | 1.0000000000001539 | 1.0000000000001930 |

**They read 1.0 and no longer read 2.0.** The kappa 6 vector had been measured
before under the same tag and is kept alongside as
`point_5c932be8a2_void_halved_denominator.txt`, so the two are directly
comparable: the first two ratios were `2.0051297578649980` and
`2.0051297578650247` and are now `1.0025696551268057` and
`1.0025696551268173`, which is half, to the precision a re-solve preserves.

Two qualifications, neither of which is the doubling.

The first two ratios land on 1.0026 at kappa 6 and 1.0001 at kappa 7, not on
1.0 to machine precision the way an untouched one-pass point does (those sit at
1.0000000000001). That residual is pre-existing histogram slack, not a remnant
of the halved denominator: it was carried doubled in the void file, and halving
2.0051 gives 1.0026 exactly. It scales with the size of the drug-using
population and is worth a look on its own, but it is a different question.

The third ratio never read 2.0. Numerator and denominator both doubled, so it
read 1.0000000000001372 before the fix and 1.0000000000001539 after. Only two
of the three were ever evidence of the bug.

### The correction table above does not match what was measured

The section "What it invalidated" predicts every LEVEL moment is exactly twice
its truth and lists `b` at kappa 6 going 0.35445 -> 0.17722. That is not what
happened. At the same vector, before and after the fix:

| moment | void file | re-measured | predicted |
|---|---|---|---|
| `h_1` | 0.0059186761757833 | 0.0059189150015387 | 0.00296 |
| `b` | 0.35445396446262112 | 0.35447284416957869 | 0.17722 |
| `lambda_d` | 0.25177165162774140 | 0.12589531819433361 | -- |
| `w_bot` | 0.031401427868322791 | 0.15082054272707920 | not a simple factor |

`h_1` and `b` are unchanged to five significant figures. Only `lambda_d` halved.
`w_bot` moved by a factor of about five, in the direction the section already
warned was not a simple factor, and now agrees with the one-pass point's 0.157
rather than with its own previous 0.031.

The one-pass point `point_110278961e_onebeta.txt` says the same thing from the
other side: against its voided two-pass counterpart at the same vector, `h_1` is
0.00391 against 0.00416 and `b` is 0.02462 against 0.02777 -- close, not half --
while `lambda_d` moved *up*, 0.00715 against 0.00578.

So the halved denominator reached `lambda_d` and `w_bot` and did not reach `h_1`
or `b`, and the blanket claim that every level moment doubled is wrong. The list
of twenty-eight division sites should be re-read against which moments actually
moved before any of those numbers is quoted.

### What these two points are and are not

They are two-pass, two-type runs. `discount_factor` and
`discount_factor_impatient` were both handed over at 0.99715, but `d092b49`
establishes that the patient one is bisected internally on wealth over output
while the impatient one is not, so the two did not stay equal through the solve.
Neither point is an equal-beta run and neither should be read as one.

They were also overtaken while they solved. `48a8e70` made the beta type count a
vector coordinate defaulting to one and `d092b49` added `freeze_beta_bisection`,
which is inert at its declared 0; the source is now `d70ad1c545`. Both points
carry `MODEL ab22a2f5ba`, so they are identifiable, but the same two lines run
today would take the one-type path and would not reproduce them.

## THE UTILITY COST HAS PLENTY OF ROOM. MY CAVEAT WAS BACKWARDS

`point_d4ffbfdab5`, one beta, utility cost ZERO, model d70ad1c545. All three
`want 1.0` checks read 1.0000000000.

    tau_u = 0.90058 against a target of 0.245

**Take-up OVERSHOOTS by 268 per cent at zero cost.** I warned, when the author
asked to switch back, that the utility cost had run to its floor before and
might not be able to reach tau_u from above. The opposite is true on this model:
at zero cost nine households in ten take treatment, so the cost has to go UP to
bring take-up DOWN, and it has the whole range above zero to do it in. The old
"-100%, its floor" record was about a different model and does not carry.

Lines 2 and 3 of ANCHOR1B (0.05 and 0.5) will place the target inside the
bracket rather than extrapolating to it.

### THE ONE-BETA MODEL AT THIS VECTOR: TEN MOMENTS INSIDE TEN PER CENT

    beta       0.0   theta      0.9   h_1       1.1   pi_V       1.2
    omega_l    0.2   kappa_uem  0.2   sigma_y   1.7   tau_l      6.4
    h_3        6.8   lambda_m   7.0   p_m       8.1

    still out: w_bot 525, tau_u 268, cbar 182, y_u 54, h_2 49,
               lambda_d 43, b 33, gamma 31, aleph 29, kappa_ued 17,
               pi_eu 15, mu_H 13

Compare the two-beta table at the equivalent vector: pi_V was 35 per cent off
and is now 1.2, theta was 32 and is now 0.9, tau_l was 47 and is now 6.4, aleph
was 103 and is now 29. This is a materially better economy and it is the one
that has been validated.

**w_bot is the exception and it is structural, not a fitting failure.** At one
beta it has no instrument at all: `discount_factor_impatient` does nothing when
`number_of_beta_types=1`. 525 per cent is what the moment reads when nothing is
driving it, and it will stay there until the two-pass path is cleared.

## GATE EXIT 2 ON THE NEW MODEL: THE DRUG BLOCK REOPENED, REPAIR EMITTED

`next_batch.py` scored 2 of 103 points, skipping 101 measured on earlier models,
and closed at exit 2: best on max(|b gap|,|lambda_d gap|) is `d4ffbfdab5` at
42.7 per cent against a gate of 5. pi_eu is also out, at +14.9, so `repair3.py`
is the right tool rather than `restore.py`.

    Jacobian (rows b, lambda_d, pi_eu; cols lambda_addiction,
              addiction_scalar_1, probability_becoming_unemployed)
        b          -1.53   -26.33   -0.98
        lambda_d   -1.36   -36.67   -1.59
        pi_eu      -0.16    -2.52   +0.31
        condition number 132

        lambda_addiction                 19.3086   -> 17.0388
        addiction_scalar_1             0.0183295   -> 0.0184871
        probability_becoming_unemployed 0.0075412  -> 0.0053142

        predicted  b -8%, lambda_d -13%, pi_eu +3%
        from       b -33%, lambda_d -43%, pi_eu +15%

`REPAIR3_d4ffbfdab5.txt`, one line, carrying `number_of_beta_types=1`,
`money_cost_of_treatment=0` and `utility_cost_of_treatment=0`, so it is on the
live configuration and not a stale one.

## THE UTILITY COST IS FLATTER THAN IT LOOKED

    utility cost   tau_u        target 0.245
        0          0.90058
        0.05       0.86350

A cost step of 0.05 buys 0.037 of take-up. Naively that puts the target near
0.88, but that is an EXTRAPOLATION seventeen times the length of the pair that
produced it and the rule here is not to make it. Line 3 at 0.5 is still solving
and will say whether the curve steepens.

What is already settled is the direction and the sign of the problem: take-up
overshoots at zero cost rather than pinning under target, so the instrument
pushes the right way and has unbounded room above. Whether it needs a cost of
0.5 or of 5 is for line 3 and, if necessary, a fourth point.

## THERE IS A kappa BRACKET AFTER ALL, AND y_u's TARGET IS INSIDE IT

I told the author there was no usable bracket on kappa and only the single point
at 8. Wrong: KAPPA_REDO had landed and I had not read it. Both its points are on
`ab22a2f5ba`, the fixed denominator, both two beta, both with the money cost of
treatment still at 0.0600702.

    kappa      y_u        b        lambda_d     tau_u
      6      0.8398     0.3545     0.1259      0.2079
      7      0.6773     0.1423     0.0342      0.2274
    target   0.740      0.089      0.0368      0.245

**y_u STRADDLES ITS TARGET.** 0.740 sits between 0.8398 and 0.6773, at 0.614 of
the way from 6 to 7, so linear interpolation puts kappa at about 6.6. That is an
interpolation INSIDE a measured pair, which is the thing this file keeps saying
to prefer, not an extrapolation past one.

lambda_d at kappa 7 is 0.0342 against 0.0368, seven per cent out, and tau_u is
0.2274 against 0.245, also seven. Neither is being aimed at by kappa.

### WHY 6.6 IS AN UPPER BOUND AND NOT THE ANSWER

b is 0.3545 at kappa 6 and 0.1423 at kappa 7, against a target of 0.089. BOTH
ENDS OF THE BRACKET SIT ABOVE THE TARGET, one by four times and one by sixty per
cent. When that many households use, users are close to the whole population and
their average income drifts toward one for reasons that have nothing to do with
the death multiplier. So y_u is INFLATED at both ends, more so at 6 than at 7.

Correct b downward and y_u falls at every kappa, which means the kappa that
delivers 0.740 at the right b is LOWER than 6.6. How much lower is not
recoverable from this pair; it needs a point where b is near 0.089, which is
what REPAIR3 is for.

That is the same ordering the file already records and it now has numbers on it:
**fix b first, then read kappa off y_u.** Reading kappa now would fit the
artefact rather than the mechanism.

### AND THEY ARE STILL PROVISIONAL

Two beta points on a path whose equal-beta test has not yet passed. If VALIDATE2
fails, the bracket goes with it. If it passes, the bracket stands and only needs
re-siting at the corrected b.

## UTILITY COST OF TREATMENT, BRACKETED ON THE CURRENT MODEL

Three points, ANCHOR1B lines 1-3, one beta, model `d70ad1c545`, identical in
every coordinate except `utility_cost_of_treatment`. All three report
`HANDOVER OK: 29 of 29` and all three close with `END OF MOMENTS`.

| utility cost | point file | tag | tau_u | target |
| --- | --- | --- | --- | --- |
| 0 | `code/points/point_d4ffbfdab5.txt` | d4ffbfdab5 | 0.90058 | 0.245 |
| 0.05 | `code/points/point_3194cee78d.txt` | 3194cee78d | 0.86350 | 0.245 |
| 0.5 | `code/points/point_549be97e28.txt` | 549be97e28 | 0.47477 | 0.245 |

Every `MOMENT` line of the three points, one column per point. The target is
the same at all three except where marked `*`.

| moment | description | cost 0 | cost 0.05 | cost 0.5 | target |
| --- | --- | --- | --- | --- | --- |
| `sigma_y` | bottom half earnings share | 0.16905 | 0.16905 | 0.16905 | 0.17200 |
| `tau_l` | average labour income tax | 0.23828 | 0.23822 | 0.23786 | 0.22400 |
| `omega_l` | labour supply / total hours | 0.40098 | 0.40101 | 0.40104 | 0.40000 |
| `beta` | wealth over output | 4.00162 | 4.00313 | 4.01263 | 3.00000 |
| `h_2` | above half of spending | 0.05113 | 0.05103 | 0.05007 | 0.10100 |
| `h_3` | share in the largest unit | 0.66949 | 0.66902 | 0.67148 | 0.62672 |
| `gamma` | housing over expenditure | 0.18628 | 0.18626 | 0.18672 | 0.26800 |
| `h_1` | homelessness rate | 0.00395 | 0.00394 | 0.00392 | 0.00399 |
| `b` | total drug users | 0.05982 | 0.05821 | 0.03792 | 0.08900 |
| `lambda_d` | disorder rate | 0.02108 | 0.02003 | 0.01283 | 0.03680 |
| `theta` | drug spending share | 0.16343 | 0.16136 | 0.18833 | 0.16200 |
| `aleph` | value of life / income | 56.74720 | 56.74009 | 56.90349 | 80.00000 |
| `pi_eu` | unemployment rate | 0.05574 | 0.05553 | 0.05410 | 0.04850 |
| `kappa_ued` | unemployment given SUD | 0.13537 | 0.13450 | 0.12413 | 0.16250 |
| `kappa_uem` | employment given SMI | 0.29935 | 0.29953 | 0.30079 | 0.30000 |
| `p_m` | SMI population share | 0.04442 | 0.04439 | 0.04416 | 0.04834 `*` |
| `lambda_m` | SMI share of the homeless | 0.23260 | 0.23280 | 0.23304 | 0.25000 |
| `pi_V` | eligibles with a voucher | 0.26929 | 0.26939 | 0.27070 | 0.26600 |
| `cbar` | food stamps / labour income | 0.01182 | 0.01178 | 0.01144 | 0.00420 |
| `tau_u` | treatment take up | 0.90058 | 0.86350 | 0.47477 | 0.24500 |
| `mu_H` | recovery housed / homeless | 1.27838 | 1.25273 | 1.04469 | 1.47321 |
| `w_bot` | net worth share, bottom half | 0.15630 | 0.15644 | 0.15733 | 0.02500 |
| `y_u` | income of drug users | 0.34108 | 0.33755 | 0.26925 | 0.74000 |

`*` `p_m`'s target is not a constant: it reads 0.0483431, 0.0483317 and
0.0482612 at costs 0, 0.05 and 0.5. It is a share of a population the model
computes, so it moves a little with the point. No other target moves.

`theta` is a real value at all three points, so the empty-population sentinel of
-1.0 does not arise here.

### (a) DOES tau_u RISE AS THE COST FALLS? YES, MONOTONICALLY

    cost 0.5   tau_u 0.47477
    cost 0.05  tau_u 0.86350
    cost 0     tau_u 0.90058

The sign is the expected one and there is no reversal in the bracket. The
response is strongly non-linear: the whole interval from 0 to 0.05 buys 0.037 of
take-up, while 0.05 to 0.5 buys 0.389. Take-up is flattening as the cost goes to
zero, which is what a ceiling near one looks like.

### (b) tau_u AT ZERO COST DOES NOT REACH 0.245, AND IT MISSES FROM ABOVE

    tau_u(0) = 0.90058    target 0.245    difference +0.65558

**It does not reach the target, but the shortfall is an overshoot, not a
shortfall.** Zero cost is the top of the instrument's range, not the bottom, so
this is the opposite of the moment being unreachable: at no cost at all nine
households in ten take treatment, and the cost has to be RAISED to bring take-up
down to 0.245. The instrument has the whole half-line above zero to work in.

**What the three points do NOT do is bracket the target.** 0.245 lies below all
three, the lowest of which is 0.47477 at a cost of 0.5, still 0.230 above
target. Reading the answer off these points is therefore an extrapolation past
the end of the measured range, not an interpolation inside it. On the local
slope between 0.05 and 0.5, -0.864 per unit of cost, 0.245 would arrive at a
cost of about 0.77; that number is an indication of where to put the next point
and nothing more, because the response is visibly curved and the slope over the
last stretch of the bracket need not continue. **A fourth point above 0.5 is
what would close this**, and the target should be inside the pair before a value
is read off it.

### WHAT THE COST COSTS ELSEWHERE

Raising the cost from 0 to 0.5 moves four other moments materially, and all four
move AWAY from their targets:

    b         0.05982 -> 0.03792  (target 0.089, 33% out becomes 57% out)
    lambda_d  0.02108 -> 0.01283  (target 0.0368, 43% out becomes 65% out)
    y_u       0.34108 -> 0.26925  (target 0.740, 54% out becomes 64% out)
    theta     0.16343 -> 0.18833  (target 0.162, 0.9% out becomes 16% out)

`mu_H` also falls, 1.27838 to 1.04469 against 1.47321, from 13 per cent out to
29. So the cost that would deliver `tau_u` is not free: it is taken out of the
use and disorder moments, which are already low, and it walks `theta` off a
target it currently sits on. Whatever cost is eventually read off the extended
bracket has to be re-checked against `b` and `lambda_d`, in that order.

### THE want 1.0 DIAGNOSTICS AT LINE 1's POINT

From `code/points/point_d4ffbfdab5.txt`, verbatim:

     DIAG income histogram mass / distribution (want 1.0) =   1.0000000000000839
     DIAG histogram mass / distribution  (want 1.0)   =   1.0000000000000908
     DIAG histogram wealth / total wealth (want 1.0)  =   1.0000000000000910

All three read 1.0 to twelve places. The halved-denominator correction recorded
above is in effect on this model and none of the three reads 2.0.
## THE UTILITY COST BRACKET DOES NOT REACH tau_u, AND IT DRAGS b WITH IT

Three rungs, one beta, model d70ad1c545:

    utility cost   tau_u      b        y_u
        0         0.90058   0.05982   0.34108
        0.05      0.86350   0.05821   0.33755
        0.5       0.47477   0.03792   0.26925
    target        0.245     0.089     0.740

**The target is below all three, so this is not yet a bracket.** The curve does
steepen: 0.05 of cost bought 0.037 of take-up, while the step from 0.05 to 0.5
bought 0.389, a slope of 0.865 per unit against 0.74. At that slope the target
lands near 0.77, but the slope is still accelerating and that is an
extrapolation past the pair, so `TAUU_HIGH.txt` measures 1.0 and 2.0 instead of
assuming it.

### THE COUPLING, WHICH IS THE PART THAT MATTERS

Raising the cost of treatment LOWERS drug use: b falls from 0.05982 to 0.03792
across the bracket, and y_u falls with it. The mechanism is an insurance effect
and it runs the sensible way -- cheap treatment makes experimenting safer, so
dear treatment deters initiation. It is not an artefact.

But it means tau_u and b are NOT orthogonal, and they pull the SAME way when
they need to pull opposite ways:

    b needs to RISE   0.0598 -> 0.089
    tau_u needs to FALL 0.901 -> 0.245, which lowers b

Measured across the bracket, db/dtau_u is about 0.0514. Taking tau_u the whole
0.655 it has to travel would cost 0.034 of b, carrying it from 0.060 to about
0.026 -- from 33 per cent below target to seventy.

**So REPAIR3's step is already stale in one coordinate.** It was computed at a
utility cost of zero and its `addiction_scalar_1` increase was sized against b
at 0.0598. Once the cost rises to whatever tau_u needs, b falls again and the
repair has to be re-run at the new cost. That is not wasted: the repair's
measured Jacobian is what will size the second attempt, and its point is the
first one on this model with the drug block aimed at rather than drifting.

The ordering that follows: bracket tau_u first, then repair b AT the cost that
tau_u wants, not before it.

## kappa AT ONE BETA, ON THE AUTHOR'S INSTRUCTION

"i would also explore the case with 1 beta and kappa chosen to match the income
of users". `KAPPA_1B.txt` is that case: kappa 6.0 and 7.0 at the one-beta
vector of `point_d4ffbfdab5`, which already sits at kappa 8 with y_u 0.34108.

It repeats the KAPPA_REDO pair at one type instead of two, so the two brackets
are directly comparable and the question of whether the second beta changes
kappa's answer becomes a measurement rather than an argument. At two betas the
pair gave y_u of 0.8398 and 0.6773 and straddled the target of 0.740; at one
beta and kappa 8 y_u is 0.34108, well below the 0.6773 that two betas gave at
kappa 7, so the one-type curve sits LOWER and the kappa that hits 0.740 may be
below 6.

The same caveat carries and is the reason this is a bracket and not an answer:
b is 0.0598 at this vector against a target of 0.089, and y_u is only readable
where b is near target.

## DO THE TWO BETAS EARN THEIR KEEP? THEY DO A DIFFERENT JOB FROM kappa

The author asks whether the second beta is needed now that kappa matches the
income of users. The two are not substitutes and do not touch the same moment:

    kappa_phi_d_level         -> y_u,   income of drug users
    discount_factor_impatient -> w_bot, net worth share of the bottom half

Dropping the second beta loses nothing on y_u. What it loses is w_bot, which at
one beta reads 0.1563 against 0.025 -- SIX TIMES the target -- because nothing
drives it there at all.

So the real question is not "beta or kappa", it is **whether the bottom half's
share of net worth is a moment this paper wants to hit**. It is currently in the
targeted list, and Section 1 of the note advertises it in the untargeted
validation set: "the earnings held by the bottom and top tenths and the share of
net worth held by the bottom half". A six-fold miss on a number the paper
reports is a visible weakness whether or not it is targeted.

THE EVIDENCE FOR KEEPING, measured rather than argued. The unequal-beta pair put
w_bot at 0.02265 at an impatient beta of 0.95, nine per cent from target, and
carried wealth over output to 3.015 at the same time -- half a per cent from the
centre of its band, which one beta has never managed (it sits at 4.00, inside
the band but at its top). So the second beta closes two things at once.

THE COST. One extra solve per point, ten minutes against twenty, plus a
two-pass path whose equal-beta test has not yet passed.

VALIDATE2 settles the cost side. If it passes, the second beta is cheap and buys
a six-fold improvement on an advertised moment. If it fails, dropping it is
clearly right and w_bot goes back to being untargeted, which is what it was
before the second beta was added.

## WHAT THE SECOND BETA BUYS ON THE UNTARGETED SET: NOT YET MEASURABLE

The author asks, setting w_bot aside, what two betas buy on the untargeted
statistics. **It cannot be answered from the archive.** The only points ever run
with the betas actually DIFFERENT are `point_38cd0063be` (0.95) and
`point_c6e8793eb5` (0.90), both on model `920988590e`, and that model reports
the LAST TYPE SOLVED rather than the pooled economy. Their untargeted block is
the impatient half's own statistics, not the mixture's. Reading them as the
answer would be reading one half of the population as if it were all of it.

`TWOBETA_UNTARGETED.txt` is the measurement: impatient beta 0.95 and 0.90, at
two types, with every other coordinate identical to `point_d4ffbfdab5`, which is
therefore the one-beta control. Three points, one comparison, 46 untargeted
moments each.

### WHERE TO LOOK WHEN IT LANDS, AND WHY

**The three bottom wealth shares, which are the sharpest test.** The data are
NEGATIVE and the model cannot produce a negative number at all:

    wealth share bottom  1 pct    model 0.00000   data -0.00225
    wealth share bottom  5 pct    model 0.00044   data -0.00422
    wealth share bottom 10 pct    model 0.00310   data -0.00446

The bottom decile of the SCF is in DEBT. A one-beta economy of patient
households does not borrow into negative net worth, so it puts the floor at
zero and the sign is simply wrong. Impatient households are the standard way to
get a household that borrows rather than saves. If the second beta cannot turn
these three negative, its case is much weaker than w_bot alone suggests.

**The homelessness age profile, which is the one I would bet on.** At this
vector it is not merely wrong, it has collapsed:

    share of the homeless   band 1  0.979   data 0.260
                            band 2  0.013   data 0.272
                            band 3  0.004   data 0.210
                            band 4  0.004   data 0.184
                            band 5  0.0004  data 0.075

Ninety-eight per cent of the model's homeless are 25 to 34. This is far worse
than the 34.7 per cent recorded from the August baseline, so it has moved a long
way with the rest of the calibration and the earlier reading should not be
quoted for the current model.

The mechanism ties directly to the age question the author raised: homelessness
here requires exhausting assets, the young hold none, and by 40 a patient
household holds a buffer that no spell of the length this model generates can
burn through. **An impatient household never builds that buffer.** It is exposed
at 55 as much as at 30. If anything in this model can put weight in bands 3 to
5 without touching the unemployment process, it is a household that does not
save -- and that is exactly what the second beta adds.

That is a hypothesis with a mechanism, not a result. It is also the cheapest
test of it available: the run is needed anyway.

Also worth watching, on the same logic: renters above 50 per cent of income
(0.257 against 0.175, too many), the tenant contribution rate (0.471 against
0.312) and the income and employed share of the homeless (0.274 against 0.191,
and 0.976 against 0.460).

NOT expected to move: the earnings shares. Beta heterogeneity acts on wealth,
not on the earnings process, so the top tenth at 0.309 against 0.411 is
somebody else's problem.

## IMPATIENCE IS NOT THE MISSING MECHANISM FOR THE HOMELESSNESS AGE PROFILE

I wrote, one round ago, that the homelessness age profile was the thing I would
bet the second beta on: homelessness needs exhausted assets, an impatient
household never builds a buffer, so it should be as exposed at 55 as at 30.

Measured, the bet loses.

    share of the homeless   one beta   imp 0.95   imp 0.90    data
        band 1 (25-34)       0.9787     0.9232     0.9003    0.260
        band 2 (35-44)       0.0134     0.0429     0.0541    0.272
        band 3 (45-54)       0.0038     0.0175     0.0223    0.210
        band 4 (55-64)       0.0037     0.0147     0.0174    0.184
        band 5 (65+)         0.0004     0.0016     0.0059    0.075

The direction is right and the mechanism is real: bands 3 and 4 rise about
five-fold and band 5 fifteen-fold. But band 1 only falls from 98 to 90 per cent
against a data value of 26, so the movement is a rounding error against the gap.

**AND THIS IS AN UPPER BOUND, not a sample of the mixture.** These two points are
on model `920988590e`, which reports the LAST TYPE SOLVED -- so the 0.9003
column is an economy in which EVERY household is impatient at a discount factor
of 0.90, not one in which half are. Half-and-half must land between the control
and that column. Reading the per-type numbers is legitimate here precisely
because that model computes numerator and denominator consistently per type; it
is the pooling that was wrong, and pooling is not what is being read.

So: even a population made entirely of very impatient households puts nine in
ten of its homeless under 35. Impatience is not what is missing.

**WHAT THIS LEAVES.** The earlier diagnosis stands and is now the only candidate:
entry requires exhausted assets and exit is fast, so the stock never ages. The
unemployment process has no age dimension at all, and homelessness is exactly
zero from 66 onward because retirement income always covers the lowest rung.
Impatience removes the buffer but does not slow the exit, and it does not reach
retirees at all -- band 5 goes from 0.0004 to 0.0059 against a target of 0.075,
still more than ten times short at the extreme of the instrument.

Recorded so the second beta is judged on what it does do -- the wealth
distribution -- and not on this.

## REPAIR3 MEASURED AGAINST ITS PREDICTION

`REPAIR3_d4ffbfdab5.txt` solved as point `9eedd54f04` (10 min, 4 cores,
HANDOVER OK: 29 of 29, MODEL `d70ad1c545` -- the same model hash that measured
`d4ffbfdab5`, so the two points are comparable). Gap is `model/target - 1`, the
convention that reproduces the starting figures below to a tenth of a per cent.

    moment      start    predicted    measured    landed?
    b            -33         -8         +33.8      no, overshot the target
    lambda_d     -43        -13         +38.5      no, overshot the target
    pi_eu        +15         +3          +5.1      close, still 2 points high

**Two of the three did not land, and they did not miss by falling short -- they
crossed.** The step was sized to take b from -33 to -8 and lambda_d from -43 to
-13, that is, to close roughly three quarters of each gap from below. Instead b
moved +67 points and lambda_d +81 points, landing about as far above target as
they began below it, and the two gaps are now nearly the same size with the sign
reversed. The realised move is close to three times the predicted one on b and
roughly two and a half times on lambda_d.

That is the signature of a Jacobian whose drug-block entries are too small in
magnitude at this vector, not of a wrong sign or a wrong instrument: every
direction is the one the linearisation said it would be. `addiction_scalar_1`
carries the large entries (-26.3 on b, -36.7 on lambda_d) and moved only from
0.0183295 to 0.0184871, so a modest error in those two numbers is enough to
account for the overshoot on its own. The condition number of 132 already said
the three-by-three was poorly conditioned.

pi_eu is the one that behaved: predicted +3, measured +5.1, moving from +15.
Its own column entry (+0.31) is the smallest in the matrix and most of its
predicted movement came from the two drug-block columns, so it is worth noting
that it landed reasonably well even though those columns turned out to be
mis-scaled -- its remaining error is about the size of the ones that carried it.

**What this says for the next step.** A second repair taken from the same
Jacobian would be taken from a matrix now known to understate the drug-block
response by a factor of two to three, and the gaps to close are of the same
magnitude as the ones just crossed, so it would be at real risk of crossing
back. The two points `d4ffbfdab5` and `9eedd54f04` differ in three coordinates
and bracket the target on both b and lambda_d, which is a better basis for the
next move than the linearisation was: a secant between them is available on
exactly the moments that matter, and it is fitted to the response the model
actually showed rather than to the one that was estimated.

### EVERY TARGETED MOMENT AT POINT 9eedd54f04

    moment      model         target        gap
    sigma_y     0.16905       0.172           -1.7%
    tau_l       0.239244      0.224           +6.8%
    omega_l     0.39966       0.4             -0.1%
    beta        3.90937       3              +30.3%
    h_2         0.0498483     0.101          -50.6%
    h_3         0.667475      0.626723        +6.5%
    gamma       0.184644      0.268          -31.1%
    h_1         0.00427346    0.00399         +7.1%
    b           0.119086      0.089          +33.8%
    lambda_d    0.0509748     0.0368         +38.5%
    theta       0.18361       0.162          +13.3%
    aleph       59.3982      80              -25.8%
    pi_eu       0.0509975     0.0485          +5.1%
    kappa_ued   0.110628      0.1625         -31.9%
    kappa_uem   0.377837      0.3            +25.9%
    p_m         0.0453705     0.0486614       -6.8%
    lambda_m    0.171129      0.25           -31.5%
    pi_V        0.273752      0.266           +2.9%
    cbar        0.010701      0.0042        +154.8%
    tau_u       0.943635      0.245         +285.2%
    mu_H        1.34203       1.47321         -8.9%
    w_bot       0.154122      0.025         +516.5%
    y_u         0.355095      0.74           -52.0%

`theta` printed a real value, 0.18361, not the -1.0 empty-population sentinel,
so the drug population was non-empty at this vector.

Four moments outside the drug block are worth flagging as unchanged in
character rather than as new damage. `w_bot` at +516 is the structural one-beta
reading recorded above: `discount_factor_impatient` does nothing at
`number_of_beta_types=1`, and it was +525 at `d4ffbfdab5`. `tau_u` at +285 is
treatment take-up at zero utility cost and zero money cost, which is the
configuration this point was run on deliberately; it was +268 before, and the
utility-cost line elsewhere in this file is the instrument for it. `cbar` and
`y_u` are likewise close to their values at the previous point. Of the moments
that were inside ten per cent at `d4ffbfdab5`, `theta` (0.9 -> 13.3) and
`kappa_uem` (0.2 -> 25.9) were pushed out by this step, which is the cost of
moving the drug block this far and is worth recovering in whatever comes next.
## A PREDICTION FOR THE TWO-BETA AGE PROFILE, WRITTEN BEFORE THE MEASUREMENT

`TWOBETA_UNTARGETED` will report the pooled profile. Recording the prediction
now so the run can falsify it rather than confirm whatever is said afterwards.

**The pooled share of the homeless in a band is a HOMELESS-weighted mix of the
two types, not a population-weighted one.** Each type carries unit mass, but the
impatient type generates more than twice as much homelessness -- h_1 of 0.00894
at 0.95 and 0.01004 at 0.90, against 0.00395 for the patient control -- so it
supplies about seventy per cent of the stock and the mixture sits about seventy
per cent of the way to the impatient column, not halfway.

    band    control   imp .95   imp .90    data
      1      0.9787    0.9402    0.9224   0.260
      2      0.0134    0.0339    0.0426   0.272
      3      0.0038    0.0133    0.0171   0.210
      4      0.0037    0.0113    0.0135   0.184
      5      0.0004    0.0012    0.0043   0.075

Predicted: band 1 lands near 0.92 at an impatient beta of 0.90, against a data
value of 0.26. **The age profile stays badly wrong.**

The per-type inputs come from the two void points, which are on model
`920988590e` at a slightly different vector, so the arithmetic is approximate.
The QUALITATIVE claim is not: the pooled value is bounded below by the
pure-impatient column, which is 0.9003, so no mixture of these two types can put
band 1 under ninety per cent. That bound holds whatever the weights.

If the measurement comes back with band 1 much under 0.90, something in this
reasoning is wrong and it is the reasoning that gets revised, not the number.

## REPAIR3 OVERSHOT, WHICH IS WHAT FINALLY BRACKETS b

    moment    before    after    target    predicted
    b        0.05982   0.11909   0.089      -8%   ->  measured +33.8%
    lambda_d 0.02108   0.05097   0.0368    -13%   ->  measured +38.5%
    pi_eu    0.05574   0.05100   0.0485     +3%   ->  measured  +5.2%

The Jacobian was badly wrong on the two drug moments and close on the third. It
predicted a step that would leave b eight per cent short and instead carried it
thirty-four per cent past. pi_eu, whose column came from a different experiment
(the PEU_LADDER rungs), landed where it said it would.

**But the overshoot is worth more than a hit would have been.** b's target has
never been bracketed on this model, and now it is: 0.05982 below and 0.11909
above. So is lambda_d's: 0.02108 and 0.05097 around 0.0368. An interpolation
inside a measured pair replaces a Jacobian that has just been shown to be
unreliable here.

Scanning the fraction of the step that minimises the worse of the two:

    f = 0.511      b        -> 0.09011   +1.2%
                   lambda_d -> 0.03635   -1.2%
                   pi_eu    -> 0.05332   +9.9%

    addiction_scalar_1               0.01832949  -> 0.018410013
    lambda_addiction                   19.30858  -> 18.148733
    probability_becoming_unemployed 0.007541168  -> 0.0064031725

Both drug moments inside the five per cent gate, pi_eu just inside ten.
`REPAIR3_HALF.txt`.

The linearity this assumes is an interpolation between two measured points and
not an extrapolation past them, which is the one form this file trusts. If the
truth is convex between them the measured value will miss and the pair will
narrow, which is still progress.

**AND IT UNBLOCKS kappa.** y_u is only readable where b is near target, which is
why every kappa reading so far has been provisional. If this lands at b +1.2 per
cent, the kappa bracket becomes worth measuring for the first time.

## THE EXCESS DEATH RISK FROM THE STREET IS NOW FLAT IN AGE

The author's instruction, and the reasoning that got there is worth keeping
because the obvious version of it is wrong.

**94 PER CENT OF THE MODEL'S HOMELESS ARE HOMELESS BY CHOICE.** The model's own
diagnostic: `homeless who could afford it on INCOME ALONE = 0.9358` and
`homeless by choice = 0.9358`, where by-choice tests income PLUS assets against
the rent on the smallest dwelling. They are also 97.6 per cent employed against
46 in Meyer et al., and their income is 0.274 of average against 0.191. The
model's homeless are comfortable and working.

So the age profile is not a profile of who cannot afford rent. It is a profile
of who is willing to sleep rough, and what they trade off is the extra chance of
dying.

**THAT DETERRENT RISES STEEPLY WITH AGE, AND A FLAT MULTIPLIER MAKES IT WORSE.**

    age     qx      (a) Baggett  x26   (b) flat 1.6  x26   (c) flat risk  x26
     26   0.00116     0.00396   1.00     0.00070    1.00     0.00396    1.00
     45   0.00304     0.00869   2.19     0.00183    2.62     0.00396    1.00
     65   0.01316     0.01917   4.84     0.00790   11.34     0.00396    1.00

(b) is the 1.6 the note's `external_calibration.tex` quotes from Meyer, Wyse and
Logani, and which `increased_risk_of_death_homeless=0.6` still carries in the
source. **A flat MULTIPLIER is not a flat RISK.** The excess is (kappa-1) times
baseline mortality, and baseline mortality rises elevenfold over the working
life, so the flat multiplier has the STEEPEST age gradient of the three. It
would have made the profile younger, not older.

(c) holds the excess RISK flat, which makes the multiplier fall with age:

    age 26  4.41    age 35  3.10    age 45  2.30    age 55  1.66    age 65  1.30

`homeless_death_risk_flat_in_age=1` selects it, `homeless_excess_death_risk`
carries the level, defaulting to 0.00396 -- Baggett's own implied excess at 26,
so the youngest household's deterrent is UNCHANGED and only the gradient is
removed. It is a handover parameter, in the vector, and deliberately NOT given a
moment in `next_batch.py`: `size_homelessness` already owns h_1 and giving both
the same moment is the duplicate-driver mistake beta was cured of an hour ago.

### WHAT THIS DOES NOT FIX, STATED IN ADVANCE

Retirement. Homelessness is exactly zero from 66 onward and the reason is that
social security plus accumulated assets always clear the lowest rung, not the
death risk. Band 5 is 7.5 per cent of the homeless in the HUD count.

And the level, not just the shape. Making the old less deterred raises
homelessness at older ages but also raises the aggregate, so `size_homelessness`
will have to come back down to hold h_1 at 0.399 per cent. The two move
together and the profile is what should be read, not the level.

### A DISAGREEMENT BETWEEN THE NOTE AND THE CODE, ALREADY ON RECORD

`code/FORTRAN_AUDIT.md` line 538 has it: the note says kappa_phi_H is 1.6 flat,
the code ran 4.41 falling to 1.09. That was true before this change and is still
true after it, differently. **Section 5's external calibration table needs to
say what the code now does** -- but that is prose in the paper and so the
author's call, not mine, and it is not being edited here.

## KAPPA AT ONE BETA

`KAPPA_1B.txt` is now measured. Both lines solved at the one-beta vector of
`point_d4ffbfdab5`, which supplies the kappa 8.0 row:

    kappa   point         y_u              b              lambda_d         tau_u
    ------  ------------  ---------------  -------------  ---------------  ---------------
    6.0     cd817d0401    0.47060          0.37765        0.26045          0.96268
    7.0     abc9b6aa2c    0.40835          0.18573        0.10954          0.95963
    8.0     d4ffbfdab5    0.34108          0.05982        0.02108          0.90058
    target                0.740            0.089          0.0368           0.245

`y_u` falls monotonically in kappa across all three points, by roughly 0.062
per unit of kappa between 6.0 and 7.0 and 0.067 between 7.0 and 8.0.

**The target for `y_u` of 0.740 does NOT lie inside the measured pair 6.0 to
7.0.** The pair spans 0.40835 to 0.47060, and 0.740 sits above the whole of it
-- above even the kappa 6.0 endpoint, by 0.269. There is no interpolation to
report. Since `y_u` decreases in kappa, the bracket has to extend DOWNWARD, to
kappa below 6.0, and how far below is not something these three points can say:
no value is quoted here because it would be an extrapolation off the end of the
measured range, and the curve is under no obligation to stay linear over a gap
that is more than four times the step already measured.

This confirms the reading recorded above from kappa 8 alone -- that the one-type
curve sits lower than the two-type one and the kappa matching 0.740 may be below
6 -- and turns it from an inference into a measurement.

WARNING, and it is why nothing here is an answer. `b` is nowhere near its target
of 0.089 at these points, and the direction reverses across the bracket: it runs
to 0.37765 at kappa 6.0 and 0.18573 at kappa 7.0, four times and twice the
target, while at kappa 8.0 it falls to 0.05982, a third below it. `y_u` is only
trustworthy where `b` is near target, so every kappa read off this bracket is
provisional, and the two endpoints that would set a downward extension are the
two where `b` is furthest wrong.
## THE THREE DEATH-RISK SPECIFICATIONS ARE BEING MEASURED, NOT ARGUED

The author objected to the flat-risk change: a flat 1.6 multiplier lowers the
deterrent for everyone, the old included, from 4.41 to 1.6 at 26 and from 2.46
to 1.6 at 65. That is correct and my table did not contradict it. The
disagreement is about WHICH OBJECT the household trades off.

    Baggett -> flat 1.6      multiplier        excess death probability
        age 26              4.41 -> 1.60       0.00396 -> 0.00070   (to 18%)
        age 65              2.46 -> 1.60       0.01917 -> 0.00790   (to 41%)
        age 75+             1.09 -> 1.60       an INCREASE

On the multiplier the young's cut is bigger. On the excess PROBABILITY, which is
(kappa-1) times baseline mortality and is what enters the value function, the
young's cut is also bigger -- to eighteen per cent against forty one -- so the
old-to-young ratio of the deterrent WORSENS, from 4.84 to 11.34. On that
arithmetic a flat 1.6 makes the profile younger.

**But the level effect cuts the other way and arithmetic cannot settle it.**
Every household gets a cheaper street; which group crosses its indifference
margin first depends on where each sits relative to it, and that is general
equilibrium, not algebra. The author may be right and I may be reading a ratio
where a level decides.

`homeless_death_risk_flat_in_age` is now a VECTOR COORDINATE rather than a
compile-time parameter -- 0 Baggett, 1 flat excess risk, 2 flat multiplier 1.6
-- so all three run from one build and land in one archive.
`DEATHRISK3.txt` is the three of them at an otherwise identical vector, with
`point_d4ffbfdab5` as the reference.

**Read the band shares, not h_1.** All three change the level of homelessness as
well as its shape, and `size_homelessness` will have to move afterwards to hold
h_1 at 0.399 per cent. The question this settles is which specification puts
weight in bands 2 to 5, against HUD's 0.260, 0.272, 0.210, 0.184, 0.075.

## THE MORTALITY GRADIENT IS NOT WHY THE HOMELESS ARE YOUNG. REVERTED

I told the author the deterrent was 4.84 times larger at 65 than at 26 and built
a change on it. That number was the excess death PROBABILITY and ignored what a
death costs. Weighted by discounted expected remaining life on the housed life
table at the model's own discount factor:

    age   multiplier   excess qx   disc. years left   DETERRENT   x age 26
     26      4.41       0.00396         47.7            0.189       1.00
     34      4.46       0.00628         41.2            0.259       1.37
     42      3.85       0.00748         34.7            0.259       1.37
     50      3.60       0.01053         28.2            0.296       1.57
     58      3.01       0.01550         21.8            0.337       1.79
     66      2.32       0.01849         15.7            0.290       1.53
     74      1.15       0.00396          9.7            0.038       0.20
     82      1.09       0.00556          3.6            0.020       0.11

**Nearly flat from 26 to 66.** The young face a far larger proportional risk and
lose far more life per death, and the two very nearly cancel. A deterrent ratio
of 1.37 between 26 and 34 cannot produce the EIGHTY-FOLD difference in
homelessness rates between band 1 and band 2 that the model shows.

And the last two rows finish it off: at 74 and 82 the deterrent COLLAPSES to a
fifth and a tenth of the young's, so the street is far cheaper for the very old
-- and band 5 is empty anyway. Whatever holds the old in housing, it is not fear
of dying.

`homeless_death_risk_flat_in_age` is back to 0, Baggett, on the author's
instruction. The coordinate and the other two settings stay, because they cost
nothing and DEATHRISK3 is already measuring them.

## SO WHY ARE THEY YOUNG? NOT KNOWN, AND NOT TO BE GUESSED AT AGAIN

The mortality story was the second explanation offered and the second to fail
on measurement -- impatience was the first. The remaining candidate is the other
side of the trade: what the household GAINS by not paying rent, which should be
largest where the marginal value of resources is largest. But that is a
hypothesis of exactly the kind that has now been wrong twice, and the model does
not report by age the things that would settle it.

`print_all_moments` now prints four columns, age by age:

    homelessness rate, homeownership rate, renter wealth, renter income

with the reasoning in the source. If homelessness tracks renter WEALTH it is a
buffer story. If it tracks the OWNERSHIP rate it is tenure -- an owner cannot be
homeless, and two thirds of this model's households sit in the largest unit. If
it tracks neither it is preferences, and the housing utility at the lowest rung
is where to look.

`AGEDIAG.txt` is one run at the reference vector to read them off.
## REPAIR3_HALF MEASURED AGAINST ITS INTERPOLATION

`point_4796363037`, model `d70ad1c545`, 29 of 29 parameters applied, 17 min on
four cores. This is the f = 0.511 point of the REPAIR3 step, the one the section
above predicted by linear interpolation between the two measured endpoints.

    moment      predicted    measured    vs prediction    target    vs target
    b             0.09011    0.083713          -7.1%      0.089        -5.9%
    lambda_d      0.03635    0.034312          -5.6%      0.0368       -6.8%
    pi_eu         0.05332    0.053566          +0.5%      0.0485      +10.4%

**THE INTERPOLATION DID NOT HOLD.** The gate is five per cent on b and lambda_d
and neither is inside it: b came in at -5.9 per cent and lambda_d at -6.8. Both
missed in the SAME direction, each landing below the straight line drawn between
the endpoints, so the two drug surfaces are convex in the step fraction over
this interval rather than linear. The section above named that possibility --
"if the truth is convex between them the measured value will miss and the pair
will narrow" -- and that is what happened. It is a near miss, not a failure of
the bracket: an interpolation inside a measured pair is still the right
instrument here, it was simply evaluated on a chord that sits under the curve.

pi_eu is the third confirmation that its column is trustworthy. It was predicted
+9.9 per cent against target and measured +10.4, half a per cent off its own
prediction, which is the same behaviour it showed on the overshoot point. The
drug instruments are the unreliable ones; the p_eu column is not.

**THE PAIR NARROWS AND BOTH MOMENTS NOW AGREE ON THE SAME FRACTION.** b's target
is still bracketed, now by 0.083713 below and 0.11909 above instead of 0.05982
and 0.11909; lambda_d's by 0.034312 and 0.05097. Re-interpolating on the
narrowed pair:

    f implied by b        = 0.5841
    f implied by lambda_d = 0.5840

The two instruments were three percentage points of step apart at the last
reading and are now within one ten-thousandth of each other, which is a much
stronger signal than either number alone. The vector at f = 0.584:

    addiction_scalar_1               0.01832949  -> 0.0184215254
    lambda_addiction                   19.30858  -> 17.9829095
    probability_becoming_unemployed 0.007541168  -> 0.00624047316

Convexity means this second chord is again drawn under the curve, so the same
bias should be expected a second time and the next reading should undershoot
slightly rather than land exactly. The interval it is drawn across is now a
quarter of the width, so the bias should be smaller by about that much.

### EVERY TARGETED MOMENT AT THIS POINT, WORST FIRST

    moment     description                      model      target      gap
    w_bot      net worth share, bottom half    0.155384    0.025000   +521.5%
    tau_u      treatment take up               0.942830    0.245000   +284.8%
    cbar       food stamps / labour income     0.011368    0.004200   +170.7%
    y_u        income of drug users            0.364526    0.740000    -50.7%
    h_2        above half of spending          0.050923    0.101000    -49.6%
    beta       wealth over output              3.964183    3.000000    +32.1%
    gamma      housing over expenditure        0.185807    0.268000    -30.7%
    aleph      value of life / income         57.954883   80.000000    -27.6%
    kappa_ued  unemployment given SUD          0.124728    0.162500    -23.2%
    lambda_m   SMI share of the homeless       0.193250    0.250000    -22.7%
    kappa_uem  employment given SMI            0.335603    0.300000    +11.9%
    pi_eu      unemployment rate               0.053566    0.048500    +10.4%
    mu_H       recovery housed / homeless      1.322949    1.473214    -10.2%
    theta      drug spending share             0.177788    0.162000     +9.7%
    p_m        SMI population share            0.044848    0.048486     -7.5%
    h_1        homelessness rate               0.003710    0.003990     -7.0%
    h_3        share in the largest unit       0.669244    0.626723     +6.8%
    lambda_d   disorder rate                   0.034312    0.036800     -6.8%
    tau_l      average labour income tax       0.238712    0.224000     +6.6%
    b          total drug users                0.083713    0.089000     -5.9%
    pi_V       eligibles with a voucher        0.273785    0.266000     +2.9%
    sigma_y    bottom half earnings share      0.169050    0.172000     -1.7%
    omega_l    labour supply / total hours     0.400173    0.400000     +0.0%

**THE WORST MOMENT IS `w_bot`, AT +521.5 PER CENT.** Excluding h_3 does not
change the ranking: h_3 is at +6.8 per cent here, seventeenth of twenty three,
nowhere near the top. The three above a hundred per cent are all previously
recorded structural readings rather than new damage, and none of them is a
consequence of this step:

  - `w_bot` +521.5 is the one-beta reading. `discount_factor_impatient` does
    nothing at `number_of_beta_types=1`, and this moment has sat at +516 and
    +525 at the two neighbouring points, and +521.5 sits between them.
  - `tau_u` +284.8 is treatment take-up at zero utility cost AND zero money
    cost, which is the configuration this vector was deliberately run on
    (`utility_cost_of_treatment=0`, `money_cost_of_treatment=0`). It was +285
    at the overshoot point.
  - `cbar` +170.7 and `y_u` -50.7 are close to their values at the endpoints of
    this step.

`theta` printed 0.1778, a real value and not the -1.0 empty-population
sentinel, so the drug block is populated and lambda_d, tau_u and kappa_ued are
being read off a real population rather than an emptied one.

Of the moments that matter for the gate, ten are now inside ten per cent and
b and lambda_d are both inside seven. That is the closest b has come on this
model -- it was -7.5 at `point_7add914d47` -- but NOT the closest lambda_d,
which was -1.7 at that same point; what is new is that both are close at once
and at a vector whose pi_eu is also inside eleven.

`y_u` at -50.7 is the reading the section above said would
become worth trusting once b was near target; b is now within six per cent, so
this is the first y_u reading on this branch that is worth acting on, and it is
badly out.

## THE TWO-BETA CALIBRATION THE AUTHOR ASKED FOR, RUN AS SPECIFIED

"patient beta to net worth to income and impatient beta to match the share of
net worth of the bottom 50%". Both are wired and both have been all along:

    patient beta      -> wealth over output, target 3.0, by the model's internal
                         bisection, gap_discount_factor_1 at line 33887
    impatient beta    -> w_bot, target 0.025, by next_batch.py's OWN map

`TWOBETA_CAL.txt`: three lines at `number_of_beta_types=2`, impatient beta at
0.95, 0.93 and 0.97, from `point_4796363037` -- the REPAIR3_HALF result and the
best drug block measured on any model, b at -6.0 per cent and lambda_d at -6.8.
The patient beta bisects to its own target inside each run, so only the
impatient one needs bracketing, and 0.025 sat between 0.90 and 0.95 on the
earlier pair.

### I CALLED THE TWO-BETA MODEL UNUSABLE AND THAT WAS WRONG

The equal-beta validation reports which moments disagree AND BY HOW MUCH, and
the two the author's assignment targets are among the accurate ones:

    moment                    one-pass     two-pass    ratio
    beta   wealth over output  4.012148     4.047583   1.0088
    w_bot  bottom half share   0.157160     0.159292   1.0136

**Both inside one and a half per cent.** The badly wrong ones are elsewhere:
tau_l 0.497, pi_eu 0.509, y_u 1.973, tau_u 0.090, kappa_ued 4.18, aleph 2.82.
I generalised from "23 of 46 differ" to "no number can be trusted", which throws
away the very information the test was run to get.

Two further things I got wrong on the way here, recorded because the pattern
matters more than any one of them:

- Equal betas is a configuration NOBODY ASKED FOR. It is a unit test I invented,
  and the specified configuration has the two betas different by construction,
  each pushed to its own moment. Treating a failure in a state the model is
  never meant to occupy as a gate on the state it IS meant to occupy cost
  several runs.
- I claimed the first validation failed because the patient beta drifts away
  from the impatient one during a run. `freeze_beta_bisection` disproved it:
  frozen and unfrozen agree to six digits. The original failure was real and my
  correction to it was not.

### WHAT TO STILL TREAT AS PROVISIONAL IN A TWO-BETA POINT

tau_l and pi_eu are halved AND are internal adjuster targets, so the tax rate
and the separation rate are driven by a moment that is wrong by a factor of two.
That distorts the economy every other moment is measured in. The 1.4 per cent
agreement on w_bot says the distortion is small in practice AT ONE VECTOR, which
is an observation and not a guarantee. So: read w_bot and wealth over output.
Treat tau_l, pi_eu, y_u, tau_u, kappa_ued and aleph as provisional until the
pooling bug is found.

## THE ARCHIVE WAS BEING THROWN AWAY BY MY OWN EDITS. EQUIVALENCE DECLARED

`dc8abdfbce` differs from `d70ad1c545` by print statements and by two
compile-time parameters becoming runtime coordinates, BOTH defaulting to the
value that reproduces the old behaviour exactly. A point that passes
`homeless_death_risk_flat_in_age=0` on the new hash is the same economy as one
measured on the old. Declared in `EQUIVALENT_MODELS`; the archive went from 0
scored points to 8.

Worth naming as a process cost: the source changed five times today and each
change orphaned every measurement. `EQUIVALENT_MODELS` exists for exactly the
print-only case and should be used at the time of the edit, not after the gate
comes back empty.

## THE DRUG BLOCK, CLOSED ON THREE MEASURED POINTS

The repair overshot and its half-step undershot, which leaves three points on one
line and no need for a Jacobian at all:

    fraction   b        lambda_d     (targets 0.089 and 0.0368)
      0.000   0.05982   0.02108
      0.511   0.08371   0.03431
      1.000   0.11909   0.05097

Interpolating, **b and lambda_d both land on target at f = 0.584** -- the same
fraction to three decimals, which is the local linearity the interpolation
assumes showing up as a coincidence it did not have to produce.

    addiction_scalar_1                 0.018421517
    lambda_addiction                   17.98304
    probability_becoming_unemployed    0.0062406018

`DRUGCLOSE.txt`. If it lands the gate opens for the first time on this model,
and y_u becomes readable -- kappa has been unmeasurable all day precisely
because b was never near target.

## WHERE THE AUTHOR'S SEVEN STAND, AT THE BEST POINT, ONE BETA

    b          0.083713   0.089     5.9   IN
    lambda_d   0.034312   0.0368    6.8   IN
    h_1        0.003710   0.00399   7.0   IN
    aleph      57.955     80       27.6   out
    h_2        0.050923   0.101    49.6   out
    y_u        0.36453    0.74     50.7   out
    w_bot      0.15538    0.025   521.5   out, and has no instrument at one beta

Three of seven, and 11 of 23 overall. The four that are out have instruments and
none of them is stuck: `value_of_life` owns aleph, `largest_house_size` owns h_2
and moves it at +1.73, `kappa_phi_d_level` owns y_u and its target sits inside a
measured pair, and `discount_factor_impatient` owns w_bot and is bracketed.

**The untargeted set is not worth reading until those close.** The author asked
for the age profile of homelessness and the rest of the untargeted table at a
properly calibrated point, and that is the right order: an age profile read off
a point with y_u fifty per cent out is a profile of the wrong economy.

## THE POOLING BUG, LOCALISED BY COMPARING DIAGNOSTICS RATHER THAN GUESSING

Third attempt, and this one is a measurement. The two frozen-beta points differ
only in `number_of_beta_types`, so every diagnostic that disagrees is a
bookkeeping error. Comparing all 58:

    ratio   diagnostic
    1.9937  mass in the top THREE savings grid points
    1.9950  mass ON the top savings grid point
    2.0230  mass with a NEGATIVE value of life
    2.0637  working age homeless mass
    2.1886  average assets of the homeless

**A clean family at exactly 2.0, and all of them are printed in
`print_all_moments`**, which runs AFTER the two-pass loop has ended and
`accumulating_beta_types` is back to zero. Pooled numerators over a denominator
holding one type.

**The cause.** `calculate_welfare_by_characteristics` is SEVENTH of the nine
statistics routines in the loop. It recomputes `sum_of_distribution` from
`distribution_stationary` and does not scale it to pooled mass. Since that
variable is MODULE scope, the one-type value it leaves behind is what every
later reader sees -- the eighth and ninth routines, and then every print.

Positions 1, 2, 3, 3 and 5 all scale correctly. Position 7 does not, and it is
the last one to touch the variable.

**I caused it.** The scaling was applied to all seventeen sites, then reverted
at seven of them on the reasoning that they were "per-type or outside the loop".
This one is inside the loop, and the reasoning was wrong in a specific way worth
naming: **the routine does not OWN the variable.** Whether a routine's own use
of a shared module variable wants the one-type value says nothing about what the
routines after it want, and `sum_of_distribution` is read by nine routines and
two hundred lines of prints.

`VALIDATE3.txt` re-runs the equal-beta test. If the 2.0 family goes to 1.0 the
diagnosis holds; tau_l, halved for a reason not yet found, is the test of
whether it was the ONLY cause.

## TWO BETAS IS THE MODEL NOW. ONE BETA IS STOPPED

The author: "you can stop running the one beta model, let's focus on the two
beta model", and "i want it calibrated properly first to see what it gives".

`number_of_beta_types` defaults to 2 in both the source and `run_one_point.sh`,
so nothing runs one type by accident. The DRUGCLOSE run was interrupted; its
vector is not wasted, it is the base of `TWOBETA_DRUGCLOSE.txt`.

**CALIBRATED PROPERLY MEANS THE MOMENTS HAVE TO BE RIGHT FIRST.** At two types
`tau_l` and `pi_eu` read half their true values, and both are internal adjuster
targets: the model would drive the labour income tax rate and the separation
rate to hit numbers that are wrong by a factor of two, and every parameter
downstream would land somewhere wrong. `probability_becoming_unemployed` is also
one of the three instruments the drug repair uses and pi_eu is its moment. So a
two-type calibration run before the pooling fix is checked is a calibration to
the wrong targets, which is worse than no calibration because it looks like one.

`VALIDATE3.txt` is that check and it is 30 minutes, against roughly six hours
for a full calibration loop. It is not a detour from the author's instruction,
it is the first step of carrying it out.

Order:
  1. VALIDATE3 -- does the fix take the 2.0 family to 1.0, and does tau_l follow?
  2. TWOBETA_DRUGCLOSE -- the closed drug vector at two types, impatient beta at
     0.95 and 0.93, which is where w_bot's target was bracketed.
  3. TWOBETA_CAL -- already running, the impatient beta bracket at 0.93/0.95/0.97.
  4. Then the gate, at two types, on whatever survives.

## CHECKED PROPERLY, ON THE AUTHOR'S INSTRUCTION. THREE MORE BUGS, ONE CLASS

"you need to check it". The check was: for every module-scope mass recomputed
per pass inside the loop, which routines READ it afterwards? That is the
question that catches this class, because a routine can be internally consistent
and still poison everything downstream of it.

**IT ALSO SHOWED MY LIST OF THE TWO-PASS CHAIN WAS WRONG.** The driver calls
nine routines, and `stationary_equilibrium_wealth_distribution`,
`stationary_equilibrium_income_distribution` and
`stationary_equilibrium_income_bottom_distribution` are NOT among them. I had
been auditing four routines that do not run in the loop and missing what does.
`calculate_cdf_of_incomes_earned` IS in it, nested inside position 8.

### 1. THE SCALING WAS RIGHT ONLY INSIDE THE LOOP

`(accumulating_beta_types+1)` is the pass number, which is what a recomputed mass
must be scaled by -- INSIDE the loop. After the loop that expression is 1, so
every routine running afterwards scaled by nothing while reading pooled
accumulators. `stationary_equilibrium_wealth_distribution` is called at 36568,
after the loop ends at 33782, and divides pooled wealth by a one-type mass.

Replaced at all eleven sites by `mass_passes`, which the driver sets to
`current_beta_type` inside the loop and to `number_of_beta_types` after it. One
expression, correct in both places.

### 2. A ROUTINE CALLED TWICE, THE SECOND TIME DESTRUCTIVELY

`calculate_homeownership_by_characteristics` was called inside the loop once per
type AND again at 36562. Out there `accumulating_beta_types` is zero, so every
one of its guarded resets fired: it wiped the pooled totals and refilled them
from `distribution_stationary`, which by then holds only the last type solved.

**Every by-age number was the impatient half's, reported as the population's** --
the homelessness profile, the ownership rate, renter wealth and renter income.
Which is precisely the table the author asked for. Removed.

Harmless at one type, which is why it survived: with one pass the wipe-and-refill
reproduces exactly what was there.

### 3. TWO DEAD ROUTINES

`stationary_equilibrium_income_distribution` is never called from anywhere.
`stationary_equilibrium_income_bottom_distribution` has only commented-out calls.
Left alone -- deleting them is not a repair -- but noted so no one audits them
again.

### THE CLASS, WHICH IS THE POINT

All three bugs, and the one before them, are the same shape: **a routine written
for a single pass, called in a place where the pass count is no longer what it
assumes.** The guards and the scaling are both correct in the context they were
written for and both silently wrong outside it. Neither a syntax check nor a
reading of the routine finds that; only asking who calls it, and when, does.

## DRUGCLOSE MEASURED AGAINST ITS INTERPOLATION

`points/point_6716556560.txt`, MODEL `dc8abdfbce`, HANDOVER OK 31 of 31, solved
in 10 min on 4 cores. This is the f = 0.584 point on the three-point line of the
section above, the one the interpolation said would put b and lambda_d on target
simultaneously.

A caveat on the hash, recorded because it is the standing hazard: the branch
moved while this point was solving. `57863ad` ("Fix two more pooling bugs")
changed the source, so HEAD now hashes `c7cb2b24b6` and this point is stamped
`dc8abdfbce`. The measurement is of the PRE-FIX model and is labelled as such.
Anything the pooling fixes touch -- the audit names tau_l, pi_eu, y_u, tau_u,
kappa_ued and aleph as provisional under that bug -- has to be re-measured before
it is read. b and lambda_d are not in that list.

### (a) The drug block: both inside five per cent, and the interpolation held

    measured    target    gap      predicted   gap vs prediction
    b          0.087684   0.089     -1.5%      0.08899   -1.5%
    lambda_d   0.035697   0.0368    -3.0%      0.03680   -3.0%

**Both are inside five per cent, so the drug block gate is open.** It is the
first time on this model that b and lambda_d have been simultaneously inside it.

The interpolation was not merely close, it was correct to the accuracy it
claimed: it predicted the two moments would land on target and they landed 1.5
and 3.0 per cent below, both on the same side and both small. The line through
the three measured points is real and the local linearity it assumed holds.

### (b) Every targeted moment, worst first

    moment                                       model        target      gap
    w_bot      net worth share, bottom half     0.15623       0.025     +525%
    tau_u      treatment take up                0.947152      0.245     +287%
    cbar       food stamps / labour income      0.0109639     0.0042    +161%
    y_u        income of drug users             0.364232      0.74       -51%
    h_2        above half of spending           0.0512945     0.101      -49%   (conceded)
    beta       wealth over output               3.96146       3.0        +32%   (banded 3.0-4.5, inside)
    gamma      housing over expenditure         0.185575      0.268      -31%
    lambda_m   SMI share of the homeless        0.175167      0.25       -30%
    aleph      value of life / income          58.2037       80.0        -27%
    kappa_ued  unemployment given SUD           0.122695      0.1625     -25%
    kappa_uem  employment given SMI             0.341462      0.3        +14%
    mu_H       recovery housed / homeless       1.32814       1.47321    -9.8%
    pi_eu      unemployment rate                0.0530953     0.0485     +9.5%
    theta      drug spending share              0.175902      0.162      +8.6%
    p_m        SMI population share             0.0448898     0.0484979  -7.4%
    h_3        share in the largest unit        0.668672      0.626723   +6.7%   (conceded)
    tau_l      average labour income tax        0.238731      0.224      +6.6%
    h_1        homelessness rate                0.00411101    0.00399    +3.0%
    lambda_d   disorder rate                    0.0356975     0.0368     -3.0%
    sigma_y    bottom half earnings share       0.16905       0.172      -1.7%
    b          total drug users                 0.0876836     0.089      -1.5%
    pi_V       eligibles with a voucher         0.269701      0.266      +1.4%
    omega_l    labour supply / total hours      0.400355      0.4        +0.1%

**The worst moment excluding h_3 is `w_bot`, the bottom-half net worth share, at
+525 per cent** -- 0.156 against a target of 0.025. h_3 does not need conceding
here to get that answer: at +6.7 per cent it is the sixteenth worst of
twenty-three and is itself inside ten. The concession is not costing anything at
this point.

Nine of twenty-three are inside ten per cent and thirteen are inside thirty. The
three that dominate -- w_bot, tau_u, cbar -- are all above 160 per cent, and they
are a different order of miss from everything below them: the gap falls from
+161 to -51 in one step. `theta` is 0.176, a real value and not the -1.0
empty-population sentinel.

### (c) THE AGE PROFILE OF THE HOUSING MARGIN

    age    homeless      own    renter wealth   renter income
     26    0.149708   0.00000        0.00000        -0.03582
     29    0.005882   0.00000        0.32058        -0.02052
     32    0.001413   0.00000        0.56279        -0.01043
     35    0.000570   0.00000        0.80530        -0.00037
     38    0.000326   0.00000        1.05852         0.00997
     41    0.000185   0.00000        1.31175         0.02001
     44    0.000110   0.00000        1.57106         0.02975
     47    0.000073   0.00000        1.82889         0.03851
     50    0.000066   0.00000        2.07752         0.04618
     53    0.000061   0.00000        2.30847         0.05240
     56    0.000055   0.00000        2.49855         0.05634
     59    0.000078   0.00000        2.62823         0.05778
     62    0.000078   0.00000        2.68586         0.05699
     65    0.000071   0.00000        2.67277         0.05330
     68    0.000000   0.00000        2.43250         0.63128
     71    0.000000   0.00000        2.06073         0.62012
     74    0.000000   0.00000        1.63830         0.60745
     77    0.000000   0.00000        1.18256         0.59378
     80    0.000000   0.00000        0.72744         0.58013
     83    0.000000   0.00000        0.33151         0.56825

**Homelessness tracks renter wealth. It does not track the ownership rate, and
it cannot: the ownership column is 0.00000 at every one of the twenty ages
printed.** There are no owners anywhere in this economy, so that column has no
variation to explain anything with, and the tenure story is ruled out by
inspection rather than by comparison.

What the wealth column shows is the whole of the age profile in one movement.
Renter wealth is exactly zero at 26 and homelessness is 0.1497 -- fifteen per
cent of the cohort on the street. By 29 renter wealth is 0.32 and homelessness
is 0.0059, a fall of a factor of twenty-five in one three-year step. By 32
wealth is 0.56 and homelessness is 0.0014. The collapse is over before age 35,
and it is over exactly as the first units of renter wealth are accumulated. From
there wealth rises monotonically to 2.69 at 62 and homelessness grinds down to
0.000055 at 56. Rank correlation over the fourteen ages where homelessness is
non-zero is -0.82.

Two things in the columns qualify that, and both are small:

- Renter income rises over the same span, from -0.036 at 26 to +0.058 at 59, and
  its rank correlation with homelessness is -0.83, indistinguishable from
  wealth's. **Over the working life the wealth and income columns move together,
  so this profile on its own does not separate them.** What it does separate is
  either of them from ownership.
- Past 68 the co-movement with wealth breaks: renter wealth falls back from 2.43
  to 0.33 while homelessness stays at exactly zero. Renter income jumps at the
  same age from 0.053 to 0.631 and stays there. So at retirement ages the two
  right-hand columns diverge from each other, and homelessness -- already at
  zero from 68 on -- follows neither.

Read against the question the diagnostic was written to answer, the answer is
the buffer story and not the tenure story, with the caveat that the buffer could
be the wealth stock or the income flow and these twenty rows do not tell them
apart over the ages where homelessness is positive.

The remaining fact in the column is the one the diagnostic was added to explain:
homelessness in this model is almost entirely an age-26 phenomenon. 0.1497 at
26 against 0.0059 at 29 and nothing at all past 65.

### (d) The untargeted set

Read with the caveat in (a) -- this is the pre-pooling-fix model -- and against
the standing note that the untargeted table is not worth much while y_u is 51
per cent out. It is recorded because the gate is open and the author asked for
it at a point with the drug block closed.

    moment                                    model        observed
    mean age of drug users                   44.3223      45.48
    users aged 26-34, share                   0.493201     0.28404
    users aged 35-44, share                   0.154772     0.25054
    users aged 45-54, share                   0.0783022    0.17768
    users aged 55-64, share                   0.0582706    0.16327
    users aged 65 plus, share                 0.215454     0.12445
    housing over income, renters              0.255199     0.202
    delta_d child SUD ratio                   1.15755      2.0
    wealth share bottom  1 pct                0.0         -0.00225
    wealth share bottom  5 pct                0.000458318 -0.00422
    wealth share bottom 10 pct                0.00313072  -0.00446
    income share bottom  1 pct                0.000699866  0.00009
    income share bottom  5 pct                0.00349933   0.00288
    income share bottom 10 pct                0.00849702   0.00924
    delta_h child homelessness ratio          2.67167      2.1
    homelessness rate, band 1                 0.0226353    0.003161
    homelessness rate, band 2                 0.000275785  0.003378
    homelessness rate, band 3                 0.0000721794 0.002912
    homelessness rate, band 4                 0.0000732767 0.002496
    homelessness rate, band 5                 0.0000044099 0.00077
    homelessness profile, band 1              5.50601      1.28079
    homelessness profile, band 2              0.0670846    1.36872
    homelessness profile, band 3              0.0175576    1.17990
    homelessness profile, band 4              0.0178245    1.01135
    homelessness profile, band 5              0.00107271   0.31199
    share of the homeless, band 1             0.980298     0.26
    share of the homeless, band 2             0.0130139    0.272
    share of the homeless, band 3             0.00328807   0.21
    share of the homeless, band 4             0.00311429   0.184
    share of the homeless, band 5             0.000285312  0.075
    earnings share, bottom tenth              0.0125067    0.0099
    earnings share, top tenth                 0.308662     0.411
    renters above 30 pct of income            0.411678     0.406
    renters above 50 pct of income            0.257031     0.175
    tenant contribution rate                  0.470537     0.312
    voucher holders, wages main               0.483513     0.28
    participation, with a SUD                 0.855880     0.658
    participation, without a SUD              0.746606     0.615
    homeless at treatment admission           0.000145722  0.145
    SMI alongside SUD at admission            0.0187683    0.431
    working, homeless in treatment            0.168283     0.066
    SUD share of the homeless                 0.00120125   0.217
    drug deaths, share of deaths              0.274794     0.2
    income of the homeless                    0.238084     0.191
    employed share of the homeless            0.980744     0.46
    income with a SUD                         0.430890     0.711

Four rows land close without having been targeted: renters above 30 per cent of
income (0.412 against 0.406), the bottom-tenth earnings share, the bottom-five
and bottom-ten income shares, and the mean age of drug users (44.3 against 45.5).

The homelessness band rows are the same fact as the age profile seen along the
income dimension: band 1 holds 98 per cent of the model's homeless against 26
per cent in the data, and bands 2 through 5 are each one to two orders of
magnitude below their observed rates. Homelessness in this economy is
concentrated in one income band and one age in a way it is not in the data.

Two rows are near-degenerate and worth naming rather than leaving in the list:
`SUD share of the homeless` is 0.0012 against 0.217, and `homeless at treatment
admission` is 0.00015 against 0.145. The homeless population and the SUD
population barely intersect at this point. That is a strong statement and it sits
next to `employed share of the homeless` at 0.98 against 0.46 -- the model's
homeless are young, employed and clean, which is not the population the data
describes.

## TEN RUNTIME INVARIANTS, CHECKED ON EVERY POINT

The model carried three: the histogram mass checks. **Those three are what
caught the first pooling bug.** They had been printing 2.0000 for hours while
the code was read and the diagnosis guessed at, wrongly, three separate times.
Reading 38,000 lines does not find that class. A number that must be 1.0 and is
not finds it on the first run.

So the block now checks ten, each printing PASS or FAIL, with a count on the
last line so a run can be triaged with one grep:

  - the income histogram holds the whole distribution
  - the wealth histogram holds the whole distribution
  - the wealth histogram holds the whole of net worth
  - THE RENTAL MARKET CLEARS: demand over supply is 1. If this fails the price
    every household faces is wrong and with it every housing choice, so it is
    the one invariant here that guards the economics rather than the reporting.
  - six shares lie in [0,1]: homelessness, drug users, the disorder, SMI,
    unemployment, homeownership. A share above one is a pooling error or a
    denominator that lost its mass; a negative one is an accumulator running
    backwards.
  - the five age bands hold ALL of the homeless. This one is aimed squarely at
    today's worst bug: `homelessness_by_age_group` is normalised to sum to one
    by construction, so a failure means the normalisation ran against a
    different population from the one the bands were filled from -- which is
    exactly what a routine called once inside the two-pass loop and once outside
    it produces.

`check_one` and `check_range` are two small helpers beside `print_all_moments`.
Adding an invariant is now one line.

**This is the durable half of the audit.** Seven readers on 38,000 lines will
find dead parameters, guard mismatches and index errors, and then they stop.
These ten run on every point forever, including for the classes nobody thought
to look for.

## THE tau_l BUG, FOUND BY THE CALL GRAPH. AND ELEVEN ROUTINES IN THE SAME SHAPE

A line-range audit cannot find this class, because the defect is not in any one
slice: it is a routine defined in one place and called from another, in a
context it was not written for. So the call graph was built and every routine
checked for the pattern that produced today's worst bug.

**Eleven routines are called both inside the two-pass loop (lines 33803-33898)
and outside it.**

    calculate_aggregate_consumption        calculate_welfare
    calculate_homeownership_by_char...     calculate_welfare_by_characteristics
    calculate_household_housing_spending   converge_to_stationary_equilibrium
    govt_revenues_calc                     initialize_feasible_distribution
    solve_value_function_and_policy_...    stationary_equilibirum_homeownership_rate
    stationary_equilibrium_statistics

Most of the outside calls are in `long_run_counter_factual` and
`transition_simulation`, which do not run in a point. Two are not.

### THE LIVE ONE: govt_revenues_calc AT LINE 36285

In `calibrating_model`, in the benchmark path, after the loop has ended and
`accumulating_beta_types` is back to ZERO. So every guarded reset in that
routine fires, and it refills from `distribution_stationary` -- which by then
holds ONLY THE LAST TYPE SOLVED.

    govt_revenues_from_labour_income   reset and refilled -> ONE type
    model_total_efficiency_units       untouched, still     -> TWO types
    model_financial                    untouched, still     -> TWO types

    tau_l = govt_revenues_from_labour_income
            / (model_total_efficiency_units + model_financial*r)
          = one type's revenue over two types' income
          = HALF

**Measured: 0.497.** That is the mechanism and the number agrees.

It matters more than a wrong print, because `tau_l` is an internal adjuster
target: the model drives `labor_income_tax_rate` to make this halved number
equal 0.224, so the tax rate converges to roughly twice what the data asks for,
and every household in the model faces it. This is the one bug today that
reaches the economics.

### THE FIX IS NOT OBVIOUS AND IS NOT BEING MADE UNILATERALLY

The call exists to refresh revenues after the driver has updated average labour
income, median income and average net wealth for the internal calibration. It
CANNOT simply be made to accumulate instead of reset: `distribution_stationary`
no longer holds type 1 at that point, so there is nothing to accumulate onto.
The candidates, none free:

  1. move the refresh inside the two-pass loop -- but the averages it refreshes
     against are pooled and updated once per outer iteration, so this changes
     what is being computed, not just where;
  2. keep both types' distributions alive so a post-loop routine can rebuild
     the pooled object -- correct, and the largest change;
  3. drop the call and accept revenues one outer iteration stale.

This is a modelling decision about what the refresh is for, so it is the
author's.

### THE SECOND, GATED OFF BUT LIVE IF ENABLED

`print_all_moments` contains two child-penalty counterfactual blocks that
re-solve, re-converge and re-run `stationary_equilibrium_statistics` and
`govt_revenues_calc`, then never restore the baseline. They are skipped because
`measure_child_gap=0`. Set it to 1 and every moment printed after that point is
a single-type counterfactual's, silently.

## THREE FIXES APPLIED ON THE AUTHOR'S INSTRUCTION

### 1. tau_l: the post-loop refresh call is REMOVED  [LIVE, benchmark, economics]

`call govt_revenues_calc(1)` in `calibrating_model`, after the two-pass loop
where `accumulating_beta_types` is back to zero. Every guarded reset fired: it
wiped the pooled revenue totals and refilled from `distribution_stationary`,
which holds only the last type solved. Its denominators are accumulated
elsewhere and stayed pooled.

    tau_l = one type's revenue / two types' income = HALF.   Measured 0.497.

tau_l is an internal adjuster target, so the model drove
`labor_income_tax_rate` up until the halved number reached 0.224 -- toward twice
the tax rate the data asks for, faced by every household. **The only bug found
today that reaches the household's decision rather than the reporting.**

Removed rather than repaired, because it cannot be repaired locally: type 1's
distribution does not exist at that point, so there is nothing to accumulate
onto. Dropping the call leaves every revenue quantity holding the value the LOOP
computed -- pooled and correct, one outer iteration stale -- and the next outer
iteration re-runs the whole chain anyway. `set_SS_benefits`, the only call
between it and the adjusters, reads nothing `govt_revenues_calc` produces.

### 2. The band-7 print that fired 372 times  [LIVE, reporting]

`k_1=min(k_1+1,7)` pinned the band index at 7, so once cumulative mass passed
the last NSDUH cut the print condition fired on every remaining bin. Band 7 was
printed 372 times in `point_4796363037`. Every print after the first is ONE
BIN's rate, not the band's, because the accumulators reset just above -- so a
reader taking the last value got 0.0 where the band was 3.3e-8. Now exits after
the top band. Numerically tiny; 370 lines of noise removed from every point.

### 3. The stale comment on number_of_beta_types  [documentation]

Said it defaulted to one type; it has defaulted to two since the author moved to
the two-type model.

## AND A CORRECTION THE AUTHOR MADE, WHICH KILLS A CLAIM OF MINE

I wrote that the second beta BRACKETS y_u's target, on 0.3645 at one type
against 1.5725 at two. The author: "you have too many users and too many SUD, so
it is not fully comparable to the one beta model."

Correct, and it voids the claim. At the two-type point b is 0.60 and lambda_d
0.26, six times their targets. With that share using, the composition of users
is nothing like the one-type point's, so the y_u difference is mostly the drug
block being open and not the second beta.

**The clean test is two betas WITH b AT 0.089**, which is what DRUG2B measures.
If y_u sits near 0.740 there, the second beta helped. If it falls back toward
0.36, it did not. Until then y_u at two betas says nothing.

## TWO MORE FIXES: PINNED ADJUSTERS STAY PINNED  [Audit A, finding 2]

`damp_on_flip`'s damping branch is `max(adj*0.5, floor)`. At `adj=0` that is
`max(0, floor) = FLOOR`. So the first time a gap changed sign, an adjuster
sitting at exactly zero jumped to the floor and then grew by 1.2 a loop up to
its start value -- 1e-4 reaches 5e-2 in about thirty four loops. The growth
branch, `min(0*1.2, start)=0`, was harmless; only the damping branch
resurrected.

Four adjusters reach `damp_on_flip`, every one documented as fixed:

    relative_share_of_housing      "ZERO, AND DELIBERATELY ... next_batch.py
                                    owns it across points instead"
    relative_share_of_leisure      frozen by freeze_fitted_internals
    housing_status_grid_expander   declared zero
    penalty_child_homeless         "EXTERNALLY SET"

and `penalty_child_addicted` has the same rule written out inline at 35143 with
the same effect. Both sites now return early on a non-positive adjuster.

**What it was doing.** In a calibrating run, delta_h, gamma and omega_l would
move away from the values handed in on the vector, while the archive still
recorded them as pinned. A parameter drifting with no record that it moved --
which also means a point could not be reproduced from its own VECTOR line.

Dead in a single-point run, because that is one loop and needs a sign FLIP.
Live in any calibration loop, which is exactly what the author is about to run.

## SO: IS THE TWO-BETA CALIBRATION READY? NOT YET, AND HERE IS THE LIST

1. **VALIDATE4 must pass.** The equal-beta test on the fully fixed source is the
   only complete check of the two-pass path -- with identical types every one of
   242 reported numbers must match the one-type run. It failed twice; four
   causes have been found and fixed; whether that was all of them is not
   something reading can answer. Running, thirty minutes.

2. **Audit A finding 1 is not fixed.** `distance_utility_cost_of_treatment`
   gates the calibration while-loop, but `utility_cost_of_treatment_adjuster=0`,
   so the distance can never fall below its stopping rule and the loop cannot
   exit on it. Meanwhile the live cost, `money_cost_of_treatment`, has an
   adjuster, a distance and a stopping rule referenced NOWHERE. This one needs
   a decision: either tau_u is calibrated internally on one of the two costs, or
   its distance comes out of the loop condition and next_batch owns it.

3. **DRUG2B is measuring on the pre-tau_l source.** Its three points carry the
   halved tax rate. The BRACKET on addiction_scalar_1 still transfers -- b is
   monotone in it and steeply so -- but the levels do not, so whatever
   `addiction_scalar_1` it identifies has to be re-measured on the fixed source
   before it is believed.

## THE BIGGEST FINDING: 187 IN-PLACE NORMALISATIONS, AND THE FOUNDING ASSUMPTION IS FALSE

Audit C, finding 1. The pattern, on `model_fraction_unemployed`:

    reset       if (accumulating_beta_types==0) X=0     guarded to pass 1
    accumulate  X = X + distribution_mass_used          correct
    normalise   X = X / mass                            EVERY PASS, ungated

    pass 1   X = u        then  X = u/T      a RATE is now in the accumulator
    pass 2   X = u/T + u  then  X = (u/T + u)/(2T)      a rate plus a mass

against a correct pooled `2u/2T = u/T`. The ratio is **(1+T)/(2T)**.

**That is one only when T is exactly one.** The driver's comment asserts "each
type's distribution carries unit mass, so summing both passes doubles the
numerator and the denominator of every one of them" -- **and it does not**. The
run log prints `sum(distribution_guess) = 51.718`, the life-cycle sum of cohort
masses. So the factor is just above one half for a large denominator and blows
up as `1/(2m)` for a small subpopulation.

The whole two-pass design rests on that sentence, and the sentence is false.

Audit C counted 69 in its own slice. Across the nine-routine chain there are
**187**:

    61  govt_revenues_calc
    43  stationary_equilibrium_statistics
    31  calculate_welfare_by_characteristics
    26  stationary_equilibirum_homeownership_rate
    20  calculate_homeownership_by_characteristics
     3  calculate_household_housing_spending
     3  calculate_welfare

All 187 are now gated on `current_beta_type==number_of_beta_types`, so the
division happens once, on the last pass, over the fully accumulated numerator
and denominator. At one type that is every pass and nothing changes, which is
why none of this was ever visible in the one-beta model.

This also subsumes Audit B's F2: `model_fraction_homeless` was normalised in
`stationary_equilibrium_statistics` and then re-accumulated and re-normalised in
`govt_revenues_calc`, giving a 1:3 mixture of the two types instead of 1:1.
Gating both normalisations fixes the pair.

**Every two-beta number measured before this is void.** Not scaled by a known
factor -- the error depends on the size of each denominator, so it differs
moment by moment. Nothing measured at one beta is affected.

## FIXES 8 TO 12, WORKING THROUGH THE AUDIT

**8. aleph was a LEVEL over a mean, so it scaled with the number of types.**
[Audit B F4] `model_value_of_life` is a mass-weighted SUM of V/MU and was never
divided by anything; `model_average_labour_income` is a mean. The driver's own
comment says to look for exactly this -- "A LEVEL would come out doubled, which
is why it is worth checking that no targeted moment is one" -- and this one was.
Normalised to a per-household mean on the last pass. All four sites that read
`model_value_of_life` read it as this same ratio, so one division fixes them all.
`vsl_data=80` is defined in the declaration as a multiple of AVERAGE household
income, so per household is the intended object.

**9. cbar was the second level-over-mean moment.** [Audit B F5] Same shape, but
`govt_spending_on_food_stamps` is ALSO the government budget's spending line and
the results file's level, so it cannot be normalised in place. A new
`model_food_stamps_per_household` is computed once where the pooled mass is
known, and the moment reads that. Note it read roughly right BEFORE, only
because the duplicate `govt_revenues_calc` call was halving it; fixing that
without this would have doubled cbar.

**10. mass_by_age was rebuilt by three routines in sequence.** [Audit B F6] All
three resets guarded to pass one, all three accumulating every pass, so
`govt_revenues_calc` ended at M1+M2 (correct), `calculate_welfare_by_
characteristics` at M1+2*M2 and `calculate_homeownership_by_characteristics` at
M1+3*M2 -- and the last is where `homelessness_by_age` and `homeownership_by_age`
are normalised. **The age profile the author asked for was reading half its true
value.** It is the same quantity in all three, so the first owner's copy is kept
and the later reset/accumulate pairs are disabled. The call order is the same in
the driver and in `long_run_counter_factual`, so it is always built before read.

**11. Four trackers reset unguarded.** [Audit C finding 5]
`model_largest_negative_value_of_life` and
`smallest_financial_chosen_in_equilibrium` are extreme-value trackers whose
second-pass reset discarded the patient type's extreme entirely; both have
guarded twins a line away, which is what marks them as oversights.
`average_rent_by_age` and `mass_of_renters_by_age` are both halves of a ratio,
internally consistent but describing only the last type solved.

**12. Three one-type routines unscaled.** [Audit C finding 3, my own regression]
Recorded above.

## STILL OPEN, AND WHY

  - Audit A finding 1: the treatment take-up distance gates a loop it cannot
    close. Needs a decision, not a fix: either tau_u is calibrated internally on
    one of the two costs, or its distance comes out of the loop condition.
  - Audit E finding 1: the memoised expectation is not keyed on the treatment
    choice. Counterfactual only, and the fix touches the solver's hot path.
  - Audit F-04, F-05, F-07, F-10: a probability vector that does not sum to one,
    an unassigned array index, a race in a `default(none)` region, and two
    `intent(out)` arguments left unassigned on one path.
  - Audit B F9 to F14 and Audit G 3 to 12: universe and denominator mismatches.

## FIXES 13 TO 15, AND A DECISION TAKEN IN THE AUTHOR'S ABSENCE

**13. An array index that is assigned nowhere in the file.** [Audit F-05]
`years_left_on_mortgage_index_used` subscripts `distribution_guess`, which is
`dimension(1:2)`, on both a read and a write, and it is never assigned anywhere.
It would not fail loudly: a local integer most often reads 0, one element below
the array. The enclosing loop runs over `years_left_on_mortgage_index`, which is
plainly what was meant. Dead while `solve_transition_dynamics=0`; **live the
moment the transition is switched on, which CLAUDE.md says is being built now.**

**14. A probability vector that did not sum to one.** [Audit F-04] Six long, the
clean block 1:3 and the SMI block 4:6, and the row was completed over 1:2 only,
leaving the SMI entries outside the sum. It totalled one plus the SMI share of
the clean population. It is the initial guess for the distribution iteration,
which converges to a fixed point independent of its guess, so no moment moves --
but it inflated the starting mass and cost sweeps. Now completed over the whole
vector.

**15. THE DECISION: the treatment take-up distance is out of the convergence
test.** [Audit A finding 1, which I had said needed the author's call]

`distance_utility_cost_of_treatment` sits in the `do while` condition while
`utility_cost_of_treatment_adjuster` is zero, so the step cannot move the
parameter and the distance can never fall below its stopping rule. **The
calibration loop therefore ran to its iteration cap on every point and stopped
with the other distances wherever they happened to be, rather than converged.**

The author left before deciding. I have taken it, and the reasoning is:
`next_batch.py` already owns tau_u through `utility_cost_of_treatment` -- it is
in OWN, with bounds, and the author asked for that switch explicitly this
afternoon. So the moment is not abandoned by removing it from the loop; it is
calibrated across points instead of inside one. The alternative -- giving the
adjuster a non-zero value -- would put tau_u under two drivers at once, which is
the mistake beta was cured of earlier today.

Implemented as `merge(0, abs(gap), adjuster<=0)`, so the distance returns to the
test automatically if anyone ever gives the adjuster a value. Same shape as
`freeze_fitted_internals`: an adjuster at zero takes its distance with it.

**This one may matter more than its severity suggests.** Every calibration loop
run against this model stopped at its cap rather than at convergence.

## FIX 16: y_u's NUMERATOR EXCLUDED INTEREST INCOME WHILE ITS DENOMINATOR INCLUDED IT

[Audit B F9] LIVE, TARGETED, and it points the way the failure points.

    numerator    model_avg_income_drug_users, accumulated with income_1
                 = social security, or earnings, or UI/DI. NO interest.
    denominator  model_average_income, which adds
                 r*max(a,0)*mass UNCONDITIONALLY.

The interest-inclusive object, `income_2`, is computed a hundred lines above the
numerator's accumulation and used for the voucher eligibility test just below it,
but was not used here.

**Why it is a mismatch and not a convention.** NSDUH's income variable is total
personal income, so the 0.740 target is the interest-inclusive ratio. And the
model's users are not asset-poor: `assets of drug users / average net worth`
prints 0.4589, against a wealth-to-output ratio near four, so the omitted term is
large.

**The bias is DOWNWARD, and y_u has been failing downward all day** -- 0.33 to
0.47 against 0.740, with kappa unable to close it. This may be a large part of
why. Not measured; the direction is unambiguous.

Five numerators switched to `income_2`, all with the same fault:

    model_avg_income_drug_users     y_u, targeted
    val_user_inc_band               the NSDUH income-band gradient
    val_user_income_working         income of working-age users
    model_average_income_addicted   UNTARGETED income with a SUD
    model_avg_homeless_income       UNTARGETED income of the homeless

**Checked before believing it**: `income_2` is assigned at 11521 and 11959, and
every one of the five new uses sits in the SAME loop body as its assignment --
net loop depth zero and no `end do` crossed between them -- so none reads a stale
value. A use-before-set does exist at line 11031, with no prior assignment
anywhere; it is pre-existing and not one of these five, and is left for the next
pass.

## FIX 17: h_1 HAD TWO OWNERS

[Audit B F2, Audit G 12] `model_fraction_homeless` was reset, accumulated AND
divided in BOTH `stationary_equilibrium_statistics` and `govt_revenues_calc`.
Both resets guarded to the first pass, so on the second pass the later routine
accumulated a MASS on top of the RATE the earlier one had produced, then divided
again:

    after pass 2, SES   (M1+M2)/2          the correct pooled rate
    after pass 2, GRC   ((M1+M2)/2 + M2)/2 = 1/4 h1 + 3/4 h2

**A 1:3 mixture over-weighting the impatient type**, and h_1 is TARGETED --
`size_homelessness` is bisected on it. Ownership given to
`stationary_equilibrium_statistics`, which runs first.

## THE SAME CLASS, DOCUMENTED AND NOT YET FIXED

Six more variables are reset by more than one chain routine. All untargeted, so
none of them moves a calibration; all of them make a reported statistic wrong at
two types. Left deliberately rather than fixed blind, because each needs its
universes confirmed and I have already introduced one regression today by moving
fast on this exact class:

    mass_by_employment          SES, GRC, CWBC, CHBC -- four owners. The worked
                                example in Audit G: welfare-by-employment comes
                                out HALVED and homeownership_by_employment at
                                0.4 times truth.
    mass_by_employment_and_age  CWBC, CHBC
    total_homeless_1            SES, GRC
    mass_of_owners              SES, SEHR -- dead while ownership is off
    mass_renters_by_age         SEHR, calculate_household_housing_spending

The rule to apply to each: exactly ONE routine may reset and accumulate a
variable; the rest read it. The call order inside the loop is SES, SEHR, GRC,
aggregate_consumption, welfare, housing_spending, welfare_by_characteristics,
homeownership_by_characteristics, wealth_of_old -- and it is the same order in
`long_run_counter_factual`, so the first owner in that list is always safe.

# ===================================================================
# THE PLAN WHILE THE AUTHOR IS AWAY, 31 AUGUST 20:20
# ===================================================================

The author: "once the code is ready, start the calibration of the two beta
model", and before that, "keep fixing and auditing, i will let you continue on
your own". This is the standing plan. The engine fires every thirty minutes and
should read THIS section first.

## STEP 1 -- VALIDATE5 MUST PASS. Nothing else matters until it does.

`session_01FWJv2tYBanDkntKvY6RRx9`, source `df02e3db80`. The equal-beta test:
both discount factors equal, bisection frozen, so the two types are identical
copies and all 242 reported numbers must match the one-type run. It found 135
disagreements before the seventeen fixes.

  - **PASS** -> go to step 2.
  - **FAIL with a much smaller count** -> the remaining disagreements name the
    remaining bugs, one per line, with the ratio. Fix those, re-run, repeat.
    This is the loop that converges; do not start a calibration inside it.
  - **FAIL with 135 again** -> something is wrong with the test or the checkout,
    not the model. Check the source hash the worker actually ran.

## STEP 2 -- RE-MEASURE THE DRUG BLOCK AT TWO TYPES

Everything measured at two betas before 20:00 today is void: the 187-site
normalisation bug alone changed every ratio by (1+T)/(2T) with T the denominator
mass, so the error differs moment by moment and no scaling recovers it.

`DRUG2B.txt` is written and its three lines are still the right experiment --
`addiction_scalar_1` at 0.0182, 0.0180, 0.0178 from the drug-closed vector, at
two betas. Re-launch it on the validated source. At two types the one-beta
closure did NOT transfer: b came out at 0.601 against 0.089, because impatient
households discount the future cost of the disorder and use far more. The
elasticity of b on `addiction_scalar_1` measured 80 at one beta, so bracket,
never step.

## STEP 3 -- THEN THE CALIBRATION LOOP, AT TWO TYPES

`number_of_beta_types` defaults to 2 in both the source and `run_one_point.sh`.
The assignment the author specified: patient beta bisected internally on
wealth over output, target 3.0; impatient beta driven by `next_batch.py` on
`w_bot`, target 0.025. Both are wired and verified.

Run the gate as normal. The archive has ZERO points on the fixed source, so seed
first -- do not run `next_batch.py` against an empty archive.

## WHAT TO WATCH, AND WHY

  - **y_u.** Fix 16 made its numerator interest-inclusive to match its
    denominator. The bias was downward and y_u has been failing downward all day
    at 0.33 to 0.47 against 0.740, with kappa unable to close it. It may now come
    in much closer without kappa moving at all. If it does, the kappa bracket
    measured earlier is void and kappa should be re-sited.
  - **The age profile.** Fix 10 found it was divided by three times one type's
    mass instead of two, so every by-age number was half its true value. The
    author has asked for this table repeatedly. It is in every point now as the
    `DIAG age` block: homelessness, ownership, renter wealth, renter income.
  - **h_1.** Fix 17 gave it a single owner; it had been a 1:3 mixture.
  - **The ten INVARIANT lines.** All must read PASS on every point. If one FAILS
    the point is not evidence, whatever its moments say.

## THE DRUG-CLOSED VECTOR AT TWO BETAS

`TWOBETA_DRUGCLOSE.txt`, both lines, run one at a time. Both printed
`HANDOVER OK: 31 of 31 parameters applied` and both ended at
`===== END OF MOMENTS =====`.

    line   discount_factor_impatient   point file
      1              0.95              code/points/point_a4e79fb29e.txt
      2              0.93              code/points/point_d4997341f9.txt

### THE VECTOR THAT RAN IS NOT THE DRUG-CLOSED VECTOR

Read this before reading (a). `TWOBETA_DRUGCLOSE.txt` does not set
`addiction_scalar_1`. `DRUGCLOSE.txt` does, at `0.018421517`, and that value is one
of the three coordinates the drug closure interpolated -- it is named as such in
THE DRUG BLOCK, CLOSED ON THREE MEASURED POINTS above, beside `lambda_addiction`
and `probability_becoming_unemployed`. Diffing the two command lines, they differ
in exactly three places:

    addiction_scalar_1=0.018421517      present in DRUGCLOSE, ABSENT in TWOBETA_DRUGCLOSE
    discount_factor_impatient           0.99715  ->  0.95 / 0.93   intended
    number_of_beta_types                1        ->  2             intended

`run_one_point.sh` hands `addiction_scalar_1` to the model through
`B_SWEEP_GRID.txt` rather than through `PARAM_HANDOVER.txt`, so an omitted value
falls back to the script default silently and the handover count still reads
31 of 31. Both `VECTOR` lines record what actually ran:

    addiction_scalar_1=0.0224532        the run_one_point.sh default, f = 0
    addiction_scalar_1=0.018421517      what the closure asked for, f = 0.584

**So the two points hold two of the three closed drug coordinates and the third at
its pre-repair value.** `lambda_addiction` and `probability_becoming_unemployed`
are at the closure; `addiction_scalar_1` is 21.9 per cent above it. Whatever (a)
reports is therefore a property of a vector the closure never proposed, and the
excess in `b` cannot be split between the missing coordinate and the second type
from these two runs alone. **The run that splits it is line 1 with
`addiction_scalar_1=0.018421517` appended**, which is one 25-minute solve.

### THE TWO POINTS CARRY DIFFERENT MODEL STAMPS, AND IT DOES NOT MATTER HERE

The branch moved under the runs. Line 1 is stamped `c7cb2b24b6` (commit `57863ad`,
"Fix two more pooling bugs"); line 2 is stamped `597c747ad7` (commit `82a59ba`,
"Check ten invariants on every point"). I read the diff between those two
revisions of the Fortran: it adds `check_one`, `check_range` and one call block at
the end of `print_all_moments`, and changes no quantity the model computes. The
pair is comparable. Neither stamp is HEAD -- the source was `aaffea6ff8` when this
section was written and had already moved to `df02e3db80` by the time it was
committed -- so `next_batch.archive()` will not score either point until they are
re-measured. The branch is being pushed to by more than one session at once and
the source is moving faster than a 25-minute solve, which is the standing hazard
here: a point is orphaned by a source change that lands while it is still solving.

My own first solve of line 1 landed on the older `80a0966e5c` (commit `5292489`,
before the pooling fix) and read `b` at 0.601452 -- exactly 2.0000 times the
0.300726 the same vector gives on `c7cb2b24b6`, with `lambda_d`, `w_bot` and `beta`
unmoved to five figures. That is the pooled-numerator signature again, and it is
the reason the stale line-1 file was replaced rather than kept.

### THE NOISE FLOOR, MEASURED RATHER THAN ASSUMED

Line 2 was solved twice, same vector and same `597c747ad7`, in two containers.
Across all 23 targeted moments the two readings differ by:

    worst   tau_l         0.165 %
    median  (all 23)      0.005 %

**A 0.95-against-0.93 difference smaller than about 0.2 per cent is solver noise,
not the discount factor.** `sigma_y`, `omega_l`, `p_m` and the two earnings shares
all sit at or under that.

### (a) b AND lambda_d: THE ONE-TYPE CLOSURE DID NOT TRANSFER

At one beta the interpolated vector put `b` at 0.08899 and `lambda_d` at 0.03680,
on targets of 0.089 and 0.0368. At two types, on the vector described above:

    discount_factor_impatient        b     gap vs 0.089    lambda_d   gap vs 0.0368
              0.95              0.300726     +237.9 %      0.255213     +593.5 %
              0.93              0.360406     +305.0 %      0.309200     +740.2 %

**Plainly: it did not transfer.** `b` is between three and four times its target
and `lambda_d` between seven and nine times its, and both move further away as the
impatient factor falls. Nothing here is a near miss to be interpolated back onto
target; the drug block is open again at two types.

The one honest qualification is the one above: `addiction_scalar_1` was not at its
closed value in either run, so **"the closure did not transfer" is established for
the vector that ran and not yet for the closure itself.** Both readings are
consistent with either story and the deciding run is named above.

### (b) w_bot AND beta: THE TARGET IS NOT BRACKETED

These are the two moments the two-beta assignment aims at. The patient factor is
bisected onto `beta` inside the model; the impatient factor is set from outside and
aimed at `w_bot`.

    discount_factor_impatient      w_bot    gap vs 0.025        beta   vs band 3.0-4.5
              0.95              0.068756     +175.0 %      2.7508   below the band
              0.93              0.050575     +102.3 %      2.7223   below the band

**0.025 does NOT lie between the two measured `w_bot` values.** They are 0.050575 at
0.93 and 0.068756 at 0.95; the target sits below both, so it is not bracketed and
there is nothing to interpolate. The 0.02 step in the impatient factor moved
`w_bot` down by 0.018181, which is 71.1 per cent of the distance from the 0.93
reading to the target.

Extrapolating the same slope, 0.9091 of `w_bot` per unit of the impatient factor,
puts the crossing at **0.9019** -- outside the measured span by more than the span
itself. That number is written down as the next place to solve and NOT as an
answer: the bracket has to be closed by a run below 0.93 before any value is read
off it.

`beta` is below the 3.0 to 4.5 band at both points (2.7508 and 2.7223) even though
it is the coordinate the model bisects and `freeze_beta_bisection` is 0. The
internal bisection is not reaching its target from this vector, and that is a
separate failure from the `w_bot` bracket, not a consequence of it.

### (c) EVERY TARGETED MOMENT, BOTH POINTS, WORST FIRST

Ranked on the larger of the two gaps.

    moment     description                    target  |      0.95      gap  |      0.93      gap
    cbar       food stamps / labour income    0.0042  |   0.05273  +1155.4% |   0.06088  +1349.4%
    lambda_d   disorder rate                  0.0368  |   0.25521   +593.5% |   0.30920   +740.2%
    b          total drug users                0.089  |   0.30073   +237.9% |   0.36041   +305.0%
    tau_u      treatment take up               0.245  |   0.98502   +302.0% |   0.98762   +303.1%
    w_bot      net worth share, bottom half    0.025  |   0.06876   +175.0% |   0.05057   +102.3%
    theta      drug spending share             0.162  |   0.36158   +123.2% |   0.37309   +130.3%
    y_u        income of drug users             0.74  |   1.57250   +112.5% |   1.63923   +121.5%
    aleph      value of life / income             80  | 142.39205    +78.0% | 138.40334    +73.0%
    pi_V       eligibles with a voucher        0.266  |   0.09626    -63.8% |   0.09167    -65.5%
    h_1        homelessness rate             0.00399  |   0.00146    -63.4% |   0.00145    -63.6%
    tau_l      average labour income tax       0.224  |   0.09579    -57.2% |   0.08914    -60.2%
    h_3        share in the largest unit     0.62672  |   0.46895    -25.2% |   0.42595    -32.0%
    gamma      housing over expenditure        0.268  |   0.18670    -30.3% |   0.18530    -30.9%
    pi_eu      unemployment rate              0.0485  |   0.05817    +19.9% |   0.06247    +28.8%
    h_2        above half of spending          0.101  |   0.07446    -26.3% |   0.07671    -24.0%
    kappa_ued  unemployment given SUD         0.1625  |   0.13265    -18.4% |   0.13619    -16.2%
    lambda_m   SMI share of the homeless        0.25  |   0.28070    +12.3% |   0.24337     -2.7%
    mu_H       recovery housed / homeless     1.4732  |   1.33791     -9.2% |   1.31526    -10.7%
    beta       wealth over output                  3  |   2.75077     -8.3% |   2.72233     -9.3%
    kappa_uem  employment given SMI              0.3  |   0.31531     +5.1% |   0.31030     +3.4%
    omega_l    labour supply / total hours       0.4  |   0.38266     -4.3% |   0.38209     -4.5%
    sigma_y    bottom half earnings share      0.172  |   0.16905     -1.7% |   0.16905     -1.7%
    p_m        SMI population share         0.050716/0.051532  |   0.05065     -0.1% |   0.05154     +0.0%

`p_m` carries two targets because the SMI (serious mental illness) target is
itself recomputed from the solved population.

**Two invariants FAIL on line 2**, which is the only one of the two points whose
stamp prints them at all:

    INVARIANT FAIL     income histogram holds the whole distribution  =     1.1933543996   want   1.0000
    INVARIANT FAIL     wealth histogram holds the whole distribution  =     1.1933543996   want   1.0000

Nineteen per cent of surplus mass in the two histograms. `w_bot`, `sigma_y` and
the six bottom-tail shares are all read off those histograms, so **(b) rests on a
failing identity** and its numbers should be re-read once that is closed. Line 1
predates the check and is presumed to carry the same failure.

### (d) THE BY-AGE MARGIN

    age  |            beta_imp 0.95            |            beta_imp 0.93
         | homeless   own  rnt wealth rnt inc  | homeless   own  rnt wealth rnt inc
     26  | 0.027525  0.00    0.00000 -0.03590 | 0.027525  0.00    0.00000 -0.03683
     29  | 0.002745  0.00    0.32750 -0.02215 | 0.002718  0.00    0.29916 -0.02314
     32  | 0.001208  0.00    0.53498 -0.01580 | 0.001256  0.00    0.48084 -0.01741
     35  | 0.000632  0.00    0.67786 -0.00695 | 0.000697  0.00    0.61344 -0.01139
     38  | 0.000375  0.00    0.82937 -0.00302 | 0.000466  0.00    0.76656 -0.00494
     41  | 0.000218  0.00    0.96330  0.00310 | 0.000333  0.00    0.91362  0.00113
     44  | 0.000187  0.00    1.09562  0.00897 | 0.000205  0.00    1.06070  0.00705
     47  | 0.000179  0.00    1.23475  0.01463 | 0.000170  0.00    1.21016  0.01300
     50  | 0.000156  0.00    1.38015  0.01984 | 0.000148  0.00    1.36586  0.01860
     53  | 0.000136  0.00    1.52733  0.02431 | 0.000127  0.00    1.52435  0.02359
     56  | 0.000124  0.00    1.66531  0.02754 | 0.000113  0.00    1.67539  0.02737
     59  | 0.000111  0.00    1.78476  0.02954 | 0.000130  0.00    1.81162  0.02956
     62  | 0.000158  0.00    1.87894  0.02971 | 0.000187  0.00    1.92089  0.03061
     65  | 0.000114  0.00    1.94632  0.02874 | 0.000102  0.00    1.99979  0.03006
     68  | 0.000000  0.00    1.82678  0.55172 | 0.000000  0.00    1.90253  0.56891
     71  | 0.000000  0.00    1.62657  0.57362 | 0.000000  0.00    1.73026  0.59633
     74  | 0.000000  0.00    1.39843  0.60402 | 0.000000  0.00    1.50636  0.63228
     77  | 0.000000  0.00    1.12020  0.64789 | 0.000000  0.00    1.21388  0.68149
     80  | 0.000000  0.00    0.78542  0.71446 | 0.000000  0.00    0.85325  0.75446
     83  | 0.000000  0.00    0.41098  0.83903 | 0.000000  0.00    0.44751  0.89109

**The homelessness profile tracks `renter income`, inversely, and it tracks the
SIGN of it.** Over the working ages 26 to 65 the correlation of log homelessness
with each column is:

                        0.95      0.93
    own                    --        --   identically zero, no information
    renter wealth     -0.8876   -0.8817
    renter income     -0.9277   -0.9254

`renter income` wins at both points, but the ranking is not the point -- the two
columns rise together over the working ages and either would fit. What separates
them is the shape. Renter income is NEGATIVE from 26 to 38 and positive from 41
on, and homelessness collapses by a factor of 126 between 26 and 41: it is
0.027525 at 26, where renter income is at its most negative and renter wealth is
exactly 0.00000, and it is flat at one to two parts in ten thousand from 41 on. At
68 and beyond, where renter income steps up to 0.55 and above, homelessness is
exactly zero at every age. `own` is 0.00 at every age at both points, because the
homeownership rate is zero in this economy, so the second column is empty.

The profile is far too steep against the data: `homelessness profile, band 1` in
(e) is 4.64 and 4.45 against an observed 1.28, and band 1 holds 91 per cent of
the model's homeless against an observed 26 per cent. Lowering the impatient
factor from 0.95 to 0.93 barely touches it, which is the same answer IMPATIENCE IS
NOT THE MISSING MECHANISM FOR THE HOMELESSNESS AGE PROFILE reached above, now at
two types.

### (e) EVERY UNTARGETED QUANTITY

    quantity                                    observed  |      0.95        0.93
    mean age of drug users                      45.48000  |  41.397945   42.390222
    users aged 26-34, share                      0.28404  |   0.330875    0.301562
    users aged 35-44, share                      0.25054  |   0.329812    0.314318
    users aged 45-54, share                      0.17768  |   0.207619    0.228333
    users aged 55-64, share                      0.16327  |   0.086334    0.106272
    users aged 65 plus, share                    0.12445  |   0.045361    0.049514
    housing over income, renters                 0.20200  |   0.128328    0.125085
    delta_d child SUD ratio                      2.00000  |   1.016479    1.014560
    wealth share bottom 1 pct                   -0.00225  |   0.000000    0.000000
    wealth share bottom 5 pct                   -0.00422  |   0.000000    0.000000
    wealth share bottom 10 pct                  -0.00446  |   0.000000    0.000000
    income share bottom 1 pct                    0.00009  |   0.000553    0.000519
    income share bottom 5 pct                    0.00288  |   0.002767    0.002596
    income share bottom 10 pct                   0.00924  |   0.005533    0.005193
    delta_h child homelessness ratio             2.10000  |   4.744696    5.282657
    homelessness rate, band 1                    0.00316  |   0.011735    0.011180
    homelessness rate, band 2                    0.00338  |   0.000659    0.000792
    homelessness rate, band 3                    0.00291  |   0.000307    0.000294
    homelessness rate, band 4                    0.00250  |   0.000222    0.000243
    homelessness rate, band 5                    0.00077  |   0.000012    0.000011
    homelessness profile, band 1                 1.28079  |   4.638916    4.447658
    homelessness profile, band 2                 1.36872  |   0.260526    0.315123
    homelessness profile, band 3                 1.17990  |   0.121453    0.117018
    homelessness profile, band 4                 1.01135  |   0.087577    0.096668
    homelessness profile, band 5                 0.31199  |   0.004812    0.004197
    share of the homeless, band 1                0.26000  |   0.907328    0.893768
    share of the homeless, band 2                0.27200  |   0.053945    0.066920
    share of the homeless, band 3                0.21000  |   0.023038    0.022513
    share of the homeless, band 4                0.18400  |   0.014524    0.015831
    share of the homeless, band 5                0.07500  |   0.001164    0.000968
    earnings share, bottom tenth                 0.00990  |   0.012507    0.012507
    earnings share, top tenth                    0.41100  |   0.308662    0.308662
    renters above 30 pct of income               0.40600  |   0.353238    0.342487
    renters above 50 pct of income               0.17500  |   0.339943    0.331238
    tenant contribution rate                     0.31200  |   0.701637    0.691518
    voucher holders, wages main                  0.28000  |   0.471600    0.466618
    participation, with a SUD                    0.65800  |   0.976447    0.971543
    participation, without a SUD                 0.61500  |   0.642404    0.630494
    homeless at treatment admission              0.14500  |   0.000357    0.000550
    SMI alongside SUD at admission               0.43100  |   0.019566    0.023779
    working, homeless in treatment               0.06600  |   0.061681    0.041682
    SUD share of the homeless                    0.21700  |   0.060557    0.113572
    drug deaths, share of deaths                 0.20000  |   0.829068    0.839731
    income of the homeless                       0.19100  |   0.348951    0.313372
    employed share of the homeless               0.46000  |   0.810052    0.777701
    income with a SUD                            0.71100  |   1.655894    1.709808

### PROVISIONAL

**These six moments in this section are PROVISIONAL and are not to be calibrated
against:**

    tau_l      pi_eu      y_u      tau_u      kappa_ued      aleph

An equal-beta validation found the two-pass code disagrees with the one-pass code
on all six. `w_bot` and `beta` agreed to within 1.4 per cent in that test and are
**not** provisional -- which is what makes (b) worth reading at all, and (c)
readable only in the rows outside that list.

Independently of the six, everything in this section inherits two further
qualifications, both stated above: `addiction_scalar_1` was not at its closed value
in either run, and the two histogram invariants fail.

### FOUR THINGS THAT LOOK WRONG AND ARE NOT

    lambda_addiction                     17.98304        deliberate
    addiction_scalar_1                    0.0224532      deliberate as a DEFAULT --
                                                         but see the first subsection:
                                                         0.018421517 was intended
    probability_becoming_unemployed       0.0062406018   deliberate
    kappa_uem (the parameter, not the moment)  28.67112  deliberate

And `MOMENT theta` of -1.0 is an empty-population sentinel rather than a value. It
did not arise here: theta reads 0.361578 and 0.373092 at the two points, so the
population it is computed over was non-empty on both.

## FIXES 8 AND 9 REVERTED. THE ARITHMETIC CONTRADICTED THE AUDIT

The author asked whether any of these fixes would change the output. Checking
that question found that two of mine would have changed it BADLY.

Audit B F4 and F5 argued that `aleph` and `cbar` are aggregates over means, so
both scale with total mass and should be normalised. The STRUCTURE of that
argument is right. The arithmetic says the conclusion is not:

    sum_of_distribution = 51.1     (the life-cycle sum of cohort masses)

    aleph  measured 57.95    target 80       28 per cent off
           after dividing by 51.1 -> 1.13    98.6 per cent off

    cbar   measured 0.0157   target 0.0042
           after dividing by 51.1 -> 0.000307, thirteen times too SMALL

**A moment sitting 28 per cent from its target is not one that is wrong by a
factor of fifty.** The targets were evidently set against the aggregate form.
Both normalisations are reverted, before any point was measured with them.

The audit flagged its own evidence honestly -- "supporting but not decisive" for
F4, and its magnitude check as "consistent with a doubling rather than a
measurement of one". I applied it anyway without checking the magnitude. That is
the third time today reasoning-from-structure has beaten checking-a-number, and
the third time it has been wrong.

**WHAT REMAINS TRUE AND IS NOT FIXED.** At TWO types the ratio does scale with
the number of types, so aleph doubles for a reason that has nothing to do with
the value of life. The right correction there is a division by `mass_passes`,
NOT by the whole mass -- and it needs the equal-beta test to confirm the factor
before it is applied. Recorded in the source at the site.

## ANSWERING THE QUESTION DIRECTLY: WHICH FIXES CHANGE THE OUTPUT

**At ONE beta, almost nothing changes.** Every pooling fix is inert: the loop
runs once, `accumulating_beta_types` is always 0 and
`current_beta_type==number_of_beta_types` is always true. That covers fixes 1-5,
10-12 and 17 and all 187 normalisation sites.

Three DO change one-beta output:

  - **Fix 16, y_u's numerator.** LIVE at one beta and it moves a targeted moment.
    y_u should RISE. Every income-of-a-subgroup ratio moves with it.
  - **Fix 15, the treatment distance.** The calibration loop could not exit on it
    and ran to its iteration cap on every point. Points will now converge, so
    the internally calibrated parameters will land somewhere else -- better, but
    different.
  - **Fix 7, damp_on_flip.** In a calibration loop, parameters documented as
    pinned were drifting. They will now hold.

Two are dead today: fix 13 (the transition is off) and fix 14 (initial guess
only). Two are cosmetic: the band-7 print and a comment.

**At TWO betas, essentially everything changes**, and no earlier two-beta number
survives.

## FIXES 18 AND 19

**18. Two undefined reads in the labour-supply secant.** [Audit F-10] `objective`
declares `MU_1` and `MU_2` `intent(out)` and assigns NEITHER on the
`can_consume_1=0` path, so both are undefined on return. `secant` read them on
exactly that path to set `distance_secant`, which is the `do while` termination
test. Under gfortran the dummies alias the caller's variables, so what was read
was the previous iteration's pair rather than garbage -- which is why it never
showed, and why it is still an undefined read the loop's exit depended on.

Both sites now use `abs(x_0-x_2)`, the bisection's own bracket width, which is
what the SIBLING branch a few lines away already used and is always defined. The
other three call sites guard on `can_consume_1==1` before reading MU; these two
could not, because they are the not-consuming path.

Adjacent: `abs(MU_1-MU_1)`, identically zero, so a warning that the secant left
its loop unconverged could never fire. Now `abs(MU_1-MU_2)`, guarded on
`can_consume_1==1` so both are defined.

**19. A data race in the distribution sweep.** [Audit F-07] `voucher_index_1` was
in the `shared` clause of an `!$omp parallel do default(none)` and WRITTEN inside
the loop, once per iteration, from a quantity that varies with the loop index.
Two threads write it and either may read the other's value -- as the fourth
subscript of `voucher_probabilities` and as an argument to
`calculate_future_voucher_index_and_opportunity`.

Harmless in the benchmark ONLY by arithmetic accident: both
`increased_prob_of_voucher_if_homeless` multipliers are 1, so
`voucher_probabilities` is identical across its fourth index and a raced index
picks the same number. **It becomes live nondeterminism the moment either
multiplier moves off 1 -- line 36622 already carries a commented-out 5.81, so
someone has tried -- or in any Treatment First counterfactual**, where
`voucher_conditional_on_clean` makes index 3 differ from 1 and 2 by the whole
detection and false-positive structure. Now `private`.

Every other temporary in that loop body is a threadprivate module variable.
`voucher_index_1` and `is_addicted_1` were the two exceptions, and `is_addicted_1`
is benign -- a function of an OUTER loop variable, so every thread writes the
same value.

## FIXES 20 AND 21: THE LAST OF THE SHARED-ACCUMULATOR CLASS, AND aleph AT TWO TYPES

**20. Five more variables given a single owner.** [Audit G 12] Thirteen sites.
`mass_by_employment` had FOUR owners, so it reached 5*M where the pooled mass is
2*M -- every welfare-by-employment average halved and
`homeownership_by_employment` at 0.4 times truth. Also
`mass_by_employment_and_age`, `mass_of_owners`, `mass_renters_by_age` and
`total_homeless_1`. First owner in call order keeps each; the rest read it.

**21. aleph's aggregate no longer grows with the number of types.** Divided by
`mass_passes`, NOT by the mass. The distinction is the whole lesson of the
reverted attempt: the target was set against the aggregate form, so dividing by
the mass of 51.1 destroys a moment that is 28 per cent off, while dividing by
`mass_passes` removes only the spurious doubling and leaves every one-type value
untouched -- `mass_passes` is 1 at one type.

## WHAT IS DELIBERATELY NOT FIXED, AND WHY

Audit B F10, F11 and F12 are three targeted moments whose universes do not match
their targets: `kappa_ued` counts retirees on both sides where `pi_eu` two lines
above excludes them, `kappa_uem` counts retirees as employed on a carried index,
and `theta`'s two halves divide by income concepts that differ by a bequest.

**These are NOT two-pass bugs.** They are wrong at one beta in exactly the same
way, and the author's instruction is to get the code running the TWO-BETA model
correctly. Fixing them changes what the moments mean and so changes every
calibrated parameter that answers to them -- a bigger disturbance than the
two-pass work, and one that should be made deliberately rather than in the same
sweep.

Both direction-check favourably, which is recorded here so the work is not
repeated: excluding retirees RAISES `kappa_ued`, which is 0.1247 against a target
of 0.1625, and LOWERS `kappa_uem`, which is 0.3356 against 0.3000. Both move
toward target. `theta`'s direction cannot be checked without the size of the
bequest term, which is not printed.

## b AND lambda_d BRACKETED AT TWO BETAS

Three points were run to bracket `b` (target 0.089) and `lambda_d` (target
0.0368) at two beta types, by cutting `addiction_scalar_1` below the value
used at the last two-type point. **The bracket failed: both targets lie
outside the measured range, and cutting `addiction_scalar_1` moved both
moments further away rather than closer.**

### FIRST, TWO CORRECTIONS TO THE PREMISE

The brief for these runs described the anchor as "`addiction_scalar_1` =
0.018421517, `b` = 0.60145, `lambda_d` = 0.25521, in
`code/points/point_a4e79fb29e.txt`". Two of those three numbers do not
belong to that file.

    quantity              brief said      point_a4e79fb29e.txt actually has
    addiction_scalar_1    0.018421517     0.0224532
    b                     0.60145         0.30072648728203133
    lambda_d              0.25521         0.25521304771452158    (agrees)

`point_a4e79fb29e.txt` is nonetheless the right anchor: its VECTOR differs
from the three run lines in `addiction_scalar_1` and in nothing else.
Corroborating this, `code/B_SWEEP_GRID.txt` held `0.0224532` immediately
before the first of these runs overwrote it.

The 0.018421517 figure belongs to a DIFFERENT file,
`code/points/point_6716556560.txt`, which is `number_of_beta_types=1` with
`discount_factor_impatient` set equal to `discount_factor`. That is the
one-type run in which `b` = 0.0877 and `lambda_d` = 0.0357 were on target.
So the one-type scalar was attributed to the two-type row.

The stated `b` of 0.60145 is exactly twice the file's 0.30073. Whether that
is a transcription doubling or a separate halving bug of the `tau_l` family
was not established here; it is flagged rather than diagnosed.

The correction matters for the design of the sweep. Read as a cut from
0.018421517, the three points are a 1-2% perturbation. Read from the true
anchor of 0.0224532 they are a cut of 19 to 21%, which is what was actually
run. And `b` at the anchor is 3.4 times its target, not 6.8; the "six times
target" description holds for `lambda_d` alone.

### (a) THE FOUR POINTS

All four are `number_of_beta_types=2`, `discount_factor=0.99715`,
`discount_factor_impatient=0.95`, identical in every parameter except
`addiction_scalar_1`.

    addiction_scalar_1        b    lambda_d       y_u     w_bot      beta   point
              0.0178    0.50173     0.38210   0.54561   0.06317   2.79982   f386b7abb8
              0.0180    0.48242     0.36931   0.53108   0.06273   2.80555   6989b023d1
              0.0182    0.38883     0.32509   1.49692   0.07015   2.84741   aabf8dbf95
           0.0224532    0.30073     0.25521   1.57250   0.06876   2.75077   a4e79fb29e  (anchor)

    target               0.089      0.0368     0.740     0.025    3.0-4.5

`beta` is below the 3.0-4.5 band at all four points, by a little (2.75-2.85).
`w_bot` is 2.5 to 2.8 times its target at all four and barely moves.
`y_u` is not monotone and not even close to smooth: it is about 1.5 at
0.0182 and at 0.0224532, but about 0.53 at 0.0180 and 0.0178. It crosses its
own target of 0.740 somewhere between 0.0180 and 0.0182, by falling through
it, not by approaching it.

### (b) NEITHER TARGET IS INSIDE THE MEASURED RANGE

**`b`: NO.** Measured range over the three new points is 0.38883 to 0.50173;
including the anchor it is 0.30073 to 0.50173. The target 0.089 lies BELOW
all four. There is nothing to interpolate between, so no interpolated value
of `addiction_scalar_1` exists.

**`lambda_d`: NO.** Measured range over the three new points is 0.32509 to
0.38210; including the anchor, 0.25521 to 0.38210. The target 0.0368 lies
BELOW all four. Same conclusion.

**Do the two agree?** The question as posed does not arise, because neither
target is bracketed. What can be said is that across the four points in the
table above both `b` and `lambda_d` FALL as `addiction_scalar_1` RISES, so
cutting the scalar, which the sweep did, raises both, and reaching either
target requires moving `addiction_scalar_1` UP from 0.0224532, not down.

That is an endpoint statement, not a global one. The next subsection shows
`b` is NOT monotone once the other two-type points in the repository are
included, so the slope below should be read as the average over this
interval and not as a local derivative.

Extrapolating the anchor-to-0.0182 segment linearly (`b` slope about
-20.71 per unit of `addiction_scalar_1`) puts `b` = 0.089 near
`addiction_scalar_1` = 0.0327. The corresponding `lambda_d` slope, about
-16.43, puts `lambda_d` = 0.0368 near 0.0357. Those disagree by 0.0031,
about 9% of the midpoint 0.0342, so on this evidence `lambda_addiction`
very likely does have to move as well. Both figures are extrapolations well
outside the sampled interval, they assume a linearity the next subsection
contradicts, and they are offered only as a direction to search rather than
as a solution.

### THE RESPONSE IS NON-MONOTONE, WHICH IS THE LARGER PROBLEM

Every two-type point in `code/points` with `discount_factor_impatient=0.95`,
sorted by `addiction_scalar_1`:

    addiction_scalar_1        b    lambda_d   point
              0.0178    0.50173     0.38210   f386b7abb8   (this sweep)
              0.0180    0.48242     0.36931   6989b023d1   (this sweep)
              0.0182    0.38883     0.32509   aabf8dbf95   (this sweep)
          0.01832949    0.76120     0.31901   18da9be82d
         0.018410013    0.76876     0.32084   445884ebe4
           0.0224532    0.30073     0.25521   a4e79fb29e

`b` is not monotone. It nearly DOUBLES between 0.0182 and 0.01832949, from
0.38883 to 0.76120, then falls to 0.30073 by 0.0224532. A move of 0.00013 in
the scalar changes `b` by 0.37. `lambda_d` is closer to monotone but inverts
between 0.01832949 and 0.018410013.

A jump of that size across an interval that narrow is not a smooth
calibration response. Either the solver is landing in different equilibria
across a knife edge in this region, or something is not converged. Fitting
`b` by moving `addiction_scalar_1` alone is not going to work while this
holds, and a bisection would be actively misleading here. This should be
understood before more points are spent on the same one-dimensional search.

### (c) FULL MOMENT TABLE, BEST OF THE THREE, WORST GAP FIRST

Best is taken as closest on `b` and `lambda_d`, the two targets this sweep
exists to hit: that is `addiction_scalar_1` = 0.0182, point `aabf8dbf95`,
which is nearest on both. Note it is NOT the best on overall mean relative
gap; 0.0180 is, because `y_u` happens to sit near its target there.

Gap is |model - target| / |target|.

    moment     description                          model        target   rel gap
    cbar       food stamps / labour income       0.052368      0.004200   1146.9%
    lambda_d   disorder rate                     0.325092      0.036800    783.4%
    b          total drug users                  0.388829      0.089000    336.9%
    tau_u      treatment take up                 0.958174      0.245000    291.1%
    w_bot      net worth share, bottom half      0.070151      0.025000    180.6%
    theta      drug spending share               0.363128      0.162000    124.2%
    y_u        income of drug users              1.496925      0.740000    102.3%
    pi_V       eligibles with a voucher          0.094311      0.266000     64.5%
    tau_l      average labour income tax         0.089537      0.224000     60.0%
    aleph      value of life / income          121.403798     80.000000     51.8%
    lambda_m   SMI share of the homeless         0.123082      0.250000     50.8%
    gamma      housing over expenditure          0.180316      0.268000     32.7%
    h_3        share in the largest unit         0.430433      0.626723     31.3%
    pi_eu      unemployment rate                 0.063583      0.048500     31.1%
    h_2        above half of spending            0.072078      0.101000     28.6%
    h_1        homelessness rate                 0.004594      0.003990     15.1%
    mu_H       recovery housed / homeless        1.271251      1.473214     13.7%
    kappa_ued  unemployment given SUD            0.140376      0.162500     13.6%
    beta       wealth over output                2.847407      3.000000      5.1%
    sigma_y    bottom half earnings share        0.169050      0.172000      1.7%
    omega_l    labour supply / total hours       0.394667      0.400000      1.3%
    kappa_uem  employment given SMI              0.303255      0.300000      1.1%
    p_m        SMI population share              0.052825      0.052413      0.8%

`tau_l` reads half its true value in a two-type run and is not a real gap;
see the section above on `govt_revenues_calc`. Doubling it to 0.179 leaves a
20% gap rather than 60%.

`theta` is a real number here (0.363), not the -1.0 empty-population
sentinel. At `addiction_scalar_1` = 0.0180 and 0.0178 it IS -1.0, so the
drug-spending population is empty at those two points and `theta` should be
ignored there. That the sentinel appears at two of the three points is worth
noting on its own.

`cbar` is the worst gap in THIS table, at 1147%, but it is not stably so.
Across the three points it reads 0.052368, 0.002803 and 0.000040 against a
target of 0.004200 -- a factor of about 1300 between the largest and the
smallest, produced by a 2% change in `addiction_scalar_1`. It is worst-in-
table at 0.0182, twelfth at 0.0180 and eighth at 0.0178. This is the same
instability as the `b` jump documented above, in a second moment, and it is
further evidence that this region is not being solved smoothly.

### (d) DIAG age, BEST OF THE THREE (aabf8dbf95)

    age   homeless   renter wealth   renter income   own
     26   0.080644         0.00000        -0.03536   0.0
     29   0.005809         0.34924        -0.02070   0.0
     32   0.002246         0.58502        -0.01307   0.0
     35   0.001234         0.73289        -0.00650   0.0
     38   0.000799         0.87726        -0.00014   0.0
     41   0.000590         1.01287         0.00597   0.0
     44   0.000388         1.15509         0.01229   0.0
     47   0.000309         1.30872         0.01852   0.0
     50   0.000289         1.47356         0.02463   0.0
     53   0.000284         1.65218         0.03044   0.0
     56   0.000275         1.83434         0.03542   0.0
     59   0.000463         2.00524         0.03878   0.0
     62   0.000399         2.14609         0.04111   0.0
     65   0.000488         2.26152         0.04187   0.0
     68   0.000000         2.16613         0.62261   0.0
     71   0.000000         1.97106         0.65787   0.0
     74   0.000000         1.72899         0.70496   0.0
     77   0.000000         1.41005         0.77099   0.0
     80   0.000000         1.02267         0.87777   0.0
     83   0.000000         0.63115         1.13872   0.0

**Which column the homelessness profile tracks.** It tracks `renter wealth`,
inversely, and the mechanism is visible in the first two rows: homelessness
is at its maximum of 0.0806 at exactly the age where renter wealth is
exactly 0.00000, and falls fourteen-fold in one three-year step as wealth
reaches 0.349. It is the mirror image of the wealth accumulation profile.

The correlations, over the fourteen ages where homelessness is non-zero and
in logs, because the profile spans two orders of magnitude:

    corr(log homeless, renter income) = -0.845
    corr(log homeless, renter wealth) = -0.789
    corr(log homeless, age)           = -0.749

Renter income is marginally the tighter fit, but the two regressors rise
together monotonically over ages 26 to 65, so this profile cannot cleanly
separate them; the zero-wealth spike at entry is the discriminating evidence
and it points at wealth. Neither explains the mild uptick from age 56 to 65,
during which homelessness rises while both wealth and income are still
rising.

Two further things in this block:

  - `own` is identically 0.0 at every age. There is no homeownership
    anywhere in the model at this point, consistent with the
    `homeownership rate` invariant reading 0.0000000000.
  - homelessness is exactly 0.000000 from age 68 on, where renter income
    jumps fifteen-fold at retirement.

### (e) INVARIANTS -- PRESENT, AND NOT ALL PASS

These three runs are the first points to carry an `INVARIANTS` block. **They
do not all pass. Two of eleven FAIL at every one of the three points.**

    invariant                                        0.0182      0.0180      0.0178
    income histogram holds whole distribution   FAIL 1.19002  FAIL 1.18647  FAIL 1.18457
    wealth histogram holds whole distribution   FAIL 1.19002  FAIL 1.18647  FAIL 1.18457
    wealth histogram holds whole of net worth   PASS 1.00000  PASS 1.00000  PASS 1.00000
    rental market clears, demand over supply    PASS 1.00000  PASS 1.00000  PASS 1.00000
    homelessness rate                           PASS 0.00459  PASS 0.00463  PASS 0.00648
    drug users                                  PASS 0.38883  PASS 0.48242  PASS 0.50173
    disorder rate                               PASS 0.32509  PASS 0.36931  PASS 0.38210
    SMI population share                        PASS 0.05282  PASS 0.05300  PASS 0.05330
    unemployment rate                           PASS 0.06358  PASS 0.09474  PASS 0.09623
    homeownership rate                          PASS 0.00000  PASS 0.00000  PASS 0.00000
    the five age bands hold all of the homeless PASS 1.00000  PASS 1.00000  PASS 1.00000

The two failures are the same number to eight digits within each run, and
they are the two histograms that are supposed to hold the WHOLE
distribution. The net worth histogram, which is a different object, passes at
exactly 1.0, as do the rental market and the age-band partition.

An overshoot of about 1.19 on two independent histograms, with the
distribution-wide ones failing and the net-worth one passing, has the shape
of the pooled-distribution accumulation problem across beta types already
documented above for `tau_l` -- but the opposite sign, since `tau_l`
UNDERCOUNTS by half and these OVERCOUNT by a fifth. The factor is not
constant across the three points (1.19002, 1.18647, 1.18457), so it is not a
clean count of types; it drifts with `addiction_scalar_1`. That drift argues
against a pure double-counting bug and for something that depends on the
distribution itself.

This has NOT been diagnosed. It is recorded here because it is new
information and because the histograms are inputs to `sigma_y` and `w_bot`,
both of which are reported as passing moments above. `w_bot` being 2.5 to 2.8
times its target at all four points, and immovable across a 19% change in
`addiction_scalar_1`, is consistent with a histogram that does not sum to
one, and should be re-checked once this is understood.

### WHAT THIS SWEEP ESTABLISHES

  1. Cutting `addiction_scalar_1` from 0.0224532 to 0.0178 does not bracket
     `b` or `lambda_d`. It moves both further from target. The search
     direction was backwards.
  2. Both targets lie below the entire measured range, so no interpolation
     is available and none is reported.
  3. `b` responds non-monotonically to `addiction_scalar_1` in this region,
     with a near-doubling across an interval of 0.00013. A one-dimensional
     search on this parameter is not viable until that is explained.
  4. The `INVARIANTS` block works and is already earning its place: two
     checks fail at every point, on the distribution histograms.

## THE INVARIANTS PAID FOR THEMSELVES, AND FOUR MORE FIXES CAME OUT OF IT

The `INVARIANTS` block was added on the argument that a number which must be 1.0
and is not finds a class of bug that reading 38,000 lines does not. Its first
three points reported two FAILs, and following them produced four fixes. What
follows is what each one was, how it was found, and what it does and does not
move.

### 1. The pooled mass was a pass count, not a mass

The two histogram checks read 1.19002, 1.18647 and 1.18457 at three points
differing only in `addiction_scalar_1`. Every chain routine rebuilt the mass
from `distribution_stationary`, which holds only the type just solved, and
multiplied by `mass_passes`. That is exact if and only if the two
discount-factor types weigh the same, and they do not: newborn cohorts are
equal but survival is not, so the type that is homeless and addicted more ends
the life cycle lighter. **A miscount of types would have been a constant, 2.0 or
0.5. A number that drifts with a drug parameter is a survival gap.**

Nine sites now accumulate the real thing one pass at a time.
`stationary_equilibrium_statistics` runs first in each pass and owns three
accumulators -- the total, the retirees, and each type's own mass -- and the
five later routines read the total instead of rebuilding it.

**What this moves.** `w_bot`, and in the wrong direction. The old denominator was
`2 * m_impatient` where the truth is `m_patient + m_impatient = 2.38 *
m_impatient`, so `percentile_1 * sum_of_distribution` walked only to the 42nd
percentile of the pooled mass and reported the bottom 42 per cent's share of
wealth under the name of the bottom half's. The corrected walk goes further up
the distribution and collects more, so `w_bot` -- already 2.2 to 3.4 times its
target of 0.025 at every two-type point -- **gets larger, not smaller**. That is
the honest consequence of a correct denominator and it is not a reason to keep
the wrong one.

`aleph`'s divisor was the same pass count and is now the measured ratio of
pooled mass to the first type's, which is exactly one at a single type.

**Nothing at one discount-factor type moves**, at any of the nine sites: one
pass, factor one. And the equal-beta test could never have caught this, because
equal betas make the masses equal by construction.

### 2. A reset was disabled on a variable no other routine can own

`total_homeless_1` is declared a local of `govt_revenues_calc` and, separately, a
local of `stationary_equilibrium_statistics`. They are two variables that share
a name. The one-owner rule applied in the previous round -- the first routine in
call order keeps the counter and the rest read it -- holds for module variables
and does not hold for these. Disabling the reset did not hand ownership to the
earlier routine; it left this routine's own local undefined on entry, and the
eight homeless averages normalised by it were divided by whatever the stack held.

It printed plainly and went unread for a day. `point_03ac59f09e` reports
`homeless by choice, share of the homeless` at **1.6552**, and a share of the
homeless cannot exceed one.

**What this moves.** Nothing targeted. Every quantity normalised by it appears
on `DIAG` lines only: the average income, after-tax income, tax rate and assets
of the homeless, the addicted-and-homeless averages, the two by-choice shares,
and the rent-to-income distribution of the homeless. **The 94-per-cent
"homeless by choice" figure reported earlier came off this divisor and should
be treated as unmeasured until a point on the fixed source reports it.**

Five range invariants now cover these, so the next one is caught by the run that
makes it.

### 3. Thirteen cross-pass counters had no storage that survives the call

Thirteen locals are reset only when `accumulating_beta_types` is zero and added
to on every pass, so that they hold both types by the time they are divisors.
That is the right shape and it was missing its one requirement: **a local
without `save` does not survive from one call to the next.** On the second pass
the routine is entered fresh, the reset is skipped because the pass is not the
first, and the accumulation lands on whatever the stack holds.

It has been working by accident -- same call site, same order, frame usually
reused -- which is a property of this build and not a guarantee. `save` makes it
one. They stay local rather than moving to module scope on purpose:
`total_homeless_1` is the name of two different locals counting the same
population in two separate loops, and merging them would put two counts in one
divisor.

**What this moves.** Probably nothing, and that is the point: it converts an
accident into a rule. None of the six routines contains an OpenMP directive and
none is recursive, so static storage introduces no sharing.

### 4. Nine more in-place normalisations outside the last-pass guard

The same fault as the 187 already gated, found by matching `X = X / ...` in the
chain routines against the list of variables reset under
`accumulating_beta_types==0` rather than by reading. `average_rent_by_age`,
the two owner-occupied unit size averages' companions, the two grid-adequacy
corners, `model_LTV_by_age_group`, the three MID shares, and the two
origination LTVs. None is a targeted moment.

### WHAT WAS CHECKED AND LEFT ALONE

  - The other nine disabled resets are all on module-scope variables
    (`mass_of_owners`, `mass_by_employment`, `model_fraction_homeless`,
    `mass_renters_by_age`, `mass_by_age`, `mass_by_employment_and_age`), so the
    one-owner rule is sound for them. For each, exactly one accumulation site is
    live and the duplicates are commented out, and in every case the live site
    is in a routine that runs before every reader.
  - `fraction_with_drug_spending_relative_to_average` and
    `total_experimenters_1` are reset every pass and normalised every pass, so
    the light-user threshold at 29211 is built from the last type alone. It is
    left as it is because **its consumer is commented out and
    `distance_drug_threshold` is set to zero**: the computation is dead. Pooling
    it would change a number nothing reads.
  - `mass_of_quintile` is reset every pass but divided by the pooled
    `sum_of_distribution` at the two file-writing sites, so the quintile masses
    in the written outputs are short by a type. Output files only; recorded, not
    fixed.
  - The omega counterfactual in `print_all_moments` re-solves and re-measures
    with ONE type while the benchmark it is compared against has two. The mass
    fix stops it doubling a one-type mass, but the comparison is still one type
    against two. Recorded for the author; it is a design question, not a defect.

### THE STANDING RULE THIS COST

Two of these four -- the disabled reset and the missing `save` -- are faults in
work done EARLIER THE SAME DAY to fix the pooling. The pattern is the same both
times: a rule about ownership was applied to a name without checking the name's
scope. **Before disabling a reset or moving a counter's ownership, check whether
the variable is declared at module level or inside the routine.** The two look
identical at the call site and behave completely differently.

## WHAT THE POOLED-MASS FIX SHOULD MOVE, AS A CHECKLIST AND NOT AS A TABLE

The standing rule is that a mechanism is not a measurement and a table of
corrected values derived from reasoning about a bug is not to be published. So
what follows is a list of PREDICTIONS with the factor attached, to be checked
against the first point measured on the fixed source and then thrown away.

At two types the old denominator was `2 * m_impatient`; the truth is
`m_patient + m_impatient`, and the measured histogram ratio puts that at
`2.38 * m_impatient`. So every moment divided by `sum_of_distribution` was
reading a denominator **1.19 times too small** and is expected to FALL by that
factor; every moment divided by one of those is expected to RISE by it.

  falls by ~1.19   `b`, total drug users
                   `lambda_d`, the disorder rate
                   `model_addicted`, `model_exprimenters`
                   `model_average_income` and `model_average_income_plus_assets`
                   `average_welfare_of_all_cohorts`
  rises by ~1.19   anything divided by `model_average_income` -- `y_u` above all
  rises            `w_bot`, but not by a clean factor: the percentile walk
                   stopped at the 42nd percentile and now goes to the 50th, so
                   the change is whatever wealth sits in that slice

  unaffected       `gamma` and `h_2`, whose denominator is
                   `sum_of_distribution_not_be_homeless` -- that one already
                   accumulated across passes correctly and was never scaled
                   `h_1`, normalised on `model_sum_of_lowest_productivities`
                   everything at ONE discount-factor type, at every site

If the first fixed point does not show `b` and `lambda_d` about a fifth lower
and `y_u` about a fifth higher, the diagnosis is wrong and this section is the
record of what was expected.

## WHY NOTHING LANDED BETWEEN 21:00 AND 22:50 ON 31 AUGUST

Three worker sessions were launched at 20:43, 21:00 and 21:01 and none of them
produced a point. The cause was not a stalled worker, a permission prompt or a
bad batch file: **the account hit its five-hour session limit at about 21:33**
and every session was rejected with "You've hit your session limit, resets
10:50pm UTC". `VALIDATE6` and `DRUGUP` both died there; `BETALOW` never got past
installing gfortran.

Two things follow for the engine.

  1. A worker container has to install gfortran before it can build, which
     costs it fifteen minutes of a rate-limited budget. **The coordinator's own
     container already has gfortran.** Running a point here, in the background,
     costs one Bash call and no session at all. When the fleet is rate limited
     -- or whenever a single point is what is wanted rather than a fan-out --
     run it here.
  2. "Nothing landed in two firings" is in the engine prompt as the signal that
     the fleet has drained, and the remedy given is to respawn. That remedy is
     exactly wrong under a rate limit: respawning burns the budget that is
     already exhausted. **Check `rate_limit_info.status` on a failed session
     before respawning it.** A `rejected` status with a `resetsAt` is a clock to
     wait out, not a fleet to rebuild.

## THE SEVENTEENFOLD CLUSTER IS CLOSED, AND THE SEVENTEEN IS THE WORKING POPULATION

`VALIDATION_RESULT_5.md`, measured on `50e121d`, reported three quantities off
by almost exactly the same factor in the two-type run: `aleph` at 17.305, `cbar`
at 17.051 and `DIAG treatment price / average labour income` at 17.274. All
three divide by `model_average_labour_income`, so one fault produces three
symptoms.

The third one settles it without any modelling argument, because its numerator
is a pure input. `money_cost_of_treatment` is 0.0600702 in both runs, so

    one type   0.0600702 / 0.1006946494  =  0.59656
    two types  0.0600702 / 0.005829414   = 10.30460      ratio 17.274

**`model_average_labour_income` really was 17.27 times larger at two types.**

The mechanism follows from the arithmetic. If the in-place division is gated to
the FIRST pass instead of the last, then pass one divides and leaves the average,
and pass two adds the second type's RAW SUM on top of it:

    10.30460 - 0.59656 = 9.70804  = the second type's total labour income
    9.70804 / 0.59656  = 16.27    = the number of workers behind that average

Sixteen and a quarter workers on a population of about fifty-two is a
participation rate of 31 per cent, which is what this life cycle gives once
retirees and non-participants are taken out, and it is consistent with
`omega_l` at 0.40. Nothing else in the model is near seventeen.

**It is already fixed.** The division is now gated on
`current_beta_type==number_of_beta_types` and nothing further is needed. The
confirming measurement is cheap and specific: on a fixed-source equal-beta run,
`DIAG treatment price / average labour income` must read the same number in both
lines. That is the check to make, rather than re-reading the code.

## WHAT THE SECOND BETA BUYS AND WHAT IT COSTS, AT THE TWO ANCHORS

The author asked directly whether the two-beta runs gave a better bottom-half
net worth share. They do, and by a lot. The comparison is between the best
one-type point, `point_6716556560` (`MODEL dc8abdfbce`), and the two-type
anchor `point_a4e79fb29e` (`MODEL c7cb2b24b6`) with its impatient discount
factor at 0.95, and the three `TWOBETA_CAL` points around it.

    moment      target       one beta        two betas (0.93 / 0.95 / 0.97)
    w_bot        0.025       0.15623         0.05446  0.06974  0.08434
    b            0.089       0.08768         0.4243   0.7688   0.3614
    lambda_d     0.0368      0.035697        0.3652   0.3208   0.2743
    beta         3.0-4.5     3.9615          2.827    2.864    2.933
    tau_u        0.245       0.94715         0.9671   0.9595   0.9559
    h_1          0.00399     0.0041110       0.004644 0.009014 0.003812
    h_2          0.101       0.051295        0.07438  0.0721   0.06646
    aleph        80          58.204          119.2    121.7    5.064
    y_u          0.74        0.36423         1.6056   1.4973   0.54379
    pi_eu        0.0485      0.053095        0.06712  0.06413  0.08686
    tau_l        0.224       0.23873         0.083067 0.089797 0.241

**THE BUY. `w_bot` goes from 6.2 times its target to 2.2.** That is a factor of
2.9, and it is the second beta rather than anything else: `w_bot` barely moved
across a 19 per cent change in `addiction_scalar_1` in the DRUG2B sweep
(0.06273 to 0.07015), so the parameter difference between the two anchors cannot
account for it. `h_2` also improves, from 49 per cent short to 26 to 34 short.

**THE COST is the drug block, and it is the author's own diagnosis.** `b` and
`lambda_d` are both essentially ON TARGET at one beta -- 1.5 and 3.0 per cent
short -- and both blow out to three to nine times target at two. That is the
"too many users and too many SUD" the author named. It is a re-calibration
problem rather than a defect: `addiction_scalar_1` moves both, in the right
direction, and `DRUG_UP.txt` is the bracket for it. `beta` also falls from 3.96,
comfortably inside its band, to 2.75-2.93, just below it.

**WHAT THE SECOND BETA IS NOT RESPONSIBLE FOR.** Two of the largest gaps in the
whole table are the same size at one beta as at two, so nothing about the
two-type model caused them and nothing about it will fix them:

  - `tau_u`, treatment take-up, is 0.947 at one beta against a target of 0.245.
    That is +287 per cent, and at two betas it is +290. **It is at a corner in
    both.** Almost everyone who could take treatment takes it.
  - `aleph` is 27 per cent short at one beta.
  - `y_u` is 51 per cent short at one beta and above target at two, so the
    second beta moves it through its target rather than toward or away.

TWO CAVEATS ON THIS TABLE, both real. The two anchors were measured on DIFFERENT
BUILDS (`dc8abdfbce` against `c7cb2b24b6`) and differ in `addiction_scalar_1`
as well as in the two beta settings. And the `aleph`, `cbar` and `tau_l` columns
of the two-beta rows straddle a source change, as `TWOBETA_CAL_RESULT.md`
records. The `w_bot` conclusion survives both caveats because of its size; the
smaller rows should be re-measured on one build before they are quoted.

## A POINT RAN ON A STALE BINARY, AND THE ARCHIVE'S MODEL STAMPS ARE ONLY AS GOOD AS THE BUILD TEST

The first point launched in the coordinator's own container failed its handover
assertion with six names unrecognised, among them `number_of_beta_types` and
`discount_factor_impatient`. The names are all present in the source's
`PARAM_HANDOVER` select case. The binary was the problem: `hftf` was dated 28
seconds after the source, and a 38,000 line `-O3` build takes twenty five
minutes, so it was not built from it. A `supervise_calibration.py` running in
this checkout had been killed a minute earlier and left it behind.

`run_one_point.sh` tested freshness with `source -nt hftf`. That test passes for
any binary that merely wins on mtime, whatever it was built from.

**The dangerous case is not the one that happened.** This binary predated six
handover names, so the assertion caught it and nothing was archived. A binary
one commit behind would have had every name, passed the assertion, solved, and
been archived under `MODEL_HASH` -- which `run_one_point.sh` computes from the
SOURCE while the moments come from the BINARY. That is a point stamped with a
model it was never measured on, and nothing downstream can tell.

The test is now on content: `hftf.srcmd5` records the md5 of the source the
binary was built from, written only after a build that succeeded, and a binary
with no stamp or a disagreeing one is deleted and rebuilt.

**WHAT THIS MEANS FOR POINTS ALREADY IN THE ARCHIVE.** It is not possible to
tell from a point file which binary produced it, so this cannot be audited
retrospectively. Two things bound the exposure and neither eliminates it:

  - Any point run on a binary predating the two-type commit would have failed
    the handover assertion loudly, as this one did, and would not be in the
    archive at all.
  - A point run on a stale binary from WITHIN the two-type era is silent, and
    the supervisor was in this checkout for an unknown period.

The practical consequence is a reason to prefer FRESH measurements over archived
ones whenever a conclusion turns on a small difference between points, and to
treat cross-point comparisons that straddle a source change as indicative --
which `TWOBETA_CAL_RESULT.md` already concluded on independent grounds.

## THE AGE PROFILE AND THE UNEMPLOYED, AT THE ANCHORS, AND ONE DIAGNOSTIC THAT IS WRONG

### (a) THE SHARE OF THE HOMELESS BY AGE BAND

    point             betas  imp     25-34    35-44    45-54    55-64      65+
    6716556560          1    --     0.9803   0.0130   0.0033   0.0031   0.0003
    f5d32f8765          2    0.93   0.9083   0.0521   0.0192   0.0178   0.0026
    445884ebe4          2    0.95   0.9129   0.0499   0.0178   0.0174   0.0020
    b1c5d0df00          2    0.97   0.9370   0.0349   0.0135   0.0133   0.0011
    a4e79fb29e          2    0.95   0.9073   0.0539   0.0230   0.0145   0.0012
    HUD                            0.2600   0.2720   0.2100   0.1840   0.0750

The second beta moves band one from 0.980 to 0.907-0.937 and roughly quadruples
every older band. **That is a real move in the right direction and it is
nowhere near enough.** The gap that has to close is 0.91 against 0.26.

### (b) THE HOMELESS ARE EMPLOYED, WHICH IS THE SAME PROBLEM SEEN SIDEWAYS

    point             betas  imp    employed share of the homeless
    6716556560          1    --                 0.9807
    f5d32f8765          2    0.93               0.9153
    445884ebe4          2    0.95               0.9252
    b1c5d0df00          2    0.97               0.9766
    a4e79fb29e          2    0.95               0.8101
    data                                        0.4600

So between 8 and 19 per cent of the model's homeless are unemployed against 54
per cent in the data. The second beta improves this too, and by about the same
disappointing margin as the age profile.

`model_fraction_of_unemployed_homeless` -- the homelessness rate AMONG the
unemployed, which is the other direction of the same conditional -- is
accumulated and normalised in the model and **never printed**. It cannot be read
off any point in the archive. A print is owed here; it is held until the kappa
sweep finishes so the four points stay on one build.

What CAN be derived without it is the risk ratio, because the working-age mass
cancels:

    P(homeless | unemployed) / P(homeless | working age)
      = (1 - employed share of the homeless) / pi_eu

    6716556560  1 beta        0.363
    f5d32f8765  2 betas 0.93  1.262
    445884ebe4  2 betas 0.95  1.167
    b1c5d0df00  2 betas 0.97  0.270
    a4e79fb29e  2 betas 0.95  3.265

**This is too unstable to use.** It runs from 0.27 to 3.27 across four two-beta
points, and the five points sit on five different builds. Its one robust feature
is that it is nowhere near large: unemployment is not the route into
homelessness in this model, at either number of betas. The employed shares above
say the same thing from printed numbers, so prefer them.

### (c) NOBODY OWNS A HOME, AT EITHER NUMBER OF BETAS

`own` is exactly 0.00000 at all twenty printed ages in all five points, and the
`homeownership rate` invariant reads 0.0000000000. The model has a full
ownership sector -- mass_of_owners, mortgages, LTV at origination, the mortgage
interest deduction -- and it is empty.

This is NOT flagged as a defect, because it may be the intended configuration of
this generation. It is recorded because it settles what the age profile can be
about: **there is no tenure margin.** Every household is a renter, so the only
choice is renting versus the street, and homelessness by age can only be a story
about what a renter of that age can afford.

And it is: homelessness by age tracks renter wealth almost exactly at 445884ebe4.

    age        26      29      32      35      41      47      53      59      65
    homeless 0.0782  0.0049  0.0020  0.0011  0.0006  0.0003  0.0003  0.0005  0.0005
    wealth   0.000   0.349   0.582   0.731   1.013   1.308   1.646   1.987   2.226

That is a buffer-stock story, not a preference story. The young are homeless
because they hold nothing, and the drop from 7.8 per cent to 0.5 per cent
happens over the three years in which renter wealth goes from zero to 0.35.

### (d) THE RENTER INCOME COLUMN IN THAT BLOCK IS WRONG. DO NOT READ IT.

The same `DIAG age` block prints `renter income` as NEGATIVE from age 26 to 38,
which would have been the obvious explanation for everything in (c) and would
have been wrong.

`income_by_age_renter` computes, for an employed renter,

    gross - max(gross - personal_exemption, 0)**curvature_of_labor_income_taxes

while the budget constraint the household actually faces computes

    taxable  = max(gross - exemption - deduction, 0)
    tax_paid = max(taxable - (rate + increase) * taxable**curvature, 0)
    net      = gross - tax_paid

Three differences, and the first is fatal: **the diagnostic omits
`labor_income_tax_rate` entirely**, so it subtracts `taxable**curvature` where
the model subtracts `taxable - rate*taxable**curvature`. With the rate at 0.752
and the curvature at 0.85, a taxable income of 0.04 pays ZERO tax in the model
(0.04 - 0.752*0.0655 is negative, and the outer max floors it) and pays 0.0655
in the diagnostic, which is more than the whole income. It also drops the
deduction and the floor.

So the young do not have negative income. The diagnostic does.
`income_by_age_renter` is read by nothing except this print, so the fix moves no
moment; it is held until the kappa sweep finishes so its four points stay on one
build.

## WHY THE YOUNG ARE ALL THE HOMELESS AND WHY THE HOMELESS ARE ALL EMPLOYED

Both questions have one answer: **the model has almost no route ONTO the street
except choosing to go there, and the household's asset position is a sufficient
statistic for that choice.** Everything else follows.

### (a) THE EMPLOYMENT PUZZLE IS A HARD-CODED 0.2, AND THE ARITHMETIC CLOSES

The only link from homelessness to the labour market is
`increased_prob_if_homeless`, at line 26961:

    real(8), parameter :: increased_prob_if_homeless=0.2

The homeless lose a job at `(1+x)` times the housed rate and find one at
`1/(1+x)` times it, so the ratio of separation to job finding scales by
`(1+x)**2`. A group whose odds ratio is multiplied by `k` has a steady-state
employment rate of `1/(1+k*(s/f))`, and at the `pi_eu` target of 0.0485 the
housed ratio `s/f` is 0.05097. So:

    x        k=(1+x)^2     employed share of the homeless
    0.0        1.00              0.9515
    0.2        1.44              0.9316      <- what the model ships
    1.0        4.00              0.8306
    2.0        9.00              0.6855
    3.0       16.00              0.5508
    3.8       23.04              0.4599      <- the data's 0.46
    5.0       36.00              0.3527

**The measured employed share at `point_445884ebe4` is 0.9252 against 0.9316
predicted by this formula.** Within seven parts in a thousand, on a formula that
uses only `pi_eu` and the one parameter. That is not a coincidence and it is not
selection: the composition of the homeless is essentially the mechanical
steady state of a 20 per cent penalty.

**To hit the data, `increased_prob_if_homeless` has to be about 3.8, not 0.2 --
a factor of nineteen.** It is a `parameter`, a compile-time constant, so it is
not in `PARAM_HANDOVER`, is not calibrated, and cannot be moved by a batch line.

**THIS IS A SCOPE DECISION AND IT IS THE AUTHOR'S.** Turning a hard-coded
constant into a calibrated parameter changes what the model is, and the value it
would need is large enough that its effect on `h_1`, `pi_eu` and the whole drug
block has to be measured rather than assumed. It is written up here and NOT
changed.

### (b) THE AGE PUZZLE IS THE SAME FACT

Three separate routes should put a household who is not young onto the street,
and every one of them is at roughly half its target or worse at
`point_445884ebe4`:

    route                                    model    data     ratio
    employed share of the homeless          0.9252   0.4600     2.01
    SUD share of the homeless               0.0664   0.2170     0.31
    SMI share of the homeless (lambda_m)    0.1297   0.2500     0.52
    income of the homeless                  0.4503   0.1910     2.36

The model's homeless are too employed, too sober, too well, and **two and a
third times too rich**. Those are four different measurements of one thing:
nobody in this model is ever put on the street by something happening to them.

What is left is the choice, and the choice is made on wealth. The homelessness
penalty is a flow utility loss with NO age gradient --
`housing_size(lowest_housing_grid_point) = housing_size(0)*size_homelessness`,
one number for every household -- while the gain, the rent saved, is an absolute
amount whose utility value falls as consumption rises. So homelessness is chosen
by whoever has the highest marginal utility of consumption, which is whoever has
the least wealth, which is whoever is youngest. The profile is the inverse of the
age profile of wealth, and the numbers say exactly that:

    age        26      29      32      35      41      47      53      59      65
    homeless 0.0782  0.0049  0.0020  0.0011  0.0006  0.0003  0.0003  0.0005  0.0005
    wealth   0.000   0.349   0.582   0.731   1.013   1.308   1.646   1.987   2.226

The whole collapse -- a factor of sixteen -- happens over the three years in
which renter wealth goes from exactly zero to 0.35. Age 26 is not special
because of age. It is special because it is the only cohort with no assets.

**And the model already contains the second population, in miniature.** The SUD
share of the homeless BY BAND at the same point:

    band            25-34   35-44   45-54   55-64     65+
    SUD share      0.0215  0.2672  0.2305  0.1756  0.3594

The young homeless are 2 per cent addicted and the older homeless are 18 to 36
per cent addicted. So there ARE two distinct homeless populations here: a large
young group who choose the street to build a buffer, and a small older group
driven there by the disorder. **Matching the HUD profile means growing the
second, not shrinking the first**, and the instruments for that are the three
rows in the table above, not `size_homelessness`.

### (c) WHAT THIS RULES OUT

  - It is NOT the mortality gradient. Measured earlier: weighted by discounted
    remaining life the deterrent runs 1.00, 1.37, 1.57, 1.79 from 26 to 58,
    nearly flat, and making the excess death risk flat in age was tried and
    reverted because it did not move the profile.
  - It is NOT tenure. Nobody owns a home at any age in any point, so there is no
    owner-versus-renter margin to explain anything.
  - It is NOT that young renters cannot pay. The renter-income column that said
    so was the broken diagnostic, now repaired.
  - It is NOT the second beta's doing. One beta puts 0.980 in band one and two
    betas 0.907. The second beta helps and is nowhere near sufficient, which is
    what should be expected if the binding constraint is the missing route in
    rather than the strength of the savings motive.

## HOW SUD AND SMI EACH REACH HOMELESSNESS, AND THE CHANNEL NEITHER OF THEM USES

The author asked whether the unemployment rate of those with a disorder is being
used to match their share of the homeless. It is not, for either disorder. Each
one's labour market moment has its own instrument and its own data target:

    moment                          target    model    instrument
    kappa_ued unemployment | SUD    0.1625    0.1423   multiple_of_probabilities_
                                                       of_employment_if_addicted
    SUD share of the homeless       0.2170    0.0664   rho_d          (new)
    kappa_uem employment | SMI      0.3000    0.2999   kappa_uem
    lambda_m SMI share of homeless  0.2500    0.1297   lambda_m

**But the two disorders reach homelessness by different mechanisms, and that is
worth being deliberate about rather than inheriting.**

  - SMI reaches it through the STOCK. The `lambda_m` parameter is the RECOVERY
    rate from SMI, so slowing the exit leaves more SMI households alive in the
    state and more of them turn up among the homeless.
  - SUD now reaches it through IMPOVERISHMENT. `rho_d` cuts the wage of a
    household with the disorder so it runs its assets down and ends on the
    street.

Neither is wrong, but they are not the same kind of instrument and they will not
respond alike. In particular `lambda_m` cannot help the AGE profile, for the
reason recorded above -- SMI onset and prevalence both fall steeply with age in
the model's own data file -- while `rho_d` should, because the SUD stock
accumulates with age where onset does not.

### THE CHANNEL THAT DOES NOT EXIST, AND WHICH TODAY'S TWO CHANGES DO NOT ADD

`kappa_ued` is 0.1423 against 0.1625. **The SUD-to-unemployment link is already
roughly right.** Addicts in this model do lose their jobs at close to the data
rate. They still do not become homeless, and the reason is that there is no
unemployment-to-homelessness channel of any strength: the measured homelessness
risk ratio for the unemployed runs 0.27 to 3.27 across the four two-beta points,
never large, and unstable enough that only its smallness is trustworthy.

`increased_prob_if_homeless` does NOT close that gap. It runs the other way --
being homeless costs you the job -- which is the Housing First channel and is
worth having, but it is not a route IN. After both of today's changes the model
still contains nothing by which losing your job puts you on the street. `rho_d`
connects the disorder to destitution directly and bypasses unemployment.

If the mechanism is meant to run SUD -> unemployment -> homelessness, that is a
THIRD change and it is a scope decision: making unemployment itself
impoverishing, through UI generosity or duration or the food stamp floor. It has
been put to the author and is not being made on this session's initiative.

One candidate to settle rather than a finding: `cbar`, food stamps over labour
income, reads 0.0532 against a target of 0.0042 at `point_445884ebe4`, which
would say the safety net is twelve times more generous than intended and is
exactly why an unemployed household can still pay rent. But `cbar` has the same
aggregate-over-a-mean form as `aleph`, and that normalisation is the one applied
and reverted this morning. Settle the normalisation before reading the level.

## THE TWO DISORDER UNEMPLOYMENT RATES ARE CALIBRATED, NOT ASSIGNED

The author's ruling, in their own words:

    "It's ok if the unemployment rates of those with SUD and SMI are not aligned
    with the data we have. We don't truly know what they are so we calibrate
    them."

So `kappa_ued` and the employment-given-SMI moment are OUTPUTS. Their parameters
-- `multiple_of_probabilities_of_employment_if_addicted` and `kappa_uem` -- now
answer to the SUD and SMI shares of the homeless instead, and the two labour
rates are what falls out. They are reported at every point and never scored; a
drift in either is information rather than a miss. This is the whole of the
first coherence objection raised against the re-pointing and it is now closed.

**For the paper.** Table 5 and the calibration section will need these shown as
CALIBRATED, with the homelessness shares as their targets, rather than as
assigned numbers the model happens to reproduce. Not edited -- the author has
asked to hold paper edits.

### WHERE THE MAP STANDS, AUDITED RATHER THAN ASSERTED

Seventeen externally searched parameters, one moment each, **no duplicate
drivers**:

    discount_factor_impatient                            -> w_bot
    increased_prob_if_homeless                           -> emp_homeless
    kappa_phi_d_level                                    -> y_u
    kappa_uem                                            -> lambda_m
    largest_house_size                                   -> h_2
    max_food_cost                                        -> cbar
    mu_homeless                                          -> mu_H
    multiple_of_probabilities_of_employment_if_addicted  -> sud_homeless
    probability_becoming_unemployed                      -> pi_eu
    probability_of_voucher_benchmark_used                -> pi_V
    relative_share_of_addiction_1                        -> theta
    relative_share_of_housing                            -> gamma
    size_homelessness                                    -> h_1
    smallest_rental_relative_to_lowest_income            -> h_3
    smi_onset_level                                      -> p_m
    utility_cost_of_treatment                            -> tau_u
    value_of_life                                        -> aleph

`b` and `lambda_d` are driven by the drug-block repair path on
`addiction_scalar_1` and `lambda_addiction`, not by the gate. `beta`, `tau_l`,
`omega_l` and `sigma_y` are bisected inside the model. `h_3` is conceded.

### THE ONE OBJECTION THAT REMAINS: THE STOPPING RULE MAY BE UNREACHABLE

`h_age1` to `h_age5` are in the minimax and **no parameter owns any of them.**
That is deliberate -- the author chose to score the outcome rather than its
proximate causes -- but it means the loop cannot stop until five undriven
moments are all inside ten per cent, and band one is currently 736 per cent out
(0.02641 against 0.00316).

The rule as it stands is therefore a test the search may never pass, and it will
never report DONE even if every moment that HAS an instrument is inside ten per
cent. Three ways out, for the author:

  1. leave it, and read the gap table by hand rather than waiting for exit 4;
  2. score ONE summary of the profile instead of five bands -- the share of the
     homeless in band one, 0.91 against 0.26, carries the whole issue in a
     single number and is one constraint rather than five;
  3. score the five bands at a looser tolerance than the ten per cent the other
     moments use, on the grounds that no instrument points at them.

Not decided here. Put to the author.

## cbar IS THE WORST SCORING MOMENT AND ITS DEFINITION IS NOT SETTLED

With the profile scored through `h_share1`, the gap table on `point_445884ebe4`
puts `cbar` first at **1166 per cent**, ahead of `lambda_d` at 772 and `b` at
764. So it is now the moment the minimax chases hardest. Three things about it
are unresolved and they move it by a factor of about thirty between them.

### (a) A FALSE LEAD, RECORDED SO IT IS NOT FOLLOWED AGAIN

The first check looked decisive and was wrong. Food-stamp spending is 0.053169
in the printed units, the maximum allotment prints as 0.0073311, and 3.9556
households receive it, so spending is 1.833 times the most those recipients
could possibly draw -- which would be impossible, since `snap_benefit =
max(0, max_food_cost - food_stamp_taper*net_1)` is a hard cap with no household
size scaling.

It is not impossible, because **the DIAG line compares a level against a ratio.**
`DIAG max allotment / avg labour income` prints `max_food_cost` RAW and sets it
beside 0.039586, which the comment derives as 291 dollars a month over mean wage
income of 88,212. That comparison is only valid if average labour income is one
in model units, and it is about 0.6. The true ratio is
`max_food_cost/model_average_labour_income`, near 0.012, so the allotment is
about three times too small rather than five, and the 1.833 dissolves. The same
applies to `DIAG gross eligibility cutoff`, which prints
`max_food_cost/food_stamp_taper` against 0.214872.

Both lines should divide by `model_average_labour_income`. Held, with the rest
of the source, until the UNEMP round lands.

### (b) THE DENOMINATOR IS A MEAN AND THE LABEL SAYS OTHERWISE

    cbar = govt_spending_on_food_stamps / model_average_labour_income

An aggregate over a MEAN, which is dimensionally the same object as `aleph` --
and the note on `aleph` concluded its target "was evidently set against the
aggregate form". Whether the same is true here is not recorded anywhere.

### (c) THE TARGET HAS NO DOCUMENTED CONSTRUCTION

`food_stamps_share_data=0.0042` at line 1908 carries NO comment. Every target
around it does: `participation_rate_data` explains its NSDUH severity split,
`vsl_data` explains the nine million over $113,000, `drug_user_income_data`
cites NSDUH. This one is a bare number.

It matters because the reading changes the gap by more than an order of
magnitude. SNAP outlays in FY2023 were about $113bn against a GDP near $27.7tn,
a ratio of 0.0041, which matches 0.0042 to two digits -- but that is recall of
US aggregates rather than anything the repository states, and if it is right then
the denominator should be OUTPUT and not average labour income, and the moment as
computed is meaningless rather than badly missed.

**A QUESTION FOR THE AUTHOR, not a change.** How was 0.0042 built? Total SNAP
outlays over GDP, over total labour income, or something else? Until that is
answered, `cbar` is the binding constraint of the whole calibration on a target
nobody can reconstruct, and there is a case for moving it to UNSCORED so the
search is not driven by it. Not done here.

## "NOTHING LANDED IN TWO FIRINGS" DOES NOT MEAN THE FLEET HAS DRAINED

The engine prompt treats two quiet firings as the signal that every worker has
finished and stopped, and tells the next firing to respawn. That rule misreads
the commonest case, and acting on it wastes the rate limit that emptied the fleet
once already tonight.

**A fresh worker cannot produce a point for about forty minutes.** Its container
arrives without gfortran, so it installs one (about fifteen minutes) and then
compiles 38,000 lines at -O3 (about twenty five). Only then does the first solve
start, and that is another twenty. Two firings thirty minutes apart therefore
land entirely inside the setup of a round launched just before the first of them,
and the archive is legitimately empty at both.

Distinguish them before respawning anything:

  - `list_sessions` and read `post_turn_summary`. A worker mid-setup says so --
    "gfortran install + 40m Fortran compile underway", "run alive; awaiting line
    4 (pid 2355)". A drained one says it has finished, and a rate-limited one
    says "You've hit your session limit" with `rate_limit_info.status` at
    `rejected`.
  - Only a worker that is IDLE with no run in flight and no result pushed has
    actually stopped.

At 00:21 on 1 September all five live workers were mid-setup or mid-solve, the
archive held zero points on the current hash, and respawning would have been
exactly wrong.

## WHERE A POINT ACTUALLY SPENDS ITS TIME, FROM A STACK TRACE RATHER THAN A GUESS

The control point on the fixed source ran 25 minutes with a silent log and was
about to be killed on the inference that it had hung. It had not. `gdb -p` on the
live process:

    #0  _gfortran_mminloc0_4_r8 () from libgfortran.so.5
    #1  stationary_equilibrium_wealth_distribution_of_old (time_period=1)
        at housing_first_or_treatment_first_SR_v1.f90:11195
    #2  calibrating_model () at housing_first_or_treatment_first_SR_v1.f90:35274

**The time is in `stationary_equilibrium_wealth_distribution_of_old`, ninth of
the nine chain routines, and specifically in the `do while` at 11186.** That loop
walks the wealth distribution upward one grid cell per iteration, and each
iteration does TWO full masked scans of `wealth_matrix(time_period,:,:,:)` -- a
`minval` and a `minloc` over the same masked array -- plus a `sum` over a slice of
`distribution_stationary`. It is O(cells) iterations with O(cells) work in each.

Live values from the same trace:

    sum_of_distribution_of_old = 15.41214567938221
    wealth_of_top_x_perc_index = 1
    (wealth_counter_2 optimised out)

The divisor looks like one type's retiree mass and not an inflated one, so the
`save` added to it earlier tonight is NOT obviously the cause. And the routine was
still on the FIRST of its percentile targets after 25 minutes.

### WHAT THIS DOES AND DOES NOT SETTLE

  - The 500x secant slowdown is genuinely fixed: the age loop is 3.5 minutes of
    the run and working ages cost 2.49 s against 191 s.
  - The silence is NOT buffering. `GFORTRAN_UNBUFFERED_ALL` was restored and the
    log is still quiet, so this phase simply prints nothing. The earlier
    attribution of the silence to the missing environment variable was wrong --
    the variable was genuinely missing and `OMP_STACKSIZE` genuinely mattered,
    but it was not what made the log go dark.
  - Whether this loop is slow-but-finite or actually stuck is NOT settled. The
    process is at 177 per cent CPU, so it is executing rather than blocked. The
    test is whether `wealth_of_top_x_perc_index` advances past 1.

**DO NOT KILL IT ON AN INFERENCE.** The previous run was killed on the buffering
theory and the theory was wrong. Sample the index again before deciding.

### THE TOOL THAT SHOULD HAVE BEEN USED HOURS AGO

`gdb -p <pid> -batch -ex "thread apply 1 bt 12"` answers "where is it" in seconds
and needs no instrumentation, no rebuild and no guessing. Two hours went into
inferring what a stack trace states. `gdb` is installed in these containers.
Reach for it the first time a run looks slow, not the fifth.

## tau_u was never being calibrated: its instrument has been zero at every point

`tau_u` has read 0.99969 to 0.99998 at every point measured for weeks, against a
target of 0.245, and it went on the author's list of moments to fix. It is not a
calibration failure. **Treatment is free in every vector measured so far**, so
every household carrying the disorder takes it, and 1.0 is the arithmetic
answer rather than a bad fit.

There are two cost channels and the vector zeroes both:

- `money_cost_of_treatment` is declared 0.02 and handed over as 0. It is not
  internally calibrated -- `money_cost_of_treatment_adjuster` and
  `distance_money_cost_of_treatment` are both declared and never read, and
  there is no update block -- so the handover is the only thing that sets it.
- `utility_cost_of_treatment` is declared 0 in the Fortran, defaulted to
  **0.0908753** in `run_one_point.sh`, and handed over as **0**.

`next_batch.py`'s `OWN` map points `tau_u` at `utility_cost_of_treatment`, on
the author's instruction of 31 August, with the money price held at zero. So the
one instrument that owns the moment has been pinned at zero by the vector while
the runner's own default for it is 0.0908753. Checked across the twelve most
recent points: `utility_cost_of_treatment=0` in all twelve.

The moment itself is computed correctly and is properly guarded for the two-pass
chain -- `model_treatment_take_up` is divided by `model_mass_with_sud` inside
`if (current_beta_type==number_of_beta_types)` at line 13043, and its reset at
11576 is inside `if (accumulating_beta_types==0)`. Nothing is wrong with the
measurement.

`utility_cost_of_treatment` is subtracted from flow utility once per period of
treatment, at line 20479, wherever flow utility is evaluated. Flow utility is
negative and of order one before `value_of_life` is added, so 0.0909 is a small
fraction of it and the bracket is expected to need more; the handover clamps
the parameter to [0, 10] and `next_batch.py` brackets it to [0, 8].

**It is coupled to b and lambda_d and must be measured, not assumed.** Charging
for treatment lowers take-up, which lowers recovery, which raises the disorder
rate: `lambda_d` should rise when this parameter leaves zero, and `b` with it.
The next point therefore moves this parameter alone from the best available
addiction pair, so the tau_u response and the b/lambda_d feedback are read off
the same controlled step.

## cbar: the food stamp formula makes spending quadratic in max_food_cost, and that pins the step

The benefit is linear and tapered to zero, at line 4803:

```
snap_benefit = max(0, max_food_cost - food_stamp_taper*net_income)
```

with `food_stamp_taper` a parameter fixed at 0.30. So a household is paid
whenever net income is below `max_food_cost/0.30`, and aggregate spending is

```
integral over y below cbar/tau of (cbar - tau*y) dF(y)
```

If the income density is roughly flat over that range -- and the range is tiny,
0 to 0.024 of a distribution whose mean is 0.55 -- then the number of recipients
is proportional to `max_food_cost` and the average payment is proportional to it
as well, so **aggregate spending goes as the square of `max_food_cost` while the
recipient share goes as the first power**.

That gives one step with two independent checks, which is why it is worth
stating before measuring rather than after:

| | model at cbar = 0.007331089 | target | ratio |
|---|---|---|---|
| food stamps / output | 0.00072248 | 0.0042 | 5.813 |
| households receiving food stamps | 0.049964 | 0.125 | 2.502 |

The square root of 5.813 is **2.411**, and the recipient ratio is **2.502**. The
two agree to four per cent, which is the quadratic story confirming itself out
of numbers measured in the same run. Scaling `max_food_cost` by 2.411 predicts
spending of 0.0042 and a recipient share of about 0.1204 against 0.125, and both
are checkable in a single point.

**So the step is `max_food_cost` = 0.007331089 x 2.411 = 0.017676**, and it
replaces the earlier guess of "up about four times", which came from treating
the gap as if spending were linear in the floor. If spending comes back near
0.0042 AND recipients near 0.12, the mechanism is right and cbar is finished in
one move; if spending overshoots while recipients land, the density is falling
rather than flat and the exponent is between one and two.

### The eligibility diagnostic compares two different objects

`DIAG gross eligibility cutoff` prints `max_food_cost/food_stamp_taper` over
average labour income, 0.0445, against 0.214872, which is 130 per cent of the
poverty line over mean wage income. Those are not the same quantity: the model's
number is the income at which the benefit tapers to nothing, and the data number
is the statutory gross income screen. In the programme both exist and the
screens bind different households. The ratio of the two diagnostics implies a
taper of 0.184 in the data against the model's 0.30, which is not evidence the
taper is wrong -- it is the arithmetic of comparing a benefit exhaustion point
with an eligibility test. Left as it is, and flagged rather than changed,
because `food_stamp_taper` is assigned at 0.30 from the programme rule.

## The value of life diagnostic had two faults, and neither changes a moment

The author asked whether there is a bug in the value of life estimation. There
are two, both in the diagnostic rather than in the estimate, and both are now
fixed.

**1. `val_life_min` was reset on every beta pass.** At line 29073 the reset

```
val_life_min(time_period)=10.d0**(10)
```

carried no `if (accumulating_beta_types==0)` guard, while the eleven resets
immediately around it -- including `val_neg_life_mass`, `val_ugoods_users` and
`val_umass_users`, its own siblings in the same diagnostic -- all did. So the
second pass threw away the first type's minimum and
`DIAG lowest value of a period of life` printed the LAST beta type's minimum
alone. This is the same bug the author already found and fixed in
`model_largest_negative_value_of_life`, whose note at line 7763 says exactly
this and calls the guard on its twin the reason it is an oversight rather than a
decision. Now guarded, so the minimum is taken over both types and can only fall.

**2. The negative mass was printed as a mass in a block of ratios.** It read

```
DIAG mass with a NEGATIVE value of life = 0.30321006402406536
```

which invites reading as thirty per cent of households preferring not to be
alive -- which, on the author's own note beside it, would make the selection
into drug use a defect rather than a mechanism. It is not thirty per cent.
`val_neg_life_mass` accumulates `distribution_mass_used`, so it is a mass on a
pooled population of 95.4, and the share is **0.32 per cent**. The line now
prints the share, with the raw mass and the divisor beside it, in the same form
the food stamp line two lines below already used.

So the substantive answer is that the value of life is not broken: a third of
one per cent of households sit below zero, not a third of the population. The
minimum itself may move once the guard takes effect, since it can now see both
types, and -9.83 was measured on one of them.

**Neither fix touches a moment.** Both are inside diagnostic prints or a
diagnostic's reset; no moment, no invariant and no calibration update reads
`val_life_min` or `val_neg_life_mass`. Points measured before and after are
comparable on every scored quantity.

## ev_table_key not keyed on treatment is correct, and comes off the deferred list

It was on the deferred list as a suspected bug and it is not one. The cache key
at line 17728 carries six fields -- age, employment, unemployment, voucher,
housing status, years left on the mortgage -- and neither the treatment choice
nor the addiction state appears in it. Both omissions are deliberate and both
are safe, for different reasons.

`smooth_addiction_hazard` is a `parameter` fixed at 1, so at line 17851
`haz_1` is identically one and **the table carries no hazard at all**. Its
second index is the future disorder STATE, and the caller forms

```
(1 - pi_d(v)) * EV(a', clean) + pi_d(v) * EV(a', disorder)
```

once the quantity is known. Treatment changes today's flow utility and today's
recovery hazard, and it changes neither of those two continuations -- EV(a',
clean) is the same object whether or not the household is in treatment this
period. So the caller, not the table, is where treatment belongs, and that is
where it is: `addiction_transition` takes `treatment_1` and applies
`min(1, g * pi_r)` at line 6531.

The folded branch, where the hazard IS inside the table and a treatment-keyed
cache would be needed, is unreachable while `smooth_addiction_hazard` is a
parameter equal to 1. If it is ever turned off, the key has to gain the
treatment choice; noted here rather than guarded, because it is a compile-time
constant and a guard would be dead code.

Checked one thing on the way past, because it would have been serious: the
continuation sum at line 17873 discounts with the bare `discount_factor`, and
with two beta types that would solve the impatient household with the patient's
beta. It does not. `discount_factor` is reassigned per pass at lines 35267 and
35268 from `discount_factor_patient_saved` and `discount_factor_impatient`
before each type is solved. Correct as written.

## The addiction pair is bracketed, and the step now in flight interpolates inside it

Two measured points straddle both targets, which is the first time that has been
true. At `addiction_scalar_1` = 0.0438 with `lambda_addiction` = 2.67 both
moments are ABOVE target; at 0.0434 with 3.451 both are BELOW it.

| point | as_1 | lambda_add | b | lambda_d | b/lambda_d |
|---|---|---|---|---|---|
| 85f8304979 | 0.0438 | 2.670 | 0.113679 | 0.044264 | 2.568 |
| ccd590735a | 0.0434 | 3.451 | 0.082282 | 0.034287 | 2.400 |
| target | | | 0.089000 | 0.036800 | 2.418 |

Log-linear along the segment joining them, the root for `b` is at t = 0.7572 and
the root for `lambda_d` at t = 0.7230, both inside [0,1] and 3.4 points of t
apart. Taking t = 0.7401 gives

```
addiction_scalar_1 = 0.04350395
lambda_addiction   = 3.24803
```

predicting b = 0.089493 (+0.55 per cent) and lambda_d = 0.036640 (-0.44 per
cent). **This is an interpolation between two measured points, not a slope
extrapolated past the pair that produced it**, which is the standing rule; the
two roots agreeing to within four per cent of t is the evidence that one point
on the segment can carry both moments.

The batcher's gate is five per cent on `max(|b gap|, |lambda_d gap|)`, not the
ten per cent acceptance rule, so ccd590735a at 7.5 per cent does not open the
full correction batch and this step is deliberately PURE -- no other instrument
moves in it. Anything else moved here would shift b and lambda_d and the gate
would have to be re-earned, which is what the gate exists to prevent.

## Why restore.py's repair was NOT used this firing, and the measurement that settles it

The gate exits 2 at ccd590735a, and the loop's step 3 sends exit 2 to
`restore.py`. It was run, and its proposal is recorded in
`RESTORE_ccd590735a.txt`, but it was not launched. The reason is a measurement,
not a preference.

restore.py refits the two-by-two drug-block Jacobian from the archive and warned
that it could not do so locally: *"base slice too small; Jacobian borrowed from
4 points elsewhere, so the step is halved"*. Its borrowed slopes are

```
d ln b        / d ln lambda = -1.83   / d ln as1 = -16.4
d ln lambda_d / d ln lambda = -1.13   / d ln as1 = -22.4
```

Those slopes can now be tested, because the move from ccd590735a to
85f8304979 is a MEASURED displacement in both parameters at once:
`d ln lambda = -0.2566`, `d ln as1 = +0.00917`.

| moment | borrowed Jacobian predicts | measured | ratio |
|---|---|---|---|
| b | +0.3191 | +0.3232 | **0.99** |
| lambda_d | +0.0844 | +0.2554 | **0.33** |

**The borrowed Jacobian is excellent for b and wrong by a factor of three for
lambda_d**, and lambda_d is the moment that has been binding all along. A step
built on it -- then halved -- moves lambda_d roughly a sixth as far as intended,
which is why restore proposed a lambda_addiction move of -0.013 e-folds where
the bracket says -0.062 are needed.

So the standing rule decides it: PREFER A MEASURED BRACKET TO AN ELASTICITY. The
step in flight is a straight interpolation between two measured points that
straddle both targets, needs no Jacobian at all, and its two roots agree to
within four points of t. `RESTORE_ccd590735a.txt` is kept as the record of what
was rejected and why; it must not be mistaken for the live step.

This also explains why the local search stalled for so long at a b/lambda_d
ratio of 1.5: every step was built from a Jacobian that understated lambda_d's
sensitivity threefold, so the ratio could not be moved even though b tracked
predictions closely.

## STATE AT 06:10 ON 1 SEPTEMBER: the gate is open and the archive is being seeded

**The anchor is `point_9a13317e65`**, and it is the best point measured to date:

```
addiction_scalar_1 = 0.04350395    lambda_addiction = 3.24803
b = 0.086789 (-2.5%)   lambda_d = 0.035791 (-2.7%)   ratio 2.4249 vs 2.418
all sixteen invariants PASS
```

Nine of twenty-one scored moments are inside ten per cent: theta, tau_l, b, p_m,
lambda_d, aleph, lambda_m, sigma_y and h_3.

### The gate opened and the batch was still empty

`next_batch.py` exits 0 at this point but wrote **zero** correction arms, with
the same reason twelve times: *no controlled pair in the archive*. Every point
measured on this model varies only `addiction_scalar_1` and `lambda_addiction`,
so for every other instrument there is neither a bracket nor an elasticity to
step on. **Opening the gate is not the same as having a search**, and that
distinction cost a firing to notice.

`SEED_26.txt` supplies the missing pairs: twelve arms, one coordinate each, from
the anchor. `run_seed_batch.sh` runs them sequentially on this box and commits
each point as it lands. Sequential rather than a fleet: the model already uses
all four cores, so there is nothing to win locally, and every recorded fleet
failure -- stalling at "ready to run", the permission prompt on command
substitution, the rate limit that emptied it at 21:33 -- costs more than the
wall clock saved. Twelve arms at about ten minutes each is roughly two hours.

Step sizes come from mechanism where one exists and from a modest e-fold
otherwise, which is the honest distinction:

| parameter | moment | gap | step | where the step came from |
|---|---|---|---|---|
| max_food_cost | cbar | -83.4% | x2.411 | square root of the spending ratio, from the benefit formula |
| utility_cost_of_treatment | tau_u | +308% | 0 -> 2.0 | off a corner; 2.12 was the old loop's value |
| probability_of_voucher_benchmark_used | pi_V | -48.3% | x1.936 | coverage taken as roughly linear in the lottery |
| discount_factor_impatient | w_bot | +101% | 0.95 -> 0.90 | direction only |
| size_homelessness | h_1 | -62.6% | +0.30 e-folds | direction only |
| largest_house_size | h_2 | -32.3% | +0.30 e-folds | direction only |
| relative_share_of_housing | gamma | -27.4% | +0.30 e-folds | direction only |
| kappa_phi_d_level | y_u | +22.5% | 8.0 -> 6.0 | direction only, inside the authorised floor of 4 |
| probability_becoming_unemployed | pi_eu | +10.4% | -0.15 e-folds | direction only |
| mu_homeless | mu_H | +754% | 0.8047 -> 0.95 | direction only; denominator near-empty |
| increased_prob_if_homeless | emp_homeless | +110% | 0.2 -> 3.8 | the steady-state formula |
| multiple_of_probabilities_of_employment_if_addicted | sud_homeless | -100% | 4 -> 8 | direction only |

### Two of the worst gaps are artifacts and must not be chased as fits

- **`tau_u` +308%** is a corner. Both treatment cost channels are handed over as
  zero, so treatment is free and everyone with the disorder takes it. Arm 2
  gives it a price for the first time.
- **`mu_H` +754%** divides by a homeless SUD mass of 7.96e-15. The author's own
  comment at line 13055 anticipates it: the homeless SUD mass "is exactly zero
  whenever the housing margin has collapsed". It cannot be calibrated until the
  homeless population contains people with the disorder.

### omega_l is scored and has no owner

`omega_l`, labour supply over total hours, is -17.9 per cent and is NOT in
`SKIP`, so the stopping rule counts it -- but it has no entry in `OWN`, so no
arm is ever generated for it and the loop can never close it.
`relative_share_of_leisure` is in the vector, is the obvious candidate, and is
mapped to nothing. **This needs the author's decision** rather than a silent
mapping: either `relative_share_of_leisure` owns `omega_l`, or `omega_l` joins
`h_3` as a concession. Flagged, not changed.

### The one structural fact behind four of the misses

`homeless by choice = 1.0000`, `homeless who could afford it on income =
1.0000`, 96.8 per cent of the homeless in age band 1, 96.7 per cent employed,
SUD share of the homeless about zero. **Every homeless household in this model
is a young worker with no wealth choosing homelessness to avoid rent.** There is
no involuntary channel at all, which is why the age profile, the employment
share, the SUD share and `mu_H` are wrong together rather than separately. Arms
11 and 12 are the first attempt to move it from inside the current model.

## 08:50 INCIDENT: a supervisor came up and the working tree was rolled back

Three of the loop's checks failed at once at the 08:50 firing:

```
DIVERGED                       HEAD was 4a244d6, origin was 0556783
SUPERVISOR UP                  supervise_calibration.py, pid 1372, up 1m02s
code/CALIBRATION_ACTIVE        present
points on model: 0             the source in the tree was 924b0fabd5, not 033a668663
```

Handled in the order the loop prescribes: `kill -9` on the supervisor, marker
removed, then `git checkout -B <branch> FETCH_HEAD`.

**Nothing was lost, and it is worth recording why rather than just that.**
`git branch -a --contains 4a244d6` shows that commit on both the branch and
origin, so it is an ANCESTOR of the current tip and not a competing commit. The
tree had been rolled back to an earlier point in its own history -- consistent
with the stale-snapshot restore the loop prompt describes -- rather than written
over by the supervisor. Every commit made during the seed round was already on
origin. After the restore: HEAD at 0556783, source hash back to 033a668663, all
twelve arm points and the anchor present, 159 point files, working tree clean,
and the gate runs and exits 3.

The damage was potential rather than actual this time, but the same sequence
with an uncommitted arm in flight would have destroyed it. Two lessons, both
already followed during the seed round and worth stating as rules:

- **commit and push every point as it lands**, which `run_seed_batch.sh` does
  per arm, so the window in which work exists only in the container is one solve
  long;
- the checkout guard in step 0 is not a formality. It fired for real here, and
  the tree it found was three hours stale.

A watchdog is now running for the rest of this session: every thirty seconds it
kills any `supervise_calibration.py` it finds and removes the marker. This is the
standing instruction ("If up: kill -9 it, remove the marker") turned into a loop
rather than a check, because the supervisor has now appeared during a firing and
a check only catches it every twenty minutes.

## WHY MORE UNEMPLOYMENT WILL NOT FIX THE HOMELESS COMPOSITION ON ITS OWN

The author asked why raising unemployment would not fix it, given UI lasts one
period and only thirty per cent of job losers get it. The mechanism is right and
the arithmetic supports it:

```
probability_becoming_employed            0.55        spell 1.8 years
  ... if addicted (divided by 4)         0.1375      spell 7.3 years
probability_becoming_unemployed          0.00568
  ... if addicted (times 4)              0.0227      steady-state u given SUD 14.2%
probability_of_ui                        0.30        so 70 per cent get nothing at all
```

(The declarations of `probability_becoming_unemployed_if_addicted` and
`..._employed_if_addicted` read zero at lines 3381-3382, which looks like frozen
employment for the addicted. They are overwritten at 33586 from
`multiple_of_probabilities_of_employment_if_addicted`. Not a bug; checked.)

Against wealth buffers of, at zero income and consumption near 0.30 a period:

```
age 26  wealth 0.000  ->  0.00 periods      age 35  wealth 0.521  ->  1.74 periods
age 29  wealth 0.236  ->  0.79 periods      age 41  wealth 0.749  ->  2.50 periods
```

**A household that loses its job faces a spell several times longer than its
savings can cover, at every age.** It should be destitute within one to three
years. So the author is right that the mechanism is there, and the question is
why it produces no homelessness.

### Because the bottom rung of the housing ladder is too cheap to fall off

`DIAG homeless who could afford it on INCOME ALONE` reads **exactly 1.0000** at
every point measured today, as does `homeless by choice`. Every homeless
household could have paid the rent out of current income. **No household is ever
priced out of housing**, so homelessness is always a choice and never a
constraint, and enlarging the pool of jobless households simply produces more
jobless households who can still afford the smallest unit.

The parameter that sets that rung is
`smallest_rental_relative_to_lowest_income`, currently 0.0377, and at line 28809
the scaling its own name describes is commented out:

```
smallest_house_size=smallest_rental_relative_to_lowest_income   !net_income_lowest*smallest_rental_relative_to_lowest_income/1.079
```

so the smallest unit is the raw parameter rather than a fraction of the lowest
income. Whether that is deliberate is the author's to say; the consequence is
that the cheapest dwelling does not scale with the bottom of the income
distribution.

### And that parameter is parked on a moment it cannot move

`OWN` assigns `smallest_rental_relative_to_lowest_income` to `h_3`, where
`next_batch.py`'s own comment records it moving the moment at **-0.01** -- which
is nothing -- while noting in the same breath that "smallest_rental's strongest
moment is actually h_1 at 2.81". So the one parameter controlling whether anyone
can be priced out of housing is assigned to a moment it does not move, and has
never been stepped on anything meaningful.

**The order that follows from this**: raising the price of the bottom rung is
what creates involuntary homelessness; more unemployment then feeds it. Done the
other way round the extra unemployment changes nothing. This is a measurement to
make, not a conclusion: the arm is `smallest_rental_relative_to_lowest_income`
from the best point, one coordinate, watching `homeless by choice` and
`could afford it on income alone` for the first departure from 1.0000 in the
whole session.

# STATE AT 13:40 ON 1 SEPTEMBER: the housing block was restructured and the archive is void

## What changed in the model, and why the archive no longer applies

The rental ladder is now ASSIGNED off one free parameter, on the author's
instruction:

```
h_1  street          = h_2 * size_homelessness    calibrated on the homelessness rate
h_2  cheapest rental = smallest_rental_relative_to_lowest_income, currently 0.20
h_3                  = 2 * h_2    ASSIGNED
h_4                  = 3 * h_2    ASSIGNED
```

`largest_house_size` and `housing_status_grid_expander` now determine nothing and
are held. The inverted-grid guard in `run_one_point.sh` is retired with them: it
compared the two endpoints and fired a false positive on an inert parameter.

Two targets moved as well: `pi_eu` from 0.0485 to **0.139**, and `gamma` from
housing over expenditure at 0.268 to housing over **income** at 0.202.

**This voids the archive.** The target changes were bookkeeping and were handled
with `TARGET_OVERRIDE` and an equivalence entry. The grid change is a different
economy, so all 170 earlier points are genuinely inapplicable and the gate has
nothing. It must be RESEEDED, not interpolated.

## The one thing that was solved today

`homeless who could afford it on INCOME ALONE` and `homeless by choice` had read
**exactly 1.0000 at every point ever measured**. Nobody could be priced out of
housing, so all homelessness was voluntary, so only households at literal zero
wealth chose it, so 86 per cent of the homeless were age 26 -- the entry cohort,
which is the only group with exactly zero assets because newborn endowments are
switched off. Every instrument tried against the age profile failed because they
all acted on households that had already saved past the threshold.

Raising the cheapest rent breaks it. Three points:

```
h_2    involuntary   employed   band 1   SUD share   h_1
0.09         0.1%     0.9381    0.9521    0.003932   0.003431
0.12        23.6%     0.9014    0.9151    0.003222   0.002656
0.20        75.2%     0.9045    0.8047    0.001708   0.002251
target                0.4600    0.2600    0.2170     0.003990
```

## What that sweep establishes, and it is not what was predicted

**The level moments are calibratable. The composition moments are not.**
`h_1` is reachable and `homeless by choice` spans 1.00 to 0.25. But the employed
share of the homeless sits at **0.90 across a 2.2-fold range of the cheapest
rent**, and the SUD share FALLS as the rent rises.

The prediction recorded before the 0.20 point -- that composition would move once
the priced-out were a majority -- is falsified. The reason is measured: the
affordability constraint sorts on INCOME, and the lowest incomes in this model
belong to young workers. Raising the rent excludes more of the same people. The
unemployed are 7.9 per cent of working-age households, and the disorder cuts no
wage at all with `rho_d` held at 1, so neither group is poorer than a
twenty-six-year-old.

Reaching the composition needs one of two things the model does not currently
have: `rho_d` below one, which the author has ruled out on a double-counting
argument, or an out-of-labour-force state with genuinely low income. The model's
three employment states are all IN the labour force, which is why
`DIAG participation, working age` reads 1.0000 and why the no-wage share equals
`pi_eu` exactly.

## The open decision, and the two jobs behind it

The 1:2:3 ladder ties the ceiling to the floor, so pricing people out at the
bottom drags `rent50` (0.554 -> 0.644, target 0.175) and `gamma` (0.393 -> 0.425,
target 0.202) the wrong way. Loosening the top ratio separates them and gives
`largest_house_size` back a job; keeping it means conceding those two.

Behind that, whatever is decided: the drug block is collapsed at these housing
values -- `b` 0.0071 against 0.089, `lambda_d` 0.0011 against 0.0368 -- and needs
the addiction pair re-solved, which has worked before from a measured two-by-two;
and the archive needs a full reseed on the new grid.

## CORRECTION: "the economy spends over 100 per cent of income on rent" was wrong

At 14:45 I read `DIAG aggregate rent / aggregate income = 1.0849` and reported
that the model was spending more than it earned on rent, calling it "not a
sensible economy". The author pushed back that this must be a bug. It is neither
a bug nor what I said it was, and the diagnostic's own comment at line 5113 says
why:

> aggregate_rent_spending is GROSS rent, before housing vouchers, and covers
> housed renters only, so the homeless contribute nothing to the numerator and
> their income is still in the denominator.

So the numerator includes the part of rent paid by the government through
vouchers, and excludes the homeless while their income stays in the denominator.
It is not a household spending share and cannot be read as one. A ratio above one
violates nobody's budget constraint.

The household-level figure sits two lines away and is the one that matters:

```
housing over income, renters (mean of household ratios)  0.429   target 0.202
aggregate housing / aggregate expenditure                0.327
```

**Households spend 43 per cent of income on housing, not 108.**

The checks that would have made it a real bug were run and all pass:
`aggregate_rent_spending` and `model_output` are both reset under
`if (accumulating_beta_types==0)` and both accumulate across both beta passes, so
the pooling is consistent; the assigned ladder holds the values it was given; and
the rental market clears with its invariant at exactly 1.0.

**What survives is the smaller true version.** `gamma` at 0.429 against 0.202
means the ladder still makes housing about twice as expensive as it should be.
That is the same tension as `rent50` and points the same way -- the 1:2:3 ratio
ties the top rung to the floor -- and it is a calibration problem rather than a
broken model.

**The lesson, which is the third time today.** A diagnostic's label is not its
definition. `mass with a NEGATIVE value of life` was a mass read as a share,
`mu_H` at +754 per cent was a ratio over an empty set, and this was gross rent
read as household spending. Read the accumulation before reporting the number.
