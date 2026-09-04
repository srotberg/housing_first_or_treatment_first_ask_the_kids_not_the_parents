"""A MEASURED RANGE FOR EVERY INSTRUMENT, not a displacement around one point.

The author, 4 September: *"all parameters should be sampled across many values so
they have a range to go off of"*.

Two failures made this necessary. The seed displaced every coordinate UPWARD, so
kkk_sigma_scale was never measured below 2.20949 in 1245 points against a lower
bound of 0.8 -- and lower is the direction it has to go, because the bottom half's
income share is BELOW target and a smaller dispersion scale raises it. And the
elasticities that were measured came from single matched pairs, which is exactly
the "mechanism, not a measurement" the standing rule warns about: pbu -> pi_eu read
0.27-0.51 at one step and 0.15 at another.

So: one batch file per instrument, seven values spanning a wide range inside the
hard bounds, everything else held at the anchor. That is a coordinate scan, and it
gives the search a measured curve per instrument instead of a local slope.

Geometric spacing where the bounds span more than a factor of four, linear across
the bounds otherwise, and the anchor's own value is dropped because the base point
is measured once for the whole scan.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import newton as N, next_batch as NB, nelder as NM

N_VALUES = 7
ANCHOR = os.path.join(HERE, 'points', 'point_ce7b2519d4.txt')


def anchor_vector():
    src = open(ANCHOR).read()
    v = dict(kv.split('=', 1)
             for kv in re.search(r'^VECTOR (.*)$', src, re.M).group(1).split())
    # THE AUTHOR'S ECONOMY: homelessness allowed at 84, barred at 85.
    v['max_age_to_choose_homelessness'] = '59'
    return v


def values(x, lo, hi):
    if lo > 0 and x > 0 and hi / lo > 4.0:
        import math
        a, b = math.log(max(lo, x / 8.0)), math.log(min(hi, x * 8.0))
        out = [math.exp(a + (b - a) * i / (N_VALUES - 1)) for i in range(N_VALUES)]
    else:
        a, b = lo, hi
        out = [a + (b - a) * (i + 0.5) / N_VALUES for i in range(N_VALUES)]
    return [t for t in out if abs(t - x) > 1e-9 * max(1.0, abs(x))]


def main():
    NB._apply_process_mapping()
    base = anchor_vector()
    inst, _ = NM.instruments_all(N, NB, None)          # every stage, unioned
    out = os.path.join(HERE, 'scan')
    os.makedirs(out, exist_ok=True)
    line = lambda v: ('bash code/run_one_point.sh '
                      + ' '.join(f'{k}={v[k]}' for k in sorted(v)))
    open(os.path.join(out, '_base.txt'), 'w').write(line(base) + '\n')
    total = 0
    for p, m in inst:
        if p not in NB.BOUNDS:
            print(f'  {p:<45} no bounds, skipped')
            continue
        lo, hi = NB.BOUNDS[p]
        x = float(base.get(p, (lo + hi) / 2))
        vals = values(x, lo, hi)
        lines = []
        for t in vals:
            v = dict(base); v[p] = f'{t:.8g}'
            lines.append(line(v))
        open(os.path.join(out, f'{p}.txt'), 'w').write('\n'.join(lines) + '\n')
        total += len(lines)
        print(f'  {p:<45} {m:<12} {len(lines)} values '
              f'{min(vals):.6g} .. {max(vals):.6g}   (anchor {x:g})')
    print(f'\n  {len(inst)} instruments, {total} points, plus one base')


if __name__ == '__main__':
    main()
