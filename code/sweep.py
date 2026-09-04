"""Parallel coordinate brackets with a damped, measured assembled step.

*"ok, can you do that instead? but make sure it is automated so it can continue
to work while i sleep"* -- the author, 4 September.

WHY THIS AND NOT NELDER-MEAD. nelder_test.py drives the real Nelder-Mead state
machine against objectives whose minimiser is known:

    quadratic bowl, 20-dim   1200 evals   1.2e-09   PASS
    Rosenbrock,      8-dim    900 evals   4.6e-14   PASS
    Rosenbrock,     20-dim   3000 evals   0.187     FAIL

The implementation is right and the METHOD is wrong at this dimension: it solves
a twenty dimensional bowl and fails a twenty dimensional curved valley with three
thousand evaluations, which is a known property of the method above about ten
dimensions. This objective is the curved kind -- the drug block swings lambda_d
from -4.5 to -96.5 per cent on a 0.35 per cent parameter move -- and three
thousand solves at four minutes each is two hundred hours.

THE METHOD HERE is the one that has produced every real finding: a MEASURED
BRACKET per instrument, never an elasticity. Each round,

  1. probe all twenty instruments, each at two values either side of the base,
     everything else held -- forty INDEPENDENT solves;
  2. for each instrument, interpolate from its own measured pair the value that
     zeroes ITS OWN residual;
  3. assemble all twenty moves into one vector, DAMPED, and measure it;
  4. accept if the sum of squared residuals fell; otherwise halve the damping and
     measure again, and if that keeps failing shrink the probe step and re-round.

Step 4 is what separates this from the Newton attempt, which built a linear model
from finite differences and then trusted it. Nothing here is trusted: the
assembled step is accepted only against a measurement.

The damping exists because each bracket holds the other nineteen instruments
fixed, so a coupled block overshoots. Under Newton the drug pair overshot its own
instruments about threefold, which is why DAMP starts at 0.5 and not at 1.

IT COOPERATES WITH THE FLEET WITHOUT LOCKING. The pending probes are written to
sweep_probes.txt; the loop runs them one at a time and SKIPS any whose vector is
already in the archive. So a worker landing a probe simply removes work from the
local queue, and nothing has to be coordinated.

    python3 code/sweep.py --run        # forever, one point at a time
    python3 code/sweep.py --status
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

STATE  = os.path.join(HERE, '.sweep_state.json')
TRACE  = os.path.join(HERE, 'sweep_trace.txt')
PROBES = os.path.join(HERE, 'sweep_probes.txt')

STEP0   = 0.15   # first probe displacement, as a fraction of the parameter value
STEP_MIN = 0.01
TRUST   = 0.50   # no instrument moves more than this fraction of its value
DAMP0   = 0.50
DAMP_MIN = 0.05


def setup():
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    inst, dead = NM.instruments_all(N, NB)
    return N, NB, inst, [p for p, _ in inst], [m for _, m in inst], dead


def ssr(N, mom, keys):
    return sum(x * x for x in N.residual(mom, keys))


def line(v):
    return 'bash code/run_one_point.sh ' + ' '.join(
        f'{k}={v[k]}' for k in sorted(v)) + '\n'


def find(A, want):
    """The archive tag whose vector is exactly this one, or None."""
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


def probe_values(NB, base, p, step):
    """Two values either side, clipped to the bound, as strings."""
    lo, hi = NB.BOUNDS[p]
    x = float(base[p])
    d = step * abs(x) if abs(x) > 1e-12 else step * max(abs(hi), 1e-6)
    out = []
    for xn in (x - d, x + d):
        xn = min(max(xn, lo), hi)
        if abs(xn - x) > 1e-12 * max(1.0, abs(x)):
            out.append(f'{xn:.8g}')
    return out


def solve(cmd):
    """Run one point. run_one_point.sh skips a tag it has already measured."""
    subprocess.run(cmd, shell=True, cwd=os.path.dirname(HERE),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def say(msg):
    with open(TRACE, 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")}  {msg}\n')
    print(msg, flush=True)


def new_round(N, NB, names, keys, base_tag, A, step):
    """Write every probe for a round and record what each one is for."""
    base = A[base_tag][0]
    jobs, out = [], []
    for p in names:
        for s in probe_values(NB, base, p, step):
            v = dict(base); v[p] = s
            jobs.append({'p': p, 'x': float(s), 'v': v})
            out.append(line(v))
    open(PROBES, 'w').writelines(out)
    return jobs


def interpolate(N, NB, base, p, m, pts, mom0):
    """The value of p that zeroes p's OWN residual, from measured points.

    pts is [(x, residual)] for this instrument, plus the base. A secant through
    the two points that straddle zero, or through the closest pair when none do,
    with the move capped by TRUST and by the bound. An instrument whose residual
    does not respond -- the secant is flat -- does not move, which is the right
    behaviour for a dead column and needs no special case.
    """
    x0 = float(base[p])
    allp = sorted(pts + [(x0, N.residual(mom0, [m])[0])])
    best = None
    for i in range(len(allp) - 1):
        (xa, ra), (xb, rb) = allp[i], allp[i + 1]
        if ra == rb:
            continue
        if (ra <= 0 <= rb) or (rb <= 0 <= ra):
            best = (xa, ra, xb, rb); break
    if best is None:
        cands = [(abs(ra), i) for i, (xa, ra) in enumerate(allp)]
        cands.sort()
        i = cands[0][1]
        j = i + 1 if i + 1 < len(allp) else i - 1
        if j < 0 or allp[i][1] == allp[j][1]:
            return x0
        best = (allp[i][0], allp[i][1], allp[j][0], allp[j][1])
    xa, ra, xb, rb = best
    xn = xa - ra * (xb - xa) / (rb - ra)
    cap = TRUST * abs(x0) if abs(x0) > 1e-12 else TRUST
    xn = min(max(xn, x0 - cap), x0 + cap)
    lo, hi = NB.BOUNDS[p]
    return min(max(xn, lo), hi)


def main():
    args = sys.argv[1:]
    N, NB, inst, names, keys, dead = setup()
    own = dict(inst)

    if os.path.exists(STATE):
        st = json.load(open(STATE))
    else:
        A = N.archive()
        if not A:
            print('no points on the live economy; seed first'); return 1
        _, tag, _, _ = N.best(A, keys)
        st = {'base': tag, 'round': 0, 'step': STEP0, 'damp': DAMP0,
              'phase': 'probe', 'jobs': None, 'names': names, 'keys': keys}
        json.dump(st, open(STATE, 'w'), indent=1)

    if '--status' in args:
        A = N.archive()
        b = st['base']
        print(f'round {st["round"]}  phase {st["phase"]}  base point_{b}  '
              f'SSR {ssr(N, A[b][1], keys):.4f}  step {st["step"]:.3f}  '
              f'damp {st["damp"]:.3f}')
        if os.path.exists(TRACE):
            print(''.join(open(TRACE).readlines()[-12:]))
        return 0

    if '--run' not in args and '--once' not in args:
        print(__doc__); return 1

    while True:
        A = N.archive()
        base_tag = st['base']
        if base_tag not in A:
            say(f'base point_{base_tag} is no longer on this economy; reseeding')
            _, base_tag, _, _ = N.best(A, keys)
            st['base'] = base_tag
        base, mom0 = A[base_tag]
        f0 = ssr(N, mom0, keys)

        if st['phase'] == 'probe':
            if st['jobs'] is None:
                st['round'] += 1
                st['jobs'] = new_round(N, NB, names, keys, base_tag, A, st['step'])
                r = N.residual(mom0, keys)
                say(f'=== ROUND {st["round"]}  base point_{base_tag}  SSR {f0:.4f}  '
                    f'inside {sum(1 for x in r if abs(x) <= 0.10)}/{len(r)}  '
                    f'step {st["step"]:.0%}  {len(st["jobs"])} probes')
                json.dump(st, open(STATE, 'w'), indent=1)
            todo = [j for j in st['jobs'] if find(A, j['v']) is None]
            if todo:
                j = todo[0]
                say(f'  probe {j["p"]} = {j["x"]:.6g}   ({len(todo)} left)')
                solve(line(j['v']).strip())
                if '--once' in args:
                    return 0
                continue
            st['phase'] = 'assemble'; json.dump(st, open(STATE, 'w'), indent=1)
            continue

        if st['phase'] == 'assemble':
            byp = {}
            for j in st['jobs']:
                t = find(A, j['v'])
                if t is None:
                    continue
                m = own[j['p']]
                byp.setdefault(j['p'], []).append(
                    (j['x'], N.residual(A[t][1], [m])[0]))
            v = dict(base); moved = []
            for p in names:
                if p not in byp:
                    continue
                xn = interpolate(N, NB, base, p, own[p], byp[p], mom0)
                x0 = float(base[p])
                xd = x0 + st['damp'] * (xn - x0)
                if abs(xd - x0) > 1e-12 * max(1.0, abs(x0)):
                    v[p] = f'{xd:.8g}'; moved.append((p, x0, xd))
            if not moved:
                say(f'  no instrument moved; shrinking the probe step')
                st['step'] = max(st['step'] * 0.5, STEP_MIN)
                st['phase'] = 'probe'; st['jobs'] = None
                json.dump(st, open(STATE, 'w'), indent=1); continue
            say(f'  assembled step, damp {st["damp"]:.2f}, {len(moved)} instruments moved')
            t = find(A, v)
            if t is None:
                solve(line(v).strip())
                A = N.archive(); t = find(A, v)
            if t is None:
                say('  the assembled point did not solve; halving the damping')
                st['damp'] = max(st['damp'] * 0.5, DAMP_MIN)
                json.dump(st, open(STATE, 'w'), indent=1); continue
            f1 = ssr(N, A[t][1], keys)
            r1 = N.residual(A[t][1], keys)
            ins = sum(1 for x in r1 if abs(x) <= 0.10)
            if f1 < f0:
                say(f'  ACCEPTED  SSR {f0:.4f} -> {f1:.4f}   inside {ins}/{len(r1)}'
                    f'   point_{t}')
                st['base'] = t; st['phase'] = 'probe'; st['jobs'] = None
                st['damp'] = min(DAMP0, st['damp'] * 1.5)
                json.dump(st, open(STATE, 'w'), indent=1)
                if '--once' in args:
                    return 0
            else:
                say(f'  rejected  SSR {f0:.4f} -> {f1:.4f} at damp {st["damp"]:.2f}')
                if st['damp'] > DAMP_MIN:
                    st['damp'] = max(st['damp'] * 0.5, DAMP_MIN)
                else:
                    say('  damping exhausted; shrinking the probe step and re-rounding')
                    st['step'] = max(st['step'] * 0.5, STEP_MIN)
                    st['damp'] = DAMP0
                    st['phase'] = 'probe'; st['jobs'] = None
                    if st['step'] <= STEP_MIN + 1e-12:
                        say('  probe step at its floor with no accepted move: '
                            'this base is a local minimum on every axis probed')
            json.dump(st, open(STATE, 'w'), indent=1)
            continue


if __name__ == '__main__':
    sys.exit(main())
