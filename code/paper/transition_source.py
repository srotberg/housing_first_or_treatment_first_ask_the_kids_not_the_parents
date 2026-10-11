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
# 11 October 00:40 (the author: "pin the paper to T=70 now"): the T = 70 run on the same build, started from the
# converged T = 60 loop 1_r5 paths (code/remote_transition_2c_t70.sh), loop 0, its first iterate from those seeds,
# archived in results/transition_2c_t70/loop0 (run.log.gz, the paths, the curve) and gunzipped here, since the
# readers open a plain log and code/trtf70 is not tracked. Every cohort's CEV agrees with the T = 60 pin to within
# 0.005 points (2.74 against 2.73 for the cohort born at the reform); the worst budget residual on the path is
# 1.27e-2 and the worst drug gap 1.60e-2, both in the years the longer horizon added. The arms it was solved
# between (results/transition_2c_t70/arm_*) re-solve the T = 60 arms to a worst relative difference of 2.4e-4 and
# carry only final.txt, so REF below stays on the T = 60 arms, which carry the logs and the by-node values.
# Previous pin: T = 60 loop 1_r5 (9 October 10:03, results/transition_2c/loop1_r5).
LOG = os.path.join(ROOT, 'code', 'trtf70', 'tr2c_t70_loop0', 'run.log')
TAG = 'tr2c_t70_loop0'
# THE PINNED RUN'S HORIZON AND THE START OF ITS DRIFTING END: the path covers years 1 to HORIZON - 1, and the
# figure's peaks are read before UNCONVERGED_FROM, where the path stops being iterated: in this loop 0 the years
# 60 to 69 that the horizon added carry the terminal prices as seeds (budget residual up to 1.25e-2 there, under
# 2e-3 before), while years 1 to 59 reproduce the converged T = 60 path to five decimals. Both move with the pin.
HORIZON = 70
UNCONVERGED_FROM = 60
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
# the benchmark welfare curve the cohort CEVs are read against, and the two steady states the path is
# solved between: Housing First with no policy change, and the Treatment First long run, on the same build
CURVE = os.path.join(ROOT, 'code', 'trtf70', 'tr2c_t70_loop0', 'welfare_curvebaseline_benchmark.dat')
REF = os.path.join(ROOT, 'results', 'transition_2c')
REF_NULL, REF_TF = 'arm_null', 'arm_tf'
# the previous pin, kept for the record: restart 3g's loop 0 on the old build (30 September)
#   LOG = code/trtf60/restart3g_loop0/run.log, TAG = 'restart3g_loop0'
