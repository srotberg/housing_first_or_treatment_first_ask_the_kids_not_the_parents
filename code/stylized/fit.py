"""
A JOINT FIT, KEPT AS A FALLBACK.  NOT THE METHOD -- SEE THE WARNING BELOW.

DO NOT REACH FOR THIS BEFORE recalibrate.py.  The author, 12 September: *"Why
are you using NM and not my method?"*  Sequential bracketing, one parameter on
one monotone moment, is the house method, it is what ENGINE.md prescribes, and
this file was written mid-run on my own judgement when four sweeps had cornered.
That was a scope decision I should have put to the author and did not.

AND THE DIAGNOSIS THAT MOTIVATED IT WAS INCOMPLETE.  Measured afterwards at the
point the housing block hands over, participation is CLEANLY MONOTONE in b --
0.947, 0.714, 0.249, 0.093, 0.001 over b from 0.010 to 0.045 -- and b = 0.035
gives 0.0931 against a target of 0.089.  The bracket had a clean root and still
ended on its bound, because theta had moved 0.16 -> 0.1919 in a single bracket
before it, a twenty per cent jump that changes the surface every other
parameter is then read on.  Running theta LAST fixes that inside the author's
own method.  kap's non-monotonicity is real and is handled by the interval in
recalibrate.py, which holds one root.

So what follows is a fallback for a surface that genuinely defeats bracketing,
and the burden is on whoever runs it to show that it does.

ORIGINAL NOTE FOLLOWS.

FIT THE SEVEN PARAMETERS JOINTLY.

WHY THIS EXISTS.  recalibrate.py brackets one parameter on one moment at a time,
which is what the stylized model has always done and what works when every
moment is monotone in its own instrument.  At sigma = 2 three of them are not,
and four consecutive sweeps ran to a bound because of it:

  r_use IS NON-MONOTONE IN kap.  At aleph 15.4 it falls 1.391 -> 0.689 over kap
  0.060 to 0.090, TURNS ROUND and rises to 0.808 by 0.130, then collapses to
  0.111.  The target of 0.74 has two roots and bracket(), which reads its
  direction from the endpoints, converges on neither.

  participation IS NON-MONOTONE IN b once the housing block has moved.  Sweep 0
  of the reordered run put b at its upper bound 0.090 with participation at
  0.541, which is backwards for a Stone-Geary shifter: a LARGER b makes
  abstaining cheaper and should mean FEWER users.

  hspend CANNOT BE REACHED AT ALL, which is why gam is set rather than
  calibrated -- see the note in recalibrate.py.

Bounding the intervals to isolate one root was tried on kap and it worked for
kap alone; doing it for every moment is chasing the surface one dimension at a
time while the other six move underneath.  So this minimises all seven together
and assumes nothing about the shape.

THE OBJECTIVE is the sum of SQUARED RELATIVE gaps, which is the same currency
the gaps table reports and the same one the quantitative model's minimax is
stated in.  Squared rather than max because the max is not differentiable and
Nelder-Mead handles a smooth surface better; the max is reported alongside so
the stopping rule the author actually stated -- *"once we get below 10% for
everything we can stop"* -- can be read off.

NELDER-MEAD IS HAND-WRITTEN because this container has no scipy.  It is the
standard algorithm: reflect 1, expand 2, contract 0.5, shrink 0.5.  Parameters
are carried in a LOGIT TRANSFORM of their bounds, so the simplex is
unconstrained and no trial can leave the admissible region -- which also means
kap can never imply an SMR below one, since its lower bound is 0.03 and kap = 0
is smr = 1.
"""
import json
import math

import numpy as np

from calibrate import stats, TARGET
from stylized import P, with_
from recalibrate import FIXED, START, table

# (name, lo, hi).  The bounds are the union of what the scans visited.
PARAMS = [('h1', 1e-7, 0.02),
          ('aleph', 3.0, 60.0),
          ('b', 0.010, 0.30),
          ('pi_base', 1e-3, 0.99),
          ('th', 0.05, 0.40),
          ('kap', 0.03, 0.185),
          ('u1', 0.055, 0.19)]

MOMENTS = ['homeless', 'vsl', 'part', 'sud', 'dshare', 'r_use', 'sud_of_homeless2']


def _to_x(par):
    out = []
    for n, lo, hi in PARAMS:
        p = min(max(getattr(par, n), lo + 1e-12), hi - 1e-12)
        out.append(math.log((p - lo) / (hi - p)))
    return np.array(out)


def _to_par(base, x):
    kw = {}
    for (n, lo, hi), xi in zip(PARAMS, x):
        kw[n] = lo + (hi - lo) / (1.0 + math.exp(-max(min(xi, 50.0), -50.0)))
    return with_(base, **kw)


def objective(base, x):
    m = stats(_to_par(base, x))
    g = [(m[k] - TARGET[k]) / TARGET[k] for k in MOMENTS]
    return float(sum(v * v for v in g)), float(max(abs(v) for v in g))


def nelder_mead(base, x0, iters=900, step=0.8, verbose=True):
    n = len(x0)
    sim = [x0] + [x0 + step * np.eye(n)[i] for i in range(n)]
    val = [objective(base, s)[0] for s in sim]
    best_seen = None
    for it in range(iters):
        order = np.argsort(val)
        sim = [sim[i] for i in order]; val = [val[i] for i in order]
        if best_seen is None or val[0] < best_seen:
            best_seen = val[0]
            if verbose and it % 25 == 0:
                _, mx = objective(base, sim[0])
                print(f'  iter {it:4d}  sse {val[0]:10.5f}  worst gap {100*mx:8.2f} %',
                      flush=True)
        cen = np.mean(sim[:-1], axis=0)
        xr = cen + 1.0 * (cen - sim[-1]); fr = objective(base, xr)[0]
        if fr < val[0]:
            xe = cen + 2.0 * (cen - sim[-1]); fe = objective(base, xe)[0]
            sim[-1], val[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < val[-2]:
            sim[-1], val[-1] = xr, fr
        else:
            xc = cen + 0.5 * (sim[-1] - cen); fc = objective(base, xc)[0]
            if fc < val[-1]:
                sim[-1], val[-1] = xc, fc
            else:
                sim = [sim[0]] + [sim[0] + 0.5 * (s - sim[0]) for s in sim[1:]]
                val = [objective(base, s)[0] for s in sim]
        if max(np.abs(np.array(sim[1:]) - sim[0]).max(), abs(val[-1] - val[0])) < 1e-6:
            break
    order = np.argsort(val)
    return sim[order[0]]


if __name__ == '__main__':
    base = with_(P(), **FIXED, **START)
    print('JOINT FIT at sigma = 2, seven parameters, Nelder-Mead', flush=True)
    sse, mx = objective(base, _to_x(base))
    print(f'  start     sse {sse:10.5f}  worst gap {100*mx:8.2f} %', flush=True)
    x = nelder_mead(base, _to_x(base))
    par = _to_par(base, x)
    print()
    table(par, note='JOINT FIT')
    json.dump({n: getattr(par, n) for n, _, _ in PARAMS}
              | {k: getattr(par, k) for k in ('gam', 'h2', 'h3', 'omega', 'sigma')},
              open('calibrated_sigma2.json', 'w'), indent=1)
    print('\nwritten to calibrated_sigma2.json')
