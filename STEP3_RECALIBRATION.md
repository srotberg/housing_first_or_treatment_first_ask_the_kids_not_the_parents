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
