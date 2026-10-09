"""Participation as a function of b at fixed (aleph, theta, kappa, cbar), log utility: every b that gives
8.90 per cent, and the users' income and bands at each.  Shows whether the b-root (and so the band) is unique.

usage: python3 part_of_b.py aleph theta kappa cbar
"""
import sys
import numpy as np
from scipy.optimize import brentq
from common import G, FIX_LOG


def roots(al, th, k, cb, n=160):
    q = G.full([al, 0.003, th, k, cb], FIX_LOG)
    lb = np.linspace(np.log(1e-4), np.log(0.08), n)
    f = np.array([G.moments({**q, 'b': np.exp(x)})['part'] - G.TARGET['part'] for x in lb])
    out = []
    for i in range(1, n):
        if f[i - 1] * f[i] < 0:
            x = brentq(lambda x: G.moments({**q, 'b': np.exp(x)})['part'] - G.TARGET['part'], lb[i - 1], lb[i], xtol=1e-13)
            m = G.moments({**q, 'b': np.exp(x)})
            d = m['dist']
            out.append(dict(b=float(np.exp(x)), r_use=float(m['r_use']), vsl=float(m['vsl']), dshare=float(m['dshare']),
                            bands=[(round(float(lo), 3), round(float(hi), 3), round(100 * float(d.F(lo)), 1),
                                    round(100 * float(d.F(hi)), 1)) for lo, hi in m['intervals']]))
    return out


if __name__ == '__main__':
    for r in roots(*map(float, sys.argv[1:5])):
        print(r)
