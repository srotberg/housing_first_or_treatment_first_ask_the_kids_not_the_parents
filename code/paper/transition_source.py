"""
WHICH T = 60 TRANSITION PASS THE PAPER READS: one pin, imported by transition_series.py,
transition_figure.py and export_results.py, so the figure, its names and the introduction's
numbers can never come from different passes (on 30 September the newest-log rule had
moved export_results.py to restart 3c while the figure read restart 3).

LOG is the run log whose FIRST forward pass (loop 0) is read; TAG names the directory under
results/transition/ the series are written to.  code/trtf60 is not tracked, so a pass is
archived there before it is pinned.
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
# 6 October 08:30 (the author: "we can put them when you have them"): the T = 60 run on the current
# (2c) build, tr2c_t60, restart_r2, loop 1 -- its second iterate.  The budget clears to a median residual
# of 5.5e-4 (worst 3.6e-3, above 1e-3 in 22 of 58 years) and the drug market to a median gap of 1.0 per
# cent of the price (worst 3.4 per cent, above 0.005 in 39 of 59 years), against 2.9 and 5.3 per cent in
# loop 0_r2.  Not converged: the rule is 0.005 in every year, so every number read from it is provisional.
# The log here is loop 1's segment alone (from its 'TRANSITION INIT PARENT SHARE RESTORED' to its 'PATHS
# SAVED'), because the readers take a log's FIRST pass; the full log and the paths are archived in
# results/transition_2c/loop1_r2/.
LOG = os.path.join(ROOT, 'code', 'trtf60', 'tr2c_loop1_r2', 'run.log')
TAG = 'tr2c_loop1_r2'
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
# the benchmark welfare curve the cohort CEVs are read against, and the two steady states the path is
# solved between: Housing First with no policy change, and the Treatment First long run, on the same build
CURVE = os.path.join(ROOT, 'code', 'trtf60', 'tr2c_loop1_r2', 'welfare_curvebaseline_benchmark.dat')
REF = os.path.join(ROOT, 'results', 'transition_2c')
REF_NULL, REF_TF = 'arm_null', 'arm_tf'
# the previous pin, kept for the record: restart 3g's loop 0 on the old build (30 September)
#   LOG = code/trtf60/restart3g_loop0/run.log, TAG = 'restart3g_loop0'
