# The two arms that converged before the secant guard

`tf_rationed` and `universal_hf` as they landed on model `6c8b8d6c24`, kept so
that re-running them on the guarded source is a TEST rather than a replacement.

The guard (commit c3990c2e) damps the drug price update when the secant would
overshoot. It changes no equilibrium condition: the fixed point is still
`implied_price == price_faced` inside `stopping_rule_drug_market`, and only the
path there changes. So these two arms should land where they landed before, and
if they do not, the claim in that commit is wrong and the difference is the
evidence.

What they landed on, for the diff:

| | tf_rationed | universal_hf |
|---|---|---|
| homelessness rate | 0.01681 | 0.00009 |
| participation rate | 0.07635 | 0.11158 |
| SUD rate | 0.03186 | 0.04990 |
| CEV of newborns | -0.04282 | +0.46878 |
| unemployment rate | 0.04870 | 0.05280 |
| tax change at benchmark income | -0.03946 | +0.00607 |
| treatment take-up given a SUD | 0.22283 | 0.17422 |
| average age of drug users | 36.825 | 34.153 |
| final `distance_drug_market` | 7.13e-4 | 5.37e-4 |
| loops to converge | 39 | 23 |

`universal_tf` is not here because it never converged: 47 loops with the price
oscillating between 1.02 and 1.20 and `distance_drug_market` growing to 0.520.
That is what the guard is for.
