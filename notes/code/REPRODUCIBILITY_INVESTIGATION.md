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

---

## RESOLVED, 27 August: the cause, the fix, and a correction to the section above

### The cause

`read_calibration_state()` has **two early returns above the handover read**:

```fortran
inquire(file="calibration_state.dat",exist=state_exists_1)
if (.NOT. state_exists_1) then
    write(*,*) "no calibration_state.dat, starting from the declared values"
    return                      ! <-- 190 lines above the handover
end if
...
if (trim(state_tag_1) .NE. "calibration_state_v3") then
    ... ; return                ! <-- the second one
end if
```

`calibration_state.dat` is **not in the repository**. A container that has never
run the model therefore has none, takes the first return, and never opens
`PARAM_HANDOVER.txt` at all. The run then solves at the values written in the
Fortran declarations, prints a complete moments block, and says nothing about
the vector it threw away.

### The proof, in both directions

| test | `calibration_state.dat` | binary | HANDOVER lines | `PARAM_HANDOVER.txt` after |
|---|---|---|---|---|
| A | absent | before the fix | **0 of 3** | still there, unread |
| B | present | before the fix | 3 of 3 | consumed |
| C | absent | **after the fix** | **3 of 3** | consumed |

Test B is the control that says the handover code itself was never broken: with
a state file present it applied `value_of_life` 34.4153 -> 200, exactly as
written. Only the path to it was.

### Why it stayed hidden for a day

It bites the **first** run in a container that has never run the model, and only
that one. That run's own calibration loop writes `calibration_state.dat` at the
end of its first pass, so every later run in the same container finds the file,
falls past the early return, and gets its handover. A worker that measured six
points lost its first and honoured its other five.

### The blast radius: one point in 423

A run that discarded its handover ran the same declared vector as every other
such run, so it has a fixed signature: `aleph` = -2.8373745075468442 and
`cbar` = 2.0325575259878872, every time. Scanning the archive for it:

```
points measured with the handover DISCARDED : 1    (point_01658bd93e, rank 358, loss 2.564)
points whose parameters reached the model   : 422
```

The leader at 0.266 and the whole ranking above it are unaffected.

### The correction

**The entry above concluded that every point measured on 26 August was invalid.
That was wrong, and it should be read with this paragraph attached.** All three
reproducibility re-runs it rests on were first runs in a container that had
never run the model, so all three hit the bug; their agreeing to four decimals
was the bug's signature and not evidence about the archive. The archive itself
refutes the conclusion directly: of the 11 values of b measured by more than one
point with the other 23 parameters differing, **all 11 give different moments**.
The parameters were reaching the model in the workers. They were not reaching it
here.

The wider lesson is the one that was already written down and not followed: the
inference ran from a diff and a coincidence rather than from a falsifiable test,
and it was the fourth confident wrong diagnosis in the same investigation. Test A
above -- run the binary, count the lines -- costs ninety seconds and would have
settled it before any of the four.

### What was changed

1. **`apply_param_handover()`**, split out of `read_calibration_state` verbatim
   and called by the caller straight afterwards, so the seed is applied whether
   or not there is a state to resume from.
2. **`run_one_point.sh` deletes `calibration_state.dat` and
   `calibration_distribution*.dat` before each point**, so a point is a function
   of its vector and nothing else. Without this the fix would have created a
   second version of the same defect: the first point in a container now banks
   its handover into a state file, and the second point -- whose handover is
   consumed and deleted as it is read -- would resume from the first point's
   parameters.
3. **`run_one_point.sh` counts the HANDOVER lines and fails the point unless the
   model echoed one for every parameter it was handed**, and records
   `HANDOVER OK: n of n parameters applied` in the point file when it did. A
   name the model does not recognise fails the point too.

### The cross-check required by TRANSITION_LESSONS section 7

Does it carry to the stylized model? **No.** The stylized model takes its
parameters as function arguments -- `calibrate(seed, ...)`, `with_(P(), **kw)` --
so there is no file channel through which a caller's vector can be dropped.
`calibrated.json` is a *seed*: its absence means a cold start from the class
defaults, which is a slower calibration and not a discarded specification. The
defect is specific to a model whose parameters arrive by side channel.

---

## 27 August, later: bug two, and a supervisor nobody was watching

### The leader does not reproduce, and it is not the build

Re-measured the leader's exact vector cold with the handover fix. All 23
parameters applied. Loss 0.304 against the archived 0.266; rank 41 against
rank 1.

The build was ruled out by rebuilding at `79e1af9`, the exact commit the leader
was measured at, patched ONLY to move the handover past the early return, and
running it cold on the same vector. The two binaries agree with each other on
all 23 moments to better than 1e-4 relative and both disagree with the archive:

| moment | archived | cold HEAD | cold 79e1af9 |
|---|---|---|---|
| b | 0.0729013 | 0.0578761 | 0.0578760 |
| gamma | 0.290055 | 0.248740 | 0.248740 |
| h_4 | 0.640946 | 0.576379 | 0.576379 |
| aleph | 57.6674 | 66.6564 | 66.6564 |
| cbar | 0.0039226 | 0.0024510 | 0.0024510 |

So what the archived run had and a cold run does not is CONTAINER STATE.

### What was in it: `.claude/hooks/session-start.sh`

The hook relaunches `supervise_calibration.py` -- the JOINT CALIBRATION LOOP --
on every remote session in this repository whenever `code/CALIBRATION_ACTIVE`
exists. It fires on every session, which means it fired in **every worker
container that measured a point**. It was found running here, unasked, ninety
seconds after a container restart, taking four cores beside a controlled test.

The supervisor writes `calibration_state.dat` and `calibration_distribution*.dat`
at the end of every loop, and it MOVES every internally calibrated parameter as
it goes. A point measured in such a container therefore read whatever the
supervisor had most recently written, which is a moving target, and competed with
it for the cores. That is the mechanism: an archived point is a measurement of
its vector PLUS wherever the joint loop happened to be at that instant.

The hook is not a bug; it is a documented device with `CALIBRATION_ACTIVE` as its
off switch, and it exists because a container rebuild used to cost half an hour
of idle. What was missing is that a POINT RUN and the JOINT LOOP must not share a
container, and nothing said so.

`code/CALIBRATION_ACTIVE` is now removed, which is the documented way to stop it,
and the removal is committed so the next container does not bring it back.
`touch code/CALIBRATION_ACTIVE` restarts it when the calibration resumes.

### The named suspect inside that state

Diffing the state a worker-era container carried against the one a cold run
writes, over the region where the alignment is verified -- seven handed
parameters land exactly where they should, through index 18 -- two economically
meaningful scalars differ, and neither is in any point vector:

| scalar | worker-era | cold (declared) |
|---|---|---|
| `relative_share_of_housing` | 0.19393803 | 0.14833560 |
| `drug_supply_shifter` | 0.57224533 | 1.0 |

`relative_share_of_housing` is internally calibrated, has its own adjuster in the
joint loop, and IS a case in the Fortran's handover -- `run_one_point.sh` simply
never hands it. Parameter updating is switched off during a b sweep, so whatever
it starts at is what the point is measured at. `drug_supply_shifter` is solved
inside the run, so it may converge to the same place regardless; not claimed.

Both point the right way: a lower housing weight gives less housing spending
(gamma 0.290 -> 0.249), costlier drugs give fewer users (b 0.0729 -> 0.0579).

The state file's alignment is only verified through index 18, because
`write_calibration_state` writes arrays (`rent(1,:)`, `housing_price`) that a
line-by-line reading cannot step over, and the two files differ in length. There
may be more differences past that point and this note does not claim there are not.

### Open, and not to be asserted without a run behind it

1. Does handing `relative_share_of_housing` at the worker-era value move the cold
   moments back toward the archive? Running.
2. Are two cold runs of the SAME binary bit-identical? The two builds gave
   0.05787611 and 0.05787596, which is small but not zero, and until the
   same-binary-twice test is run "deterministic" is not established.
3. If the answer to 1 is yes, every internally calibrated parameter that is not in
   the point vector has to go into it, and the 423-point archive has to be
   re-measured before its ranking means anything.

### The determinism test, and what it does not excuse

Same binary, same vector, twice, cold. The two runs are NOT bit identical: the
worst moment moves by 2.5e-5 relative (`lambda_d`), with `kappa_ued`, `tau_u` and
`theta` at roughly 1e-5 and most of the rest below 1e-6. That is the shape of
OpenMP reduction order -- floating point addition is not associative, the thread
that finishes first varies, and an iterative solver stopping on a tolerance
carries the difference forward.

It does not matter at the scale anything here is decided on. **Both runs score
0.304 to three decimals**, the archive's leader is 0.266, and the gap to explain
is 0.038 -- three orders of magnitude above the noise. The top of the archive is
separated by 0.001 between ranks, still forty times the noise. So run-to-run
non-determinism is real, is worth knowing about, and is NOT what makes an
archived point irreproducible.

### Bug two, closed as a diagnosis

Every alternative has a run behind its refutation:

| candidate | verdict | what settled it |
|---|---|---|
| the build | refuted | HEAD and 79e1af9 agree cold on all 23 moments to better than 1e-4 |
| run-to-run noise | refuted | two cold runs of one binary both score 0.304; worst moment wobble 2.5e-5 |
| the internal loop moving the vector | refuted | parameter updating is switched off during a b sweep |
| the handover | refuted | 23 of 23 applied, confirmed in the log of every run above |
| inherited container state | **the cause** | the SessionStart hook ran the joint loop in every worker container, rewriting the state each point read |

What remains is not a mystery but a decision. The archive's 423 points are each a
real measurement, but of "this vector PLUS wherever the joint loop stood at that
instant", and the quantity that varies between them is not the vector alone. The
ranking across them is therefore not a ranking of vectors, and the search that
was driven by that ranking was reading a signal it could not have been reading.

### Two things that should change before any point is measured again

1. **`relative_share_of_housing` and `housing_status_grid_expander` go into the
   point vector.** The model accepts both today; `run_one_point.sh` simply never
   hands them. Note this changes TAG, which is the md5 of the vector, so every
   archived point's filename stops matching -- which is moot if the archive is
   being re-measured and a blocker if it is not.
2. **The joint loop and a point measurement must never share a container.** The
   hook is the mechanism but the rule is the point: one of them owns
   `calibration_state.dat` and the other reads it, and they cannot both be right.
