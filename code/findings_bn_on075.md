# bn_on075 — unsecured borrowing ON at the 0.75 impatient-beta vector

Point id `d42e5af187` (batch `code/batch_bn_on075.txt`, binary built from
src md5 `1b081ebc4d54ffc28733415fe67f5989`).

## Outcome: the measurement did not land

**The solve produced no point file.** It ran 5h30m and was killed by a
container restart (SIGKILL, exit 137). `code/points/point_d42e5af187.txt`
does not exist, and no scored moment was ever written.

The run was NOT retried, per the standing instruction not to retry with a
changed vector. It was also not retried with the same vector, for the reason
in "Why a retry is not the next step" below.

Because nothing was scored, every question the measurement was meant to
answer is unanswered:

| Question | Answer |
|---|---|
| `w_bot` against the 0.0250 target | **not measured** |
| every bottom-percentile wealth share | **not measured** |
| is ANY bottom-percentile share negative? | **not measured — neither YES nor NO** |
| are the bottom shares still exact multiples of one another? | **not measured** |
| `beta` against the 3.0–4.5 band | **not measured** |
| every other scored moment, per-cent gap | **not measured** |

The borrowing-OFF control at this same vector (point `de322e4659`) therefore
still stands unmatched: its `w_bot` is 0.0247429 (−1.03% off target), no
bottom-percentile share is negative (+1.213e-04 / +6.064e-04 / +1.213e-03
against data −2.250e-03 / −4.220e-03 / −4.460e-03), and the three shares are
exactly 1x, 5x and 10x each other. **Whether switching borrowing ON breaks
that degeneracy remains an open question.**

## What the run actually did

Two facts are established from `worker_d42e5af187.log` (445,378,560 bytes,
9,149,575 lines; committed compressed as `worker_d42e5af187.log.gz`):

**1. The household solve emitted a budget-clearing diagnostic 1,016,518 times,
always at the same node.** In every single one of those 1,016,518 lines,

    min(financial_grid(financial_index_used),0.d0) = -0.95587205886840820

which is exactly the most negative point of the financial grid — the deepest
debt node that `include_unsecured_borrowing=1` opens. No other negative grid
point ever appears in the diagnostic. The shortfall itself takes only two
values (to rounding): −0.95587205886840820, i.e. the entire value of the debt,
and −0.89828943890932111.

The seven negative grid points this run switched on are

    -0.955872  -0.702273  -0.487690  -0.312121  -0.175568  -0.078030  -0.019508

so the failure is confined to the first of the seven. The reading this
supports is that at this vector the deepest borrowing node is one no household
can service: the budget identity fails there by approximately the whole debt,
and the solver reports it rather than failing. The remaining six negative
nodes never trip the diagnostic.

This is also what made the run slow. Writing 425 MB of diagnostic text from
the innermost household loop, not the extra grid points themselves, dominated
the first twelve minutes. The value-function work was cheap by comparison: 118
`AGE_TIME` records (the priming solve plus one full pass), the slowest single
age 8.37 s wall / 26.10 s cpu.

**2. The run then went silent for 5h18m while still burning CPU.** The last
byte was written at 15:49:40, mid-line, in the middle of the 54th distribution
iteration. The process was still running at 108–133% CPU when the container
restarted at ~21:07. It emitted nothing in that window — not even the ~1 KB
that would have flushed the next block.

The 53 distribution iterations that did complete were converging, but slowly
and geometrically:

    iter  1   0.15597618726983351
    iter  2   1.5426849133154508E-002
    iter  3   1.4343298976114888E-002
    ...
    iter 51   6.9519069401210998E-004
    iter 52   6.6711843422147948E-004
    iter 53   6.3848641832394554E-004

The tail ratio is ~0.959 per iteration, so from 6.38e-04 a 1e-06 tolerance was
still roughly 150 iterations away. Those 53 iterations fit inside a twelve
minute window at most; the 54th did not finish in five and a quarter hours.

## Why a retry is not the next step

The gap between "53 iterations in at most twelve minutes" and "iteration 54
unfinished after 5h18m" is about four orders of magnitude. That is the shape of
a hang, not of a job that needed more wall clock. A same-vector rerun would
most likely reproduce it and spend another container lifetime returning
nothing.

I want to be explicit about the limit of this claim: the process was never
attached to a debugger and no stack was captured, so "hung" is inferred from
zero output at sustained CPU, not directly observed. What is certain is the
container restart, the exit code, and the absent point file.

The two things worth looking at before this point is run again are the deepest
debt node — whether the grid should extend to −0.9559 at all when the budget
cannot clear there — and whether the distribution iteration can stall once mass
reaches that node.

## Incidental

- `build_d42e5af187.log` carries a compile warning unrelated to this solve:
  `Array reference at (1) out of bounds (0 < 1)` for `lump_sum_transfer(i)` in
  the transition write loop. The transition does not run in this benchmark
  point, so it is not implicated here, but it is a real out-of-bounds
  reference and should be fixed on its own account.
- The killed run left `code/calibration_state.dat` modified (the log records
  "handover banked into calibration_state.dat before the first solve"). It has
  been reverted to its committed state so a half-written state from a failed
  run cannot be picked up by a later solve.
