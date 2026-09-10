# Step 3: the fast one-class recalibration

`.gitignore` excludes `*.log`, so without this file every number below lives
only on an ephemeral container's disk.

## The settings, and where each one lives

| setting | value | where | why |
| --- | --- | --- | --- |
| `child_penalty_classes` | 1 | compile time, line 3844 | 28 min a point becomes about 7 |
| `voucher_exclusion_states` | 0 | compile time, line 359 | the benchmark has no conditionality, so the third voucher slice is dead weight HERE |
| `calibrate_penalty_child_addicted` | 0 | compile time, line 858 | delta_d is HELD at 0.36 |
| `calibrate_penalty_child_homeless` | 0 | compile time, line 892 | delta_h is HELD at 0.14, provisionally |
| `calibrate_weight_on_child` | 1 | compile time, line 497 | omega_c is calibrated |
| `measure_child_gap` | 1 | handover, line 514 | omega must be measured for omega_c to be calibrated |
| `sweep_addiction_scalar` | 0 | compile time, line 1861 | 1 is a fixed-parameter point run; the calibration loop needs 0 |

`voucher_exclusion_states` MUST go back to 1 for any counterfactual arm: it
dimensions the arrays the arms read from the benchmark.

## Why this is a VARIANT and not an edit to the master

`make_variant.py` already exists for exactly this and states the reason: the tag
of a point is the md5 of its vector and the MODEL stamp is the md5 of the master
source, so an edit to the master resets every point in `points/` for a run that
is not a calibration point at all. Step 4 returns to four classes, so the master
must still be the four-class model when it gets there.

## Why step 3 is TWO runs and not one

The frozen-equilibrium loop and `print_all_moments` both sit inside
`if (sweep_addiction_scalar==1)` at line 42938. A calibration run has that
switch at 0, so it never reaches either: it prints its per-loop parameter
updates and no moments block at all.

So the shape is:

* **Run A**, the `calib1` variant: `sweep_addiction_scalar=0`, the calibration
  loop runs and moves every parameter except the child ones.
* **Run B**, the `point1` variant: `sweep_addiction_scalar` left at 1, at Run A's
  converged vector, one class. This reaches the frozen loop and prints the gap
  table after `FROZEN CONVERGED`, which is the block the report is read from.

Reading Run A's last loop instead of Run B would be reading a pre-frozen state,
which is what the banner at the top of `ENGINE.md` is the record of: `b` read
0.0795 before the frozen loop and 0.0849 after, a 6.4 per cent difference.

## The standing builds, on the master

Both pass. gfortran 13.3.0, which is NOT the compiler the archive was measured
on -- this container had no Fortran compiler at all and one was installed. That
is a cross-container difference of exactly the kind `ENGINE.md` records under
"the container is part of the measurement", and it is stated here rather than
left to be discovered.

    -O1 -fcheck=bounds,pointer -g -fbacktrace                          7 warnings, 0 errors
    -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace   7 warnings, 0 errors

Seven warnings is the documented pre-existing count.


# THE CONFIGURATION MOVED TWICE WHILE THIS WAS BEING SET UP

Recorded because three briefs gave three different answers within one session and
a reader of the results has to know which one the run actually used.

| | delta_d | delta_h | rho | classes | omega_c |
| --- | --- | --- | --- | --- | --- |
| step 3 brief | 0.36 held | 0.14 held, provisional | 0.35, fixed | 1 | calibrated |
| `ODDS_RATIO_FIT.md`, first update | 0.36 held | externally set | **calibrated** on the odds ratio | 1 | calibrated |
| the two-class commit, latest | 0.36 held | **0 , fixed** | **0.30, assigned** | **2** by default | calibrated |

**THE RUN USES THE LATEST VALUES AND THE BRIEF'S CLASS COUNT.** delta_d 0.36,
delta_h 0, rho 0.30 assigned with its adjuster at zero, omega_c calibrated, and
`child_penalty_classes=1`.

Why one class rather than the new default of two: the brief's class setting is a
SPEED setting and says so -- *"28 min a point becomes ~7"* -- not a claim about
the model. The two-class change already cut the employment grid from 28 nodes to
14; one class halves it again to 7. Nothing about step 3 was superseded by it.
**The benchmark that goes in the paper is the two-class one, and step 4
re-measures there. Nothing fitted here transfers without being re-measured.**

## THE HOMELESSNESS ODDS RATIO NOW HAS NO INSTRUMENT, AND THAT CHANGES THE BUILD

Both of its candidate instruments are assigned: delta_h at 0 and rho at 0.30. So
`calibrate_penalty_child_homeless` goes to 0 in the variant, and the reason is
not tidiness. Its gap is about 0.7 against a stopping rule of 5e-2, and
`distance_penalty_child_homeless` sits in the outer `do while`. Left live it
would hold that loop open until the cap on every single run while no parameter
in the model could close it -- and that failure is invisible in a log. The loop
does not error; it simply never terminates, and every other parameter goes on
being stepped around a distance that is pinned.

The same argument closes `calibrate_penalty_child_addicted`: delta_d pins near
1.11 against a target of 2.00 with the classes off, so its moment cannot be met
here either.

## FOUR OF THE EIGHT OUT-OF-BAND MOMENTS ARE NOT IN THE AUTHOR'S LOSS

Read out of `gaps.py`'s own sets rather than assumed, because the recalibration
cannot be asked for what nothing can reach:

| moment | gap in the brief | status | instrument |
| --- | --- | --- | --- |
| `w_bot` | +268% | `UNSCORED`, and a BAND of 0.008-0.05 | none: `discount_factor_impatient` retired with the second beta |
| `kappa_uem` | +174% | scored | `kappa_uem` |
| `h_3` | -89% | `SKIP`, conceded | none: h_3 = 2 x h_2 by the 5 September ladder ruling |
| `kappa_ued` | +27% | `UNSCORED` | `multiple_of_probabilities_of_employment_if_addicted` |
| `h_2` | +25% | scored | `smallest_rental_relative_to_lowest_income` |
| `lambda_m` | -24% | scored | `lambda_m` -- see below |
| `y_u` | -23% | not scored: mortality pinned at 8 by the author | none |
| `beta` | +17% | scored | `discount_factor` |

So **four** of the eight are moments the author has already taken out of the
loss, and only `kappa_uem`, `h_2`, `lambda_m` and `beta` are scored moments this
recalibration can work on.

**`lambda_m` HAS NO ROW IN `gaps.OWN` AND IT IS INTERNALLY CALIBRATED.**
`distance_lambda_m` sits in the outer `do while` and the update steps it on
`model_smi_share_of_homeless` against `smi_share_of_homeless_data`, which is
exactly that moment. This is the same class of fault `gaps.py` already records
against its own `y_h` and `ssi_floor_level` rows: the report named one parameter
and the walk moved another. NOT fixed here -- that file is the author's report
and editing it is not step 3's job -- but the row is carried in step 3's own
table with its source named.


# RUN A, THE CALIBRATION LOOP: 45 loops, and omega_c IS AT ITS CEILING

`variant_calib1_20260910T160538Z.log`, 45 loops in about 100 minutes, 2.2 min a
loop. Stopped by PID rather than left to the cap, for the reasons below. 88 of 88
handover, so the model took the vector it was given.

## omega_c WALKS TO 1.0 AND PINS THERE. IT IS NOT A FITTED PARAMETER.

The brief asked for this to be said plainly if it happened, and it happened:

    omega_c   0.17 -> 0.288 -> 0.403 -> 0.490 -> 0.550 -> 0.634 -> 0.710
           -> 0.788 -> 0.837 -> 0.913 -> 0.983 -> 1.0000 and stays

**21 of the last 25 updates sit at exactly 1.0000.** The final value in
`step3_fitted_vector.txt` is `weight_on_child=1.0000000000000000`. Reporting that
as a calibrated weight would be reporting a parameter that was never fitted.

## BUT THE CEILING IS NOT THE WHOLE STORY, AND THIS CORRECTS THE STRUCTURAL CLAIM

`ODDS_RATIO_FIT.md` says omega "saturates near 0.037 even at the parameter's
ceiling of 1.0". At ONE class that is not what the log shows. With omega_c pinned
at exactly 1.0 the measured gap ranges over

    min +0.01385    max +0.17365    spread 0.15980

against a target of 0.18343. **The spread at a single fixed parameter value is
0.87 times the target.** So the moment does reach the neighbourhood of its target
-- several readings land at +0.18629, +0.19512, +0.20873, +0.21819, +0.26734 --
and the distance drops as low as 0.00145, which in a log reads exactly like
convergence.

It is not convergence. Over those same 21 readings the BASELINE, which is the
gap's denominator, ranges from 0.01532 to 0.09104 -- a factor of six. The gap is
tracking where `b` happened to be that loop, not what the child term is worth.

The Fortran's own comment beside `weight_on_child_adjuster` predicted this in so
many words: *"the measured gap has been +4.31, +1.31, -0.18, -0.23, +0.93 and
-0.29 across consecutive loops at an omega that never left 0.02."*

**THE GUARD THAT WOULD CATCH THIS IS IN THE WRONG FILE.**
`ODDS_RATIO_FIT.md` records that `fit_child_parameters.py` "refuses an omega_c
step unless BOTH readings clear five times the frozen distance". That guard is in
the PYTHON fitter. The Fortran's own internal update has no such test, so the
internal loop steps omega_c on noise and walks it to the bound. That is a real
gap between the two fitters and it is why raising the adjuster, which was the
right thing to do to make the parameter move at all, also made it reach the
ceiling on readings that mean nothing.

## AND THE RECALIBRATION ITSELF DOES NOT CONVERGE. b IS THE BINDING PROBLEM.

    distance_addiction_scalar, last ten loops
    0.0572  0.0402  0.0289  0.0239  0.0305  0.0569  0.0421  0.0613  0.0639  0.0737

It falls to 0.0239 and climbs back to 0.0737. `b` oscillates between 0.0153 and
0.0910 against a target of 0.0890 with no sign of narrowing, and
`addiction_scalar_1` has been walked from 0.0025499 down to 0.00055163, a factor
of 4.6. This is the cliff the project already records -- *"total users went
0.947, 0.759, 0.000158 across b of 0.05, 0.06, 0.12: flat, then a cliff"* -- and
it is ENGINE.md's **pin b and lambda_d first** rule reappearing INSIDE the
internal loop rather than outside it.

**omega_c cannot be fitted until b is on target**, because b is the omega gap's
denominator. That ordering is not a preference, it is arithmetic.

## WHAT 45 LOOPS MOVED, for the record

Seventeen parameters moved. `step3_fitted_vector.txt` carries all of them.

| parameter | start | after 45 loops |
| --- | --- | --- |
| `weight_on_child` | 0.17 | **1.0000 (ceiling)** |
| `addiction_scalar_1` | 0.0025499 | 0.00055163 |
| `lambda_addiction` | 0 | 23.924 |
| `value_of_life` | 177.77 | 330.17 |
| `relative_share_of_leisure` | 4.23887 | 7.8254 |
| `kappa_uem` | 1 | 16.274 |
| `size_homelessness` | 2.7525e-05 | 0.0021115 |
| `smallest_rental_relative_to_lowest_income` | 0.102084 | 0.030002 |
| `discount_factor` | 0.934317 | 0.932262 |
| `labor_income_tax_rate` | 0.782021 | 0.773384 |
| `largest_house_size` | 0.6 | 0.523502 |
| `relative_share_of_addiction_1` | 0.27 | 0.365338 |
| `mu_homeless` | 0.560903 | 0.759164 |
| `max_food_cost` | 0.0412539 | 0.0381581 |
| `probability_becoming_unemployed` | 0.0196932 | 0.0126722 |
| `probability_of_voucher_benchmark_used` | 0.0433173 | 0.0485831 |
| `rho_d` | 1 | 0.05 |

`lambda_addiction` going from 0 to 23.9 is the largest move in the table and it
is worth flagging on its own: it is the SUD dose-response gradient that
`EXPERIMENT_PLAN.md` records as deliberately FLAT at zero, with its own design
waiting on the author. The internal loop is free to move it and has moved it a
long way, against `addiction_scalar_1` falling 4.6-fold -- the two fight for the
same moments, which is part of why neither settles.

## WHY IT WAS STOPPED AT 45 RATHER THAN RUN TO THE CAP

The cap is 300 loops, about eleven hours. The internal convergence test is
roughly 1e-3 ABSOLUTE on forty-odd distances at once -- `employment_multiplier`
stood at 682 times its rule, `largest_house_size` at 491, `value_of_life` at 233
-- which is the "days of wall clock" the Fortran's own resume comment describes.
Nothing in 45 loops suggests it is heading for that, the question the brief
actually asked about omega_c is already answered, and the container is ephemeral.


# CORRECTION: THE CEILING OF 1.0 WAS A CAP THE AUTHOR HAS SINCE REJECTED

Written immediately on reading the other session's work, because the section
above would otherwise be read as "omega_c = 1.0 is the answer", and it is not.

`weight_on_child_cap` is now **25**, raised on the author's own question --
*"wait, why cant omega_c be larger than 1?"* -- with the reason recorded in
`OMEGA_STRUCTURE.md`: in the specification this model runs the child term is
ADDED, `V = u + beta*[phi*V' + (1-phi)*omega*X]`, so omega is a MULTIPLIER and
not a share, and nothing makes it improper above one. The bound belonged to a
weighted-average form the model does not use.

My `calib1` run was built before that change and carried the old hard cap of 1.0.
So **"omega_c walks to its ceiling" is a statement about a cap that no longer
exists**, and the fitted 1.0000 in `step3_fitted_vector.txt` is a bound artefact,
not an estimate. Anyone reading that vector should know it.

## WHAT THE RUN STILL SHOWS, AND IT CORROBORATES THE OTHER SESSION

Two things survive the correction, and the first is an independent confirmation
from a direction that session did not use.

**1. THE CAP WAS BINDING, MEASURED BY A SEARCH RATHER THAN BY AN ARGUMENT.** An
internal calibration loop, free to move omega_c and given an adjuster 250 times
the declared one, walked it from 0.17 to the top of its admissible range in
twelve loops and then held it there for 21 of the next 25 updates. A parameter
that wanted to stop below 1.0 would have stopped. That is consistent with
`OMEGA_STRUCTURE.md`'s measured ladder, which puts the target at

    omega_c ~ 1.39, itself a LOWER bound

and it was reached without using their cross-run statistic at all.

**2. AND THE INTERNAL MOMENT CANNOT DISCIPLINE omega_c, WHICH IS INDEPENDENT OF
THE CAP.** This is the part that is new and that still stands. With omega_c
pinned at exactly 1.0, the model's own internal gap ranged +0.01385 to +0.17365
-- a spread of 0.87 times its target -- while the BASELINE it is divided by
ranged 0.01532 to 0.09104, a factor of six. The readings near omega_c = 1
straddle the 0.18343 target rather than sitting below it.

That is the quantitative case for the choice the other session made on other
grounds. `OMEGA_STRUCTURE.md` notes the internal moment read 2.03 per cent where
the cross-run statistic read 2.24 and calls the cross-run one "the cleaner", the
difference being that the internal version holds some general equilibrium objects
fixed. Measured inside the loop, the difference is not 0.2 percentage points of
bias; it is a spread comparable to the whole target, because the denominator is
moving. **So the ladder of separate runs is not merely cleaner, it is the only
one of the two that can identify the parameter** -- and the Fortran's internal
omega_c update should not be used for this moment until it carries the noise
guard `fit_child_parameters.py` already has.

**3. AND b IS STILL THE BINDING PROBLEM.** Nothing above touches it. The
one-class internal recalibration does not converge: `b` oscillates 0.0153 to
0.0910 against 0.0890 over 45 loops with no narrowing, and it is the omega gap's
denominator, which is why the gap's spread is what it is. Both findings are the
same fact seen twice.


# THE RESULT: THE FULL GAP TABLE, AND THE RECALIBRATION MADE THINGS WORSE

Two `point1` runs, BOTH on source `e1d609a8`, both `FROZEN CONVERGED`, both in
this one container -- which is the project's standing requirement for a
controlled pair, because the cross-container spread on `w_bot` alone is 1.8e-2.

    start       variant_point1_20260910T184514Z.log   FROZEN CONVERGED, 2 passes, 1.29e-5
    45 loops    variant_point1_20260910T185405Z.log   FROZEN CONVERGED, 2 passes, 5.89e-5

Read after `FROZEN CONVERGED`, and scored by `gaps.py`'s own `load()` and
`gap()` rather than by any logic of mine, so this table and the author's own
report cannot disagree about what is in the loss.

## A CORRECTION I HAVE TO MAKE FIRST: THE LOSS IS NOT A MINIMAX

I reported a minimax earlier in this session. It is not the objective. The
author, 4 September: *"i want you to use a better measure than minmax. use sum
of squared residuals"*, and `gaps.py`'s live promotion test is
`improved = _sq < old_sq`.

Two things in that file still say otherwise and both are stale:

* its module docstring -- *"THE LOSS IS THE AUTHOR'S OWN ... A MINIMAX over the
  scored moments"*;
* `_better_vec`, the lexicographic comparator, which is **defined at line 618 and
  never called**.

That matters here rather than being a tidiness point, because the two objectives
give OPPOSITE answers on this pair, and I nearly reported the wrong one.

## THE BASELINE, one class, delta_d 0.36, delta_h 0, rho 0.30, omega_c 0.17

| moment | instrument | model | target | gap | in the loss |
| --- | --- | --- | --- | --- | --- |
| `kappa_uem` | `kappa_uem` | 0.82134 | 0.3 | +173.8% | yes |
| `h_3` | none: h_3 = 2 x h_2 by the ladder ruling | 0.0671208 | 0.626723 | -89.3% | **no** |
| `omega_c` | `weight_on_child` | 0.0206389 | 0.183432 | -88.7% | yes |
| `w_bot` | none: `discount_factor_impatient` retired with the second beta | 0.0917651 | 0.025 | +267.1% | **no** |
| `h_share5` | `rr_homeless_old_level` | 0.0133001 | 0.075 | -82.3% | yes |
| `y_h` | `homeless_job_penalty_pp` | 0.0596907 | 0.191 | -68.7% | yes |
| `kappa_ued` | `multiple_of_probabilities_of_employment_if_addicted` | 0.206796 | 0.1625 | +27.3% | **no** |
| `y_u` | none: mortality pinned at 8 by the author | 0.55066 | 0.74 | -25.6% | yes |
| `lambda_m` | `lambda_m` -- Fortran update, no `gaps.OWN` row | 0.19152 | 0.25 | -23.4% | yes |
| `h_2` | `smallest_rental_relative_to_lowest_income` | 0.0976233 | 0.08 | +22.0% | yes |
| `h_share1` | `newborn_endowment_scale` | 0.213237 | 0.26 | -18.0% | **no** |
| `sud_homeless` | `lambda_addiction` | 0.253612 | 0.217 | +16.9% | yes |
| `beta` | `discount_factor` | 3.49573 | 3 | +16.5% | yes |
| `tau_u` | `utility_cost_of_treatment` | 0.224843 | 0.245 | -8.2% | yes |
| `h_1` | `size_homelessness` | 0.012529 | 0.0116 | +8.0% | yes |
| `tau_l` | `labor_income_tax_rate` | 0.207809 | 0.224 | -7.2% | yes |
| `theta` | `relative_share_of_addiction_1` | 0.131066 | 0.14098 | -7.0% | yes |
| `aleph` | `value_of_life` | 74.7899 | 80 | -6.5% | yes |
| `b` | `addiction_scalar_1` | 0.0833427 | 0.089 | -6.4% | yes |
| `pi_V` | `probability_of_voucher_benchmark_used` | 0.252134 | 0.266 | -5.2% | yes |
| `omega_l` | `relative_share_of_leisure` | 0.412999 | 0.4 | +3.2% | yes |
| `mu_H` | `mu_homeless` | 1.43064 | 1.47321 | -2.9% | yes |
| `lambda_d` | `addiction_onset_base` | 0.0357809 | 0.0368 | -2.8% | yes |
| `pi_eu` | `probability_becoming_unemployed` | 0.0500456 | 0.049 | +2.1% | yes |
| `burden50` | none: reported, not targeted | 0.177862 | 0.175 | +1.6% | yes |
| `emp_homeless` | `homeless_job_penalty_pp` | 0.453939 | 0.46 | -1.3% | yes |
| `cbar` | `max_food_cost` | 0.00424153 | 0.0042 | +1.0% | yes |
| `p_m` | `smi_onset_level` | 0.0489272 | 0.048453 | +1.0% | yes |
| `gamma` | `relative_share_of_housing` | 0.266161 | 0.268 | -0.7% | yes |
| `sigma_y` | `kkk_sigma_scale` | 0.172199 | 0.172 | +0.1% | yes |

Scored moments: 26. Outside ten per cent: 9. Worst 173.8% on `kappa_uem`. Median 7.0%. Sum of squared residuals 5.2196.

## THE CONTROLLED PAIR

| moment | start | after 45 loops | target | gap start | gap after |
| --- | --- | --- | --- | --- | --- |
| `kappa_uem` | 0.82134 | 0.306047 | 0.3 | 173.8% | 2.0% |
| `omega_c` | 0.0206389 | 0.0861065 | 0.183432 | 88.7% | 53.1% |
| `beta` | 3.49573 | 2.90427 | 3 | 16.5% | 3.2% |
| `tau_l` | 0.207809 | 0.226978 | 0.224 | 7.2% | 1.3% |
| `y_h` | 0.0596907 | 0.0674221 | 0.191 | 68.7% | 64.7% |
| `mu_H` | 1.43064 | 1.46536 | 1.47321 | 2.9% | 0.5% |
| `aleph` | 74.7899 | 75.602 | 80 | 6.5% | 5.5% |
| `pi_V` | 0.252134 | 0.279448 | 0.266 | 5.2% | 5.1% |
| `omega_l` | 0.412999 | 0.419569 | 0.4 | 3.2% | 4.9% |
| `p_m` | 0.0489272 | 0.0466309 | 0.048453 | 1.0% | 3.3% |
| `sigma_y` | 0.172199 | 0.16327 | 0.172 | 0.1% | 5.1% |
| `h_share5` | 0.0133001 | 0.00609148 | 0.075 | 82.3% | 91.9% |
| `cbar` | 0.00424153 | 0.00477891 | 0.0042 | 1.0% | 13.8% |
| `h_1` | 0.012529 | 0.0148832 | 0.0116 | 8.0% | 28.3% |
| `pi_eu` | 0.0500456 | 0.0684996 | 0.049 | 2.1% | 39.8% |
| `gamma` | 0.266161 | 0.150423 | 0.268 | 0.7% | 43.9% |
| `y_u` | 0.55066 | 0.22107 | 0.74 | 25.6% | 70.1% |
| `emp_homeless` | 0.453939 | 0.226938 | 0.46 | 1.3% | 50.7% |
| `lambda_d` | 0.0357809 | 0.0169641 | 0.0368 | 2.8% | 53.9% |
| `theta` | 0.131066 | 0.0509121 | 0.14098 | 7.0% | 63.9% |
| `b` | 0.0833427 | 0.0294229 | 0.089 | 6.4% | 66.9% |
| `h_2` | 0.0976233 | 0.000247792 | 0.08 | 22.0% | 99.7% |
| `burden50` | 0.177862 | 0.0127488 | 0.175 | 1.6% | 92.7% |
| `sud_homeless` | 0.253612 | 0.456649 | 0.217 | 16.9% | 110.4% |
| `lambda_m` | 0.19152 | 0.548032 | 0.25 | 23.4% | 119.2% |
| `tau_u` | 0.224843 | 0.644732 | 0.245 | 8.2% | 163.2% |

| objective | start | after 45 loops | winner |
| --- | --- | --- | --- |
| **sum of squared residuals -- the live objective** | **5.2196** | **11.0590** | **the start, by 2.1x** |
| worst scored gap, printed beside it | 173.8% | 163.2% | the 45-loop point |
| moments outside ten per cent | 9 of 26 | 17 of 26 | the start |
| median scored gap | 7.0% | 50.7% | the start |
| moments improved / worsened | -- | 7 / 18 | the start |

## THE VERDICT: 45 LOOPS PRODUCED A WRECKED ECONOMY

Under the live objective the starting point wins by a factor of **2.1**. The
economy after 45 loops is not a worse calibration, it is a broken one:

    b        0.0294 against 0.0890   -- drug use a third of target
    h_2      0.000248 against 0.08   -- the cost burden essentially emptied
    tau_u    0.645 against 0.245     -- treatment take-up nearly tripled
    gamma    0.150 against 0.268     -- the housing share collapsed
    theta    0.0509 against 0.141

Eighteen of twenty-six scored moments got worse, seven improved, and the median
scored gap went from 7.0 per cent to 50.7.

**AND THE RETIRED OBJECTIVE WOULD HAVE PROMOTED IT.** The worst scored gap FELL,
173.8 per cent to 163.2, because the update repaired the one moment that was
binding -- `kappa_uem`, 173.8 per cent to 2.0 -- while eighteen others
deteriorated and the new worst, `tau_u` at 163.2, happened to land just under the
old one. `_better_vec` returns "better" on this pair.

That is precisely the failure the author's own instruction of 4 September was
aimed at, and `gaps.py` records the evidence that prompted it: *"Under a minimax
one bad moment sets the score and everything behind it is invisible."* It is also
the same shape as the `point_b2969f8ebb` case in `ENGINE.md` -- a wrecked
equilibrium whose one moment improved as a side effect -- except that there the
minimax rejected it and here it would not have. **So this pair is a second,
independent argument for the change the author already made**, and a reason to
delete the stale docstring and the dead comparator rather than leave them to be
read as live.

## THE BRIEF'S LIST OF EIGHT IS WRONG IN BOTH DIRECTIONS

Five of the eight are confirmed almost exactly, which is a real consistency check
-- those gaps were quoted off the FOUR-class benchmark and they survive at one
class with delta_h = 0 and rho = 0.30:

    kappa_uem  +174 brief, +173.8 measured
    h_2         +25 brief, +22.0
    lambda_m    -24 brief, -23.4
    y_u         -23 brief, -25.6
    beta        +17 brief, +16.5

**THREE OF THE EIGHT ARE NOT IN THE LOSS AT ALL**, so no recalibration can be
asked for them: `w_bot` (+267.1, `UNSCORED`, its instrument retired with the
second beta), `h_3` (-89.3, `SKIP`, it IS 2 x h_2 by the ladder ruling and has no
instrument), `kappa_ued` (+27.3, `UNSCORED`).

**AND IT OMITS FOUR SCORED MOMENTS THAT ARE BADLY OUT:**

| moment | gap | why it matters |
| --- | --- | --- |
| `omega_c` | -88.7% | the moment this session was sent to fit |
| `h_share5` | -82.3% | the 65+ share of the homeless, restored to the loss on 4 September |
| `y_h` | -68.7% | see below |
| `sud_homeless` | +16.9% | the untargeted half of the Gutwinski meta-regression |

**`y_h` HAS CROSSED OVER AND NOBODY HAS SAID SO.** `gaps.py` describes it as
*"the moment that says the model's homeless are the WRONG HOUSEHOLDS"*, sitting at
0.709 against 0.191 -- **271 per cent too HIGH**. It now reads 0.0597, **68.7 per
cent too LOW**. The composition fault has not been repaired; it has reversed
sign, and its instrument `homeless_job_penalty_pp` also owns `emp_homeless`,
which is at -1.3 per cent and would be given up to fix it.
