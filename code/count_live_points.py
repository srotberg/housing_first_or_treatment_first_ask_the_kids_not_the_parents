#!/usr/bin/env python3
"""How many solved points sit on the economy the source currently describes.

WRITTEN BECAUSE THE ONE-LINER FOR IT IS WRONG. The obvious version,

    sum(1 for f in glob(...) if ts._resolve(ts.parse(f)[0]) == sem)

raises TypeError on the first unparseable file, and there are 90 of them in the
archive -- failed solves and pre-format points. It failed exactly that way at
23:24 on 7 September while counting toward the author's 200-iteration mark, so
the count that matters most is the one that must not be improvised.

Prints the count, the number skipped, and whether the archive still resolves to
the live source, which is the check that catches a silent stall: if they differ,
three_step has been exiting 2 and the loop has been dead since they diverged.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model_hash                                   # noqa: E402
import three_step as ts                             # noqa: E402

SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')


def main():
    sem = model_hash.semantic(open(SRC, encoding='utf-8',
                                   errors='surrogateescape').read())
    live = skipped = 0
    for f in glob.glob(os.path.join(HERE, 'points', 'point_*.txt')):
        try:
            parsed = ts.parse(f)
        except Exception:
            skipped += 1
            continue
        if not parsed or not parsed[0]:
            skipped += 1
            continue
        if ts._resolve(parsed[0]) == sem:
            live += 1
    connected = sem == ts._resolve('c9ebefc35f')
    print('economy        %s   %s' % (sem, 'CONNECTED' if connected else
                                      'DISCONNECTED -- the loop is dead'))
    print('live points    %d' % live)
    print('skipped        %d unparseable' % skipped)
    base = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if base is not None:
        print('against base   %d, so %d done' % (base, live - base))
    return 0 if connected else 1


if __name__ == '__main__':
    sys.exit(main())
