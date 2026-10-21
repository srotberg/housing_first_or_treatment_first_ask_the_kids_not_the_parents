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

13:00 (19 Oct) THE HALF RATE RE-POINTED: tf_pdet10_Cu ACCEPTED at 11:00 (cleared against the corrected Housing First's
5.8372; tf_pdet10_C had cleared against the old 5.8275). rulec_paths.TF_HALF_DIR now reads it when it is in. Footnote
fn:halfrate moves in red: homelessness 7 -> 6 percent, the newborn's CEV 1.81 -> 1.65; drug use 14 unchanged.
THE ANNOUNCED 1.00 PATH'S LOOP 0 has a drug-market distance of 0.219 (price units: |implied supply price - price|)
somewhere in years 1-7, against 1.5e-2 on the main 1.00 path: the seed holds Housing First's price for years 1-5, and
the price moves at most 0.5 per cent a year a loop, so six loops cannot close a gap that size. When loop 0 is archived,
read the 'implied supply price=' lines by year; if the gap sits in years 1-5 (households cutting use before the screen
starts), re-seed the announced runs from loop 0's implied prices and relaunch.

16:00 (19 Oct) ROUND r356 (2 comments; the author: "make a new subsection called something like: alternative transition
specifications", "it should just explain what each experiment does and how the first years of the transition look like
on homelessness, childhood homelessness and newborn welfare", "the last paragraph of the conclusion should be in yellow
since we might change it"). New Section 6.5 (sec:alttrans), in red: what each alternative does, Table tab:alttrans, the
no-escape paragraph moved from the end of 6.4 (opening changed to "In the first alternative,"), and x_at_results (the
announced and grace sentences, yellow until both detection rates of a rule are in). code/paper/export_alttrans.py
(in export_all_C.sh after export_noescape.py) reads each run's latest archived loop: largest rise over years 1-15 of
homelessness and of children in a shelter, the years above Housing First, and the reform cohort's CEV (cohort_cev.py less
Housing First's cev_free; the main row's is x_tr_cev_b1_2). A row is yellow while its run has no archived loop or its
pass misses the budget by more than 0.6 per cent or the drug market (5e-3) in more than three years. The helpers path(),
child_steady() and levels() moved from export_noescape.py to code/paper/trpaths.py (its output unchanged). Section 6's
opening lists the alternatives (red); the third lesson is in yellow; page 1: "The author owns the code; he wrote ...".
When a phased run lands: bash code/paper/export_all_C.sh fills its row and sentence; rebuild with splice against the
round's base.

15:10 (19 Oct) ROUND r357 (17 comments on Section 6's opening and 6.5). Red cleared (base_r357); the third lesson stays
yellow. The alternatives sentence in Section 6's opening is its own paragraph, "from the day of the reform", periods for
years. 6.5: periods for years throughout its new text and Table tab:alttrans ("Periods above"), "look like", "only after
recovery can they stay sober and pass the screen", "or", "from day one of the reform", "even if it uses drugs", "the
Housing First benchmark", "(first row)", "Catching only one in five users" (x_at_pdet_words from x_tf_pdet_pc), the
third alternative renamed "sobriety while in treatment exempt for five periods" (table label and the generated
sentences), the table note on yellow cells removed.

15:45 (19 Oct) ROUND r358 (3 comments). Red and green cleared (base_r358). "from the day of the reform" -> "from the first
day of the reform" (Section 6's opening); the green note under Table tab:alttrans removed (the author: "remove"; no
note added for this round's table change); the third alternative "exempt for the first five periods" in the table
label, its note and the placeholder sentence.

16:15 (19 Oct) A HEDGE FOR THE 0.20 NO-ESCAPE PATH. results/transition_2c_t70_CA20e had been in its backward pass for 14
hours after its 01:47 restart (status alive every 20 minutes, no forward year), against 8.2 for CAgrace20 (same
terminal arm, same seeds) and 7.4-10 for the others. code/transition_fix/remote_tr70_CAne.sh (a copy of
remote_tr70_CAann.sh with no phase-in: tr70_CA from build_tr70_CA.sh, seeds unshifted, no schedule check; a NEW file, so
the four workers running remote_tr70_CAann.sh are untouched) runs it in a fresh container -> results/
transition_2c_t70_CAne20. export_alttrans.py reads it for the no-exemption 0.20 row while CA20e has no archived loop.

21:45 (19 Oct) THE ANNOUNCED 1.00 PATH'S LOOP 0 ARCHIVED (results/transition_2c_t70_CAann100/loop0). Homelessness against
Housing First: periods 1-6 below (-0.6 to -4.2 per cent, children -0.7 to -5.3), then a jump in period 7 (+5.7) to a peak
of +7.3 in period 9, above until period 16; children in a shelter peak +3.6 in period 9, above until 12. Against the
immediate no-escape path (CAb loop 0): +13.8 in period 2, above to 14; children +11.0, above to 11. Reform cohort's
CEV +4.94 (immediate: +7.27; main transition 1.50). NOT A REASONABLE PASS: the drug market's implied supply price in
periods 1-5 is 0.78-0.82 against the seeded 0.994 (households cut use as soon as the screen is announced), distance
0.18-0.22; 0.01-0.09 after. Proposed to the author: re-seed both announced runs from their loop-0 implied prices and
relaunch (about a day). Table tab:alttrans: periods above Housing First now printed as ranges, with changes under
0.05 per cent (period 1's +0.02) not counted.

23:40 (19 Oct) TWO MORE FIRST PASSES. CAc (1.00 no exemption, both prices clearing; loop 0): homelessness +13.6 in period
2, above Housing First to period 15; children +10.8, above to 11; reform cohort +6.74. It replaces CAb's held-price
loop 0 in x_ne_tr_* (export_noescape.py: x_ne_tr_h_yrs 14 -> 15, the rest unchanged) and in Table tab:alttrans
(x_at_ne_cev 7.27 -> 6.74). CAgrace20 (grace years at 0.20; loop 0): homelessness below Housing First in periods 2-8
(to -3.9 in period 6), +0.7 to +1.5 in periods 9-15 (peak period 11), below after; children in a shelter never above;
reform cohort +3.14; drug distances 0.005-0.037, budget 0.55 per cent.

02:30 (20 Oct) THE MAIN TRANSITION RE-PINNED TO RULE C T = 70 LOOP 1 (results/transition_2c_t70_Cu/loop1, archived 01:57;
the binary's loop 0 after the 01:50 relaunch on 19 October, one forward pass; staged at code/trtf70/tr2c_t70_Cu_loop1).
REASONABLE: worst budget residual 1.21e-2 (0.21 per cent), drug market inside 5e-3 in every year (worst 3.84e-3).
Moved in the text (red): the reform cohort's CEV 1.50 -> 1.45 (x_tr_cev_b1_2, also the main row of Table 7), adults
alive worse off 8 -> 11 and those with a SUD better off 34 -> 33, the first-year share of the fall in use 80 -> 81,
children in a shelter 0.99 -> 1.00 by year 10 and 0.92 -> 0.93 by year 69, homelessness 0.55 -> 0.56 by year 69,
parents using 13.59 -> 13.57 and above the long run until year 12 (11), pi_V in the first decade 6.78-6.95 ->
6.55-6.90, the price above its long run 34 -> 33 years, nine tenths of the SUD fall by year 27 (26), panel (h)'s
worse-off range 2-8 -> 2-11. ONE SENTENCE NO LONGER HELD: "Third, pi_V stays above its Housing First level of 6.75
percent throughout" -- loop 1's pi_V is 6.55, 6.64, 6.73 in years 1-3. It is now generated (x_trf_piv_reason,
transition_figure.py): "Third, after the first three years, when it is as low as 6.55 percent, pi_V stays above its
Housing First level of 6.75 percent, ...". Homelessness and children in a shelter still never rise (year 1 -0.001 per
cent, then falling), so "Neither rises at any point" and the introduction's claim stand.

02:45 (20 Oct) THE ANNOUNCED RUNS RE-SEEDED, AND THE FIRST SAFEGUARD (the author: "you can start the runs with better
guesses. sure. yes, you can restart the other safeguards too"). code/transition_fix/remote_tr70_CAann2.sh <rate> (a new
file; remote_tr70_CAann.sh untouched) in two fresh sessions -> results/transition_2c_t70_CAann2_100 and _CAann2_20. Seeds:
reseed_implied.py on the old run's latest archived loop (its updated paths; the drug price in periods 1-5 moved 0.6 of
the way to the implied supply price: at 1.00, 0.994 -> 0.867-0.888). Every 20 minutes progress_tr.py publishes
progress.txt: each forward period reached, homelessness and children in a shelter against Housing First, the drug
distance and pi_V. export_alttrans.py reads the re-seeded runs once they land. The old announced runs keep running.
The second safeguard (checkpoint the backward pass so a restart resumes the forward pass) is next, for later relaunches.

03:00 (20 Oct) THE PHASED-IN RESULTS IN THE PAPER (the author: "i think you can probably update the paper....the
exemption for 5 years while in treatment seems pretty good"). Section 6.5 now closes with two generated paragraphs
(export_alttrans.py, x_at_ann_par and x_at_gr_par, replacing the x_at_results placeholder), and the third lesson takes
one generated sentence in red and yellow after its yellow paragraph (x_at_lesson): "A temporary exemption keeps that
rise small: if a household in treatment keeps its voucher, sober or not, for the first five periods, and the screen
catches one in five users, the share of children in a shelter never rises above its Housing First level and
homelessness rises by at most 1.5 percent, while newborns still gain." Checked in the logs before writing: the
announced 1.00 run's drug use is 31 per cent below Housing First in period 1 (at a drug price that is too high), the
grace-years 0.20 run's treatment take-up is 36 per cent of those with a SUD in periods 1-5 against 25 under Housing First
(31 after). Numbers from passes that are not yet reasonable print yellow; runs still going print a yellow sentence.

03:00 (20 Oct) THE SECOND SAFEGUARD, BUILT, FOR THE NEXT RELAUNCH. The forward pass already writes the price and pi_V
paths every period (a relaunch starts from the latest paths); what a restart loses is the loop's backward pass (8-15
hours). code/transition_fix/patch_ckpt.py saves VF_CHECKPOINT.bin after each backward pass (the value-function path of
both tenures and the five paths it was solved under, sizes and a checksum, via a temporary file and a rename), restores
it at a relaunch's first loop and skips the backward pass (the forward pass re-solves each period's policies from the
value functions, as the source already relies on), and deletes it at each loop's end; prints TRANSITION CHECKPOINT
... restored= / SAVED / CLEARED. code/transition_fix/build_tr70_ckpt.sh [OUT] [LAG] [none|announce|grace] builds it on
top of the mode's source (default OUT code/tr70_CAck_<mode>); compiled -O0 locally without errors, all three modes pass
their guards. NOT IN THE RUNNING BINARIES (their launchers built before it; their scripts must not change under them).
To use it in a relaunch: copy the launcher, build with build_tr70_ckpt.sh instead of build_tr70_CAann.sh/build_tr70_CA.sh,
and before starting the binary after a killed run delete VF_CHECKPOINT.bin if the killed log ends in CHECKPOINT CORRUPT.
The run directory needs about 1 GB free for the file. First use: confirm 'restored= 1' and that the forward pass's first
period matches the killed log's.

03:17 (20 Oct) ROUND r360 (9 comments on 6.5 and the third lesson). Red cleared (base_r360); the third lesson stays
yellow. CAann20 (announced at 0.20) loop 0 landed and fills its row: homelessness +3.1 in period 12, above Housing First
in 7-19; children in a shelter +0.6 in period 11, above in 9-13; reform cohort +2.57 (not yet a reasonable pass: the
drug market misses in the announcement periods, as at 1.00). export_alttrans.py: "lowers the rise but does not
eliminate it"; the announced drug-use sentence says Housing First continues while the screen is only announced ("in
anticipation of a screen that will catch every user"); "but rises above it"; rises under one percent print one decimal.
Three generated explanations of the newborn's gains, each checked against the paths before it prints: (1) no
exemption gains more than the main transition because the share with a SUD falls faster (2.80 per cent by period ten at
1.00, against the main transition's x_trf_sud10 3.47) and pi_V is higher in every period of the cohort's childhood;
(6) the 0.20 exemption likewise (3.22 by period ten); (4) the announced 1.00 path gains less than the immediate one
because pi_V stays at Housing First's 6.75 per cent until the screen starts and drug use falls 31 rather than 40 per
cent in period 1 (the cohort's childhood part is two thirds of the gap: 0.246 of 0.369 utils). The third lesson goes
straight to the exemption (the author: "can remove this"): "A temporary exemption for those with a SUD keeps any rise
small: ..., with newborns gaining even more than in the main transition" (3.14 against 1.45).

03:28 (20 Oct) ROUND r361 (3 comments). Red cleared (base_r361); the third lesson stays yellow. (1) "why is the 2.57
higher than the main simulation?": the announced 0.20 path's newborn gain now has its reason, generated in
export_alttrans.py (why_more on the 0.20 path: 3.27 per cent with a SUD by period ten against 3.47; pi_V is not higher
in every childhood period there, so that clause does not print). (2) "how can it deter more when both cases have 20
percent detection rate?": the rule, not the rate -- in the main transition a household with a SUD keeps its voucher by
entering treatment and not using, here it cannot, so using drugs risks more (long-run drug use -30 per cent at 0.20
against -21). Said in full the first time (announced paragraph), referred to in the exemption paragraph; the first
alternative's sentence now names both differences (the rate and the rule). (3) The lesson: "keeps the latter from ever
rising and keeps the former's rise small" (the author's words).

03:36 (20 Oct) ROUND r362 (3 comments, and "i asked you before you remove all red and you didnt. please remove all
red and put only updates in red"). WHY THE RED STAYED: the splice marked a generated name that moved red AS A WHOLE, so
6.5's paragraphs and the third lesson (x_at_ne_cev, x_at_ann_par, x_at_gr_par, x_at_lesson; and the src wrapper
\new{\tocheck{@@x_at_lesson@@}}) printed entirely red whenever one clause changed. FIX: code/paper/splice.py diffs a
generated sentence (six words or more at brace depth 0, braces and $...$ kept whole) word by word against what it
printed in the base and wraps only the inserted or changed runs in \new{} (two black words or fewer between red runs
join them); a deletion leaves nothing red. writing/tools/fix_soul.py splits a yellow passage around a red run
(\tocheck{A }\new{\tocheck{v}}\tocheck{ B}) instead of printing it plain, so red shows inside the yellow third lesson,
and the lesson's src wrapper is plain \tocheck{@@x_at_lesson@@} again. Comments: the two reasons the author found
"makes no sense" (announced 0.20 and exemption 0.20 against the main transition) now say it from the households' side --
a household with a SUD cannot stop using, so the disorder puts its voucher at risk until it recovers, while in the
main transition it keeps the voucher by entering treatment and not using; starting to use risks more and fewer
households use drugs -- in full in the announced paragraph and in short in the exemption paragraph; the first
alternative's sentence says the same at 1.00 ("costs it its voucher"). The lesson: "keeps the latter from ever rising
and the former's rise small" (the second "keeps" removed).
In the same round, CAgrace100 (the exemption at 1.00; loop 0, archived 03:3x) landed: homelessness below Housing First in
periods 2-6, then +3.6 in period 7 to a peak of +4.2 in period 9, above until 13; children in a shelter at most +0.2
(periods 8-9); reform cohort +6.88 (no exemption at 1.00: +6.74); budget 0.98 per cent, drug market not yet clearing
(yellow). The exemption paragraph now states both rates in the same words (it printed "by up to 0 percent" for 0.22)
and gives the 1.00 newborn gain after the 0.20 one's reason.

03:45 (20 Oct) ALL RED REMOVED (the author: "remove all red"; base_r363, splice 0 red). The author asked how close the
yellow is to clearing. What is yellow: Table 7's six alternative rows (30 cells) and 20 passages in 6.5 that quote them,
plus the third lesson (yellow on the author's instruction). The drug-market gap by period of each latest pass (implied
supply price against the path's price): at 1.00 (CAc, CAann100, CAgrace100) periods 51-69 sit 8-10 per cent off,
because the terminal arm is the 1.00 best pass, which has no clearing price (16 Oct: drug use jumps between -56 and -63
per cent near 0.80; implied 0.72-0.73 against the held 0.7977-0.8017), so no number of loops turns those rows black under
the 5e-3 rule. At 0.20 the end state clears (0.5-1.9 per cent in periods 51-69) but the paths are 2-12 per cent off in
periods 1-30 (CAgrace20 0.4-3.9 per cent in 1-15, CAann20 10.6-12.4 in 1-5), and the price moves at most 0.5 per cent a
period per loop, a day a loop: about a week of loops unless re-seeded from the implied prices (reseed_implied.py, as the
announced runs were). Put to the author: the 1.00 decision and a re-seed of the 0.20 exemption run.

03:52 (20 Oct) THE TRIALS IN THE ABSTRACT AND THE INTRODUCTION (the author: "should i say something in the
intro/abstract about how i generate the micro evidence from trials but show that when accounting for the macro effects,
the conclusions change?", "something like the second lesson in the conclusion", then "go for it" to the proposed text).
Abstract, before its last sentence (122 -> 145 words): "As in trials, households with a disorder lose from sobriety
conditions, but counting those deterred from using, and the children, reverses the verdict." Introduction, a paragraph
after the long-run decomposition and before the transition: the model reproduces what the trials find for the
households they follow, and what changes the conclusion is what they do not observe (the second lesson's terms). Red.

03:58 (20 Oct) WHAT THE MODEL REPRODUCES FROM THE TRIALS, said exactly (the author: "it's not just that they lose. can
you explain exactly what the model reproduces for the trials?", then "sure" to the rewording). The evidence: Milby et
al. (2005) housing against no housing (targeted, mu_H); Milby's abstinence-contingent against non-contingent housing,
1.26, the model 1.40 in the condition's first year (Block 8, untargeted); Costantini (2025, not a trial), Housing First
lowers the three-year mortality of homeless veterans with mental illness by 4.6 points, losing a voucher raises it by
3.6 for households with SMI in the model (Block 7, untargeted); At Home / Chez Soi, SMI unaffected by housing (assumed).
Not compared: the main trials' housing-stability gains and mixed-to-null drug-use effects. The abstract sentence
("As in trials, households with a disorder lose from sobriety conditions", unsupported) is now "The model reproduces what
trials find for the households they follow; counting those deterred from using, the budget and the children changes the
verdict" (146 words); the introduction's paragraph names the three comparisons with their generated numbers; the second
lesson's first sentence likewise, and "Those with a SUD do lose from sobriety conditions, in the data and in the model"
is deleted (no trial measures it), with "Trials, however," -> "They". Red.

04:00 (20 Oct) TABLE 7 KEEPS THE 1.00 ROWS, WITH A NOTE (the author: "keep the 100% rows with a note, and restart the
20% run"). The note adds (red): "When every user is caught, no drug price clears the long-run drug market, because drug
use jumps as the price moves through the level that would clear it; those transitions end at the long-run solution that
comes closest." A 1.00 row is now judged on periods 1-25 only (WINDOW_100 in export_alttrans.py, trpaths.pass_quality's
last=): budget within 0.6 per cent and the drug market within 5e-3 in all but three of them. None passes yet (CAc 0.62
per cent and 21 periods off, CAann100 0.36 and 25, CAgrace100 0.91 and 22). THE NOTE'S RED: export_alttrans.py compares
the note sentence by sentence with code/paper/tab_alttrans_prev.json and prints a new one in \textcolor{red}; at the
next red strip run `python3 code/paper/export_alttrans.py --freeze` with calib_tables.py --freeze and export_longrun.py
--freeze, or the sentence stays red. The 20% exemption restart is being prepared in a background agent
(remote_tr70_CAgr2.sh, reseed_path.py).

04:02 (20 Oct) THE 0.20 EXEMPTION RUN RESTARTED FROM ITS IMPLIED PRICES (the author: "restart the 20% run").
code/transition_fix/remote_tr70_CAgr2.sh 0.20 (a copy of remote_tr70_CAann2.sh, MODE grace, built as remote_tr70_CAann.sh
grace builds it; remote_tr70_CAann2.sh untouched) in a fresh session, session_01TRiWgJkAReAo2cCbsxpuek ->
results/transition_2c_t70_CAgr2_20. It solves the two arms (~8 h), then re-seeds from results/transition_2c_t70_CAgrace20's
latest archived loop with code/transition_fix/reseed_path.py 1 69 0.6 9: pi_V its updated path, the drug price in every
period moved 0.6 of the way to the implied supply price, tapering to zero over periods 61-69 (on loop 0: t1 0.9404 ->
0.9432, t2 0.9437 -> 0.9412, t3 0.9428 -> 0.9390, t4 0.9430 -> 0.9350, t5 0.9423 -> 0.9324, t10 0.9372 -> 0.9215, t15
0.9302 -> 0.9105, t30 0.9057 -> 0.8936, t60 0.9050 -> 0.9014, t69 unchanged; largest move 2.4 per cent, period 14).
THE CHECKPOINT, first use: the launcher also builds code/tr70_CAgr2ck (build_tr70_ckpt.sh grace), accepted only if its
source is the plain one with lines added and the same patches' md5 (checked locally: 59 lines added, none changed), and
at staging uses it if the free disk is at least 6 GB (the value-function paths, 5.2-5.6 GB) + 4 margin + 4 for the swap
file, else the plain binary; the status says "checkpoint ON/OFF". On a relaunch it keeps VF_CHECKPOINT.bin in the run
directory, deletes it if the killed log ends in CHECKPOINT CORRUPT (and relaunches once if the binary stops on it), and
every TRANSITION CHECKPOINT line (restored=, SAVED, CLEARED) goes into the status. export_alttrans.py does not read the
run yet: point the 0.20 exemption row at it (fallback CAgrace20) once it archives a loop.

13:25 (20 Oct) ROUND r364 (5 comments). Red cleared (base_r364; export_alttrans.py --freeze with the other freezes).
(1) Abstract, shorter (the author: "something similar but shorter"): "The model reproduces trial evidence, and users with a
disorder lose, but effects on other households and children overturn the verdict." (143 words). (2) Introduction (the
author: "too detailed ... the model captures the micro effects on those with SUD, and they lose on average in the model
as well. But the macro effects on other households, vouchers and children overtake the micro effects"): the paragraph
now says that, with x_trf_alive_sud_worse_pc (67 per cent of those with a SUD when the reform lands are worse off; the
paper has no average CEV for that group, so "most", not "on average"), and ends "on children across the economy" (the
author's words for "the children's adult lives"). (3) Second lesson: after its evidence sentence, "As that evidence
implies, those with a SUD lose from Treatment First: 67 percent ... are worse off. The macro effects the trials do not
capture, however, overturn the conclusions." (replacing "Once the whole economy is taken into account, however, the
conclusions change."). (4) Table 7 and 6.5 (the author: "if you have initial numbers for the full table, put them all in
the table and paper, and remove the yellow (but keep the tab on your side ...)"): YELLOW_PROVISIONAL = False in
export_alttrans.py prints a provisional number plain; THE TAB is code/paper/alttrans_provisional.json (each row's source
loop, reasonable or not, budget gap, drug periods off), rewritten at every build. Only the 0.20 no-exemption row, which
has no archived pass, keeps yellow dashes. splice.word_red ignores a number that only lost its yellow (plain()), so the
provisional numbers did not turn red. The third lesson stays yellow (the author's earlier instruction); asked.

13:50 (20 Oct) ROUND r365 (6 comments). Red cleared (base_r365). Abstract: "micro evidence", "macro effects" (the author's
words; 144 words). Second lesson: "the micro evidence behind Housing First". The 67 per cent of those with a SUD at the
reform who are worse off (x_trf_alive_sud_worse_pc, prices clearing) now comes after the same share with the drug price
and pi_V HELD (the author: "you need to report how many of them lose when the pv and piv are constant!", "you may have
to simulate this transition", "that transition only needs one iteration"): x_trfix_sud_worse_pc, code/paper/
export_trfix.py (in export_all_C.sh), from results/transition_2c_t70_Cfix's 'TRANSITION BETTER OFF TOL t= 1' worse_sud,
the field transition_series.py reads for the 67; a yellow dash until that run archives its loop. The run (main
transition, rule C 0.20, prices held, one pass) is being launched by a background agent (remote_tr70_Cfix.sh). For
reference, the long-run held-price comparison (decomp fixboth, shares.txt): 96 per cent of households with a SUD worse
off -- a steady state, not those alive at the reform, so not quoted. The third lesson is no longer yellow (the author:
"remove this yellow and just leave in your notes that you have to double check this after all the simulations are
done"): THE NOTE is in code/paper/alttrans_provisional.json, '_to_check_when_all_runs_are_reasonable'.

13:40 (20 Oct) THE MAIN TRANSITION WITH BOTH PRICES HELD, ONE LOOP (the author, on the 67 per cent of households with a
SUD at the reform who are worse off: "you need to report how many of them lose when the pv and piv are constant", "you
may have to simulate this transition", "that transition only needs one iteration"). code/transition_fix/
remote_tr70_Cfix.sh (new; remote_tr70_Cu.sh, which a worker still runs, untouched) in session_014NWqivkMRLg2nJ6B74mLEy
-> results/transition_2c_t70_Cfix. Rule C at detection 0.20, T = 70, the main run's builds and Housing First arm; the
terminal arm is Table 5's held column re-solved (cf_fix2_treatC, DRUG_MARKET_ADJUSTER=0 at P_HELD 0.99938969, adjust_taxes
0 at V_HELD 0.067533863, as remote_decomp_shares_Cu3.sh's fixboth), checked to hold both exactly and compared with
results/decomp_2c_shares_Cu3/arm_fixboth/final.txt. Staging seeds both paths flat at the held values (checked), the
handover keeps drug_market_adjuster 0 and adjust_taxes 0 (checked in the run's HANDOVER lines), and the forward pass's
period 1 must print p_drug and pi_v at the held values. Loop 0's forward pass reads only the seeds, so MAX_LOOPS=1: the
binary is stopped once loop 0 is archived. Rent and the house price are constant in the main run too; the lump sum is the
binary's own ramp, as there. THE NUMBER: 'TRANSITION BETTER OFF TOL t=   1 ... worse_sud=' (the share of households with
a SUD alive at the reform who are worse off, tolerance 1e-3; transition_series.py's worse_off_sud, the paper's
x_trf_alive_sud_worse_pc, 67 in the main transition), printed at the START of the forward pass and copied to
results/transition_2c_t70_Cfix/better_off_t1.txt and the status as soon as it appears: about 2-3 hours of arms plus the
8-15 hour backward pass after launch. Safeguards: progress.txt every 20 minutes; the backward-pass checkpoint where the
disk allows, through code/transition_fix/build_tr70_C2ck.sh (new: patch_ckpt.py on the plain rule-C build's own tr.f90,
59 lines added, none changed, syntax-checked locally), ON if free disk >= 6 + 4 + 4 GB, and a relaunch reseeds from the
staged flat paths.

13:45 (20 Oct) ROUND r366 (4 comments). Red cleared (base_r366). Abstract: "micro evidence of randomised controlled
trials" (the author's "randomized", in the paper's British spelling; 148 words). Second lesson: "with the drug price and
pi_V held, as in a trial, which is too small to move either," (the author: "add here that those are held because this
is the consistent check compared to the trials that are done on small number of people") and "and even once both
clear, 67 percent are" (the author: "and even still"); the introduction's matching sentence was not commented and is
unchanged. Table 7 (the author on the two-line third label: "is there a way to make it clear that this text is for both
rows?"): each alternative's name is now a line of its own across the table (\multicolumn{7}{@{}l}), its two detection
rates below it, for all three alternatives so the table has one layout; layout only, no red.

13:55 (20 Oct) ROUND r367 (1 comment). Red cleared (base_r367). The introduction's held-price sentence takes the second
lesson's wording (the author: "maybe something a bit more explanatory like in the conclusion? why holding them?"):
", as in a trial, which is too small to move either," and "and even once both clear, 67 percent are". Red.
14:05 (20 Oct) The introduction's held-price sentence reworded so it does not repeat the second lesson (the author: "try
to use language that is not identical to the second lesson of the conclusion. you used exactly the same words"): "A trial
enrols too few households to change the drug price or the chance of drawing a voucher, so the comparison that matches it
keeps both at their Housing First levels. Then -- percent of the households that have a SUD at the time of the reform
lose, and when both adjust, 67 percent still do." and "outweigh these micro effects" (was "them"). Red, against base_r367.

14:10 (20 Oct) ALL RED REMOVED (the author: "remove all red"; base_r368 frozen, export_alttrans.py --freeze with the
others; splice 0 red, no \new left). Yellow left: only the dashes with no run behind them (Table 7's 0.20 no-exemption
row and its sentence in 6.5, x_trfix_sud_worse_pc in the introduction and the second lesson).

15:55 (20 Oct) ALL RED REMOVED (the author: "remove all red"; base_r369 frozen with export_alttrans.py --freeze and the
others; splice 0 red). Since base_r368: two introduction sentences an AI detector flagged were rewritten without the
cleft "What X is Y" and the colon-led list of three, content kept ("The verdict turns on the children. ..."; "The higher
risk of dying that comes with a SUD reverses the gradient: ..."). The author will send more flagged text tomorrow.
writing/ai_check/ holds the paper in four parts and in 15 chunks of at most 2,000 words (chunks_2000/, PDF and text);
regenerate them if the paper changes before the author uses them. writing/letters/qje_katz.tex is the letter to Katz.

16:35 (20 Oct) ROUND r370 (the author: "remove all red and crossed line. put only updates in red"; one comment). All
red and every strike from the AI-detector rewrites (passages 1-55) removed; base_r370 frozen with export_alttrans.py
--freeze and the others. The one update: theta's paragraph opens "The drug's weight in the bundle mostly determines how
much a household that uses spends on drugs, ..." (was "As the drug's weight in the bundle, it mostly determines"),
struck old words before the red new ones (track_changes.py against the stripped source). 43 pages. The check-in on the
runs uses base_r370 from now on.

16:38 (20 Oct) ALL RED AND STRIKES REMOVED (the author: "remove all red and crossed lines"; base_r371 frozen with
export_alttrans.py --freeze and the others; splice 0 red, no \new or \del left, 43 pages). The check-in uses base_r371.

16:49 (20 Oct) THE AI-FLAGGED SENTENCES HIGHLIGHTED IN BLUE (the author: "almost all the previous sentences are still
highlighted by the AI detector", "i need to bring it down to 0% AI", then "highlight for me the sentences, and ill try
to write them myself"). \ai{...} (preamble: soul \hl in aiblue) wraps every sentence whose words changed between
eb24d2fdc (base_r368, before any rewrite) and base_r371: the two introduction sentences of da167dc31 and passages 1-55,
194 sentences on 26 pages (word diff, expanded to whole sentences; footnotes, headers, \item labels and displays
excluded). fix_soul.py treats \ai like \tocheck (a moved number splits it in red) and turns 'et al.\ ' into a tie
inside it (soul cannot rebuild a control space). strip_red.py leaves \ai alone. When the author sends their own
wording for a sentence: replace that \ai{...} with \new{their text} (numbers back as @@names@@, no polishing of their
words), strike the old with track_changes.py, and drop the \ai.

18:00 (20 Oct) ROUND r372: THE AUTHOR'S OWN WORDING FOR THE AI-FLAGGED SENTENCES ON PAGES 1-10 (24 comments; "see my
comments until page 10 ... give me back in the repo the updates just for the first 10 pages in a new pdf", "put updates
in red", "i want to run the first 10 pages in the AI detector"). Each blue sentence replaced by the author's text in red,
the old struck before it (\del{old} \new{new}; no blue is left before Section 4). Their words kept; numbers back as
@@names@@, references as \ref; only clear slips fixed: missing spaces, "bring"->"brings", "to cost"->"the cost", "bring
alive"->"being alive", "is a smaller"->"is smaller", "sell"->"to sell", "spend ... to show"->"showing", "in the
bottom"->"at the bottom", a stray "not." and "..", "each of the strength of each of two"->"the strength of each of the
two", "housing policy affects homelessness is not tied"->"the effect of housing policy on homelessness is not tied". Four
accuracy fixes, told to the author: "proportional to" theta/(b+v) kept (the marginal utility is not equal to it);
"conceived" kept for "gave birth to" (Nilsson's exposure is by conception); "Evidence from other experiments" ->
"Non-experimental evidence" (Balsa 2008 is not an experiment) and "drinker parents" -> "problem-drinking parents"; "among
service members who stayed" kept in "They find that ... 61 percent" (Mehay and Pacula's own estimates are 11-45 per
cent; 61 is the raw comparison). Comment 21 ("remove" on "also reverses the gradient: on") struck "also reverses the
gradient:" and "it". writing/children_first_housing_later_pages1-10.pdf: pages 1-10 of a clean build (red kept, no
struck text, no blue) for the detector.

18:12 (20 Oct) ROUND r373 (the author: "remove all red and all crossed lines and put updates in red"; two comments, page 4;
base_r373 frozen with export_alttrans.py --freeze and the others; blue \ai sentences kept, 137 left, none before
Section 4). The trials' limitations paragraph in the author's words ("These studies, however, consider effects on
participants over six to thirty-six months, ..."; "a short period", "recovery process" and "thirty-six" fixed), which
drops the closing sentence on what no trial follows. The military evidence in the author's words: "They find that drug
testing of service members reduced past-year marijuana use by @@mp_stay_rel_pc@@ percent." (the qualifier "among
service members who stayed" the author removed; footnote 34 in Section 5 still says 61 is the raw comparison among those
who stayed and Mehay and Pacula's own estimates are 11-45 per cent -- told to the author). Old text struck, new red.
writing/children_first_housing_later_pages1-10.pdf regenerated (clean: red, no struck text, no blue).

18:48 (20 Oct) ROUND r374 (the author: "remove all red and put updates in red. make sure that if i have typos, or grammar
mistakes, you fix them"; 15 comments, pages 4-19, "and then i want pages 11-20 as a seprate pdf"). base_r374 frozen
with the others (export_alttrans.py --freeze). Each blue sentence the author rewrote replaced by their text in red, the
old struck; typos and grammar fixed in their text ("Moverover", "earnsy", "intreatment", "chane", "drawl", "whose parent
who had", "equilibirum", "drugprice", "spends on drug", "raisesthe", "everyage", "disorderin", "This is because,", "..",
"Treatment First's deters"), numbers and references back as @@names@@ and \ref/\eqref. Meaning fixes told to the
author: recovery "is likely" -> "is more likely" in treatment; "it increases the risk of mortality" -> "it still raises"
(the disorder, not treatment); "decides the value of life it" -> "decides the value of life"; iota "how much drug use"
-> "how much a SUD" affects SMI onset; lambda_m "Treatment First's deters drug use less" -> "Treatment First's
deterrence of drug use matters less". Slips left from r372-r373 fixed in red: "already adult" -> "adults", "but rather
take ... and price" -> "to take ... and to price", "counts" -> "would count", "for coarseness" -> "for the
coarseness", "every target, and" -> "every target and", "switched off both" -> "switched off, both". No blue is left
before page 21. CAgrace100 loop1 landed (18:41): Table 7's 1.00 exemption row 4.6 (9), 7-14, 0.7 (8), 7-9, CEV 6.58
(was 4.2/0.2/6.88), budget 0.78 per cent (still above 0.6), x_at_gr_par red. writing/children_first_housing_later_pages
1-10.pdf regenerated and pages11-20.pdf added (clean builds: red kept, no struck text, no blue).

19:02 (20 Oct) ROUND r375 (the author: "remove all crossed lines and all red. put updates in red. give me the 11-20 page
pdf again with no red in it", then "i will write the whole thing myself. fix the full pdf until page 20 and give me the
11-20 pdf"). base_r375 frozen with the others. Four fixes in red: "totake", "toprice" and "thecoarseness" were MY
glued words from r374 (an inserted word with nothing struck got no space after it -- in a round script, an insertion
needs its own trailing space); "beyond SUDs" -> "beyond drug use and SUD"; lambda_m's "matters less" -> "declines".
A spell check of pages 1-20 found nothing else. The author will rewrite the remaining 108 blue sentences (pages 21 on)
themselves: 86 of 194 done. The detector PDFs (pages1-10, pages11-20) now carry NO red (/pages_det.sh unwraps \new).

19:05 (20 Oct) ALL RED AND STRIKES REMOVED (the author: "remove all crossed lines and red from the pdfs"; base_r376 frozen
with export_alttrans.py --freeze and the others; splice 0 red). The full paper and the two detector PDFs (pages 1-10,
11-20) carry no red and no struck text; 108 blue sentences remain from page 21 on, for the author to rewrite.

19:21 (20 Oct) ROUND r377 (the author: "remove all red and put only updates in red. remove all crossed out lines", then "you
can also remove the pdfs for 1-10 and 11-20", then "make sure there are not grammar mistakes or typos"). base_r377
frozen with the others. Block 4's opening and the n.a. note of tab_eleven and tab_standard in the author's words (red,
old struck; "how quickly" given its verb, "a households" -> "a household"; "how much treatment raises recovery" added
for g). The pages 1-10 and 11-20 PDFs removed. A grammar pass over all 91 sentences the author has rewritten found nine
more slips, fixed in red: "as well as the same cohorts" -> "and than", "take those" -> "take the existing estimates",
"how much drugs" -> "how much of the drug", commas after "externally", "DATA_APPENDIX.md)" and "calibrated model",
"therefore would" -> "would therefore", "consequences to" -> "of", "how much beyond drug use and SUD Treatment First
prevents" -> "how much Treatment First prevents beyond drug use and SUD". Double spaces the strips left removed. A spell
check of the whole PDF finds nothing but URLs and terms.

19:25 (20 Oct) ALL RED AND STRIKES REMOVED (the author: "remove all red and crossed lines"; base_r378 frozen with
export_alttrans.py --freeze and the others; the two table notes' \del/\textcolor{red} wrappers removed by hand; splice
0 red, 43 pages). 108 blue sentences remain from page 21 on.

22:31 (20 Oct) CAann2_20 loop0 LANDED (the re-seeded announced 0.20 run) and replaces CAann20/loop0 in Table 7 and 6.5, red
against base_r378: homelessness +3.4 (12), periods 7-19; children +0.9 (11), periods 8-13; newborn CEV 1.92 (was 2.57);
budget 0.29 per cent; drug market off in 46 of 69 periods (was 69; the gap is about halved), so still provisional. Its
SUD share is no longer below the main transition's in every period 2-25, so why_more() no longer explains its newborn
gain; the explanation now sits in the exemption paragraph (x_at_gr_par), generated.

00:42 (21 Oct) CA20e loop0 LANDED: Table 7's 0.20 no-exemption row filled (no more yellow there): homelessness +5.4 (7),
periods 2-17; children +3.1 (5), periods 2-11; newborn CEV 3.09; budget 0.29 per cent; drug market off in 46 periods,
so provisional. export_noescape.py's x_ne20_so_* now read the transition's peaks (5 and 3, were the screen-only 6 and 4)
and 6.5 strikes "before its savings are recycled and the drug price falls,". x_at_ne_cev's reason covers both rows once
the 0.20 cohort also gains more for the same reason (SUD share by period ten 2.80 and 3.24 against 3.47): "it catches
every user" dropped, since at 0.20 it does not. Later loops also in: CAann100 loop1 (7.4 (9), 3.7 (9), CEV 4.62), CAgrace20
loop1 (1.8 (11), children never above, CEV 2.98); the third lesson's "at most 1.8 percent" follows. The main transition
has a loop2 (budget 0.18 per cent, drug 1 period off); 6.4 stays pinned to loop1. CAgr2_20 forward pass started (14
periods by 00:35): nearly the old CAgrace20 loop1 path (homelessness +1.6 against +1.8 at period 11).

01:11 (21 Oct) ROUND r379 (the author: "remove all red and put updates in red", "tell me how many more sentences are left",
"make sure to fix any grammar and typos in the comments"; nine comments, pages 21-23). base_r379 frozen with the others.
The author's wording, grammar and typos fixed, in red with the old struck: epsilon_s and its footnote (", which faces no
such cap," struck from the footnote's last sentence, its cap now gone), the homeless ages, the odds sentence, its
footnote removed (struck), Costantini, Milby, the two adjusting objects and the experiments, moral hazard ("borne not
by others" -> "borne by others", the meaning). 83 blue sentences left (1,706 words); 111 of 194 done. OPEN: the author
asks whether the model's homelessness odds ratio (u_odds_hl_m, 6.23) should be computed within the bottom of the
productivity distribution, as Bassuk et al. compare poor housed with poor homeless mothers -- not yet checked.

01:28 (21 Oct) ROUND r380 (the author: "remove all red and put updates in red. and remove all crossed lines"; 13 comments,
pages 21-24, on their own rewritten text; base_r380 frozen with the others). Red, old struck: "As this parameter's value
rises", "does" for "would", "are therefore poor" and "As a result, Treatment First's direct effects ...", the
Costantini sentence ("this matters because in the model, the effect of losing a voucher on the survival rates ..."),
"did" and "horizon" (Milby), and the two objects paragraph in the author's words ("allow it to adjust" -> "allow to
adjust", $\pi_V$ kept, "Thus, whatever the screen saves ..." struck, "Overall, I conduct three experiments."). 83 blue
sentences left. The author asked to compute the homelessness odds ratio for the bottom of the productivity
distribution, as Bassuk et al.: a background job (a copy of the benchmark build with a DIAG line, in the scratchpad) is
computing it; within one productivity node the model's exposed and unexposed rates are equal by construction (no
penalty for growing up in a shelter), so the restricted ratio will be near 1.

02:08 (21 Oct) ROUND r381 (the author: "remove all red and put updates in red. remove also all crossed lines", "make sure
to fix any grammatical errors and typos"; 15 comments, pages 21-24; base_r381 frozen with the others). In the author's
words, red with the old struck: "fall harder on", the two objects ("Within each of my experiments, I play around with
two objects. The first object is the drug price: I either hold it fixed or allow it to clear ..."), the first
experiment's paragraph, the second's steps, the drug price last, the transition, the screen, the military evidence and
its footnote (61 the raw comparison among those who stayed, 11 to 45 accounting for those who left), the counterpart.
Fixed: "keep the drug price stays fixed", "deterringusers", "both run", "breaks downthe", "wouldafter",
"equilibirum", "many period", "or is eligible and was offered", "stayed..", "between 11 to 45", "compared to" -> "than",
"can only harm itself" -> "the household itself", the relative clauses "which I either hold fixed or allow it" made
"the drug price: I either hold it fixed or allow it". Meaning, told to the author: "with no externalities" -> "which had
no externalities" (the first experiment's runs had none; the second's steps have them); "can only keep their
assistance" -> "can only be sure of keeping" (detection is imperfect); "I therefore set it" -> "I set it" (its reason,
"no programme reports that", went with the rewrite). 55 blue sentences left (1,111 words); 139 of 194 done.

02:40 (21 Oct) ROUND r382 (12 comments, pages 24-26; base_r382 frozen with the others). Red, old struck: "but" out,
"isolates", "households", "keep" (the author reverts r381's "be sure of keeping"), "concerns", and the welfare section
in the author's words (birth under the veil of ignorance, the sign of Delta, newborn welfare, the externality's weight,
the two horizons, the case without externalities). Fixed: "captures" -> "captured", "its childhood, is not counted" ->
"its childhood is not counted"; "is not discounted" kept with "in this way" (the parent's value is a discounted
lifetime value, just not by the child's years at home). The two sentences after it (the parent at j=1, and why the
child's own child enters A_t with weight omega_c) the author found unclear: left blue, explained to the author in chat.
44 blue sentences left (896 words); 150 of 194 done.

03:04 (21 Oct) ROUND r383 (10 comments, pages 26-33; base_r383 frozen with the others). In the author's words, red with
the old struck: the parent's value "is not discounted because the parent is already at age j=1, while a newborn child
will reach that age only J_K periods into their life" (the two sentences after it struck, the author: "maybe best to
remove it"), "weight on it", Delta P's paragraph, "This part is not an externality ..." struck, what the parent counts,
the conclusion's opening and the children's costs. Fixed: "the the", "enterants into adults" -> "entrants into
adulthood", "theearnings", "whensober", "invokedl", "the argument that dominate" -> "dominates", "awayan", a comma
pair round "in an economy without the externalities on children". Meaning, told to the author: "since it includes the
general-equilibrium effects" -> "and it includes"; "when pi_V and the drug price clear" -> "or"; "holding everything
other than the general-equilibrium effects constant" -> "with the distribution of entrants held at Housing First's"
(Delta P varies the policy, not only the general equilibrium). The author asked whether "Suppose the policy stays at
Treatment First and only who enters adult life changes" is right and why "two reasons": it is Delta E = Delta A -
beta^{J_K} Delta P (policy at Treatment First, entrants change); the second reason is the next paragraph's Delta P;
answered in chat. 28 blue sentences left (576 words); 166 of 194 done.
CFIX LANDED: the share with a SUD at the reform that is worse off with the drug price and pi_V held is 74 per cent
(better_off_t1.txt, worse_sud at tol 1e-3, forward pass's first period; the backward pass's checkpoint was saved at
02:30), against 67 per cent when both clear: the introduction's and the second lesson's yellow dashes are filled (red).

03:26 (21 Oct) ROUND r384 (13 comments on the author's own text, pages 28 and 33; base_r384 frozen with the others; red,
old struck): Delta P's paragraph ("and only change the policy", "where the drug is cheaper and it is easier to draw a
voucher when sober", "because it includes", "can adjust", "This captures the gain Delta P") and the conclusion's
opening ("Yes"/"No" in quotes, "but", "And I show that although", ", because", "then demonstrate", "But because", "than
the loss it inflicts on the parent"). Grammar read through in the final text; spell check clean. The author asked what
the Delta E paragraph means: explained in chat (the two reasons are Delta E, entrants change under Treatment First, and
Delta P, the policy changes for the same entrants; omega_c of Delta E is counted by the parent through D(y,d), the rest
is the earnings externality); its sentences are still blue for the author to rewrite. 28 blue sentences left.

03:31 (21 Oct) ROUND r385 (the author: "remove all red, put updates in red and address this specific paragraph in blue as
well"; base_r385 frozen with the others). "Specifically, I show that although" (the author's "Specifially" fixed),
"the screen creates". The Delta E paragraph rewritten at the author's request (red, old struck): a new one-sentence
paragraph before both headings ("I split the change in adult life, Delta A, into two parts that add up to it
exactly."), then "Better productivity at entry." in plain first-person sentences (keep Treatment First, compare
entrants under the two policies, fewer carry the penalty, Delta E, omega_c counted through D(y,d), the rest the
earnings externality). Written by me, so the detector may flag it: told the author. 23 blue sentences left (505 words).

03:46 (21 Oct) ROUND r386 (base_r386 frozen with the others). The Delta E paragraph in the author's words (red, old
struck), "holding ... at their benchmark levels" taken out (welfare_nok.parts values Delta E under Treatment First's
arm: E = A - beta^J_K P), and one sentence on it (the author: "use yours then", "just add one sentence to explain how the
Delta E is computed using the prices under TF"): "I value both distributions under Treatment First's policy, drug price
and probability of drawing a voucher, so that the second part below equals the parent's own gain exactly."
Conclusion: "generates more gain to the child than it costs the parent". "carrythe", "omega_cof" fixed.

03:50 (21 Oct) ROUND r387 (the author: "remove all red and crossed lines. and give me the paper without the appendix and
references so i can run it with the AI detector"; base_r387 frozen with the others). One comment ("remove" on "it"):
"than it costs the parent" -> "than cost to the parent" (dropping "it" alone leaves no grammar; red, old struck).
writing/children_first_housing_later_no_appendix.pdf: the paper cut at \appendix (34 pages, through the conclusion; no
appendix, no references), with no red, no struck text and no blue, for the detector.

03:55 (21 Oct) More of the author's own sentences highlighted blue (\ai) at their request, for them to rewrite
(the detector flags them): the thirty-year-period footnote (four sentences), the n.a. table note (tab_eleven and
tab_standard, written with a tie after "n.a." since soul cannot take a control space), Block 1's opening sentence, the
voucher-rent footnote, and the parent's-value sentence. 30 blue runs now.

04:37 (21 Oct) ROUND r388 (18 comments; base_r388 frozen with the others). Every remaining blue sentence replaced by the
author's wording, typos and grammar fixed, red with the old struck: the thirty-year footnote, both n.a. notes (tables
in \textcolor{red}), Block 1's opening, the voucher-rent footnote, the parent's welfare change, 6.4's reform cohort,
Appendix A's opening paragraphs, h_2, the ladder, Block 9, J/J_R/J_K, the tilt, r, the progressivity, tau_k, UI.
Fixed: "distance future", "casethe", "the tenant pay", "voucher holder", "an lower", "many parameter, many which",
"thirty three parameter", "andthe", "in same seven blocks", "muchweight", "are cost burdened, are more likely ... and a
voucher", "how much housing services are", "the affect", "expect earn", "low productivity households", "a higher the
risk", "psi's value if lower" -> "its value is lower" (the parameter is varphi), "ratereduces", "discourages households
to save", "a households", "Table X" -> Table~\ref{tab:eleven}, double full stops. Meaning, told to the author: "J and
J_R set the maximum years of life" -> "the maximum number of years a household can live and work, respectively" (J_R is
the retirement age). NO BLUE LEFT: all 194 flagged sentences (plus the author's six later additions) rewritten.
CAgrace100 loop2 landed: Table 7's 1.00 exemption row 5.0 (9), 1.3 (7), CEV 6.37; x_at_gr_par red.

04:50 (21 Oct) ROUND r389 (six word edits in Appendix A; base_r389 frozen with the others; the two table notes' red and
strikes removed by hand). Red, old struck: "estimates", "that I covered", "how much of its income", "rent it", "the
maximum number of periods of life" (the author's "maximum periods of life" given "number of"), "the return".

04:56 (21 Oct) ROUND r390 (base_r390 frozen with the others): "rent it," -> "rent," and "maximum number of periods" ->
"maximum periods" (the author's removals; old struck). writing/children_first_housing_later_appendix.pdf: Appendix A
alone (pages 35-39 of a clean build: no red, no struck text), for the AI detector.

## Round r391 (21 October)

Red from r390 stripped (base_r391). The author's rewrites of the four appendix sentences flagged blue (Block 7's
opening, sigma, the job-finding rate) replace them, with "their" -> "they" and "raise" -> "raised". The whole-paper
proofreading fixes stay in red: "point in this research", "I scale", Stone--Geary, J_E footnote's "The value of
J_E" / "The limit", iota "prevalence of SMI more", "cannabis, using", "and the other four are free", "the
participants did", "As in the case", "lives with it"; generated: export_alttrans.py "and more households do"
(struck by hand in the .tex: the splice only reds it), calib_tables.py tau_k source "long-term" (table cell red).

## Round r393 (21 October): the transition shown for sixty years

The author: the homelessness panels "tick up" at the end, no T = 80. Diagnosis: every cohort entering adult life from
year 60 (loop 1; 58 in loop 2) is homeless at age 29 at 0.945 per cent against 0.849 for every earlier cohort and 0.849
in the long run itself (arm_tf DIAG age 29); a jump between neighbouring cohorts with pi_V and the price flat, that
moves between iterates: the horizon's last decade, not an age cycle. transition_source.SHOWN = 60: the figure (all
eight panels, panel (g) the cohorts born in years 1-60), its x_trf_* names, x_tr_horizon_word ("sixty", the author:
"so i dont claim 70 years of transition") and the budget and drug gaps (unchanged) read years 1-60. Moved: 6.4's "0.56
by year 69" -> 0.55 by 60, children 0.93 -> 0.92, panel (h)'s "by year 69" -> 60. splice.py now strikes what a moved
name used to print (\del{old} \new{new}; \new alone inside maths), as the standing r305 rule asks.

## Round r394 (21 October)

Red and strikes from r393 removed (base_r394). Panel (h)'s sentence quotes the entrants' share at year 59, the year
before the last one shown (the author: "instead of saying 99.9 percent by year 60 say by year 59"); 99.89 there.

## 10:20 (21 October): CAgr2_20 loop0 landed

The re-seeded 0.20 exemption run's first pass replaces CAgrace20 loop1 in Table 7 (as planned): homelessness peak +1.6 (11)
against +1.8 (11), above 9-16 (was 8-16), children never above, reform cohort CEV 2.87 (2.98). Less converged than the
old loop 1: worst budget 0.65% of revenue (0.42), drug market off 5e-3 in 68 years (41). CAc loop1 landed too: the
1.00 no-exemption CEV 6.74 -> 6.57 (budget 0.42%, drug 17 years off). Built in red against base_r395.

## 21 October: the new title and file names

The author: the title is now "Housing First or Treatment First? Ask the Kids, Not the Parents" (in red, the old one
struck), and the paper's files are writing/housing_first_or_treatment_first.{src.tex,tex,pdf} (were
housing_first_children_later.{src.tex,tex} and children_first_housing_later.pdf). Every script that named them is
updated (splice.py, export_all_C.sh, build.sh, fill.py, verify.py, writing/tools/check_*.py, strip_red_before_transition.py,
ai_chunks.py), and README.md and CLAUDE.md. Build: pdflatex -jobname=housing_first_or_treatment_first
housing_first_or_treatment_first.tex. The GitHub URL in the title footnote is the repository's and is unchanged.

## 21 October: the file name after the full title, the title everywhere, red removed (r398)

The paper's files are writing/housing_first_or_treatment_first_ask_the_kids.{src.tex,tex,pdf} (the author: name them
after the full title); scripts, README.md and CLAUDE.md follow. The title "Housing First or Treatment First? Ask the Kids,
Not the Parents" replaces "Housing First, Children Later" in README.md, code/archive/run_files/readme.txt and the RED
round-1 letters (README, preamble comment, the five letters, PDFs rebuilt), and "Children First, Housing Later" in
writing/letters/qje_katz.tex (PDF rebuilt). Left as they are: the RED letters' "submitted as Housing First or Treatment
First?" (the manuscript's original title), the QJE letter's declined MS 45355, Costantini (2025)'s title, historical
notes and the GitHub URL. All red and struck text removed (base_r398).

## 21 October (r399): the replication link and the letter to Katz

The title footnote's link is the renamed repository, https://github.com/srotberg/housing_first_or_treatment_first_ask_the_kids_not_the_parents
(the author's screenshot), in red with the old one struck; nothing else in the paper moved (base_r398). writing/letters/qje_katz.tex
re-edited with the paper's current numbers and wording (abstract, intro, 6.1, 6.4, 6.5): the uninsurable mortality risk, "moral
hazard alone does not justify conditionality", the three externalities, childhood homelessness -11, parents +0.69 in GE, 67 per cent
of those with a SUD worse off, the three reasons the transition does not rise, the alternatives (14 per cent; 1.6 with the exemption);
changes \new, removals \del (ulem added). Squeezed to one page at 10pt, 0.9in margins (11pt ran to two with or without the strikes).

## Round r400 (21 October)

Red and strikes from r399 removed (base_r400). Two later passes landed since and move 6.5 and Table 7, so they are red:
CAann100 loop2 (announce 1.00: peak 7.4 -> 7.3, children 3.7 -> 3.6, first-period drug fall 30 -> 29, CEV 4.62 -> 4.54;
budget 0.15%, drug off 23 of periods 1-25) and CAgrace100 loop3 (exemption 1.00: peak 5.0 (9) -> 5.2 (7), children 1.3 ->
1.7, CEV 6.37 -> 6.24; budget 0.59%, drug off 12, both better than loop2). Cu loop3 landed too; the main row is unchanged
and the figure stays on loop1. The footnote link is black now.

## 21 October (r401): the letter to Katz, the author's comments

The author's 28 comments on qje_katz.pdf applied with \del/\new (my r399 red accepted): "under the title", the
parenthetical removed, "The question in the new paper... are all new. Among the changes, the model...", the two-period
sentence rewritten ("uninsurable risk due to a SUD"), addiction -> SUD, "rationed vouchers", "as an exogenous parameter",
"Instead, I show that the answer depends on the impact that Treatment First has on the children through its impact on
drug use", "during childhood", "but a voucher revoked exposes the child to childhood homelessness. The parent only counts a
part of these effects.", "because the savings ... more vouchers to sober households", "about three quarters of them are
worse off" (74 per cent, prices held), "are the macro effects that trials do not control for", "SUD during their childhood",
"under Treatment First is set based on", "(veterans in the study)", "The model also now includes other new elements",
"I also included transitions", "due to low detection and households entering treatment", "about 7 percent more vouchers"
(share of households holding a voucher +6.83 per cent in the long run, arm_tf/final.txt), "transition specifications, in
which ... include ... and show that the impact ... depends on the reform's design". Typos fixed (throuugh, externaltiies,
Specifially, specifiations), TF -> Treatment First. 10pt, 0.8in, parskip 0.35em: one page once the strikes go.

## Round r402 (21 October)

All red and strikes removed from the paper and from the letter to Katz (base_r402 = the current numbers, so the one pass
that landed during the build, the 0.20 no-exemption row 5.4 (7) -> 5.3 (6), CEV 3.09 -> 3.02, is black; told to the author
in chat). Whole-paper spell check: no typos (28 unknown words, all technical terms or British spellings).

## 17:40 (21 October): CAann2_100 loop0 landed (r403)

The re-seeded announced 1.00 run replaces CAann100 loop2 in Table 7 (as planned): peak 7.9 (10) against 7.3 (9), children
4.4 (9) against 3.6 (9), above Housing First 7-17 / 7-13, reform cohort CEV 3.46 against 4.54; budget 0.40% against 0.15%,
drug off 23 of periods 1-25 in both. The gap in CEV between two passes of the same experiment is flagged to the author.
CAann2_20 loop1 also landed: 3.3 (12), 0.9 (10), CEV 1.91 (was 3.4, 0.9 (11), 1.92). Red against base_r402.
