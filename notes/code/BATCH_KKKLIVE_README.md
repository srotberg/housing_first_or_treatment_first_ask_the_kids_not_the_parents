# batch_kkklive.txt — stochastic productivity, live, with the other levers

On the author's instruction of 3 September: *"I want to use the stochastic
productivity please.. Can you make sure it runs correctly and run the
calibration of model with it?"* and *"I also want the other levers we
discussed"*.

All five lines are the current best point `6d1662b473` with `fixed_productivity`
flipped to 0 and one thing changed each. So every difference from the best point
is attributable, and line 1 against `6d1662b473` itself is the clean
frozen-versus-stochastic comparison the author asked for and has never had.

| line | sigma_scale | ssi_floor_takeup | bottom_productivity_level | rho_shock | what it asks |
|---|---|---|---|---|---|
| 1 | 1.0 | 0 | 0 | 0.90 | KKK at the author's published numbers |
| 2 | 2.20949 | 0 | 0 | 0.90 | the same, scaled so the dispersion hits sigma_y |
| 3 | 2.20949 | **0.5** | 0 | 0.90 | + the SSI floor, which owns elderly homelessness |
| 4 | 2.20949 | 0 | **0.004** | 0.90 | + the bottom-node level, which owns emp_homeless |
| 5 | 2.20949 | 0 | 0 | **0.952** | + the data fan, a bigger rise in within-cohort variance |

## What each is for

**Line 1 is expected to fail on inequality and that is the point.** At the
published sds the bottom half holds 33 per cent of earnings against 17.2 in the
SCF, and the poorest household earns 0.232 of mean productivity — rich enough to
pay the cheapest rent out of income. If homelessness collapses here, that is the
measurement behind the closed-form argument in `KKK_VS_SIGMA_Y.md`, and it is
worth having.

**Line 2 is the real candidate.** Scaling both innovation sds by 2.20949 leaves
the ratio between them — and therefore the fanning out — untouched, and puts the
pooled dispersion on 1.00.

**Lines 3 and 4 are the levers the author asked for.** `ssi_floor_takeup` has
never been solved at anything but zero, and `bottom_productivity_level` has never
been solved at anything but zero in ANY point in the archive.

**Line 5 asks whether the fan matters.** Lines 2 and 5 hit the same cross
sectional dispersion and differ only in how it is spread over the life cycle:
the within-cohort variance rises by 0.211 in line 2 and 0.555 in line 5. Line
5's `sd_employment_surviving` is scaled so the pooled dispersion still lands on
1.00 at the higher persistence.

## The lever that had to be built for this batch

`bottom_productivity_level` lived inside `if (fixed_productivity==1)` and did
NOTHING under KKK. Line 4 would have been a duplicate of line 2. It now applies
the same mean-preserving override under KKK, **at every age rather than only at
age one**, because the KKK grid fans out: the masses are age-invariant in
standardised units but the levels are not, so each age gets its own rescale
factor from its own bottom node. The fan survives; only the bottom node and the
scale of the block above it move.

## What is NOT yet decided

Whether the calibration switches to this economy. That needs one clean
measurement first. `fixed_productivity=1` remains the committed default until
line 2 comes back with 16 of 16 invariants and finite moments, because flipping
it points the whole engine at an economy no measurement has ever validated.
