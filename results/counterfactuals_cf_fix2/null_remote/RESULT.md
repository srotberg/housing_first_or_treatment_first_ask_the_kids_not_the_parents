# No policy change, remote container: the budget target for this container's arms

26 September, 17:57 to 19:30 UTC. CONVERGED at pass 5; all checks pass. ONE equilibrium, the
pass the run exited on.

## Why this run

This container's STAGE 1 benchmark (`code/cfarm_bench`, same tracked source, gfortran 13.3.0)
ended at average_welfare_with_childhood 789.34923420870734 against the coordinator's
789.34893176009462 (relative 3.8e-7; probability_of_voucher identical, 6.7533863251354007E-002).
Under the coordinator's amended rule (b) this run's net revenue is the budget target for the arms
solved in this container (elast5_85, uniq85).

## Settings

- Build `cf_fix2` (`code/cf_runs/build_cf_fix.sh` then `build_cf_fix2.sh`).
- Command, from `code/`:
  `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench DIAG_TAG=_fix2 DRUG_PRICE_START=1.0 sh cf_runs/cf_arm.sh null > cfarm_null_fix2.out 2>&1`
- `weight_on_child` 0.06, no budget clearing (`adjust_taxes` 0), drug supply elasticity 1.46.

## Checks (from `run.out`)

    VOUCHER CHECK PASS: arm ran at 6.7533863251354007E-002, benchmark 6.7533863251354007E-002
    DIST CHECK PASS: 5 passes, sweeps [81, 71, 74, 70, 72], largest final 4.83e-05 (rule 5e-05, at least 70 sweeps)

Exit pass 5: drug-market gap 5.19e-4 (rule 5e-3), change in the moments from pass 4 4.86e-5
(rule 1e-4). The budget is not cleared in this arm.

## Passes (`passes.txt`; changes against the benchmark constants b 0.081255, lambda_d 0.034611, h_1 0.0060789)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  1.0029  0.06753    +1.8%    +1.8%    -1.1%  2.94e-02  0.00e+00   789.8652  +1.53%
      2  1.0022  0.06753    -0.7%    -0.7%    -0.4%  9.44e-03  0.00e+00   789.4659  +0.34%
      3  0.9995  0.06753    -0.4%    -0.4%    -0.1%  7.47e-03  0.00e+00   789.3650  +0.05%
      4  0.9997  0.06753    -0.0%    -0.1%    -0.1%  6.86e-04  0.00e+00   789.3607  +0.03%
      5  1.0000  0.06753    -0.0%    -0.0%    -0.1%  5.19e-04  0.00e+00   789.3590  +0.03%

CEV is read off the coordinator's benchmark welfare curve (`results/reference/hf_omega_c_006`),
so the +0.03 per cent at exit is the no-policy run's distance from that benchmark, not a policy effect.

## The equilibrium (pass 5)

| outcome | this run | coordinator's null (`counterfactuals_cf_local/null_fix`) |
|---|---|---|
| drug use b | 0.08123638 | 0.081249 |
| SUD lambda_d | 0.034595368 | 0.034607 |
| homelessness h_1 | 0.0060751021 | 0.0060759 |
| drug price | 0.99995482 | 1.0000 |
| pi_V | 0.067533863 | 0.067534 |
| **net government revenue** | **6.0373408770945769** | 6.0370824602930142 |
| welfare (with childhood) | 789.35899 | 789.35794 |

(The coordinator's column is its no-policy row in `counterfactuals_cf_fix2/tf85/RESULT.md`, and its
final welfare from `null_fix/cf.log.gz`.)

**Budget target for this container: 6.0373408770945769**, 2.58e-4 above the coordinator's.
Full final statistics in `final.txt`.
