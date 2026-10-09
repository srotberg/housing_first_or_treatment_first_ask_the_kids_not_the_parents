"""Users' income against kappa near the log calibration, aleph, theta and cbar held at their log-calibrated
values, every b-root that gives 8.90 per cent participation found by a grid in b.  Shows how users' income
moves from the top to the bottom as kappa rises, and whether one middle band ever gives 0.74.

usage: python3 code/stylized/referee_item7/log_utility/kappa_fine_scan.py
"""
import json
import os
from multiprocessing import Pool

import numpy as np

from common import OUT, load_log
from part_of_b import roots

Q = load_log()
KS = list(np.round(np.linspace(10.0, 14.0, 41), 3)) + [11.954205318975035]


def run(k):
    return dict(kappa=float(k), roots=roots(Q['aleph'], Q['theta'], float(k), Q['cbar']))


if __name__ == '__main__':
    with Pool(os.cpu_count()) as pool:
        res = sorted(pool.map(run, KS, chunksize=1), key=lambda r: r['kappa'])
    json.dump(res, open(os.path.join(OUT, 'kappa_fine_scan.json'), 'w'), indent=1)
    for r in res:
        print(f"{r['kappa']:.3f}", [(f"{x['r_use']:.3f}", x['bands']) for x in r['roots']])
