# The h_2 ladder: raising the cheapest rental does not move the employed share

`smallest_rental_relative_to_lowest_income` (h_2) is the bottom rung of the
rental ladder, and h_3 and h_4 are fixed multiples of it
(`rung_ratio_h3=1.5`, `rung_ratio_h4=2.0`), so raising it lifts the whole
ladder: every unit gets bigger and therefore dearer. The question was whether
that pushes the **employed share of the homeless** down toward its target of
0.46, and what it costs in the homelessness rate `h_1` and in `gamma`.

Everything below is on ONE economy, semantic model hash **`6d75e61a1d`**
(full stamp `9d410dfdb9`), and all four points pass every invariant.
Every other parameter is identical across the four rows.

| h_2 | employed share of the homeless | homeless by choice | could afford it on INCOME ALONE | h_1 | gamma |
|---|---|---|---|---|---|
| **target** | **0.46** | -- | -- | **0.00399** | **0.268** |
| 0.039 (anchor) | 0.98310 | 0.98826 | 0.98552 | 0.015398 | 0.12969 |
| 0.060 | 0.98276 | 0.93952 | 0.97884 | 0.034159 | 0.17711 |
| 0.100 | 0.98289 | 0.90324 | 0.94988 | 0.054069 | 0.25469 |
| 0.130 | 0.98023 | 0.84290 | 0.93619 | 0.056715 | 0.30391 |

Point files: `point_b2f80f5abb.txt` (0.039, measured by another worker on this
same economy and an exact match to this vector in every parameter),
`point_0003e01edf.txt` (0.060), `point_d45c55446e.txt` (0.100),
`point_b50caf4734.txt` (0.130).

## The answer: no. The employed share is flat, and 0.46 is not in reach

Across a rung that more than TRIPLES, from 0.039 to 0.130, the employed share
of the homeless moves from 0.98310 to 0.98023 -- a total of 0.0029, and not
even monotonically: it falls to 0.98276 at 0.060, rises to 0.98289 at 0.100,
then falls to 0.98023. The movement is smaller than the non-monotonicity, which
is to say this instrument does not move this moment at all.

**No measured pair brackets 0.46.** Every one of the four rows sits between
0.980 and 0.984, and the target is 0.46. It is not that the bracket lies
outside the three rungs I was given -- it lies outside the measured range
entirely, and a slope estimated from these points has no business being
extrapolated to it. Reaching 0.46 by this rung alone would require the moment
to fall by more than half while three rungs' worth of variation moved it by
0.3 per cent. h_2 is not the instrument for the employed share of the homeless.

## What it does cost

`h_1` and `gamma` both rise monotonically and steeply, so the rung is
expensive in exactly the two places the ladder was supposed to be cheap:

- **`h_1` moves the wrong way and hard.** It nearly quadruples, 0.015398 to
  0.056715, against a target of 0.00399. The anchor already overshoots by 3.9x;
  at h_2=0.130 the overshoot is 14.2x. Every step up the rung makes the
  homelessness rate worse, and the marginal cost is front-loaded: 0.039->0.060
  buys +0.0188 and 0.100->0.130 only +0.0026.
- **`gamma` rises through its target.** 0.12969 -> 0.17711 -> 0.25469 ->
  0.30391 against a target of 0.268. **The pair (0.100, 0.130) brackets
  gamma's target**: 0.25469 is below 0.268 and 0.30391 is above it. That is the
  one useful bracket in this ladder, and it is for gamma, not for the employed
  share.

So the rung is a real instrument for `gamma` and a real cost in `h_1`, and it
is inert on the moment it was raised to fix.

## Why the employed share will not move: the homeless here are not priced out

The two diagnostics explain the flatness. At the anchor, 98.8 per cent of the
homeless are homeless BY CHOICE and 98.6 per cent could afford housing on
income alone. Raising the rung does bite on both -- by choice falls to 0.84290,
could-afford falls to 0.93619 -- but even at the top rung roughly six in seven
of the homeless are still there by choice and more than nine in ten could still
pay for a unit out of income alone.

That is the mechanism. Homelessness in this economy is not a budget constraint
binding on the employed, so making units dearer adds households who are still
overwhelmingly employed and still overwhelmingly able to pay. The composition
of the homeless barely changes because the margin being moved has the same
employment status as the inframarginal mass. An instrument that lowers the
employed share has to make the homeless POORER or LESS EMPLOYED, and this one
does neither -- it only makes housing dearer for people who were not choosing
it on price.

## A note on how this was measured

The Fortran moved four times while this ladder was being run -- `358057d`,
`0f581bb`, `d9ff1a8` and `9023afc`, all of them fixes to the unsecured
borrowing path this batch turns ON -- and each move superseded whatever was in
flight. Three earlier solves of the 0.060 rung were discarded for that reason
and are in `points_superseded/`; the numbers they carried are not comparable
to anything here and should not be read (the first two were measured on a
source where, per `0f581bb`, the renter arrays had no negative indices at all).

The three rungs here were therefore run back-to-back WITHOUT pulling between
them, which is a deliberate deviation from the usual commit-and-push-after-each
-line rhythm: a pull swaps the working-tree source, and a ladder whose rungs sit
on different economies answers no question at all. The pushes were deferred to
the end instead. The 0.039 anchor needed no run: another worker had already
measured that exact vector on this exact economy.
