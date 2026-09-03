# Borrowing, measured now: the control is in, the borrowing arms are not

**STATUS AT THE TIME OF WRITING: ONLY LINE 1, THE BORROWING-OFF CONTROL, HAS
BEEN SOLVED.** Lines 2 and 3 -- the two arms that actually carry
`include_unsecured_borrowing=1` -- have NOT been measured. Question one and
question two are therefore both UNANSWERED, and nothing below should be read as
bearing on either.

This file is written and committed before the borrowing arms are in because the
control is a real measurement and holding it costs more than publishing it
early: a previous worker held four solved points and lost them when the source
moved.

## What was asked and what exists

| line | `include_unsecured_borrowing` | limit | `discount_factor_impatient` | point | state |
|---|---|---|---|---|---|
| 1 | 0 (control) | 0.30 (inert) | 0.75 | `de322e4659` | **SOLVED**, 13 min |
| 2 | 1 | 1.50 | 0.75 | `d42e5af187` | **NOT MEASURED** |
| 3 | 1 | 1.50 | 0.90 | -- | **NOT MEASURED** |

## The MODEL lines

Only one point exists, so there is nothing yet to agree with. Line 1 was solved on

    MODEL 1b081ebc4d

which is the md5 of `code/housing_first_or_treatment_first_SR_v1.f90` at branch
commit `4591262`, the head this batch started from. The source in the working
tree was verified byte-identical (`1b081ebc4d54ffc28733415fe67f5989`) at every
restart listed below, and `hftf.srcmd5` matched it throughout, so no rebuild
ever occurred mid-batch. **When lines 2 and 3 are measured they must be checked
to carry this same MODEL line**; if they do not, the three points are not one
economy and the comparison is void.

Note that `origin/claude/two-period-addiction-hazard-d7gb61` has since moved
**180 commits ahead**, and its head rewrites the Fortran source by **1180
insertions and 110 deletions** -- its md5 is `372c0fd0bfe465a41a9bf6c992202149`
against this batch's `1b081ebc4d54ffc28733415fe67f5989`. Merging or rebasing
into this working tree would rebuild the binary and split the batch across two
economies, which is why it was not done. This file and the line 1
point were pushed from a SEPARATE CLONE so that the source under the batch never
moved.

## Why lines 2 and 3 are missing

Not a build failure and not a segfault. The container running this session was
restarted five times, killing the solver each time. Line 2 was attempted five
times and never completed:

| attempt | survived | outcome |
|---|---|---|
| 1 | -- | container restart |
| 2 | -- | container restart |
| 3 | ~47 min | container restart |
| 4 | ~4 min | container restart (run was detached with `setsid`; did not help) |
| 5 | ~81 min | container restart, still solving |

The restarts are not caused by the run. Resident memory was sampled through
attempt 5 and sat flat at **678 MB against 16 GB available**, with no cgroup
limit and no OOM record; the process was in state `R` with all 4 threads live
and CPU falling smoothly from 221% to 127% as the parallel phase gave way to a
serial one. It was healthy when it was killed.

The load-bearing fact for whoever picks this up:

**THE BORROWING ARM IS AT LEAST SIX TIMES SLOWER THAN THE CONTROL.** Line 1 with
borrowing OFF solved in 13 minutes. Line 2 differs from it in exactly two names
-- `include_unsecured_borrowing` 0 -> 1 and `unsecured_borrowing_limit` 0.30 ->
1.50, the latter inert when the former is 0 -- and was still solving at 81
minutes. Turning the seven negative grid points on is what costs this. Any
future attempt should budget well over 81 minutes per borrowing point, and the
run has no checkpointing, so a restart loses all of it.

## Line 1: the borrowing-OFF control, point `de322e4659`

`w_bot`, net worth share of the bottom half:

    w_bot   model 2.4448e-02   target 2.5000e-02   rel 2.2%   IN

The lower tail, untargeted, against the data values in the brief:

    UNTARGETED wealth share bottom  1 pct   model +1.2093e-04   data -2.250e-03
    UNTARGETED wealth share bottom  5 pct   model +6.0464e-04   data -4.220e-03
    UNTARGETED wealth share bottom 10 pct   model +1.2093e-03   data -4.460e-03

All three model figures are POSITIVE, all three data figures NEGATIVE. This is
the zero-wealth floor and it is exactly what the brief describes; it is the
control, so it is the expected result and not a finding. The three figures stand
in ratio 1 : 5 : 10, i.e. the bottom ten per cent hold a share exactly
proportional to their number, which is the signature of a mass of households
sitting at precisely zero.

Whether borrowing moves any of these negative is the question this batch exists
to answer, and it remains open.

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

The two that are out are `beta` and `pi_eu`, which are the two the brief said to
expect out: `pi_eu`'s target moved to 0.049 today and `beta`'s band floor went
back to 3.0 today. Neither is a failure of this batch. The other seven are in,
and `w_bot` is on target at 0.75 impatience, which is the premise the batch was
built to test.

## What is NOT established

Stated explicitly, because the two questions this file was commissioned to
answer are the two it cannot answer:

- **Question one, is any bottom-percentile share negative?** UNKNOWN. No point
  carrying `include_unsecured_borrowing=1` has been solved. It remains true, as
  the brief states, that borrowing has never once been measured on a sound
  build. The control's positive shares say nothing about this either way -- with
  borrowing off the floor is at zero by construction.
- **Question two, where does `w_bot` land at impatience 0.90?** UNKNOWN. Line 3
  was never started.
- Whether 0.75 is an artefact. UNKNOWN, and it is worth being blunt: line 1
  shows `w_bot` on target at 0.75 with borrowing off, which is the situation the
  brief already described. It is not evidence about what borrowing does.

No extrapolation past the one arm measured is offered here, and none should be
read in.

## To finish this

Lines 2 and 3 of `code/batch_borrow_now.txt`, run from the repository root, on a
source whose md5 is `1b081ebc4d54ffc28733415fe67f5989` -- otherwise line 1 has
to be re-solved too. Budget over 80 minutes each and expect to lose runs to
restarts.
