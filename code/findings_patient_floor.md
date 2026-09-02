# Controlled pair: restrict_borrowing_to_impatient = 0 vs 1

## Status: PAIR NOT OBTAINED. Run 1 was killed before it produced a point file.

No moments, no wealth shares and no DIAG lines are reported below, because
neither run completed. Nothing in this file is a measurement of the flag.

## What was run

`code/batch_patient_floor.txt` line 1, typed verbatim, in the foreground, on a
single blocking call:

    bash code/run_one_point.sh ... include_unsecured_borrowing=1 \
        unsecured_borrowing_limit=1.50 unsecured_borrowing_rate=0.055 \
        number_of_beta_types=2 discount_factor=0.99980 \
        discount_factor_impatient=0.75 restrict_borrowing_to_impatient=0

Model hash `86a921e21d`, built from source `9575c59af0ff8632a4169d80352f134d`,
on 4 cores. Line 2 was never started.

## Timeline (UTC, 2026-09-02)

| time | event |
|---|---|
| 16:15:57 | run 1 launched, foreground |
| 16:16 | `gfortran` absent from the container, installed by `run_one_point.sh` |
| 16:17 | `hftf` built, solve begins: `running 86a921e21d on 4 cores` |
| 17:15 | 59 min elapsed, 85 min CPU, 147% CPU. Still solving. |
| 18:03 | 107 min elapsed, 133 min CPU, 126% CPU. Still solving. |
| 19:00 | 165 min elapsed, 190 min CPU, 116% CPU. Still solving. |
| 20:27 | 252 min elapsed, 267 min CPU, 111% CPU. Still solving. |
| ~21:32 | **container recycled.** `hftf` killed, exit 137. No point file. |

**Run 1 ran for at least 5 h 16 min of wall clock and did not converge.**
The estimate in the task was 15-25 minutes. The observed floor is **12-21x**
that, and it is a floor, not a runtime -- the solve was killed while still
running, so its true runtime is unknown and strictly greater than 5 h 16 min.

## Evidence the solve was healthy, not hung

`hftf` accumulated CPU time monotonically for the whole 5 h 16 min and never
dropped below 111% CPU. It was doing work the entire time. It wrote nothing to
stdout after the `running ... on 4 cores` line and touched no file under
`code/` -- this build emits the point file only on completion, so there is no
partial result to salvage and no progress signal to read.

## Why it died

`dmesg` in the replacement container shows a fresh boot (`crng reseeded due to
virtual machine fork`, filesystems mounted at t+2.6 s), not an out-of-memory
kill inside a surviving container. Memory was not the constraint: the box has
15 GB and reported 15 GB free after restart. The container was recycled out
from under the run at roughly 5 h 17 min of session wall clock.

## The consequence for this experiment

The pair requires both solves in ONE container, because results differ across
containers by up to 1.8e-02 and the effect being measured may be smaller than
that. That requirement cannot be met by this method on this hardware:

- run 1 (the `=0` side, the wide grid) needs **> 5 h 16 min**;
- run 2 (the `=1` side) is predicted only 10-12% faster, so **> 4 h 40 min**;
- the pair therefore needs **> 10 h** in one container;
- the container just demonstrated a lifetime of about **5 h 17 min**.

Ten hours of work does not fit in a five-hour container. Retrying the same
vector unchanged would consume another five hours and end the same way. Per
the run protocol the failure is recorded here rather than retried.

## What would make the pair obtainable

Not attempted, and listed only so the next attempt is not spent rediscovering
the wall:

1. **More cores.** The solve held 111-147% CPU against 4 available, so it is
   not saturating even this box; whether that is Amdahl or oversubscription is
   unmeasured. A wider box helps only if the parallel section is the long one.
2. **A cheaper point.** Every run at this vector switches unsecured borrowing
   ON with `restrict_borrowing_to_impatient=0`, which is the widest negative
   grid the model admits. A coarser grid would break comparability with the
   merged setting but would establish the sign of the effect.
3. **A checkpoint in `hftf`.** With no intermediate output there is no way to
   resume, so every container recycle costs the entire run rather than the
   last iteration.

## The two questions the pair exists to answer

**1. How much faster is run 2?** Unanswered. Run 2 was never started, and run 1
never finished, so there is no pair of times to difference. The 10-12%
prediction is neither confirmed nor refuted.

**2. Did any moment move?** Unanswered, and this is the one that matters. The
question of whether `restrict_borrowing_to_impatient` is a speed setting or a
**model change** is still open, and the flag is **already merged**. Nothing
here licenses treating it as safe.

## Repository state

`code/` was not modified. `code/calibration_state.dat` shows as modified in
`git status`; it was written by the killed solve, not by hand, and is
deliberately left uncommitted.
