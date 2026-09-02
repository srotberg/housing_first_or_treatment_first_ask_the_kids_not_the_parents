# The already-measured check does not compare MODEL hashes, and there are now
# stale points on the branch that it will serve

Running `batch_s2_00.txt` (3 lines, the unsecured-borrowing triple) against the
source with the net-worth fix, `ca9479b`. Recording a hazard found while doing
it, because it is invisible from any point file and it will bite the next
worker rather than announce itself.

## The hazard

`run_one_point.sh` line 283:

    if [ -f "points/point_${TAG}.txt" ] && grep -aq "END OF MOMENTS" ...; then
        echo "run_one_point: $TAG is already measured, skipping"

`TAG` is the md5 of the parameter vector ALONE (line 238). It does not include
the model hash. The script's own comment at line 174 says so in as many words:
"the already-measured check does not compare model hashes". That was written
about the one-type to two-type change, where a new parameter NAME changed every
tag and so kept stale points from being served. Nothing changed a parameter
name this time.

## Why it bites now

The net-worth fix changed the source and nothing else:

    a3f7ba4  b75ae0454f   the borrowing branch compiles
    848bc9f  51eb57a15e   disarm the latent default(none) trap
    ca9479b  1b0babfbed   w_bot could not see the borrowing  <- the fix

The parameter vectors in `batch_s2_00.txt` are unchanged across that fix, so
every tag is unchanged. Two point files measured BEFORE the fix are on the
branch right now:

    points/point_4659380b40.txt   MODEL b75ae0454f   = batch_s2_00 line 1
    points/point_6aadbe9c3d.txt   MODEL b75ae0454f   = batch_s2_02 line 1

Both carry `END OF MOMENTS`. A worker who pulls the branch and then asks for
either tag gets "already measured, skipping" and a point file whose numbers
came from the truncated net-worth formula -- the formula the fix exists to
discard. The run completes, exits zero, and says nothing about the source it
did not use.

## What happened here

Line 1 of this batch escaped it by timing, not by design. The run started
before `point_4659380b40.txt` had been pulled into the working tree; the file
arrived mid-solve, in the rebase onto `a1d8621`. The solve was already past
line 283 and went on to overwrite the stale file with a measurement under
`1b0babfbed`, which is the wanted outcome. Had the pull come one minute
earlier, this session would have committed the old numbers as its result and
reported success.

Lines 2 and 3 are not exposed: no point file on the branch carries their
vectors. `grep -l unsecured_borrowing_limit points/*.txt` returns exactly the
two files above, so those two tags are the whole of the exposure today.

## What would close it

Not fixed here -- the instruction for this batch is to measure three points and
not to patch the harness, and the check is load-bearing for other callers.
Stating the options rather than choosing one:

- have the skip compare the recorded `MODEL` line against `MODEL_HASH` and
  re-solve when they differ, which is the direct reading of what the check was
  always for;
- or put the model hash into the tag, which is honest but orphans every point
  in `points/` on every source edit, including comment-only ones;
- or, narrowest, delete the two stale files above, which fixes today and leaves
  the mechanism in place for the next source fix.

The first is the only one that survives the next net-worth-shaped change.

## Cross-check against the stylized model

Per TRANSITION_LESSONS.md section 7: this is a harness bug, not a model bug, so
there is no stylized counterpart to check it against. The stylized model has no
tag cache. Recorded here rather than in that table for the same reason.
