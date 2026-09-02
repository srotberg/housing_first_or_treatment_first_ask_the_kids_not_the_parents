# BORROW15: unsecured borrowing at a limit of 1.50 years' average income

Three arms of `code/batch_borrow15.txt`: borrowing ON, limit 1.50, with
`discount_factor_impatient` at 0.75, 0.90 and 0.96. Solved on source md5
`64d52d8b6a`, semantic `197407b07d`, `pi_eu` target 13.9 per cent.

**Status: INCOMPLETE. Arm 1 (0.75) did not terminate and was killed at
4h06m. Arms 2 and 3 pending.** Nothing below extrapolates past what was
measured.

## The headline questions, so far as they can be answered

### Is borrowing inert? No -- households reach the limit.

This is answerable without a completed arm, and the answer is that the
feature is **live, not inert**. The bounds were not merely fixed; the
behaviour changed.

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

Households then *use* it. The budget audit described below fires 1,016,518
times in the 0.75 arm, and in every one of those the position being taken
is `-0.95587205886840820` -- rung 1, the limit itself. Nobody is sitting at
rung 7. Whether the resulting bottom-percentile wealth shares go negative
cannot be stated, because the arm produced no moments block.

### At which impatience does `w_bot` hold its target once debt is available?

**Not answerable yet.** Arm 1 produced no moments. Arms 2 and 3 pending.

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

## Arm 2: `discount_factor_impatient=0.90` -- PENDING

## Arm 3: `discount_factor_impatient=0.96` -- NOT STARTED

## Cost note

The batch budgeted 11-16 min a line. The borrowing-OFF control took 12.
Arm 1 was killed at 246 min without finishing. If the remaining arms behave
like arm 1, this batch is a multi-hour job per line rather than a
quarter-hour one, and that should be planned for rather than discovered.
