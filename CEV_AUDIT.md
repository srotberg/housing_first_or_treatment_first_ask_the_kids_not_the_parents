# The welfare comparison, audited

Written 10 September, after the author asked why universal Housing First beats
universal Treatment First when both drive homelessness to zero, and then said
"i wonder if maybe you have an error in the computation / you should double
check the code".

## What the metric is

`calculate_welfare_gains` loads the benchmark's POLICY functions and its
stationary distribution from the `baseline_benchmark` files and bisects x on

    E_{bench newborns}[ V_comparison(x) ]  =  E_{arm newborns}[ V_arm ]

`V_comparison` is built by `compute_value_function_comparison`, which walks the
benchmark's own policies backward through life with non-drug consumption scaled
by (1+x). x is the reported consumption equivalent.

The structure is sound. Both sides are mass-weighted MEANS over their own
newborn distributions, so the normalisations agree, and the child penalty is
counted on the arm's side through the newborn distribution: a newborn of a
parent with the disorder is placed in the penalised class and carries a lower
value function for life. That happens whatever `weight_on_child` is, which is
why omega_c governs BEHAVIOUR and not the welfare accounting.

## Defect one: the benchmark is re-evaluated in the arm's environment

In a counterfactual `use_old_results=1` calls `upload_vars(1)`, which SEEDS
prices from the benchmark. The arm then solves to its own equilibrium and
overwrites `risk_free_rate`, `rent`, `housing_price`, `lump_sum_transfer` and
`labor_income_tax_rate`. Nothing restores them before the comparison runs.

So x = 0 does not reproduce the benchmark's own newborn welfare, and every
reported CEV carries that offset. Fitting W = A + B(1+x)^k to the three measured
comparison points of the universal Housing First arm -- and W(0) is an
INTERPOLATION between x = -0.5 and x = 0.25, not an extrapolation:

    W(x) = 2033.96 + 114.29 (1+x)^1.5271
    W(0) implied            2148.25
    benchmark's own welfare 2203.54
    offset                  -55.29 utils
    x reproducing benchmark +0.29485

    arm            reported   bias removed
    universal HF   +40.28%    +16.9%
    universal TF   +30.39%    +13.2%
    rationed TF    +0.235%     -4.0%

Rationed Treatment First turning negative is the independent corroboration: its
newborn welfare is 2195.64 against the benchmark's 2203.54, so a positive CEV
was arithmetically impossible. The HF-TF gap falls from 9.89 points to 3.7,
which is the same order as the child externality's 2.75% rather than four times
it.

## Defect two: the arms and the benchmark are not solved the same way

A counterfactual run at the BENCHMARK'S OWN PARAMETERS settles at a newborn
welfare of 2200.32 against the benchmark's 2203.69. Identical parameters, a
3.37 util difference, because the counterfactual path never runs the frozen
moment loop while the benchmark does -- the loop that moved b from 0.0795 to
0.0849. At about 180 utils per unit of x that is worth 1.9 points of CEV, in the
same direction for every arm.

## Two smaller things, neither large enough to matter

The compensation scales only NON-DRUG consumption: `consumption_1 =
(1-frac)*total_consumption_1*(1+x)` with `total_consumption_1` passed unscaled,
so the drug quantity stays at its benchmark level. A standard consumption
equivalent would scale total consumption, which is also the faithful reading
because the household's own policy is a SHARE of total consumption. It is
identical machinery for both arms, so it does not tilt the gap. NOT changed in
the same patch as the fix: two changes at once make the move unattributable.

The `kappa_x` externality term inside the comparison uses the ARM's homelessness
rate while valuing BENCHMARK households. Inconsistent, worth about 3e-5 utils.

## Also found, unrelated to the CEV

`bequests_to_net_wealth_data = 0.012` appears EXACTLY ONCE in the file, at its
own declaration. Nothing brackets on it. This is the same scar the file already
records for `child_homeless_ratio_data`. Bequests are untargeted, so they cannot
discipline omega_c without the moment being built first.

A comment at the `utility_cost_of_treatment` subtraction says it "is held at
zero"; the live vector runs it at 12.6916. It is not double charged, because
`money_cost_of_treatment` is 0, but the comment will mislead the next reader.

## The fix

Compute the benchmark's welfare curve IN THE BENCHMARK RUN, where the
environment is by definition the benchmark's, and save it; a counterfactual then
inverts the saved curve. The alternative -- restoring the benchmark environment
around the comparison in the counterfactual -- needs every global the comparison
touches enumerated, and `upload_vars` does not cover `lump_sum_transfer`,
`voucher_probabilities_benchmark`, `price_of_addictive_good`, the survival arrays
or `model_fraction_homeless`. A missed one is silent.

The identity check becomes a permanent assert rather than a one-off: the curve's
value at x = 0 must equal `average_welfare_of_youngest_cohort`, or the run stops.
Defect two is fixed by giving the counterfactual path the same frozen moment
loop the benchmark has, so the two are the same kind of object.
