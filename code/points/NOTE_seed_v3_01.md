# Batch `code/batch_s2_01.txt` (seed v3, lines 1-3)

All three lines built and solved -- the `shared()` fix cleared the build failure
that had been killing them. Two of the three are clean; the third is degenerate
and should not be read as a measurement of the model.

| line | point | `discount_factor_impatient` | `unsecured_borrowing_limit` | `unsecured_borrowing_rate` | invariants |
|---|---|---|---|---|---|
| 1 | `point_30f09ca36e` | 0.55 | 1.00 | 0.055 | all PASS |
| 2 | `point_deef8f1e37` | 0.55 | 0.30 | 0.20  | all PASS |
| 3 | `point_65c5d119a5` | 0.50 | 0.30 | 0.055 | **2 FAILED** |

## Line 3 diverged

Both failures are the same quantity, the mass the histogram holds:

    INVARIANT FAIL  income histogram holds the whole distribution = 1.4949252181  want 1.0000
    INVARIANT FAIL  wealth histogram holds the whole distribution = 1.4949252181  want 1.0000

The histograms hold about 1.49 times the population, so the distribution the
moments are computed from is not the distribution the model solved. The moments
agree that the solution is not usable:

| moment | line 1 | line 2 | line 3 | target |
|---|---|---|---|---|
| `tau_l`   average labour income tax   | 0.2343 | 0.2343 | **NaN** | 0.2240 |
| `omega_l` labour supply / total hours | 0.3785 | 0.3785 | **0.0367** | 0.4000 |
| `beta`    wealth over output          | 2.6747 | 2.6748 | **7.71e12** | 3.0000 |

Wealth over output is twelve orders of magnitude off and the tax rate is NaN.
The untargeted side is degenerate in the same way: the working-age share of drug
users is 1.4e-10, essentially all users are 65-plus (share 0.99999999996, mean
age 84.2 against 45.5 observed), the SMI population share prints 0.905 and
unemployment 0.552. The invariant block still marks those rows PASS because
they are range checks, not fits -- only the two histogram rows test the
accounting, and they are the two that failed.

Note that the invariant totals are self-consistent at 1.4949 in both rows, so
this looks like one population that is scaled wrong rather than two independent
accounting errors.

## What separates line 3

Line 3 differs from line 2 in two coordinates (`discount_factor_impatient`
0.55 -> 0.50 and `unsecured_borrowing_rate` 0.20 -> 0.055) and from line 1 in
two others (`discount_factor_impatient` 0.55 -> 0.50 and
`unsecured_borrowing_limit` 1.00 -> 0.30). The one change common to both
comparisons is `discount_factor_impatient` = 0.50, and it is the only
coordinate on which line 3 differs from both clean points. That makes it the
first suspect, but this batch does not isolate it: no line here holds
`discount_factor_impatient` at 0.50 while varying the borrowing block, so
the divergence could also need the tighter limit or the low rate alongside it.
A point at `discount_factor_impatient=0.50` with `unsecured_borrowing_limit=1.00`
would settle it.

Lines 1 and 2 are worth one further remark: they differ only in the borrowing
block (limit 1.00 at rate 0.055 against limit 0.30 at rate 0.20) and their
moments agree to four decimals. Over that range the borrowing margin is doing
almost nothing to the benchmark.

`code/housing_first_or_treatment_first_SR_v1.f90` was not edited.
