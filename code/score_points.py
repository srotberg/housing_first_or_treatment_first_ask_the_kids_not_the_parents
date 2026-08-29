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
# LAMBDA_M CARRIES THE SAME WEIGHT AS H_1. The level of homelessness and its
# composition by mental illness are the same claim from two sides, and the
# paper turns on both. At weight one the search traded the composition away
# for nothing: two vertices reached an identical loss of 0.329 with the SMI
# share of the homeless at 0.095 and at 0.021, a factor of five apart, so the
# moment eta_DI was introduced to own was not disciplining eta_DI at all.
WEIGHT = {'b': 3.0, 'lambda_d': 3.0, 'theta': 2.0, 'aleph': 2.0, 'h_1': 2.0,
          'lambda_m': 2.0}
# A ratio that explodes when its denominator empties is not a miss.
CAP = 5.0

# A CONDITIONAL MOMENT MEASURED OVER NOBODY IS A MISS, NOT A HIT. Most of these
# targets are conditional -- the disordered share of USERS, the mental illness
# share of THE HOMELESS, take-up among THE DISORDERED -- and the model can empty
# the conditioning population. Scoring the reading anyway does not merely lose
# information, it PAYS for the emptying: at the point that led this search,
# homelessness was 0.089 per cent against a target of 0.399, and delta_h came
# back at +1 per cent and lambda_m at -27, both computed over almost nobody. The
# loss read that as two moments nearly on target and ranked the point first,
# ahead of a point whose homelessness was exact.
#
# So a gated moment whose conditioning moment is more than a factor of TOL from
# its own target scores a full CAP. converge.py has had this rule for its
# secants since generation three; the loss never did, which is why the search
# could walk away from a homelessness rate it had already hit.
#
# Keyed by MOMENT here and by PARAMETER in converge.GATE, which is the same
# claim from the two ends of each instrument.
GATE = {
    'lambda_d':  ('b', 3.0),
    'theta':     ('b', 3.0),
    'tau_u':     ('b', 3.0),
    'kappa_ued': ('b', 3.0),
    'lambda_m':  ('h_1', 3.0),
    # omega's gap is a ratio of using populations, so it is meaningless
    # when the baseline one is empty. The model refuses to print it in
    # that case rather than printing a fabricated number, so this is a
    # second line of defence and not the first.
    'omega':     ('b', 3.0),
}


def gated(name, moments):
    """Is this moment being read off a population the model has emptied?"""
    if name not in GATE:
        return False
    cond, tol = GATE[name]
    if cond not in moments:
        return False
    model, target = moments[cond]
    if abs(target) < 1e-12:
        return False
    r = abs(model) / abs(target)
    return r > tol or r < 1.0 / tol

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


# A MOMENT WHOSE PARAMETER IS PINNED IS NOT SCORED, AND IS NOT SCORED FOR ANY
# POINT, old or new. omega is the use rise with the child term off, and
# weight_on_child is pinned while the rest of the block converges; across points
# sharing weight_on_child = 0.007 omega runs from 0.019 to 0.418, because every
# other parameter moves it. Scoring it would charge each point for a gap nothing
# in the search can close, and rank on the noise.
#
# lambda_m joins it for a different reason: zeta_DI, the only instrument that
# moved the SMI share of the homeless, is now set to zero externally, so the
# moment has nothing pointing at it and becomes a validation number rather than
# a target. Scoring an unreachable moment charges every point the same fixed
# penalty and tells the search nothing.
#
# EXCLUDING THEM EVERYWHERE IS WHAT KEEPS THE ARCHIVE COMPARABLE. The loss is a
# MEAN weighted gap, so a point that measured omega and a point that skipped it
# are otherwise on different denominators and cannot be ranked against each
# other. Dropping it from both puts every point back on the same 21 moments.
EXCLUDE = {'omega', 'lambda_m'}


# A TARGET THE DATA GIVES AS A RANGE IS A RANGE, NOT ITS MIDPOINT.
#
# beta, wealth over output, is the case. The declared 3.0 came from BEA private
# fixed assets over NIPA output. The author replaced it on 29 August with
# Piketty and Zucman (2014) and set the range at 3.0 to 4.5: their US figure is
# 4.0 to 4.5 read directly and about 3.4 to 3.8 once converted from national
# income to output, both readings are defensible and the band spans them and the
# old BEA number too. The data does not pin this more finely than a range, and a
# band is the right shape for that.
#
# THE WIDTH IS WHAT DOES THE WORK, NOT THE LEVEL. Under the old point target of
# 3.0 the search was pulled toward a discount factor of 0.9918, where beta is
# 3.03 and b is 0.219 against a target of 0.089 -- so the beta target was
# dragging b, at weight three, off a value it had already hit. The band removes
# that pull and leaves the discount factor free across its whole usable range,
# 0.9918 upward, which the b repair needs: b has to move fourteen fold at
# lambda 30 and this is one of only two instruments with the range for it.
#
# Inside the band the gap is ZERO -- not the distance to a midpoint, because
# there is no midpoint being claimed. Outside it, the gap is measured to the
# nearer edge, so the moment is continuous at both ends.
BAND = {'beta': (3.0, 4.5)}


def band_gap(name, model):
    """Relative distance outside the band, or None if the moment has no band."""
    if name not in BAND:
        return None
    lo, hi = BAND[name]
    if lo <= model <= hi:
        return 0.0
    edge = lo if model < lo else hi
    return abs(model - edge) / abs(edge)


def loss(moments):
    tot, n, worst = 0.0, 0, []
    for name, (model, target) in moments.items():
        if name in EXCLUDE:
            continue
        if abs(target) < 1e-12:
            continue
        bg = band_gap(name, model)
        if gated(name, moments):
            g = CAP
        elif bg is not None:
            g = bg
        else:
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
    return tot / n, len([k for k in moments if k not in EXCLUDE]), worst[:4]


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
    by_w = {}
    for name, w in sorted(WEIGHT.items()):
        by_w.setdefault(w, []).append(name)
    how = ', '.join(f'{w:g}x on ' + ' and '.join(ns)
                    for w, ns in sorted(by_w.items(), reverse=True))
    print(f'{len(rows)} point(s) scored. Lower loss is better. The loss is the mean '
          f'absolute relative gap,\nweighted {how}, and capped at {CAP:.0f} per moment.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
