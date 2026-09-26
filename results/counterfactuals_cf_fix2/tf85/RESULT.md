# Treatment First, 85 per cent detection: long-run steady state on the corrected build

26 September, 12:44 to 17:08 UTC. CONVERGED: every stopping rule was met at pass 7, and
all the checks pass. This is ONE equilibrium, the one at the pass the run exited on.

## Settings

- Build `cf_fix2` (`code/cf_runs/build_cf_fix.sh` then `build_cf_fix2.sh`). Against the
  tracked source it neutralises the hidden labour-tax warm start, solves the population
  distribution fully every pass (at least 70 sweeps, then 5e-5), clears the budget to 1e-3
  and updates pi_V with a step of 0.12 of the gap that ignores pass 1 and halves on each
  sign change (it halved once, at pass 3).
- Command: `BUILD=cf_fix2 SEED_FROM=seed_tf_tdm85 PDET=0.85 PV_START=0.082
  DRUG_PRICE_START=0.8647 NET_TARGET=6.0370824602930142 sh tightdist_cf_arm.sh tf`
  (the scratchpad original of `code/cf_runs/cf_arm.sh`).
- Voucher conditional on being clean, detection 0.85, no false positives, exclusion on,
  `weight_on_child` 0.06, drug supply elasticity 1.46. pi_V clears the budget; the labour
  tax does not move.
- Budget target 6.0370824602930142: the net revenue of the no-policy run on the same
  machinery, which reproduces the benchmark (`../../counterfactuals_cf_local/null_fix`).

## Checks (from `run.out`)

    TARGET CHECK PASS: cleared against 6.0370824602930000
    DIST CHECK PASS: 7 passes, sweeps [70, 71, 70, 70, 70, 70, 70], largest final 4.57e-05

Exit pass 7: budget gap -0.00037 (rule 1e-3), drug-market gap 3.5e-4 (rule 5e-3), change
in the moments from pass 6 4.9e-6 (rule 1e-4).

## Passes (`passes.txt`; changes against the benchmark)

    pass  price    pi_V     b(chg)   SUD(chg)  h_1(chg)  drug gap  budget gap  welfare    CEV
      1  0.8667  0.08200   -28.8%   -29.4%    +5.1%  2.04e-02  9.13e-02   790.1816  +2.48%
      2  0.8667  0.08200   -30.4%   -31.1%    +5.1%  1.23e-04  3.79e-03   789.9260  +1.71%
      3  0.8667  0.08245   -30.4%   -31.0%    +5.0%  5.60e-05  8.61e-03   789.8777  +1.57%
      4  0.8667  0.08194   -30.4%   -31.0%    +5.3%  1.26e-04  4.89e-03   789.8566  +1.50%
      5  0.8669  0.08164   -30.2%   -30.9%    +5.5%  1.17e-03  2.54e-03   789.8394  +1.45%
      6  0.8672  0.08149   -30.2%   -30.9%    +5.5%  9.00e-04  1.35e-03   789.8322  +1.43%
      7  0.8674  0.08141   -30.2%   -30.8%    +5.6%  3.54e-04  3.71e-04   789.8275  +1.42%

The budget gaps are absolute values. Pass 1 is inflated by the parent-share start-up
artefact and is not used for the pi_V update.

## The equilibrium (pass 7) against the no-policy run (`final.txt`)

| outcome | Treatment First 85% | no policy | change |
|---|---|---|---|
| drug use b | 0.056717 | 0.081249 | -30.2% |
| SUD lambda_d | 0.023935 | 0.034607 | -30.8% |
| homelessness h_1 | 0.0064189 | 0.0060759 | +5.6% |
| drug price | 0.8674 | 1.0000 | -13.3% |
| pi_V, voucher probability | 0.081411 | 0.067534 | +20.5% |
| households holding a voucher | 0.06309 | 0.06231 | +1.3% |
| eligibles getting a voucher | 0.2771 | 0.2725 | +1.7% |
| treatment take-up | 0.2929 | 0.2501 | +17.2% |
| SUD share of the homeless | 0.2148 | 0.1922 | +11.8% |
| SMI share of the homeless | 0.2319 | 0.2545 | -8.9% |
| employed share of the homeless | 0.2257 | 0.2142 | +5.4% |
| voucher spending | 0.69234 | 0.68398 | +1.2% |
| food stamps | 0.23468 | 0.23852 | -1.6% |
| drug-test cost | 0.00120 | 0 | |
| net government revenue | 6.03671 | 6.03708 | -0.00037 |

## Welfare

- CEV against the benchmark's welfare curve: **+1.416 per cent** (`average_welfare_with_childhood`
  789.82747). The no-policy run itself is at +0.027 per cent, so the gain net of it is
  **+1.39 per cent**.
- Split against the no-policy run, in utils (1 per cent CEV is about 0.338 here): childhood
  utility +0.237, the discounted adult part +0.233, total +0.470. About half of the gain
  comes through childhood and half through adulthood.

## Notes

- pi_V is the value the pass-7 equilibrium was solved at. The run applied one more step
  after it (the log's last print is 0.081389) and then exited, so that value was never
  solved.
- This run's directory, `code/cfarm_tf_fix2_85`, is the terminal steady state for the
  transition and is kept.
