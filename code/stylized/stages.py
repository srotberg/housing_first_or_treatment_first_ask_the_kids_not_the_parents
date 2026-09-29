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
           delta_d.  omega_c is fitted on the child use gap and delta_d is set
           from Nilsson (2017) as in the quantitative model (see
           DELTA_D_NILSSON), and every stage-1 parameter is refitted.
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
    # NO INCOME FLOOR (the author, 29 September: "there doesnt need to be a minimum
    # UI", "it is just a proportion of income up to a cap").  At 0.099 it no longer
    # did its old job: the share of period-2 states with a negative value of life
    # was 2.07 per cent with it and 2.19 without at stage 1 (0.88 and 0.96 at stage 2).
    v['y_floor'] = 0.0
    return v


# delta_d IS SET, AS IN THE QUANTITATIVE MODEL, not fitted.  Nilsson (2017)'s 24 per
# cent earnings loss is penalty_child_addicted = 0.24 there, a proportional cut; in
# logs, which is how stylized.py applies it, that is -log(1 - 0.24).  Fitted on the
# child's SUD odds ratio of 2, as sr_calibrate.py does, it ran to its bound of 1.0
# (a 63 per cent cut) in the 13 September run without reaching the target, so the
# odds ratio is reported beside it instead, as the quantitative model reports its.
DELTA_D_NILSSON = -math.log(1.0 - 0.24)


# THE DRUG SPENDING TARGET IS THE QUANTITATIVE MODEL'S, read from its declaration.
# sr_calibrate.py aims theta at 0.14098, data/drug_spending_target.csv's figure with
# the open top income band at 125,000; the Fortran's drug_spending_share_data is
# 0.16 from 17 September, on the author's instruction, and Section 5 reports it.
# Both sections cite Midgette et al. (2019) for the same moment, the aggregate
# spending of users over their aggregate income, so the two models aim at one
# number.  Changed 28 September.
sys.path.insert(0, os.path.join(HERE, '..', 'paper'))
from fortran_consts import constants as _fc
DSHARE_TARGET = float(_fc()['drug_spending_share_data'])


def spec(stage):
    out = []
    for r in FULL_SPEC:
        if stage == 1 and r[0] in CHILD_ROWS:
            continue
        if r[0] == 'delta_d':
            r = (r[0], r[1], r[2], r[3], 0.0, r[5], r[6])
        if r[0] == 'th':
            r = (r[0], r[1], DSHARE_TARGET, r[3], r[4], r[5], r[6])
        if r[0] == 'u1':
            # u1 IS CALIBRATED on the SUD share of the homeless (the author, 29
            # September: "i think u1 can be calibrated"), with the sign MEASURED on
            # this model, floor off, b refit on participation (probe_u1.py): the
            # share FALLS in u1, 25.4 per cent at u1 = 0.048 against 16.3 at 0.108,
            # because the job-loss risk deters the poorest users and b's refit
            # replaces them with richer ones.  The 21.7 per cent target lies between
            # the two, above u0, so the rule lowers u1 when the share is short.
            r = (r[0], r[1], r[2], -1, 0.40, r[5], r[6])
        out.append(r)
    return out


# HOMELESSNESS IS QUANTISED on this income grid -- across twenty-eight tables on
# 13 September it took two values, 0.0096 and 0.0103, either side of the target --
# so its row is held to four per cent and every other live row to two; the author
# stopped the 13 September run at 3.1 per cent on this row for that reason.  The
# gap is scaled so that a single tolerance of two per cent applies to all.
ROW_TOL = {'homeless': 4.0}


def live_worst(m):
    gaps = [abs(m[mom] - tgt) / tgt * 100 * 2.0 / ROW_TOL.get(mom, 2.0)
            for name, mom, tgt, sgn, adj, lo, hi in S.SPEC
            if adj > 0 and m.get(mom) is not None]
    held = [name for name, mom, tgt, sgn, adj, lo, hi in S.SPEC
            if adj > 0 and m.get(mom) is None]
    return math.inf if held else max(gaps)


def save(par, stage, it, m, worst):
    names = sorted({r[0] for r in FULL_SPEC} | set(STAGE_SET[stage]) |
                   {'pi_base', 'beta', 'y_floor', 'u1', 'xi', 'omega', 'delta_d'})
    out = {'_stage': stage, '_iteration': it, '_worst_gap_pc': round(worst, 3),
           '_moments': {k: (round(v, 6) if isinstance(v, float) else v)
                        for k, v in m.items() if not isinstance(v, (list, dict, np.ndarray))}}
    out.update({k: float(getattr(par, k)) for k in names})
    json.dump(out, open(os.path.join(HERE, f'calibrated_stage{stage}.json'), 'w'), indent=1)


def calibrate(stage, iters=6000, tol=2.0, every=25, resume=None):
    S.SPEC = spec(stage)
    if stage == 1:
        v = start_vector()
        if resume:
            r = json.load(open(os.path.join(HERE, resume)))
            v.update({k: x for k, x in r.items() if not k.startswith('_')})
            v['y_floor'] = 0.0          # the floor is off whatever the file says
            print(f'  resumed from {resume}: {r.get("_from", "")}')
    else:
        prev = json.load(open(os.path.join(HERE, 'calibrated_stage1.json')))
        v = {k: x for k, x in prev.items() if not k.startswith('_')}
        # delta_d is set.  omega_c STARTS AT 0.01 AND MAY STEP 1 PER CENT A PASS.
        # Measured 28 September: at stage 1's vector with the child added and
        # omega_c at the 13 September 0.00055, the child use gap is 0.25 per cent
        # against 18.3, and the gap is close to linear in omega_c there, so the
        # target sits near 0.04.  At sr_calibrate's cap of 0.05 per cent a pass
        # that is some 8,000 passes away; the sign-flip ratchet still damps it
        # if it overshoots.
        v.update(omega=0.01, delta_d=DELTA_D_NILSSON)
        S.PER_PARAM_STEP['omega'] = 0.01
        # A WARM START FOR omega_c (29 September).  With the floor off, omega_c =
        # 0.01 made the child gap 91 per cent at iteration 50 and participation
        # 4.2, and omega_c moves a per cent a pass, so it starts at the floor-era
        # stage 2 value instead; everything else starts at stage 1's exit.
        f1, f2 = (os.path.join(HERE, f'calibrated_stage{k}_floor.json') for k in (1, 2))
        if os.path.exists(f1) and os.path.exists(f2):
            o1, o2 = json.load(open(f1)), json.load(open(f2))
            # ONLY omega_c.  Scaling the others by the floor-era shift as well
            # (tried first) put the start on the corner branch, drug share 0.092
            # against CORNER = 0.10, where the drug moments are not read.
            v['omega'] = o2['omega']
            print('  warm start, omega_c from the floor-era stage 2: ' +
                  ', '.join(f'{k}={v[k]:.5g}' for k in ('aleph', 'b', 'th', 'omega', 'u1', 'kap')))
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
            S.table(par, m, it)
            # THE STOPPING RULE READS THE LIVE ROWS ONLY.  sr_calibrate's table
            # counts every row with a moment, including a held one (u1, adjuster
            # zero), whose gap nothing can close, so its worst never falls below
            # the tolerance and the loop would run to its cap.
            worst = live_worst(m)
            print(f'  LIVE    worst {worst:.2f} %  over '
                  f'{", ".join(r[0] for r in S.SPEC if r[4] > 0)}')
            sys.stdout.flush()
            save(par, stage, it, m, worst)
            if worst < tol:
                print(f'\n  every gap inside {tol} per cent at iteration {it}, stopping')
                break
        # THE BRANCH GUARD IS USED, which sr_calibrate's own loop does not: stage 1
        # run with the plain step alternated between the interior and the corner
        # every 25 to 50 passes (stage1.log, iterations 350 to 525), with b and
        # theta chasing a drug share that kept collapsing.  step_on_branch halves
        # a step that would leave the interior and lets a step taken from the
        # corner climb out.
        par = S.step_on_branch(par, m, state)
    else:
        m = S.moments(par, iters)
        S.table(par, m, iters)
        worst = live_worst(m)
        save(par, stage, iters, m, worst)
    print(f'\nSTAGE {stage} EXIT: iteration {it}, worst gap {worst:.2f} per cent, '
          f'written to calibrated_stage{stage}.json')
    return par


if __name__ == '__main__':
    calibrate(int(sys.argv[1]), resume=sys.argv[2] if len(sys.argv) > 2 else None)
