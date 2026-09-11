"""Print a run's moments LOOP BY LOOP, because one loop is not an equilibrium.

WHY THIS EXISTS. calibration_report.py reads the LAST value a log printed for
each quantity, which is the right thing to do once a run has settled and the
wrong thing while it is still settling. On 11 September the benchmark's own log
turned out to hold three different economies:

    loop      b        lambda_d   theta
    1       9.2695%    3.8051%    0.13780
    2       6.7526%    2.5451%    0.17467
    3       6.4771%    2.5159%    0.17870

and every benchmark figure reported up to that morning had been read off loop 1.
The cause is in ENGINE.md: compute_expected_child_value reads the current value
function, so the child term is iterated once per loop with no convergence test,
and loop 1 computes it off a value function solved without it.

So a number quoted out of a log has to say which loop it came from, and whether
the sequence had stopped moving by then. That is what this prints.

    python3 code/loop_trace.py code/worker_<tag>.log [moment ...]

With no moment names it prints the six the drug block turns on. The last column
is the change from the previous loop, which is the only thing that says whether
the run has settled: a run whose moments still move several per cent a loop has
not, whatever its distances say.
"""

import re
import sys

DEFAULT = ['b', 'lambda_d', 'theta', 'tau_u', 'pi_eu', 'h_1']

# " MOMENT b         total drug users            model=   7.66E-002  target=  8.90E-002"
LINE = re.compile(r'^\s*MOMENT\s+(\S+)\s+.*?model=\s*(\S+)\s+target=\s*(\S+)\s*$')
CF = re.compile(r'omega counterfactual: drug users with the child penalty off =\s*(\S+)')
GAP = re.compile(r'model child use gap =\s*(\S+)\s+target =\s*(\S+)')


def fortran_float(s):
    return float(s.replace('D', 'E').replace('d', 'e'))


def read(path):
    """One record per MOMENT block, in order, plus the counterfactual prints."""
    loops, cur, seen, extras = [], {}, set(), []
    with open(path, errors='replace') as f:
        for line in f:
            m = LINE.match(line)
            if m:
                name = m.group(1)
                # A repeated name opens the next block: the print is one pass
                # over a fixed list, so a name never recurs inside one block.
                if name in seen:
                    loops.append(cur)
                    cur, seen = {}, set()
                seen.add(name)
                try:
                    cur[name] = (fortran_float(m.group(2)), fortran_float(m.group(3)))
                except ValueError:
                    pass
                continue
            m = CF.search(line)
            if m:
                extras.append(('counterfactual b', fortran_float(m.group(1))))
                continue
            m = GAP.search(line)
            if m:
                extras.append(('child use gap',
                               (fortran_float(m.group(1)), fortran_float(m.group(2)))))
    if cur:
        loops.append(cur)
    return loops, extras


def block_table(path, n):
    """EVERY moment of ONE loop, which is the only honest way to quote a point.

    calibration_report.py reads the last value in the log, and a run that walks
    THROUGH its target -- which is what value_of_life does at a local elasticity
    near -25 -- leaves the last loop on the far side of it. Loop 7 of arm
    16da70b64e put b within 1.3 per cent of target and loop 8, one capped step
    later, was at -10.4. Quoting the run means quoting loop 8; quoting the point
    means asking for loop 7 by name.
    """
    loops, _ = read(path)
    if not 1 <= n <= len(loops):
        sys.exit(f'{path} has {len(loops)} moment block(s); asked for {n}')
    rows = []
    for name, (model, target) in loops[n - 1].items():
        gap = (model - target) / target * 100 if target else float('nan')
        rows.append((abs(gap), name, model, target, gap))
    rows.sort(reverse=True)
    print(f'{path}, loop {n} of {len(loops)}: every moment it printed\n')
    print(f'{"moment":18s} {"model":>14s} {"target":>14s} {"gap":>9s}')
    print('-' * 58)
    for _, name, model, target, gap in rows:
        mark = '  ON TARGET' if abs(gap) <= 3 else ''
        print(f'{name:18s} {model:>14.6g} {target:>14.6g} {gap:>+8.1f}%{mark}')
    print('-' * 58)
    inside = [r for r in rows if r[0] <= 10]
    med = sorted(r[0] for r in rows)[len(rows) // 2]
    print(f'{len(inside)} of {len(rows)} inside ten per cent; median |gap| {med:.1f}%')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--block':
        return block_table(path, int(sys.argv[3]))
    want = sys.argv[2:] or DEFAULT
    loops, extras = read(path)
    if not loops:
        sys.exit(f'no MOMENT block in {path}')

    print(f'{path}: {len(loops)} moment block(s)\n')
    for name in want:
        present = [(i, L[name]) for i, L in enumerate(loops, 1) if name in L]
        if not present:
            print(f'{name}: not printed in this log')
            continue
        target = present[0][1][1]
        print(f'{name}   target {target:.6g}')
        prev = None
        for i, (model, _) in present:
            gap = (model - target) / target * 100 if target else float('nan')
            move = '' if prev is None else f'{(model - prev) / prev * 100:+8.1f}% on the loop before'
            print(f'    loop {i}  model {model:<14.6g} gap {gap:+7.1f}%   {move}')
            prev = model
        print()

    gaps = [v for k, v in extras if k == 'child use gap']
    if gaps:
        print('child use gap, the moment omega_c is bracketed on')
        prev = None
        for i, (model, target) in enumerate(gaps, 1):
            move = '' if prev is None else f'{(model - prev) / prev * 100:+8.1f}% on the one before'
            print(f'    {i}  model {model:<12.6g} target {target:.6g}   {move}')
            prev = model
        print()

    if len(loops) < 3:
        print('FEWER THAN THREE BLOCKS: nothing here says whether the run settled.')


if __name__ == '__main__':
    main()
