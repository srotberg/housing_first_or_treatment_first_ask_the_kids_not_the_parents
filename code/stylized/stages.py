"""
THE STYLIZED MODEL BUILT IN STAGES, each one recalibrated.

The author, 28 September: *"build the model slowly. First, without the children or
externalities. Then add them after showing the income reversal and that tf is not
optimal. Then add the children and kappax"*, and *"recalibrate each stage"*.

  STAGE 1  THE BASELINE. No child in the household (xi = 1 in period 1 as in
           period 2), no weight on one (omega_c = 0) and no penalty (delta_d = 0),
           so nothing a household does lands on anybody else.  Every parameter
           that remains is fitted with the author's rule on its own moment.
  STAGE 2  THE CHILD, as CHILD_FLOW_UTILITY.md specifies it: the child shares the
           period-1 bundle through xi = sqrt 2, the parent weighs it at omega_c,
           and a parent who acquires the disorder cuts its child's income by
           delta_d.  omega_c is fitted on the child use gap and delta_d on the
           child's SUD odds ratio, and every stage-1 parameter is refitted with
           them.
  STAGE 3  kappa_x, the disamenity of aggregate homelessness, solved from the
           willingness to pay in Loubiere et al. (2020).  It enters welfare and no
           choice, as in the quantitative model with internalise_homelessness_cost
           = 0, so stage 2's calibration stands unchanged and is not rerun.

THE RULE AND ITS SETTINGS ARE sr_calibrate.py's, unchanged: one relative step on
every parameter at once, the sign-flip ratchet, the per-parameter step caps and
the runaway probe.  This file chooses only which rows of its SPEC are live at
each stage and what is switched off.

THE STARTING POINT IS sr_calibrate.py's OWN, the last one it ran from (its
__main__: recalibrate.FIXED and START, then its SEED, then y_floor 0.099).
calibrated_sep13.json does NOT reproduce under the current code -- measured 28
September, participation 0.0554 against the 0.0887 it records and the drug share
in the corner -- so it is a record, not a start.

THE CHILD DAMAGE IS SHORT-CIRCUITED WHERE IT IS EXACTLY ZERO.  stats() solves the
child damage to a fixed point on every call, which costs two full solves even when
the answer is known: with omega_c = 0 it multiplies nothing and with delta_d = 0
it is identically zero.  Those two cases return chdmg = 0 directly, which is exact,
and every other case is solved as before.

usage:  STYLIZED_WORKERS=1 python3 stages.py 1          -> calibrated_stage1.json
        STYLIZED_WORKERS=1 python3 stages.py 2          -> calibrated_stage2.json
                                                           (starts from stage 1's)
"""
import json
import math
import os
import sys

import numpy as np

import stylized as ST
from stylized import P, with_
import calibrate as C
import sr_calibrate as S

HERE = os.path.dirname(os.path.abspath(__file__))

_solve = ST.solve_child_damage


def _solve_or_zero(par, *a, **k):
    if par.omega == 0.0 or par.delta_d == 0.0:
        return with_(par, chdmg=0.0)
    return _solve(par, *a, **k)


C.solve_child_damage = _solve_or_zero
S.solve_child_damage = _solve_or_zero

FULL_SPEC = list(S.SPEC)
CHILD_ROWS = ('omega', 'delta_d')

STAGE_SET = {
    1: dict(xi=1.0, omega=0.0, delta_d=0.0),
    2: dict(xi=2.0 ** 0.5),
}


def start_vector():
    """sr_calibrate.py's own start, in the order its __main__ applies it."""
    from recalibrate import FIXED, START
    v = {**{k: x for k, x in FIXED.items() if k != 'kap'},
         **{**START, 'th': 0.25, 'beta': 0.995 ** 30, 'kap': 1.0 - 0.91 ** 2,
            'delta_d': 0.24, 'y_floor': 0.0, 'h1': 0.005, 'b': 0.07}}
    v.update(dict(aleph=12.45683, gam=0.44351, h1=0.01017, b=0.05110,
                  pi_base=0.0368 / 0.089, u0=0.04622, u1=0.10814, omega=0.00065,
                  delta_d=0.85980, kap=0.10748, th=0.14962))
    v['y_floor'] = 0.099
    return v


def spec(stage):
    return [r for r in FULL_SPEC if stage >= 2 or r[0] not in CHILD_ROWS]


def save(par, stage, it, m, worst):
    names = sorted({r[0] for r in FULL_SPEC} | set(STAGE_SET[stage]) |
                   {'pi_base', 'beta', 'y_floor', 'u1', 'xi', 'omega', 'delta_d'})
    out = {'_stage': stage, '_iteration': it, '_worst_gap_pc': round(worst, 3),
           '_moments': {k: (round(v, 6) if isinstance(v, float) else v)
                        for k, v in m.items() if not isinstance(v, (list, dict, np.ndarray))}}
    out.update({k: float(getattr(par, k)) for k in names})
    json.dump(out, open(os.path.join(HERE, f'calibrated_stage{stage}.json'), 'w'), indent=1)


def calibrate(stage, iters=6000, tol=2.0, every=25):
    S.SPEC = spec(stage)
    if stage == 1:
        v = start_vector()
    else:
        prev = json.load(open(os.path.join(HERE, 'calibrated_stage1.json')))
        v = {k: x for k, x in prev.items() if not k.startswith('_')}
        # the child's two parameters start where the 13 September fit left them
        v.update(omega=0.01518, delta_d=0.57906)
    v.update(STAGE_SET[stage])
    par = with_(P(), **v)
    print(f'STAGE {stage}: {len(S.SPEC)} parameters live: '
          f'{", ".join(r[0] for r in S.SPEC if r[4] > 0)}; held: '
          f'{", ".join(r[0] for r in S.SPEC if r[4] == 0) or "none"}')
    print('  set: ' + ', '.join(f'{k}={getattr(par, k):.5g}' for k in
                                ('xi', 'omega', 'delta_d', 'beta', 'R', 'y_floor', 'u1',
                                 'h2', 'h3', 'rho', 'pV', 'kappa_r', 'pi_base')), flush=True)
    # THE EXIT PASS IS WHAT IS KEPT, never the best pass seen (standing rule): the
    # file is rewritten at every table as a checkpoint and last at the pass the
    # loop stops on, and that vector is the one every later stage and result reads.
    state = {}
    for it in range(iters):
        m = S.moments(par, it)
        if it % every == 0:
            worst = S.table(par, m, it)
            sys.stdout.flush()
            save(par, stage, it, m, worst)
            if worst < tol:
                print(f'\n  every gap inside {tol} per cent at iteration {it}, stopping')
                break
        par, _ = S.step(par, m, state)
    else:
        m = S.moments(par, iters)
        worst = S.table(par, m, iters)
        save(par, stage, iters, m, worst)
    print(f'\nSTAGE {stage} EXIT: iteration {it}, worst gap {worst:.2f} per cent, '
          f'written to calibrated_stage{stage}.json')
    return par


if __name__ == '__main__':
    calibrate(int(sys.argv[1]))
