"""
untargeted_compare.py -- how the untargeted statistics move across points.

    python3 code/paper/untargeted_compare.py point_a.txt point_b.txt ...
    python3 code/paper/untargeted_compare.py --latest 4

WHY A COMPARISON AND NOT A REPORT. validation_report.py prints one point
against the data, which answers "how far off is this". The question here is
different: a parameter moved, and the thing worth seeing is which untargeted
statistics moved with it and in which direction. A single column cannot show
that and two reports side by side have to be diffed by eye.

The data value is carried on the row itself, as "observed=", so it comes from
the Fortran and is not repeated here. A DIAG row has no observed value and is
printed with a blank in that column; it is still worth carrying because most of
what we have been arguing about -- how many of the homeless could pay the rent,
where the cost burden sits, what the homeless earn -- is a DIAG and not an
UNTARGETED.

Rows are ordered by how much they move across the points given, largest first,
so the effect of whatever changed is at the top.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POINTS = os.path.join(HERE, '..', 'points')

UNT = re.compile(r'UNTARGETED\s+(.*?)\s+model=\s*([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)')
DIAG = re.compile(r'DIAG\s+(.*?)\s*=\s*([0-9.eE+-]+)\s*$')


def read(path):
    """label -> (model, observed or None), in the order the point prints them."""
    out = {}
    for line in open(path):
        m = UNT.search(line)
        if m:
            out[m.group(1).strip()] = (float(m.group(2)), float(m.group(3)))
            continue
        m = DIAG.search(line)
        if m:
            label = m.group(1).strip()
            # "DIAG unit 2  share of renters" and the band rows carry an index
            # inside the label, so they stay distinct without extra work.
            out.setdefault(label, (float(m.group(2)), None))
    return out


def tag(path):
    b = os.path.basename(path)
    return b.replace('point_', '').replace('.txt', '')[:10]


def main(argv):
    if argv[:1] == ['--latest']:
        n = int(argv[1]) if len(argv) > 1 else 3
        files = sorted(glob.glob(os.path.join(POINTS, 'point_*.txt')),
                       key=os.path.getmtime)[-n:]
    else:
        files = [f if os.path.exists(f) else os.path.join(POINTS, f) for f in argv]
    if not files:
        print(__doc__)
        return 2

    cols = [read(f) for f in files]
    names = [tag(f) for f in files]

    # A LABEL MISSING FROM ONE POINT IS NOT A ZERO. Points solved before a print
    # was added simply do not have the row, and filling it with anything would
    # invent a movement that never happened. It is shown as a dash instead.
    labels = []
    for c in cols:
        for k in c:
            if k not in labels:
                labels.append(k)

    def spread(label):
        vals = [c[label][0] for c in cols if label in c]
        if len(vals) < 2:
            return -1.0
        lo, hi = min(vals), max(vals)
        return abs(hi - lo) / max(abs(lo), abs(hi), 1e-14)

    labels.sort(key=spread, reverse=True)

    w = max(len(l) for l in labels) + 2
    head = f"{'statistic':<{w}}{'data':>10}" + ''.join(f'{n:>13}' for n in names)
    print(head)
    print('-' * len(head))
    for label in labels:
        obs = next((c[label][1] for c in cols if label in c and c[label][1] is not None), None)
        row = f"{label:<{w}}" + (f"{obs:>10.4g}" if obs is not None else f"{'':>10}")
        for c in cols:
            row += f"{c[label][0]:>13.5g}" if label in c else f"{'-':>13}"
        moved = spread(label)
        print(row + (f"   {100*moved:>6.1f}%" if moved >= 0 else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
