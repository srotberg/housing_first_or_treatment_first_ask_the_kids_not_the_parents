# omega_c = 1, no budget clearing: long-run steady state on the corrected build

27 September, 07:49 to 09:54 UTC, remote container. CONVERGED at pass 7; all checks pass. ONE
equilibrium, the one at the pass the run exited on.

## Settings

- Build `cf_fix2` (`code/cf_runs/build_cf_fix.sh` then `build_cf_fix2.sh`).
- Command, from `code/`:
  `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench DIAG_TAG=_fix2 DRUG_PRICE_START=0.870 sh cf_runs/cf_arm.sh omega1 > cfarm_omega1_fix2.out 2>&1`
- Housing First at `weight_on_child` 1, otherwise the omega_c = 0.06 benchmark. No budget clearing
  (`adjust_taxes` 0): pi_V stays at the benchmark's and the change in net revenue is unfunded.
  Drug supply elasticity 1.46, price clearing.
- Ran on this container's benchmark (welfare 789.34923420870734, 3.8e-7 relative from the
  coordinator's; same pi_V). Compared below with this container's no-policy run (`../null_remote`).

## Checks (from `run.out.gz`)

    HANDOVER voucher probability:   5.9999998658895493E-002 ->   6.7533863251354007E-002
    VOUCHER CHECK PASS: arm ran at 6.7533863251354007E-002, benchmark 6.7533863251354007E-002
    DIST CHECK PASS: 7 passes, sweeps [71, 70, 70, 72, 70, 70, 72], largest final 4.38e-05 (rule 5e-05, at least 70 sweeps)

Exit pass 7: drug-market gap 3.71e-3 (rule 5e-3), change in the moments from pass 6 9.16e-5
(rule 1e-4). The budget is not cleared in this arm.

## Passes (`passes.txt`; changes against the benchmark)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8743  0.06753   -29.3%   -29.5%   -14.7%  8.30e-02  0.00e+00   779.6589  -23.64%
      2  0.8700  0.06753   -42.6%   -42.9%   -13.3%  9.78e-02  0.00e+00   779.4425  -24.07%
      3  0.8675  0.06753   -36.9%   -37.2%   -12.8%  3.52e-02  0.00e+00   779.3268  -24.30%
      4  0.8632  0.06753   -36.9%   -37.2%   -12.8%  3.09e-02  0.00e+00   779.3186  -24.32%
      5  0.8648  0.06753   -34.6%   -34.9%   -12.7%  1.85e-02  0.00e+00   779.2951  -24.36%
      6  0.8645  0.06753   -35.7%   -36.0%   -12.7%  4.01e-03  0.00e+00   779.2961  -24.36%
      7  0.8630  0.06753   -35.7%   -36.0%   -12.7%  3.71e-03  0.00e+00   779.2984  -24.36%

The CEV column is against the omega_c = 0.06 benchmark's welfare curve and is NOT a welfare
comparison for this arm: omega_c = 1 changes the welfare function itself, and the author asked for
no CEV on this arm (`../../counterfactuals_cf_local/omega1/RESULT.md`). It is left in only
because `passes.py` prints it.

## The equilibrium (pass 7)

Against the benchmark (b 0.081255, lambda_d 0.034611, h_1 0.0060789):

| outcome | level | change against the benchmark |
|---|---|---|
| drug use b | 0.052248 | -35.7% |
| SUD lambda_d | 0.022146 | -36.0% |
| homelessness h_1 | 0.0053093 | -12.7% |
| drug price | 0.86303 | |
| pi_V, voucher probability | 0.067534 (held at the benchmark's) | |
| budget gap | not cleared: net revenue 5.89736 against 6.03734 in the no-policy run, -0.13998 | |
| drug-market gap | 3.71e-3 | |
| welfare (with childhood) | 779.29845 | |
| CEV | not reported (see above) | |

Against this container's no-policy run (`final.txt`):

| outcome | omega_c = 1 | no policy | change |
|---|---|---|---|
| drug use b | 0.052248 | 0.081236 | -35.7% |
| SUD lambda_d | 0.022146 | 0.034595 | -36.0% |
| homelessness h_1 | 0.0053093 | 0.0060751 | -12.6% |
| drug price | 0.8630 | 1.0000 | -13.7% |
| households holding a voucher | 0.06251 | 0.06231 | +0.3% |
| eligibles getting a voucher | 0.2726 | 0.2725 | +0.0% |
| treatment take-up | 0.2496 | 0.2500 | -0.2% |
| SUD share of the homeless | 0.1121 | 0.1921 | -41.6% |
| SMI share of the homeless | 0.2111 | 0.2545 | -17.0% |
| employed share of the homeless | 0.2493 | 0.2142 | +16.4% |
| voucher spending | 0.69171 | 0.68397 | +1.1% |
| food stamps | 0.23500 | 0.23852 | -1.5% |
| net government revenue | 5.89736 | 6.03734 | -2.3% |
| welfare (with childhood) | 779.29845 | 789.35899 | |
| childhood utility | 452.21135 | 450.79811 | +1.41 utils |

## Welfare lines of the exit pass (verbatim)

     average_welfare_of_all_cohorts=   1019.7296146669873
     average_welfare_of_youngest_cohort=   1307.2063442965430
     welfare_by_addiction=   1019.3004685622656
     welfare_by_addiction_youngest=   1307.2063442965427
     welfare_by_addiction=   1038.6710611923158
     welfare_by_addiction_youngest=   0.0000000000000000
     average_welfare_of_youngest_cohort=   1307.2096727997016
     average_welfare_of_all_cohorts=   1019.7344635293226
     average_welfare_with_childhood=   779.29844580686427

The coordinator's 25 September omega_c = 1 run on the older build ended at
average_welfare_with_childhood 779.13796 (`../../counterfactuals_cf_local/omega1`).
