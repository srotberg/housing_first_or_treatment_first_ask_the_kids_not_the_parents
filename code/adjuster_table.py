"""HOW FAST EACH ADJUSTER ACTUALLY MOVES ITS PARAMETER, at the current point.

The author, 4 September: *"did you make sure they update each parameter at a good
pace? show me a table to see how they update parameters for each"*.

The step is  ADJ * clamp(relgap, -1, 1) * |x|,  so what a parameter does on the
NEXT iteration is fully determined by three things this prints: its adjuster, its
current gap, and its current value. The last column is the honest one -- how many
iterations at THIS pace to cover the distance the measured ray says the parameter
has to travel.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    import newton as N, next_batch as NB, nelder as NM, expand as E
    import fixed_point as FP, directions_table as D
    NB._apply_process_mapping()
    A = N.archive()
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    tag = N.best(A, keys)[1]
    v, mom = A[tag]
    R = E.rays(A, [p for p, _ in inst])

    def crossing(pts, t):
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            if (y0 - t) * (y1 - t) <= 0 and y1 != y0:
                return x0 + (x1 - x0) * (t - y0) / (y1 - y0)
        return None

    print(f'\n  at {tag}\n')
    print(f'  {"moment":<13} {"parameter":<40} {"value":>11} {"gap":>8} '
          f'{"adj":>7} {"step now":>10} {"needs":>8} {"iters":>6}')
    print('  ' + '-' * 112)
    rows = []
    for m, (p, rule, _) in D.RULES.items():
        if p in FP.FROZEN or p not in NB.BOUNDS or p not in v or m not in mom:
            continue
        model, target = mom[m]
        if not target:
            continue
        rel = model / target - 1.0
        x = float(v[p])
        adj = FP.ADJUSTERS.get(p, FP.DEFAULT_ADJ)
        step = adj * max(-1.0, min(1.0, abs(rel)))          # as a fraction of |x|
        pts = sorted((a, mm[m][0]) for a, _, mm in R.get(p, []) if m in mm)
        want = crossing(pts, target) if len(pts) >= 2 else None
        dist = abs(want / x - 1.0) if (want is not None and x) else None
        iters = (dist / step) if (dist is not None and step > 0) else None
        rows.append((abs(rel), m, p, x, rel, adj, step, dist, iters))
    rows.sort(reverse=True)
    for _, m, p, x, rel, adj, step, dist, iters in rows:
        d = f'{100*dist:>7.0f}%' if dist is not None else f'{"no ray":>8}'
        i = f'{iters:>6.0f}' if iters is not None else f'{"-":>6}'
        print(f'  {m:<13} {p:<40} {x:>11.5g} {100*rel:>+7.1f}% '
              f'{adj:>7.4f} {100*step:>9.2f}% {d} {i}')
    print('\n  step now = adjuster x gap, as a per cent of the parameter\'s own value')
    print('  needs    = distance to the ray\'s crossing, as a per cent of that value')
    print('  iters    = needs / step, at this pace')
    return 0


if __name__ == '__main__':
    sys.exit(main())
