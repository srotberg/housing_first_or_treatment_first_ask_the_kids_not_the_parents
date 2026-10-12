# The referee plan (agreed with the author 12 October, 03:15 UTC: "yes to all three, go ahead")

An hourly routine ("referee plan check") fires into the main session and works through this file. Each run below
publishes a status file on the branch every 20 minutes; a run with no commit for more than 90 minutes is dead.

| # | run | worker session | script | results | expected |
|---|---|---|---|---|---|
| 1 | Treatment First at detection 0.50 | session_01U6oSxH75fzw3bcbss5Yoxn | code/pdet/remote_pdet.sh 0.50 | results/counterfactuals_2c/tf_pdet50 | resumes from pass 3; about 4-6 h |
| 2 | delta_d = delta_h = 0, one class | session_015xAVdM3PZAKWssDvzZrLYp | code/deltad/remote_deltad1c.sh | results/deltad/dd0_1c | benchmark ~2 h, null ~2 h, tf ~3 h |
| 3 | transition welfare cohort by cohort (T = 70 loop 2 with the entrant print) | session_011AVKB7xRWCWXnA3g25E5bR | code/transition_fix/remote_tr70_cohort.sh | results/transition_2c_t70_cohort | arms ~6 h, loop ~10 h |
| 4 | both penalties (delta_d 0.24, delta_h 0.31), long run then T = 25 | session_018N3fsfggMz4fumbypJRXwp | code/deltah/remote_deltah_both.sh (+ _tr25) | results/deltah_both, deltah_both_tr25 | benchmark 25-40 h, arms ~2.5 days, T = 25 ~1 day |
| 5a | Treatment First with treatment meeting the condition | session_017vq7TAYbFN6WBPXTHviuKH | code/treat/remote_treat.sh treat | results/counterfactuals_2c/tf_treat | ~6 h |
| 5b | the paper's two arms with the MILBY SPLIT print | session_016fs45yE21insqcHar6sFj4 | code/treat/remote_treat.sh split | results/counterfactuals_2c/milby_split | ~3-4 h |

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
   - 5a: the footnote on the screen's rule gains the result with treatment meeting the condition.
   - 5b: the p.22 Milby paragraph gains the driver: treatment take-up and SMI shares of housed SUD households by voucher
     status, Housing First against Treatment First.
4. When every run has landed and been written in (4 reported), delete the routine and say so.
