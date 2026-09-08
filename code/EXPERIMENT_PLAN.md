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
- `p_det`, `p_fp` and `c_test` do nothing in the benchmark because
  `voucher_conditional_on_clean` is 0. Per `CLAUDE.md` they belong with the
  experiment and must NOT be added to the calibration table.

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
