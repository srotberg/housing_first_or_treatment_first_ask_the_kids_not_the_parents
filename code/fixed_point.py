"""THE AUTHOR'S ITERATIVE SOLVER, RUN AGAINST THE MODEL.

*"you have a distance function multiplied by an adjuster. so param = param +
adjuster*(model moment - data)... adjuster small enough so that the param does not
move more than 1-2% between iterations when it is 100% off"*, and *"you should
create this for every single parameter"* -- the author, 4 September.

It is the model's own method: the Fortran carries 78 adjusters and updates, for
instance, kkk_sigma_scale by its own adjuster times (model - data), clipped to
bounds. run_one_point.sh does not iterate that loop -- a point is a single
fixed-parameter solve -- so this drives it from outside, over the handover vector.

WHY IT IS WORTH RUNNING BESIDE NELDER-MEAD. Dimension does not enter. Every
instrument updates from ONE model solve, where a simplex spends twenty-two solves
before it can take a single step. Measured on Rosenbrock at 21 parameters, no
arrangement of Nelder-Mead worked at all (best 4.42 against a 1e-3 tolerance), and
the reason is curvature in high dimension -- which a fixed point does not care
about, because it never builds a simplex.

WHAT CAN GO WRONG, and it is the only thing to be afraid of: A WRONG SIGN RUNS
AWAY FROM THE ANSWER WHILE THE TRACE LOOKS BUSY. So no sign here is reasoned. Each
is a least-squares slope over a MEASURED RAY in the archive -- points identical
except in that one parameter -- and an instrument whose ray reverses inside the
sampled range gets NO RULE AND NO UPDATE, because a constant adjuster pushes the
wrong way on one side of a reversal. On 126 points that was five of eighteen.

THE STEP. With slope D = d(moment)/d(param) and gap g = model - data, the Newton
step is -g/D. That is taken as the DIRECTION and magnitude, then capped at the
author's band: at most ADJ of the parameter's own value when the moment is 100 per
cent off, and proportionally less as the gap closes. So the cap binds far away --
where a Newton step off a secant is not to be trusted anyway -- and releases near
the answer, where it is.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

ADJ = float(os.environ.get('FP_ADJ', '0.02'))   # the author's 1-2 per cent band
ITERS = int(os.environ.get('FP_ITERS', '400'))
LOG = os.path.join(HERE, 'fixed_point.log')
TRACE = os.path.join(HERE, 'fixed_point_trace.txt')


def say(s):
    print(s, flush=True)
    with open(LOG, 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")}  {s}\n')


def slopes(N, NB, NM, E, A, inst):
    """Least-squares slope per instrument over its measured ray, monotone only."""
    R = E.rays(A, [p for p, _ in inst])
    out = {}
    for p, m in inst:
        if p not in R:
            continue
        pts = [(x, mm[m][0]) for x, _, mm in R[p] if m in mm]
        if len(pts) < 3:
            continue
        xs = [a for a, _ in pts]; ys = [b for _, b in pts]
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        den = sum((a - mx) ** 2 for a in xs)
        if den <= 0:
            continue
        s = sum((a - mx) * (b - my) for a, b in pts) / den
        if s == 0 or not all((ys[i + 1] - ys[i]) * s >= 0 for i in range(n - 1)):
            continue                      # reversing ray: no fixed sign, no rule
        out[p] = (s, m)
    return out


def solve(vec):
    """One model solve through run_one_point.sh, which flocks. Returns its tag."""
    cmd = ['bash', 'code/run_one_point.sh'] + [f'{k}={vec[k]}' for k in sorted(vec)]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    mm = re.search(r'point ([0-9a-f]{10})', r.stdout or '')
    if not mm:
        mm = re.search(r'([0-9a-f]{10})', r.stdout or '')
    return mm.group(1) if mm else None


def main():
    import newton as N, next_batch as NB, nelder as NM, expand as E, gaps as G
    NB._apply_process_mapping()
    A = N.archive()
    if not A:
        say('no points on the live economy; nothing to start from')
        return 1
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    S = slopes(N, NB, NM, E, A, inst)
    say(f'{len(A)} points, {len(inst)} instruments, {len(S)} with a monotone ray')
    for p, (s, m) in sorted(S.items()):
        say(f'   {p:<44} {m:<13} slope {s:>11.4g}')
    skipped = [p for p, _ in inst if p not in S]
    if skipped:
        say('NO RULE, left where they are: ' + ', '.join(sorted(skipped)))

    tag, v, mom = N.best(A, keys)[1], None, None
    v = dict(A[tag][0]) if tag in A else dict(next(iter(A.values()))[0])
    mom = A[tag][1] if tag in A else None
    say(f'starting from {tag}')

    for it in range(1, ITERS + 1):
        moved = []
        for p, (s, m) in S.items():
            if m not in mom or not mom[m][1]:
                continue
            model, target = mom[m]
            g = model - target
            lo, hi = NB.BOUNDS[p]
            x = float(v[p])
            newton = -g / s
            relgap = min(1.0, abs(g / target))
            cap = ADJ * relgap * max(abs(x), 1e-9)
            step = max(-cap, min(cap, newton))
            xn = min(max(x + step, lo), hi)
            if abs(xn - x) > 1e-12:
                v[p] = f'{xn:.8g}'
                moved.append((p, x, xn, 100.0 * g / target))
        if not moved:
            say(f'iteration {it}: nothing moved; converged or all capped out')
            return 0
        say(f'iteration {it}: {len(moved)} parameters moved, '
            f'worst gap {max(abs(z[3]) for z in moved):.1f}%')
        with open(TRACE, 'a') as f:
            f.write(json.dumps({'it': it, 'moved': moved}) + '\n')
        t = solve(v)
        if not t:
            say(f'iteration {it}: solve produced no point; stopping')
            return 1
        A = N.archive()
        if t not in A:
            say(f'iteration {it}: {t} not on the live economy; stopping')
            return 1
        mom = A[t][1]
        say(f'iteration {it}: {t}  SSR {NM.ssr(N, mom, keys):.4f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
