# No-policy counterfactual on the fully swept build, 26 September 04:35

The counterfactual binary with no policy change (omega_c 0.06, pi_V at the benchmark's
0.067534, no budget clearing), build code/cf_tdm: distribution swept at least 70 times a
pass (one lifetime, life_span 60) and then to 5e-5, seeded from the benchmark's saved
distribution. Drug price clears at elasticity 1.46; start 1.00014.

## Checks at exit (pass 5)

- `VOUCHER CHECK PASS`; `DIST CHECK PASS: 5 passes, sweeps [75, 73, 70, 70, 70], largest
  final 4.94e-05`; `simulation_ended`.
- Drug-market gap 1.2e-3 (rule 5e-3), CF moments 1.1e-4 (rule 5e-4).

## Result against the saved benchmark (passes.txt holds every pass)

| pass | price | b | SUD | h_1 | net revenue | welfare | CEV |
|---|---|---|---|---|---|---|---|
| 1 | 1.0034 | +2.2% | +2.2% | -0.9% | 6.3177 | 789.7594 | +1.21% (pass-1 artefact) |
| 2 | 1.0024 | -0.8% | -0.8% | -0.4% | 6.1887 | 789.3630 | +0.04% |
| 3 | 1.0004 | -0.4% | -0.4% | -0.1% | 6.1758 | 789.2621 | -0.25% |
| 4 | 0.9983 | -0.3% | -0.3% | -0.0% | 6.1754 | 789.2614 | -0.26% |
| 5 | 0.9978 | -0.2% | -0.2% | +0.0% | 6.1753 | 789.2597 | -0.26% |

    CEV from the saved benchmark curve: target=   789.25969101961334       x=  -2.6155885603710684E-003

With no policy the behaviour matches the benchmark to 0.2 per cent, but welfare is 0.26 per
cent of CEV below it and net revenue 0.137 above it (the saved 6.0389). The old loose-solve
no-policy run gave +0.14 per cent and 6.2646: the no-policy economy's welfare and revenue move
with how fully the distribution is solved, which points at the benchmark's own saved values
(solved on the loose rule). The benchmark re-solve on the same numerics (code/cfarm_bench_tdm)
decides it. Budget target for TF runs on this build, if the benchmark stands: 6.1753486647.
The final distribution is kept gzipped in the scratchpad (seed_null_tdm) for seeding.
