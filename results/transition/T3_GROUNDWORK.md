# T = 3 groundwork for the T = 60 transition

Prepared 23 September in a fresh container on branch
`claude/two-period-addiction-hazard-d7gb61` at
`4e97f02`, source md5 `b181aee24a0ca2ca32294b70bd1a9d7f`.

(This note was rebased onto `94a794f` before pushing, because the live
counterfactual runs advanced the branch while it was being written. None of
their four commits touches the Fortran -- `git diff 4e97f02 94a794f --
housing_first_or_treatment_first_SR_v1.f90` is empty and the md5 above is
unchanged -- so every line number and measurement below still refers to the
source as it stands.)

**NOTHING IN THE FORTRAN WAS CHANGED AND NOTHING WAS PUSHED.** Three
counterfactual runs are live off this branch and the switch this note describes
turns transitions on for every one of them. Every binary here was built from a
`sed`-generated copy of the source in a gitignored build directory, exactly the
way `build_transition_t60.sh` already does it; the tracked
`housing_first_or_treatment_first_SR_v1.f90` is byte-identical to `HEAD`.

    compiler   GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
               -- the same version the T=45 arm was solved on; gfortran is NOT
               in the base image and was installed here.
    flags      -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium
               -O3 -funroll-loops
    box        4 cores, 15 GiB

---

## What this found, in one page

**The machinery works.** A T = 3 transition runs: prologue, backward pass,
forward pass, welfare, budget, price update, loop closure, and a second full
loop with both equilibrium instruments moving. Nothing failed.

**Raising the horizon is a no-op for a steady-state solve, proved twice.** The
before and after binaries at `is_counterfactual=0` are byte-identical
(md5 `a3d4bda31926fb6c9c172aea232b4035`), so a benchmark run after the change
cannot differ from one before it. The two one-block runs the brief asked for
agree anyway: `b` 0.083468653643308396 against 0.083466809898833066 and
`lambda_d` 0.035965729175956591 against 0.035964576278425552, both about
3e-5 relative, inside the 1e-4 rule.

**T = 60 is affordable.** The brief's 0.0746 GB per period is exactly right,
confirmed three ways. The T-independent constant is larger than the brief
assumes -- 6.09 GB rather than 4.93 -- because the peak is not where the memory
model was measured, so T = 60 is about 10.6 GB rather than 9.4. It still fits.

**But three things are wrong, none of which makes the run fail**, and the first
was measured in the log rather than reasoned out:

1. **The reform period draws its newborns against "every parent clean and
   housed."** `newborn_parent_share` is the live intergenerational channel, has
   no time index, and at t = 1 has no predecessor to read, so it takes a
   cold-start fallback. The T = 3 run reads `1.0, 0.0, 0.0` at t = 1 and
   measures `0.967, 0.0285, 0.0018` one step later. There is no seed file that
   would fix it: `seeds/benchmark_dat/` has none and the tracked one is 104
   zeros. **Every transition run made from the committed seeds has had this**,
   including the T = 45 arm in `results/`. Section 2c.
2. **The budget's term in the exit test is zero at loop 0 because it is never
   measured there**, and there is no `CONVERGENCE govt_budget` line to say so.
   After loop 0 the drug distance is the only live term, and seeding the drug
   price path -- which is the T = 60 plan -- is what makes that distance small.
   Section 1.
3. **The transition's CEV is the newborn cohort's and nobody else's.** The
   equilibrium integrates over the whole age distribution alive at the reform,
   correctly; the welfare *report* does not. The 59 caught generations have no
   consumption equivalent. Section 2a.

**And one correction to the standing instructions.** TRANSITION_LESSONS
section 14 certifies the child's keying off a branch that cannot execute -- the
source's own comment at line 32931 says the arm is dead. Its verdict is right,
its evidence is not, and it tells the next auditor to ignore the array that is
actually carrying the mechanism. Section 2b.

**The diff is safe to land in halves.** The horizon change alone compiles to a
bit-identical binary on *both* arms and can go in today. The
`solve_transition_dynamics` line is the one that breaks the three live
counterfactual runs. Section 4.

---

## 1. Does a T = 3 transition run to completion?

**Yes. It starts, it is the right model, and it produces welfare, mechanism and
budget numbers.** Nothing failed: `run.err` is zero bytes and no runtime error,
bounds violation or backtrace appears anywhere in the log.

    build      code/tr3_gw/       from a sed copy, 8 diff lines, guards passed
               is_counterfactual                             0 -> 1
               use_revenues_to_increase_voucher_probability   0 -> 1
               solve_transition_dynamics   is_counterfactual*1+(1-is_counterfactual)*0
               transition_length                            30 -> 3
               grandfather_voucher_states  0   ASSERTED by value in the generated file
               window_distributions        1   ASSERTED by value in the generated file
    run        code/t3_gw_run/    staged by stage_transition.sh
               initial condition  seeds/benchmark_dat/       90 files
               terminal condition seeds/arm3_counter_TF/     10 files
               handover           seeds/PARAM_HANDOVER_trans_postfix.txt
               price seed         first 2 entries of seeds/drug_price_path_seed_t60_nogf.txt
               check_transition_inputs.py:  79 required, 79 present
    threads    OMP_NUM_THREADS=2

The standing rule that transition tests are done at T = 3 is what makes this
affordable: one backward age pass is about 7.5 minutes at 60 ages, so loop 0's
two backward periods and two forward periods are well under an hour.

### The prologue is right, and every defect section 13 records is fixed IN THE RUN

This matters more than it looks, because all three of those defects produced no
error and a plausible-looking log. Checked against the run's own output rather
than against the source:

    TRANSITION INIT: file_number=counter_TF_transition
    TRANSITION INIT: old_results=baseline_benchmark
    TRANSITION INIT: benchmark_simulation=baseline_benchmark
    TRANSITION INIT: long_run_simulation=counter_TF
    TRANSITION INIT: transition_length=           3
    TRANSITION INIT: renter_floor_by_age(1:5)=  3  3  3  3  3
    TRANSITION INIT: smallest_house_size=   4.0674274685127916E-002
    TRANSITION INIT: initial condition kept, mass=   50.861206888360229
    TRANSITION INIT RESTORED loop=           0  mass=   50.861206888360229

- **`long_run_simulation=counter_TF`, not `baseline_benchmark`.** Defect 1 --
  the one that would have solved the path from the benchmark TO the benchmark
  and reported a reform that does nothing, converging cleanly the whole way.
- **`file_number=counter_TF_transition`**, so the transition's own outputs
  cannot overwrite the arm files it is still reading its terminal condition
  from.
- **`renter_floor_by_age` is 3 before the distribution is built.** Defect 2 --
  the out-of-bounds write at index 0 of a dimension starting at 3.
- **The handover was applied: 102 `HANDOVER` lines echoed against the 102 lines
  handed over.** That is the receipt `run_one_point.sh` exists to count, and it
  is the difference between running Treatment First and running the Fortran's
  declared defaults while looking healthy. Spot-checked on two that prove it is
  not the declared vector: `addiction_onset_base 0.0 -> 3.3600679648463409E-002`
  (declared zero is the collapse where nobody develops a disorder) and
  `discount_factor 0.94400000572204590 -> 0.94653324195575295`.
- **The price path seed was read and is in force**: `DRUG PRICE PATH seeded
  FROM FILE, entries read= 2 of 2`, and `t=1 0.92738703055540905` against the
  seed file's own first entry `0.927387030555409`.

### What the run reached, and what it produced

The backward pass ran to completion over both periods and all 60 ages
(118 `AGE_TIME` lines, 59 per period). The forward pass then re-solved the
policies at t = 1, converged the distribution, ran the statistics, and printed:

    TRANSITION WELFARE loop= 0  t= 1  with_childhood= 792.20409841074240
                                      youngest= 1352.2122427650268
                                      benchmark_youngest= 1352.0465724142973
    TRANSITION MECH t= 1  h_1= 7.7082381684724227E-003
                          b= 4.6125463830616172E-002
                          lambda_d= 3.3609216800936308E-002
                          p_drug= 0.92738703055540905
                          pi_v= 7.6876159888350143E-002
    TRANSITION WELFARE DIAG t= 1  current_beta_type= 1  number_of_beta_types= 1
                          mass at t-1= 50.861206888360229
    TRANSITION BUDGET loop= 0  t= 1  net_govt_revenues= 6.0519500612071555
                          constraint= 6.0212721765369999  residual= 3.0677884...E-002

Three things in that block are worth stating rather than passing over.

**`mass at t-1 = 50.861206888360229` is the whole benchmark population**, at the
exact line the welfare is computed, which is the runtime half of the check in
section 2a: the economy the reform lands on is the full age distribution and
not a cohort.

**The budget is printed at loop 0.** That is section 15's fix in force -- the
residual used to be computed only inside `if (loop_count>start_updating_at_loop_number)`,
which is also where pi_v moves, so the whole first loop printed nothing about
the budget and a run with `net_govt_revenues` sitting at zero looked healthy for
three and a half hours. Here loop 0 reports a residual of 0.0307 against a
constraint of 6.021, which is 0.5 per cent and already inside the 5e-2 rule.

**The welfare number is real rather than the zero the diagnostics were added to
explain.** `with_childhood= 792.2` is non-zero and `current_beta_type` equals
`number_of_beta_types`, so neither of the two candidates for a zero applies.

### Loop 0 closed, loop 1 opened, and both instruments moved

The run was carried past loop 0 deliberately, because closing the loop is a
different claim from running the passes. It closed:

    largest_housing_market_distance=   0.0000000000000000
    largest_rental_market_distance=    0.0000000000000000
    largest_distance_govt_budget=      0.0000000000000000
    CONVERGENCE drug_market distance=  0.11651339654025572  rule= 5.0E-003  OPEN
    loop_count=           1
    solving value functions

and loop 1 reproduced the initial condition exactly --
`TRANSITION WELFARE DIAG t= 1 ... mass at t-1= 50.861206888360229`, the same
digits as loop 0 -- which is the `init_keep` restore working.

**Both equilibrium instruments move.** The drug price updated between loops,

    loop 0, t=1   p_drug= 0.92738703055540905
    loop 1, t=1   p_drug= 0.92275009550627562

and pi_v, gated off at loop 0, moved at loop 1 on its own period's residual:

    TRANSITION PI_V loop= 1  t= 1  pi_v= 7.8410510324625385E-002
        budget_residual= 3.0687008268232674E-002  step= 1.534...E-003

against the 7.6876159888350143E-002 it was held at through loop 0. So the
machinery the transition needs -- backward pass, forward pass, welfare, budget,
two instruments, loop closure and restore -- is all exercised and all works.

**The welfare path is already flat at T = 3**, which is what one should expect
and is not a result about anything:

    loop 0, t=1   with_childhood= 792.20409841074240   youngest= 1352.2122427650268
    loop 1, t=1   with_childhood= 792.20253511822921   youngest= 1352.2141990187079

2e-6 relative between loops. T = 3 is a machinery test, not a transition: the
drug market is still open at 0.117 against a rule of 0.01, so the path has not
converged and nothing here should be read as an economic result.

### WHAT THE RUN EXPOSED: THREE OF THE FOUR EXIT-TEST DISTANCES ARE ZERO AT LOOP 0, AND ONE OF THEM IS ZERO BECAUSE IT WAS NEVER MEASURED

Section 15 of TRANSITION_LESSONS is *"a diagnostic must not share a gate with
the instrument it diagnoses"*, and it cost a 3.5-hour loop. The fix was applied
to the PRINT. It was not applied to the EXIT TEST, and the T = 3 run printed the
evidence at the close of loop 0:

    largest_housing_market_distance=   0.0000000000000000
    largest_rental_market_distance=    0.0000000000000000
    largest_distance_govt_budget=      0.0000000000000000
    loop_count=           1

while, forty lines earlier, the budget residual for the same loop was

    TRANSITION BUDGET loop= 0  t= 1  net_govt_revenues= 6.0519500612071555
        constraint= 6.0212721765369999  residual= 3.0677884...E-002

**The residual is 0.031 and the number in the convergence test is 0.000.** They
are different quantities. `distance_govt_budget` and `largest_distance_govt_budget`
are computed only inside

    55097:  if (loop_count>start_updating_at_loop_number) then
    55099:      distance_govt_budget=adjust_taxes*abs(net_govt_revenues(time_index)-net_govt_revenue_constraint)
    55101:      if (distance_govt_budget>largest_distance_govt_budget) then
    55103:          largest_distance_govt_budget=distance_govt_budget

which is the same gate pi_v moves behind. `largest_distance_govt_budget` is
zeroed before the per-period sweep (line 54607), so on any loop where the update
is gated off it ends the loop at exactly zero -- the value that means "the
budget clears in every period".

**Why that is not academic.** The exit test is

    54549:  do while ((largest_housing_market_distance>...) .OR. &
            (largest_rental_market_distance>...) .OR. &
            (largest_distance_govt_budget>...) .OR. &
            (largest_distance_drug_market>...) .OR. (loop_count<1))

`peg_prices_in_counterfactual=1` zeroes the housing and rental terms by design.
`loop_count<1` is false once loop 0 has incremented the counter at line 55570.
So **after loop 0 the drug-market distance is the only term that can keep the
run alive**, and whether the budget was ever measured has no bearing on it.

**Confirmed by carrying the run into loop 1.** The same quantity, printed at the
close of each loop:

    loop 0   largest_distance_govt_budget=   0.0000000000000000
    loop 1   largest_distance_govt_budget=   3.0687008268232674E-002

The 0.0307 at loop 1 is the same residual the loop-0 `TRANSITION BUDGET` line
already printed. Nothing about the economy changed between the two loops to
make the budget stop clearing; what changed is that the gate opened and somebody
measured it.

It did not fire here: the T = 3 run reported

    CONVERGENCE drug_market distance=  0.11651339654025572  rule= 5.0000000000000001E-003  OPEN

0.117 against a rule of 0.005 x 2, so the loop continued and loop 1 began, where
the gate opens and the budget starts being measured. **But the thing that saved
it is the thing the T = 60 launch plan is designed to remove.** Seeding the drug
price path is exactly what makes that distance small at loop 0 --
`seeds/drug_price_path_seed_t60_nogf.txt` exists for that purpose, and the
seeds README says the ramp "cost about ten loops on the T=30 arm". A well-seeded
cold-start T = 60 run whose drug distance opens inside 1e-2 would exit after
loop 0 and report a converged transition whose budget was never in the test.

**The condition is precise, so it can be checked before launching.** The gate is
`loop_count > start_updating_at_loop_number`, and line 54472 sets
`start_updating_at_loop_number = -1` when `seed_count_2 > 0`, that is when a
`pi_v_path_seed.txt` was read. With a pi_v seed the budget IS measured at loop 0
and the hazard does not exist. This run had none --

    PI_V PATH: no pi_v_path_seed.txt, flat at   7.6876159888350143E-002
    PI_V GATE: cold start, pi_v updates from loop 1 (start_updating_at_loop_number=0)

-- which is why it is visible here. **So: a T = 60 launch that seeds the drug
price path must also seed pi_v, or it is exposed.** The T = 45 session seeded
both, which is presumably why this has not been seen before.

**And the log gives no way to notice.** `report_convergence_terms()` prints a
`CONVERGENCE <name> distance= ... rule= ... OPEN/closed` line for every term it
covers -- `drug_market`, `drug_threshold`, `convexity_of_rental_company` and
twenty more -- and **there is no `CONVERGENCE govt_budget` line at all**. A
reader cannot distinguish "zero because it cleared" from "zero because nobody
looked".

Two one-line fixes, both cheap and neither requiring the run to change
behaviour: move the two `largest_distance_govt_budget` lines OUT of the
`loop_count>` gate and leave only the pi_v update inside it, which is what
section 15 says; and give the budget a row in `report_convergence_terms()`.

### One difference from the steady-state run, traced and benign

The transition prints

    smallest_house_size*free_market_rent_to_house_price*housing_price(1)/net_income_lowest=  NaN

where the steady-state control prints `2.4951914176877468`. Traced: the
transition calls `set_smallest_house_size()` in the prologue, BEFORE
`initialize_variables_and_grids()`, so `employment_grid(1,1)` is still zero and
`net_income_lowest` is zero; the print is 0/0.

**It is not a transition defect and not new.** `long_run_counter_factual` has
the same order (`set_smallest_house_size` at 52374, grids at 52493), so the
three live counterfactual arms print the same NaN today; only
`calibrating_model` builds the grids first (47035 before 47173), which is why
the benchmark control differs. And the branch taken at `loop_count<1` assigns
`smallest_house_size = smallest_rental_relative_to_lowest_income` directly and
never reads `net_income_lowest`, so only the diagnostic is affected: both runs
report the identical `4.0674274685127916E-002`. Worth knowing before somebody
sees a NaN in a T = 60 log and stops the run.

### Timing, for sizing T = 60

    backward age pass, 60 ages, 2 threads      about 7.5 min
    loop 0 backward pass (T-1 = 2 periods)     about 15 min
    forward period (re-solve + distribution
      + statistics + welfare + revenues)       about 12 min

At T = 60 the backward pass is 59 periods and the forward pass 59, so one path
iteration is roughly 59 x (7.5 + 12) = 19 hours at two threads, and about
11 hours at four on the measured 3.5x OpenMP scaling this repository records.
That is in line with the 16-30 hours TRANSITION_LESSONS already quotes for the
recompute-forward design, and it is per LOOP -- the T = 45 arm needed more than
one.

**How many loops is the open question, and this run gives a first number with a
large caveat.** Two loops closed here, and the live convergence condition moved

    loop 0   CONVERGENCE drug_market distance=  0.11651339654025572   rule= 5.0E-003  OPEN
    loop 1   CONVERGENCE drug_market distance=  0.10880745627490562   rule= 5.0E-003  OPEN

-- a fall of 6.6 per cent per loop. Extrapolated naively that is about forty
loops to reach the rule, which at T = 60 would be months and is obviously not the
plan.

**The caveat is bigger than the number**, so do not carry the forty across. This
T = 3 run was seeded with the FIRST TWO ENTRIES of a 59-entry path seed, because
that is all a 3-period horizon can use, so it is close to the linear ramp that
`seeds/README.md` records as costing "about ten loops on the T = 30 arm". A
T = 60 run seeded with the whole of `drug_price_path_seed_t60_nogf.txt` starts
far closer and should need far fewer. The honest reading is that **the loop count,
not the per-loop cost, is what sizes a T = 60 run**, and that this test says
nothing reliable about it -- which is itself worth knowing before an overnight
run is booked on a per-loop figure alone.

It also sharpens the exit-test finding above. The better the seed, the smaller
the loop-0 drug distance, and the drug distance is the only term standing between
a cold-start run and an exit at the end of loop 0.


## 2. The two TRANSITION_LESSONS checks

### 2a. Does the transition integrate over the whole age distribution alive at the reform?

**The equilibrium does. The CEV that gets reported does not.** These are two
different layers and only the first has ever been audited.

**The initial condition is the whole benchmark age distribution.** In
`initialize_feasible_distribution`, gated on the transition switch:

    32077:  if (solve_transition_dynamics==1) then
    32085:      do age_index=1,life_span
    ...
    32119:          distribution_guess(years_left_on_mortgage_index)%vector_transition_real&
    32120:              (0,age_index,financial_index,unemployment_index,employment_index,&
    32121:              housing_status_index,voucher_index)=&
    ...
    32125:              distribution_to_fetch(years_left_on_mortgage_index)%vector_real&
    32126:              (age_index,financial_index,unemployment_index,employment_index,&
    32127:              housing_status_index,voucher_index)

`do age_index=1,life_span` with `life_span=60` (line 507): every age alive at
the switch is carried in, not just newborns. The T=3 run confirms it at
runtime -- `TRANSITION INIT: initial condition kept, mass= 50.861206888360229`,
which is the whole benchmark population (the steady-state control's own warm
start reports `sum= 50.745559768178460`).

The forward pass then pushes that whole distribution: `converge_to_stationary_equilibrium`
reads `distribution_guess(...)%vector_transition_real(time_period-solve_transition_dynamics, age_index, ...)`
over the same age range, and `stationary_equilibrium_statistics` accumulates
over `do age_index=1,life_span` (line 14192).

**Who supports the reform is measured over everyone alive.**
`frac_of_households_in_support_of_policy(time_period)` (line 24621) runs
`do age_index=1,life_span` and produces `frac_in_support(t)`,
`frac_in_support_addicted(t)` and `frac_in_support_by_tenure_and_employment(t,:,:)`.
That is a genuine whole-age-distribution welfare statistic, it is computed
every period of the path, and it is written out --
`write(2,'(F14.12)') frac_in_support(1:transition_length-1)`. It is the ONLY
whole-population welfare object the transition driver saves, and it is a
support share rather than a consumption equivalent: it says how many households
alive prefer the reform, not what it is worth to them.

**THE CEV IS NOT.** The number the transition prints as its welfare path, and
the only one converted to a consumption equivalent, is the cohort *born* at t:

    54712:  call calculate_welfare(time_index)
    54727:  call calculate_childhood_utility(time_index)
    54767:  write(*,*) "TRANSITION WELFARE loop=", loop_count, " t=", time_index, &
    54768:      " with_childhood=", average_welfare_with_childhood(time_index), &
    54769:      " youngest=", average_welfare_of_youngest_cohort(time_index), ...
    54815:  call calculate_welfare_gains(time_period,average_welfare_with_childhood(time_index),1,cev_this_period)

and the source's own comment at 54730 says what that object is:

    ! average_welfare_of_youngest_cohort is the value function at
    ! age 1 -- ADULT life only.

Inside `calculate_welfare` the accumulation is gated `if (age_index==1)`
(line 21288), and the divisor is `sum_of_distribution_youngest`. So
`cev_this_period` is the CEV of the newborn cohort of period t and of nobody
else.

That is exactly the object section 1 of TRANSITION_LESSONS says is not a
transition: *"The households the reform actually falls on were not in the
figure at all... The transition must integrate over the whole age distribution
alive at the switch, not just follow newborns."* In the stylized model the gap
between the two readings was 0.08 percentage points against 8.7 per cent of
consumption. Here there are **59 caught generations with no CEV of their own**:
the households aged 2..60 at the reform appear in the equilibrium, in
`frac_in_support`, and in the mechanism series (`TRANSITION MECH` prints `h_1`,
`b`, `lambda_d` per period), but nothing converts their value change into a
consumption equivalent.

**This is a reporting gap, not an equilibrium error, and it is cheap to close**
relative to a T = 60 run -- `calculate_welfare_gains` already exists and
`distribution_stationary` at t-1 is live at exactly the line the welfare block
sits on. It should be closed BEFORE T = 60 is launched, because the run is the
expensive part and re-running it to add a number is the expensive mistake.

### 2b. Does the child's inherited penalty key on the period the parent DIES in?

**Yes -- but NOT by the route TRANSITION_LESSONS section 14 records, and that
section's reasoning is now inverted.** Both halves were re-checked here.

**The value function half is correct.** `child_continuation_value` (line 10420)
takes `homeless_1`, and at its main call site that argument is the CHOSEN
housing status, not the entering one:

    26091:  is_homeless_1=1
    26093:  if (future_housing_status_index_to_use==lowest_housing_grid_point) then
    26095:      is_homeless_1=2
    ...
    26355:  ! The second index was already the choice: is_homeless_1 is
    26356:  ! set from future_housing_status_index_to_use above.
    26359:  child_continuation_value(age_index,is_homeless_1,addiction_index,&

with the author's 26-to-50 age gate inside it: the death probability up to 49,
weight one at `child_at_home_last_index`, zero after. A revocation that puts a
household on the street in the period it dies is in the index the child
inherits from.

**The forward-pass half is correct too, but section 14 proves it off DEAD
CODE.** Section 14 quotes the newborn write at line 33290,

    newborn_employment_probability(future_employment_index, employment_index, &
                                   is_addicted_1, is_homeless_2)

with `is_homeless_2` set from `policy_function_housing_status_index(...)(time_period,...)`.
That write is unreachable. It sits in the `else` of

    32929:  if ((have_probablistic_death==1) .OR. (newborns_inherit_addiction==0)) then

and the source says so itself, immediately underneath:

    32931:  ! THIS IS THE NEWBORN ROW, AND IT IS THE ONLY ONE. The branch
    32932:  ! below, which builds newborns out of the households that die and
    32933:  ! is the one both newborn arrays were written for, is unreachable:
    32934:  ! have_probablistic_death is one and newborns_inherit_addiction is
    32935:  ! zero, so this arm always runs.

`have_probablistic_death=1` (line 2754) and `newborns_inherit_addiction=0`
(line 1371), both compile-time parameters, so the branch section 14 audited has
never executed.

**The live channel is `newborn_parent_share`,** which section 14 explicitly
tells the next auditor to ignore: *"newborn_parent_share looks like it ought to
be the thing that carries this and is NOT: its only consumer is
print_all_moments. It is a diagnostic... it must not be read as the
transmission channel."* It is the transmission channel. Line 32980, in the arm
that always runs:

    32980:  newborn_productivity_draw(:)=newborn_productivity_draw(:)+&
    32981:      newborn_parent_share(newborn_parent_node_1,&
    32982:      newborn_d_index_1,newborn_h_index_1)*&
    32983:      newborn_employment_probability(:,newborn_parent_node_1,&
    32984:      newborn_d_index_1,newborn_h_index_1)

**And that channel keys correctly.** It is built in
`stationary_equilibrium_statistics`, over every age, weighted by the death
hazard, on the CHOSEN housing status:

    14192:  do age_index=1,life_span
    ...
    14255:  housing_status_index_used=policy_function_housing_status_index(years_left_on_mortgage_index)%&
    14256:      vector_transition_integer(time_period,age_index,financial_index,&
    14257:      unemployment_index,employment_index,housing_status_index,voucher_index)
    ...
    14998:  is_homeless_1=1
    15000:  if (housing_status_index_used==lowest_housing_grid_point) then
    15002:      is_homeless_1=2
    ...
    15014:  ! Weighted by the probability of dying, because a newborn
    15015:  ! replaces a household that dies and the death hazard is
    15016:  ! itself a function of the disorder and of homelessness.
    15017:  newborn_parent_share_acc(employment_index,is_addicted_1,is_homeless_1)=&
    15018:      newborn_parent_share_acc(employment_index,is_addicted_1,is_homeless_1)+&
    15019:      distribution_mass_used*(1-survival_probability(age_index,is_homeless_1,&
    15020:      is_addicted_1,smi_of(unemployment_index)))

The variable is *named* `is_homeless_1`, but line 14255 shows it holds the
policy function's output -- the same period-2 object the dead branch called
`is_homeless_2`. So the rule holds: the child inherits the parent's state in
the period it dies, which is the period conditionality acts in. **The name is
the trap here.** Anyone auditing this by grepping for `is_homeless_2` will find
only the dead branch and conclude the live one is wrong; anyone grepping for
`is_homeless_1` will find the name of the error and conclude the same. Only
line 14255 settles it.

**The keying is right; the VALUE the keying is applied to is not, in the one
period that matters.** These are separate questions and only the first is what
section 14 asked. `newborn_parent_share` is indexed correctly -- by the parent's
productivity node, its disorder state, and its CHOSEN housing status at the
period it dies -- and at t = 1 of a transition the array it indexes into holds
the cold-start fallback rather than the benchmark's composition. Section 2c
below is that finding, and it was measured in this run rather than reasoned out.

### 2c. MEASURED: the transition's FIRST period draws its newborns against a parent composition of "everyone clean and housed"

Section 7's "Carried forward: newborn_parent_share needs a time index before the
transition runs" is **live, and worse than it was written down as**. It is the
transmission channel, not a diagnostic, so the defect is in the mechanism; and
the T = 3 run shows it firing, in the reform period, in the log.

**What loop 0 printed.** `converge_to_stationary_equilibrium` prints the share
it is about to draw newborns against; `stationary_equilibrium_statistics`
prints the share it has just measured. In order, from `t3_gw_run/run.log`:

    t=1 READ   newborn_parent_share (clean housed, disordered housed, clean street, ...)
               =  1.0000000000000000   0.0000000000000000   0.0000000000000000
    t=1 WRITE  parents replaced by newborns: clean housed= 0.96708503899839415
               clean homeless= 1.7906142126064412E-003  disordered housed= 2.8469009685325335E-002
    t=2 READ   newborn_parent_share = 0.96708503899839415  2.8469009685325335E-002  1.7906142126064412E-003
    t=2 WRITE  parents replaced by newborns: clean housed= 0.96728678036225224
               clean homeless= 1.7821796762782260E-003  disordered housed= 2.8208456100937761E-002

Two things are visible at once.

**The within-loop lag is CORRECT.** t = 2 reads exactly what t = 1's statistics
wrote, to the last digit. Period t's newborns are drawn against the parents
measured at t-1, which is when those parents died. The merged forward loop

    do time_index=1,max(transition_length-1,1)
        call solve_value_function_and_policy_functions(time_index)
        call converge_to_stationary_equilibrium(time_index)   ! READS
        call stationary_equilibrium_statistics(time_index)    ! WRITES
        call govt_revenues_calc(time_index)

produces that lag by construction, and it is the right one.

**t = 1 HAS NO SUCH PREDECESSOR, AND FALLS BACK TO A DEGENERATE VALUE.** The
`1.0, 0.0, 0.0` at t = 1 is not the benchmark. It is the cold-start fallback in
`GKKOC_intergenerational_employment_process`:

    36053:  if (sum(newborn_parent_share)<=10.d0**(-12)) then
    36055:      newborn_parent_share=0
    36057:      do employment_index=1,employment_base_size
    36059:          newborn_parent_share(employment_index,0,1)=&
    36060:              p_edge_1(employment_index+1)-p_edge_1(employment_index)
    36062:      end do
    36064:  end if

-- the unconditional productivity distribution with **every parent clean and
housed**. Against the benchmark's true composition, which the run's own t = 1
statistics measured one step later, that puts 2.85 per cent of parents who carry
the disorder and 0.18 per cent who are on the street into the no-penalty column.

**So in the period the reform lands, no child inherits anything.** The
intergenerational channel -- `weight_on_child = 0.055`,
`penalty_child_addicted = 0.24` in this arm -- is switched off for the cohort
born at the reform. Under `fixed_productivity` the newborn draw is that
household's productivity for life, so that cohort carries the error to the end
of the horizon.

**It is invisible.** `1.0, 0.0, 0.0` is a perfectly well-formed probability
vector, it sums to one, the population is preserved (`mass at t-1 =
50.861206888360229`), and by t = 2 the numbers look right. Nothing fails.

### Why it is not self-correcting: loop 1 was run, and it reads the END of loop 0

`newborn_parent_share` appears NOWHERE in `transition_simulation` -- grep over
lines 53557-55798 returns nothing -- so it is neither restored nor re-seeded at
the top of a loop. The T = 3 run was carried into loop 1 to test that, and the
three READs and three WRITEs line up exactly as predicted:

| | READ, at the top of the period | WRITE, by that period's statistics |
|---|---|---|
| loop 0, t = 1 | **1.00000000000000000**  0.0  0.0 | 0.96708503899839415  2.8469009685325335E-002  1.7906142126064412E-003 |
| loop 0, t = 2 | 0.96708503899839415  2.8469009685325335E-002  1.7906142126064412E-003 | 0.96728678036225224  2.8208456100937761E-002  1.7821796762782260E-003 |
| loop 1, t = 1 | **0.96728678036225224**  2.8208456100937761E-002  1.7821796762782260E-003 | 0.96708498100955809  2.8468908040757371E-002  1.7906141052367371E-003 |
| loop 1, t = 2 | 0.96708498100955809  2.8468908040757371E-002  1.7906141052367371E-003 | 0.96728574276742796 ... |

**Every READ is the previous WRITE, with no reset anywhere.** That is the whole
mechanism in one sentence: the array is a single unbroken one-step chain running
from the first period of the first loop to the last period of the last one, and
the loop boundary is invisible to it. Read down the diagonal:

- **Within a loop the lag is correct.** t = 2 reads t = 1's write to the last
  digit, in loop 0 and again in loop 1. Period t's newborns are drawn against
  the parents measured at t-1, which is when those parents died.
- **At the loop boundary the same chain keeps running, and that is the defect.**
  loop 1, t = 1 reads loop 0, t = 2's write -- the composition at the END of the
  transition -- when the thing it needs is the benchmark's composition the
  instant before the reform. Nothing distinguishes "the previous period" from
  "the previous period of the previous loop", because nothing ever resets.
- **And the run tells us what that correct value is**, because loop 1's t = 1
  statistics measure it one step later: 0.96708498100955809, which agrees with
  loop 0's t = 1 write to eight significant figures. So t = 1 reads
  0.96728678 where it should read 0.96708498, and the disordered-housed share it
  draws against is 2.8208E-2 against a true 2.8469E-2.

The error in loop 1 is small -- 0.9 per cent on the disordered share -- and the
error in loop 0 is total, because the fallback puts that share at zero. Neither
is the right number and neither converges to it, because the array is never
returned to the initial condition.

**The contrast with the distributions is the point.** The same run prints

    TRANSITION INIT RESTORED loop=           0  mass=   50.861206888360229

so the four distribution arrays ARE snapshot in the prologue and restored at the
top of every loop, which is the fix line 9128 documents at length. Four arrays
carrying the initial condition were protected. The fifth -- the one carrying the
intergenerational channel -- was not, and nothing in the log distinguishes
them.

The comment at line 36051 says the fallback fires "only if nothing has set it:
a resumed run reads its own shares from the state file and must not be
overwritten." **The transition never calls `read_calibration_state`,** so it can
never be that resumed run: the T = 3 log contains no
`newborn_parent_share resumed:` line at all, where the steady-state control
prints one. The transition is structurally always a cold start for this array.

### AND THERE IS NO SEED FILE TO FIX IT WITH

`stage_transition.sh` already tries, and its own comment already knows what is
at stake:

    # The warm start. Optional: it shortens nothing and changes nothing, but the
    # newborn shares are the intergenerational channel's own state and starting
    # without them switches it off for a block.
    for f in calibration_distribution1.dat calibration_distribution2.dat \
             calibration_distribution_shape.dat newborn_parent_share.dat; do
      [ -f "$BM/$f" ] && cp "$BM/$f" "$N/$f"
    done

It copies it if it is there. **It is not there.** `seeds/benchmark_dat/` holds
90 files and none of them is `newborn_parent_share.dat`, so the `[ -f ]` test
silently fails and the run starts without it -- the staging log says nothing,
because the copy is conditional and the condition is false.

The one copy in the repository, `code/newborn_parent_share.dat`, is tracked and
is **104 entries of exactly zero**, total sum 0.0. Staging that file would not
help: `sum(newborn_parent_share)<=1e-12` is precisely the test at line 36053, so
it would trip the same fallback.

**So every transition run made from the committed seeds -- including the T = 45
arm already in `results/`, and including T = 60 unless this is fixed -- has had
the intergenerational channel off in its first period.**

### The fix, which is cheap and belongs before T = 60

Three parts, in increasing order of correctness:

1. **Harvest a real `newborn_parent_share.dat` into `seeds/benchmark_dat/`.**
   The benchmark solve computes it and `write_calibration_state` writes it
   (line 45219). This is a file copy and it removes the degenerate t = 1.
   It does not fix the cross-loop leak.
2. **Restore it at the top of every path iteration**, exactly as the four
   distributions already are. The machinery and the precedent both exist --
   `init_keep_guess/stat/prev1/prev2` and the
   `TRANSITION INIT RESTORED loop= 0  mass= 50.861206888360229` line the run
   prints -- and `newborn_parent_share` is 104 doubles, so a fifth snapshot
   costs nothing. This is the smallest change that makes loop k open like
   loop 0.
3. **Give it the time index section 7 asked for**,
   `newborn_parent_share(transition_length,employment_grid_size,0:1,1:2)`,
   written by the sweep at the period it measured and read by the distribution
   iteration at the period it is building, with slot 0 seeded from the
   benchmark. That is the version that is right rather than merely consistent.

Section 7 predicted the symptom exactly -- *"a composition that is slightly off
in a model where the composition is the mechanism, and nothing about it looks
wrong on inspection"* -- and asked for it to go in BEFORE the transition was
turned on. It did not.


## 3. Measured GB per transition period

**The brief's 0.0746 GB per period is exactly right.** It was checked three
independent ways -- empirically by moving the horizon, analytically from the
allocation, and by enumerating every `allocate` in the file that carries the
horizon at all -- and they agree.

### Empirically, by moving the horizon

Two transition binaries identical but for `transition_length`, staged from the
same seeds and run to the same point (post-allocation, first backward age
pass), RSS sampled every 2 s from `/proc/<pid>/status`:

| horizon | RSS plateau | samples held |
|---|---|---|
| T = 3 | 2.6493 GiB (2,777,940 KiB) | 310+ |
| T = 9 | 3.0666 GiB (3,215,572 KiB) | 124 |

    slope = (3.0666 - 2.6493) / (9 - 3) = 0.4173 / 6 = 0.06955 GiB per period

Both plateaus are flat and both are reached **before** the backward pass starts
descending, so this is an allocation-level measurement and not an artefact of
which slices happen to be resident: the T = 9 run was still printing
`TRANSITION INIT` lines while already holding its full 3.0666 GiB.

### Analytically, from the allocation itself

    43399:  allocate(value_function(i)%&
    43400:      vector_transition_real(transition_length,life_span+1,is_owner*1+(1-is_owner)*renter_array_floor:&
    43401:      financial_grid_size,unemployment_grid_size,employment_grid_size,(1-is_owner)*lowest_housing_grid_point+&
    43402:      is_owner*index_of_smallest_house_hhld_can_buy:housing_status_grid_size-1,0:(1-is_owner)*voucher_state_max))

Evaluated at this build's own constants (by compiling the module and reading
them out, not by hand): `life_span=60`, `financial_grid_size=27`,
`unemployment_grid_size=18`, `employment_grid_size=26`,
`housing_status_grid_size=3`, `lowest_housing_grid_point=-1`,
`voucher_state_max=2`, `renter_array_floor=3`,
`index_of_smallest_house_hhld_can_buy=2`:

    renter block (i=1)        8,564,400 doubles
    owner  block (i=2)          770,796 doubles
    TOTAL per period          9,335,196 doubles  =  74,681,568 bytes
                              = 0.069553 GiB  =  0.074682 GB

Measured 0.06955 GiB against analytic 0.069553 GiB. **The two agree to five
significant figures.**

### And nothing else in the file is sized by the horizon

This is the check that makes the slope safe to extrapolate, and it is the one
worth having rather than assuming. Joining Fortran continuations first and then
scanning every `allocate` statement in all 55,798 lines:

    ALLOCATE statements whose bounds mention transition_length :  1   (line 43399, value_function)
    ALLOCATE statements using dslot_lo:dslot_hi                 : 12   (distributions, = 1:1 here)
    ALLOCATE statements using tslot_lo:tslot_hi                 : 32   (policy functions, one slice)

`dslot_hi` is `window_distributions*1+(1-window_distributions)*transition_length`
and `window_distributions=1`, so the twelve distribution arrays are 1:1 and
T-independent. **`value_function` is the only structure in the model whose size
depends on the horizon**, exactly as the memory-window design claims. So
whatever else the peak is made of, its T-dependence is 0.074682 GB per period
and nothing else.

### Two corrections to the brief's arithmetic, neither of which changes its conclusion

1. **The unit is GB (10^9), not GiB.** 0.0746 is `9,335,196 x 8 / 1e9`. In
   binary units the same quantity is 0.0696 GiB. Everything downstream --
   the 4.93 GB constant, the 9.41 GB at T = 60, the 13.36 GB cap -- is
   therefore in GB, and must not be compared against an RSS figure in GiB.
   A 7 per cent error in the direction that flatters a feasibility call.
2. **The element count is 9,335,196 per period, not 10,020,348.** The brief's
   own 0.0746 GB corresponds to 9,335,196, so the GB figure is right and the
   count is the slip. (The renter block alone, 8,564,400, is the number stamped
   in `scan_seed/calibration_distribution_shape.dat`, which is probably where
   it entered.) `10,020,348 x 8 / 1e9` would be 0.0802 GB.

### THE PEAK IS NOT THE PLATEAU, AND THE BACKWARD PASS IS MISLEADING

This is the part worth reading twice, because measuring the horizon cost at the
wrong moment gives a number that is right and a total that is not.

The T = 3 run held a flat 2.6493 GiB through the whole backward pass and through
the forward pass's first value-function solve -- 310 consecutive samples -- and
then **jumped to 5.7101 GiB** the moment
`converge_to_stationary_equilibrium` started writing, rose to 5.8549 GiB in the
second forward period, and drifted only to 5.8779 GiB across two complete loops:

    T = 3 backward-pass plateau   2.6493 GiB = 2.8447 GB
    T = 3 PEAK                    5.8779 GiB = 6.3113 GB   (over two full loops)

Both figures agree with the same slope -- at the plateau the implied constant
is 2.6206 GB from T = 3 and 2.6206 GB from T = 9, to four decimals, which is the
internal check that growth is linear -- but they imply very different totals.

**The jump is 3.21 GiB and it is almost entirely one array:**

    43535:  allocate(distribution_implied_private(i)%&
    43536:      vector_cpu_real(max_CPUs,life_span+1,...

`max_CPUs` is a `parameter` fixed at 40 (line 9165), and the remaining
dimensions are the same 7-d shape as one `value_function` slice. So it is
40 x 0.069553 = **2.7821 GiB**, which is 87 per cent of the observed jump. It is
allocated in `allocate_matrix` up front but only becomes resident when the
forward pass first writes into it, which is exactly where the jump appears.

Two things follow, and both matter for T = 60:

- **It is T-independent**, so it does not change the slope -- it changes the
  constant, and the constant must be taken from the PEAK.
- **It is also independent of the thread count.** It is sized at `max_CPUs=40`
  whether the run uses 2 threads or 4, so the T = 3 peak measured here at
  `OMP_NUM_THREADS=2` is directly comparable to a 4-thread T = 60 run.

### The T = 60 projection, from the measured peak

    peak(T) = 6.087 GB + 0.074682 * T          (constant = 6.3113 - 3 x 0.074682)

    T =  3   6.31 GB   <- measured, 5.8779 GiB over two complete loops
    T = 30   8.33 GB
    T = 45   9.45 GB
    T = 60  10.57 GB
    T = 75  11.69 GB
    T = 120 15.05 GB

Broken out at T = 60, in GiB:

    value_function, 60 slices            4.173 GiB
    distribution_implied_private (x40)   2.782 GiB
    everything else                      2.887 GiB
    ------------------------------------------------
    TOTAL                                9.842 GiB  =  10.57 GB

**T = 60 fits, with about 2.8 GB of headroom against the 13.36 GB cap the brief
quotes.** It is tighter than the brief's 9.41 GB, because the true constant is
6.09 GB rather than 4.93 GB, but the conclusion is unchanged. T = 120 does not
fit, which the brief also said.

### The headroom lever, if T = 60 ever turns out tight

`max_CPUs=40` on a four-core box is 2.78 GiB reserved for 40 thread slots of
which four are used. Sizing that array to the real thread count would return
36/40 of it -- **2.50 GiB, or 2.69 GB** -- which is more than the whole
difference between the brief's projection and this one, and would take T = 60
to about 7.85 GB and T = 120 to about 12.3 GB. It is a one-line change to a
`parameter` and it is the cheapest memory available in this model. It is NOT
needed for T = 60; it is recorded so that nobody reaches for a coarser time
grid or `real(4)` before reaching for this.

Note this box reports `memory.max` unlimited with 15 GiB (16.1 GB) of RAM and
no swap, rather than the 13.36 GB cgroup cap the brief quotes; a T = 60 run
should be sized against the cap it will actually meet.


## 4. The steady-state no-op control

### The strongest form of it: the two benchmark binaries are BIT-IDENTICAL

The control asked for was one benchmark moment block before the change and one
after. There is a stronger version available for free, and it is the one
TRANSITION_LESSONS section 13 already reaches for when it says a change meant
to be a no-op should be proved by comparing the compiled object rather than by
re-running an arm. Section 13 settled for a disassembly diff over 202
functions. Here the comparison is exact:

    pristine source, is_counterfactual=0   md5 a3d4bda31926fb6c9c172aea232b4035
    landing diff,    is_counterfactual=0   md5 a3d4bda31926fb6c9c172aea232b4035

Same compiler, same flags, same 1,721,984-byte binary, byte for byte. At
`is_counterfactual=0` the diff compiles away entirely: `solve_transition_dynamics`
constant-folds to `0*1+1*0 = 0`, `transition_length` to `(1-0)*1+0*60 = 1`,
`dslot_lo=dslot_hi=1`, and every `allocate` is what it was. **A benchmark or
calibration run after the change cannot differ from one before it, because it
is the same program.** That is stronger than any number of runs, because it
covers every input rather than the one that was tried.

### And the same test shows exactly what the change DOES break

The reason the brief says not to push this is confirmed, not assumed. The same
two sources compiled at `is_counterfactual=1` -- the configuration the three
live counterfactual runs use:

    pristine source,      is_counterfactual=1   md5 0babc63f1b2ebdf60d778b22983b8cf0
    horizon change only,  is_counterfactual=1   md5 0babc63f1b2ebdf60d778b22983b8cf0
    full landing diff,    is_counterfactual=1   md5 5cd71eac31652d522e0e90991a85bc68

**The two lines are not equally dangerous, and this is worth having.**

- **`transition_length` 30 -> 60 on its own is a no-op EVERYWHERE, including on
  the counterfactual arm.** Bit-identical binary. While
  `solve_transition_dynamics` is zero the parameter collapses to
  `(1-0)*1+0*60 = 1` in every build, so the horizon is unreachable and the
  constant is dead text. It can be landed today, against the three live runs,
  with no risk at all.
- **`solve_transition_dynamics` is the line that breaks them.** It is the only
  one that changes the counterfactual binary, and it changes it into a
  different program: `main_program` branches on it and calls
  `transition_simulation` instead of `long_run_counter_factual`. A live arm
  rebuilt from a source carrying it would not solve a steady state at all.

So the landing can be split, and probably should be: the horizon now, the
switch when the arms are done.

### The runs that were asked for

Both from `code/scan_seed/` unchanged -- `calibration_state.dat`, the two
gzipped distributions (`calibration_distribution1.dat` verified at 265,496,400
bytes, shape stamp 8564400), and `PARAM_HANDOVER_base.txt` with the single
edit `frozen_stop_after_blocks 0 -> 1`, which is what makes the run stop after
exactly ONE block. `weight_on_child` is 0 and `freeze_all_but_omega_c` is 1, so
every adjuster is frozen and a block is one clean iteration of the equilibrium
map. `OMP_NUM_THREADS=2`.

**Reference values, stated before the runs** (from
`code/scan_seed/PROVENANCE.txt`, the converged source run `oc2c0`):

    b        = 9.8916056747807166E-002
    lambda_d = 4.3579290623499613E-002

### RESULT: the control passes

|  | BEFORE | AFTER | relative difference |
|---|---|---|---|
| `b` | 0.083468653643308396 | 0.083466809898833066 | **2.21e-05** |
| `lambda_d` | 0.035965729175956591 | 0.035964576278425552 | **3.21e-05** |
| `h_1` | 0.007126657711096049 | 0.0071263554635781559 | 4.24e-05 |
| average labour income | 1.1459965086423596 | 1.145997256547417 | 6.53e-07 |

All four are inside 1e-4 relative, which is the standard this note was told to
judge on and not equality, because the model is not bit-reproducible in general.
**Raising the horizon is a no-op for a steady-state solve.**

### Two honest notes on what these numbers are

**The residual difference is OpenMP noise and cannot be anything else.** The two
binaries are byte-identical, the inputs are byte-identical, and the thread count
is the same, so the only source of difference is reduction order across threads.
That makes the table above a useful by-product: **2e-5 to 4e-5 is this model's
own run-to-run spread on b and lambda_d at two threads**, which is the floor any
future comparison of two solves has to beat before it means anything.

**One block from this seed does NOT reproduce the seed's converged values, and
should not be read as a failure to.** The reference stated above --
b = 0.0989, lambda_d = 0.0436 -- is where the source run `oc2c0` ENDED after 22
loops. Both runs here report b = 0.0835 and lambda_d = 0.0360, about 16 and 17
per cent below it, and both report `BLOCK MOVE 1.0` against a rule of 1e-3, so
the economy is nowhere near still. That is what one block from a restart looks
like: the distribution re-converges from the loaded warm start and the
equilibrium map moves the moments before the blocks settle again. It is
irrelevant to the control, which asks only whether the two runs agree with each
other, and they do. It would be very relevant to anyone reading 0.0835 as a
measurement of this calibration.


## 5. The exact diff needed to enable T = 60 -- WRITTEN OUT, NOT PUSHED

Against `code/housing_first_or_treatment_first_SR_v1.f90` at
`b181aee24a0ca2ca32294b70bd1a9d7f`. Two lines, four diff lines:

```diff
--- a/code/housing_first_or_treatment_first_SR_v1.f90
+++ b/code/housing_first_or_treatment_first_SR_v1.f90
@@ -2946 +2946 @@
-        integer, parameter :: solve_transition_dynamics=is_counterfactual*0+(1-is_counterfactual)*0
+        integer, parameter :: solve_transition_dynamics=is_counterfactual*1+(1-is_counterfactual)*0
@@ -2948 +2948 @@
-        integer, parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*30
+        integer, parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*60
```

(The trailing whitespace on line 2946 is preserved; the sed used here matched
the parameter text only and left the padding alone.)

`is_counterfactual*1+(1-is_counterfactual)*0` rather than a flat `1` is what
keeps the benchmark and calibration arms untouched: at `is_counterfactual=0`
the parameter is 0, `transition_length` collapses to `(1-0)*1+0*60 = 1`, and
every array allocates exactly as before. Section 4 proves that.

### LANDING THIS BREAKS SEVEN BUILD SCRIPTS, AND THEY MUST MOVE IN THE SAME COMMIT

This is the operational cost of landing it and it is easy to miss, because the
scripts fail SAFE -- they refuse rather than building the wrong thing -- which
means the failure arrives as a refusal at build time rather than as a wrong
number later. That is the good failure mode, but it still stops every
transition build until they are updated.

Seven scripts `sed` on the old `solve_transition_dynamics` text and will match
nothing, so their `diff`-line guards will refuse:

    build_t3_cap.sh  build_t45_cap.sh  build_transition.sh
    build_transition_gf.sh  build_transition_nogf.sh
    build_transition_t45.sh  build_transition_t60.sh

Four of those also `sed` on `solve_transition_dynamics*30` and will match
nothing once the horizon is 60:

    build_t3_cap.sh  build_t45_cap.sh  build_transition_t45.sh
    build_transition_t60.sh

Worked through for `build_transition_t60.sh`: after the diff lands, its
`is_counterfactual` and `use_revenues...` seds still match (4 diff lines) and
its other two match nothing, so it sees 4 where its guard demands 8 and
**refuses**. `build_transition.sh` sees 4 against 6 and refuses; `build_t3_cap.sh`
sees 4 or 6 against 8 or 10 and refuses. None of them builds the wrong binary,
which is the guard working -- but none of them builds at all. The fix is to
reduce each to ASSERTING the two values by value in the generated file, exactly
as they already do for `grandfather_voucher_states` and `window_distributions`,
rather than setting them. The same rule the
repository already records for `run_one_point.sh` and `PARAM_HANDOVER` applies
here: **a structural parameter set in the SOURCE is worthless if a script also
names it**, and a `sed` that silently matches nothing is the failure that rule
exists to catch.

### Landing it is not sufficient to launch T = 60

Four things in this note should be settled first. All four are cheap; all four
are expensive to discover after a 19-hour loop; and none of them makes the run
fail, which is why they need doing rather than watching for.

1. **Harvest `newborn_parent_share.dat` into `seeds/benchmark_dat/` and restore
   it per path iteration (2c).** As it stands the reform period draws its
   newborns against "every parent clean and housed", so the intergenerational
   channel -- the mechanism the paper is about -- is off in period 1 and on the
   wrong period's composition in every loop after the first. MEASURED, not
   inferred. This is the one I would fix before anything else.
2. **Move `largest_distance_govt_budget` out of the pi_v gate, and give the
   budget a row in `report_convergence_terms()` (section 1).** Until then, a
   cold-start T = 60 run that seeds the drug price path -- which is the plan --
   can exit after loop 0 on a budget term that is zero because nobody measured
   it. **If this is not fixed, seed `pi_v` as well as the drug price**, which
   sets `start_updating_at_loop_number=-1` and closes the hole.
3. **Add a CEV for the generations alive at the reform (2a).** A T = 60 run that
   reports only newborn welfare answers the question section 1 of
   TRANSITION_LESSONS says is the wrong one, and re-running is the expensive way
   to add the number. The stylized model's `caught()` is the template, including
   its warning to integrate over the assets households actually saved.
4. **Correct TRANSITION_LESSONS section 14 (2b).** Its verdict is right and its
   evidence is dead code, so the next auditor who follows it will look at a
   branch that cannot run and will not look at line 14255, which is where the
   answer is.

A T = 60 run also still needs the two committed steady states on disk
(`seeds/benchmark_dat/`, 90 files, and `seeds/arm3_counter_TF/`, 10 files) and
a price path seed; `seeds/drug_price_path_seed_t60_nogf.txt` carries 59 entries,
which is T-1 and correct for T = 60.

---

## 6. Section 7 of TRANSITION_LESSONS: the rows these findings owe that table

Section 7 is standing and runs both ways: a bug found in one model is checked
against the other before it is closed, and the answer is written into the table
whether it carried across or not. These are quantitative-model findings, so
they belong in the **second** table -- "bug found in the quantitative model |
does the stylized model have it?".

**I have not edited `TRANSITION_LESSONS.md`.** It is the author's standing
instruction file and the brief authorised one file, this one. The rows are
written out here, checked against the stylized model's source rather than
asserted, and are ready to paste.

| bug found in the quantitative model | does the stylized model have it? |
|---|---|
| **The transition's CEV is the newborn cohort's and nobody else's.** The equilibrium carries the whole age distribution alive at the reform -- `initialize_feasible_distribution` seeds slot 0 over `do age_index=1,life_span` -- and `frac_of_households_in_support_of_policy` measures support over every age. But `calculate_welfare` accumulates under `if (age_index==1)` (line 21288) and `cev_this_period` is computed off `average_welfare_with_childhood(t)`, the cohort BORN at t. The 59 caught generations have no consumption equivalent of their own | **No, and it is the one place the stylized model is ahead.** This is precisely the bug section 1 records the stylized model having and FIXING. `transition.py` carries `caught(par, pv_new)` (line 350) alongside `path()`, exports `tr_caught_tf` / `tr_caught_hf`, and draws the initial old "at cohort 0" on the same axis as the cohort path (line 618), so the figure shows both readings at once. Its comment at line 363 adds the rule the quantitative model will need when it closes this: integrate over **the assets they actually saved**, because the caught generation's loss is 32.6 per cent at zero assets and 8.7 per cent integrated. The quantitative model's `distribution_stationary` at t-1 is live at exactly the line the welfare block already sits on, so the integration is available where it is needed. |
| **The transition's first period draws newborns against a parent composition of "everyone clean and housed", and there is no seed file that would fix it.** `newborn_parent_share` is the live transmission channel (line 32980, in the arm that always runs), has no time index, is never restored between path iterations, and at t = 1 has no predecessor to read -- so it falls back to line 36053, the unconditional productivity draw with every parent clean and housed. MEASURED in the T = 3 run: t = 1 reads `1.0, 0.0, 0.0` where its own statistics measure `0.967, 0.0285, 0.0018` one step later. `seeds/benchmark_dat/` has no `newborn_parent_share.dat`, and the tracked `code/newborn_parent_share.dat` is 104 zeros, which trips the same fallback | **No, by construction, and the design difference is the lesson.** The stylized model's analogue is the mixture `p` inside `path()` (line 486): a LOCAL variable, initialised `p = p0.copy()` from the pre-reform rest point on every call and threaded explicitly through `for t in range(1, n+1)`, so it cannot survive between calls, cannot be read at the wrong cohort, and has no cold-start branch to fall into. Section 9's bridge (`_bridge_grids`, `_bridge_hl_by_shift`) is the same discipline applied to the first step: the generation straddling the reform is built EXPLICITLY rather than defaulted. The rule to carry is the one the quantitative model already applied to its four distributions at line 9128 and did not apply here: **any array carrying the initial condition must be snapshot in the prologue and restored at the top of every path iteration** -- and an array with a cold-start fallback must say in the log which branch it took, because `1.0, 0.0, 0.0` is a well-formed probability vector and fails nothing. |
| **The budget's term in the transition exit test is computed inside the gate that also moves pi_v, so at loop 0 it is zero-because-unmeasured, and there is no `CONVERGENCE govt_budget` line to say so.** Section 15's fix moved the budget PRINT out of that gate; `largest_distance_govt_budget` stayed in (line 55097). MEASURED: loop 0 ends with `largest_distance_govt_budget= 0.000` beside a printed residual of `3.07E-002`. With housing and rental zeroed by `peg_prices_in_counterfactual=1` and `loop_count<1` spent, the drug distance is the only live term after loop 0 | **The mechanism does not arise -- `transition.py` has no government budget at all, which section 10 already records as one of the two channels absent from it -- but THE CLASS DOES, and the stylized model has already fixed its instance.** Section 8's settling test was the same shape: it measured each cohort against the last one COMPUTED, so a path still drifting at the end of a short run reported the end and read as converged. The fix is the one the Fortran's budget term needs: the stylized model now exports `tr_horizon`, what was actually computed, and `tr_drift`, the gap between the last two cohorts (transition.py lines 775 and 778), **so the convergence claim can be checked rather than trusted.** The Fortran's equivalent is one row in `report_convergence_terms()` -- it prints an OPEN/closed line for `drug_market`, `drug_threshold` and twenty more, and none for the budget. **The general rule, which neither model had written down: a quantity in a convergence test must be printed with the test, and a quantity that can be skipped must be distinguishable in the log from one that was measured and came back zero.** |
| **An audit note certified the child's keying off a branch that cannot execute.** TRANSITION_LESSONS section 14 verifies the newborn write at line 33290 (`is_homeless_2` from the policy function at `time_period`) and concludes the forward pass keys correctly. That branch is the `else` of line 32929 and is unreachable: `have_probablistic_death=1` (line 2754) and `newborns_inherit_addiction=0` (line 1371) are both compile-time parameters and the source's own comment at 32931 says the arm is dead. The conclusion happens to be right -- the live channel keys correctly too, at line 14255 -- but it was reached from code that has never run | **The class is live in it and one instance was already paid for.** Section 11's `children.py` row is the same shape from the other side: a module solved its own parameter vector at import and *every number it produced* was at that vector, and a transition table had to be withdrawn. Both are "the thing being audited is not the thing running". The guard that closes it is cheap and neither model has it: **before certifying a branch, establish that it executes** -- by a constant-fold check where the gate is `parameter`, or by a counter where it is not. In the Fortran the check is one `grep` of the two parameters at lines 1371 and 2754; nothing in section 14 recorded having done it. |

