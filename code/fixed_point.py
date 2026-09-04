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


# HARD-DAMPED INSTRUMENTS. Three parameters cannot take the normal step, and the
# reasons are measured, not cautious:
#
#   addiction_scalar_1  a CLIFF. 0.0368 -> lambda_d 0.038198 and 0.04048 ->
#                       0.000223: a ten per cent rise collapses the moment 99.4 per
#                       cent. The same cliff killed the Newton attempt. A normal
#                       step crosses into the dead region, where the moment stops
#                       responding -- which LOOKS like convergence.
#   lambda_addiction    ray reverses and is nearly flat, and it pulls on a
#                       population nested inside addiction_scalar_1's.
#   rr_homeless_old_level  the densest ray we have, twelve points, and it reverses
#                       above the anchor. The ruling holds near the current value
#                       only.
DAMPED = {'addiction_scalar_1': 0.05, 'lambda_addiction': 0.25,
          'rr_homeless_old_level': 0.25}

# NO RULE CAN BE ACTED ON. multiple_of_probabilities_of_employment_if_addicted
# spans its whole bound range, 1 to 32, at slope -1.2e-07 while sud_homeless sits
# at 6.1e-07 against a target of 0.217. An adjuster on it walks the parameter to a
# bound and changes nothing. That is a structural problem -- something prevents
# households with the disorder from becoming homeless -- and it is the author's to
# decide, not an adjuster's to hide.
FROZEN = {'multiple_of_probabilities_of_employment_if_addicted'}


def rules(NB):
    """The author's ruling per moment: which way the PARAMETER goes when the
    MODEL MOMENT IS ABOVE TARGET.

    The author, 4 September: *"you dont need the slope to determine the adjuster
    ....you can reason it out"*, and then ruled on all twenty-one moments one at a
    time. This is the authority. The measured rays remain a CHECK -- fifteen agree,
    and the disagreements are recorded in directions_table.py rather than resolved
    silently in favour of either side.
    """
    import directions_table as D
    out = {}
    for m, (p, rule, _) in D.RULES.items():
        if p in FROZEN or p not in NB.BOUNDS:
            continue
        # 'lower' means parameter and moment move together, so to close a positive
        # gap the parameter must fall: the step carries -gap. 'raise' is the
        # opposite sign.
        out[p] = (m, -1.0 if rule == 'lower' else 1.0)
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
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    A = N.archive()
    if not A:
        say('no points on the live economy; nothing to start from')
        return 1
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    R = rules(NB)
    say(f'{len(A)} points, {len(inst)} instruments, {len(R)} with a ruling')
    for p, (m, sgn) in sorted(R.items()):
        d = f'  damped to {DAMPED[p]:.0%}' if p in DAMPED else ''
        say(f'   {p:<44} {m:<13} {"above -> lower" if sgn < 0 else "above -> raise"}{d}')
    for p in sorted(FROZEN):
        say(f'   {p:<44} FROZEN, its instrument cannot move its moment')

    tag = N.best(A, keys)[1]
    v = dict(A[tag][0])
    mom = A[tag][1]
    say(f'starting from {tag}, SSR {NM.ssr(N, mom, keys):.4f}')

    for it in range(1, ITERS + 1):
        moved = []
        for p, (m, sgn) in R.items():
            if m not in mom or not mom[m][1] or p not in v:
                continue
            model, target = mom[m]
            rel = (model - target) / target
            lo, hi = NB.BOUNDS[p]
            x = float(v[p])
            # THE AUTHOR'S BAND: at most ADJ of the parameter's own value when the
            # moment is 100 per cent off, proportionally less as the gap closes.
            step = sgn * ADJ * DAMPED.get(p, 1.0) * max(-1.0, min(1.0, rel)) \
                * max(abs(x), 1e-12)
            xn = min(max(x + step, lo), hi)
            if abs(xn - x) > 1e-12:
                v[p] = f'{xn:.8g}'
                moved.append((p, x, xn, 100.0 * rel))
        if not moved:
            say(f'iteration {it}: nothing moved; converged or every step clipped')
            return 0
        worst = max(moved, key=lambda z: abs(z[3]))
        say(f'iteration {it}: {len(moved)} moved, worst gap '
            f'{worst[3]:+.1f}% on {worst[0]}')
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
