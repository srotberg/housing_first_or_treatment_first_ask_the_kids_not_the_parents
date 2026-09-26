> SUPERSEDED 26 September by ../tf_tight85 (the budget closed to 2e-3); this run stopped with a gap of 0.014.

> UNDER REVIEW with the 70 per cent run: the welfare figures are being checked (see ../tf/RESULT.md).

# Rationed TF at 85 per cent detection, like-for-like budget, 25 September

The author, 25 September: "ok, run the 85% detection one" (tests are by surprise).
Identical to ../tf (the 70 per cent run) except probability_of_detection 0.85 and
a price start of 0.87. TARGET CHECK PASS at 6.26479885996; exit after pass 10 by
the run's own rule; budget gap 0.014 and drug-market gap 0.002 at exit.

## Result against the benchmark, next to the 70 per cent run

| outcome | 70% detection | 85% detection |
|---|---|---|
| drug participation | -27.7% | -28.0% |
| SUD | -28.2% | -29.6% |
| homelessness | +8.9% | +10.3% |
| SMI prevalence | -0.3% | -0.4% |
| SMI share of homeless | -6.0% | -6.7% |
| drug quantity | -17.5% | -18.0% |
| drug price | -11.9% | -12.9% |
| voucher probability | +5.9% | +5.2% |
| eligibles holding a voucher | -5.3% | -6.5% |
| voucher spending | -6.0% | -7.2% |

Welfare: CEV -0.20 per cent (model: x = -2.0158146899279103E-003, lifetime welfare
789.2802 against the benchmark's 789.3489), against +0.15 per cent at 70 per cent.
The no-policy run's own CEV is +0.14 per cent, so net of it: -0.34 against +0.01.

## Lifetime welfare by pass (benchmark 789.3489)

| pass | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| welfare | 789.379 | 789.018 | 789.128 | 789.318 | 789.510 | 789.600 | 789.552 | 789.446 | 789.341 | 789.280 |
| CEV | +0.09% | -0.94% | -0.63% | -0.09% | +0.49% | +0.76% | +0.62% | +0.29% | -0.02% | -0.20% |
