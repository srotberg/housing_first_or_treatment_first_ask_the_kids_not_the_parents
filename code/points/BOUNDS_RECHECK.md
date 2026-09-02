# Bounds re-check after the wealth-walk fix: the 11791 violation is gone

The same diagnostic procedure as `BOUNDS_CHECK.md`, repeated on the fixed
source. **The violation did not recur, and no new one fired.** The run went to
completion in 20 min 28 s with exit status 0, against a previous run that
aborted at 9 min 47 s.

Not a calibration point. No moment below is a measurement of anything: the
binary is `-O1` with bounds and pointer checking, and nothing here should be
read as a number about the economy.

## What was run

Source: `code/housing_first_or_treatment_first_SR_v1.f90` at branch head
`bec81dd`, unchanged since the fix in `d9ff1a8`.

    semantic hash   2f7c317e75          (python3 code/model_hash.py ...)
    md5             b8dc1077adc90fe0d9b497289e93e7c5
    compiler        GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0

The compiler was absent from this container and was installed, exactly as
`run_one_point.sh` does when it finds none. It is the same version the previous
bounds run used.

Build command, run in `code/`, 28 s, exit 0:

    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -fimplicit-none -O1 -ffree-line-length-none -g -fbacktrace \
        -fcheck=bounds,pointer -o hftf_bounds

`run_one_point.sh` was again NOT used: it builds `-O3 -funroll-loops` with no
checks. Its parameter handover was reproduced by hand as before --
`calibration_state.dat` and `calibration_distribution*.dat` deleted,
`B_SWEEP_GRID.txt` written with `addiction_scalar_1`, `PARAM_HANDOVER.txt`
written with the other 42 names -- from the script's own default block
overridden by line 1 of `code/batch_s2_00.txt`, the anchor with
`include_unsecured_borrowing=1` and `unsecured_borrowing_limit=0.30`.

The model consumed all 42 handover lines and reported

    DIAG unsecured borrowing limit, yrs of income   =  0.29999999999999999
    DIAG borrowing floor, model units                = -0.19117441177368164

which is the previous run's borrowing floor to the last digit, so the
configuration under test is the same one. Run with `OMP_NUM_THREADS=4
OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1`, `ulimit -s unlimited`, on 4
cores, stdout and stderr merged and captured unfiltered (372,233,509 bytes,
7,644,957 lines; not committed).

## Did the 11791 violation recur? NO

The expression that aborted has moved with the fix: old line 11791 is **line
11814** in this source, and it is unchanged --

    sum_distribution_used=sum(distribution_stationary(min_wealth_index(3))%&

so a recurrence would have named 11814. It did not fire.

An exhaustive sweep of the whole log for `runtime error`, `error termination`,
`backtrace`, `out of bounds`, `below lower`, `above upper`, `not associated`
and `segmentation fault`, case-insensitive, returns **zero matches**. The only
hit for `signal` is the word "signalling" in the IEEE note at exit.

## Was the routine that used to abort actually exercised?

Yes, twice. A clean run proves nothing if the code never ran, so this was
checked rather than assumed.

`stationary_equilibrium_wealth_distribution_of_old(1)` is called from line
36173 and announces itself with `begining wealth distribution for old`. That
string appears at log lines **5,059,635** and **7,644,570**.

The previous run's log was 5,059,650 lines and its abort text began at line
5,059,637. So this run reaches the same routine at essentially the same
position in the output stream -- within a line or two of where the old run
died -- and passes straight through it, then solves again and enters it a
second time. That is as direct a confirmation as this procedure can give: the
walk now reaches its stopping rule instead of consuming every cell, so `minloc`
is never taken over an all-false mask and `min_wealth_index` is never
`(0,0,0)`.

## What this run does NOT test

**Two of the three routines the fix changed were never reached.** The fix
keyed three wealth walks on `renter_array_floor`; only one of them ran here.

`stationary_equilibrium_wealth_distribution(1)` and
`calculate_gini_coefficient(1)` are called at lines 39037-39038, inside
`calibrating_model`'s "calculating inequality" block. The B-sweep branch ends
with a bare `stop` at line **38752**, which is before them. Under the
`B_SWEEP_GRID.txt` path that `run_one_point.sh` drives -- and which this
procedure reproduces -- those two calls are unreachable, and the log confirms
it: `calculating inequality` and `simulation ended` appear **zero** times.

So the same fix in those two routines is untested by this run. Reaching them
needs a configuration that does not take the B-sweep exit.

## How far it got

Wall time 1228 s (20 min 28 s) from process start to normal exit, status 0.
The run completed the whole point:

- three value-function solves (log lines 403, 2,529,913 and 5,059,638);
- 91 stationary-distribution iterations, distance falling monotonically;
- the full statistics chain, both passes through the old households' wealth
  distribution, the moments block, the invariants block;
- `B SWEEP POINT DONE at b= 3.5999999999999997E-002 participation=
  6.7334447902329411E-002`, then a clean stop.

On wall time: it is longer than the previous run's 587 s to abort, and that is
not evidence of anything by itself. `CALIBRATION_STATE.md` records the same
vector on one source taking 17 min in one session and 11 min in another, so
wall-clock pace here varies by half again between runs.

## An observation, recorded and not fixed

The run finished with one invariant failing, and the field overflowed:

     INVARIANT FAIL     wealth histogram holds the whole of net worth  = ****************   want   1.0000
     INVARIANTS:            1  FAILED -- see the lines above

No archived point fails this invariant. Across `points/` and
`points_superseded/`, 21 carry `include_unsecured_borrowing=1`; of the 12 in
`points/`, 11 print the line and all 11 pass it at exactly `1.0000000000` (the
twelfth has no invariants block). But those all sit on model hashes from before
the borrowing actually did anything -- `CALIBRATION_STATE.md` records that it
was inert -- and no point exists on `2f7c317e75`, `1288193c8a` or `17529c7177`,
so there is no like-for-like comparison to make.

The arithmetic is at line 9879 in `stationary_equilibrium_statistics`:

    wealth_hist_wealth_check=sum(wealth_hist_wealth)/&
        max(model_total_net_wealth(time_period),10.d0**(-12))

and this economy's aggregate net wealth is **negative**:

    model_total_net_wealth(1)=  -16.019442977082811
    wealth_to_output_model = -0.86946241969456661   target =  3.0

`max(-16.02, 1e-12)` is `1e-12`, so the ratio is on the order of `1e12` and
overflows the printed field. The guard is a divide-by-zero floor written for a
quantity that cannot be negative, applied to one that can. That is a real
defect, but it is **not a bounds violation**, it is in a routine the fix did
not touch, and nothing was changed: the instruction for this run was to record,
not to fix.

Whether the aggregate is negative *because* the fix opened the three debt
points to the wealth walk, or was negative already at this vector, is not
settled by this run and is not claimed here. This economy also has no
homeowners at all (`model_fraction_of_homeowners_with_mortgage = 0`,
`aggregate_housing_consumption = 0`), as the previous bounds run also found.

The process also exited with `IEEE_INVALID_FLAG` and `IEEE_DIVIDE_BY_ZERO`
signalling. That is a note, not an error, and it does not by itself say where.

## Compile-time bounds warnings

The same seven static out-of-bounds warnings as before, all in
`transition_simulation`, at line numbers shifted by +28 from the fix. None is
reached at run time, for the reason given in `BOUNDS_CHECK.md`:
`transition_simulation` is called only under `is_counterfactual==1 .AND.
solve_transition_dynamics==1`, and both are compile-time parameters set to 0.

    :40009:26  housing_price(transition_length-25:transition_length-1)=...   (-24 < 1)
    :40030:30  lump_sum_transfer(transition_length-25:transition_Length-1)=... (-24 < 1)
    :40325:56  write(2,'(F10.8)') homeownership_by_age(2,:)                  (2 > 1)
    :40272:54  write(1,'(F15.12)') housing_price(i)              [do i=0,...] (0 < 1)
    :40285:54  write(1,'(F15.12)') housing_stock(i)-...          [do i=0,...] (0 < 1)
    :40285:78  write(1,'(F15.12)') ...-total_housing_demand(i)   [do i=0,...] (0 < 1)
    :40312:58  write(2,'(F15.12)') lump_sum_transfer(i)          [do i=0,...] (0 < 1)

## What this run settles, and what it does not

It settles that the abort at the old 11791 is gone, on this vector, in the
routine that used to abort, which the run demonstrably entered twice.

It does not settle that the model is free of bounds violations. `-fcheck=bounds`
aborts on the first one, so a clean run bounds nothing beyond the paths it
actually took -- and this one never took the inequality path at all, which is
where two thirds of the fix lives.
