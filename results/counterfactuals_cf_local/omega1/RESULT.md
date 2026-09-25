# omega_c = 1, damped (drug_market_adjuster 0.1), 25 September

This is Housing First at weight_on_child 1 (otherwise the omega_c = 0.06 benchmark),
kappa_x 0.9329, no budget clearing (adjust_taxes 0), and the drug price clearing at
supply elasticity 1.46. It ran in the coordinator's container against the benchmark
in code/cfarm_bench, the one the damped internalisation arm used (b -6.9e-5 against
the reference; results/counterfactuals_cf_local/bench). drug_price_start is 0.81,
estimated from two demand points (see CALIBRATION_STATE.md, 25 September 04:50).
A first attempt started at 0.6 and was stopped after one pass: at that price demand
was 1.91 against supply 0.24.

## Checks

- `VOUCHER CHECK PASS`: the arm ran at 0.067533863251354, the benchmark's value.
- `HANDOVER drug_market_adjuster 0.2 -> 0.1`, `drug_price_start 0.81` applied.
- Exit after pass 16, with every live distance inside its rule: the CF moments
  9.24e-05 against 5e-4, the drug market 3.14e-03 against 5e-3; then `simulation_ended`.

## Passes (price = the price households faced in that pass)

| pass | price | b | lambda_d | h_1 | drug V | drug gap | CF distance | change in b |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.81000 | 0.070816 | 0.028839 | 0.0052457 | 0.6243 | 3.520e-01 | 1.63e+00 |  |
| 2 | 0.81405 | 0.068419 | 0.028889 | 0.0052894 | 0.6001 | 3.170e-01 | 3.43e-03 | -3.38% |
| 3 | 0.81812 | 0.066763 | 0.028510 | 0.0052906 | 0.5777 | 2.839e-01 | 1.66e-03 | -2.42% |
| 4 | 0.82221 | 0.066349 | 0.028370 | 0.0052894 | 0.5726 | 2.731e-01 | 5.38e-04 | -0.62% |
| 5 | 0.82632 | 0.063303 | 0.027440 | 0.0052802 | 0.5506 | 2.400e-01 | 3.05e-03 | -4.59% |
| 6 | 0.83045 | 0.062621 | 0.027130 | 0.0052776 | 0.5396 | 2.212e-01 | 6.82e-04 | -1.08% |
| 7 | 0.83461 | 0.062069 | 0.026757 | 0.0052707 | 0.5304 | 2.047e-01 | 5.52e-04 | -0.88% |
| 8 | 0.83878 | 0.059117 | 0.025271 | 0.0052466 | 0.4960 | 1.539e-01 | 2.95e-03 | -4.75% |
| 9 | 0.84297 | 0.058337 | 0.024893 | 0.0052439 | 0.4851 | 1.347e-01 | 7.80e-04 | -1.32% |
| 10 | 0.84719 | 0.057834 | 0.024754 | 0.0052416 | 0.4795 | 1.228e-01 | 5.03e-04 | -0.86% |
| 11 | 0.85142 | 0.057648 | 0.024676 | 0.0052397 | 0.4756 | 1.132e-01 | 1.86e-04 | -0.32% |
| 12 | 0.85568 | 0.054926 | 0.023943 | 0.0053358 | 0.4456 | 6.673e-02 | 2.72e-03 | -4.72% |
| 13 | 0.85996 | 0.054826 | 0.023873 | 0.0053370 | 0.4422 | 5.770e-02 | 1.00e-04 | -0.18% |
| 14 | 0.86426 | 0.054550 | 0.023671 | 0.0053333 | 0.4367 | 4.552e-02 | 2.76e-04 | -0.50% |
| 15 | 0.86858 | 0.052879 | 0.023274 | 0.0053289 | 0.4126 | 6.541e-03 | 1.67e-03 | -3.06% |
| 16 | 0.86931 | 0.052787 | 0.023184 | 0.0053286 | 0.4108 | 3.139e-03 | 9.24e-05 | -0.17% |

The price ended at 0.86997.

## Result against the benchmark

| outcome | final | change |
|---|---|---|
| b | 0.052787 | -35.04% |
| lambda_d | 0.023184 | -33.02% |
| h_1 | 0.0053286 | -12.34% |
| drug price | 0.86997 | -13.00% |

`model_treatment_take_up,  0.26052576822535978`
`model_eligibles_getting_voucher=  0.27301821565213569`

## The caveat: b moves in steps

b falls in steps of 3 to 5 per cent at passes 5, 8, 12 and 15, and barely moves in
between. The drops come each time the price has risen about 1.5 to 2 per cent: the
price faced was 0.8263, 0.8386, 0.8557 and 0.8693. The value function is re-solved
EVERY pass (the AGE_TIME lines are in every pass), so these are not solve-skipping
artefacts. The likeliest reading is that drug demand responds to price in discrete
jumps. By pass 16 the price had stopped (0.8693 to 0.8700, with the drug gap 3.1e-3
inside its rule), so no further step was due. The fixed-price omega_c = 1 run (price
1, results/counterfactuals/omega_c_1) got b -75 per cent; with the price clearing it
falls 13 per cent, and the drop in b is about half as large.

## Welfare lines (verbatim; the author asked for no CEV on this arm)

```
 average_welfare_of_youngest_cohort=   1306.8510273401641
 average_welfare_of_all_cohorts=   1019.5862976768858
 average_welfare_with_childhood=   779.13796457465105
 average_welfare_of_all_cohorts=   1019.5862976768858
 average_welfare_of_youngest_cohort=   1306.8510273401641
 welfare_by_addiction=   1019.2973134323637
 welfare_by_addiction_youngest=   1306.8510273401641
 welfare_by_addiction=   1031.7620808521483
 welfare_by_addiction_youngest=   0.0000000000000000
 CEV from the saved benchmark curve: target=   779.13796457465105       x= -0.24676096866962272
 welfare_of_gains_by_addiction= -0.24676096866962272
```
