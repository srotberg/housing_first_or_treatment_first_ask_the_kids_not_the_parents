#!/usr/bin/env python3
"""Rank every measured point by how far its moments are from their targets.

WHY A SCORE AND NOT AN EYE. With twenty five containers returning points every
twenty minutes, "which combination was best" has to be a number or it becomes a
matter of which table someone read last. This reads every code/points/*.txt,
computes one loss per point, and ranks them, so the next generation of workers
can be placed around the winner the way a pattern search would.

THE LOSS. Mean absolute RELATIVE gap over the moments a point actually
reported, so moments on different scales count equally: a homelessness rate of
0.004 and a wealth to output ratio of 3 contribute on the same footing. Two
guards matter.

  A moment at or near zero against a positive target contributes a gap of one,
  not of infinity. Those points are empty models, and an unbounded penalty would
  make the ranking about which empty model was least empty.

  A moment the model could not compute is DROPPED rather than scored, and the
  count of scored moments is reported beside the loss. mu_H returns 3e10 when
  nobody homeless has the disorder, which is a division by almost zero, not a
  miss of ten orders of magnitude.

BLOCK C IS WEIGHTED because it is what the paper turns on and what the search is
for. Everything else is held pinned during a sweep, so its gaps are information
about the pins rather than about the point.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHT = {'b': 3.0, 'lambda_d': 3.0, 'theta': 2.0, 'aleph': 2.0, 'h_1': 2.0}
# A ratio that explodes when its denominator empties is not a miss.
CAP = 5.0

ROW = re.compile(r'MOMENT\s+(\S+)\s+.*?model=\s*([-+0-9.eEdD]+)\s+target=\s*([-+0-9.eEdD]+)')


def _f(x):
    return float(x.replace('D', 'E').replace('d', 'e'))


def read(path):
    head, moments = '', {}
    for line in open(path, errors='replace'):
        if line.startswith('point '):
            head = line.strip()
        m = ROW.search(line)
        if m:
            try:
                moments[m.group(1)] = (_f(m.group(2)), _f(m.group(3)))
            except ValueError:
                pass
    return head, moments


def loss(moments):
    tot, n, worst = 0.0, 0, []
    for name, (model, target) in moments.items():
        if abs(target) < 1e-12:
            continue
        g = abs(model - target) / abs(target)
        if g > CAP:
            g = CAP
        w = WEIGHT.get(name, 1.0)
        tot += w * g
        n += w
        worst.append((g, name, model, target))
    if not n:
        return float('inf'), 0, []
    worst.sort(reverse=True)
    return tot / n, len(moments), worst[:4]


def main():
    files = sorted(glob.glob(os.path.join(HERE, 'points', '*.txt')))
    if not files:
        print('no points measured yet: code/points/ is empty')
        return 0
    rows = []
    for f in files:
        head, moments = read(f)
        if not moments:
            print(f'{os.path.basename(f):48s} no moments block (the run failed)')
            continue
        L, n, worst = loss(moments)
        rows.append((L, os.path.basename(f), n, worst, head))
    rows.sort()
    print(f'{"rank":>4} {"loss":>7} {"n":>3}  point')
    print('-' * 100)
    for i, (L, name, n, worst, head) in enumerate(rows, 1):
        print(f'{i:>4} {L:>7.3f} {n:>3}  {name}')
        if i <= 3:
            for g, mom, model, target in worst:
                print(f'{"":>17}worst: {mom:<12s} model {model:>12.6g}  target {target:>10.6g}'
                      f'  off {g*100:.0f}%')
    print('-' * 100)
    print(f'{len(rows)} point(s) scored. Lower loss is better. The loss is the mean '
          f'absolute relative gap,\nweighted 3x on b and lambda_d, 2x on theta, aleph '
          f'and h_1, and capped at {CAP:.0f} per moment.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
