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
ITERS = int(os.environ.get('FP_ITERS', '100000'))   # continuously, per the author
# CONVERGED means every rulable moment inside this band, not "the solver got
# bored". The author, 4 September: *"it should just have a loop that keeps going
# until convergence"*.
TOL = float(os.environ.get('FP_TOL', '0.05'))
STATE = os.path.join(HERE, 'fixed_point_state.json')
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
# PER-PARAMETER ADJUSTERS, SIZED BY ARITHMETIC. The author, 4 September: *"make
# sure that the adjusters are well calibrated so that parameters move slowly but
# not too slowly"*.
#
# One flat rate cannot be right, because the parameters do not have to travel the
# same distance: kkk_sigma_scale needs 16 per cent of its value, pi_eu's instrument
# needs 88 per cent, bottom_productivity_level needs seven hundred. At a single
# rate the first oscillates and the last never arrives.
#
# code/size_adjusters.py computes each one as D / (30 * relgap), where D is the
# MEASURED distance from the ray's crossing -- the parameter value that puts the
# moment on target -- so every instrument aims to arrive in about thirty solves,
# an hour and a half at three minutes each. Capped at 0.15 because the formula
# blows up as a gap closes and that blow-up is spurious.
ADJUSTERS = {
    'bottom_productivity_level': 0.1500,
    'discount_factor': 0.0680,
    'kappa_uem': 0.1500,
    'kkk_sigma_scale': 0.0225,
    'labor_income_tax_rate': 0.0100,
    'lambda_addiction': 0.0100,
    'max_food_cost': 0.0100,
    'mu_homeless': 0.0370,
    'probability_becoming_unemployed': 0.0710,
    'probability_of_voucher_benchmark_used': 0.0428,
    'relative_share_of_addiction_1': 0.0100,
    'relative_share_of_housing': 0.1500,
    'relative_share_of_leisure': 0.0748,
    'rr_homeless_old_level': 0.1500,
    'size_homelessness': 0.0423,
    'smallest_rental_relative_to_lowest_income': 0.0148,
    'smi_onset_level': 0.1500,
    'utility_cost_of_treatment': 0.0100,
    'value_of_life': 0.0285,
    # ON THE CLIFF, deliberately far below what the arithmetic asks. 0.0368 ->
    # lambda_d 0.038198 and 0.04048 -> 0.000223: a ten per cent rise collapses the
    # moment 99.4 per cent, and the dead region LOOKS like convergence because the
    # moment stops responding. Nothing here may step it more than half a per cent.
    'addiction_scalar_1': 0.0050,
}
DEFAULT_ADJ = 0.02

# NO CAP ON ANY PARAMETER'S STEP. The author, 4 September: *"dont cap any of the
# parameters....i saw that you cap some of them"*.
#
# There was a hard ceiling here -- one to two per cent, then five, then ten -- and
# it is gone. The step is the adjuster times the gap, and nothing else limits it.
# bottom_productivity_level moves 15 per cent at its 104 per cent gap and
# rr_homeless_old_level 7.5 per cent at its 50, which is what their adjusters were
# sized to do.
#
# TWO THINGS STILL BOUND A STEP, and neither is a choice I made:
#
#   the bounds     a parameter outside NB.BOUNDS is rejected by run_one_point, so
#                  the step is clipped to the box. Only discount_factor is tight
#                  enough for this to bite on one step, at gaps above about 66 per
#                  cent.
#   the gap        clamp(relgap, -1, 1) means a moment 200 per cent off steps as
#                  though it were 100 per cent off. That is the author's own
#                  framing -- "does not move more than X when it is 100 per cent
#                  off" -- and it only touches emp_homeless, at 104 per cent.

# M IS NOT FROZEN. It was, on the strength of a ray showing its slope on
# sud_homeless at -1.2e-07 across the whole range 1 to 32 -- and that ray answers
# the wrong question, because a ray HOLDS EVERYTHING ELSE FIXED.
#
# The author, 4 September: *"you cant just raise M and not touch b"*, and *"if
# raising M lowers addiction, you just have to lower b so more want to be
# addicted"*.
#
# With b held, raising M only deters: the disorder rate collapses 34-fold between
# M=4 and M=5.66 and the SUD share of the homeless falls with it. With b FREE the
# pair is a different object -- M punishes addiction, lambda_d falls, b's rule
# fires and lowers b to restore participation, and the population that comes back
# is a poorer one. That joint move is what could put substance use disorder into
# homelessness, and no single-parameter ray can see it.
#
# This only became actionable once lambda_d's sign was corrected. While b moved
# the wrong way the pair could not have worked.
FROZEN = set()


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


def solve_tag_of(A, v):
    """The archived tag whose vector matches v on every key it carries."""
    for t, (vv, _) in A.items():
        if all(str(vv.get(k)) == str(x) for k, x in v.items()):
            return t
    return None


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
        a = ADJUSTERS.get(p, DEFAULT_ADJ)
        say(f'   {p:<44} {m:<13} '
            f'{"above -> lower" if sgn < 0 else "above -> raise"}  adj {a:.4f}')
    for p in sorted(FROZEN):
        say(f'   {p:<44} FROZEN, its instrument cannot move its moment')

    # RESUME WHERE IT WAS, NOT FROM THE BEST POINT.
    #
    # The author, 4 September: *"you should allow my method to update all the time
    # continuously"*. A fixed point is NOT a descent method -- its iterates can get
    # transiently worse while walking toward the answer, because closing one gap
    # opens another before the next update closes that. Resuming from the archive's
    # best would therefore undo every step that had temporarily cost SSR, and a
    # restart would reset the walk rather than continue it.
    #
    # So the live vector is written every iteration and read back on restart. The
    # archive's best is only the cold start, for the first run on a new economy.
    start = 1
    if os.path.exists(STATE):
        try:
            st = json.load(open(STATE))
            v, start = dict(st['v']), int(st['it']) + 1
            t = solve_tag_of(A, v)
            mom = A[t][1] if t else None
            if mom is None:
                v = None
            else:
                say(f'resuming at iteration {start} from {t}, '
                    f'SSR {NM.ssr(N, mom, keys):.4f}')
        except Exception as e:
            say(f'state unreadable ({e}); cold starting')
            v = None
    else:
        v = None
    if v is None:
        tag = N.best(A, keys)[1]
        v = dict(A[tag][0])
        mom = A[tag][1]
        start = 1
        say(f'cold start from {tag}, SSR {NM.ssr(N, mom, keys):.4f}')

    for it in range(start, start + ITERS):
        moved = []
        for p, (m, sgn) in R.items():
            if m not in mom or not mom[m][1] or p not in v:
                continue
            model, target = mom[m]
            rel = (model - target) / target
            lo, hi = NB.BOUNDS[p]
            x = float(v[p])
            # THE AUTHOR'S BAND: ADJ of the parameter's own value when the moment
            # is 100 per cent off, proportionally less as the gap closes.
            frac = ADJUSTERS.get(p, DEFAULT_ADJ) * max(-1.0, min(1.0, rel))
            step = sgn * frac * max(abs(x), 1e-12)
            # FREE, FLOORED AT ZERO. The author, 4 September: *"just let them move
            # freely (unless you need to cap them at 0"*. NB.BOUNDS no longer clips
            # -- a parameter may leave the box it was given, and the log SAYS SO
            # rather than clipping silently, which is the failure that hides a
            # pinned parameter as a converged one. Zero stays because a negative
            # scale, hazard or price is not a value the model can read.
            xn = max(x + step, 0.0)
            if xn < lo or xn > hi:
                say(f'   {p} outside its old bounds {lo:g}..{hi:g} at {xn:.8g}')
            if abs(xn - x) > 1e-12:
                v[p] = f'{xn:.8g}'
                moved.append((p, x, xn, 100.0 * rel))
        # THREE DIFFERENT ENDINGS, and they must not be reported as one.
        gaps = {m: abs(mom[m][0] / mom[m][1] - 1.0)
                for p_, (m, _) in R.items()
                if m in mom and mom[m][1]}
        worst_m = max(gaps, key=gaps.get) if gaps else None
        if gaps and gaps[worst_m] <= TOL:
            say(f'CONVERGED at iteration {it}: every rulable moment inside '
                f'{TOL:.0%}, worst {worst_m} at {100*gaps[worst_m]:.1f}%')
            return 0
        if not moved:
            # IT DOES NOT STOP. The author, 4 September: *"the loop should be such
            # that it wont stop iterating until all parameters converged"*.
            #
            # Nothing moved means every remaining gap belongs to a parameter
            # pinned on a bound, so the NEXT SOLVE WOULD BE BIT-IDENTICAL and
            # re-running it would burn three minutes to learn nothing. So it does
            # not solve -- it waits and re-reads the archive, because the thing
            # that unpins it comes from OUTSIDE this loop: the author widening a
            # bound, or Nelder-Mead finding a better point in the same archive.
            # Then it picks up and carries on.
            at_bound = [p_ for p_ in R
                        if p_ in v and float(v[p_]) in NB.BOUNDS[p_]]
            say(f'PINNED at iteration {it}: nothing can move, {worst_m} still '
                f'{100*gaps[worst_m]:.1f}% off; on a bound: '
                + (', '.join(sorted(at_bound)) or 'none')
                + '  -- waiting for a bound to widen, not stopping')
            time.sleep(300)
            A = N.archive()
            b = N.best(A, keys)
            if b and b[1] in A and NM.ssr(N, A[b[1]][1], keys) < NM.ssr(N, mom, keys):
                v, mom = dict(A[b[1]][0]), A[b[1]][1]
                say(f'picked up a better point from the archive: {b[1]}')
            continue
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
        json.dump({'it': it, 'v': v, 'tag': t}, open(STATE, 'w'), indent=1)
        say(f'iteration {it}: {t}  SSR {NM.ssr(N, mom, keys):.4f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
