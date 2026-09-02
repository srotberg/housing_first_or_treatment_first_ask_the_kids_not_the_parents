# Round 1 arms b: `discount_factor` and `probability_becoming_unemployed`

`code/batch_r1b.txt`, two lines, each moving one round 1 instrument off the
anchor. Both were measured, and a third point was added because without it
neither line was a measurement. All three are on **MODEL b8dc1077ad**.

## What had to be re-run, and why

The batch was written against anchor `point_6aadbe9c3d` (MODEL 1b0babfbed).
Between that anchor and this session the source moved four times, and three of
those moves changed the economy:

| commit | what it changed |
| --- | --- |
| `358057d` | the EV fill range; both floors now key on the ARRIVING age |
| `0f581bb` | renter arrays had no negative indices, so the borrowing CHOICE was never live |
| `d9ff1a8` | three wealth walks keyed on an unset `age_index` |

This session checked out `c5f6589` and ran line 1 before the first two were on
the branch, so line 1 landed on `e55e1cc855`. That measurement is worthless,
and it is worth recording exactly how worthless, because the point file looked
like a result:

| point | `discount_factor` | beta | pi_eu |
| --- | --- | --- | --- |
| `point_4659380b40` on `e55e1cc855` (the base) | 0.99715 | 7.6997e12 | 0.5516735 |
| `point_8967680c10` on `e55e1cc855` (line 1) | 0.99800 | 7.7031e12 | 0.5516735 |

The base was measured independently by another session at the same vector. The
two agree to four figures on both owned moments, with the same two invariant
failures and 1.4949 of the distribution in both histograms. The bug, not the
parameter, was setting both numbers. Moved to `points_superseded/`.

Line 2 was then started on `c823331449` and killed after **2 hours 1 minute**
without finishing. That is the bug `d9ff1a8` describes: the wealth walk's
stopping rule cannot be reached and the walk consumes every cell. Points on the
next source solve in 10 to 17 minutes, so this was a hang, not a slow solve.

Both lines were re-run on `b8dc1077ad`, and so was the base, which had never
been solved on it.

## The three points

All at `include_unsecured_borrowing=1`, `unsecured_borrowing_limit=0.30`,
`discount_factor_impatient=0.55`, `number_of_beta_types=2`.

| point | `discount_factor` | `probability_becoming_unemployed` | beta | pi_eu |
| --- | --- | --- | --- | --- |
| `point_4659380b40` (base) | 0.99715 | 0.0437 | -0.8694720 | 0.2820969 |
| `point_8967680c10` (line 1) | **0.99800** | 0.0437 | -0.8694557 | 0.2820990 |
| `point_0ef155fbde` (line 2) | 0.99715 | **0.0498** | -0.8907403 | 0.2994565 |

Every one of the three fails the same single invariant: the wealth histogram
does not hold the whole of net worth, and the ratio prints as asterisks.
Aggregate net worth at this vector is negative and close to zero, so `w_bot`
comes back as -8.09e12 and the histogram ratio as -1.60e13. beta is a ratio
with that aggregate on top, which is why it is negative.

## Arm 1: `discount_factor`, which owns beta

    0.99715 -> 0.99800     beta  -0.8694720 -> -0.8694557     band 3.0 to 4.5

**Does not bracket the band.** Neither value is in it, and neither has the sign
the band requires.

This was a probe for the slope, and the slope it returns is **1.6e-5 of beta
for 8.5e-4 of `discount_factor`** — beta is inert in its own instrument here,
to five decimal places. pi_eu moves by 2.1e-6 across the same arm. **No value
of `discount_factor` is projected from this pair**, and not only because the
standing instruction forbids it on this quantity: a slope of essentially zero
projects nothing at all.

The inertness is itself the finding, and it is a property of the vector rather
than of beta. On the same economy with **borrowing off**, another session's
points move beta exactly as expected:

| point | `discount_factor` | beta | invariants |
| --- | --- | --- | --- |
| `point_f9c16d5308` | 0.99715 | 2.6846376 | all PASS |
| `point_906b19d36f` | 0.99900 | 2.8965440 | all PASS |

So beta is alive in `discount_factor` when borrowing is off, and dead in it
when borrowing is on at a limit of 0.30. The reading that fits: with the
borrowing choice live since `0f581bb`, enough households sit against the
borrowing limit that the wealth aggregate is set by the limit, which is a hard
constraint and carries no `discount_factor` in it.

## Arm 2: `probability_becoming_unemployed`, which owns pi_eu

    0.0437 -> 0.0498       pi_eu  0.2820969 -> 0.2994565      target 0.139

**Does not bracket the target.** Both values are roughly double it, and the arm
moves *away* from it.

The instrument is moving in the wrong direction, and the reason is on the
record rather than in the model. `batch_r1b` raised it because at the anchor
the batch was written against, `point_6aadbe9c3d`, pi_eu was 0.1220 — *below*
the 0.139 target — so raising it closed the gap. On this economy pi_eu is
0.2820 at the same instrument value, *above* target, so raising it opens the
gap. The sign of the required step flipped when the economy changed, and the
batch was not rewritten.

The slope is well behaved and positive, 2.85 of pi_eu per unit of instrument,
and the borrowing-off pair agrees closely at 3.10:

| point | `probability_becoming_unemployed` | pi_eu | borrowing |
| --- | --- | --- | --- |
| `point_a6ae2d65f0` | 0.0300 | 0.2182957 | off |
| `point_f9c16d5308` | 0.0437 | 0.2607963 | off |

Both borrowing settings put pi_eu near 0.22 to 0.30 across this range and
rising, so **0.139 is below everything measured on this economy in either
setting**, and reaching it needs the instrument to go down, not up. Nothing
here says how far: the lowest value measured, 0.0300, still gives 0.2183.

## What this leaves

- Neither arm brackets its target, and neither is a step toward it.
- The `pi_eu` arm's direction is wrong on this economy and should be re-issued
  downward from 0.0437 rather than upward.
- The `discount_factor` arm cannot be re-issued as it stands. beta is inert in
  it at `include_unsecured_borrowing=1`, so a `beta` step at this vector buys
  nothing; the instrument only works with borrowing off, which is where the
  rest of the search has already moved. Every other point on `b8dc1077ad`
  except these three carries `include_unsecured_borrowing=0`.
- The three points here are the only ones on `b8dc1077ad` with borrowing on,
  and all three fail the net worth invariant. That the aggregate goes negative
  at a 0.30 limit is a fact about the borrowing feature, not about either
  instrument, and it is what makes beta unusable at this vector.
