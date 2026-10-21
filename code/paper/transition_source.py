"""
WHICH TRANSITION PASS THE PAPER READS (T = 70 since 11 October): one pin, imported by transition_series.py,
transition_figure.py and export_results.py, so the figure, its names and the introduction's
numbers can never come from different passes (on 30 September the newest-log rule had
moved export_results.py to restart 3c while the figure read restart 3).

LOG is the run log whose FIRST forward pass (loop 0) is read; TAG names the directory under
results/transition/ the series are written to.  code/trtf60 and code/trtf70 are not tracked, so a pass is
archived there before it is pinned.
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
# 11 October 20:30: loop 2 of the T = 70 run (results/transition_2c_t70/loop2), the third iterate of the prices,
# re-pinned because quoted numbers moved against loop 1: half of the long-run fall in the number with a SUD is done
# by year 11 (loop 1: 10; loop 0: 11) and nine tenths by year 27 (26; 27), the year childhood homelessness peaks is 6
# (7), the first-year fall in the share of parents who use is 5.00 points (5.01); unquoted, the reform cohort's CEV
# 2.97 (2.96), the peak fall in drug use 29 percent (30), the first decade's CEV 3.16 (3.20). The two SUD years flipped
# back to loop 0's values, so the path is still oscillating between iterates, not converged. The worst budget residual
# on the path is 8.14e-3 (loop 1: 1.19e-2) and the worst drug gap 1.20e-2 (1.85e-2). The log carries three forward
# passes; the plain log here keeps the lines before the first marker and everything from the THIRD (last) marker on.
# Previous pin: loop 1, below.
# 11 October 09:15: loop 1 of the T = 70 run (results/transition_2c_t70/loop1), the second iterate of the prices,
# re-pinned because two quoted numbers moved against loop 0 (the author, 11 October: re-pin to loop 1 only if a
# quoted number moves): half of the long-run fall in the number with a SUD is done by year 10 (was 11) and nine
# tenths by year 26 (was 27); the reform cohort's CEV is 2.96 against 2.95, the peak fall in drug use 30 against
# 29 percent, nothing else the paper quotes moved. The worst budget residual on the path is 1.19e-2 (loop 0:
# 1.27e-2) and the worst drug gap 1.85e-2 (1.60e-2), both in years 60 to 69. The run log in
# results/transition_2c_t70/loop1/run.log.gz carries BOTH forward passes, and transition_series.py reads the first
# pass of the log it is given, so the plain log here is that file with loop 0's pass cut out: the lines before the
# first 'TRANSITION INIT PARENT SHARE RESTORED' marker, then everything from the second marker on
# (code/trtf70 is not tracked, so a pin is staged there before it is read).
# Previous pin: loop 0 of the same run (11 October 00:40, the author: "pin the paper to T=70 now"), the first
# iterate from the converged T = 60 loop 1_r5 paths (code/remote_transition_2c_t70.sh), whose years 1 to 59
# reproduced the T = 60 path to five decimals and whose cohort CEVs agreed with the T = 60 pin to within 0.005
# points. The arms the run is solved between (results/transition_2c_t70/arm_*) re-solve the T = 60 arms to a worst
# relative difference of 2.4e-4 and carry only final.txt, so REF below stays on the T = 60 arms, which carry the
# logs and the by-node values. Before that: T = 60 loop 1_r5 (9 October 10:03, results/transition_2c/loop1_r5).
# 16 October (round r324, the author: "please update the transition figures to include the new T=50"): RULE C, the
# corrected Housing First, T = 50, the fourth and last loop (results/transition_2c_t50_Cu/loop3; the binary's loop 0
# after the 01:49 relaunch, so its log carries one forward pass). NOT CONVERGED: the worst budget residual on the
# path is 2.08e-2 and the worst drug gap 3.56e-3, and pi_V in years 40-49 sits 2.2 per cent below its terminal value,
# further than in loop 0 (1.5), so the horizon may be short (T = 60 is the open question). The steady states are the
# T = 50 run's own terminal re-solves (final.txt, 'no policy' column) and the corrected long-run arms' logs
# (results/decomp_2c_shares_Cu/arm_tf/{null,tf}/cf.log.gz), staged in code/trtf50/ref (untracked symlinks).
# 17 October, 23:50 (the author, 18:10: "you should update the figures", and before that "why didnt you update the
# transition figures? Dont we have some intiial T=70 results?!"): RULE C, the corrected Housing First, T = 70, loop 0
# (results/transition_2c_t70_Cu/loop0, archived 23:4x; code/transition_fix/remote_tr70_Cu.sh). Its seeds are rule C's
# T = 50 loop-3 paths extended to 69 years (extend_seeds_C70.py), so this first pass is the T = 50 iterate run out to the
# longer horizon. NOT CONVERGED: the worst budget residual on the path is 1.80e-2 and the worst drug gap 5.98e-3 (the
# sentence in 6.4 states the budget's worst gap, x_tr_bud_worst_pc); its last ten years sit within 0.01 per cent
# (price) and 0.25 per cent (pi_V) of the terminal values. The steady states are the run's own re-solved arms
# (results/transition_2c_t70_Cu/arm_{null,tf}: cf.log.gz, final.txt), the terminal one 1.2e-4 from the accepted
# rule-C arm. Stage the log on a fresh machine with:
#   mkdir -p code/trtf70/tr2c_t70_Cu_loop0 && zcat results/transition_2c_t70_Cu/loop0/run.log.gz > code/trtf70/tr2c_t70_Cu_loop0/run.log
# 20 October, 02:10: loop 1 of the same run (results/transition_2c_t70_Cu/loop1; the binary's loop 0 after the 01:50
# relaunch on 19 October, from loop 0's saved paths, so its log carries one forward pass). REASONABLE in the author's
# sense (18 October: "it's enough if they are reasonable"): the worst budget residual on the path is 1.21e-2 (0.21 per
# cent of net revenue, loop 0: 1.80e-2) and the drug market is inside 5e-3 in every year (worst 3.84e-3, loop 0: 5.98e-3).
# Stage the log with:
#   mkdir -p code/trtf70/tr2c_t70_Cu_loop1 && zcat results/transition_2c_t70_Cu/loop1/run.log.gz > code/trtf70/tr2c_t70_Cu_loop1/run.log
# Previous pin: loop 0, above.
LOG = os.path.join(ROOT, 'code', 'trtf70', 'tr2c_t70_Cu_loop1', 'run.log')
TAG = 'tr2c_t70_Cu_loop1'
HORIZON = 70
UNCONVERGED_FROM = 60
# THE YEARS THE PAPER SHOWS (21 October, the author: "make the homelessness and childhood homelessness graphs a bit
# more smooth at the end ... i dont want to run a T=80 transition", then "change the words from seventy to sixty in the
# text so i dont claim 70 years of transition", "and any other place that refers to the transition"). The figure, its
# names, the horizon word and the budget and drug gaps read years 1 to SHOWN only. Why: every cohort entering adult life
# from year 60 (loop 1; year 58 in loop 2) is homeless at age 29 at 0.945 per cent against 0.849 for every cohort before
# it and 0.849 in the long run itself (arm_tf DIAG age 29), a jump between neighbouring cohorts with pi_V and the drug
# price flat to the fourth decimal, which moves between iterates: an artefact of the horizon's last decade, so the path
# ticks up from year 61-63 to end above the long run. Years SHOWN+1 to 69 stay in the run and in series.csv.
SHOWN = 60
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
CURVE = os.path.join(ROOT, 'results', 'transition_2c_t70_Cu', 'loop1', 'welfare_curvebaseline_benchmark.dat')
# (18 October, the author: "in some places you write 2.57 and here you wrote 2.59") the long run the path is compared
# with is the paper's main arm, as at T = 50: the run's own re-solved terminal arm gives a newborn 2.59 against the main
# arm's 2.57. code/trtf70/ref (untracked symlinks, as code/trtf50/ref): arm_{null,tf}/cf.log.gz ->
# results/decomp_2c_shares_Cu/arm_tf/{null,tf}/cf.log.gz, arm_{null,tf}/final.txt -> results/transition_2c_t70_Cu/arm_*/final.txt
REF = os.path.join(ROOT, 'code', 'trtf70', 'ref')
REF_NULL, REF_TF = 'arm_null', 'arm_tf'
# the previous pin (rule C, T = 50, loop 3; 16 October to 17 October 23:50), kept for the record:
_RULE_C_T50_LOG = os.path.join(ROOT, 'code', 'trtf50', 'tr2c_t50_Cu_loop3', 'run.log')
_RULE_C_T50_TAG = 'tr2c_t50_Cu_loop3'
_RULE_C_T50_HORIZON = 50
_RULE_C_T50_UNCONVERGED_FROM = 40
_RULE_C_T50_CURVE = os.path.join(ROOT, 'results', 'transition_2c_t50_Cu', 'loop3', 'welfare_curvebaseline_benchmark.dat')
_RULE_C_T50_REF = os.path.join(ROOT, 'code', 'trtf50', 'ref')
# on a fresh machine stage the log first: zcat results/transition_2c_t50_Cu/loop3/run.log.gz > LOG
# the previous pin (rule A, T = 70, loop 2), kept for the record:
_RULE_A_LOG = os.path.join(ROOT, 'code', 'trtf70', 'tr2c_t70_loop2', 'run.log')
_RULE_A_TAG = 'tr2c_t70_loop2'
# THE PINNED RUN'S HORIZON AND THE START OF ITS DRIFTING END: the path covers years 1 to HORIZON - 1, and the
# figure's peaks are read before UNCONVERGED_FROM, where the path is least converged: the years 60 to 69 that the
# horizon added were seeded with the terminal prices in loop 0 and have been iterated once in loop 1 (budget
# residual up to 1.19e-2 there, under 2e-3 before). Both move with the pin.
_RULE_A_HORIZON = 70
_RULE_A_UNCONVERGED_FROM = 60
_RULE_A_OUT = None
# the benchmark welfare curve the cohort CEVs are read against, and the two steady states the path is
# solved between: Housing First with no policy change, and the Treatment First long run, on the same build
_RULE_A_CURVE = os.path.join(ROOT, 'code', 'trtf70', 'tr2c_t70_loop2', 'welfare_curvebaseline_benchmark.dat')
_RULE_A_REF = os.path.join(ROOT, 'results', 'transition_2c')
# the previous pin, kept for the record: restart 3g's loop 0 on the old build (30 September)
#   LOG = code/trtf60/restart3g_loop0/run.log, TAG = 'restart3g_loop0'
