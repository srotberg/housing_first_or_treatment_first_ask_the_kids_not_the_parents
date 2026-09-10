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

## The assert fired on its first run, and it is NOT the environment

10 September, 17:06. The welfare curve now runs inside the benchmark, so the
prices, taxes and transfers the walk reads are the benchmark's by construction.
It still does not reproduce the benchmark:

    WELFARE CURVE identity check: w(0) = 2195.9485
        against average_welfare_of_youngest_cohort = 2203.7556
        relative difference = 3.54e-3
    THE WELFARE CURVE DOES NOT REPRODUCE THE BENCHMARK AT x = 0.

7.81 utils, which at ~172 utils per unit of x is 4.5 CONSUMPTION EQUIVALENT
POINTS, in every number the project has ever computed. The run stopped, as it is
meant to.

THE AUTHOR WAS RIGHT AND I WAS WRONG. The identity run returned -0.894 per cent
and I read that as the routine being very nearly right. They said: *"i think
your CEV calculations being wrong and accidentally cancelling out is no proof of
the signs being right"*. This is that, demonstrated -- the -0.894 was two errors
of 4.30 and -5.05 points cancelling, and with the environment one removed the
remaining 4.5 points stands exposed.

So there are TWO defects, not one, and the second is inside
compute_value_function_comparison rather than around it.

LEADING SUSPICION, to be checked: the two sides are not the same object. The
benchmark side is a POLICY-FIXED WALK; the arm side is the model's own value
function, which is a max over choices. Any point where the saved policies are
re-discretised inside the walk loses value, and loses it DOWNWARD, which is the
sign observed. 0.35 per cent is the right order for a grid or interpolation
mismatch.

If that is the cause, the fix is to compare like with like rather than to hunt
the discrepancy: walk BOTH sides, so a uniform re-discretisation loss cancels.
That is a bigger change than the one just made, because
compute_value_function_comparison reads the *_benchmark arrays and would have to
be pointed at an arm's own policies.

## The walk diagnostic ran, and the defect is not in the walk

10 September, 17:5x, the omega_c = 0 benchmark. The age profile of
(comparison - benchmark), mass weighted:

    age  1   +0.994
    age  6   +1.389
    age 11   +1.725
    age 16   +1.980
    age 21   +2.077
    age 26   +2.102      <- peak
    age 31   +1.441
    age 36   +0.523
    age 41   +0.038
    age 46   -0.025
    age 51   -0.0042
    age 56   -0.00024
    age 60   -0.000026

Zero at the terminal age and growing backward, so it is a CONTINUATION effect
rather than a missing flow term -- and it is SMALL, about a util where it
matters for the consumption equivalent, which is age one.

Meanwhile the identity check on the same run:

    w(0) = 2195.9489   against average_welfare_of_youngest_cohort = 2203.7556
    shift applied 7.8067 utils, 4.54 per cent of consumption

Both routines cover the SAME mass at age one, 0.99999999999999989 to the last
digit -- compute_value_of_comparison's own mass_1 and the diagnostic's full
array sum agree -- so the two averages are over the same population and can be
subtracted. Therefore

    mean(V_comparison) at age 1 = w(0)              = 2195.949
    mean(V_comparison) - mean(V_benchmark)          = +0.994
    mean(V_benchmark)  at age 1                     = 2194.955
    the model reports                                 2203.756
    GAP                                               8.80 utils

THE MODEL'S REPORTED NEWBORN WELFARE IS 8.80 UTILS ABOVE THE MASS WEIGHTED
AVERAGE OF THE VALUE FUNCTION IT SAVED. The consumption equivalent was being
solved against a target that does not match the value function the target is an
average of.

## Ruled out, each with evidence

THE ENVIRONMENT. Fixed; the curve is built inside the benchmark now and this
measurement is from there.

A survival_sud_of MISMATCH. The comparison uses is_addicted_1 and the model
uses survival_sud_of(addiction_index,treatment_choice_now). Since treatment
stopped suspending the mortality penalty the function returns d_1 unchanged, so
they are the same. Looked promising and was not it.

large_negative_num CONTAMINATION. The model's welfare loop prints "stuck" for
any newborn cell with positive mass holding it. It never fires. And at
-1.7977e10 a mass of 1e-9 would be worth -18 utils, so any contamination would
present as a catastrophe rather than as 7.81.

THE FILE ROUND TRIP. value_function is written as rank 7
(vector_transition_real, time first) and read into rank 6 (vector_real). The
allocations match dimension for dimension and transition_length is 1, so the
leading extent is a singleton and the layout is identical. Fragile, not wrong.

## What is left, and the one number that separates them

  - the welfare loop's index bounds against the array's own: it starts
    financial_index at renter_floor_by_age(age) and stops housing at
    housing_status_grid_size-1, while the array runs from renter_array_floor;
  - stale timing: calculate_welfare runs during a pass and
    save_vars_and_functions after the frozen loop, whose 4e-5 convergence is on
    MOMENTS and not on the value function.

THE TEST, five lines: compute the mass weighted average of
value_function_benchmark at age one inside the run and print it beside
average_welfare_of_youngest_cohort. Agreement puts the defect back in the walk;
a difference of 8.80 puts it in the reporting.

The arms are unaffected either way. The curve is normalised at x = 0, so levels
are right to first order and every difference between arms is untouched.

## FOUND. The welfare denominator is 0.4 per cent short.

Computed OFFLINE from the saved benchmark files, so no source edit and no risk
to the six arms in flight. Age one is every 61st record of the rank 7 array --
time is fastest and age next, and transition_length is 1 -- and the value and
distribution files have identical shapes, so they pair element for element
without needing the inner extents:

    age-1 mass                                = 1.000000000000000  exactly
    mass weighted mean of the SAVED value fn  = 2194.954665
    model reports average_welfare_of_youngest = 2203.755553
    GAP                                       = -8.800888
    cells with mass and NEGATIVE value        = 0

That last line kills the index bounds candidate: with no negative cells,
excluding cells from the numerator could only push the reported number DOWN,
and it is UP. Which leaves the denominator, and the arithmetic reconstructs the
reported number exactly:

    numerator   sum V*mass over age one, at full unit mass = 2194.954665
    denominator sum_of_distribution_youngest               = 0.996006414
    quotient                                               = 2203.755553

THE NUMERATOR IS SUMMED OVER THE FULL UNIT MASS AND THE DENOMINATOR IS 0.3994
PER CENT SHORT OF IT. Every average_welfare_of_youngest_cohort the model has
printed is inflated by 0.4 per cent. That is the whole of the 7.81, and it is
NOT in the comparison walk -- the age profile showed the walk accurate to about
a util at age one.

The saved distribution sums to exactly one at age one, so the IN MEMORY
distribution_stationary that calculate_welfare reads is short at the moment it
reads it. sum_of_distribution_youngest is assigned from pooled_mass_youngest,
accumulated pass by pass, and it falls out of step. This is the stale timing
candidate rather than the index bounds one.

FALSIFIABLE: print sum_of_distribution_youngest and it will read 0.996006414.

## Why the arms in flight are still sound

compute_value_of_comparison's own mass is exactly 1.0, so the CURVE is right.
The TARGET is the arm's inflated welfare, which is the 4.5 point bias. But the
normalisation already applied shifts the curve up by exactly the benchmark's own
inflation, and both arms and benchmark are inflated by the same 0.4 per cent, so
the residual across arms is 0.004*(W_arm - W_bench), about 0.14 utils. The six
arms do not need redoing.

## The fix

Divide by the mass the numerator actually covers rather than by a separately
accumulated pooled_mass_youngest that can fall out of step with it. Staged with
the child term patch; neither is safe to apply mid chain, because run_variant.sh
rebuilds from master between arms.
