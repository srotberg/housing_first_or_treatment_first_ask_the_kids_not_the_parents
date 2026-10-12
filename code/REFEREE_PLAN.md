# The referee plan (agreed with the author 12 October, 03:15 UTC: "yes to all three, go ahead")

An hourly routine ("referee plan check") fires into the main session and works through this file. Each run below
publishes a status file on the branch every 20 minutes; a run with no commit for more than 90 minutes is dead.

| # | run | worker session | script | results | expected |
|---|---|---|---|---|---|
| 1 | Treatment First at detection 0.50 | session_01U6oSxH75fzw3bcbss5Yoxn | code/pdet/remote_pdet.sh 0.50 | results/counterfactuals_2c/tf_pdet50 | resumes from pass 3; about 4-6 h |
| 2 | delta_d = delta_h = 0, one class | session_01L9GRYJjZjPxSkVBUa6u7LR (relaunched 06:41 12 Oct: the first container, session_015xAVdM3PZAKWssDvzZrLYp, disconnected after "benchmark done" at 05:08; the benchmark files were local, so it is solved again) | code/deltad/remote_deltad1c.sh | results/deltad/dd0_1c | benchmark ~2 h, null ~2 h, tf ~3 h; ~13:30 |
| 2b | delta_d = 0 decomposition: Treatment First with pi_V and the price held (fixboth) and with the price held (fixp), the counterparts of Table 6's first two columns (the author: "sure, do these runs too") | session_01L9GRYJjZjPxSkVBUa6u7LR (run 2's container, after run 2) | code/deltad/remote_deltad1c_decomp.sh | results/deltad/dd0_1c_decomp | ~3-4 h after run 2 |
| 3 | transition welfare cohort by cohort (T = 70 loop 2 with the entrant print) | session_017djaHFjuRkcptdYGCAMXRx (relaunched 07:19 12 Oct: session_011AVKB7xRWCWXnA3g25E5bR's container disconnected about 05:20, with run 2's; starts from the arms again) | code/transition_fix/remote_tr70_cohort.sh | results/transition_2c_t70_cohort | arms ~6 h, loop ~10 h; ~23:30 |
| 4 | both penalties (delta_d 0.24, delta_h 0.31), long run then T = 25 | session_018N3fsfggMz4fumbypJRXwp | code/deltah/remote_deltah_both.sh (+ _tr25) | results/deltah_both, deltah_both_tr25 | benchmark 25-40 h, arms ~2.5 days, T = 25 ~1 day |
| 5a | Treatment First with vouchers conditional on being in treatment (third try, 12 Oct ~14:20: the second, tf_treat2, was inert too -- the screen read a treatment flag the distribution leaves at 0; patch_treat2.py now sets it from each household's own policy) | session_01CJQQueaamcLMeiBTc9HVwx (14:09) | code/treat/remote_treat2.sh | results/counterfactuals_2c/tf_treat3 | ~7 h; ~21:30. INERT CHECK: pass 1 welfare must differ from the paper's 789.9398 |
| 5a-old | SUPERSEDED, do not write into the paper: the first version (remote_treat.sh treat) exempted treatment from the disorder test only; a household with a SUD keeps using, so it still failed the use test and the arm reproduced the paper's (pass 8: CEV 4.38 vs 4.37). Left to finish as a check of that diagnosis | session_017vq7TAYbFN6WBPXTHviuKH | code/treat/remote_treat.sh treat | results/counterfactuals_2c/tf_treat | finishing |
| 5b | the paper's two arms with the MILBY SPLIT print | session_016fs45yE21insqcHar6sFj4 | code/treat/remote_treat.sh split | results/counterfactuals_2c/milby_split | LANDED 10:04 12 Oct; in the paper (round r313, p.22) via code/paper/export_milby_split.py |
| 6 | the omega_c = 0.686 arms re-solved for their values by node | (launched 12 Oct ~04:00) | code/omega_nishiyama/remote_nish_nodes.sh | results/omega_nishiyama/nodes | LANDED 12:40 12 Oct; in the paper (round r314, p.19 footnote) via code/paper/export_nish_parts.py |

Stopped at the author's word: T = 70 (converged enough, "will not change the figures anymore"), detection 0.70, the
two-class delta_d = 0 run (replaced by 2), delta_d 0.05 and 0.12, equal-budget Housing First.

## On each check
1. Fetch and fast-forward the branch. For each run, read its latest status line and its last commit time.
2. A dead run (no commit for 90 minutes, a GUARD line, or a worker session in FAILED): relaunch it ONCE in a fresh
   session with the same one-command brief (model claude-sonnet-5-5, replies one line), archive the dead session, and
   update the table above. A run that dies twice is reported to the author, not relaunched. Never relaunch 4 without the
   author (its brief says so); never edit a script a running worker executes.
3. When a run lands, write it into the paper (red, struck deletions, the base being the state the author last read),
   build, commit content then PDF, push, send the PDF, and tell the author in chat:
   - 1: the footnote "The qualitative results continue to hold with a detection rate of 70 percent ..." becomes the
     50 percent result: the newborn's gain (CEV(tf) - CEV(paper's null)), drug use, SUD, homelessness, pi_V.
   - 2: one sentence where delta_d is set (Section 5): with no penalty, every other parameter as calibrated, Treatment
     First's gain is X percent (CEV on the one-class benchmark's own curve, welfare_nok.Bench(results/deltad/dd0_1c)),
     and which parts remain.
   - 3: cohort_cev.py extended to the entrant-by-parent-age lines: the cohort born at the reform along its own life
     replaces the 3.0 and panel (g); every child alive at the reform by age and parent's state; eq. 31's text and its
     footnote rewritten to the cohort object.
   - 4: NOT written into the paper. Report the numbers to the author (gain against 4.52, use, SUD, homelessness, price,
     pi_V; then the T = 25 cohort CEVs); the author decides the two yellow passages.
   - 5a: the footnote on the screen's rule gains the result with treatment meeting the condition (results/counterfactuals_2c/tf_treat3, NOT tf_treat or tf_treat2).
   - 6: the omega_c footnote (p.19, marked yellow) gives the sensitivity's gain split into externalities and the rest,
     welfare_nok.parts on results/omega_nishiyama/nodes/{tf,null} with the sensitivity's benchmark, against Table 6's
     last column (the author: "break it down by externalities and non-externalities").
   - 2b: report to the author with run 2: the delta_d = 0 gain split into the screen alone (fixboth), + recycling (fixp - fixboth), + the cheaper drug (tf - fixp), beside Table 6's 3.75 / 11.32 / 4.52; into the paper only as the author directs. THE AUTHOR DIRECTED IT, 12 October 14:50: "in the case of deltad=0 we need to explain the the small gain is driven by the small elasticity, and if we used an elasticity like becker, murphy, and grossman, the gains would still be very large". fixp IS that case: with nu_1 fixed, epsilon_s -> infinity holds the price at Housing First's. So the delta_d = 0 sentence (run 2) gets a second clause from fixp's CEV, through an exporter, its direction word from compare() against the clearing arm's CEV; if fixp's gain is NOT large, the sentence says what it is and the author is told before it goes in.
   - 5b: the p.22 Milby paragraph gains the driver: treatment take-up and SMI shares of housed SUD households by voucher
     status, Housing First against Treatment First.
4. When every run has landed and been written in (4 reported), delete the routine and say so.
5. THE SCRIPTS' REORGANISATION WAITS FOR THE RUNS (the author, 12 October: "can you also do a general reordering/cleanining of all the repo?"). Done that day: the root, writing/ (tools/), and code/'s unread run files and old notes. Left: code/'s 98 .sh and 92 .py at the top level, which running workers call by path. When runs 1, 2, 2b, 3 and 5a have all ended and before the both-penalties run is launched, map every script's callers, move the August-September calibration machinery (nelder, newton, sweep, supervise, next_batch, resume, worker, stage_night and their state files, CORRECT_*, RESTORE_*, batch_stage*, worker_*) to code/archive/, group the live scripts by role, fix every path, and re-run the paper's exporters and checkers before pushing.
