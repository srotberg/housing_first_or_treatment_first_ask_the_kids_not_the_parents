# Bounds checks

A record of runs of the model under `-fcheck=bounds,pointer`. One dated section
per check. A check states the exact compile line, whether a single violation was
raised, and how far the run got, because "it ran" and "it ran clean" are
different claims and only the second one is worth anything.

---

## 2026-09-03 -- KKK_process (`fixed_productivity=0`), first bounds check

The model had just been switched to a second productivity process, `KKK_process`,
selected by `fixed_productivity=0`. The new code all runs in setup: the
productivity grid, its retirement rows, `log_y_edge`, the newborn draw, social
security and the unemployment tilt. It had passed `-fsyntax-only` and had never
been bounds checked. Source at commit `2d01c6b`, branch
`claude/two-period-addiction-hazard-d7gb61`.

### (i) The compile line

    gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace -fimplicit-none \
        -ffree-line-length-none -mcmodel=medium -fopenmp \
        code/housing_first_or_treatment_first_SR_v1.f90 -o /tmp/bc_kkk

Exit 0, 25 seconds, gfortran 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1).

The vector run is LINE 2 of `code/batch_kkk.txt`:

    ssi_floor_takeup=0.5 fixed_productivity=0 kkk_s_deviation_bottom=3.35

`run_one_point.sh` was not modified and not invoked. Its scaffolding was
reproduced by hand: the `declare -A P=( ... )` block was extracted verbatim from
the script with `awk` and `eval`ed, the three overrides applied the same way the
script applies `"$@"`, `addiction_scalar_1` written to `B_SWEEP_GRID.txt` and the
other 59 names written to `PARAM_HANDOVER.txt` in the same
`printf '"%s" %s\n'` form. No `calibration_state.dat` and no
`calibration_distribution*.dat` were present, so the point started cold from the
declarations plus its own handover. The run directory was a scratch `code/`
with a `../data` symlink to the repository's `data/`, because the model resolves
`../data/us_mh_onset_shape.csv` and `../data/us_mortality_multipliers.csv`
relative to the working directory and stops without them. Environment as the
script sets it: `ulimit -s unlimited`, `OMP_NUM_THREADS=4`, `OMP_STACKSIZE=512M`,
`GFORTRAN_UNBUFFERED_ALL=1`.

The handover was applied in full: 59 `HANDOVER` lines, 0 `HANDOVER IGNORED`.

### (ii) Violations raised: NONE

**Not one bound violation and not one pointer violation was raised.** No
`Fortran runtime error`, no `out of bounds`, no `Backtrace`, no
`Segmentation fault`, no "not associated". The scan of the whole 105,932-byte
log for those strings returns nothing.

### Compile-time warnings, which are a separate matter

The build is not silent. Seven warnings were emitted, all of them in the
TRANSITION block and none of them on the KKK path or on anything the benchmark
solve reaches. They are recorded here because a bounds-checked build is the one
place they surface, not because this check found them firing.

    housing_first_or_treatment_first_SR_v1.f90:40964:26:
    40964 |   housing_price(transition_length-25:transition_length-1)=housing_price(transition_length)
          |                1
    Warning: Lower array reference at (1) is out of bounds (-24 < 1) in dimension 1

    housing_first_or_treatment_first_SR_v1.f90:40985:30:
    40985 |   lump_sum_transfer(transition_length-25:transition_Length-1)=lump_sum_transfer(transition_length)
          |                    1
    Warning: Lower array reference at (1) is out of bounds (-24 < 1) in dimension 1

    housing_first_or_treatment_first_SR_v1.f90:41280:56:
    41280 |   write(2,'(F10.8)') homeownership_by_age(2,:)
          |                                          1
    Warning: Array reference at (1) is out of bounds (2 > 1) in dimension 1

    housing_first_or_treatment_first_SR_v1.f90:41227:54  housing_price(i)
    housing_first_or_treatment_first_SR_v1.f90:41240:54  housing_stock(i)
    housing_first_or_treatment_first_SR_v1.f90:41240:78  total_housing_demand(i)
    housing_first_or_treatment_first_SR_v1.f90:41267:58  lump_sum_transfer(i)
    Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
      (each inside `do i=0,transition_length`)

The first two are the compiler evaluating `transition_length` as 1 at compile
time; the last five are `do i=0,...` against arrays whose lower bound is 1. They
belong to whoever owns the transition, and per
`code/stylized/TRANSITION_LESSONS.md` section 7 they are worth checking against
the stylized model's transition before they are closed. **This check says
nothing about whether they fire**, because the transition never ran.

### (iii) How far the run got

Far past the three milestones asked for, and it was killed rather than stopping.

* **(a) Grid construction and the "KKK productivity process live" write** --
  reached, log line 189.
* **(b) `create_newborn_employment_probability` and `verify_newborn_process`** --
  reached and clean:

        newborn process: p(1)=  0.12128700000000001       rows not summing to one=           0  rows off p(1)=           0

* **(c) At least the first 25 ages of backward induction** -- 145 `AGE_TIME`
  lines. Backward induction runs from the oldest age, so the first ages solved
  are exactly the retirement rows of the grid this change had to fill in
  (fix 1 in `code/KKK_VS_SIGMA_Y.md`), and those were all reached. The first
  pass ran the full 60 ages down to age 2:

        AGE_TIME age=  60  wall_s=      0.08  cpu_s=      0.33
        ...
        AGE_TIME age=   2  wall_s=      2.22  cpu_s=      7.99

  It then completed a full distribution sweep --
  `DIST_DONE sweeps=  60  final_distance=  4.1376388714990664E-004` -- and was
  25 ages into a second backward induction (`AGE_TIME age=  34`) when it was
  killed at roughly nine minutes. Two full value-function passes over the new
  retirement rows and one complete distribution sweep, all clean.

### The five numbers, verbatim from stdout

For checking the process against the arithmetic in `code/KKK_VS_SIGMA_Y.md`:

     KKK productivity process live. sd of log y at age 1 =  0.40903300600318310
       grid age 1  :  0.23276647231993933       0.35885878369756974       0.55325676998657514       0.85296241151488639        1.3150220926803016        2.0273848892895781        3.1256429167224478
       grid last working age:  0.19700978439390091       0.32016503177804023       0.52030739431948192       0.84556324930328386        1.3741438549176437        2.2331520859779501        3.6291456831545150
       masses at age 1:   2.0923206540859290E-003   3.1575798741540706E-002  0.19782980557482699       0.41176128354274028       0.28479342028665156        6.5446625789998089E-002   6.5007454101564440E-003

     KKK grid: bottom half's share of productivity =  0.35029113148163599       target =  0.17199999999999999

The line immediately after the four is worth having too, because it is fix 3 in
`KKK_VS_SIGMA_Y.md` (the `exp(var/2)` constant subtracted in logs) reporting
that it worked:

     mean productivity at age 1 =   1.0000000000000002

Read against `code/KKK_VS_SIGMA_Y.md`: sd of log y at age 1 is 0.40903 against
the document's 0.4090; the bottom node's mass is 0.20923 per cent against the
design target of 0.198 per cent that `kkk_s_deviation_bottom=3.35` was chosen
for; and the bottom half's share is 35.03 per cent against a target of 17.2, so
the factor of two the document describes is confirmed live in the model at the
author's own numbers. The grid does fan: the bottom node falls from 0.2328 at
age 1 to 0.1970 at the last working age and the top rises from 3.126 to 3.629.
