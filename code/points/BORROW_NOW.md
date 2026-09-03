# Borrowing, measured now: the control is in, and BOTH borrowing arms fail to terminate

**ANSWER TO QUESTION ONE, UP FRONT: NOT ESTABLISHED, AND NOT BECAUSE THE SHARES
CAME BACK POSITIVE.** Neither borrowing arm produced a point. Both were run, on
the correct source, and both entered a phase roughly nine minutes in from which
they never returned. So this batch cannot say whether any bottom-percentile
share goes negative, and in particular it does **not** show that borrowing is
still inert. That question is still open.

**ANSWER TO QUESTION TWO: NOT ESTABLISHED.** `w_bot` at impatience 0.90 was
never measured, for the same reason.

What the batch did establish is operational and it is the reason the two
questions are still open:

> **Turning `include_unsecured_borrowing` on makes the solve non-terminating in
> practice.** The borrowing-OFF control solved in 13 minutes. The two arms that
> differ from it only in that switch ran **182 minutes** and **143 minutes**
> without producing a moment, and both stopped writing anything to disk about
> nine minutes in -- each having written the same 65,536 bytes and no more.

## What was asked and what exists

| line | `include_unsecured_borrowing` | limit | `discount_factor_impatient` | point | state |
|---|---|---|---|---|---|
| 1 | 0 (control) | 0.30 (inert) | 0.75 | `de322e4659` | **SOLVED**, 13 min |
| 2 | 1 | 1.50 | 0.75 | `d42e5af187` | **NOT MEASURED** -- ran **182 min**, no moments |
| 3 | 1 | 1.50 | 0.90 | `a2778b36aa` | **NOT MEASURED** -- ran **143 min**, no moments |

## The MODEL lines

Only one point exists, so there is nothing yet to agree with. Line 1 was solved on

    MODEL 1b081ebc4d

the md5 of `code/housing_first_or_treatment_first_SR_v1.f90`
(`1b081ebc4d54ffc28733415fe67f5989`) at branch commit `4591262`, the head this
batch started from. That md5 and `hftf.srcmd5` were re-verified at every
interruption below and never changed, and no rebuild occurred at any point, so
lines 2 and 3 were attempted against exactly the economy line 1 was measured on.
**If they are ever completed they must be checked to carry this same MODEL
line.**

`origin/claude/two-period-addiction-hazard-d7gb61` has meanwhile moved **180
commits ahead**, and its head rewrites the Fortran source by **1180 insertions
and 110 deletions** -- md5 `372c0fd0bfe465a41a9bf6c992202149`. Merging or
rebasing into this working tree would have rebuilt the binary and split the
batch across two economies. It was not done: line 1 and this file were pushed
from a **separate clone**, so the source under the batch never moved.

## The failure, in detail

This is not a build failure and not a segfault. The binary built cleanly and
both arms ran.

Both borrowing arms show the same signature. The solver does about nine minutes
of productive work, writes
`percentage_spending_on_housingbaseline_benchmark.txt`, and then computes
indefinitely without writing another byte:

| | line 2 (0.75) | line 3 (0.90) |
|---|---|---|
| run started | 03:57:05 | 06:59:57 |
| last file written | 04:06:07 (9 min in) | 07:08:51 (9 min in) |
| stopped by hand at | **182 min** | **143 min** |
| silent for | 173 min | 134 min |
| total `write_bytes` | 65,536 | 65,536 |
| state / threads | `R`, 4 threads | `R`, 4 threads |
| CPU over the run | 321% falling to 110% | 319% falling to 131% |
| resident memory | flat 678 MB of 16 GB | flat |

### Read the two stub point files with care

Stopping each run left `code/points/point_d42e5af187.txt` and
`code/points/point_a2778b36aa.txt`. They are committed because the runner writes
a file on every exit path so that a failure is not invisible, but **they are not
measurements, and their first line is misleading**: it reads `point ... solved
in 182 min`, which is the script's wording for elapsed time, not success. What
makes them stubs is the last line,

    NO MOMENTS BLOCK; hftf exit status 143

Status 143 is SIGTERM -- me stopping them deliberately. Neither file contains an
`END OF MOMENTS` marker or a single `MOMENT` line, so `run_one_point.sh` will
re-solve both rather than serve them, and nothing downstream can mistake them
for points. They are useful only as a record of the exact vector and MODEL line
each attempt ran under.

### The attempts

Line 2 was attempted **six** times in all. Five attempts were cut short by
container restarts (at roughly 47 min, 4 min and 81 min among them; one attempt
was detached with `setsid`, which did not help, because the whole container goes
down). The sixth ran undisturbed for 3 h 02 m and was stopped deliberately, not
killed. Line 3 was then started to see whether the stall was particular to the
0.75 discount factor. It is not: line 3 reproduces it at 0.90, to within two
minutes on the same file.

The restarts are not the cause and were not caused by the run: memory was flat
at 678 MB against 16 GB, there is no cgroup limit and no OOM record, and the
process was healthy in state `R` with all four threads live whenever it was
inspected.

**The inference, flagged as an inference:** a run that holds four threads at
100%+ for three hours while performing no I/O, having completed the same nine
minutes of work as its control, is very likely circling in a loop that is not
converging rather than merely working slowly. What is *fact* is the timing, the
silence and the two independent reproductions; that it is a non-convergent loop
rather than a very expensive one is not proven, and the model source was not
read or modified to find out, since this batch was instructed not to touch it.

## Line 1: the borrowing-OFF control, point `de322e4659`

`w_bot`, net worth share of the bottom half:

    w_bot   model 2.4448e-02   target 2.5000e-02   rel 2.2%   IN

The lower tail, untargeted, against the data values in the brief:

    UNTARGETED wealth share bottom  1 pct   model +1.2093e-04   data -2.250e-03
    UNTARGETED wealth share bottom  5 pct   model +6.0464e-04   data -4.220e-03
    UNTARGETED wealth share bottom 10 pct   model +1.2093e-03   data -4.460e-03

All three model figures POSITIVE, all three data figures NEGATIVE. This is the
zero-wealth floor the brief describes. It is the control, with borrowing off, so
it is the expected result and not a finding, and it says nothing about what
borrowing would do. The three figures stand in ratio 1 : 5 : 10 -- the bottom ten
per cent hold a share exactly proportional to their number, the signature of a
mass of households sitting at precisely zero.

### All nine round-1 moments, line 1

| moment | model | target | rel gap | inside 10%? |
|---|---|---|---|---|
| `aleph` | 75.9244 | 80.0 | 5.1% | yes |
| `beta` | 2.45321 | band 3.0-4.5 | 18.2% below the 3.0 floor | **no** |
| `omega_l` | 0.363506 | 0.40 | 9.1% | yes |
| `sigma_y` | 0.169050 | 0.172 | 1.7% | yes |
| `tau_l` | 0.226110 | 0.224 | 0.9% | yes |
| `pi_eu` | 0.134270 | 0.049 | 174.0% | **no** |
| `pi_V` | 0.255826 | 0.266 | 3.8% | yes |
| `cbar` | 3.9343e-03 | 4.2e-03 | 6.3% | yes |
| `w_bot` | 2.4448e-02 | 2.5e-02 | 2.2% | yes |

**Count inside ten per cent: 7 of 9.**

The two that are out are `beta` and `pi_eu`, the two the brief said to expect
out: `pi_eu`'s target moved to 0.049 today and `beta`'s band floor went back to
3.0 today. Neither is a failure of this batch. `w_bot` is on target at 0.75
impatience, which is the premise the batch was built to test and which it
reconfirms.

## What is NOT established

- **Is any bottom-percentile share negative?** UNKNOWN. No point carrying
  `include_unsecured_borrowing=1` has ever been solved -- still true after this
  batch, and now known to be hard rather than merely undone.
- **Where does `w_bot` land at impatience 0.90?** UNKNOWN.
- **Is 0.75 an artefact?** UNKNOWN. Line 1 reconfirms `w_bot` on target at 0.75
  with borrowing off, which is the situation the brief already described. It is
  not evidence either way about debt substituting for impatience.

No extrapolation past the one arm that produced a point is offered here, and
none should be read in. In particular, the three positive lower-tail shares
above are the control's, and must not be quoted as the borrowing result.

## To finish this

The blocker is now the runtime, not the batch. Someone has to decide whether the
borrowing arm converges at all before more wall-clock is spent on it: three
hours on one point, with no checkpointing and a container that restarts, is not
a measurement strategy. If it is to be retried as-is, it must be on a source
whose md5 is `1b081ebc4d54ffc28733415fe67f5989`, or line 1 has to be re-solved
alongside it.
