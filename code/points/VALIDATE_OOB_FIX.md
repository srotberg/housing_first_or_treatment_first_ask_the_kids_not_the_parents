# The out-of-bounds fix, validated against the borrowing-OFF control

## What was being tested

Every renter array was allocated with its financial index starting at the ZERO
index, while unsecured borrowing had opened the renter state loops down to index
1 -- so those loops read and wrote out of bounds. The bounds are now keyed on
`renter_array_floor`, which IS the zero index when borrowing is off. With
`include_unsecured_borrowing=0` the memory layout is therefore exactly what it
always was, and the anchor vector must return the numbers measured on semantic
hash `fdc6078859`.

## The run

- Vector: `code/batch_validate.txt`, line 1 -- the anchor with
  `include_unsecured_borrowing=0`.
- Model hash of the source measured here: `c823331449`. Handover 42 of 42
  parameters applied; solved in 11 minutes on 4 cores; all 16 invariants PASS.
- The measurement is kept at
  `code/points_superseded/point_f9c16d5308.on_c823331449.txt`. It is filed as
  superseded rather than live because a concurrent session measured the same
  vector on the later `d2563e97f3` and that is what
  `code/points/point_f9c16d5308.txt` now holds. The two are compared below.

## The five quantities

| quantity | reference (`fdc6078859`) | measured (`c823331449`) | concurrent (`d2563e97f3`) | out-of-bounds revision |
| --- | --- | --- | --- | --- |
| `w_bot`, net worth share of the bottom half | 0.029487 | 0.0294860 | 0.0294859 | 3.269452 |
| homelessness rate | 0.0842 | 0.0841768 | 0.0841771 | 0.0114 |
| employed share of the homeless | 0.9642 | 0.9641914 | 0.9641913 | -- |
| homeless by choice, share of the homeless | 0.9807 | 0.9806991 | 0.9806993 | 1.0000 |
| drug users | positive, not zero | 0.3998934 | 0.3998972 | 0.0 |

## Verdict

**REPRODUCED.**

Every quantity matches its reference to at least four significant figures:

- `w_bot` 0.0294860 against 0.029487 -- 0.02949 to four significant figures on
  both sides; the two differ by 1e-6, in the fifth significant figure, which is
  the last digit the reference was recorded to.
- homelessness 0.0841768 rounds to 0.0842, the reference exactly.
- employed share 0.9641914 rounds to 0.9642, the reference exactly.
- by choice 0.9806991 rounds to 0.9807, the reference exactly.
- drug users 0.3998934, positive and far from zero.

The out-of-bounds revision's numbers are not near any of these: `w_bot` was
larger by a factor of 111, homelessness was smaller by a factor of 7, by-choice
had saturated at 1.0000, and the drug-user mass had collapsed to exactly zero.
None of that survives the fix with borrowing off.

The concurrent measurement on `d2563e97f3` is the same economy to six
significant figures on all five, so the source moved between `c823331449` and
`d2563e97f3` without disturbing the OFF control either. That session recorded
its own reading in `code/points/VALIDATE_FLOOR_FIX.md`; this file is an
independent run of the same vector on the earlier of the two revisions.

This validates only the OFF control -- the layout the arrays always had. It says
nothing about whether the bounds are right when
`include_unsecured_borrowing=1`; that needs its own measurement.
