"""Sequential Nelder-Mead on the fifteen open instruments.

*"you claimed this method was better than nelder mead, and faster....but we have
been stuck on it for like 12 hr"* and *"we are better off trying nelder mead
sequentially"* and *"since each iteration is just 2.5 minutes, we are better off
doing that"* -- the author, 4 September.

WHY NEWTON WAS THE WRONG TOOL HERE, recorded so it is not tried a fourth time.
Three Jacobians were measured, fifteen model solves each.  Every step they
produced landed ABOVE its own base: base SSR 0.9603, full step 2.2025, quarter
step 1.7283.  The cause is the drug block.  A finite-difference nudge of 0.35 per
cent in addiction_scalar_1 moves lambda_d from -4.5 per cent to -96.5 per cent,
so that column of the Jacobian is not a derivative of anything -- it is a secant
across a cliff -- and being the largest column by far it dominates the normal
equations and drags every other instrument with it.  A truncated SVD cannot fix
that, because the direction is strongly identified; it is just not linear.

Nelder-Mead never differentiates.  It only ever compares two measured objective
values, so a cliff in one coordinate costs it one reflection, not a whole step.

THE OBJECTIVE is the sum of squared residuals over the fifteen open moments, the
same number gaps.py prints and newton.best now ranks on, so "better" here and
"better" in the report cannot disagree.

COORDINATES are scaled to the unit box, u = (x-lo)/(hi-lo).  The raw units span
six orders of magnitude -- value_of_life is ~42 and bottom_productivity_level is
~0.004 -- and a simplex built in raw units is degenerate on arrival.  Bounds are
enforced by clipping the trial back into the box, which is standard for
bound-constrained Nelder-Mead and costs at worst a wasted reflection.

THE INITIAL SIMPLEX IS SEEDED FROM POINTS ALREADY MEASURED.  There are 152 solved
points on this economy, most of them single-instrument perturbations of the base
left behind by the three Jacobians.  Sixteen affinely independent vertices are
picked out of them greedily, by Gram-Schmidt residual, so the search starts with
a full simplex having spent NO model time.  That is the one thing the Newton work
leaves behind that is worth keeping.

A TRIAL THAT HAS ALREADY BEEN MEASURED IS NOT RE-RUN.  A vector's tag is the md5
of the vector, so re-running one overwrites a real measurement with an identical
one and wastes 2.5 minutes; --ask prints nothing and --tell reads the archive.

Usage, one model solve per turn of the loop:

    python3 code/nelder.py --init          # build the simplex from the archive
    python3 code/nelder.py --ask           # writes code/batch_nm.txt, ONE line
    bash code/batch_nm.txt                 # 2.5 minutes
    python3 code/nelder.py --tell          # score it, update the simplex

code/nm_loop.sh does those three forever.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

STATE = os.path.join(HERE, '.nm_state.json')
BATCH = os.path.join(HERE, 'batch_nm.txt')

# The textbook coefficients.  Reflection, expansion, contraction, shrink.
ALPHA, GAMMA, RHO, SIGMA = 1.0, 2.0, 0.5, 0.5

# How long an edge has to be, in the unit box, to count as its own direction.
MIN_EDGE = 0.05

# How much worse than the best a seed vertex may be.
#
# 5.0 WAS RIGHT FOR AN ARCHIVE-SEEDED SIMPLEX AND WRONG FOR A PURPOSE-BUILT ONE.
# The cap exists to stop greedy Gram-Schmidt over a whole archive dragging in a
# vertex from an abandoned corner at SSR 7202. But the rescale round builds the
# simplex deliberately -- one instrument per vertex, ten per cent of its own
# range -- and those displacements legitimately span SSR 1.46 to 1608 because
# some instruments are near a corner. At 5.0 the cap admitted twelve of
# twenty-one and left NINE DIRECTIONS UNSPANNED, which is the anisotropy problem
# the rescale round was run to fix, returning as a filter rather than as a
# geometry. A bad vertex costs a few contractions; a missing direction costs the
# instrument entirely.
POOL_MULT = 2000.0


# THE AUTHOR'S STAGES, 4 September: "calibrate the seven inside 10%, then add,
# pi_V, tau_l, aleph, sigma_y, pi_eu....and keep the rest after you finish the
# first one. aleph is very important".
#
# THIS IS NOT THE OLD STAGING RETURNING. That staging existed to keep a secant
# well conditioned and was dropped because a direct search forms no secant. This
# staging exists for a different and better reason: DIMENSION. nelder_test.py
# passes 8-dim Rosenbrock at 4.6e-14 and FAILS 20-dim at 0.187 with three
# thousand evaluations, so Nelder-Mead is competent at seven or twelve
# instruments and not at twenty. Staging puts the search back where it works.
#
# It also makes seeding cheap: a stage of seven needs eight vertices, not
# twenty-one.
# FROZEN. The author, 4 September: *"stop restarting NM and let it run"*.
#
# THIS LIST MUST NOT CHANGE WHILE THE SOLVER IS RUNNING. Every edit to it forces
# stage_night to re-init, and a re-init throws away the simplex and rebuilds
# thirteen vertices before a single search step -- about two hours at the current
# contention. Reading the trace for 4 September: the scope went 9 instruments, then
# 10, then 12, then all 21, then 12/4/5, and in four hours Nelder-Mead took SEVEN
# actual search steps and spent everything else building simplexes it then threw
# away. It never got a run at the problem, and that was my churn, not the method.
#
# Any future change waits until the stage has converged or the author asks for it.

# TWELVE, FOUR, FIVE -- the author's shape, 4 September: *"the first stage can be
# 12 parameters maybe... and you can do the second stage with the extra 3-4 and 3rd
# stage with another 4-5"*, under their constraint *"you cannot hold anything in
# stage 1 fixed on the parameters that are key"*.
#
# WHY NOT ONE STAGE OF TWENTY-ONE. Measured, not assumed. nelder_test.py drives
# this exact ask/tell machine against analytic objectives:
#
#     quadratic bowl, 21-dim     3000 evals    2.4e-10        PASS
#     ROSENBROCK,     21-dim     3000 evals    4.42           FAIL   (want < 1e-3)
#     Rosenbrock,      8-dim      900 evals    1.2e-12        PASS
#
# The bowl says the machinery is sound at twenty-one; the Rosenbrock says
# Nelder-Mead cannot follow a curved valley in that many dimensions. A calibration
# is a curved valley. So one stage of twenty-one was tried on the author's
# instruction, measured, and cut back.
#
# THE CUT ITSELF answers the author's objection rather than the dimension count:
# stage 1 holds nothing that stage 1's own parameters are being fitted against.
# The income process (sigma_y, pi_eu), the tax that turns it into net income
# (tau_l), every preference parameter (beta, gamma, omega_l, theta), what
# mortality is worth (aleph), both onset hazards (lambda_d, p_m), addiction
# prevalence (b) and subsistence (cbar) move together. Twelve.
#
# What is deferred is DOWNSTREAM of that block, not held against it:
#
#  2. the housing and homelessness block, level and composition TOGETHER because
#     they are the pair that fight -- h_1 sets how big the street is and h_share5
#     who is on it, and moving them in turn is what produced the level/composition
#     conflict. h_2 is the rent the choice is made against and pi_V the voucher.
#
#  3. the SUD and treatment margins, which only bite once a homeless population
#     exists to measure them on: sud_homeless, emp_homeless, lambda_m, tau_u, mu_H.
STAGE_MOMENTS = [
    ['sigma_y', 'pi_eu', 'tau_l', 'beta', 'gamma', 'omega_l', 'theta',
     'aleph', 'lambda_d', 'b', 'p_m', 'cbar'],
    ['h_1', 'h_2', 'h_share5', 'pi_V'],
    ['sud_homeless', 'emp_homeless', 'lambda_m', 'tau_u', 'mu_H'],
]


def stage_scope(n):
    """The moments in scope at stage n, cumulative."""
    out = set()
    for i in range(min(n, len(STAGE_MOMENTS))):
        out |= set(STAGE_MOMENTS[i])
    return out


def instruments_all(N, NB, stage=None):
    """Every instrument in every stage, because Nelder-Mead does not need stages.

    *"and in fact, with Nelder Mead, i think you can just converge on all the
    points at the same time, no?"* and *"you can do all the stages combined"* --
    the author, 4 September.  He is right, and the reason is worth writing down:
    staging existed to keep the LOCAL problem well conditioned, because a secant
    or a Jacobian column is only meaningful when the other instruments are still.
    A direct search never forms either, so the only thing staging buys it is a
    smaller simplex, and the price is that the stage-0 optimum is not the joint
    optimum -- tau_u sits 85.5 per cent off while stage 0 polishes moments that
    it is coupled to.

    A moment NO POINT IN THE ARCHIVE MEASURES is dropped, and its instrument with
    it.  residual() scores an absent moment as zero, so keeping one would add a
    coordinate the objective is flat in: the simplex would wander in it forever
    and every shrink would cost an extra solve.  sud_homeless is never emitted
    and omega_c needs measure_child_gap=1, so both go; if the model starts
    emitting them they come back here on their own.
    """
    if stage:
        scope = stage_scope(stage)
    else:
        scope = set()
        for st in NB.STAGES:
            scope |= set(st)
    scope -= set(NB.UNSCORED) | set(NB.SKIP)
    A = N.archive()
    seen = set()
    for _, m in A.values():
        seen |= set(m)
    # A MOMENT IS ONLY DEAD IF THE ARCHIVE COULD HAVE SHOWN IT AND DID NOT.
    # On a fresh economy the archive is empty, so `seen` is empty and every
    # moment looks dead -- which silently produced a stage with ZERO
    # instruments. The check is about a moment the model never emits, so it
    # needs points to have been measured before it means anything.
    out, dead = [], []
    for p, m in sorted(NB.OWN.items()):
        if m not in scope or p not in NB.BOUNDS:
            continue
        (out if (m in seen or not seen) else dead).append((p, m))
    return out, dead


def stage_now():
    """The live stage, from code/nm_stage.txt. Absent means all instruments."""
    f = os.path.join(HERE, 'nm_stage.txt')
    try:
        return int(open(f).read().strip())
    except Exception:
        return None


# THE SIMPLEX ONLY SPANS THE MOMENTS THAT ARE STILL OUTSIDE THE BAND.
#
# The author, 4 September, after the same rule was put into the fixed point: *"can
# you do the same with the NM algorithm? when you open more stages, you keep
# updating only the ones that are outside the 10% in the best point?"*
#
# THE OBJECTIVE IS UNCHANGED -- every scored moment still counts, so a held
# parameter's moment cannot be wrecked for free. Only the DIMENSIONS of the
# simplex shrink. That distinction is not cosmetic: stage_test.py measured the two
# forms against each other and the block-only objective was FROZEN, identical to
# six figures between 900 and 3000 evaluations, while the full-objective form
# progressed 9.41 -> 6.28.
#
# WHY IT SHOULD HELP MORE HERE THAN ANYWHERE ELSE. nelder_test.py measures this
# machine solving a 12-dimensional Rosenbrock to 5.22e-13 and failing a
# 21-dimensional one at 4.42. Dimension is the binding constraint, and this makes
# it ADAPTIVE: eleven of twenty-one moments are inside ten per cent right now, so
# the simplex would span ten rather than twenty-one, and it shrinks further as
# more arrive.
#
# The band is re-read at every --init, so a moment that drifts back out brings its
# parameter back into the search on the next rebuild.
NM_BAND = float(os.environ.get('NM_BAND', '0.10'))
# A HELD parameter needs a gap this large to come back into the simplex. The
# gap between the two is the hysteresis; equal values reproduce the old
# single-threshold behaviour, and thrash with it.
NM_RELEASE = float(os.environ.get('NM_RELEASE', '0.15'))


def _previously_live():
    """The parameters the CURRENT simplex spans, or None if there is no simplex."""
    try:
        return set(json.load(open(STATE))['names'])
    except Exception:
        return None


def outside_band(N, NB, inst, keys):
    """The instruments whose own moment is outside the band at the live best.

    HYSTERESIS: HOLD AT NM_BAND, RELEASE AT NM_RELEASE.

    With one threshold for both, a moment sitting near the line is held, released
    and held again as the incumbent moves, and every re-entry SHRINKS the live set,
    which is what triggers a rebuild in stage_night. A parameter hovering at 9.9
    and 10.1 per cent would spend the night re-seeding the simplex at three model
    solves a time and never search anything.

    So the two directions have different thresholds: a LIVE parameter is held once
    its gap is inside NM_BAND, and a HELD parameter is only released once its gap
    exceeds NM_RELEASE. A parameter cannot change state twice inside that gap, so
    it cannot thrash.

    On a cold start there is no previous simplex and _previously_live() returns
    None; then every instrument is judged on NM_BAND alone, which is the old
    behaviour and the right one -- with nothing held, nothing can be released.
    """
    A = N.archive()
    if not A:
        return inst
    try:
        _, _, _, mom = N.best(A, keys)
    except Exception:
        return inst
    if not mom:
        return inst
    was = _previously_live()
    out = []
    for p, m in inst:
        if m not in mom or not mom[m][1]:
            out.append((p, m))
            continue
        gap = abs(mom[m][0] / mom[m][1] - 1.0)
        held_before = was is not None and p not in was
        if gap > (NM_RELEASE if held_before else NM_BAND):
            out.append((p, m))
    # NEVER RETURN AN EMPTY SIMPLEX. If everything is inside the band the stage is
    # converged and the caller decides that; handing back nothing would build a
    # one-vertex simplex, which is the fault nelder_test.py caught on 4 September.
    return out or inst


def setup():
    import newton as N, next_batch as NB
    NB._apply_process_mapping()
    inst, dead = instruments_all(N, NB, stage_now())
    if dead:
        print('  dropped, never measured on this economy: '
              + ', '.join(m for _, m in dead))
    keys = [m for _, m in inst]            # THE WHOLE OBJECTIVE, always
    live = outside_band(N, NB, inst, keys)
    if len(live) < len(inst):
        held = sorted(m for _, m in inst if (_, m) not in live)
        print(f'  simplex spans {len(live)} of {len(inst)} instruments; '
              f'{len(inst) - len(live)} held inside {NM_BAND:.0%}')
    return N, NB, live, [p for p, _ in live], keys


def ssr(N, mom, keys):
    r = N.residual(mom, keys)
    return sum(x * x for x in r)


def to_u(NB, v, names):
    """Scaled coordinates, CLIPPED to the box.

    A point whose value for an instrument lies outside that instrument's bounds
    -- which happens when a parameter's default and its bounds disagree, as
    rr_homeless_old_level's did on the day it was added -- otherwise produces a
    negative or greater-than-one coordinate, and every distance and centroid
    computed from it is then outside the box the search believes it is in.
    """
    u = []
    for p in names:
        lo, hi = NB.BOUNDS[p]
        x = (float(v[p]) - lo) / (hi - lo) if hi > lo else 0.0
        u.append(min(max(x, 0.0), 1.0))
    return u


def to_x(NB, u, names):
    x = {}
    for p, uu in zip(names, u):
        lo, hi = NB.BOUNDS[p]
        x[p] = min(max(lo + uu * (hi - lo), lo), hi)
    return x


def vector_for(N, NB, base_v, names, u):
    """A full run vector: the base point's, with the fifteen instruments moved."""
    v = dict(base_v)
    for p, val in to_x(NB, u, names).items():
        v[p] = f'{val:.8g}'
    return v


def find_measured(N, NB, base_v, names, u, A):
    """The archive tag of this exact vector, or None.

    NOT the md5, deliberately.  run_one_point.sh hashes the newline-joined
    name=value list and ALSO recognises a LEGACY_TAG in which a name still at the
    default it was introduced with is dropped, so a vector can legitimately land
    in a file whose name this module cannot predict.  Matching on the VECTOR line
    the point file records is the thing the header of run_one_point.sh says the
    coordinator should do: read what was actually run.
    """
    want = vector_for(N, NB, base_v, names, u)
    for tag, (v, m) in A.items():
        if len(v) != len(want):
            continue
        ok = True
        for k, val in want.items():
            if k not in v:
                ok = False; break
            try:
                if abs(float(v[k]) - float(val)) > 1e-12 * max(1.0, abs(float(val))):
                    ok = False; break
            except ValueError:
                if v[k] != val:
                    ok = False; break
        if ok:
            return tag
    return None


def seed(N, NB, inst, names, keys):
    """Sixteen affinely independent measured vertices, greedily by GS residual.

    THE POOL IS CAPPED BY OBJECTIVE VALUE, not by independence alone.  Greedy
    Gram-Schmidt over all 152 points spans the whole box and drags in vertices at
    SSR 7201, left behind in an abandoned corner of the search.  Nelder-Mead does
    contract those away, but each contraction is a 2.5 minute model solve spent
    recovering ground already known to be bad.  Taking the widest sixteen out of
    the best POOL instead starts every vertex inside the competitive region: the
    best 64 points on this economy are all under SSR 2.67.  The cap widens only
    if sixteen independent directions cannot be found inside it.
    """
    A = N.archive()
    pts = []
    for tag, (v, m) in A.items():
        if any(p not in v for p in names):
            continue
        try:
            f = ssr(N, m, keys)
        except Exception:
            continue
        pts.append((f, tag, to_u(NB, v, names), v))
    pts.sort()
    if not pts:
        raise SystemExit('no scored points on this economy')

    # A VERTEX HAS TO BE COMPETITIVE, and if no measured point spans a direction
    # competitively the direction is left to --ask to fill with a fresh solve.
    # Widening the pool until a nineteenth direction appeared put a vertex at SSR
    # 693 into the simplex against a best of 1.99; Nelder-Mead would spend four
    # or five solves contracting that away, which is more than the single solve a
    # fill costs.  POOL_MULT is on the objective, not on a rank, so it does not
    # drift as the archive grows.
    k = len(names)
    chosen = []
    for pool in (64, 96, 128, len(pts)):
        cand = [q for q in pts[:pool] if q[0] <= POOL_MULT * pts[0][0]]
        chosen, basis = [cand[0]], []
        for _ in range(k):
            # THE LOWEST-f CANDIDATE THAT IS INDEPENDENT ENOUGH, not the most
            # independent one.  Maximising the Gram-Schmidt residual picks the
            # candidate FURTHEST from the span, which is reliably the worst point
            # in the pool: widening the pool to find a nineteenth direction
            # promptly dragged in the SSR 7202 vertex again.  A direction only
            # has to be well conditioned, not extremal, so cand is walked in
            # ascending f and the first vertex clearing MIN_EDGE of the unit box
            # is taken.  The max-residual pick stays as the fallback for a
            # direction nothing in the pool spans well.
            bestj, bestr, bestw = None, 0.0, None
            for j, (f, tag, u, v) in enumerate(cand):
                if any(tag == c[1] for c in chosen):
                    continue
                w = [x - y for x, y in zip(u, chosen[0][2])]
                for e in basis:
                    d = sum(x * y for x, y in zip(w, e))
                    w = [x - d * y for x, y in zip(w, e)]
                nrm = sum(x * x for x in w) ** 0.5
                if nrm > MIN_EDGE:
                    bestj, bestr, bestw = j, nrm, w
                    break
                if nrm > bestr:
                    bestj, bestr, bestw = j, nrm, w
            if bestj is None or bestr < 1e-9:
                break
            basis.append([x / bestr for x in bestw])
            chosen.append(cand[bestj])
        if len(chosen) == k + 1:
            break
    return chosen, len(pts)


def save(st):
    json.dump(st, open(STATE, 'w'), indent=1)


TRACE = os.path.join(HERE, 'nm_trace.txt')


def trace(st, kind, f, inside, ntot, best_f, best_tag):
    """One line per evaluation, with the BEST SSR after it.

    *"and after each iteration, i want to get a reading on the new best SSR"* --
    the author, 4 September.  The loop's own stdout carries it, but buried among
    the solver's chatter and rewritten by every restart, so it goes to its own
    file as well: one fixed-width line per model solve, appended, never
    rewritten, committed with the points.  An arrow marks the evaluations that
    actually moved the best, which is the thing being asked for -- most
    reflections do not.
    """
    moved = '  <-- NEW BEST' if abs(f - best_f) < 1e-12 else ''
    import time
    with open(TRACE, 'a') as fh:
        fh.write(f'{st["evals"]:4d}  {time.strftime("%H:%M:%S")}  {kind:34s}  '
                 f'this {f:9.4f}   best {best_f:9.4f}  {best_tag}  '
                 f'inside {inside}/{ntot}{moved}\n')


def report(st):
    S = st['simplex']
    print(f'  simplex {len(S)} vertices   best {S[0]["f"]:.4f} ({S[0]["tag"]})   '
          f'worst {S[-1]["f"]:.4f}   spread {S[-1]["f"] - S[0]["f"]:.4f}')


def main():
    args = sys.argv[1:]
    N, NB, inst, names, keys = setup()

    if '--init' in args:
        chosen, npts = seed(N, NB, inst, names, keys)
        if len(chosen) < len(names) + 1:
            print(f'WARNING: only {len(chosen)} independent vertices from {npts} '
                  f'measured points; {len(names)+1} wanted.')
            print('The missing directions are instruments no measured point ever '
                  'moved off the base.  --ask will fill them one at a time.')
        base_v = chosen[0][3]
        st = {'names': names, 'keys': keys,
              'base_v': {kk: base_v[kk] for kk in base_v},
              'simplex': [{'u': u, 'f': f, 'tag': tag} for f, tag, u, _ in chosen],
              'phase': 'reflect', 'pending': None, 'evals': 0, 'history': []}
        st['simplex'].sort(key=lambda d: d['f'])
        save(st)
        print(f'seeded from {npts} measured points, {len(chosen)} vertices, '
              f'ZERO model solves')
        report(st)
        return 0

    st = json.load(open(STATE))
    names, keys = st['names'], st['keys']
    base_v = st['base_v']
    S = st['simplex']

    if '--ask' in args:
        if st['pending'] is not None:
            print('a trial is already pending; run --tell first')
            return 1
        k = len(names)

        # A short simplex is completed before any reflection: a direction no
        # vertex spans is a direction the search can never move in, and NM gives
        # no error when that happens -- it just silently optimises a subspace.
        if len(S) < k + 1:
            have = [[a - b for a, b in zip(d['u'], S[0]['u'])] for d in S[1:]]
            basis = []
            for w in have:
                for e in basis:
                    dd = sum(a * b for a, b in zip(w, e))
                    w = [a - dd * b for a, b in zip(w, e)]
                nn = sum(a * a for a in w) ** 0.5
                if nn > 1e-9:
                    basis.append([a / nn for a in w])
            for i in range(k):
                w = [1.0 if j == i else 0.0 for j in range(k)]
                for e in basis:
                    dd = sum(a * b for a, b in zip(w, e))
                    w = [a - dd * b for a, b in zip(w, e)]
                if sum(a * a for a in w) ** 0.5 > 1e-6:
                    u = list(S[0]['u'])
                    u[i] = min(max(u[i] + 0.10, 0.0), 1.0)
                    if abs(u[i] - S[0]['u'][i]) < 1e-9:
                        u[i] = min(max(S[0]['u'][i] - 0.10, 0.0), 1.0)
                    kind = f'fill:{names[i]}'
                    break
            else:
                kind = None
            if kind:
                st['pending'] = {'u': u, 'kind': kind}
                save(st)
                open(BATCH, 'w').write(N.line(vector_for(N, NB, base_v, names, u)))
                print(f'{kind}   simplex is short {k+1-len(S)} directions')
                return 0

        cen = [sum(d['u'][i] for d in S[:-1]) / (len(S) - 1) for i in range(k)]
        w = S[-1]['u']
        ph = st['phase']
        if ph == 'reflect':
            u = [min(max(c + ALPHA * (c - x), 0.0), 1.0) for c, x in zip(cen, w)]
            kind = 'reflect'
        elif ph == 'expand':
            u = [min(max(c + GAMMA * (c - x), 0.0), 1.0) for c, x in zip(cen, w)]
            kind = 'expand'
        elif ph == 'contract_out':
            rr = st['refl']['u']
            u = [min(max(c + RHO * (x - c), 0.0), 1.0) for c, x in zip(cen, rr)]
            kind = 'contract_out'
        elif ph == 'contract_in':
            u = [min(max(c + RHO * (x - c), 0.0), 1.0) for c, x in zip(cen, w)]
            kind = 'contract_in'
        elif ph == 'shrink':
            # THE ANCHOR IS SAVED, NOT READ OFF S[0].
            #
            # A shrink is the one step that addresses vertices BY INDEX across
            # several evaluations, so it is the only one that cannot survive the
            # simplex being reordered underneath it -- and the simplex WAS being
            # reordered, by a sort at the end of every --tell. Measured by
            # nelder_test.py's shrink audit on an eight-vertex simplex: four
            # vertices were never shrunk at all and four were shrunk TWICE,
            # landing at 0.6 of the way to the anchor instead of 0.5. Nothing in
            # the output said so; the phase advanced and the search carried on
            # with a simplex half of which had not moved.
            #
            # Reading S[0] was the second half of the same fault: a shrunk vertex
            # that beats the incumbent becomes S[0], and the rest of the walk
            # then contracts toward a different point than it started from.
            i = st['shrink_i']
            # A state written before the anchor existed -- a run already
            # mid-shrink when this was fixed -- falls back to the incumbent,
            # which is what the old code always did.
            anchor = st.get('shrink_anchor') or list(S[0]['u'])
            st['shrink_anchor'] = anchor
            u = [min(max(b + SIGMA * (x - b), 0.0), 1.0)
                 for b, x in zip(anchor, S[i]['u'])]
            kind = f'shrink:{i}'
        else:
            print(f'unknown phase {ph}'); return 1

        st['pending'] = {'u': u, 'kind': kind}
        save(st)
        open(BATCH, 'w').write(N.line(vector_for(N, NB, base_v, names, u)))
        print(f'{kind}')
        return 0

    if '--tell' in args:
        p = st['pending']
        if p is None:
            print('nothing pending'); return 1
        A = N.archive()
        want = find_measured(N, NB, base_v, names, p['u'], A)
        if want is None:
            print('the trial vector is not in the archive yet; '
                  'run bash code/batch_nm.txt')
            return 1
        f = ssr(N, A[want][1], keys)
        node = {'u': p['u'], 'f': f, 'tag': want}
        kind, ph = p['kind'], st['phase']
        st['evals'] += 1
        st['history'].append({'kind': kind, 'f': f, 'tag': want})
        best_f, worst_f = S[0]['f'], S[-1]['f']
        second = S[-2]['f'] if len(S) > 1 else worst_f
        msg = ''

        def _t():
            # How many of the scored moments the LIVE BEST vertex has inside ten
            # per cent, which is the author's stopping rule, alongside the SSR
            # the search actually minimises.
            #
            # IT MUST NOT SORT. It did, and that was a second way into the shrink
            # bug below: a trace helper quietly reordering the simplex is exactly
            # the kind of thing the indexed shrink cannot survive. The caller
            # sorts when sorting is correct; this only reads.
            b = min(S, key=lambda d: d['f'])
            e = A.get(b['tag'])
            rb = N.residual(e[1], keys) if e else []
            trace(st, kind, f, sum(1 for x in rb if abs(x) <= 0.10), len(rb),
                  b['f'], b['tag'])

        if kind.startswith('fill:'):
            S.append(node); msg = 'direction added'
        elif kind == 'reflect':
            if f < best_f:
                st['refl'] = node; st['phase'] = 'expand'
                msg = 'better than the best; trying an expansion'
                st['pending'] = None; S.sort(key=lambda d: d['f']); save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
            if f < second:
                S[-1] = node; msg = 'accepted, reflection'
            elif f < worst_f:
                st['refl'] = node; st['phase'] = 'contract_out'
                msg = 'between the second worst and the worst; contracting outside'
                st['pending'] = None; save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
            else:
                st['refl'] = node; st['phase'] = 'contract_in'
                msg = 'worse than the worst; contracting inside'
                st['pending'] = None; save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
            st['phase'] = 'reflect'
        elif kind == 'expand':
            r = st['refl']
            S[-1] = node if f < r['f'] else r
            msg = 'expansion kept' if f < r['f'] else 'expansion rejected, reflection kept'
            st['phase'] = 'reflect'
        elif kind in ('contract_out', 'contract_in'):
            ref = st['refl']['f'] if kind == 'contract_out' else worst_f
            if f < ref:
                S[-1] = node; msg = 'contraction accepted'; st['phase'] = 'reflect'
            else:
                msg = 'contraction failed; shrinking'
                S.sort(key=lambda d: d['f'])
                st['phase'] = 'shrink'; st['shrink_i'] = 1
                st['shrink_anchor'] = list(S[0]['u'])
                st['pending'] = None; save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
        elif kind.startswith('shrink:'):
            i = int(kind.split(':')[1])
            S[i] = node
            if i + 1 < len(S):
                # NO SORT HERE. The walk is still running and the next index
                # must mean the same vertex it meant when the walk started.
                st['shrink_i'] = i + 1; msg = f'shrunk vertex {i}'
            else:
                st['phase'] = 'reflect'; msg = 'shrink complete'
                st.pop('shrink_anchor', None)
                st['pending'] = None; S.sort(key=lambda d: d['f']); save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
            st['pending'] = None; save(st)
            print(f'  {kind}  SSR {f:.4f}   {msg}')
            _t(); report(st); return 0

        st['pending'] = None
        S.sort(key=lambda d: d['f'])
        save(st)
        print(f'  {kind}  SSR {f:.4f}   {msg}')
        _t()
        report(st)
        return 0

    if '--status' in args:
        report(st)
        print(f'  {st["evals"]} evaluations, phase {st["phase"]}')
        for h in st['history'][-12:]:
            print(f'    {h["kind"]:16s} {h["f"]:.4f}  {h["tag"]}')
        return 0

    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main())
