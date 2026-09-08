# The plan after convergence

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
