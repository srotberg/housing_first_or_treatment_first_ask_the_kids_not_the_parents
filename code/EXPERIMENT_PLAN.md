# The plan after convergence

## THE LIVE STATE, 8 September 18:15. Read this first; the sections below are the design.

The four Phase 1 runs of 17:52 COMPLETED and are SUPERSEDED. They were solved
through `calibrating_model()` with the policy switches flipped, which is not a
counterfactual: the voucher eligibility threshold re-equilibrated instead of
being held at the benchmark's median, no tax cleared the government budget, and
`p_v` never moved. Their points are `point_914c6dd5eb` (TF rationed),
`point_bbc416b4fa` (universal HF), `point_2208a6b871` (universal TF). Keep them
as a first pass; do not put them in the paper.

Three model edits then landed on the author's instruction (commit 7e13fa42):
the two government costs of homelessness and disorder to zero,
`clear_drug_market` called in the counterfactual's loop, and
`distance_drug_market` added to its convergence test. Those reset the archive.

### The queue, in order. One step per firing.

1. **RUNNING.** The benchmark re-solve at the frozen vector on the new economy,
   `code/bench_rerun_nocosts.log`, launched 18:05. Its purpose is a CHECK, not a
   new calibration: with the costs zeroed nothing feeds back off
   `net_govt_revenues` while a fixed vector is measured, so **every calibration
   moment should be unchanged** against the superseded `point_6876263050` in
   `points_superseded/`. If any moved, that claim was wrong and the reason has
   to be found before anything else proceeds.

2. **The benchmark SAVE run.** A point run stops at line ~41704 inside
   `if (sweep_addiction_scalar==1)`, immediately after the moments, so it never
   reaches `save_vars_and_functions(1)` and writes no `*baseline_benchmark.dat`.
   Without those the counterfactual has no `median_income` to freeze the voucher
   threshold at, no `govt_revenues_to_use_in_tests` to use as its budget
   constraint, and no `average_labor_income_by_employment` to refill the zeroed
   profile the `STOP` at 29464 guards. Build a variant with
   `sweep_addiction_scalar=0` and `diagnostic_simulation=1` -- their max is
   `re_do_simulation_with_fixed_parameters`, so the vector is still measured
   rather than calibrated -- and note that `addiction_scalar_1` must then come
   through `PARAM_HANDOVER` (case at 37620) because the sweep grid is what
   normally carries it.

3. **The counterfactual binary**, `is_counterfactual=1`. It cannot be a handover
   parameter: seven other `parameter` declarations are initialised from it
   (1650, 1797, 2114, 2116, 2245, 2953, 4365, 4376), so it is a build-time
   substitution into a generated copy of the source. Keep the master byte
   identical so the point archive stays valid. Both binaries run in ONE
   directory, because the counterfactual reads the benchmark's `.dat` files.

4. **Re-run the four experiments** through `long_run_counter_factual()`.

5. **The v=0 TF condition.** The author, 8 September: *"As for the TV
   experiment, I want it to be conditional on v=0. So any use is forbidden if you
   want a voucher"* and then *"and yes, TF is v=0 and no SUD"* -- BOTH, so a
   disordered household abstaining without treatment does not pass.
   `compute_voucher_index_1` (~25882) currently keys category 3 on the disorder
   state alone. `v` is a choice, not a state, and is in scope at only three of
   the six call sites (17458, 20065, 22063, 24609, 26358, 27670).

6. **The validation table** re-run against a current-economy point, so the
   "34 or less" age bands and the all-household wealth and income shares appear.

### What does NOT need doing, checked rather than assumed

`upload_vars` (33404, 33434-33437) refreshes every `*_calibrated` aggregate from
the benchmark's files at run time, and in `long_run_counter_factual` it is called
at 42053, BEFORE the `GKKOC` guard at 42096. So the stale numbers in the
declarations look dangerous and are not used, once step 2 exists.

`set_files_names` (8879 onward) already names the experiments -- `counter_VTE_TF`,
`counter_VTE_HF`, `counter_TF` -- keyed on exactly the two switches
`run_experiments.sh` sets. It does NOT distinguish `voucher_conditional_on_clean`,
so a TF run with testing and one without would write to the same files. That
needs a name before both are run.


The author's, given at 02:13 UTC on 8 September, in their own words:

> once the program converges, i think we should do the experiments to see how the
> model performs. one is keeping pi_V in the benchmark and doing TF with cost of
> testing all eligibiles and false positive and false negative. then do a
> universal HF and universal TF (all Long run equilibria). after we do these it
> would be good to maybe do further calibrations like we said about lambda_d and
> try to understand why so many young are users relative to the data. but also,
> it would be good to get the untargeted statistics

**The order is theirs: experiments FIRST, further calibration SECOND.** That is
the opposite of the instinct to keep calibrating until everything is in band, and
it is deliberate -- the experiments are what say whether the model is worth
calibrating further.

## Phase 1, the experiments. All LONG-RUN EQUILIBRIA, no transitions.

### 1a. Treatment First at the benchmark voucher rate

Hold `probability_of_voucher_benchmark_used` at its benchmark value -- pi_V stays
where the calibration put it -- and make the voucher conditional on being clean.
Charge the programme for:

- the cost of testing EVERY eligible, not only those who fail;
- false positives, clean households denied a voucher;
- false negatives, using households granted one.

The author's phrase is "cost of testing all eligibiles", and "all" is the
operative word: the budget carries a test for each eligible household rather than
a test for each detection.

### 1b. Universal Housing First

### 1c. Universal Treatment First

## Phase 2, further calibration, only after Phase 1

### 2a. lambda_d, the SUD dose-response gradient

Design recorded in `CALIBRATION_STATE.md` at 01:50 on 8 September. In short: the
onset hazard is `min(addiction_onset_base + (1 - exp(-lambda_addiction*q)), 1)`
and `lambda_addiction` is currently 0, so it is FLAT -- conversion is whoever the
base hazard catches, regardless of how much they use. The target is that heavier
users are on average **3.22 times** more likely to acquire a SUD.

**One question is open and must be settled before building it.** The author said
"more than the mean v" on 8 September; the earlier specification was the **53.9th
percentile**. For a right-skewed quantity distribution those are different points
and the 3.22 would be identified off a different comparison. ASK.

### 2b. Why the model's users are so young

Mean age of users is 34.3 against 45.5 in the data, and 65 per cent of users are
26-34 against 28 per cent. Two leads are already measured and recorded:

- **Treatment is not the cause.** `d(mean age)/d log tau_u = +13.65 years`, so
  LESS treatment gives a YOUNGER stock. Landing tau_u makes the profile worse,
  not better.
- **Mortality is the better candidate.** Drug deaths are 0.321 of all deaths
  against 0.200 observed, +60 per cent, so users are killed before they reach 45.
  `kappa_phi_d_level` is ASSIGNED at 8.0, the midpoint of a literature range of 6
  to 10, and is pinned. Six is inside that range.

## Phase 3, the untargeted statistics

Their state as of 8 September is in `CALIBRATION_STATE.md` at 01:20. Note the
unit trap recorded there: the `UNTARGETED homelessness rate, band k` lines print
the model's ANNUAL rate against HUD's raw POINT-IN-TIME observed, a factor of
5.27 apart. Use the scored gaps, never those lines.

## What already exists, checked rather than assumed

- `voucher_conditional_on_clean`, line 199, with
  `voucher_conditional_on_clean_just_addicts` at 192.
- `cost_per_drug_test` already feeds `govt_spending_on_drug_tests` at line 15490,
  gated on the same switch, so the testing cost is ALREADY in the government
  budget and does not need adding.
- `is_counterfactual`, line 5, retunes the rental and inheritance tolerances and
  turns on `use_old_results`.
- `probability_of_voucher_benchmark_used` IS settable from `run_one_point.sh`,
  which is exactly what "keeping pi_V in the benchmark" requires.
- THE DETECTION PARAMETERS EXIST, BUT NOT UNDER THE NAMES THIS FILE FIRST GAVE.
  `p_det`, `p_fp` and `c_test` are the PAPER's notation and appear nowhere in the
  Fortran; grepping for them returns nothing, which is exactly the trap a heading
  reading "checked rather than assumed" should not have set. The code names are

      probability_of_detection        = 0.9      line 214
      probability_of_false_positive   = 0.05     line 215
      cost_per_drug_test              = 0.00031  line 231

  All three are plain `real(8)`, not parameters, so they are mutable -- but see
  the settability note below. They do nothing in the benchmark because
  `voucher_conditional_on_clean` is 0. Per `CLAUDE.md` they belong with the
  experiment and must NOT be added to the calibration table.

- NONE OF THE THREE IS SETTABLE FROM `run_one_point.sh`: no handover case, no
  whitelist entry. Being a `real(8)` rather than a `parameter` makes them
  changeable in source, not from a vector. Varying detection or the false
  positive rate across experiments needs the same one-time edit as
  `voucher_conditional_on_clean` below.

## Two things that will bite if not planned for

**`voucher_conditional_on_clean` is an `integer, parameter`.** Exactly like
`measure_price_elasticity`, it cannot be set from `run_one_point.sh` and each
variant needs its own build. Either make it a plain integer with a handover case,
mirroring `measure_child_gap` -- one hash change, done once -- or build a binary
per experiment, which changes the hash per experiment. The first is cleaner.

**`solve_transition_dynamics` is hardwired to 0 in BOTH branches** of its
`is_counterfactual` expression at line 1769. That suits long-run equilibria,
which is what was asked for. Anyone wanting a transition must change that line
and read `code/stylized/TRANSITION_LESSONS.md` first -- it is a standing
instruction, not notes.


## Readiness, audited 8 September 15:20

THE MECHANISM IS ALL THERE. The conditionality switch, the detection probability,
the false positive rate and the test cost all exist, and the cost already reaches
the government budget through `govt_spending_on_drug_tests`. Nothing has to be
built from scratch.

WHAT IS NOT READY IS THE BENCHMARK, and that is the binding constraint rather than
any of the code above. At the time of writing b reads -10.9 per cent and
sud_homeless +15.0 and rising until the sign fix works through; lambda_m is
conceded at about -20 with its instrument pinned; and closing sud_homeless needs
roughly 150 iterations that drag b further out as they go. A counterfactual run
off a moving benchmark has to be run again when the benchmark moves, and at about
one solve per firing that is expensive to repeat.

THE ORDER IS THEREFORE: settle the sud_homeless-versus-b trade, freeze the
benchmark, then run Phase 1. The three settability edits can be made at any time
because they are inert while `voucher_conditional_on_clean` is 0.

## READY TO RUN, as of 8 September 16:00

Everything below was checked by running it, not by reading the source.

### The runner

    bash code/run_experiments.sh code/points/point_<frozen benchmark>.txt
    bash code/run_experiments.sh code/points/point_<benchmark>.txt tf_benchmark

Each experiment is a one-line change off a frozen benchmark vector, run through
run_one_point.sh like any calibration point, so it lands as an md5-tagged point
file with the HANDOVER assertion behind it. Names and switch settings are in the
script's own table. It appends to `code/experiment_index.txt`.

    python3 code/compare_experiments.py

reads that index and prints levels and differences from the benchmark. It does
NOT print gaps against targets: a counterfactual has no target, and printing one
would invite reading the benchmark's targets as though they still applied.

### The four handles, all settable from a vector now

    probability_of_voucher_benchmark_used              already was
    increased_prob_of_voucher_if_homeless_and_addicted converted 8 September
    voucher_conditional_on_clean                       converted 8 September
    voucher_conditional_on_clean_just_addicts          converted 8 September
    probability_of_detection                           handover added
    probability_of_false_positive                      handover added
    cost_per_drug_test                                 handover added

All measured inert at their defaults: re-solving the same vector under each
change moved the worst of 36 scored moments by 0.017 per cent of target.

### CONDITIONALITY FIRES, and here is what it does

point_5b89ba333a -> point_bdeb35efe1, voucher_conditional_on_clean 0 -> 1 and
nothing else:

    pi_V          0.26568 -> 0.06788   -74 per cent
    lambda_d      0.03449 -> 0.01290   -59
    b             0.07987 -> 0.03221   -54
    sud_homeless  0.25288 -> 0.18070   -33

Vouchers are revoked on failed tests, take-up collapses, and drug use falls with
it. Thirty-four scored moments move by more than half a per cent of target.

### THE TESTING COST IS NOW OBSERVABLE, and it was not before

govt_spending_on_drug_tests is built at 15522 and taken out of the budget at
15531, and appeared in NO write statement, so the fiscal cost of testing every
eligible could not be read off a run -- the one number Phase 1a exists to
produce. Two DIAG lines now report it as a level and over output, matching
cbar's convention.

### THE ONE THING THE AUTHOR MUST SETTLE BEFORE 1a RUNS

"Treatment First" has two readings here and they are different experiments:

  (a) the SOURCE's naming, at 8850 and 8873: TF is
      increased_prob_of_voucher_if_homeless_and_addicted = 0, vouchers simply not
      steered to the addicted homeless. Nothing is tested and nothing revoked.
  (b) the AUTHOR's phase 1a: "TF with cost of testing all eligibles and false
      positive and false negative", which is voucher_conditional_on_clean = 1.

run_experiments.sh currently applies BOTH for tf_benchmark and universal_tf,
since 1a names the testing explicitly and the source names the steering. If only
one is meant, change the one line in the script's EXP table.

### STILL BLOCKING: the benchmark, not the code

b and sud_homeless contest multiple_find_if_addicted -- closing one opens the
other -- and lambda_m is conceded with its instrument pinned at 60. A
counterfactual run off a moving benchmark has to be run again when it moves.
Settle the trade, freeze the benchmark, then Phase 1.

---

## 9 September: why every counterfactual came out richer than the benchmark

The author, reading the phase 1 arms: *"The economic response for universal tf
makes no sense and is too large in the counterintuitive way"*. They were right,
and the cause is not in the policy.

### The defect

`long_run_counter_factual` overwrites `inheritance_amount` with a hard-coded
constant, one per arm, at 42470-42497:

    inheritance_amount=1.3297417759844228E-002    ! rationed TF
    inheritance_amount=1.39072551538156174E-002   ! universal HF
    inheritance_amount=1.372690695275861320E-002  ! universal TF

`upload_vars` has already read the benchmark's own value at 33497, and on the
current benchmark that value is ZERO at all sixty ages
(`inheritance_amountbaseline_benchmark.dat` is sixty lines of zeros, and the
benchmark log prints sixty zeros). The hard-coded line discards it.

Nothing ever revises it. The update block at 42760 is gated on
`residual_bequests_to_government==0` and that parameter is 1, so
`distance_inheritance_amount` is zero on every loop and the constant stands for
the whole solve. `inheritance_amountcounter_TF.dat` comes back as sixty lines of
`.01329741813242` -- the warm start, untouched.

These read as stale warm starts from a configuration in which the benchmark's
own inheritance was non-zero. They are not warm starts for anything the loop
solves.

### Why it is large

`inheritance_amount` is a live transfer, not a guess:

    bequest = employment_grid(age_index,employment_index)*inheritance_amount(age_index) + ...

paid to every household, at every age, in every period. At 0.0133 against an
average labour income of 0.63725 that is about 2.1 per cent of average income a
year for sixty years -- on the order of a year and a quarter of average labour
income, given to everybody, in every counterfactual and in none of the
benchmark.

### The chain to the reported result

| | benchmark | tf_rationed | universal_hf |
|---|---|---|---|
| `inheritance_amount` | 0 | 0.013297 | 0.013907 |
| `model_bequests` | 0.4923 | 0.8492 (+72.5%) | 0.5034 (+2.2%) |
| `beta` wealth over output | 3.0018 (target 3.0) | 4.265 | 2.676 |
| `tau_l` average labour tax | 0.2241 (target 0.224) | 0.1475 | 0.2208 |
| `increase_in_labour_income_tax` | 0 | +0.0574 (a CUT) | -0.0091 |

`govt_revenues_to_use_in_tests` carries
`(model_bequests - value_of_initial_assets - model_total_inheritance)` at FULL
weight, because `include_bequests=1` and `residual_bequests_to_government=1`
make the coefficient exactly one: unclaimed estates are government revenue.
Bequests moving 0.492 to 0.849 is a windfall of the same order as the entire net
budget of 0.545, and the budget rule returns it as a 7.7 point cut in the
average labour income tax. Higher after-tax income, more drug use.

Two calibration targets move in the counterfactual as a result -- `beta` by 42
per cent and `tau_l` by 7.7 points -- which no voucher revocation can do.

### What this does NOT yet explain

The two arms get nearly the same hard-coded transfer, 0.0133 against 0.0139, yet
universal HF comes out with wealth BELOW the benchmark and its tax essentially
unmoved. So there is a level defect, identified here, and possibly a second
arm-specific one on top of it.

### The null test, which should have been run before any arm

The counterfactual path at the BENCHMARK'S OWN switches
(`voucher_conditional_on_clean=0`,
`increased_prob_of_voucher_if_homeless_and_addicted=1`,
`probability_of_voucher_benchmark_used=0.0433173`) has to reproduce

    net_govt_revenues = 0.545217
    tau_l             = 0.2241
    beta              = 3.0018

and a conditionality-only arm behind it separates the two switches that
`tf_rationed` moves together. Until the null passes, no arm's numbers mean
anything. The cleared-price universal TF run was stopped to give the null the
cores; its partial log is kept as `code/PARTIAL_universal_tf_cleared.log`.

### For the author to settle, because it is accounting and not code

- should the counterfactual inherit the benchmark's `inheritance_amount` (zero,
  so the transfer disappears), or actually solve for it, which needs
  `residual_bequests_to_government` set so the update block runs;
- should the residual bequest fund the counterfactual's tax at all? As it
  stands, any policy that changes saving changes the government's non-tax
  revenue by more than the policy costs.

### Also found, and separate

`experiment_table.py`'s "change in average tax" row reports -3.9pp where the
model's own `tau_l` moment says -7.7pp. The row reconstructs the rate instead of
reading `tau_l`, and it should read `tau_l`.

---

## 9 September, later: the full state after four defects

The author asked for the whole plan in one place. This is it.

### FIXED AND COMMITTED

1. `inheritance_amount` overwrite (04bc57b5). long_run_counter_factual replaced
   the benchmark's zero with a hard-coded ~0.0133 at all sixty ages -- a
   transfer of about 2 per cent of average labour income a year for life, paid
   in every counterfactual and in none of the benchmark. It could never be
   revised, because the update block at 42760 is gated on
   `residual_bequests_to_government==0` and that parameter is 1.

   The author's rule, which the code now implements exactly: no inheritance
   anywhere; a flat endowment paid to newborns only, held at the benchmark's
   average labour income; and the government takes the difference between the
   bequests in each equilibrium and that fixed endowment.

2. Stale income constants (4075635b). `average_labor_income_calibrated` was
   declared 0.637248 against a realised 0.646389, and `median_income_calibrated`
   0.475981 against 0.431324 -- ten per cent out. A counterfactual overwrites
   both in upload_vars; the benchmark never calls upload_vars, so it ran on the
   declarations. The median one was inert (every voucher site selects
   `is_counterfactual*median_income_calibrated`); the income one was not, since
   the wealth and income histogram bin edges read it with no selector. A
   STALE CONSTANT guard beside the benchmark's own write now prints if the
   benchmark drifts more than half a per cent from either.

3. Stale rent and housing price warm starts (4075635b), in the same block:
   `rent_calibrated*1.0051` and `calibrated_stationary_housing_price*1.002`.
   Masked by fix_rent and peg_prices_in_counterfactual, which overwrite both
   inside the loop -- but a constant that is harmless only because something
   downstream overwrites it is one edit from being harmful.

4. The tax search (4075635b, corrected in the follow-up). Two defects. The gain
   was `0.005*gap` against a Newton step of about `1.46*gap`, three hundred
   times too small, so no arm could close the budget inside the eighty loop cap
   and each exited on the loose tolerance mid-walk. And it integrated the cold
   start: the distribution begins far from stationary, loop-one revenue runs 1.4
   to 2.4 against a target of 0.545, and an integrator cannot give that back.
   Across four runs the final tax tracked loop-one revenue and not the policy,
   and a null with NO policy change walked further than either TF arm.

   Replaced with a guarded secant plus a hold. The hold criterion was wrong
   first time -- it compared the drift to the GAP, which is permissive exactly
   when the cold start is worst -- and now compares it to
   stopping_rule_govt_budget: do not move the tax while revenue is still moving
   further per loop than the distance the budget is being asked to close.

### THE ACCEPTANCE TEST, WHICH GATES EVERYTHING

The null -- the counterfactual path at the BENCHMARK'S OWN switches -- must
return

    net_govt_revenues = 0.545217   tau_l = 0.2241   beta = 3.0018
    increase_in_labour_income_tax ~ 0
    b = 0.077700   h_1 = 0.011650   lambda_d = 0.033558

No arm's numbers mean anything until it does. It should have been run before any
arm was, and was not.

### FOUND, NOT FIXED, NEEDS THE AUTHOR

- ENFORCEMENT TIMING. probability_of_false_positive=0.05 is applied every
  period, so a clean household has a 13 per cent chance (0.95^40) of never being
  wrongly removed across a life; probability_of_detection=0.9 per period makes
  detection certain over a decade. These read as per-TEST rates applied per
  PERIOD.
- TF'S SANCTION IS ONE PERIOD, NOT A TERMINATION. Stop using and the voucher
  returns at 0.95. Real programmes terminate with a re-application delay. This
  is the largest single reason the stylized model's TF deters everyone
  (`sudt=0.000`) and the quantitative model's deters almost nobody.
- THE BEQUEST ARITHMETIC THAT DOES NOT BALANCE. A transfer costing about 0.013 a
  period was associated with 0.357 a period of extra estates. Either the
  population mass is being misread or there is a second leak. Needs
  model_total_inheritance printed, which is a diagnostic and not a model change.
- THREE INCONSISTENT CAPS on penalty_child_addicted: 0.4 in the calibrator, 0.6
  in the handover, 0.9 in a warning.
- experiment_table.py reconstructs the average tax rather than reading the
  model's own tau_l moment, which is why it reported -3.9pp where tau_l said
  -7.7pp.

### OPEN ON THE ECONOMICS, NOT BUGS

- Participation elasticity -3.14 against -0.63. The flat hazard is why: with
  addiction_onset_base charged on any use whatever the dose, the only way to
  escape it is to stop, so the extensive margin carries the whole response.
- The author's trap, and it is correct: a pure dose hazard with no base needs a
  large b to deter the first unit, which needs theta up to hold the 14 per cent
  spending share, which cuts the effective housing weight gamma*(1-theta) --
  and since gamma*(1-theta)*[log h_small - log h_1] is the ONLY deterrent to the
  street (consumption_penalty_homeless, extra_job_loss_if_homeless and
  homeless_job_penalty_pp are all zero), size_homelessness would have to fall
  from 2.75e-5 to about 2e-10 at theta=0.7 and 1e-14 at theta=0.8 to hold the
  deterrent constant. Not a calibration. The way out is base PLUS dose, since
  the marginal hazard lambda*exp(-lambda*v) does not involve the base at all;
  that grid has not been run.
- Intensive elasticity -1.37 against -0.55, and nothing in the hazard shape
  moves it.
- Child SUD odds ratio cannot reach 2.0 within any plausible penalty; child
  homelessness ratio needs a penalty under 0.07 against Chetty, Hendren and
  Katz's 0.31.

### WHAT IS VOID

Every counterfactual run before 4075635b. The benchmark is unaffected -- the
overwrites were all in long_run_counter_factual.

---

# THE PLAN, as of 9 September 04:00. Supersedes everything above it.

Everything above this line is a log of what was found. This is the ordered
sequence of what to do, what it depends on, and how each step is known to have
worked. Steps run in order; a step whose CHECK fails stops the sequence.

## Where the work stands

The benchmark of record was not a stationary equilibrium -- it was saved at one
iterate of the calibration sweep, with the outer loop's own
`distance_average_labor_income` at 1.8281e-2 against a rule of 1e-4. Converging
it at frozen parameters moves the headline moments a long way:

| | saved state | converged | target |
|---|---|---|---|
| `b` participation | 0.077700 | 0.086434 | 0.089 |
| `lambda_d` disorder | 0.033558 | 0.036437 | 0.0368 |
| `h_1` homelessness | 0.011650 | 0.013203 | 0.0116 |

Two of three fit far better once solved. Everything measured against the old
state -- every counterfactual, both elasticities, every calibration gap -- was
measured against a point that is not a solution.

## THE SEQUENCE

### 1. Converge the benchmark  [RUNNING]
The save path iterates the equilibrium map at frozen parameters until the
largest move across `b`, `lambda_d`, `h_1` and average labour income is below
1e-6, then writes the state.
**CHECK**: the log carries `FROZEN CONVERGED after N passes`. If it says
`FROZEN DID NOT CONVERGE`, stop and report -- nothing downstream is valid.

### 2. Converge the counterfactuals  [NEXT, blocked on 1 finishing so code/ is free]
`long_run_counter_factual`'s `do while` tests the market distances and never
asks whether its own moments have stopped moving. The drug market can clear
while participation is still drifting -- exactly the trap that caught the tax
criterion twice. Add `distance_frozen_moments` over `b`, `lambda_d`, `h_1` and
average labour income to that loop's test.
**CHECK**: a counterfactual log shows the moment distance falling below 1e-6
before the loop exits, and does not exit on the market distances alone.

### 3. Rewrite the elasticity  [blocked on 2]
The author's design: hold the BENCHMARK distribution, re-solve the value
function at the new price, read the moments off the same distribution. No
re-convergence, no second stationary equilibrium. Same households, one price
change. Drop both `converge_to_stationary_equilibrium` calls from the block.
**CHECK**: the zero-step null returns users unchanged to at least five
significant figures. Before the symmetry fix it moved +8.6661 per cent.

### 4. A new benchmark of record  [blocked on 1]
Re-run `benchmark_of_record.py` and `verify_benchmark_state.py` against the
converged state. Every downstream vector and every reported moment comes from
this.
**CHECK**: `VERDICT: the counterfactual imports this benchmark`, and the moments
in the record match the last `FROZEN PASS` line.

### 5. THE NULL TEST  [blocked on 2 and 4] -- THE GATE
The counterfactual path at the benchmark's own switches:
`voucher_conditional_on_clean=0`,
`increased_prob_of_voucher_if_homeless_and_addicted=1`,
`probability_of_voucher_benchmark_used=0.0433173`.
**CHECK**: reproduces the converged benchmark on `b`, `lambda_d`, `h_1`,
`tau_l`, `beta` and `net_govt_revenues`, with
`increase_in_labour_income_tax` near zero. **No arm is run until this passes.**
This is the author's own test: "run a counterfactual once to see that the
rationed HF gives the exact same economy as the benchmark".

### 6. Re-measure the participation elasticity  [blocked on 3 and 4]
On the converged benchmark, with the new method. The old -3.2074 was measured on
a state that is not a solution, by a procedure that contributed +0.872 of its
own with the wrong sign. Do NOT propose an instrument for it until it has been
measured properly.
**CHECK**: a number, with the zero-step null passing beside it.

### 7. The four arms  [blocked on 5]
benchmark rerun, tf_rationed, universal HF, universal TF, at
`probability_of_detection=0.95` and `probability_of_false_positive=0.005`.
Cleared drug price throughout; held-price versions only as decomposition.
**CHECK**: each converges on its own stopping rules without hitting
`max_counterfactual_loops`, and `tau_l` and `beta` stay near the benchmark's
unless the policy explains why.

### 8. A conditionality-only arm  [blocked on 7]
`tf_rationed` moves two switches at once -- testing on, steering off -- so it
cannot say which did what.

## DECIDED, CLOSED, DO NOT REOPEN

- **No inheritance anywhere.** A flat endowment to newborns only, held at the
  benchmark's average labour income; the government takes the difference between
  bequests in each equilibrium and that endowment. Implemented and verified.
- **Enforcement rates**: `probability_of_detection=0.95`,
  `probability_of_false_positive=0.005`. Per period. Confirmed urine testing is
  two stage and confirmation drives the false positive under one per cent.
- **The dose-dependent onset hazard is DROPPED.** `lambda_addiction=0` stays,
  the base stays. No base-plus-dose grid.
- **The intensive elasticity is accepted at about -1.** It is bounded below -1
  by the Cobb-Douglas nest: with `theta*log(b+v)` inside a Cobb-Douglas
  aggregator the own-price elasticity is exactly `-1 - (1-theta)*b/v`, so the
  -0.55 target is unreachable for ANY `b` and `theta`. The paper needs one
  sentence saying so; ASK before writing it.
- **One child-penalty cap at 0.99**, replacing four numbers that disagreed.

## OPEN, NEEDS THE AUTHOR

- The three-period exclusion state: caught, barred three consecutive periods,
  early reinstatement on completing treatment. Four voucher states rather than
  two, so about 2x on the value function, the policy functions and the
  distributions. Not started.
- Whether the paper states the intensive elasticity as a limitation, and in
  what words.

## STANDING RULES THIS SEQUENCE OBEYS

- Never edit `code/` while a solve is running.
- Both standing builds on every source change: `-fcheck=bounds,pointer` and
  `-finit-real=snan -ffpe-trap=invalid,zero,overflow`.
- Report ONE equilibrium, never a best-of across points.
- A capped or unconverged run is not a result and is reported as a failure.

---

# RESULT: universal Treatment First, 9 September 05:57

THE FIRST NULL-VALIDATED COUNTERFACTUAL OF THE PROJECT. Converged at loop 37 of
a cap of 80, all three conditions inside their rules:

    CF MOMENTS distance  = 3.72e-05   (rule 5e-4)
    distance_drug_market = 1.54e-04   (rule 5e-3)
    distance_govt_budget = 2.48e-02   (rule 2.5e-2)

| | benchmark | universal TF | change |
|---|---|---|---|
| `b` total drug users | 0.085038 | 0.069361 | -18.4% |
| `lambda_d` disorder | 0.036045 | 0.029914 | -17.0% |
| `h_1` homelessness | 0.012537 | 0.009617 | -23.3% |
| drug price | 1.000 | 0.909 | -9.1% |
| `tau_l` average tax | 0.207863 | 0.181988 | -2.6 points |
| `beta` wealth over output | 3.497 | 4.330 | +23.8% |
| newborn CEV | -- | -0.214 | |

Use, disorder and homelessness all fall, and the drug price FALLS with them, so
the reduction is deterrence and not a price choking off demand. Newborn welfare
is nevertheless negative: the policy improves all three quantities and a newborn
behind the veil still does not want it.

FLAGGED, NOT SWEPT UP:

- `beta` moves +23.8 per cent, 3.50 to 4.33. Coherent -- Treatment First strips
  voucher insurance from users, so precautionary saving rises -- but a 24 per
  cent move in aggregate wealth in a calibration target deserves looking at. It
  is inside the (3.0, 4.5) band, only just.
- The budget cleared at 0.02484 against a rule of 0.025. Inside, barely. That is
  the author's loosened tolerance doing its job and the number would tighten if
  the rule did.

WHAT THIS RESULT COST. Seven defects, three of which only became visible after
the ones above them were fixed:

1. the benchmark was not a stationary equilibrium -- saved mid-sweep, its own
   convergence test 183 times out of tolerance;
2. `inheritance_amount` overwritten with a hard-coded transfer in every
   counterfactual and none of the benchmark;
3. the tax search's gain and cap set in per-household units against an aggregate
   budget, 50 times too large a first step;
4. the counterfactual loop free to exit while its own moments were still moving;
5. two stale income constants, one of them the median that sets voucher
   eligibility, 13 per cent out;
6. the null arm running with an empty `file_number`, so its state files had no
   name (mild, ignored, still to fix);
7. and then the over-correction to (3): one cap doing two jobs, throttling the
   secant step that cannot run away as hard as the blind step that can.

THE ONE I DID NOT MAKE. The drug price and the tax are solved in a nested loop,
so every tax step knocks the drug market out and costs six or seven loops to
re-clear -- visible in the log as TAX HELD runs between TAX STEPs. Solving them
jointly would remove that, and it is a solver redesign that would invalidate the
null test. Not to be attempted unsupervised.

---

# RESULT: rationed Treatment First, 9 September 06:45

Converged at loop 38 of 80, comfortably inside every rule:

    CF MOMENTS distance  = 8.62e-05   (rule 5e-4)
    distance_drug_market = 3.53e-03   (rule 5e-3)
    distance_govt_budget = 2.98e-03   (rule 2.5e-2)

## The two Treatment First arms, against the converged benchmark

| | benchmark | rationed TF | universal TF |
|---|---|---|---|
| `b` total drug users | 0.085038 | 0.066063 (-22.3%) | 0.069361 (-18.4%) |
| `lambda_d` disorder | 0.036045 | 0.026188 (-27.3%) | 0.029914 (-17.0%) |
| `h_1` homelessness | 0.012537 | 0.016954 (+35.2%) | 0.009617 (-23.3%) |
| drug price | 1.000 | 0.862 | 0.909 |
| `tau_l` average tax | 0.207863 | 0.191811 | 0.181988 |
| `beta` wealth over output | 3.497 | 3.832 | 4.330 |
| newborn CEV | -- | -0.0998 | -0.2141 |

## What it says

CONDITIONALITY DETERS; UNIVERSALITY CATCHES. Rationed Treatment First cuts use
HARDER than universal -- 22.3 against 18.4 per cent, and disorder 27.3 against
17.0 -- and drives homelessness UP 35 per cent. Universal Treatment First gets a
slightly smaller reduction in use and takes homelessness DOWN 23 per cent.

The reading that fits: losing the voucher costs more when there is no expanded
programme to fall back into, so rationing sharpens the deterrent -- and the same
sharpness is what puts the households it strips onto the street.

THE WELFARE ORDERING IS THE INTERESTING PART AND IT IS NOT YET EXPLAINED.
Rationed TF is the LESS bad arm for a newborn, -0.0998 against -0.2141, despite
cutting use more AND raising homelessness. Both are negative: every arm improves
drug outcomes and a newborn behind the veil rejects all of them. Why universal
is worse behind the veil than an arm that raises homelessness 35 per cent needs
a decomposition -- the candidates are the tax (universal TF cuts tau_l further,
0.182 against 0.192, so it is not obviously the tax), the coverage cost, and the
disorder rate itself. NOT to be asserted without measuring.

Also unexplained and worth measuring: `beta` moves +9.6 per cent under rationed
TF and +23.8 under universal, both away from the 3.0 target and in the same
direction. Precautionary saving against losing voucher insurance is the natural
story and it is a story, not a measurement.

---

# THE COMPLETE 2x2, 9 September 07:30

All four cells converged on their own stopping rules, none capped, all on code
where the null test passes.

| | benchmark | rationed TF | universal TF | universal HF |
|---|---|---|---|---|
| `b` total drug users | 0.085038 | 0.066063 (-22.3%) | 0.069361 (-18.4%) | 0.114119 (+34.2%) |
| `lambda_d` disorder | 0.036045 | 0.026188 (-27.3%) | 0.029914 (-17.0%) | 0.050670 (+40.6%) |
| `h_1` homelessness | 0.012537 | 0.016954 (+35.2%) | 0.009617 (-23.3%) | 0.000188 (-98.5%) |
| drug price | 1.000 | 0.862 | 0.909 | 1.208 |
| `tau_l` average tax | 0.207863 | 0.191811 | 0.181988 | 0.247890 |
| `beta` wealth over output | 3.497 | 3.832 | 4.330 | 2.674 |
| `vouchers_2` outlay | 0.218 | -- | -- | 0.831 |
| newborn CEV | -- | -0.0998 | -0.2141 | +0.3838 |
| loops / cap | -- | 38 / 80 | 37 / 80 | 42 / 80 |

## The reading

CONDITIONALITY SETS THE SIGN ON DRUG USE. Both Treatment First arms cut it;
Housing First raises it 34 per cent and the disorder rate 41.

UNIVERSALITY SETS WHO ENDS UP HOUSED. Housing First all but eliminates
homelessness, universal TF cuts it 23 per cent, and rationed TF RAISES it 35 per
cent because it strips vouchers with no expanded programme to catch anyone.

WELFARE SPLITS FROM THE DRUG OUTCOMES ENTIRELY. Universal HF is the only arm a
newborn wants (+0.384) and it is the arm with the most drug use. Both TF arms
are negative. So the paper's trade-off is not "which policy works" but that the
policy which is best behind the veil is the one that produces the most disorder.

## Why these hang together rather than look like noise

- The drug price moves with demand in every arm: down to 0.86 and 0.91 where use
  falls, up to 1.21 where it rises. Behavioural responses, not a price artefact.
- The tax moves with the programme's cost. Universal HF is the only arm that
  RAISES taxes, and it is the only one paying universal vouchers with no
  revocations: `vouchers_2` 0.831 against the benchmark's 0.218, nearly four
  times the bill. Every TF arm cuts taxes because revocation saves money.
- Universal TF being worse for a newborn than rationed TF, which puzzled me
  earlier, resolves here: it is the more expensive programme without the welfare
  payoff of unconditional coverage -- paying for near-universal vouchers while
  revoking them from exactly the households whose risk it would otherwise
  insure.

## STILL OPEN, AND NOT TO BE NARRATED WITHOUT MEASURING

- `beta` ranges 2.674 to 4.330 across the arms against a 3.0 target. The natural
  story is precautionary saving against voucher insurance -- rising where
  conditionality strips it, falling where universality supplies it, and the
  ordering does fit -- but it is a story until someone decomposes it.
- The calibration vector was fitted against a benchmark that was not a solution.
  Converging it moved `tau_l` and `beta` off target by 7.2 and 16.6 per cent
  while pulling `b` and `lambda_d` much closer. How much to re-fit is the
  author's call.
- The drug price and the tax are solved in a nested loop, so every tax step
  costs six or seven loops of re-clearing. Solving them jointly would remove it
  and would invalidate the null test. Not to be attempted unsupervised.

---

# THE ZERO-STEP ELASTICITY NULL PASSES EXACTLY, 9 September 07:55

    ELASTICITY_DIAG base price= 1.0000  users= 8.5316054836136107E-002
    ELASTICITY_DIAG new price = 1.0000  users= 8.5316054836136107E-002

Bit-identical, every digit. At an unchanged price the number of drug users does
not move. The reported elasticity is NaN because the model divides log(1/1)=0 by
log(1+0)=0, which is what a null that passed perfectly looks like: zero over
zero rather than something over zero.

The history, since it took three attempts:

| | zero-step movement | reported participation elasticity |
|---|---|---|
| original, asymmetric procedure | +8.6661% (wrong sign) | -3.2074 |
| after the symmetry fix, unconverged benchmark | +2.5394% (wrong sign) | -3.7220 |
| author's design on a converged benchmark | **0.0000%** | to be measured |

TWO THINGS HAD TO BE TRUE TOGETHER and neither alone was enough. The author's
design -- hold the benchmark distribution, re-solve the value function at the
new price, read the moments off the same households -- removes the
distributional feedback. The frozen convergence makes the distribution being
held an actual equilibrium. Each earlier attempt had one and not the other.

The base confirms the anchoring: 0.085316 against the converged benchmark's
0.085038, a 0.3 per cent difference, where the PRE-convergence block reads
0.081484.

## A TRAP IN READING THE LOG, and it caught me once

`print_all_moments` is called TWICE in a save run: at 42229, BEFORE the frozen
loop, and again at 42376, AFTER it. The elasticity block lives inside that
subroutine, so a save log carries TWO `ELASTICITY_DIAG` sets. The first is
measured on the unconverged state and is meaningless.

**Always read the SECOND block.** `grep ... | head` gives the wrong one;
`grep ... | tail` gives the right one. I read the first and briefly concluded
the null had failed at +3.56 per cent.

Worth suppressing the first call's elasticity so the wrong number cannot be read
at all. Not done -- it is a source edit and a solve was running.

---

# THE DECOMPOSITION: the drug test is the whole mechanism, 9 September 08:55

`tf_rationed` moves TWO switches -- the sobriety test on, AND the
addicted-homeless steering off -- so it could never say which did what. This arm
turns on only the test, leaving `increased_prob_of_voucher_if_homeless_and_
addicted` at the benchmark's 1. Converged at loop 45, all conditions inside
their rules (moments 6.27e-05, drug 3.90e-04, budget 1.75e-03).

| | benchmark | conditionality only | rationed TF (both) |
|---|---|---|---|
| `b` drug users | 0.085038 | 0.057202 (-32.7%) | 0.066063 (-22.3%) |
| `lambda_d` disorder | 0.036045 | 0.022552 (-37.4%) | 0.026188 (-27.3%) |
| `h_1` homelessness | 0.012537 | 0.016279 (+29.8%) | 0.016954 (+35.2%) |
| drug price | 1.000 | 0.821 | 0.862 |
| `tau_l` | 0.207863 | 0.192176 | 0.191811 |
| newborn CEV | -- | -0.0952 | -0.0998 |

THE SOBRIETY CONDITION IS THE ENTIRE MECHANISM, in both directions. Alone it
cuts use 32.7 per cent and disorder 37.4, and alone it raises homelessness 29.8.
Adding the steering removal WEAKENS the use reduction to 22.3 per cent and adds
only five points of homelessness.

So steering vouchers away from the addicted homeless is a pure cost: it buys no
additional deterrence -- it destroys some -- and adds homelessness. The likely
reason is that it pushes users onto the street, where there is no voucher left
to lose and the test stops binding on exactly the households it targets.

TWO PREDICTIONS MADE BEFORE THIS RAN, BOTH WRONG, recorded because the pattern
matters more than the guesses. I said conditionality would deliver MOST of the
use reduction and the steering removal MOST of the homelessness. It delivers
MORE THAN ALL of the use reduction and nearly all of the homelessness. I also
narrated a mechanism off loop-9 numbers (-82 per cent on use) that unwound to
-32.7 as the drug price fell.

THE STANDING LESSON, now visible in all five arms: the early-loop deterrent is
always far larger than the converged one, because the price has not yet fallen
to absorb the drop in demand. Mid-solve numbers are not results and reading a
mechanism off them produced a wrong story three times tonight.


# THE PLAN, as of 10 September 03:55. Supersedes everything above it.

## THE LIVE STATE, 10 September 03:45. Read this first; the sections below are the design.

Everything above the 8 September queue is superseded. What changed since:

* the child's inherited penalty is a STATE, not a one-off shift at birth. Four
  classes -- neither, a parent with a substance use disorder (SUD), a homeless
  parent, both -- packed into the productivity index, block-diagonal transitions,
  permanent for life including retirement. `child_penalty_classes=4`.
* both child ratios are ODDS ratios now, not ratios of rates, on the author's
  instruction of 10 September. The two underlying rates print beside each.
* the channel-shutdown ladder's three rungs -- `kappa_x`, `child_penalty_off`,
  `adjust_taxes` -- are handover parameters at last. None could be set before.
* `voucher_exclusion_states=1` again: the arms need the third voucher slice and
  the benchmark must carry it, because it dimensions the arrays the arms read.

**The saved four-class benchmark** is `variant_save_20260910T024704Z`,
FROZEN CONVERGED in 2 passes at 3.38e-5. Against the one-class benchmark it
replaces, `lambda_d` went from 2.4 per cent below target to 0.06 per cent below
and `sigma_y` to 0.1 per cent; `b` halved its gap; `h_1` went from +8.0 to
+12.7 per cent and `delta_h` from 3.73 to 4.73, both because 31 per cent is far
too large a homelessness penalty once it lasts a lifetime.

### The queue, in order, ON THE AUTHOR'S SEQUENCING OF 10 SEPTEMBER

*"find out what delta d, delta h and omega c should be in the current
benchmark. Then test what happens in the tf and hf simulations. Then if it's
ready, we hold them fixed and recalibrate the other parameters using the faster
method with no permanent impact on the child and then at the end run the
benchmark with the delta h and delta d and omega c that should give moments
close to the data with the model with full permanence and then run the other
simulations"*.

**STEP 1. FIT THE THREE CHILD PARAMETERS, at four classes.** Four points, each
differing from the anchor in exactly ONE parameter, all on ONE build. A secant
across two points that differ in anything else is not a secant.

| point | moves | to | log |
| --- | --- | --- | --- |
| anchor | -- | 0.24, 0.31, 0.007 | `arm_benchmark.log` |
| B | `penalty_child_addicted` | 0.36 | `fit_delta_d.log` |
| C | `penalty_child_homeless` | 0.15 | `fit_delta_h.log` |
| D | `weight_on_child` | 0.05 | `fit_omega_c.log` |

Targets: SUD odds ratio 2.00, homelessness odds ratio 2.10, `omega` 0.18343.
Then ONE verification run at the interpolated triple. Read the ratios with
`bash /tmp/claude-0/read_probes.sh` or by grepping `UNTARGETED delta_` and
`MOMENT omega` from the last block of each log -- **the LAST block, after
`FROZEN CONVERGED`**. omega prints twice and the pre-frozen print is off a state
that is not an equilibrium; quoting it once already produced a wrong number in
this session, 0.0613 against a true 0.000252.

**STEP 2. THE TF AND HF ARMS** on that fitted benchmark. `/tmp/claude-0/arms.sh`
holds the four commands. The switches, from the model's own `file_number` block:

| arm | offer | homeless-with-SUD eligible | conditional | 3-year bar |
| --- | --- | --- | --- | --- |
| benchmark | 0.0433 | yes | no | -- |
| rationed TF | 0.0433 | no | yes | yes |
| universal TF | 1 | no | yes | yes |
| universal HF | 1 | yes | no | -- |

The question being asked: does Treatment First gain more now that it eliminates
a bigger externality? The old flat-supply table had -2.14, +26.41 and +40.74 per
cent. Note before reading the answer that `omega` is still about 4 per cent of
what the data implies, so a 43-point gap closing would be a result to CHECK.

**STEP 3. THE FAST RECALIBRATION,** at ONE class, with the three child
parameters HELD at their step 1 values. The efficient settings, and why:

* `child_penalty_classes=1` -- 28 min a point becomes about 7;
* `voucher_exclusion_states=0` -- the benchmark has no conditionality and
  nothing to exclude, so the third slice is dead weight HERE. It goes back on
  for the arms, and the two must never disagree within one comparison;
* `measure_child_gap=0` -- it buys a whole extra solve-converge-statistics pass
  to measure `omega`, which is fitted at four classes anyway.

**WHAT IS NOT CUT: the frozen-equilibrium loop.** It looks like the obvious
saving, three extra full solves a point. Today's benchmark reported `b` = 0.0795
before it and 0.0849 after, a 6.4 per cent difference, so a search scored on
pre-frozen moments is steered by that bias -- which is what the banner at the
top of ENGINE.md is the record of.

The three child parameters CANNOT be fitted here and must not be: `delta_d`
pins near 1.11 at any penalty with the classes off, and `omega_c` is clamped at
1.0 while the target needs about 5.1, so it would park at the ceiling and report
a fitted parameter that was never fitted.

**STEP 4.** The benchmark at four classes with the step 1 values, then the arms
again. This is the number that goes in the paper.


# STEPS 1 AND 2 ARE DONE, 10 September 12:20

**STEP 1.** `delta_d` = 0.36 hits the SUD odds ratio at 1.9857 against 2.00.
The other two hit limits that are the author's to rule on, not mine to fit
around, and both are recorded with their evidence in `ODDS_RATIO_FIT.md`:

* `delta_h` floors near 2.5 against a 2.10 target, because homeless parents are
  poor and `rho_intergenerational` transmits that with no penalty at all;
* `omega` cannot reach 0.18343 while `b` is held. Use with the child term off is
  0.088117 and is pinned by `addiction_scalar_1`, so omega = 0.18343 needs the
  BASELINE at 0.0745 against b's own target of 0.0890. `omega_c` and
  `addiction_scalar_1` have to be fitted jointly, which amends the sequencing.

**STEP 2.** All three arms, in `LIFETIME_PENALTY_ARMS.md`. The author's
hypothesis is confirmed and the arms order by how much drug use they cut:

| arm | one class | lifetime penalty | change |
| --- | --- | --- | --- |
| rationed TF | -2.14% | +0.235% | +2.37 pts |
| universal TF | +26.41% | **+30.39%** | **+3.98 pts** |
| universal HF | +40.74% | +40.28% | -0.46 pts |

The Housing First advantage over universal Treatment First fell from 14.33
points to 9.89 -- the externality closed 31 per cent of it -- at a channel
strength about a NINTH of what the data implies.

**A TRAP THAT COST TWO ARMS.** `probability_of_false_positive` is 0.05 in the
benchmark's vector and 0.005 in the arms the one-class table came from. It does
nothing in the benchmark, so lifting the vector from a benchmark log carried the
wrong value in silently. Under the exclusion it bars innocent households for
three years: universal TF read -3.18 per cent instead of +30.39. **Check every
counterfactual-only parameter against the ARM it is being compared with, never
against the benchmark.**

**IN FLIGHT.** `delta_h` = 0.02 with `delta_d` 0.36 and `omega_c` 0.17, to
MEASURE the floor rather than extrapolate it. Three linear extrapolations were
wrong tonight by factors of nine, thirty and a thousand, and one of the author's
two decisions rests on that number.

**STEP 3 IS BLOCKED** on those two decisions. Starting a calibration loop is
also a phase change this file forbids, so it needs the author either way.
