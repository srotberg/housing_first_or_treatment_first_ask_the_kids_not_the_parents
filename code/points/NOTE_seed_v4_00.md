# batch_s2_00: three points, measured four times, and what each source said

This session was asked to measure the three lines of `batch_s2_00.txt` -- the
unsecured-borrowing triple -- against the net-worth fix `ca9479b`. The source
moved three more times while it ran, and every one of those moves invalidated
what had already been measured. Recording the sequence, because the individual
point files do not show it and because two separate mechanisms conspired to
make a stale measurement look like a good one.

## The three lines

    line 1   include_unsecured_borrowing=1  limit=0.30    tag 4659380b40
    line 2   include_unsecured_borrowing=0  limit=0.30    tag f9c16d5308   <- OFF control
    line 3   include_unsecured_borrowing=1  limit=0.60    tag f4a40be627

## The source moved under the batch

    a3f7ba4  b75ae0454f   the borrowing branch compiles
    848bc9f  51eb57a15e   disarm the latent default(none) trap
    ca9479b  1b0babfbed   w_bot could not see the borrowing        <- batch commissioned here
    307aa35  e55e1cc855   the borrowing CHOICE was inert
    358057d  (interim)    the EV fill range broke the economy
    0f581bb  c823331449   renter arrays had no negative indices

Lines 1 and 2 were measured on `1b0babfbed`; line 3, started later, built
`e55e1cc855` without anything announcing that the source had changed mid-batch.
The run log is the only place it shows, in the `built hftf from` line, and only
if you compare it against the previous line's.

## What survived: nothing, and the reasons differ

- Lines 1 and 2 on `1b0babfbed`: invalidated by `307aa35` in its own words --
  "every borrowing arm measured so far". Both passed every invariant, which is
  the point: the ON and OFF arms agreed because the choice never opened.
- Line 3 on `e55e1cc855`: invalidated by `0f581bb`. It had already failed two
  invariants here, both histograms holding 1.4954 of the distribution instead
  of 1.0, the same number to eight figures on income and on wealth. That is the
  out-of-bounds write `0f581bb` names, seen from the outside: a renter's
  financial index started at the zero index in all forty-two allocations while
  the borrowing commit had opened twenty-five renter state loops down to index
  1. The 1.4954 is recorded in `point_f4a40be627.txt` as measured.

`0f581bb` withdraws the "borrowing is inert" reading too. So after four
measurements of three points, whether anyone borrows is still unmeasured.

## Two ways a stale point gets served as a good one

Both fired in this session, and neither announces itself.

**1. The skip check ignores the MODEL hash.** `run_one_point.sh` line 283 skips
when `points/point_<TAG>.txt` exists with `END OF MOMENTS`, and `TAG` (line 238)
is the md5 of the parameter vector alone. The script's own comment at line 174
says so: "the already-measured check does not compare model hashes". It was
written when a new parameter NAME changed every tag; nothing changed a name
across any of the four source moves above, so every tag stayed put while the
economy underneath it changed three times. Line 1 escaped only by timing -- the
stale `point_4659380b40.txt` arrived in a rebase mid-solve, after line 283 had
already been passed. One minute earlier and this session would have committed
the pre-fix numbers and exited zero.

**2. A concurrent worker's stale point wins the rebase.** Line 3's push hit a
conflict: another session had measured `f4a40be627` on `1b0babfbed` and pushed
first. Both files are 240 lines and differ only in numbers; nothing but the
`MODEL` line distinguishes the superseded economy from the current one, and
`git` has no reason to prefer either. Resolved by reading the `MODEL` line and
keeping `e55e1cc855`. A resolution that took "theirs" on principle, or that
diffed the moments and picked the one that passed its invariants, would have
kept the wrong file -- the stale one is the one that passes.

## Re-measuring

All three lines are being re-run on `c823331449`. Line 2, the OFF control, goes
first rather than in file order, because `0f581bb` sets it as the gate: "The OFF
control on this source must reproduce w_bot 0.029487 exactly. Nothing else is
worth measuring until it does." Its result is reported below.

Line 3's re-run needs `points/point_f4a40be627.txt` removed first or it will be
skipped, per mechanism 1 above.

## What would close mechanism 1

Not patched here -- this batch's instruction is to measure and not to touch the
harness, and the check is load-bearing for other callers. The options:

- compare the recorded `MODEL` line against `MODEL_HASH` and re-solve when they
  differ, which is the direct reading of what the check was always for;
- or put the model hash in the tag, which orphans every point in `points/` on
  every source edit, comment-only ones included;
- or delete stale files by hand as they are found, which is what happened here
  (`3ec5236`, `5f0eeb5`, and this session) and which does not scale to a source
  that moves three times in an afternoon.

The first is the only one that survives the next fix.

## Cross-check against the stylized model

Per TRANSITION_LESSONS.md section 7. Mechanism 1 is a harness bug with no
stylized counterpart: the stylized model has no tag cache. The out-of-bounds
renter arrays are quantitative-only as well -- the stylized model has no
financial grid and no tenure-keyed allocation. Neither carries across, and both
are recorded here rather than in that table for that reason.
