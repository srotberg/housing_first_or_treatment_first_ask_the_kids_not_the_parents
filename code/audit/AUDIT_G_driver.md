# Audit G: the driver, the counterfactuals and the transition

Slice: lines 25643 to 38137. Routines covered: `create_unemployment_process`,
`build_unemployment_process_smi`, `calculate_aggregate_consumption`,
`save_vars_and_functions`, `upload_vars`, `write_outputs`,
`recompute_derived_parameters`, `write_/read_calibration_state`,
`apply_param_handover`, `calibrating_model`, `long_run_counter_factual`,
`transition_simulation`. Where a finding is about a routine defined outside the
slice but CALLED from it, the call site in the slice is the finding.

Source audited: md5 `c7cb2b24b6` (HEAD of
`claude/two-period-addiction-hazard-d7gb61`).

**12 findings.** Findings 2, 3, 4, 6, 7 (with 7b and 7c) and 12 are LIVE in the
configuration a point actually runs. Findings 8, 9 and 10 are live only in a
calibrating configuration and cannot fire today. Finding 5 is dead output at
live cost. Finding 11, and the `implicit none` hazard under (b), are open
hazards with no current instance. Every claim about what is live was checked
against the compile-time flags in force, which are:

    is_counterfactual=0        solve_transition_dynamics=0   use_old_results=0
    sweep_addiction_scalar=1   diagnostic_simulation=0
    => re_do_simulation_with_fixed_parameters = 1
    number_of_beta_types=2 (run_one_point.sh default)  freeze_fitted_internals=1
    include_addiction=1        number_of_smi_states=2        tie_gamma_to_theta=0

`re_do_simulation_with_fixed_parameters=1` matters throughout: the whole
parameter-update block (lines 33865-36021) is SKIPPED and every distance in it
is set to zero. A point run therefore executes the two-pass loop once and stops
at line 36305. Findings that live inside the update block are marked as such.

---

## 1. THE ANSWER TO THE MAIN QUESTION: what is called inside the two-pass loop
   and what is called after it

The loop is `do current_beta_type=1,number_of_beta_types` at **33696**, closing
at **33785**. Immediately before it, 33694 saves the patient beta; immediately
after it, 33790-33793 restore `discount_factor`, set `mass_passes=2`,
`accumulating_beta_types=0`, `current_beta_type=1`.

### INSIDE the loop, in order (33696-33785)

| line | call | note |
|---|---|---|
| 33703 | `solve_value_function_and_policy_functions(1)` | |
| 33725 | `initialize_feasible_distribution(1)` | conditional, see finding 6 |
| 33752 | `converge_to_stationary_equilibrium(1)` | or the `load_test_distribution` read branch |
| 33774 | `stationary_equilibrium_statistics(1)` | chain 1 |
| 33775 | `stationary_equilibirum_homeownership_rate(1)` | chain 2 |
| 33776 | `govt_revenues_calc(1)` | chain 3 |
| 33777 | `calculate_aggregate_consumption(1)` | chain 4 |
| 33778 | `calculate_welfare(1)` | chain 5 |
| 33779 | `calculate_household_housing_spending(1)` | chain 6 |
| 33780 | `calculate_welfare_by_characteristics(1)` | chain 7 |
| 33782 | `calculate_homeownership_by_characteristics(1)` | chain 8 |
| 33783 | `stationary_equilibrium_wealth_distribution_of_old(1)` | chain 9, see finding 5 |

### AFTER the loop but still inside the `do while` body (33790-36568)

| line | call | touches the distribution? |
|---|---|---|
| 33803 | `calculate_updated_inheritance_amounts(1)` | yes, but `loop_count>0` and inside the bequests branch |
| 34177, 34244, 34364, 34543, 35141, 35567, 35583, 35609 | `damp_on_flip(...)` | no, scalar helper |
| 34887, 35157, 35524, 35591, 35988 | `trust_step(...)` | no, scalar clamp |
| 35084, 35176 | `create_newborn_employment_probability()` | no |
| 35362 | `apply_gamma_tie()` | no |
| 36038 | `clear_drug_market(1)` | no |
| 36132 | `initialize_variables_and_grids()` | rebuilds the grids |
| 36133 | `GKKOC_intergenerational_employment_process(1)` | rebuilds the productivity process |
| 36134 | `initialize_financial_grid(1)` | rebuilds the asset grid |
| 36138 | `set_smallest_house_size()` | conditional |
| 36177 | `function_of_utility_advantage_from_homeowning(1)` | no |
| **36178** | **`govt_revenues_calc(1)`** | **YES -- this is the duplicate, see finding 2** |
| 36179 | `set_SS_benefits(1)` | no |
| 36185 | `solve_elasticity_of_rental_housing(1,...)` | no |
| 36267 | `print_all_moments()` | reads everything, sweep only |
| 36565 | `write_calibration_state()` | no |
| 36566 | `write_calibration_distribution()` | no |

### AFTER the `do while` ends (36568-36601), and after `calibrating_model` returns

| line | call | note |
|---|---|---|
| 36590 | `stationary_equilibrium_wealth_distribution(1)` | see finding 3 |
| 36591 | `calculate_gini_coefficient(1)` | see finding 4 |
| 36596 | `save_vars_and_functions(1)` | |
| 6669 (main) | `write_outputs(1)` | reads the corrupted values, finding 2 |

**Exactly one routine appears in both lists: `govt_revenues_calc`.** The comment
at 36569-36585 records that the second call to
`calculate_homeownership_by_characteristics` was removed from the tail of this
subroutine for precisely this reason. `govt_revenues_calc` at 36178 is the
survivor of the same class, and unlike the removed one it sits INSIDE the while
loop, so it fires on every calibration iteration.

`mass_passes` is confirmed correct in both places: set to `current_beta_type` at
33699 inside the loop and to `number_of_beta_types` at 33791 after it. Those are
its only two assignments in the whole file. It is never stale in
`calibrating_model`. It IS stale in the sense that findings 3 and 4 read it in
routines that do not pool.

---

## 2. `govt_revenues_calc` is called inside AND after the two-pass loop, and the
   second call wipes its own pooled totals

**Line 36178, `calibrating_model`. LIVE in the benchmark, and live in the
configuration every archived point runs.**

```fortran
            call function_of_utility_advantage_from_homeowning(1)
            call govt_revenues_calc(1)
            call set_SS_benefits(1)
```

`accumulating_beta_types` was set to 0 at 33792 and nothing between there and
36178 changes it (those are the only two assignments in the file, at 33698 and
33792). So every one of the ~150 guarded resets in `govt_revenues_calc`
(lines 10742-10880) fires, and the routine refills from `distribution_stationary`,
which by this point holds only the LAST TYPE SOLVED -- the impatient one. The
author's own comment at 36578 states that fact.

At the same time `mass_passes` is 2, so the denominator recomputed at 12254 and
12522 is scaled up for two passes:

```fortran
        sum_of_distribution=sum_of_distribution*mass_passes
```

The result is a one-type numerator over a two-type denominator. The quantities
divided by `sum_of_distribution` and therefore hit on both counts are:

  `model_fraction_homeless` (12545), `model_total_drug_users` (12527),
  `model_addicted` (12529), `model_exprimenters` (12531),
  `fraction_using_MID` (12533), `model_drug_use_percent_by_age_group` (12524),
  `model_eligibles_getting_voucher_relative_to_pop` (12255).

Everything else `govt_revenues_calc` owns -- every government spending
aggregate, `model_treatment_take_up`, `model_recovery_housed/homeless`,
`percent_addicted_by_employment`, `percent_homeless_by_employment`,
`model_mass_with_sud`, `net_govt_revenues` -- becomes the impatient type's alone
rather than the mixture.

**Who reads the corrupted values.** The parameter updates do not: they all sit
above line 36022 and read the pooled values from the in-loop call at 33776. The
readers below 36178 are the ones that matter, and they are the outputs:

  - `print_all_moments()` at 36267, which is what a point archives. Seven
    targeted moments come straight out of `govt_revenues_calc`:
    `MOMENT h_1` (5048), `MOMENT b` (5050), `MOMENT pi_V` (5067),
    `MOMENT cbar` (5079), `MOMENT tau_u` (5081), `MOMENT mu_H` (5083), and
    `MOMENT theta` (5054) to the extent `weighted_drug_share_now` reads
    `govt_revenues_calc`'s aggregates. `MOMENT lambda_d` is NOT affected:
    `model_fraction_addicted` is owned entirely by
    `stationary_equilibrium_statistics` (7292, 7690, 8884).
  - the `B_SWEEP_RAW.tsv` row at 36292. Of its six columns
    `model_exprimenters`, `model_total_drug_users`,
    `model_avg_income_drug_users` and `model_average_income_addicted` are
    `govt_revenues_calc`'s; `model_fraction_addicted` is not.
  - the plain prints at 36219-36221.
  - `write_outputs(1)`, called from `main_program` at 6669.

**MEASURED, not reasoned.** `print_all_moments` prints the homelessness rate
twice by two independent routes: `MOMENT h_1` reads
`model_fraction_homeless` (`govt_revenues_calc`) and
`DIAG homelessness rate rebuilt from the bands` (5169) reads
`val_homeless_band`/`val_mass_band`, which are built by
`calculate_homeownership_by_characteristics` -- chain position 8, called ONLY
inside the two-pass loop and therefore correctly pooled. The two are the same
quantity and must agree. In the archive:

| point | `number_of_beta_types` | MOMENT h_1 | rebuilt from bands | ratio |
|---|---|---|---|---|
| `point_beb77d236b` | 1 | 3.9472078803200273e-3 | 3.9472078803197350e-3 | 1.000000000 |
| `point_cc2658fdf5_frozen_beta` | 1 | 3.9142591310700296e-3 | 3.9142591310697581e-3 | 1.000000000 |
| `point_02bb4b5ab3` | 1 (pre-flag) | 5.3523431083864967e-3 | 5.3523431083860196e-3 | 1.000000000 |
| `point_18da9be82d` | **2** | 8.7359518615624018e-3 | 5.9495737855734098e-3 | **1.468** |

At one type they agree to twelve significant figures. At two types they differ
by 47 per cent. That is the signature of this defect and nothing else.

`point_18da9be82d` was measured at MODEL `d70ad1c545` = commit `d092b49`, which
is BEFORE `mass_passes` existed (introduced in `57863ad`). At that commit the
corrupted value was `H_impatient / M` against a true `(H_patient+H_impatient)/2M`,
so the observed 1.468 says the impatient type carries
1.468/2 = **73.4 per cent of the model's homelessness**. On the current source
the `*mass_passes` line makes the corrupted value `H_impatient / 2M`, so the
same point would now report **about 0.73 of the true pooled rate** instead of
1.47 times it. The sign of the error flipped when `mass_passes` was added; the
error did not go away.

**What fixing it would change:** the seven targeted moments listed above, by
roughly the impatient type's share of each quantity divided by one half. For
homelessness that factor is 0.734 as measured. For the others it is not measured
and I will not guess. There is no archived two-type point on the current source
to read them off; running one and diffing `MOMENT h_1` against
`DIAG homelessness rate rebuilt from the bands` would confirm the current
magnitude in one point.

---

## 3. `stationary_equilibrium_wealth_distribution` is scaled by `mass_passes`
   but has nothing pooled to match

**Line 9747, called from 36590. LIVE at `number_of_beta_types=2`.**

```fortran
        sum_of_distribution=0
        do i=1,2
            sum_of_distribution=sum_of_distribution+&
                sum(distribution_stationary(i)%vector_transition_real(time_period,:,:,:,:,:,:))
        end do
        ! POOLED MASS, NOT ONE TYPE'S. ...
        sum_of_distribution=sum_of_distribution*mass_passes
```

The comment is the right comment for the nine chain routines. It is the wrong
comment here. This routine is NOT in the chain: it is called once, at 36590,
after the loop has ended. It has no `accumulating_beta_types` guard anywhere in
its 168 lines, and it builds `pop_of_top_wealth_x_perc`,
`model_wealth_of_top_x_perc` and `model_total_net_wealth_1` FRESH from
`distribution_stationary` -- the same one-type object it just measured the mass
of. Numerator and denominator come from the same place, so the correct scaling
here is 1, and `mass_passes` is 2.

The consequence is not a factor on a printed number, it is a wrong SELECTION.
The bracket loop at 9829 accumulates households until
`pop_of_top_wealth_x_perc/sum_of_distribution` exceeds
`stopping_rule_wealth_dist`. With the denominator doubled it accumulates twice
the mass, so "the top 1 per cent" is the top 2 per cent of the type it has, and
the wealth share written at 29252 as
`model_wealth_of_top_x_perc(i)/model_total_net_wealth_1` is the top 2 per cent's
wealth over one type's total wealth. The top-wealth shares in the output are
overstated.

The last bracket (`loop_over_complete_distribution=1`) is unaffected: it walks
the whole distribution and does not use the share test.

**What fixing it would change:** the top-x-per-cent wealth shares written by
`write_outputs`, by an amount I have not measured. Unknown.

---

## 4. `calculate_gini_coefficient` inherits that same wrong `sum_of_distribution`

**Lines 10617-10631, called from 36591. LIVE at `number_of_beta_types=2`.**

This routine never sets `sum_of_distribution`. It reads whatever the previous
call left in it, which is finding 3's `2M`:

```fortran
            gini_coefficient_numerator(time_period)=gini_coefficient_numerator(time_period)+&
                (sum_distribution_used/sum_of_distribution)*(...)
```

`sum_distribution_used` is one type's mass at a node; `sum_of_distribution` is
twice one type's mass. Every population weight in the Lorenz sum is halved. The
denominator `gini_coefficient_cumulative_wealth(...,2)` is NOT divided by
anything, so the numerator alone is halved and

    gini_printed = 1 - (1-gini_true)/2 = (1 + gini_true)/2

A true Gini of 0.80 prints as 0.90. This is arithmetic on the code, not a
measurement -- I have no archived two-type Gini to check it against -- but the
halving of the weight is unambiguous from the two lines.

Independent of the factor, taking `sum_of_distribution` as an implicit argument
from whatever ran last is a module-scope coupling: the routine is only correct
in the position it is currently called from.

---

## 5. `stationary_equilibrium_wealth_distribution_of_old` is the ninth routine of
   the chain and nothing reads its output

**Lines 10417-10548, called from 33783 (twice per calibration iteration).
LIVE, in the sense that it runs; its results are dead.**

Two things, and the second makes the first academic.

(a) **Its numerator is not pooled and its denominator is.**
`sum_of_distribution_of_old` at 10417-10425 is genuinely accumulating: the reset
is guarded and the recomputation ADDS to the previous pass, so after two passes
it holds both types' old mass. Correct, and correctly NOT scaled by
`mass_passes`. But `pop_of_top_wealth_x_perc` is reset UNGUARDED at 10477, once
per bracket, on every pass, and refilled from `distribution_stationary`, which
holds one type. The share test at 10500 and the distance at 10515 therefore put
one type's mass over two types' mass, and select the top 2x per cent of the
impatient type where they mean the top x per cent of everybody. Same shape as
finding 3.

(b) **The output is never read.** The routine's one distinctive product is
`model_wealth_of_x_perc_of_old`, assigned at 10479 and 10523. Its only
appearances anywhere else in the file are the two COMMENTED-OUT write statements
at 10533-10536. Everything else it writes -- `wealth_matrix`,
`wealth_matrix_saved`, `wealth_counter`, `pop_of_top_wealth_x_perc`,
`distance_pop_of_top_wealth_x_perc` -- is reset and rebuilt by
`stationary_equilibrium_wealth_distribution` at 36590 before any consumer sees
it. So the routine is a pure cost: a full sort-and-select over the wealth matrix,
run twice per calibration loop, whose every result is either discarded or never
read.

**What fixing it would change:** nothing in any number, because nothing reads it.
Removing it from the chain would save two sort-and-select passes per calibration
loop. If the "of old" distribution is wanted in the paper, (a) has to be fixed
first.

---

## 6. `loop_count` counts SOLVES, not calibration loops, and the two-pass loop
   solves twice

**`loop_count=loop_count+1` at line 16169, inside
`solve_value_function_and_policy_functions`. LIVE.**

`calibrating_model` sets `loop_count=0` at 33209 and never increments it; the
only increment in the file is inside the value function solve. The two-pass loop
calls that solve once per type, so `loop_count` advances by **2 per calibration
iteration** at `number_of_beta_types=2`, plus one more on the first iteration if
the priming solve at 33676 fires, plus one more per iteration if the omega
counterfactual at 33608 fires.

Under one discount factor solves and loops were the same thing and every guard
written as `loop_count` meant what it said. They are no longer the same thing.
The guards affected, all in this slice:

  - **33718**, the cold-start guard `if (((loop_count<3) .OR. ...)`. Intended as
    "the first three calibration loops". At two types it is the first one and a
    half: iteration 2's impatient pass sees `loop_count=3` and warm-starts from
    the PATIENT type's converged distribution. With
    `stopping_rule_stationary_distribution` at 6e-4 that is a loose stopping
    rule applied to a guess drawn from the other type.
  - **33604**, the omega counterfactual, gated `loop_count>=1`: fires from the
    second half of iteration 1 rather than from iteration 2.
  - **33566**, sigma_y, gated `loop_count>=1`: same.
  - **33867**, `loop_count>aftr_how_mny_lps_start_update` with the constant at 0:
    immaterial here, but it is the same conflation.
  - **33795**, `if (loop_count>0)` gating the inheritance update: same.
  - every `if (loop_count<1)` one-shot diagnostic, including
    `verify_unemployment_process` at 26069 and the age print at 16158. These now
    print for the patient pass and not the impatient one, which is probably what
    is wanted but is not what the code says.

`resumed_loop_count` (32423) is read from the checkpoint and only printed, so a
resume does not restore `loop_count`; every resumed run restarts the counter at
zero and re-triggers whatever `loop_count<3` was meant to gate.

**What fixing it would change:** the number of cold-started distribution solves,
and which pass gets the one-shot diagnostics. No moment changes if the
distribution solves to tolerance either way. Unknown.

---

## 7. `calculate_aggregate_consumption`: the LTV normalisation is not guarded, so
   the second pass divides an already-divided number

**Lines 27989-27993, chain position 4. LIVE at `number_of_beta_types=2`;
affects a diagnostic output only.**

The accumulators are guarded correctly:

```fortran
        if (accumulating_beta_types==0) model_average_LTV_at_orgination(time_period)=0
        if (accumulating_beta_types==0) model_mass_origination(time_period)=0
```

The final normalisation is not:

```fortran
        model_average_LTV_at_orgination(time_period)=&
            model_average_LTV_at_orgination(time_period)/model_mass_origination(time_period)
        model_average_LTV_at_orgination_2(time_period)=&
            model_average_LTV_at_orgination_2(time_period)/model_mass_origination_2(time_period)
```

Pass 1 leaves `N1/M1` in the numerator variable and `M1` in the mass variable.
Pass 2 does not reset, accumulates `N2` on top of `N1/M1` and `M2` on top of
`M1`, and divides: the result is `(N1/M1 + N2)/(M1+M2)` where the pooled answer
is `(N1+N2)/(M1+M2)`. The error is `(N1/M1 - N1)/(M1+M2)`, which is large
whenever `M1` (the mass of households originating a mortgage) is small, and it
is small.

Two further points on the same two lines. There is no `max(...,1e-14)` on the
divisor, unlike every other ratio in the routine; and the comments elsewhere in
this file record that with home ownership switched off `model_mortgages` and
`model_gross_housing_wealth` are identically zero. If `model_mass_origination`
is zero the line is 0/0 and a NaN is written to the output file at 29057-29058.
I have not run the model, so I state the risk, not that it bites.

**What fixing it would change:** the two LTV-at-origination lines in
`write_outputs` (29057, 29058). Nothing else reads either variable. Unknown
magnitude; possibly a NaN today.

## 7b. `val_life_min` is reset unguarded, so it is one type's minimum

**Line 27555. LIVE; a DIAG line only.**

```fortran
        val_life_min(time_period)=10.d0**(10)
```

Every neighbour on the surrounding lines carries the
`if (accumulating_beta_types==0)` guard; this one does not, because a running
minimum cannot be reset to zero. The consequence is the same: on pass 2 it
starts again at 1e10 and ends holding the minimum over the impatient type only.
`DIAG lowest value of a period of life` at 4993 therefore reports one type's
lowest value of life, and the true minimum could be lower in the patient type.
The fix is the same guard, on the 1e10.

## 7c. `fraction_with_drug_spending_relative_to_average` is one type's histogram

**Lines 27543-27544 and 27974. LIVE, but its only consumer is commented out.**

The histogram and its normaliser `total_experimenters_1` are both reset
unguarded, so the array is internally consistent per pass but holds only the
impatient type after the second. It is read at 27979 to compute `index_drug_1`,
which is then used only inside the commented-out `model_drug_threshold` update
at 27985-27987. So it is a one-type object with no live reader. Reported for
completeness rather than as a defect.

---

## 8. The omega counterfactual measures a share with a two-pass denominator and a
   one-pass numerator

**Lines 33604-33655. LIVE ONLY when `sweep_addiction_scalar==0`, i.e. NOT in the
configuration a point runs today.**

The block calls, outside the two-pass loop:

```fortran
                call solve_value_function_and_policy_functions(1)
                call converge_to_stationary_equilibrium(1)
                call stationary_equilibrium_statistics(1)
                call govt_revenues_calc(1)
                drug_users_without_child=model_total_drug_users(1)
```

`accumulating_beta_types` is 0 here, which is right -- the counterfactual wants
its own fresh measurement. But `mass_passes` is 2, left there by the previous
iteration's 33791, and this is a single pass. `model_total_drug_users` is divided
by `sum_of_distribution*mass_passes` at 12529, so `drug_users_without_child`
comes out at half what it should be. It is then compared at 34971 against a
baseline that WAS pooled:

```fortran
                        child_use_gap_1=drug_users_without_child/model_total_drug_users(1)-1
```

so the gap that drives omega is biased down by roughly one half. There is a
second, independent mismatch in the same comparison: the counterfactual solves
ONE type (the patient beta, restored at 33790) while the baseline is the
two-type mixture, so even with the scaling fixed the two sides are different
economies.

The comment at 33645 records the measured gap as +0.93 against a target of +0.18.
If the halving is real the underlying gap is nearer +2.9, which would change how
far omega has to move, not the direction.

**What fixing it would change:** `child_use_gap_1`, hence `weight_on_child`'s
step. Not currently exercised: `calibrate_weight_on_child=1` and
`include_child_in_continuation` gate it, but `sweep_addiction_scalar==0` does
not hold today.

---

## 9. Zero adjusters can be resurrected by their own damping floor, which gives a
   vector-owned parameter a second driver

**LIVE ONLY in a calibrating configuration
(`re_do_simulation_with_fixed_parameters==0`). In a point run today the whole
update block is skipped, so nothing below fires.**

`damp_on_flip` (5844-5885) is:

```fortran
            if (have_gap_1==1) then
                if ((gap_1*prev_gap_1)<0) then
                    adj_1=max(adj_1*0.5d0,floor_1)
                else
                    adj_1=min(adj_1*1.2d0,start_1)
                end if
            end if
```

`max(0*0.5, floor)` is `floor`, not zero. So an adjuster deliberately set to
zero -- which is how this file freezes a parameter and hands it to the search
instead -- becomes the floor the first time its gap changes sign, and then grows
by 1.2 a loop back toward `start_1`, which is NOT zeroed. Five parameters are
frozen this way, are named in `apply_param_handover`, and are passed through a
ratchet with a positive floor:

| parameter | adjuster decl | ratchet | floor | why it is zero |
|---|---|---|---|---|
| `relative_share_of_housing` | 1684 `=0` | 34177 `damp_on_flip` | 1e-4 | "next_batch.py owns it across points instead" |
| `relative_share_of_leisure` | 1734 `=(1-freeze_fitted_internals)*0.5` | 34244 `damp_on_flip` | 1e-4 | frozen as already fitted |
| `housing_status_grid_expander` | 2787 `=0` | 34364 `damp_on_flip` | 1e-3 | "varsigma is no longer calibrated" |
| `penalty_child_homeless` | 612 `=0.d0` | 35141 `damp_on_flip` | 1e-4 | "EXTERNALLY SET" |
| `penalty_child_addicted` | 576 `=0.d0` | 35026 inline ratchet | 1e-4 | set from the earnings literature |

All five adjusters, their `previous_gap_` and their `have_gap_` flags are
written to `calibration_state.dat` (items 85-103 of the writer) and read back, so
once an adjuster is resurrected it persists across every resume: the declaration
`=0` is never seen again.

The trigger is a sign flip in the moment's gap on the second or later loop, which
is exactly what happens when other parameters move the moment across its target.
I have NOT observed it: the checkpoint in the repo
(`code/calibration_state.dat`) has `loop_count=0`, all five `have_gap_` flags at
0 and all five adjusters at 0.000000000000000 (file lines 144, 147, 156, 160 and
107). So the mechanism is certain from the code and the occurrence is not
demonstrated. It cannot occur at all while
`re_do_simulation_with_fixed_parameters=1`.

`sd_permanent_productivity`, the other parameter frozen by
`freeze_fitted_internals`, is NOT at risk: its update at 33578 is a plain
additive step with no ratchet.

**What fixing it would change:** in a calibrating run, whether the archived
vector is the vector that was solved. Nothing today.

---

## 10. Four distances stay in the convergence test with a zero adjuster

**LIVE ONLY in a calibrating configuration, same caveat as finding 9.**

The comment at 34093 states the rule: "A DISTANCE WHOSE PARAMETER CANNOT MOVE
MUST NOT BE IN THE CONVERGENCE TEST", and `advantage_to_owning`,
`minimum_inheritance`, `discount_factor_on_child`, `lambda_m`, `kappa_uem`,
`rho_m` and `rho_d` all follow it by guarding on `X_adjuster>0`. Four do not:

| distance | set at | adjuster | guard |
|---|---|---|---|
| `distance_relative_share_of_housing` | 34191 | `relative_share_of_housing_adjuster=0` | only `tie_gamma_to_theta`, which is 0 |
| `distance_housing_status_grid_expander` | 34376 | `housing_status_grid_expander_adjuster=0` | only `calibrate_size_of_smallest_house_hhld_can_buy`, which is 1 |
| `distance_penalty_child_addicted` | 35076 | `penalty_child_addicted_adjuster=0` | only `calibrate_penalty_child_addicted`, which is 1 |
| `distance_penalty_child_homeless` | 35164 | `penalty_child_homeless_adjuster=0` | only `calibrate_penalty_child_homeless`, which is 1 |

Each is `abs(gap)` and each is tested in the `do while` at 33522. With a frozen
parameter the gap cannot be walked onto the target, so the loop cannot terminate
on it -- unless finding 9 resurrects the adjuster, in which case it terminates
on a parameter the vector was supposed to own. The two findings are two halves of
one problem and neither is safe on its own.

Also in this class, and harmless: `distance_fixed_cost_to_moving` is set to 0 at
34608 and its update at 34598 is commented out, so the parameter and its distance
are both inert; `distance_drug_threshold` is set to 0 unconditionally at 27983
inside `calculate_aggregate_consumption`.

---

## 11. Three distances in the `do while` condition are read before they are ever
   assigned

**Lines 33551-33553. LIVE, but masked.**

`distance_median_income` (declared 2921), `distance_average_net_wealth`
(declared 2925) and `distance_drug_threshold` (declared 3890) have no
initialiser at declaration and are not among the thirty-odd distances
initialised at 33266-33305. They are first assigned at 36147/36158 and at 27994,
which is inside the loop body. The first evaluation of the `do while` condition
therefore compares uninitialised memory against a stopping rule -- the same
defect the comment at 33271 records for
`distance_convexity_of_rental_company`, which was fixed by adding
`distance_convexity_of_rental_company=0` at 33276.

It is masked: `.OR. (loop_count<1)` in the same condition is true on the first
evaluation, so the loop is entered whatever the garbage says. It stops being
masked if that term is ever removed, and Fortran does not guarantee that the
other terms are not evaluated.

**What fixing it would change:** nothing today. Three lines beside line 33276.

---

## 12. CROSS-CUTTING, OUTSIDE THIS SLICE: six accumulators are RESET BY MORE THAN
   ONE ROUTINE OF THE CHAIN, so on the second pass each one accumulates on top
   of another routine's already-finished total

**LIVE at `number_of_beta_types=2`. The lines are in slices 7173-15300, not
mine. I found this while tracing finding 2 and I am recording it here so it is
not lost; the auditors who own those routines should confirm the universes.**

The guarded-reset pattern is safe only if exactly ONE routine owns a variable.
Where two or more routines each reset it and each accumulate into it, the guard
that protects pass 2 from resetting also lets each routine start from whatever
the previous one left. Mechanically searching every
`if (accumulating_beta_types==0) X=0` in the nine chain routines for names that
appear in more than one gives:

| variable | reset in |
|---|---|
| `mass_by_employment` | SES 7336, GRC 10771, `calculate_welfare_by_characteristics` 13257, `calculate_homeownership_by_characteristics` 14537 |
| `mass_by_age` | GRC, `calculate_welfare_by_characteristics`, `calculate_homeownership_by_characteristics` |
| `mass_by_employment_and_age` | `calculate_welfare_by_characteristics`, `calculate_homeownership_by_characteristics` |
| `model_fraction_homeless` | SES 7257, GRC 10833 |
| `total_homeless_1` | SES 7206, GRC 10840 |
| `mass_of_owners` | SES 7249, `stationary_equilibirum_homeownership_rate` 9138 |
| `mass_renters_by_age` | `stationary_equilibirum_homeownership_rate` 9155, `calculate_household_housing_spending` 12609 |

**Worked example, `mass_by_employment`.** Four routines reset it, all four
accumulate into it (8513, 11675, 13672, 15001) and three read it back as a
DIVISOR within themselves (9099, 13867-13900, 15230-15233). Writing `M` for one
type's mass at an employment node:

  - pass 1 (`accumulating_beta_types=0`): each routine resets and refills, so the
    array leaves each routine holding `M` and leaves the pass holding `M`.
  - pass 2 (`accumulating_beta_types=1`): SES starts at `M`, adds `M`, divides by
    `2M` -- accidentally correct. GRC adds another `M` (`3M`) and does not divide
    by it. `calculate_welfare_by_characteristics` adds another (`4M`) and divides
    by `4M` where the pooled mass is `2M`, so every welfare-by-employment average
    is **halved**. `calculate_homeownership_by_characteristics` adds another
    (`5M`) and divides by `5M` at 15230-15233, so
    `homeownership_by_employment` and `housing_size_by_employment` come out at
    **0.4 times** the truth.

**`model_fraction_homeless` is the same defect on a targeted moment.** It is
accumulated at 7765 and divided by `model_sum_of_lowest_productivities` at 9026
inside SES, and accumulated again at 11771 and divided by `sum_of_distribution`
at 12545 inside GRC. Two independent constructions of the same quantity into one
variable. At one type it is harmless -- GRC resets and its value wins, which is
why the one-type points in finding 2 agree to twelve digits. At two types, pass
2 has SES adding its count on top of GRC's pass-1 QUOTIENT and dividing the
result, then GRC adding its count on top of THAT and dividing again. The in-loop
value at two types is not a homelessness rate at all. It is then overwritten by
the post-loop call of finding 2, which at least computes something well defined
(one type over twice the mass) -- so the moment a point archives is finding 2's
error and not this one, but the value the size_homelessness update reads in a
calibrating run is this one.

I have NOT verified that the several routines accumulate over identical
universes; if they do not, the arithmetic above is indicative rather than exact.
The multiple ownership is certain from the reset lines.

---

# The other priorities

## (b) `create_unemployment_process` -- I found nothing in the row-sum class

`number_of_smi_states=2`, so **the hand-written block at 25925-26053 is not the
live array**. Line 26059 dispatches: at one SMI state the hand-written block is
live and `verify_unemployment_process` checks it; at two,
`build_unemployment_process_smi` (26209-26301) overwrites `unemployment_process`
entirely and is the live builder. I checked the live builder.

**The rows sum to one.** For fixed `(a, i, h, d_f, p)`,

    sum_j P = sum_{m_f} P_smi(m_c->m_f | d_c, a) * sum_{e_f} P_emp(e_c->e_f | d_f, m_f, h, p)

and both legs are complete:

  - `smi_transition` (6448-6503) returns `lambda_m` / `1-lambda_m` from state 1
    and `onset` / `1-onset` from state 0, and 1 at one state. Sums to 1 over
    `future_m_1` in every branch.
  - `employment_transition` (6508-6595). From `e_c=1`: `1-sep`, `sep*(1-p_ui)`,
    `sep*p_ui`, sum 1. From `e_c=2`: `find` to state 1, `1-find` to state 2 via
    the `e_f_1==e_c_1` branch, 0 to state 3, sum 1. From `e_c=3` with
    `ui_first_period_only=1`: `find` to 1, `1-find` to 2 via the dedicated
    branch, and state 3 correctly falls through that branch's inner `if` to 0,
    sum 1. With `ui_first_period_only=0`: `find` to 1, `1-find` to 3, sum 1.
    The clamps `max(min(sep_1,1),0)` are applied before the row is formed, so
    they do not break the sum.
  - `idx_of` (5887) is `3*S*d + 3*m + e`, a bijection from
    `{1,2,3}x{0,1}x{0,1}` onto 1..12, and `unemployment_grid_size` is
    `1*6*2 = 12`. Indices match on both sides.
  - `newborn_unemployment_process` gets the same employment leg times
    `m_f*p + (1-m_f)*(1-p)`, which sums to 1 over `m_f` at two states and to 1
    at one state because `newborn_smi_1` is then 0.

**The `implicit none` hazard is still open, but I found no instance.**
`create_unemployment_process` is one of three scopes in the whole file with no
`implicit none` (the others are `objective` at 19560 and
`optimize_frac_spent_on_addiciton` at 20575, outside this slice). The comment at
25862 records that this is exactly how `probability_becoming_employed1` became
an uninitialised real and made a row sum to 1.4583. I extracted every identifier
used in the routine's 563 lines and checked each against the module's
declarations and the routine's locals: every one resolves. There is no second
instance today. The scope is still unprotected against the next one.

**No row-sum check runs in the live configuration.** `verify_unemployment_process`
is called only when `number_of_smi_states==1` (26059-26071). The four nested loop
nests at 26085-26190 that look like row-sum checks have **entirely commented-out
bodies**: they iterate over `unemployment_index`, `i`, `j` and `employment_index`
and execute nothing. At two SMI states nothing anywhere verifies that
`unemployment_process` rows sum to one at run time.

## (c) `calculate_aggregate_consumption`, chain position 4

Findings 7, 7b and 7c above. The twenty-four accumulators reset at 27548-27572
are all correctly guarded and all correctly pooled; the three exceptions are the
two normalisation lines at 27989-27993, the `val_life_min` sentinel at 27555 and
the drug-spending histogram at 27543.

## (d) The counterfactuals and the transition

**`is_counterfactual=0` and `solve_transition_dynamics=0`, so `main_program`
(6628-6687) calls only `calibrating_model`. `long_run_counter_factual` and
`transition_simulation` ARE NOT RUN IN THIS BUILD AT ALL.** Everything below is
live only in a configuration not currently run.

  - **Neither routine has a two-pass loop.** `current_beta_type` appears in the
    whole file only at its declaration, at 33696 and at 33793. So both solve a
    ONE-type economy at whatever `discount_factor` holds, while the benchmark
    they are compared against is the two-type mixture. Any welfare or
    homelessness comparison across a two-type benchmark and a one-type
    counterfactual is a comparison across two different economies. This is the
    largest thing wrong in this half and it is structural, not a line.
  - `mass_passes` is never assigned in either routine, so it keeps its declared
    1. That is the CORRECT value for a single pass, so the counterfactual is
    self-consistent; it is only inconsistent with the benchmark it loads.
  - `long_run_counter_factual` calls `govt_revenues_calc(transition_length)`
    twice per iteration, at 36984 and 37096, with a tax and price update in
    between. At one pass every reset fires and the second call is a clean
    recomputation, so this is not the finding-2 defect -- but it becomes exactly
    that defect the moment anyone gives the counterfactual a two-pass loop.
  - `transition_simulation` calls four chain routines per period at 37712-37715
    and `calculate_welfare` at 38116, but never `calculate_aggregate_consumption`
    per period, so `aggregate_consumption` and its siblings are not built for
    transition periods. Whether anything reads them there I did not trace.
  - Every `distance_` is re-initialised to 1 at 37945-38085, including the three
    that finding 11 says are uninitialised in `calibrating_model`. The
    transition is the more careful of the two on that point.

## Additions to the brief's dead-code list

The brief already names `adjusting_unemployment_probabilities_based_on_productivity`,
`stationary_equilibrium_income_distribution`, `distance_money_cost_of_treatment`,
`distance_discount_factor_impatient`, `discount_factor_impatient_adjuster` and
`beta_type_weight`. From this slice, add:

  - **`stationary_equilibrium_income_bottom_distribution`** (10162-10406) is
    never called: the only two call sites, 36544 and 36592, are commented out.
    It carries its own `sum_of_distribution=sum_of_distribution*mass_passes` at
    10189, so it has been maintained as if live.
  - **`model_wealth_of_x_perc_of_old`** is written and never read (finding 5b).
  - **The four loop nests at 26085-26190** iterate with empty bodies.
  - **`fixed_cost_to_moving`**: its update at 34598 is commented out, its
    adjuster is 0 and its distance is hard-set to 0. Nothing about it is live.

## Things I checked and found correct

  - `mass_passes` is set in both required places and is never stale inside
    `calibrating_model` (finding 1).
  - `write_calibration_state` and `read_calibration_state` write and read the
    same 104 items in the same order. `newborn_parent_share` sits at different
    ordinal positions in the two lists but goes to unit 73, a separate file, so
    there is no positional drift in `calibration_state.dat`. I mapped the
    reader's order onto the 162 lines of the committed
    `code/calibration_state.dat` and every value is consistent with its
    variable's declared value or clamp.
  - `apply_param_handover` overwrites no derived quantity and
    `recompute_derived_parameters` overwrites no handover parameter, so the seed
    path itself creates no duplicate driver.
  - `apply_gamma_tie` is a no-op at `tie_gamma_to_theta=0`, so
    `relative_share_of_housing` is not silently rebuilt from theta.
  - In the configuration a point actually runs
    (`re_do_simulation_with_fixed_parameters=1`), **no vector-owned parameter is
    stepped by the model at all**: the update block is skipped and only
    `inheritance_amount`, the drug market clearing and `sd_permanent_productivity`
    (frozen, adjuster 0) sit outside it, none of which the handover sets. There
    is no live duplicate driver today. The duplicate-driver risk is findings 9
    and 10, and both need `re_do_simulation_with_fixed_parameters=0`.
