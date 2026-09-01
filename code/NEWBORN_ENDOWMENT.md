# The endowment of the youngest

Everything here is measured, from `code/worker_2af18641a4.log` and from
`financial_gridbaseline_benchmark.txt`, not inferred.

## The scale of the economy

| quantity | value |
|---|---|
| average labour income | 0.6372 |
| labour income at age 26 | 0.2892 |
| annual rent on the cheapest rental unit (h_2 = 0.12, rent = 1.0) | 0.120 |

## What every newborn currently holds

The last measured run used RS-2024's SCF distribution, so the endowment varied
with the productivity fixed effect and only a fraction of each bin got anything
at all:

| productivity bin | relative endowment | share with positive wealth | amount held |
|---|---|---|---|
| 1-5 | 0.132 - 0.261 | 0.478 - 0.595 | 0.2376 |
| 6 | 0.852 | 0.665 | 0.6721 |
| 7-9 | 1.385 | 0.769 | 0.9392 |

Mean over all newborns, `value_of_initial_assets` = **0.0960**. That is 15.1
per cent of average labour income, 33.2 per cent of what a 26 year old earns,
and **0.80 of a year's rent on the cheapest unit in the model**.

## THE ENDOWMENT IS SNAPPED TO A COARSE GRID, AND IT IS ROUNDED UP

`initial_endowment` is `minloc(financial_grid - target, mask = ... > 0)`, the
smallest asset grid point STRICTLY ABOVE the desired amount. The asset grid is
built with curvature 1.5 from zero, so near the bottom the rungs are far apart:

| grid index | assets | years of rent |
|---|---|---|
| 61 | 0.0000 | 0.00 |
| 62 | 0.0840 | 0.70 |
| 63 | 0.2376 | 1.98 |
| 64 | 0.4365 | 3.64 |
| 65 | 0.6721 | 5.60 |
| 66 | 0.9392 | 7.83 |
| 68 | 1.5558 | 12.97 |

Three consequences, all of them real:

1. **`newborn_endowment_scale` is a step function, not a dial.** Between zero
   and one year's average income there are exactly four reachable endowments.
   It can be bracketed but it cannot be bisected, and a secant on it will
   report a zero derivative over most of its range.
2. **Scale 0 does not give zero wealth.** The mask is strict, so a target of
   zero returns index 62 and every newborn starts with 0.0840 -- 0.70 of a
   year's rent. The no-endowment economy is not reachable from the vector; it
   needs `start_assets_of_newborns_at_zero=0`, a compile-time flag.
3. **Rounding is always upward and sometimes large.** A scale of 2.0 asks for
   1.2745 and delivers 1.5558, 22 per cent more.

The fix, once the bracket is in, is a lottery over the two adjacent grid points
rather than a snap to one -- `compute_asset_lottery` already exists in the model
and is used for the same purpose elsewhere. That makes the endowment continuous
in the scale and therefore calibrable. It is deliberately NOT done before the
bracket, because it changes the source and every point in the sweep has to share
one model hash to be comparable.

## What the six running points actually deliver

| batch line | scale requested | endowment delivered | years of rent |
|---|---|---|---|
| 1 | 0.0 | 0.0840 | 0.70 |
| 2 | 0.5 | 0.4365 | 3.64 |
| 3 | 1.0 | 0.6721 | 5.60 |
| 4 | 2.0 | 1.5558 | 12.97 |

Lines 5 and 6 hold the endowment at scale 1.0 and bracket `pi_eu` at 0.05 and
0.09, because the anchor's 0.01546 was calibrated to the retired 4.85 per cent
unemployment target and the new one is 13.9.

The delivered column is a prediction from the grid and the previous run's
average labour income; income is itself an equilibrium object, so it will move a
little. `value_of_initial_assets` in each run's log is the realised number and
is what should be quoted.

## Why the endowment is the instrument for the age profile

Recovered from the age-by-age diagnostic:

| age | homeless | mean renter wealth | mean renter income | SUD |
|---|---|---|---|---|
| 26 | 13.35% | 0.0960 | 0.2892 | 0.355 |
| 27 | 1.13% | 0.2287 | 0.2552 | 0.356 |
| 28 | 0.72% | 0.2983 | 0.2424 | 0.326 |
| 29 | 0.22% | 0.3443 | 0.2386 | 0.329 |

Homelessness falls by a factor of twelve between 26 and 27 while income FALLS,
0.2892 to 0.2552, and the disorder rate is flat, 0.355 to 0.356. The only thing
that changes is wealth, 0.0960 to 0.2287 -- one year's saving, and it happens to
land exactly on grid point 63. Whatever puts a 26 year old on the street is
undone by roughly 0.13 of assets, which is about one year's rent on the cheapest
unit. That is the measurement the endowment target rests on.

Note also that the age profile of income is DECLINING from 26 to 29 even though
the GKKOC efficiency profile rises over that range. That is a composition
effect in the reported statistic -- it is conditional on being a renter, and at
26 the households excluded as homeless are the poorest -- and it is worth
confirming separately rather than assuming.
