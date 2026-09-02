# The floor fix against the unsecured-borrowing-OFF control

## What was measured

One point: the anchor vector with `include_unsecured_borrowing=0`, the single
line of `code/batch_validate.txt`. With borrowing off both asset-choice floors
reduce to `negative_financial_grid_size` at every age, so the vector must give
back the numbers it gave on semantic hash `fdc6078859`, before the floor was
broken and repaired.

Point `f9c16d5308`, solved in 14 minutes on 4 cores, exit code 0, all sixteen
invariants PASS. Stamped `MODEL d2563e97f3`, which is semantic hash
`a734fffba5` -- the revision this validation was asked to speak for.

## The five quantities

| quantity                       | reference, `fdc6078859` | measured, `a734fffba5` | broken `99752a3cab` |
|--------------------------------|-------------------------|------------------------|---------------------|
| `w_bot`                        | 0.029487                | 0.0294859              | 3.269452            |
| homelessness rate              | 0.0842                  | 0.0841771              | 0.0114              |
| employed share of the homeless | 0.9642                  | 0.9641913              | --                  |
| homeless by choice             | 0.9807                  | 0.9806993              | 1.0000              |
| drug users                     | positive, not zero      | 0.3998972              | 0.0                 |

## Verdict

**REPRODUCED.**

Every quantity matches the `fdc6078859` reference to at least four significant
figures, and the drug-user mass is positive rather than the exact zero the
broken revision gave. Two places where the agreement stops, stated rather than
smoothed over:

- `w_bot` agrees to four significant figures (0.02949) and parts company in the
  fifth: the reference reads 0.029487, the measurement 0.029486, a relative
  difference of 3.8e-5. This clears the four-figure bar and no more.
- the homelessness rate reference is quoted to three significant figures only.
  The measurement, 0.084177, agrees with 0.0842 to every figure the reference
  carries. A fourth figure cannot be checked against a reference that does not
  state one.

The other three agree at four figures or better; `homeless by choice` agrees at
five.

None of the broken revision's signatures is present: `w_bot` is not two orders
of magnitude high, homelessness is not collapsed to about a hundredth, the
homeless are not all there by choice, and the drug margin is not shut off.

## Scope, and what this does not cover

This validates `a734fffba5`. The branch has since moved past it: head now
carries `0f581bb`, "the real bug: renter arrays had no negative indices, and
never did", which changes 123 lines of the Fortran and puts the source at
semantic hash `17529c7177`. That revision is not measured here, and nothing in
this file speaks to it. The OFF control is the weakest test available of a
change to the borrowing floors -- with borrowing off both floors collapse to
the same constant, so it shows the fix did not disturb the control, not that
the floors are right where they bind. The ON arm remains unmeasured.
