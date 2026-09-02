# Borrowing-ON measurement at bn_on075 — RUN DID NOT COMPLETE

Tag: `b083f765a0`
Vector: `code/batch_bn_on075.txt`, run verbatim, no substitutions.
Binary: hftf built from source md5 `9d410dfdb996f127536efd3c7f71abb6`
(gfortran 13.3.0, installed into the container by `run_one_point.sh` at start).
Cores: 4.

## Outcome

**No measurement. There is no point file and no moments block.**

The solve started 2026-09-02 17:07 UTC and was killed at **04:21:15 elapsed
wall clock** (exit 137, SIGKILL) when the session container was restarted. The
kill was infrastructural, not a model failure: at the moment it died the
process was alive, holding ~114 per cent CPU, and had produced no error of any
kind. `code/points/point_b083f765a0.txt` was never created, and there is no
`.FAILED.txt` either — the binary simply never reached its output stage.

Per the standing instruction, the log is committed and reported; the vector has
NOT been changed and the run has NOT been retried.

## Step 4 first check — budget failures

    grep -ac "budget does not clear" code/worker_b083f765a0.log
    0

**The count is 0.** Caveat that matters: the log on disk is 237,568 bytes and
its last write was 17:25, eighteen minutes into a four-hour run. Fortran
buffers its output, so this is the flushed prefix of the solve, not the whole
of it — everything after 17:25 died in the buffer. The zero is therefore
genuine but partial: it covers the build, the parameter handover, and the first
passes over the distribution, which is exactly the stretch in which the broken
economy produced its 250,039 failures. Nothing in the flushed prefix looks like
the old bug.

A grep for `error|warn|NaN|Infinity` returns 5 hits, all of them false
positives: the substring "NaN" inside "fi**nan**cial". There are no genuine
error or warning lines in the log.

## The one economically informative line that did survive

    model_bequests(1) = -0.27481314748065910

Negative bequests. Debt is being held and carried to death, which is the thing
the borrowing-ON economy is supposed to do and which the borrowing-OFF control
at this vector cannot do at all. This is a sign of life, not a measurement — it
says renters are reaching the negative grid, it says nothing about where w_bot
or the bottom percentile shares land.

Other flushed diagnostics, for the record:

| quantity | value |
| --- | --- |
| bottom half's share of productivity | 0.16905002140174125 (target 0.17199999999999999) |
| model_financial(1) | 68.362621139013328 |
| model_total_net_wealth(1) | 35.033875133958148 |
| model_average_net_wealth | 0.40108947548409163 |
| model_homeownership_rate | 0.0 (as expected, ownership off) |
| model_average_rental_unit_size | 6.7047906883836286e-02 |
| mortgage_interest_rate | 2.9999996e-02 |
| sum_of_distribution | 87.346782389825364 |

None of these are scored moments and none of them answer the question the run
was set to answer.

## What cannot be reported

Everything the brief asked for in step 5 beyond the budget count:

- w_bot against the 0.0250 target — **not measured**
- the bottom-percentile wealth shares and whether any is negative — **not
  measured**, so no YES or NO can honestly be given
- beta against the 3.0–4.5 band — **not measured**
- every other scored moment and its per-cent gap — **not measured**

The open question stands exactly where it stood: whether pricing a renter's
debt as an unsecured loan rather than by the dwelling puts the bottom decile
mildly negative (against data −2.250e-03 / −4.220e-03 / −4.460e-03) or wildly
negative as the broken economy did (w_bot −0.068 to −0.487).

## The estimate was wrong by an order of magnitude

The brief budgeted 20–45 minutes and warned that the ON estimate had already
been too low twice. It was too low a third time, and not marginally: the run
was still going at **4 hours 21 minutes**, roughly six times the upper bound,
with no sign of being near the end. Borrowing-off points take 13–17 minutes on
these 4 cores, so borrowing-ON at this vector is at least fifteen times the
off cost, not "slower".

That is the finding that governs the next attempt. A 4-hour-plus solve driven
from a foreground shell in this container will keep losing to container
restarts, and each loss costs four hours and yields nothing. Whoever picks this
up should decide the mechanism before re-running — a longer-lived host, a
checkpoint the binary can resume from, or flushing the Fortran output so a
killed run still leaves a readable prefix. Re-running the same command in the
same place is a coin flip against the restart clock.

## Reproduction

    bash code/run_one_point.sh $(cat code/batch_bn_on075.txt | sed 's/^bash code\/run_one_point.sh //')

or, as run here, the line of `code/batch_bn_on075.txt` typed out verbatim.
