> NOT FIRM, 26 September 02:30: the run stopped at the bottom of a pi_V cycle, not at the fixed point (CALIBRATION_STATE.md, 26 September 02:30). The same settings stopped at CEV +0.70 per cent in ../tf_childsplit70. Do not use.

# Rationed TF, 70 per cent detection, budget closed to 2e-3, 26 September

Same build (code/cf_tightbudget: stopping_rule_govt_budget 2.0e-3, nothing else) and
same like-for-like target (6.2647988599575077) as ../tf_tight85; detection 0.70.
Warm start from the earlier 70 per cent split run: price 0.8776, pi_V 0.0753.

## Checks at exit (pass 15)

- `TARGET CHECK PASS: cleared against 6.2647988599579998`; `simulation_ended`.
- Budget gap 0.00171 (rule 0.002), drug-market gap 0.00049 (rule 0.005), CF moments
  9.04e-05 (rule 5e-4).

## Result against the benchmark

| outcome | benchmark | TF 70% | change |
|---|---|---|---|
| drug participation b | 0.081255 | 0.059178 | -27.2% |
| SUD lambda_d | 0.034611 | 0.024884 | -28.1% |
| homelessness h_1 | 0.0060789 | 0.006705 | +10.3% |
| drug quantity V | 0.50135 | 0.41495 | -17.2% |
| drug price (last) | 1.0 | 0.87805 | -12.2% |
| pi_V (last) | 0.067534 | 0.068739 | +1.8% |
| eligibles holding a voucher | 0.27244 | 0.25115 | -7.8% |
| voucher spending | 0.68388 | 0.62581 | -8.5% |
| SMI prevalence | 0.04822 | 0.048038 | -0.4% |
| SMI share of homeless | 0.25453 | 0.24201 | -4.9% |

## Welfare

    CEV from the saved benchmark curve: target=   789.24748217305000       x=  -2.9726834579012545E-003

CEV -0.30 per cent (-0.44 net of the no-policy run's +0.14). Against the no-policy
run: lifetime -0.149, childhood -0.113, adult (discounted) -0.036.
