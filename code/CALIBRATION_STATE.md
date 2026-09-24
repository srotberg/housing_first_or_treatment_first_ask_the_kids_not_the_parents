# THE TREATMENT FIRST RUN IS NOT THE PAPER'S TREATMENT FIRST, 24 September 03:05

The TF worker flagged this in its partial table (`results/counterfactuals/
treatment_first/RESULT_PARTIAL.md`, commit 9006ef40). I checked it against the
source before recording it, and it is wider than the worker said.

## WHAT THE SOURCE DOES ON THE FROZEN PATH

Every counterfactual this round runs on the FROZEN SCAN PATH: the benchmark
binary, `is_counterfactual = 0` (a compile-time `parameter`, line 189), with the
policy switched on through handover names. Two branches in the voucher code
were written when a counterfactual always meant `is_counterfactual = 1`, and
both are dead on this path:

    32257  elseif ((is_counterfactual==1) .AND. (fails_1==1) .AND. &
               ((increased_prob_of_voucher_if_homeless_and_addicted==0) .OR. &
                (voucher_conditional_on_clean==1))) then
               voucher_index_1=3        ! "THE HOUSED LOSE IT TOO"

    32381  if ((is_counterfactual==1) .AND. (voucher_index_1==3) .AND. &
               (increased_prob_of_voucher_if_homeless_and_addicted==0)) then
               first_voucher_index=0    ! a failed holder can drop to no voucher

32257 is what puts a HOUSED household that fails the test into the tested
category; 32381 is what lets a failed voucher holder actually lose the voucher.
The worker found the first. The second depends on it and is dead for the same
reason. Together: **on the frozen path no housed voucher holder is ever
tested out of the voucher.** Conditionality bites only on homeless households,
through the ungated branch at 32247.

## WHY IT MATTERS

The paper's Treatment First is universal. Line 372 of the note: "some
households lose the voucher though they meet the condition and some keep it
though they do not" -- a holder who uses faces p_det. And the source's own
comment at 32259 says the same thing: "Under a universal programme that is
every household there is." CLAUDE.md's hardest-won transition lesson is about
exactly these revocations reaching a child. The current TF run measures
conditionality at ENTRY for the homeless only.

## WHAT A FIX WOULD INVALIDATE

Deleting `(is_counterfactual==1) .AND.` from both lines is inert everywhere
except Treatment First, and that follows from the conditions themselves rather
than from a run: both branches ALSO require
`increased_prob_of_voucher_if_homeless_and_addicted == 0` or
`voucher_conditional_on_clean == 1`, and the base handover carries 1 and 0
(lines 18 and 91). So the benchmark, every omega_c scan point, omega_c = 1 and
the internalisation run cannot reach either branch with or without the guard.
It invalidates the current TF run and nothing else.

NOT APPLIED. It is a model edit and the author's call, and three solves are
live in other containers. If approved, it goes in by sed into a build directory
for the TF run -- as the transition scripts now do -- and into the tracked
source only once no solve is running.

## OTHER is_counterfactual GATES, FOR THE RECORD

The frozen path differs from the old `is_counterfactual = 1` path in more than
the voucher code: rental supply (16970), the FMR standard pinned at the
benchmark's calibrated rent (18244), the benchmark's voucher probabilities read
from file (36766). Those apply equally to every frozen-path counterfactual,
including the whole omega_c scan the author has already accepted, so they are a
design choice already made rather than a TF defect. Recorded, not raised.

## A CORRECTION: EARLY BLOCKS DO NOT ALWAYS OVERSTATE THE DROP

I told the TF worker the early blocks of every point overstate the drop, and it
repeated that in its write-up. Its own table contradicts it: b FALLS at every
block, 0.0511 -> 0.0398 -> 0.0374 -> 0.0371 -> 0.0356 -> 0.0333 -> 0.0322, so
here the early blocks UNDERSTATE it. The claim came from omega_c = 1 and the
control, where b rose after block 1. It is a property of those points, not of
the family.

# THE REFERENCE FOR EVERY CEV THIS ROUND DID NOT EXIST, 24 September 02:56

`save_welfare_curve` (22710) writes the curve of the economy that just ran,
`welfare_curvebaseline_benchmark.dat`, from its own saved policies. It does not
compare two economies. A CEV is formed by reading one economy's welfare against
another's curve, so every counterfactual at omega_c = 0.06 needs HOUSING FIRST
AT omega_c = 0.06 to have a curve. Its converged state was lost when that
session blocked on a commit and was reclaimed, and nothing of it is on the
branch (`git ls-files | grep welfare_curve` shows only the n90 and old seed
benchmarks).

Re-solving it: session_015uvFUYEc5ziAB37Ckjvp5o, `remote_scan_point.sh 0.06`
with `frozen_stop_after_blocks 12` so it exits into the curve without a kill or
a resume, and `kappa_x 0.9329`. Control stated in advance: block 9 must
reproduce the lost run's b = 0.081242 at 1e-4 relative.

kappa_x in the runs already going: omega_c = 1 and TF carry 0.8139 from the
base. With internalise_homelessness_cost = 0 it moves no policy function, and
the welfare it subtracts is exactly kappa_x * H * beta^K * D_adult, which the
KAPPA_X PROBE prints as hd_1. So a curve built at 0.8139 converts EXACTLY to
0.9329 by subtracting (0.9329 - 0.8139) * hd_1 at every x. No rerun needed,
provided the probe lines are kept.

ω_c = 1's welfare is a comparison across different preferences (the parent
weights the child at 1 against 0.06), so what its CEV means is for the author
to decide; it is a bookend on drug use first.

