# SEED2 lines 4, 5 and 6 -- no moments measured

Branch `claude/two-period-addiction-hazard-d7gb61`.
Source `code/housing_first_or_treatment_first_SR_v1.f90`
md5 `3ef2b74f29945282733c633f9c7205d3`, stamped `MODEL 3ef2b74f29`.
Binary built from that md5 and verified by `hftf.srcmd5`, so the moments and the
stamp come from the same source.

## Status

| line | point | vector change | result |
|---|---|---|---|
| 4 | `b79faeb4c2` | `increased_prob_if_homeless=4.0` | **VOID** -- stopped at 73 min, still in the priming solve, no moments block |
| 5 | not run | `increased_prob_if_homeless=6.0` | **not run** -- see below |
| 6 | `c03bbf9c1e` | `rho_d=0.70`, x left at 0.2 | **in flight** -- same cost profile as line 4 |

No line produced `===== END OF MOMENTS =====`, so by the rule in the brief no
numbers from any of them are reported. `points/point_b79faeb4c2.FAILED.txt` is
filed as FAILED, not as a point: it carries `HANDOVER OK: 33 of 33` and a
correct VECTOR line but no moments, and the already-measured check keys on
`END OF MOMENTS`, so it will not be served in place of a real measurement.

**The three questions in the brief are unanswered.** Question 1 needs the
employed share at x=4.0 and x=6.0; question 2 needs the band-1 share at both;
question 3 needs a completed solve at `rho_d=0.70`. None exists. No
interpolated x and no extrapolated value is quoted anywhere below.

## Why nothing completed

Every working age costs about 191 seconds instead of about 0.4 seconds. From
line 4's flushed `AGE_TIME` lines, the step is clean and it is not gradual:

```
AGE_TIME age=  42  wall_s=      0.39   cpu_s=      1.54
AGE_TIME age=  41  wall_s=      0.37   cpu_s=      1.50
AGE_TIME age=  40  wall_s=    191.52   cpu_s=    223.63
AGE_TIME age=  39  wall_s=    193.67   cpu_s=    226.31
...
AGE_TIME age=  18  wall_s=    186.49   cpu_s=    218.33
```

Ages 60 down to 41 are retired, have no binding labour-supply solve, and cost
0.23-0.40 s each. From age 40 down -- every working age -- the cost is ~191 s,
a factor of about 500.

The cause is the labour-supply secant warning at
`housing_first_or_treatment_first_SR_v1.f90:20826`. It fires when the secant
leaves its loop without converging, and on this source it fires for
essentially every working-age household state. Each occurrence costs twice:

- `max_loop_count=1000` against `stopping_rule_secant=1e-8`, so a failing state
  runs the full thousand secant iterations;
- eleven `write(*,*)` statements, and `run_one_point.sh` sets
  `GFORTRAN_UNBUFFERED_ALL=1`, so each is a syscall on a shared stdout. All
  four OpenMP threads serialise on it, which is why the process sits at
  117-120% CPU rather than near 400%.

Line 4 emitted **6.3 GB** of this in 73 minutes. The `SPAM` filter in
`run_one_point.sh` keeps it off the disk -- the worker log stayed at 36 KB --
so this is invisible in the archived output and costs only time.

The warning is inert. It fires *after* the loop, writes no state, and the
normal `call objective(...)` follows it. The arithmetic is not corrupted; only
the cost is prohibitive.

Extrapolating line 4: the priming solve alone is ~40 slow ages, about 128
minutes, and the priming solve only fills age one so the child term can be
computed. The B-sweep solve follows, across two beta types. One point is
several hours at best.

## It is NOT the parameter under test

This was my first reading and it was wrong; recording the correction because it
changes what the fix is. Line 6 holds `increased_prob_if_homeless` at its
default 0.2 and emits the same firehose at the same rate:

| run | x | stdout rate |
|---|---|---|
| line 4 | 4.0 | 1,426,907 B/s |
| line 6 | 0.2 | 1,420,652 B/s |

0.4 per cent apart. The non-convergence is therefore not caused by pushing
`increased_prob_if_homeless` to the top of its bracket, and line 4 was not
misbehaving relative to any other point on this source.

What this evidence does **not** settle is whether the cause is the source or
the rest of the SEED2 vector, which is common to all nine lines and carries
`lambda_addiction=18.148733` (default 5.0554) and `kappa_uem=28.67112`
(default 1.01931). Separating those needs a run at the script's defaults on
this source, which is another multi-hour solve and was not done. Both
candidates are consistent with what was measured and neither is asserted here.

The archive cannot settle it either: **no point has ever been measured on this
source.** `MODEL 3ef2b74f29` appears on exactly one file in `points/`, which is
line 4's own void record. This matches `run_one_point.sh`'s own note that no
archived point carries a hash at or after `84c1ee5`, the commit that made this
warning able to fire, and matches `f323b06` ("Cap the run log at 2 GB, because
one run wrote 24 and nearly filled the disk"), which capped the symptom.

## Why line 5 was not run

`increased_prob_if_homeless=6.0` sits further into the same region and costs at
least what line 4 cost, for the same outcome: hours of compute and no moments
block. It was skipped deliberately rather than dropped silently. It is worth
running once a point completes on this source at all.

## What would make these measurable

The fix is in the Fortran and is out of scope for this session, which was told
not to edit that file:

1. **Throttle the warning.** Fire it once, or count occurrences and report the
   count with the invariants. This alone should recover most of the 500x. It is
   what `run_one_point.sh`'s comment already proposes, and it belongs to whoever
   owns that file.
2. **Then ask why the secant fails.** A thousand iterations to 1e-8 failing on
   essentially every working-age state is a real numerical finding independent
   of its cost, and it is currently silent in every archived moments block.

Only after (1) is it worth re-running lines 4, 5 and 6.

## A separate note on rho_d

While this session ran, `c16a0f9` ("Hold both wage penalties at one and
re-point the unemployment shocks") landed on this branch and moved
`run_one_point.sh`'s default `rho_d` from 0.85 to **1.0**, recording an author
instruction that a substance use disorder should cost earnings by costing the
job rather than by cutting the wage of a household that keeps one.

Line 6 passes `rho_d=0.70` explicitly, so what it measures is unaffected. But
the brief describes line 6 as cutting `rho_d` "from 0.85 to 0.70", and 0.85 is
no longer the branch's centre. If `rho_d` is being held at 1.0 on instruction,
the whole 0.85/0.70/0.55/0.40/0.25 sweep in `SEED2.txt` (lines 1, 6, 7, 8, 9)
is a sweep away from a value the author has since switched off, and is worth
confirming before more compute is spent on it.
