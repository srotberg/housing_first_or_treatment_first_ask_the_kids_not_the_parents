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

### 1.4 The homelessness disamenity. Absent entirely.

`grep -n "kappa_x\|disamenity\|aggregate_homeless"` returns **zero**. Section 2
of the note now prices a disamenity from aggregate homelessness, calibrated to
Loubiere et al.\ (2020), and says it is the only place where a household's
utility depends on an aggregate and hence what makes `H` a genuine fixed point.
None of that is in the code.

It was dropped once and brought back deliberately, so this is a gap to close
rather than text to delete. Three things it needs:

* an aggregate `H` computed from the distribution each equilibrium iteration,
  **on the headcount alone**. Not weighted by the SUD, and not counting only the
  homeless who carry one: the contingent valuation asked what people would pay
  to end homelessness, so that is what may be priced.
* a `- kappa_x * H` term in flow utility, identical across households, which is
  what makes it a pure externality rather than a preference.
* `kappa_x` set so that households would pay 0.08 per cent of average annual
  earnings to move `H` to zero, with 0.20 per cent as the top of the reported
  range.

It is small by construction and cannot decide a ranking on its own, so it is not
urgent. But the note asserts it, so either the code gains it or Section 2 loses
the passage, and the first is the intent.

### 1.5 Two calibration targets have their adjusters switched off.

`size_homelessness_adjuster` and `smallest_house_size_adjuster` are both **zero**
in the original source, so the update lines that read

    size_homelessness = size_homelessness - adjuster*(model - data)

subtract zero and the parameters never move. The homelessness rate and the share
of renters spending above half of income are listed as targets in the note's
internal table, and neither was being iterated: they were reached by hand between
runs.

That was workable while the rental grid was stable. It is not now. Taking the
mortgage eligibility overwrite out of `housing_size` (item 2.5) moved the
smallest rental, so the hand set `size_homelessness = 0.21` leaves homelessness at
0.007 per cent against a target of 0.399.

`size_homelessness_adjuster` is now **20**, which moves the parameter about 0.08
per iteration at the current gap and crosses its `[0,1]` range in roughly a dozen
equilibrium solves. The sign was already correct.

`smallest_house_size_adjuster` is **left at zero for now**, deliberately: it moves
homelessness too, and turning both on in the same sweep lets them fight over the
same moment. It should be switched on afterwards, once the street is settled, and
bracketed on the share of renters spending above half of income.

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

**Switched off.** Ownership is now unreachable at the three places that led to
it, rather than deleted, so the change is one line to reverse and the owner code
is still there to read:

| Switch | Was | Now | Effect |
|---|---|---|---|
| `max_amortization_years` | 2 | **1** | `has_house` is set from this loop index, so it never leaves zero and no owner state is solved |
| `include_homeownership` | did not exist | **0** | `renters_problem` skips the renter to owner branch, so buying is not in the choice set |
| `housing_status_grid_size` | 7 | **3** | the index runs `-1 .. 2`: homelessness plus three rental sizes, the four point grid of the written model |

`smallest_index_for_purchase` moves from 5 to 2 so that references which compile
whether or not they are reachable stay inside the smaller grid. Compiles clean,
with the same nine pre-existing warnings and no new bounds warnings.

Two things are deliberately left: the negative asset grid, because the renter
loops *start* at `negative_financial_grid_size` so setting it to zero would send
those loops through index zero, and it costs no time now that no owner is solved;
and the house price and rental company loops, which are next.

**None of this is verified numerically.** A backward pass is 51 minutes and a
benchmark equilibrium is hours, so what is checked here is that it compiles and
that the switches do what reading them says. The model has to be solved before
any of it is trusted.

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

This is not a matter of taste between two defensible specifications. It is the
thing three referees objected to in the submitted paper: Referee 2 (C5),
Referee 3 (M2a) and the AE (A8) all said that a taste weight rising with `d`
makes reducing the SUD and expanding housing complements "even absent incentive
effects". The model note already records the objection and the fix, and the AE's
suggested alternative, A8, was to vary `b` instead.

**Fixed.** `change_utility_for_addicts` is now `0`, which with
`size_of_penalty = 0` sends `relative_share_of_addiction_2` back to
`relative_share_of_addiction_1` and the housing and consumption weights with it,
so the flow utility is the same function clean and with the SUD. The consistency
check at line 13394 was relaxed to test the weights only, since the shifter is
now meant to differ. Compiles clean, and the model has to be recalibrated before
it produces a number.

And the mirror image held for the shifter the note says does move.
`addiction_scalar_2 = addiction_scalar_1` at line 354, so **`b_1 = b_0`
exactly**: the Stone-Geary endowment did not vary with the SUD at all. The model
note explains why two values are needed and it is not decoration: a single `b`
large enough to deter clean households pushes the interior choice below zero for
households that already have the SUD, so their expenditure goes to the corner and
`theta_v` has nothing to pin. `b_0` pins participation and `b_1` keeps the choice
interior.

**Partly fixed.** `addiction_scalar_2` is now `b_sud_ratio * addiction_scalar_1`
with `b_sud_ratio` a declared parameter, so the structure matches the written
model. The ratio is one, which is the neutral value, and it is flagged in the
source as needing to be bracketed on abstinence among homeless adults with a SUD,
18.7 per cent from the no housing arm of Milby et al., before anything is
reported. At one the SUD has no effect on drug demand at all.

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

**Fixed, structurally.** Every place that evaluates the drug term now goes
through one function, `b_shifter(is_sud, housing_size)`, added to `Global_Vars`:
the flow utility, its marginal utility, the closed form split in `objective` and
`optimize_frac_spent_on_addiciton`, twenty four call sites in four routines. They
cannot drift apart, which is why this was not patched one site at a time.
Homelessness is identified by the housing size rather than the index, because the
call chain carries the size; the homeless flow is about a fifth of the smallest
rental, so the test has an enormous margin. `rho_b_homeless` is one, the neutral
value, and is flagged in the source: it has to be bracketed on Milby's housed
against unhoused abstinence ratio of 1.473 before anything is reported. Until it
is, the sign of the central experiment is still wrong.

So `rho^b_H` did not exist, and it is not one channel among four. The model
note is explicit about what it is:

> "This is the only parameter in the model that governs the elasticity of drug
> use with respect to housing access, the object Referee 2 (C1) calls the crux on
> which all the welfare results rest, and which Referee 3 and the AE (A13) name
> independently. Without it that moment is not merely untargeted, it is
> *untargetable*: housing a household only raises its resources, drugs are a
> normal good, and the model would predict that housing *raises* use, the
> opposite sign to Milby et al. (2005)."

So the parameter the referees identify as the crux of the paper is absent from
the code, and without it the model gets the sign of the central experiment
backwards. This is the most consequential single finding in this audit, and it
moves to the head of the queue.

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
| `kappa_phi_d` | mortality multiplier, SUD | was `6.9`, **now `5.9`** | fixed: the constant is the multiplier minus one, so the effective ratio is now 6.9 |
| `kappa_phi_H` | 4.41 at 26 falling to 1.09 at 80 | `increased_risk_of_death_homeless = 0.6`, flat | **disagrees**: flat, and an effective 1.6 |
| homeless and SUD together | multiplicative in the note | `0.6 + 6.9`, additive | **disagrees in functional form** |
| `bar_pi_r` | 0.025 a year | `probability_of_stopping_addiction = 0.025` | agrees |
| `mu_H` | calibrated to the SUD share of the homeless, 21.7 per cent | `= 1/6` exactly | set, not calibrated |
| `pi_d` | calibrated to the SUD rate, 3.68 per cent | `probability_of_becoming_addicted_if_experiment = 0.037` | agrees |
| `chi_D` | 0.212 | `addict_cost_govt_as_perc_of_avg_inc = 0.212` | agrees |
| `chi_H` | 0.4286 | was `0.252`, **now `0.4286`** | fixed to the literally homeless figure |
| `xi` | 0.85 | `curvature_of_labor_income_taxes = 0.85` | agrees |
| `tau_k` | 0.15 | `investment_income_tax = 0.15` | agrees |
| `kappa_V` | 0.50 of median | `threshold_income_vouchers = 0.5` | agrees |
| `kappa_r` | 0.30 | `rent_to_income_ratio_vouchers = 0.3` | agrees |
| `pi_V` | 26.6 per cent of the eligible | `probability_of_voucher_benchmark_used = 0.06` | different objects; the 0.06 is a per period draw and has to be shown to deliver the 26.6 |
| `sigma` | 2.0 | `risk_aversion_consumption = 2` | agrees |
| `delta_d` | 0.30 | `penalty_child_addicted = 0.30` | agrees |
| `delta_h` | 0.31 | `penalty_child_homeless = 0.31` | agrees |
| `omega` | 0.014 | `weight_on_child = 0.0137` | value agrees, **but see 4** |
| homelessness target | 0.399 percent | was `0.0045`, **now `0.00399`** | fixed to the HUD count converted to households |
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

**Wired, switched off.** `compute_expected_child_value` fills
`expected_child_value(d, homeless)` with `E V_1(0, y_child, ...)`, taking the
newborn to where the distribution iteration puts it: age one, the zero asset
index, employed and clean, no housing carried in, no voucher, productivity drawn
from the penalised distribution. The renter continuation then adds
`(1 - phi_j) * weight_on_child * expected_child_value` alongside the existing
bequest hook. It does not depend on `a'`, because the estate goes to the
government rather than to the child, so it shifts the level and the housing and
drug choices through `phi_j` and leaves saving alone.

`include_child_in_continuation` is **0**, so nothing changes yet. Turning it on
puts the age one value function into every age's continuation, which is a fixed
point across ages: the outer loop already iterates on prices, taxes and
inheritance and will carry the lag, but that has to be *seen* to converge before
the switch is trusted. That is the first thing to check on the first real run.

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
    **40 points  1.56x    ->  19 hours on four,  1.9 on forty  <- CHOSEN**
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
