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

Note for anyone scheduling these: a full point here takes longer than the
container's idle lifetime is guaranteed to be, so a restart mid-solve is a
live risk for every point in this batch, not a one-off.
