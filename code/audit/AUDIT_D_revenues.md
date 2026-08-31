# AUDIT D — revenues and welfare

Slice: lines 10719–14503 of `code/housing_first_or_treatment_first_SR_v1.f90`.

Routines read in full:

| lines | routine | position in the nine-routine chain |
|---|---|---|
| 10719–12584 | `govt_revenues_calc` | 3 |
| 12586–13023 | `calculate_household_housing_spending` | 6 |
| 13025–13226 | `calculate_welfare` | 5 |
| 13228–13982 | `calculate_welfare_by_characteristics` | 7 |
| 13984–14115 | `calculate_welfare_gains` | outside the chain |
| 14117–14402 | `compute_value_function_comparison` | outside the chain |
| 14404–14502 | `compute_value_of_comparison` | outside the chain |

Everything below is read from the source. Nothing was run and no number in this
file was measured; where I give a factor it is an algebraic consequence of the
code and I say so. Per the brief, no code was changed.

---

## 0. Summary

11 findings. In priority order:

| # | class | what | live? |
|---|---|---|---|
| 1 | 1 | **`MOMENT tau_l` is halved by the extra `govt_revenues_calc(1)` at line 36178** | LIVE, benchmark |
| 2 | 1 | **95 in-place normalisations `X = X/D` run on BOTH passes; 93 of them are corrupted, because pass 2 starts from pass 1's ratio instead of pass 1's sum** | LIVE, benchmark |
| 3 | 1/4 | five LOCAL variables carry `if (accumulating_beta_types==0)` resets, so on pass 2 they start from an indeterminate stack value; four of them are denominators | LIVE, benchmark |
| 4 | 1 | the omega counterfactual's `drug_users_without_child` is scaled by `mass_passes=2` against a baseline that is not | LIVE, calibration |
| 5 | 3 | `model_homeowners_experimenting` is a MASS divided by a RATE | LIVE |
| 6 | 4 | `wealth_by_employment_and_tenure` multiplies positive financial assets by house value; the two sibling statistics do not | LIVE |
| 7 | 1 | levels leaving a two-type benchmark are read by a one-type counterfactual: `model_drugs_consumed_by_users` → `drug_supply_shifter` | LIVE, counterfactual |
| 8 | 4 | `calculate_welfare_gains` is passed `average_welfare_of_youngest_cohort(1)`, which nothing in `long_run_counter_factual` ever writes | LIVE, counterfactual |
| 9 | 4 | 50 divisions with no epsilon floor, several over groups that can be empty | latent |
| 10 | 2 | `frac_getting_vouchers` computed and never read; `govt_lump_sum_transfers` reset and never assigned | dead |
| 11 | 1 | `mass_by_age` and `mass_by_employment` carry two different definitions inside the chain | latent |

`model_average_labour_income_tax` is **not** overwritten after `govt_revenues_calc`
by anything other than `govt_revenues_calc` itself. Line 12535 is its only
assignment in the whole file. Finding 1 is about a second CALL, not a second write.

---

## 1. `MOMENT tau_l` — the factor of two, traced end to end

### Where the numerator is written

`govt_revenues_from_labour_income` has exactly **one** reset and **one**
accumulation in the whole file:

```
10742:  if (accumulating_beta_types==0) govt_revenues_from_labour_income(time_period)=0

11738:  govt_revenues_from_labour_income(time_period)=&
11739:      govt_revenues_from_labour_income(time_period)+income_tax_used*distribution_mass_used
```

Line 11738 sits directly in the body of the innermost `housing_status_index`
loop at indentation 36, the same indentation as `lived_in_size_used` at 10930.
It is not inside any `if`. Every household on the grid contributes on every pass.
Nothing resets it between 11738 and the division at 12535. The reset is guarded,
so across the two passes of the type loop it holds **both types**.

### Where the denominator is written

```
12535:  model_average_labour_income_tax(time_period)=&
12536:      govt_revenues_from_labour_income(time_period)/(model_total_efficiency_units(time_period)+&
12537:      model_financial(time_period)*risk_free_rate(time_period))
```

Both denominator terms are owned by `stationary_equilibrium_statistics`
(position 1), not by this routine:

* `model_total_efficiency_units` — reset 7230 (guarded), accumulated 7577.
* `model_financial` — reset 7224 (guarded), accumulated 8228.

Both are therefore also two-type accumulators.

### So inside the type loop the ratio is right

Calls at 33774–33776:

```
call stationary_equilibrium_statistics(1)
call stationary_equilibirum_homeownership_rate(1)
call govt_revenues_calc(1)
```

Pass 1: `accumulating_beta_types=0`, both sides hold type 1. Pass 2:
`accumulating_beta_types=1`, no reset fires anywhere, both sides hold types 1+2.
`tau_l` is the fifty-fifty mixture, exactly as the comment at 33682 describes.
Line 34544, where the retention scale is updated against this moment, runs
between the loop's end and line 36178, so **the internal calibration reads the
correct value**.

### The bug: a tenth call, outside the loop

```
36177:  call function_of_utility_advantage_from_homeowning(1)
36178:  call govt_revenues_calc(1)
36179:  call set_SS_benefits(1)
```

Line 36178 is inside `calibrating_model`'s main `do while` (33522–36568) at
indentation 12, with no enclosing `if`. It runs on every iteration, **after** the
type loop has closed and after line 33792 has put `accumulating_beta_types` back
to `0` and `mass_passes` to `number_of_beta_types` (2).

At that point:

* every guarded reset in `govt_revenues_calc` fires, so
  `govt_revenues_from_labour_income(1)` goes to zero;
* it is refilled from `distribution_stationary`, which holds **only the last type
  solved** — the impatient one — and from that type's policy functions;
* `stationary_equilibrium_statistics` is **not** called again anywhere between
  33774 and 36178 (the only call sites in the file are 5398, 5474, 33610, 33774,
  36982, 37337, 37712), so `model_total_efficiency_units(1)` and
  `model_financial(1)` still hold **both** types.

Line 12535 then divides a **one-type numerator by a two-type denominator**.

```
tau_l_reported = R2 / (B1 + B2)      instead of      (R1 + R2) / (B1 + B2)
```

which is `R2/(R1+R2)` times the correct value — one half exactly when the two
types pay equal labour income tax, and near enough to a half that it reads as
one. This is the reported symptom.

### Who reads the halved value

* 36189 `write(*,*) "model_average_labour_income_tax=", ...` — halved.
* 36267 `call print_all_moments()`, which prints at 4837
  `"MOMENT tau_l average labour income tax model="` — **halved**. This is the
  line `run_one_point.sh` keeps and the calibration driver scores.
* 29046 and 29590 in `write_outputs`, called from `main_program` after
  `calibrating_model` returns — halved.

Line 34544's internal update is *not* affected, which is the asymmetry to be
aware of: the model's own loop drives the retention scale to the right target
while the point file reports half of it. A driver that scores on the printed
moment and a loop that scores on the internal one are chasing different numbers.

### What else the same call breaks

`mass_passes` is 2 at line 36178 while the accumulators hold one type, so
`sum_of_distribution` at 12508–12522 comes out at 2 against numerators of 1.
Every share `govt_revenues_calc` forms against it is therefore also halved by
that call, and these are read afterwards:

| line | statistic | read at |
|---|---|---|
| 12524 | `model_drug_use_percent_by_age_group` | 36249 print, `write_outputs` |
| 12527 | `model_total_drug_users` | 5379/5382 in `print_all_moments` (omega's baseline), 34971 |
| 12529 | `model_addicted` | `write_outputs` |
| 12531 | `model_exprimenters` | 36207 print |
| 12533 | `fraction_using_MID` | 34570 in the standard-deduction update |
| 12545 | `model_fraction_homeless` | 36205 print, and 14315 as the `kappa_x` externality |

`total_govt_revenues`, `net_govt_revenues` and every `govt_spending_on_*` level
are likewise one-type after 36178 while `model_GDP*` are two-type, so any ratio
of the two formed downstream (29602, 29607, 34572) is halved.

Ratios formed *within* `govt_revenues_calc` from two of its own accumulators
(`percent_addicted_by_employment / total_mass_by_employment`,
`model_fraction_homeless_recieving_food_stamps / model_fraction_homeless`) are
unaffected by this call, because both sides are refilled together.

**Fix direction (author's call):** either call
`stationary_equilibrium_statistics(1)` immediately before 36178 so both sides
agree, or delete 36178 and let the loop's own pass-2 values stand. Deleting is
the smaller change and there is nothing between 33776 and 36178 that changes the
distribution; `function_of_utility_advantage_from_homeowning(1)` at 36177 does
not touch `distribution_stationary`.

**Effect if fixed:** `tau_l` printed as roughly twice its current value, i.e.
back onto its target. All the shares in the table above likewise double. I have
not measured any of this.

---

## 2. In-place normalisation on a routine that runs twice

This is the largest thing in the slice and it is a generalisation of the
`sum_of_distribution` bug that was fixed today.

### The mechanism

The pattern throughout the slice is

```
if (accumulating_beta_types==0) NUM(t)=0        ! guarded
if (accumulating_beta_types==0) DEN(t)=0        ! guarded
   ... NUM(t)=NUM(t)+x*mass ; DEN(t)=DEN(t)+mass ...
NUM(t)=NUM(t)/DEN(t)                            ! UNGUARDED, at the foot
```

The reset is guarded so that the accumulator survives into pass 2. The
normalisation at the foot is **not** guarded, so it also runs at the end of pass
1 and destroys the very accumulator the guard was protecting. Pass 2 then adds
its own raw sum to pass 1's *ratio*:

```
pass 1 leaves   NUM = N1/D1
pass 2 computes NUM = (N1/D1 + N2) / (D1 + D2)
correct value is        (N1 + N2) / (D1 + D2)
```

The error is `(N1/D1 - N1)/(D1+D2)`. It vanishes exactly when `D1 = 1`, and
`D1 = 1` for one divisor only: `sum_of_distribution`, whose pass-1 value is one
type's total mass times `mass_passes = 1`. That each type's distribution sums to
exactly one is confirmed by the comment at 13825 ("the mass diagnostics came out
at exactly 2.0"). For every other divisor — a conditional mass, a group total,
a rate — `D1 ≠ 1` and the statistic is wrong.

When the group is small the distortion is not small. With `D1 = D2 = d` and equal
per-pass ratios `r`, the reported value is `r(1+d)/(2d)`, so a group holding one
per cent of the mass reports about fifty times its true average.

### The count

95 in-place normalisations in the slice. Two are not two-pass objects
(`fraction_of_income_spent_on_housing` at 12897 is per household;
`welfare_adjusted_1` at 14494 is in a single-pass routine). Of the remaining 93:

**8 are safe** — divisor is `sum_of_distribution`:

```
12524 model_drug_use_percent_by_age_group      12545 model_fraction_homeless
12527 model_total_drug_users                   13215 average_welfare_of_all_cohorts
12529 model_addicted                           13848 mass_mortgage_to_house_value_ratio_of_owners_by_age
12531 model_exprimenters
12533 fraction_using_MID
```

**85 are exposed.** The full list is the set of `X = X/D` statements at
12151–12545, 12967–12989, 13178, 13217, 13784–13976. Named because they are read
by the calibration or the paper:

* **13217** `average_welfare_of_youngest_cohort = .../sum_of_distribution_youngest`.
  The divisor looks safe and is not: it is the newborn mass, not one. This is the
  welfare number the whole counterfactual comparison is built on (37353) and the
  one printed at 36214.
* **12986** `mass_of_renters_at_housing_spending = .../mass_of_renters_1` — the
  income-denominator rent-burden headcount. It is read at 34209, where it drives
  the smallest-rental update, with its distance at 34212, and printed at 34526,
  36215 and as UNTARGETED rows at 5250 and 5252. (The expenditure version that `MOMENT h_2`
  now uses, `val_burden50_expend_all(1)/val_mass_expend_all(1)` at 4859, is formed
  at print time from two raw accumulators and is **correct** — that is the pattern
  the rest should follow.)
* **12277** `model_eligibles_getting_voucher = .../model_eligibles`. Corrupted at
  the foot of pass 1, and then used as the divisor at 12237, 12262 and 12265 on
  pass 2, so it takes three more statistics with it.
* **12156** `model_treatment_take_up`, **12167/12174** `model_recovery_housed`
  and `model_recovery_homeless` — mu_H's moment is the ratio of the last two.
* **13866–13976** every conditional welfare average in
  `calculate_welfare_by_characteristics`.
* **13877** `MID_share_by_employment / govt_spending_on_mortgage_interest_deductions`
  — and this one crosses routines as well, see §11.

### How to see it in one run

Any statistic in the exposed list will differ between `number_of_beta_types=1`
and `number_of_beta_types=2` with the two discount factors set equal; the eight
safe ones will not. That is a decisive test and it is cheap.

### Shape of a fix

Guard the normalisation the way the reset is guarded — do it only when the last
pass has run — or keep the raw sums and form the ratio at the point of use, as
`MOMENT h_2` already does. I have not written either; the brief says not to.

---

## 3. Five locals given a two-pass reset

```
10731  real(8) :: ... total_addited_1 ... frac_getting_vouchers ... total_addicted_and_homeless_1 ...
10730  real(8) :: total_homeless_1 ...
10762  if (accumulating_beta_types==0) total_addited_1=0
10838  if (accumulating_beta_types==0) frac_getting_vouchers=0
10840  if (accumulating_beta_types==0) total_homeless_1=0
10841  if (accumulating_beta_types==0) total_addicted_and_homeless_1=0

12596  real(8) :: total_income,mass_of_renters_1,...
12611  if (accumulating_beta_types==0) mass_of_renters_1=0
```

All five are subroutine locals with no `SAVE`. The build is
`gfortran -O3 -fopenmp` (`run_one_point.sh:280`) with no `-fno-automatic` and no
`-finit-local-zero`, so they are automatic storage and their value on entry is
undefined. Between the pass-1 call and the pass-2 call the program runs
`calculate_aggregate_consumption`, `calculate_welfare`,
`calculate_household_housing_spending`, `calculate_welfare_by_characteristics`,
`calculate_homeownership_by_characteristics`,
`stationary_equilibrium_wealth_distribution_of_old`,
`solve_value_function_and_policy_functions` and
`converge_to_stationary_equilibrium` — the stack frame is long gone.

The intent is plainly two-pass accumulation, and a local cannot do that. The
numerators these divide **are** module scope and **are** correctly pooled, so on
pass 2 the result is a two-type numerator over an indeterminate denominator.

Four of the five are denominators, and between them they divide sixteen reported
statistics:

* `total_addited_1` → 12304, 12389, 12392, 12404
* `total_homeless_1` → 12401, 12410, 12413, 12422, 12425, 12428, 12431
* `total_addicted_and_homeless_1` → 12416, 12419, 12434
* `mass_of_renters_1` → 12986 (the rent-burden headcount, see §2)

`frac_getting_vouchers` is never read at all (§10).

The comment at 11912 uses the word "guarded" about `total_addited_1`, but it is
talking about the `unemployment_index>threshold_addiction_index` test, not about
`accumulating_beta_types`. Nothing in the file documents this as deliberate.

Note that §2 applies on top of this: even with `SAVE` added, these thirteen
statistics would still be wrong, because they are normalised in place at the end
of pass 1.

---

## 4. The omega counterfactual reads a `mass_passes`-scaled number against one that is not

Not my slice's call site, but it is my slice's variable and the brief asks who
reads it afterwards.

```
33620  call govt_revenues_calc(1)            ! child_penalty_off=1 counterfactual
33622  drug_users_without_child=model_total_drug_users(1)
...
34971  child_use_gap_1=drug_users_without_child/model_total_drug_users(1)-1
```

At 33620 the block is entered only when `loop_count>=1`, so `mass_passes` is
already `number_of_beta_types` = 2 (set at 33791 on the previous iteration) and
`accumulating_beta_types` is 0. The counterfactual was solved **once**, so
`distribution_stationary` holds one unit of mass; line 12522 multiplies
`sum_of_distribution` by 2 anyway; `model_total_drug_users` at 12527 comes out at
**half** the participation rate of that counterfactual economy.

At 34971 it is divided by `model_total_drug_users(1)` as left by the *pooled*
call at 33776, which is correctly normalised. So `child_use_gap_1` is
approximately `(true ratio)/2 - 1` instead of `(true ratio) - 1`: with the true
ratio near one the gap reads about `-0.5` against a target of
`child_use_gap_data = 1/0.845 - 1 = +0.183`. omega is then updated at 34981 on a
gap that is wrong in sign as well as size.

The same pair inside `print_all_moments` (5382 baseline, 5410 counterfactual,
5418 the ratio) is **self-consistent**, because the baseline it holds at 5382 was
itself produced by the one-type call at 36178 and carries the same factor. So the
printed `MOMENT omega` and the internally used `child_use_gap_1` do not agree
with each other — worth knowing when the two are compared.

Second-order but real: the counterfactual at 33608–33620 solves a **one-type**
economy (`discount_factor` was restored to the patient value at 33790) and
compares it against a two-type baseline. Even with `mass_passes` corrected, the
two sides are different economies.

---

## 5. A mass over a rate

```
12259  model_homeowners_experimenting(time_period)=&
12260      model_homeowners_experimenting(time_period)/max(model_homeownership_rate(time_period),10.d0**(-14))
```

`model_homeowners_experimenting` is accumulated at 11227 as a mass. The divisor
is not a mass: line 9614 defines

```
model_homeownership_rate(time_period)=mass_of_owners(time_period)/sum_of_distribution_not_be_homeless
```

so it is a share in `[0,1]`. The statistic the name promises — the share of
homeowners who experiment — needs `mass_of_owners(time_period)` as the divisor.
As written the result is the intended share multiplied by
`sum_of_distribution_not_be_homeless` — the non-homeless mass, about one per
type and so about two in a two-type run. So the number changes with the number of types
even after everything above is fixed.

Read at 28981 (`write_outputs`) and 36515.

---

## 6. A misplaced parenthesis in `wealth_by_employment_and_tenure`

```
13706  wealth_by_employment_and_tenure(time_period,employment_index_to_use,i)=&
13707      wealth_by_employment_and_tenure(time_period,employment_index_to_use,i)+&
13708      housing_price(time_period)*housing_size(housing_status_index)*&
13709      (max(min(years_left_on_mortgage_index-1,1),0)+&
13710      min(financial_grid(financial_index),0.d0)+&
13711      max(financial_grid(financial_index),0.d0))*distribution_mass_used
```

= `p·h·(owner + a)·mass`. Positive financial holdings are multiplied by the
house value.

The same quantity is built twice more in the model, both times differently:

```
13562  wealth_by_employment ...
13564      (housing_price*housing_size*(max(min(ylm-1,1),0)+min(fin,0))+max(fin,0))*mass

14993  wealth_by_employment_and_age ...        ! calculate_homeownership_by_characteristics
14995      (housing_price*housing_size*(max(min(ylm-1,1),0)+min(fin,0))+max(fin,0))*mass
```

= `(p·h·(owner + min(a,0)) + max(a,0))·mass`.

The two-out-of-three form is also the one the rest of the file uses: negative
balances are a fraction of house value (`-min(financial_grid,0)*housing_price*housing_size`
is the mortgage, 13727) while positive balances are levels (`max(financial_grid,0)`
used raw at 11406, 11994, 12007). So 13706 is the odd one out and it inflates
renters' and unlevered owners' wealth by `p·h`.

LIVE; written to `wealth_by_employment_and_tenure*.txt` at 30568.

---

## 7. Levels crossing from a two-type benchmark into a one-type counterfactual

`model_drugs_consumed_by_users` is accumulated at 11549 in my slice and is
**never normalised** — it leaves `govt_revenues_calc` as a level. It is read at
32071:

```
32071  quantity_1=model_drugs_consumed_by_users(time_period)
...
32085  drug_supply_shifter=1/(quantity_1**(drug_supply_curvature-1))     ! is_counterfactual==0
```

The benchmark normalises the supply curve on its own quantity and writes
`drug_supply_shifter` to disk; the counterfactual reads that file back and clears
against it. `calibrating_model` runs the two-type loop, so the benchmark's
`quantity_1` is on a mass of 2. `long_run_counter_factual` and
`transition_simulation` contain no `current_beta_type` loop anywhere (the only
occurrences in the file are 33696–33793), so `mass_passes` stays at its declared
1 and their `quantity_1` is on a mass of 1. The shifter therefore carries a
factor of `2**(drug_supply_curvature-1)` from one run to the other, and the drug
price in every counterfactual is wrong by it.

The author's own note at 33690 says "A LEVEL would come out doubled, which is why
it is worth checking that no targeted moment is one." This is not a targeted
moment but it crosses runs, which is worse.

The same exposure applies to every level `govt_revenues_calc` writes and
`upload_vars`/`save_vars_and_functions` carries between processes.

---

## 8. `calculate_welfare_gains` is handed a variable nothing fills

```
37353  call calculate_welfare_gains(transition_length,average_welfare_of_youngest_cohort(1),j,&
37354      welfare_of_gains_by_addiction(j))
```

`average_welfare_of_youngest_cohort` is written in exactly one place, 13217, at
whatever `time_period` `calculate_welfare` is called with. Inside
`long_run_counter_factual` the only live call is `calculate_welfare(transition_length)`
at 37097; `calculate_welfare(1)` at 37342 is commented out. `upload_vars` reads
the saved benchmark value into a **different** variable,
`average_welfare_of_youngest_cohort_calibrated` (28381–28382), not into the array.

So `average_welfare_of_youngest_cohort(1)` is never assigned in that process. The
counterfactual's own value is at index `transition_length`; the benchmark's is in
the `_calibrated` scalar. Neither is index 1.

With gfortran the module array is static and reads back as `0.0`, which is above
`max(w0,w2)` — both are value functions, large and negative — so
`calculate_welfare_gains` takes the branch at 14083 and `stop`s the run with
"target welfare not bracketed by x in [-1,1]". A run that reaches 37353 dies
there. The same index appears at 37262 in a print and at 37317/37358 for
`welfare_by_addiction_youngest(1,·)` (dead, `do j=1,1`), while the print at 37267
uses `transition_length` — so the two indices are already inconsistent inside the
same block.

Two smaller things in the same routine:

* the bisection at 14102–14106 assumes `welfare_adjusted_1` rises in `x_1`, while
  the bracket test at 14083 accepts either orientation via `min`/`max`. If the
  bracket were ever decreasing the search would converge to the wrong end. In
  practice `x_1` scales consumption so it should rise; noted, not claimed.
* the message says `[-1,1]` and the bracket is `[-0.5,0.5]` (14069–14070).

And a consistency point that matters for what §2 does to the target:
`compute_value_of_comparison` averages over `distribution_stationary_benchmark`,
which is the saved benchmark distribution and therefore holds **one** type,
while the target it is matched against is meant to be the pooled newborn average.

---

## 9. Divisions with no epsilon floor

50 of the divisions in the slice have no `max(·,1e-14)` guard. The full list is
in §2's exposed set; the ones over groups that can genuinely be empty are:

* `total_addicted_and_homeless_1` (12416, 12419, 12434). With homelessness at a
  few tenths of a per cent, the addicted-and-homeless mass can be exactly zero;
  the file already says so at 12162 ("it is exactly zero whenever the housing
  margin has collapsed"). Result is `0/0`, a NaN in the drug block, and the note
  at 12206 records that a NaN there survived into the next iteration once.
* `total_homeless_1` (12401, 12410, 12422, 12425, 12428, 12431) — the sibling at
  12413 does use `max(total_homeless_1,1e-14)`, so the inconsistency is visible
  inside one block of eight lines.
* `population_by_quintile` (13178). Income cutoffs are economy-wide and the
  denominator counts newborns only; an empty top quintile among the youngest is
  plausible.
* `mass_renters_by_age` (12967), `mass_by_addiction_youngest` (13812),
  `mass_by_employment_tenure_and_age` (13948, 13952) — the last is dimensioned
  `life_span/3 = 20` and filled only at indices 1–7, but the normalisation loop
  at 13938 runs `1..int(life_span/10) = 6`, so the empty slots are not touched.

No array-bounds violation found: `age_group = int(floor(real(age_index)/10)+1)`
at 13741 reaches 7 at `age_index=60` against a bound of 20.

---

## 10. Dead

* **`frac_getting_vouchers`** — declared 10731, reset 10838, accumulated 12104,
  **never read anywhere in the file**. (Also one of the five locals in §3.)
* **`govt_lump_sum_transfers`** — declared 4247, reset 10748, and never assigned
  a non-zero value anywhere. It is subtracted in `total_govt_revenues` at 12551
  and reported as a share of revenue at 29607, so a permanently-zero term is
  being printed as if it were measured. The household-side `lump_sum_transfer`
  is a different variable and appears in only one place in my slice — the
  `average_income` diagnostic at 13598 — and in no budget constraint, so the
  government budget is right to ignore it; it is the reporting that is
  misleading.
* **Duplicated block**: `sum_of_distribution` is recomputed identically twice
  inside `govt_revenues_calc`, at 12240–12254 and again at 12508–12522. Harmless,
  but the first is only needed by line 12256.
* **`kappa_x`** appears exactly once in the file, at 14315, inside
  `compute_value_function_comparison`. The block at 1645 documents that as
  deliberate — it cannot move a policy function — so this is **not** reported as
  a fault. But two things about that line are worth the author's eye: it is
  indexed `model_fraction_homeless(1)` while the routine takes `time_period`, and
  inside `long_run_counter_factual` index 1 is never written (the counterfactual
  writes `transition_length`); and the target it is matched against,
  `average_welfare_of_youngest_cohort`, comes from `value_function`, which carries
  no `kappa_x` term at all. So a constant is subtracted from one side of the
  comparison and not the other.

---

## 11. Module-scope variables the slice recomputes, and who reads them after

The slice writes 224 module-scope variables. The ones where a *different*
routine also writes or reads the same name are the ones that matter:

| variable | written by | read after the chain by | verdict |
|---|---|---|---|
| `sum_of_distribution` | pos 3 (12240, 12508), pos 5 (13183), pos 7 (13817) | pos 8, pos 9, 29052, 37280 | all three scale by `mass_passes` — **correct**, this is today's fix and it holds in my slice |
| `sum_of_distribution_youngest` | pos 5 (13199) | nothing outside `calculate_welfare` | scaled; correct |
| `mass_by_age` | pos 3 (10870/11960), pos 7 (13246/13469), pos 8 (14542/15023) | 15254–15272, `write_outputs` | pos 3 counts every household, pos 7 and 8 likewise — the three definitions agree, so the overwrites are harmless. Latent only. |
| `mass_by_employment` | pos 1 (7336/8513), pos 3 (10771/11675), pos 7 (13257/13672), pos 8 (14537/15001) | 29752, 30657, 30750, 36363 | **two different definitions under one name.** pos 3 counts only households carrying the disorder; pos 1, 7 and 8 count everyone. The print at 36363 labels it "mass with the disorder by node", which is pos 3's meaning, and it happens to be pos 3's value there only because of the extra call at 36178 (§1). Remove that call and the label becomes wrong. |
| `model_homeownership_rate` | pos 2 | used as a divisor by pos 3 at 12260 | see §5 |
| `govt_spending_on_mortgage_interest_deductions` | pos 3 | used as a divisor by pos 7 at 13877 | cross-routine divisor; correct inside the loop, wrong after 36178 if 13877 were ever re-run |
| `mass_of_owners_with_mortgage` | pos 1 | divisor at 12989 in pos 6 | pooled on both sides; correct |
| `model_total_efficiency_units`, `model_financial` | pos 1 | divisor at 12536 in pos 3 | **the tau_l pair, §1** |
| `fraction_of_income_spent_on_housing`, `val_gross_rent_1`, `val_labour_income_1`, `val_is_homeless_1`, `val_is_sud_1`, `val_in_labour_force_1`, `val_treat_1`, `val_band_2` | pos 3, pos 6 | nothing | per-household scratch that happens to live at module scope. The stale-value hazard on `fraction_of_income_spent_on_housing` (a homeless household matches neither branch at 12806 or 12812) is already documented at 12841 and the value is not read for those households. Not reported as a fault. |
| `i`, `k`, `age_index`, `years_left_on_mortgage_index`, `unemployment_index`, `employment_index`, `housing_status_index`, `voucher_index`, `in_retirement`, `newborn_household`, `age_group` | all four routines | everywhere | module-scope loop indices. I checked the subroutines my slice calls from inside its loops. `calculate_income`, `calculate_housing_voucher`, `calculate_housing_voucher_2` and `calculate_flow_utility` assign none of them. **`calculate_bequest_amount` does**: line 10147 is `do i=1,number_of_inheritance_ages` and `i` is module scope. Its only call site in my slice is 10916, inside the `employment_index` loop of `govt_revenues_calc`, where `i` is not live — `govt_revenues_calc` first uses `i` at 12242, after every loop has closed. So no index is clobbered in my slice, but the hazard is real for any other caller that holds a live `i` across that call. |

---

## Classes where I found nothing

* **Class 4, `intent(out)` never assigned** — the only `intent` arguments in the
  slice are `intent(in)` and two `intent(inout)` (`x_1` at 13993,
  `welfare_adjusted_1` at 14414), both of which are assigned on every path.
* **Class 4, implicit typing** — all seven routines carry `implicit none`, and
  the build adds `-fimplicit-none`.
* **Class 4, array bounds** — nothing out of range; see §9.
* **Class 4, integer division where real was meant** — the divisions in the slice
  are all `real(8)`. `int(floor(real(age_index)/real(10))+1)` at 13741 and
  `int((real(life_span)/real(10)))` at 13938 both convert before dividing.
* **Class 2, `distance_` without an adjuster** — none of my slice's variables are
  `distance_` or `_adjuster` names.
* **Class 3, a moment measuring the wrong universe** — the moments printed out of
  my slice's variables (`tau_l`, `h_2`, the TEDS-A rows, the LFP rows, the drug
  poisonings row) all have numerator and denominator accumulated in the same loop
  nest over the same set, and each carries a comment saying which universe it is
  and why. The two exceptions are §5 (`model_homeowners_experimenting`, a
  denominator that is not a mass) and one wording point: `lowest_welfare_of_addicted`
  (13447–13460) is a running minimum over **all** age-one households, with no
  addiction test in the condition, so the name promises a restriction the code
  does not apply. It is a diagnostic and its only reader (37302) is commented out,
  so nothing depends on it. The guarded reset there is correct — a minimum
  initialised at 0 against value functions that are all negative behaves properly
  across both passes.

## What I did not verify

Everything in §1–§8 is read off the source. The factors of two are algebra, not
measurement. The single cheapest check that would settle §1 and §2 together is a
pair of runs at `number_of_beta_types=1` and `=2` with the two discount factors
set equal: `tau_l` and the 85 exposed statistics should be identical and will not
be, and the eight `sum_of_distribution`-normalised ones should be identical and
will be.
