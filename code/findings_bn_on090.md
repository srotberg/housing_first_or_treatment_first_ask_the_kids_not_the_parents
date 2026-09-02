# bn_on090 — borrowing ON, impatient discount 0.90

**Status: NO MEASUREMENT. The solve did not finish and produced no point file.**

Point id `c71818d904`, built from source hash `9575c59af0ff8632a4169d80352f134d`,
run on 4 cores from the batch line in `code/batch_bn_on090.txt` (typed verbatim,
no substitutions, no value changed).

## Outcome

- Started ~15:55 UTC, killed ~21:31 UTC by a container restart (SIGKILL, exit 137).
- **Wall clock: ~336 minutes (5 h 36 m), terminated, not completed.** CPU time at the
  last sample was 5 h 54 m at ~106-138% across the run.
- `code/points/point_c71818d904.txt` was **never written**. Nothing in `code/points/`
  is attributable to this run.

The estimate for this point was ~20 minutes. It was killed at 16x that having still
not reached the point where it writes output.

## The two DIAG lines requested

Both were emitted, identically, on each of the 3 outer iterations that ran:

```
DIAG unsecured borrowing limit, yrs of income    =   1.5000000000000000
DIAG borrowing floor, model units                =  -0.95587205886840820
DIAG patient type barred from the negative grid  =            1
```

- **`DIAG borrowing floor, model units` = -0.95587205886840820**
- **`DIAG patient type barred from the negative grid` = 1** — reads 1 as expected, so the
  patient type is correctly barred and only the impatient pass should pay the wider grid.

## Scored moments

**None available.** `w_bot`, the bottom-percentile wealth shares, `beta` and every other
scored moment are computed and written only at the end of the solve. The run never got
there, so there is nothing to compare against the 0.0250 `w_bot` target, nothing to test
for a negative bottom share, no multiples to check, and no `beta` to place against the
3.0-4.5 band or against the OFF control at `de322e4659`. Reporting any number here
would be fabrication.

The question this arm was meant to answer — whether, with borrowing on, a much less
impatient household (0.90, still on the borrowing side of the 5.5% knife-edge
beta = 1/1.055 = 0.947867) can still produce a low bottom share — remains open.

## What the log shows, and the likely reason it never finished

The run logged 226,099,200 bytes in its first ~10 minutes and then emitted **nothing at
all** for the remaining 5 h 21 m while still burning CPU (State R, 4 threads, 1.9 GB RSS;
`wchar` frozen at 226,118,933, i.e. no further writes attempted). Disk was not the
constraint — 30 GB remained free.

Two things stand out.

**1. The budget constraint fails at the borrowing floor, 515,598 times.** The log is
dominated by this block:

```
budget does not clear by -0.89828943890932111
min(financial_grid(fin_index_frac_used),0.d0)= -0.95587205886840820
min(financial_grid(financial_index_used),0.d0)= -0.95587205886840820
amortization_used=           1
years_left_on_mortgage_index=           1
housing_status_index=          -1
housing_status_index_used=           2
```

The shortfall is -0.8983 against a borrowing floor of -0.9559 — the household is being
pushed essentially to the bottom of the newly opened negative grid and the budget will
not clear there. `housing_status_index = -1` is a sentinel, not a valid housing state.
The 515,598 occurrences differ only in the last two or three digits (-0.89828943890932056
through -0.89828943890932189), which is a solver being driven repeatedly against the same
infeasible corner rather than a handful of unlucky states. Five diagnostic lines each is
what produced the 226 MB.

**2. It stalled after the third outer iteration.** There are exactly 177 `AGE_TIME` lines
= 3 passes x 59 ages (60 down to 2), and 3 `DIAG` blocks, so three full backward
inductions completed. The stationary distribution then converged cleanly over 117
iterations (0.1560 -> 9.09e-04, monotone). After that the log stops mid-number inside a
`newborn_productivity_draw` line — a buffer boundary, not a crash — and no fourth
iteration ever announced itself. A fourth pass would have printed a `DIAG` block and 59
more `AGE_TIME` lines within a few minutes; none appeared in 5 h 21 m.

So the run was not merely slow: it stopped making the kind of progress that produces
output, in a phase that emits none, most plausibly wedged on the same infeasible
borrowing corner the 515,598 diagnostics point at. That failure is specific to this
borrowing-ON configuration — it is the negative grid that creates the corner.

## Not done, deliberately

Per instruction, the vector was **not** changed and the point was **not** re-run with a
different vector. `code/` was not modified while the solve ran. `supervise_calibration.py`
was not run and `code/points_pregrid/` was not touched.

`code/calibration_state.dat` was modified by the solver itself during the run; it is left
uncommitted as incidental state from a failed run.

The raw 226 MB log cannot be committed (it exceeds GitHub's file limit).
`code/worker_c71818d904.excerpt.log` carries the head, every DIAG / AGE_TIME /
distribution-distance line, the distinct budget-failure values, and the tail.
