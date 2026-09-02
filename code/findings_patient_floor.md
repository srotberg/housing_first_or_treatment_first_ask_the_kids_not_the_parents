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

An earlier draft of this file said two-type solves had no precedent and were
simply slow. **That was wrong, and the archive says so.** Of the 493 points in
`code/points/`, **201 are two-type** and they solve in 8 to 27 minutes. The
comment at `run_one_point.sh:175` -- "every point in points/ was measured on the
ONE-type model" -- is stale.

Across all 493 archived points:

| | minutes |
|---|---|
| min | 0 (a crash) |
| median | 10 |
| p90 | 16 |
| **max ever recorded** | **27** |

Attempt 3 ran **45 minutes** without writing a moment: 1.7x the slowest point
ever measured and 4.5x the median. So this vector is not merely "a two-type
solve"; it is far outside anything the archive has measured.

### What is unprecedented about this vector

| feature | this vector | the archive |
|---|---|---|
| `restrict_borrowing_to_impatient` | present | **0 of 493 points** -- the flag is new in `f3fe6d9` and has never been measured |
| `unsecured_borrowing_limit` | **1.50** | 0.30 in twelve of thirteen points, 0.60 in the thirteenth |
| `include_unsecured_borrowing=1` | yes | 13 of 493 points |

The borrowing limit is the one to look at: **1.50 is five times the largest
value ever measured**. And solve time in the archive rises with it --

```
limit 0.30  ->  9, 10, 11, 13, 13, 13, 16, 17, 17, 17, 22 min
limit 0.60  ->  21 min
limit 1.50  ->  this vector, >45 min and still going
```

A bigger unsecured limit extends the negative asset grid, so a much longer solve
is the expected cost of this vector rather than evidence of a hang. That is
consistent with everything observed: converged distribution, 100% of one core,
steady memory, no error.

For completeness, the one borrowing point that did fail (`f62a932c11`) failed
quite differently -- SIGSEGV in `fill_ev_table_` at
`housing_first_or_treatment_first_SR_v1.f90:18414` with
`housing_status_index=-1`, at 0 minutes, loudly, leaving a `.FAILED.txt`. Our
three attempts produced no such file and no such trace. It is not the same
failure and does not bear on this vector.

### Why the pair, specifically, does not fit

One arm needs **more than 45 minutes** -- the true figure is still unknown,
because no attempt has ever reached the end. The pair needs **two** such solves
inside **one** container, because the task's own premise is that the
cross-container spread (1.8e-02) may exceed the effect being measured, which
makes an arm-1-here, arm-2-there comparison worthless.

Container lifetimes observed tonight: roughly 10 minutes, 48 minutes, and (the
first) at least 11. The longest was 48. The pair needs something on the order of
100 minutes of uninterrupted container life, and that has not been seen once in
seven hours.

## What would make it measurable

1. **An execution environment that outlives two solves of this vector** -- a
   longer-lived or dedicated runner. This is the binding constraint, and it is
   the only one that matters.
2. **The runtime of one arm**, still unknown and known only to exceed 45 minutes.
3. If the question is really "is `restrict_borrowing_to_impatient` a model change
   or a speed setting", it could be settled far more cheaply at
   `unsecured_borrowing_limit=0.30`, where the archive shows 9-22 minute solves
   and a pair fits inside one container comfortably. That changes the vector, so
   it was NOT done here -- it needs the author's say-so.

## Rules followed

- The vector was NOT changed on any of the three attempts; each was typed
  verbatim, with no command substitution.
- The Fortran source was NOT modified.
- `supervise_calibration.py` was not run; `code/points_pregrid/` untouched.
- Everything committed to `wip/patient-floor` only; no rebase, no merge.
