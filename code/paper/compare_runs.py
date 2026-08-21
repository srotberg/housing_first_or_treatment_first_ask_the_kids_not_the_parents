"""
Two runs side by side, on every moment either of them printed.

WHY THIS EXISTS. Turning a mechanism off changes far more than the moment it was
calibrated on, and the question that decides whether the change is acceptable is
never "did the targeted moment survive" alone. It is whether the UNTARGETED ones
moved somewhere indefensible. Reading that off two thousand-line logs by eye
invites finding what one is looking for.

So this joins the two runs on label, marks which moments are calibration targets
by reusing calibration_report's pairing out of the Fortran, and sorts by relative
movement so the largest changes are read first rather than last. A moment that
only one run printed is listed separately: it appeared or vanished, which is
itself a finding.

Run:  python3 compare_runs.py <base.log> <alt.log> [base_label] [alt_label]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import export_moments
import calibration_report


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    a_path, b_path = sys.argv[1], sys.argv[2]
    a_name = sys.argv[3] if len(sys.argv) > 3 else 'base'
    b_name = sys.argv[4] if len(sys.argv) > 4 else 'alt'

    a = export_moments.parse(a_path)
    b = export_moments.parse(b_path)

    # Which labels are somebody's calibration target, so the report can say
    # "this one was supposed to move" versus "this one was not".
    targeted = set()
    try:
        for _, (model_q, _) in calibration_report.pairs().items():
            targeted.add(model_q)
    except Exception:
        pass

    both = sorted(set(a) & set(b))
    rows = []
    for k in both:
        x, y = a[k], b[k]
        if abs(x) < 1e-12 and abs(y) < 1e-12:
            continue
        denom = max(abs(x), 1e-12)
        rel = (y - x) / denom
        rows.append((abs(rel), rel, k, x, y))

    rows.sort(reverse=True)
    print(f'\n{"moment":<58}{a_name:>14}{b_name:>14}{"change":>10}  T')
    print('-' * 100)
    for _, rel, k, x, y in rows:
        if abs(rel) < 0.005:
            continue
        mark = '*' if k in targeted else ' '
        print(f'{k[:57]:<58}{x:>14.5g}{y:>14.5g}{rel*100:>9.1f}%  {mark}')

    print(f'\n{len([r for r in rows if abs(r[1]) >= 0.005])} moments moved by more '
          f'than half a per cent; * marks a calibration target.')

    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    if only_a:
        print(f'\nprinted only by {a_name} ({len(only_a)}): ' + ', '.join(only_a[:12]))
    if only_b:
        print(f'printed only by {b_name} ({len(only_b)}): ' + ', '.join(only_b[:12]))


if __name__ == '__main__':
    main()
