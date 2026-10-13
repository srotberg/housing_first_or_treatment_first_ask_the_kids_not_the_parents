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
