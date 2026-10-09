"""Is there a log calibration with users in ONE band, as in the benchmark?  kappa is held on a grid; at each
value aleph, theta and cbar are fitted to the VSL, the spending share and the food share (b inside on
participation), exactly as gradient._resid does without the users'-income row.  The users' income and the
bands that result are then read off.  A single-band calibration exists if r_use crosses 0.74 with one band.

usage: python3 code/stylized/referee_item7/log_utility/single_band_search.py
"""
import json
import os
from multiprocessing import Pool

import numpy as np
from scipy.optimize import least_squares

from common import G, FIX_LOG, OUT

KAPPAS = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 30.0, 34.0]
START = dict(aleph=4.02, b=0.0027, theta=0.204, cbar=0.0985)   # start_0, which ended in a middle band


def resid(z, kappa, state):
    al, th, cb = np.exp(z)
    q = G.full([al, state['b'], th, kappa, cb], FIX_LOG)
    try:
        q['b'] = state['b'] = G.b_for_part(q, G.TARGET['part'], state['b'])
    except ValueError:
        return np.full(3, 10.0)
    m = G.moments(q)
    return np.array([m[k] / G.TARGET[k] - 1.0 for k in ('vsl', 'dshare', 'fshare')])


def run(kappa):
    state = dict(b=START['b'])
    r = least_squares(resid, np.log([START['aleph'], START['theta'], START['cbar']]), args=(kappa, state),
                      diff_step=1e-4, xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=200)
    al, th, cb = np.exp(r.x)
    q = G.full([al, state['b'], th, kappa, cb], FIX_LOG)
    q['b'] = G.b_for_part(q, G.TARGET['part'], state['b'])
    m = G.moments(q)
    d = m['dist']
    out = dict(kappa=kappa, aleph=al, b=q['b'], theta=th, cbar=cb, maxerr3=float(np.abs(r.fun).max()),
               r_use=float(m['r_use']), vsl=float(m['vsl']), dshare=float(m['dshare']), fshare=float(m['fshare']),
               bands=[(float(lo), float(hi), 100 * float(d.F(lo)), 100 * float(d.F(hi))) for lo, hi in m['intervals']])
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    with Pool(os.cpu_count()) as pool:
        res = pool.map(run, KAPPAS, chunksize=1)
    json.dump(res, open(os.path.join(OUT, 'single_band_search.json'), 'w'), indent=1)
