#!/usr/bin/env python3
"""One direction, measured at many lengths, instead of many directions measured once.

WHY THIS REPLACES THE SIMPLEX ROUND. Multi-directional search reflects twenty-one
vertices through the best and each vertex differs from it in ONE coordinate, so a
round of twenty-six points buys twenty-six separate one-coordinate readings and
one scalar out of each. Round three cost twenty-six points and about four hours
of an eight-worker fleet and moved the loss from 0.2834 to 0.2785 -- 1.7 per cent
-- because the moves the calibration actually needs are large and joint, and a
simplex whose vertices are one coordinate from the best cannot express one.

The Jacobian already knows the joint direction. What nobody knows is HOW FAR it
can be trusted, and that is the one thing a fleet of parallel workers is perfectly
shaped to answer: put every worker on the SAME direction at a DIFFERENT length and
read the turning point off the results.

WHAT THE PROBES OF 29 AUGUST PROVED, AT THE COST OF SIX POINTS. Each instrument
was moved on its own moment's reading, taken from the archive point that had come
closest to that moment. Every one did exactly what was predicted OF ITS OWN
MOMENT: pi_eu from +74 per cent to -3, h_2 from +74 to -5, pi_V from -31 to -7,
and b from -31 to +6 as a bonus. Every one also broke moments that were already on
target -- kappa_uem from +18 to +87, kappa_ued from +2 to -47, tau_u from +9 to
+48 -- and stacking four of them collapsed homelessness from +4 per cent to -96.
Both probes scored WORSE than the point they were built from. That is the
diagonal approximation failing exactly as jacobian.py's docstring says generation
four failed: individually right and jointly wrong. A Jacobian row carries the
cross effects, so the solve holds an instrument back when another moment's row
says what it would cost, and pays for it with the other parameters in the SAME
step. That is the whole argument for this file.

THREE DEFECTS IN THE EXISTING SOLVE, FIXED HERE.

  THE REGRESSION JACOBIAN WAS SILENTLY DEAD. assemble_regression demands every
  coordinate be positive so it can fit in logs, and zeta_DI sits at 0.0 in the
  vector, so EVERY row failed the test, the function returned None for all 82
  candidate points, and jacobian.step() has been falling back to finite
  differences without saying so. Non-varying coordinates are simply not search
  coordinates and are dropped here rather than poisoning the fit.

  MOMENTS NOTHING CAN MOVE WERE IN THE FIT. lambda_m carries the second largest
  residual in the whole system, +1.54 in log space, and zeta_DI -- its only
  instrument -- is externally set to zero. score_points excludes it from the loss;
  the Jacobian did not exclude it from the solve, so the step was partly spent
  chasing a moment with no instrument. EXCLUDE is honoured here.

  THE TRUST REGION WAS A GUESS WHERE A MEASUREMENT WAS AVAILABLE. The step is
  refused unless every moment's predicted move is inside max(1.5x, 80 per cent of
  its own gap), which damps it by a factor of a thousand down to a 1.02x parameter
  move. The rule was earned -- a step once carried size_homelessness over its
  cliff -- but it is a guess about where linearity fails, and this file measures
  that instead. A ladder that spans 1.02x to 2.2x sees the cliff rather than
  assuming its position, which is strictly more cautious than trusting either the
  cap or the undamped step.
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jacobian                                          # noqa: E402
import score_points                                      # noqa: E402
from converge import BOUNDS                              # noqa: E402

# THE LADDER IS GEOMETRIC AND SPANS TWO ORDERS OF MAGNITUDE, because the
# question is which order of magnitude is right and a linear ladder answers only
# within one. Read as the largest move any single parameter makes: 1.02x at the
# bottom, which is where the capped step sits today, to 2.23x at the top.
LADDER = (0.02, 0.05, 0.10, 0.18, 0.30, 0.45, 0.62, 0.80)

# A fit needs points that are actually near the centre; beyond this many
# e-folds away in the full vector a point says nothing about the local slope.
BANDWIDTH = 0.8
RIDGE = 0.05


def varying(pts, centre, tol=1e-9):
    """The coordinates that actually move in the archive AND are positive.

    A coordinate pinned at a constant contributes a column of zeros, which the
    ridge then fills with noise; one pinned at zero cannot be fitted in logs at
    all and kills every row. Neither is a search direction, so neither is a
    column.
    """
    out = []
    for k in sorted(centre):
        if centre[k] <= 0:
            continue
        seen = {round(v[k], 12) for v, _m, _n in pts if k in v}
        if len(seen) > 1 and all(x > 0 for x in seen):
            out.append(k)
    return out


def fit(centre, pts, params):
    """Local weighted log-log regression of every usable moment on every param."""
    rows = []
    for vec, mt, name in pts:
        if any(k not in vec or vec[k] <= 0 for k in params):
            continue
        dp = np.array([math.log(vec[k] / centre[k]) for k in params])
        rows.append((dp, mt, name))
    if len(rows) < len(params) // 2:
        return None

    ref = min(rows, key=lambda r: float(np.linalg.norm(r[0])))
    moments = sorted(k for k, (m, t) in ref[1].items()
                     if k not in score_points.EXCLUDE and jacobian.usable(k, m, t))
    if not moments:
        return None

    X = np.array([r[0] for r in rows])
    w = np.exp(-(np.linalg.norm(X, axis=1) / BANDWIDTH) ** 2)
    A = np.hstack([np.ones((len(rows), 1)), X])
    M = A.T @ (A * w[:, None]) + RIDGE * np.eye(A.shape[1])

    J = np.zeros((len(moments), len(params)))
    for i, name in enumerate(moments):
        tgt = ref[1][name][1]
        y = np.array([jacobian.scaled(mt[name][0], tgt) if name in mt
                      else jacobian.scaled(jacobian.FLOOR, tgt) for _d, mt, _n in rows])
        y = np.array([v if v is not None else jacobian.scaled(jacobian.FLOOR, tgt) for v in y])
        try:
            coef = np.linalg.solve(M, A.T @ (w * y))
        except np.linalg.LinAlgError:
            continue
        for j in range(len(params)):
            J[i][j] = max(-jacobian.MAX_ELASTICITY, min(jacobian.MAX_ELASTICITY, coef[1 + j]))

    # The LEVEL is what the model actually said at the nearest measured point;
    # only the SLOPES come from the fit. Same rule as jacobian.assemble_regression
    # and for the same reason: a fit over the whole archive is accurate around a
    # point, not at it.
    r = np.array([jacobian.scaled(ref[1][n][1], ref[1][n][1])
                  - jacobian.scaled(ref[1][n][0], ref[1][n][1]) for n in moments])
    wt = np.array([score_points.WEIGHT.get(n, 1.0) for n in moments])
    return moments, J, r, wt, ref[2], len(rows)


def direction(J, r, w, ridge=1e-3):
    """The Gauss-Newton direction, ridged only enough to be well posed.

    NOT damped to a trust region: the length is what the ladder measures, so
    damping here would bake in the very guess this file exists to replace. The
    ridge is for conditioning alone and is three orders below the smallest
    singular value the assembled system has shown.
    """
    W = np.diag(w)
    d = np.linalg.solve(J.T @ W @ J + ridge * np.eye(J.shape[1]), J.T @ W @ r)
    n = float(np.max(np.abs(d)))
    return d / n if n > 0 else d


def clip(name, value):
    lo, hi = BOUNDS.get(name, (1e-12, 1e12))
    return min(max(value, lo), hi)


# A ROUND IS DONE WHEN THE LADDER IS DONE, not when most of it is. Re-centring
# on a partial ladder throws away the rung still solving, and the rung still
# solving is disproportionately the LONG one -- a big step changes the model most
# and takes longest to converge -- so a partial re-centre is biased towards short
# steps, which is exactly the timidity this file exists to remove.
STATE = os.path.join(HERE, 'LINE_SEARCH_STATE.txt')
LADDER_FILE = os.path.join(HERE, 'LINE_SEARCH.txt')
# Converged when a whole ladder cannot better the centre by this much. The
# ladder spans 1.02x to 2.23x, so if none of eight lengths in the Gauss-Newton
# direction buys half a per cent, the direction is exhausted, not merely short.
CONVERGED_GAIN = 0.005


def _tag(line):
    import hashlib
    vec = dict(t.split('=', 1) for t in line.split()[2:])
    return hashlib.md5(''.join(f'{k}={vec[k]}\n' for k in sorted(vec)).encode()).hexdigest()[:10]


def _landed():
    """(loss, tag, rung) for every rung of the current ladder that has a point."""
    out, missing = [], []
    for i, line in enumerate(open(LADDER_FILE), 1):
        line = line.strip()
        if not line:
            continue
        tag = _tag(line)
        p = os.path.join(HERE, 'points', f'point_{tag}.txt')
        if os.path.exists(p) and 'END OF MOMENTS' in open(p, errors='replace').read():
            _h, mt = score_points.read(p)
            if mt:
                out.append((score_points.loss(mt)[0], f'point_{tag}.txt', i))
                continue
        if os.path.exists(os.path.join(HERE, 'points', f'point_{tag}.FAILED.txt')):
            continue                                    # a failed rung is not waited for
        missing.append(i)
    return out, missing


def advance():
    """Score the ladder; if it is complete, re-centre and write the next one."""
    landed, missing = _landed()
    if missing:
        print(f'ladder: {len(landed)} of {len(landed) + len(missing)} rungs landed, '
              f'still out {missing}')
        return 0
    if not landed:
        print('ladder: every rung failed; not advancing')
        return 1

    landed.sort()
    best_loss, best_name, best_rung = landed[0]
    pts = [(v, m, n) for v, m, n in jacobian.points() if 'relative_share_of_housing' in v]
    prev = min(score_points.loss(m)[0] for _v, m, _n in pts) if pts else float('inf')

    print('ladder result, by rung:')
    for L, name, rung in sorted(landed, key=lambda t: t[2]):
        print(f'   rung {rung}  t={LADDER[rung-1]:<5} loss {L:.4f}')
    gain = (prev - best_loss) / prev if prev else 0.0
    print(f'best rung {best_rung} at {best_loss:.4f}; archive best {prev:.4f} '
          f'({gain*100:+.1f}%)')

    if best_loss >= prev * (1 - CONVERGED_GAIN):
        print('CONVERGED: no length in this direction improves on the archive best.')
        print('The direction is exhausted. Re-solve from a different centre, or the '
              'remaining gap is a frontier rather than a search failure.')
        return 3

    with open(STATE, 'a') as fh:
        fh.write(f'centre {best_name} loss {best_loss:.5f} rung {best_rung} '
                 f'gain {gain*100:+.2f}%\n')
    sys.argv = [sys.argv[0], '--centre', best_name, '--emit']
    lines = []
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main()
    if rc:
        print('could not build the next ladder around the new centre')
        return rc
    lines = [l for l in buf.getvalue().splitlines() if l.startswith('bash ')]
    if len(lines) != len(LADDER):
        print(f'expected {len(LADDER)} run lines, got {len(lines)}; not writing')
        return 1
    with open(LADDER_FILE, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print(f'ADVANCED: new ladder around {best_name}, {len(lines)} rungs written')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--centre', help='point file to step from; default the best measured')
    ap.add_argument('--emit', action='store_true', help='print the run lines')
    ap.add_argument('--advance', action='store_true',
                    help='if every rung has landed, re-centre on the best and rewrite '
                         'LINE_SEARCH.txt; otherwise report what is still out')
    args = ap.parse_args()

    # THE LOOP, SO A ROUND DOES NOT NEED A HAND ON IT. --advance is what the
    # engine trigger runs: it refuses to move while any rung is still out, so a
    # slow worker cannot cause the centre to jump before its point is counted,
    # and it re-solves the direction from the archive the new centre sits in.
    if args.advance:
        return advance()

    pts = [(v, m, n) for v, m, n in jacobian.points()
           if 'relative_share_of_housing' in v]            # new era only
    if not pts:
        print('no new-era points', file=sys.stderr)
        return 2

    scored = []
    for vec, mt, name in pts:
        L, _n, _w = score_points.loss(mt)
        scored.append((L, vec, mt, name))
    scored.sort(key=lambda t: t[0])
    if args.centre:
        pick = [s for s in scored if args.centre in s[3]]
        if not pick:
            print(f'no such point: {args.centre}', file=sys.stderr)
            return 2
        L0, centre, _mt, cname = pick[0]
    else:
        L0, centre, _mt, cname = scored[0]

    params = varying(pts, centre)
    got = fit(centre, pts, params)
    if got is None:
        print('could not fit a Jacobian around this centre', file=sys.stderr)
        return 2
    moments, J, r, w, refname, used = got
    d = direction(J, r, w)

    s = np.linalg.svd(J, compute_uv=False)
    print(f'centre {cname}  loss {L0:.4f}', file=sys.stderr)
    print(f'fit over {used} points, {len(moments)} moments x {len(params)} parameters,'
          f' condition {s[0]/max(s[-1],1e-30):.1e}', file=sys.stderr)
    print(f'residual norm {np.linalg.norm(r):.3f}; predicted at full unit step'
          f' {np.linalg.norm(r - J @ d):.3f}', file=sys.stderr)
    print('the direction, largest movers first:', file=sys.stderr)
    for j in sorted(range(len(params)), key=lambda j: -abs(d[j]))[:8]:
        print(f'   {params[j]:<50} {d[j]:+.3f}', file=sys.stderr)

    for t in LADDER:
        v = dict(centre)
        for j, k in enumerate(params):
            v[k] = clip(k, centre[k] * math.exp(t * d[j]))
        line = 'bash code/run_one_point.sh ' + ' '.join(
            f'{k}={v[k]:.7g}' for k in sorted(v))
        if args.emit:
            print(line)
        else:
            print(f'  t={t:<5} max move {math.exp(t):.2f}x', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
