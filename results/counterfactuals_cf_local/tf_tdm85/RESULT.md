# Rationed TF, 85 per cent detection, on the fully swept build, 26 September 08:00

Build code/cf_tdm: distribution swept at least 70 times a pass then to 5e-5; budget cleared to
1e-3 through pi_V with the step halved on each sign change; seeded from the no-policy run's
converged distribution. Target 6.1753486647 (the no-policy run on the same build,
../null_tdm), `TARGET CHECK PASS`; `DIST CHECK PASS: 6 passes, sweeps [70, 72, 70, 72, 70, 70]`;
`simulation_ended`. Start pi_V 0.074, price 0.874.

| pass | price | pi_V | b | SUD | h_1 | drug gap | budget gap | CEV |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.8747 | 0.07400 | -27.7% | -28.5% | +9.6% | 7.5e-3 | 1.55e-1 | +1.04% (pass-1 artefact) |
| 2 | 0.8709 | 0.08173 | -32.9% | -33.5% | +4.6% | 3.9e-2 | 2.6e-3 | +1.54% |
| 3 | 0.8679 | 0.08186 | -31.4% | -32.0% | +5.0% | 1.7e-2 | 8.7e-4 | +1.30% |
| 4 | 0.8670 | 0.08184 | -30.4% | -31.0% | +5.3% | 4.0e-3 | 4.5e-4 | +1.20% |
| 5 | 0.8663 | 0.08185 | -30.3% | -30.9% | +5.4% | 1.9e-3 | 1.4e-3 | +1.18% |
| 6 | 0.8666 | 0.08184 | -29.8% | -30.4% | +5.6% | 3.4e-3 | 6.7e-4 | +1.13% |

    CEV from the saved benchmark curve: target=   789.73096942391930       x=   1.1278505737441052E-002

CEV +1.13 per cent against the saved benchmark, about +1.39 net of the no-policy run (-0.26).
pi_V settled at once (no cycle). NOT FIRM, two reasons: (1) drug use was still rising about half
a point a pass and welfare slipping about 0.05 a pass at exit; the moments rule (5e-4) passed
at 4.3e-4. The drift is most likely the parent-to-child penalty converging one generation per
pass (newborn shares update once a pass); a 1e-4 moments rule would settle it. (2) The
no-policy counterfactual does not reproduce the benchmark (revenue +0.137, welfare -0.26) and
the benchmark re-solve shows the gap is in the counterfactual binary (../../reference/
hf_omega_c_006_tdm); if that is an error, this run is redone after the fix. The converged
distribution is kept gzipped in the scratchpad (seed_tf_tdm85).
