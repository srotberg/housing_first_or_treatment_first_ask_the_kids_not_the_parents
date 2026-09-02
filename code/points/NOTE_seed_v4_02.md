# Tag 6aadbe9c3d landed twice, on two different models, and the collision was
# resolved in favour of the current one

`batch_s2_02.txt` line 1 was measured in this session and pushed. The push was
rejected, and the rebase that followed hit an add/add conflict on
`points/point_6aadbe9c3d.txt`: another session had already committed a file
under the same tag (`ede53c4`, "point: seed v3 line 1").

This is NOT the case `REPRODUCIBILITY.md` describes. That note is about two
runs of one tag on ONE model disagreeing in the sixth digit. Here the two
files came from two different binaries:

    remote's copy   MODEL b75ae0454f   ->  semantic 9caeb7a139
    this session    MODEL 1b0babfbed   ->  semantic fdc6078859

`9caeb7a139` is the model the net-worth fix superseded (`ca9479b`, "w_bot
could not see the borrowing: net worth truncated a renter's debt at zero").
`fdc6078859` is the current one, and the semantic hashes were read from
`code/.model_hash_map`, not inferred. The raw source md5 at `ca9479b`, at
`ede53c4` and in the working tree is the same `1b0babfbed...`, so the remote's
copy was measured before that rebase and carried forward -- the situation
`a64b314` ("the seed v3 point was stamped on a model the rebase superseded")
already flagged once for a different tag.

## The resolution

Kept this session's file. The conflict was resolved to the run stamped
`1b0babfbed`, and the committed file now carries that `MODEL` line.

The check that settles it is not a preference between two measurements.
`next_batch.py` reports:

    427 of 428 points are on a different model (fdc6078859) and were skipped
    GATE OPEN at point_6aadbe9c3d

`point_6aadbe9c3d` is the ONLY point in the archive on the current model, so
it is the entire base the calibration has. Had the `b75ae0454f` copy been
kept, the count would have been 428 of 428 skipped and there would have been
no base to correct from at all -- `CORRECT_60.txt` exists because this file is
on `fdc6078859`.

## What is still exposed

The `b75ae0454f` copy is not gone from history, it was only superseded on this
branch. A session still holding it can re-push it under the same path, and
because the tag is the md5 of the VECTOR and not of the model, nothing in the
filename or in `run_one_point.sh`'s already-measured check would notice: the
script skips a solve whenever `points/point_<tag>.txt` exists with an
`END OF MOMENTS`, whatever model wrote it. The guard that does catch it is
`gaps.py` / `next_batch.py` reading the `MODEL` line through
`.model_hash_map`, which is downstream of the archive rather than in it.

Worth checking on the next pull that `points/point_6aadbe9c3d.txt` still says
`MODEL 1b0babfbed`. If it says `b75ae0454f`, the stale copy has come back and
the calibration base is empty again.

## Numerically, the two agree

For the record, and so the choice above is not read as a claim that the fix
moved this point: over the 667 shared numbers, 173 lines differ, and `w_bot`
itself -- the moment the net-worth fix was about -- agrees to seven figures:

    b75ae0454f   w_bot  0.073826575417577714
    1b0babfbed   w_bot  0.073826625225613826

So at THIS vector the truncation the fix removed was not binding, and the
divergence is the solver tolerance of `REPRODUCIBILITY.md`, not the fix. The
model hash still decides which file is admissible, because admissibility is a
statement about the source that produced the number, not about the number.

## State at the end of this session

- `point_6aadbe9c3d.txt` measured, 9 min on 4 cores, HANDOVER 42 of 42, all
  invariants PASS.
- `CORRECT_60.txt` written: 12 arms, two-sided explore brackets on the six
  coordinates whose response turns (`discount_factor_impatient`,
  `probability_of_voucher_benchmark_used`, `max_food_cost`, `value_of_life`,
  `discount_factor`, `probability_becoming_unemployed`). Round 1 is the only
  open round; rounds 2-5 were skipped as held.
- `GAPS_seed_v4.md` written: loss 646.4% minimax, median 36.2%, 5 of 20 inside
  ten per cent, worst `h_1` at +646.4% and `w_bot` at +195.3%.

---

# CORRECTION, later in the same session: the point was quarantined by path and
# had to be brought back

The paragraph above ("What is still exposed") worried about the wrong failure.
It guessed the stale copy would come back under the same name. What actually
happened is the mirror image, and it is worth writing down because the guard
that failed is the one the quarantine itself relied on.

`b5bace8`, "quarantine the three points measured on the superseded economy",
moved three files out of `points/` and into `points_superseded/`, stamping the
economy into each filename:

    points_superseded/point_30f09ca36e.9caeb7a139.txt   MODEL b75ae0454f   correct
    points_superseded/point_4659380b40.9caeb7a139.txt   MODEL b75ae0454f   correct
    points_superseded/point_6aadbe9c3d.9caeb7a139.txt   MODEL 1b0babfbed   WRONG

The third is this session's measurement. `c15d9a1`, which replaced that file's
contents with the `fdc6078859` run, is an ancestor of `b5bace8` -- checked with
`git merge-base --is-ancestor`, not assumed. So by the time the quarantine ran,
only TWO files in `points/` resolved to `9caeb7a139`, not three. The commit
message says "counted rather than assumed: exactly three of the 428 files in
`points/` carry a stamp resolving to `9caeb7a139`", and that count was taken
before the rebase that fixed one of them, or from the path rather than from the
`MODEL` line inside. Either way the file was moved on its name and its history,
and its new name then asserted an economy its contents contradict.

The effect: the archive lost its only point on `fdc6078859` at that moment, and
`next_batch.py` went from "427 of 428 skipped, GATE OPEN at point_6aadbe9c3d"
to "425 of 427 skipped". Two further current-model points (`5168ca9757`,
`6ee0ab23e5`) landed in the same window and kept the calibration from having no
base at all, which is luck, not a safeguard.

Restored: `points_superseded/point_6aadbe9c3d.9caeb7a139.txt` moved back to
`points/point_6aadbe9c3d.txt`, contents untouched, still `MODEL 1b0babfbed`.
`next_batch.py` now reads 425 of 428 skipped and `gaps.py` reports 3 points in
this economy. The other two quarantined files are correctly stamped and were
left where they are.

This does NOT reintroduce the hazard `b5bace8` was guarding against. That
commit's concern is a worker running the OLD `run_one_point.sh`, whose
already-measured guard tests the parameter tag and not the model, being served
a stale file instead of solving. A worker handed tag `6aadbe9c3d` will now be
served this file -- which is the right answer, because this file is on the
current economy. The hazard was files on `9caeb7a139` being served; those two
are still out of `points/`.

## The lesson, which is the same one in both directions

`points/point_<tag>.txt` names a vector. It does not name an economy, and
neither the tag nor the git history of the path tells you which model wrote
the numbers. The only thing that does is the `MODEL` line in the file, read
through `.model_hash_map`. Both mistakes in this session -- the stale file
nearly overwriting the current one on a rebase, and the current file being
quarantined as stale -- were the same mistake: deciding a file's economy from
its path instead of opening it.

If `points_superseded/` is going to carry the economy in the filename, the move
should be driven by grepping `^MODEL` out of each candidate at the moment of
the move, not by a list of tags assembled earlier. Three commits separated the
count from the move here, and a concurrent push landed in between.

## Consequences for what this session committed

- `CORRECT_60.txt` was computed with `point_6aadbe9c3d` as the gate's base
  (worst 195%). `5168ca9757` has since landed at worst 91% and is now what the
  gate picks. The twelve arms in `CORRECT_60.txt` are still valid measurements
  to take -- they are two-sided brackets around coordinates whose response
  turns -- but they are no longer centred on the best available base. Whoever
  runs the loop next should re-run `next_batch.py` and prefer its output.
- `GAPS_seed_v4.md` has been regenerated after the restore and reports 3 points
  in this economy. The earlier version of it, committed a few commits back, said
  1 and was accurate when written.
- `.stage_state` was left uncommitted deliberately. The copy in this session's
  working tree was written by a diagnostic `next_batch.py` run made while the
  archive was missing this point, so it records `npts 2`, and committing it
  would have propagated a count taken from a corrupted archive.
