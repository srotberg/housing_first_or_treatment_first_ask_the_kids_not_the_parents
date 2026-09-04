"""THE SIGN OF EVERY INSTRUMENT, MEASURED, PLUS THE RULE IT IMPLIES.

The author, 4 September: *"you have to know how each parameter affects the model
moment in order to know whether to raise or lower it"*, and *"give me a clear plan
for each of the parameters with reasoning on the direction of the change when the
model moment is above or below"*.

A fixed-point update with a WRONG SIGN runs away from the answer while the trace
looks busy, so no sign here is reasoned -- every one is a finite difference taken
off a measured ray in the archive, using the same ray-finder expand.py uses. Where
the archive has no ray the row says so and the parameter is NOT given a rule.

A ray that is NOT MONOTONE is flagged, because a fixed sign is exactly what such a
parameter must not be given: the response reverses inside the sampled range, and a
constant adjuster will push the wrong way on one side of it.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    import newton as N, next_batch as NB, nelder as NM, expand as E
    NB._apply_process_mapping()
    A = N.archive()
    inst, _ = NM.instruments_all(N, NB, None)
    R = E.rays(A, [p for p, _ in inst])
    _, _, _, mom0 = N.best(A, [m for _, m in inst])

    print(f'\n  {len(A)} points on the live economy\n')
    print(f'  {"parameter":<44} {"moment":<13} {"ray":>3} {"slope":>11}  rule')
    print('  ' + '-' * 108)
    rows = []
    for p, m in sorted(inst, key=lambda z: z[1]):
        if p not in R or m not in mom0:
            print(f'  {p:<44} {m:<13} {"-":>3} {"":>11}  NO RAY, no rule')
            continue
        pts = [(x, mm[m][0]) for x, _, mm in R[p] if m in mm]
        if len(pts) < 2:
            print(f'  {p:<44} {m:<13} {len(pts):>3} {"":>11}  NO RAY, no rule')
            continue
        xs = [a for a, _ in pts]; ys = [b for _, b in pts]
        # Least squares slope over the whole ray, and the monotonicity check.
        n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
        den = sum((a - mx) ** 2 for a in xs)
        slope = sum((a - mx) * (b - my) for a, b in pts) / den if den else 0.0
        mono = all((ys[i + 1] - ys[i]) * slope >= 0 for i in range(n - 1))
        rule = ('above target -> LOWER it' if slope > 0
                else 'above target -> RAISE it')
        flag = '' if mono else '   NOT MONOTONE, no fixed sign'
        print(f'  {p:<44} {m:<13} {n:>3} {slope:>11.4g}  {rule}{flag}')
        rows.append((p, m, slope, mono))
    ok = sum(1 for r in rows if r[3])
    print(f'\n  {len(rows)} instruments have a ray; {ok} are monotone over it '
          f'and can take a fixed sign.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
