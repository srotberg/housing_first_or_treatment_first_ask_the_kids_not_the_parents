# RULE C: THE PLAN TO FINISH THE PAPER (12 October)

The author: "I think we should redo the whole paper with rule C", "all the stuff we are waiting on should be done on rule
C. and all the stuff already in the paper should be redone for rule C including any validation we rely on", "go ahead,
write out the plan, and execute to finish the paper fully finally", "use parallel sessions where you can".

Rule C: a household with the disorder must be in treatment, and no household may use (EO 14321 Sec. 5(b); the
ONDCP/HHS/HUD 2026 toolkit, p. 9). code/treat/patch_treatC.py. Housing First, the no-policy arms and the benchmarks have
no screen and are NOT re-run. The stylized model (Section 3) has no treatment choice and is NOT re-run.

## Workstreams (parallel)

| id | what | where | depends on | status |
|---|---|---|---|---|
| C1 | main Treatment First arm, detection 0.85, $35 test, price and pi_V clearing | cloud session_01RuzfgApLN9fv3B7J6B8kpS, code/treat/remote_treatC.sh -> results/counterfactuals_2c/tf_ruleC | - | building 17:01; INERT CHECK at pass 1 |
| INV | inventory of every Treatment First-dependent number in the paper (validation included) and the run behind it | local agent -> scratchpad ruleC_inventory.md, then into this file | - | running |
| BOTH | both penalties (delta_d 0.24, delta_h 0.31), long run, rule C, single precision + checkpoints; the disk (29 GB) cannot hold the four-class benchmark's text files plus an arm's, so the engineering is part of the job | cloud session_01V66tfNJk92jP5jndoK5C3F (Opus, launched 17:09): engineering, then code/deltah/remote_deltah_both_C.sh -> results/deltah_both_C | - | engineering |
| ARMS | every other rule-C arm the inventory lists (decomposition columns, no-externality columns, detection 0.70 and 0.50, omega_c 0.686, delta_d = 0 with its benchmark re-solved, the Milby split, who-stops and revocation prints), one cloud session each | cloud sessions | C1 passes the inert check; warm start from C1's latest pass | after INV |
| C1-INERT | C1 pass 1: welfare 789.9738 against rule A's 789.9399 at the same start; voucher holders with a SUD 0.0183, of them 0.0137 in treatment (75%) | - | - | PASSED 18:03 |
| S-tf | the main arm re-solved beside Housing First: final, shares, newborn shares (who gains, Table 5's better-off rows) | session_011MbNMbytyRE8eUCaNB6tY3, code/extra_2c/remote_decomp_shares_C.sh tf -> results/decomp_2c_shares_C/arm_tf | C1 warm start | launched 18:21 |
| S-fixboth | Table 5: price and pi_V both held | session_01TNAGv2iochuLa8URX3U78w, remote_decomp_shares_C.sh fixboth -> results/decomp_2c_shares_C/arm_fixboth | - | launched 18:21 |
| S-fixpv | Table 5: pi_V held, price clears | session_01PpnqC2wyZrmsMJNMvbr89D, remote_decomp_shares_C.sh fixpv | - | launched 18:21 |
| S-fixp | Table 5: price held (= perfectly elastic supply), pi_V clears | session_01Rc5f71NPBc4XASW7thMJEn, remote_decomp_shares_C.sh fixp | - | launched 18:21 |
| P70 | detection 0.70 | session_01RNvwXhPVxvvJEHnwJ8jJfB (relaunched 19:01 with a rule-A warm start: price 0.8642, pi_V 0.0932, interpolated between rule A's 0.85 and 0.50 arms; first session 01XQrGMF archived), P0_START=0.8642 V0_START=0.0932 code/pdet/remote_pdet_C2.sh 0.70 -> results/counterfactuals_2c/tf_pdet70_C | - | running |
| P50 | detection 0.50 | session_01L9WL4M6h5tbSFAUek8SZsZ (relaunched 19:01 at rule A's pdet50 values, price 0.8757, pi_V 0.08929; first session 01U7N2fZ archived), P0_START=0.8757 V0_START=0.08929 code/pdet/remote_pdet_C2.sh 0.50 -> results/counterfactuals_2c/tf_pdet50_C | - | running |
| DD0 | delta_d = delta_h = 0, one class: benchmark re-solved, Housing First, Treatment First on rule C, then fixboth and fixp (fixp = perfectly elastic supply, the author's point on the small gain) | session_01McpMNmiZC346o9SRtsHdqz, code/deltad/remote_deltad1c_C.sh + remote_deltad1c_decomp_C.sh -> results/deltad/dd0_1c_C, dd0_1c_C_decomp | - | launched 18:46 |
| COLLECT | the four shares runs keep the arms' cf.log.gz and value_at_26_by_node.txt for the welfare split (export_welfare.py): code/extra_2c/collect_shares_C.sh <arm>, added to each S-* worker's brief at 19:20 | S-* sessions | S-* done | queued |
| NOEXT | the three no-externality Treatment First arms (pe_noext Arm B, noext_fixp Arm D, noext_clear Arm C; x_pe, x_fx, x_nc, Table 7's last column) | session_01KfNXrhtt2bGBBJh7QNhh7N (Opus, engineering + run) -> results/pe_noext_C, noext_fixp_C, noext_clear_C | - | launched 19:21 |
| VALID | validation: who-stops (Mehay and Pacula, x_ws) and revocations (Costantini, x_rv) | session_015BJgiEXCE5sV9MseUiTq3i (Opus) -> results/whostops_2c_C, revoked_2c_C, revoked_2c_street_C | - | launched 19:21 |
| NISH | omega_c = 0.686: Treatment First by node (x_nish) | session_01TFwE8JW9kmsjD4reqkh7Eh (Opus) -> results/omega_nishiyama_C | - | launched 19:21 |
| TR | T = 70 transition on rule C, two loops, cohort print, first-year Milby print, newborn shares / age split / value shares | session_0158cnCRSjM6REt1e96n92QW (Opus): builds now, runs when C1 is accepted -> results/transition_2c_t70_C, transition_2c_C | C1 accepted | engineering |
| NOT REDONE | omega_c = 1 and internalisation arms (no screen), Housing First and no-policy arms, benchmarks, elasticities (benchmark), the stylized model (no treatment choice), the old elasticity-5 arm (not in the text) | - | - | - |
| PAPER | exporters re-pointed to the rule-C arms, every number regenerated, Section 4's rule and its footnote, the rule-A footnote, introduction and abstract; red, struck deletions, notes | this session | arms land | as they land |
| ABSTAIN | under rule C a household with the disorder had NO option to spend nothing on the drug (its v is the static closed-form split, zero only at a budget corner), so treatment-and-abstain to keep the voucher, the margin the author expects, was missing; found 12 Oct 20:50 from whostops_C being identical to rule A. Patch: a v=0 option for treated households with the disorder when the screen is on (inert without a screen); use statistics counted by v>0 | session_01X8qsuzJKVGeCpLCL7UQM5w (Opus): code/treat/patch_treatC2.py, build_treatC2.sh, build_tr70_C2.sh; tests -> results/counterfactuals_2c/tf_ruleC2_test | - | engineering; if the test shows the margin is used, APPROVED (the author, 12 Oct 21:05: "You need to fix this bug"). When the inert check, the compile table over every rule-C build and the test pass: copy patch_treatC2.py over patch_treatC.py (old kept as patch_treatC_v1.py), move each arm's results folder to <folder>_v1, and restart every rule-C arm on the fixed build from its _v1 folder's latest price and pi_V; the current runs keep going until then, as warm starts |
| CODE | the code/ scripts reorganised (REFEREE_PLAN item 5) | this session | no run executing them | last |

WARM STARTS (the author, 12 Oct: "start the simulations from guesses that equal each corresponding simulation with rule a"): every arm starts from its rule-A counterpart's price and pi_V (C1, fixpv, fixp, DD0, P50; P70 interpolated, since rule A's 0.70 arm never ran past pass 1), except S-tf and BOTH, which start from C1's latest pass. The rule-A distributions were not kept, so the distribution starts from the benchmark's in every arm.

- THE MILBY ROW OF THE VALIDATION TABLE (calib_tables.py, x_milby_model_impact) AND THE MILBY PARAGRAPH: the rule-C FIRST-YEAR recovery ratio of voucher holders against housed households without a voucher, both with a SUD, from the rule-C transition's 'TRANSITION MILBY t=1' line (export_results.py builds x_milby_model_impact from the transition's t=1; point it at the rule-C transition log). The author, 12 Oct: "We need rule c first year too", "That is the number to use in the table". The first-year treatment shares (export_milby_split.py's inversion) from the same line. The long-run ratio (1.37 at C1's pass 4, against 1.09 under rule A and Milby's 1.26) is secondary.

## RELAUNCH ON THE FIXED BUILD (12 Oct, 21:05 UTC)

The author: "You need to fix this bug", then "End the other runs, and start new ones". The bug: under rule C a household
with the disorder had no option to spend nothing on the drug, so it could never go into treatment and stop using to keep
its voucher (see the ABSTAIN row). The 12 sessions below were ENDED (archived) at 21:00 and must NOT be relaunched on
their old briefs or the old build. Their briefs are saved in code/rulec_relaunch/briefs_v1/<id>.md.

KEPT RUNNING: BOTH (session_01V66tfNJk92jP5jndoK5C3F). Its stages A (benchmark) and B (Housing First) have no screen,
so the fix cannot touch them; it was told at 21:02 to stop at the end of stage B, rebuild cf_fix2_both_spC once
code/treat/ABSTAIN_READY is on the branch, and only then run stage C.

SWITCH-OVER, when the ABSTAIN session's inert check and compile table pass (the one-to-two-pass test is NOT waited for:
the relaunched main arm is the test, and the author wants the runs going):
1. git mv code/treat/patch_treatC.py code/treat/patch_treatC_v1.py; cp code/treat/patch_treatC2.py code/treat/patch_treatC.py;
   check the "RULE C (patch_treatC.py)" marker and the MILBY SPLIT / TRANSITION MILBY prints are in it; push
   code/treat/ABSTAIN_READY (one line: the commit of the fixed patch).
2. Every results folder of the ended runs is COPIED to <folder>_v1 (the record of the buggy run), and in the original
   folder everything except passes.txt is removed, so each launcher that resumes from its own passes.txt warm-starts at
   the v1 run's latest price and pi_V, and the first publish of the new run overwrites passes.txt with its own passes.
   Folders whose stage was not touched by the screen are kept whole: results/deltad/dd0_1c_C's benchmark and null
   (Housing First), results/omega_nishiyama_C/*/null, every */null.
3. STAGED, NOT ALL AT ONCE (the author, 12 Oct ~21:20: "Maybe start with the key ones... Don't do all at once"; the weekly
   usage limit is also near, resetting Fri 16 Oct ~14:00 UTC):
   STAGE 1: C1 ONLY (the main arm), which is also the test of the fix. After its second pass, report to the author: the
     ABSTAIN lines (treated households with the disorder who stop vs still use, holders and not), use/SUD/h_1/CEV against
     the v1 pass, and the MILBY CHECK: the abstinence of voucher holders with a SUD against housed households with a SUD
     and no voucher, set beside Milby's contingent/non-contingent abstinence ratio (milby_ach_nach_ratio). If the model's
     ratio is far above Milby's, stopping is too easy and the author decides whether to add a cost of abstaining for a
     household with the disorder, calibrated to that ratio (the author, 12 Oct: "Should we add some additional cost to
     being in treatment and not using?"). NOTHING ELSE LAUNCHES BEFORE THAT DECISION.
   BUDGET (the author, 12 Oct ~21:25: "Prioritize them yourself so we have enough until Friday", "Don't run the four class
   model"): the weekly limit resets Fri 16 Oct ~14:00 UTC. BOTH (four classes) was ENDED at 21:07 and is DROPPED, as is P50
   (not quoted in the paper). Workers are Sonnet one-command sessions running the scripts already on the branch; an Opus
   session only where a script must be written. One check routine an hour (the :47 one was deleted). Order, by what the
   paper quotes: Table 5 and the abstract (C1, S-tf, decompositions, 26 names incl. the welfare split), the no-externality
   columns (15 names), the transition (30 names and the Milby first-year row), then the validations and sensitivities
   (who-stops 4, omega_c 0.686 4, revocations 2, detection 0.70 for footnote's claim, delta_d = 0 for the sentence the
   author asked for). Anything not done by Friday stays on rule A with the rule-A footnote saying so.
   STAGE 2 (after the author's go-ahead): S-tf and the three decompositions (S-fixboth, S-fixpv, S-fixp) and NOEXT, the
     author's priority ("the main experiments and the no externalities with the decompositions. And then the transition").
   STAGE 3: TR (when C1 is accepted; it is the longest, so it starts the moment C1 is accepted).
   STAGE 4, in this order and only as the budget allows: VALID who-stops, NISH, P70, DD0, VALID revocations. P50 and BOTH dropped.
   Each relaunch: a fresh session with its v1 brief plus a preamble: the fixed build, the warm start below,
   "the folder's passes.txt is the v1 run's and is only a warm start", and for the engineering sessions (NOEXT, VALID,
   NISH, TR) "your v1 scripts are on the branch; rebuild everything from the fixed patch_treatC.py; verify
   `grep -c abstain_now` > 0 in every rule-C cf.f90 before solving".

WARM STARTS (latest v1 pass, price / pi_V):
| id | folder | v1 latest | note |
|---|---|---|---|
| C1 | results/counterfactuals_2c/tf_ruleC | 0.8549 / 0.09819 (pass 4) | remote_treatC.sh resumes from passes.txt |
| S-tf | results/decomp_2c_shares_C/arm_tf | 0.8553 / 0.09615 (pass 2); the script reads tf_ruleC's latest | |
| S-fixboth | results/decomp_2c_shares_C/arm_fixboth | held at 1.0001 / 0.06753 | nothing to warm |
| S-fixpv | results/decomp_2c_shares_C/arm_fixpv | 0.8763 / 0.06753 held (pass 1) | script starts at 0.8742 |
| S-fixp | results/decomp_2c_shares_C/arm_fixp | 1.0001 held / 0.11606 (pass 3) | script starts at 0.11453 |
| P70 | results/counterfactuals_2c/tf_pdet70_C | 0.8651 / 0.09320 (pass 2) | P0_START/V0_START |
| P50 | results/counterfactuals_2c/tf_pdet50_C | 0.8793 / 0.08929 (pass 1) | P0_START/V0_START |
| DD0 | results/deltad/dd0_1c_C (+ _decomp) | tf 0.8729 / 0.07590 (pass 1) | benchmark and null DONE and kept: restore them, do not re-solve |
| NISH | results/omega_nishiyama_C | tf 0.8537 / 0.09547 (pass 1) | null kept |
| NOEXT | results/pe_noext_C, noext_fixp_C, noext_clear_C | noext_clear 0.9063 / 0.07613 (pass 2); pe_noext / noext_fixp arm at 1.0203 / 0.06753 | |
| VALID | results/whostops_2c_C, revoked_2c_C, revoked_2c_street_C | - | who-stops MUST be redone: with the fix a household with the disorder can stop on impact, so rule C no longer equals rule A there |
| TR | results/transition_2c_t70_C | endpoint tf 0.8555 / 0.09887 | runs after C1 is accepted, on the fixed transition build (build_tr70_C2.sh or the fixed patch) |

SWITCH-OVER DONE 12 Oct 22:10 UTC: patch_treatC.py is now the fix (old: patch_treatC_v1.py), code/treat/ABSTAIN_READY pushed,
results/counterfactuals_2c/tf_ruleC_v1 holds the v1 passes; C1 relaunched on the fixed build in session_01CmU5WFWASpRzVK167PwWdY
(Sonnet worker, code/treat/remote_treatC.sh, warm start 0.8549 / 0.09819 from the v1 pass 4), BEFORE the inert check finished
(inert_C2 due ~22:45): if results/counterfactuals_2c/tf_ruleC2_test shows the Housing First pass differs between the old and the
new build, archive C1 at once and tell the author. Then archive the ABSTAIN session.

## PAPER SWITCH: every rule-A path an exporter reads, and its rule-C replacement (12 Oct 22:25)
Done when the arm is accepted, one exporter at a time; the rule-A footnote's names are frozen first in
code/paper/ruleA_numbers.json (export_ruleA.py, DONE 22:21), so switching the exporters cannot move them.
| exporter (line) | rule A reads | rule C reads |
|---|---|---|
| export_results.py TF_ARM (69) | counterfactuals_2c/tf85_c35/tf | counterfactuals_2c/tf_ruleC/tf (env TF_ARM, or change the default) |
| export_results.py 345/358 (_dc), 393 | decomp_2c/arm_fixpv, arm_fixp; decomp_2c_both/arm_fixboth | decomp_2c_shares_C/arm_fixpv, arm_fixp, arm_fixboth (layout {tf,null}/ from collect_shares_C.sh) |
| export_results.py 176 (nish curve), 79 | omega_nishiyama_2c, omega_nishiyama/cf/{null,tf} | omega_nishiyama_C (null kept from v1; tf re-run) |
| export_results.py 213-214, transition_source.py 51, welfare_nok.py 197, export_longrun.py 210-252/838/915 | transition_2c (+ t70) | transition_2c_t70_C / transition_2c_C (TR) |
| export_results.py 728, export_longrun.py 68-80, export_pe_noext.py 21 | noext_clear, pe_noext, noext_fixp | noext_clear_C, pe_noext_C, noext_fixp_C |
| export_longrun.py 87-89, 320-322, 343; export_decomp_use.py 7 | decomp_2c, decomp_2c_both, decomp_2c_shares | decomp_2c_shares_C |
| export_welfare.py 34-37 | decomp_2c_both/arm_fixboth, decomp_2c/arm_fixp, (tf85_c35/tf, transition_2c/arm_tf) | decomp_2c_shares_C/arm_fixboth, arm_fixp, (tf_ruleC/tf or decomp_2c_shares_C/arm_tf, the TR arm) |
| export_milby_split.py 17 | counterfactuals_2c/milby_split | the long run: tf_ruleC/tf/milby_split.txt; the TABLE ROW: the rule-C transition's TRANSITION MILBY t=1 (RULE_C_PLAN Milby row) |
| export_whostops.py 26 | whostops_2c | whostops_2c_C |
| export_revoked.py 24, 55 | revoked_2c, revoked_2c_street | revoked_2c_C (street split dropped unless the budget allows) |
| export_nish_parts.py 22-23 | omega_nishiyama, omega_nishiyama_2c | omega_nishiyama_C |
| export_deltah.py 26-27 | counterfactuals_2c (delta_h) | NOT SWITCHED: the four-class run is dropped (the author) |
Any exporter whose rule-C run is not done by Friday keeps its rule-A path, and the rule-A footnote names it.

## SCOPE OF THE TEXT CHANGES (the author, 12 Oct ~22:35)
"the only things to change are the TF rule, any footnotes that say the experiment is different from the executive
order, and anything that describes the experiments in section 6". So: (1) the rule (Section 4's rule and its footnote;
the introduction's one-line definition of Treatment First, with the SUD acronym moved to it), (2) the struck footnote
that called the rule no programme's (no other such footnote exists: checked 22:35), (3) Section 6's descriptions of the
experiments, rewritten with the rule-C numbers. Everything else keeps its prose and only its generated numbers change:
the J_E footnote stays (reverted 22:30), the military paragraph's wording stays, and the Milby paragraph keeps the
recovery-hazard counterpart (no switch to abstinence).
Then (~22:40): "look for other places you think are relevant. any change should be in red". Found, besides the three:
- DONE now, in red with \why (true whatever the numbers): Section 6's description of the third experiment ("cannot
  respond quickly" -> can keep the voucher by entering treatment and stopping; the disorder clears slowly), and the
  transition's "households who do not have a SUD have agency" (+ "as do those with a SUD, who keep their voucher by
  entering treatment and stopping").
- WITH THE NUMBERS, in red: Section 5's military paragraph ("those with a SUD ... cannot stop on impact", twice; the
  rule-C who-stops run decides what replaces it); the transition paragraph on users without a SUD (line ~1031); the
  Discussion's summary ("households with a SUD lose their vouchers within a year"), its second lesson (the early cost
  "falling on households already having a SUD") and its design point on grandfathering ("They cannot respond quickly ...";
  under rule C they can, so the case for grandfathering rests on what the rule-C transition shows).
- UNCHANGED: the abstract, the Milby paragraph's wording (numbers only), the treatment-cost item in Section 5.

NOISE CHECK (22:57): the old build run twice gives welfare 789.1269 and 789.1271, voucher mass 0.180592 and 0.180644; the
fixed build 789.1273 and 0.180623, inside that spread (a pre-existing thread race, about 2e-4 in welfare, 0.01 pp of CEV).
So the fix is consistent with leaving Housing First unchanged; a one-thread bit-for-bit check is running in the ABSTAIN
session. Compile table PASSED on every base except transition_fix/build_tr70_C.sh, whose guard refuses the larger patch:
THE TRANSITION MUST BE BUILT WITH build_tr70_C2.sh. C1's warm start fell back to rule A's 0.8555 / 0.09615 (its first
publish overwrote passes.txt before it was read); harmless, but the other relaunches should pass P0/V0 explicitly.

STAGE 1 REPORT SENT 13 Oct 00:20 UTC (C1 pass 3: use -48.9%, SUD -47.5%, h_1 -27.5%, CEV +10.36%, gaps 6.8e-3 / 1.9e-2;
holders with a SUD 91.5% in treatment vs 24.4% of housed non-holders; long-run recovery ratio 1.51 vs Milby 1.26). The
one-thread inert check PASSED bit for bit (23:23); the ABSTAIN session archived. The C1 worker would not publish the
ABSTAIN lines (asked twice); they come with the arm's cf.log.gz at its end, or from the S-tf shares run. OPEN FOR THE
AUTHOR: (1) the go for STAGE 2; (2) an extra cost of stopping (recommended: no, proceed); (3) drug use counted like for
like: the fixed build's b drops treated households with a SUD at v=0, the no-policy arm's b keeps them (about 0.4 points
on the use change); recommended: subtract the comparison arm's own treated_v0 in the exporters.

THE AUTHOR'S DECISIONS, 13 Oct ~00:25: "1. Yes. 2. No, don't add it. 3. Count those in treatment with 0 drug use as non users."
So: STAGE 2 GO; no extra cost of stopping; and drug use excludes a household with the disorder that is in treatment and
spends nothing IN EVERY ARM. Done 00:40: patch_treatC.py / patch_treatC2.py count it in every arm (statistic only; C1, a
screen arm, is unchanged by this), the Housing First arms of the shares runs and of the no-externality runs now run on
patched builds (treat/build_share_treatC.sh: cf_fix2_share_treatC, cf_fix2_share_pe_treatC), so both sides of every
drug-use change count the same way. The v1 folders of the shares and no-externality runs moved to *_v1. STAGE 2 launched:
S-tf, S-fixboth, S-fixpv, S-fixp (one worker each, collect_shares_C.sh at the end) and NOEXT (one worker, all three scripts).
STAGE 2 SESSIONS (launched 00:38, Sonnet workers): S-tf session_01B8SBE89U2yDkdGh6xPt4HP, S-fixboth session_01FdoN6xM5HFzHdP4F8kBeVe,
S-fixpv session_01HJJJLdjar2KkXTSJY5PqgQ, S-fixp session_01NdUvKkjgHa3FvXpoUvayH7, NOEXT session_012LAue7QgHBbsNe2235T3M9 (relaunched 01:18 after a build-order error in noext_C_lib.sh; first worker 0128V3mR archived)
(all three no-externality scripts in one container). C1 is session_01CmU5WFWASpRzVK167PwWdY. FIRST CHECK: each build
compiles and each Housing First arm reaches its first pass (the shares' null now on cf_fix2_share_treatC through
treat/cf_arm_C.sh; NOEXT's Arm A on cf_fix2_share_pe_treatC); a GUARD there is a launcher error of mine, fix and relaunch.

TREATMENT IS PUBLICLY FUNDED (the author, 13 Oct ~02:00: "I think it should be add to the benchmark too... And all the
runs. You need to add it as a cost in the budget"). patch_treatC.py charges public_cost_of_treatment = 0.1332056
($9,426 a treated year, Roebuck, French and McLellan 2003, residential episode; first $3,000, ASPE Medicaid 2008, too low for a year per the author) per treated household with the disorder in
govt_spending_on_addicts, every arm. The benchmark is not re-solved (no choice reads net revenue there); Housing First's
budget target falls 5.8918411 -> 5.8275447 (code/treat/net_target_with_treatment.py), set in every rule-C launcher that
carries it. NISH and DD0 compute their targets from their own no-policy runs, solved before this: recompute at relaunch.
RESTARTED 02:11 at $9,426 (the 02:06 launch at $3,000 archived): C1 session_01P9BZwZSsi2ALKeiYxQgLLU (warm start
0.8615 / 0.09577, the v2 pass record restored into tf_ruleC/passes.txt), S-tf session_014SMDkjup43SJvf43yQ57Ej (relaunched 02:14 with the TREATSHARE print; 01C2HAuk archived), S-fixp
session_01D5LLBHWG2WNeQu48mh6cEA, NOEXT session_01UQEhx2Zo82w24DLqopVZQg.
13 Oct 08:41 UTC: C1 ACCEPTED after 8 passes (price 0.86347392, pi_V 0.097395854, b 0.0456, SUD 0.0199, h_1 0.00443,
CEV +10.65%, net revenue 5.82707 against 5.82754). Done by 09:15: S-fixboth (05:23), S-fixpv (08:31), pe_noext_C and
noext_fixp_C (08:53). Still running: S-tf, S-fixp, noext_clear_C (NOEXT session).
STAGE 3 LAUNCHED 09:20: TR session_015HhjEE3kd2YULdViLpywyh (Sonnet, code/rulec_relaunch/briefs_v2/TR.md):
bash code/transition_fix/remote_tr70_C.sh, now building with build_tr70_C2.sh (build_tr70_C.sh's guard refused the
current patch; test-built here first, binary b25b1720) and guarding on patch_treatC2.py's checksum. It re-solves the
no-policy arm and the terminal arm from C1's accepted price and pi_V, writes results/transition_2c_C/, then two T = 70
loops into results/transition_2c_t70_C/loop1, loop2 (the Milby row is loop2's TRANSITION MILBY t=1).
STAGE 4 LAUNCHED 09:22 (pre-fix results archived as _v1): WS session_016gJzSnkiKenKPq4hvGCNib (who-stops,
run_whostops_C.sh -> results/whostops_2c_C), P70 session_012jh446VKmXz3kJJpV51xYn (remote_pdet_C2.sh 0.70 ->
results/counterfactuals_2c/tf_pdet70_C, warm start tf_ruleC's accepted pass). Still to launch: NISH, DD0 (targets to
recompute with the treatment cost), revocations.
WHO-STOPS DONE 10:39 (results/whostops_2c_C). Holders who used under Housing First and stop under Treatment First:
all users 76.1% (rule A and pre-fix rule C 6.0%), users without a SUD 33.3% (53.2%); the tested (holders and offered):
all users 89.1% (19.4%), users without a SUD 100.0% (58.9%; the validation row's x_ws_tested_nosud_pc against Mehay and
Pacula's 61%). The reference (Housing First) moved too, 0.0608 -> 0.0556 among holders, because treated households
spending nothing are no longer users. All users jump because a treated household with the disorder can now stop on
impact. Users WITHOUT a SUD should not change (rule C is rule A for them) unless the EV-key or internal fix does it:
the EV-key fix says the old code's use candidate did not foresee losing the voucher, which should RAISE stopping, so
holders' fall from 53% to 33% is unexplained. DIAGNOSTIC 11:21: WSS session_018FkEpr8uTHRhKc5Q3SAXGs runs
deter_2c/run_whostops_C_switch.sh (all switches off, which must give rule A's numbers, then each switch off alone) ->
results/whostops_2c_C_switch.
P70 DIED 11:23 (its worker ended its turn at the 2-hour background cut instead of re-attaching; the container was
reclaimed and the solve lost after pass 1): RELAUNCHED 12:19 as session_015Pws8Uk5eaRhmdxLtKbMcg with the 2-hour cut
spelled out in the brief. The old session_012jh446VKmXz3kJJpV51xYn is dead; do not message it.
WHO-STOPS SWITCH DIAGNOSTIC DONE 12:40 (results/whostops_2c_C_switch; holders all / holders no SUD / tested all / tested
no SUD, per cent): all three switches off 6.6 / 53.2 / 20.7 / 58.9 (rule A's no-SUD rows exactly; the all-user rows
differ only because the reference no longer counts treated non-spenders as users); EV key off 18.6 / 52.2 / 29.5 / 58.0;
abstention off 5.8 / 47.3 / 35.2 / 100.0; internal off 76.1 / 33.3 / 89.2 / 100.0 (= all on). So: the EV-KEY FIX moves
the tested users without a SUD from 59 to 100 and holders without a SUD from 53 to 47; ABSTENTION takes holders without
a SUD on to 33 (getting the disorder no longer costs the voucher, so continuing to use is cheaper) and drives the
all-user rows; the internal fix does nothing here. The 59 per cent that matched Mehay and Pacula's 61 was produced by
the EV-table bug, which was in every Treatment First arm, rule A's included.
NOEXT DONE 12:28 (noext_clear_C as well; all three no-externality arms finished).
NOEXT TARGET BUG (found 12:55): noext_C_lib.sh kept rule A's NET_A 6.3830441, which has no treatment spending, while
the rule-C Arm A (with the public treatment cost) nets 6.3180936; Arms D and C therefore cleared 0.065 too high and pi_V
fell (6.11 and 6.23 per cent against 6.75) instead of rising. Arm B (PE, no clearing) is unaffected. Fixed NET_A =
6.3180936; the wrong runs archived as results/noext_fixp_C_wrongtarget, noext_clear_C_wrongtarget. RELAUNCHED 12:58:
session_017DH6daSd4sKVT7jCVBAGUo runs run_noext_fixp_C.sh and run_noext_clear_C.sh in one container (Arm A re-solved
first, ~4 h, then D and C; ~10-14 h).
PE ARM B (correct): against Arm A, use -76.1%, SUD -75.4%, homelessness -14.1% (rule A: -60, -61, +3); newborn adult CEV
(externality-free) -1.86% (rule A -1.50); population -0.73%; households with a SUD -10.7%. BUT 0.66% of households are
better off (all with a SUD: 17% of them, +2.6% CEV), where rule A's PE run had none: at fixed prices Treatment First
should only remove options, so something available only with the screen on (the abstention option, or the internal
fix, which leaves Housing First's treated households re-priced as untreated) favours it. To be checked with the switches,
as for who-stops, before the welfare numbers go in the paper; reported to the author.
DETECTION SCAN FOR WHO-STOPS (the author, 13 Oct: "I would look for the detection rate that gives the 61% first"):
PSCAN session_011jyPCcUtagjooEpr8Ppseo, 13:00, deter_2c/run_whostops_C_pscan.sh -> results/whostops_2c_C_pscan: the
reference, then detection 0.05 / 0.15 / 0.30 / 0.50, then four points inside the crossing interval, interpolated for
61 per cent of tested users without a SUD stopping on impact (0.85 gives 100). ~3.5-4 h. The PE better-off check
(switches on pe_noext Arm B) waits for the author.
THE AUTHOR, 13 Oct ~13:05: "Try a bunch of numbers to match that evidence... That should be the number we use". So the
detection rate p* at which 61% of tested users without a SUD stop on impact BECOMES THE PAPER'S DETECTION RATE. Plan:
(1) wait for PSCAN (~16:30-17:00 UTC); if the curve cannot hit 61 (a jump), tell the author before anything is stopped.
(2) With p*: stop TR, P70 and NOEXT2 (all at 0.85, obsolete); let S-tf and S-fixp finish (0.85, nearly done). Archive
every 0.85 rule-C result as *_p85 (tf_ruleC, decomp_2c_shares_C, pe_noext_C, ...) and relaunch at p* to the same paths:
C1 (remote_pdet_C2.sh p* or remote_treatC.sh with PDET), S-tf, S-fixboth, S-fixpv, S-fixp, pe_noext B, noext D and C,
who-stops at p*, and TR at once alongside C1 (its launcher starts from C1's latest pass and re-solves if needed). Make
PDET an env setting in each launcher first (only after the worker running it has stopped). C1 at 0.85 stays as the
sensitivity; P70 is dropped. Paper: the detection item in Section 5 / the experiment section gets the new value and
its target (Mehay and Pacula's 61 per cent on impact), and the validation row becomes a calibration target.
THE AUTHOR, 13 Oct ~13:15: "pick pdet to match the 59% and then run one sensitivity with half that pdet, and say the
results hold even then and state what the drug use response is relative to the 59%". The data number is 61
(mp_stay_rel_pc; 59 was the model's old, bug-made value): TARGET 61 unless the author says 59 (the scan's curve gives
either). SENSITIVITY: ONE long-run Treatment First arm at p*/2 (remote_pdet_C2.sh p*/2, price and pi_V clearing) plus
ONE who-stops impact run at p*/2 (the exact share stopping at half detection, quoted against 61 at p*). P70 and any
0.85 sensitivity are dropped; C1 at 0.85 stays on disk but is not quoted.
NOEXT2 (12:58) FAILED AT ONCE in run_noext_fixp_C.sh: "GUARD: no gfortran" -- the two launchers started side by side
and the fixp one does not install gfortran (the same race as the first NOEXT launch; that brief had the worker run
apt-get install gfortran first, the NOEXT2 prompt did not). Not relaunched: it is at 0.85 and obsolete. AT THE p*
RELAUNCH the no-externality worker must install gfortran BEFORE starting either launcher.
13 Oct 13:22, THE AUTHOR: "Yes. No need to run them since we need to find pdet". ARCHIVED (containers released, jobs
ended): TR session_015HhjEE3kd2YULdViLpywyh, P70 session_015Pws8Uk5eaRhmdxLtKbMcg (and the dead 012jh446), NOEXT2
session_017DH6daSd4sKVT7jCVBAGUo, S-tf session_014SMDkjup43SJvf43yQ57Ej, S-fixp session_01D5LLBHWG2WNeQu48mh6cEA.
ONLY PSCAN (session_011jyPCcUtagjooEpr8Ppseo) RUNS. Everything at 0.85 stops here; the next launches are at p*.
PSCAN FILLED ITS DISK at the end of round 1 (~14:35; five run directories, each a full copy of the benchmark plus its
output); the worker went idle, no commit after 14:32, the who-stops lines were never published. RELAUNCHED 15:19 as
PSCAN2 session_01YHexQ4gUbb3GFmpvsw2KvL: deter_2c/run_whostops_C_pscan2.sh -> results/whostops_2c_C_pscan2 (two runs
at a time, finished runs trimmed to their logs; round 1 at 0.02 / 0.05 / 0.10 / 0.20, since the first scan's published
tested-use rates, all users, fell 29% at 0.05 and 51% at 0.15). ~3.5 h.
15:25 (the author: "Why an hr?"): THREE MORE CONTAINERS, deter_2c/run_whostops_C_points.sh, each its own reference and
two rates: session_01AKNDcu3M15zvoera9E9WH5 (0.10, 0.20 -> results/whostops_2c_C_pts_0p10_0p20),
session_01BcBGsGiU1qFKr9tVa1632t (0.075, 0.125 -> ..._pts_0p075_0p125), session_01RpgCnWwA1wGctvk2vEWJNC (0.15, 0.25 ->
..._pts_0p15_0p25). With PSCAN2's 0.02 and 0.05, eight points by ~16:45 UTC; PSCAN2 then repeats 0.10 and 0.20 (a
reproducibility check) and refines. CHECKS before any number goes to the author: hf file = 1; the tested-no-SUD
denominator equals the reference's 0.0986619 in every run; start = 0; monotone in detection; the reference's use rates
equal 0.0555847124 / 0.1780291188 / 0.0743861992; every percentage recomputed from the archived cf.log.gz at the end.
16:26 FIRST NUMBERS (verified from the logs: hf file 1, denominator 0.0986619, start 0, p_det set as asked): detection
0.15 -> 36.06% of tested users without a SUD stop (all tested users 51.0%, matching the first scan's published 51%);
0.25 -> 55.24% (all 66.5%). The crossing is ABOVE 0.25: 16:28 THREE MORE CONTAINERS, run_whostops_C_points.sh 0.275 0.30
(session_01LAFAx64hLWpDskCE1W6Cbh), 0.325 0.35 (session_01AURE7ftkrsfer38L9Aia9z), 0.40 0.50
(session_01K4GpjSsmNAFsJGJ6CQTYtj); due ~17:50 UTC.
16:39 GRID COMPLETE (all verified from logs): tested users without a SUD / ALL tested users stopping on impact:
0.02 11.5 / -; 0.05 17.6 / -; 0.075 22.2 / 35.5; 0.10 25.9 / 41.3; 0.125 30.0 / 46.6; 0.15 36.1 / 51.0; 0.20 49.5 /
61.6; 0.25 55.2 / 66.5; 0.85 100 / 89. THE AUTHOR (16:50): "I think it should count all tested users" -> p_det = 0.20
(61.6% of all tested users stop, Mehay and Pacula's 61; interpolated 0.197). Half-rate sensitivity 0.10 (41.3%).
Who-stops at both is done: results/whostops_2c_C_pts_0p10_0p20. Rule-C reason for counting all users: under rule C a
user with a SUD can stop on impact (treatment + abstention), so Block 8's reason for leaving them out is gone.
The three containers above 0.25 archived (not needed); PSCAN2 kept until it repeats 0.10 and 0.20 (reproducibility).
16:58 LAUNCHED AT 0.20 (every launcher now defaults to 0.20, RULEC_PDET overrides; 0.85 results archived *_p85):
  C20  session_01Ew762nUPBnLaz9VF73dA6Z  pdet/remote_pdet_C2.sh 0.20 -> results/counterfactuals_2c/tf_pdet20_C
  C10  session_01H6FotGSmzvg98twWQfWTYY  pdet/remote_pdet_C2.sh 0.10 -> results/counterfactuals_2c/tf_pdet10_C
  S-tf session_01TZxWsr5pSTaaWpRt8ycU2J, S-fixboth session_01WfknydYFoDXBRgeyLDnq1j, S-fixpv session_01NcPdayBHZdJfufaHciswDd,
  S-fixp session_018ixGRpLBP7wDvWBSME5pmF   extra_2c/remote_decomp_shares_C.sh <arm> -> results/decomp_2c_shares_C/arm_*
  NOEXT session_01FXm2FJQcFfyMKvmru6Fdou  gfortran first, then run_pe_C.sh, run_noext_fixp_C.sh, run_noext_clear_C.sh
       -> results/pe_noext_C, noext_fixp_C, noext_clear_C
  TR   session_01Dkk3xgSVS2rMQbfZroUGd7  transition_fix/remote_tr70_C.sh (terminal arm checked against tf_pdet20_C)
       -> results/transition_2c_t70_C, transition_2c_C
  REVK session_01J1YCiMyKJTj8Uat4Fiv3P9  revoked_2c/run_all_C.sh (the Costantini validation's five-script pipeline at 0.20)
       -> results/revoked_2c_C, revoked_2c_street_C
VALIDATING THE EXPERIMENT (the author, 13 Oct ~17:05: "add those little validation results for the counterfactual too.
The milby comparison, ie, the increase in treatment take up... And anything to validate the experiments"). With Block 8
moved to the experiment section as the calibration of p_det and c_test, the experiment gets its own validation:
Milby et al. (2005) first-year recovery ratio (transition at 0.20, TRANSITION MILBY t=1); Padgett et al. (2011) take-up
46% vs 7% (x6.6; transition year 1 or S-tf TREATSHARE, SMI+SUD holders) and leaving the programme 54% vs 11% (AWOL;
model: holders losing the voucher within a year, from the revocations pipeline or a transition print); Costantini (2025)
mortality of the revoked (REVK); Mehay and Pacula's own policy estimates, 11-45% (use among the tested after year 1).
OPEN for the author: Padgett also finds Treatment First clients used MORE (65% vs 30%); the model will show less.
THE AUTHOR (17:12): "You show me the numbers compared to the data and we can decide what to show at the end" -- one
table, data against the model at 0.20 (and 0.10), every validation; nothing into the paper before the author chooses.
REPRODUCIBILITY (17:08): PSCAN2's independent 0.10 and 0.20 give 25.8876% and 49.4551% of tested users without a SUD,
identical to the 0p10_0p20 container's; PSCAN2 archived after it.
18:35 RESTART FROM A NEARER PRICE (the author: "Do the decompositions you suggested"). The drug price moves at most
0.5% a pass (max_drug_price_move = 0.005, the author 8 Sept) and the 16:58 runs started from the 0.85 price 0.86: the
0.10 run sat at 0.872 after two passes with a 50% drug-market gap (use +21%, an off-equilibrium artefact). Warm starts
from the year-one use falls (0.85: -52.3%, 0.20: -27.2%, 0.10: -17.7%) and the 0.85 run's price fall per unit of that
(13.65/52.3): 0.20 -> price 0.93, pi_V 0.082; 0.10 -> 0.955, 0.077 (the 0.85 run's price was the same with pi_V held or
clearing, 0.861 / 0.864). First passes archived as tf_pdet20_C_slowstart, tf_pdet10_C_slowstart,
decomp_2c_shares_C_slowstart/arm_tf, arm_fixpv. Relaunched:
  C20  session_014BV5qjcEFHQ6Z5ueM2HsdF  P0_START=0.93 V0_START=0.082 bash code/pdet/remote_pdet_C2.sh 0.20
  C10  session_014GswRL6uHo1efdYWSYymZH  P0_START=0.955 V0_START=0.077 bash code/pdet/remote_pdet_C2.sh 0.10
  S-tf session_018Hx3hhwtWBXMEKme9BjY95  SHARES_P0=0.93 SHARES_V0=0.082 bash code/extra_2c/remote_decomp_shares_C2.sh tf
  S-fixpv session_016yrmFb79EoSwu8AmVsvAhJ  SHARES_P0=0.93 bash code/extra_2c/remote_decomp_shares_C2.sh fixpv
Not restarted: S-fixboth and S-fixp (price held), NOEXT (a 4 h Housing First re-solve each restart), TR (re-solves
its end state from C20's accepted values), REVK.
DELTA_H DROPPED (the author, 13 Oct: "It looks like homelessness and child homelessness are both going to drop even in
transition... So we won't need the deltah run at all"). No delta_h run on rule C, one class or four; the paper quotes no
delta_h number (export_deltah.py stays unswitched). If the rule-C transition confirms it, the intro's and Section 6's
"first rise, by up to x_trf_h_peak_pc / x_trf_hchild_peak_pc" sentences need rewording, not only new numbers.
TREATMENT TAKE-UP CHECK (the author, 13 Oct: report it as a factor): New York treatment-first vs Housing First clients
46% vs 7% in treatment (6.6x; Padgett et al., SSWR 2006 abstract; ask the author for the published paper), against
the model's voucher holders with a SUD under Treatment First vs under Housing First (pass-3 v2: 91.5% vs 27.7%, 3.3x).
THE GOOD COMPARISON (the author: "We need a good comparison"): match the study's population, programme status and
window. The 46%/7% is most likely the New York Recovery Study (Padgett, Stanhope, Henwood and Stefancic 2011, Community
Mental Health Journal; 27 Housing First and 48 treatment-first clients with serious mental illness, interviewed at 0, 6
and 12 months): ASKED THE AUTHOR TO UPLOAD IT. The model side: the TREATSHARE print (S-tf, both arms' cf.log.gz via
collect_shares_C.sh) gives households with a SUD by status (holder, housed without voucher, homeless) x SMI, mass and
treated; the counterpart is SMI + SUD voucher holders under each policy (and the screened population as a variant).
FIRST TREATSHARE READING (13 Oct 06:20, S-fixboth, decomp_2c_shares_C/arm_fixboth/{null,tf}/cf.log.gz): under Housing
First NO voucher holder with SMI + SUD is in treatment (mass 0.0233, treated exactly 0; all SMI + SUD 0.2%), because
b_smi_multiple raises their taste for the drug so treatment never pays without the voucher at stake. Non-SMI holders
with a SUD 31.5%, all holders with a SUD 27.7%. Treatment First at fixed price and pi_V: SMI + SUD holders 96%, non-SMI
90.5%, all 91.7%. So the like-for-like factor (SMI + SUD holders) is undefined off a zero base; the all-holders factor
is 3.3 against Padgett's 6.6. The data (46% / 7%) sits between the two: the model's gap is larger in the study's own
population, smaller across all holders. Equilibrium Treatment First figures come from S-tf; the Housing First side is
the benchmark and will not change.
S-fixboth and S-fixpv ALSO RESTARTED 02:15 (the author: "you'll need to rerun everything with the new updates"; every
run on the same code): S-fixboth session_017GEgxbEZ3Jk93hEDnXbDWa, S-fixpv session_01UfobFPfyCKyp8Lifrev8Cc.
EVERY RUNNING RUN IS NOW ON: the abstention fix, use counted v>0 in every arm, the $9,426 public treatment cost, and
(S-tf, S-fixboth, S-fixpv) the TREATSHARE print. Stages 3-4 (TR, who-stops, P70, NISH, DD0, revocations) will build
from the same patch when they launch. The
no-cost C1 passes are in results/counterfactuals_2c/tf_ruleC_v2. PAPER: Section 4's government budget gains the
treatment term and Section 5 the parameter and its source (red, with a note).

## Gates
- C1 inert check (pass 1): welfare differs from rule A's 789.9399 at the same start, and the MILBY SPLIT line shows
  voucher holders with a SUD in treatment. Fail -> stop, diagnose, tell the author before anything else launches.
- Every arm: DIST CHECK PASS, budget cleared (TARGET CHECK PASS) where pi_V clears, no GUARD.
- The paper is rebuilt only from accepted arms; the checkers pass; the author gets the PDF with every change red.

## On each check (every 30 minutes: the routine at :17 and a second at :47)
The author, 12 Oct: "make sure to check that all the runs are working all the time so we dont waste time".
1. Fetch. For every live rule-C session: get_session (status_bucket failed or a rate-limit stop = dead) and the last
   commit on its results folder. Silent for 45 minutes while solving, or 90 while building or in a transition loop that
   publishes less often = dead.
2. A run that is alive but not advancing is wasting time too: the pass count must rise at least every 90 minutes, and an
   arm whose budget gap and drug gap have stopped falling for 4 passes is reported to the author with its passes table.
3. A dead run is relaunched at once in a fresh session with the same brief (arms resume from their last published pass);
   a run that dies twice is reported, not relaunched. A rate-limit stop is relaunched on another model if one is available.
4. One line to the author when nothing changed; a message at once when something died, stalled or landed.

19:35 TRANSITION AT T = 50, LAUNCHED ONLY AFTER C20 IS ACCEPTED (the author: "for the old rule A we know T had to be
70...50 was not enough", "but here we can probably use T=50"; then "we cant run the T=50 yet...we first need the main
long run experiment"). code/transition_fix/remote_tr50_C.sh (commit e3cd61e9; build_tr50_C.sh test-built here, binary
0487a9eb): T = 50; seeds = rule A's T = 70 loop-2 paths RESCALED to the rule-C terminal (rescale_seeds_C.py), because
the transition moves each year's price at most 0.5% a loop and remote_tr70_C.sh's raw rule-A seed ends at 0.857
against a rule-C terminal near 0.93 -- the T = 70 run as launched could not have closed that; four loops, each with a
horizon check (horizon_check_C.py, last ten years against the terminal); newborn values after the path.
THE SWITCH, AT C20's "arm tf ACCEPTED" and not before: message TR session_01Dkk3xgSVS2rMQbfZroUGd7 (create_trigger with
persistent_session_id + fire_trigger + delete_trigger) to (1) stop remote_tr70_C.sh and its processes (pkill -f
remote_tr70_C.sh; pkill -f cf_arm_tr2c_C.sh; pkill -x hftf_cf; pkill -x hftf; check with pgrep) and never relaunch it,
(2) git fetch + rebase, (3) bash code/transition_fix/remote_tr50_C.sh with run_in_background=true, re-run after every
2-hour cut until "remote_tr50_C: finished". Until then the T = 70 worker keeps running (its terminal arm walks from 0.86
and is useless, but it keeps the container, its builds and the solved no-policy arm alive for the switch).
WHY THE TWO NUMBERS DIFFER (the author: "drug use drops by 41% ... when pv is held, but then 8% drop and it drug use
rises by 5.5%??"): the -41% is S-fixp (the paper's economy, price held at 1.00); the +5.5% is noext_clear (no
externalities, whose own Housing First clears at 1.031, at a non-equilibrium 0.921 with a 34% drug gap), both against
the paper's benchmark. In the paper's economy Treatment First use is -43% at 1.00 and +12% at 0.868 (the slow-start
pass): very price-elastic, so the price falls little (estimate 0.93-0.94) and use ends perhaps 15-20% below Housing First.

19:40 NO-EXTERNALITY ARM C FROM A NEARER START (the author: "are you now relaunching the long run with better price
guess?"). The 16:58 Arm C started at rule A's 0.907; after four passes 0.926, drug gap 0.32, walking 0.5% a pass
(results/noext_clear_C_slowstart/status.txt). Relaunched in a FRESH container so the NOEXT container's two solve slots
go to Arms D and B (Arm D had not started: the slot gate let A and C run): NOEXTC2 session_01RAQUXs5kJFd5Ea2zZqHXY8,
NOEXT_P0=0.98 NOEXT_V0=0.071 bash code/noext_clear/run_noext_clear_C2.sh (re-solves Arm A there, identical inputs).
Start 0.98 hedges two readings: the paper's economy's two-point slope (0.868 and 1.00) puts the no-externality price
near 0.97, this run's own pass-to-pass slope near 1.00. The NOEXT session (session_01FXm2FJQcFfyMKvmru6Fdou) was told
to run code/noext_clear/stop_clear_C.sh (stops only run_noext_clear_C.sh and the solver whose cwd is
cfarm_tf_noext_clear_C) and never to relaunch run_noext_clear_C.sh; it keeps run_noext_fixp_C.sh and run_pe_C.sh.

20:20 WORKERS DO NOT ACT ON TRIGGER MESSAGES. Three create_trigger(persistent_session_id) + fire_trigger instructions
(NOEXT stop at 19:38 and 19:54, C20's signed net revenue at 19:46) were delivered (each session took a turn within
seconds) and not acted on: the old run_noext_clear_C.sh published again at 20:13, and C20's 20:01 publish carried no
net_revenue_signed.txt. A worker treats such a message as a stored routine prompt, not its user. So a running worker
can only be stopped by archiving its session, and archive_session was REFUSED here by the permission classifier
(Interfere With Workloads): it needs the author. Consequences:
  * NOEXT (session_01FXm2FJQcFfyMKvmru6Fdou) still runs the old Arm C beside Arm A, D and B; NOEXTC2 runs Arms A and C
    from 0.98. Both write results/noext_clear_C. A fresh D+B session (session_01SkXhdbttXYRonPQLgXk4T1) was created
    together with the refused archive and interrupted while still pending (cancel_queued); check it started nothing.
  * THE TRANSITION SWITCH CANNOT BE DONE BY MESSAGE. TR (session_01Dkk3xgSVS2rMQbfZroUGd7) must be archived (by the
    author, or with the author's permission) before remote_tr50_C.sh runs in a fresh session: both write
    results/transition_2c_C.
  * The sign of C20's budget gap comes from pi_V's first move (it moves once the drug market is nearly cleared) or the
    accepted final.txt.

21:09 T = 50 LAUNCHED, WAITING FOR C20 (the author: "yes, you can archive the old T=70...i think T=50 would be enough").
TR session_01Dkk3xgSVS2rMQbfZroUGd7 ARCHIVED with the author's permission. TR50 session_01Nu3rXPEQeXsPgAsGvrgc5o runs
bash code/transition_fix/remote_tr50_C.sh (commit 60de5043): builds, the no-policy arm, then waits for
results/counterfactuals_2c/tf_pdet20_C "arm tf ACCEPTED" before starting the terminal arm from the accepted price and
pi_V (TF_EARLY=0, the default now), then the T = 50 loops with the horizon check -> results/transition_2c_t50_C.
No message is needed at acceptance: the launcher sees it on the branch itself.

21:35 TWO WRITERS ON results/noext_clear_C. The old NOEXT container's duplicate Arm C (from 0.907) and NOEXTC2's (from
0.98) both publish there, and git's rebase -X theirs merges their hunks, so the status file can MIX the two runs (21:31:
NOEXTC2's header over the old run's pass table). NOEXTC2's Arm C cleared the drug market at 0.985 in two passes and will
finish first; the moment it does, COPY its results to results/noext_clear_C2 (git cp of arm_A, arm_C, walk, analysis)
and point the exporters there, because the old copy finishing hours later would overwrite results/noext_clear_C.
The revocation guard (21:27) was analyse.py crashing on the two-thread logs run_paths_C.sh never runs: fixed in
08ec5f91; the REVK worker, asked to rerun its own command, did so and the pair PASSED at 21:29 (a worker does act on a
message that only asks it to continue its original job).

22:55 NOEXTC2 DONE, FLOWS RELAUNCHED, FIXP SEE-SAWING.
- NOEXTC2 (run_noext_clear_C2.sh) finished 22:50: price 0.9849, pi_V 0.06974, use -16.8%, SUD -14.9%, h_1 -6.1%,
  gaps 2.2e-4 / 3.6e-4. Frozen as results/noext_clear_C2 (b8a23e3a); the PAPER SWITCH row for noext_clear reads
  noext_clear_C2, not noext_clear_C (the old slow-start Arm C still writes there).
- BCGHW flows: the crash was cf_arm_flows.sh's seeded-build case not listing cf_flows (no
  distribution_stationary{1,2}seed.dat), not patch_flows.py. Fixed aefb00ff; relaunched at -O3 in
  session_019AhRcBkr1snb4enEJx2Wcb. The bounds-checked session 01C2CgE7 is finished; leave it (archive needs the author).
- S-fixboth newborn shares in (results/decomp_2c_shares_C/arm_fixboth/newborn_shares.txt): 82% of newborns better off.
- S-fixp (price held, pi_V clearing) jumps between two states: pi_V 0.0917-0.0924 gives use -48%, 0.0932-0.0943 gives
  -42%, budget gap 6e-3 to 2.4e-2 across passes 4-8. Use FALLS less as pi_V rises, so a discrete switch of a group in
  between, and the budget may have no root inside the jump. If not settled by pass 10-11, find which cells switch.

00:25 (14 Oct) FLOWS DONE; FIXP RESTARTED; NOEXT B AND D DONE.
- BCGHW flows finished (5 passes, simulation_ended, CEV vs benchmark 1.8e-5): results/bcghw_flows/flows.txt. Its GUARD was
  false: cf_arm_flows.sh's DIST rule did not name cf_flows among the cf_fix builds (5e-6 instead of 5e-5/70); every pass
  met the cf_fix rule. Fixed in the script. Entry ratio SUD/no SUD 2.70 (theirs 4.56 long-standing, 3.43 new; ours is
  raw, theirs adjusted); still homeless a year after entry 56.6% (theirs ~25%): the model's homelessness is too
  persistent at an annual period. Show the author before anything goes into the paper.
- S-fixp's container restarted (worker_epoch 2) and the job began again at 23:16 from PV_START 0.11453: the nine
  see-sawing passes are lost. Same start and binary, so it will likely retrace them (~03:00 UTC). Proposed to the author:
  accept the bracket near pi_V 0.0937 (use -42.2%, h_1 -21%, CEV ~+8.1%) with a note, or rerun with a damped pi_V rule.
- pe_noext_C (Arm B) and noext_fixp_C (Arm D) done 23:59. Their notes say "detection 0.85" (stale text in the note);
  the handovers ran 0.20 (HANDOVER probability_of_detection 0.95 -> 0.20). B: use -27.6%, SUD -25.9%, h_1 -7.3%.
  D: pi_V 0.0693, use -30.7%, SUD -29.0%, h_1 -9.2%.

00:50 (14 Oct) TABLE tab:longrun GETS THE NO-EXTERNALITY 'BOTH CLEAR' COLUMN BACK (the author: "Now we can show the price
one as well in the table... Where both clear", once rule C's newborn loses there too, -0.54% against +0.39% under rule A).
- export_longrun.py: nc_c in TABLE_MAIN after fx_d; headers span 4+4 (cmidrule 2-5/6-9, 3-5/7-9). 422pt wide at
  scriptsize/4pt against the 470pt text width (402pt before). Table note renumbered in \new{} with a \why (the striker
  skips tables, so the replaced words are listed in the note).
- STILL TO DO IN THE ROUND, with the switch NC -> results/noext_clear_C2: the 6.2 paragraph "If the drug price is also
  allowed to clear the drug market, newborns gain x_nc_newborn_cev ... That gain is the general-equilibrium effect"
  must take its direction from the number (newborns LOSE under rule C) and point at the fourth column; "And yet, no
  household is better off under Treatment First" is false under rule C (1% better off, 26% of SUD households); the
  decomposition sentences x_dcp_why (use falls LESS with pi_V clearing under rule C) and x_dc_b_source ("most of the
  gain": the screen alone, 4.07, exceeds the full 3.30) need branches for the rule-C direction.
- code/stylized/fill.py stops at TARGET["hsmall"] (KeyError) when run alone here: check how the round build fills
  before the round, not during it.

01:00 (14 Oct) NEW RUN CA: RULE A'S SCREEN ON RULE C'S BUILD, DETECTION 0.20 (the author: "a run with rule a but where
gov't doesn't give vouchers or revokes them to those with Sud. So treatment doesn't help them retain it ... Use the same
pdet. Just to be able to answer to those who might say that people can't stop using in treatment. Gov't still pays for
treatment, but doesn't give vouchers to those in treatment even if they don't use.... Unless they can't detect it").
- code/treat/patch_treatCA.py = patch_treatC.py, then fails_1 back to rule A's line (the disorder fails in treatment or
  not; any use fails) and tc2_abstain_on default 0. Source differs from rule C's at those two lines only; compiles.
  Public treatment cost, EV-table key, own treatment in internal_computations, v>0 use count all kept.
- build_treatCA.sh -> code/cf_fix2_treatCA; treat/cf_arm_CA.sh (cf_arm_C.sh + cf_fix2_treatCA, threads from the
  caller); pdet/remote_pdet_CA.sh 0.20 -> results/counterfactuals_2c/tf_pdet20_CA. Budget target 5.8275447063 (Housing
  First with its treatment spending), the $35 test. Warm start P0_START/V0_START = C20's pass 7 (0.9461, 0.07891).
- One long-run arm only (no shares, no transition) unless the author asks for more.

01:05 (14 Oct) TABLE tab:longrun: ALL USEFUL COMBINATIONS (the author: "You can add all the combinations to table if they
are actually useful. But make sure the table fits the page and doesn't become horizontal"). dc_pv (pi_V held, price
clears) is a column again, eighth, before the main experiment; its childhood share from welfare_nok with
decomp_2c/arm_fixpv's by-node values (rule C: decomp_2c_shares_C/arm_fixpv at the switch). Ten columns, 449pt against
470pt, portrait. Table note, the dc_pv footnote and the prose's column numbers (dc_b sixth, dc_p seventh) updated in red.
The one combination with no run is no externalities with only the price clearing; not run (it adds nothing to the
moral-hazard verdict, which the held-price columns carry, and the budget is short).

01:20 (14 Oct) THE NO-EXTERNALITY PRICE-CLEARS RUN (the author: "Sure add the price clears only runs"). New launcher
code/noext_clear/run_noext_pclear_C.sh (run_noext_pclear.sh on the rule-C build via noext_C_lib.sh): Arm A re-solved,
Arm E = Treatment First at 0.20, price clearing from 0.985, pi_V held at 0.067533863, adjust_taxes 0; pi_V check; the
walk; analyse A vs E -> results/noext_pclear_C. export_longrun.py: ne_e (results/noext_pclear until the switch, then
noext_pclear_C) in the no-externality block, fourth column; eleven columns at tabcolsep 3pt, 458pt of 470pt.
x_nc_newborn_dir added (gain/lose) and the assert that newborns gain when both clear removed (rule C: they lose).
S-fixpv done 00:46; its worker asked (trigger trig_01TH2UpECvdNHScPD5ZmCghH) to run newborn_C.sh fixpv + collect_shares_C.sh.

01:45 (14 Oct) A CODE ASYMMETRY IN EVERY RULE-C WELFARE COMPARISON, AND A DIAGNOSTIC.
- Symptom: with price and pi_V held (screen only), 24% of households with a SUD are better off under rule C (decomp
  fixboth, tol 1e-3; rule A: 0%); without externalities, 25.5% (pe_noext_C; rule A: 0%). A screen that only removes
  options cannot do that. The share matches the treated share of SUD households (29%).
- Not the abstention option: treated households without a voucher abstain at 0.004% (ABSTAIN print), so v=0 is not
  valued for itself. Not the voucher probabilities: under Housing First category 3 draws pi_V like the others.
- Cause found: patch_treatC2.py's third fix (the household's own treatment before internal_computations) is gated on the
  screen (voucher_conditional_on_clean==1), and internal_computations OVERWRITES THE NODE'S VALUE
  (value_function_1=val_fun_internal). So Housing First's treated households are valued as untreated, Treatment First's
  correctly: the two arms run different arithmetic. Rule A had both on the old arithmetic.
- Diagnostic (launched 01:45): treat/patch_treatCu.py (the gate removed on that one fix; source differs at one line;
  syntax-checked), build_share_treatCu.sh, cf_arm_Cu.sh, extra_2c/remote_decomp_shares_Cu.sh fixboth ->
  results/decomp_2c_shares_Cu/arm_fixboth: Housing First on the ungated build beside the screen-only arm, shares, and
  the comparison with the gated run. If the SUD share falls to ~0: re-solve every Housing First comparison run on the
  ungated build (nulls, no-externality Arm A + walks); if Housing First's net revenue moves, the pi_V-clearing arms'
  target moves too. The PDF waits for this.

05:20 (14 Oct) THE DIAGNOSTIC: THE ASYMMETRY WAS REAL, AND IT MOVES ONLY THE SUD SHARES.
- results/decomp_2c_shares_Cu/arm_fixboth (done 05:08): with the internal_computations fix ungated, so Housing First runs
  the same arithmetic as Treatment First, the screen alone leaves 0 percent of households with a SUD better off (gated:
  24.2 at tol 1e-3), 0 of all households (0.9), and the same 99.8 percent of entrants at 26 worse off. The Treatment
  First arm is bit for bit the gated one (passes 1-4 identical).
- Housing First itself barely moves: drug price 0.9994 (1.0003), use 8.920 (8.895), SUD 3.828 (3.815), homelessness
  0.6184 (0.6186), treatment take-up 24.57 (24.92), welfare 787.4916 (787.4962: about +0.01 points on the newborn's
  CEV). Its net revenue is 5.8372 against 5.8278, 1.6e-3 relative, above the budget tolerance: the pi_V-clearing arms
  re-clear against it (pi_V perhaps 0.1 point lower).
- WRONG IN THE r320 TABLES until re-solved: the SUD better-off row in every rule-C column (and all households by up to a
  point), and the sentences quoting them (x_pe_better_clause, the 71 percent worse off, the main column's 52 percent).
- LAUNCHED 05:13: CU-tf session_017VnBYL9usdejwN3rLMzpJM, extra_2c/remote_decomp_shares_Cu2.sh tf (SHARES_P0=0.94610081
  SHARES_V0=0.079100383): the corrected Housing First, the main arm re-cleared against its revenue, shares, newborns
  (newborn_Cu.sh) and the welfare-split files (collect_shares_Cu.sh) -> results/decomp_2c_shares_Cu/arm_tf. When it
  lands: rulec_paths.py NULL_DIR, TF_NODES and DC['tf'] -> decomp_2c_shares_Cu/arm_tf (TF_DIR's final numbers too, if
  the re-cleared arm moved). Still to decide with the author: the other columns (fixboth's shares are already in the
  diagnostic; fixpv, fixp after their gated runs), the no-externality economy's Arm A on an ungated no-ext build, and
  whether the T = 50 transition (benchmark start, gated) is restarted.

12:35 (14 Oct) THE r320 PDF SENT (~11:55, commit e3a27cf4); THE AUTHOR: "Yes to 1-4". LAUNCHED, all against the corrected
Housing First (internal_computations fix ungated):
- CU-fixboth session_017AD88HWnpyuE8Sv5s3WkAQ: remote_decomp_shares_Cu2.sh fixboth -> decomp_2c_shares_Cu/arm_fixboth.
- CU-fixpv session_01U1xpEbCvGSe8cNQaX8rrY9: SHARES_P0=0.9444 SHARES_HOLD_PRICE=1 ... fixpv (price held at the mean
  of the gated run's three-pass cycle, which the drift rule could never leave) -> arm_fixpv.
- CU-fixp session_01HN6Xax8qgdXyBtSBnyEikG: SHARES_HOLD_PV=1 SHARES_V0=0.0924 ... fixp. NO PI_V BALANCES THIS
  COLUMN: drug use jumps from -48 to -42 percent as pi_V crosses ~0.0930, the budget misses by 1-2 percent either
  side, so a damped step cannot settle it; pi_V held where the gated run came closest (0.0924, gap 5.7e-3), reported
  with its budget gap. Old S-fixp session_018ixGRpLBP7wDvWBSME5pmF ARCHIVED (author's yes).
- TR50Cu session_01S2FhWe1HANhWtUimJa3Xdz: transition_fix/remote_tr50_Cu.sh (Housing First on cf_fix2_share_treatCu,
  terminal = the corrected main column, REL_TOL 5e-3) -> transition_2c_t50_Cu, transition_2c_Cu. The old TR50 fails
  its own 1e-3 check by itself.
- NISHCu session_019UuJRLfh3DFA7qTAsLqqfZ: omega_nishiyama/remote_nish_nodes_Cu.sh (this economy's Housing First
  re-solved on the corrected build, detection 0.20) -> omega_nishiyama_Cu.
- NOEXTCu session_01Y88f2Kqz9kxZ3ox8PtS8sE (engineering + run): the no-externality economy with Arm A on an ungated
  build, NET_A from it, Arms B, D, C, E -> pe_noext_Cu, noext_fixp_Cu, noext_clear_Cu, noext_pclear_Cu.
- Block 7's closing line generated from the street share (x_rv_street_close; the author: yes to changing it).
WHEN THEY LAND: rulec_paths.py DC[fixboth|fixpv|fixp] -> decomp_2c_shares_Cu, PE/FX/NC/NE -> the _Cu folders, drop
STALE_SHARES entries; export_nish_parts.py / export_results.py's nish paths -> omega_nishiyama_Cu; the transition
exporters -> transition_2c_t50_Cu / transition_2c_Cu. The old S-fixpv (gated, cycling) still runs: ask before archiving.

15:00 (14 Oct) ROUND r321 (the author's annotated PDF, 18 comments; "remove all red and crossed lines and put updates in
red"; "look at sentences that no longer make sense given the new results"). Whole source and tables stripped at the
author's explicit request; calib_tables and export_longrun baselines frozen; number baseline sec2/base_r321 = HEAD's
jsons; splice_r321 = splice_r320 on base_r321; scratchpad r321/build.sh (track_changes against r321/src_old.tex, a hook
that strikes the intro's deterrence sentence by hand and keeps x_trf_h_sr from reading as a replacement).
- Beauregard et al. removed (paragraph, Table 4 rows, reference): "not directly testable with my model" (68% of their
  homeless have a SUD against the 21.7% target). Block 7's closing line removed. Footnote on the ninth column moved
  into 6.2's text. "Lastly..." deterrence sentence removed from the intro.
- New generated sentences (export_longrun.py): x_abs_hchild_sentence, x_intro_ext_sentence, x_dcb_ext_sentence
  ("no trade-off in the aggregate, though there can be one for an individual child"), x_disc_cheaper.
- New footnote (intro, main result): the run in which households with a SUD cannot respond (CA,
  export_ca.py -> x_ca_*), yellow until CA meets its tolerances; the newborn's gain there is from the run's own print.
- Transition sentences (abstract, intro, 6.2, Discussion) yellow and noted: still rule A's until TR50Cu lands.
- Open with the author: Block 7's 2.2 pp (under rule C almost no one with SMI is put on the street, 1.4e-7 of the
  mass, and 96% of those leave it within a year, so it is not like-for-like with Costantini's three years); Milby's
  model numbers come from the transition's first year (TR50Cu).
- 14:30 the author: "remove all the crossed lines". Every \del removed from the r321 source (red \new and green \why
  kept), rebuilt with splice_r321 directly (no track_changes rerun); the struck version is r321/src_with_strikes.tex in
  the scratchpad and in commit 8e841632. Whether strikes stop for good (as after r120) is asked, not assumed.

15:20 (14 Oct) ROUND r322 (6 comments; "remove all crossed lines and red and put updates in red. you can remove all the
green stuff that is not relevant anymore. just keep yellow for portions that need to be adjusted once the results
arrive"). Whole source and tables stripped, baselines frozen, base_r322 = HEAD's jsons, splice_r322. No strikes this
round (the author asked twice to remove crossed lines; scratchpad r322/drop_del.py after track_changes and the splice)
and no green notes. Section 6.4 is yellow paragraph by paragraph (\soulregister{\ref}{7} lets \ref sit inside \hl), as
is 6.2's transition sentence. The footnote on the run where households with a SUD cannot respond moved from the
introduction to 6.2, beside the treatment take-up sentence; "in the long run" out of it. Exporter wording: the intro's
no-trade-off sentence without the individual-child clause; 'still lose'; 'A cheaper drug narrows that loss but does not
reverse the conclusions.'; the Discussion's next sentence names the elasticity of the drug's supply; 6.2 "first five
columns". ETA given to the author: with-externality columns 18-20 UTC, no-externality and Nishiyama about midnight,
CA tomorrow morning, T=50 first loop 21-23 UTC and converged tomorrow evening.

15:45 (14 Oct) ROUND r323 (3 comments; "remove all red and put updates in red"). Stripped and frozen as before, base_r323,
splice_r323, scratchpad r323/build.sh (r322's, no strikes). Table 3 gains c_treat (calib_tables.py reads
public_cost_of_treatment from patch_treatC2.py; data cell the $9,426 of lit ctreat_usd), so n_main is twenty-six. The
Discussion's elasticity sentence removed. The third lesson's two design paragraphs are yellow: the author, "these
lessons are not so correct anymore! we will need to think of new ones" -- candidates proposed in chat, not written.

14:00-15:30 (16 Oct) ROUND r324 (51 comments; "remove all red and put updates in red", "update all the numbers you can
based on our most recent results", "please update the transition figures to include the new T=50", push to main). The
container restarted overnight and the scratchpad went with it: the round splice is now code/paper/splice.py (in the
repo; whole-sentence red, no strikes), LaTeX and the Python packages were reinstalled. rulec_paths.py moves the three
decomposition columns and the four no-externality runs to their corrected (_Cu) runs once their files are in, and
clears STALE_SHARES; the omega_c = 0.686 check reads omega_nishiyama_Cu/cf; CA is accepted (pass 56). The transition is
pinned to rule C's T = 50, loop 3 (transition_source.py; the log staged, untracked, in code/trtf50): NOT CONVERGED
(worst budget residual 2.08e-2; pi_V in years 40-49 2.2 per cent below its terminal value and drifting further with each
loop, so T = 60 is the open question). Under rule C neither homelessness nor the share of children in a shelter rises
on the path; the cohort born at the reform gains 1.8 (long run 2.57). Section 6.4's (e)-(f) and (g) paragraphs and the
abstract, introduction and Discussion transition sentences rewritten for it. NEW RUN (the author's comment 34): detection
1.00 with the CA rule, long run then T = 50 transition, session_01HCs7CLwRjKRkfJPm7g5f4t -> results/counterfactuals_2c/
tf_pdet100_CAu and results/transition_2c_t50_CAu. The design lessons stay yellow until it lands.

15:00-16:00 (16 Oct) ROUND r325 (31 comments; "yes, run the comparison for block 7"; on 'fifty years': "I say do 70").
Two workers: session_014eQm4cqvV2NnMDFSRPoCNN, Block 7's revoked-voucher SMI x street split at detection 1.00 under the CA
rule against the corrected Housing First -> results/revoked_2c_CA100, results/revoked_2c_street_CA100 (point
export_revoked.py's STREET at it when its tables.md has the GUARD SUMMARY); session_013y8jvfsS8APQgy2mzy1vEj, the rule-C
T = 70 transition -> results/transition_2c_t70_Cu (re-pin transition_source.py to it when it lands). Fixed two exporters
still reading the gated runs: export_pe_noext.py (pe_noext_C: 'only 1 percent better off', newborns -1.15; corrected:
nobody better off, -1.17, as Table 5 says) and export_decomp_use.py (decomp_2c_shares_C/arm_fixboth). Block 8's
treatment shares are the long run's (78 against 24 percent, the main arm's MILBY SPLIT); the transition log has no split.
The entrants' path sentence now says what it measures (34 percent of entrants better off in year 1, 99 by year 49).

15:40 (16 Oct) THE AUTHOR ON THE DETECTION-1.00 TRANSITION: "you can do T=70 in that too". The worker
session_01HCs7CLwRjKRkfJPm7g5f4t cannot be messaged (cloud sessions are not reachable by SendMessage, and workers
ignore trigger prompts), and interrupting it now would lose the long run in its container. So: WHEN
results/counterfactuals_2c/tf_pdet100_CAu IS ACCEPTED, interrupt that worker (it will have started its T = 50,
results/transition_2c_t50_CAu, which is then dropped) and launch a FRESH worker that makes code/transition_fix/
remote_tr70_CAu.sh as a copy of remote_tr50_CAu.sh with the T = 70 changes remote_tr70_Cu.sh made to remote_tr50_Cu.sh
(build at T = 70, extend_seeds_C70.py, horizon_check_C70.py, report_tr70_Cu.py), and runs it ->
results/transition_2c_t70_CAu.

16:20 (16 Oct) ROUND r326 SWEEP (the author: numbers text against tables, long sentences and paragraphs, explanation
inconsistencies, "any sentences that can be improved and flow", every change marked). The four reviewer subagents were
killed by an interruption at 15:32 and could not be resumed, so the sweep was done by hand, section by section; every
edit is \new{}, every split paragraph opens with \parmark{}. Fixed: Table 7's note called Table 5's last column the
'eleventh' (it has ten columns of numbers; export_welfare.py); Section 6 wrote $\bar R$ for Section 4's
$\bar{\mathcal R}$; the delta_d item's 'Block 6 below' pointed at the drug-market block, not the validation's
transmission block; 6.3's 'the other 0.43 percent' read as if it contained the 0.19 the parent counts; the long-run
homelessness sentence (export_results.py) now gives the spending channel the author named in r325, as 6.4 does.
Flagged to the author, not changed: experiment 1 is described as two runs but 6.2 discusses three and Table 5 has four
(its fourth column, price clearing with pi_V held, is never discussed); experiment 2 is 'three steps' but has a fourth
column (the ninth); 'Block 7' and 'Block 8' name both validation blocks and appendix parameter blocks.

16:55 (16 Oct) ROUND r327 (13 comments, and "double check that all numbers throughout the paper are consistent with
the tables"). Red stripped, comments in red; the panel (h) legend moved to the empty upper right. The check of every
table against the text (Tables 1-2 of the stylized model, 5, 6, 7, the parameter table and Table A1): agreed except
Block 1's 55-and-over share (11.4 in the text, 10.7 + 0.8 = 11.5 in the table; calib_tables.py now sums the bands as
printed) and the SUD unemployment rate (16.25 in Section 3, 16.2 in Block 2 and Table 6; Section 3 now quotes u_unemp_d).

17:16 (16 Oct) SECOND DETECTION-1.00 RUN (the author: "yes, start a second worker. i want results faster"). The first
(tf_pdet100_CAu) walks the drug price down from 0.90 at the half-per-cent cap a loop; at price 0.874 its supply price
of the quantity demanded is 0.386, so with a supply elasticity of 1.46 and demand elasticities of 1 to 3 the market
clears near 0.55-0.67, some seventy loops away. session_014GGaH2BLE1DWy6kpPHYLXG runs code/pdet/remote_pdet_CAuB.sh
(a copy differing only in the arm name) with P0_START=0.62 V0_START=0.12 -> results/counterfactuals_2c/
tf_pdet100_CAuB. Whichever is ACCEPTED first is the result; the T = 70 transition (15:40 entry) starts from it.

17:50 (16 Oct) THE TWO FOOTNOTE RUNS RE-SOLVED AGAINST THE CORRECTED TARGET (the author: "ok...lets see what we get").
tf_pdet20_CA (the no-escape footnote) and tf_pdet10_C (the half-rate footnote) cleared the budget against 5.8275447063,
the gated Housing First's net revenue; the main arm clears against 5.8371628. And tf_pdet20_CA/tf has no cf.log or
final.txt, so the footnote's yellow newborn clause cannot be computed from it. Two workers, warm-started at each run's
last pass: remote_pdet_CAu.sh 0.20 (P0_START=0.9048 V0_START=0.0876) -> results/counterfactuals_2c/tf_pdet20_CAu, and
remote_pdet_C2u.sh 0.10 (a copy of remote_pdet_C2.sh at the corrected target; P0_START=0.9651 V0_START=0.07511) ->
results/counterfactuals_2c/tf_pdet10_Cu. When they land: point export_ca.py at tf_pdet20_CAu and fill the newborn
clause from its cf.log as export_results.py does the half rate's; point rulec_paths.TF_HALF_DIR at tf_pdet10_Cu/tf.
17:40 (16 Oct) DETECTION 0.05 (the author: "you can also try 5% detectino", "ie, 5% detection and allow those with SUD
in treatment and sober to retain vouchers", i.e. rule C, the main arm's rule). session_01QE7vbErj5eKqKgP9tB8VWF:
P0_START=0.982 V0_START=0.0713 bash code/pdet/remote_pdet_C2u.sh 0.05 -> results/counterfactuals_2c/tf_pdet05_Cu.

19:40 (16 Oct) CHECK-IN. The two detection-1.00 runs bracket the clearing price: supply price of the quantity demanded
0.55 at 0.8435 (CAu, pass 14), 1.70 at 0.626 (CAuB, pass 2); the log interpolation crosses at 0.77-0.78. CAu needs ~17
more half-per-cent loops (about 01:00-02:00 UTC), CAuB ~40 (it is now only a cross-check). A third start at 0.777,
pi_V 0.116: code/pdet/remote_pdet_CAuC.sh -> results/counterfactuals_2c/tf_pdet100_CAuC. Block 7: arms done, the T = 10
Treatment First path running since 18:31, street waiting. tf_pdet10_Cu pass 2 (gaps 6.6e-3, 3.8e-2), tf_pdet05_Cu pass
1, tf_pdet20_CAu restarted 19:13 from its own pass (0.9033, 0.0888). T = 70: long-run arm ACCEPTED 17:24, terminal arm
re-solving (pass 2 at 19:24).

21:25 (16 Oct) THE DETECTION-1.00 TRANSITION AT T = 70, READY (the author: "We would need to run a transition to make that
statement for the conclusion", on homelessness rising along it). transition_fix/remote_tr70_CAu.sh, a copy of
remote_tr50_CAu.sh at T = 70 (build_tr70_CA.sh, rescale_seeds_CA70.py, results/transition_2c_t70_CAu, MAX_LOOPS 4). It
polls the branch for the long-run arm's acceptance and starts the terminal arm from its latest pass meanwhile, so it is
launched now with C1R_OVERRIDE=results/counterfactuals_2c/tf_pdet100_CAuC. If CAuC fails and CAu is accepted first,
relaunch with C1R_OVERRIDE pointing there.

23:58 (16 Oct) THE BEST PASS (the author: "yes, take the best pass and start the transition"). Neither detection-1.00 run
settles: near 0.80 drug use jumps between -57 and -63 per cent for a 0.1 per cent price move, and the drug-market gap
alternates between 1e-2 and 8e-2. results/counterfactuals_2c/tf_pdet100_CAbest is tf_pdet100_CAuC's pass 7 (price
0.8017, pi_V 0.10240, drug gap 9.64e-3, budget 5.86e-4; drug use -56.6, SUD -56.9, homelessness -26.2 per cent).
transition_fix/remote_tr70_CAb.sh (a copy of remote_tr70_CAu.sh) holds the terminal price there (DRUG_MARKET_ADJUSTER=0),
re-clears pi_V, accepts within 5 per cent of the best pass, and runs T = 70 -> results/transition_2c_t70_CAb. The
waiting T = 70 worker (session_019NDD7S6oXV1WdF9SiLo1p3, transition_2c_t70_CAu) is superseded.
BLOCK 7: results/revoked_2c_CA100/tables.md is analyse.py's traceback (ZeroDivisionError: a revoked cohort of zero
starting mass, since at detection 1.00 every user is revoked in the first year); the street stage is running.

03:40 (17 Oct) BLOCK 7 AT DETECTION 1.00 LANDED (results/revoked_2c_street_CA100, GUARD SUMMARY PASS). Households with SMI
the revocation puts on the street, 6.4 percent of the revoked (against almost none at 0.20 under rule C): three-year
mortality 10.20 against 6.62 percent with the voucher kept, a gap of 3.6 percentage points against Costantini's 4.6 (it
was 2.2 at 0.20). export_revoked.py's STREET points at it; Block 7's yellow removed, the setting stated in red in the
paragraph and in Table 6's note b. revoked_2c_CA100/tables.md (the unsplit analysis) is a traceback (empty cohorts at
1.00); the paper does not read it.

03:45 (17 Oct) THE BEST-PASS TRANSITION'S TERMINAL ARM WAS RESTARTED BY ITS OWN CHECK. remote_tr70_CAb.sh started the
terminal arm at 00:08, then at 02:05 found its pi_V (0.1071) more than 2 per cent from the best pass's (0.1024) and
killed it to re-solve from scratch; when the re-solve ends it GUARDs out unless drug use, the SUD and homelessness are
also within 5 per cent of the best pass, and at the held price drug use lands on either -55 or -62 per cent. Hedge:
transition_fix/remote_tr70_CAb2.sh (REL_TOL 1, results/transition_2c_t70_CAb2) in a second worker. The first to reach
its path is the result. tf_pdet100_CAu ended NOT accepted (exit 143, killed); its worker session_01HCs7CLwRjKRkfJPm7g5f4t
and the drifting CAuB worker session_014GGaH2BLE1DWy6kpPHYLXG interrupted.

07:30 (17 Oct) THE NO-ESCAPE TRANSITION'S PATH IS RUNNING. remote_tr70_CAb.sh GUARDed at 06:32 on the 5-per-cent check
(1.75e-1: its held-price terminal arm cleared on the -64 per cent drug-use branch, pi_V 0.1089, homelessness -30.4 per
cent); a trigger message asked its worker to continue with REL_TOL=1 and it did: T = 70 staged and started 07:22. The
hedge (CAb2), which had also killed its early arm at 06:32, was interrupted. tf_pdet05_Cu ACCEPTED 06:38: drug use -8.9,
SUD -8.2, homelessness -3.6 per cent against the corrected Housing First, pi_V 7.14 per cent, newborn CEV +1.01.

14:20 (17 Oct) THE CONCLUSION WRITTEN (the author: "I think then you can write the conclusion"). Discussion lessons 2 and
3 rewritten in red, out of yellow. Lesson 2: how strict the condition is decides whether its costs come first; the
strict rule (detection 1.00, no exemption for treatment) does more in the long run (drug use -64, homelessness -30, newborn
+11.33 against +2.57) but, before its savings are recycled (Block 7's ten-year paths, price and pi_V held), homelessness
rises by up to 15 and children in a shelter by up to 12 percent, still +11 and +6 in year 9. Lesson 3b: under the
order's rule 66 percent of those with a SUD are worse off in year 1; under the strict rule 28 percent of the revoked are
homeless in each of years 1-3, against none with the voucher kept. Names from code/paper/export_noescape.py (x_ne_*).
OPEN: the full no-escape transition (results/transition_2c_t70_CAb, savings recycled) has not landed; when it does, check
whether homelessness still rises with the savings recycled and say so in lesson 2.

14:40 (17 Oct) DETECTION 0.20 WITH NO ESCAPE ALONG THE TRANSITION (the author: "I want to launch both because I want to see
if homelessness rises with 20% detection and no escape"). Two workers:
 (a) code/revoked_2c/run_all_CA20.sh: Block 7's pipeline at 0.20 (copies of the *_CA100 scripts, every name CA20) ->
     results/revoked_2c_CA20, revoked_2c_street_CA20; its tf10/hf10 paths give homelessness and children in a shelter
     year by year with the price and pi_V held, as export_noescape.py reads the 1.00 ones. About 12 hours.
 (b) code/transition_fix/remote_tr70_CA20b.sh: T = 70 from results/counterfactuals_2c/tf_pdet20_CAbest (tf_pdet20_CAu's
     pass 13, inside both tolerances), price held there, pi_V clearing, REL_TOL 1, the early arm no longer killed for
     drifting -> results/transition_2c_t70_CA20b. A loop takes about 15-20 hours.

14:50 (17 Oct) NO ESCAPE AT 0.10 AND 0.05, LONG RUN AND T = 70 (the author: "Also do transition for 5% no escape and 10%
no escape"). Four workers: pdet/remote_pdet_CAu.sh 0.10 (P0_START=0.935 V0_START=0.080) -> tf_pdet10_CAu, and 0.05
(P0_START=0.962 V0_START=0.075) -> tf_pdet05_CAu, the warm starts between Housing First and the 0.20 no-escape solution;
transition_fix/remote_tr70_CA10u.sh and remote_tr70_CA05u.sh (copies of remote_tr70_CAu.sh; TF_EARLY=1) poll for those
arms' acceptance -> results/transition_2c_t70_CA10u, CA05u. If a long run sits on a knife-edge, take its best pass as for
0.20 and 1.00.

17:50 (17 Oct) ROUND r333 (11 comments; "even if there is no escape, low detection lowers homelessness even in the short
run. it is when there is no escape and detection is too good that it rises in the short run"; "a policymaker who wants
to avoid raising homelessness and childhood homelessness should do imperfect enforcement but it needs to deter enough").
Red cleared. Removed: the introduction's strictness paragraph, Block 7's and Table 6 note b's detection clause, the
framing sentence, lesson 3 (two lessons now). Lesson 2 rewritten to the author's point and a last paragraph of 6.4 added
(no escape: catching every user against catching 20 percent), both YELLOW until the 0.20 no-escape transition (and the
screen-only 0.20 paths) confirm the short run, and the 1.00 full transition says whether recycling removes the early
rise. x_ne_hchild_pc (children in a shelter, 1.00 long run, -31) added to export_noescape.py. fix_soul.py now unwraps a
\new nested in a \new inside \tocheck. Pending: comment 3 (the 0.20 no-escape newborn CEV, from
results/transition_2c_t70_CA20b/arms/arm_tf when its terminal arm lands; re-point export_ca.py there too), comment 4 (the
transition figures to T = 70: re-pin transition_source.py to results/transition_2c_t70_Cu loop0 when archived, ~23:00).

18:00 (17 Oct) ROUND r334 (9 comments; "why didnt you update the transition figures? Dont we have some initial T=70
results?!"). Red cleared, comments in red. THE FULL 1.00 NO-ESCAPE TRANSITION (partial loop-0 log the CAb worker
published at the author's request, 19 years): with the savings recycled homelessness still rises, +14 per cent in years
2-3, above Housing First until year 14; children in a shelter +11 per cent, above until year 11; pi_V only 6.9-8.4 per
cent in years 2-19 against 10.9 in the long run. 6.4's closing paragraph now quotes these (x_ne_tr_* from
export_noescape.py: the latest archived loop of transition_2c_t70_CAb, else the partial log). The 0.20 rule's children
in a shelter (x_ne20_hchild_pc) is '--' until results/transition_2c_t70_CA20b/arms lands. The rule-C T = 70 worker asked
at 17:48 to publish its partial loop-0 log (37 of 69 years done) for a preview of the transition figure; the paper's
figure is re-pinned when loop 0 is archived (~23:00).

## 17 October, 21:45 -- the no-escape transitions held the drug price along the whole path

The author: "the transition result has to allow pv and piv to clear in each period", "the point is about the real
transition with no escape, 20% detection, vs 100%". remote_tr70_CAb.sh (1.00) and remote_tr70_CA20b.sh (0.20) solve the
terminal arm with the price held at the best pass (DRUG_MARKET_ADJUSTER=0, approved 16 October), and stage_tr_fix.sh
copies the arm's PARAM_HANDOVER into the transition, so the PATH ran with drug_market_adjuster 0 too: the CAb log reads
"HANDOVER drug_market_adjuster: 0.2 -> 0.0" and TRANSITION DRUG distance 0 at every t, the price at its seed in every
loop. pi_V is updated loop by loop, and loop 0 is the seed: budget residual (absolute, net revenue less the target 5.837) +0.009 to +0.010 in
years 2-4 (0.16-0.17 per cent of the target, a surplus a clearing pi_V would spend on vouchers), -0.054 by year 19
(0.9 per cent), 0.086 at worst (1.5 per cent). So x_ne_tr_* (the 14/11
per cent rise, 14/11 years) and "pi_V rises only as the savings accrue" in 6.4's yellow paragraph are NOT a cleared
result. The screen-only paths (results/revoked_2c_CA*) hold both prices by design and are a diagnostic only.
Fix: code/transition_fix/remote_tr70_CAc.sh and remote_tr70_CA20c.sh (made by a script from remote_tr70_CA20b.sh): the
terminal arm is still the best pass, the handover the path reads is reset to drug_market_adjuster 0.1 (the arms' default,
what the rule-C transition runs with) with a GUARD that the binary read it, MAX_LOOPS 6. Each runs in its predecessor's
container, stops it, marks its transition finished so a re-attach cannot restart it, and reuses its builds and arms
(CA20c adopts the terminal arm still solving). The yellow stays until these clear.

21:35: within a loop both prices sit at their seeds and are updated only at its end, so the held-price CAb's loop 0 is
exactly the loop 0 remote_tr70_CAc.sh would solve. CAc (regenerated) therefore waits for CAb's loop 0 to save its paths
(year ~50 of 70 at 21:20, about 01:00 UTC), keeps them as its seeds, and stops CAb only then; its loops archive as loop1
on. The CAb switch-over request was disabled before it fired; CA20b was switched at 21:24 (its path had not started).

## 17 October, 22:00 -- audit: do the long runs the paper reads clear both markets?

The author: "double check that the long run runs allowed the prices to clear". Every cf.log.gz the exporters read, last
pass, against the solver's rules (drug market 5e-3, budget 1e-3) and the drug_market_adjuster the run read
(scratchpad audit.py; the implied supply price where the price is held):
* CLEAR, as they should: the main rule-C arm (decomp_2c_shares_Cu/arm_tf/tf: drug 7.9e-4, budget 8.2e-4) and its
  Housing First; no externalities, arm_C (both clear) and arm_D/arm_E (the one that clears does); the 0.05 rule-C run;
  the Nishiyama arms; the rule-C T = 70 terminal arm; the 0.20 no-escape best pass (tf_pdet20_CAbest).
* HELD BY DESIGN, labelled in Table 5: 'Both held' (both columns); the price in 'pi_V clears'; pi_V in 'Price clears'.
  With externalities 'Price clears' holds the price at 0.9444 (the gated cycle's mean), but the implied supply price
  there is 0.9450: the market clears to 6.7e-4, inside 5e-3.
* NOT CLEARED: (1) the 1.00 no-escape long run. No pass of tf_pdet100_CAu, CAuB or CAuC cleared the drug market (85
  passes alternating between drug use -56 and -63 per cent at a price near 0.80, gaps 1.4e-2 to 6e-2), and the terminal
  arm the paper and the transition read (price held at 0.8017, pi_V cleared to 0.1089) has an implied supply price of
  0.7219, a 10 per cent gap: x_ne_* is not an equilibrium. (2) Table 5's 'pi_V clears' with externalities: no pi_V
  balances that budget (14 October: drug use jumps -48 to -42 as pi_V crosses ~0.0930); held at 0.0924 the corrected
  run's net revenue is 5.8501 against 5.8372, a 2.2e-3 surplus against the 1e-3 rule.
* OLD BUDGET TARGET (net_govt_revenue_constraint 5.8275 against the corrected 5.8372): tf_pdet20_CA, the footnote's
  no-escape run (export_ca.py now reads tf_pdet20_CAbest against the corrected Housing First: 30/30/11, was 30/30/12),
  and tf_pdet10_C, the half rate (tf_pdet10_Cu is re-solving it).

## 18 October, 10:40 -- Table 5's eighth column has no balancing pi_V in the corrected model either

results/decomp_2c_fixp_clear (pi_V free, price held at Housing First's, 15 passes, stopped 10:27): NOT CLEARED. Drug use
flips between -48 and -42 per cent as pi_V crosses about 0.093 (0.0928 -> 0.0931), and the budget misses on both sides
(gaps 7.9e-3 to 2.2e-2, one early pass 1.5e-3 at pi_V 0.09354 before the distribution settled). The table note now says
so, generated (x_dcp_jump_piv, x_dc_p_rev_pc from the column's final.txt, 0.22 per cent at pi_V 0.0924). The column is
re-solved with pi_V held at 0.09354 and the price at the corrected Housing First's (remote_decomp_shares_Cu3.sh fixp,
session_01BmNrng1jocAzG4s8PDKi1h -> results/decomp_2c_shares_Cu3/arm_fixp); rulec_paths prefers Cu3 once it lands, and
the note's miss then reads that run.

## 18 October, 13:05 -- the 20% no-escape path from the cleared long run; the price-held hedge stopped

The author asked why no transition had initial results, then "yes, do both" to (1) stopping the two dead runs and (2)
starting the 20% no-escape path now. (1) The 1.00 hedge (remote_tr70_CAb2.sh, price held along the path,
session_01EKUpZvtXQ5jXkT2MgpB481) is ARCHIVED; its loop 0 stays in results/transition_2c_t70_CAb2/loop0. The first 1.00
transition (remote_tr70_CAu.sh, session_019NDD7S6oXV1WdF9SiLo1p3, waiting for tf_pdet100_CAuC, which will never be
accepted) could not be archived: the classifier refused it (Interfere With Workloads), so the author has to. It is idle.
(2) remote_tr70_CA20d.sh's free-price terminal re-solve had swung around the tolerances for 16 passes (drug 4e-3 to
5.5e-3, budget 9e-4 to 3e-3) at price 0.9051-0.9056, pi_V 0.0861 against the accepted 0.90564, 0.08592.
remote_tr70_CA20e.sh (session_01Bw4Fphs8xT328eABnBuUCm, a fresh container) is remote_tr70_CA20c.sh with the long-run
arm set to the accepted tf_pdet20_CAu: the terminal arm holds the price at 0.90563748 while pi_V clears, and the path
clears both prices (handover reset to drug_market_adjuster 0.1, GUARDed). CA20d keeps running. BEFORE ANY NUMBER
READS CA20e: check its terminal arm's implied supply price (as the 17 October audit did; CA20b's held arm at 0.9044 was
rejected for a 7.4e-3 drug gap). export_noescape.py still reads CA20d's arms.

The yellow passages (footnote 966, 6.4's closing paragraph 1062, the third lesson 1076) all wait on these paths: the
footnote on a 20% end state (CA20e's arms, ~6-8 hours, or CA20d's), the other two on the 20% and 1.00 paths' first
pass in which the prices move (CAc's second pass ~11:00 UTC 19 October; CA20e's ~2 days after its arms).

## 18 October, 15:45 -- the delta_d checks on the current model

The author: "can you add in the lit review a footnote saying that even if we use delta_d=0 and half, the qualitative
results continue to hold?", then "please do these checks then for the long run" and "you have to solve the benchmark for
each first, and then the long run". No such run existed on the current model (results/deltad/dd0* are 12 October, on
the earlier rule, and never finished there). code/deltad/remote_deltad_Cu.sh <dd> (made from remote_deltad.sh by
$SP/r352/make_deltad_Cu.py): STAGE A the benchmark with penalty_child_addicted <dd>, every adjuster frozen, omega_c
pinned; B corrected Housing First (cf_fix2_share_treatCu) against it, its net revenue the target; C Treatment First,
rule C, detection 0.20, both prices clearing; D newborn values (cf_kid_C). Workers: dd0 session_01XNEE6rjB72r98hfsDqPK2z,
dd0.12 session_01FjCM1uyiPJg2pphFSAYcGn; results/deltad_Cu/dd{0,0.12}. The footnote (Section 2, end of the Nilsson
paragraph) is in yellow until both show Treatment First still raising a newborn's welfare and lowering homelessness and
the share of children in a shelter against their own Housing First.

## 18 October, 18:30 -- Table 5's eighth column at the corrected held price lands on the other side of the jump

results/decomp_2c_shares_Cu4/arm_fixp (pi_V held at 0.0924, the drug price held at the corrected Housing First's
0.99938969) is in, and rulec_paths reads it. At the same pi_V as the paper's column, the 0.07 per cent lower held
price puts the economy on the other side of the jump in drug use: drug use -41.8 per cent (was -47.8), homelessness
-20.4 (-21.1), children in a shelter -19 (-20), net revenue -0.29 per cent of the benchmark's (was +0.22), a newborn's
gain 6.45 (6.98), the externality two thirds of it (three quarters), the parents 2.42 (2.41). The column is consistent
with the text now ("the drug price held at its Housing First level"). 6.2's "because drug use falls by more and the
higher pi_V houses more children" became "because the higher pi_V houses more children" (drug use now falls about as
much as with both held, which x_dcp_why says). Still open for the author: the Table 5 note's "when it clears, pi_V
holds net government revenue at its benchmark level" overstates this column (0.29 per cent off).

## 18 October, 23:00 -- footnote 36's yellow cleared

results/transition_2c_t70_CA20e/arms landed (terminal arm at the accepted price 0.9056 held, pi_V re-cleared to 0.0864,
budget 9.0e-4). Its implied supply price, p_null (V_tf/V_null)^(1/eps_s) with eps_s 1.46 (checked against the solver's
own distance on two free-price runs: 5.0e-5 against 5.3e-5, 7.1e-4 against 7.9e-4), is 0.9006: a drug gap of 5.0e-3, AT
the rule. The footnote's numbers therefore come from the cleared long run itself, tf_pdet20_CAu, against the corrected
Housing First, as its other numbers already did: newborn CEV 4.45 (welfare_nok.cev_free, the main arm's 2.57 the same
way), so 'a newborn gains at least as much' holds and is now x_ca_nb_clause (export_ca.py); children in a shelter 1.03
-> 0.91, -11 (x_ne20_hchild_pc, export_noescape.py, which no longer waits for CA20d). The held-price arm gives 4.63 and
-11.6. CA20e's path runs from that terminal arm; whether its 5.0e-3 drug gap matters for the path is a question for its
first archived pass.

## 19 October, 00:10 -- the delta_d = 0 check is in; the Section 2 footnote's yellow cleared

results/deltad_Cu/dd0 (benchmark re-solved at delta_d 0, 11 blocks; Housing First accepted, drug gap 7.5e-4; Treatment
First accepted in 4 passes, drug 1.9e-3, budget 9.5e-5), against its own Housing First: drug use -20.8, SUD -19.5,
homelessness -4.3, children in a shelter 1.00 -> 0.95 (-4.7), pi_V +1.4 (not +16), newborn CEV +0.31 on its own
benchmark curve (+0.33 on the paper's), against 2.57. The author: "You can just say that welfare gains continue to arise.
No need for exact numbers. You can skip the deltad=0.12 since we already know deltad=0 gives a gain", at the first place
in Section 2 that calls the penalty conservative: the footnote now reads "Welfare gains from Treatment First continue to
arise even when the penalty is set to zero." (red, yellow cleared). dd0.12 (session_014gxR6UdgHXeDkzy62Su3DY) is left to
finish on its own and is not used. Told the author: footnote 27's "only 18 percent of the welfare gain" understates what
switching the penalty off does in general equilibrium (the gain falls by about 88 per cent, mostly through pi_V); they did
not ask for it to change.

## 19 October, 01:30 -- the no-escape reform phased in: announced, and with grace years

The author: "assume those with SUD cannot stop using", "whether 100% or 20% can result in decrease in homelessness in
short run", "Consider HF but with announcement about TF to happen in 5 years. And consider another case in which
treatment alone is exempted even if there is drug use, but only in the first 5 years". Four fresh workers, each
code/transition_fix/remote_tr70_CAann.sh <1.00|0.20> <announce|grace> (a copy of remote_tr70_CA20e.sh for a fresh
container; same arms, same terminal, both prices clearing every year, MAX_LOOPS 6):
 * announce (patch_announce.py, code/tr70_CAann): the screen OFF in years 1-5 and rule CA from year 6, known from year 1.
   Two fixes the per-year switch needs: the lottery is zeroed before every rebuild (build_voucher_probabilities never
   clears the screen's rows, so year 5 would have kept year 6's revocation row beside a stay row of 1), and the
   own-treatment fix is ungated as the corrected Housing First runs it (tr70_CA gates it on the screen, which was on in
   every year of the main paths). Seeds: the main path shifted 5 years, Housing First's price and pi_V before.
 * grace (patch_grace.py, code/tr70_CAgrace): the screen on from year 1; in years 1-5 a household in treatment passes
   whatever it uses (only one with a SUD can choose treatment); rule CA from year 6. Seeds: the main path unshifted.
 Both print the year's rule (TRANSITION ANNOUNCE / TRANSITION GRACE) and the launcher kills the run if it is not the one
 asked for. Results to results/transition_2c_t70_CA{ann,grace}{100,20}; report_tr70_CAann.py gives homelessness and
 children in a shelter for 25 years against Housing First. Timing: builds and the two arms ~8 hours, then a loop ~a day;
 the first forward years land about 20-24 hours after launch.

01:10 (19 Oct) ROUND r353 (2 comments; "remove all yellow and red and put updates in red"). Red and yellow cleared (the
6.4 no-escape paragraph and the third lesson out of \tocheck). Comment 1, "Need to fix this" on "catching 20 percent ...
lowers them even along the transition": the 0.20 screen-only paths (results/revoked_2c_CA20, price and pi_V held) raise
homelessness by up to 6 and children in a shelter by up to 4 percent, so the sentence now says the 0.20 rule also raises
them at first, though by less (x_ne20_so_* and x_ne20_so_cmp in export_noescape.py, the direction against the 1.00
transition's 14/11); replace with the 0.20 transition (transition_2c_t70_CA20e) when it lands. Comment 2: "They still
fall" -> "However, they still fall".

01:30 (19 Oct) ROUND r354 (2 comments, both on the third lesson). Red cleared (base_r354). "fall from the start only if
... are a real option" -> "do not fall along the transition if ... are not a real option" (the author: "do not fall in
transition if", "are not a"); the next sentence, which repeated the condition ("When they are not, both rise ..."),
now reads "Both rise in the first years instead, because ...".
