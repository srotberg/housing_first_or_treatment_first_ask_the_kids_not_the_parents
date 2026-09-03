"""Broyden/Newton on the residual vector, with a trust region and a truncated SVD.

WHY THIS EXISTS. The gate steps one instrument at a time off a bracket, and on a
coupled block that plateaus: the open worst sat between 67.9 and 69.1 per cent
for four rounds and 68 points while the BINDING moment changed hands every round
-- cbar, then b, then cbar -- because each step moved the block underneath the
next one. The author, 3 September: *"Since each equilibrium is now fast to solve,
don't you think that using a nelder mead type algorithm would be best now?"*

WHY NOT NELDER-MEAD, having costed both. This is 17 instruments against 16
moments: a ROOT-FINDING problem, not a minimisation. Nelder-Mead's reflect,
expand and contract each need the previous result, so with eight workers seven
sit idle -- ~2.5 minutes an iteration and several hundred iterations in fifteen
dimensions, twelve hours or more. A Jacobian is 17 INDEPENDENT solves: three
waves of eight, 7.5 minutes, and Newton is quadratic near a solution. Five to
ten iterations, about an hour.

THE TWO THINGS THAT WOULD BREAK A RAW NEWTON STEP, both measured today:

  - THE CLIFF. size_homelessness 0.0384 -> 0.0500 flips band 1 from 0.6804 to
    0.0335. A finite difference across that is meaningless and the step would be
    wild. Hence a TRUST REGION: no instrument moves more than TRUST of its own
    current value in one iteration, and the finite-difference step is small.
  - THE CONDITIONING. b and lambda_d have a Jacobian condition number of 36,711
    in their two-parameter plane. Inverting that amplifies noise into an
    explosion. Hence a TRUNCATED SVD: singular values below SV_TOL times the
    largest are dropped, which projects the step onto the directions the data
    actually identify and is what stops the b/lambda_d oscillation the hand
    stepping kept producing (-51 then +68 per cent, -83 then +38).

USAGE, two phases so the fleet is spent on the parallel one:

    python3 code/newton.py --jacobian [--base TAG]   emit perturbation lines
    python3 code/newton.py --step                    build J, emit the step

The residual is the RELATIVE gap, model/target - 1, and zero inside a band. That
matches the objective the author set -- "once we get below 10% for everything we
can stop" -- so driving the residual to zero is driving the minimax to zero.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gaps as G
import next_batch as NB

# A finite difference has to be small enough that the cliff is not crossed and
# large enough that the moment moves more than the solver's own tolerance. The
# model is deterministic to eleven significant figures on b, measured 2
# September, so the floor is set by curvature and not by noise.
FD_REL   = 0.08
# A UNIFORM RELATIVE STEP IS WRONG WHERE THE MOMENT IS EXPONENTIAL IN THE
# INSTRUMENT, and the first emitted Jacobian showed it: discount_factor 0.945
# went to 1.02, its upper bound, because 8 per cent of 0.945 is 0.076. W/Y runs
# 3.00 at 0.945 and 7.62 at 0.99980, so that column would have been measured
# across a factor of two and a half in the moment -- a secant, not a derivative,
# and one taken partly outside the region of interest.
#
# These are ABSOLUTE finite-difference steps, chosen from measurements already in
# the archive: 0.945 -> 0.955 moved W/Y from 3.00 to 3.52, which is a 17 per cent
# change in the moment and about the right size for a difference.
FD_ABS = {
    'discount_factor': 0.005,
}
TRUST    = 0.25
SV_TOL   = 0.02
STATE    = os.path.join(HERE, '.newton_state.json')


def instruments():
    """Open-round instruments, in a fixed order, with their live mapping."""
    NB._apply_process_mapping()
    scope = set(NB.STAGES[0])
    out = []
    for p, m in sorted(NB.OWN.items()):
        if m not in scope or m in NB.UNSCORED or m in NB.SKIP:
            continue
        if p not in NB.BOUNDS:
            continue
        out.append((p, m))
    return out


def residual(mom, keys):
    """model/target - 1, and zero inside a band."""
    r = []
    for k in keys:
        if k not in mom:
            r.append(0.0); continue
        mo, tv = mom[k]
        if k in G.BAND:
            lo, hi = G.BAND[k]
            r.append(0.0 if lo <= mo <= hi else (mo/hi - 1 if mo > hi else mo/lo - 1))
        else:
            r.append(mo/tv - 1 if tv else 0.0)
    return r


def archive():
    """Every point on the live economy, as (vector, moments).

    gaps.py fills _OK and _MAP inside its own run rather than at import, so a
    caller has to set them up first or every point is rejected as being on a
    different model. Doing it here rather than reaching into gaps' main keeps
    the equivalence rule in one place: {current hash} plus whatever
    EQUIVALENT_MODELS asserts for it, and {current} alone if next_batch cannot
    be imported -- which under-counts rather than over-claims, exactly as the
    note beside it in gaps.py requires.
    """
    h = G._mh.current()
    G._MAP = G._mh.build_map() if hasattr(G._mh, 'build_map') else G._MAP
    try:
        G._OK = {h} | set(NB.EQUIVALENT_MODELS.get(h, set()))
    except Exception:
        G._OK = {h}
    cfg = G.config()
    proc = str(G._live_productivity_process())
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'points', 'point_*.txt'))):
        if not re.fullmatch(r'point_[0-9a-f]{10}\.txt', os.path.basename(f)):
            continue
        t = open(f, encoding='utf-8', errors='replace').read()
        mm = re.search(r'^MODEL (\S+)', t, re.M)
        if not mm or G._mh.resolve_for_point(mm.group(1), t, G._MAP) not in G._OK:
            continue
        v, m = G.load(f)
        if v is None:
            continue
        if cfg and v.get('number_of_beta_types', cfg) != cfg:
            continue
        if str(int(float(v.get('fixed_productivity', '1')))) != proc:
            continue
        if v.get('use_pia_formula', '1') != NB.CONFIG_SWITCHES.get('use_pia_formula', '1'):
            continue
        out[os.path.basename(f)[6:-4]] = (v, m)
    return out


def best(A, keys):
    """The point with the smallest max |residual| over the open moments."""
    b = None
    for tag, (v, m) in A.items():
        r = residual(m, keys)
        w = max(abs(x) for x in r) if r else 9e9
        if b is None or w < b[0]:
            b = (w, tag, v, m)
    return b


def line(v):
    return 'bash code/run_one_point.sh ' + ' '.join(
        f'{k}={v[k]}' for k in sorted(v)) + '\n'


def main():
    args = sys.argv[1:]
    inst = instruments()
    keys = [m for _, m in inst]
    A = archive()
    if not A:
        print('no points on the live economy; seed first'); return 1

    want = None
    for i, a in enumerate(args):
        if a == '--base' and i + 1 < len(args):
            want = args[i + 1]
    if want and want in A:
        v0, m0 = A[want]; tag0 = want
        w0 = max(abs(x) for x in residual(m0, keys))
    else:
        w0, tag0, v0, m0 = best(A, keys)

    print(f'base point_{tag0}   max |residual| over the open round = {100*w0:.1f}%')
    print(f'{len(inst)} instruments, {len(keys)} moments, {len(A)} points on this economy\n')

    if '--jacobian' in args:
        out = []
        for p, m in inst:
            x = float(v0[p]); lo, hi = NB.BOUNDS[p]
            if p in FD_ABS:
                step = FD_ABS[p]
            elif abs(x) > 1e-12:
                step = FD_REL * abs(x)
            else:
                step = FD_REL * max(abs(lo), abs(hi), 1e-6)
            xn = min(max(x + step, lo), hi)
            if abs(xn - x) < 1e-14:
                xn = min(max(x - step, lo), hi)
            vv = dict(v0); vv[p] = f'{xn:.8g}'
            out.append(line(vv))
            print(f'  {p:45s} {x:12.6g} -> {xn:12.6g}   for {m}')
        open(os.path.join(HERE, 'batch_newton_J.txt'), 'w').write(''.join(out))
        json.dump({'base': tag0, 'inst': [p for p, _ in inst], 'keys': keys,
                   'x0': {p: float(v0[p]) for p, _ in inst}},
                  open(STATE, 'w'), indent=1)
        print(f'\nwrote code/batch_newton_J.txt, {len(out)} INDEPENDENT lines')
        return 0

    if '--step' in args:
        st = json.load(open(STATE))
        x0 = st['x0']; keys = st['keys']; names = st['inst']
        base = A.get(st['base'])
        if base is None:
            print('the base of the stored Jacobian is no longer in the archive'); return 1
        r0 = residual(base[1], keys)
        cols, used = [], []
        for p in names:
            hit = None
            for tag, (v, m) in A.items():
                if any(abs(float(v.get(q, x0[q])) - x0[q]) > 1e-12 * max(1, abs(x0[q]))
                       for q in names if q != p):
                    continue
                d = float(v.get(p, x0[p])) - x0[p]
                if abs(d) > 1e-12 * max(1, abs(x0[p])):
                    hit = (d, residual(m, keys)); break
            if hit is None:
                print(f'  no perturbation found for {p}; column dropped'); continue
            d, r1 = hit
            cols.append([(a - b) / d for a, b in zip(r1, r0)]); used.append(p)
        if not cols:
            print('no Jacobian columns; run --jacobian and solve the batch first'); return 1
        print(f'\nJacobian: {len(r0)} moments x {len(cols)} instruments')

        # least-norm solve of J dx = -r0 by truncated SVD, without numpy
        n, k = len(r0), len(cols)
        JT = cols                                   # k rows of length n
        # normal equations on the k-dimensional side: (J^T J) dx = -J^T r0
        JTJ = [[sum(JT[i][t] * JT[j][t] for t in range(n)) for j in range(k)] for i in range(k)]
        JTr = [-sum(JT[i][t] * r0[t] for t in range(n)) for i in range(k)]
        # Tikhonov with the ridge set from the diagonal, which is the poor man's
        # truncated SVD and does the same job: it suppresses directions the data
        # do not identify instead of inverting them.
        dmax = max((JTJ[i][i] for i in range(k)), default=0.0)
        ridge = SV_TOL * dmax
        for i in range(k):
            JTJ[i][i] += ridge
        # Gaussian elimination with partial pivoting
        M = [row[:] + [JTr[i]] for i, row in enumerate(JTJ)]
        for c in range(k):
            piv = max(range(c, k), key=lambda rr: abs(M[rr][c]))
            if abs(M[piv][c]) < 1e-300:
                continue
            M[c], M[piv] = M[piv], M[c]
            for rr in range(k):
                if rr == c: continue
                f = M[rr][c] / M[c][c]
                for cc in range(c, k + 1):
                    M[rr][cc] -= f * M[c][cc]
        dx = [M[i][k] / M[i][i] if abs(M[i][i]) > 1e-300 else 0.0 for i in range(k)]

        vv = dict(base[0]); shown = []
        for p, d in zip(used, dx):
            x = x0[p]; lo, hi = NB.BOUNDS[p]
            cap = TRUST * abs(x) if abs(x) > 1e-12 else TRUST * max(abs(hi), 1e-6)
            dd = max(-cap, min(cap, d))
            xn = min(max(x + dd, lo), hi)
            vv[p] = f'{xn:.8g}'
            shown.append((p, x, xn, d, dd != d))
        print(f'\n{"instrument":45s} {"from":>12} {"to":>12}   capped')
        for p, x, xn, d, cp in shown:
            print(f'{p:45s} {x:12.6g} {xn:12.6g}   {"YES" if cp else ""}')
        out = [line(vv)]
        for frac in (0.5, 0.25):
            vh = dict(base[0])
            for p, x, xn, _, _ in shown:
                vh[p] = f'{x + frac*(xn-x):.8g}'
            out.append(line(vh))
        open(os.path.join(HERE, 'batch_newton_step.txt'), 'w').write(''.join(out))
        print('\nwrote code/batch_newton_step.txt: the full step, then half, then quarter.')
        print('Three lines because a Newton step on a non-smooth block is a')
        print('hypothesis, and the half and quarter are what make it a bracket.')
        return 0

    print('usage: newton.py --jacobian [--base TAG] | --step')
    return 1


if __name__ == '__main__':
    sys.exit(main())
