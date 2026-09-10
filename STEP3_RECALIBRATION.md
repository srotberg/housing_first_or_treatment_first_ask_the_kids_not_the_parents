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
