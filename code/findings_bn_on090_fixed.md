# bn-on090 on the fixed budget constraint: RUN DID NOT COMPLETE

Tag `c71818d904`. Model hash `9d410dfdb996f127536efd3c7f71abb6`, built from
`9023afc` ("A renter's negative position is unsecured debt, not a mortgage: fix
three sites") -- i.e. this is the post-fix binary.

## Outcome: no measurement

**There is no point file and no moments block.** The solve ran 4 h 20 m of
wall-clock (4 h 39 m of CPU, 111-148 per cent of 4 cores throughout) and was
then killed by a container restart, exit 137. `code/points/point_c71818d904.txt`
was never written.

Nothing below is a moment. w_bot, beta and the wealth shares are NOT reported
here because they were never produced. The run was not retried and the vector
was not changed.

## The one thing the partial log does say: budget failures = 0

    grep -ac "budget does not clear" code/worker_c71818d904.log
    0

Zero, against the 250,039 the pre-fix binary produced in one solve.

Two qualifications, both of which matter:

1. **The log is truncated at 266,240 bytes** -- exactly 65 x 4096, a `grep`
   block boundary -- and stopped growing at 17:20, about ten minutes into a
   four-hour run. So this is zero failures over the opening phase (parameter
   handover, grid construction, the start of the value-function and
   distribution sweeps), not zero over the whole solve. The count is a
   favourable early signal, not the clean bill of health step 4 asked for.
2. **The SPAM filter is not hiding them.** `SPAM` in `run_one_point.sh` drops
   only twelve debug lines (`labor*`, `loop_1=`, `MU_1=`, `MU_2=`, `x_0..2=`,
   `distance_secant=`, `addiction_index_1=`, `consumption_choice=`,
   `frac_spent_on_addiction=`, `taxable_income_1=`). "budget does not clear" is
   not among them and would have survived the pipeline, and the grep here
   carries `-a`.

The log's last flushed content is mid stationary-distribution sweep
(`distribution distance= 1.249E-003`, newborn parent shares and productivity
draws printing normally). No NaN, no error, no warning anywhere in the 1,382
captured lines.

## Why it took four hours

Borrowing-ON was flagged as slower than the 13-17 min borrowing-OFF points and
as having been under-estimated twice. It is worse than that: this point was
still running at 4 h 20 m having shown no sign of finishing.

There is a prior at almost exactly this coordinate. The log-cap comment in
`run_one_point.sh` records that on 31 August a point at
`discount_factor_impatient=0.91` was "still going after forty two minutes" with
a 24 GB log, and was killed as a runaway loop. This run sits at 0.90, one
hundredth away, and ran six times longer than that one did before it was
stopped. The symptom differs -- the log here stayed at 266 KB rather than
exploding, so whatever is slow is not the thing that was printing -- but the
neighbourhood is the same, and a high impatient discount with borrowing on has
now failed to terminate twice.

That is the finding worth acting on: at `discount_factor_impatient=0.90` with
`include_unsecured_borrowing=1` this model may not be solvable in a sane time on
4 cores, independently of the budget bug that was just fixed.

## What is still unknown

Everything the run was commissioned to decide. Whether a less impatient
household can produce a low bottom share with borrowing correctly priced is
untested: w_bot against the 0.0250 target, the sign of every bottom-percentile
wealth share, and beta against the 3.0-4.5 band are all unmeasured. The
borrowing-OFF control `de322e4659` (w_bot 0.0247429, beta 2.4532 at an impatient
discount of 0.75) has nothing to be compared against yet.

Deciding what to do next -- a longer-lived runner, more cores, or an impatient
discount stepped down from 0.90 toward the 0.947867 knife-edge -- is the
author's call, not something to be settled by relaunching a changed vector here.

## Reproduce

    bash code/run_one_point.sh $(cat code/batch_bn_on090.txt | sed 's/^bash code\/run_one_point.sh //')

or just the verbatim line in `code/batch_bn_on090.txt`. Partial log committed as
`code/worker_c71818d904.log` (force-added; `*.log` is gitignored).
