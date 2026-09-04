"""SIZE EVERY ADJUSTER SO ITS PARAMETER ARRIVES IN A SENSIBLE NUMBER OF SOLVES.

The author, 4 September: *"make sure that the adjusters are well calibrated so that
parameters move slowly but not too slowly"*.

A single adjuster for everything cannot be right, because the parameters do not
have to travel the same distance. sigma_y's instrument needs a few per cent;
pi_eu's needs several hundred. At one flat rate the first oscillates and the second
never arrives.

THE ARITHMETIC. The step is ADJ * relgap * |x|, so the FIRST step covers a fraction
ADJ * relgap of the parameter's value. If the parameter must travel a fraction D of
its value to put its moment on target, then aiming to arrive in TARGET_ITERS solves
means

    ADJ = D / (TARGET_ITERS * relgap)

D is not guessed: it comes from the measured ray, by interpolating for the
parameter value at which the moment crosses its target. Where the ray does not
bracket the target, the distance to the far end of the sampled range is used as a
lower bound on D, which under-steps rather than over-steps.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TARGET_ITERS = 30          # solves to arrive, at three minutes each
# THE CAP IS NOT COSMETIC. ADJ = D / (iters * relgap) blows up as the gap closes,
# and the blow-up is spurious: it happens when a ray's crossing disagrees with the
# current best point, which it will, because the ray was measured at a DIFFERENT
# vector. relative_share_of_housing came out at 0.469 while sitting 0.3 per cent
# from target -- a step that size on a parameter already home is how a fixed point
# starts oscillating. 0.15 is the ceiling: at a 100 per cent gap that is a 15 per
# cent move, well inside stability given the cross-effects measured on this model.
ADJ_MIN, ADJ_MAX = 0.01, 0.15


def crossing(pts, target):
    """Parameter value where the ray's moment crosses target, or None."""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if (y0 - target) * (y1 - target) <= 0 and y1 != y0:
            return x0 + (x1 - x0) * (target - y0) / (y1 - y0)
    return None


def main():
    import newton as N, next_batch as NB, nelder as NM, expand as E
    import directions_table as D
    NB._apply_process_mapping()
    A = N.archive()
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    tag = N.best(A, keys)[1]
    v, mom = A[tag]
    R = E.rays(A, [p for p, _ in inst])

    print(f'\n  best {tag}, aiming to arrive in {TARGET_ITERS} solves\n')
    print(f'  {"parameter":<44} {"gap":>8} {"now":>10} {"needs":>10} '
          f'{"travel":>8} {"ADJ":>7}')
    print('  ' + '-' * 94)
    out = {}
    for m, (p, rule, _) in sorted(D.RULES.items()):
        if p not in NB.BOUNDS or p not in v or m not in mom:
            continue
        model, target = mom[m]
        if not target:
            continue
        rel = abs(model / target - 1.0)
        x = float(v[p])
        pts = sorted((a, mm[m][0]) for a, _, mm in R.get(p, []) if m in mm)
        want = crossing(pts, target) if len(pts) >= 2 else None
        if want is not None and x:
            dist = abs(want / x - 1.0)
            note = ''
        elif pts and x:
            far = max(pts, key=lambda z: abs(z[0] - x))[0]
            dist = abs(far / x - 1.0)
            note = ' (not bracketed; lower bound)'
        else:
            dist, note = 0.30, ' (no ray; default)'
        adj = dist / max(TARGET_ITERS * max(rel, 0.01), 1e-9)
        adj = min(max(adj, ADJ_MIN), ADJ_MAX)
        out[p] = adj
        print(f'  {p:<44} {100*rel:>7.1f}% {x:>10.5g} '
              f'{(want if want is not None else float("nan")):>10.5g} '
              f'{100*dist:>7.0f}% {adj:>7.3f}{note}')
    print('\nADJUSTERS = {')
    for p, a in sorted(out.items()):
        print(f"    '{p}': {a:.4f},")
    print('}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
