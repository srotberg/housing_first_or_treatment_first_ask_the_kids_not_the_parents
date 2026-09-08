# The two drug price elasticities at the benchmark of record

Measured by compiling with `measure_price_elasticity=1` (line 429 of
`code/housing_first_or_treatment_first_SR_v1.f90`) and running the `VECTOR` line
of `code/benchmark_of_record.txt` through `code/run_one_point.sh`. Output:
`code/points/point_6876263050.txt`, stamped `MODEL 567e5ce595`.

Both are **validation moments, not targets**. Nothing in the calibration
disciplines either one: the participation margin comes out of the drug market
and the intensive margin out of the utility weight, and neither enters the loss.

## What the experiment is

The price of the addictive good is **set** to 1.10 times its benchmark value and
demand is re-solved directly — `solve_value_function_and_policy_functions`, then
`converge_to_stationary_equilibrium`, then `stationary_equilibrium_statistics`
and `govt_revenues_calc`. The drug market clears in the *outer* calibration loop,
so the price stays where it is put. What comes back is therefore the quantity
demanded at the new price and not a new equilibrium, which is what an elasticity
of demand is. Rents, house prices, taxes and inheritances are held for the same
reason. The step is +10 per cent.

| | benchmark (p = 1.0) | p = 1.1 | change |
|---|---|---|---|
| drug users (share) | 0.07769929 | 0.05762084 | −25.84% |
| quantity per user | 0.05332149 | 0.04575340 | −14.19% |
| quantity per addict | 0.06985202 | 0.06127863 | −12.27% |
| quantity per experimenter | 0.04075481 | 0.03389269 | −16.84% |
| addict share of users | 0.43188605 | 0.43309509 | +0.28% |

## The participation margin

```
UNTARGETED price elasticity, participation   model=  -3.1367243309284976       observed= -0.63000000000000000
```

| model | data (Saffer and Chaloupka) | gap |
|---|---|---|
| **−3.137** | **−0.63** | **+398%** too elastic (4.98× the data value) |

## The intensive margin

The intensive margin is the **per-addict** number, not the per-user one:
Olmstead et al. measure a conditional elasticity among continuing regular users.

```
UNTARGETED price elasticity, intensive       model=  -1.3739137300224997       observed= -0.55000000000000004
```

| model | data (midpoint of −0.3 to −0.8) | gap |
|---|---|---|
| **−1.374** | **−0.55** | **+150%** too elastic (2.50× the midpoint) |

Against the ends of the range rather than the midpoint: 72% more elastic than
the most elastic end (−0.8), and 358% more elastic than the least (−0.3).

## The mixed quantity-per-user diagnostic

```
DIAG elasticity, quantity per USER (mixed)      =  -1.6060542288585282
DIAG elasticity, quantity per ADDICT            =  -1.3739137300224997
DIAG elasticity, quantity per EXPERIMENTER      =  -1.9344697755235933
DIAG elasticity, ADDICT SHARE of users          =   2.9330939392551932E-002
```

Quantity per user, **−1.606**, is the mixed statistic and is not comparable to
the literature: it blends each household's own response with a shift in who is
being averaged over. Here the two pieces work in opposite directions and the
composition term is small. Experimenters cut back much harder than addicts
(−1.934 against −1.374), which pulls the mean down; but the addict share of
users *rises* slightly (elasticity +0.029, from 43.19% to 43.31% of users),
which pushes it up, because addicts consume more. The net −1.606 sits between
the two per-type numbers and 0.23 more elastic than the per-addict figure that
the literature actually measures.

Note that the per-addict −1.374 is close to the bound the first-order condition
puts on an individual, about −1.3, which the source cites as how an earlier
−5.06 per-user reading was caught as a composition artefact. It is now only
just outside that bound, so the intensive margin is no longer obviously a
mis-measurement — it is a genuinely over-elastic household response.

## Any ELASTICITY HELD or ELASTICITY SKIPPED lines

**None.** `point_6876263050.txt` contains zero lines matching
`ELASTICITY HELD` or `ELASTICITY SKIPPED`. Both numbers were computed:
`measure_price_elasticity` was 1, `measure_child_gap` was 0 in the vector so
omega did not run first and leave its distribution behind, drug use was strictly
positive in the benchmark, and participation and quantity per addict were both
strictly positive at the higher price. The two guard rows that would have
replaced a number with a held line did not fire.

## Does the model sit inside the literature's range?

**No — neither margin does, and both miss on the same side by a wide margin.**

- The participation elasticity, −3.14, is five times Saffer and Chaloupka's
  −0.63. There is no reading of that literature that admits it.
- The intensive elasticity, −1.374, is outside the −0.3 to −0.8 range
  altogether, 72% beyond even the most elastic end.

Both are over-elastic, so a 10 per cent price rise moves this economy's drug
market far more than the evidence says it should: a quarter of users leave, where
the data imply about 6 per cent would. Since neither moment is targeted, this is
information about the model rather than a failed solve — the drug market and the
utility weight jointly produce a demand curve much flatter than the estimated
one, and nothing in the calibration was ever asked to stop them. Anything that
turns on the response of drug use to its price — the price-capped benchmark, and
any counterfactual that moves the effective price of using — inherits that
overstatement.

For context, the benchmark also undershoots its own targeted drug-use moment
(`MOMENT b total drug users` model 7.77% against target 8.90%), so the level of
use is a little low at the same time as its price response is much too strong.
