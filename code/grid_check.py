"""
Hold two asset grids against each other at IDENTICAL parameters.

WHY THIS EXISTS. The asset grid has been cut twice without ever being checked:
the author shipped fifty positive points, a commit cut it to forty with a
comment saying in as many words that it MUST BE VALIDATED, and a later commit
cut it to twenty five. Neither cut was validated. This is the validation, and
it is a script rather than a hand comparison because the check is wanted again
every time the grid moves.

WHAT MAKES IT LIKE FOR LIKE. The model prints a block of moments after every
distribution solve, and the FIRST such block is the only one that can be
compared across builds, because it is the only one reached with the parameters
still at their declared values. Every later block sits after a parameter update
that used the previous block's moments, so two builds have already drifted apart
by then and a difference no longer says anything about the grid. The script
therefore reads the first block after the first DIST_DONE and nothing else, and
it prints the parameters alongside the moments so that a run which is not in
fact like for like shows itself: if any declared parameter differs, the
comparison is void.

WHAT IT REPORTS. Every key both blocks share, as a relative difference, sorted
worst first. Relative rather than absolute because the block mixes aggregates of
order ten with prevalences of order a thousandth, and only the relative form
ranks them.

Run:  python3 grid_check.py LOG_A LOG_B [label_a label_b]
"""

import re
import sys


def cold_block(path):
    """The moment block that follows the first DIST_DONE, up to loop_count."""
    lines = open(path, errors='ignore').read().splitlines()
    start = None
    for i, line in enumerate(lines):
        if 'DIST_DONE' in line:
            start = i + 1
            break
    if start is None:
        raise SystemExit(f'{path}: no DIST_DONE yet, the first distribution '
                         f'solve has not finished')
    for j in range(start, len(lines)):
        if re.match(r'\s*loop_count=', lines[j]):
            return lines[start:j]
    return lines[start:]


def parse(block):
    """Every `name= numbers` line in the block, first occurrence only.

    First occurrence because a few names are printed again after the update
    that changed them, and the pre-update value is the one that belongs to the
    solve.
    """
    out = {}
    for line in block:
        m = re.match(r'\s*([A-Za-z_][^=]*?)=\s*(.*)$', line.rstrip())
        if not m:
            continue
        key, rest = m.group(1).strip(), m.group(2).strip()
        nums = re.findall(r'[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?', rest)
        if nums and key not in out:
            out[key] = [float(x.replace('D', 'E').replace('d', 'e')) for x in nums]
    return out


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    pa, pb = sys.argv[1], sys.argv[2]
    la = sys.argv[3] if len(sys.argv) > 3 else 'A'
    lb = sys.argv[4] if len(sys.argv) > 4 else 'B'

    a, b = parse(cold_block(pa)), parse(cold_block(pb))
    rows = []
    for key in a:
        if key not in b or len(a[key]) != len(b[key]):
            continue
        for i, (x, y) in enumerate(zip(a[key], b[key])):
            den = max(abs(x), abs(y))
            rel = 0.0 if den < 1e-12 else 100.0 * (y - x) / den
            name = key if len(a[key]) == 1 else f'{key}[{i + 1}]'
            rows.append((abs(rel), name, x, y, rel))
    rows.sort(reverse=True)

    moved = [r for r in rows if r[0] > 0.5]
    print(f'{"":<52s} {la:>14s} {lb:>14s} {"rel":>8s}')
    for _, name, x, y, rel in moved:
        print(f'{name[:52]:<52s} {x:14.6g} {y:14.6g} {rel:7.2f}%')
    print(f'\n{len(rows)} shared numbers, {len(moved)} moved by more than '
          f'half a per cent, {len(rows) - len(moved)} did not')
    if moved:
        print(f'worst: {moved[0][1]} at {moved[0][4]:.2f}%')


if __name__ == '__main__':
    main()
