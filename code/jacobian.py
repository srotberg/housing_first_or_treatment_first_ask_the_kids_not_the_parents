#!/usr/bin/env python3
"""Move every parameter at once, using how every moment responded to each of them.

WHY THIS REPLACES TWENTY-TWO INDEPENDENT SECANTS. Each arm in a generation
differs from the centre in exactly one parameter, so it measures how ALL
twenty-two moments respond to that one parameter. The secant rule used one
number out of each arm -- the moment that parameter is said to own -- and threw
the other twenty-one away. Those discarded numbers are the cross effects, and
the cross effects are what has been going wrong:

  size_homelessness was moved on its own reading of the homelessness rate and
  took that rate from 0.03 per cent to 12.9 against a target of 0.399, because
  nothing in the rule knew what else was pushing on it;

  theta and lambda each move the total user rate as hard as b does, which had to
  be discovered by hand and patched in as a special case;

  generation four moved nine parameters at once on nine separate readings and
  came back worse, because the readings were individually right and jointly
  wrong.

A Jacobian answers all three at once. J[i][j] is the elasticity of moment i to
parameter j, read straight off the arms. The step solves J d = r for the whole
vector of log parameter changes together, so a parameter that would wreck
another moment is held back by that moment's row rather than by a hand-written
rule.

DAMPED, BECAUSE J IS MEASURED AND NOISY. This is Levenberg-Marquardt: the
damping starts small and is raised until the step fits inside the trust region,
which is what keeps a nearly singular direction from producing an enormous move.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_points                                      # noqa: E402
from suggest_next import points as _vectors               # noqa: E402


def points():
    """(vector, {moment: (model, target)}, filename) for every measured point.

    suggest_next.points gives the vector and the model values; the targets come
    from score_points, which reads them off the same line of the same file. Both
    are needed here because the residual is target over model.
    """
    out = []
    for vec, _mom, name in _vectors():
        _head, mt = score_points.read(os.path.join(HERE, 'points', name))
        if mt:
            out.append((vec, mt, name))
    return out

FLOOR = 1e-8            # a moment at zero is treated as this, so its log exists
MAX_ELASTICITY = 25.0   # a single entry may not dominate the whole solve
TOL = 1e-5              # two parameter values within this are the same value


def read_centre(path=None):
    """The vector the current generation was built around."""
    centre = {}
    for line in open(path or os.path.join(HERE, 'GENERATION.txt')):
        if line.startswith('CENTRE '):
            key, _, value = line[7:].strip().partition('=')
            centre[key] = float(value)
    return centre


def _same_but(a, b, key):
    return all(abs(a[k] - b[k]) <= TOL * max(1.0, abs(b[k])) for k in b if k != key)


def assemble(centre, pts):
    """(moment names, parameter names, J, residual, weights) around the centre.

    A column comes from the arm nearest the centre in that parameter, so the
    elasticity is local rather than an average over the whole range explored.
    """
    ref = None
    for vec, mom, name in pts:
        if set(vec) == set(centre) and _same_but(vec, centre, None):
            ref = (vec, mom, name)
            break
    if ref is None:
        return None
    _rv, rm, rname = ref

    arms = {}
    for vec, mom, name in pts:
        if set(vec) != set(centre) or name == rname:
            continue
        moved = [k for k in vec if abs(vec[k] - centre[k]) > TOL * max(1.0, abs(centre[k]))]
        if len(moved) != 1:
            continue
        key = moved[0]
        step = abs(math.log(max(vec[key], FLOOR) / max(centre[key], FLOOR)))
        if key not in arms or step < arms[key][0]:
            arms[key] = (step, vec, mom)

    moments = sorted(k for k, (m, t) in rm.items()
                     if t and t > 0 and m == m and abs(t) > 1e-12)
    params = sorted(arms)
    if not params or not moments:
        return None

    J = np.zeros((len(moments), len(params)))
    for j, key in enumerate(params):
        _s, vec, mom = arms[key]
        dp = math.log(max(vec[key], FLOOR)) - math.log(max(centre[key], FLOOR))
        if abs(dp) < 1e-12:
            continue
        for i, name in enumerate(moments):
            here = rm[name][0]
            got = mom.get(name)
            there = got[0] if got else None
            if there is None or there != there or here != here:
                continue
            dm = math.log(max(there, FLOOR)) - math.log(max(here, FLOOR))
            e = dm / dp
            J[i][j] = max(-MAX_ELASTICITY, min(MAX_ELASTICITY, e))

    r = np.array([math.log(rm[n][1] / max(rm[n][0], FLOOR)) for n in moments])
    w = np.array([score_points.WEIGHT.get(n, 1.0) for n in moments])
    return moments, params, J, r, w, rname


# HOW FAR A LINEARISATION MAY BE TRUSTED IN MOMENT SPACE, not just parameter
# space. A derivative measured where a moment is two hundred per cent off says
# nothing about the whole distance back to target: the response is flat and then
# cliffs, and the further the step the less the slope means. Bounding the
# PREDICTED move of every moment is the direct expression of that -- a step is
# refused not because some parameter moved a lot but because the linearisation
# claims a moment will move further than a linearisation can be believed over.
MOMENT_CAP = 1.5        # no moment may be predicted to move by more than this factor


def step(centre, pts, trust=1.5, regression=True, moment_cap=None):
    """The log-space move for every parameter, damped to fit the trust region."""
    got = assemble_regression(centre, pts) if regression else None
    how = 'regression over %d points' % (got[5] if got else 0)
    if got:
        moments, params, J, r, w, _n = got
        rname = 'local fit'
    else:
        got = assemble(centre, pts)
        if got is None:
            return None, None
        moments, params, J, r, w, rname = got
        how = 'finite differences'

    W = np.diag(w)
    A = J.T @ W @ J
    bvec = J.T @ W @ r
    limit = math.log(trust)
    # A FINE LADDER, so the step lands ON the trust boundary rather than far
    # inside it. Powers of ten jumped from a step three times too long to one a
    # third of what was allowed, which threw away most of the move the data
    # supported.
    d = None
    for k in range(-24, 41):
        damping = 10.0 ** (k / 4.0)
        try:
            trial = np.linalg.solve(A + damping * np.eye(len(params)), bvec)
        except np.linalg.LinAlgError:
            continue
        predicted = J @ trial
        cap = math.log(moment_cap or MOMENT_CAP)
        if np.max(np.abs(trial)) <= limit and np.max(np.abs(predicted)) <= cap:
            return dict(zip(params, trial)), {
                'moments': moments, 'reference': rname, 'damping': damping,
                'residual': float(np.linalg.norm(r)),
                'used': float(np.max(np.abs(trial)) / limit),
                'how': how,
                'predicted_moment_move': float(np.max(np.abs(predicted))),
                'predicted_residual': float(np.linalg.norm(r - predicted))}
        d = trial
    d = d * (limit / max(np.max(np.abs(d)), 1e-12))
    return dict(zip(params, d)), {'moments': moments, 'reference': rname,
                                  'damping': 'scaled', 'residual': float(np.linalg.norm(r)),
                                  'used': 1.0}


# ---------------------------------------------------------------------------
# THE JACOBIAN FROM EVERY NEARBY POINT, NOT JUST THE ONE-CHANGE ARMS.
#
# Two problems the finite-difference version cannot fix.
#
# IT THROWS AWAY ALMOST EVERYTHING MEASURED. A hundred and fifty-five points
# carry a full vector and a full set of moments, and the finite-difference
# assembly uses one arm per parameter from the current generation and ignores
# the rest. Every round then has to re-measure derivatives that the archive
# already contains, which is what makes a round cost fifteen sessions.
#
# ITS "DERIVATIVES" ARE SECANTS OVER LARGE STEPS. The arm size is scaled to how
# wrong the moment is, up to a factor of three, so a parameter that is badly off
# is probed furthest -- exactly where the response is least linear. On a
# response that is flat and then falls off a cliff, a secant across that range
# is not a derivative and using it as one is how size_homelessness crossed its
# cliff in a single step.
#
# A weighted regression over the archive answers both. Points near the centre
# dominate, points far away still inform the fit weakly, and the ridge term
# keeps the solve conditioned when parameters have not been varied
# independently. The bandwidth is in log-parameter distance, so a point that
# differs by a factor of e in one parameter sits one unit away.
def assemble_regression(centre, pts, bandwidth=0.8, ridge=1e-3):
    """(moments, params, J, residual, weights, n_used) by local weighted regression."""
    params = sorted(centre)
    rows = []
    for vec, mt, name in pts:
        if set(vec) != set(centre):
            continue
        dp = []
        ok = True
        for k in params:
            a, b = vec.get(k), centre.get(k)
            if not a or not b or a <= 0 or b <= 0:
                ok = False
                break
            dp.append(math.log(a / b))
        if ok:
            rows.append((np.array(dp), mt, name))
    if len(rows) < 4:
        return None

    ref = min(rows, key=lambda r: float(np.linalg.norm(r[0])))
    moments = sorted(k for k, (m, t) in ref[1].items()
                     if t and t > 0 and m == m and abs(t) > 1e-12)
    if not moments:
        return None

    X = np.array([r[0] for r in rows])
    w = np.exp(-(np.linalg.norm(X, axis=1) / bandwidth) ** 2)
    A = np.hstack([np.ones((len(rows), 1)), X])
    WA = A * w[:, None]

    J = np.zeros((len(moments), len(params)))
    at_centre = {}
    for i, name in enumerate(moments):
        y = []
        for _dp, mt, _n in rows:
            got = mt.get(name)
            y.append(math.log(max(got[0], FLOOR)) if got else math.log(FLOOR))
        y = np.array(y)
        M = A.T @ WA + ridge * np.eye(A.shape[1])
        try:
            coef = np.linalg.solve(M, A.T @ (w * y))
        except np.linalg.LinAlgError:
            continue
        at_centre[name] = coef[0]                       # the fit's value AT the centre
        for j in range(len(params)):
            J[i][j] = max(-MAX_ELASTICITY, min(MAX_ELASTICITY, coef[1 + j]))

    r = np.array([math.log(ref[1][n][1]) - at_centre.get(n, math.log(max(ref[1][n][0], FLOOR)))
                  for n in moments])
    wt = np.array([score_points.WEIGHT.get(n, 1.0) for n in moments])
    return moments, params, J, r, wt, len(rows)


if __name__ == '__main__':
    centre = read_centre()
    pts = points()
    d, info = step(centre, pts)
    if d is None:
        print('The centre of this generation has not been measured yet, so there '
              'is nothing to differentiate around.')
        raise SystemExit(1)
    print('%s, %d moments, %d parameters, damping %s, step uses %.0f%% of the '
          'trust region, largest predicted moment move %.2fx'
          % (info.get('how', info['reference']), len(info['moments']), len(d),
             info['damping'], 100 * info.get('used', 0),
             math.exp(info.get('predicted_moment_move', 0))))
    print('residual norm in logs: %.3f\n' % info['residual'])
    print('%-52s %12s %12s %8s' % ('parameter', 'now', 'jacobian says', 'factor'))
    print('-' * 90)
    for key in sorted(d, key=lambda k: -abs(d[k])):
        print('%-52s %12.5g %12.5g %8.3f'
              % (key, centre[key], centre[key] * math.exp(d[key]), math.exp(d[key])))