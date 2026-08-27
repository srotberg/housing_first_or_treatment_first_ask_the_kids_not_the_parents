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

## Further candidates eliminated, 23:50Z to 00:05Z

5. **The bisect used the wrong Fortran.** It did not. The Fortran at 79e1af9 is
   byte-identical to 20a5fc0, the last change before the anchor was committed,
   and no Fortran commit falls in the window between them. The pre-change
   binary tested WAS the one in force.

6. **A data input changed.** No. The model reads only
   `data/us_mh_onset_shape.csv` (19 Aug) and `data/us_mortality_multipliers.csv`
   (16 Aug). Neither has been touched since.

7. **The archive is internally inconsistent.** No, at least not on the axis
   that is checkable: for every point tested, the VECTOR line hashes to the
   filename, exactly as run_one_point.sh computes TAG. Vector and name agree.
   (This does NOT rule out moments coming from a stale `worker_TAG.log`, which
   remains untested.)

8. **Thread-count non-determinism.** No. 412 of 422 archived points record
   "4 cores", the anchor among them, and this container has 4.

9. **A truncated run.** The anchor took 33 min and the re-run 12, but the
   archive's runtimes span 8 to 54 min with a median of 14, so 12 is
   unremarkable. `code/CALIBRATION_ACTIVE` is a marker for other scripts;
   neither the Fortran nor run_one_point.sh reads it.

## Where that leaves it

Same code, same data, same disk state, same 24 parameters, same core count --
and 0.2660 becomes 2.5642. Every cheap explanation is now excluded. What
remains needs real work rather than another quick check:

- **Whether the moments in a point file can come from a stale worker log.**
  run_one_point.sh takes the VECTOR from its own `P` array but the moments from
  `worker_${TAG}.log`. TAG hashes the PARAMETERS ONLY. If that log survived
  from an earlier run of the same vector under different code, the file would
  pair a correct vector with foreign moments and hash-check clean. This is the
  strongest remaining lead and it is testable by looking for surviving
  worker_*.log files older than their point files.
- **Whether the anchor's 0.2660 was ever real.** If several other pre-26-August
  points also fail to reproduce, the fault is systemic and old, not something
  that happened on 26 August. Re-running two or three of them settles it and
  costs about an hour.

DO NOT propose a cause without a test that could refute it. Three confident
diagnoses on 26 August were each built from reading a diff, and each was wrong.

## FOUND: the parameters never reach the model

**2026-08-27 ~01:50Z. This supersedes every hypothesis above.**

### The proof

Three archived points, three completely different parameter vectors, re-run:

| point | recorded loss | re-run loss |
|---|---|---|
| point_ad09bce9b1 | 0.2660 | **2.5642** |
| point_0a9aeef808 | 0.2871 | **2.5642** |
| point_d882c4a789 | 1.5301 | **2.5642** |

Identical to four decimals, with identical moments (`cbar` 2.0326, `b` 0.95854,
`lambda_d` 0.035822). A broken model gives varying wrong answers. One fixed
answer for every input means the input is not being read.

Confirmed directly: `value_of_life` set to **200.0** against the anchor's
35.0957 -- a 5.7x change in a headline parameter -- returns loss 2.5642 and
`aleph` -2.8374, unchanged to four decimals. And the model log contains
**ZERO `HANDOVER` lines**, where the Fortran prints one per parameter it
applies.

`run_one_point.sh` has not been specifying points. The model runs one fixed
configuration whatever is passed to it.

### The mechanism, from the Fortran's own comment at line ~30425

> THE HANDOVER FILE, AND IT CONSUMES ITSELF. ... The model takes the value
> from a file instead, AFTER the state is read, and deletes the file as it
> does.

The handover is a ONE-SHOT SEED, not a specification. It is applied on top of
`calibration_state.dat` and the file is deleted as it is consumed. It only
takes effect if the run reaches that read with the file present. It currently
never does -- no HANDOVER lines are printed at all.

### What it explains

Every confusing observation of 26 August, at once: three vectors giving one
answer; "simplex arms" uniformly at ~2.5; "0 of 19 vertices improved"; the
pre-change and post-change binaries agreeing exactly; zeta_DI having no effect;
clearing the disk state changing nothing. None of those were about the model.

### What it costs

The 422-point archive records whatever calibration state each container
inherited, NOT the parameters on its VECTOR line. Pre-26-August points DO
differ from one another, so the handover worked at some point and broke at a
specific moment. Finding when tells you which points are trustworthy.

### The next steps, in order

1. Find why the handover read is not reached. It is guarded by
   `handover_status==0` from an `open(...status='old')`; if the file is absent
   at that moment the whole block is skipped silently. Check whether an earlier
   run deletes it before the read, or whether the read sits behind a branch the
   current configuration does not enter.
2. Find WHEN it broke, by bisecting over archived points: the last point whose
   moments differ from its neighbours' is the last one that honoured its
   parameters.
3. Make a point specify itself. A parameter file that is consumed and deleted
   cannot make a run reproducible; the model needs to read its parameters on
   every run, or run_one_point.sh must verify the HANDOVER lines appear and
   fail loudly when they do not.
4. Only then re-establish a baseline and restart the search.

### The rule this should leave behind

`run_one_point.sh` must assert that the model echoed a HANDOVER line for every
parameter it was given, and fail the point if not. A silent no-op in the one
step that makes a measurement mean anything is what turned a full day of
compute into noise.
