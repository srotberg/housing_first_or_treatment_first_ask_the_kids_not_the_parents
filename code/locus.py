#!/usr/bin/env python3
"""Trace the locus on which b sits exactly on target, and read lambda_d along it.

WHY A LOCUS AND NOT A BRACKET. The author's instruction is to start from the one
point where b is close and there is too much substance use disorder, then lower
the addiction hazard and adjust b as it goes until both land. Those are two
moments and two instruments -- lambda_addiction and addiction_scalar_1 -- so the
solution is a point, but the SEARCH is one dimensional: for each lambda there is
one addiction_scalar_1 that puts b on target, and along that curve lambda_d is a
function of lambda alone. Finding where THAT function crosses its target is a
scalar root find, which is a far easier object than a two dimensional solve.

WHY IT IS BUILT FROM CROSSINGS AND NOT FROM SLOPES. The elasticity of b in
addiction_scalar_1 is about -26 at the centre's nearest neighbours and about -14
across the wider grid, and the local number carried out to lambda 11.8 predicts
b = 0.060 where the model returns 0.138. So a slope measured at one place is not
a slope anywhere else, and the only trustworthy statements are crossings: two
measured points that STRADDLE b = 0.089 pin the addiction_scalar_1 that hits it,
by interpolation rather than extrapolation, and pin lambda_d with it. This reads
the archive for every such straddling pair and reports the locus they define.

The centre is fixed by name rather than by score. It is the only point measured
with b within fifteen per cent of target AND lambda_d ABOVE target, which is the
corner the instruction names, and a scored centre would drift off it.
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CENTRE = 'point_842d561134'
B_TARGET = 0.089
LD_TARGET = 0.0368
# The two coordinates the walk is allowed to move. A point differing from the
# centre in anything else is not on this surface and is dropped, however close
# its lambda happens to be: the four points at lambda 11.8 that also moved
# probability_becoming_unemployed read b from 0.138 to 0.283 at IDENTICAL
# lambda and addiction_scalar_1, which is the whole reason for the filter.
FREE = ('lambda_addiction', 'addiction_scalar_1')


def vector(text):
    m = re.search(r'^\s*VECTOR (.*)$', text, re.M)
    if not m:
        return None
    return dict(tok.split('=', 1) for tok in m.group(1).split() if '=' in tok)


def moment(text, name):
    m = re.search(r'MOMENT ' + name + r'\s+\S.*?model=\s*([0-9.eE+-]+)', text)
    return float(m.group(1)) if m else None


def read_surface():
    """Every archive point differing from the centre ONLY in lambda and as1."""
    cen = vector(open(os.path.join(HERE, 'points', CENTRE + '.txt')).read())
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        text = open(path).read()
        vec = vector(text)
        if not vec or set(vec) != set(cen):
            continue
        moved = [k for k in vec if vec[k] != cen[k]]
        if any(k not in FREE for k in moved):
            continue
        b, ld = moment(text, 'b'), moment(text, 'lambda_d')
        if b is None or ld is None or b <= 0 or ld <= 0:
            continue
        out.append((float(vec['lambda_addiction']), float(vec['addiction_scalar_1']),
                    b, ld, os.path.basename(path)[6:-4]))
    return sorted(out)


def crossings(surface):
    """For each lambda, the as1 that puts b on target -- from straddling pairs only."""
    by_lambda = {}
    for lam, a, b, ld, tag in surface:
        by_lambda.setdefault(lam, []).append((a, b, ld, tag))
    loci = []
    for lam in sorted(by_lambda):
        arm = sorted(by_lambda[lam])
        for (a0, b0, d0, t0), (a1, b1, d1, t1) in zip(arm, arm[1:]):
            lo, hi = min(b0, b1), max(b0, b1)
            if not (lo <= B_TARGET <= hi):
                continue
            f = (math.log(B_TARGET) - math.log(b0)) / (math.log(b1) - math.log(b0))
            loci.append((lam, a0 + f * (a1 - a0),
                         math.exp(math.log(d0) + f * (math.log(d1) - math.log(d0))),
                         t0, t1))
    return loci


def main():
    surface = read_surface()
    print(f"{len(surface)} archive points move ONLY {' and '.join(FREE)} from {CENTRE}\n")
    print(f"{'lambda':>7s} {'as1':>10s} {'b':>9s} {'b gap':>8s} {'lambda_d':>9s} {'ld gap':>8s}  tag")
    for lam, a, b, ld, tag in surface:
        print(f"{lam:7.2f} {a:10.5f} {b:9.5f} {100*(b/B_TARGET-1):+7.1f}% "
              f"{ld:9.5f} {100*(ld/LD_TARGET-1):+7.1f}%  {tag}")

    loci = crossings(surface)
    if not loci:
        print("\nNo lambda arm straddles b = %.4f yet. Bracket one before fitting." % B_TARGET)
        return 1
    print(f"\n=== the b = {B_TARGET} locus, from straddling pairs only ===")
    print(f"{'lambda':>7s} {'as1 on locus':>13s} {'lambda_d':>10s} {'gap':>8s}  from")
    for lam, a, ld, t0, t1 in loci:
        print(f"{lam:7.2f} {a:13.6f} {ld:10.5f} {100*(ld/LD_TARGET-1):+7.1f}%  {t0} / {t1}")

    if len(loci) < 2:
        print("\nOne locus point. A second lambda arm has to straddle b before the "
              "crossing in lambda can be located.")
        return 0

    # Bracket the crossing in lambda: the adjacent pair whose lambda_d gap turns.
    lo = hi = None
    for (l0, a0, d0, *_), (l1, a1, d1, *_) in zip(loci, loci[1:]):
        if (d0 - LD_TARGET) * (d1 - LD_TARGET) <= 0:
            lo, hi = (l0, a0, d0), (l1, a1, d1)
    ends = (lo, hi) if lo else (loci[0][:3], loci[-1][:3])
    (l0, a0, d0), (l1, a1, d1) = ends
    sd = (math.log(d1) - math.log(d0)) / (l1 - l0)
    sa = (a1 - a0) / (l1 - l0)
    lam = l0 + (math.log(LD_TARGET) - math.log(d0)) / sd
    print(f"\nlambda_d crosses {LD_TARGET} at lambda = {lam:.2f}, "
          f"addiction_scalar_1 = {a0 + (lam - l0) * sa:.6f}")
    if lo is None:
        print("  EXTRAPOLATED -- the measured arms do not straddle the target. "
              "Bracket it before trusting this.")
    print(f"\n  as1 locus slope   {sa:+.7f} per unit lambda")
    print(f"  ln lambda_d slope {sd:+.5f} per unit lambda")
    return 0


if __name__ == '__main__':
    sys.exit(main())
