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
