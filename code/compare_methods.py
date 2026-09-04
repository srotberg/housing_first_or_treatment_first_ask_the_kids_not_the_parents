"""FIXED POINT AGAINST NELDER-MEAD, ON THE SAME OBJECTIVE, PER MODEL SOLVE.

The author, 4 September: *"i want you to report how my method does relative to
NM"*.

THE COMPARISON MUST BE PER SOLVE, NOT PER MINUTE. The two are not getting equal
compute and cannot be: Nelder-Mead runs in this checkout beside the coordinate
scan, the missing-ray scan and the coverage loop, all four serialised on one flock,
so it gets roughly one solve slot in four. The fixed point has its own container to
itself. Wall-clock would flatter the fixed point for a reason that has nothing to do
with the method.

A model solve is the scarce thing either way, so solves is the honest denominator.

BOTH ARE SCORED ON THE SAME SET -- every moment in every stage, sum of squared
relative residuals -- regardless of which subset either method happens to be
optimising at the time. A method cannot be credited for a scope it chose.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def trajectory(A, N, NM, keys, tags):
    """Running best SSR over an ordered list of point tags."""
    out, best = [], None
    for t in tags:
        if t not in A:
            continue
        f = NM.ssr(N, A[t][1], keys)
        best = f if best is None else min(best, f)
        out.append((t, f, best))
    return out


def main():
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    A = N.archive()
    inst, _ = NM.instruments_all(N, NB, None)
    keys = [m for _, m in inst]

    # THE FIXED POINT'S OWN POINTS, in order, from its trace: each iteration
    # records the vector it built, and the solve that followed is the next point.
    # IT RUNS IN ITS OWN CONTAINER, so its trace is on its branch and not on
    # disk here. Read it from the branch rather than assuming a local copy.
    fp = []
    f = os.path.join(HERE, 'fixed_point_trace.txt')
    raw = ''
    if os.path.exists(f):
        raw = open(f).read()
    else:
        import subprocess
        subprocess.run(['git', 'fetch', '-q', 'origin', 'fixed-point-run'],
                       cwd=os.path.dirname(HERE), capture_output=True)
        r = subprocess.run(['git', 'show', 'FETCH_HEAD:code/fixed_point_trace.txt'],
                           cwd=os.path.dirname(HERE), capture_output=True, text=True)
        raw = r.stdout
    fp = [json.loads(l) for l in raw.splitlines() if l.strip()]

    # NELDER-MEAD'S, from its trace.
    nm = []
    for name in ('nm_trace.txt', 'trace.txt'):
        g = os.path.join(HERE, name)
        if os.path.exists(g):
            nm = [l.split() for l in open(g) if l.strip()]
            break

    print(f'\n  {len(A)} points on the live economy, scored on all {len(keys)} moments\n')
    print(f'  fixed point : {len(fp)} iterations traced')
    print(f'  nelder-mead : {len(nm)} evaluations traced')
    # THE TRACE'S OWN COLUMNS, not a guess at which token is a number. Each line
    # reads: n  time  kind  this <SSR>  best <SSR>  <tag>  inside k/n
    vals = []
    for row in nm:
        try:
            vals.append(float(row[row.index('this') + 1]))
        except (ValueError, IndexError):
            continue
    if vals:
        run, b_ = [], None
        for x in vals:
            b_ = x if b_ is None else min(b_, x)
            run.append(b_)
        print(f'                {len(vals)} solves, first {vals[0]:.4f}, '
              f'running best {run[-1]:.4f}')
        for k in (10, 20, 30, 50, 100, len(run)):
            if k <= len(run):
                print(f'                  after {k:>4} solves   best {run[k-1]:.4f}')

    if not fp or len(fp) < 2:
        print('\n  TOO EARLY. The fixed point has not completed enough iterations to')
        print('  compare. Report again once both have spent a comparable number of')
        print('  model solves -- thirty is where the adjusters were sized to arrive.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
