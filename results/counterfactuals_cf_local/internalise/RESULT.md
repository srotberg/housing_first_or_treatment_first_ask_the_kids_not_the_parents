# Internalisation, damped (drug_market_adjuster 0.1), 25 September

`code/remote_cf_arm.sh internalise`, run in the coordinator's container. It is
Housing First at omega_c = 0.06 with internalise_homelessness_cost 1, kappa_x 0.9329,
no budget clearing (adjust_taxes 0), and the drug price clearing at supply
elasticity 1.46. The benchmark was solved in the same directory, code/cfarm_bench.

## Benchmark (stage 1, 12 blocks)

b = 0.0812550098, lambda_d = 0.0346112458, h_1 = 0.0060788992. Against the
reference b = 0.081260630474628087 the relative difference is -6.9e-5.

## Checks

- `VOUCHER CHECK PASS`: the arm ran at 0.067533863251354, the benchmark's value.
- `HANDOVER drug_market_adjuster 0.2 -> 0.1`, `drug_price_start 1.0` applied.
- Exit: every live distance was inside its rule after pass 10 (the CF moments
  2.96e-04 against 5e-4, the drug market 2.60e-03 against 5e-3); `simulation_ended`.

## Passes

| pass | b | lambda_d | h_1 | price after | drug gap | CF distance | change in b |
|---|---|---|---|---|---|---|---|
| 1 | 0.077884 | 0.032557 | 0.0058488 | 0.99843 | 1.573e-02 | 1.629e+00 |  |
| 2 | 0.079046 | 0.033685 | 0.0059152 | 0.99600 | 9.548e-03 | 2.983e-03 | +1.492% |
| 3 | 0.079163 | 0.033686 | 0.0059199 | 0.99362 | 5.955e-03 | 8.160e-04 | +0.149% |
| 4 | 0.079930 | 0.033759 | 0.0059218 | 0.99479 | 5.776e-03 | 8.511e-04 | +0.969% |
| 5 | 0.079868 | 0.033816 | 0.0059245 | 0.99617 | 3.459e-03 | 8.764e-04 | -0.078% |
| 6 | 0.079324 | 0.033816 | 0.0059220 | 0.99564 | 5.308e-03 | 5.439e-04 | -0.681% |
| 7 | 0.079883 | 0.033834 | 0.0059272 | 0.99579 | 2.121e-03 | 5.586e-04 | +0.704% |
| 8 | 0.079375 | 0.033835 | 0.0059266 | 0.99534 | 4.493e-03 | 5.079e-04 | -0.636% |
| 9 | 0.079903 | 0.033851 | 0.0059280 | 0.99551 | 2.738e-03 | 5.281e-04 | +0.665% |
| 10 | 0.079923 | 0.033869 | 0.0059288 | 0.99655 | 2.599e-03 | 2.960e-04 | +0.025% |

## Result against the benchmark

| outcome | final | change |
|---|---|---|
| b | 0.079923 | -1.64% |
| lambda_d | 0.033869 | -2.14% |
| h_1 | 0.0059288 | -2.47% |
| drug price | 0.99655 | |

**b is soft; lambda_d and h_1 are not.** From pass 4 on, b alternates between
about 0.0793 and 0.0799 (0.7 per cent) while the price stays inside 0.9953 to
0.9966. So the swing is not the drug market's: the 0.2-damped run
(results/counterfactuals_cf_v2/internalise) shows the same swing and stops at the
same top, b = 0.07991. Over the last five passes b averages 0.079682
(-1.94%), and the range is -2.38% to
-1.64%. The CF-moments rule is 5e-4 ABSOLUTE on b,
about 0.6 per cent, so it cannot resolve a swing this size. Over the same passes,
lambda_d moves less than 0.1 per cent and h_1 less than 0.05 per cent.

## Welfare lines (verbatim; the author asked for no CEV on this arm)

```
 average_welfare_of_youngest_cohort=   1352.9346438845055     
 average_welfare_of_all_cohorts=   1031.7970785774048     
 average_welfare_with_childhood=   789.39704844490370     
 average_welfare_of_all_cohorts=   1031.7970785774048     
 average_welfare_of_youngest_cohort=   1352.9346438845055     
 welfare_by_addiction=   1031.0992776450360     
 welfare_by_addiction_youngest=   1352.9346438845057     
 welfare_by_addiction=   1051.7021037789152     
 welfare_by_addiction_youngest=   0.0000000000000000     
 CEV from the saved benchmark curve: target=   789.39704844490370       x=   1.4100510439405973E-003
 welfare_of_gains_by_addiction=   1.4100510439405973E-003
```
