"""Referee item 7, claim C: does the mortality channel reverse the income gradient without sigma = 2 and an
additive value of life?  Partial equilibrium (the Section 3 model has no prices to clear).

Variants, everything else at gradient.json:
  base   sigma = 2, additive aleph            (the paper)
  log    sigma = 1, additive aleph
  prop   sigma = 2, value of life aleph * y   (proportional to permanent income; equal to aleph at mean income)
  logprop sigma = 1, aleph * y
  log80   sigma = 1, additive aleph refitted so the VSL at mean income is 80, as in the benchmark
  vslprop sigma = 2, value of life aleph * y^(1-sigma), so the VSL (value over marginal utility) is
          proportional to income, as it roughly is under log with additive aleph; equal to aleph at mean income
For each, kappa_phi_d - 1 is scaled by x over a wide range, either with the unemployment channel off (u1 = u0,
Figure 1's mortality curve) or with u1 at its calibrated value, and b is refitted at every point so that
participation stays at the calibrated 8.90 per cent, walking from x = 0 as gradient.scan does.

The value-of-life switch is made in a scratch copy of gradient.py's source, loaded in memory: the two places
aleph enters utility (W and plan) read aleph * y when q['aleph_prop'] is set.  gradient.py itself is untouched.

usage: python3 code/stylized/referee_item7/c_curvature_scan.py   (uses every core)
"""
import json, math, os, sys, types
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, SRC)

src = open(os.path.join(SRC, 'gradient.py')).read()
old_w = "u * _U0(a + q['cbar'], q) + q['aleph']"
old_p = "V = flow(y - a + f) + q['aleph'] + bt * cont(a)"
assert src.count(old_w) == 1 and src.count(old_p) == 1
src = src.replace(old_w, "u * _U0(a + q['cbar'], q) + _al(q, y)")
src = src.replace(old_p, "V = flow(y - a + f) + _al(q, y) + bt * cont(a)")
src += "\n\ndef _al(q, y):\n    y = np.asarray(y, dtype=float)\n    if q.get('aleph_vsl'):\n        return q['aleph'] * y ** (1.0 - q['sigma'])\n    return q['aleph'] * (y if q.get('aleph_prop') else 1.0)\n"
G = types.ModuleType('gradient_scratch')
G.__file__ = os.path.join(SRC, 'gradient.py')
exec(compile(src, 'gradient_scratch', 'exec'), G.__dict__)

Q = json.load(open(os.path.join(SRC, 'gradient.json')))
# LOG WITH aleph REFITTED SO THE VSL AT MEAN INCOME IS STILL 80 (at the benchmark aleph, log gives about 251)
from scipy.optimize import brentq  # noqa: E402
ALEPH_LOG80 = brentq(lambda al: G.vsl({**Q, 'sigma': 1.0, 'aleph': al}) - 80.0, -5.0, Q['aleph'])
PART = G.TARGET['part']
XS = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0, 20.0, 35.0, 60.0, 100.0]
VARIANTS = dict(base=dict(sigma=2.0), log=dict(sigma=1.0), prop=dict(sigma=2.0, aleph_prop=True),
                logprop=dict(sigma=1.0, aleph_prop=True),
                vslprop=dict(sigma=2.0, aleph_vsl=True), log80=dict(sigma=1.0, aleph=ALEPH_LOG80))


def run(job):
    var, unemp = job
    q0 = {**Q, **VARIANTS[var]}
    if unemp == 'off':
        q0['u1'] = q0['u0']
    dist = G.Dist(q0['sig_y'], q0['y_min'])
    ysg = dist.quantile(1.0 - PART)
    b = q0['theta'] * ysg / ((1.0 - q0['theta']) * q0['p_v'])
    out = []
    for x in XS:
        g = {**q0, 'kappa': 1.0 + x * (Q['kappa'] - 1.0)}
        try:
            g['b'] = b = G.b_for_part(g, PART, b)
            m = G.moments(g)
            iv = [(round(lo, 4), round(hi, 4), round(100 * float(dist.F(lo)), 2), round(100 * float(dist.F(hi)), 2))
                  for lo, hi in m['intervals']]
            out.append(dict(x=x, kappa=g['kappa'], surv_sud=g['phibar'] ** g['kappa'], b=b, part=m['part'],
                            r_use=m['r_use'], bands=iv, v1_bottom=float(G.V1(g['y_min'], g)[0])))
        except Exception as e:      # noqa: BLE001  record and stop the walk: b is refitted from the neighbour
            out.append(dict(x=x, kappa=g['kappa'], error=repr(e)))
            break
        print(var, unemp, x, round(m['r_use'], 4), iv, flush=True)
    return (var, unemp), out


if __name__ == '__main__':
    jobs = [(v, u) for v in VARIANTS for u in ('off', 'cal')]
    with Pool(os.cpu_count()) as pool:
        res = dict(pool.map(run, jobs, chunksize=1))
    outp = os.path.join(SRC, '..', '..', 'results', 'referee_item7', 'c_scan.json')
    json.dump({f'{v}|unemp_{u}': r for (v, u), r in res.items()}, open(outp, 'w'), indent=1)
    print('\nusers mean income / population mean, participation held at', PART)
    print(f'{"x":>6}{"kappa":>8}{"surv1":>7}' + ''.join(f'{v+"|"+u:>13}' for v, u in jobs))
    for i, x in enumerate(XS):
        row = f'{x:6.2f}{1 + x*(Q["kappa"]-1):8.2f}{Q["phibar"]**(1 + x*(Q["kappa"]-1)):7.3f}'
        for j in jobs:
            r = res[j]
            row += f'{r[i]["r_use"]:13.3f}' if i < len(r) and 'r_use' in r[i] else f'{"--":>13}'
        print(row)
