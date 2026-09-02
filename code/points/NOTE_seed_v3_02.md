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

## A second, independent bug: `gaps.py` destroys `.model_hash_map`

Running `python3 code/gaps.py` on an intact, freshly-checked-out
`code/.model_hash_map` rewrites that tracked file from **330 lines (329
mappings) to 8 lines (7 mappings)**. This is reproducible from a clean
checkout and is not a side effect of anything done by hand here:

    git checkout HEAD -- code/.model_hash_map   # 329 mappings
    python3 code/gaps.py                        # "no scoreable point ..."
    wc -l < code/.model_hash_map                # 8

Mechanism, in `code/model_hash.py`:

- `archive()` calls `resolve(stamp, _map)`; the first stamp missing from the
  cache sets `_rebuilt` and calls `build_map(force=True)`;
- `build_map` starts `m = {}` and, **when `force` is set, never loads the
  existing cache** -- the `if os.path.exists(CACHE) and not force` guard skips
  it;
- it then repopulates `m` from `_git_revs()` and `json.dump`s it over the
  cache.

`_git_revs()` is `git log -- code/housing_first_or_treatment_first_SR_v1.f90`.
**This checkout is shallow** (`git rev-parse --is-shallow-repository` is
`true`, 61 commits), so that walk sees only the handful of revisions present
locally. The 329-entry map was accumulated when deeper history was reachable;
one unknown stamp replaces it with the 7 revisions this clone can see, and the
other 322 mappings are gone. Any worker that then commits the file propagates
the loss to everyone.

The truncated file was NOT committed here; it was restored with
`git checkout HEAD -- code/.model_hash_map`. Every worker on a shallow clone
will keep re-truncating it, so this needs a real fix. Two independent ones,
either sufficient:

- seed the map from the cache even under `force` (`m = {}` becomes a load of
  the existing cache, with the git walk merged on top), so a rebuild is
  additive and a shallow clone can only ever add mappings; and/or
- `git fetch --unshallow` in the worker setup so `_git_revs()` sees the whole
  history it assumes it has.

## This bug is NOT why the archive is empty

Worth stating explicitly, because the two failures look alike and the second
one is the tempting explanation for the first. Resolving every stamp in
`points/` against the **full, untruncated** 329-entry map gives:

    points by semantic hash          count
    <no MODEL line>                     86   (predate the stamp)
    3af48ddb51                          78
    ddde1a91e1                          72
    222bb7fd3f                          52
    31818f2e83                          24
    671f8a037b                          24
    ... 28 further hashes               ...
    9caeb7a139                           1   (this run's first measurement)
    fdc6078859  (CURRENT)                0

**Not one point resolves to `fdc6078859`, with the full map in place.** The
archive is genuinely stale: `ca9479b` changed the economy and no point had yet
been measured on it. Restoring the map does not recover a single point, and
fixing `build_map` will not make the loop scoreable today. Both problems are
real; only the model change explains the empty archive.

Two other things the resolution table shows, neither new: 86 points predate
the MODEL stamp entirely, and 2 carry an empty stamp (the `code/code`
`dirname` bug that `run_one_point.sh:204` records as fixed). Those 88 points
can never be scored again.

## What was done about it

The stale point was moved aside (it survives in git history at `45d4839`) and
the same batch line was re-run against `fdc6078859`. The result of that re-run
is recorded in the "Re-measurement" section appended below.

## Re-measurement, and a noise floor worth knowing

The vector was re-run against `fdc6078859`. Meanwhile another worker measured
the same vector on the same model and pushed it as `c15d9a1`; that duplicate
was kept and this run's own copy dropped with `git rebase --skip`, since the
two are equally valid.

Which is the useful part. Three measurements of this one vector now exist:

| run | model | semantic |
|---|---|---|
| `45d4839` (this worker, first) | `b75ae0454f` | `9caeb7a139` |
| this worker, re-run            | `1b0babfbed` | `fdc6078859` |
| `c15d9a1` (other worker)       | `1b0babfbed` | `fdc6078859` |

Comparing the two runs on the **same** model (`c15d9a1` vs this worker's
re-run), `h_1` is 0.029782528635873978 against 0.029782551198649861 and
`lambda_d` is 3.2163823662893997e-3 against 3.2155922015596108e-3. They are
not bit-identical; `a1d8621` already records that two runs of one tag do not
agree exactly.

The addition here is the **size** of it, and the comparison it licenses. The
run-to-run spread on an identical model is order 1e-5 relative -- and the
spread across the `ca9479b` model change, at this vector, is **the same order
or smaller**. Every moment agrees to five or six significant figures across
the change that invalidated the archive.

Two consequences:

1. **`ca9479b` is unmeasurable at this vector.** That is not a claim that it
   is unmeasurable everywhere -- it fixes `w_bot` for renters carrying debt,
   and this point may simply not exercise that path hard enough. But if it
   holds at a couple more vectors, an `EQUIVALENT_MODELS` entry pairing
   `9caeb7a139` with `fdc6078859` would recover far more of the archive than
   re-measuring it point by point at ~13 minutes each. That is the author's
   call, not a worker's, which is why it is written here rather than applied.
2. **Nothing below ~1e-5 relative is a measurement.** Any elasticity the loop
   computes from a moment difference near that size is reading solver noise.
   Worth keeping in view when a secant returns a very small response.

## State of the loop after this run

With one point on the current model, `next_batch.py` runs and writes
`CORRECT_60.txt` -- 12 EXPLORE arms across six parameters whose response turns
without straddling the target. `gaps.py` now exits 0 and reports:

    FIRST POINT in this economy -- nothing to compare against yet.
    LOSS (minimax over scored) 646.4%   median 36.2%   inside ten per cent 5 of 20

`GAPS_seed_v3.md` in this directory holds the full table. The loss is
dominated by `h_1` at +646% and `w_bot` at +195%; five of twenty moments are
already inside ten per cent.
