# Audit B — `print_all_moments` and what follows it

Slice: lines 4753–7172 of `code/housing_first_or_treatment_first_SR_v1.f90`.
That is `print_all_moments` (4753–5708), `weighted_drug_share_now`,
`apply_gamma_tie`, `move_factor`, `trust_step`, `damp_on_flip`, the small
hazard/transition functions, `compute_asset_lottery`, `report_asset_lottery`,
`reset_asset_lottery_counters`, `set_files_names`, `calculate_income` and
`calculate_cdf_of_incomes_earned`.

Every `MOMENT` and `UNTARGETED` line was traced back to the loop that builds its
numerator and its denominator. Because almost nothing is *computed* in this
block — it prints objects other routines build — most of the findings name an
accumulation site outside the slice. That is where the moments printed here come
from, and the brief asks for the trace, not for the print statement.

Twenty-two findings. Numbered F1–F22, worst first inside each class.

**What is measured and what is not.** Four solved point files were used as
evidence. Three of them (`point_1c4b7759d4`, `point_cd817d0401`,
`point_02bb4b5ab3`, `point_6716556560`) are one-beta-type runs; exactly one,
`points/point_f48e057502_frozen_beta.txt`, is a two-type run, and it was written
at commit `48ee9d2`, BEFORE the two pooling fixes `0fd901f` and `57863ad`. There
is no point file from the current code with two types, so nothing below that
depends on the state of HEAD's `mass_passes` could be measured. Where a number is
measured it says so; where it is derived from the code it says "derived, not
measured".

---

## Class 1 — the two-pass machinery

### F1. `govt_revenues_calc` is called a THIRD time after the loop, and `mass_passes` now makes that a factor of two — LIVE, and it hits `MOMENT b` and `MOMENT h_1`

**Line 36178**, `subroutine calibrating_model`:

```fortran
            call function_of_utility_advantage_from_homeowning(1)
            call govt_revenues_calc(1)
            call set_SS_benefits(1)
```

This sits after the `do current_beta_type=1,number_of_beta_types` loop closes at
line 33790, where the driver has already restored

```fortran
            mass_passes=number_of_beta_types
            accumulating_beta_types=0
```

so on this call every one of `govt_revenues_calc`'s ~120 guarded resets
(`if (accumulating_beta_types==0) X(time_period)=0`, lines 10755–10860) fires.
The pooled totals built over the two passes are wiped and refilled from
`distribution_stationary`, which holds **only the last type solved** — the
impatient one. Nothing between line 33791 and line 36178 rebuilds
`distribution_stationary` (the calls in that window are
`calculate_updated_inheritance_amounts`, `damp_on_flip`, `trust_step`,
`create_newborn_employment_probability`, `apply_gamma_tie`, `clear_drug_market`,
`initialize_variables_and_grids`, `initialize_financial_grid`,
`set_smallest_house_size`, `function_of_utility_advantage_from_homeowning`), so
the refill carries one unit of mass.

The divisor does not. At line 12522,

```fortran
        sum_of_distribution=sum_of_distribution*mass_passes
```

and `mass_passes` is 2 here. So every rate this routine normalises by
`sum_of_distribution` comes out at **half the impatient type's value**:

- line 12527 `model_total_drug_users` → `MOMENT b` (line 5049)
- line 12545 `model_fraction_homeless` → `MOMENT h_1` (line 5047)
- lines 12529, 12531 `model_addicted`, `model_exprimenters`
- line 12524 `model_drug_use_percent_by_age_group`
- line 12256 `model_eligibles_getting_voucher_relative_to_pop`

and every statistic that is a ratio of two of this routine's own accumulators
becomes a **one-type** statistic rather than the fifty–fifty mixture: `MOMENT
tau_u`, `MOMENT mu_H`, `MOMENT pi_V`, `MOMENT cbar`'s numerator, `MOMENT y_u`'s
numerator, `UNTARGETED income with a SUD`, `UNTARGETED income of the homeless`,
`UNTARGETED participation with/without a SUD`, the three TEDS-A rows, the five
drug-user age bands, `UNTARGETED drug deaths` and the buyer/non-buyer DIAGs.

**What it should do.** Exactly what commit `57863ad` did for the sister case. That
commit's own message says it: *"calculate_homeownership_by_characteristics was
also called a second time outside the loop, where its guarded resets fire, wiping
the pooled totals and refilling them from the last type solved."* It removed that
call (line 36569 now carries the comment where the call used to be) and left this
one. In the same commit the scaling changed from `(accumulating_beta_types+1)` to
`mass_passes`. Before that change this call scaled by `0+1 = 1`, which matched the
one unit of mass it had just refilled, so the halving is **new with `57863ad`** —
the fix for one copy of the bug created a worse copy in the routine next door.

**Live?** LIVE in the benchmark whenever `number_of_beta_types = 2`, which is the
declared default (line 2203).

**What it would change.** `MOMENT b` and `MOMENT h_1` by a factor of two, in the
direction of reading low. Derived, not measured — there is no two-type point file
from HEAD. Both are scored: `score_points.py` reads `MOMENT` lines, per the
comment at line 5089, so the loss the external search minimises is computed on
halved values of the two moments `addiction_scalar_1` and `size_homelessness` own.

**A second consequence worth separating.** The parameter-update block (lines
34177–35988) reads `model_fraction_homeless(1)` and `model_total_drug_users(1)`
*before* line 36178, and `print_all_moments` reads them *after*. The internal
bisection and the printed `MOMENT` lines are therefore looking at two different
populations in the same loop iteration.

### F2. `model_fraction_homeless` is built and normalised in TWO routines, so `h_1` weights the two types 1:3 — LIVE

The variable is reset, accumulated and divided in `stationary_equilibrium_statistics`:

- 7257 `if (accumulating_beta_types==0) model_fraction_homeless(time_period)=0`
- 7765 `model_fraction_homeless(time_period)=model_fraction_homeless(time_period)+distribution_mass_used`
- 9026 `model_fraction_homeless(time_period)=model_fraction_homeless(time_period)/model_sum_of_lowest_productivities(time_period)`

and again in `govt_revenues_calc`, which runs immediately after it in the loop:

- 10833 reset, 11771 accumulate, 12545 `/sum_of_distribution`.

`model_sum_of_lowest_productivities` (7833) is accumulated for every household
with no condition, so despite its name it is the total mass: 1 after pass 1, 2
after pass 2.

Writing `M_i` for type `i`'s homeless mass and taking each type's distribution at
unit mass (line 33690 asserts this):

| point | `model_fraction_homeless` |
|---|---|
| after pass 1, S | `M1` |
| after pass 1, G | `M1 / 1 = M1` |
| after pass 2, S | `(M1 + M2) / 2` — the correct pooled rate |
| after pass 2, G | `((M1+M2)/2 + M2) / 2 = ¼h1 + ¾h2` |

So the value the update block reads is a **1:3 mixture, over-weighting the
impatient type**, not the 1:1 mixture. `stationary_equilibrium_statistics` had
already produced the right answer and `govt_revenues_calc` added a mass on top of
a rate.

The two routines are the only pair in the nine-routine chain that both reset AND
both normalise the same variable. `mass_by_employment` and `total_homeless_1` are
also reset in both, but neither is divided in place by the earlier one.

**Live?** LIVE at two types. Masked at print time by F1, which overwrites the
result; it is the value the internal parameter update sees.

**What it would change.** The homelessness rate the bisection on
`size_homelessness` is driving. Derived, not measured.

### F3. `mass_of_renters_at_housing_spending` is divided in place every pass while its reset is guarded to the first — MEASURED at 8.9 per cent

`calculate_household_housing_spending`, lines 12605 and 12986:

```fortran
        if (accumulating_beta_types==0) mass_of_renters_at_housing_spending(time_period,:)=0
        ...
            mass_of_renters_at_housing_spending(time_period,i)=&
                mass_of_renters_at_housing_spending(time_period,i)/mass_of_renters_1
```

The division runs on both passes. On pass 2 the accumulator therefore starts from
pass 1's **share**, not pass 1's mass, and pass 2's mass is added to it.

Worse, `mass_of_renters_1` is a plain local (declared line 12596, no `save`, no
initialiser) whose reset is guarded the same way at line 12611. A non-`SAVE`d
local without an initialiser is undefined on entry, so on the second pass the
denominator starts from whatever is in that stack slot — and a whole value
function solve and distribution convergence run between the two calls.

**Measured.** Rows 5249–5252 print this array; rows 4869–4876 print
`val_burden50_by_unit(1,k)/val_mass_by_unit(1,k)` and
`val_mass_by_unit(1,k)/sum(val_mass_by_unit(1,:))`, which are accumulated in the
same loop nest of the same routine under the same condition and are never divided
in place. `Σ_k share_k × rate_k` therefore rebuilds
`UNTARGETED renters above 50 pct of income` exactly:

| point | types | rebuilt from DIAG units | printed | gap |
|---|---|---|---|---|
| `point_1c4b7759d4` | 1 | 0.6702628 × 0.3830765 = 0.2567619 | 0.25676189 | 0 |
| `point_cd817d0401` | 1 | 0.6493436 × 0.4535204 = 0.2944905 | 0.29449053 | 0 |
| `point_02bb4b5ab3` | 1 | 0.6582479 × 0.4097756 = 0.2697340 | 0.26973395 | 0 |
| `point_f48e057502_frozen_beta` | 2 | 0.6731092 × 0.4085962 = 0.2750304 | **0.29960787** | **+8.9%** |

(The one-type points are identified by `MOMENT h_1` agreeing with `DIAG
homelessness rate rebuilt from the bands` to twelve digits; in the two-type point
those two differ, 4.1636e-3 against 4.0389e-3.)

The 8.9 per cent gap is larger than the in-place division alone can produce if
`mass_of_renters_1` retained its pass-1 value — that case predicts about 0.2 per
cent, since the renter mass is 0.996 of the total when only 0.4 per cent are
homeless — and it does not match the "starts at zero" case either, which predicts
0.55. So the measured value is evidence that `mass_of_renters_1` held an
**indeterminate** value on the second pass. I did not determine what.

**Live?** LIVE at two types. Affects `UNTARGETED renters above 30 pct` and
`above 50 pct` (5249, 5251), and the same in-place division at 12989 hits
`mass_of_homeowners_at_housing_spending`, and at 12968
`model_rent_burden_by_age`.

### F4. `MOMENT aleph` is a LEVEL, and the two-pass comment says to look for exactly this

Line 4790: `vsl_1 = model_value_of_life(1)/max(model_average_labour_income(1),…)`.

`model_value_of_life` is reset at 7296 and accumulated at 7533:

```fortran
                                            model_value_of_life(time_period)=model_value_of_life(time_period)+&
                                                (value_function_used/MU_1)*distribution_mass_used
```

and it is **never divided by any mass anywhere in the file** — grep gives exactly
those two lines plus the print. It is a mass-weighted *sum* of `V/MU_c`. The
denominator, `model_average_labour_income`, is divided by `model_total_workers`
at 9082, so it is a *mean*.

An aggregate over a mean is proportional to the total mass. The comment at line
33686 states the test: *"A LEVEL would come out doubled, which is why it is worth
checking that no targeted moment is one."* This one is. `model_value_of_life` is
owned by `stationary_equilibrium_statistics`, which is not among the routines
called after the loop, so it keeps two units of mass at print time and F1 does
not mask it.

**Target.** `vsl_data = 80`, and the declaration at 1857–1864 defines it as a
multiple of average labour income — "nine million dollars against a mean
household income of $113,000 is eighty times it". A per-household mean, not a
population aggregate.

**Live?** LIVE at two types.

**What it would change.** A factor of `number_of_beta_types`. Supporting but not
decisive: the only two-type point prints `MOMENT aleph = 162.0` where the four
one-type points sit at 52.8, 56.7, 58.2 and 60.9. Those are different parameter
points and aleph is sensitive to β, so this is consistent with a doubling rather
than a measurement of one.

### F5. `MOMENT cbar` is the second level moment, and it currently reads right only because F1 halves it

Line 5078:

```fortran
                govt_spending_on_food_stamps(1)/max(model_average_labour_income(1),10.d0**(-12))
```

`govt_spending_on_food_stamps` is an aggregate accumulated over the distribution
(11800); the denominator is a mean. Same shape as F4. The difference is that this
numerator IS one of the accumulators F1 refills from one type, so it presently
carries one unit of mass and the ratio happens to be a per-household mean over a
mean. Fix F1 without fixing this and `cbar` doubles.

`food_stamps_share_data = 0.0042` is described in DATA_APPENDIX.md as "USDA SNAP
average benefit against average labour income" — a mean, so the intended object
is `aggregate / total mass / mean labour income`.

**Live?** LIVE. Latent today, not latent after F1 is fixed.

### F6. `mass_by_age` is reset and accumulated in three routines in sequence — the DIAG age profile is divided by roughly twice the pooled mass

Reset and accumulated in `govt_revenues_calc` (10870, 11960), in
`calculate_welfare_by_characteristics` (13246, 13469) and in
`calculate_homeownership_by_characteristics` (14542, 15023), and those run in that
order inside the loop. All three resets are guarded to the first pass. So on pass
2 each routine adds another copy of the second type on top of what the previous
one left:

| after pass 2 | value |
|---|---|
| `govt_revenues_calc` | `M1 + M2` — correct, and it uses it correctly at 12284/12287 |
| `calculate_welfare_by_characteristics` | `M1 + 2·M2` — used at 13790 |
| `calculate_homeownership_by_characteristics` | `M1 + 3·M2` — used at 15253, 15261, 15264, 15267, 15270 |

The last of those is where **`homelessness_by_age` and `homeownership_by_age` are
normalised** (15270, 15261), and both are printed in this slice, in the age
profile at lines 5695–5703. With equal type masses the divisor is 2× the pooled
mass, so those two columns read **half** their true value; so do
`model_assets_by_age`, `housing_size_by_age` and `consumption_by_age`.

`mass_by_employment` has the same shape across four routines
(`stationary_equilibrium_statistics`, `govt_revenues_calc`,
`calculate_welfare_by_characteristics`, `calculate_homeownership_by_characteristics`),
and `mass_by_employment_and_age` across two.

**Live?** LIVE at two types. Derived, not measured — the one two-type point file
predates the age-profile block.

### F7. `mass_of_owners` is reset and accumulated in two routines — DEAD today, live the moment ownership is switched on

`stationary_equilibrium_statistics` resets at 7249 and accumulates at 8462;
`stationary_equilibirum_homeownership_rate`, which runs next, resets at 9138 and
accumulates at 9396. Same structure as F6 with two routines, so on pass 2 the
second sees `M1 + 2·M2` and

```fortran
9614:  model_homeownership_rate(time_period)=mass_of_owners(time_period)/sum_of_distribution_not_be_homeless
```

is inflated by about half the ownership rate, as are
`model_average_owner_occupied_unit_size`, `model_average_owners_income` and
`model_fraction_of_homeowners_with_mortgage`.

**Live?** DEAD in the benchmark: `include_homeownership = 0` (464) and
`max_amortization_years = 1` (3044), so `amortization_used >= 2` is never true and
`mass_of_owners` is identically zero. It becomes live in any run with ownership on.

### F8. `MOMENT omega` and the two price elasticities re-solve one type against a pooled baseline — dead by default

Lines 5390–5405 and 5470–5477 in this slice re-solve, re-converge, and call
`stationary_equilibrium_statistics(1)` and `govt_revenues_calc(1)` inside
`print_all_moments`, where `accumulating_beta_types` is 0 and `mass_passes` is 2.
That is F1 again: the counterfactual's `model_total_drug_users` is one type's
count over twice the mass, while `baseline_users_for_gap` / `val_users_base_1` was
captured from the pooled baseline. `MOMENT omega =
drug_users_without_child/baseline_users_for_gap - 1` therefore carries an
additional −0.5 and the participation elasticity carries an extra
`log(0.5)/log(1+step)`, which at `elasticity_price_step = 0.10` is about −7.3
against a target of −0.63.

Also, both counterfactuals solve at `discount_factor = discount_factor_patient_saved`
only, so even with the factor of two removed they are one-type experiments
compared with a two-type base.

**Live?** DEAD as declared: `measure_child_gap = 0` (318) and
`measure_price_elasticity = 0` (335), so both blocks print their SKIPPED line.
Live the moment either flag is turned on.

---

## Class 3 — a moment that does not measure what its target measures

### F9. `MOMENT y_u` puts an income concept WITHOUT capital income over one WITH it — LIVE and targeted

Line 5637:

```fortran
            write(*,*) "MOMENT y_u       income of drug users        model=",&
                model_avg_income_drug_users(1)/max(model_average_income(1),10.d0**(-14)),&
                " target=", drug_user_income_data
```

**Numerator.** `model_avg_income_drug_users` is accumulated at 11324–11325 with
`income_1`, which is what `calculate_income` returns (6809–6870): social security
in retirement, labour earnings when employed, and UI or DI otherwise.
**No interest income.**

**Denominator.** `model_average_income` is accumulated at 8521–8542 with the same
three cases and then, unconditionally, at 8542:

```fortran
                                    model_average_income(time_period)=model_average_income(time_period)+&
                                        risk_free_rate(time_period)*max(financial_grid(financial_index),0.d0)*&
                                        distribution_mass_used
```

So the denominator includes `r·max(a,0)` and the numerator does not. The
interest-inclusive object exists two lines above the numerator's accumulation —
line 11221, `income_2=income_1+risk_free_rate(time_period)*max(financial_grid(financial_index),0.d0)`
— and is used for the voucher eligibility test six lines further on, but not here.

**Why this is a mismatch and not a convention.** NSDUH's income variable is total
personal income, so the 0.740 target is the interest-inclusive ratio. And the
model's users are not asset-poor: `DIAG assets of drug users / average net worth`
prints 0.4589 at `point_cd817d0401`, so the omitted term is `r` times about half
of average net worth, against a wealth-to-output ratio of 3.97 in the same run.

**Same fault, same routine:** `UNTARGETED income with a SUD` (5641,
`model_average_income_addicted`, accumulated with `income_1` at 11925),
`UNTARGETED income of the homeless` (5575, `model_avg_homeless_income`, 11971),
`DIAG income of experimenters / average` (5648), `DIAG users band k income/average`
(5943, `val_user_inc_band`, 11353), `DIAG income of WORKING AGE drug users`
(4927, `val_user_income_working`, 11363). The buyer/non-buyer income DIAGs
(11382, 11389) use `income_1` on both sides so their ratio is consistent.

**Live?** LIVE in the benchmark. `y_u` is targeted, with `kappa_phi_d_level` as
its instrument.

**What it would change.** `y_u` rises by `r × (mean assets of users) / (mean
income)`. Not measured — `model_average_income` is not printed, so I could not
compute the term from a point file, and the brief says not to guess a number I
have not computed. The direction is unambiguous and it is the direction of the
reported failure (0.33 to 0.47 against 0.740).

### F10. `MOMENT kappa_ued` counts retirees on both sides, where `MOMENT pi_eu` two lines above does not

The code fixed this fault for the unemployment rate and left it in the
disorder-conditional one. Line 7601, in `stationary_equilibrium_statistics`:

```fortran
                                    ! UNEMPLOYMENT IS A WORKING AGE STATE. Retirees keep
                                    ! whatever employment index they carried in, and the
                                    ! retirement transition is absorbing, so without this
                                    ! guard they were counted in every employment moment
                                    ! below. Most of them carry emp_of 1 …
                                    if ((emp_of(unemployment_index)>1) .AND. (in_retirement==0)) then
                                        model_fraction_unemployed(time_period)= …
```

and at 8871 that is divided by `model_mass_total_raw`, the working-age base.

`model_fraction_addicted_and_unemployed` (line 7695) sits in a different block
with **no `in_retirement==0` guard**:

```fortran
                                        if ((sud_of(unemployment_index)==1 .AND. emp_of(unemployment_index)>1)) then
                                            model_fraction_addicted_and_unemployed(time_period)=&
                                                model_fraction_addicted_and_unemployed(time_period)+distribution_mass_used
```

and at 8881 it is divided by `model_fraction_addicted`, which at that point is the
**all-ages** mass of households carrying the disorder (7688; it is normalised on
the next line, 8884).

**Target.** `unemployment_rate_sud_data = 0.1625`, DATA_APPENDIX.md line 112:
"NSDUH 2024, adults 26 and over with a past year disorder" — an unemployment
rate, so a labour-force concept on both sides.

**Live?** LIVE, targeted, `κ_ued`'s own moment. `pi_eu` and `kappa_ued` are the
pair that identifies `κ_ued`, and they are not the same statistic.

**What it would change.** Unknown; it depends on the retired share of the
disorder-carrying mass, which is not printed. The file's own note at 7833 says
"about thirty per cent of the model's homeless are retired", so the retired share
is not negligible.

### F11. `MOMENT kappa_uem` counts retirees as employed

Line 5061 prints `model_employment_rate_given_smi`, built at 8938 as
`model_smi_and_employed / model_mass_smi`. The numerator (7673) fires on
`emp_of(unemployment_index)==1` at **every age**, and the denominator (7666)
counts SMI households at every age. Per the comment quoted in F10, retirees keep
the employment index they carried in and most carry `emp_of` 1, so they enter this
numerator as employed.

**Target.** `employment_rate_given_smi_data = 0.30`, DATA_APPENDIX.md line 158:
"the midpoint of the employment range for high disability diagnoses in the
clinical literature: roughly a fifth of people with schizophrenia are in work".
That is a working-age employment rate.

**Live?** LIVE, targeted. `kappa_uem` also enters `employment_transition` (6536),
so it is not a reporting-only parameter.

The `UNTARGETED participation, with/without a SUD` rows immediately below (5270,
5273) get this right and say why, at 11058–11073: NSDUH's 65.8 and 61.5 are
participation among adults 26 and over including the retired, so the all-ages
denominator is the matching one, and the working-age version is kept separately as
a DIAG. That reasoning was applied there and not to `kappa_ued` or `kappa_uem`.

### F12. `MOMENT theta`'s two halves use different income denominators

`weighted_drug_share_now()` (5710–5761, in this slice) mass-weights
`model_experimenters_total_drug_spending_to_total_income` and
`model_addicted_total_addiction_spending_to_total_income`. Their denominators are
built differently:

- experimenters, line 11458: `model_experimenters_total_income += income_2 * mass`,
  where `income_2` is the one assigned at 11221, `income_1 + r·max(a,0)`;
- addicts, line 11650: `income_2` is **reassigned** to
  `income_1 + r·max(a,0) + bequest_1` immediately before
  `model_addicted_total_income += income_2 * mass`.

So one half of the weighted average is a spending share of income including the
bequest received and the other is not. `drug_spending_share_data` is one number;
the model quantity is a weighted average of two differently defined ones.

**Live?** LIVE, targeted, `theta`'s own moment.

**What it would change.** Unknown; it is the size of `bequest_1` relative to
income for households carrying the disorder, which is not printed.

### F13. Four documents disagree about what `MOMENT h_2` is

Line 4859 prints `val_burden50_expend_all/val_mass_expend_all` — the share of ALL
households paying more than half of TOTAL EXPENDITURE on housing — against
`severe_cost_burden_data`. What that constant is:

- **the declaration** (1481–1499): *"0.101 is SCF 2022, ALL households, owners
  and renters together, housing cost above half of **income**. Owner cost is
  SCF's pirmort … Renters alone give 0.181 and owners alone 0.025."*
- **the print block** (4844–4857): *"gamma's 26.8 per cent is CEX shelter and
  utilities over TOTAL EXPENDITURE and the 10.1 per cent beside it is the share
  of households paying more than half of TOTAL EXPENDITURE on housing, from the
  same survey."*
- **`data/DATA_APPENDIX.md` line 337**: *"h_2, the smallest rental size — a 50
  percent employment rate among the homeless … The moment is not a size share."*
- **`writing/housing_first_children_later.src.tex` line 2615**: *"h_2, the
  smallest rental size … its value is chosen so the model generates the
  `@@q_h_2@@` percent of housed households living in the smallest unit size in
  the 2023 ACS, Table B25042"*, and `q_h_2` resolves to 13 in
  `code/paper/params_numbers.json`.

The declaration and the print block cannot both be right about the same constant:
one says SCF and income, the other says CEX and expenditure. **If the declaration
is right, the model quantity was moved onto an expenditure denominator to match a
target measured on income** — which is the calibration error the brief cites as
its example, inverted. The appendix and the paper describe two further, different
moments for the same parameter.

**Live?** LIVE, targeted, and it is the moment the smallest rung is calibrated on.

**What it would change.** The gap. `MOMENT h_2` reads 0.0402–0.0524 against 0.101
in the point files; the income-based counterpart the same routine computes,
`UNTARGETED renters above 50 pct of income`, reads 0.257–0.300. Swapping which
one is scored moves `h_2` from far below target to far above it.

### F14. `UNTARGETED housing over income, renters` is a mean of ratios compared with a ratio of means

Line 5045 prints `model_avg_housing_spending_renters` against 0.202. The comment
80 lines above, at 4880–4890, states the objection against `gamma` and it applies
unchanged here:

> *"gamma is model_avg_housing_spending_renters, a mass weighted mean of household
> RATIOS, and a mean of ratios is not the ratio of the means whenever the two are
> correlated … A data figure built as total rent over total income has to be
> compared with this line and not with gamma."*

0.202 is described at 5036–5041 as "CEX's income based figure for the same
numerator", i.e. aggregate shelter and utilities over aggregate income, over CEX
consumer units. The model row is a mean of household ratios over housed renters.
Two mismatches: the kind of average, and the universe. `DIAG aggregate rent /
aggregate income` at 4891 is the line that matches 0.202's construction; it is
printed as a diagnostic with no data value beside it.

**Live?** LIVE but UNTARGETED — it is reported, not scored.

### F15. `UNTARGETED renters above 30/50 pct of income`: the model universe is every housed renter, the data universe is not

Lines 5249–5251 print over all housed renters at every age.
`data/DATA_APPENDIX.md` line 715 says of 40.6 and 17.5: *"The universe is renters
with positive income and positive rent, dropped of homeowners, and restricted to
the 80th to 100th percentile band of the income CDF used in that script"*, and
notes the ACS figures for the same concept are 49.5 and 26.5 — a different pair
again.

The code comment at 5245 says "The universe is renters, which is the SCF universe
the appendix derives 40.6 and 17.5 on", which is true of the tenure restriction
and not of the positive-income, positive-rent or percentile-band restrictions.

**Live?** LIVE, UNTARGETED. Note that F3 also hits these two rows.

### F16. The HUD homelessness bands start at 25, the model's start at 26

`val_hud_rate_1` and `val_hud_share_1` (4783–4787) are read straight from
`data/us_homeless_by_age.csv`, whose first row is `25,34`. The model's band 1 is
`age_index<=9` (15036), and model age 1 is data age 26 (the mean-age accumulator
at 11335 uses `25 + age_index`), so it is a nine-year band 26–34 against a
ten-year band 25–34. The comment at 5688 refers to the band as "25 to 34". The
top band is HUD's 65–84 against the model's 65 to `25+life_span`.

**Live?** LIVE, UNTARGETED, five rows of the validation table.

**What it would change.** About a tenth of band 1's width, so of order ten per
cent of its rate, with the profile normalisation absorbing part of it. Not
measured.

---

## Class 2 — dead code that looks live

### F17. `calculate_cdf_of_incomes_earned` is never called on the benchmark path

The only call is line 14572, inside `calculate_homeownership_by_characteristics`:

```fortran
        if (simulation_ended==(compute_income_cdf+(1-compute_income_cdf)*1)) then
            if (is_counterfactual==0) then
                call calculate_cdf_of_incomes_earned(time_period,life_span)
```

`compute_income_cdf = 0` (1203), so the test is `simulation_ended == 1`.
`simulation_ended` is set to 1 once, in the main program at 6660, and then
`calibrating_model` sets it to 0 at its first executable statement, line 33175,
and never sets it back (the other writes inside it, 36570 and 36644, are also 0).
So the routine — 300 lines of this slice — never runs during a calibration or a
point run, and neither do the two other blocks under the same guard, at 14722 and
15282. Every income-quintile statistic (`model_drug_use_by_income_quintile`,
`MID_share_by_income_quintile`, `rent_burden_by_income_quintile`,
`tenure_by_income_quintile`) is therefore built on a CDF that was never computed.

### F18. When it does run, it clobbers the module-scope `sum_of_distribution` with a single distribution cell

Line 7029, inside `calculate_cdf_of_incomes_earned`:

```fortran
                                    sum_of_distribution=distribution_stationary(years_left_on_mortgage_index)%&
                                        vector_transition_real(time_period_used,age_index,financial_index,&
                                        unemployment_index,employment_index,housing_status_index,voucher_index)
```

`sum_of_distribution` is module scope and is the pooled total mass that a dozen
routines divide by. Used here as a scratch scalar for one cell's mass, it is left
holding that cell when the routine returns. The routine is called from the eighth
of the nine chain routines, and the ninth
(`stationary_equilibrium_wealth_distribution_of_old`) does not recompute it, so
the next reader is line 36126:

```fortran
            write(*,*) "fraction of hhlds who make it to the highest net wealth=", mass_at_top_financial/sum_of_distribution
```

which would print a ratio against one cell. Line 36178 (F1) recomputes
`sum_of_distribution` before `print_all_moments`, so the two mass DIAGs at 5669
and 5671 are not reached by this.

**Live?** Latent, because of F17. It becomes live wherever `simulation_ended`
is 1 — the counterfactual path sets it at 37334.

### F19. `calculate_income`'s `avg_income_to_use_2` is `intent(in)` and never read

Lines 6809–6870. The dummy appears in the argument list and the declaration and
nowhere in the body. Every call site computes it: `calculate_household_housing_spending`
builds it at 12680 inside the voucher loop, `govt_revenues_calc` and
`stationary_equilibrium_statistics` likewise, and
`calculate_cdf_of_incomes_earned` builds `avg_income_to_use_2` for the same
purpose.

### F20. `model_average_income_plus_assets` is assigned, not accumulated

Line 8546, inside the household loop of `stationary_equilibrium_statistics`:

```fortran
                                    model_average_income_plus_assets(time_period)=model_average_income(time_period)+&
                                        (bequest_2+max(financial_grid(financial_index),0.d0))*distribution_mass_used
```

`=`, not `+=`. After the loop it holds the running total of `model_average_income`
plus **one cell's** assets, and line 9084 divides that by `sum_of_distribution`.
`model_average_income_plus_all_assets` is built from it five lines later (8551,
8558) and inherits the fault.

**Live?** LIVE, and not inert: `model_average_income_plus_all_assets_previous` is
the denominator of `income_to_avg_income` at 7898 and 7905 under
`use_income_or_income_plus_assets==4`, which the comment at 7881 identifies as
"the live flag". So a numerator that includes assets is divided by a denominator
that is, in effect, mean income alone. Not printed in the moments block; it feeds
`income_to_avg_income_wide_pdf_1` and the income-profile files.

### F21. Two more locals with guarded resets, and a dead sub-expression

- `sum_of_distribution_1` and `sum_of_distribution_2` in
  `calculate_cdf_of_incomes_earned` (declared 6880, reset at 6887 and 6896 under
  `if (accumulating_beta_types==0)`) are non-`SAVE`d locals, the same hazard as
  `mass_of_renters_1` in F3. `sum_of_distribution_1 == sum_of_distribution_2` at
  7063 is the loop's early-exit test, so an indeterminate value there either exits
  the whole age loop early or never exits it.
- Line 4874, the DIAG unit denominator, carries
  `mass_of_renters_at_housing_spending(1,1)*0 +`, which is a leftover with no
  effect. Harmless, but it reads as though the two objects are related.

---

## Class 4 — the ordinary Fortran hazards

### F22. Three unguarded divisions that are 0/0 in the benchmark

- 12989: `mass_of_homeowners_at_housing_spending(time_period,i)/mass_of_owners_with_mortgage(time_period)`.
  With `include_homeownership = 0` and `max_amortization_years = 1` there are no
  owners, so `mass_of_owners_with_mortgage` is identically zero and this is 0/0.
  The result is written to stdout and to `percentage_spending_on_housing*.txt` at
  13000 and 13014. Every other division in the same block carries a
  `max(...,10.d0**(-14))`; these do not.
- 12968: `model_rent_burden_by_age/mass_renters_by_age`, unguarded, at any age
  with no renters.
- 15277: `MID_share_by_income_quintile/total_MID_value` and 15280
  `MID_itemizers_by_income_quintile/mass_by_income_quintile`, both unguarded and
  both zero under F17.

### Smaller, reported for completeness

- The NSDUH income-band loop (5127–5147) advances with `k_1=min(k_1+1,7)` and
  prints inside the same test, so once the cumulative share passes
  `nsduh_band_cum(7)` every remaining bin prints another "band 7" line; and if
  the walk reaches `i==income_bins` at band `k` the bands above `k` never print
  at all. A diagnostic, not a moment.
- `size_of_quintile=real(1)/real(number_of_quintiles)` at 6880 evaluates in
  default (single) precision before being stored in a `real(8)`. It is a quintile
  cut point, so the error is about 1e-9 — noted, not a finding.

---

## Where I found nothing

- **`compute_asset_lottery` (6165–6325).** The three-point vertex is the correct
  general (unequally spaced) formula: with `d1=(y1−y0)/(x1−x0)`,
  `d2=(y2−y1)/(x2−x1)` and `c=(d2−d1)/(x2−x0)`, the Newton form gives
  `x* = (x0+x1)/2 − d1/(2c)`, which is line 6295 exactly. The lottery weight puts
  the mean of the two-point lottery on the vertex in both branches. Its
  inertness, the refusal branches and the counters are all documented at 6165.
- **`employment_transition` (6506–6597).** The three destinations sum to one in
  every current state, including the `ui_first_period_only` branch where `e_c=3`
  cannot return to 3.
- **`survival_with_smi`, `recovery_with_smi`, `smi_transition`,
  `addiction_transition`, `addiction_onset_hazard` and its slope,
  `lognormal_tail_mean`, `normal_cdf`, `normal_quantile`, `out_of_work_income`,
  `sud_of`, `emp_of`, `idx_of`, `b_shifter`, `survival_sud_of`.** All have
  `implicit none`, all bounds are clamped where the index can leave the grid
  (`min(max(age_1,1),life_span)` at 6488), and the oddities — `b_shifter`
  ignoring both of its arguments, `survival_sud_of` ignoring `treatment_1` — are
  the ones the comments explain as deliberate.
- **`move_factor`, `trust_step`, `damp_on_flip`, `apply_gamma_tie`,
  `weighted_drug_share_now`, `set_files_names`.** Nothing found beyond F12, which
  is about what `weighted_drug_share_now` is handed rather than what it does.
- **`MOMENT beta`, `MOMENT omega_l`, `MOMENT tau_l`, `MOMENT h_3`,
  `MOMENT lambda_d`, `MOMENT p_m`, `MOMENT lambda_m`, `MOMENT sigma_y`,
  `MOMENT w_bot`, the wealth and income share rows, the five age-band rows, the
  three TEDS-A rows, the two earnings tenths.** Each is a ratio of two aggregates
  or two masses accumulated in the same loop nest over the same set, so the pass
  count cancels; the universes match the targets as the comments describe. `h_3`
  in particular conditions on being housed (9529: over `renters_by_rental`), which
  is the ACS occupied-units universe the declaration at 1475 names.
- **`MOMENT h_2`'s own construction.** The expenditure denominator at 12854–12888
  is built correctly: `policy_function_total_consumption` is net of rent, mortgage
  cost, property tax, depreciation and `cost_of_housing` (20421–20432), so adding
  the housing outlay back gives total expenditure without double counting, and the
  outlay is net of the voucher on both sides. The all-households-versus-CEX
  -consumer-units choice is stated in the comment. The problem with `h_2` is its
  target (F13), not its numerator.
