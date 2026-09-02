# BORROW15: unsecured borrowing at a limit of 1.50 years' average income

Three arms of `code/batch_borrow15.txt`: borrowing ON, limit 1.50, with
`discount_factor_impatient` at 0.75, 0.90 and 0.96. Solved on source md5
`64d52d8b6a`, semantic `197407b07d`, `pi_eu` target 13.9 per cent.

**Status: NO ARM PRODUCED A MOMENTS BLOCK.** Arm 1 (0.75) was killed at
4 h 06 min and arm 2 (0.90) at 2 h 32 min, both without moments; arm 3
(0.96) is running as a confirmation probe only. Neither completed arm
reached the code path where `discount_factor_impatient` is read, so
**none of the three questions the batch was built to answer can be
answered from it.** Nothing below extrapolates past what was measured.

## The headline questions, so far as they can be answered

### Is borrowing inert? The PATIENT type's solved policy reaches the limit; the mass on debt is unmeasured.

The ladder is built as declared, and in the one pass that ran -- the
patient type's -- the policy function chooses the deepest rung. So the
feature is not dead in the sense of the bounds being unreachable. But the
claim the batch was meant to test, that households *hold* debt and some
bottom-percentile wealth share therefore turns negative, is **NOT
established by anything measured here**, and cannot be until a run
produces a moments block.

The negative ladder is built exactly as declared. Recovering
`average_labor_income_calibrated` from the deepest rung the solver printed,
`-0.95587205886840820 / 1.5 = 0.637248`, and applying
`financial_grid(i) = financial_grid(1)*((8-i)/7)**2`:

| i | level | multiple of average income |
|---|---|---|
| 1 | -0.955872 | -1.500 |
| 2 | -0.702346 | -1.102 |
| 3 | -0.487690 | -0.765 |
| 4 | -0.312122 | -0.490 |
| 5 | -0.175569 | -0.276 |
| 6 | -0.078031 | -0.122 |
| 7 | -0.019508 | -0.031 |
| 8 |  0.000000 |  0.000 |

which reproduces the specified ladder
`-1.500 -1.102 -0.765 -0.490 -0.276 -0.122 -0.031 0.000` to three decimals.

**What the audit hits do and do not show.** The budget audit described
below fires 1,016,518 times in the 0.75 arm, and the next-period position
in every one is `-0.95587205886840820` -- rung 1, the limit itself, never
rung 7 or any rung between.

That call sits inside a nested sweep over the STATE SPACE (age x
amortization x employment x voucher x housing status x unemployment x
financial index, `SR_v1.f90:17717-17901`). It is **not mass-weighted**. So
the count is a count of *states at which the policy function chooses to
borrow*, not of households holding debt. It establishes that the solved
policy goes to the limit wherever the audit fires; it does NOT establish
how much population mass sits on debt.

"Nobody borrows" and "the policy would borrow but no mass reaches those
states" are different claims, and only the bottom-percentile wealth shares
separate them. Those need a moments block, which this arm did not produce.

### WITHDRAWN: the "corner solution" reading of the identical audit counts

An earlier version of this file read the identical audit counts across
arms 1 and 2 as a corner solution -- both impatience levels far above the
borrowing rate, so both types pinned at the limit -- and predicted that
arm 3 at 0.96 would show a sharply lower count. **That is withdrawn. The
cause is mundane and the prediction is void.**

`SR_v1.f90:36099-36104`:

    do current_beta_type=1,number_of_beta_types
        if (current_beta_type==1) discount_factor=discount_factor_patient_saved
        if (current_beta_type==2) discount_factor=discount_factor_impatient

Beta type 1 is the **patient** type, at `discount_factor=0.99980`, which is
identical in all three arms. `discount_factor_impatient` enters only at
beta type 2. **Neither arm 1 nor arm 2 ever reached beta type 2**: both
were killed inside the first type's pass.

The proof is that their flushed aggregates agree to every digit printed:

| | arm 1 (0.75) | arm 2 (0.90) |
|---|---|---|
| `sum_of_distribution` | 51.449733435841217 | 51.449733435841217 |
| `model_total_income` | 4.1868157019145498 | 4.1868157019145498 |
| `average_welfare_of_all_cohorts` | 49620.713469575305 | 49620.713469575305 |
| `sum(total_rental_demand(...))` | 3.9992818297899717 | 3.9992818297899717 |
| audit failures | 1,016,518 | 1,016,518 |

Two runs at different impatience cannot agree to sixteen digits unless the
differing parameter has not yet been used. It had not.

So the 1,016,518 count is a property of the **patient** pass, common to
every arm, and says nothing whatever about impatience. Arm 3 will show the
same count for the same reason, and that will confirm nothing about a
corner.

### The consequence, which is the real result of this batch

**The bottleneck is the patient type's borrowing-ON pass, and it is shared
by all three arms.** No setting of `discount_factor_impatient` can avoid
it, because it is reached before that parameter is ever read. Two runs
spent 4 h 06 min and 2 h 32 min without getting past it, against a 12 min
borrowing-OFF control.

`discount_factor_impatient` has therefore **never been exercised in a
borrowing-ON run**, and the question the batch was built to answer -- at
which impatience `w_bot` holds its target once debt is available -- cannot
be reached at all until the patient pass completes.

It is also worth noting on its own account that a household discounting at
0.99980 is choosing the borrowing limit at a million states. A nearly
perfectly patient type going to the corner is not obviously sensible
economics, and is one more reason to check the accounting defect below
before trusting any borrowing result.

## Arm 1: `discount_factor_impatient=0.75` -- NO MOMENTS

| | |
|---|---|
| point tag | `d42e5af187` |
| outcome | **no moments block**; `hftf` exit status 143 (SIGTERM) |
| wall time before termination | 4 h 06 min (246 min), 4 h 29 min CPU on 4 cores |
| for comparison, the control | 12 min |

I terminated it. It had run ~20x the 11-16 min the batch budgeted, at a
steady 110-170 per cent CPU with flat RSS, so it was computing rather than
hung -- but it was not close to finishing, and the batch has two further
arms to measure.

**How far it actually got.** The last line it reached is `begining wealth
distribution for old`. In the control that line appears **twice**, at log
lines 1004 and 1332 of 1718 -- once per beta type. Arm 1 reached the
*first*. So after four hours it was still inside the FIRST beta type's
aggregation, and the entire second beta type's backward induction had not
begun. It was not cut off near the finish.

This is worth stating precisely because it was invisible while the run was
live: `hftf` writes stdout to a pipe, gfortran block-buffers to a pipe, and
the visible log froze 3.5 hours before the kill at a point ~40 log lines
earlier. The buffer only flushed on termination. **A live borrowing run
cannot be monitored by tailing its log.**

### The economy it was heading for was degenerate

The flushed aggregates, against the control at the comparable stage:

| | control | arm 1 |
|---|---|---|
| `model_total_income` | 19.709 | **4.187** |
| `aggregate_consumption` | 24.833 | **55.826** |
| `model_total_income - model_total_expenditure` | -- | **-46.430** |
| `model_average_rent(time_period)` | 1.000 | **3.999** |
| `total_experimenters_1` | 9.891 | **1.131e-05** |
| `sum_of_distribution` | 51.411 | 51.450 |

Aggregate consumption exceeds total income by more than a factor of
thirteen, and experimenters fall by six orders of magnitude.

**This is measured, not diagnosed.** Two readings are open and this run
does not separate them: it may be the genuine economics of an impatient
type at 0.75 handed 1.5 years' income of credit and never made to repay
it, or it may be a consequence of the accounting defect below. Separating
them needs the source instrumented, which was out of scope here.

## A stale budget audit, live only when borrowing is ON

`housing_first_or_treatment_first_SR_v1.f90:24001` prints `budget does not
clear by` when its reconstruction of the household budget misses by more
than `5e-8`. In the 0.75 arm it fires **1,016,518 times**, writing 445 MB
of diagnostics -- against 195-450 KB for every one of the 48 archived
worker logs. It fires **zero** times in the borrowing-OFF control and in
every archived log.

The residual takes 19 distinct values in two clusters, `-0.95587...` and
`-0.89829...`. The first is *exactly* the value printed on the adjacent
`min(financial_grid(fin_index_frac_used),0.d0)` line.

The reconstruction at line 23988 admits a negative asset position only
through a mortgage term:

    min(financial_grid(...),0.d0) * max(amortization_used-1,0)
        * housing_price(time_period) * housing_size(housing_status_index_used)
    + max(financial_grid(...),0.d0)
    + (1+consumption_tax)*(consumption_used + frac_spent_on_addiction_used*total_consumption_used)

`amortization_used` is **1 in every one of the million failures**, so
`max(amortization_used-1,0)` is identically zero and the renter's debt
drops out entirely. What is left of next-period assets is `max(grid,0)`,
which is zero for a borrower. The residual is therefore the borrowed amount
itself, which is exactly what the printed values show.

The Bellman's own budget (line 21867) is

    consumption_1 = (after_tax_wealth_net_of_expenses_1 - future_financial_amount_1)
                    / (1+consumption_tax)

with `future_financial_amount_1` **signed**, so the solve itself accounts
for debt correctly. On that reading the audit is stale -- it predates
unsecured borrowing and still assumes any negative position is a mortgage
scaled by house value -- and the moments would be unaffected.

**That reading is inferred from reading the two code paths plus the exact
numeric match, and it is not verified.** It also sits awkwardly beside the
degenerate aggregates above. It should be checked before any borrowing
result is trusted. The model source was not edited.

Per `CLAUDE.md` section 7, this is a quantitative-model finding and wants
checking against the stylized model's transition, which was not done here.

## Arm 2: `discount_factor_impatient=0.90` -- NO MOMENTS

| | |
|---|---|
| point tag | `a2778b36aa` |
| outcome | **no moments block**; `hftf` exit status 143 (SIGTERM) |
| wall time before termination | 2 h 32 min (152 min), 2 h 55 min CPU on 4 cores |

I terminated it at a bound shortened from 4 h to 2 h 30 min, because it was
tracking arm 1 minute for minute -- identical log size, identical freeze
point, identical CPU profile -- and arm 1 had already demonstrated that
this trajectory does not finish. Its flushed tail then proved the two runs
were doing bit-identical work, which is the finding recorded above.

## Arm 3: `discount_factor_impatient=0.96` -- RUNNING, as a probe only

Started to confirm, rather than assume, that the patient-pass bottleneck is
common to all arms. The check is cheap: the audit spam is written early, so
if arm 3 reaches ~445 MB with 1,016,518 failures and the same aggregates,
the shared-bottleneck reading is confirmed by measurement instead of by
extrapolation. It is not expected to produce moments.

## Cost note

The batch budgeted 11-16 min a line. The borrowing-OFF control took 12 min.
Arm 1 ran 246 min and arm 2 ran 152 min, both killed without moments, both
still inside the patient pass.

Turning borrowing on is not a marginal change in cost. Until the patient
pass is made to complete, adding arms to this batch buys nothing: every arm
pays the same shared cost before it reaches the parameter that
distinguishes it.

## What would have to happen before this batch is worth re-running

Not attempted here, and listed as what the measurement showed it needs:

1. Establish why the patient type's borrowing-ON pass does not complete,
   when the same pass with borrowing off takes 12 minutes.
2. Resolve the budget audit at `SR_v1.f90:24001` -- either it is stale and
   should be taught about unsecured borrowing, or the solve is wrong. A
   million failures per run is not a state anything should be measured in,
   and the 445 MB of diagnostics is itself part of the cost.
3. Explain a household at `discount_factor=0.99980` choosing the borrowing
   limit, and aggregate consumption at thirteen times total income.

Only after those does varying `discount_factor_impatient` measure
anything.
