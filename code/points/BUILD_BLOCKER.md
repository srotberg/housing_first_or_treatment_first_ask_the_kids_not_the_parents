# The borrowing branch does not compile: `unsecured_borrowing_rate` under `default(none)`

Status: OPEN. No point on this branch has been measured since unsecured
borrowing was added. Every `run_one_point.sh` invocation dies in the build,
before the solver starts.

## The error

    housing_first_or_treatment_first_SR_v1.f90:24592:190:
    Error: 'unsecured_borrowing_rate' not specified in enclosing 'parallel'
    housing_first_or_treatment_first_SR_v1.f90:24534:67:
    note: enclosing 'parallel'

## Cause

`unsecured_borrowing_rate` is a module variable (declared line 3760,
`real(8) :: unsecured_borrowing_rate=0.055d0`), not a `parameter` and not
`threadprivate`. The new borrowing interest term

    risk_free_rate(time_period)*max(financial_grid(financial_index),0.d0)
      + unsecured_borrowing_rate*min(financial_grid(financial_index),0.d0)

was added inside the distribution-iteration loop at line 24592. Its enclosing
region opens at line 24497 with `!$omp parallel do default(none)`. Under
`default(none)` every referenced variable needs an explicit data-sharing
attribute; the `shared(...)` list there names `risk_free_rate` and
`financial_grid` but not `unsecured_borrowing_rate`, so the compile fails.

The same term appears at line 25858, inside the region opening at 25274, whose
`shared(...)` list is also missing it. gfortran stops at the first error, so
25858 has not been reached yet and further omissions may surface behind it.

The other ~13 uses of the variable (9049, 9397, 12517, 12955, 13309, 13455,
14252, 15925, 16955, 23311, 23351, 23423) are outside `default(none)` regions
and compile fine. This is a data-sharing-clause omission only -- no model
arithmetic is implicated.

## What it is not

- Not parameter-dependent. Batch `code/batch_s2_01.txt` was run line by line;
  all three lines fail at the identical line and column despite differing in
  `unsecured_borrowing_limit` (1.00 vs 0.30), `unsecured_borrowing_rate`
  (0.055 vs 0.20) and `discount_factor_impatient` (0.55 vs 0.50).
  Tags: 30f09ca36e, deef8f1e37, 65c5d119a5.
- Not a flake, and not the container. gfortran 13.3.0 installs cleanly; the
  failure reproduces byte-identically across sessions -- the FAILED records
  those three runs wrote matched the already-committed ones exactly, leaving
  the tree clean.
- Not the two `Array reference ... out of bounds` warnings at 40111/40138.
  Those are warnings on `do i=0,transition_length` writes and are pre-existing.

## Fix

Add `unsecured_borrowing_rate` to the `shared(...)` list of the region at
24497, and to the one at 25274, then rebuild and see whether anything else
behind the first error surfaces. Left undone here deliberately: the batch
instructions for this run forbid editing the Fortran, so this is the author's
call.

Until that lands, every point line on this branch will produce a
`point_<tag>.FAILED.txt` and no measurement.
