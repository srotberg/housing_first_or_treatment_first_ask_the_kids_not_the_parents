#!/usr/bin/env python3
"""The loss, generation by generation, so the search can be seen converging.

One point's loss says which combination was best. What tells you whether the
search is working is the SEQUENCE: the best loss in each generation, and the
median, which says whether the whole cloud moved or only its luckiest member.

A point does not record which generation ran it, so the generation is read off
the commit that added the file -- workers commit as "gen3 worker: <arm>". Points
from the first sweep predate that convention and are collected as gen1.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_points                                        # noqa: E402

GEN = re.compile(r'\bgen\s*(\d+)\b', re.I)


def generation_of():
    """filename -> generation, from the commit that first added it."""
    out = subprocess.run(
        ['git', 'log', '--diff-filter=A', '--name-only', '--format=%x00%s', '--', 'code/points'],
        cwd=os.path.dirname(HERE), capture_output=True, text=True).stdout
    where, subject = {}, ''
    for chunk in out.split('\x00'):
        lines = [l for l in chunk.splitlines() if l.strip()]
        if not lines:
            continue
        subject, files = lines[0], lines[1:]
        m = GEN.search(subject)
        gen = int(m.group(1)) if m else 1
        for f in files:
            where.setdefault(os.path.basename(f), gen)
    return where


def by_generation():
    """generation -> best loss in it, for the trust region to read."""
    where = generation_of()
    best = {}
    for path in sorted(os.listdir(os.path.join(HERE, 'points'))):
        if not path.endswith('.txt'):
            continue
        got = score_points.loss(score_points.read(os.path.join(HERE, 'points', path))[1])
        if not got:
            continue
        gen = where.get(path, 1)
        if gen not in best or got[0] < best[gen]:
            best[gen] = got[0]
    return best


def main():
    where = generation_of()
    rows = {}
    for path in sorted(os.listdir(os.path.join(HERE, 'points'))):
        if not path.endswith('.txt'):
            continue
        _head, mt = score_points.read(os.path.join(HERE, 'points', path))
        got = score_points.loss(mt)
        if not got:
            continue
        rows.setdefault(where.get(path, 1), []).append((got[0], path))

    print('%-12s %8s %10s %10s %10s %7s %6s %6s %6s   %s'
          % ('generation', 'points', 'best', 'median', 'worst',
             'w/in 5%', '10%', '25%', '50%', 'best point'))
    print('-' * 118)
    best_so_far = None
    for gen in sorted(rows):
        ls = sorted(rows[gen])
        med = ls[len(ls) // 2][0]
        mark = ''
        if best_so_far is None or ls[0][0] < best_so_far:
            best_so_far = ls[0][0]
            mark = '  <- new best'
        # HOW MANY MOMENTS ARE ACTUALLY NEAR TARGET, beside the loss. The loss is
        # weighted three times on b and lambda_d and twice on theta, aleph and
        # h_1, so it can report a round as worse while the count of moments near
        # target goes up -- which is exactly what generation four did. Both
        # numbers belong in the same table.
        _h, mt = score_points.read(os.path.join(HERE, 'points', ls[0][1]))
        rel = sorted(abs(m - t) / abs(t) for m, t in mt.values()
                     if t and m == m)
        near = [sum(1 for x in rel if x < c) for c in (0.05, 0.10, 0.25, 0.50)]
        print('%-12s %8d %10.3f %10.3f %10.3f %7d %6d %6d %6d   %s%s'
              % ('gen %d' % gen, len(ls), ls[0][0], med, ls[-1][0],
                 near[0], near[1], near[2], near[3], ls[0][1], mark))
    return 0


if __name__ == '__main__':
    sys.exit(main())
