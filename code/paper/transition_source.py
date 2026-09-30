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
# 30 September 12:40 (the author: "merge it to the paper"): restart 3g's loop 0, seeded
# from restart 3c's paths, one iterate on from restart 3's.  It clears the budget better
# (median residual 0.0015 against 0.0027 in years 2-40; above 0.005 in 5 years against
# 10) and the drug market about as well (median gap 0.0036 against 0.0039; its worst year
# 0.026 against 0.020).  Neither has converged: the rule is 0.005 in every year.
LOG = os.path.join(ROOT, 'code', 'trtf60', 'restart3g_loop0', 'run.log')
TAG = 'restart3g_loop0'
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
