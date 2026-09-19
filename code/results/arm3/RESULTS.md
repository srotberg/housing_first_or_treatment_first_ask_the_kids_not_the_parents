# ARM 3 -- TREATMENT FIRST

**CONVERGED**, block 22, run completed cleanly (exit 0, `simulation_ended`).

    weight_on_child 0.055 (the benchmark's own)   internalise_homelessness_cost 0
    voucher_conditional_on_clean 1   include_voucher_exclusion 1
    probability_of_detection 0.70   probability_of_false_positive 0.0
    increased_prob_of_voucher_if_homeless_and_addicted 0
    kappa_x 0.8139   adult_taxes 1   drug price cleared at eps_s = 1.46

Warm started at price 0.7700 and pi_v 0.068274, both guesses. The FIRST attempt
started at 0.95 and would have needed ~53 blocks of clipped walking; it was
abandoned after 3 blocks and restarted. Its log is kept at
`$S/arm3_partial_p095.log` because it holds the only elasticity measurement in
that price region.

## THE THREE LIVE RULES

    CF moments   2.3197e-04   (rule 5e-4)    ok
    budget       7.1691e-03   (rule 2.5e-2)  ok
    drug gap    -4.3699e-03   (rule 5e-3)    ok

Rental, housing and inheritance are identically 0.0 every loop -- the rent is
pinned at 1 and supply is set equal to demand. THREE rules were checked, not six.

## THE EQUILIBRIUM, AGAINST THE BENCHMARK

| | benchmark (n90) | arm 3 TF | change |
|---|---|---|---|
| b, total drug users | 0.081813 | **0.047121** | **-42.4%** |
| lambda_d, SUD | 0.033609 | **0.019133** | **-43.1%** |
| h_1, homelessness | 0.0064583 | **0.0067903** | **+5.1%** |
| drug quantity V | 0.494427 | 0.382458 | -22.6% |
| drug price | 1.000000 | 0.842220 | -15.8% |
| pi_v | -- | 0.070288 | (arm 1: 0.068989) |
| average_welfare_with_childhood | 791.39464 | 791.96771 | +0.5731 |

## Q3: WELFARE. CEV = +1.646 PER CENT OF CONSUMPTION AND HOUSING

The model's own number, `CEV from the saved benchmark curve: target=791.96771
x=+0.016457573`. **This one is legitimately comparable to the benchmark**,
unlike arms 1 and 2, because omega_c stays at the benchmark's 0.055.

**THE ENTIRE GAIN IS THE CHILDHOOD PHASE.**

| | benchmark | arm 3 | change | share of the gain |
|---|---|---|---|---|
| total | 791.3946 | 791.9677 | +0.5731 | 100% |
| childhood phase | 449.1085 | 449.6984 | **+0.5899** | **+103%** |
| adult phase (discounted) | 342.2861 | 342.2693 | -0.0168 | -3% |

In CEV terms: childhood +1.694%, adult -0.048%.

"Childhood" and "adult" are the two PHASES OF ONE LIFE, not two populations:
the measure is `own_childhood + beta^25 * adult_value`, verified because
adult(disc)/adult(undisc) = 0.25316 = beta^25 to five digits.

**THE CHANNEL IS RESOURCE DIVERSION, and the code makes it exact.** The child's
flow argument is `housing(...) * c_util^(...) * b_shifter(1,housing_size)^(...)`
-- `b_shifter` ALONE, with no term in the parent's drug purchases, where the
parent's own term carries `(b_shifter + frac_spent*total_consumption/price)`.
Total consumption splits into goods and drugs; the parent values both and the
child values only the goods half. Every unit diverted to drugs is a unit out of
the child's consumption with no offsetting benefit.

That channel is large enough to win DESPITE the child's housing getting worse
(homelessness up, and the child bears kappa_x*H too).

**The adult phase is a net of opposing forces, not nothing happening:**
fewer children inherit the earnings penalty (+0.115 utils, estimated by valuing
the 1.12pp fall in penalised births at the welfare curve's W(0)-W(-0.24) =
10.205 utils), against the drug utility forgone, the voucher option destroyed by
conditionality, higher homelessness and the testing bill (-0.132 residual). Only
the total and the flow/adult split are MEASURED; the split inside the adult
component is inferred.

## MORE CHILDREN ARE BORN INTO HOMELESSNESS

| | born to a homeless parent | clean-street | SUD-street |
|---|---|---|---|
| benchmark | 0.3012% | 0.1791% | 0.1222% |
| arm 1 (the optimum) | 0.2173% | 0.1593% | 0.0580% |
| arm 3 TF | **0.3286%** | 0.1850% | **0.1436%** |

+9.1% against the benchmark, **+51.2% against the optimum**, and concentrated in
the worst cell: born to a parent both homeless AND disordered, +17.5% against
the benchmark where the optimum more than halves it.

This is the parent's state AT BIRTH. Cumulative childhood exposure is not
available -- `homelessness_mass_by_age` exists in the code and is never printed.

Homelessness decomposed: addicted-homeless -3.0%, clean-homeless **+7.0%**.

## OPEN: THE EXCLUSION STATE IS EMPTY AND THAT IS NOT UNDERSTOOD

    DIAG voucher-state mass: none= 47.674  holding= 3.382  excluded= 0.0000000

at log line 7141 of 7345 -- the CONVERGED state, not block 1.
`include_voucher_exclusion` was handed over as 1 and verified in the log, but no
household ends up barred. **So the three-period exclusion the author specified is
not binding**, and the 42 per cent fall in drug use is produced by the voucher
CONDITIONALITY and by removing the Housing First prioritisation of homeless
addicts, not by the bar.

This does not affect convergence and it does not change any number above. It
changes what the numbers MEAN, so it has to be diagnosed before the mechanism is
written up.
