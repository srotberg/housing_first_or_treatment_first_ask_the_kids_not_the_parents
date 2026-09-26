> SUPERSEDED 26 September by ../tf_tight70 (the budget closed to 2e-3); this run stopped with a gap of 0.021.

> UNDER REVIEW, 25 September 21:40: the author finds the welfare result (CEV about zero, childhood -0.01 against the no-policy run) too small to be credible next to the 19 September run (children +0.78). Do not use until the welfare split and the reruns of the 19 September design (CALIBRATION_STATE.md) explain the gap.

# Rationed Treatment First, like-for-like budget, 25 September

Rationed TF at omega_c = 0.06 on the fixed voucher model (a102cfaa), with the drug
price clearing at supply elasticity 1.46 and the budget clearing through pi_V
against the LIKE-FOR-LIKE target: the net revenue the counterfactual binary gives
with no policy change (the null arm, 6.2647988599575077), not the benchmark's saved
6.038875634967. The author, 25 September: "You need to rerun the rationed tf with
the correct budget and budget clearing". The earlier run against the saved target
is kept as RESULT_saved_target.md; it credited TF with a 0.226 surplus that exists
with no policy at all.

Only voucher holders and lottery winners are tested; a household fails if it uses
(v > 0) or has SUD; detection 0.70, no false positives; a caught holder loses the
voucher and a caught winner does not get it, both then excluded for three years on
average; a holder the test misses keeps the voucher and is paid.

## Checks

- `TARGET CHECK PASS: cleared against 6.2647988599579998` (the arm's own copy of
  govt_revenues_to_use_in_testsbaseline_benchmark.dat, kept here as
  budget_target_used.dat; cfarm_bench's file still reads 6.038875634967).
- Handover as in the earlier run: test 1, applicant switch 1, detection 0.70, false
  positives 0, exclusion 1, adjust_taxes 1, omega_c 0.06, pi_V start 0.067534
  (the benchmark's), drug_price_start 0.86, drug_market_adjuster 0.1;
  tax_system_type 3 in the log.
- Exit after pass 10 by the run's own rule, then `simulation_ended`: CF distance
  1.39e-04 against 5e-4, drug-market gap 4.35e-03 against 5e-3, budget gap 2.09e-02
  against 2.5e-02. At exit TF spends 0.021 more than the target and pi_V was still
  easing down (0.07295, 0.07154, 0.07050).

## Passes (price = the price households faced in that pass)

| pass | price | b | lambda_d | h_1 | drug V | drug gap | budget gap | pi_V next |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.86000 | 0.065516 | 0.026963 | 0.0068064 | 0.4792 | 1.09e-01 | 7.86e-02 | 0.06360 |
| 2 | 0.86430 | 0.064816 | 0.027423 | 0.0069711 | 0.4761 | 1.01e-01 | 1.16e-01 | 0.06940 |
| 3 | 0.86862 | 0.061618 | 0.026845 | 0.0068419 | 0.4519 | 6.28e-02 | 8.10e-02 | 0.07345 |
| 4 | 0.87296 | 0.060589 | 0.026362 | 0.0067325 | 0.4414 | 4.35e-02 | 3.67e-02 | 0.07529 |
| 5 | 0.87733 | 0.060043 | 0.026168 | 0.0066847 | 0.4349 | 2.99e-02 | 1.97e-02 | 0.07627 |
| 6 | 0.88172 | 0.059326 | 0.025778 | 0.0066074 | 0.4266 | 1.35e-02 | 9.49e-03 | 0.07580 |
| 7 | 0.88534 | 0.057921 | 0.025420 | 0.0065690 | 0.4154 | 6.23e-03 | 2.55e-02 | 0.07452 |
| 8 | 0.88419 | 0.058266 | 0.025240 | 0.0065668 | 0.4149 | 5.78e-03 | 3.14e-02 | 0.07295 |
| 9 | 0.88188 | 0.058869 | 0.025000 | 0.0065943 | 0.4161 | 1.76e-03 | 2.82e-02 | 0.07154 |
| 10 | 0.88117 | 0.058775 | 0.024868 | 0.0066198 | 0.4138 | 4.35e-03 | 2.09e-02 | 0.07050 |

## Result

Against the saved benchmark, and against the null arm (the same binary with no
policy change, converged; CALIBRATION_STATE.md, 25 September 18:20).

| outcome | benchmark | null arm | TF | vs benchmark | vs null |
|---|---|---|---|---|---|
| drug participation b | 0.081255 | 0.080903 | 0.058775 | -27.7% | -27.4% |
| SUD lambda_d | 0.034611 | 0.034513 | 0.024868 | -28.2% | -27.9% |
| homelessness h_1 | 0.0060789 | 0.0060470 | 0.0066198 | +8.9% | +9.5% |
| SMI prevalence | 0.04822 | 0.048226 | 0.048057 | -0.3% | -0.4% |
| SMI share of homeless | 0.25453 | 0.25484 | 0.23917 | -6.0% | -6.1% |
| drug quantity V | 0.50135 | 0.50025 | 0.4138 | -17.5% | -17.3% |
| drug price (faced in pass 10) | 1.0 | 1.00014 | 0.88117 | -11.9% | -11.9% |
| pi_V (in force in pass 10) | 0.067534 | 0.067534 | 0.07154 | +5.9% | +5.9% |
| eligibles getting a voucher | 0.27244 | 0.27069 | 0.25805 | -5.3% | -4.7% |
| voucher spending | 0.68388 | 0.67341 | 0.64279 | -6.0% | -4.5% |

pi_V rises while coverage and spending fall: under TF a caught winner is refused
and a caught holder is removed, so a higher offer rate is needed for each voucher
in use.

## Welfare (verbatim)

    CEV from the saved benchmark curve: target=   789.40061213742513       x=   1.5146041980787629E-003

The null arm's own CEV against the same curve is 1.4026510672890576E-003, so TF's
welfare effect net of that offset is about +0.01 per cent: zero at this precision.
