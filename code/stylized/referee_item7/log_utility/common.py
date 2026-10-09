"""Shared set-up for the log-utility (sigma = 1) recalibration of the Section 3 model.

gradient.py is imported unmodified.  Every formula in it already handles sigma = 1 except y_zero, which divides
by (sigma - 1); its log limit is U(X) + aleph = log X + aleph = 0, so X = exp(-aleph), defined here.  U(), _U0p,
_U1p, plan(), W(), vsl() and the moments are written in forms that are valid at sigma = 1 (U switches to log
when s == 1.0, and the marginal utilities are X^(1-s)/c, which is 1/c at s = 1)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..'))
ROOT = os.path.normpath(os.path.join(SRC, '..', '..'))
OUT = os.path.join(ROOT, 'results', 'referee_item7', 'log_utility')
sys.path.insert(0, SRC)
import gradient as G  # noqa: E402

FIX_LOG = {**G.FIXED, 'sigma': 1.0}
BENCH = json.load(open(os.path.join(SRC, 'gradient.json')))


def y_zero(q):
    """Consumption at which U + aleph = 0, valid for any sigma including the log limit."""
    s = q['sigma']
    xz = math.exp(-q['aleph']) if s == 1.0 else (q['aleph'] * (s - 1.0)) ** (-1.0 / (s - 1.0))
    return (xz / q['b'] ** q['theta']) ** (1.0 / (1.0 - q['theta']))


def load_log():
    return json.load(open(os.path.join(OUT, 'log_calibration.json')))['q']
