"""Multi-directional search over all twenty two parameters, in parallel.

WHY NOT NELDER-MEAD OVER THE WHOLE VECTOR.

Two objections were raised to a twenty two parameter simplex and only one of
them survives.

The one that does not: that twenty three vertices is too many to initialise.
Twenty three vertices is twenty three sessions, which is one round of this
fleet, and the fleet already runs rounds that size. It costs a round, once.

The one that does: NELDER-MEAD REPLACES ONE VERTEX PER ITERATION. Reflection,
expansion and contraction all act on the worst vertex alone, and the other n
stay exactly where they were. With twenty three vertices and a twenty minute
solve, the simplex needs twenty three iterations -- close to eight hours -- before
it has so much as touched each vertex once, and it needs several passes to move.
Running the trials in parallel does not help, because the limit is not how many
points can be evaluated at once. It is that the method only knows what to do with
one of them.

WHAT REPLACES IT.

Multi-directional search (Torczon), which was designed for parallel machines and
fixes exactly this. Every iteration reflects ALL n vertices through the best one
at once:

    r_i = v0 + (v0 - v_i)          i = 1 .. n

If any reflection improves on the best vertex the whole reflected simplex is
kept, and an expansion of all n is tried against it; if none does, all n are
contracted toward the best. Every vertex moves every iteration, the n
evaluations are independent, and unlike Nelder-Mead the method is provably
convergent -- MDS keeps the simplex's shape, so it cannot collapse into a
subspace and go blind, which is the failure Nelder-Mead is best known for and
which gets worse as the dimension rises.

So the parallelism is real rather than cosmetic: twenty two points a round, all
at once, and after one round every parameter has moved.

AND MANY STEPS ALONG THE DIRECTION, NOT ONE. MDS fixes the step SHAPE and takes
it at one scale. The scale is the part worth sampling, and it is cheap: the ray
through the best vertex along the winning direction is sampled at RAY scales in
the same batch. That is the same argument that turned Nelder-Mead's four trials
into sixteen -- the method samples a line, and a line deserves more than one
point when the points are free.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import jacobian                                          # noqa: E402
import score_points                                      # noqa: E402
from suggest_next import OWNS                            # noqa: E402

STATE = os.path.join(HERE, 'SIMPLEX.txt')

# EVERY PARAMETER THAT OWNS A MOMENT. There is no background any more: a vertex
# is the whole vector, so nothing can shift underneath the simplex and the
# comparability rules the four parameter version needed are unnecessary here.
BLOCK = sorted(OWNS)

# Torczon's coefficients: contract to a half, reflect, expand to double.
MU, THETA = 2.0, 0.5

# EVERY VERTEX GETS ITS OWN RAY, not just the winning one.
#
# MDS moves vertex i along the line through the best vertex, x(t) = v0 + t*(v0 -
# v_i), and the three coefficients above are three samples of it: -0.5 the
# contraction, +1 the reflection, +2 the expansion. That is the same structure
# Nelder-Mead had and the same waste: the method samples twenty two lines and
# takes three points on each because a sequential implementation could not afford
# more.
#
# The information ceiling of one iteration is "for each of the twenty two
# directions, where along it is the best point", and more samples per direction is
# strictly closer to that ceiling. So the scale list is a budget knob rather than
# a constant: three scales is textbook MDS at 66 points, seven is a real line
# search on all twenty two directions at once at 154, and nothing in the method
# changes -- the acceptance rule still takes the best simplex it can build.
#
# Ordered so that a truncated list is still a sensible MDS: the first three are
# the textbook's own.
SCALES = (-0.5, 1.0, 2.0, 0.5, 3.0, -0.75, 4.0, 1.5, -0.25, 6.0)

# The initial simplex: each vertex is the base point with ONE coordinate moved by
# this factor. It is the trust region the Jacobian is allowed, so the simplex
# starts no wider than a step the search already believes in.
EDGE = 1.4

# A UNIFORM EDGE IS THE WRONG SHAPE WHEN ONE PARAMETER IS FAR MORE UNCERTAIN THAN
# THE REST. The simplex should be as wide in each direction as the answer might
# be, and for kappa_uem that is not 40 per cent: it has sat pinned at its floor
# of 1.0 for every generation, where it is the identity and serious mental
# illness costs nothing on either employment margin. Its moment is 17.8 per cent
# of the loss on its own and the log-odds fit across the three measured points
# puts the answer near 8.5, so that is where its vertex goes. Starting it at 1.4
# would spend several iterations walking somewhere the evidence already points.
EDGE_OVERRIDE = {'kappa_uem': 8.5, 'zeta_DI': 0.025}
# zeta_DI's vertex goes DOWN, not up. Its moment, the SMI share of the
# homeless, is 0.0347 against a target of 0.25, and less DI coverage is what
# raises it: an uncovered household with SMI falls to the same zero income as
# everyone else out of work, and it is out of work about two thirds of the time
# against five per cent for everyone else. A uniform 1.4x edge would have put
# the vertex at 0.462 and spent a solve learning that more insurance makes the
# moment worse, which is not in doubt.

# Scales sampled along the winning direction, on top of the MDS step.
RAY = (-0.5, 0.5, 1.5, 2.5, 4.0, 6.0)

MATCH = 1e-4


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


def canon(x):
    """The vertex as it will actually be RUN, which is the only thing to store.

    A POINT THAT HITS A BOUND CAN NEVER MATCH ITS OWN VERTEX. from_log clips into
    BOUNDS, so the command sent to the fleet carries the clipped value while the
    state file kept the unclipped one, and look_up compared the two in log space
    and found them different for ever. The simplex then listed a vertex as
    unmeasured after it had been measured, waited for it, and could not step.

    discount_factor is where it showed up: base 0.993881 times an edge of 1.4 is
    1.3914, the bound is 0.999, the fleet ran 0.999 and the state was still
    holding 1.3914. Every clamp in this calibration has produced a bug of this
    shape -- kappa_uem's arms at 0.10 and 0.30 were silent no-ops for the same
    reason -- so nothing is stored that has not been through the clip first.
    """
    return to_log(from_log(x))


# THE MOMENT SET IS PART OF THE LOSS, so two points measured over different
# ones cannot be ranked against each other. The loss is a MEAN weighted gap: a
# point reporting 24 moments and a point reporting 23 are on different scales,
# and the extra moment drags the newer point down whenever it is worse than the
# average of the others. omega joined the block when its counterfactual was
# moved into print_all_moments, so every one of the 260 points on disk predates
# it. Reusing them beside points that carry it would rank the two generations
# against each other and call the difference progress.
REQUIRED = ('omega',)

# A ZERO omega IS A POINT FROM BEFORE THE COUNTERFACTUAL WAS FIXED. The child
# term's counterfactual read back a user count that govt_revenues_calc never
# recomputed, so it reported the BASELINE count and MOMENT omega came out as
# exactly 0.0000000000000000 at every weight_on_child. Every point measured
# before that fix carries the moment and carries it as an exact zero, so
# requiring the moment's PRESENCE is no longer enough to tell the two models
# apart -- and the two models are very different: at one vector b was 9.04 per
# cent with the child channel off and 1.80 with it on.
def complete(mt):
    if not all(k in mt for k in REQUIRED):
        return False
    return abs(mt['omega'][0]) > 1e-12


# WHERE TO START, WHEN NOTHING MEASURED CAN ANCHOR. The archive fixes the
# location but weight_on_child's own coordinate is set here, because the channel
# it multiplies was inert when every archived point was measured: at 0.5 the
# seed would sit at b = 1.80 per cent against a target of 8.9, and b carries
# triple weight, so the first simplex would spend itself climbing out.
SEED_OVERRIDE = {'weight_on_child': 0.02}


def measured(require=True):
    out = []
    for vec, mt, name in jacobian.points():
        if any(k not in vec for k in BLOCK):
            continue
        if require and not complete(mt):
            continue
        out.append((to_log(vec), vec, score_points.loss(mt)[0], name))
    return out


def look_up(x, pts):
    """The measured loss at this point, if the fleet has run it.

    A vertex is the whole vector, so a match here is a match on everything.
    """
    best = None
    for lx, _vec, loss, name in pts:
        if max(abs(a - b) for a, b in zip(lx, x)) < MATCH:
            if best is None or loss < best[0]:
                best = (loss, name)
    return best


def spec(vec):
    return ' '.join('%s=%.6g' % (k, vec[k]) for k in sorted(vec))


def _reuse(cand, pts):
    """How many of this candidate's vertices the fleet has already measured."""
    n = 0
    for i, key in enumerate(BLOCK):
        edge = EDGE
        if key in EDGE_OVERRIDE:
            edge = EDGE_OVERRIDE[key] / max(cand[1][key], 1e-12)
            if abs(math.log(max(edge, 1e-12))) < 1e-6:
                edge = EDGE
        for sign in (1.0, -1.0):
            x = canon([cand[0][j] + (sign * math.log(edge) if j == i else 0.0)
                       for j in range(len(BLOCK))])
            if look_up(x, pts):
                n += 1
                break
    return n


def initial(pts):
    """Twenty three vertices: the best point, and it with each coordinate moved.

    Any of them the fleet has already run is reused, in either direction -- the
    four vertices launched for the earlier four parameter simplex are exactly
    this shape and are picked up here rather than wasted.
    """
    # THE ANCHOR IS THE POINT THAT REUSES THE MOST WORK, not simply the best
    # one. Anchoring on the best point re-centres the whole simplex every time a
    # new best lands, and every vertex around the previous anchor stops matching:
    # when the weighting changed and zeta_DI replaced di_takeup, a simplex with
    # 22 of 24 vertices measured reported 2, and would have spent 22 fresh points
    # rebuilding what was already on disk. Which point anchors an INITIAL simplex
    # is a free choice -- it only has to be non-degenerate, and the first
    # reflection moves toward the best vertex regardless -- so it is spent on
    # reuse, with the loss as the tie-break.
    base = max(pts, key=lambda r: (_reuse(r, pts), -r[2]))
    verts = [(base[0], base[2])]
    reused = 1
    for i, key in enumerate(BLOCK):
        edge = EDGE
        if key in EDGE_OVERRIDE:
            # An absolute target rather than a factor: the override says where
            # the vertex should BE, so the edge is whatever gets it there --
            # INCLUDING AN EDGE BELOW ONE. Clamping it above one silently
            # collapsed every downward override onto the base point, so
            # zeta_DI's vertex became a duplicate of the base and the
            # simplex reported it as already measured.
            edge = EDGE_OVERRIDE[key] / max(base[1][key], 1e-12)
            if abs(math.log(max(edge, 1e-12))) < 1e-6:
                edge = EDGE          # the override is already the base value
        found = None
        for sign in (1.0, -1.0):
            x = canon([base[0][j] + (sign * math.log(edge) if j == i else 0.0)
                       for j in range(len(BLOCK))])
            got = look_up(x, pts)
            if got:
                found = (x, got[0])
                break
        if found:
            verts.append(found)
            reused += 1
        else:
            x = canon([base[0][j] + (math.log(edge) if j == i else 0.0)
                       for j in range(len(BLOCK))])
            verts.append((x, None))
    print('%d of %d vertices already measured, %d to run.\n'
          % (reused, len(verts), len(verts) - reused))
    return verts


def load():
    if os.path.exists(STATE):
        with open(STATE) as fh:
            st = json.load(fh)
        if st.get('block') == BLOCK:
            return st
        print('The state file is for a different parameter set; starting over.\n')
    return None


def save(st):
    st['block'] = BLOCK
    with open(STATE, 'w') as fh:
        json.dump(st, fh, indent=1)


# A SIMPLEX THAT FLATTENS CANNOT SEARCH, AND THE PER-VERTEX RAY IS WHAT FLATTENS
# IT. Torczon's convergence rests on applying ONE coefficient to every vertex:
# that is a similarity transform about the best vertex, so the simplex's shape is
# preserved exactly and it can never collapse into a subspace. Letting each
# vertex take the best point on its own ray is a better step per round and it is
# NOT a similarity transform -- twenty two independent choices can land the
# vertices close to a common face, and the simplex is then blind in whatever
# direction it lost, permanently.
#
# The guard was written for the Nelder-Mead version, dropped in the rewrite to
# MDS, and is needed more here than it was there. A candidate simplex that costs
# more than this share of the previous volume is refused, and the round falls
# back to the single best coefficient applied to every vertex -- textbook MDS,
# shape-preserving by construction.
#
# BE HONEST ABOUT WHAT THIS TEST MEASURES: volume, which conflates shape with
# size. A uniform contraction is shape-preserving and still loses volume by
# design, so it fails the test and takes the fallback -- where it finds itself
# again, since the fallback IS that contraction. The effective rule is therefore
# "the per-vertex form runs while the simplex is not shrinking, and every shrink
# goes through the shape-preserving path". That is conservative in the right
# direction and cheap to state, which a true shape test at this dimension is
# not.
VOLUME_FLOOR = 0.10


def log_volume(verts):
    """log of the simplex volume, up to the constant that cancels in a ratio.

    In logs because twenty two edges of 0.34 multiply to about 1e-11, and the
    ratio of two such numbers is not something to compute by dividing them.
    """
    x0 = verts[0][0]
    m = [[v[0][i] - x0[i] for i in range(len(BLOCK))] for v in verts[1:]]
    n = len(m)
    total = 0.0
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(m[r][i]))
        if abs(m[p][i]) < 1e-300:
            return float('-inf')
        if p != i:
            m[i], m[p] = m[p], m[i]
        total += math.log(abs(m[i][i]))
        for r in range(i + 1, n):
            fac = m[r][i] / m[i][i]
            for c in range(i, n):
                m[r][c] -= fac * m[i][c]
    return total


def moved_vertex(v0, x, phase):
    if phase == 'reflect':
        return [2 * v0[j] - x[j] for j in range(len(BLOCK))]
    if phase == 'expand':
        return [v0[j] + MU * (v0[j] - x[j]) for j in range(len(BLOCK))]
    return [v0[j] + THETA * (x[j] - v0[j]) for j in range(len(BLOCK))]


def step_set(verts, phase):
    """All n moved at once, the way MDS moves them."""
    v0 = verts[0][0]
    out = {}
    for i, (x, _l) in enumerate(verts[1:], start=1):
        out['%s%02d' % (phase[0], i)] = canon(moved_vertex(v0, x, phase))
    return out


# ONE BATCH PER ITERATION INSTEAD OF TWO. Plain MDS decides between expansion and
# contraction by looking at the reflection first, which costs a second round trip
# -- and a round trip here is twenty five minutes of wall clock, not a function
# call. Evaluating all three sets at once removes it: the rule is applied with
# everything already in hand, exactly as written, and a full iteration takes one
# round.
#
# Two thirds of the points are not used by the step, and that is the price. It is
# smaller than it looks: an unused expansion or contraction is still a measured
# point in the archive, where the Jacobian and the loss history read it like any
# other. What it really costs is sessions, so it is a choice and not a default
# buried in the method -- the caller passes --speculative when the fleet has the
# room, and takes the two round version when it does not.
def speculative_set(verts, scales=3):
    v0 = verts[0][0]
    use = SCALES[:max(3, scales)]
    out = {}
    for i, (x, _l) in enumerate(verts[1:], start=1):
        for t in use:
            out['s%02d@%+.2f' % (i, t)] = canon(
                [v0[j] + t * (v0[j] - x[j]) for j in range(len(BLOCK))])
    return out


def resolve_speculative(verts, t, f):
    """Build the best simplex the batch supports, one vertex at a time.

    Classic MDS keeps a whole reflected or contracted simplex. With every scale
    measured there is no reason to move all vertices by the same coefficient:
    each vertex takes the best point on ITS OWN ray, which is a strictly better
    simplex than any single-coefficient one, since the single coefficient is one
    of the choices available to every vertex.

    The best vertex is kept, as MDS keeps it.
    """
    out = [verts[0]]
    improved = 0
    for i, (x, loss) in enumerate(verts[1:], start=1):
        best = (loss, x)
        for k, l in f.items():
            if not k.startswith('s%02d@' % i):
                continue
            if l < best[0]:
                best = (l, t[k])
        if best[1] is not x:
            improved += 1
        out.append((best[1], best[0]))

    before = log_volume(verts)
    after = log_volume(out)
    if before > float('-inf') and after - before >= math.log(VOLUME_FLOOR):
        return out, improved, 'per-vertex'

    # Too flat. Fall back to one coefficient for every vertex, which is a
    # similarity transform about the best vertex and cannot degenerate.
    best_common, best_score = None, None
    for scale in set(float(k.split('@')[1]) for k in f):
        got = []
        for i in range(1, len(verts)):
            key = 's%02d@%+.2f' % (i, scale)
            if key in f:
                got.append((t[key], f[key]))
        if len(got) != len(verts) - 1:
            continue
        score = min(l for _x, l in got)
        if best_score is None or score < best_score:
            best_common, best_score = got, score
    if best_common is None:
        return verts, 0, 'nothing usable'
    moved_count = sum(1 for (nx, nl), (ox, ol) in zip(best_common, verts[1:])
                      if nl < ol)
    return [verts[0]] + best_common, moved_count, 'one coefficient (shape kept)'


def jacobian_candidate(verts, pts):
    """One extra trial: where the derivatives think the best vertex should go.

    THE JACOBIAN IS NOT DISCARDED, IT IS DEMOTED TO A CANDIDATE. Direct search is
    robust and slow; a linearisation is fast and, on this model, unreliable --
    it has been wrong about the scale of a response, wrong across a cliff, and
    right about the other eighteen parameters for eight generations. Running its
    proposal as ONE point among twenty two costs one session and lets the
    evidence decide, instead of the method having to be chosen in advance.
    """
    centre = from_log(verts[0][0])
    try:
        move, _info = jacobian.step(centre, pts, trust=1.4, regression=True)
    except Exception:
        return None
    if not move:
        return None
    x = list(verts[0][0])
    for i, key in enumerate(BLOCK):
        if key in move:
            x[i] += move[key]
    return canon(x)


def ray_set(v0, direction):
    """The winning direction, sampled at several scales."""
    out = {}
    for t in RAY:
        out['ray%+.1f' % t] = canon(
            [v0[j] + t * direction[j] for j in range(len(BLOCK))])
    return out


# WHEN THIS IS DONE, in the author's words on 25 August: "it is ok if we can't
# hit every single moment. It's many moments. As long as almost all are within
# 5-10 per cent or so, and maybe one a bit off it's ok."
#
# That is a statement about the WORST moments and not about the mean, and the
# loss is a weighted mean of relative gaps. A mean of 0.10 is reachable with one
# moment two hundred per cent out and everything else perfect, which is the
# outcome this criterion rules out. So the mean is still what the search
# minimises -- changing it now would break comparability with two hundred
# archive points -- and the criterion below is what the search is JUDGED by, and
# it is printed every round.
DONE_BAND = 0.10        # a moment inside this is landed
DONE_ALLOWED_OUT = 1    # and this many may sit outside it


def standing(mom):
    """The acceptance scoreboard: how many moments are actually landed."""
    g = sorted((abs(mo - t) / abs(t), k) for k, (mo, t) in mom.items()
               if abs(t) > 1e-12)
    within = {b: sum(1 for x, _k in g if x <= b) for b in (0.05, 0.10, 0.25)}
    out = [(x, k) for x, k in g if x > DONE_BAND]
    print('   within  5%%: %2d of %d' % (within[0.05], len(g)))
    print('   within 10%%: %2d of %d' % (within[0.10], len(g)))
    print('   within 25%%: %2d of %d' % (within[0.25], len(g)))
    if out:
        print('   outside %d%%: %d  -- worst %s at %+.0f%%'
              % (100 * DONE_BAND, len(out), out[-1][1], 100 * out[-1][0]))
    done = len(out) <= DONE_ALLOWED_OUT
    print('   ACCEPTANCE: %s (%d outside %d%%, at most %d allowed)'
          % ('MET' if done else 'not met', len(out), 100 * DONE_BAND,
             DONE_ALLOWED_OUT))
    return done


def report(verts):
    losses = [l for _x, l in verts if l is not None]
    if losses:
        print('simplex of %d vertices: best %.3f, median %.3f, worst %.3f'
              % (len(verts), min(losses),
                 sorted(losses)[len(losses) // 2], max(losses)))
    span = 0.0
    for i in range(len(BLOCK)):
        col = [x[i] for x, _l in verts]
        span = max(span, max(col) - min(col))
    print('widest edge: a factor of %.2f in one parameter' % math.exp(span))
    return span


def emit():
    """Print the batch ALREADY RECORDED in the state file, and nothing else.

    Spawning has to happen from the batch that was written, never from a fresh
    solve: re-running the search after --write produces a different batch around
    a centre the workers were not given, which broke two rounds under the old
    method. This makes the recorded batch readable without recomputing anything,
    so a dispatcher can spawn from it and so can a check-in that has lost the
    printed output.
    """
    st = load()
    if not st or not st.get('trials'):
        print('no batch recorded')
        return
    for k in sorted(st['trials']):
        print('%s\t%s' % (k, spec(from_log(st['trials'][k]))))


def main():
    if '--emit' in sys.argv:
        emit()
        return
    pts = measured()
    seed = None
    if not pts:
        # NO POINT CARRIES THE CURRENT MOMENT SET YET. The archive still fixes
        # WHERE to start -- the best vector under the moment set it was measured
        # on is the best guess available -- but none of its vertices may be
        # reused, so the simplex is built fresh around that vector and every one
        # of its vertices is run.
        old_pts = measured(require=False)
        if not old_pts:
            print('no measured points')
            return
        seed = min(old_pts, key=lambda r: r[2])
        if SEED_OVERRIDE:
            vec = dict(seed[1])
            vec.update(SEED_OVERRIDE)
            seed = (to_log(vec), vec, seed[2], seed[3])
            print('   seed coordinates overridden: %s'
                  % ', '.join('%s=%g' % kv for kv in sorted(SEED_OVERRIDE.items())))
        print('NO POINT CARRIES %s YET, so nothing is reused.\n'
              'Seeding the simplex at the best vector measured without it: '
              '%s, loss %.3f\n' % (' and '.join(REQUIRED), seed[3], seed[2]))
        # THE SEED IS A LOCATION, NOT A MEASUREMENT. Leaving it in pts let
        # look_up hand its old-moment-set loss straight back to the base vertex,
        # which is the mixing this guard exists to prevent, one vertex at a time.
        pts = []
    st = load()
    if st is None or '--init' in sys.argv:
        verts = initial(pts if seed is None else [seed])
        if seed is not None:
            # the seed's own loss was measured on the old set, so it is not a
            # measurement of this vertex either
            verts = [(x, None) for x, _l in verts]
        st = {'iter': 0, 'phase': 'reflect', 'best_direction': None,
              'vertices': [[x, l] for x, l in verts], 'trials': None,
              'reflected': None}
        print('A FRESH SIMPLEX over all %d parameters.\n' % len(BLOCK))
    verts = [(x, l) for x, l in st['vertices']]
    verts = [(x, l if l is not None else
              (look_up(x, pts)[0] if look_up(x, pts) else None)) for x, l in verts]

    # Any vertex still unmeasured has to be run before the simplex can step.
    if any(l is None for _x, l in verts):
        todo = [x for x, l in verts if l is None]
        print('%d vertices still to measure:\n' % len(todo))
        for x in todo:
            print('  bash code/run_one_point.sh %s' % spec(from_log(x)))
        st['vertices'] = [[x, l] for x, l in verts]
        if '--write' in sys.argv:
            save(st)
        return

    # Resolve the batch in flight.
    if st.get('trials'):
        t = st['trials']
        f = {}
        for k, x in t.items():
            got = look_up(x, pts)
            if got:
                f[k] = got[0]
        if len(f) < len(t) and '--force' not in sys.argv:
            # SAY WHICH NUMBER IS WHICH. This read "5 of 67 points still
            # solving" while len(f) was the number that had LANDED, so a batch
            # with five results looked like a batch with five stragglers, and
            # the round was nearly resolved on five points out of sixty seven.
            print('iteration %d, %s: %d of %d points have landed, %d still to come'
                  % (st['iter'], st['phase'], len(f), len(t), len(t) - len(f)))
            report(verts)
            return
        phase = st['phase']
        best_now = verts[0][1]
        moved = [(t[k], f[k]) for k in sorted(f) if not k.startswith('ray')]
        rays = [(t[k], f[k]) for k in sorted(f) if k.startswith('ray')]
        best_trial = min(f.values()) if f else None

        if phase == 'all':
            verts, improved, how = resolve_speculative(verts, t, f)
            print('iteration %d: %d of %d vertices improved, by %s; '
                  'best %.3f -> %.3f'
                  % (st['iter'], improved, len(verts) - 1, how, best_now,
                     min(l for _x, l in verts)))
            st['iter'] += 1
        elif phase == 'reflect':
            if best_trial is not None and best_trial < best_now:
                # The reflection found something. Keep it and try to go further.
                st['reflected'] = [[x, l] for x, l in moved]
                st['phase'] = 'expand'
                print('iteration %d: reflection improved the best vertex, '
                      '%.3f -> %.3f. Expanding.' % (st['iter'], best_now, best_trial))
            else:
                st['phase'] = 'contract'
                print('iteration %d: no reflection beat the best vertex (%.3f). '
                      'Contracting.' % (st['iter'], best_now))
        elif phase == 'expand':
            ref = [(x, l) for x, l in st['reflected']]
            best_ref = min(l for _x, l in ref)
            if best_trial is not None and best_trial < best_ref:
                verts = [verts[0]] + moved
                print('iteration %d: the expanded simplex is better, %.3f -> %.3f.'
                      % (st['iter'], best_ref, best_trial))
            else:
                verts = [verts[0]] + ref
                print('iteration %d: the expansion did not beat the reflection; '
                      'keeping the reflected simplex at %.3f.' % (st['iter'], best_ref))
            st['reflected'] = None
            st['phase'] = 'reflect'
            st['iter'] += 1
        else:
            verts = [verts[0]] + moved
            print('iteration %d: contracted toward the best vertex.' % st['iter'])
            st['phase'] = 'reflect'
            st['iter'] += 1

        # A ray point that beat everything is worth taking whatever the phase says.
        if rays:
            br, bl = min(rays, key=lambda r: r[1])
            if bl < min(l for _x, l in verts):
                verts = [(br, bl)] + verts[:-1]
                print('   a ray point beat every vertex at %.3f and becomes the best'
                      % bl)

        verts.sort(key=lambda v: v[1])
        st['trials'] = None
        st['vertices'] = [[x, l] for x, l in verts]
        # The direction to sample next time: best vertex away from the worst.
        v0, vn = verts[0][0], verts[-1][0]
        st['best_direction'] = [v0[j] - vn[j] for j in range(len(BLOCK))]

    verts.sort(key=lambda v: v[1])
    span = report(verts)

    # Judge the best vertex against the acceptance criterion, not against zero.
    best_name = look_up(verts[0][0], pts)
    if best_name:
        for _v, mt, name in jacobian.points():
            if name == best_name[1]:
                print('\nthe best vertex, %s, against the criterion:' % name)
                if standing(mt) and span < 0.10:
                    print('\nSTOP: the criterion is met and the simplex is tight. '
                          'Further rounds are polishing, not calibrating.')
                    return
                break

    if span < 0.02:
        print('\nCONVERGED on the parameters: the widest edge is under two per '
              'cent, whatever the moments say. If the criterion above is not met '
              'at this point, no vector nearby meets it and the remaining gaps '
              'are a specification question rather than a search one.')
        return

    if '--speculative' in sys.argv:
        st['phase'] = 'all'
        scales = 3
        for a in sys.argv:
            if a.startswith('--scales='):
                scales = int(a.split('=')[1])
        t = speculative_set(verts, scales)
    else:
        if st.get('phase') == 'all':
            st['phase'] = 'reflect'
        t = step_set(verts, st['phase'])
    if st.get('best_direction'):
        t.update(ray_set(verts[0][0], st['best_direction']))
    jc = jacobian_candidate(verts, jacobian.points())
    if jc is not None and max(abs(a - b) for a, b in zip(jc, verts[0][0])) > MATCH:
        t['jacobian'] = jc
    st['vertices'] = [[x, l] for x, l in verts]
    st['trials'] = t
    if '--write' in sys.argv:
        save(st)
    print('\nIteration %d, %s: %d points, all at once (%s):\n'
          % (st['iter'], st['phase'], len(t),
             '--write recorded them' if '--write' in sys.argv
             else 'not recorded, pass --write'))
    for k in sorted(t):
        print('  bash code/run_one_point.sh %s   # %s' % (spec(from_log(t[k])), k))


if __name__ == '__main__':
    main()
