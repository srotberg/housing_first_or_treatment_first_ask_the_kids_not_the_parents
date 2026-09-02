# The h_2 rung ladder, unsecured borrowing OFF

Three points from `code/batch_h2_off.txt`, moving
`smallest_rental_relative_to_lowest_income` and nothing else.
`include_unsecured_borrowing=0` in all three vectors.

The rung is the cheapest rental unit. Raising it makes that unit bigger and so
dearer, and the whole ladder rises with it, because `h_3` and `h_4` are fixed
ratios of `h_2`.

## The economy these were measured on

All three points carry the SAME `MODEL` line:

    MODEL c823331449

so the three are comparable with each other. This was checked on the `MODEL`
line of each file, not inferred from the run order.

They are NOT the repository head. The Fortran moved to `b8dc1077ad` in the
commits this branch picked up during the rebase that followed the third run, so
every number here describes the `c823331449` economy, and nothing measured on
the current source should be compared against it without re-measuring.

| rung  | point file             | solve   |
|-------|------------------------|---------|
| 0.060 | `point_952219eba8.txt` | 14 min  |
| 0.100 | `point_3352112c72.txt` | 16 min  |
| 0.130 | `point_d63e6fb381.txt` | 15 min  |

All three solved cleanly: `HANDOVER OK: 42 of 42 parameters applied` and
`INVARIANTS: all PASS` on every one.

## The 0.039 anchor is NOT in this table

No point at the anchor exists on `c823331449` with the batch's base vector, so
under the rule for this ladder the anchor is left out and the comparison base
is 0.060.

This is worth stating precisely, because `code/points/` does contain 0.039
points on `c823331449` and they are easy to mistake for the anchor. There are
five, and each one differs from this batch's base vector in exactly one
coordinate, so each is an arm of the round-1 search rather than the anchor:

| file                   | the one coordinate that differs                    |
|------------------------|----------------------------------------------------|
| `point_03fd927a5c.txt` | `probability_becoming_unemployed` 0.0437 -> 0.0498  |
| `point_60036d292a.txt` | `discount_factor` 0.99715 -> 0.99800                |
| `point_690ae9b00a.txt` | `probability_of_voucher_benchmark_used` -> 0.038800 |
| `point_81f7071729.txt` | `value_of_life` 38.4 -> 54.5                        |
| `point_ca25f19a3f.txt` | `max_food_cost` 0.0136 -> 0.0196                    |

The anchor vector itself was measured, as `RUN1_f9c16d5308.txt`, but on
`b8dc1077ad` -- the head source, not this one -- so it is not comparable with
these three either.

Note for whoever maintains `ROUND1_ARMS_A_OFF.md`: that file states its anchor
is `point_f9c16d5308.txt` on `c823331449`. No such file is in the tree at this
commit; it was superseded three times and the surviving copy is the
`b8dc1077ad` replicate named above. This note does not touch that file.

## The ladder

| rung  | employed share of the homeless | homeless by choice | could afford it on INCOME ALONE | h_1      | gamma    |
|-------|--------------------------------|--------------------|---------------------------------|----------|----------|
| 0.060 | 0.961461                       | 0.960529           | 0.957032                        | 0.121556 | 0.181004 |
| 0.100 | 0.957192                       | 0.894284           | 0.878283                        | 0.150169 | 0.251392 |
| 0.130 | 0.954226                       | 0.836263           | 0.813543                        | 0.158686 | 0.295169 |
| target| 0.46                           | --                 | --                              | 0.00399  | 0.268    |

## The question: does the rung pull the employed share down to 0.46?

**No, and not by a margin that any amount of reading between these arms would
close.** The rung more than doubles across the measured span, 0.060 to 0.130,
and the employed share of the homeless falls by 0.007234, from 0.961461 to
0.954226. The distance still left to the target at the highest rung measured is
0.494226 -- sixty-eight times the total movement the ladder bought.

The local slope is flat and getting flatter, not steepening:

| interval      | d(employed share) / d(rung) |
|---------------|-----------------------------|
| 0.060 -> 0.100 | -0.1067                    |
| 0.100 -> 0.130 | -0.0989                    |

**No measured pair brackets 0.46.** All three measured values lie above it, and
the target lies OUTSIDE the measured range. No rung that would reach 0.46 is
named here, because that would mean running the slope out past the arms
measured, and the arms give no warrant for it.

## What it costs

**`h_1` moves the wrong way, and this is the expensive part.** The homelessness
rate rises monotonically with the rung, 0.121556 -> 0.150169 -> 0.158686
against a target of 0.00399. It is already about thirty times its target at the
lowest rung and about forty times at the highest. Raising the rung prices
households out of the cheapest unit, and they become homeless; that is the same
mechanism that lowers the affordability share, seen from the other side.

**`gamma` is the one thing the rung buys.** Housing over expenditure rises
0.181004 -> 0.251392 -> 0.295169 and crosses its target of 0.268. **The pair
(0.100, 0.130) brackets `gamma`.** Interpolating between those two measured
arms puts the crossing at a rung of about 0.111. That is interpolation inside a
bracketing pair, not extrapolation beyond one, but it is still worth measuring
rather than trusting if the crossing matters.

So the ladder trades `gamma` against `h_1` and leaves the employed share alone.

## Why the employed share does not follow the affordability share

The two margins decouple, and the reason shows in the income of the homeless.

| rung  | income of the homeless (observed 0.191) | SUD share of the homeless (observed 0.217) |
|-------|-----------------------------------------|--------------------------------------------|
| 0.060 | 0.526460                                | 0.262785                                   |
| 0.100 | 0.723710                                | 0.273937                                   |
| 0.130 | 0.881008                                | 0.305129                                   |

Raising the rung does move the affordability margin hard: the share of the
homeless who could pay the cheapest rent out of income alone drops from 0.957
to 0.814, and homelessness by choice from 0.961 to 0.836. But that is the
cheapest rent rising, not the homeless getting poorer. Their income rises by
two thirds across the span, away from an observed 0.191 that is already far
below the lowest value measured.

The households the higher rung pushes into homelessness are, at the margin,
higher-income and employed. So the composition of the homeless does not shift
toward the unemployed, and the employed share stays pinned near 0.95 while the
affordability share falls away underneath it. A rung that makes the homeless
richer is not an instrument that can hit an employed share of 0.46.

## Collateral, for whoever is fitting the other moments

Three moments not asked for here are bracketed by these same arms, and one
moves away.

| moment | 0.060    | 0.100    | 0.130    | target   | verdict                    |
|--------|----------|----------|----------|----------|----------------------------|
| h_3    | 0.547599 | 0.676099 | 0.767348 | 0.626723 | bracketed by (0.060, 0.100)|
| beta   | 2.678420 | 2.924893 | 3.129493 | 3.000000 | bracketed by (0.100, 0.130)|
| w_bot  | 0.029440 | 0.026756 | 0.018598 | 0.025000 | bracketed by (0.100, 0.130)|
| h_2    | 0.127790 | 0.178454 | 0.221860 | 0.101000 | moves away, already over   |

`pi_eu` is flat across the ladder at 0.262 to 0.266 against a target of 0.139,
and `lambda_m` is flat at 0.0259 to 0.0263 against 0.250. Neither is a rung
instrument.
