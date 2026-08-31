# Audit A — the module preamble, lines 1–4752

`code/housing_first_or_treatment_first_SR_v1.f90`, `module Global_Vars`:
declarations to line 4637, then the five module procedures at 4638–4752
(`emp_of`, `smi_of`, `snap_benefit`, `sud_of`, `out_of_work_income`).

Read in full. 1,654 distinct names are declared in the slice; every one was
checked with `grep -n` against the whole 38,136-line file for (a) any read
outside its own declaration, (b) whether a declared value is overwritten
before it is read, and (c) for every `distance_`/`_adjuster`/`stopping_rule_`
triple, whether the three are wired to each other and to the calibration
loop's `do while` at 33521–33563.

Nothing here was run. Where a finding says what it would change, that is
either arithmetic on the code as written or "unknown"; no number below was
measured from a solve.

## A note on which configuration is live

Two switches decide whether most of this matters:

- `sweep_addiction_scalar=1` (L1301), so
  `re_do_simulation_with_fixed_parameters = max(1,0) = 1` (L1370).
- The `if (re_do_simulation_with_fixed_parameters==1)` branch at 33836 zeroes
  27 distances and **skips the entire parameter-update block** (its `else`
  runs from 33867 to about 36040).

So as committed, the binary is a single b-sweep point and the calibration
update block does not execute. Every finding below tagged **LIVE (calibrating
run)** fires as soon as `sweep_addiction_scalar` goes back to 0 with
`diagnostic_simulation=0` — which is the file's normal state and the state the
comments are written for. I have tagged each one rather than calling them all
live or all dead.

---

# CLASS 2 — dead code that looks live

## FINDING 1 (most important). The treatment take-up moment has no live instrument, and its distance still gates the calibration loop, so the loop cannot terminate

**Lines 225–241 (declarations), 34847–34925 and 35195 (the update),
33543 (the loop condition).**

What the declarations say:

```
L225   real(8) :: utility_cost_of_treatment=0
L226   real(8) :: utility_cost_of_treatment_adjuster=0
L237   real(8) :: money_cost_of_treatment=0.02
L238   real(8) :: money_cost_of_treatment_adjuster=0.05
L239   real(8) :: distance_money_cost_of_treatment
L240   real(8) :: stopping_rule_money_cost_of_treatment=10.d0**(-3)
```

The comment above L225 is explicit that the policy changed: *"ZERO. Treatment
costs MONEY now and nothing else."* `money_cost_of_treatment` is the live
cost — it is subtracted from resources at L20490–20491 inside
`optimize_frac_spent_on_addiciton`'s budget:

```
L20490   total_consumption_choice_1=max(total_consumption_choice_1-&
L20491       money_cost_of_treatment,10.d0**(-10))
```

But `money_cost_of_treatment_adjuster`, `distance_money_cost_of_treatment` and
`stopping_rule_money_cost_of_treatment` **are referenced nowhere else in the
file** (verified: each appears exactly once, on its own declaration line).
`money_cost_of_treatment` itself is only ever read (L20491), printed (L5007,
L28976 region) or set from `PARAM_HANDOVER.txt` (L32895–32897). It is never
calibrated.

Meanwhile the *retired* parameter is still driven, and still gates the loop:

```
L33543   (distance_utility_cost_of_treatment>stopping_rule_utility_cost_of_treatment) .OR. &
...
L34847   if (include_treatment==1) then          ! include_treatment=1, L194
L34868       treatment_step_1=utility_cost_of_treatment-&
L34869           utility_cost_of_treatment_adjuster*&
L34870           (treatment_take_up_data-model_treatment_take_up(1))
...
L34895       distance_utility_cost_of_treatment=&
L34896           abs(model_treatment_take_up(1)-treatment_take_up_data)
```

Trace the update with the adjuster at zero:

1. Loop 1: `have_treatment_secant=0`, so the secant at 34872–34881 is skipped.
   The fallback is `treatment_step_1 = u - 0*gap = u`. Then
   `previous_utility_cost_of_treatment=u`, `have_treatment_secant=1`.
2. Loop 2 onwards: the secant's own guard at 34874 requires
   `abs(utility_cost_of_treatment-previous_utility_cost_of_treatment)>1e-10`,
   and the difference is exactly 0 because loop 1 did not move it. The
   fallback runs again and returns `u` again.
3. `trust_step(treatment_step_1,u,...)` clamps `u` into a band centred on `u`,
   so it returns `u`. `utility_cost_of_treatment=max(min(u,10),0)=u=0`.

`utility_cost_of_treatment` is therefore pinned at 0 for every loop, forever,
while `distance_utility_cost_of_treatment` is
`abs(model_treatment_take_up(1) - 0.245)` and is tested against `1e-3` in the
`do while`. There is no loop-count cap on that `do while` (checked 33521–36400).

The one place the distance is zeroed, L35195, is the `else` of
`if (include_treatment==1)`, and `include_treatment` is a `parameter` equal to
1, so that branch is unreachable.

The code even prints the diagnosis and then does not act on it (34910–34918):
*"utility_cost_of_treatment IS AT ITS FLOOR 0 and take up is ... treatment is
declined even when free, so the target is out of reach on the benefit side,
not on the cost."* That message is the condition under which the distance
should be zeroed, and it is not.

- **Status: LIVE in a calibrating run** (`sweep_addiction_scalar=0`); dead in
  the committed b-sweep configuration, where 33845 zeroes the distance.
- **What it would change:** the calibration would terminate. Today, in a
  calibrating run, it cannot: the loop exits only when every distance is under
  its rule, and this one is `abs(take_up - 0.245)` with no instrument that can
  move it. The paper's Treatment First arm is the policy this parameter
  prices, so a second consequence is that `bar_tau^u`/the money price of
  treatment is not fitted to its target at all — `money_cost_of_treatment`
  sits at its declared 0.02 in every run. Magnitude of the take-up miss:
  unknown, not measured.

## FINDING 2. Five adjusters that are documented as pinned at zero are silently resurrected at the damping floor by `damp_on_flip`

**`damp_on_flip` at L5844–5885; adjusters declared at L576, L612, L1684,
L1734, L2787.**

`damp_on_flip` (in this slice's `contains` block) never assigns `start_1`;
it only scales the current value:

```
L5871   if ((gap_1*prev_gap_1)<0) then
L5873       adj_1=max(adj_1*0.5d0,floor_1)
L5875   else
L5877       adj_1=min(adj_1*1.2d0,start_1)
L5879   end if
```

At `adj_1=0` the growth branch is `min(0*1.2, start) = 0`, which is fine. But
the **damping** branch is `max(0*0.5, floor_1) = floor_1`. So the first time
the gap changes sign, an adjuster sitting at exactly zero jumps to the floor
and then grows by 1.2× a loop up to its `_start` value.

The adjusters this reaches, all declared 0 with a comment saying they are
fixed:

| adjuster | decl | comment says | call site | floor it lands on |
|---|---|---|---|---|
| `relative_share_of_housing_adjuster` | L1684 | *"ZERO, AND DELIBERATELY … next_batch.py owns it across points instead"* | 34177 | `damp_adjuster_floor`=1e-4, grows to 5e-2 |
| `relative_share_of_leisure_adjuster` | L1734 | `(1-freeze_fitted_internals)*(5*10.d0**(-1))`, and `freeze_fitted_internals=1` (L1359) | 34244 | 1e-4, grows to 0.5 |
| `housing_status_grid_expander_adjuster` | L2787 | declared 0 | 34364 | `housing_status_grid_expander_floor`=1e-3, grows to 0.1 |
| `penalty_child_homeless_adjuster` | L612 | *"EXTERNALLY SET, for the same reason as penalty_child_addicted"* | 35141 | 1e-4, grows to 5e-2 |

`penalty_child_addicted_adjuster` (L576, *"EXTERNALLY SET, AT THE EARNINGS
ESTIMATE … It stopped being calibrated"*) has the same rule written out inline
rather than through `damp_on_flip`, with the same effect:

```
L35026   penalty_child_addicted_adjuster=&
L35027       max(penalty_child_addicted_adjuster*penalty_child_adjuster_damping,&
L35028       penalty_child_adjuster_floor)
```

`penalty_child_adjuster_floor=10.d0**(-4)` (L580).

`sd_permanent_productivity_adjuster` (L1718) is the one frozen internal that
is genuinely frozen: it is not routed through `damp_on_flip` and its own
distance is multiplied by `(1-freeze_fitted_internals)` at L33583.
`relative_share_of_leisure`'s distance is zeroed the same way at L34256, so
the loop does not wait on omega_l — but the parameter still moves, which is
not what "freeze" says.

- **Status: LIVE in a calibrating run**; dead in the committed b-sweep
  configuration.
- **What it would change:** `delta_d`, `delta_h` and `gamma` are reported as
  externally set / owned by `next_batch.py`, and `omega_l` as frozen. If a
  run's gap flips sign on any of them, the in-model loop moves the parameter
  away from the handed-in value while the archive still records it as pinned.
  How far it drifts depends on how many loops run after the first flip;
  1e-4 growing at 1.2× reaches 5e-2 in about 34 loops. Not measured.

## FINDING 3. Six fully dead calibration triples

Each of these is a `parameter` + `_adjuster` + `distance_` + `stopping_rule_`
set in which **none** of the last three is referenced anywhere outside its own
declaration line. Verified by whole-word grep over the whole file.

| lines | base | note |
|---|---|---|
| 237–239 | `money_cost_of_treatment` | see Finding 1 — this is the live cost with dead machinery |
| 2228–2230 | `discount_factor_impatient` | named in the brief; `discount_factor_impatient` itself is read (33701) but never calibrated, though L2185–2189 says the author set a bracket for it on the bottom half's wealth share |
| 2305–2307 | `max_initial_endowment` | and see Finding 5 |
| 2473–2475 | `scaling_of_ss` | `scaling_of_ss` is read; `reduce_ss_by_half=0` so it is 1 |
| 2602–2604 | `utility_improvement` | `utility_improvement=include_addiction*0`, i.e. 0 |
| 1741–1743 | `relative_share_of_addiction` | superseded by `relative_share_of_addiction_1`/`_2`; the base parameter (L1740, `=0.13`) is itself dead too |

`distance_calibration=1` (L3819) and `pop_of_x_perc`/`distance_pop_of_x_perc`
(L4063) are dead in the same way — declared, never assigned, never read.

**Status: dead in every configuration. Effect if removed: none numerically.**
The reason to report them is that `distance_discount_factor_impatient` and
`stopping_rule_discount_factor_impatient` exist and are unwired, so the
two-type economy's impatient beta is not being calibrated even though the
comment at L2185–2189 says the author set its bracket.

## FINDING 4. `stopping_rule_value_function` and `distance_value_function` are a convergence test that does not exist

```
L1515   real(8), parameter :: stopping_rule_value_function=5*10.d0**(-8)
L3786   real(8) :: distance_value_function
```

`stopping_rule_value_function` appears in exactly two places: its declaration
and a `write(2,*)` at L29763. `distance_value_function` appears in its
declaration, two unconditional `=1` assignments (L33266, L36711) and one
`write` (L29766). Neither is ever compared against anything.

This is probably harmless — the household problem is a finite-horizon backward
induction over `life_span`, so there is no value-function iteration to
converge — but the two names are written into the run's parameter dump at
29763/29766, where they read as a live tolerance and a live residual.

- **Status: dead.** Effect if fixed: none on any number; it would stop the
  parameter dump reporting a tolerance nothing uses.

## FINDING 5. `max_initial_endowment=7` is overwritten before it is read

```
L2304   real(8) :: max_initial_endowment=7
...
L22021  max_initial_endowment=is_counterfactual*average_labor_income_calibrated+&
L22022      (1-is_counterfactual)*model_average_labour_income(time_period)
```

The assignment at 22021 is unconditional and sits above every read (8 reads,
all after it in the setup path). The declared 7 never reaches anything. With
its adjuster/distance/stopping rule all dead (Finding 3), the whole block is a
parameter that looks calibrated and is a pure function of average labour
income.

- **Status: the overwrite is live and correct; the declared value and the
  triple are dead.** Effect if fixed: none.

## FINDING 6. `distance_zeta_DI` is computed and never tested

```
L1009   real(8) :: distance_zeta_DI
L1010   real(8) :: stopping_rule_zeta_DI=10.d0**(-3)
```

`distance_zeta_DI` is assigned at 35667 and 35675. `stopping_rule_zeta_DI` is
referenced nowhere but its own declaration, and `distance_zeta_DI` never
appears in the `do while` at 33521–33563.

`zeta_DI=0` and `zeta_DI_adjuster=0.d0` today, both documented as deliberate
(L1005–1008), and the update at 35656 is guarded by
`(zeta_DI_adjuster>0)`, so nothing is wrong now. The trap is the other
direction: if `zeta_DI_adjuster` is ever set positive to calibrate it on the
SMI share of the homeless — which L1020–1032 says is now zeta_DI's moment —
the loop will not wait for it to converge, because its distance is not in the
condition. That is the mirror image of the `distance_convexity_of_rental_company`
bug the comment at 33272–33278 records.

- **Status: inert now, a trap for the next person to un-freeze zeta_DI.**

## FINDING 7. The whole FY2023 SNAP schedule is declared and unread

```
L2656  snap_max_size=8
L2657  snap_allotment_scale=(/1.000000d0, … ,6.017182d0/)
L2667  snap_max_allotment_one=0.039586d0
L2672  snap_gross_limit_one=0.214872d0
L2673  snap_gross_limit_add=0.075744d0
L2679  snap_standard_deduction=0.026256d0
L2680  snap_earned_income_deduction=0.20d0
```

None of the six values is read anywhere. `snap_benefit` (L4674–4705) is the
sole consumer of SNAP parameters and computes

```
L4703   snap_benefit=max(0.d0,max_food_cost-food_stamp_taper*net_1)
```

The revert is documented inside `snap_benefit` (L4685–4703) on the author's
instruction, so the *behaviour* is deliberate. What is not is that the comment
block at L2630–2655, headed **"SNAP AS THE PROGRAMME ACTUALLY WORKS, FY2023,
48 states and DC"**, sits directly above seven dead constants and reads as a
description of the implemented programme. A reader checking whether the model
implements the eligibility limit will find the limit declared, sourced and
never used. `hh_size_1` and `avg_labour_1` are likewise assigned to
`scale_1`/`limit_1` in `snap_benefit` and discarded (L4696–4701), which is
documented.

- **Status: dead. Effect if fixed: none numerically**; it is a comment that
  describes machinery which was removed.

## FINDING 8. `sweep_index` — the counter whose comment explains why it exists, declared and never used

```
L1322  ! ITS OWN COUNTER, NOT loop_count. loop_count is incremented twice per
L1323  ! calibration pass … Indexing a grid by it would take
L1325  ! every other point and then run off the end.
L1327  integer :: sweep_index=1
```

`sweep_index` appears once in the file. The sweep reads up to 64 values into
`sweep_b_grid` (33504–33509) and then uses only

```
L33516   addiction_scalar_1=sweep_b_grid(1)
```

The one-point-per-process design is documented at 33491–33496 (*"the driver
rewrites this file with the remainder before each launch"*), so reading only
element 1 is intentional. The stale part is the declaration and its comment,
which describe an indexing scheme that was never built and which contradict
the design note eighty lines below.

- **Status: dead.** Effect if fixed: none.

## FINDING 9. Other declarations that are never read

Verified individually by whole-word grep. Grouped by why they matter.

**Statistics the author asked for that nothing computes**

- `bottom_half_wealth_share` (L811). The comment above it, L785–802, is about
  the bottom half's share of net worth being reported and never matched. The
  live object is `model_bottom_half_wealth_share`, filled at L8790; this one
  is a second, empty declaration of the same name-idea and is never written.
  A future block that assigns it would report an uninitialised value.
- `var_log` (L3922), `min_income`, `min_income_gini`, `min_income_index`,
  `min_income_index_gini` (L4073–4074), `pop_of_x_perc`,
  `distance_pop_of_x_perc` (L4063), `lower_age_for_old=50`,
  `upper_age_for_old=75` (L4066–4067).

**Superseded parameters**

- `relative_share_of_addiction=0.13` (L1740) and its triple (Finding 3).
- `relative_share_of_housing_0` (L1669), `proportion_addicted=0.3634` (L1624),
  `amount_middle_age` (L1630), `free_market_unit_to_controlled_market_unit=0.24`
  (L1507), `median_nw_to_income_old_to_mid_age_data=2.3` (L1505),
  `fraction_of_income_spent_on_food=0.4` (L3272),
  `average_rent_calibrated=1.d0` (L3506),
  `total_rental_supply_upload` (L3529).
- `beta_type_weight=0.5d0` (L2204) — named in the brief. It is genuinely
  unnecessary: the comment at 33681–33692 explains that each pass carries a
  full unit of mass so every ratio is the 50–50 mixture by construction. The
  declaration is the only thing suggesting a weight exists.
- `rho_b_homeless=1.0` (L2166) — the comment says it is *"Kept as a
  declaration only, so that a robustness run has a name to turn"*. Turning it
  would do nothing, because nothing reads it; that is worth knowing before
  someone runs the robustness check.
- `weight_on_child_saved=0` (L307), `smi_ten_year_recovery_data=0.50` (L945),
  `fraction_itemizing_MIDs_data` (L1449), `bequests_to_net_wealth_data=0.012`
  (L1451), `include_rental_income=1` (L1205),
  `re_calibrate_management_costs=1` (L1248 — its only other mention is the
  commented-out block at 33383).

**Grid and index leftovers**

- `unemployment_grid` (L3077) and `has_mortgage` (L3970): each appears once in
  code, in its declaration, plus only inside `!$omp shared(...)` clause lists
  (15890, and 15878/22538/22992/23288 respectively). `default(none)` means an
  extra name in `shared()` is harmless, but neither variable is ever read or
  written.
- `financial_grid_distance_negative` (L3031) — its sibling
  `financial_grid_distance_positive` is used.
- `largest_possible_financial_index`, `largest_possible_mortgage_index`
  (L3331), `value_of_house_without_min_down_payment` (L3332),
  `value_of_bequests` (L3082), `slope_of_housing_price_guess`,
  `slope_of_housing_stock_guess`, `slope_of_rent_guess` (L3534),
  `slope_of_space_lived_in_internal` (L3790),
  `dis_next_index_space_lived_in`, `dis_prev_index_space_lived_in` (L3792),
  `loop_index` (L3817), `large_num=10.d0**(4)` (L4276),
  `cut_off_1`, `cut_off_2` (L4278).
  Note `largest_possible_financial_index` is also given a
  `!$omp threadprivate` directive (L4357) — a threadprivate copy of a dead
  variable.

**Channel-shutdown switches that shut nothing down**

- `freeze_labor_supply=0` (L397) and `fix_drug_price=0` (L398). The comment
  block at L371–396 sets out "THE CHANNEL SHUTDOWN LADDER" and lists both as
  rungs (*"freeze_labor_supply=1  the tax distortion off"*,
  *"fix_drug_price=1  general equilibrium off"*). Neither variable is read
  anywhere. `child_penalty_off` and `cost_per_drug_test`, the other two rungs,
  are wired. So two of the five rungs of the decomposition the paper's
  channel-separation argument rests on do not exist yet.
  **Status: dead; setting either to 1 would change nothing.** This is the one
  entry in this list I would not call cosmetic.

## FINDING 10. `distance_convexity_of_rental_company`'s adjuster

`convexity_of_rental_company_adjuster=0` (L2685) is never read. Its distance
is live in the `do while` (33529) but is forced to 0 at 33278 and 33859, and
the comment at 33272–33277 records that this was exactly the hang described
above and was fixed. Reported only for completeness — no action.

---

# The `_data` targets: which ones carry no source

38 parameters end in `_data` in this slice. For each I read the comment block
immediately above the declaration and grepped the rest of the file for the
name. **Sixteen carry no source of any kind, anywhere in the file.** Ranked by
whether the model actually uses them.

**Live targets with no source — these are the ones to fix**

| line | parameter | value | uses |
|---|---|---|---|
| 1387 | `average_labor_income_tax_data` | 0.224 | 6 |
| 1868 | `unemployment_rate_data` | 0.0485 | 6 |
| 1867 | `voucher_coverage_data` | 0.266 | 4 |
| 1869 | `unemployment_rate_sud_data` | 0.1625 | 4 |
| 1862 | `food_stamps_share_data` | 0.0042 | 3 |
| 1088 | `homeless_income_share_data` | 0.191 | 2 |
| 1107 | `employed_share_of_homeless_data` | 0.50 | 2 |
| 1415 | `avg_labor_supply_data` | 0.4 | 8 |
| 1398 | `fraction_of_average_house_price_data` | 100000 | 8 |
| 3323 | `risk_free_rate_data` | 0.03 | 4 |

`fraction_of_average_house_price_data` is the worst of these: it is a bare
dollar figure with a commented-out expression beside it,
`! real(500000)/real(767336)`, so the number in force and the number the
comment shows are different quantities and neither is attributed.

Two more have a source *somewhere* but not beside the declaration, which
`check_alignment.py` will not see and a reader will not find:

- `smi_share_of_homeless_data=0.25` (L1069) — attributed to Gutwinski et al.
  inside the `zeta_DI` comment at L1026, forty lines away.
- `employment_rate_given_smi_data=0.30` (L1083) — described as *"the midpoint
  of the high disability range"* in the comment at L956–957, with
  no citation.

**Dead targets with no source** (no action needed beyond deleting them):
`fraction_itemizing_MIDs_data` (L1449), `bequests_to_net_wealth_data` (L1451),
`median_nw_to_income_old_to_mid_age_data` (L1505),
`homeownership_rate_of_old_data` (L1504, 2 uses but ownership is off),
`fraction_leaving_bequests_data` (L1506, same),
`MID_to_GDP_data=0.41` (L1450, one use, inside the
`mortgage_deductibility==1` branch which is unreachable),
`personal_exemption_data` (L1394, covered by the adjacent comment).

## FINDING 11. Two `_data` comments contradict the value they sit above

**(a) `sud_rate_data`, L1773–1781.** The comment block reads:

```
! NSDUH 2024, adults 26 and over, MODERATE OR SEVERE drug use disorder,
! svyrdudany in (2,3) on the file in data/. Weighted share 0.0454.
!
! It was 0.0368, which matched no cut of that variable. …
real(8), parameter :: sud_rate_data=0.0368
```

The comment says the value should be 0.0454 and that 0.0368 "matched no cut".
The declaration says 0.0368.

**The declared value is almost certainly the right one and the comment is
stale**, on the file's own evidence: the `drug_spending_share_data` block
thirty lines below says *"It also quoted 10.13 and 4.54 per cent, which are
the EIGHTEEN and over cuts. The model's universe is 26 and over, where the
same variable gives 8.90 and 3.68, and those are the figures in use."*
(L1826–1829). `participation_rate_data=0.0890` (L1851) carries the same stale
header — *"Weighted share 0.1013"* — above a value of 0.0890, and 0.0890 is
the 26+ figure.

I am reporting this because `sud_rate_data` is the target for
`lambda_addiction` and `probability_of_becoming_addicted_if_experiment` (10
uses, L34734–34825), and the next person to read the comment block will
"correct" a correct number by 23 per cent. It needs the author's ruling, not a
code change.

- **Status: comment is wrong, value is live and appears right. Effect if the
  comment were acted on: the SUD-rate target would move from 3.68 to 4.54 per
  cent, a 23 per cent change in the moment lambda is fitted to.**

**(b) `drug_spending_share_data`, L1814 vs L1837.** The comment computes
*"177.8/1095.2 = 0.1623, and the declared value is that number"*; the
declaration is `0.1620`. A 0.2 per cent discrepancy, no consequence, but the
sentence asserts an equality that does not hold.

## FINDING 12. `number_of_beta_types` defaults to 2 where its comment says one

```
L2193   ! A RUNTIME COORDINATE, NOT A COMPILE-TIME PARAMETER, and defaulting to
L2194   ! ONE type. The two-pass path fails its own equal-beta test …
L2203   integer :: number_of_beta_types=2
```

The default is 2. It is only changed by `PARAM_HANDOVER.txt` (32946–32949),
and it drives the two-pass loop bound (33696) and `mass_passes` (33791).

The comment's argument is that the two-pass path fails the equal-beta
validation and that *"Until that is repaired the one-type economy is the one
that can be calibrated"*. If that is still true, every run launched without a
handover line for it runs the path the comment says is broken. If it is no
longer true, the comment should go. Either way the declaration and the comment
disagree about the model being solved.

- **Status: LIVE in every configuration.** Effect: unknown — this is the
  two-pass machinery the brief's class 1 is about, and whether the second pass
  is correct is Audit B/C's question, not mine. I flag only that the default
  is not what the declaration's own comment says it is.

---

# Classes I found nothing in

**Class 3 (a moment that does not measure what its target measures).** Not my
slice — `print_all_moments` begins at 4753. The one thing visible from the
declarations is Finding 11's universe question (26+ vs 18+), which is a target
issue rather than a moment issue, and the two contradictory comments resolve
in favour of the declared values.

**Class 4 (ordinary Fortran hazards).** I found nothing in the slice.
Specifically checked:

- `implicit none` is present at module scope (L3) and in all five module
  procedures.
- `emp_of`, `smi_of`, `sud_of` against the layout the comment at L640–653
  states, `index = 3*number_of_smi_states*d + 3*m + e`: at
  `number_of_smi_states=2`, `emp_of=mod(i-1,3)+1` gives e,
  `smi_of=mod((i-1)/3,2)` gives m and `sud_of=(i-1)/6` gives d. All three are
  right, and `idx_of` at L5887 is their exact inverse.
- `out_of_work_income` (L4725) reads the module-scope `age_index` rather than
  taking it as an argument. I checked all four call sites — 6862 (inside
  `calculate_income`, whose callers set `age_index`), 8535, 13588, 15138 — and
  each sits inside a `do age_index=1,life_span` nest (e.g. L7346 for 8535), so
  the value is correct. `age_index` is **not** `threadprivate`, unlike the
  other loop indices; that is consistent with age being the serial outer loop
  in every parallel nest I checked, but it is the one hidden coupling in this
  function and worth knowing about.
- No integer division where real was meant in the slice's initialisers; the
  ones that look like it (`real(1)/real(life_span)` at L1632,
  `real(1000000)/real(71764)` at L2277) are explicitly cast.
- All array-dimension expressions in the slice
  (`0:have_two_rental_markets`, `lowest_housing_grid_point:housing_status_grid_size-1`,
  `1-solve_transition_dynamics:transition_length`,
  `0:number_of_smi_states-1`) evaluate to non-empty ranges at the current
  switch settings.

**Subroutines never called.** All five module procedures in the slice are
called: `emp_of` 54 times, `sud_of` 45, `smi_of` 38, `snap_benefit` 9,
`out_of_work_income` 4.

---

# Summary

12 findings.

| # | severity | live? | one line |
|---|---|---|---|
| 1 | **high** | calibrating run | treatment take-up has no live instrument and its distance still gates the `do while`, which therefore cannot exit |
| 2 | **high** | calibrating run | five adjusters documented as pinned at 0 are resurrected at the damping floor on the first sign flip |
| 12 | medium | always | `number_of_beta_types=2` where its own comment says it defaults to 1 |
| 11 | medium | always | `sud_rate_data`'s comment says 0.0454, the declaration says 0.0368; the declaration is probably right and the comment invites a wrong "fix" |
| 9 | medium | — | `freeze_labor_supply` and `fix_drug_price`, two rungs of the channel-shutdown ladder, are declared and read nowhere |
| — | low | — | Findings 3–8, 10 and the rest of 9: dead triples, dead SNAP schedule, dead value-function tolerance, dead counters and grids |
| — | low | — | 16 `_data` targets with no source; 10 of them live |

The single most important is **Finding 1**.
