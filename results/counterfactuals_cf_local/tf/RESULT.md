> NOT FINAL, 25 September 18:10: the budget rule cleared against a target 0.23 below what the counterfactual binary gives with no policy change, so pi_V, the voucher coverage, homelessness and the CEV here all include a spurious surplus. See code/CALIBRATION_STATE.md, 25 September 18:10.

# Rationed Treatment First, voucher fixes in (a102cfaa), 25 September

Rationed TF at omega_c = 0.06 against the Housing First benchmark in code/cfarm_bench
(results/counterfactuals_cf_local/bench). Only voucher holders and lottery winners
are tested; a household fails if it uses (v > 0) or has SUD; detection 0.70, no false
positives; a caught holder loses the voucher and a caught winner does not get it,
both then excluded for three years on average; a holder the test misses keeps the
voucher and is paid. The drug price clears at supply elasticity 1.46
(drug_market_adjuster 0.1, start 0.86) and the budget clears through pi_V
(tax_system_type 3, printed in the log).

Built from a102cfaa, which closed the excluded-state range leak, the holder range
with exclusion off and the payment rule. Every TF run before that commit, including
the 24 September run in results/counterfactuals/treatment_first_rationed, carried
the leak.

## Checks

- Handover in the log: voucher_conditional_on_clean 1,
  increased_prob_of_voucher_if_homeless_and_addicted 1, probability_of_detection
  0.70, probability_of_false_positive 0, include_voucher_exclusion 1, adjust_taxes 1,
  weight_on_child 0.06, voucher probability 0.067533863251354 (the benchmark's),
  drug_price_start 0.86, drug_market_adjuster 0.1.
- Exit after pass 9 by the run's own rule, then `simulation_ended`: CF distance
  7.2e-05, 6.4e-05, 2.2e-04 over the last three passes against 5e-4; drug-market gap
  3.6e-03 against 5e-3 (demand 0.4012 at the pass-9 price 0.86208, against supply
  0.5013*0.86208^1.46 = 0.4037; the price then updated to 0.86065).
- The budget gap at exit is 1.06e-02: it was 1.5e-03 at pass 6 and widened as the
  price fell, and pi_V was still drifting down (0.10413, 0.10404, 0.10381, 0.10328).
  A fully closed budget would put pi_V slightly lower still.
- No-op check on the benchmark: the fixed build's block 1 is within the run-to-run
  noise of the old binary (CALIBRATION_STATE.md, 25 September 16:45).

## Passes (price = the price households faced in that pass)

| pass | price | b | lambda_d | h_1 | drug V | drug gap | budget gap | pi_V next |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.86000 | 0.065514 | 0.026961 | 0.0068064 | 0.4792 | 1.10e-01 | 1.47e-01 | 0.07491 |
| 2 | 0.86430 | 0.060340 | 0.026020 | 0.0066124 | 0.4431 | 5.47e-02 | 2.54e-01 | 0.08760 |
| 3 | 0.86858 | 0.057843 | 0.025212 | 0.0062827 | 0.4251 | 2.46e-02 | 1.76e-01 | 0.09642 |
| 4 | 0.87208 | 0.056005 | 0.024489 | 0.0060243 | 0.4116 | 1.57e-03 | 9.86e-02 | 0.10135 |
| 5 | 0.87232 | 0.055034 | 0.024048 | 0.0058696 | 0.4046 | 8.91e-03 | 5.43e-02 | 0.10406 |
| 6 | 0.87143 | 0.054422 | 0.023516 | 0.0057276 | 0.3983 | 1.72e-02 | 1.48e-03 | 0.10413 |
| 7 | 0.86971 | 0.054356 | 0.023443 | 0.0057154 | 0.3983 | 1.56e-02 | 1.85e-03 | 0.10404 |
| 8 | 0.86536 | 0.054402 | 0.023379 | 0.0057056 | 0.4003 | 8.20e-03 | 4.66e-03 | 0.10381 |
| 9 | 0.86208 | 0.054616 | 0.023245 | 0.0056875 | 0.4012 | 3.58e-03 | 1.06e-02 | 0.10328 |

## Result against the benchmark

| outcome | benchmark | TF | change |
|---|---|---|---|
| drug participation b | 0.081255 | 0.054616 | -32.8% |
| SUD lambda_d | 0.034611 | 0.023245 | -32.8% |
| homelessness h_1 | 0.0060789 | 0.0056875 | -6.4% |
| SMI prevalence | 0.04822 | 0.048041 | -0.4% |
| SMI share of homeless | 0.25453 | 0.22218 | -12.7% |
| drug quantity V | 0.50135 | 0.40124 | -20.0% |
| drug price (faced in pass 9) | 1.0 | 0.86208 | -13.8% |
| pi_V (in force in pass 9) | 0.067534 | 0.10381 | +53.7% |
| eligibles getting a voucher | 0.27244 | 0.32762 | +20.3% |

## Welfare (verbatim)

    CEV from the saved benchmark curve: target=   790.91875843267485       x=   4.7556941135798850E-002
