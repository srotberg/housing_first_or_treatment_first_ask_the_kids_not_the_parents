# Calibration state — 3 September, 23:55

## THE CONFIGURATION, settled today and not to be changed without the author

    number_of_beta_types  1          one beta for everyone
    discount_factor       0.945      calibrated on W/Y = 3
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor

Both are CONFIG_SWITCHES in next_batch.py and gaps.py: a point that differs on
`number_of_beta_types` or `use_pia_formula` does not pool. 91 points are skipped
for the first and 617 are on older source revisions.

## THE ECONOMY CHANGED AT 22:00: the street is barred at the addiction cap

`max_age_to_choose_addiction` is the last age a household may START using, so the
value of ABSTAINING falls discretely there -- earlier, abstaining keeps the option
to start later; at the cap that option is worth nothing. Use bunched at exactly the
cap, drug spending crowded out rent, and the street was taken in the same period.
Age 80 carried **74.2 per cent of all homelessness in the model**.

MEASURED, on an isolated branch whose points were never merged, same vector at
three caps: cap 57 put the peak at age 82 at 0.322621, cap 55 at age 80 at 0.190450.
The spike follows the cap, so RAISING the cap relocates it and roughly doubles it.
The author's own suggestion was implemented instead: `allow_to_choose_homelessness=0`
at `age_index==max_age_to_choose_addiction`, at BOTH sites where that flag is set.
The drug margin is untouched; only the street is barred, in that one period.

Model hash moved to 4df7be4132 and the archive was re-seeded. **The old economy's
46.58 per cent and this economy's numbers are NOT comparable** -- three quarters of
the old homelessness was the artefact.

## THE BINDING STRUCTURE, measured tonight and unresolved

Best point `point_42ddb999fb` at **56.42 per cent**, worst `h_share1`.

    ON THE STREET RAY ALONE (labor_income_tax_rate 0.752)
    street    max|res|     h_1  h_share1
    0.04450       58.4   -58.4     -19.0
    0.04480       56.4   -22.7     -56.4     <- best
    0.04500       67.6    +4.0     -67.6
    0.04700      224.3  +224.3     -89.6

h_1 lands on target at 0.04500, the first time all day. But h_1 and h_share1 move in
OPPOSITE directions along this ray, so the minimax bottoms at 56.4 and cannot go
lower. One instrument, two moments.

    WITH THE TAX CORRECTED (labor_income_tax_rate 0.835)
    street     h_1   h_share1
    0.0448   -91.5      +18.8
    0.0500   -91.3      +16.9
    0.060    -91.0      +16.5

The tax fix closes tau_l (+33.4 -> -4.2), b (+25.1 -> +2.9) and flips h_share1 to
+18.8. **And then the street goes INERT**: a 34 per cent move in a parameter whose
elasticity was 29 an hour earlier travels half a point.

WHY. Homelessness here is a MARGINAL choice and the margin is set by INCOME, not by
the street's size. labor_income_tax_rate is the level in the Benabou function, so
0.835 cuts the average tax from 30 per cent to about 21, and nobody is left near the
margin for the street to act on.

**So tau_l and h_1 cannot both be matched with the instruments now open.** Either the
tax is right and there is essentially no homelessness, or the tax is wrong at +33 per
cent and homelessness is reachable. This is a modelling question, not a tuning one.

The candidates for putting households near the margin, all the author's call:
`y_grid_kappa` (bottom node mass, fixed at 3.2, so the poorest node is 0.198 per
cent of households); the transfer floors; the rent level, where the cheapest unit
costs 16.55 times the LOWEST net income.

## OPEN WITH THE AUTHOR

1. **The newborn endowment double count**, still unfixed and now cheap: an
   INERT_CHANGES entry keyed on `newborn_endowment_scale=0.0` would keep the archive
   pooled, since every point has it at zero. The fix embeds a design choice --
   delete `newborn_transfer_1`, or keep it and add it to `objective` -- and that is
   the author's to make.
2. **Whether to use a negative newborn endowment against the data.** The 2022 SCF
   says every productivity node's MEAN non-housing net worth is positive, the bottom
   quintile's at +0.044 of average wage income. 20 per cent of that quintile are
   negative, but the model sets a mean per node and cannot represent the dispersion.

## SETTLED TONIGHT

- pi_eu is targeted at 0.139, verified in the Fortran parameter, the MOMENT line and
  TARGET_OVERRIDE. The 4.85 per cent the author saw is `p_m`, the SMI population
  share. Nothing is calibrated to it.
- emp_homeless is inside ten per cent and the author said to leave it.
- Ten of twelve instruments had never moved until the joint step; the author noticed
  before the loop did. `tau_l` is now closable at labor_income_tax_rate 0.835, which
  the Benabou algebra gives independently as 0.833.

## THE SEARCH IS A NEWTON SOLVER NOW, AND IT SPLITS THE BLOCK IN TWO

`code/newton.py`, built 3 September on the author's *"since each equilibrium is
now fast to solve, don't you think that using a nelder mead type algorithm would
be best now?"*.  Two phases: `--jacobian` emits sixteen INDEPENDENT perturbation
lines, `--step` builds the Jacobian and emits a full, half and quarter step.

**Two solver bugs found and fixed in the first step, both in newton.py.**

1. THE RIDGE WAS ANNIHILATING THE SEARCH.  A column is d(residual)/d(instrument)
   in raw units and the units are incommensurable -- the finite-difference step is
   3.36 for value_of_life and 0.00032 for bottom_productivity_level -- so the raw
   J^T J diagonal ran 0.109 to 2.24e5 and one ridge set from the largest was over
   a hundred times the entire diagonal of eleven of fifteen instruments.  The step
   moved everything under one per cent from a 68 per cent residual and looked
   converged.  Columns are now scaled by the largest move the instrument is
   allowed in one iteration, bound or trust region, whichever binds.
2. THE TRUNCATED SVD WAS A UNIFORM RIDGE, which shrinks the identified directions
   along with the unidentified.  It is now a real truncation by a Jacobi sweep on
   the symmetric k-by-k matrix; the sweep reconstructs to 3e-14 and reproduces a
   direct solve to machine precision with nothing truncated.

**The first step then separated the block cleanly, and this is the finding that
shapes everything after it.**  Predicted versus actual at the full step:

    twelve moments within a few points   b -0.3, cbar 0.5, pi_eu 0.1, sigma_y 0.7,
                                         beta 0.4, gamma 0.6, omega_l 1.0,
                                         theta 1.1, tau_l 1.3, aleph -2.8,
                                         lambda_d 4.6, pi_V -6.2
    h_share1      predicted   0.0   actual  +126.7
    h_1           predicted  -0.3   actual   -84.0
    emp_homeless  predicted  -9.2   actual   +46.4
    h_2           predicted   3.9   actual   +18.3

On the twelve, Newton did its job: b, the worst moment in the block, went 67.6 ->
15.8 in ONE step, and tau_l, lambda_d, pi_V and omega_l all closed inside five.

The four are the homelessness moments and they are NOT DIFFERENTIABLE here.  At
this point `DIAG homeless who could afford it on INCOME ALONE = 0.9385`: 94 per
cent of the model's homeless can pay for housing and choose the street, so who is
homeless is a knife-edge discrete choice.  The derivative is genuinely near zero
locally -- the Jacobian measured it right -- and then it flips.  size_homelessness
moved 2.7 per cent and the homelessness rate fell 84.

So `NONSMOOTH` in newton.py takes those four rows out of the LINEAR SOLVE and
holds their four instruments.  **They are not conceded**: the moments stay in the
residual vector and in every report, the instruments keep their bounds, and the
block is to be closed by a MEASURED BRACKET.  Dropping a row from a linear model
is a statement about the derivative, not about the target.

## THE BOTTOM PRODUCTIVITY NODE IS DESTITUTE AND EMPTY

Asked by the author why homelessness is not coming from the poorest households.
`y_grid_kappa=3.2` fixes the bottom node's mass at exactly (1/7)**3.2 = 0.198 per
cent of households against a working-age homeless mass of 3.52 per cent, so even
if every bottom-node household were on the street they would be 5.6 per cent of
the homeless.  Measured, not argued: an 8 per cent move in
bottom_productivity_level takes emp_homeless from 0.611113 to 0.611115.  It is the
weakest of the fifteen columns by three orders of magnitude and pinned at its
lower bound.  The instrument with leverage is the MASS, `y_grid_kappa`, and it is
deliberately fixed -- next_batch.py:438.  Opening it is with the author.

## OPEN WITH THE AUTHOR: the newborn endowment is delivered twice

The author asked for a NEGATIVE newborn endowment, so the young start with debt
and more of them become homeless.  h_share1 is below the data, so the sign is
right and it is the one direction the instrument could not travel before.

It cannot be wired up yet.  In `calculate_after_tax_wealth` (22614-23022) both
branches at 22680-22690 put `newborn_age_transfer(age_index)` into `bequest_1`,
and `inheritance_age_grid` runs 1..60 so age 1 is in it; then 22975-22989 add
`newborn_transfer_1` -- the SAME quantity under the live uniform path, since
`max_initial_endowment` (24679) and `newborn_age_transfer(1)` (11817) have the
same definition and both scaling arrays are 1.  So the endowment enters cash on
hand TWICE at age 1.  `objective` (22105-22612) has the bequest half only and
never calls calculate_after_tax_wealth, so it counts it ONCE: the choice problem
and the wealth accounting differ by one endowment.

Invisible today because every live vector has newborn_endowment_scale=0.  With a
negative scale the debt is doubled in one path and single in the other.

Also: the production build is -O3 with NO -ffpe-trap, and the `consumption <= 0`
sites only PRINT ("internal eror") -- they do not guard the utility call.  A debt
big enough to drive consumption negative would archive garbage silently, so the
first negative bracket must be checked in the LOG, not in the point file.

## BLOCK 1 IS ONE JOINT ROUND, AND IT IS CONVERGING

The open round's worst gap today: **1188% -> 175% -> 154% -> 70% -> 64.1%**.

Best point `point_538b363d6e`, 46 points in this economy, 5 of 21 inside ten.

    cbar          -70.2%   max_food_cost = 0.0130        <- binding, open
    lambda_d      -55.1%   addiction_scalar_1 = 0.03680
    theta         -50.8%   relative_share_of_addiction_1 = 0.463
    pi_eu         -48.3%   probability_becoming_unemployed = 0.0122
    sigma_y       -39.2%   kkk_sigma_scale = 2.20949
    aleph         -36.3%   value_of_life = 42.0
    h_share1      -35.9%   newborn_endowment_scale = 0.0 (one-sided, at floor)
    emp_homeless  +35.0%   bottom_productivity_level = 0.004
    tau_l         +33.1%   labor_income_tax_rate = 0.7522432
    b             -30.3%   lambda_addiction = 2.69141
    h_1           -29.9%   size_homelessness = 0.0425
    pi_V          +17.1%   probability_of_voucher_benchmark_used = 0.052
    h_2           -11.2%   smallest_rental_relative_to_lowest_income = 0.114
    beta           +8.2%   discount_factor = 0.945                      *
    p_m            -8.2%   smi_onset_level = 0.002761206                *
    gamma          -6.7%   relative_share_of_housing = 0.100            *
    omega_l      inside 10 -- relative_share_of_leisure = 0.9693        *

`CORRECT_67.txt`, 12 lines, running on three workers.

## WHAT IS PARKED, AND WHY

`h_share5`, old-age homelessness, on the author's instruction: *"Ignore the old
homelessness for now. Just calibrate the rest of the block first."* It was 765
per cent out and dominates a MINIMAX, so nothing else could be ranked while it
was scored. `ssi_floor_level` still owns it and is idle. Restoring it is
deleting one line from UNSCORED.

`w_bot` is unscored: with one beta there is no second factor to aim at it. It
reads 0.021 against 0.025 anyway.

## THE THREE THINGS THE AUTHOR HAS ASKED FOR AND NOT YET GOT

1. **The SSI asset test.** Real SSI has a $2,000 limit, about 0.03 of the
   average wage index. The floor lives in `model_ss_benefits(employment_index)`,
   a function of the productivity type only, so an asset test means threading
   wealth through `calculate_income` -- **19 call sites** -- or applying the
   floor at each site where assets are known. Deferred to the age-profile work,
   which is where it bites, on the author's own sequencing.
2. **Their third instruction of 18:20**, which arrived truncated at "Third,".
3. **State SSI supplements**, worth about +0.02 on the floor. Measured at 0.195
   in `batch_joint2_1820.txt` line 4.

## THE FINDING THAT WILL DECIDE THE AGE PROFILE

The street carries **no disutility at all**. Housing enters preferences only as
`housing_size**((1-sigma)*gamma)`, and `mu_homeless` is the addiction recovery
hazard, not a homelessness penalty. So a household prefers the street below an
income of **0.4579** -- 0.72 of average labour income -- and retiree income runs
0.400 to 0.510. That is why the old are homeless here, and why no transfer
programme closes it: at a floor above 0.75082 every retiree gets the same
benefit, because PIA is capped there.

Full argument in `SSI_FLOOR_ANALYSIS.md` and `US_RETIREE_TRANSFERS.md`.

## THE CLIFF, which the age profile has to be read off

At the calibrated leisure weight, across a step of 0.0116 in the street's size:

    street 0.0384 -> h_1 0.00068, band1 0.6804, band5 0.2725
    street 0.0500 -> h_1 0.01420, band1 0.0335, band5 0.9640

h_1's target is inside that interval and the composition inverts across it.
Rungs at 0.0425, 0.0448 and 0.0470 are in the archive or in flight.

## Solve time

About 2.5 minutes at one beta type; 5 minutes 0 seconds was measured at two.
