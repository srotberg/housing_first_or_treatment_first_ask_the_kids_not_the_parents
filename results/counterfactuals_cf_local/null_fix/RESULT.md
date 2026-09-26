# No-policy counterfactual on the fixed build -- reproduces the benchmark, 26 September 11:10

Build code/cf_fix: the fully swept build (at least 70 sweeps a pass, then 5e-5) with the hidden
labour-tax rise removed (the three hard-coded increase_in_labour_income_tax warm starts keep the
benchmark's uploaded value, 0; ENGINE.md, 26 September 10:00) and the counterfactual moments rule
1e-4. No policy change; seeded from the old build's no-policy distribution; price start 1.0.
`VOUCHER CHECK PASS`; `DIST CHECK PASS: 5 passes, sweeps [70, 70, 72, 75, 70]`; `simulation_ended`.

| pass | price | b | SUD | h_1 | net revenue | CEV |
|---|---|---|---|---|---|---|
| 1 | 1.0029 | +1.8% | +1.9% | -1.1% | 6.1797 | +1.53% (pass-1 artefact) |
| 2 | 1.0022 | -0.6% | -0.7% | -0.4% | 6.0513 | +0.34% |
| 3 | 0.9997 | -0.4% | -0.4% | -0.1% | 6.0377 | +0.05% |
| 4 | 0.9999 | -0.0% | -0.0% | -0.1% | 6.0376 | +0.03% |
| 5 | 1.0000 | -0.0% | -0.0% | -0.0% | 6.0371 | +0.03% |

    CEV from the saved benchmark curve: target=   789.35793557166676       x=   2.6362611341242457E-004

THE COUNTERFACTUAL PATH NOW REPRODUCES THE BENCHMARK: behaviour to 0.0 per cent, net revenue
6.03708 against 6.03888, total tax revenue 14.045 against 14.040, CEV +0.026 per cent (the old
build: 6.1753 and -0.26). Budget target for TF runs on this build: 6.0370824602930142. (TF 85,
code/cfarm_tf_fix85, was launched against pass 3's 6.03766, 0.0006 away: inside the 1e-3 budget
rule, worth about 0.01 per cent of CEV.) Final distribution kept in code/seed_null_fix.
