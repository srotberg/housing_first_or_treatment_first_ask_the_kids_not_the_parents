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

**SUPERSEDED, and by something better than what I proposed.** I was going to
make the snap a lottery over the two adjacent grid points. The author's answer
was to stop snapping at all: "instead of pegging them to a financial grid, just
give them an endowment only in the first period. that would be continuous ...
and it would show in the BC not the initialization."

That is what the model now does. Newborns start at ZERO assets and receive
`newborn_endowment_scale` times average labour income as cash in hand at age 26,
carried as `newborn_age_transfer`, a per-age array with only element 1 nonzero,
added at the nine sites that already add a transfer to resources. It is added
outside the productivity scaling, because the endowment is flat.

Three things the lottery would not have given:

- the endowment is continuous in the scale, so it can be bisected rather than
  only bracketed;
- a scale of zero is a genuine zero, which the snap could not deliver;
- the household, not the grid, decides how much of it to carry into age 27.

The bequest side matches: the transfer is removed from the bequests and the rest
goes to the government. `model_total_inheritance` accumulates the newborn
transfer, and what the government collects is `model_bequests -
value_of_initial_assets - model_total_inheritance`, with `value_of_initial_assets`
now zero because nobody is endowed in the distribution any more.

The grid table above still matters, just not for the endowment. It is the grid
every household's SAVING decision is made on, and one rung between zero and a
year's rent was an artifact sitting exactly on the margin the model measures. On
the author's instruction -- "I think we should make the grid expander around 2
or 3 in general" -- `financial_grid_expander_positive` is a settable parameter
now, default 3.0, which puts five rungs below a year's rent instead of one.

## What the six running points actually deliver

**These four were stopped.** They ran the snapped mechanism, which no longer
exists, so they answer a question that has been retired. The table is kept
because it is what showed the mechanism was wrong. The live sweep is
`code/batch_transfer.txt`: six points at scale 0, 0.15, 0.30, 0.50, 0.75 and
1.00, delivering 0 to 0.637 in cash at age 26 -- zero to 5.3 years of rent --
all at expander 3.0 so they share one model. Scale 0.15 delivers 0.0956, within
a rounding error of the 0.0960 the SCF distribution was handing newborns on
average, so it is the no-change point of the sweep.


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
