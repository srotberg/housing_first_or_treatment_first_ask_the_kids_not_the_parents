# Treatment First, 85 per cent detection, FROM A DIFFERENT START: a uniqueness check

27 September, 09:45 to 20:26 UTC in two legs (a container restart in between), remote container.
CONVERGED: every stopping rule met at pass 7 of the second leg, all checks pass. ONE equilibrium,
the one at the pass the run exited on. **It is the coordinator's TF 85 equilibrium
(`../tf85`) to four or five significant figures.**

## Settings

- Build `cf_fix2` (`code/cf_runs/build_cf_fix.sh` then `build_cf_fix2.sh`).
- Leg 1, the different start (`../uniq85_partial`), from `code/`:
  `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench PDET=0.85 DIAG_TAG=_uniq85 PV_START=0.075 DRUG_PRICE_START=0.90 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf > cfarm_tf_uniq85.out 2>&1`
  The coordinator's run started at pi_V 0.082 and price 0.8647, from TF 85's own distribution; this
  one at 0.075 and 0.90 from the benchmark's. It walked to pi_V 0.08150, price 0.8673 in 12 passes
  (b -30.2 per cent, moments change 1.8e-5, drug gap 7.4e-4, budget gap 1.7e-3) and was killed by
  the container restart in pass 13.
- Leg 2, continued from leg 1's last printed values (the arm script always restarts the
  distribution from the benchmark's, so a restart re-solves it in full):
  `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench PDET=0.85 DIAG_TAG=_uniq85 PV_START=0.081470 DRUG_PRICE_START=0.8673 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf > cfarm_tf_uniq85.out 2>&1`
- Voucher conditional on being clean, detection 0.85, no false positives, exclusion on,
  `weight_on_child` 0.06, drug supply elasticity 1.46. pi_V clears the budget.
- This container's benchmark (3.8e-7 relative from the coordinator's) and its own budget target
  6.0373408770945769 (`../null_remote`), 2.58e-4 above the coordinator's.

## Checks (leg 2, from `run.out.gz`)

    HANDOVER voucher probability:   5.9999998658895493E-002 ->   8.1470000000000001E-002
    tf: voucher probability first printed 8.1470000000000001E-002, last 8.1378732608369531E-002 (benchmark 6.7533863251354007E-002); it is the budget instrument and moves
    TARGET CHECK PASS: cleared against 6.0373408770949997
    DIST CHECK PASS: 7 passes, sweeps [70, 70, 70, 74, 70, 75, 71], largest final 4.77e-05 (rule 5e-05, at least 70 sweeps)

Exit pass 7: budget gap -2.60e-4 (rule 1e-3), drug-market gap 5.26e-4 (rule 5e-3), change in the
moments from pass 6 1.67e-5 (rule 1e-4).

## Passes

Leg 1 (`../uniq85_partial/passes.txt`):

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8955  0.07500   -35.7%   -36.3%    +7.1%  1.24e-01  1.34e-01   790.0367  +2.04%
      2  0.8910  0.07500   -42.0%   -42.6%    +6.7%  1.97e-01  5.41e-02   789.8782  +1.57%
      3  0.8866  0.08149   -42.3%   -42.9%    +3.4%  1.91e-01  4.38e-04   790.1230  +2.31%
      4  0.8821  0.08154   -35.6%   -36.2%    +4.4%  1.03e-01  8.22e-03   789.9986  +1.93%
      5  0.8777  0.08253   -33.3%   -33.9%    +4.3%  5.25e-02  5.57e-03   789.9826  +1.88%
      6  0.8733  0.08219   -33.0%   -33.6%    +4.6%  4.34e-02  6.54e-03   789.9494  +1.78%
      7  0.8690  0.08180   -32.8%   -33.3%    +4.9%  3.36e-02  4.05e-03   789.9246  +1.71%
      8  0.8683  0.08156   -30.5%   -31.1%    +5.4%  4.28e-03  1.06e-03   789.8550  +1.50%
      9  0.8671  0.08159   -30.4%   -31.1%    +5.4%  3.05e-03  2.30e-03   789.8468  +1.47%
     10  0.8669  0.08156   -30.3%   -31.0%    +5.4%  4.35e-04  2.27e-03   789.8401  +1.45%
     11  0.8670  0.08152   -30.2%   -30.9%    +5.5%  8.96e-04  1.66e-03   789.8339  +1.44%
     12  0.8673  0.08150   -30.2%   -30.9%    +5.5%  7.37e-04  1.72e-03   789.8319  +1.43%

Leg 2 (`passes.txt`):

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8686  0.08147   -29.0%   -29.7%    +5.3%  1.34e-02  9.48e-02   790.1623  +2.42%
      2  0.8683  0.08147   -30.5%   -31.2%    +5.2%  4.07e-03  7.52e-03   789.9068  +1.65%
      3  0.8673  0.08237   -31.4%   -32.0%    +4.9%  1.00e-02  1.08e-02   789.9041  +1.65%
      4  0.8672  0.08172   -30.4%   -31.0%    +5.4%  1.03e-03  2.59e-03   789.8517  +1.49%
      5  0.8669  0.08157   -30.3%   -31.0%    +5.4%  7.71e-04  2.31e-03   789.8416  +1.46%
      6  0.8671  0.08143   -30.2%   -30.9%    +5.6%  7.44e-04  5.96e-04   789.8294  +1.42%
      7  0.8673  0.08139   -30.2%   -30.9%    +5.6%  5.26e-04  2.60e-04   789.8270  +1.41%

The budget gaps are absolute values.

## The equilibrium (leg 2, pass 7) against the coordinator's

| outcome | this run | coordinator's TF 85 (`../tf85`) |
|---|---|---|
| drug use b | 0.056711 (-30.2%) | 0.056717 (-30.2%) |
| SUD lambda_d | 0.023928 (-30.9%) | 0.023935 |
| homelessness h_1 | 0.0064196 (+5.6%) | 0.0064189 |
| drug price | 0.86726 | 0.8674 |
| pi_V | 0.081394 | 0.081411 |
| budget gap | -2.60e-4 against 6.03734 (this container); -1.8e-6 against 6.03708 | -3.7e-4 |
| drug-market gap | 5.26e-4 | 3.5e-4 |
| welfare (with childhood) | 789.82705 | 789.82747 |
| CEV against the benchmark's curve | **+1.415 per cent** | +1.416 per cent |

Percentages are against the benchmark (b 0.081255, lambda_d 0.034611, h_1 0.0060789). The
differences are of the size of the two containers' benchmark difference (3.8e-7 in welfare) and
their budget targets (2.58e-4): **no sign of a second equilibrium from this start.**

Against this container's no-policy run (`final.txt`): b -30.2%, h_1 +5.7%, treatment take-up
+17.1%, SUD share of the homeless +11.8%, welfare split childhood +0.236 and adult part +0.233
utils (the coordinator's: +0.237 and +0.233).

## Notes

- pi_V is the value the pass-7 equilibrium was solved at (0.081394348, the last print inside the
  pass). The run applied one more step (last print 0.081378733) and then exited, so that value was
  never solved.
