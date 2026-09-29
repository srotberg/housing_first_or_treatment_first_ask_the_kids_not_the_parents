# 29 September 01:56: CONTAINER RESTART KILLED RESTART 3 IN LOOP 0'S BACKWARD PASS (period 19, 41 of 59 done); RELAUNCHED

- Killed about 01:53. The backward pass keeps no checkpoint, so loop 0 starts again from the same seeds (restart
  3's: price t=1 0.905872, pi_V t=1 0.083132, from relaunch2_loop0_2232) on the same binary (md5 aed5b190, items
  1-9). The killed run's 7 output files are in code/trtf60/restart3_killed_0155; PARAM_HANDOVER.txt restored from
  PARAM_HANDOVER.kept.txt; start-up HANDOVER and seed lines identical to the killed run's. Relaunched 01:56
  (task b90rf06c3). About 3.4 hours lost: at ~5 minutes a period the backward pass ends near 07:00 and loop 0
  near 10:30-12:00; the first children's-homelessness lines (item 8) print in its forward pass from ~07:00.
- Nothing else ran beside it after 01:33 (the Figure 1 scan, stage_results.py 1 --figure-only, finished then).

# 29 September 00:10: THE STYLIZED MODEL, BUILT IN STAGES AND RECALIBRATED AT EACH

- code/stylized/stages.py: stage 1 (no child: xi = 1, omega_c = 0, delta_d = 0) exits at iteration 500 with every
  live row within 1.3 per cent; stage 2 (the child: xi = sqrt 2, omega_c on the 18.3 per cent child use gap,
  delta_d set from Nilsson as in the quantitative model) at iteration 300 within 1.8. theta aims at the Fortran's
  0.16 drug share, not sr_calibrate's 0.14098. u1 held at 0.108. calibrated_sep13.json does NOT reproduce under
  the current code (participation 0.0554, drug share in the corner) and is a record only.
- Results (stage_results.py, stage_transition.py -> stage_numbers.json): stage 1 users earn 3.88x average with no
  consequence, 0.53 with mortality at full strength, unemployment never moves it; at pi_V 0.266 participation is
  8.02 / 2.13 / 8.90 with none / TF / HF; 7.5 per cent worse off under TF, none better. Stage 2: TF beats HF for a
  newborn by 1.336 per cent (0.404 childhood, 0.926 adult); omega_c = 0.0022; child SUD odds ratio 1.17 (reported,
  data 1.44-2.51). Stage 3: kappa_x 0.438 from the 0.2 per cent WTP, TF gain 1.349. Stage 4: at omega_c = 1 nobody
  uses, worth 2.475; transition (null test 4e-14): old -1.13, young -0.075, cohort 1 +1.03, cohort 2 on +1.34.
- Welfare accounting corrected relative to optimal_sud.py: a newborn's life is childhood + beta * adulthood, and the
  childhood aleph is in the CEV's constant; the child bears kappa_x H once per period, as the Fortran does.
- welfare.tab_welfare and transition.caught call cev() without the level and raise at sigma = 2; the stage scripts
  carry the level. Section 3 is rewritten in the four stages; Figures 2 and 3 are gone (Table 3 replaces Figure 2).

# 28 September 22:35: TRANSITION RESTARTED WITH ITEMS 7-9; TWO CODE FINDINGS FROM THE SECTION 4 AUDIT

- Loop 0 of relaunch 2 finished year 59 at 22:31 and was stopped (TaskStop); its files are archived in
  code/trtf60/relaunch2_loop0_2232. The seeds for the restart are its paths (price t=1 0.905872, t=59
  0.867475; pi_V t=1 0.083132, t=59 0.077337, the last from its PI_V line).
- Restart 3 runs code/tr60_fix/hftf_tr_prod (md5 aed5b190...): items 1-8 as before, plus item 9, the child
  value paired with its own period (transition_fix/README.md). Found by an audit of Section 4 against the
  Fortran: the backward pass priced period t's child with V_{t+2}(1). Built with 0 warnings and 0 errors.
- NOT FIXED, FOR THE AUTHOR (it moves the benchmark): an employed, income-eligible voucher holder in a
  shelter is paid the voucher through the secant/objective path, which has no h_1 guard
  (f90 ~29466-29469), while calculate_after_tax_wealth pays it nothing there (29985); and the
  government books the payment for every eligible holder at h_1, employed or not (19014-19018). Size
  unmeasured. It binds only where kappa_r*y_hat < p_r*h_1 = 0.0216, i.e. the bottom productivity node.
- The stylized staged build started (code/stylized/stages.py, stage1.log) on one worker beside the
  transition.

# 28 September 21:20: TWO INCONSISTENCIES IN HOW THE CHILD'S PENALTY IS KEYED -- for the author, not fixed

Found while mapping the Fortran for the Section 4 rewrite (read-only audit, verified by hand):

1. THE PARENT'S OBJECTIVE COUNTS THE FULL PENALTY FOR ANY USE. child_continuation_value (10420-10467) keys on
   transmitted_1 = max(ever_sud_of(unemployment_index_1), future_addiction_index_1) (10449), and at the call sites
   (26358 ff.) future_addiction_index is the DRUG CHOICE being maximised over. So a never-SUD parent that chooses any
   v > 0 counts the whole Delta EV of a penalised child, although onset is a flat addiction_onset_base = 0.0345 with
   lambda_addiction = 0 (12688-12709). The deterrent the child exerts on use is overstated by about 1/0.0345 = 29,
   and weight_on_child = 0.06 was calibrated to the 18.3 per cent moment THROUGH that overstatement.
2. THE LAW OF MOTION KEYS ON THE SUD AT DEATH. newborn_parent_share_acc (15006-15020) uses the parent's CURRENT SUD
   (block 2) in the period it dies; the Bellman keys on the latch (ever had it between 26 and 50) or the use choice,
   with weight one at age 50. The two halves of the same rule disagree.

Both change results if fixed (omega_c recalibrates; the omega_c = 1 optimum and the full-altruism arm move most),
so the model stays frozen until the author decides. The paper's Section 4 will describe the intended rule
(the parent weighs the penalty by the chance it is realised; the child inherits it if the parent carried the
disorder while the child lived at home) and say so in chat.

Other facts the audit established that the paper's Section 4 did not reflect (all now being written in):
onset is flat in quantity; kappa_x H is in welfare only (internalise_homelessness_cost = 0); productivity is an
AR(1) over working life (fixed_productivity = 0); hours are fixed (inelastic_labor_supply = 1); treatment allows
use, keeps the SUD's mortality and does not exempt from Treatment First's test; DI is zero; UI reaches 30 per
cent of separations; mortality multipliers act on the death probability; the homeless multiplier is flat in age;
newborns enter at the parent's death with a one-time transfer; pi_V clears the budget in experiments with the
labour tax held; a third voucher state (excluded, released at a third a year).

# 28 September 20:40: STYLIZED MODEL -- WAITING FOR THE AUTHOR TO REACH SECTION 3

The author, 28 September: the stylized model needs the aggregate homelessness externality "the same way we did
in the full model" (a disamenity in flow utility in proportion to the homelessness rate, kappa_x), "but this
will be done later when i get to that section". Until then the introduction's claims about it are ahead of the
code. Found in the same check, for that round:
- neither model has a homelessness penalty (the author: "we dont have a homelessness penalty"); Sections 3, 4 and
  5 still describe delta_h = 0.31 from Chetty et al. (2016) and have to lose it;
- stylized.py sets omega at 0.09, the full model's old weight, where the introduction says it is calibrated to
  the parents' drug-use gap; optimal_sud.py uses a calibrated 0.00055; the code is not in one state;
- the stylized build is broken and every stylized number in the paper is from 30 August (blanks in the intro);
- the calibration section never states rho_intergenerational = 0.50 or cites Solon, Mazumder and Chetty et al.,
  which the introduction now does;
- Section 7 is still the plan, not the experiments that were run.

# 28 September 20:10: THE PI_V PAIRING FIX IS BUILT; IT GOES IN WHEN LOOP 0 OF RELAUNCH 2 ENDS (about 22:30)

The author, 28 September: "fix the updating rules so that they work better", and chose to let the running loop
finish first. patch_transition_fix.py item 7: the budget residual at t steps pi_V(t-1), the instrument that sets
it; residual(1) is reported and left out of the stopping rule; the last free period takes t-1's value; the secant
is used only when its slope is negative. Item 8, print-only: TRANSITION HOMELESS_BY_AGE, MASS_BY_AGE, SUD_BANDS
and DRUG lines each period, for childhood homelessness along the path (the author asked what happens to it; the
transition never printed homelessness by age). build_tr60_fix.sh now expects a 172-line diff. Test-built in the
scratchpad at nice 19: bounds, snan and prod all 0 warnings, 0 errors; the patch reproduces the built source.
The drug price rule is left alone: it is paired with its own period and moved at most 0.0025 in this loop.

Where loop 0 of relaunch 2 stands (year 29 at 19:50): price moved under 0.005 in 29 of 29 years (median 0.0003);
budget within 1e-3 in 2 of 29 (median 0.0035, worst 0.016 at t = 2) -- the pairing problem, as diagnosed.

At the end of the loop (the PI_V line for t = 59): stop b9e7qq9qd, archive the files newer than START_EPOCH,
restore PARAM_HANDOVER.txt, seed both paths from the checkpoint (pi_V 59 from its PI_V line), install the new
binary, relaunch. The PI_V line's t= is the instrument period from then on.

# 28 September 19:35: RELAUNCH 2, LOOP 0 REACHES YEAR 26 -- cohort born at the reform +2.13%

Forward pass 0 of the run launched 12:58 (seeded from the loop-1 checkpoint) reached year 26. cohort_cev.py on
run.log: the cohort born at the reform gains +2.1266% of consumption (the code's own t = 1 check agrees at +2.3312%
on the cross-section measure). Of its +0.7058 utils over no policy, +0.4960 is childhood and +0.2098 adulthood;
the long-run newborn's +0.4692 splits +0.2364 / +0.2328.

export_results.py would now read this run and move three transition numbers the paper quotes: x_tr_cev_b1
2.8 -> 2.1, x_tr_h_peak_pc 13 -> 14, x_tr_new_t1_pc 51 -> 48. results_numbers.json was restored to the earlier
values, so the paper and the file agree; the move goes into the paper at the author's next round, in red.
The budget is still unconverged (pi_V pairing, entry below), so neither run's numbers are final.

# 28 September 13:10: SECOND CONTAINER RESTART (loop 1, year 19) -- and THE PI_V UPDATE IS PAIRED WITH THE WRONG PERIOD

Killed about 12:56 at loop 1, year 19. Relaunched 12:58 (task b9e7qq9qd, launched through `bash -c 'cd ... && exec'`
because a background command's leading cd is not honoured) from the checkpoint: price and pi_V years 1-19 after
loop 1, years 20-59 after loop 0 (pi_V year 19 from its PI_V line). Files in code/trtf60/relaunch_killed_1256/.
Both seeds read 59 of 59, cwd confirmed.

Loop 1, years 1-19, against loop 0: drug within 0.005 in 10 of 19 (4), median 0.0045 (0.0078). Budget within 0.001
in 1 of 19 (1), median 0.0050 (0.0053) -- the budget is NOT converging, and the log says why:

- pi_V(t) sets the voucher lottery households face IN period t (build_voucher_probabilities at time_index); a draw
  in t makes a holder in t+1, and the budget at t is paid on the holders at t. So residual(t) is set by
  pi_V(1..t-1), not by pi_V(t). Measured, loop 0 -> loop 1: pi_V(2) +0.0018 and receiving at t = 2 FELL (3.0914 ->
  3.0878) while receiving at t = 3 rose (3.1889 -> 3.1958); the cuts to pi_V in years 3-6 lowered receiving in
  years 5-11 by 0.012-0.023 and flipped years 8-11 from deficit to surplus (-0.0023 -> +0.0027 at t = 8).
- the update steps pi_V(t) on residual(t) (pi_v_gap_1 = net_govt_revenues(time_index) - constraint). It is an
  instrument paired with a residual it cannot move:
  * residual(1) = +0.0014 is predetermined by the benchmark's holders: no pi_V reaches it, and it is above the
    1e-3 rule, so the budget rule can never be met at t = 1 as written;
  * residual(2) = +0.015 is set by pi_V(1), which only chases residual(1): it stays at +0.015 while pi_V(2) drifts
    upward by ~0.002 a loop (0.0945 -> 0.0962 -> 0.0980) without effect on it;
  * later years become a lagged integral controller: overshoot and sign flips, as years 8-11 did in one loop.
- FIX (a solver change, not a model change; for the author): step pi_V(t) on residual(t+1), applied when period
  t+1's residual is known in the forward pass, and exempt residual(1) from the rule, reporting it. Not applied:
  it needs the author's word, and the Fortran is not touched while a solve runs.

# 28 September 08:10: T = 60 RELAUNCH, LOOP 0 DONE -- per-cohort CEV b = 1..34; the late years are the unconverged part

Loop 0 of the relaunch ended 08:01; loop 1 runs on the code's own updates (per-period secants now armed).
- CEV of the cohort born in year b (cohort_cev.py): +2.78 (b = 1), +2.15, +2.05, +1.99, +2.01 (b = 5), +1.57 to
  +1.64 (b = 6-11), +1.34 to +1.36 (b = 12-15), +1.25 to +1.30 (b = 16-28), rising to +1.42 by b = 34. Long run
  +1.42. The steps at b = 6 and b = 12 are where each cohort's childhood starts after a fall in the price path.
- cohorts 12-30 sit BELOW the long run: childhood equals it (451.02-451.05 against 451.034), adulthood is lower
  (338.74-338.78 against 338.793). They enter adulthood in years 37-55, the least converged stretch:
  drug price above clearing in years 30-45 (gap -0.013 to -0.021: the SUD stock undershoots the long run, -32.6
  against -30.8 per cent, because early initiation fell, so the price should dip below 0.867 there); budget in
  deficit in years 41-56 (-0.008 to -0.011) with pi_V falling 0.084 -> 0.077 and homelessness rising again from
  +4.3 (t = 40) to +7.4 per cent (t = 59) against +5.6 in the long run -- the T = 60 end.
- gaps, all 59 years: drug within 0.005 in 15, median 0.0095, max 0.021 (t = 38); budget within 0.001 in 14,
  median 0.0045, max 0.016 (t = 4). By decade, drug / budget medians: 1-10 0.006 / 0.006, 11-20 0.006 / 0.005,
  21-30 0.009 / 0.0004, 31-40 0.019 / 0.0005, 41-50 0.013 / 0.011, 51-59 0.003 / 0.008.
- loop 0's steps were small: price -0.06 to -0.23 per cent, pi_V about 0.001. The secant is capped at the
  author's 0.5 per cent a loop, so years 30-45 need 3-5 more loops on their own. Re-seeding them is the option
  put to the author; nothing changed without an answer.

# 28 September 05:15: T = 60 RELAUNCH (checkpoint seeds), YEAR 26 -- new cohort's CEV +2.78 per cent

cohort_cev.py on code/trtf60/run.log (the relaunch, whose seeds are loop 0's updates in years 1-32):
- cohort born at the reform: CEV +2.7815 per cent (killed run +2.8876). Utils against no policy: childhood +0.708
  (+0.750), adulthood +0.213 (+0.207). Code's cross-section CEV t = 1 +2.61, t = 26 +1.34.
- years 1-26, against the killed run's loop 0: drug within 0.005 in 7 of 26 (5), median |gap| 0.0074 (0.0097), max
  0.0137 (0.0207); budget within 0.001 in 3 of 26 (1), median |residual| 0.0045 (0.0064). The budget at t = 2
  (+0.0147) and t = 5 (-0.0137) barely moved: pi_V acts on a stock, and the damped step is small.
- new users -51 (t = 1), -44 (5), -41 (10), -32 (20) per cent; homelessness +12.7 (t = 2), +13.1 (5), +12.8 (10),
  +9.2 (20), +7.3 (25) per cent. Early drug price 0.906-0.908 (years 1-5), 0.895 at 10, 0.878 at 20.
- the waiter for this reading failed silently for five hours: a background command's leading `cd DIR &&` is not
  honoured, so `grep run.log` ran in the wrong directory. USE ABSOLUTE PATHS in background waiters.
- Loop end about 07:05 UTC.

# 28 September 00:40: WHY THE TRANSITION COHORT BEATS THE LONG RUN -- the early drug price, through initiation

The author asked why the reform-year cohort's CEV (+2.89) exceeds the long run's (+1.42). Decomposed on the three
loop-0 runs (scratchpad decomp.py; cohort b = 1 against no policy, utils, discounted to age 1):
- all of the excess is childhood flow utility at ages 1-10, i.e. in periods 1-10: ages 1-5 +0.57 (long run +0.26),
  ages 6-10 +0.15 (+0.02). The homelessness externality term is -0.009 in every run. Adulthood is slightly BELOW
  the long run (+0.207 against +0.233).
- it scales with the early price: at the long-run price throughout (flat run) the childhood gain is +0.18, BELOW
  the long run's +0.24, because the transition has more SUD and more homelessness; at 0.909 (bracket) +0.75; at
  0.922 (Newton) +0.87.
- the channel is initiation: experimenters at t = 1-5 are 1.62-1.66 at price 0.867, 1.16-1.31 at 0.909,
  1.04-1.17 at 0.922. A 5 per cent dearer drug cuts initiation by about 30 per cent, so fewer young parents (a
  child aged a lives with a parent at model age a) spend on the drug, and their children consume more.
- the price is high because the reform inherits the benchmark's SUD stock (1.76, falling to 1.34 by t = 15), which
  keeps demand up against an upward-sloping supply curve. As the stock falls the price falls, initiation returns,
  and each later cohort's gain shrinks toward the long run (+2.89, +2.21, +2.07, +2.02, +2.01, +1.65, +1.58).
- WHY ABOUT TWICE (01:00, for the author): the long run's +0.26 at ages 1-5 is NET of conditionality's costs. Across
  the three runs each 0.1 fewer new users a year in years 1-5 adds about 0.06-0.07 utils, so the long run's 30 per
  cent cut is worth roughly +0.5 gross and exclusions, lost vouchers and homelessness take about half back. The
  transition's further cut (0.4-0.5 fewer a year) comes from the price, not from more exclusions, so it adds its
  ~+0.3 with nothing taken back: 0.26 + 0.31 = 0.57. Inferred, not measured (no child utility by parent state).
  Confound: the bracket run has ~4 per cent more voucher recipients in years 3-8 than the flat run (pi_V 0.0945 at
  t = 2) while its budget is in deficit, so part of the +0.3 may shrink as the budget clears.
- CAVEAT: the size rests on initiation's sensitivity to price near its threshold, the same jump that stops TF 70
  and permban85 clearing (12:55 entry). And the price path is loop 0's.

# 28 September 00:10: CONTAINER RESTART killed the bracket-seeded T = 60 at loop 0, year 32 of the forward pass; relaunched from its checkpoint

Killed about 23:58, six hours in. The code checkpoints both instruments every period (drug_price_path_seed_out.txt,
pi_v_path_seed_out.txt), so the restart keeps what loop 0 computed:
- drug price: periods 1-32 as updated in loop 0 (moves of at most 0.23 per cent on the bracket seed; equal to the
  log's price_of_addictive_good lines to 4e-16), periods 33-59 the bracket seed;
- pi_V: periods 1-31 from the checkpoint (equal to the TRANSITION PI_V lines), period 32 from its PI_V line
  (0.083314; THE CHECKPOINT HOLDS PERIOD t's pi_V BEFORE ITS UPDATE, because it is written ahead of the pi_V
  step in the same period), periods 33-59 the Newton run's post-loop-0 path.
Lost: the per-period secant memory, so years 1-32 take a damped step again on the next update.
The killed run's log and start-up files are in code/trtf60/bracketseed_killed_0000/. PARAM_HANDOVER.txt restored
from the kept copy. Relaunched 00:05 (task bm9nrc673, 4 threads); both seeds read 59 of 59, parent share as before.
Year 26 of this loop about 04:45 UTC, loop end about 06:40.

# 27 September 23:35: BRACKET-SEEDED T = 60, LOOP 0, YEAR 26 -- new cohort's CEV +2.89 per cent

cohort_cev.py on code/trtf60/run.log (task bhp5c6ar6, loop 0, years 1-26):
- cohort born at the reform: lifetime 790.31463, CEV +2.8876 per cent. Between the flat run's +1.00 (price too
  low) and the Newton run's +3.19 (too high), nearer the latter. Against no policy, utils: childhood +0.750
  (flat +0.137, Newton +0.865, long run +0.236), adulthood +0.207 (flat +0.194, Newton +0.189, long run +0.233).
  The code's cross-section CEV: t = 1 +2.62, t = 26 +1.31.
- the childhood gain moves with the early drug price across the three runs: the transition's price sits above the
  long run's 0.867 for about twenty years (0.909 at t = 1, 0.897 at 10, 0.877 at 20), because the SUD stock the
  reform inherits keeps demand high, and a dearer drug cuts parents' use further while their children are young.
- drug market, years 1-26: within 0.005 in 5 of 26, median |gap| 0.0097, max 0.021 (the seeds' 0.04-0.13).
  Budget within 0.001 in 1 of 26, median |residual| 0.0064: -0.016 at t = 5, +0.005 to +0.007 in years 15-26.
- path: b -29 to -31 per cent from year 1, SUD -9 (t = 5), -17 (10), -27 (20), -31 (26); h_1 +13 (t = 5),
  +11 (15), +7 (26), against +5.6 in the long run.
- NOT CONVERGED: loop 0 of perhaps 4-8. Loop 0 ends about 01:40 UTC; loop 1 then runs on the code's own updates.

# 27 September 20:35: WORKER DONE -- TF 85 is unique from a second start; its final table in code/cf_runs/STATUS_remote.md

- uniq85 (TF 85 from pi_V 0.075, price 0.90) converged at 20:26 onto the same equilibrium: price 0.86726, pi_V
  0.081394, b -30.2, h_1 +5.6, CEV +1.415 against +1.416 (results/counterfactuals_cf_fix2/uniq85).
- internalise exited at pass 7 on the damped build, probably on the quiet phase of its period-three cycle: b -2.0,
  h_1 -2.2, no CEV (the author's instruction for this arm).
- Still without an equilibrium: TF 70 and permban85 (the demand jump, 12:55 entry; the author's call on (a)/(b)/(c)).
- No worker runs left. Here: T = 60 bracket-seeded, loop 0 backward pass.

# 27 September 18:00: T = 60 RESTARTED FROM THE BRACKETED PRICE PATH (third seed)

The Newton-seeded run finished loop 0 at 17:55 (log and outputs in code/trtf60/newtonseed_run/); stopped at the
loop boundary and restarted at 17:57 (task bhp5c6ar6, 4 threads). Seeds:
- drug price, per period, the secant between the two runs' loop 0 (flat: price 0.8674, gap positive everywhere;
  Newton: gap negative in every year to 58), code/transition_fix/bracket_seed.py: 0.909 at t = 1, 0.897 at 10,
  0.877 at 20, 0.870 at 30, 0.8674 from about 45. Bracketed in years 1-58; t = 59 is capped extrapolation.
  The secant is per period and ignores that a lower early price raises the later SUD stock, so the later
  years' clearing prices will sit somewhat above it; the 0.5 per cent cap then walks them.
- pi_V: the Newton run's path after loop 0 (0.0824 at t = 1, 0.0945 at t = 2, 0.0792 at 20, 0.0770 at 59).
The log confirms both read (59 of 59), the parent share and the target. The new cohort's CEV from this loop
at year 26, about 22:45 UTC; the two earlier readings, +1.00 (price too low) and +3.19 (too high), bracket it.

# 27 September 15:50: NEW COHORT'S CEV FROM THE PRICE-TOO-HIGH SIDE: +3.19 per cent -- the two runs bracket it

Restarted T = 60, loop 0, year 26 reached 15:46 (cohort_cev.py on code/trtf60/run.log):
- cohort born at the reform: lifetime 790.41212, CEV +3.1858 per cent (flat-seeded run: +1.0018).
  Against no policy, utils: childhood +0.865 (flat run +0.137, long run +0.236), adulthood +0.189
  (flat +0.194, long run +0.233). The code's cross-section CEV: t = 1 +2.87, t = 26 +1.53.
- this run's drug price is ABOVE clearing in every year to 26: gap -0.039 (t = 1), -0.046 (5), -0.058 (10),
  -0.077 (15), -0.097 (20), -0.065 (25). Drug use -31 to -38 per cent (long run -30), SUD -36 by year 25.
  Budget -0.023 to -0.026 in years 5-10 (pi_V seeded high early, fewer exclusions), +0.004 by 26.
- the flat run's price was below clearing everywhere, so the two runs bracket the equilibrium path and the
  cohort's CEV: between +1.0 and +3.2 per cent. Log-linear between the two runs' (price, gap) per year the
  clearing price is about 0.909 at t = 1 but only about 0.877 at t = 20: demand is far more elastic in the
  middle years (log slope about 6.8 at t = 20), because higher early prices also cut the SUD stock later.
- PLAN unchanged: at the end of this loop (~17:30) restart at the boundary with each year's price from the
  bracket (both runs' full paths), pi_V from this run's updated path.

# 27 September 14:10: THE NEWTON PRICE SEED OVERSHOT -- the drug gap flipped from +0.13 to -0.04; the root is now bracketed

Restarted T = 60, loop 0, years 1-3, against the flat-seeded run's loop 0 at the same years:
- price 0.922 (was 0.867): implied supply price 0.883 (was 0.999), gap -0.039 / -0.064 / -0.044 at t = 1-3
  (was +0.132 / +0.137 / +0.137). Drug use -30.8 per cent at t = 1 (was -18.3): demand responds to a 6 per
  cent price rise about 30 per cent more strongly than the 0.5 per cent step measured (log slope 3.0, not
  2.3), as the jump in initiation found in the steady-state arms would do. The clearing price at t = 1 is
  bracketed, 0.867 (gap +0.14) and 0.922 (gap -0.04); log-linear between them it is about 0.909.
- budget +0.0013 / +0.0142 / -0.0061 (pi_V's year-2 secant step now shows in year 3).
- the code's cross-section CEV at t = 1 (cohort entering adulthood) +2.87 per cent (was +1.67).
PLAN: let loop 0 finish (~17:30), then restart at the loop boundary with each period's price from the
bracket (log-linear between the two runs' price and gap), pi_V from this run's updated path. A restart at
the boundary loses only the secant memory; with the 0.5 per cent cap binding it saves two to three loops.
The new cohort's CEV from this loop (~15:40) is at prices about 4 per cent too high early on; with the
flat run's +1.00 at prices 13 per cent too low, the two bracket it.

# 27 September 12:55: WHY THREE ARMS CYCLE -- drug demand JUMPS at a threshold price; no pure clearing price exists

TF 70 (damped), permban85 (damped) and internalise (pi_V fixed, no conditionality) all flip the same way, and
the logs show why. Per pass, against the price the pass was SOLVED at (the passes tables print the price after
the update):
- total_experimenters_1 jumps (TF 70 1.7046 -> 1.7157, permban85 1.651 -> 1.679, internalise 2.326 -> 2.367):
  the flip is in INITIATION, a mass of households switching to trying drugs at once.
- permban85: high whenever p <= 0.85934, low whenever p >= 0.85961. internalise: high at p <= 0.99512, low at
  p >= 0.99557. A clean threshold price in both. TF 70 also moves pi_V each pass, so its threshold moves.
- the signed gap (implied supply price minus p) is NEGATIVE on the low side and strongly POSITIVE on the high
  side in all three: TF 70 -0.0003 to -0.0007 / +0.0030 to +0.0037; permban85 -0.0033 to -0.0039 / +0.0114 to
  +0.0132; internalise -0.0016 to -0.0035 / +0.0152 to +0.0155. Excess demand jumps across zero at the
  threshold, so no price clears the market exactly and the price update walks back and forth across it.
  The damped parent share cannot fix this; it is not a lag.
- every LOW state clears the drug market inside its rule (|gap| <= 0.0039 against 5e-3); the high states
  do not except in TF 70. What fails is the moments-change rule, because the iteration keeps crossing.
- the clearing mixture (the share theta of the jumping mass that must try drugs for the gap to be zero,
  theta = |gap_low| / (|gap_low| + gap_high)) is close to the low state: theta about 0.12 (TF 70), 0.23
  (permban85), 0.17 (internalise). Its numbers: TF 70 b about -28.8 per cent, CEV about +1.46;
  permban85 b about -30.9, CEV about +2.24; internalise b about -1.7, CEV about +0.12.
Options for the author (asked in chat, nothing done): (a) a build copy that stops updating the price once
the gap is inside its rule, so the run settles and exits on the low state, which clears to the paper's
tolerance; (b) report the clearing mixture computed from the two states; (c) smooth the jump in the model,
which is a model change. The difference between (a) and (b) is at most 0.4 per cent of b and 0.02 points
of CEV in these three arms.

# 27 September 11:05: CONTAINER RESTART killed the Newton-seeded T = 60 at loop 0, backward period 4; relaunched

Started 08:16, killed ~11:02 two periods short of its forward pass (2 h 46 min lost). The killed run's log and
the files it wrote at start-up are in code/trtf60/newtonseed_killed_1103/; PARAM_HANDOVER.txt restored from
the kept copy; the same seeds (price 0.922 at t = 1, the flat run's pi_V path). Relaunched 11:04 (task
bar3pulcu, 4 threads); the log confirms both seeds read 59 of 59, the parent share and the target. Next
reading of the new cohort's CEV at loop 0, year 26: about 15:40 UTC. Nothing else was running here.

# 27 September 09:55: TF 70 ALSO FLIPS ON THE DAMPED BUILD -- but its flip sits inside both equilibrium rules

The worker stopped TF 70 damped at pass 12 (results/counterfactuals_cf_fix2/tf70_remote_damp_cycle). b jumps
0.0578 <-> 0.0582 (-28.9 / -28.4 per cent) on passes 7, 10, 12 while the price creeps 0.8730 -> 0.8739 and
pi_V 0.0805 -> 0.0800. What fails is ONLY the moments-change stopping rule (3.7e-4 against 1e-4): at passes
10-12 the drug market is inside its rule on both sides of the flip (3.0-3.5e-3 high, 7.4e-4 low, rule 5e-3)
and the budget too (1.3e-4, 9.6e-4, 4.6e-4, rule 1e-3). The bracket: b -28.4 to -28.9, h_1 +4.9, CEV
+1.43 to +1.47 per cent. Permban85 differs: its high-b state breaks the drug rule (1.1-1.3e-2).
Both look like a discrete jump in drug demand at a price the iteration keeps crossing, not the one-pass
parent-share lag. Whether a state inside both equilibrium rules is reportable when the moments rule cannot
be met is the author's call (the standing rule is one equilibrium, the exit pass, never a best-of);
asked in chat. The worker moved on: uniq85 launched 09:45, omega1 at pass 6.

# 27 September 08:25: T = 60 RESTARTED FROM A NEWTON-SEEDED DRUG PRICE PATH (the flat seed would have cost ~12 loops)

Loop 1 of the flat-seeded run showed the drug price moving by exactly +0.5 per cent in EVERY period
(0.8674 -> 0.8717 -> 0.8761): max_drug_price_move = 0.005, the per-loop cap the author set on 8 September
("You might need to update the price more slowly. Like 0.5% at most"), binds wherever the gap exceeds it.
The early periods need about +6 per cent, so about twelve loops of ~6.5 hours for the price alone.
Loops 0 and 1 measure the demand response: +0.50 per cent on the price moved V by -0.95 per cent and the
implied supply price by -0.65 per cent at t = 1, so d log-gap / d log-price = 2.32 (2.41 by t = 6; the
steady state's is 3.15). A Newton step p0*exp(log(implied/p0)/s), s measured for t <= 6 and ramped to 3.15
by t = 40, gives 0.922 at t = 1, 0.912 at t = 10, 0.892 at t = 20, 0.877 at t = 30, 0.870 at t = 40.
- Stopped the flat-seeded run at loop 1, period 6 (TaskStop; nothing to revert, the tree was clean).
  Its log and every file it wrote are in code/trtf60/flatseed_run/ (run_flatseed_loops0-1.log); the
  restart starts from the staged state exactly as the first start did.
- New seeds: drug price the Newton path (scratchpad drug_price_path_seed.newton.txt, copied in with a
  header saying how it was made); pi_V the flat run's latest written path (its loop 1 through period 6,
  loop 0 after -- note period 2 at 0.0928, a secant step: the per-period budget barely responds to its
  own period's pi_V because holders are a stock, so the per-period secant takes big steps there).
- The cap still governs every update from here; the seed is the only change. Restarted 08:22 as task
  bn41cw4qx, 4 threads; the log confirms both seeds read (59 of 59), the parent share, the target.
- Checked in passing: the path's t = T price prints 0.8647 (the handover's drug_price_start), not the
  terminal equilibrium's 0.8674. price_of_addictive_good_path(transition_length) is only set and printed,
  never used, so it is a mislabel and not a bug.
- Next reading of the new cohort's CEV at this run's loop 0, year 26: about 13:00 UTC.

# 27 September 07:50: PERMBAN 85 HAS NO CLEAN EQUILIBRIUM ON EITHER BUILD -- for the author

The worker stopped permban85's damped rerun at pass 8 (results/counterfactuals_cf_fix2/permban85_damp_cycle).
From pass 6 drug use flips 0.05687 / 0.05590 every pass while the price it was solved at moves only
between about 0.8593 and 0.8596 (the passes table prints the price after each pass's update, so each
row's b was solved at the row above's price): a 0.03 per cent price change flips b by 1.7 per cent. That
is a jump in demand near p = 0.8594, not the one-pass parent-share lag the damped build removes (the
parent share moves 1e-4). The two states bracket the answer: CEV +2.19 to +2.32 per cent, b -30.0 to
-31.2 per cent, h_1 +5.8 to +6.0. Pass 5 nearly met every rule (drug 3.5e-3, budget 7.0e-4, moments
change 1.15e-4 against 1e-4). Not pursued further without the author: a bisection on the price or a
tighter distribution rule are the candidates. omega1 took the slot (07:49); TF 70 at pass 8.

# 27 September 05:50: T = 60 LOOP 0 DONE -- the drug market is far from clearing early on; the 03:31 CEV will move

Loop 0's forward pass finished around 05:45 and loop 1's backward pass started (the waiter bhqqo2vjn
fires at loop 1's forward start, about 09:00; year 26 about two hours after that). Findings:
- DRUG MARKET: largest gap 0.137 (rule 5e-3), 0.13 in years 1-10, 0.028 at year 30, below 1e-3 after
  about year 45. The drug quantity V barely falls at the reform (0.5007 against 0.5015 with no policy)
  because SUD falls slowly, so the clearing price starts near 1.0 and falls to 0.867 over ~45 years; the
  seed held it flat at 0.867. Written up in TRANSITION_LESSONS section 16. The transition's own update
  is price + 0.1 x gap in loop 1 (drug_market_adjuster 0.1 from the handover), then a per-period
  secant bounded at 4x that step: by the code's own estimate of the steady-state gain (2.15) the
  damped step closes about a third of the gap per loop and the secant much more, so perhaps 4-6 loops.
  Not restarted: a restart resets the secant memory and would save at most one loop.
- BUDGET: residual +0.019 at year 2, -0.011 at year 20, +0.005 at year 40, -0.018 at year 59; pi_V
  updated per period (0.0837 at year 2, 0.0792 at year 59). The year-59 deficit is the horizon:
  revenue 14.109 against the terminal 14.130 and still rising (TRANSITION_LESSONS section 16).
- The new cohort's +1.00 per cent (03:31 entry) was computed with drug prices about 13 per cent below
  clearing throughout its childhood. It will move, in a direction that cannot be signed from here.

# 27 September 03:31: T = 60 LOOP 0 REACHED YEAR 26 -- the new cohort's CEV, FIRST ITERATE, +1.00 per cent

The author clarified (after the 22:50 entry) that the number they want is the cohort BORN at the reform,
lifetime including childhood, not the all-alive one; the all-alive worker was dropped and the transition
restarted with a print-only CHILDHOOD / CHILDHOOD_BY_AGE line; code/transition_fix/cohort_cev.py assembles
the cohort's lifetime along its own life (childhood in years 1..25, adult from 26) and reads it off the
benchmark curve. Loop 0, prices and pi_V flat at the TF 85 terminal values, budget not cleared:
- cohort born at the reform: lifetime 789.68860, CEV +1.0018 per cent (the no-policy run itself sits at
  +0.027, so about +0.97 net), against +1.39 net in the long run (results/counterfactuals_cf_fix2/tf85).
- split against the no-policy run, utils: childhood +0.137 (long run +0.236), adult part +0.194 (long run
  +0.233). The shortfall is mostly childhood: SUD falls gradually (-1.6 per cent in year 2, -25 in year 26,
  -31 in the long run) and homelessness overshoots (+12.8 to +14.8 in years 2-6, +7.6 in year 26, +5.6 long
  run).
- the code's own measure (cohort entering adulthood at t): +1.67 at t = 1, +1.07 at t = 26.
- budget residual (revenue minus target): +0.019 in year 2, +0.008 in year 5, then negative from about
  year 10 (-0.011 around year 20). The next loop raises pi_V early and lowers it later, so the direction
  of the cohort's number is not predictable from here. Not reportable until the path clears.
Loop 0's forward pass ends around 06:00; each loop about 6.5 hours; the next reading at loop 1's year 26.

# 26 September 22:50: THE PERIOD-1 CEV THE AUTHOR ASKED FOR IS THE ALL-ALIVE ONE -- instrumented

The author wants the CEV "in period 1 of implementation". The transition's TRANSITION CEV t=1 is the
newborn cohort's (with childhood), read off the benchmark's newborn curve; it is not TRANSITION_LESSONS
6.1's welfare of everyone alive at the reform. The support routine already compared, on the pre-reform
distribution, each state's path value with its benchmark value, but only counted winners. So:
- patch_transition_fix.py gained a print-only TRANSITION ALLALIVE line per period (path and benchmark
  average values, share better off; all ages and six ten-year bands; zero-mass cells skipped so an
  unset value cannot poison the sums). tr60_fix rebuilt (56 diff lines, 0 warnings / 0 errors x3);
  T = 60 stopped at 22:52 after 45 minutes of backward pass and restarted from the same staging with
  the new binary (task bledy824u); the aborted log kept as trtf60/run_aborted_no_allalive.log.
- The conversion needs the benchmark curve averaged over every age: code/transition_fix/
  patch_allage_curve.py (benchmark, print-only: compute_value_of_comparison's own loops widened to all
  ages, ALLAGE CURVE lines). Worker session_019E8MxoQ4iRWJww1ne4rf8Z re-solves the benchmark with it
  (STAGE1_ONLY, BENCH_BIN; cf_arm.sh gained both, default unchanged) and pushes
  results/transition_fix/allage_curve/allage_curve.csv. CEV_all(t) = the x where w(x)-w(0) equals
  V_reform-V_bench from the ALLALIVE line, band by band.
Transition scripts now in code/transition_fix (path-independent).

# 26 September 22:10: CONTAINER RESTART killed TF 70 (damped, pass 7); T = 60 launched here, TF 70 moved to the worker

Everything on disk survived (trtf60 staging, cfarm_tf_fix2_85, seeds, builds). Lost: cfarm_tf_damp70 in
pass 7 (six passes archived in results/counterfactuals_cf_fix2/tf70_damp_partial; flip gone, moments
met, budget -0.0034 and closing slowly), the T = 60 launcher and the monitors.
T = 60 TF 85 launched here at 22:07 with 4 threads (task b4u4vishc): detection 0.85, initial parent
share read, seeds 59 of 59, constraint 6.0370824603. TF 70 damped moved to the worker, ahead of its
queue (trigger trig_01CWGDkRBJyUmJ3kpRuYmUWp, 22:10): cf_fix2_damp, SEED_FROM=bench, pi_V 0.0800, price
0.8733, against the worker's own target 6.0373408771.

# 26 September 20:20: FLAT CONTROL PASSED; T = 60 TF 85 staged, launches when TF 70 exits

results/transition_fix/flat10: T = 10, no reform, both ends the no-policy steady state (cf_fix2_share),
section-16 fixes. One loop, every per-period rule met (budget at most 1.07e-4), welfare within 0.0011
utils of the steady state in all nine periods, 0.00007 at t = 1; the t = 1 parent share restored from
the no-policy run. TRANSITION_LESSONS section 16 updated.
code/trtf60 staged (scratchpad stage_tr_fix.sh): terminal cfarm_tf_fix2_85 (counter_arm), t = 0 the
no-policy distribution and parent share (code/seed_null_share), target 6.0370824602930142, price and
pi_V seeds flat at TF 85's 0.8674 and 0.0814112, handover pi_V set to the same. It must NOT share the
box with a steady-state solve (T60_STOPPED: an OOM when it did), so background task baw1htwyf starts it
with 4 threads once cfarm_tf_damp70 has exited and at least 11 GB are available.
TF 70 damped (cfarm_tf_damp70): the flip is gone (b 0.057645 -> 0.057637, passes 2 -> 3); budget
closing with the halved step.

# 26 September 18:05: TF 70 CYCLED ON THE PARENT SHARE; rerun with a damped update

TF 70 on cf_fix2 alternated between two states from pass 4 (b -28.4 / -28.9%, disordered-housed
parent share 0.01917 / 0.01905, moments change stuck at 3.6e-4 against 1e-4) while pi_V and the
price moved smoothly: the one-pass lag in newborn_parent_share overshoots at 70% detection.
Stopped by TaskStop, log in results/counterfactuals_cf_fix2/tf70_cycle. Build cf_fix2_damp
(scratchpad build_cf_fix2_damp.sh; 11 diff lines against cf_fix2, 7 warnings / 0 errors x3)
damps that update 50/50 once per pass, skipping the clean-housed default; fixed point unchanged.
Running: code/cfarm_tf_damp70, seeded from cfarm_tf_fix2_85, pi_V 0.0801, price 0.8736, target
6.0370824602930142. TF 85 needs no rerun: its share converged without damping.

# 26 September 17:20: TF 85 CONVERGED (results/counterfactuals_cf_fix2/tf85); TF 70 flips on drug use

TF 85, cf_fix2, pass 7, every rule met, TARGET and DIST checks pass: pi_V 0.081411, drug price
0.8674, b -30.2%, SUD -30.8%, h_1 +5.6%, CEV +1.416% (+1.39% net of the no-policy run's +0.027),
split against no policy: childhood +0.237 utils, adult part +0.233. code/cfarm_tf_fix2_85 is KEPT
(the transition's terminal state). code/cf_runs/finalstats.py reads a run's exit pass against the
no-policy run.
TF 70: budget cleared at pass 7 (-0.00043), drug market 3.5e-3, but b alternates -28.4% / -28.9%
between passes (moments change 3.6-3.8e-4 at passes 5, 6, 7 against 1e-4): a knife-edge group moving
with the small pi_V and price steps. Waiting on passes 8-9; CEV +1.45 to +1.50 either way.
Running here: code/cfarm_null_share (build cf_fix2_share: cf_fix2 plus a write of the final
newborn_parent_share, for the transition's t = 0), seeded from seed_null_fix.
Built (0 errors): code/cf_fix2_share, code/tr10_fix (T = 10 flat control; its one warning is in the
dead use_old_transition_results branch, index T-25), code/tr60_fix (0 warnings).
Disk: oc2c0, arm1 and the scratchpad's arm2 gzipped in place (3.9 GB -> 0.27 GB).
Worker session_01CNbZe1BHmxiBzKxWgBVugk: builds clean, STAGE 1 benchmark running; a one-shot routine
(trig_01V4XUEqAGdS1rhEYBPYAZuT, 17:40) tells it to check the benchmark and start arm 2.

# 26 September 14:40: STEADY-STATE ARMS MOVED TO A PARALLEL SESSION; the transition stays here

The author asked for the T = 60 transition in a parallel session. It cannot start anywhere until
TF 85 converges here (its terminal state), and a fresh container has none of the multi-GB
steady-state files, so the transition runs HERE when TF 85/70 finish (T = 60 peaks ~9.8 GiB, alone).
The other steady-state arms went to worker session_01CNbZe1BHmxiBzKxWgBVugk instead, from
code/cf_runs (commit 06e0c56c; its builds regenerate the running arms' cf_fix2 source byte for
byte): it re-solves the benchmark (must reproduce welfare 789.34893176009462, pi_V 0.0675338...),
then permanent ban 85, elasticity 5 at 85, omega_c = 1, TF 85 from pi_V 0.075 (uniqueness) and
internalisation, all against 6.0370824602930142. It writes only results/counterfactuals_cf_fix2/
and code/cf_runs/STATUS_remote.md.
TF runs here after round 3: 85% pi_V 0.08245, gap -0.0086 (overshoot; the budget answers pi_V at
about -27, not -9), gain halved to 0.06; 70% gap -0.0131, gain 0.06. Expected exit round 6-7.
Disk: t45_nogf gzipped in place (4.5 GB -> 0.36 GB; superseded, its terminal arm carried +0.00145).
Transition build copy ready, not compiled: scratchpad patch_transition_fix.py / build_tr45_fix.sh
(section 16 fixes; 29 diff lines). Initial parent share: code/cfarm_bench/newborn_parent_share.dat
(benchmark's own; within 1.3e-4 of the no-policy run's).

# 26 September 12:55: TF 85 and 70 restarted on cf_fix2 (pi_V update ignores pass 1, step 0.12)

On cf_fix both TF runs crawled: pass 1's parent-share artefact inflated revenue (surplus 0.09),
pi_V jumped to about 0.086, pass 2's deficit flipped the sign, the step halved to 0.025 and pi_V
fell about 0.001 a pass against a deficit of 0.034-0.043 (15-20 more passes). Readings then, NOT
results: TF 85 pass 3 pi_V 0.0856, CEV +2.08; TF 70 pass 3 pi_V 0.0850, CEV +2.25, both in deficit
(logs in the scratchpad, cf_tf_fix85/70_slow_stopped). Build cf_fix2 (+ _permban; scratchpad
build_cf_fix2.sh): cf_fix with the pi_V update skipped after pass 1 and its step starting at 0.12
(about 1/slope; the budget answers pi_V at roughly -9), still halved on each sign change. Three
builds each, 7 warnings / 0 errors; 15 diff lines against cf_fix, exactly the intended ones.
Running: code/cfarm_tf_fix2_85 (pi_V 0.082, price 0.8647) and code/cfarm_tf_fix2_70 (pi_V 0.081,
price 0.8702), both against the no-policy target 6.0370824603, seeded from TF 85's distribution.

# 26 September 10:35: THE FIX WORKS -- the no-policy run reproduces the benchmark

code/cfarm_null_fix (build cf_fix: tax warm starts neutralised, moments rule 1e-4): pass 3 net revenue
6.03766 against the benchmark's 6.03888, CEV +0.05 per cent (the old build: 6.1753, -0.26). The hidden
labour-tax rise was the whole gap. TF 85 relaunched on cf_fix (code/cfarm_tf_fix85): target 6.03766
(pass 3; checked against the no-policy run's final value when it ends), seeded from TF 85's converged
distribution, pi_V 0.0818, price 0.8666; its log confirms tax adjustment 0 and detection 0.85.
Freed: code/cfarm_bench_tdm (its file set, final calibration state and distribution are kept in the
scratchpad) and code/cfarm_bench_revdiag.

# 26 September 10:00: FOUND -- a hidden labour-tax rise in every counterfactual (ENGINE.md, same time)

The no-policy gap (revenue +0.148, welfare -0.26%) is the hard-coded tax warm start
increase_in_labour_income_tax = -2.599e-3 (lambda 0.8935 -> 0.8909), which no arm ever solves.
Every counterfactual so far carried it: omega_c = 1, internalisation, every TF run, the 19
September arms. TF measured against its own no-policy run is like-for-like in the tax (+1.39 net
for TF 85 on cf_tdm); levels and anything read against the benchmark directly are off.
Build code/cf_fix (+ _permban): cf_tdm with the three warm starts neutralised (the benchmark's
uploaded 0 stands) and the counterfactual moments rule 5e-4 -> 1e-4. Three builds each, 7
warnings / 0 errors; diff against cf_tdm exactly 4 lines. Running: code/cfarm_null_fix (no policy,
tax 0 confirmed in its log) -- it must reproduce the benchmark: revenue about 6.036-6.039, CEV
about 0. Then TF 85 against its revenue. The 12-block revenue diagnostic was stopped (not needed).
SOURCE FIX PROPOSED, NOT MADE: apply the tax warm start only when the tax is the instrument.

# 26 September 08:15: TF 85 CONVERGED (not firm); the benchmark's 12 blocks are an income fixed point

TF 85 on cf_tdm exited at pass 6 on every rule: pi_V 0.08184, b -29.8%, SUD -30.4%, h +5.6%,
CEV +1.13% (+1.39 net of the no-policy run); results/counterfactuals_cf_local/tf_tdm85. Not firm:
drug use was still rising about half a point a pass at exit (moments 4.3e-4 against 5e-4; the
parent-to-child penalty converges one generation per pass), and the no-policy gap is unexplained.
REVDIAG, benchmark side: warm-started from the re-solve's FINAL state, block 1 still gives net
revenue 10.34 (labour-income tax 12.98, investment 0.94, consumption and property 0). The
benchmark restarts its income normalisers every run: average labour income 1.148 -> 1.384 ->
... -> 1.617 at block 12, median income 0.580 -> 0.863, eligibles holding a voucher 0.072 ->
0.273. Only block 12 is its fixed point, so the diagnostic now runs all 12 blocks
(code/cfarm_bench_revdiag, about 2.5 h). The counterfactual side (code/cfarm_null_revdiag, no
policy seeded from its converged distribution) prints the same components.

# 26 September 07:55: THE BENCHMARK REPRODUCES ITSELF -- the no-policy gap is in the counterfactual binary

Re-solve (results/reference/hf_omega_c_006_tdm): 12 blocks at the counterfactual's numerics end at
net revenue 6.03603 against the old 6.03888, every saved value within 0.05 per cent. So the
no-policy counterfactual's +0.137 of net revenue (all of it in total revenue, spending barely
moves) and -0.26 per cent of welfare come from something the counterfactual binary does
differently. Checked and matching the benchmark: average labour income, net wealth, median
income, drug threshold, rental management costs, c_1 (its 592.94 prints are startup values; the
saved 171.39 is the value that clears the benchmark's housing market). Next: REVDIAG copies of
both binaries print the four revenue components (labour, consumption, investment income,
property) where they are summed; the benchmark side runs two blocks warm-started from the
re-solve's final state (code/cfarm_bench_revdiag), the counterfactual side a no-policy run seeded
from the no-policy distribution. TF 85 (code/cfarm_tf_tdm85, target 6.1753) is near convergence:
pass 5 pi_V 0.08185, b -30.3%, SUD -30.9%, h +5.4%, CEV +1.18% (+1.44% net of the no-policy
run) -- NOT firm until the counterfactual-side gap is explained.

# 26 September 03:50: BENCHMARK RE-SOLVE FIRST (the author: "run the benchmark re-solve first")

Why: a no-policy counterfactual should reproduce the benchmark (CEV about 0). The old converged
no-policy run gave +0.14 per cent and net revenue 6.2646 against the benchmark's saved 6.0389
(+0.226). Almost all of it is total revenue (14.278 against 14.040, +1.7 per cent); spending
barely differs; income +0.44 and consumption +0.14 per cent. The counterfactual's imported
averages match the saved benchmark (average labour income 1.6164, net wealth 3.3461). Leading
suspect: the benchmark itself, solved on the loose 6e-4 rule, with net revenue still falling in
its last four blocks (6.060, 6.049, 6.041, 6.039) and one sweep in the last. The +1.21 per
cent of a no-policy FIRST pass is separate: in pass 1 newborn_parent_share is (1,0,0,0), so no
child inherits a penalty (the first-sweep wave repeats when pass 2 restores the shares).
Build code/bench_tdm (scratchpad build_bench_tdm.sh): the benchmark binary with the calibration
loop's rule 6e-4 -> 5e-5 (47815) and at least 70 sweeps -- the counterfactual build's numerics.
Three builds, 7 warnings / 0 errors, 4 diff lines. Running code/cfarm_bench_tdm (scratchpad
bench_tdm.sh): same seed, same 97-line handover as cfarm_bench's stage 1, 12 frozen blocks,
into save_welfare_curve; it saves a full benchmark file set. TF 85 on cf_tdm was stopped after
pass 1 (log in the scratchpad) since a changed benchmark changes what every arm imports.
Still running: code/cfarm_null_tdm (no policy on cf_tdm, the other half of the comparison).

# 26 September 03:20: 5e-6 IS BELOW THE DISTRIBUTION'S FLOOR -- at least 70 sweeps a pass, then 5e-5

The no-policy run's first pass on cf_tightdist: the transient washes out after one lifetime
(per-sweep change 7.9e-4 at sweep 58, 7e-5 at 61; life_span 60), then the change bounces
between 1e-5 and 4e-4 with spikes in identical pairs and never settles below 5e-6 (156
sweeps, still 4.4e-5). So every pass would run to the 200-sweep cap: about an hour a TF
pass (TF sweeps take about 16 s, the no-policy run's about 7 s). The lag that made pi_V
cycle is removed by sweeping a whole lifetime every pass, not by the tolerance: build copy
code/cf_tdm (and _permban), scratchpad build_cf_tdm.sh = the 1e-3 halving build, seeded,
with the loop's rule 5e-5 and `do while ((distance > rule) .OR. (loop_count_dist < 70))`.
Seeding (the author: "You can also use the old equilibrium distribution"): use_old_distribution
1, read from distribution_stationary{1,2}seed.dat, which the arm script copies from a finished
run's counter_arm files or, with SEED_FROM=bench, from the benchmark's (sizes checked); the
benchmark's own files are not touched. The old runs' distributions were not kept. The arm
script's check now requires every pass at least 70 sweeps, final at or below 5e-5, and
below the cap. Three builds each, 7 warnings / 0 errors; each diff exactly the intended lines.
Running: code/cfarm_null_tightdist (no policy, 5e-6 rule, so 200 sweeps a pass -- the most
tightly solved run, and the source of the budget target) and code/cfarm_tf_tdm85 (seeded
from the benchmark, pi_V 0.0725, price 0.874, target 6.26479886, rule 1e-3; confirmed in
its log). Plan: TF 70 seeded from the no-policy run; the ban and elasticity 5 seeded from
TF 85; TF 85 repeated from the benchmark seed at a different pi_V as the uniqueness check.

# 26 September 03:10: TF RUNS MOVE TO THE 1e-3 HALVING BUILD (author's requests)

The author: "Why can't you clear the budget around 0.0002?", then "Maybe you need to update
piv more slowly closer to the end", then "You can do 0.001 too if it helps". Build copies
code/cf_tightdist_b3h and _b3h_permban (scratchpad build_cf_tightdist_b3h.sh): cf_tightdist
plus budget rule 1e-3 and pi_V's step HALVED whenever the budget gap changes sign (floor
0.05/8, prints "PV STEP: gap= gain="). Gain left at 0.05: the budget's slope in pi_V was
measured at about -8 (pass 1 of the two 70% runs) and about -21 including the distribution's
response, so a larger fixed gain could overshoot. Three builds each, 7 warnings / 0 errors;
diffs against cf_tightdist_b4 and between the pair are exactly the intended lines.
TF 85 on cf_tightdist was stopped in its first pass and relaunched as code/cfarm_tf_b3h85
(pi_V start 0.0725, price 0.874, target 6.26479886 pending the new no-policy run); its log
confirms detection 0.85, pi_V 0.0725, rule 1e-3. The no-policy run continues on cf_tightdist
(no budget clearing, so neither change touches it). Its first pass shows the distribution
converging in waves (a bump from 9.4e-6 to 1.2e-4 at sweep 68; acceleration is off,
accelerate_distribution = 0), most likely the parent-to-child link echoing a generation on.
Every relaunch starts from the best equilibrium guesses available (the author).

# 26 September 02:50: THE DISTRIBUTION SOLVED EACH PASS -- no-policy and TF 85 running

Build copies code/cf_tightdist and code/cf_tightdist_permban (scratchpad
build_cf_tightdist.sh): cf_childdecomp_tight (budget rule 2e-3 plus the diagnostic
children's and adults' split) with the counterfactual loop's distribution rule
6e-4 -> 5e-6 (source line 52877 only; the benchmark loop's 47815 untouched, asserted);
the permban copy also sets voucher_exclusion_release 0 and differs from the other by
that one line. Three builds each, 7 warnings / 0 errors. Arm script scratchpad
tightdist_cf_arm.sh (BUILD, PDET, PV_START, DRUG_PRICE_START, NET_TARGET, SUPPLY_ELAST,
DIAG_TAG); after the run it prints DIST CHECK PASS only if every pass ended at or below
5e-6 without hitting the 200-sweep cap.
Running: code/cfarm_null_tightdist (no policy, pi_V at the benchmark's, price start
1.00014) and code/cfarm_tf_tightdist85 (detection 0.85, target 6.26479886 -- to be
checked against the new no-policy net revenue -- price start 0.874, pi_V start 0.0725,
the middle of the old cycle). Next: TF 70, the permanent ban, elasticity 5 (85 per
cent), omega_c = 1.

# 26 September 02:30: THE TF WELFARE NUMBERS ARE NOT FIRM -- pi_V cycles because the distribution converges across passes

The "firm" 70 and 85 per cent runs (results/counterfactuals_cf_local/tf_tight70, tf_tight85)
stopped at the bottom of a cycle, not at a fixed point. PROOF: tf_childsplit70, same model,
rules and target, warm-started at tf_tight70's exit, stopped at pass 7 near the TOP of the
same cycle: pi_V 0.0758, h +8.2%, CEV +0.70%, against tf_tight70's 0.0688, +10.3%, -0.30%.
Both satisfy every stopping rule. The permanent ban (tf_permban85) stopped on the way down
at +0.15% (peak +1.03% at pass 7). The loose-rule pair of 22:45 (+0.15%, +0.73%) was the
same cycle, NOT the budget tolerance.

CAUSE: in the counterfactual loop stopping_rule_stationary_distribution is 6e-4 when
include_addiction is 1 (source ~52877), a per-sweep change, reached in 1 to 9 sweeps a pass.
The distribution is therefore a lagged state carried from pass to pass; the budget each
pass sees trails the pi_V that produced it, and pi_V overshoots with a period of about 12
passes. Measured in tf_tight70: passes 2 -> 3 moved pi_V 0.0681 -> 0.0685 while the budget
residual moved +0.057. Within one pass the budget answers pi_V with a slope of about -21,
so the static step (gain 0.05) contracts almost at once; the cycle is the distribution.
The source already says this for the benchmark loop (~47794: "the distribution converges
ACROSS blocks rather than within them") and gives its fixed-parameter pass 1e-8; the
counterfactual loop was never given the same.

What survives: in every pass TF cuts b 27-30% and SUD 28-30% and raises h (+7 to +17%).
The sign of welfare does not: 70% ranges -0.3 to +0.7 across the cycle.

PROPOSED FIX (awaiting the author; a kill of the two runs was refused by the permission
system at 01:25 and both have since exited on their own): a build copy with the
counterfactual loop's distribution rule 6e-4 -> 5e-6, a solver tolerance, not a model
change. Passes lengthen (value function ~4.2 min, a sweep ~19 s), passes should fall to a
handful. Order: the no-policy run first (the budget target and the +0.14% offset come
from it), then TF 70, TF 85, permanent ban, elasticity 5; omega_c = 1 on the same build
for comparability.

# 26 September 01:00: SUPPLY ELASTICITY 5 queued (the author: "run the supply elasticity 5 case")

Rationed TF, 85 per cent detection, tight budget rule (cf_tightbudget), target 6.26479886,
drug_supply_elasticity 5 with the supply level refitted (shifter 1.604666 -> 1.148080, price
1.000 at the benchmark quantity; see ENGINE.md). Script: scratchpad tight_elast_cf_arm.sh,
SUPPLY_ELAST=5 PDET=0.85 DIAG_TAG=_elast5_85, price start 0.94, PV_START 0.0702. Starts in
the first free slot (running: cfarm_tf_permban85, cfarm_tf_childdecomp_tight).

# 26 September 00:25: PERMANENT BAN queued (the author: "try the permanent ban")

Build copy code/cf_permban (scratchpad build_cf_permban.sh): voucher_exclusion_release
1/3 -> 0 (used only in the exclusion rows, no division) plus the tight budget rule
2e-3; three builds 7 warnings / 0 errors. Run at 85 per cent detection (the author:
"i think the 85% is more reasonable"), corrected target 6.26479886, warm start from
the tight 85 run, via scratchpad permban_cf_arm.sh with DIAG_TAG _permban85. Starts
when a tight run finishes and its directory is saved and freed.

# 25 September 22:55: FIRM TF NUMBERS -- 70 and 85 per cent detection with the budget closed tightly

The author: "finish both and give me firm numbers for 70% and 85%". Build copy
code/cf_tightbudget (scratchpad build_cf_tightbudget.sh): stopping_rule_govt_budget
2.5e-2 -> 2.0e-3, nothing else; three builds 7 warnings / 0 errors (a first attempt
ran them in parallel in one directory and collided on the module file).
Running (scratchpad tight_cf_arm.sh): code/cfarm_tf_tight70 (warm start price 0.8776,
pi_V 0.0753) and code/cfarm_tf_tight85 (0.8708, 0.0711); logs confirm the rule 2e-3,
the target 6.26479886, detection 0.70 / 0.85, applicant switch 1.
PAUSED (killed by pid, logs in the scratchpad *_paused.log.gz, directories removed):
cfarm_tf_old_saved (pass 5) and cfarm_tf_old_like (pass 0); restart after, ideally
on the tight build too so the comparison uses the same tolerance.

# 25 September 22:45: TWO CONVERGED TF RUNS DISAGREE ON WELFARE -- the budget tolerance is too loose

Same settings (rationed TF, 70% detection, target 6.26479886), different start:
run 1 (from the benchmark pi_V; results/counterfactuals_cf_local/tf): 10 passes, budget
gap at exit 0.021, pi_V 0.0705, voucher spending 0.643, h 0.00662, lifetime 789.4006,
CEV +0.15%. run 2 (warm start at pi_V 0.0715, price 0.881; the childdecomp run,
scratchpad cf_tf_childdecomp.log.gz): 8 passes, gap 0.008, pi_V 0.0753, spending
0.656, h 0.00655, lifetime 789.5976, CEV +0.73%. Both pass every stopping rule;
stopping_rule_govt_budget = 0.025 (declared, no handover case) is about 4% of voucher
spending, and welfare moves ~0.6pp of CEV inside it. NOT a best-of: neither is THE
number until a run closes the budget tightly (build copy with the declared value
changed, e.g. 2e-3). Welfare split, run 2 against the null: childhood +0.091 (users'
children 20.1% -> 14.6%, excluded 0.54%, homeless 0.97 -> 1.03%), adult +0.110 of
which the inherited penalty (penalised newborns 2.93% -> 2.10%) about +0.047.
Running: cfarm_tf_old_saved, cfarm_tf_old_like (19 Sep design, both targets).

# 25 September 22:05: QUEUE (the author: "yes, rerun both after the diagnostic")

1. running: cfarm_null_childdecomp (welfare split, no policy) and cfarm_tf_pdet85.
2. next, in the slot the null frees: TF on the cf_childdecomp build, corrected target
   6.2647988599575077, warm start (price 0.881, PV_START 0.0715).
3. after the diagnostic: the 19 September design (INC=0) on the fixed code, twice,
   via scratchpad design2_cf_arm.sh -- DIAG_TAG _old_like with NET_TARGET
   6.2647988599575077, and _old_saved without it -- price start 0.85.
At most two solves at once (ENGINE.md, memory).

# 25 September 21:55: the inherited channel works under TF; diagnostic extended to adults

The author: TF is "totally misaligned" with the stylized model, whose TF gain runs
through children inheriting better draws. The quantitative model's analogue is the
penalty class (child_penalty_classes 2, fed by newborn_parent_share), and it UPDATES
in the counterfactual: newborns with a disordered parent 2.93% (null) -> 2.18% (TF,
-26%) and 2.07% (omega_c 1, -29%); disordered or homeless 3.09% -> 2.34% (-24%) and
2.23% (-28%). Difference in the experiments: the stylized comparison is UNIVERSAL HF
against universal TF with zero homelessness under both; the quantitative one is
rationed TF with homelessness +9% and vouchers -5%. Diagnostic rebuilt with
ADULTDECOMP (age-one value by penalty class x SUD); cfarm_null_childdecomp restarted
on it (the first start had 2.7 minutes of run time).

# 25 September 21:30: the author bets on a code error behind TF's CEV of about 0

Checked and CLEARED: the child's flow uses goods consumption net of drugs
(consumption_choice = total*(1-frac_spent), asserted at six places). b_shifter is
addiction_scalar_1 (0.0055) for every child regardless of parental SUD (times
b_smi_multiple under SMI), and value_of_life (87.62) enters the child's flow as
(xi-1)*(u+aleph), so children do not die and the constant cancels. Homeless size
0.0216 against the smallest rental 0.0407 (53 per cent); housing share 0.447, sigma 2.
The author: drug spending is about 16 per cent of income for the 10 per cent who use,
so the diversion channel should be worth roughly +0.3 to +0.5 to children under TF,
against a measured -0.01. DIAGNOSTIC: scratchpad build_cf_childdecomp.sh prints
CHILDDECOMP mass/util/cons by household (1 homeless, 2 housed and using, 3 voucher,
4 excluded, 5 other), discounted and age-normalised so util sums to own childhood
before the kappa_x term. Running: cfarm_null_childdecomp (no policy); next, TF on the
same build with the corrected target once cfarm_tf_pdet85 frees memory.

# 25 September 21:10: the 19 September null stopped after pass 1 -- its benchmark's big files are gone

code/null19 ran pass 1 and then died reading value_function1baseline_benchmark.dat:
code/arm1 kept only the small benchmark files and no copy of the large ones exists
on this machine. Pass 1 against its target 6.0213: net revenue 6.0868 (+0.0655),
revenue 14.322, ss 8.648, vouchers_2 0.696, income 63.33; b 0.082059, lambda 0.033087,
h 0.0063302. Today's null at the same stage: 6.0920 against 6.0389 (+0.0531), which
settled at +0.2259. So the 19 September model shows the same gap at pass 1, slightly
larger. Not proven to convergence; finishing it means re-solving the 19 September
benchmark (hours). Log in the scratchpad (cf_null19_pass1.log.gz).

# 25 September 21:00: the 85 per cent detection run is going

The author: "ok, run the 85% detection one"; "i think the 85% is more reasonable";
tests are by surprise, so nobody can abstain ahead of one. code/cfarm_tf_pdet85:
rationed TF, probability_of_detection 0.85, like-for-like target (log: 6.26479885996),
price start 0.87. To make room cfarm_tf_old_like (19 Sep design, corrected budget)
was stopped by pid at pass 1 (its pass-1 log in the scratchpad) and removed; rerun
later if the attribution is still wanted. Running now: null19, cfarm_tf_pdet85.

# 25 September 20:45: memory, and the detection-rate test queued

cfarm_tf_old_saved was killed by the kernel (out of memory: three 4.9 GB solves on
16 GB); removed, not rerun (the TF pair already measures the target's effect).
QUEUED: the author asks whether 15 per cent false negatives would deter more.
Rationed TF with probability_of_detection 0.85, like-for-like target, price 0.87,
via scratchpad design2_cf_arm.sh (PDET), DIAG_TAG _pdet85, as soon as null19 frees
its memory. Running: cfarm_tf_old_like, null19.

# 25 September 20:40: NULL ARM ON THE 19 SEPTEMBER MODEL (did arm 3 have the surplus too?)

The author: "start it now". code/null19: the 19 September counterfactual binary
(code/arm1/hftf, built 19-Sep 13:14, the arms' shared binary) against the 19 September
benchmark files in code/arm1 (saved target 6.021272176537, the value arm 3 cleared
against). Handover rebuilt from arm 3's 101 echoed HANDOVER lines with the policy off:
test 0, exclusion 0, adjust_taxes 0, applicant switch back to 1, price start 1.0,
omega_c 0.055, pi_V 0.068274, adjuster 0.1 (102 lines, all echoed back). If its net
revenue settles well above 6.0213, arm 3's 3.25% carried the same surplus.
The author also asked that pi_V balance the budget: it does (tax_system_type 3 in the
TF logs; the labour tax rate stays at the benchmark's 0.8935).

# 25 September 20:30: the author doubts the TF CEV (about 0, against 3.25% in arm 3)

Welfare split (childhood + beta^25*adult), against the null arm, 1% CEV ~ 0.33 utils:
TF fixed, like-for-like target: childhood -0.01, adult +0.02 (CEV 0.15%, null 0.14%);
TF fixed, SAVED target: childhood +0.89, adult +0.63 (CEV 4.76%); 19 Sep settings on
today's model, unfixed, saved target: childhood +0.78, adult +0.09 (CEV 2.75%).
The CEV code passes the null and the curve is shifted to w(0) = benchmark welfare
(bench log: shift -0.0917 utils). With sigma = 2 the voucher money (to the poorest)
carries most of the welfare. IN FLIGHT, to attribute the old 3%:
- code/cfarm_tf_old_like: INC 0 (the 19 Sep design), fixed code, target 6.26479886
- code/cfarm_tf_old_saved: INC 0, fixed code, saved target 6.03887563
(scratchpad design_cf_arm.sh = remote_cf_arm.sh with DIAG_TAG and INC; price 0.85).
code/cfarm_tf removed for disk; its log, handover and target are in results/.

# 25 September 19:50: RATIONED TF CONVERGED against the like-for-like budget

results/counterfactuals_cf_local/tf/RESULT.md (the saved-target run kept beside it as
RESULT_saved_target.md). TARGET CHECK PASS at 6.26479885996; exit after pass 10.
Against the benchmark (against the null arm): b -27.7% (-27.4%), lambda_d -28.2%
(-27.9%), h_1 +8.9% (+9.5%), SMI -0.3%, SMI share of homeless -6.0%, drug quantity
-17.5%, price 0.88117 (-11.9%), pi_V 0.07154 (+5.9%), eligibles getting a voucher
-5.3% (-4.7%), voucher spending -6.0% (-4.5%). CEV +0.151% against the null's
+0.140%: about zero. Budget gap 0.021 at exit, pi_V still easing down.

# 25 September 18:40: rationed TF RERUN against the like-for-like budget target

The author: "Go ahead with the rerun... You need to rerun the rationed tf with the
correct budget and budget clearing". code/cfarm_tf, remote_cf_arm.sh tf with
NET_TARGET 6.2647988599575077 (the null arm's converged net revenue) and price start
0.86; binary cf/ from a102cfaa. The log confirms net_govt_revenue_constraint
6.2647988599580; cfarm_bench's file still reads 6.038875634967.
- The target file is govt_revenues_to_use_in_tests, not net_govt_revenues:
  clear_only_vouchers_govt_budget is a compile-time 0. The first launch wrote the
  wrong file, cleared against 6.0389 and was stopped by pid at startup.
- Report TF's CEV next to the null arm's own CEV against the saved curve: +0.14%.

# 25 September 18:20: the null arm converged (exit after pass 4, VOUCHER CHECK PASS)

b 0.080903 (-0.4%), lambda_d 0.034513 (-0.3%), h_1 0.0060470 (-0.5%), price 1.00014,
total income 63.236 (+0.44%), revenue 14.2783 (labour 13.5104, investment 0.7679),
ss 8.4384. NET REVENUE 6.2647988599575077 against the saved target 6.038875634967:
+0.2259. That is the proposed arm-local TF budget target. Log in the scratchpad
(cf_null_revsplit.log.gz). Waiting on the author.

# 25 September 18:10: TF's voucher expansion is a BUDGET-TARGET ARTEFACT

The author doubted pi_V +54 per cent ("But not that much"). A NULL ARM settles it:
the counterfactual binary with NO policy change (code/cfarm_null_revsplit: omega_c
0.06, test 0, exclusion 0, adjust_taxes 0, price clearing from 1.0), built with one
extra print, the revenue split (scratchpad build_cf_revsplit.sh; source untouched).
Pass 3 against the saved benchmark:
  b 0.080884 (-0.5%), lambda_d 0.034528 (-0.2%), h_1 0.0060467 (-0.5%)  -- moments reproduce
  total income 63.246 vs 62.956 (+0.46%); revenue 14.2817 vs 14.0405
  (labour 13.514, investment 0.768, consumption 0, property 0); ss 8.4385 vs 8.4078
  NET REVENUE 6.2685 vs the target 6.0389 read from net_govt_revenuesbaseline_benchmark.dat
So the budget rule sees +0.23 of "surplus" with no policy at all -- a third of
voucher spending -- and TF's pi_V clearing hands it to vouchers. Against the null,
TF's net revenue BEFORE vouchers is about 0.065 LOWER (warm-started TF, pass 4:
net 6.0588 with vouchers 0.8182, i.e. 6.877 before vouchers, vs the null's 6.942):
more retirees (ss +0.06), smaller bequest residual (-0.04), revenue +0.036. Budget-
neutral TF would cut voucher spending about 9 per cent, not raise it 20.
Unaffected: omega1 and internalise (adjust_taxes 0). Their moments are measured
against the saved benchmark, which the null reproduces within 0.5 per cent.
Root cause of the +0.46 per cent income gap: NOT FOUND. The warm-started TF
diagnostic was stopped by pid after pass 4 (its log in the scratchpad).
Proposed: rerun TF with the target set, arm-locally, to the null's converged net
revenue (the arm directory's copy of net_govt_revenuesbaseline_benchmark.dat, not
cfarm_bench's). Waiting on the author.

# 25 September 17:15: RATIONED TF CONVERGED on the fixed model

results/counterfactuals_cf_local/tf (RESULT.md, cf.log.gz, the 100-line arm
handover). Exit after pass 9 by the run's own rule. Against the benchmark: b -32.8%,
lambda_d -32.8%, h_1 -6.4%, SMI prevalence -0.4%, SMI share of homeless -12.7%,
drug quantity -20.0%, price 0.86208 (-13.8%), pi_V 0.10381 (+53.7%), eligibles
getting a voucher +20.3%, CEV +4.76%. Caveat: budget gap 1.06e-02 at exit, pi_V
still drifting down. The 24 September TF result is marked superseded.

# 25 September 16:45: the voucher fixes are a NO-OP for the benchmark, within run-to-run noise

cfarm_det_bench ran cfarm_bench's OWN binary (built 01:42) from the same seed
and handover. Block 1:
  b        7.1887043830630423E-002  (reference 7.1894758675946219E-002, -0.011%)
  lambda_d 3.1450566266557796E-002  (reference 3.1458335936491132E-002, -0.025%)
  h_1      7.0776658289252760E-003  (reference 7.0781358129644208E-003, -0.007%)
So a run is NOT bitwise reproducible at 2 OpenMP threads: the same binary moves
b by 1e-4 relative between runs. The fixed build's gap (-0.005%) is inside that,
so a102cfaa is a no-op for the benchmark and cfarm_bench's baseline files stand.
STANDING CONSEQUENCE for no-op checks: compare against a SECOND run of the old
binary, not against its saved log, or the noise reads as a change.
Both check directories stopped by pid; their files are not used.
TF pass 4 at 0.8723: b 0.05600 (-31.1%), lambda 0.02449 (-29.2%), h 0.006024 (-0.9%).

# 25 September 16:35: grandfathering is not needed

The author, on the latent voucher_gf leak: "It is ok with the grandfathering. We
don't need to run it". Leave grandfather_voucher_states at 0 and the gf leak
unfixed; revisit only if the author asks for a grandfathered run.

# 25 September 16:30: no-op check NOT bitwise; determinism test running

cfarm_noop_bench block 1 (fixed build a102cfaa, same seed, same 97-line handover
with exclusion 0, test 0, inc 1) against cfarm_bench block 1 (binary built 01:42,
no source commit in between but this one):
  b        7.1890971726074712E-002  vs 7.1894758675946219E-002  (-0.005%)
  lambda_d 3.1454560537358053E-002  vs 3.1458335936491132E-002  (-0.012%)
  h_1      7.0780456256119388E-003  vs 7.0781358129644208E-003  (-0.001%)
  y        1.1459324862351796       vs 1.145927...
Every changed line is gated on vcc 1 or exclusion 1, so the gap is either run
to run noise (2 OpenMP threads) or -O3 code generation. Test: code/cfarm_det_bench
runs cfarm_bench's OWN binary from the same start; if it reproduces the reference
exactly, runs are deterministic and the gap is the build. noop run stopped by pid
after block 1.
TF (code/cfarm_tf) pass 1 at 0.860: b 0.06551 (-19.4%), lambda 0.02696 (-22.1%),
h 0.006806 (+12.0%); price moved to 0.8643.

# 25 September 16:05: the voucher fixes are in the source (a102cfaa); rationed TF relaunched

The author, 25 September: "Go ahead with the fix, keep the exclusion running".
Three fixes, each gated on the test or the exclusion switch:
- (a) calculate_future_voucher_index_and_opportunity: an excluded household no
  branch catches (above the income gate, or buying) now gets the range
  [0, voucher_excl], so the stay row is summed and the exclusion keeps running.
- (b) same routine, holder branch: with the test on and exclusion off the range
  starts at 0, where the test sends a caught holder.
- (c) calculate_housing_voucher_2: the branch that zeroed every user's and SUD
  holder's voucher under the test is gone; the test acts only through the
  transition, so a holder the test misses is paid.
Three builds 7 warnings / 0 errors each; benchmark -O3 7 / 0. Binaries in cf/
and bench/ are from a102cfaa.

IN FLIGHT (both harness background tasks, 2 threads each):
- code/cfarm_tf: remote_cf_arm.sh tf, DRUG_PRICE_START 0.86 (the leak-fixed,
  payment-unfixed diagnostic was clearing near 0.854 at pass 13: b 0.05315,
  lambda 0.02302, h 0.005870, pi_V 0.0968). Handover checked in the log:
  vcc 1, inc 1, p_det 0.70, p_fp 0, exclusion 1, adjust_taxes 1, omega_c 0.06,
  pi_V 0.067534, adjuster 0.1.
- code/cfarm_noop_bench: NO-OP CHECK. The fixed benchmark binary from scan_seed
  with cfarm_bench's own 97-line handover must reproduce cfarm_bench block 1:
  b 7.1894758675946219E-002, lambda_d 3.1458335936491132E-002,
  h_1 7.0781358129644208E-003. Kill it (by pid) once block 1's BLOCK MOVE line
  prints; its baseline files stay in that directory and are not used.

LATENT, NOT FIXED: with grandfather_voucher_states = 1 (a compile-time 0 today)
voucher_gf has the same leak -- rows (gf,gf)=1 only, but the range is [0,0]
above the gate or buying and [0,2] for has_house = 1. Must be settled before
any grandfathered transition runs; the author said on 20 September a
grandfathered household leaves the state when its income rises past the gate.
Also latent: the holder range's inc==0 case is gated on is_counterfactual while
its row is not, so a BENCHMARK with inc 0 would leak (every benchmark has inc 1).

# 25 September 14:35: the 19 September TF settings on the current model, FINISHED (record only, leak in)

code/cfarm_tf_diagold19 (inc 0, exclusion on, p_det 0.70, unfixed build, so the
excluded-state leak bites every excluded HOLDER) exited 0 after 10 passes.
Against the benchmark (b 0.08126, lambda 0.03461, h 0.006079, price 1.0, pi_V 0.06753):
b 0.04558 (-43.9%), lambda 0.01861 (-46.2%), h 0.006239 (+2.6%), price 0.8239
(-17.6%), pi_V 0.07143 (+5.8%), CEV 2.75%. Drug market cleared: demand 0.3769
against supply 0.5013*0.8239^1.46 = 0.3779; budget distance 0.0175.
Close to the old run's recollected size (price -13, drug use -35, h +5), so the
recalibration is not what moved TF. NOT A RESULT: the leak inflates it by an
unknown amount. Log kept outside the repo (scratchpad cf_tf_diagold19_final.log.gz).

# 25 September 14:20: CONFIRMED -- the excluded-state leak is what made TF -99 per cent

The new design (inc 1, exclusion on, p_det 0.70, unfixed payment) on the
range-fixed build (code/cfarm_tf_rangefix, price start 0.80), against the
benchmark b 0.08126, h 0.006079, V 0.5013 at price 1.0:

| pass | price | b | vs bench | h_1 | vs bench | V (demand) | pi_V next |
|---|---|---|---|---|---|---|---|
| 1 | 0.800 | 0.08200 | +0.9% | 0.007088 | +16.6% | 0.6870 | 0.0748 |
| 2 | 0.804 | 0.07495 | -7.8% | 0.006850 | +12.7% | 0.6237 | 0.0885 |

The same design on the unfixed build: pass 1 b 0.00057 (-99 per cent) at 0.86.
So the leak, not the model, drove the collapse. The fixed run is nowhere near a
cleared market: supply at 0.808 is 0.5013*0.808^1.46 = 0.367 against demand
0.624, so the price walks up at the 0.5 per cent cap and b will fall as it does.
Its equilibrium is not known yet; it is a diagnostic (payment rule still unfixed).

The leak is OLD: the exclusion state and its range date from 9-10 September,
so the 19 and 24 September TF runs had it too, but with inc 0 only holders could
be excluded. The old design on the current model (code/cfarm_tf_diagold19, same
unfixed binary) sits at b 0.0433 (-47 per cent), price 0.831, h +3 per cent, so its
size is also inflated by the leak to an unknown degree.

Proposed (author's call, and only once no solve is running): fix in the source
(a) the excluded-state range, (b) the holder range with exclusion off,
(c) the payment rule so a holder who passes is paid; three builds; rerun TF.
Open design choice for (a): an excluded household above the income gate either
keeps its exclusion clock running (range [0,2], what the diagnostic does) or is
released on leaving eligibility (row 1 to state 0).

# 25 September 13:55: SUSPECTED CAUSE -- a probability leak for the excluded state

calculate_future_voucher_index_and_opportunity (32273-32400) gives an EXCLUDED
household with has_opportunity = 0 (income above 0.5 * median, or buying) the
next-state range [0,0]. But voucher_probabilities writes the exclusion rows for
BOTH opportunity slices: (excl,0) = 1/3 and (excl,excl) = 2/3 (36757-36759, and
the comment there says so deliberately). The 2/3 fall outside the range, so in
the VALUE FUNCTION such a household keeps a third of its continuation value.
Exclusion is then close to catastrophic for anyone whose income might rise.
The simulation loses no mass: every run's sum of the distribution is about 51,
the same as omega1, which has no exclusion. So only decisions are distorted.
- It fits the asymmetry. With inc 0 only holders (about 7 per cent) can be
  excluded; with inc 1 every failing lottery winner can be.
- The exclusion-off diagnostic (b 0.00001) hit a SECOND leak: a holder's range
  is [1,2], so with exclusion OFF a failing holder's 0.7 to state 0 is dropped.
  That leak cannot bite with exclusion on.
- omega1, internalise and the HF benchmark have exclusion off, so they are unaffected.
- Test: code/build_cf_rangefix.sh (ignored build copy) adds, before the routine's
  end, "if has_opportunity==0 and exclusion on and voucher_index==voucher_excl:
  range [0, voucher_excl]". The new design (inc 1, unfixed payment) runs on it in
  code/cfarm_tf_rangefix at price 0.80. Compare with the unfixed new design's
  pass 1 (-99 per cent) and the old design (-40 per cent).

# 25 September 13:40: the TF size traced to the applicant switch, not the model

Pass-1 first answers, all against the same local benchmark (b 0.0813):
- 19 September design (inc 0) on the CURRENT model, unfixed, p 0.83: b 0.0487
  (-40%), lambda_d -43%, h_1 +4%. This reproduces the old arm 3 (-44.6%, h +1.3%)
  and the author's memory, so the recalibration since 21 September is NOT it.
  (Handover diff against PARAM_HANDOVER_arm3_converged.txt: the homeless-state
  parameters are identical; only modest recalibrations moved.)
- New design (inc 1), unfixed, p 0.86: b 0.00057 (-99%).
- New design (inc 1), payment fixed, p 0.85: b 0.00146 (-98%). So the payment
  rule is not what separates the two designs.
- Probe B (inc 1, p_det 0, unfixed, p 1): b 0.0298 (-63%). Payment zeroing alone.
- Code: inc changes only the row for a FAILING NON-HOLDER. With inc 0 it is never
  offered, tested or excluded. With inc 1 it wins with probability pi, then
  30% get the voucher and 70% are excluded. On paper that is MORE generous except
  for the exclusion, so the size is not explained yet.
- The comment at 32366 records an earlier bug in which a voucher carried no
  continuation value: drug use fell 0.0849 to 0.0253. In this model drug use
  leans heavily on the voucher as a safety net.
- Running: code/cfarm_tf_diagnoexcl (inc 1, exclusion OFF, unfixed, p 0.86)
  isolates the applicant exclusion. code/cfarm_tf_diagold19 continues to converge.

# 25 September 13:12: two TF diagnostics running locally (the author: "do both")

- The payment zeroing is NOT new. git blame puts line 18194 at 304e9ed4
  (30 August), so the 19 September arm 3 had it too. It cannot explain why TF is
  larger now than then.
- Probe B (unfixed, p_det 0, price 1, pass 1): b 0.0298, -63 per cent. The
  payment zeroing ALONE removes two thirds of drug use in the current model.
- (1) code/cfarm_tf_payfix: the payment fixed (build copy), the author's TF
  settings (inc 1), price start 0.85.
- (2) code/cfarm_tf_diagold19: the 19 September design (inc 0, p_det 0.70, p_fp 0,
  exclusion, vcc 1) on the CURRENT model with the unfixed binary, price start
  0.83. If still huge, the model changes since 19 September are the cause; if
  near -35 to -45 per cent, the test-and-exclude applicant design (inc 1) is.

# 25 September 13:05: TF PAYMENT BUG, diagnostic run on a build copy

The author's rule: test only holders and those about to get a voucher; a fail
revokes it (holder) or withholds it (new winner), then about 3 years of exclusion;
false negatives 30 per cent; SUD fails the test even without use this period
("those who have sud can't change anything and the test reveals if they have sud").
The transitions (voucher_probabilities, compute_voucher_index_1) match this.
THE PAYMENT DOES NOT: calculate_housing_voucher_2 (18191-18194) zeroes a holder's
voucher every period the holder uses drugs or has SUD, even when the test missed
them. That contradicts equation 32's own comment ("a household that is not
caught gets the whole voucher") and the author's 30 per cent false negatives.
- code/build_cf_payfix.sh (ignored) builds the cf binary with line 18194's
  condition set to ==-1 (asserted by content) into code/cf_payfix. The tracked
  source is NOT edited, because solves were running.
- TF on that binary: code/cfarm_tf_payfix, drug_price_start 0.85 (the earlier
  TF price was about -13 to -17 per cent).
- The unfixed TF (price about 0.38, b -85 per cent) was stopped. Its logs are in
  the scratchpad only.
- Probe B (unfixed, p_det 0, price 1) in code/cfarm_tf_diagB isolates the zeroing
  channel.
If the fix brings TF back near the 19 September size, fix the source (with all
three builds) once no solve is running, with the author's OK.

# 25 September 13:00: the author accepts omega1 and internalisation; tf payment rule queried

The author: *"Omegac=1 and internalizarion seem correct to me. Similar to before"*
(results/counterfactuals_cf_local/{omega1,internalise}).

On tf the author doubts b -85 per cent. The fall is policy-driven: at p = 0.86 it
was -99 per cent, and the price then fell to about 0.38 to clear the market.
Found and put to the author, awaiting a decision:
calculate_housing_voucher_2 (18191) zeroes a holder's PAYMENT every period the
holder uses drugs or has SUD, deterministically. p_det = 0.70 governs only
revocation and exclusion, so the 30 per cent false negatives never reach the
payment. Options offered: (a) decompose who stops using, (b) pay a using holder
with probability 1 - p_det, (c) keep the rule and write it up with the caveat.
Local tf runs continue meanwhile (cfarm_tf from 0.35, cfarm_tf_probe from 0.42,
both near 0.375). v3 archived: its tf is redundant with the local runs.

# 25 September 10:35: tf settled demand is price-inelastic; main run restarted at 0.35

Settled (post-transient) demand, with the budget cleared (pi_V about 0.10):
0.0600 at p = 0.4448 and 0.0626 at 0.4359 (0.47-start run); 0.0733 at 0.4196 and
0.0743 at 0.4175 (0.42-start run); b about 0.008 to 0.009. The implied elasticity
is 2 to 4, so against supply 0.5014*p^1.46 it clears at p = 0.354 to 0.372. First
passes overstate demand, so the price climbs a few per cent before it settles. The
main run now starts at 0.35 (code/cfarm_tf); the 0.42-start run (code/cfarm_tf_probe,
now at 0.415) walks down from above as the check.

# 25 September 07:55: tf clearing price bracketed by probes, local runs at 0.47 and 0.52

These are pass-1 demands from the local benchmark at adjuster 0.1, with the voucher
probability carried:
- p = 0.86: V = 0.0018, b = 0.00057, lambda_d = 0.00019 (supply about 0.40);
  passes 2 to 4 kept b under 0.0006.
- p = 0.40: V = 0.917, b = 0.0487 (supply 0.13).
The log-linear demand has elasticity 8.1 and clears near p = 0.49. First-pass demand
overstated the settled demand in omega1, so the main run starts at 0.47
(code/cfarm_tf) and a probe at 0.52 (code/cfarm_tf_probe, via the ignored copy
code/probe_cf_arm.sh). A run started at 0.6 (v3) or 0.86 walks 20 to 60 passes at
the 0.5 per cent cap, which is why v3 has taken over 6 hours.

# 25 September 06:55: internalise and omega1 DONE (adjuster 0.1, one local benchmark); tf pending

- results/counterfactuals_cf_local/internalise: lambda_d -2.14%, h_1 -2.47% (firm);
  b -1.64% final, -1.94% averaged over the last five passes (range -2.4 to -1.6);
  price 0.9966.
- results/counterfactuals_cf_local/omega1: b -35.0%, lambda_d -33.0%, h_1 -12.3%,
  price 0.870. b steps each time the price rises 1.5 to 2 per cent; the price
  stopped with the gap inside its rule.
- tf: v3 (session_012k9WecRrXzogSi5ZtEuDRN) has been running since about 01:25.
  When it pushes results/counterfactuals_cf_v3/tf, ARCHIVE v3 (its queued omega1
  duplicates the local one).

# 25 September 04:50: omega1 restarted at drug_price_start 0.81

The omega1 arm started at 0.6. Pass 1 printed demand V = 1.91 (b = 0.157)
against supply 0.5014*0.6^1.46 = 0.238, so the price rose at the 0.5 per cent
cap, which is about 60 passes (10 hours) to anywhere near 0.8. The fixed-price
omega1 run had b = 0.0202 at p = 1, so demand there is about 0.12. The log-linear
demand through the two points has elasticity 5.4. Against supply elasticity 1.46
it clears at p^6.88 = 0.12/0.5014, so p = 0.81. Killed (pid 3063) and relaunched
with DRUG_PRICE_START=0.81 (task b14c0bziq). The same arithmetic puts TF near
0.79 (fixed-price b = 0.0154), about 54 passes from its 0.6 start.

# IN FLIGHT, 25 September 04:25: both remaining local arms from ONE local benchmark

- Local benchmark (code/cfarm_bench) done 04:15: b = 0.081255009769345327,
  -6.9e-5 against the reference; voucher probability 0.067533863251354.
  bench_files.tar.gz is 131 MB, over GitHub's 100 MB limit, which is why v2
  never pushed it. Deleted; the set lives in code/cfarm_bench only.
- Local internalise at adjuster 0.1 (task b3hj81odq), stage 2 since 04:15.
- Local omega1 at adjuster 0.1 (task b08fa7bn8), from the same benchmark, since
  04:24. Deleted code/trans_bench_to_tf (4.5 GB, the 21 September arm 3
  transition on the superseded model, results in results/transition/) to make
  disk room: one arm directory is 2.5 GB.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): tf at 0.1 since about 01:25. Archive
  it once tf is pushed; its omega1 duplicates the local one.

# IN FLIGHT, 25 September 01:35

- internalise v2 (results/counterfactuals_cf_v2/internalise/): the voucher
  check PASSED and stage-1 b is -1.8e-5 against the reference. At adjuster 0.2
  b sawtooths +/-0.65 per cent with the price (0.9949 to 0.9967), so its b
  change of -1.67 per cent is +/-0.6 pp. lambda_d -2.19 per cent and h_1 -2.50
  per cent are steady. bench_files.tar.gz was NOT pushed. v2 archived.
- THIS container: `remote_cf_arm.sh internalise` at adjuster 0.1. The 01:32
  launch used nohup and DIED when the turn ended (the container is suspended
  between firings); relaunched 01:43 as a harness background task (Bash
  run_in_background), which survives. Stage 1 started 01:43 in code/cfarm_bench (out: code/cfarm_internalise.out). The
  container restarted once (01:21), so check `uptime -s` each firing and
  relaunch the same line if it is newer than the launch. Push
  cfarm_bench/bench_files.tar.gz when stage 1 finishes.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): stage 1 passed; tf at 0.1 running
  since about 01:25, omega1 after it.

# PLAN, 24 September 22:25: ONE benchmark (v2's), every remaining arm run from it

The author: *"Wouldn't it be more efficient to run it once in this session and
use it for the other sessions??"* Yes. v2's benchmark finishes first. Its worker
pushes results/counterfactuals_cf_v2/bench/{bench_files.tar.gz,bench.log.gz}.
When those land, run tf and omega1 from them in THIS container:
`cd code && BENCH_FROM=../results/counterfactuals_cf_v2/bench sh remote_cf_arm.sh <arm>`
(4 cores, 16 GB; two arms at OMP 2 each; check the first arm's RSS before
starting the second). Then archive v3 (session_012k9WecRrXzogSi5ZtEuDRN), whose
own benchmark is a hedge only in case v2's tarball is over 40 MB and not pushed.

# IN FLIGHT, 24 September 22:10: v3 for tf and omega1; v2 is kept for internalise only

- session_012k9WecRrXzogSi5ZtEuDRN (v3) runs the benchmark, then tf, then omega1,
  at drug_market_adjuster 0.1, to results/counterfactuals_cf_v3/<arm>/.
- session_011HE2FoD9oEfGDmCFwFg9gx (v2) runs at the declared adjuster 0.2.
  Its internalise arm is fine, because the price barely moves there (0.991).
  ARCHIVE v2 AS SOON AS results/counterfactuals_cf_v2/internalise/ IS PUSHED,
  before its omega1 and tf run at 0.2.
- The first tf run (session_01LxhTRbB5QNDAeLqvVag69e) runs at 0.2 and started
  its price at 0.6. When it pushes, read its price path. It gives the tf
  clearing price and shows whether the run cycled; do not report its numbers
  unless the movement decayed into the stop.

# IN FLIGHT, 24 September 20:40: counterfactuals v2, one benchmark and three arms

- session_011HE2FoD9oEfGDmCFwFg9gx runs remote_cf_arm.sh: the HF omega_c = 0.06
  benchmark once (cfarm_bench), then internalise, omega1 and tf, each carrying
  the benchmark's voucher probability 0.067533863251354. Results go to
  results/counterfactuals_cf_v2/<arm>/. Expected: internalise about 01:00 UTC,
  the other two a few hours after.
- The first internalise arm (results/counterfactuals_cf/internalise/) ran at the
  declared 0.06 and is superseded. The first omega1 arm had the same fault and
  was archived before it finished.
- The first tf arm (session_01LxhTRbB5QNDAeLqvVag69e) is still running. pi_V is
  its budget instrument, so the start value washes out at convergence. Check its
  stage-1 b: its benchmark stage ended after about 50 minutes, where the others
  took 2.5 to 4 hours.

# THE REDO RUNS THE WAY THE OLD ARMS DID, 24 September 16:55

The author: *"the budget clearing in rationed TF is done with pi_v and in the
omega_c=1 case and internlization case for homelessness there is no budget
clear"*, and chose the old counterfactual build over patching the frozen one.

The market-clearing pilot on the frozen build was archived: that setup zeroes
voucher_probability_adjuster, so pi_V could not clear the budget.

`code/remote_cf_arm.sh tf|omega1|internalise`, one container per arm:

    STAGE 1  Housing First omega_c = 0.06 benchmark on the TRACKED source,
             12 blocks into save_welfare_curve, in the arm's own directory.
             Its full saved files were lost with the reference container, and
             the counterfactual binary reads them.
    STAGE 2  the arm on build_cf.sh's binary (is_counterfactual=1,
             use_revenues_to_increase_voucher_probability=1), in the same
             directory.

Checked in the source before writing it:
- the drug price clears in clear_drug_market's counterfactual branch against the
  benchmark's own shifter, drug_supply_shifterbaseline_benchmark.dat;
- adjust_taxes 1 plus use_revenues=1 sets tax_system_type 3 (53091), so pi_V
  moves with gain 0.05 and the tax does not. adjust_taxes 0 gives no budget
  clearing. That is tf, and omega1/internalise, respectively;
- upload_vars imports the median income, the labour income profile, the net
  revenue constraint and the rest from the benchmark's saved files. So the
  STALE CONSTANT declarations are overwritten before use, and no Fortran edit
  is needed; I told the author otherwise and corrected it;
- inc = 1 (applicants tested) takes the file-name branch 'counter_arm', and
  old_results is still 'baseline_benchmark', so every arm reads the right files.

A relaunch skips stage 1 when BENCH_DONE and the benchmark files are on disk.

