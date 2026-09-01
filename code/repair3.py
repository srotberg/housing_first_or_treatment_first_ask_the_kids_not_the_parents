#!/usr/bin/env python3
"""Hold b, lambda_d AND pi_eu together, on three instruments instead of two.

WHY THREE NOW. Until this morning pi_eu was the blocker and the repair only had
to protect b and lambda_d, so restore.py solves a two by two in
lambda_addiction and addiction_scalar_1. pi_eu is now inside the band at +4 per
cent, which makes it something to defend rather than something to chase -- and
the very first arm of the next round showed why: the kappa_uem step took its own
moment from +65 to +28 per cent and carried pi_eu from +4 to +17, straight back
out. Two employment moments moving together is not a surprise; leaving the repair
blind to it is.

So probability_becoming_unemployed joins lambda_addiction and addiction_scalar_1
as a free instrument, and pi_eu joins b and lambda_d as a protected moment. The
system is square.

WHERE THE THREE BY THREE COMES FROM. Each column is measured, and from a
different experiment, which is the point:

  lambda_addiction, addiction_scalar_1 -> b, lambda_d   the 14-point drug surface
  probability_becoming_unemployed      -> all three     the PEU_LADDER rungs
  lambda_addiction, addiction_scalar_1 -> pi_eu         the secant pair, which
      measured d ln pi_eu = -0.0263 along its own step

Nothing here is assumed. Where a column cannot be measured the tool says so and
refuses rather than filling it with a guess.
"""
import glob, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FREE = ('lambda_addiction', 'addiction_scalar_1', 'probability_becoming_unemployed')
TARGET = {'b': 0.089, 'lambda_d': 0.0368, 'pi_eu': 0.0485}
PROT = ('b', 'lambda_d', 'pi_eu')
BOUNDS = {'lambda_addiction': (0.5, 20000.0), 'addiction_scalar_1': (1e-30, 1.0),
          'probability_becoming_unemployed': (1e-6, 0.5)}
MAX_EFOLD = 0.35


def vec(t):
    # A FILE WITH NO VECTOR LINE IS NOT A POINT. Same fault and same fix as in
    # restore.py: the archive holds .FAILED.txt and .NOMOMENTS.txt records that
    # carry no VECTOR line, and this died on the first one with "'NoneType'
    # object has no attribute 'group'". Callers test for emptiness already.
    m = re.search(r'^\s*VECTOR (.*)$', t, re.M)
    if m is None:
        return {}
    return dict(x.split('=', 1) for x in m.group(1).split() if '=' in x)


def mom(t, n):
    m = re.search(r'MOMENT ' + n + r'\s+\S.*?model=\s*([0-9.eE+-]+)', t)
    return float(m.group(1)) if m else None


def load():
    out = {}
    for f in glob.glob(os.path.join(HERE, 'points', '*.txt')):
        t = open(f).read()
        v = vec(t)
        if v:
            out[os.path.basename(f)[6:-4]] = (v, t)
    return out


def column(A, param, others):
    """d ln(protected moments) / d ln(param), from the controlled pair nearest `others`."""
    best = None
    items = list(A.items())
    for i in range(len(items)):
        ta, (va, ta_) = items[i]
        for j in range(i + 1, len(items)):
            tb, (vb, tb_) = items[j]
            if set(va) != set(vb) or [k for k in va if va[k] != vb[k]] != [param]:
                continue
            xa, xb = float(va[param]), float(vb[param])
            ys = [(mom(ta_, m), mom(tb_, m)) for m in PROT]
            if any(y is None or y <= 0 for pair in ys for y in pair):
                continue
            if abs(math.log(xb / xa)) < 1e-9:
                continue
            dx = math.log(xb / xa)
            col = np.array([math.log(y1 / y0) / dx for y0, y1 in ys])
            d = abs(math.log(xa / float(others[param])))
            if best is None or d < best[1]:
                best = (col, d)
    return best[0] if best else None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    tag = sys.argv[1].replace('point_', '').replace('.txt', '')
    A = load()
    if tag not in A:
        print('no such point'); return 1
    v, t = A[tag]
    cur = {m: mom(t, m) for m in PROT}
    print(f'point_{tag}: ' + ', '.join(
        f'{m} {100*(cur[m]/TARGET[m]-1):+.1f}%' for m in PROT))

    cols, missing = [], []
    for p in FREE:
        c = column(A, p, v)
        if c is None:
            missing.append(p)
        else:
            cols.append(c)
    if missing:
        print('no controlled pair for: ' + ', '.join(missing))
        print('cannot build the three by three; use restore.py instead.')
        return 2
    J = np.column_stack(cols)
    print(f'\nJacobian (rows b, lambda_d, pi_eu; cols {", ".join(FREE)}):')
    for r, m in zip(J, PROT):
        print(f'  {m:10s} ' + '  '.join(f'{x:+8.2f}' for x in r))
    cond = np.linalg.cond(J)
    print(f'  condition number {cond:.0f}')
    if cond > 200:
        print('  WARNING: ill-conditioned; the instruments do not span these three moments here.')

    rhs = np.array([math.log(TARGET[m] / cur[m]) for m in PROT])
    step = np.linalg.solve(J, rhs)
    step = np.clip(step, -MAX_EFOLD, MAX_EFOLD)
    nv = dict(v)
    print()
    for p, s in zip(FREE, step):
        x0 = float(v[p]); lo, hi = BOUNDS[p]
        x1 = max(lo, min(hi, x0 * math.exp(s)))
        nv[p] = f'{x1:.7g}'
        print(f'  {p:34s} {x0:12.6g} -> {x1:12.6g}  ({s:+.3f} e-folds)')
    pred = J @ step
    print('\n  predicted:', ', '.join(
        f'{m} {100*(math.exp(math.log(cur[m])+d)/TARGET[m]-1):+.0f}%' for m, d in zip(PROT, pred)))
    out = os.path.join(HERE, f'REPAIR3_{tag}.txt')
    with open(out, 'w') as fh:
        fh.write('bash code/run_one_point.sh ' +
                 ' '.join(f'{k}={nv[k]}' for k in sorted(nv)) + '\n')
    print(f'\nwritten to {os.path.basename(out)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
