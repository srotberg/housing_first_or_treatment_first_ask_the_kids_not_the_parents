# Audit C: `stationary_equilibrium_statistics` and `stationary_equilibirum_homeownership_rate`

Slice: lines 7173-10718 of `housing_first_or_treatment_first_SR_v1.f90`.
Positions 1 and 2 of the nine-routine two-pass chain, plus the six smaller
routines that share the line range (`stationary_equilibrium_wealth_distribution`,
`stationary_equilibrium_income_distribution`, `calculate_bequest_amount`,
`stationary_equilibrium_income_bottom_distribution`,
`stationary_equilibrium_wealth_distribution_of_old` -- which is position 9 --
`calculate_gini_coefficient`, `calculate_housing_voucher`,
`calculate_housing_voucher_2`).

Read-only audit. Nothing in the Fortran was changed.

## THE HEADLINE, IN THREE LINES

1. `model_total_efficiency_units` and `model_financial` **are pooled correctly**.
   `MOMENT tau_l` is halved by a **second, out-of-loop call to
   `govt_revenues_calc` at line 36178**, which wipes the numerator and refills it
   from one type while the denominator keeps its pooled value. Finding 2.
2. **`total_rental_demand` is pooled correctly and `total_rental_supply` cannot
   mis-clear**, because `infinite_elasticity_of_rental_supply` is a
   `parameter` equal to 1, so supply is set identically equal to demand and rent
   never moves. Finding 6.
3. The **largest** thing in this slice is a different shape of two-pass bug that
   is not on the brief's list: **sixty-nine statistics are normalised IN PLACE**
   -- `X = X / D` where `X` is the guarded accumulator itself -- inside a routine
   that runs once per type. Pass two therefore adds a mass to a ratio. This is
   what halves `pi_eu`, and it is measurable in the author's own equal-beta pair.
   Finding 1.

## 1. IN-PLACE NORMALISATION OF A GUARDED ACCUMULATOR (69 variables) -- LIVE

### What the code does

The pattern, taking `model_fraction_unemployed` as the clean example:

    7287:  if (accumulating_beta_types==0) model_fraction_unemployed(time_period)=0
    7613:  model_fraction_unemployed(time_period)=&
    7614:      model_fraction_unemployed(time_period)+distribution_mass_used
    8872:  model_fraction_unemployed(time_period)=model_fraction_unemployed(time_period)/&
    8873:      max(model_mass_total_raw(time_period),10.d0**(-14))

The reset is guarded, the accumulation is correct, and line 8872 divides the
accumulator **into itself**. Line 8872 is not guarded and there is no
`current_beta_type` test anywhere in the normalisation block (verified: the only
top-level control flow between 8605 and 9105 is `do` loops and five
`if (mass > 1e-12)` guards).

### Why that is wrong

Write `u` for one type's unemployed mass and `T` for one type's working-age mass.

    pass 1  (accumulating=0, mass_passes=1)
        reset       X = 0
        accumulate  X = u
        normalise   X = u / T                     <- a RATE is now in the accumulator
    pass 2  (accumulating=1, mass_passes=2)
        reset       skipped
        accumulate  X = u/T + u                   <- a rate plus a mass
        normalise   X = (u/T + u) / (2T)

The correct pooled answer is `2u / 2T = u/T`. The ratio of what the code
produces to what it should produce is

    (1 + T) / (2 T)

`T` here is a MASS, and the distribution does not carry unit mass: the run log
prints `sum(distribution_guess) = 51.718393671906540` (`calibration_run.log:215`),
which is the life-cycle sum of cohort masses, not one. So for any denominator
that is a large mass the factor is **just above one half**, and for a small
subpopulation mass it **blows up** as `1/(2m)`.

The comment in the driver at 33690 -- "Each type's distribution carries unit
mass, so summing both passes doubles the numerator and the denominator of every
one of them" -- is the assumption that makes the in-place division look safe. It
is not true of this model. If the distribution really did carry unit mass the
pass-one division would be a division by one and the whole pattern would work;
at mass 51.7 it does not.

### Measured, not reasoned

The author's own equal-beta pair (`points/point_110278961e_onebeta.txt` against
`points/point_110278961e_twobeta_equal.txt`, same 28-parameter vector, both betas
equal) gives 140 comparable printed lines. The two predictions this mechanism
makes both land:

| moment | mechanism | predicted | measured 2beta/1beta |
|---|---|---|---|
| `pi_eu` | `model_fraction_unemployed` / working-age mass, in place at 8872. Large denominator | just above 0.5 | **0.5094** |
| `kappa_ued` | `model_fraction_addicted_and_unemployed` / `model_fraction_addicted`, in place at 8881, where the denominator is still the SMALL addicted mass | about 4 (worked through at the measured disorder rate: 4.3) | **4.1758** |

And the negative control lands too: the two statistics in this slice that are
formed into a THIRD variable from two clean pooled accumulators -- the bottom-half
net worth share (the histogram walk at 8761-8788, `model_wealth_share_below`) and
`model_average_net_wealth` at 8752 -- come out at **1.0136** and inside the
"within three per cent" set. The distinction the mechanism predicts is exactly
the distinction the data shows.

### Which variables

Statistics (41) and homeownership (28). Each line is
`variable  guarded-reset-line  accumulation-line  in-place-normalisation-line / denominator`.

#### `stationary_equilibrium_statistics`

    LTV_cdf                                             7207  9059  9063 / total_owners_to_consider
    median_income_cdf                                   7204  8707  8703 / sum_of_distribution
    model_addiction_by_employment                       7263  7472  8714 / model_fraction_addicted
    model_average_income                                7330  8521  9083 / sum_of_distribution
    model_average_labour_income                         7329  8477  9082 / model_total_workers
    model_average_labour_income_by_employment           7335  8508  9097 / mass_by_employment
    model_average_ss_benefits                           7333  7510  8688 / sum_of_retirees
    model_avg_housing_spending_all                      7254  8369  8853 / sum_of_distribution_not_be_homeless
    model_avg_housing_spending_owners                   7253  8365  8851 / mass_of_owners
    model_avg_housing_spending_renters                  7255  8372  8855 / model_mass_renters_to_consider
    model_avg_mortgage_spending                         7252  8362  8849 / mass_of_owners
    model_avg_rent_to_income_ratio                      7251  8054  9029 / mass_of_legit_renters
    model_fraction_addicted                             7292  7690  8884 / sum_of_distribution
    model_fraction_addicted_and_unemployed              7293  7695  8881 / model_fraction_addicted
    model_fraction_addicted_who_are_homeless            7266  7702  8711 / model_fraction_addicted
    model_fraction_addicted_with_negative_value_of_life 7299  7562  8697 / model_fraction_with_negative_value_of_life
    model_fraction_choose_little_work                   7233  7596  8719 / model_mass_can_work
    model_fraction_choose_zero_work                     7232  7591  8716 / model_mass_can_work
    model_fraction_homeless                             7257  7765  9026 / model_sum_of_lowest_productivities
    model_fraction_homeless_and_addicted                7294  7705  8885 / model_fraction_homeless
    model_fraction_homeless_with_negative_value_of_life 7298  7554  8694 / model_fraction_with_negative_value_of_life
    model_fraction_leaving_bequests                     7245  8454  8735 / mass_dying
    model_fraction_leaving_housing_bequests             7246  8446  8737 / mass_dying
    model_fraction_of_homeless_and_addicted_unemployed  7268  7710  8728 / model_fraction_homeless_and_addicted
    model_fraction_of_homeless_unemployed               7265  7626  8892 / model_mass_homeless_working_age
    model_fraction_of_unemployed_homeless               7267  7630  8863 / model_fraction_unemployed
    model_fraction_unemployed                           7287  7613  8872 / model_mass_total_raw
    model_fraction_unemployed_on_ui                     7288  7619  8860 / model_fraction_unemployed
    model_fraction_with_negative_value_of_life          7297  7549  8700 / sum_of_distribution
    model_homeless_2_years_or_more                      7258  7723  9023 / model_fraction_homeless
    model_homelessness_old                              7261  7808  8733 / model_fraction_homeless
    model_net_wealth_owners                             7220  8320  8690 / model_total_owners
    model_net_wealth_renters                            7221  8330  8692 / model_total_renters
    model_profile_of_homeless_old                       7262  7811  8731 / model_homelessness_old
    model_youngest_net_wealth_share                     7219  8312  8749 / model_total_net_wealth
    profile_of_chronic_homeless                         7259  7726  8650 / mass_profile_of_chornic_homeless
    rent_to_income_cdf                                  7200  9033  9040 / total_renters_to_consider
    rent_to_income_homeless_cdf                         7205  9035  9041 / total_homeless_1
    value_of_bequests_by_age                            7241  8425  9091 / bequests_mass_by_age
    income_to_avg_income_wide_pdf_1                     7202  7935  8644 / mass_at_profile_income_to_avg_income_wide_1
    profile_by_income_to_avg_income_wide_1              7302  7949  8671 / mass_at_profile_income_to_avg_income_wide_1

#### `stationary_equilibirum_homeownership_rate`

    average_age_of_homeowner_by_employment              9153  9500  9658 / mass_homeowners_by_employment
    fraction_with_largest_housing_size_consumed_in_eq   9142  9439  9651 / sum_of_distribution
    fraction_with_smallest_financial_in_eqilibrium      9143  9448  9654 / sum_of_distribution
    model_age_non_switcher_renters                      9164  9331  9554 / model_mass_non_switcher_renters
    model_age_switchers_mortgages_to_renting            9170  9302  9564 / model_mass_switchers_mortgages
    model_age_switchers_to_renting                      9158  9283  9542 / model_mass_switchers
    model_average_owner_occupied_unit_size              9129  9369  9603 / mass_of_owners
    model_average_owner_occupied_unit_size_to_income    9130  9375  9606 / mass_of_owners
    model_average_owner_occ_unit_size_to_income_work_age 9131 9382  9609 / working_age_mass
    model_average_owners_income                         9133  9393  9612 / mass_of_owners
    model_average_rent                                  9135  9355  9601 / sum(total_rental_demand)
    model_average_rental_unit_size                      9134  9352  9598 / mass_of_renters
    model_financial_non_switcher_renters                9166  9337  9558 / model_mass_non_switcher_renters
    model_financial_switchers_mortgages_to_renting      9172  9310  9570 / model_mass_switchers_mortgages
    model_financial_switchers_to_renting                9160  9289  9548 / model_mass_switchers
    model_fraction_of_homeowners_with_mortgage          9124  9403  9616 / mass_of_owners
    model_fraction_of_homeowners_with_mortgage_over_20  9125  9410  9627 / (fraction_with_mortgage * mass_of_owners)
    model_fraction_of_homeowners_with_mortgage_over_80  9126  9418  9619 / (fraction_with_mortgage * mass_of_owners)
    model_fraction_of_homeowners_with_mortgage_over_90  9127  9426  9623 / (fraction_with_mortgage * mass_of_owners)
    model_house_size_non_switcher_renters               9167  9341  9561 / model_mass_non_switcher_renters
    model_house_size_switchers_mortgages_to_renting     9173  9314  9573 / model_mass_switchers_mortgages
    model_house_size_switchers_to_renting               9161  9293  9551 / model_mass_switchers
    model_prod_non_switcher_renters                     9165  9334  9556 / model_mass_non_switcher_renters
    model_prod_switchers_mortgages_to_renting           9171  9306  9567 / model_mass_switchers_mortgages
    model_prod_switchers_to_renting                     9159  9286  9545 / model_mass_switchers
    model_wealth_of_renters                             9137  9360  9631 / mass_of_renters
    renters_by_rental                                   9150  9487  9524 / total_renters
    total_rental_demand_segmented                       9149  9483  9539 / sum(total_rental_demand_segmented)

### Three of these are worse than a factor

- **The three cumulative distribution functions.** `median_income_cdf` (divided
  at 8703, then cumulated in place at 8705-8709), `rent_to_income_cdf` and
  `rent_to_income_homeless_cdf` (cumulated at 9031-9038, then divided at
  9040-9041) and `LTV_cdf` (cumulated at 9057-9061, divided at 9063) are both
  normalised AND cumulated in place. On pass two the pass-one array is already a
  finished CDF; pass-two probability mass is added to it and the whole thing is
  cumulated a second time, which is a triangular re-weighting, not a scale error.
  `median_income(time_period)` is read off `median_income_cdf` at 8722-8726 and
  `percentiles_homeless_income` off `rent_to_income_homeless_cdf` at 9042-9055.
  `median_income` is module scope, it is the voucher income threshold, and
  `distance_median_income` (line 36166) gates the calibration on it.
- **`model_average_labour_income`** (in place at 9082) is the scale of the whole
  model: it is `avg_income_to_use_1` in every routine of the chain, the base for
  food stamps and voucher eligibility, and the denominator of `aleph` and `cbar`.
  In the equal-beta pair `DIAG treatment price / average labour income` moves by
  1.4214, i.e. `model_average_labour_income` itself moves by 0.7035, and `aleph`
  (a raw pooled level over it) moves by 2.8168 = 2 / 0.7035. Consistent.
- **`model_average_rent` and `model_average_rental_unit_size`** (in place at 9601
  and 9598) are read by `calculate_housing_voucher` at 10711-10713 and by
  `calculate_housing_voucher_2`, so the voucher amount every household is offered
  is computed from them.

### What it would change if fixed

Unknown as a set. Two of the numbers are measured above (`pi_eu` recovers a
factor of 1.96, `kappa_ued` loses a factor of 4.18). The rest cannot be predicted
without a run, because `model_average_labour_income` and `median_income` feed
back into eligibility and therefore into the equilibrium. The mechanical fix is
to write each ratio into a variable the loop does not accumulate, exactly as
`model_smi_share_of_homeless` (8912), `model_homeless_income_share` (8925),
`model_employment_rate_given_smi` (8938) and `model_average_net_wealth` (8752)
already do -- those four are correct under two passes and are the model to copy.

## 2. `MOMENT tau_l`: BOTH DENOMINATOR COMPONENTS ARE POOLED. THE CAUSE IS ELSEWHERE -- LIVE

Asked directly, answered plainly.

`model_total_efficiency_units` (guarded reset 7230, accumulated 7577-7579) and
`model_financial` (guarded reset 7224, accumulated 8228-8229) are **pure
accumulators**. Neither is normalised in place anywhere; the only other reads are
`model_total_investment_income` (8740) and `model_average_financial` (8742), both
of which write into a different variable. After the two-pass loop both hold two
types' worth of mass. **They are correct. The search moves elsewhere.**

Where it moves to is line 36178:

    36177:  call function_of_utility_advantage_from_homeowning(1)
    36178:  call govt_revenues_calc(1)
    36179:  call set_SS_benefits(1)

This is **after** the two-pass loop, which ends at 33785 and sets
`accumulating_beta_types=0` and `mass_passes=number_of_beta_types` at 33791-33793.
So on that call every guarded reset in `govt_revenues_calc` fires --
`govt_revenues_from_labour_income(1)` is zeroed at 10742 and refilled at 11738
from `distribution_stationary`, which holds **only the last type solved**.
`stationary_equilibrium_statistics` is NOT called again anywhere between 33774 and
`print_all_moments` at 36267, so `model_total_efficiency_units` and
`model_financial` keep their pooled two-type values.

    tau_l printed = (one type's labour tax revenue) / (two types' efficiency units)

which is one half. This is the brief's CALLED-TWICE class, and it is invisible at
one type. Measured in the equal-beta pair: `MOMENT tau_l` ratio **0.4969**.

Note that the in-loop call at 33776 computes `tau_l` correctly, and the
calibration adjuster for the retention scale reads it at 34544 -- which is before
36178. So the tax rate is being driven by the right number and the moment table
is printing the wrong one. Both are worth knowing.

The same call corrupts everything else `govt_revenues_calc` owns
(`model_fraction_homeless`, `model_total_drug_users`, `model_fraction_addicted`
is re-owned there, the food stamp and voucher shares). Those belong to the
`govt_revenues_calc` auditor; I am reporting the call site because `tau_l` was
put to me.

## 3. `mass_passes = number_of_beta_types` AFTER THE LOOP IS WRONG FOR A ROUTINE THAT REBUILDS FROM ONE TYPE -- LIVE, AND NEW TODAY

`mass_passes` was introduced this morning in `57863ad`, replacing
`(accumulating_beta_types+1)` at all eleven scaling sites. The replacement is
right for a routine whose accumulators survive the loop. It is **wrong for a
routine that runs only after the loop and rebuilds every one of its own numbers
from `distribution_stationary`**, because there the numerators are one type and
the old `+1` was correct.

Two such routines are in this line range:

- **`stationary_equilibrium_wealth_distribution`** (9724-9892), called at 36590,
  after the loop. It has **no guarded resets at all** (verified: no
  `accumulating_beta_types` appears between 9664 and 10417), so `wealth_counter`,
  `wealth_matrix` and `model_total_net_wealth_1` are rebuilt from one type. Yet
  line 9747 scales `sum_of_distribution` by `mass_passes`, and 9846-9848 take the
  top-x-per-cent cut at `sum_of_distribution*stopping_rule_wealth_dist` -- so the
  "top one per cent" cut is now taken at two per cent of the mass actually being
  walked, and 9859 divides a one-type head count by a two-type mass.
- **`calculate_gini_coefficient`** (10550-10635), called at 36591 immediately
  after, reads the `sum_of_distribution` that routine leaves behind (10621) while
  building `sum_distribution_used` from one type.

The `govt_revenues_calc` re-call in Finding 2 is the third instance, and it is
the one with teeth: under `(accumulating_beta_types+1)` the denominator there was
also one type, so `MOMENT h_1`, `b`, `lambda_d` and the food-stamp shares came
out at roughly the right value by cancellation. Measured: `h_1` ratio **1.0637**,
i.e. NOT halved, on the pre-`mass_passes` model hashes. With `mass_passes=2`
those numerators stay one-type and the denominator doubles. **I expect `h_1`,
`b`, `lambda_d`, `cbar` and `pi_V` to halve on the next run and they did not
before.** That is a prediction, not a measurement; `VALIDATE3` will settle it and
it is the cheapest thing to look at first.

What would fix it: `mass_passes` should be set to 1 before any post-loop call to
a routine in the chain, or those routines should not be called after the loop at
all.

## 4. FOUR GUARDED RESETS ON NON-SAVED LOCAL VARIABLES -- LIVE

A guarded reset only works if the variable persists between the two calls. Four
of them are applied to variables declared local to the routine, with no `save`
and no initialiser, so their value on entry to pass two is undefined:

    7206:  if (accumulating_beta_types==0) total_homeless_1=0            declared 7185
    7208:  if (accumulating_beta_types==0) total_renters_to_consider=0   declared 7183
    7209:  if (accumulating_beta_types==0) total_owners_to_consider=0    declared 7185
    10417: if (accumulating_beta_types==0) sum_of_distribution_of_old=0  declared 10414

(107 guarded resets in `stationary_equilibrium_statistics`, 3 of them on locals;
45 in `stationary_equilibirum_homeownership_rate`, none; 1 in
`stationary_equilibrium_wealth_distribution_of_old`, and it is one of the four.)

Between pass one and pass two of the chain the model runs a full value-function
solve, a distribution convergence and eight other statistics routines, so the
stack slot these occupy is certainly overwritten. On pass two they begin from
whatever is there. The first three are the denominators of `rent_to_income_cdf`
(9040), `rent_to_income_homeless_cdf` (9041) and `LTV_cdf` (9063); the fourth is
the denominator of the whole old-age wealth distribution in position 9 of the
chain.

The fix is `save`, or promotion to module scope, or -- better for the first three,
which are recomputable -- the recompute-and-scale pattern the rest of the file
uses. `-Wuninitialized` will not catch this because the write is conditional.
What it changes: unknown, and unpredictable between builds, which is the reason
to close it whatever the size.

## 5. FIVE UNGUARDED RESETS THAT SHOULD BE GUARDED -- LIVE

Everything else in both routines is guarded; these are the exceptions, excluding
per-household scalars (`has_house`, `in_retirement`, `low_quality_market`,
`is_addicted_1` and the like) which are correctly unguarded.

    7300:  model_largest_negative_value_of_life(time_period)=10000000
    7341:  average_rent_by_age=0
    7342:  mass_of_renters_by_age=0
    9145:  smallest_financial_chosen_in_equilibrium=financial_grid_size

- **`model_largest_negative_value_of_life`** is a MINIMUM tracker (7540-7543,
  `if (value_function_used < ...) then ... = value_function_used`). Resetting it
  to 1e7 on the second pass discards the patient type's minimum, so the printed
  "DIAG lowest value of a period of life" (36422) is the impatient type's alone.
  Its maximum-tracker twin `largest_financial_chosen_in_equilibrium` (9144) IS
  guarded, which is what makes this look like an oversight rather than a decision.
- **`smallest_financial_chosen_in_equilibrium`** is the same class at 9145, and
  its own guarded twin sits on the line above it.
- **`average_rent_by_age` / `mass_of_renters_by_age`** are both unguarded, so the
  ratio at 9090 is internally consistent but describes **only the last type
  solved**. It is written to `average_rent_by_age<n>.txt` at 30034-30039. Given
  that the age profile of housing is what the author is currently reading, a
  one-type age profile in a two-type model is worth knowing about.

`sum_of_distribution` (8609, 9576) and `sum_of_retirees` (8625) are also reset
unguarded, but that is correct: they are recomputed and then scaled by
`mass_passes` at 8623, 8640 and 9590. Both scalings are right for these two
routines, which run inside the loop.

## 6. THE RENTAL MARKET: POOLED CORRECTLY, AND IT COULD NOT MIS-CLEAR ANYWAY

Asked specifically, so answered specifically.

- **`total_rental_demand(time_period,:)`**: guarded reset at 9148, accumulated at
  9469-9470, never normalised in place. After the loop it holds **both types'
  demand**. Correct.
- **`total_rental_supply(time_period,:)`**: not an accumulator at all. Guarded
  reset at 9664, then overwritten wholesale in every live branch.
- **`infinite_elasticity_of_rental_supply` is `integer, parameter :: ... =1`**
  (line 1198). So both the benchmark branch (9695) and the counterfactual branch
  (9670) execute `total_rental_supply = total_rental_demand`. Supply is pooled
  because demand is.
- The rent block in `function_of_utility_advantage_from_homeowning` takes the
  `infinite_elasticity` arm at 24242-24246, which sets `rental_management_costs`
  from rent and prices **with no demand term in it at all**, and every assignment
  to `rent(1,:)` is skipped. The comment at 1160-1181 states this as the design:
  the paper has no endogenous rental market and rent is a parameter.
- The one call that would see this, `function_of_utility_advantage_from_homeowning(1)`
  at 36177, runs after the loop and therefore sees the pooled demand in any case.

**Verdict: correct.** Even in the `infinite_elasticity=0` configuration the
inversion at 24250-24256 divides by `total_rental_demand**(convexity-1)`, and
that demand is pooled, so the cost the firm's first order condition is inverted
from is the two-type one. There is no version of this in which the two types face
a price cleared against one type's demand.

One dead-branch note while I was in there: at 9693-9716 the counterfactual arm
(`is_counterfactual==1`, `infinite_elasticity==0`, `zero_elasticity==1`) assigns
`total_rental_supply` **nothing**, where the benchmark arm has an explicit
`else total_rental_supply=total_rental_demand` at 9714. Unreachable at the current
switch settings; an asymmetry that would bite if `infinite_elasticity` were ever
turned off.

## 7. `model_average_income_plus_assets` IS ASSIGNED, NOT ACCUMULATED -- LIVE

    8546:  model_average_income_plus_assets(time_period)=model_average_income(time_period)+&
    8547:      (bequest_2+max(financial_grid(financial_index),0.d0))*distribution_mass_used

Inside the innermost household loop, and the left-hand side does not appear on
the right. Every household overwrites the previous one, so what survives the loop
is `model_average_income` (the running total, which by then is the full total)
plus **one household's** asset term. Line 9084 then divides that by
`sum_of_distribution`, so `model_average_income_plus_assets` is
`model_average_income` to within one household. `model_average_income_plus_all_assets`
at 8551-8558 is built the same way off it and inherits the same fault.

Should be `... = model_average_income_plus_assets(time_period) + (income + assets)*mass`,
with its own income term rather than a read of the other accumulator.

Live: both are saved into `..._previous` at 7326-7327 and used at 7878, 7896 and
7904 as the denominators of `income_to_avg_income`, which selects the bin for
`profile_by_income_to_avg_income_wide_1` and `income_to_avg_income_wide_pdf_1` --
the income-to-average-income profiles printed at 29234-29248. So the profiles are
binned against an average that is income, not income plus assets. What it would
change: unknown; it is a re-binning, not a scale.

## 8. DEAD CODE (class 2)

- **`stationary_equilibrium_income_distribution`** (9894-10134): zero call sites
  anywhere in the file. Already named in the brief; confirmed. It carries its own
  `sum_of_distribution=sum_of_distribution*mass_passes` at 9919, harmless while
  dead but a module-scope write if it is ever revived.
- **`stationary_equilibrium_income_bottom_distribution`** (10162-10406): the only
  two references, at 36544 and 36592, are **both commented out**. Effectively
  dead, and also carries a `mass_passes` scaling (10189).
- **`model_fraction_homeless_owners`**: guarded-reset at 7264, divided at 9020,
  and **never accumulated anywhere**. It is identically zero and is written to the
  results CSV at 28961 and 29578 as a real statistic. Same family as
  `model_median_assets_to_income`, which the file already documents at 5596 and
  34113 as never computed.
- `model_median_assets_to_income` (7290): zeroed, never accumulated. Already
  documented at 34113; not reported as new.

## 9. UNFLOORED DIVISIONS (class 4)

The file's own convention, stated in the comment at 8681-8687, is that every
subpopulation denominator is floored with `max(...,1e-14)`. Five divisions in
this slice are not, and all five are capable of a zero denominator:

    8650:  profile_of_chronic_homeless(:) / mass_profile_of_chornic_homeless(:)   array-wise, empty bins likely
    8749:  model_youngest_net_wealth_share / model_total_net_wealth
    9091:  value_of_bequests_by_age(age) / bequests_mass_by_age(age)              per age
    9539:  total_rental_demand_segmented(:) / sum(total_rental_demand_segmented(:))
    9601:  model_average_rent / sum(total_rental_demand(time_period,:))

8650 is the one I would look at first: it sits four lines above the comment that
says everything below it is floored, and a chronic-homelessness profile with an
empty duration bin is not a remote possibility at this model's homelessness rate.
These are the failures that halt an `-ffpe-trap` sweep, which is how the rest of
the family was found.

## 10. A RUNNING MINIMUM USED AS IF IT WERE FINAL (class 4)

    9269:  if ((financial_index_used<smallest_financial_chosen_in_equilibrium) ...
    9272:      smallest_financial_chosen_in_equilibrium=financial_index_used
    ...
    9445:  if ((financial_index_used==smallest_financial_chosen_in_equilibrium) ...
    9448:      fraction_with_smallest_financial_in_eqilibrium=... + distribution_mass_used

Both are in the same sweep of the same loop nest. Line 9445 tests equality against
a minimum that line 9269 is still lowering, so a household visited before the true
minimum is reached is tested against a stale, larger threshold, and mass is
counted at whatever the running minimum was at the time. Its neighbour at 9436-9443
compares against a fixed constant (`housing_status_grid_size-1`) and is fine,
which is what makes the asymmetry visible.

Live in the benchmark; reaches only the diagnostic printed at 36122. Correct
version needs a second sweep, or to count the mass at the minimum after the loop.

## 11. MODULE-SCOPE VARIABLES THIS SLICE WRITES THAT LATER ROUTINES READ

Asked for, so here in full. Classification is what the variable holds when the
two-pass loop has finished.

**Left correct (pooled), later readers are safe**

    sum_of_distribution                8623, 9590   recomputed and scaled by mass_passes. Both correct.
    sum_of_retirees                    8640         same
    sum_of_distribution_not_be_homeless 7344/7830   guarded accumulator, pooled; read at 9614 by the
                                                    homeownership rate, whose numerator mass_of_owners is
                                                    also pooled. model_homeownership_rate is CORRECT.
    model_average_net_wealth           8752         two clean pooled accumulators into a third variable
    newborn_parent_share               9010         a share of its own accumulator's total; both pooled.
                                                    This is the one that feeds the intergenerational
                                                    process, and it is right.
    model_total_efficiency_units, model_financial   see Finding 2
    model_mass_homeless_raw, model_mass_total_raw, model_mass_homeless_working_age,
    model_mass_smi, model_smi_and_homeless, model_all_labour_income, mass_dying,
    mass_of_owners, mass_of_renters, model_total_owners, model_total_renters,
    total_rental_demand, total_housing_demand, wealth_hist_*, income_hist_*,
    diag_mass_top_financial, diag_mass_top3_financial   -- all pure pooled accumulators

**Left wrong (Finding 1), and read by later routines or by the calibration**

    model_average_labour_income   read as avg_income_to_use_1 by every later routine in the chain,
                                  by the food stamp and voucher thresholds, and damped at 36166
    median_income                 the voucher income threshold; distance_median_income gates the loop
    model_average_rent            read by calculate_housing_voucher (10711) and _2
    model_average_rental_unit_size same
    model_fraction_homeless       re-owned and overwritten by govt_revenues_calc, on a DIFFERENT
                                  denominator (sum_of_distribution there, model_sum_of_lowest_
                                  productivities here). Two routines own one module variable.
    model_fraction_addicted       same shape: re-owned in govt_revenues_calc at 10763-ish
    mass_by_employment            reset and re-owned by govt_revenues_calc (10771) and
                                  calculate_welfare_by_characteristics (13257) and 14537
    model_average_income, model_average_income_plus_assets, model_average_income_plus_all_assets
    rent_to_income_cdf, LTV_cdf, median_income_cdf, percentiles_homeless_income

**Left as one type's value**

    average_rent_by_age, mass_of_renters_by_age                 Finding 5
    model_largest_negative_value_of_life                        Finding 5
    smallest_financial_chosen_in_equilibrium                    Finding 5

## WHAT I LOOKED FOR AND DID NOT FIND

- **Ratios whose numerator and denominator disagree on pooling in the ordinary
  way** (a pooled numerator over a mass recomputed from `distribution_stationary`
  without scaling): none in either routine. All three recomputation sites in the
  slice that run inside the loop -- 8623, 8640, 9590 -- scale by `mass_passes`.
  The scaling errors that remain are the reverse case, Finding 3.
- **Loop index clobbering.** `calculate_bequest_amount` (10136) loops on the
  module-scope index `i`, and it is called from inside the household nest of
  `stationary_equilibrium_statistics` at 7390. I checked: `i` is not live at that
  point (the nest runs on `age_index`, `years_left_on_mortgage_index`,
  `unemployment_index`, `employment_index`, `voucher_index`, `financial_index`,
  `housing_status_index`), so nothing is corrupted today. It is a latent hazard,
  not a bug.
- **`implicit none`**: present in every routine in the range. No implicit typing.
- **Array bounds**: nothing found. The `max(median_index(1),1)` guards at 8726,
  9047 and 9054 correctly protect against `minloc` returning zero on an all-false
  mask.
- **`intent(out)` never assigned**: `calculate_bequest_amount` declares
  `bequest_1` `intent(out)` and sets it to 0 at the top before the conditional
  assignment. Correct.
- **Class 3, moment universe against target**: the two I could check in this
  slice are stated correctly and the file argues both. `model_fraction_unemployed`
  is over `model_mass_total_raw`, working age on both sides (comment 8866-8869);
  `model_homeless_income_share` puts working-age earnings over a working-age
  base on both sides (comment 7777-7790). `model_fraction_homeless` is over
  `model_sum_of_lowest_productivities`, whose name says productivity and whose
  accumulation at 7833-7834 is a mass -- but the file documents that deliberately
  at 7768-7774 and again at 8907-8909, so it is a naming complaint, not a finding.

## ORDER I WOULD FIX THEM IN

1. Finding 3, because it is new today, unmeasured, and predicts a fresh halving
   of `h_1`, `b` and `lambda_d` that were previously right.
2. Finding 2, because `tau_l` is an internal adjuster target and the fix is to
   delete or re-scope one call.
3. Finding 1, because it is sixty-nine numbers and it is what `pi_eu` and
   `kappa_ued` are, but it is a large mechanical edit and worth doing in one pass
   with a template rather than piecemeal.
4. Finding 4, because undefined behaviour does not stay put between builds.
5. The rest.
