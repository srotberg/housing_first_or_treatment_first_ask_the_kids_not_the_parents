"""Drive the REAL nelder.py against analytic objectives whose minimum is known.

*"are you sure you implemented the algorithm correctly?"* -- the author,
4 September.  The answer to that is a test, not an assurance.

This does not reimplement Nelder-Mead.  It stubs out the two things nelder.py
talks to -- the archive of solved points and the bounds table -- and then runs
its actual --ask/--tell state machine, evaluating each trial with a function
whose minimiser is known in closed form.  Whatever the search does to the model
it does here.

    python3 code/nelder_test.py
"""
import os, sys, types, json, math, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

K = 8                                   # instruments in the toy problem
NAMES = [f'p{i}' for i in range(K)]
KEYS = [f'm{i}' for i in range(K)]


def make_fakes(resid):
    """Stand-ins for newton and next_batch, backed by an in-memory archive."""
    arch = {}

    def tag_of(v):
        import hashlib
        return hashlib.md5(' '.join(f'{k}={v[k]}' for k in sorted(v))
                           .encode()).hexdigest()[:10]

    N = types.ModuleType('newton')
    NB = types.ModuleType('next_batch')
    NB.BOUNDS = {p: (-2.0, 2.0) for p in NAMES}
    NB.OWN = dict(zip(NAMES, KEYS))
    NB.STAGES = [set(KEYS)]
    NB.UNSCORED = set()
    NB.SKIP = set()
    NB._apply_process_mapping = lambda: None
    NB.EQUIVALENT_MODELS = {}
    NB.CONFIG_SWITCHES = {}

    N.archive = lambda: dict(arch)
    N.residual = lambda mom, keys: [mom[k][0] / mom[k][1] - 1 for k in keys]
    N.line = lambda v: 'RUN ' + ' '.join(f'{k}={v[k]}' for k in sorted(v)) + '\n'

    def solve(v):
        """Evaluate the objective at a vector and put it in the archive."""
        x = [float(v[p]) for p in NAMES]
        g = resid(x)
        mom = {k: (1.0 + gi, 1.0) for k, gi in zip(KEYS, g)}
        t = tag_of(v)
        arch[t] = (dict(v), mom)
        return t

    return N, NB, arch, solve


def run(resid, x0, iters, label, tol):
    N, NB, arch, solve = make_fakes(resid)
    sys.modules['newton'] = N
    sys.modules['next_batch'] = NB
    for m in ('nelder',):
        sys.modules.pop(m, None)
    import nelder as NM
    d = tempfile.mkdtemp()
    NM.STATE = os.path.join(d, 'state.json')
    NM.BATCH = os.path.join(d, 'batch.txt')
    NM.TRACE = os.path.join(d, 'trace.txt')

    # A starting simplex: x0 and x0 + 0.4 e_i, all solved.
    for i in range(K + 1):
        v = {p: f'{x0[j] + (0.4 if j == i - 1 else 0.0):.10g}'
             for j, p in enumerate(NAMES)}
        solve(v)

    argv = sys.argv
    sys.argv = ['nelder.py', '--init']
    NM.main()
    for it in range(iters):
        sys.argv = ['nelder.py', '--ask']
        if NM.main() != 0:
            break
        line = open(NM.BATCH).read().strip()
        v = dict(kv.split('=', 1) for kv in line.split()[1:])
        solve(v)
        sys.argv = ['nelder.py', '--tell']
        NM.main()
    sys.argv = argv
    st = json.load(open(NM.STATE))
    best = st['simplex'][0]['f']
    ok = best < tol
    print(f'{label:34s} {iters:4d} evals   best {best:12.3ე}' if False else
          f'{label:34s} {iters:4d} evals   best {best:12.6g}   '
          f'{"PASS" if ok else "FAIL"}  (want < {tol})')
    return ok, st


def quad(x):
    """Minimum 0 at x = 0.5 in every coordinate."""
    return [xi - 0.5 for xi in x]


def rosen(x):
    """Rosenbrock residuals; minimum 0 at x = 1 in every coordinate."""
    g = []
    for i in range(len(x) - 1):
        g.append(10.0 * (x[i + 1] - x[i] * x[i]))
        g.append(1.0 - x[i])
    return (g + [0.0] * len(x))[:len(x)]


def shrink_audit():
    """Does a shrink move EVERY vertex toward the anchor, exactly once?

    The shrink is the one step whose vertices are addressed BY INDEX across
    several evaluations, so it is the one the simplex being re-sorted underneath
    it can corrupt.
    """
    N, NB, arch, solve = make_fakes(quad)
    sys.modules['newton'] = N
    sys.modules['next_batch'] = NB
    sys.modules.pop('nelder', None)
    import nelder as NM
    d = tempfile.mkdtemp()
    NM.STATE = os.path.join(d, 's.json'); NM.BATCH = os.path.join(d, 'b.txt')
    NM.TRACE = os.path.join(d, 't.txt')
    base_v = {p: '0' for p in NAMES}
    st = {'names': NAMES, 'keys': KEYS, 'base_v': base_v,
          'simplex': [], 'phase': 'shrink', 'shrink_i': 1,
          'pending': None, 'evals': 0, 'history': []}
    # The anchor is set below, once the vertices exist.
    # A simplex whose vertices are far apart and strictly ordered.  Each is
    # actually solved so its tag is in the archive, exactly as in the live run;
    # f is then overridden to force the ordering the audit needs.
    for i in range(K + 1):
        u = [0.5] * K
        if i:
            u[i - 1] = 0.9
        t = solve(NM.vector_for(N, NB, base_v, NAMES, u))
        # ADVERSARIAL ORDERING. The shrunk vertices land near f = 1.84 on this
        # objective, so spacing the starting simplex at 0.0 .. 0.8 makes every
        # shrunk vertex sort BEHIND every vertex not yet shrunk. If anything
        # re-sorts the simplex between one shrink evaluation and the next, the
        # index walk then addresses a different vertex than it means to: one is
        # shrunk twice and one is never shrunk at all. Spacing them 0 .. 8, as
        # this test first did, hides that -- the shrunk values fall INSIDE the
        # range and the order barely moves.
        st['simplex'].append({'u': u, 'f': 0.1 * i, 'tag': t})
    anchor = list(st['simplex'][0]['u'])
    st['shrink_anchor'] = list(anchor)
    before = [list(v['u']) for v in st['simplex']]
    json.dump(st, open(NM.STATE, 'w'))
    argv = sys.argv
    for _ in range(2 * K + 4):
        sys.argv = ['nelder.py', '--ask']
        if NM.main() != 0:
            break
        line = open(NM.BATCH).read().strip()
        v = dict(kv.split('=', 1) for kv in line.split()[1:])
        solve(v)
        sys.argv = ['nelder.py', '--tell']
        NM.main()
        if json.load(open(NM.STATE))['phase'] != 'shrink':
            break
    sys.argv = argv
    st = json.load(open(NM.STATE))
    after = [v['u'] for v in st['simplex']]
    # Every vertex except the anchor must sit exactly halfway to the anchor.
    want = [[a + 0.5 * (b[j] - a) for j, a in enumerate(anchor)]
            for b in before[1:]]
    got = [u for u in after if any(abs(u[j] - anchor[j]) > 1e-12
                                   for j in range(K))]
    ok = len(got) == K
    for w in want:
        if not any(all(abs(w[j] - g[j]) < 1e-9 for j in range(K)) for g in got):
            ok = False
    print(f'{"shrink moves every vertex once":34s} {"":4}         '
          f'{len(got):2d} of {K} moved   {"PASS" if ok else "FAIL"}')
    if not ok:
        print('    wanted, each vertex halfway to the anchor:')
        for w in want:
            print('      ', [round(z, 4) for z in w])
        print('    got:')
        for g in got:
            print('      ', [round(z, 4) for z in g])
    return ok


def main():
    print()
    a, _ = run(quad, [0.0] * K, 400, 'quadratic bowl, min at 0.5', 1e-6)
    b, _ = run(rosen, [0.0] * K, 900, 'Rosenbrock, min at 1.0', 1e-3)
    c = shrink_audit()
    print()
    return 0 if (a and b and c) else 1


if __name__ == '__main__':
    sys.exit(main())
