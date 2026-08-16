# The Fortran against the written model, parameter by parameter

`housing_first_or_treatment_first_SR_v1.f90`, 24,868 lines, against Section 2 of
`writing/stylized_note.src.tex` and the two tables it prints.

The verdict up front: **the two are not the same model, and the gap is bigger
than a parameter audit.** Three things the note describes do not exist in the
code at all, three things the code does are not in the note, and one thing the
note explicitly denies is what the code does. Everything below is checked
against the source rather than against a previous summary.

Read the sections in order. The first is what has to be decided before any
number is regenerated; the rest is arithmetic.

---

## 1. In the note, absent from the code

### 1.1 Serious mental illness. Absent entirely.

`grep -ci mental` returns **zero**. There is no `m` anywhere: not in the state,
not in the transitions, not in survival, not in utility.

The note has `m` as a state variable in equation (13), a subsection of its own,
and six separate channels running through it: `rho_m` in income, `kappa_uem` in
both employment margins, `kappa_phi_m` in survival, `mu_m` in recovery,
`rho^b_m` in the Stone-Geary shifter, and `zeta_DI` in disability eligibility.
The internal table calibrates four of them and the external table assigns three
more.

The state space in the code confirms it. `unemployment_grid_size = 6` and the
comment at line 569 says it is employment crossed with the disorder: three
employment states times two disorder states. There is no room for `m` in it.

**This is a decision, not a fix.** Either the note drops mental illness or the
code gains a state variable, and the second doubles the state space. See
Section 5 for what that costs.

### 1.2 Disability income. Absent entirely.

`grep -ci disability` returns **zero**. `calculate_income` at line 1678 has
exactly four branches: social security in retirement, labour income when
employed, the insurance benefit in the first year of a spell, and zero
otherwise. The note's `zeta_DI * ybar_DI * Ybar` case for `e=3, m=1` has no
counterpart, which follows from `m` not existing.

### 1.3 The drug market. Declared, never cleared.

`price_of_addictive_good` is set once at line 343 and **never assigned again**.
The only other occurrences are `write` statements. There is no supply curve, no
`psi_1`, no `psi_2`, and no market clearing loop.

So the note's Section 2.12, the cost function `C(V)`, the elasticity of 2, the
normalisation of `psi_1`, and item 4 of the stationary equilibrium definition
describe machinery that is not there. The price is fixed at 1 in every run.

This one is cheap to add and it is what the revision's supply elasticity
discussion rests on, so it should be added rather than removed from the note.

---

## 2. In the code, absent from the note

### 2.1 Homeownership, mortgages and a housing market.

The note says the household rents, chooses from a four point grid with `h_1`
homelessness, and that `p_h` is normalised to one. The code has all of the
following, all live:

| Object | Where |
|---|---|
| `owners_problem`, `owner_owner_stay_problem`, `owner_owner_move_problem`, `owner_renter_problem`, `renter_to_owner_problem` | five subroutines, ~2,500 lines |
| `mortgage_amortization = 30`, `minimum_downpayment = 0.2`, `only_LTV = 1`, `max_amortization_years = 2` | mortgage contract |
| `negative_financial_grid_size = 61` | the debt side of the asset grid |
| `cost_of_selling = 0.06`, `fixed_cost_to_moving = 0` | transaction costs |
| `smallest_index_for_purchase = 5`, `size_of_smallest_house_hhld_can_buy = 0.23` | the ownership margin |
| `stationary_equilibirum_homeownership_rate`, `calculate_homeownership_by_characteristics` | reporting |
| `calibrated_stationary_housing_price = 13`, `rent_calibrated = 1.079`, `convexity_of_rental_company = 2.35`, `empirical_housing_supplpy_elasticity = 0.9` | an endogenous house price and rent, cleared in the outer loop |

`housing_status_grid_size = 7` with `lowest_housing_grid_point = -1`, so the
housing index runs `-1 .. 6`: **eight statuses**, against the note's four.

The revision removes all of this. Until it is removed the code is solving a
different model, and it is where most of the run time goes.

### 2.2 The Cobb-Douglas weights move with the disorder.

This is the one place the note asserts the opposite of what the code does.

> "The Cobb-Douglas weights themselves are held fixed across the disorder: only
> the shifter moves." — Section 2.2

The code, in `calculate_flow_utility` at line 11845, takes the
`include_probability_of_becoming_addicted` branch, which selects between two
complete sets of weights on `unemployment_index > threshold_addiction_index`:

| | clean | with the disorder |
|---|---|---|
| drugs | `relative_share_of_addiction_1 = 0.13` | `relative_share_of_addiction_2 = 0.45` |
| housing | 0.278 x (1 - 0.13) = 0.242 | 0.278 x (1 - 0.45) = 0.153 |
| consumption | 0.722 x (1 - 0.13) = 0.628 | 0.722 x (1 - 0.45) = 0.397 |

Each column sums to one, so the functional form is the note's. What is not the
note's is that the weight on drugs **more than triples** with the disorder,
under the switch `change_utility_for_addicts = 1`. That is a preference change,
not a Stone-Geary shifter, and it is a much stronger mechanism than `b_1`.

Either the note is wrong about its own model or the switch should be zero. It
matters for the paper's claim that addiction is transmitted without transmitting
a preference for drugs.

And the mirror image holds for the shifter the note says does move.
`addiction_scalar_2 = addiction_scalar_1` at line 354, so **`b_1 = b_0`
exactly**: the Stone-Geary endowment does not vary with the disorder at all. The
note calibrates `b_1` separately, against abstinence among homeless adults with a
SUD from Milby et al.'s no housing arm. So on both halves of Section 2.2 the code
does the opposite of what is written: the weights move and the shifter does not.

### 2.3 Bequests are redistributed, not confiscated.

> "Estates accrue to the government rather than being redistributed as a lump
> sum, because a uniform transfer to the poor has welfare consequences of its
> own that would contaminate every policy comparison." — Section 2.10

`include_bequests = 1`, and `inheritance_amount` is a vector over
`number_of_inheritance_ages = 60` that is **updated in the outer equilibrium
loop** (lines 22692 and 22795) with its own stopping rule
`stopping_rule_inheritance_amount`. `inheritance_function_of_productivity = 1`,
so the transfer is conditioned on productivity as well. Households receive
inheritances; the government does not keep them.

The note's paragraph is a description of a model the code does not solve.

### 2.4 Homelessness enters three of the four equations, not four.

> "Homelessness then enters four separate equations: survival, the employment
> transitions, the recovery hazard and the Stone-Geary shifter." — Section 2.5

Three of the four are there:

| Channel | Code | Effective size |
|---|---|---|
| survival | `increased_risk_of_death_homeless = 0.6` | death hazard x 1.6, flat in age |
| employment | `increased_prob_if_homeless = 0.2` at line 17107 | job finding / 1.2, separation x 1.2, so `kappa_ueH` = 0.833 against the note's 0.80 |
| recovery | `probability_of_stopping_addiction_if_homeless = (1/6) x 0.025` | `mu_H` = 0.167, set rather than calibrated |
| Stone-Geary shifter | **absent** | `b` is selected by the disorder index alone, never by housing |

So `rho^b_H`, which the note calls one of the four channels that make
homelessness and the SUD mutually reinforcing, does not exist. The loop the note
describes runs on three legs.

---

## 3. Where both exist and the numbers disagree

Checked against the tables as they now print.

| Symbol | Note | Code | Verdict |
|---|---|---|---|
| assets | 50 points, non negative | `positive_financial_grid_size = 50` **plus** `negative_financial_grid_size = 61` | the 50 is right, the 61 is mortgage debt and goes with ownership |
| productivity | 7 points | `employment_grid_size = 9` | code to be cut to 7; the budget's 1.3x assumes it |
| housing | 4 points | 8 statuses, `-1 .. 6` | see 2.1 |
| `j_R` | retire at 41 | `life_span = 60`, `retirement_span = 20` | agrees |
| `pi_UI` | gone, insurance certain | `probability_of_ui = 1.0` | agrees, and the note is now correct |
| `varrho_UI` | 0.50 | `replacement_rate_ui = 0.5` | agrees |
| cap on the benefit | `bar u` = 1.00 of average income | `max_ui_as_perc_of_avg_inc = 1` | agrees, and the note now shows the cap |
| `bar_pi^ue` | 0.55, Krueger et al. | `probability_becoming_employed = 0.297` | **disagrees**, code is 46 per cent lower |
| `bar_pi^eu` | calibrated to unemployment 4.9 per cent | `probability_becoming_unemployed = 0.0155` | plausible, verify against the moment |
| `kappa_ued` | calibrated to unemployment given a SUD, 16.25 per cent | `multiple_of_probabilities_of_employment_if_addicted = 2.7` | set, not calibrated |
| `kappa_phi_d` | mortality multiplier, SUD | `increased_risk_of_death_addicted = 6.9` | **the effective ratio is 7.9**, see below |
| `kappa_phi_H` | 4.41 at 26 falling to 1.09 at 80 | `increased_risk_of_death_homeless = 0.6`, flat | **disagrees**: flat, and an effective 1.6 |
| homeless and SUD together | multiplicative in the note | `0.6 + 6.9`, additive | **disagrees in functional form** |
| `bar_pi_r` | 0.025 a year | `probability_of_stopping_addiction = 0.025` | agrees |
| `mu_H` | calibrated to the SUD share of the homeless, 21.7 per cent | `= 1/6` exactly | set, not calibrated |
| `pi_d` | calibrated to the SUD rate, 3.68 per cent | `probability_of_becoming_addicted_if_experiment = 0.037` | agrees |
| `chi_D` | 0.212 | `addict_cost_govt_as_perc_of_avg_inc = 0.212` | agrees |
| `chi_H` | 0.4286 | `homeless_cost_govt_as_perc_of_avg_inc = 0.252` | **disagrees**, the note took the literally homeless figure and the code did not |
| `xi` | 0.85 | `curvature_of_labor_income_taxes = 0.85` | agrees |
| `tau_k` | 0.15 | `investment_income_tax = 0.15` | agrees |
| `kappa_V` | 0.50 of median | `threshold_income_vouchers = 0.5` | agrees |
| `kappa_r` | 0.30 | `rent_to_income_ratio_vouchers = 0.3` | agrees |
| `pi_V` | 26.6 per cent of the eligible | `probability_of_voucher_benchmark_used = 0.06` | different objects; the 0.06 is a per period draw and has to be shown to deliver the 26.6 |
| `sigma` | 2.0 | `risk_aversion_consumption = 2` | agrees |
| `delta_d` | 0.30 | `penalty_child_addicted = 0.30` | agrees |
| `delta_h` | 0.31 | `penalty_child_homeless = 0.31` | agrees |
| `omega` | 0.014 | `weight_on_child = 0.0137` | value agrees, **but see 4** |
| homelessness target | 0.399 per cent | `fraction_homeless_data = 0.0045` | **disagrees**, code targets 0.45 |
| `p_det`, `p_fp`, `p_test`, `c_test` | four parameters, swept | none exist | conditionality is perfectly enforced in the code |
| `kappa_x`, `omega_x` | removed from the note this revision | never existed in the code | now consistent |

### The mortality multiplier is 7.9, not 6.9

At line 16620 survival is built as

    survival(:,1,addicted) = survival(:,1,0) - k * (1 - survival(:,1,0))

so the death probability is `(1 + k)` times the baseline, and with `k = 6.9` the
effective mortality rate ratio is **7.9**. The parameter is named as an increase
and behaves as one. If 6.9 is meant to be the rate ratio from Hjorthoj, the
constant should be 5.9. The same reading applies to homelessness: `0.6` is an
effective 1.6, and the joint case `0.6 + 6.9` is an effective 8.5, additive
where the note's equation (24) is multiplicative.

This matters beyond the code: the stylized model's `kappa` was just derived from
a rate ratio of 6.9. If the full model's intended ratio is 7.9 the stylized
`kappa` is 0.4818 rather than 0.4302. One line, and the two should agree.

---

## 4. The child, and where it enters

`weight_on_child = 0.0137` is **declared at line 155 and never read**. The only
use of the child anywhere in the code is at line 16795, in
`newborn_employment_probability`, where the parent's disorder and homelessness
shift the newborn's productivity draw:

    penalty = (1 - penalty_child_addicted)^d * (1 - penalty_child_homeless)^(h-1)

That is equation (26) of the note, and it is correct. What is missing is the
other half: the household does not value the child at all, so `omega` is
effectively zero and the damage is entirely external.

`include_bequest_motive = 0` switches off `calculate_bequest_utility`, which is
the only place a `(1 - survival) x weight x value` term appears. Its shape is
already what is wanted,

    bequest = (1 - survival(age, homeless, addicted)) * discount_factor_on_child * u(wealth)

but it values *wealth left behind*, not the child's lifetime value, and it is
off.

So the revision's requirement, that the child enter the continuation at every
age weighted by the probability of death and by `omega`, is **not implemented**.
The hook exists and is switched off; what has to change is that it takes
`E V_1(0, y_child, ...)` in place of `u(wealth)`, and that `weight_on_child`
becomes the weight on it.

---

## 5. What this costs, and how long a calibration takes

`CALIBRATION_BUDGET.md` gets **15 hours on four cores, about 1.5 on forty**,
from five factors against the measured 51 minute backward pass:

    asset grid 90 to 50        3.2x
    housing state removed      2x
    owner branch removed       2x
    housing choice 7 to 3      2.3x
    income grid 9 to 7         1.3x
                              38x    ->  80 seconds a pass
    550 evaluations x 1.2 x 80 s   =  15 hours on four, 1.5 on forty

Every one of those five is a removal from Section 2.1 or Section 3 of this audit,
so the figure stands only if the code is cut to what the note describes.

**The drug price loop is not a cost.** The price is normalised to one at the
benchmark quantity through `psi_1`, so during the calibration it is fixed at one
and the market never has to be cleared. The budget's 2x for "no drug price loop"
therefore stands as written, and the supply curve is needed only where quantity
moves away from the benchmark, which is the counterfactuals. That is where it has
to be built, and it does not touch the fifteen hours.

**The employment dimension stays at three.** The budget considered cutting it to
two, worth 1.5x, and rejected it: one year of unemployment on a fifty per cent
replacement rate is not what costs a household its housing, long spells are. The
fifteen hours already assumes three.

**Mental illness roughly doubles it.** `unemployment_grid_size` goes from 6 to 12,
which doubles the outer loop of the backward induction. It does not double the
inner cost as well, because `hoist_expectation = 1` builds the expectation once
per age rather than inside the `a'` search, so the shock dimension enters the
table build and not the quadratic part. Call it **2x: 30 hours on four cores,
about 3 on forty.**

**The asset grid is the lever that pays for it, and the one to be careful with.**
The `a'` search is quadratic, so against fifty points

    40 points   1.56x    ->  19 hours on four,  1.9 on forty
    35 points   2.04x    ->  15 hours on four,  1.5 on forty
    30 points   2.78x    ->  11 hours on four,  1.1 on forty

so **thirty five points cancels mental illness exactly** and returns the whole
budget to where it was. But it is the one cut the budget document tells you not
to make casually, and the reason is specific rather than general: the objective is
not single peaked in `a'`, because voucher eligibility is a step function of
income which includes `ra`, the food stamp floor kinks, and housing is discrete.
Coarsening the grid coarsens precisely the dimension carrying the notches. The
fifty point choice is already flagged there as the one judgement rather than a
deduction, to be validated by solving the benchmark at fifty and at ninety and
comparing the targeted moments and both counterfactuals. Any further cut needs the
same validation against fifty, and it is cheap to run once the model is cut down.

One separate correction. `PERFORMANCE_NOTES.md` section 4 and the closing
section of `TIMING.md` both still say the expectation hoist is worth 10 to 50x.
`hoist_expectation = 1` is in the code, it was verified bit identical, and it is
worth about one per cent. Both documents should say so; the budget above does
not depend on it.

---

## 6. What to do, in order

1. **Remove homeownership.** Five subroutines, the mortgage contract, the
   negative asset grid, the house price loop, and four of the eight housing
   statuses. This is where the 38x lives, and it comes first for a practical
   reason: until it is done every test run of anything else costs the full 51
   minute pass rather than 80 seconds. Cut the model down, then grow it.
2. **Decide on `change_utility_for_addicts`.** The code triples the weight on
   drugs for a household with the disorder while the note says the weights are
   fixed. This is the one outright contradiction and it bears on the paper's
   central claim.
3. **Add mental illness.** Decided: it stays in the model, so the code gains it.
   `MENTAL_ILLNESS_PLAN.md` is the sequence, the index design and the measured
   count of touch points. It doubles the state space, which the asset grid can
   buy back if that cut validates.
4. **Add the drug supply curve, for the counterfactuals only.** The price is one
   at the benchmark by the normalisation of `psi_1`, so the calibration never
   clears the market and this costs nothing there. It is needed where quantity
   moves away from the benchmark, and the revision's elasticity discussion has
   nothing behind it until it exists.
5. **Wire up the child.** `calculate_bequest_utility` is the hook; it needs the
   child's value rather than wealth, and `weight_on_child` needs to be read.
6. **Reconcile the numeric disagreements in Section 3**, of which
   `bar_pi^ue` at 0.297 against 0.55, `chi_H` at 0.252 against 0.4286, the
   homelessness target at 0.45 against 0.399, and the mortality ratio at 7.9
   against 6.9 are the four that change results rather than wording.
