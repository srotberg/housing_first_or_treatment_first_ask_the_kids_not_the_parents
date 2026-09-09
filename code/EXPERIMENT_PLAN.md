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
