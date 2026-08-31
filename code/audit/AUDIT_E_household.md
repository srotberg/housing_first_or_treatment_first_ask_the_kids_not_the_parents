# Audit E -- the household problem

Slice: lines 14504-19559 of `code/housing_first_or_treatment_first_SR_v1.f90`.
Routines: `calculate_homeownership_by_characteristics`,
`frac_of_households_in_support_of_policy`, `copy_housing_state_slice`,
`solve_value_function_and_policy_functions`, `renters_problem`,
`ensure_ev_table`, `fill_ev_table`, `renter_to_renter_problem`,
`renter_to_owner_problem`, `owners_problem`, `owner_owner_stay_problem`,
`owner_owner_move_problem`, `owner_renter_problem`, `calculate_flow_utility`,
`calculate_bequest_utility`, `calculate_marginal_non_housing_utility`,
`which_is_better`, `secant`.

Read in full. `calculate_after_tax_wealth` (20068), `calculate_addiction_spending`
(20441), `calculate_income` (6809), `compute_voucher_index_1` (22223),
`calculate_future_voucher_index_and_opportunity` (22276) and
`calculate_cdf_of_incomes_earned` (6871) were read as well, because the budget
constraint, the treatment charge and the EV table's key cannot be checked
without them. Findings that land outside 14504-19559 are marked OUTSIDE SLICE.

Switches in force while auditing, all compile-time parameters:
`include_homeownership=0`, `max_amortization_years=1`, `track_renters_housing=0`,
`include_vouchers=1`, `include_addiction=1`, `include_treatment=1`,
`smooth_addiction_hazard=1`, `hoist_expectation=1`, `include_bequest_motive=0`,
`interpolate_a_prime=0`, `coarse_grid=0`, `number_of_beta_types=2`,
`use_cobb_douglas=0`, `use_cobb_douglas_2=0`,
`include_probability_of_becoming_addicted=1`, `voucher_conditional_on_clean=0`.

---

## THE HEADLINE ANSWERS

**Budget constraint: I found nothing wrong with it.** Section 0 below records
what was checked and why each term is counted once.

**Continuation value: I found one defect, and it is in the Treatment First
counterfactual rather than in the benchmark.** Finding 1.

---

## 0. THE BUDGET CONSTRAINT -- CHECKED, NOTHING FOUND

The single assembly point is line 20395-20401 in `calculate_after_tax_wealth`
(OUTSIDE SLICE, but every household problem in this slice reaches it and nothing
in this slice assembles resources itself):

    after_tax_wealth_net_of_expenses=gross_wage_income-wage_income_tax_paid+
        investment_income-investment_income_tax_paid+total_household_wealth-
        property_taxes_paid-housing_depreciation_expenditures-rent_spending-
        cost_of_mortgage-cost_of_housing+lump_sum_transfer_given-
        origination_cost_1-prepayment_penalty_1-fixed_cost_to_moving_1+
        bequest_1+food_stamps_recieved+housing_voucher_recieved+
        housing_voucher_recieved_2

    consumption_choice=(after_tax_wealth_net_of_expenses-
        max(financial_grid(future_financial_index_1),0.d0)-
        min(financial_grid(future_financial_index_1),0.d0)*
        housing_price(time_period)*housing_size(future_housing_status_index_1))/
        (1+consumption_tax)

Term by term, for the live (renter to renter) branch:

  - **income**: `gross_wage_income` is set once, by `calculate_income` at 20143,
    and `labor_supply_1` is `intent(in)` all the way down (6817), so
    `calculate_after_tax_wealth` cannot silently move hours behind the secant's
    back. Sign +, once.
  - **income tax**: `wage_income_tax_paid` (20199) subtracted once.
    `mortgage_deductions_tax_rebates` (20188) is NOT added to resources, which is
    right: the deduction is already inside `taxable_income_1` at 20195, so adding
    the rebate as well would be the double count. It is a reporting quantity.
  - **interest**: `investment_income` on `max(a,0)` only (20147-20148), taxed at
    20150, both once.
  - **wealth**: `total_household_wealth` is set once per node at 15903 in
    `solve_value_function_and_policy_functions` and is threadprivate (4329). For a
    renter it is `max(financial_grid(financial_index),0)` -- no house term,
    because `has_house=0`.
  - **food stamps**: set once, at 20233-20241, asset-tested on
    `financial_grid(financial_index_1)`. Added once.
  - **vouchers**: the two voucher objects are distinct programmes
    (`calculate_housing_voucher` at 20248, `calculate_housing_voucher_2` at 20260)
    and are each zeroed at 20204-20206 before the branch. Added once each.
  - **rent**: `rent_spending` is zero at homelessness and
    `rent*housing_size(future_housing_status_index_1)` otherwise (20218-20228),
    subtracted once. It is the CHOSEN dwelling, not the collapsed one, which is
    correct -- the collapsed index is only for next period's state.
  - **savings**: `max(a',0)` subtracted once. The `min(a',0)*p*h'` term looks like
    it could hand a renter borrowing capacity, but it cannot: renters loop
    `financial_index` and `future_financial_index` from
    `negative_financial_grid_size`=61 upward (15897-15901, 16687-16692), and
    `financial_grid(61)=0` (27348), so `min(.,0)` is identically zero on the whole
    renter range. Verified, not assumed.
  - **drug spending**: financed out of `consumption_choice` inside
    `calculate_addiction_spending`, so it is inside the same bucket and pays
    `consumption_tax` once. `total_consumption_choice >= consumption_choice` is
    asserted at every node (16813-16817) and the identity
    `c = C*(1-frac)` is asserted to 1e-8 at 16819 and again inside `secant` at
    19411.
  - **treatment**: charged once, at 20494-20497, as a subtraction from
    `total_consumption_choice_1` before the drug split. The routine is entered
    only when `addiction_index_1>=1`, and treatment is offered only when
    `addiction_index==1` (16609-16613), so every household that can be in
    treatment reaches the charge. `relative_share_of_addiction`, the third gate on
    that block, is kept equal to `relative_share_of_addiction_1` at 31934, so the
    gate is not accidentally shut. Checked because if it were zero the treatment
    charge would vanish while the recovery multiplier stayed.

The budget is also checked at runtime: `check_budget_constraint_clears` is called
for every node with positive resources (16113-16116).

## 0b. THE FLOW UTILITY -- CHECKED, NOTHING FOUND

`calculate_flow_utility` (18856). The live arm is the
`include_probability_of_becoming_addicted==1` branch, 18917-18939 (non-internal)
and 19000-19022 (internal).

  - housing enters once, through `housing_status_utility_function`, whose
    construction at 24417-24434 is
    `(housing_size(h)*(1+own*advantage))**((1-sigma)*relative_share_of_housing_k)`.
    The internal-refinement arm writes that expression out longhand with
    `space_lived_in_internal_1` in place of `housing_size(h)`. I checked these
    against each other term by term because the internal arm OVERWRITES the value
    function at 16020: they agree, and the homelessness penalty is not lost,
    because it lives inside `housing_size(-1)` rather than beside it.
  - the disutility of homelessness is therefore gated on the CHOSEN dwelling
    (`future_housing_status_index_1`), which is right.
  - consumption once, the drug term once through `b_shifter`, in both arms.
  - `value_of_life` added once, unconditionally, 19058.
  - `utility_cost_of_treatment` subtracted once, gated on
    `treatment_choice_now==1`, 19066-19070. `treatment_choice_now` is threadprivate
    (4352) and is set immediately above the housing loop (16617) and cleared at the
    end of each drug-choice iteration (16571, 17098), so it is the choice being
    evaluated and not a leftover.
  - the split between `relative_share_of_addiction_1/_2`, `_consumption_1/_2`,
    `_housing_1/_2` is keyed on `unemployment_index>threshold_addiction_index`,
    i.e. the SUD the household ARRIVES with, not on `addicted_status_1`, the
    drug-use choice. That is deliberate -- `b_shifter`'s comment (5974-5980) says
    the shifter depends on whether the household CARRIES a SUD -- and the two
    arms are consistent with each other and with
    `calculate_marginal_non_housing_utility` (19138-19167), which uses the same
    test. No finding.

## 0c. THE DISCOUNT FACTOR AND THE SURVIVAL PROBABILITY -- CHECKED, NOTHING FOUND

In `fill_ev_table` (16451-16467) and in the un-hoisted nest (16970-16985) the
product is

    discount_factor * survival_probability(...) * voucher_probabilities(...) *
    employment_process(...) * unemployment_process(...) * [hazard] *
    value_function(1)(t', age_index+1, ffi, fui, fei, fhsu, fvi)

`discount_factor` once, `survival_probability` once, one transition factor per
shock, and every state index on the right-hand side is next period's:
`age_index+1`, `ffi_1`/`future_financial_index`, `fui_1`, `fei_1`, `evx_fhsu`
(the collapsed next-period dwelling), `fvi_1`. The classic failure -- an index
that does not advance -- is not present here. `survival_sud_of` (5962) is the
identity in its first argument, so passing `addiction_index` in the hoisted path
and `survival_sud_of(addiction_index,treatment_choice_now)` in the un-hoisted one
is currently the same number; see finding 1 for why that is fragile.

The child term (16874-16881) is weighted by `discount_factor*(1-survival)`,
i.e. the probability of NOT surviving, which is the complement of the
continuation's weight. Once each, no overlap.

---

## FINDINGS

### 1. The memoised expectation is not keyed on the treatment choice -- LIVE IN THE TREATMENT FIRST COUNTERFACTUAL

`ensure_ev_table` 16290-16336, `fill_ev_table` 16338-16491,
`renter_to_renter_problem` 16609-16620 and 16648, 16791, 16897.

**What the code does.** `ev_table_key` carries six fields and only six
(16311-16325): `age_index`, `employment_index`, `unemployment_index`,
`voucher_index`, `housing_status_index`, `years_left_on_mortgage_index`. The
table is invalidated when one of those moves and not otherwise. The table's own
dimensions are a', the future disorder state, the chosen dwelling and voucher
eligibility.

The treatment loop sits INSIDE all six:

    16615    do treatment_choice_1=0,treatment_top_1
    16617        treatment_choice_now=treatment_choice_1
    16621        do future_housing_status_index=...
    16648            call compute_voucher_index_1(is_homeless_1,voucher_index_1)
    ...
    16897            call ensure_ev_table(...,voucher_index_1,...)

and `compute_voucher_index_1` reads `treatment_choice_now` (22249-22253,
OUTSIDE SLICE):

    meets_condition_1=0
    if ((include_treatment==1) .AND. (treatment_choice_now==1)) meets_condition_1=1
    if (is_homeless_1==1) then
        voucher_index_1=2
        if ((unemployment_index>threshold_addiction_index) .AND. &
            (meets_condition_1==0)) voucher_index_1=3

So a housed household carrying the disorder gets `voucher_index_1=3` on the
`treatment_choice_1=0` pass and `voucher_index_1=2` on the
`treatment_choice_1=1` pass. `voucher_index_1` is passed to `fill_ev_table` as
`evx_vidx` and is the fourth index of `voucher_probabilities` at 16453.

Because none of the six key fields changed between the two passes, and because
smooth mode marks every column valid at once (16482), the table built on the
NO-TREATMENT pass is still valid on the TREATMENT pass. `evx_vidx` is only read
during a fill. The treatment branch therefore reads the no-treatment
continuation.

**What it should do.** The table's key must include everything the tabulated sum
depends on. The sum depends on `evx_vidx`, `evx_vidx` depends on
`treatment_choice_now`, so `treatment_choice_now` (or `voucher_index_1` itself)
belongs in `ev_table_key`. The un-hoisted nest, 16970-16985, recomputes
`voucher_probabilities(...,voucher_index_1)` fresh at every node and is correct;
the two paths therefore disagree, which makes this testable by setting
`hoist_expectation=0`.

**Live where.** DORMANT IN THE BENCHMARK, LIVE IN THE COUNTERFACTUAL. In the
benchmark `voucher_probabilities(v,v',opp,k)` is the same for k=1,2,3: at
25698-25703 the three columns are
`p`, `p*increased_prob_of_voucher_if_homeless_1`,
`p*increased_prob_of_voucher_if_homeless_and_addicted`, and both multipliers are
1 (lines 90 and 8), while the `increased_prob_of_voucher_if_homeless_and_addicted==0`
block at 25679-25691 does not execute. So the stale row returns the same numbers
and nothing moves. Under `voucher_conditional_on_clean==1` (25722-25739) row 3
and rows 1:2 diverge by `probability_of_detection` and
`probability_of_false_positive`, and the leak becomes live.

**What it would change.** Unknown in magnitude, but the sign is not ambiguous:
the treatment branch is priced with the continuation of a household that FAILS
the sobriety condition, so the voucher gain that Treatment First is designed to
give a household in treatment is invisible to that household's own treatment
decision. Treatment is undervalued by exactly that gain, in the counterfactual
the paper is about. Measuring it means running the counterfactual twice, once
with `hoist_expectation=0`.

**Note also**, on the same mechanism: `survival_sud_of` (5962) currently returns
`d_1` and ignores treatment, which is a documented decision. If a robustness run
ever restores a treatment effect on mortality, `fill_ev_table` will not follow it
either -- it passes `evx_addidx` raw at 16452 where the un-hoisted nest passes
`survival_sud_of(addiction_index,treatment_choice_now)` at 16974 -- and the key
will still not carry treatment. The two go together.

### 2. `mass_renters_by_income_quintile` is never reset -- LIVE IN THE BENCHMARK

`calculate_homeownership_by_characteristics`, accumulated 14934-14935, divided
15294-15295. Declared 4037.

**What the code does.** Every other accumulator in this routine is reset at the
head under the two-pass guard, 14524-14561. This one is not reset anywhere in
the file -- 4037 declaration, 14934 accumulate, 15295 divide, and that is every
occurrence. It is a module array, so it survives every call.

    rent_burden_by_income_quintile(time_period,:)=&
        rent_burden_by_income_quintile(time_period,:)/&
        mass_renters_by_income_quintile(time_period,:)

The numerator IS reset (14527) and refilled from one solve; the denominator is
the sum of every solve since the program started.

**What it should do.** A denominator has to span the same passes as its
numerator. It should be reset under the same guard the numerator uses:
`if (accumulating_beta_types==0) mass_renters_by_income_quintile(time_period,:)=0`.

**Live where.** LIVE everywhere. The routine is called once per beta type per
calibration loop (33782) and again per counterfactual iteration (36986, 37336)
and per transition period (37714).

**What it would change.** After the routine has been called L times, the
numerator carries the 2 passes of the current solve and the denominator carries
2L passes, so the reported rent burden is the true share divided by L. The first
solve of a run is right and every later one is progressively too small.
`rent_burden_by_income_quintile` is written to the moments file at 29183. I have
not established whether it is a targeted moment; if it is, this has been pulling
on whatever parameter it disciplines.

### 3. Two accumulators guarded across the beta passes are LOCAL variables -- LIVE

`calculate_homeownership_by_characteristics`, declarations 14515 and 14517,
resets 14564 and 14566, accumulation 14710 and 14965, division 15277 and 15298.

**What the code does.**

    14564    if (accumulating_beta_types==0) mass_of_addicts=0
    14566    if (accumulating_beta_types==0) total_MID_value=0

Both are declared inside the subroutine (14515, 14517), have no initialiser and
no `save`. The guard exists precisely so the value survives from the first beta
pass into the second. A local without `save` cannot do that: on the second call
its value is undefined by the standard, so on `accumulating_beta_types==1` the
routine accumulates onto whatever is in that stack slot. It then divides by it:

    15277    MID_share_by_income_quintile(time_period,:)/total_MID_value
    15298    model_addicts_consuming_no_drugs(time_period)/mass_of_addicts

**What it should do.** Either give both the `save` attribute (which is what the
guard assumes), or move them to module scope beside the arrays they normalise.
The numerators here are module arrays and DO carry both passes, so the intent is
clearly to accumulate.

**Live where.** LIVE, `number_of_beta_types=2` (2203) and
`accumulating_beta_types` is 1 on the second pass (33698).

**What it would change.** Unknown, and it is undefined behaviour rather than a
predictably wrong number: with the stack frame reused between the two calls the
result may happen to be right, and with the variable in a register or the frame
reused by something else it will not be. `model_addicts_consuming_no_drugs` is
printed as a DIAG line at 5650; `MID_share_by_income_quintile` goes to the
moments file at 29187.

**The same shape, OUTSIDE SLICE but reached from this routine** (brief item e):
`calculate_cdf_of_incomes_earned` (6871), called at 14572 from inside
`calculate_homeownership_by_characteristics`, declares
`sum_of_distribution_1` and `sum_of_distribution_2` as locals at 6880 and guards
their resets the same way at 6889 and 6893. `size_of_quintile` on that same
declaration line has an initialiser and so is implicitly `save`d; the two sums
do not and are not.

### 4. Two variables written inside the OpenMP loop are declared `shared` -- LIVE, NONDETERMINISTIC

`solve_value_function_and_policy_functions`, shared clause 15873-15895,
declarations 15600 and 15604.

**What the code does.** `run_internal_grid` is a local scalar (15600) and is in
the `shared(...)` list (15890). It is written inside the parallel loop at 15930,
15934, 15942 and 15946, and read at 15952 and 16107. `labor_supply_2` is a local
scalar (15604), in the shared list (15881), written at 16120 and read at 16124.

Every other work variable of this family is threadprivate -- the file has 150
`!$omp threadprivate` lines, 4310-4633, and the comment at 4311-4320 records a
previous instance of exactly this bug found in `cutoff_taxable_income`. These
two were not converted.

**What it should do.** A variable written by every thread inside a parallel loop
must be private (or threadprivate). `run_internal_grid` and `labor_supply_2` are
both written and read within a few statements by the same thread, so they should
be `private`.

**Live where.** LIVE, in every solve, at every thread count above one.
`number_of_threads_used` comes from `omp_get_max_threads()` at 15697.

**What it would change.** `labor_supply_2` feeds only a diagnostic print (16124),
so nothing. `run_internal_grid` is not benign: at 15952 it decides whether
`internal_computations` runs, and `internal_computations` OVERWRITES the value
function at 16016-16020. A thread whose own state can consume can read another
thread's zero and skip the refinement, leaving the coarse-grid value in the
table; a thread whose state cannot consume can read another's one and refine a
node it should not have. The effect is run-to-run nondeterministic and depends
on thread count.

I am flagging this as a candidate worth testing against
`REPRODUCIBILITY_INVESTIGATION.md`, which records a re-run of the same vector
returning a different loss with four hypotheses already refuted, and does not
list a data race among them. I am NOT diagnosing that failure from this: the
test is a single-threaded re-run (`OMP_NUM_THREADS=1`) of the anchor vector,
which would be deterministic if this is the cause.

### 5. A loop stride where a bound was meant -- LIVE

`calculate_homeownership_by_characteristics`, 15239.

**What the code does.**

    15239    do employment_index=1,1,employment_grid_size

Start 1, end 1, stride `employment_grid_size`. The loop body executes exactly
once, with `employment_index=1`. Every sibling loop in the same routine is
written `do employment_index=1,employment_grid_size` (15224, for instance).

**What it should do.** The three statistics inside it are indexed by employment,
so the intent is plainly `do employment_index=1,employment_grid_size`:

    housing_size_by_employment_and_age(time_period,employment_index,age_index)=.../
        mass_by_employment_and_age(...)
    consumption_by_employment_and_age(...)=.../mass_by_employment_and_age(...)
    wealth_by_employment_and_age(...)=.../mass_by_employment_and_age(...)

**Live where.** LIVE in every call.

**What it would change.** Those three arrays are mass-weighted SUMS rather than
averages at every employment index but 1. Magnitude unknown -- it depends on the
mass in each employment cell.

**There is a trap in the repair.** `consumption_by_age(time_period,age_index)`
is also divided inside this loop, at 15251-15252, and it carries no employment
index. Today the loop runs once so it is divided once, correctly. Correcting the
bound without moving that statement out would divide `consumption_by_age` by
`mass_by_age` `employment_grid_size` times over.

### 6. A tenure normalisation over slots that cannot carry mass -- LIVE

`calculate_homeownership_by_characteristics`, 15215-15226.

**What the code does.** `do years_left_on_mortgage_index=1,3` divides
`housing_size_by_employment_and_tenure(:,:,k)` by
`mass_by_tenure_and_employment(:,:,k)` for k=1,2,3. The index `i` that fills
those arrays is set at 14680-14700 and can only be 1: it is 2 or 3 only when
`years_left_on_mortgage_index==2`, and that loop runs `1,max_amortization_years`
with `max_amortization_years=1` (3044). Slots 2 and 3 are reset to zero at 14531
and never written, so the division is 0/0.

**What it should do.** Skip the tenure slots the state space cannot reach, or
guard the division. The same shape sits at 13916 and 13946 (OUTSIDE SLICE).

**Live where.** LIVE. `housing_size_by_employment_and_tenure` is written to a
file at 30606.

**What it would change.** Two thirds of that file are NaN. The run also emits
`IEEE_INVALID_FLAG` and `IEEE_DIVIDE_BY_ZERO`, per
`REPRODUCIBILITY_INVESTIGATION.md`; this is one contributor, though I have not
established that it is the only one. Nothing downstream that I can find reads
those slots back, so I do not believe it corrupts a number -- but the flags it
raises make a genuine numerical fault harder to see.

### 7. A module array zeroed unguarded and refilled from the benchmark distribution -- DORMANT

`frac_of_households_in_support_of_policy`, 15322.

**What the code does.** `mass_by_tenure_and_employment(time_period,:,:)=0` with
no `accumulating_beta_types` guard, followed by a refill from
`distribution_stationary_benchmark` (15385-15387), which is read off disk at
15335-15338. The same module array is owned by
`calculate_homeownership_by_characteristics`, which resets it under the guard at
14533 and fills it from the CURRENT `distribution_stationary`. Call order in the
counterfactual is 36986 (homeownership), 37099 (support), 37336 (homeownership
again), so between 37099 and 37336 the array holds benchmark masses.

Two further inconsistencies in the same routine, both dormant:
the tenure code at 15369-15382 maps `financial_grid<0` to `i=3` and otherwise to
`i=2`, which is the mirror image of the mapping the other writer of this array
uses at 14690-14700; and the `years_left_on_mortgage_index==0` arm at 15364 is
unreachable, the loop starting at 1.

**What it should do.** Two routines writing one module array should agree on
both the reset discipline and the meaning of the third index, or should not
share the array.

**Live where.** DORMANT at `max_amortization_years=1`: only slot 1 is ever
filled by either writer and both agree on slot 1. Live the moment
homeownership is switched back on.

**What it would change.** Nothing today.

### 8. `secant`'s convergence check compares a quantity with itself -- LIVE

`secant`, 19536.

**What the code does.**

    if ((can_consume_1==1) .AND. (abs(MU_1-MU_1)>stopping_rule_secant) .AND. ...

`abs(MU_1-MU_1)` is identically zero, so the condition is never true and the
block that would print the unconverged labour first-order condition (19538-19551)
never runs. Every other test in the routine uses the pair `MU_1, MU_2`, and the
`distance_secant=abs(MU_1-MU_2)` at 19455 shows the intended comparison.

**What it should do.** `abs(MU_1-MU_2)`.

**Live where.** LIVE, in every solve.

**What it would change.** No number, directly -- it is a diagnostic. What it
changes is that a labour supply that hit `max_loop_count=1000` without bracketing
the root has never been reported, over the whole life of the code. Turning it on
is the cheapest way to find out whether that ever happens; note that the
bisection is on a bracket of width 1 with a 1e-8 tolerance, so 1000 iterations is
far more than it needs and the check may well be silent for a good reason.

### 9. The five ownership household problems are unreachable and out of date -- DEAD, A TRAP

`renter_to_owner_problem` 17106, `owners_problem` 17513,
`owner_owner_stay_problem` 17667, `owner_owner_move_problem` 18073,
`owner_renter_problem` 18491.

**What the code does.** `owners_problem` is called only when
`years_left_on_mortgage_index>1` (15912-15920) and that index loops
`1,max_amortization_years` with `max_amortization_years=1`, so the four owner
routines are unreachable. `renter_to_owner_problem` is reached only under
`include_homeownership==1` (16209-16219), which is 0. All five are dead.

They have also fallen behind `renter_to_renter_problem`. Greping the four
features across 16400-18900 returns hits in `renter_to_renter_problem` only:

  - the child in the continuation (`include_child_in_continuation`, 16874) -- absent from all five;
  - the treatment choice (`treatment_choice_now=`, 16617) -- absent from all five;
  - the smooth hazard's drug-risk pass (`drug_risk_active=`, 16746) -- absent from all five;
  - the hoisted EV table (`hoist_expectation`, 16892) -- absent from all five.

`which_is_better` likewise records treatment only off the renter branch
(19310, 19342), and `drug_risk_active` is threadprivate and is left holding
whatever `renter_to_renter_problem` last wrote when an owner branch reads it.

**What it should do.** Nothing, today. Reported because the brief asks for dead
code that looks live: these are 1,750 lines that read as a live alternative and
would silently drop the child externality, the treatment choice and the drug risk
term the moment homeownership is switched on.

**Live where.** DEAD. **What it would change.** Nothing today.

### 10. Class 2 -- declared and never read, computed and then constant

All within the slice unless marked.

  - `went_in_1`: declared 3560, threadprivate 4342, written at 15906 (0) and
    18799 (1), read nowhere. Four occurrences in the file, none of them a read.
  - `optimal_after_tax_wealth_owner_renter`: declared 3600, threadprivate 4596,
    assigned 0 at 18555, read nowhere.
  - `can_consume_drugs`: a local of five routines (16504, 17109, 17673, 18083,
    18499), set to 1 immediately before being tested `==1` in the node
    feasibility filter (16813-16817, 17339-17343, 17900-17904, 18315-18319,
    18685-18689). A constant standing in for a condition that no longer exists.
  - the `if (years_left_on_mortgage_index==0) i=0` arm at 15364, unreachable.
  - the `if (future_housing_status_index==-1)` guard at 18168, unreachable: the
    loop starts at `index_of_smallest_house_hhld_can_buy`.
  - the `write(*,*) "error"` at 19315-19322, nested inside a block that requires
    `unemployment_index<=threshold_addiction_index` (19295) and tests
    `unemployment_index>threshold_addiction_index`. It can never fire.
  - `pay_mortgage_insurance` set at 18674-18682 in `owner_renter_problem`, AFTER
    the budget call at 18648 that would have used it, and read nowhere else in
    that routine.
  - `changing_homes` (16501, 16601, 16707, 16711) is assigned three times and
    read nowhere -- but the comment at 15836 already says so, so it is listed
    only for completeness and is not a finding.

### 11. Latent: the a' lottery would read neighbours that were just zeroed -- DEAD

`renter_to_renter_problem`, 16838 and 17024-17040.

**What the code does.** `future_utility_vector=0` at 16838 zeroes the WHOLE
vector inside the a' loop, and only element `future_financial_index` is then
accumulated. At 17030-17036 the lottery's three points are taken as

    interp_won_y0_1=flow_utility_vector(fi-1)+future_utility_vector(fi-1)
    interp_won_y1_1=flow_utility_vector(fi)  +future_utility_vector(fi)
    interp_won_y2_1=flow_utility_vector(fi+1)+future_utility_vector(fi+1)

`future_utility_vector(fi-1)` and `(fi+1)` are zero by construction, and the
matching `flow_utility_vector` entries are stale from an earlier branch or an
earlier housing choice. The parabola would be fitted through two garbage points.

**What it should do.** Either accumulate the neighbours, or take the three
points from a pass that has them.

**Live where.** DEAD: `compute_asset_lottery` returns immediately at 6212 on
`interpolate_a_prime==0` (4416).

**Reported because** the block at 4390-4415 documents an intention to restore
the lottery and describes what restoring it would require, and this defect is
not on that list. Restoring it as written would produce a vertex fitted to
zeros, and the guard `interp_won_ok_1` would not catch it.

---

## THINGS I COULD NOT SETTLE -- QUESTIONS, NOT FINDINGS

Listed because the brief asks for the universe and the denominator of every
statistic to be checked against its target, and these are the ones where I can
state what the code does but cannot state what the target is.

**a. The food-stamp asset test in the reporting copy is vacuous.**
`calculate_homeownership_by_characteristics` 14730-14742 sets `assets_1=0` and
`avg_net_wealth_to_use_1=1` and then tests
`assets_1 < threshold_for_food_stamps_as_perc_of_average_net_wealth*avg_net_wealth_to_use_1`,
which is `0 < positive` for every household. `calculate_after_tax_wealth`, which
is what the household actually faced, tests
`financial_grid(financial_index_1) < threshold*avg_net_wealth_to_use_1` at 20233
with the real average net wealth. So `food_stamps_1` here is not the food stamps
the household received, and it is subtracted from consumption in
`profile_by_income_quintile(time_period,is_using_drugs,j,2)` at 14822-14824.
Whether that profile column is meant to be consumption net of SNAP or net of
model SNAP, I cannot tell.

**b. The rent-burden denominator is income plus a bequest.** At 14746-14768
`total_income` picks up `bequest_2` and, under
`use_income_or_income_plus_assets=4` (111), interest income and home equity.
That augmented figure is the quintile-sorting variable, and
`calculate_cdf_of_incomes_earned` builds its cutoffs the same way (6985-7000), so
the sort is internally consistent. But the SAME augmented figure is the
denominator of `rent_to_income_to_use` at 14927-14929, and a rent-burden target
is normally rent over gross income. Home equity is zero with homeownership off;
the bequest is not, `inheritance_function_of_productivity=1` giving every
household `employment_grid*inheritance_amount(age)` every period.

**c. `model_drug_use_by_income_quintile` measures use among NON-carriers.** The
whole `profile_by_income_quintile` / `mass_by_income_quintile_1` block at
14786-14903 sits under `if (unemployment_index<=threshold_addiction_index)`.
So the "drug use by income quintile" ratio at 15271-15273 is the share of
households WITHOUT the disorder who consume drugs -- experimenters. If the target
is population drug participation, that is the wrong universe. It may well be
deliberate; the file elsewhere distinguishes experimenters explicitly (5653).

**d. Division by zero in the ownership branches.** 17332, 17895 and 18310
evaluate `spending_on_housing/(gross_wage_income+investment_income)` and rely on
an `.OR.` to save them. Fortran does not guarantee short-circuit evaluation of
`.OR.`, so the division is performed for a household with no income and no
assets. Dead code, but it is another candidate source of the IEEE flags.

**e. A wider housing loop than the rest of the chain.**
`calculate_homeownership_by_characteristics` loops `housing_status_index` from
`lowest_housing_grid_point` to `housing_status_grid_size-1`, i.e. -1 to 2
(14618-14619). Every other routine in the chain, and the solve itself, stops at
`track_housing_1*(1-newborn_household)*(housing_status_grid_size-1)`, which is 0
when `track_renters_housing=0` (14188-14190, 15848-15853). Slots 1 and 2 are
never solved and never filled by the distribution, so they contribute zero mass
and nothing moves. It is correct only by that coincidence.

---

## CLASSES WHERE I FOUND NOTHING

**Array bounds.** Checked every subscript in the slice against its declaration:
`flow_utility_vector`/`future_utility_vector`/`future_bequest_vector`/
`future_leisure_vector` are `dimension(financial_grid_size)`=1:85 (3453, 3472)
and are indexed 61..85 by the renter branches and 1..85 by the owner branches;
`ev_table` is 61:85 x 0:2 x -1:3 x 0:1 x max_CPUs (31015) and is indexed 61..85,
0..1, -1..2, 0..1, `omp_get_thread_num()+1` with the thread count clamped to
`max_CPUs` at 15694-15697; `expected_child_value` is
(employment_grid_size,0:1,1:2) (3173) and is indexed
(employment_index, future_addiction_index in 0..1, is_homeless_1 in 1..2);
`survival_probability` is (life_span,2,0:1,0:smi-1) (3288) and its second index
is `is_homeless_1` in {1,2}; `voucher_probabilities` is (0:1,0:1,0:1,1:3) (3258)
and its fourth index is `voucher_index_1` in {1,2,3};
`addiction_probabilities_percieved` is (0:1,0:1,0:1,1:2) (3220). All in bounds.

**Implicit typing.** Every one of the eighteen subroutines in the slice has
`implicit none`.

**`intent(out)` never assigned.** The only `intent(out)` in the slice is `MU_1`
in `calculate_marginal_non_housing_utility` (19114), assigned unconditionally at
19192.

**Integer division where real was meant.** None in the slice.

**A loop index reused by an inner loop.** None. `i`, `j`, `k`, `age_index`,
`employment_index`, `unemployment_index`, `housing_status_index`,
`voucher_index`, `years_left_on_mortgage_index` are module-scope and shared, but
`i` is threadprivate (4482) and none of the callees reached from inside a loop
that uses one of them writes to it.

**Read before set.** Apart from finding 3, none that I could establish.
`proceed_2`, `labor_supply_1`, `gross_wage_income` and `consumption_choice` all
look at first sight as though they could go stale when `secant` is skipped -- the
guard at 16719 skips it for retirees and the non-employed -- but they cannot:
`calculate_after_tax_wealth` sets `gross_wage_income` (20143),
`consumption_choice` and `total_consumption_choice` (20428-20432) at every node
on every path, `proceed_2` is set to 1 at the head of each routine and only
`secant` clears it, and `labor_supply_1` for a household that never calls
`secant` is the constant set at 16566. The `if (labor_supply_2>0.4)` guard at
16760 is a no-op while `fixed_labor_supply_at_benchmark=0`, because
`labor_supply_2` is set to 1 four lines above (16750) and
`calculate_after_tax_wealth` cannot change it -- it passes it straight to
`calculate_income`, where it is `intent(in)` (6817). Under
`fixed_labor_supply_at_benchmark=1` that guard WOULD skip the secant and leave
`labor_supply_1` and `proceed_2` holding the previous node's values; that path is
off in the benchmark and I have not traced it further.
