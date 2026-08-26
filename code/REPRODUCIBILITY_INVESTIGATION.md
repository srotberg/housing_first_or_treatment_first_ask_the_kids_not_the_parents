# The archive does not reproduce, and the cause is not yet known

**Status at 2026-08-26 23:35Z: calibration HALTED. Four hypotheses tested and
refuted. Do not resume the search until this is resolved.**

## The fact

`point_ad09bce9b1` is the archive's leader at loss **0.2660**, measured and
committed 2026-08-26 01:33Z. Re-running its own recorded VECTOR returns
**2.5642**. Same 24 parameters, same 20 moments.

The collapsed run is not a different equilibrium, it is a broken economy:

| moment | recorded 01:33 | re-run | target |
|---|---|---|---|
| cbar (food stamps / labour income) | 0.00392 | **2.033** | 0.0042 |
| beta (wealth / output) | 3.588 | **0.1377** | 3.0 |
| aleph (value of life / income) | 57.7 | **-2.837** | 80 |
| b (drug participation) | 0.0729 | **0.9585** | 0.089 |

It also emits `IEEE_INVALID_FLAG` and `IEEE_DIVIDE_BY_ZERO`.

All 81 points measured on 26 August fall in a band of 2.427 to 2.736
**regardless of their parameter vectors**. They measure the fault, not the
parameter space. They are quarantined in `code/points_quarantine/`, not
deleted: they are evidence.

## What has been REFUTED. Do not re-propose these.

1. **zeta_DI = 0.** Running the anchor at `zeta_DI=0.0825` and at `zeta_DI=0`
   gives BIT-IDENTICAL results at every moment. zeta_DI has no effect on this
   model at all. (A whole diagnosis was built on this and it was wrong.)

2. **The 26 August Fortran edits** (`measure_child_gap` 1->0, the wealth
   histogram, the zeta_DI declaration). The pre-change binary, built from
   79e1af9, returns **2.5635** on the same vector -- indistinguishable from the
   current binary's 2.5642.

3. **Persisted disk state.** The model writes and reads
   `drug_supply_shifterbaseline_benchmark.dat`. Deleting it and re-running
   returns 2.5642, and the file regenerates at 0.27030 against the previous
   0.27028. It is an OUTPUT the model converges to, not a poisoned input.

4. **An incomplete VECTOR.** The anchor's VECTOR carries all 24 parameters that
   `run_one_point.sh` knows. Nothing is silently taking a default.

## What that leaves

Same parameters, same code, same disk state, same 24 inputs -- and a different
answer. One of those four statements must be false in a way not yet tested.
The most likely remaining candidates, untested:

- **The Fortran that PRODUCED the anchor is not the Fortran at 79e1af9.** That
  commit is where the point FILE was committed, which may be long after the
  run. Find the binary or the commit actually in force when it ran.
- **A data input changed** (the CSVs the model reads at startup). Check
  `git log` over `data/` and over `code/*.csv`.
- **The archive itself is inconsistent**: the VECTOR line and the moments in a
  point file are written from different sources (`P` array vs `worker_TAG.log`)
  and could mismatch if a stale log were present. TAG is the md5 of the
  parameter vector ONLY -- it does not include the binary -- so two runs of the
  same vector under different code collide on one filename, and the self-skip
  means the second never runs.

## Why this matters beyond today

If a point is not reproducible from its recorded vector, then two archived
points may differ because of something other than their parameters, and the
ranking that picked 0.266 as the leader is not established. This is a bigger
problem than a lost day of compute.

## The rule that would have caught it

Re-run the incumbent's own vector and confirm it reproduces BEFORE trusting a
round. That check takes one point and half an hour. It was never run, and a
full day of search measured a fault instead of a model.
