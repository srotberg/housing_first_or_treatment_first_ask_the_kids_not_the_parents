# The patient-borrowing-floor pair: measurement log

Vector: `code/batch_patient_floor.txt`. Two lines, identical but for
`restrict_borrowing_to_impatient` (0 on line 1, 1 on line 2). The pair must be
measured in ONE container, because results move by up to 1.8e-02 across
containers and the effect looked for may be smaller than that.

Tags (md5 of the sorted vector, as `run_one_point.sh` computes them):

| line | `restrict_borrowing_to_impatient` | tag | legacy tag |
|---|---|---|---|
| 1 | 0 | `86a921e21d` | `85b17b1e1a` |
| 2 | 1 | `b083f765a0` | `a2febacc4e` |

The two tags differ, so neither arm can be served the other's file, and neither
tag was present in `code/points/` beforehand: both arms genuinely solve.

## STATUS: NOTHING MEASURED. Line 1 killed three times; line 2 never started.

**No moment, no gap, no difference is reported below, because none was
measured.** Line 2 was never begun: a pair needs both arms from one container,
and no arm has ever finished.

## The three deaths

| attempt | started (UTC) | died | elapsed | container age at death |
|---|---|---|---|---|
| 1 | 15:03:55 | ~15:14 | ~11 min | — |
| 2 | 21:12:06 | ~21:21 | ~9 min | ~10 min |
| 3 | 21:25:05 | ~22:10 | ~45 min | ~48 min |

All three were reported to the session as "the container was restarted". No
`point_*.txt` and no `point_*.FAILED.txt` was ever written, because the solve
never reached the point where `run_one_point.sh` writes one.

## What the shape of the failure is NOT

Two hypotheses were formed and both were then falsified by measurement. Both are
recorded because the evidence for each looked strong.

**Not a deterministic fault at a fixed instruction.** Attempts 1 and 2 both left
logs of exactly 445,382,656 bytes with byte-identical tails, which reads as a
deterministic crash at a fixed point. It is not. Attempt 3 was instrumented and
showed the log **stops growing** at that size while the process runs on happily
for another 36 minutes. 445,382,656 bytes is simply how much this vector writes
before it goes quiet; the equal sizes say the model reaches the same silent
phase every time, not that it dies there. Attempt 3 then ran four times as long
as the others, which a fixed-point fault could not do.

**Not memory.** Sampled every 45s, then every 2s through the critical window:

```
t=  67s rss= 679MB avail=14812MB log= 85MB
t= 562s rss= 679MB avail=14807MB log=412MB     <- flat for nine minutes
t= 607s rss=1803MB avail=13662MB log=425MB     <- one 1.1GB allocation
t= 652s rss=1831MB avail=13635MB log=425MB     <- log now silent
t=2702s rss=1831MB avail=13600MB log=425MB     <- unchanged 34 min later
```

Peak resident memory is 1.8 GB against 13.6 GB free. Nothing approaches an OOM,
and RSS is perfectly flat for the last 35 minutes of the run.

**Not disk** (30 G free throughout, log at 425 MB against the script's own 2 GB
cap), **not a stale warm start** (`run_one_point.sh:444` deletes
`calibration_state.dat` and `calibration_distribution*.dat` every run by design,
so a point is a function of its vector alone), and **not idleness of the
session** — attempt 3 died while heartbeats were arriving every 90 seconds and
being answered.

## What the run was actually doing

Attempt 3, instrumented throughout, was healthy at every observation:

- `DIST_DONE sweeps=55 final_distance=5.79e-04` — the distribution converged.
- At t=922s: 245% CPU across 4 threads, state `Rl`.
- At t=2071s: instantaneous CPU exactly 100% of one core (501 ticks in 5s), with
  the master thread `R` and all three OpenMP workers `S` at a barrier.

So after the parallel distribution solve the model enters a **long serial phase**
that prints nothing. It had been in that phase for 36 minutes, making progress on
one core, when the container was taken away. It was not spinning, not blocked on
I/O, and not deadlocked.

## The actual blocker

This is a **two-type** vector (`number_of_beta_types=2`,
`discount_factor_impatient=0.75`). `run_one_point.sh:175` records that *every*
point in `code/points/` was measured on the ONE-type model, and the archive's
solve times — 5 to 27 minutes, mostly 5 to 16 — are all one-type times. There is
no precedent here for how long a two-type solve takes, and **its total runtime is
still unknown**: the longest observation is 45 minutes, still in the serial
phase, still short of writing a moment.

The pair therefore needs one container to survive **at least twice an unknown
runtime that is already over 45 minutes**. The three container lifetimes seen
tonight were roughly 10, 48 and (attempt 1) at least 11 minutes. In seven hours
no container has lived long enough to finish even one arm.

That is the finding: not a bug in the model, and not something a different flag
or vector would fix. The controlled pair, as specified, does not fit inside the
container lifetime available in this environment.

## What would make it measurable

1. **The runtime of one two-type solve**, which nobody has yet. Until that is
   known there is no way to say whether the pair needs 2 hours or 12.
2. **An execution environment that outlives it** — a longer-lived or dedicated
   runner. The "same container" requirement is what makes this binding: two arms
   that could each be measured across two containers cannot be compared, because
   the cross-container spread (1.8e-02) swamps the effect being looked for.
3. Failing that, the question "is `restrict_borrowing_to_impatient` a model
   change or a speed setting" could be settled on a **one-type** vector, which
   the archive shows solves in 5-16 minutes and fits comfortably inside a
   container's life. That changes the vector, so it was NOT done here.

## Rules followed

- The vector was NOT changed on any of the three attempts; each was typed
  verbatim, with no command substitution.
- The Fortran source was NOT modified.
- `supervise_calibration.py` was not run; `code/points_pregrid/` untouched.
- Everything committed to `wip/patient-floor` only; no rebase, no merge.
