# bn_on075 — single-point measurement

Point: `code/batch_bn_on075.txt`, run via `code/run_one_point.sh`.
Point hash: `d42e5af187` (deterministic — the relaunch after the container
restart reproduced the same hash from the same vector).

Distinguishing settings of this point: `include_unsecured_borrowing=1`,
`discount_factor_impatient=0.75`, `unsecured_borrowing_limit=1.50`,
`unsecured_borrowing_rate=0.055`, `number_of_beta_types=2`.

## Status: RUN IN PROGRESS

Results are not yet available. This section is a record of what has happened
so far; the measurement is appended below once the solve returns.

### Note on the batch file: there is no line 2

The task specified running line 2 of `code/batch_bn_on075.txt`. That file
contains exactly one line (1222 bytes, single trailing newline) — there is no
line 2. HEAD is `ed8e7e2 batch: the borrowing triple split one line per
worker`, so the instruction predates the split that gave each worker a
one-line file. Line 1 is therefore the intended point, and its parameters
match the filename (`include_unsecured_borrowing=1` → `bn_on`,
`discount_factor_impatient=0.75` → `075`). Line 1 was run, typed out verbatim,
with no command substitution.

### Container restart lost the first attempt

The first launch built cleanly (gfortran installed into the container,
`hftf` built from source hash `1b081ebc4d54ffc28733415fe67f5989`) and was
solving `d42e5af187` on 4 cores when the container was restarted. The run was
killed mid-solve. It produced no point file and no error — the Fortran did not
fail, the machine went away underneath it.

The vector was relaunched UNCHANGED. Retrying with a changed vector is
forbidden and was not done; this retry is byte-identical, as the reproduced
point hash `d42e5af187` confirms.

### Second container restart lost the second attempt too

The relaunch reproduced point hash `d42e5af187` (confirming a byte-identical
vector) and solved for roughly four minutes, 21:12 to 21:16 UTC, before the
container was restarted again. Again no point file, again no Fortran error.

A third attempt is now running, unchanged.

### Diagnosis: this is the environment, not the point

Two hypotheses were checked and one survived.

REJECTED -- disk exhaustion. The worker log grows fast (about 200 MB in the
first four minutes of solving), so filling the disk looked plausible. It is
not the cause: `df` reports 30 GB available and 21 per cent used at the moment
of the second death.

STANDS -- idle reclamation. Both deaths came within minutes of this session
ending a turn. The container is reclaimed on inactivity, and a background job
does not count as activity, so the solve is killed while the session sleeps.

This matters because there is NO mid-solve resume. `run_one_point.sh` line 313
skips work only when a COMPLETED point file already exists (it tests for the
`END OF MOMENTS` marker); a solve killed partway leaves nothing reusable, so
every relaunch restarts from zero. A point needing hours, restarted from zero
every few minutes, does not converge on this infrastructure by relaunching
alone.

Note also that `run_one_point.sh` (lines 332-346) warns that concurrent runs in
this directory collide over shared files that are not keyed to the tag --
`hftf`, `PARAM_HANDOVER.txt`, `B_SWEEP_GRID.txt`, `calibration_state.dat`. So
the throughput fix is NOT to launch several attempts at once in this working
directory; that corrupts points rather than saving them.

What would actually fix it: a longer-lived or non-reclaimed runner, or
checkpointing in the solve. Both are outside what this task permits me to
change (no Fortran edits, no `supervise_calibration.py`), so I am flagging it
rather than working around it.

---

## THE POINT IS NOT MERELY SLOW: the budget constraint does not close for unsecured borrowers

Inspecting the third run's log before it was overwritten turned up something
that matters more than the moment table this task asked for. The measurement is
still unmade, but the reason is no longer only infrastructure.

### What the log shows

In roughly five minutes of solving, `worker_d42e5af187.log` reached 301 MB and
contained **688,835** occurrences of `budget does not clear by`. This is not a
warning: it is the model's own budget-identity check at
`housing_first_or_treatment_first_SR_v1.f90:24025`, whose tolerance is
`checking_criterion = 5*10.d0**(-8)`. The observed residual is about `-0.898`
to `-0.956`, i.e. roughly 1.8e7 times the tolerance it is tested against. The
line immediately above the print, now commented out, called it
`"error budget does not clear"`.

The check only fires on economically meaningful states. Its guard requires
`after_tax_wealth_net_of_expenses_1 > 0`, `frac_spent_on_addiction_used >= 0`
and `consumption_used > 0`, so these are not junk or infeasible probes.

### The residual equals the borrowing position exactly

The residuals do not scatter. They collapse onto two values, reproduced to
fifteen significant digits:

    230310 + 163810 + 157568 + ...  -0.898289438909321...
     85466 +  15656 +  15192 + ...  -0.955872058868408...

The second is *identical* to the only value of
`min(financial_grid(financial_index_used), 0.d0)` in the entire log,
`-0.95587205886840820`, which is the most negative point of the financial grid
-- the unsecured borrowing limit itself. (The first cluster is the interpolated
case: `frac_used` mixes two adjacent grid points.) A residual that equals the
borrowing position exactly is a dropped term, not a numerical tolerance problem.

### The mechanism

The budget line at `housing_first_or_treatment_first_SR_v1.f90:24016-24018`
multiplies the negative part of the financial position by
`max(amortization_used-1, 0)`:

    (frac_used*min(financial_grid(fin_index_frac_used),0.d0) +
     (1-frac_used)*min(financial_grid(financial_index_used),0.d0)) *
     max(amortization_used-1,0) * housing_price(time_period) *
     housing_size(housing_status_index_used) + ...

In **all 688,834** of the logged failures, `amortization_used = 1`. So
`max(1-1, 0) = 0`, and the household's entire negative financial position is
multiplied by zero and vanishes from the budget identity. The budget then fails
to clear by precisely the debt that was dropped, which is exactly what the
residuals show.

The reading this suggests: that expression treats every negative financial
position as MORTGAGE debt, scaled by amortization, house price and house size.
That is coherent while the only way to hold negative assets is a mortgage. With
`include_unsecured_borrowing=1`, households hold negative positions with no
mortgage and hence `amortization_used = 1`, and their debt silently leaves the
budget constraint.

Also logged in all 688,834 cases: `housing_status_index = -1`, a sentinel,
against `housing_status_index_used = 2`.

### Why this bears directly on the question that was asked

This task exists to test whether unsecured borrowing is actually held in
equilibrium, via the bottom-percentile wealth shares. The evidence above says
the budget identity does not close for precisely the households that borrow.
Any bottom-percentile share this point eventually produces would be measured
off states that violate the household budget constraint by about the full
borrowing limit. The moment table is not yet trustworthy on the very question
it was built to answer.

I have NOT tested this by patching, because modifying the Fortran source is
outside what this task permits. The causal claim above is therefore an
inference from the log, though the exact coincidence between the residual and
the grid's most negative point, together with `amortization_used = 1` in every
single failure, makes it a strong one.

### It also plausibly explains the wall-clock

`run_one_point.sh:546` sets `GFORTRAN_UNBUFFERED_ALL=1`. Nearly 700,000
diagnostics, at about eight unbuffered lines each, in five minutes, is severe
I/O thrashing. Recorded runtimes elsewhere in this repo are 12, 21 and 27
minutes; this point may be far slower than that for reasons that are a
consequence of the defect, not of the parameter vector. A longer-lived
container alone might therefore not be sufficient to land it.

## Summary of what is and is not established

ESTABLISHED
  - The budget identity fails by ~0.9-0.96 on ~689k valid states in 5 minutes.
  - The residual exactly equals the most negative financial grid point.
  - `amortization_used = 1` in every logged failure, zeroing the debt term.
  - Disk (30 GB free) and memory (15 GiB, no cgroup cap, no OOM) are NOT causes
    of the container deaths.

NOT ESTABLISHED
  - Every scored moment for this point. w_bot, its gap to the 0.0250 target, the
    bottom-percentile wealth shares, the negativity test, and beta against the
    3.0-4.5 band are ALL still unmeasured. No point file has ever been produced.
  - Whether a fix to the amortization multiplier resolves it (not tested; source
    changes not permitted here).
