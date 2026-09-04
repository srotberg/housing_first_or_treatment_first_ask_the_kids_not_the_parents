"""WHAT ONE ITERATION ACTUALLY DOES TO EACH PARAMETER, at several gap sizes.

The author, 4 September: *"i want to see the adjuster table with examples of how
quickly a parameter moves when the model is off the target"*.

The update is  x_new = x + sign * ADJ * clamp(relgap, -1, 1) * |x|,  clipped to
bounds. So this prints, for every parameter, the value it would move TO after one
iteration if its moment were 100, 50, 20, 10 and 5 per cent off. Nothing is
modelled or estimated here -- these are the arithmetic the solver performs.

The sign shown is the AUTHOR'S RULING for a model ABOVE target, so the columns are
the direction the parameter goes when the model overshoots.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GAPS = (1.00, 0.50, 0.20, 0.10, 0.05)


def main():
    import newton as N, next_batch as NB, nelder as NM
    import fixed_point as FP, directions_table as D
    NB._apply_process_mapping()
    A = N.archive()
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]
    tag = N.best(A, keys)[1]
    v, mom = A[tag]

    print(f'\n  one iteration, from the current best {tag}')
    print('  columns are the value the parameter moves TO when the model is that '
          'far ABOVE target\n')
    hdr = ' '.join(f'{int(g*100):>11}%' for g in GAPS)
    print(f'  {"parameter":<40} {"adj":>6} {"now":>11} {hdr}')
    print('  ' + '-' * (40 + 7 + 12 + 13 * len(GAPS)))
    rows = []
    for m, (p, rule, _) in D.RULES.items():
        if p in FP.FROZEN or p not in NB.BOUNDS or p not in v:
            continue
        x = float(v[p])
        lo, hi = NB.BOUNDS[p]
        adj = FP.ADJUSTERS.get(p, FP.DEFAULT_ADJ)
        sgn = -1.0 if rule == 'lower' else 1.0
        cells = []
        for g in GAPS:
            xn = min(max(x + sgn * adj * g * abs(x), lo), hi)
            cells.append(xn)
        rows.append((p, m, adj, x, cells, lo, hi))
    rows.sort(key=lambda r: -r[2])
    for p, m, adj, x, cells, lo, hi in rows:
        c = ' '.join(f'{y:>12.6g}' for y in cells)
        print(f'  {p:<40} {adj:>6.4f} {x:>11.6g} {c}')
    print()
    print('  and the same as a per cent change in the parameter, which does not '
          'depend on its level:\n')
    print(f'  {"parameter":<40} {"adj":>6} ' +
          ' '.join(f'{int(g*100):>11}%' for g in GAPS))
    print('  ' + '-' * (40 + 7 + 13 * len(GAPS)))
    for p, m, adj, x, cells, lo, hi in rows:
        c = ' '.join(f'{100*adj*g:>11.2f}%' for g in GAPS)
        print(f'  {p:<40} {adj:>6.4f} {c}')
    print()
    print('  BOUNDS BITE: a cell equal to the bound means the step was clipped.')
    for p, m, adj, x, cells, lo, hi in rows:
        hit = [f'{int(g*100)}%' for g, y in zip(GAPS, cells)
               if abs(y - lo) < 1e-12 or abs(y - hi) < 1e-12]
        if hit:
            print(f'    {p:<40} clipped at gaps {", ".join(hit)}  '
                  f'(bounds {lo:g}..{hi:g})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
