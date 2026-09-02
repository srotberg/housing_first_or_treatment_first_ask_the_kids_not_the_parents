# seed v3, batch `code/batch_s2_02.txt` (one line, impatient beta 0.95)

## What happened

The point solved cleanly. It was then stamped with a model hash that had
already been superseded, because the source changed on the branch while the
solve was in flight.

Timeline:

- checked out `415bc6e`, whose `housing_first_or_treatment_first_SR_v1.f90`
  has full-file md5 `b75ae0454f`, semantic hash `9caeb7a139`;
- ran the batch line; it took ~13 minutes and exited 0, every invariant PASS;
- pushed, was rejected, rebased onto `d59da44`. The rebase brought in
  `ca9479b` ("w_bot could not see the borrowing: net worth truncated a
  renter's debt at zero") and `848bc9f` ("disarm the latent default(none)
  trap"), which together change the `.f90` by 44 insertions and 10 deletions;
- the source is now md5 `1b0babfbed`, semantic hash `fdc6078859`.

So the point committed as `45d4839` is a measurement of `9caeb7a139`, not of
the current economy.

## Consequence for the loop

`python3 code/next_batch.py` printed:

    426 of 426 points are on a different model (fdc6078859) and were skipped
    no archive

and `python3 code/gaps.py` printed `no scoreable point in the current
economy` and exited 1. That output is committed here as
`GAPS_seed_v3.md`. Neither is a fault in either script: `ca9479b` is a real
change to the economy, so `archive()` is right to refuse every point measured
before it. **The whole 426-point archive is stale, not just this one point.**
Nothing is scoreable until enough points are re-measured on `fdc6078859`.

## A latent bug in `run_one_point.sh` that this turned real

`run_one_point.sh:283`:

    if [ -f "points/point_${TAG}.txt" ] && grep -aq "END OF MOMENTS" ...; then
        echo "run_one_point: $TAG is already measured, skipping"

`TAG` is the md5 of the parameter vector alone. The guard does not look at
`MODEL_HASH`. The comment at line 174 already names this ("the
already-measured check does not compare model hashes") and relies on a
*parameter rename* to change every tag whenever the model changes. `ca9479b`
renamed nothing, so the protection did not fire: re-running this exact batch
line against the new source printed "already measured, skipping" and returned
the `9caeb7a139` file. A stale point is served in place of a current run,
silently and indefinitely.

This is a bug worth fixing at the source, but the instruction for this run was
not to patch, so it is recorded rather than changed. The one-line fix is to
add `&& grep -aq "MODEL ${MODEL_HASH}" "points/point_${TAG}.txt"` to the
guard, or better, to resolve both through `model_hash.resolve` so
`EQUIVALENT_MODELS` still lets a genuinely unchanged economy reuse a point.

Note that this hazard hits every worker on this branch, not just this one:
any worker whose solve straddles a model-changing push will stamp a stale
hash, and any worker re-running that vector afterwards will be handed the
stale file.

## What was done about it

The stale point was moved aside (it survives in git history at `45d4839`) and
the same batch line was re-run against `fdc6078859`. The result of that re-run
is recorded in the "Re-measurement" section appended below.
