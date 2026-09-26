> NOT FIRM, 26 September 02:30: the run stopped at the bottom of a pi_V cycle, not at the fixed point (CALIBRATION_STATE.md, 26 September 02:30). The same settings stopped at CEV +0.70 per cent in ../tf_childsplit70. Do not use.

# Rationed TF, 85 per cent detection, budget closed to 2e-3, 26 September

The author, 25 September: "finish both and give me firm numbers for 70% and 85%".
Rationed TF (test holders and lottery winners, detection 0.85, no false positives,
three-year exclusion, uncaught holders paid) on the build copy code/cf_tightbudget:
today's source with stopping_rule_govt_budget 2.5e-2 -> 2.0e-3 and nothing else
(three builds, 7 warnings / 0 errors each). Budget cleared through pi_V against the
like-for-like target 6.2647988599575077 (the no-policy run's net revenue). Warm start
from the earlier 85 per cent run: price 0.8708, pi_V 0.0711.

## Checks at exit (pass 14)

- `TARGET CHECK PASS: cleared against 6.2647988599579998`; `simulation_ended`.
- Budget gap 0.00192 (rule 0.002), drug-market gap 0.00276 (rule 0.005), CF
  moments 3.65e-05 (rule 5e-4).

## Result against the benchmark

| outcome | benchmark | TF 85% | change |
|---|---|---|---|
| drug participation b | 0.081255 | 0.058914 | -27.5% |
| SUD lambda_d | 0.034611 | 0.024712 | -28.6% |
| homelessness h_1 | 0.0060789 | 0.0067911 | +11.7% |
| drug quantity V | 0.50135 | 0.41365 | -17.5% |
| drug price (last) | 1.0 | 0.87495 | -12.5% |
| pi_V (last) | 0.067534 | 0.070164 | +3.9% |
| eligibles holding a voucher | 0.27244 | 0.25034 | -8.1% |
| voucher spending | 0.68388 | 0.62408 | -8.7% |
| SMI prevalence | 0.04822 | 0.048031 | -0.4% |
| SMI share of homeless | 0.25453 | 0.23903 | -6.1% |

## Welfare

    CEV from the saved benchmark curve: target=   789.16648627147094       x=  -5.3372202772323293E-003

CEV -0.53 per cent; the no-policy run's own CEV against the same curve is +0.14 per
cent, so net of it -0.67. Against the no-policy run: lifetime -0.230, of which
childhood -0.206 and adult (discounted) -0.024. The loss is children's, through fewer
vouchers and more homelessness, not adults' drug utility.
