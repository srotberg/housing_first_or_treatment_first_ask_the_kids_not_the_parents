"""Nelder-Mead over the coupled drug block, run in parallel.

WHY A SIMPLEX HERE AND A JACOBIAN EVERYWHERE ELSE.

Sixty seven per cent of the loss at the best point ever measured sits in five
moments, and they split into two problems with different shapes:

    lambda_d  22.0%      the drug block: a curved valley in four parameters
    kappa_uem 17.8%      an instrument that was pinned at its floor
    b         11.6%      the drug block again
    lambda_m   8.1%      the same pinned instrument, one step downstream
    tau_u      7.8%

kappa_uem's share is not an optimisation problem at all -- no method moves a
clamped parameter -- and it is handled by freeing the clamp and probing it.

The drug block is a genuine optimisation problem and the Jacobian is the wrong
tool for it. Its response is not smooth: CALIBRATION_PLAN.md records the b curve
as 0.947, 0.759, then 0.000158 across 0.05, 0.06 and 0.12 -- "flat, then a cliff
somewhere above 0.06" -- and interpolating through it gave 0.0634 and was badly
wrong. A derivative measured anywhere on the flat says nothing about the cliff.
Worse, the four parameters trade off against each other along a narrow curve, so
a single-parameter arm toward the answer scores WORSE than the centre even when
the answer lies that way: generation eight moved lambda alone from 5.06 to 9.11,
in the direction the ridge map says the answer is, and the loss went from 0.455
to 0.527. Only the joint move helps, and the trust region caps the joint move at
1.4 a round.

Nelder-Mead needs no derivatives, tolerates the cliff, and moves every parameter
in the block together by construction. In four parameters it is five vertices,
which is a size it handles well -- unlike the full twenty two, where it needs
twenty three vertices and is known to stagnate.

WHAT IS DIFFERENT HERE: textbook Nelder-Mead is sequential. It reflects, looks,
then decides whether to expand or contract, one function evaluation at a time --
which on a twenty minute solve would use one of eighteen parallel slots and be
slower than what it replaces. So every trial the decision tree could reach is
evaluated AT ONCE: reflection, expansion, and both contractions. The standard
acceptance rules then run against results already in hand. Four points a round
instead of one, same wall clock, and the logic is unchanged from the textbook.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import jacobian                                          # noqa: E402
import score_points                                      # noqa: E402

STATE = os.path.join(HERE, 'SIMPLEX.txt')

# The block. These four are coupled through the drug margin: b sets how many
# use, lambda converts use into disorder, theta is the share of the bundle the
# drug takes and aleph prices the mortality that deters it. They own b,
# lambda_d, theta and aleph, which are 43 per cent of the loss between them.
BLOCK = ['addiction_scalar_1', 'lambda_addiction',
         'relative_share_of_addiction_1', 'value_of_life']

# Textbook coefficients. There is no reason to tune them before the method has
# been seen to work.
ALPHA, GAMMA, RHO, SIGMA = 1.0, 2.0, 0.5, 0.5

# THE SIMPLEX LIVES IN LOGS, like every other step in this calibration. These
# parameters span four orders of magnitude between them and a reflection in
# levels would propose a negative b long before it proposed a useful one.
MATCH = 1e-4            # two vectors this close in logs are the same point


def bounds(name):
    from converge import BOUNDS
    return BOUNDS.get(name, (1e-12, 1e12))


def clip(vec):
    out = {}
    for k, v in vec.items():
        lo, hi = bounds(k)
        out[k] = max(lo, min(hi, v))
    return out


def to_log(vec):
    return [math.log(max(vec[k], 1e-12)) for k in BLOCK]


def from_log(x):
    return clip(dict(zip(BLOCK, [math.exp(v) for v in x])))


def measured():
    """Every archive point, as (log-vector over the block, full vector, loss)."""
    out = []
    for vec, mt, name in jacobian.points():
        if any(k not in vec for k in BLOCK):
            continue
        out.append((to_log(vec), vec, score_points.loss(mt)[0], name))
    return out


def look_up(x, pts, bg):
    """The measured loss at this point, if the fleet has run it AT THIS BACKGROUND.

    A point matching on the block alone is not this vertex; it is some other
    generation's arm that happened to pass through the same four values.
    """
    best = None
    for lx, vec, loss, name in pts:
        d = max(abs(a - b) for a, b in zip(lx, x))
        if d < MATCH and same_background(vec, bg) and (best is None or loss < best[0]):
            best = (loss, name)
    return best


def held(pts):
    """The values of everything OUTSIDE the block, taken from the best point.

    A simplex vertex is only comparable to another if the rest of the vector is
    identical, so the block is optimised against a FIXED background and the
    background is the best one known.
    """
    best = min(pts, key=lambda r: r[2])
    return {k: v for k, v in best[1].items() if k not in BLOCK}


def spec(vec, bg):
    """The WHOLE vector, not just the block.

    run_one_point.sh defaults to the current generation's centre, and
    converge.py --write moves that centre every round. A command naming only the
    four block parameters would therefore be evaluated against a different
    background each generation -- the simplex would be measuring a function that
    changes underneath it, which is the same error as building it from archive
    points with mismatched backgrounds. Naming everything makes a vertex mean the
    same thing whenever it is run.
    """
    out = dict(bg)
    out.update({k: vec[k] for k in BLOCK})
    return ' '.join('%s=%.6g' % (k, out[k]) for k in sorted(out))


# A VERTEX IS ONLY A VERTEX IF THE REST OF THE VECTOR IS THE SAME. The simplex
# is a function of four parameters and nothing else, so two points that differ in
# size_homelessness as well as in b are not two evaluations of that function.
# The archive holds a hundred and eighty points spread over eight generations and
# every one of them has a different background; reusing them as vertices because
# their block values are conveniently far apart would build the first simplex out
# of numbers that are not comparable, and Nelder-Mead has no way to notice.
#
# So the background is fixed at the best point's, archive points are reused only
# where they match it, and the rest are measured. It costs a few solves once.
BACKGROUND = 1e-4


def same_background(vec, bg):
    for k, v in bg.items():
        if k not in vec:
            return False
        if abs(math.log(max(vec[k], 1e-12) / max(v, 1e-12))) > BACKGROUND:
            return False
    return True


def initial(pts):
    """A first simplex around the best point, at that point's background."""
    best = min(pts, key=lambda r: r[2])
    bg = {k: v for k, v in best[1].items() if k not in BLOCK}
    verts = [(best[0], best[2])]
    seen = [best[0]]
    reused = 1
    for lx, vec, loss, _n in sorted(pts, key=lambda r: r[2]):
        if len(verts) > len(BLOCK):
            break
        if not same_background(vec, bg):
            continue
        if all(max(abs(a - b) for a, b in zip(lx, s)) > 0.05 for s in seen):
            verts.append((lx, loss))
            seen.append(lx)
            reused += 1
    # Whatever the archive cannot supply at this background is measured. The
    # step is a factor of 1.4 in one coordinate, which is the same size as the
    # trust region the Jacobian is allowed, so the first simplex is no wider
    # than a step the search already believes in.
    i = 0
    while len(verts) <= len(BLOCK):
        x = list(best[0])
        x[i % len(BLOCK)] += math.log(1.4) * (1 if i % 2 == 0 else -1)
        verts.append((x, None))
        i += 1
    print('%d vertices reused from the archive at the best point\'s background, '
          '%d to measure.\n' % (reused, len(verts) - reused))
    return verts, bg


def load():
    if os.path.exists(STATE):
        with open(STATE) as fh:
            return json.load(fh)
    return None


def save(st):
    with open(STATE, 'w') as fh:
        json.dump(st, fh, indent=1)


def centroid(verts):
    n = len(verts) - 1
    return [sum(v[0][i] for v in verts[:n]) / n for i in range(len(BLOCK))]


def trials(verts):
    """Every point the decision tree could ask for, all at once."""
    c = centroid(verts)
    worst = verts[-1][0]
    xr = [c[i] + ALPHA * (c[i] - worst[i]) for i in range(len(BLOCK))]
    xe = [c[i] + GAMMA * (xr[i] - c[i]) for i in range(len(BLOCK))]
    xoc = [c[i] + RHO * (xr[i] - c[i]) for i in range(len(BLOCK))]
    xic = [c[i] + RHO * (worst[i] - c[i]) for i in range(len(BLOCK))]
    return {'reflect': xr, 'expand': xe, 'outside': xoc, 'inside': xic}


def advance(verts, t, f):
    """Standard Nelder-Mead acceptance, against trials already evaluated.

    Returns (new vertices, what happened, whether a shrink is needed).
    """
    fr = f.get('reflect')
    best, second_worst, worst = verts[0][1], verts[-2][1], verts[-1][1]
    if fr is None:
        return verts, 'reflection never landed', False
    if fr < best:
        fe = f.get('expand')
        if fe is not None and fe < fr:
            return verts[:-1] + [(t['expand'], fe)], 'expanded', False
        return verts[:-1] + [(t['reflect'], fr)], 'reflected past the best', False
    if fr < second_worst:
        return verts[:-1] + [(t['reflect'], fr)], 'reflected', False
    if fr < worst:
        fo = f.get('outside')
        if fo is not None and fo <= fr:
            return verts[:-1] + [(t['outside'], fo)], 'contracted outside', False
        return verts, 'outside contraction failed', True
    fi = f.get('inside')
    if fi is not None and fi < worst:
        return verts[:-1] + [(t['inside'], fi)], 'contracted inside', False
    return verts, 'inside contraction failed', True


def shrink(verts):
    x0 = verts[0][0]
    out = [verts[0]]
    for x, _l in verts[1:]:
        out.append(([x0[i] + SIGMA * (x[i] - x0[i]) for i in range(len(BLOCK))], None))
    return out


def report(verts, pts):
    print('%-12s %11s %11s %11s %11s %9s' %
          ('vertex', 'b', 'lambda', 'theta', 'aleph', 'loss'))
    print('-' * 70)
    for i, (x, loss) in enumerate(verts):
        v = from_log(x)
        print('%-12s %11.5g %11.5g %11.5g %11.5g %9s'
              % ('best' if i == 0 else ('worst' if i == len(verts) - 1 else str(i)),
                 v['addiction_scalar_1'], v['lambda_addiction'],
                 v['relative_share_of_addiction_1'], v['value_of_life'],
                 '%.3f' % loss if loss is not None else 'not run'))
    span = 0.0
    for i in range(len(BLOCK)):
        col = [x[i] for x, _l in verts]
        span = max(span, max(col) - min(col))
    print('\nwidest edge: a factor of %.2f in one parameter' % math.exp(span))
    return span


def main():
    pts = measured()
    if not pts:
        print('no measured points')
        return
    st = load()
    if st is None or '--init' in sys.argv:
        verts, bg = initial(pts)
        st = {'iter': 0, 'vertices': [[x, l] for x, l in verts], 'trials': None,
              'background': bg}
        print('A FRESH SIMPLEX, built from the archive.\n')
    verts = [(x, l) for x, l in st['vertices']]
    bg = st['background']

    # Fill in any vertex whose point has landed since the last call.
    filled = []
    for x, loss in verts:
        if loss is None:
            got = look_up(x, pts, bg)
            loss = got[0] if got else None
        filled.append((x, loss))
    verts = filled

    if st.get('trials'):
        t = {k: v for k, v in st['trials'].items()}
        f = {}
        for k, x in t.items():
            got = look_up(x, pts, bg)
            if got:
                f[k] = got[0]
        missing = [k for k in t if k not in f]
        if missing and '--force' not in sys.argv:
            print('iteration %d: still solving -- %s' % (st['iter'], ', '.join(missing)))
            report(verts, pts)
            return
        verts, what, needs_shrink = advance(verts, t, f)
        print('iteration %d: %s' % (st['iter'], what))
        for k in sorted(f):
            print('   %-9s loss %.3f' % (k, f[k]))
        if needs_shrink:
            verts = shrink(verts)
            print('   the simplex shrinks toward its best vertex')
        st['trials'] = None
        st['iter'] += 1

    if any(l is None for _x, l in verts):
        print('\nVertices still to measure:\n')
        for x, l in verts:
            if l is None:
                print('  bash code/run_one_point.sh %s' % spec(from_log(x), bg))
        st['vertices'] = [[x, l] for x, l in verts]
        save(st)
        return

    verts.sort(key=lambda v: v[1])
    span = report(verts, pts)
    t = trials(verts)
    st['vertices'] = [[x, l] for x, l in verts]
    st['trials'] = t
    if '--write' in sys.argv:
        save(st)
    print('\nThe next four points, all at once (%s):\n'
          % ('--write recorded them' if '--write' in sys.argv else 'not recorded, pass --write'))
    for k in ('reflect', 'expand', 'outside', 'inside'):
        print('  bash code/run_one_point.sh %s   # %s' % (spec(from_log(t[k]), bg), k))
    if span < 0.02:
        print('\nCONVERGED: the widest edge is under two per cent.')


if __name__ == '__main__':
    main()
