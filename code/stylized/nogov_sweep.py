"""
THE NO-GOVERNMENT STAGE 1, FITTED BY SWEEPS (8 October).

The author: "the unemployment risk should just happen in period 2. So everyone is employed in period 1",
"We should also not have ui.. Just full income loss", "U1 should be set such that the fraction homeless and
with Sud matches the data. Like the old calibration.... Just a simpler model. All the targets are the same".
The model is stylized.py with stages.NOGOV_SET (no voucher or UI; everyone at work in period 1; saving, housing
and the street kept; food assistance kept as a floor under consumption, fitted on SNAP spending -- see stages.py).

WHY NOT stages.py's STEP RULE.  Run twice on 8 October (stage1_nogov_run1.log, stage1_nogov.log) it parked
participation near zero: raising aleph to lift the VSL raises the cost of dying for everyone, and b, capped
at a small step a pass, could not follow, so a handful of grid nodes used and r_use and the drug share froze
for fifty passes at a time.  Here every parameter is bisected exactly on its own moment in turn, and b is
re-solved on participation after every move -- inside every trial for the three whose moments are read off
the users (kappa on r_use, theta on the drug share, u1 on the SUD share of the homeless) -- so participation
is on target throughout.

usage:  STYLIZED_WORKERS=4 python3 nogov_sweep.py [start.json] [sweeps]
        -> calibrated_stage1_nogov.json after every parameter (the exit vector is the one kept)
"""
import json
import math
import os
import sys
import time

import numpy as np

import stages
from stylized import P, with_
import calibrate as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'calibrated_stage1_nogov.json')
TGT = dict(vsl=float(stages.STAGE2_VSL), hspend=0.268, homeless=C.TARGET['homeless'], part=C.TARGET['part'],
           unemployment=0.0485, sud_of_homeless2=0.217, r_use=C.TARGET['r_use'], dshare=stages.DSHARE_TARGET,
           fshare=stages.FS_TARGET)
# (parameter, moment, lower bound, upper bound, b re-solved inside every trial)
ROWS = [('kap', 'r_use', 0.03, 0.70, True),
        ('aleph', 'vsl', 3.0, 60.0, False),
        ('h1', 'homeless', 0.001, 0.095, False),
        ('gam', 'hspend', 0.05, 0.60, False),
        ('th', 'dshare', 0.05, 0.45, True),
        ('u1', 'sud_of_homeless2', None, 0.40, True),
        ('u0', 'unemployment', 0.005, 0.30, False),
        ('cbar', 'fshare', 0.01, 0.40, False)]
NB, NP = 18, 13          # bisection steps for b and for each parameter


def stats(par):
    """calibrate.stats plus the unemployment rate, which sr_calibrate.moments adds the same way."""
    m = C.stats(par)
    m['unemployment'] = (1.0 - m['sud']) * par.u0 + m['sud'] * par.u1
    return m


def bracket(par, name, mom, lo, hi, iters, tgt):
    rising = stats(with_(par, **{name: hi}))[mom] > stats(with_(par, **{name: lo}))[mom]
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        if (stats(with_(par, **{name: mid}))[mom] > tgt) == rising:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def fit_b(par):
    return bracket(par, 'b', 'part', 1e-4, 1.5, NB, TGT['part'])


def solve_row(par, name, mom, lo, hi, inner):
    def at(v):
        q = with_(par, **{name: v})
        if inner:
            q = with_(q, b=fit_b(q))
        return stats(q)[mom], q
    f_lo, f_hi = at(lo)[0], at(hi)[0]
    tgt = TGT[mom]
    if (f_lo - tgt) * (f_hi - tgt) > 0:
        # not bracketed: take the end nearer the target and say so
        v = lo if abs(f_lo - tgt) < abs(f_hi - tgt) else hi
        print(f'    {name}: {mom} not bracketed on [{lo:.4g}, {hi:.4g}] ({f_lo:.4g}, {f_hi:.4g} vs {tgt:.4g}); '
              f'at {v:.4g}', flush=True)
        return at(v)[1]
    rising = f_hi > f_lo
    for _ in range(NP):
        mid = math.sqrt(lo * hi)
        if (at(mid)[0] > tgt) == rising:
            hi = mid
        else:
            lo = mid
    q = at(math.sqrt(lo * hi))[1]
    return q if inner else with_(q, b=fit_b(q))


def report(par, tag):
    m = stats(par)
    gaps = {k: 100 * (m[k] / TGT[k] - 1) for k in TGT}
    worst = max(abs(g) for g in gaps.values())
    print(f'  {tag}: worst {worst:.2f} %  ' + '  '.join(f'{k}={m[k]:.4g}({gaps[k]:+.1f}%)' for k in TGT), flush=True)
    print('      ' + '  '.join(f'{k}={getattr(par, k):.5g}' for k in ('aleph', 'gam', 'h1', 'b', 'u0', 'u1', 'kap', 'th',
                                                                         'cbar')),
          flush=True)
    return m, worst


def save(par, m, worst, it):
    out = {k: getattr(par, k) for k in ('aleph', 'gam', 'h1', 'b', 'u0', 'u1', 'kap', 'th', 'cbar', 'rho_fs', 'beta', 'pi_base',
                                       'h2', 'h3', 'xi', 'omega', 'delta_d', 'y_floor', 'pV', 'cbar', 'repl',
                                       'emp1', 'repl', 'ycap', 'ui_sud', 'ui_sud_excess', 'rest', 'fert', 'psi',
                                       'fert_s', 'glow')}
    out.update(_stage='1_nogov', _iteration=it, _worst_gap_pc=round(worst, 3),
               _moments={k: (float(v) if isinstance(v, (int, float, np.floating)) else None) for k, v in m.items()},
               _targets=TGT)
    json.dump(out, open(OUT, 'w'), indent=1)


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else 'start_stage1_nogov.json'
    sweeps = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    v = json.load(open(os.path.join(HERE, start)))
    v = {k: x for k, x in v.items() if not k.startswith('_')}
    v.update(stages.STAGE_SET[1])
    v.update(stages.NOGOV_SET)
    par = with_(P(), **v)
    t = time.time()
    par = with_(par, b=fit_b(par))
    m, worst = report(par, f'start, b refit ({time.time() - t:.0f}s)')
    for s in range(1, sweeps + 1):
        for name, mom, lo, hi, inner in ROWS:
            t = time.time()
            lo = (par.u0 + 1e-3) if lo is None else lo
            par = solve_row(par, name, mom, lo, hi, inner)
            m, worst = report(par, f'sweep {s} after {name} ({time.time() - t:.0f}s)')
            save(par, m, worst, s)
        print(f'SWEEP {s} DONE worst {worst:.2f} %', flush=True)
        if worst < 2.0:
            print('every gap inside 2 per cent, stopping', flush=True)
            break


if __name__ == '__main__':
    main()
