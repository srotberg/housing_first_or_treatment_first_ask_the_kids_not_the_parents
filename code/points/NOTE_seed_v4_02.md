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
