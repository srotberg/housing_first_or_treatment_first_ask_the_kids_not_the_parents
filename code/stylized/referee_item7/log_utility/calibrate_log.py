"""Step 1: recalibrate all five internal parameters jointly at sigma = 1, exactly as gradient.calibrate does
(aleph on the VSL, theta on the spending share, kappa on the users' income, cbar on the food share, b inside
on participation), to the same targets, from several starting points in parallel.

usage: python3 code/stylized/referee_item7/log_utility/calibrate_log.py
"""
import json
import os
from multiprocessing import Pool

import numpy as np

from common import G, FIX_LOG, BENCH, OUT

KEYS = ('vsl', 'part', 'dshare', 'r_use', 'fshare')
# STARTING POINTS.  The earlier scan (c_scan.json, log80, unemployment on) has users' income crossing 0.74
# between kappa 26.6 (b 0.00266) and 29.1 (b 0.00247) at aleph 4.18 and theta 0.222.
STARTS = [dict(aleph=al, b=b, theta=th, kappa=k, cbar=0.0977)
          for al, b, th, k in [(4.18, 0.00266, 0.222, 27.0), (4.18, 0.00266, 0.18, 27.5), (4.18, 0.00255, 0.20, 28.0),
                               (4.18, 0.0026, 0.16, 26.0), (4.0, 0.0025, 0.20, 30.0), (4.5, 0.0027, 0.22, 25.0),
                               (4.18, 0.0024, 0.22, 33.0), (3.8, 0.0026, 0.19, 35.0)]]


def run(s):
    try:
        q = G.calibrate(dict(s), fixed=FIX_LOG)
        m = G.moments(q)
        mom = {k: float(m[k]) for k in KEYS}
        err = max(abs(mom[k] / G.TARGET[k] - 1.0) for k in KEYS)
        return dict(start=s, q={k: (float(v) if not isinstance(v, bool) else v) for k, v in q.items()},
                    moments=mom, maxrelerr=err, bands=[list(map(float, iv)) for iv in m['intervals']])
    except Exception as e:  # noqa: BLE001
        return dict(start=s, error=repr(e))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with Pool(os.cpu_count()) as pool:
        res = pool.map(run, STARTS, chunksize=1)
    for r in res:
        print(r['start'], '->', r.get('error') or
              (', '.join(f"{k}={r['q'][k]:.5g}" for k in G.FREE), f"maxrelerr={r['maxrelerr']:.2e}"), flush=True)
    ok = [r for r in res if 'error' not in r]
    best = min(ok, key=lambda r: r['maxrelerr'])
    bm = G.moments(BENCH)
    best['bench'] = dict(q={k: BENCH[k] for k in G.FREE}, moments={k: float(bm[k]) for k in KEYS})
    best['targets'] = {k: float(G.TARGET[k]) for k in KEYS}
    best['all_starts'] = res
    json.dump(best, open(os.path.join(OUT, 'log_calibration.json'), 'w'), indent=1)
    print('BEST', best['q'], best['moments'], best['maxrelerr'])
