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
POOL_MULT = 5.0


def instruments_all(N, NB):
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
    scope = set()
    for st in NB.STAGES:
        scope |= set(st)
    scope -= set(NB.UNSCORED) | set(NB.SKIP)
    A = N.archive()
    seen = set()
    for _, m in A.values():
        seen |= set(m)
    out, dead = [], []
    for p, m in sorted(NB.OWN.items()):
        if m not in scope or p not in NB.BOUNDS:
            continue
        (out if m in seen else dead).append((p, m))
    return out, dead


def setup():
    import newton as N, next_batch as NB
    NB._apply_process_mapping()
    inst, dead = instruments_all(N, NB)
    if dead:
        print('  dropped, never measured on this economy: '
              + ', '.join(m for _, m in dead))
    return N, NB, inst, [p for p, _ in inst], [m for _, m in inst]


def ssr(N, mom, keys):
    r = N.residual(mom, keys)
    return sum(x * x for x in r)


def to_u(NB, v, names):
    u = []
    for p in names:
        lo, hi = NB.BOUNDS[p]
        u.append((float(v[p]) - lo) / (hi - lo) if hi > lo else 0.0)
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


def trace(st, kind, f, inside, ntot):
    """One line per evaluation, with the BEST SSR after it.

    *"and after each iteration, i want to get a reading on the new best SSR"* --
    the author, 4 September.  The loop's own stdout carries it, but buried among
    the solver's chatter and rewritten by every restart, so it goes to its own
    file as well: one fixed-width line per model solve, appended, never
    rewritten, committed with the points.  An arrow marks the evaluations that
    actually moved the best, which is the thing being asked for -- most
    reflections do not.
    """
    S = st['simplex']
    b = S[0]['f']
    moved = '  <-- NEW BEST' if abs(f - b) < 1e-12 else ''
    import time
    with open(TRACE, 'a') as fh:
        fh.write(f'{st["evals"]:4d}  {time.strftime("%H:%M:%S")}  {kind:34s}  '
                 f'this {f:9.4f}   best {b:9.4f}  {S[0]["tag"]}  '
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
            i = st['shrink_i']
            u = [min(max(b + SIGMA * (x - b), 0.0), 1.0)
                 for b, x in zip(S[0]['u'], S[i]['u'])]
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
            S.sort(key=lambda d: d['f'])
            rb = N.residual(A[S[0]['tag']][1], keys)
            trace(st, kind, f, sum(1 for x in rb if abs(x) <= 0.10), len(rb))

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
                st['phase'] = 'shrink'; st['shrink_i'] = 1
                st['pending'] = None; save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
        elif kind.startswith('shrink:'):
            i = int(kind.split(':')[1])
            S[i] = node
            if i + 1 < len(S):
                st['shrink_i'] = i + 1; msg = f'shrunk vertex {i}'
            else:
                st['phase'] = 'reflect'; msg = 'shrink complete'
                st['pending'] = None; S.sort(key=lambda d: d['f']); save(st)
                print(f'  {kind}  SSR {f:.4f}   {msg}')
                _t(); report(st); return 0
            st['pending'] = None; S.sort(key=lambda d: d['f']); save(st)
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
