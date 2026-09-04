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
# INSTRUMENTS HELD AT THEIR CURRENT VALUE, each with the reason it is held.
#
# newborn_endowment_scale. The author, 3 September: "Keep the newborn endowment
# off for now." It sits at 0 with a bound of [0, 3], so every move it can make
# ADDS wealth to the young -- and h_share1, the young share of the homeless, is
# already 45 per cent BELOW its target, so the only direction the instrument can
# travel is the wrong one. That is the same test the author set earlier ("keep
# it off if the share of young is below the data"), and the share is below.
#
# The author's fix, same message: "You can also make it negative actually. Some
# young people have a lot of debt!" That is the right sign -- debt pushes the
# young ONTO the street and raises the share -- and it is feasible here, because
# set_renter_floor opens the whole negative financial grid to every household
# once number_of_beta_types is one, which it now is. Turning it on is three
# changes: the HANDOVER clamp at the newborn_endowment_scale case, which floors
# at 0.d0; the BOUNDS entry in next_batch.py; and a lower bound no deeper than
# unsecured_borrowing_limit, 1.50 years of average labour income. None of them
# belong in a step that is already measured and running.
#
# THE MOMENT STAYS IN THE RESIDUAL VECTOR. Holding an instrument is not the same
# as forgiving its moment: h_share1 is the third worst gap and size_homelessness
# moves it hard, so the least-squares step should go on closing it with the
# leverage it does have. Dropping the moment would tell the solver the gap does
# not matter, which is the opposite of what the author asked for.
HOLD = {'newborn_endowment_scale'}

# MOMENTS WHOSE JACOBIAN ROW IS MEANINGLESS, and the instruments that own them.
#
# Measured at the first full step, 3 September, by comparing what the Jacobian
# PREDICTED against what the model did.  Twelve moments came in within a few
# points of prediction over a very large step -- b -0.3, cbar 0.5, pi_eu 0.1,
# sigma_y 0.7, beta 0.4, gamma 0.6, omega_l 1.0, theta 1.1, tau_l 1.3, aleph
# -2.8, lambda_d 4.6, pi_V -6.2 -- and on those Newton did exactly what it is for:
# b, the worst moment in the block, went from 67.6 per cent to 15.8 in one step.
#
# These four did not:
#
#     h_share1      predicted   0.0   actual  +126.7
#     h_1           predicted  -0.3   actual   -84.0
#     emp_homeless  predicted  -9.2   actual   +46.4
#     h_2           predicted   3.9   actual   +18.3
#
# That is not noise and it is not a bad finite-difference step.  At this point 94
# per cent of the model's homeless could afford housing on income alone
# (DIAG homeless who could afford it on INCOME ALONE = 0.9385), so who is on the
# street is a knife-edge discrete choice: the derivative really is near zero
# locally -- the Jacobian measured it correctly -- and then the choice flips.
# size_homelessness moved by 2.7 per cent in that step and the homelessness rate
# fell by 84.  No finite difference will ever describe that, so these rows must
# not go through a linear solve, and the instruments that own them must not be
# moved by one.
#
# THEY ARE NOT CONCEDED.  The moments stay in the residual vector and in every
# report, the instruments keep their bounds, and the block is still to be closed
# -- by a measured bracket, which is what a non-differentiable moment needs and
# what the author's standing preference asks for.  Dropping a row from the linear
# model is a statement about the DERIVATIVE, not about the target.
# NOTHING IS EXCLUDED FROM THE LINEAR MODEL ANY MORE, and nothing is held.
#
# The author, 4 September: *"You should move them all until convergence. Ignore
# young and old homelessness for now."*  Both halves are now true by construction
# rather than by these sets:
#
#   - the two age-share moments, h_share1 and h_share5, are in UNSCORED, and
#     instruments() already skips any instrument whose moment is unscored, so
#     newborn_endowment_scale and ssi_floor_level drop out on their own;
#   - what remains is fifteen scored moments against their own fifteen
#     instruments, and every one of them belongs in the step.
#
# WHY THE EXCLUSIONS EXISTED AND WHY THEY NO LONGER APPLY.  h_1, h_2, h_share1 and
# emp_homeless were taken out of the linear model on 3 September because their
# Jacobian rows were meaningless: predicted 0.0 against an actual +126.7 for
# h_share1, -0.3 against -84.0 for h_1.  That was the age-80 spike moving under
# them.  Since then the street curve has been mapped point by point over
# 0.0425 to 0.070 and h_1 is smooth and monotone along it, with a stable measured
# elasticity.  The row is differentiable now; the old measurement described an
# artefact that is understood.
#
# bottom_productivity_level is measured DEAD -- an eight per cent move shifts
# emp_homeless by two parts in a million -- but it is included rather than held,
# because a dead column costs nothing: the truncated SVD drops it, which is
# exactly what a truncation is for, and holding it by hand would hide from the
# step that emp_homeless has no leverage of its own.
NONSMOOTH = set()
NONSMOOTH_INST = set()
# What a point that predates a switch's NAME actually ran at: the Fortran's
# compile-time default, since run_one_point.sh could not have handed it over.
PREDATE = {'homeless_death_risk_flat_in_age': '0', 'measure_child_gap': '0'}
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
        # EVERY CONFIG SWITCH IS ENFORCED, not just use_pia_formula.
        #
        # This filtered on one name out of the table and nothing said so, which
        # is how homeless_death_risk_flat_in_age came to be added to
        # CONFIG_SWITCHES on 4 September and have no effect at all: the two
        # points solved with the flat 1.6 multiplier POOLED with the 150 solved
        # on Baggett's age profile, and gaps.py ranked two different models of
        # what homelessness does to an old person against each other as one
        # economy.  Nothing in the output distinguished them.
        #
        # The fallback for a point that predates a name is the FORTRAN's
        # compile-time default -- what such a point actually ran at -- and not
        # the live value, which would silently admit it whatever it ran.
        if any(v.get(nm, PREDATE.get(nm, live)) != live
               for nm, live in NB.CONFIG_SWITCHES.items()):
            continue
        out[os.path.basename(f)[6:-4]] = (v, m)
    return out


def best(A, keys):
    """The point with the smallest SUM OF SQUARED residuals over the open moments.

    Was the minimax until 4 September, when the author asked for the sum of squares
    instead. It has to change HERE as well as in gaps.py: report.py takes its point
    from this function and its header from gaps.py, so leaving the two on different
    objectives printed a gap table for one equilibrium and an age profile for a
    DIFFERENT one, in the same report, with nothing saying so.

    The first element of the tuple is still the worst gap, because callers print it
    as the headline and the author's stopping rule is about the worst gap. Only the
    RANKING moved.
    """
    b = None
    for tag, (v, m) in A.items():
        r = residual(m, keys)
        if not r:
            continue
        sq = sum(x * x for x in r)
        if b is None or sq < b[0]:
            b = (sq, tag, v, m, max(abs(x) for x in r))
    if b is None:
        return (9e9, None, None, None)
    return (b[4], b[1], b[2], b[3])


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
        for p, m in [pm for pm in inst if pm[0] not in HOLD | NONSMOOTH_INST]:
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
        json.dump({'base': tag0,
                   'inst': [p for p, _ in inst if p not in HOLD | NONSMOOTH_INST],
                   'all': [p for p, _ in inst], 'keys': keys,
                   'x0': {p: float(v0[p]) for p, _ in inst}},
                  open(STATE, 'w'), indent=1)
        print(f'\nwrote code/batch_newton_J.txt, {len(out)} INDEPENDENT lines')
        return 0

    if '--step' in args:
        st = json.load(open(STATE))
        x0 = st['x0']; keys = st['keys']
        names = [p for p in st['inst'] if p not in HOLD | NONSMOOTH_INST]
        # A point is a clean perturbation of p only if EVERY OTHER instrument is
        # at its base value -- including the held ones. Checking only the free
        # list would let a point that moved a held instrument as well be read as
        # a clean column for p, which is exactly the silent contamination the
        # refusal below exists to prevent.
        allnames = st.get('all', st['inst'])
        base = A.get(st['base'])
        if base is None:
            print('the base of the stored Jacobian is no longer in the archive'); return 1
        r0 = residual(base[1], keys)
        cols, used = [], []
        for p in names:
            hit = None
            for tag, (v, m) in A.items():
                if any(abs(float(v.get(q, x0[q])) - x0[q]) > 1e-12 * max(1, abs(x0[q]))
                       for q in allnames if q != p):
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

        # A PARTIAL JACOBIAN MUST NOT PRODUCE A STEP UNASKED.
        #
        # A missing column does not fail loudly: it silently drops that
        # instrument from the step, so the search stops moving a parameter and
        # nothing in the emitted batch says which one. Run at 19:29 with seven
        # of sixteen columns present, this wrote a full step file that looked
        # exactly like a real one -- nine instruments held at their base values
        # for no reason anybody reading the batch could see.
        #
        # --partial is the override, and it names what is missing rather than
        # quietly proceeding.
        missing = [p for p in names if p not in used]
        if missing and '--partial' not in args:
            print(f'\nREFUSING TO STEP: {len(missing)} of {len(names)} columns are '
                  f'missing, so those instruments would be held silently.')
            for p in missing:
                print(f'    {p}')
            print('\nSolve the rest of batch_newton_J.txt, or pass --partial to step '
                  'on what is here.')
            return 2
        print(f'\nJacobian: {len(r0)} moments x {len(cols)} instruments')

        # COLUMN SCALING. A column is d(residual)/d(instrument) in the
        # instrument's OWN RAW UNITS, and the units are incommensurable: the
        # finite-difference step is 3.36 for value_of_life and 0.00032 for
        # bottom_productivity_level, so the raw columns of this Jacobian span six
        # orders of magnitude in norm. Measured 3 September, the raw diagonal of
        # J^T J ran from 0.109 to 2.24e5, and a single ridge set from the largest
        # of them -- 4474 -- was more than a hundred times the whole diagonal of
        # eleven of the fifteen instruments. The step it produced moved every
        # instrument by under one per cent from a residual of 68 per cent, with
        # nothing capped: the ridge had annihilated the search, and it looked
        # like a converged step rather than a broken one.
        #
        # The unit that makes the columns comparable is the LARGEST MOVE THE
        # INSTRUMENT IS ALLOWED IN ONE ITERATION, because that is what a step
        # actually spends. Writing dx = s * u, a scaled column is the residual
        # change per full permitted move, the trust region becomes |u| <= 1 in
        # every coordinate, and the ridge finally means what it is meant to mean.
        # s is capped by the BOUND as well as by the trust region: scaling by a
        # move the instrument cannot make in either direction would reinstate the
        # same distortion in a quieter form.
        # Only the smooth rows enter the linear model.  r0 and cols keep their
        # full length everywhere else, so the printed step and the residual
        # report still cover every moment.
        lin = [t for t, kk in enumerate(keys) if kk not in NONSMOOTH]
        r0 = [r0[t] for t in lin]
        cols = [[c[t] for t in lin] for c in cols]
        print(f'  linear model on {len(lin)} of {len(keys)} moments; '
              f'{", ".join(sorted(NONSMOOTH))} excluded as non-differentiable')
        n, k = len(r0), len(cols)
        sc = []
        for p in used:
            x = x0[p]; lo, hi = NB.BOUNDS[p]
            cap = TRUST * abs(x) if abs(x) > 1e-12 else TRUST * max(abs(hi), 1e-6)
            sc.append(max(min(cap, max(hi - x, x - lo)), 1e-300))
        JT = [[c * sc[i] for c in cols[i]] for i in range(k)]

        # TRUNCATED SVD, which is what the header promises and what a uniform
        # ridge is not. A ridge shrinks every direction, so it buys stability in
        # the directions the data do not identify by throwing away the ones they
        # do. Truncation drops the weak directions outright and leaves the strong
        # ones at full length, which is the behaviour that stops the b/lambda_d
        # oscillation without also stopping the search.
        #
        # J^T J is symmetric and k is fifteen, so a cyclic Jacobi rotation sweep
        # diagonalises it exactly and needs no numpy. Its eigenvalues are the
        # SQUARED singular values, so the cut is at SV_TOL**2 of the largest.
        JTJ = [[sum(JT[i][t] * JT[j][t] for t in range(n)) for j in range(k)] for i in range(k)]
        JTr = [-sum(JT[i][t] * r0[t] for t in range(n)) for i in range(k)]
        V = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
        for _ in range(100):
            off = max((abs(JTJ[i][j]) for i in range(k) for j in range(k) if i != j),
                      default=0.0)
            if off < 1e-14 * max(abs(JTJ[i][i]) for i in range(k)):
                break
            for i in range(k):
                for j in range(i + 1, k):
                    if abs(JTJ[i][j]) < 1e-300:
                        continue
                    th = 0.5 * (JTJ[j][j] - JTJ[i][i]) / JTJ[i][j]
                    t = (1.0 if th >= 0 else -1.0) / (abs(th) + (th * th + 1.0) ** 0.5)
                    c = 1.0 / (t * t + 1.0) ** 0.5
                    sN = t * c
                    for q in range(k):
                        a, b = JTJ[q][i], JTJ[q][j]
                        JTJ[q][i], JTJ[q][j] = c * a - sN * b, sN * a + c * b
                    for q in range(k):
                        a, b = JTJ[i][q], JTJ[j][q]
                        JTJ[i][q], JTJ[j][q] = c * a - sN * b, sN * a + c * b
                    for q in range(k):
                        a, b = V[q][i], V[q][j]
                        V[q][i], V[q][j] = c * a - sN * b, sN * a + c * b
        lam = [JTJ[i][i] for i in range(k)]
        lmax = max(lam) if lam else 0.0
        cut = (SV_TOL ** 2) * lmax
        kept = 0
        u = [0.0] * k
        for i in range(k):
            if lam[i] <= cut or lam[i] <= 0.0:
                continue
            kept += 1
            g = sum(V[q][i] * JTr[q] for q in range(k)) / lam[i]
            for q in range(k):
                u[q] += g * V[q][i]
        print(f'  kept {kept} of {k} directions; '
              f'singular values span {lmax**0.5:.4g} down to '
              f'{min(l for l in lam if l > 0) ** 0.5:.4g}')
        dx = [u[i] * sc[i] for i in range(k)]

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
