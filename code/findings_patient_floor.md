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

## STATUS: NO MOMENTS MEASURED YET. Line 1 has been killed twice.

**No moment in this file is a measurement. Nothing has been measured.**

### The two deaths

| attempt | started (UTC) | died | log at death | log bytes |
|---|---|---|---|---|
| 1 | 2026-09-02 15:03:55 | ~15:14, ~11 min in | after the SMI block | 445,382,656 |
| 2 | 2026-09-02 21:12:06 | ~21:21, ~10 min in | after the SMI block | 445,382,656 |

Both were reported to the session as "the container was restarted".

### Why this is not bad luck

The two logs are **the same size to the byte**: 445,382,656 both times, from runs
started six hours apart, with the log deleted in between. Their last 150 lines
are identical, down to the digits of the SMI prevalence block:

```
 SMI mass over the working age base (not a prevalence)=   5.8862047860371240E-002  onset(1)=   2.76120600000000
```

A deterministic binary re-reading the same vector reaches the same instruction
and stops. That is a reproducible failure at a fixed point in the solve, not a
random infrastructure restart.

Two further details:

- 445,382,656 = 4096 x 108,736 exactly. The log ends on a page boundary, which is
  what an abrupt kill leaves behind: whole buffers flushed, the last partial one
  lost. So the true death point is up to one stdout buffer PAST the last line in
  the file, and the last visible line is a lower bound on progress, not the
  faulting statement.
- The run was healthy right up to it: `DIST_DONE sweeps=55
  final_distance=5.79e-04`, distribution converged, moments being accumulated.
  Nothing in the log suggests non-convergence or a numerical blow-up.

In the source, the statement after the last logged line is the
`"SMI share of homeless="` write at
`housing_first_or_treatment_first_SR_v1.f90:10122`, inside the per-beta-type
moment block that follows the distribution solve.

### What is NOT the cause

- **Not disk.** 30 G free at both deaths; the log was 425 MB against the
  script's own 2 GB cap.
- **Not a stale warm start.** `run_one_point.sh:444` deletes
  `calibration_state.dat` and `calibration_distribution*.dat` at the start of
  every run, by design, so "a point is a function of its vector and nothing
  else". Neither arm can inherit the other's state, and the torn state file the
  first death left behind cannot contaminate anything.
- **Not the vector being changed.** Both attempts ran line 1 verbatim,
  character for character, with no command substitution.

### Leading hypothesis, not yet confirmed

Memory. This vector is a **two-type** solve (`number_of_beta_types=2`,
`discount_factor_impatient=0.75`), and `run_one_point.sh:175` records that
"every point in `points/` was measured on the ONE-type model". So there is no
precedent in the archive for a two-type solve completing, and a second beta type
multiplies the state space. A container OOM would produce exactly what is seen:
a deterministic kill at the same point, a page-aligned truncated log, and an
infrastructure-level "restart" rather than a Fortran error.

This is a hypothesis. The next attempt samples resident memory so it is settled
by measurement rather than argument.

## Rules being followed

- The vector has NOT been changed, and will not be, on any retry.
- The Fortran source has NOT been modified.
- `supervise_calibration.py` has not been run; `code/points_pregrid/` untouched.
- Work is committed to `wip/patient-floor` only.
