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
# 9 October 10:03 (the author, 8 Oct: "can you run the T=60 transition again to try and finish solving it?"): the
# T = 60 run on the same build (binary md5 4c1c6c64) relaunched from loop 0_r3's saved paths, tr2c_t60 restart r5,
# loop 0 -- its first iterate from those seeds.  The drug market clears to a median gap of 0.1 per cent of the
# price (worst 1.21 per cent, above 0.005 in 5 of 59 years), against worst 1.35 in loop 0_r3; the budget to a
# median residual of 2.0e-3 (worst 4.5e-3, above 1e-3 in 34 of 59 years), against worst 5.3e-3.  Not converged,
# so every number read from it is provisional.  The log here is loop 0_r5's segment alone (lines 10133-22617 of
# tr2c_t60/run.log, from its 'TRANSITION INIT PARENT SHARE RESTORED loop= 0' to the CONVERGENCE TERMS after its
# 'PATHS SAVED'), because the readers take a log's FIRST pass; the full log and the paths are archived in
# results/transition_2c/loop0_r5/.  Previous pin: loop 0_r3 (7 October 20:38, results/transition_2c/loop0_r3).
LOG = os.path.join(ROOT, 'code', 'trtf60', 'tr2c_loop1_r5', 'run.log')
TAG = 'tr2c_loop1_r5'
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
# the benchmark welfare curve the cohort CEVs are read against, and the two steady states the path is
# solved between: Housing First with no policy change, and the Treatment First long run, on the same build
CURVE = os.path.join(ROOT, 'code', 'trtf60', 'tr2c_loop1_r5', 'welfare_curvebaseline_benchmark.dat')
REF = os.path.join(ROOT, 'results', 'transition_2c')
REF_NULL, REF_TF = 'arm_null', 'arm_tf'
# the previous pin, kept for the record: restart 3g's loop 0 on the old build (30 September)
#   LOG = code/trtf60/restart3g_loop0/run.log, TAG = 'restart3g_loop0'
