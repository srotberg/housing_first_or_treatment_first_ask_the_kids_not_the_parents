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
