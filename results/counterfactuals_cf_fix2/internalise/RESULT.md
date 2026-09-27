# Internalisation, no budget clearing: steady state on the damped build -- READ THE CAVEAT

27 September, 12:40 to 14:54 UTC, remote container. The run EXITED at pass 7 with every stopping
rule met and all checks passing. This is the one equilibrium reported, the pass the run exited on.

**CAVEAT: the exit pass is very probably the quiet phase of a period-three cycle, not a settled
fixed point.** The undamped run of this arm (`../internalise_cycle`) cycled with b jumping to
0.08106 on passes 5 and 8 and returning in between. This damped rerun did exactly the same on
passes 5-6 (b 0.08104, moments change 1.42e-3 and 1.43e-3) and exited at pass 7, the quiet pass,
where the moments change was 2.3e-5. In the undamped run the corresponding pass 7 was at 1.6e-4,
just above the rule, and pass 8 jumped again. On the jump phase drug use is -0.3 per cent against
the benchmark instead of -2.0 per cent, and the CEV column reads +0.10 instead of +0.15, so the
phase the run stops on matters for the result. Same situation as arm 3 in ENGINE.md (24 September
22:20: "stopped on a phase of the cycle").

## Settings

- Build `cf_fix2_damp` (`code/cf_runs/build_cf_fix2.sh` then `build_cf_fix2_damp.sh`), after the
  undamped run cycled (coordinator's cycle rule).
- Command, from `code/`:
  `OMP_NUM_THREADS=2 BUILD=cf_fix2_damp SEED_FROM=bench DIAG_TAG=_damp DRUG_PRICE_START=0.9964 sh cf_runs/cf_arm.sh internalise > cfarm_internalise_damp.out 2>&1`
  (the original: `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench DIAG_TAG=_fix2 DRUG_PRICE_START=0.997 sh cf_runs/cf_arm.sh internalise`).
- `internalise_homelessness_cost` 1, `weight_on_child` 0.06, no budget clearing (`adjust_taxes` 0),
  pi_V held at the benchmark's. Drug supply elasticity 1.46, price clearing.
- Ran on this container's benchmark (3.8e-7 relative from the coordinator's; same pi_V). Compared
  below with this container's no-policy run (`../null_remote`).

## Checks (from `run.out.gz`)

    HANDOVER voucher probability:   5.9999998658895493E-002 ->   6.7533863251354007E-002
    VOUCHER CHECK PASS: arm ran at 6.7533863251354007E-002, benchmark 6.7533863251354007E-002
    DIST CHECK PASS: 7 passes, sweeps [70, 80, 70, 72, 72, 73, 71], largest final 3.52e-05 (rule 5e-05, at least 70 sweeps)

Exit pass 7: drug-market gap 2.73e-3 (rule 5e-3), change in the moments from pass 6 2.26e-5
(rule 1e-4). The budget is not cleared in this arm.

    pass  moments change  b
     1  1.628e+00  0.08298666
     2  1.045e-02  0.07909754
     3  3.875e-04  0.07923243
     4  3.792e-04  0.07961163
     5  1.425e-03  0.08103619
     6  1.433e-03  0.07960322
     7  2.259e-05  0.07960640

## Passes (`passes.txt`; changes against the benchmark)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  1.0014  0.06753    +2.1%    +2.2%    -2.9%  4.95e-02  0.00e+00   789.8599  +1.51%
      2  1.0001  0.06753    -2.7%    -2.7%    -2.5%  1.60e-02  0.00e+00   789.4937  +0.43%
      3  0.9956  0.06753    -2.5%    -2.5%    -2.4%  1.26e-02  0.00e+00   789.4480  +0.29%
      4  0.9949  0.06753    -2.0%    -2.0%    -2.2%  1.81e-03  0.00e+00   789.4211  +0.21%
      5  0.9964  0.06753    -0.3%    -0.3%    -2.2%  1.54e-02  0.00e+00   789.3814  +0.10%
      6  0.9962  0.06753    -2.0%    -2.0%    -2.2%  3.25e-03  0.00e+00   789.4008  +0.15%
      7  0.9951  0.06753    -2.0%    -2.0%    -2.2%  2.73e-03  0.00e+00   789.3995  +0.15%

The CEV column is printed by `passes.py`; the author asked for no CEV on this arm
(`../../counterfactuals_cf_local/internalise/RESULT.md`), so it is not reported below.

## The equilibrium (pass 7)

Against the benchmark (b 0.081255, lambda_d 0.034611, h_1 0.0060789):

| outcome | level | change against the benchmark |
|---|---|---|
| drug use b | 0.079606 | -2.0% |
| SUD lambda_d | 0.033906 | -2.0% |
| homelessness h_1 | 0.0059429 | -2.2% |
| drug price | 0.99509 | |
| pi_V, voucher probability | 0.067534 (held at the benchmark's) | |
| budget gap | not cleared: net revenue 6.03976 against 6.03734 in the no-policy run, +0.00242 | |
| drug-market gap | 2.73e-3 | |
| welfare (with childhood) | 789.39947 | |
| CEV | not reported (the author asked for none on this arm) | |

Against this container's no-policy run (`final.txt`):

| outcome | internalisation | no policy | change |
|---|---|---|---|
| drug use b | 0.079606 | 0.081236 | -2.0% |
| SUD lambda_d | 0.033906 | 0.034595 | -2.0% |
| homelessness h_1 | 0.0059429 | 0.0060751 | -2.2% |
| drug price | 0.9951 | 1.0000 | -0.5% |
| households holding a voucher | 0.06227 | 0.06231 | -0.1% |
| treatment take-up | 0.2508 | 0.2500 | +0.3% |
| SUD share of the homeless | 0.1884 | 0.1921 | -1.9% |
| SMI share of the homeless | 0.2566 | 0.2545 | +0.8% |
| net government revenue | 6.03976 | 6.03734 | +0.04% |
| welfare (with childhood) | 789.39947 | 789.35899 | +0.04 utils |

## Welfare lines of the exit pass (verbatim)

     average_welfare_of_all_cohorts=   1031.7943204255660
     average_welfare_of_youngest_cohort=   1352.9638537453527
     welfare_by_addiction=   1031.1272790031653
     welfare_by_addiction_youngest=   1352.9638537453527
     welfare_by_addiction=   1050.8026935544851
     welfare_by_addiction_youngest=   0.0000000000000000
     average_welfare_of_youngest_cohort=   1352.9625065588209
     average_welfare_of_all_cohorts=   1031.7967632567932
     average_welfare_with_childhood=   789.39947116316455

The coordinator's 25 September internalisation run on the older build ended at
average_welfare_with_childhood 789.39705 (`../../counterfactuals_cf_local/internalise`).
