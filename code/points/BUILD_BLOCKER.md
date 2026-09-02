# The borrowing branch does not compile: `unsecured_borrowing_rate` under `default(none)`

Status: CLOSED at a3f7ba4. `unsecured_borrowing_rate` was added to the
`shared(...)` list of the region opening at 24528, exactly as the Fix section
below prescribes, and gfortran now reports zero errors. Nothing else was behind
it -- the compiler had stopped after the one error, so this was the only way to
know.

The semantic hash did not move (9caeb7a139 before and after): an OpenMP
directive is a comment line and `model_hash.py` strips comments, so the archive
tag is unaffected and points measured before and after this fix are comparable.
The 13 `point_<tag>.FAILED.txt` records were deleted at 415bc6e -- each was
written by a run that died in the build, not by one that failed to converge, and
leaving them would have let a later reader confuse the two.

What it cost: no point on this branch measured between the borrowing commit and
a3f7ba4. Four workers' output in that window was FAILED records only.

Re-confirmed on the current head (`code/batch_s2_01.txt` run line by line
again, tags 30f09ca36e, deef8f1e37, 65c5d119a5): identical error, identical
line and column, and the three `FAILED` records rewrote byte-identically over
the committed ones.

## The error

    housing_first_or_treatment_first_SR_v1.f90:24623:190:
    Error: 'unsecured_borrowing_rate' not specified in enclosing 'parallel'
    housing_first_or_treatment_first_SR_v1.f90:24565:67:
    note: enclosing 'parallel'

Line numbers in an earlier revision of this note were 31 low throughout
(24592/24534/24497/25858/25274, warnings at 40111/40138). They were taken
before "a debt is part of the estate" (171d293) added 31 lines above the site
and were never refreshed. Everything below is checked against the source as it
stands.

## Cause

`unsecured_borrowing_rate` is a module variable (declared line 3760,
`real(8) :: unsecured_borrowing_rate=0.055d0`), not a `parameter` and not
`threadprivate`. The new borrowing interest term

    risk_free_rate(time_period)*max(financial_grid(financial_index),0.d0)
      + unsecured_borrowing_rate*min(financial_grid(financial_index),0.d0)

was added inside the distribution-iteration loop at line 24623. Its enclosing
region opens at line 24528 with `!$omp parallel do default(none)`, its
`shared(...)` list spanning 24529-24542. Under `default(none)` every referenced
variable needs an explicit data-sharing attribute; that list names
`risk_free_rate` and `financial_grid` but not `unsecured_borrowing_rate`, so
the compile fails. The convention in this file is already to list module
variables explicitly -- `median_income`, `financial_grid`, `risk_free_rate` and
`median_income_calibrated` are all in that same clause -- so this is one
omission, not a change of style.

## Only one site needs the clause

The variable is referenced 14 times. Exactly one of them, 24623, is inside a
`default(none)` region.

The earlier revision of this note claimed a second one at (its numbering)
25858, "inside the region opening at 25274, whose `shared(...)` list is also
missing it", and its fix instruction said to edit both. That is wrong. In
current numbering the two lines are 25889 and 25305, and the region opened at
25305 is closed by `!$omp end parallel do` at 25338 -- 551 lines above the use.
There is no OpenMP directive of any kind between 25338 and 25889, so at 25889
the nesting depth is zero and the reference is outside every parallel region.
Pairing the directives over the whole span confirms it:

    24528  parallel do default(none)   <- encloses 24623, THE ERROR
    ...
    24833  end parallel
    25006  parallel do default(none)
    25228  end parallel do
    25255  parallel / 25259 end parallel
    25305  parallel do default(none)
    25338  end parallel do
    (no directive between here and 25889)
    25889  unsecured_borrowing_rate     <- depth 0, compiles fine

The remaining 12 uses (9049, 9428, 12548, 12986, 13340, 13486, 14283, 15956,
16986, 23342, 23382, 23454) are likewise outside `default(none)` regions and
compile fine. This is a data-sharing-clause omission only -- no model
arithmetic is implicated.

## What it is not

- Not parameter-dependent, and could not be: the parameters are runtime
  command-line arguments parsed by `PARAM_HANDOVER`, so they cannot reach a
  compile. All three lines of `code/batch_s2_01.txt` fail at the identical line
  and column despite differing in `unsecured_borrowing_limit` (1.00 vs 0.30),
  `unsecured_borrowing_rate` (0.055 vs 0.20) and `discount_factor_impatient`
  (0.55 vs 0.50).
- Not a flake, and not the container. gfortran 13.3.0 installs cleanly; the
  failure reproduces byte-identically across sessions.
- Not the two `Array reference ... out of bounds` warnings at 40142/40169.
  Those are warnings on `do i=0,transition_length` writes and are pre-existing.

## Fix

Add `unsecured_borrowing_rate` to the `shared(...)` list of the region opening
at 24528 -- the clause block ends at 24542, so it goes there. That is the whole
change; the region at 25305 does not need it.

gfortran emitted exactly one error and then stopped, so a rebuild is still the
only way to know nothing sits behind it. But every use of this variable has now
been placed against the region structure, and none of the other 13 is inside a
`default(none)` region, so there is no second omission of THIS variable to
find.

Left undone here deliberately: the batch instructions for these runs forbid
editing the Fortran, so this is the author's call.

Until that lands, every point line on this branch will produce a
`point_<tag>.FAILED.txt` and no measurement.
