# Treatment First, 85 per cent detection, drug supply elasticity 5: long-run steady state

26 September 19:31 to 27 September 01:57 UTC, remote container. CONVERGED: every stopping rule
met at pass 12, all checks pass. ONE equilibrium, the one at the pass the run exited on.

## Settings

- Build `cf_fix2` (`code/cf_runs/build_cf_fix.sh` then `build_cf_fix2.sh`).
- Command, from `code/`:
  `OMP_NUM_THREADS=2 BUILD=cf_fix2 SEED_FROM=bench PDET=0.85 SUPPLY_ELAST=5 DIAG_TAG=_elast5_85 PV_START=0.082 DRUG_PRICE_START=0.94 NET_TARGET=6.0373408770945769 sh cf_runs/cf_arm.sh tf > cfarm_tf_elast5_85.out 2>&1`
- Voucher conditional on being clean, detection 0.85, no false positives, exclusion on,
  `weight_on_child` 0.06. pi_V clears the budget; the labour tax does not move.
- Drug supply elasticity 5 (curvature 1.2), with the supply level refitted in the arm's own copy
  so the price is 1 at the benchmark quantity:
  `supply refitted: benchmark quantity 0.501287003268, shifter 1.604797495253 -> 1.148107915147, price there 1.000000000000 (old shifter would give 1.397776)`
- **Benchmark and target are this container's own.** The STAGE 1 benchmark here ends at welfare
  789.34923420870734, 3.8e-7 (relative) from the coordinator's 789.34893176009462, with the same
  pi_V. The budget target 6.0373408770945769 is this container's no-policy run
  (`../null_remote`), 2.58e-4 above the coordinator's 6.0370824602930142.

## Checks (from `run.out.gz`)

    HANDOVER voucher probability:   5.9999998658895493E-002 ->   8.2000000000000003E-002
    tf: voucher probability first printed 8.2000000000000003E-002, last 8.1483805601104034E-002 (benchmark 6.7533863251354007E-002); it is the budget instrument and moves
    HANDOVER drug_supply_elasticity:   1.4600000381469727      ->   5.0000000000000000
       drug_supply_curvature is now   1.2000000000000000
    TARGET CHECK PASS: cleared against 6.0373408770949997
    DIST CHECK PASS: 12 passes, sweeps [70, 70, 70, 70, 70, 72, 70, 72, 70, 70, 70, 76], largest final 4.88e-05 (rule 5e-05, at least 70 sweeps)

Exit pass 12: budget gap -6.08e-4 (rule 1e-3), drug-market gap 1.23e-3 (rule 5e-3), change in
the moments from pass 11 5.85e-5 (rule 1e-4). The price walked down at the 0.5 per cent cap
for passes 1-9, which is why the run took 12 passes.

## Passes (`passes.txt`; changes against the benchmark)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.9353  0.08200   -58.1%   -58.6%    -2.8%  1.14e-01  4.26e-02   791.0367  +5.13%
      2  0.9306  0.08200   -58.2%   -58.7%    -2.3%  1.09e-01  1.06e-03   790.8472  +4.53%
      3  0.9260  0.08187   -57.4%   -57.9%    -1.9%  1.00e-01  5.52e-03   790.7704  +4.29%
      4  0.9213  0.08121   -56.3%   -56.8%    -1.5%  8.95e-02  9.75e-04   790.7111  +4.11%
      5  0.9167  0.08127   -55.1%   -55.6%    -1.2%  7.93e-02  1.46e-03   790.6711  +3.98%
      6  0.9122  0.08136   -51.0%   -51.5%    -0.6%  4.49e-02  2.20e-03   790.5988  +3.76%
      7  0.9076  0.08149   -50.5%   -51.0%    -0.5%  3.77e-02  3.87e-03   790.5755  +3.69%
      8  0.9031  0.08137   -47.1%   -47.6%    +1.2%  2.33e-02  4.62e-03   790.3812  +3.09%
      9  0.8985  0.08144   -46.3%   -46.8%    +1.5%  1.54e-02  1.71e-03   790.3350  +2.95%
     10  0.8959  0.08147   -45.1%   -45.7%    +2.0%  6.56e-03  1.16e-03   790.2927  +2.82%
     11  0.8950  0.08149   -44.8%   -45.4%    +2.1%  2.31e-03  1.93e-04   790.2769  +2.77%
     12  0.8945  0.08149   -44.8%   -45.4%    +2.1%  1.23e-03  6.08e-04   790.2747  +2.77%

The budget gaps are absolute values.

## The equilibrium (pass 12)

Against the benchmark (b 0.081255, lambda_d 0.034611, h_1 0.0060789):

| outcome | level | change against the benchmark |
|---|---|---|
| drug use b | 0.044850 | -44.8% |
| SUD lambda_d | 0.018902 | -45.4% |
| homelessness h_1 | 0.0062071 | +2.1% |
| drug price | 0.89450 | |
| pi_V, voucher probability | 0.081488 | |
| budget gap (net revenue minus target) | -6.08e-4 against this container's 6.03734; -3.49e-4 against the coordinator's 6.03708 | |
| drug-market gap | 1.23e-3 | |
| welfare (with childhood) | 790.2747 | |
| CEV against the benchmark's welfare curve | **+2.77 per cent** | |

Against this container's no-policy run (`final.txt`):

| outcome | TF 85%, elasticity 5 | no policy | change |
|---|---|---|---|
| drug use b | 0.044850 | 0.081236 | -44.8% |
| SUD lambda_d | 0.018902 | 0.034595 | -45.4% |
| homelessness h_1 | 0.0062071 | 0.0060751 | +2.2% |
| drug price | 0.8945 | 1.0000 | -10.6% |
| pi_V | 0.081488 | 0.067534 | +20.7% |
| households holding a voucher | 0.06377 | 0.06231 | +2.4% |
| eligibles getting a voucher | 0.2810 | 0.2725 | +3.1% |
| treatment take-up | 0.2973 | 0.2500 | +18.9% |
| SUD share of the homeless | 0.1917 | 0.1921 | -0.2% |
| SMI share of the homeless | 0.2358 | 0.2545 | -7.4% |
| employed share of the homeless | 0.2308 | 0.2142 | +7.8% |
| voucher spending | 0.70179 | 0.68397 | +2.6% |
| food stamps | 0.23307 | 0.23852 | -2.3% |
| drug-test cost | 0.00122 | 0 | |
| net government revenue | 6.03673 | 6.03734 | -0.00061 |

## Welfare

- CEV against the benchmark's welfare curve (`cf_runs/cev.py`, which reads the coordinator's
  `results/reference/hf_omega_c_006` curve): **+2.766 per cent** (welfare 790.2747). This
  container's no-policy run is at +0.030 per cent, so the gain net of it is **+2.74 per cent**.
- Split against the no-policy run, in utils: childhood utility +0.676, the discounted adult part
  +0.240, total +0.916. About three quarters of the gain comes through childhood.

## Notes

- pi_V is the value the pass-12 equilibrium was solved at (0.081488364, the last print inside the
  pass). The run applied one more step after it (the log's last print is 0.081483806) and then
  exited, so that value was never solved.
