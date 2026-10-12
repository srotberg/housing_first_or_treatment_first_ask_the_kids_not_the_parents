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
