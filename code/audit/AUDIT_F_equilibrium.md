# Audit F — equilibrium, distribution and the intergenerational process

Slice: lines 19560–25642 of `code/housing_first_or_treatment_first_SR_v1.f90`.
Routines: `objective`, `optimize_frac_spent_on_addiciton`, `solve_drug_split_with_risk`,
`internal_computations`, `check_budget_constraint_clears`, `initialize_feasible_distribution`,
`compute_voucher_index_1`, `calculate_future_voucher_index_and_opportunity`,
`converge_to_stationary_equilibrium`, `aitken_on_distribution`, `compute_homelessness_duration`,
`function_of_utility_advantage_from_homeowning`, `initialize_variables_and_grids`,
`build_a_prime_window`, `verify_index_map`, `compute_expected_child_value`,
`create_newborn_employment_probability`, `GKKOC_intergenerational_employment_process`.

Read-only. Nothing in the Fortran was changed.

Configuration this audit is written against (all `parameter`, all read out of the source):
`is_counterfactual=0`, `solve_transition_dynamics=0`, `transition_length=1`,
`partial_equilibrium=0`, `number_of_smi_states=2`, `threshold_addiction_index=6`,
`unemployment_grid_size=12`, `include_addiction=1`, `include_vouchers=1`,
`include_treatment=1`, `voucher_conditional_on_clean=0`, `include_ownership=0`,
`max_amortization_years=1`, `have_probablistic_death=1`, `newborns_inherit_addiction=0`,
`fixed_productivity=1`, `track_renters_housing=0`, `include_exogenous_endowment=1`,
`accelerate_distribution=0`, `restrict_a_prime=0`,
`increased_prob_of_voucher_if_homeless=1`, `increased_prob_of_voucher_if_homeless_and_addicted=1`.

---

## The three questions the brief asked first

**(a) Is mass conserved in `converge_to_stationary_equilibrium`? YES.** Traced by hand and it
balances exactly, by construction. Per source state the operator pushes

    sum_m frac(m) * S(a,h,d,m) * [sum_v' P_v] * [sum_e' P_e] * [sum_d' P_a * sum_{u' in block(d')} P_u]

`m=1,2` splits the asset lottery into `1-frac` and `frac`, which sum to one (22627/22639, and 23036/23048 in the branch that is not taken). Survivors land at `age_index+1` for `age_index=1..life_span-1`;
everyone at `life_span` is dropped. The newborn row (22916–22940) writes age one with `=` rather
than `+=`, but age one is never a destination of the survivor sweep, so nothing is clobbered, and
the newborn total is 1 whenever `newborn_productivity_draw` and `newborn_state_draw` are
distributions. Both are: `create_newborn_employment_probability` renormalises every
`(:,parent,d,h)` column explicitly (25211–25222); `newborn_parent_share` is renormalised at 9010
or set from the p_edge interval masses at 25443, which telescope to one; `newborn_state_draw` puts
`1-p` on `idx_of(1,0,0)=1` and `p` on `idx_of(1,1,0)=4`, both inside the loop bound at 22917,
`1..threshold_addiction_index=6`, so no newborn SMI mass falls outside the write loop. Newborn
inflow of one then equals the death outflow by the usual telescoping over a stationary cohort
structure. The thread-slot reduction at 23301–23311 sums slots `1..total_number_of_threads` and
`total_number_of_threads <= max_CPUs`, which is the first dimension of `vector_cpu_real`.

**(b) Does every transition-matrix row sum to one? YES in this configuration, and I derived it
rather than assumed it.** At `number_of_smi_states=2` the hand-written `unemployment_process`
block is dead (26063–26086 says so and the run prints which path it took); the live array is built
by `build_unemployment_process_smi` as the product
`employment_transition(e_c,e_f,d_f,m_f,h,p) * smi_transition(m_c,m_f,d_c,a)`.
`smi_transition` returns complementary pairs on both branches (6472–6503), so it sums to one over
`m_f`. `employment_transition` sums to one over `e_f` on all three branches: `sep*(1-p_ui) +
sep*p_ui + (1-sep)` from work, and `find + (1-find)` out of work under both the
`ui_first_period_only` and the stay-put arms (6558–6594). The row over the `sud_of(j)=d_f` block
is therefore `sum_{m_f} P_smi(m_f) * 1 = 1`. `addiction_transition` returns complementary pairs on
every branch (6109–6159), and `addiction_probabilities` is written as complementary pairs
throughout (25775–25817). `employment_process` is the identity for every age under
`fixed_productivity=1` (25543–25566). The `future_addiction_index_2` and `future_unemployment_index`
loop bounds in the distribution sweep (22715–22736) partition `1..12` into the clean block `1..6`
and the SUD block `7..12` exactly matching the `d_f` the row sums to one over.

Caveat, and it is a real one: **there is no live runtime check of these row sums.**
`verify_unemployment_process` runs only at `number_of_smi_states==1` (26063–26069) and all four
in-line row-sum diagnostics in `create_unemployment_process` (26116–26180) are commented out.
`verify_newborn_process` does check rows, but it checks `newborn_unemployment_process`, which is
read only from the dead newborn branch. See F-04 for the one probability vector that does not sum
to one.

**(c) `initialize_feasible_distribution` resets. CONFIRMED CORRECT.** It runs once per
discount-factor type and every reset in it is per-type by design: `distribution_guess` is zeroed
(21956–21962), `relative_endowments` / `fraction_with_positive_wealth` / `initial_endowment` /
`max_initial_endowment` are deterministic and identical on both passes, and the only two module
quantities it leaves behind that anything downstream reads are `value_of_initial_assets` and
`sum_of_distribution`, both of which are recomputed from scratch before any consumer sees them
(`sum_of_distribution` at 8609–8623 and eight other sites, each scaled by `mass_passes`;
`value_of_initial_assets` at 23331 in `converge_to_stationary_equilibrium`). Nothing in the
routine writes a pooled statistics accumulator. The unguarded resets are right.

**(d) `compute_homelessness_duration`. DEAD, but its output is still being published.** See F-06.

---

## Findings

### F-01 `mu_m` is in the paper's recovery equation and in no executed line of the model — HIGHEST SEVERITY

`addiction_transition` (6073–6157) takes an OPTIONAL eighth argument `smi_1`, and its own comment
says why:

>     ! OPTIONAL so that the twelve existing call sites stay valid while
>     ! they are wired one at a time. Absent means no SMI, which is what
>     ! the model was before, so leaving a site unwired is a silent
>     ! omission rather than a compile error. Every site that has the
>     ! unemployment index in scope should pass smi_of(it).

**Not one of the thirteen call sites passes it.** Lines 11510, 11527, 16913, 16980, 17436, 17995,
18413, 18776, 21678, 22760, 23165, 23188, 24036 all call with seven arguments. Two of those are in
this slice: 21678 in `internal_computations` (the continuation value) and 22760 in
`converge_to_stationary_equilibrium` (the distribution sweep), and `unemployment_index` is in
scope at both.

So `smi_used_1` is always 0, `recovery_with_smi(recovery_1,0)` returns its argument unchanged
(6437–6441), and `mu_m` multiplies nothing. `recovery_with_smi` has no other caller.

What it should do: the paper writes the recovery hazard as
`mu_H^{1{h'=h_1}} mu_m^{1{m=1}} g^tau` (`housing_first_children_later.src.tex:1560`, eq:frecover),
`mu_m` is set externally at 0.82 from dual-diagnosis relapse rates of 39.8 against 26.4 per cent
(`housing_first_children_later.src.tex:2415–2422`, and the code's own comment at 6429–6430), and
it has its own item in the calibration section. The model does not implement the equation the
paper states.

LIVE in the benchmark, in the value function and in the distribution alike.

What it would change: unknown, and I have not measured it. Directionally, wiring it multiplies the
recovery hazard by 0.82 for the SMI half of the SUD block, so SUD prevalence, the SUD-homelessness
overlap and everything calibrated against them move; `mu_m` is currently a parameter the
calibration cannot feel at all.

### F-02 `value_of_initial_assets` is summed over a THREAD NUMBER where the time period belongs

`converge_to_stationary_equilibrium`, 23339–23341:

>                         value_of_initial_assets=value_of_initial_assets+&
>                             distribution_implied(1)%vector_transition_real(thread_num+1,1,&
>                             initial_endowment(employment_index),unemployment_index,employment_index,0,0)*&
>                             financial_grid(initial_endowment(employment_index))

The first dimension of `vector_transition_real` is the time period everywhere else in the file;
here it is `thread_num+1`. The sibling accumulation in `initialize_feasible_distribution`
(22071–22077) uses `(time_period,1,...)`, which is what this should be.

Why it does not blow up today: `thread_num` is threadprivate (4478) and is set unconditionally to
0 at 22553 and 23010, so on the master thread `thread_num+1 = 1`; `transition_length = 1`, so
`distribution_implied` has first dimension `1:1` and index 1 is both in bounds and equal to
`time_period`. The right answer by coincidence.

LIVE ONLY IN THE TRANSITION. At `solve_transition_dynamics=1`, `transition_length=75`, the routine
is called as `converge_to_stationary_equilibrium(time_index)` (37699) and this line reads period 1
for every period. `value_of_initial_assets` is read by the resource constraint (28020, 28022), by
`bequests_less_initial_endowments` (26807) and by the bequest identity check (33816).

What it would change in the benchmark: nothing. In the transition: unknown, but every period after
the first would price initial endowments off period one.

### F-03 The mass-conservation diagnostic is switched off, and it is the only one there is

`converge_to_stationary_equilibrium`, 23490–23497:

>             if ((abs(sum_distribution_guess-sum_distribution_implied)>10.d0**(-10)) .AND. &
>                 (have_probablistic_death==0)) then

`have_probablistic_death=1` (1260), so the branch never runs. `sum_distribution_implied` and
`sum_distribution_guess` are computed at 23476–23488 and then thrown away. There is no other check
anywhere in the distribution iteration that the total mass is what it should be — the `DIST_MOM`
line at 23446 prints `mass=` but only every hundredth sweep and only when
`diagnose_distribution_max==1`, and it prints rather than tests.

I found mass to be conserved by reading (see (a) above), so this is not currently hiding a leak.
It is worth reporting because the whole audit turns on that property and nothing in the running
model would say if it broke. A test that works under probabilistic death is a comparison of
`sum_distribution_implied` against `1 + sum_{a=1}^{L-1} prod S(a)`, or simply against the previous
sweep's implied total once the guess has settled.

LIVE (as dead code) in the benchmark. Fixing it changes no number.

### F-04 `unconditional_unemployment_probability` does not sum to one after the first calibration loop

`GKKOC_intergenerational_employment_process`, 25292–25331. The vector is
`dimension(threshold_addiction_index)`, i.e. six long. It is zeroed at 25292. On
`loop_count >= 1` the `else` branch fills all six entries from the stationary distribution and
normalises them to sum to one (25302–25325), and then:

>             unconditional_unemployment_probability(1)=1 !0.95155279776391399
>             unconditional_unemployment_probability(2)=0 !3.4048867272342742E-002
>             unconditional_unemployment_probability(3)=1-sum(unconditional_unemployment_probability(1:2))

Entries 1, 2, 3 are overwritten with 1, 0, 0 while entries 4, 5, 6 — the SMI-clean block, indices
`idx_of(e,1,0)` for `e=1,2,3` — keep their measured shares. The vector then sums to
`1 + p4 + p5 + p6`, which is one plus the SMI share of the clean population.

Two separate defects in the same three lines. The row-completion at 25329 completes over `1:2` in
a vector of length six, which is the index-mismatch shape the brief warned about; and the whole
`else` branch's computation is overwritten for the only entries it was hardcoded for, so the twenty
lines above it are computed and discarded except for the SMI tail they were never written to
produce.

LIVE in the benchmark from the second calibration loop onwards. The only consumers are lines 22062
and 22069 in `initialize_feasible_distribution`, which build the INITIAL GUESS for the distribution
iteration. The iteration converges to a fixed point that does not depend on its guess, so this
changes no reported number; it inflates the starting mass by roughly the SMI share and costs sweeps.
It also inflates the `sum(distribution_guess)` line printed at 22126, which reads as a diagnostic.

What it would change: the sweep count, by an unmeasured amount. No moment.

### F-05 `years_left_on_mortgage_index_used` is used as an array index and never assigned

`initialize_feasible_distribution`. Declared at 21953:

>         integer :: has_house,financial_index,years_left_on_mortgage_index_used

and then used, twice, as the block index of `distribution_guess` at 22182 and 22185:

>                                         distribution_guess(years_left_on_mortgage_index_used)%vector_transition_real&
>                                             (0,age_index,financial_index,unemployment_index,employment_index,&

It is assigned nowhere in the routine and nowhere in the file. `distribution_guess` is
`dimension(1:2)`, so an uninitialised integer here is an out-of-bounds derived-type subscript on
both a read and a write. The loop it sits inside runs over `years_left_on_mortgage_index`, which is
plainly what was meant.

DEAD in the benchmark: the whole block is inside `if (solve_transition_dynamics==1)` (22151) and
`solve_transition_dynamics = is_counterfactual*0+(1-is_counterfactual)*0 = 0` (1376). It becomes
live the moment the transition is switched on, which per `CLAUDE.md` is being built now. It will
not fail loudly: gfortran zeroes static storage in practice and a local integer here will most
often read 0, which subscripts `distribution_guess(0)` — one element below the array.

What it would change: unknown; in the benchmark, nothing.

### F-06 `compute_homelessness_duration` is dead, and its unset output is written to the results file

The routine spans 23695–24127. Its only call site is line 36546 and it is commented out:

>     !            call compute_homelessness_duration(1)

as are the prints beside it (36548–36551). So `homelessness_duration`,
`homelessness_duration_everyone` and `homelessness_mass_by_age` are never assigned.

But `write_outputs` (28800, called at 6669, 6675 and 6681) is not commented out, and at 29225–29227:

>             do i=0,2
>                 write(2,*) "homelessness_duration_everyone,", homelessness_duration_everyone(time_period,i)
>             end do

`homelessness_duration_everyone` is declared at 3911 with no initialiser. The results file
therefore carries three numbers under a label that reads as a computed model moment and that no
code computed. They will read 0.000000 on any normal gfortran build, which is worse than a NaN
would be: a zero average homelessness duration looks like a result.

Two things follow, and they are separate from the brief's question about the 24-month moment:
- the routine is dead, not merely unprinted; and
- the "VALIDATION NOT COMPUTED: returns to homelessness within 24 months" line at 5343 is about a
  DIFFERENT quantity. `compute_homelessness_duration` computes an average spell length, not a
  re-entry rate within a window. Reviving it would not produce the untargeted moment the paper
  reports.

A second defect inside the dead routine, for whenever it is revived. At 24104–24108 the comment says

>                 ! this computes the average homelessness duration for everyone in a given addiction status of interest
>                 ! by taking adding the average duration of that age multiplied by the mass of future homeless for that age

but the code adds `homelessness_duration(time_period,age_index_1,addiction_index_1)` with no mass
weight, and then divides the sum by `total_homeless_count` at 24119–24121. The numerator is a sum
of per-age averages and the denominator is a mass, so the two are not commensurable. As written the
result is not the population average the comment describes.

DEAD. What it would change if the call were restored as-is: an incorrect number in place of a
missing one.

### F-07 `voucher_index_1` is `shared` in a `default(none)` parallel region and written inside it

`converge_to_stationary_equilibrium` declares it as a local at 22338:

>         integer :: financial_index,has_house,time_period,track_housing_1,voucher_index_1

and puts it in the `shared` clause of the distribution sweep's `!$omp parallel do default(none)`
at 22546:

>                                     !$omp& voucher_index_1,survival_probability_for_dist_iteration)

It is then written inside the loop, once per iteration, at 22674:

>                                             call compute_voucher_index_1(is_homeless_2,voucher_index_1)

and read twice afterwards — as an argument to
`calculate_future_voucher_index_and_opportunity` (22676) and as the fourth subscript of
`voucher_probabilities` (22754–22755). `is_homeless_2` depends on the policy's chosen future
housing status, which varies with `financial_index`, the parallel loop index, so the value genuinely
differs across iterations. Every other temporary in the same loop body — `is_homeless_2`,
`has_opportunity_2`, `first_voucher_index_1`, `second_voucher_index_1`, `choose_to_own`,
`financial_index_copy`, `fraction_copy`, `amortization_used_dist`, `addiction_choice_1`,
`treatment_choice_dist_1`, `drug_quantity_dist_1`, `thread_num` — is a threadprivate module
variable. `voucher_index_1` and `is_addicted_1` are the two that are not, and both are in the
`shared` list. That asymmetry is what makes this look like an oversight rather than a decision.

`is_addicted_1` is benign: it is a function of `unemployment_index` alone, an outer loop variable,
so every thread writes the same value. `voucher_index_1` is not.

**Currently harmless, and only by arithmetic accident.** In the benchmark
`voucher_probabilities` is identical across its fourth index in the benchmark: `increased_prob_of_voucher_if_homeless_1`
and `increased_prob_of_voucher_if_homeless_and_addicted` are both 1, so
`voucher_probabilities(0,1,1,:) = (p,p,p)` (25698–25702), the `==0` block (25678–25692) and the
`voucher_conditional_on_clean==1` enforcement block (25723–25742) are both skipped, and every other
assignment uses `(:)`. So a raced index selects an identical number.

It becomes a live nondeterminism the moment either multiplier moves off 1 — line 36622 carries
`increased_prob_of_voucher_if_homeless_1=1 !5.81`, so someone has already tried — or in any
Treatment First counterfactual, where `voucher_conditional_on_clean==1` makes index 3 differ from
1 and 2 by the whole detection and false-positive structure.

What it would change today: nothing. In the counterfactual: run-to-run nondeterminism in the
distribution, magnitude unmeasured.

### F-08 The distribution iteration reads `treatment_choice_now`, which it never sets

`compute_voucher_index_1` (22223–22273) decides `meets_condition_1` from the module variable
`treatment_choice_now`:

>         if ((include_treatment==1) .AND. (treatment_choice_now==1)) then
>             meets_condition_1=1

`treatment_choice_now` is threadprivate (4352) and is assigned only inside the value-function solve
(16571, 16617, 17098). `converge_to_stationary_equilibrium` never assigns it, so at the call at
22674 it holds whatever that thread's last backward-induction iteration left there — a value
belonging to a different state, and thread-dependent.

The household's actual treatment choice is in scope: `treatment_choice_dist_1` is read from the
policy function three lines earlier, at 22677–22680, and is passed correctly to
`addiction_transition` at 22766. That is the value `compute_voucher_index_1` should be keyed on.
The same applies at 23940 (dead branch) and at 23936–23942 in `compute_homelessness_duration` (dead
routine).

Inert in the benchmark for the reason given in F-07 — the voucher category selects among identical
probabilities. Live in the Treatment First counterfactual, where the whole point of the branch is
that a household in treatment is not the one the sobriety condition is aimed at, and where this
would decide it from a stale variable.

What it would change today: nothing. In the counterfactual: unknown.

### F-09 `objective` and `optimize_frac_spent_on_addiciton` have no `implicit none`

Every subroutine in the file after `end module Global_Vars` (6626) is an external procedure and
needs its own `implicit none`; `use Global_Vars` does not carry one across. Ninety-seven of the
ninety-nine have it. The two that do not are both in this slice: `objective` (19560, `use
Global_Vars` at 19565, no `implicit none`) and `optimize_frac_spent_on_addiciton` (20575).

I checked both scopes for names that are neither declared locally, nor dummy arguments, nor
module entities, and **found none** — no name is currently being typed implicitly. This is a latent
hazard, not a present bug.

It matters because the two documented build commands differ. `code/run_one_point.sh:280` compiles
with `-fimplicit-none`, which makes any misspelling an error everywhere and covers these two
scopes. `code/CALIBRATION_RUN_LOG.md:17`, the command recorded for the production calibration run,
is `-mcmodel=medium -fopenmp -O2 -ffree-line-length-none` with no `-fimplicit-none`. Under that
command these two scopes are exactly the conditions of the precedent the brief cites: a misspelled
name becomes an uninitialised real and nothing says so.

LIVE as a hazard in the benchmark under the CALIBRATION_RUN_LOG build. Changes no number today.

### F-10 `objective` leaves both `intent(out)` arguments unassigned on the `can_consume_1=0` path, and the caller reads them

`objective` declares `real(8), intent(out) :: MU_1,MU_2` (19567). On the final `else` at
20060–20064 it sets `can_consume_1=0` and returns without assigning either:

>         else
>                 
>             can_consume_1=0                
> 
>         end if

With `intent(out)` both become undefined on entry, so this is a return with two undefined outputs.
`secant`, at 19520, reads them on exactly that path:

>                     proceed_2=0
>                     distance_secant=abs(MU_1-MU_2)

and `distance_secant` is the `do while` termination test at 19393/19476. Under gfortran the dummies
alias the caller's variables, so what is read is the previous iteration's MU pair rather than
garbage, which is why this has not shown up; it is still an undefined read that the standard does
not sanction and that the loop's exit depends on. The three other call sites (19404, 19491, 19553)
guard on `can_consume_1==1` before reading, which is what 19520 does not.

Adjacent, one line outside the slice: 19535 reads `abs(MU_1-MU_1)`, always zero, so the "labor"
diagnostic beneath it can never fire. Presumably `MU_1-MU_2`.

LIVE in the benchmark. What it would change: unknown — the secant is bracketed and clamped, so the
likely effect is on iteration count rather than on the converged labour supply, but I have not
measured it.

### F-11 `+` where `*` was meant in the downpayment constraint

`internal_computations`, 21459–21460:

>                 if (-LTV_1<(1-minimum_downpayment+smallest_house*min_down_of_smallest+second_smallest_house+&
>                     min_down_of_second_smallest)) then

Six other sites in the file write the same expression correctly, with a product on both terms:
17230–17231, 17269–17270, 17795, 18202, 18246–18247. Only this one has
`second_smallest_house + min_down_of_second_smallest` instead of
`second_smallest_house * min_down_of_second_smallest`.

`second_smallest_house` is 0 or 1, so on the second-cheapest bracket the threshold is raised by a
full unit of loan-to-value. `min_down_of_second_smallest = (1-raise_min_down)*0` (1385) is
identically zero, so the correct expression there is `1-minimum_downpayment = 0.8` and the written
one is `1.8`. `-LTV_1` cannot exceed 1, so on that bracket the minimum-downpayment constraint would
be switched off entirely.

DEAD in this configuration. The enclosing branch is
`if ((LTV_1<financial_grid(fin_index_1)) .AND. (ownership_status_index_1==1))` (21411), and
`ownership_status_index_1 = max(min(amortization_used_dist-1,1),0)` at the call site (15999).
`include_ownership=0` (1434) makes `is_owner_better` always 0 in `which_is_better` (19207), the
policy's amortization index is always 1, and so `ownership_status_index_1` is always 0. Homeownership
is out of the model, as the comment at 3009–3012 says.

What it would change: nothing today. It is the kind of thing that will not be found again once
homeownership is switched back on.

### F-12 `total_number_of_threads` is assigned only on OpenMP sentinel lines

`converge_to_stationary_equilibrium` reduces the per-thread accumulators at 23301:

>                                         do thread_index=1,total_number_of_threads ! 1

`total_number_of_threads` is a module integer (4239) with no initialiser, and the only assignments
in the whole file are 22450, 22812 and 23238, each of the form

>                 !$ total_number_of_threads=omp_get_num_threads()

i.e. conditional-compilation sentinels. Compiled without `-fopenmp` those are comments,
`total_number_of_threads` is never set, the loop most likely runs zero times, and
`distribution_implied` stays identically zero — a silent total mass collapse. `thread_num` does not
have this problem: it is set unconditionally to 0 at 22553 and 23010 before the sentinel.

Both documented build commands pass `-fopenmp`, so this is not live today. It is a one-line
robustness gap in a routine whose failure mode is a zero distribution rather than a crash.

What it would change: nothing on the current builds.

### F-13 Computed and then discarded

Class 2 of the brief. All confirmed by reading every use of each name.

- **`bequest_1` in `objective`** (declared 19580, computed 19582–19590 via an `if` on
  `inheritance_function_of_productivity` and a call to `calculate_bequest_amount`) is never read.
  `objective` is called from inside the secant loop, so this is a wasted branch and subroutine call
  on the innermost path of the solve.
- **`bequest_1` in `internal_computations`** (declared 20972, computed 20974–20982, identical code)
  is never read either. Same cost, on the internal-grid path.
- **The KKK productivity process** is fully overwritten under `fixed_productivity=1`.
  `GKKOC_intergenerational_employment_process` calls `KKK_process` (25254) and
  `get_probabilities_KKK_process` (25263) to fill `employment_grid`,
  `unconditional_employment_probability` and `employment_process`. All three are then replaced:
  `unconditional_employment_probability` and `employment_grid(1,:)` by the p_edge quantile
  construction at 25536–25546, `employment_grid(age,:)` by the copy at 25460–25464, and
  `employment_process` by the identity loop at 25543–25566, whose lower bound is
  `fixed_productivity*1 + (1-fixed_productivity)*(life_span-retirement_span)` = 1. Nothing the two
  KKK calls produce survives. `fixed_productivity=1` (485) is a parameter.
- **`aitken_on_distribution`** (23614–23692) is never entered: `accelerate_distribution=0` (1555)
  and the two guards at 23529 and 23550 both test it. The comment block at 23503–23528
  describes it as the fix for the iteration being four fifths of a calibration loop; it is switched
  off. (Its logic reads correctly to me: the extrapolation is rejected on negative mass or a total
  moved by more than a part in a thousand, and it modifies only `distribution_guess` after the
  convergence distance has been taken, so it can never contaminate `distribution_stationary`.)
- **`build_a_prime_window`** (24832–24888) returns at its first line: `restrict_a_prime=0` (684).
  Documented at 665–684.
- **Declared and never used:** `newborn_census_i`, `newborn_census_clean`, `newborn_census_smi`
  (22353–22354) and `amortization_used` (22339) in `converge_to_stationary_equilibrium`;
  `amortization_used` (23702) in `compute_homelessness_duration`; `width_fixed_y` (25241) in
  `GKKOC_intergenerational_employment_process`. `sd_fixed_y` is assigned twice with the same value
  (25479 and 25484) and read only in a `loop_count<1` diagnostic.

### F-14 `compute_voucher_index_1`'s housing polarity does not match the name of the multiplier it selects

Flagged as a question rather than asserted as a bug, because it is inert as configured and I have
not been able to settle the intent from the code alone.

`is_homeless_1` is passed with the survival-array convention, 1 housed and 2 homeless. That is
fixed by `survival_probability(i,2,0,0) = 1 - min(1, kappa_phi_h_by_age(i)*(1-survival_probability(i,1,0,0)))`
at 24575–24576, where `kappa_phi_h` is the homelessness mortality multiplier applied at index 2,
and by both callers, which set the value from
`if (future_housing_status_index_to_use == lowest_housing_grid_point) is_homeless = 2` with
`lowest_housing_grid_point = -1` (21050–21056, 22666–22672).

`compute_voucher_index_1` then routes `is_homeless_1==1` — the HOUSED — to `voucher_index_1=2`,
and leaves the homeless at the default 1 (22254–22271). Index 2 of `voucher_probabilities(0,1,1,:)`
is the slot multiplied by `increased_prob_of_voucher_if_homeless_1` (25698–25701). So the
"increased probability if homeless" multiplier is applied to households that are not homeless.

The alternative reading is that the fourth index simply means (1 homeless, 2 housed, 3 disorder
untreated) and the parameter is misnamed. I cannot tell which from the source. It is inert either
way at present: `increased_prob_of_voucher_if_homeless=1` (90), so all three slots equal
`probability_of_voucher_benchmark_used_1` and the index makes no difference. It stops being inert
at line 36622, where the multiplier is set to 1 with `!5.81` commented beside it.

Worth resolving before that multiplier is moved off one.

### F-15 `voucher_probabilities` is never zeroed

`voucher_probabilities` is declared at 3257–3258 with no initialiser and
`create_unemployment_process` (from 25666) assigns only specific entries — there is no
`voucher_probabilities=0` anywhere in the file. In the benchmark path
`voucher_probabilities(1,0,1,1:2)` is assigned by neither the
`increased_prob_of_voucher_if_homeless_and_addicted==0` block nor the
`voucher_conditional_on_clean==1` block, both of which are skipped.

Not reachable today: `calculate_future_voucher_index_and_opportunity` returns
`first_voucher_index=second_voucher_index=include_vouchers=1` on the branch that has
`voucher_index==1` (22303–22307), so the `future_voucher_index=0` element is never read there, and
the branch that would widen the range to `0:1` is guarded by `is_counterfactual==1`. Listed only
because it is an unassigned array feeding a probability, and the module's implicit `SAVE` plus
gfortran's zeroed static storage is the only thing making it zero.

---

## What I found nothing in

- **No mass leak.** Both branches of the newborn inflow, the asset lottery, the survivor push and
  the thread-slot reduction conserve mass exactly. See (a).
- **No row of a live transition matrix fails to sum to one.** See (b). The one probability vector
  that does not is F-04, and it is a starting guess, not a transition.
- **No unguarded reset of a pooled accumulator** in `initialize_feasible_distribution`. See (c).
- **No OpenMP data race with an effect on a benchmark number.** I checked every module variable
  written by `objective` and `internal_computations` inside the value-function parallel region
  against the `threadprivate` list: the nine that are not threadprivate are the policy-function
  arrays, each written at the parallel loop's own index. `calculate_bequest_amount` uses the module
  loop counter `i`, which is threadprivate (4481). The two shared-clause slips are F-07, and only
  one of them can differ across iterations, and it selects among identical numbers today.
- **No array-bounds error that fires in the benchmark.** `verify_index_map` (24891–25037) is
  correct as written and its cardinality tests hold at `number_of_smi_states=2`.
  `dist_housing_1` is declared from `lowest_housing_grid_point`, per the comment at 22342–22352.
  `a_prime_allowed` is dimensioned `financial_grid_size` and only ever indexed 1..85.
  Newborns are written at housing index 0 and the source loop for `newborn_household=1` runs
  `lowest_housing_grid_point..0`, so they are picked up.
- **`compute_expected_child_value`** (25040–25138) reads correctly to me: the `large_negative_num`
  sentinel guard is right, the differencing at 25126–25129 is applied after the accumulation and
  within each parent node, and `expected_child_value` is re-zeroed at the top of every call so the
  differencing cannot compound.

## Two notes for the auditor holding 25643 onward

- The six row-completion lines the brief points at — 25939, 25940, 25971, 25972, 26006, 26007,
  26039, 26040 — are in the hand-written `unemployment_process` block, which is DEAD at
  `number_of_smi_states=2` (26062–26085). They are nonetheless wrong on their face and would come
  back with `number_of_smi_states=1`: the left-hand side is `(:,...)`, all ages, while the
  right-hand side is evaluated at age 1 only; and each completes a row over a three-wide slice
  (`2:3`, `5:6`) of what is now a six-wide block. Worth a verdict either way rather than leaving
  them.
- All four row-sum diagnostics in `create_unemployment_process` (26116–26180) are commented out,
  leaving four empty `do` nests. At `number_of_smi_states=2` nothing checks the live array's rows at
  runtime, and `verify_unemployment_process` is called only at one SMI state (26062–26069).
