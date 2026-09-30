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
LOG = os.path.join(ROOT, 'code', 'trtf60', 'restart3_killed_1323', 'run.log')
TAG = 'restart3_loop0'
OUT = os.path.join(ROOT, 'results', 'transition', TAG)
