#!/usr/bin/env python3
"""Move a coupled instrument AND undo its drug-block damage in the same point.

The nested loop -- step the instrument, measure, restore b and lambda_d, measure
-- costs two containers and forty minutes per outer step. But the damage is not
unknown: the correction round measured exactly what each arm does to b and
lambda_d, and restore.py measures how lambda_addiction and addiction_scalar_1
undo it. Composing the two lets one point carry both halves.

    take a FRACTION of the arm's step, predict the b and lambda_d drift from
    that arm's own measured cross-effects, and solve the two-by-two drug block
    for the lambda and addiction_scalar_1 that cancel it

FRACTION IS THE SAFETY. Both halves are log-linear approximations on a surface
known to be curved, so the composition is only as good as the drift is small. A
half step on pi_eu moves b by about +22 per cent, which is inside the band the
drug-block fit was verified over; a full step moves it +44, which is not. The
default is a half step for that reason, not out of caution about the direction.
"""
import glob, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'point_1855f8103d'
FREE = ('lambda_addiction', 'addiction_scalar_1')
B_T, LD_T = 0.089, 0.0368
BOUNDS = {'probability_becoming_unemployed': (1e-6, 0.5),
          'relative_share_of_addiction_1': (0.40, 0.58),
          'value_of_life': (1.0, 500.0),
          'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
          'lambda_addiction': (0.5, 20000.0), 'addiction_scalar_1': (1e-30, 1.0)}

def vec(t):
    m = re.search(r'^\s*VECTOR (.*)$', t, re.M)
    return dict(x.split('=', 1) for x in m.group(1).split() if '=' in x)
def mom(t, n):
    m = re.search(r'MOMENT ' + n + r'\s+\S.*?model=\s*([0-9.eE+-]+)', t)
    return float(m.group(1)) if m else None

def drug_jac():
    groups = {}
    for f in glob.glob(os.path.join(HERE, 'points', '*.txt')):
        t = open(f).read(); v = vec(t)
        b, d = mom(t, 'b'), mom(t, 'lambda_d')
        if not v or not b or not d or b <= 0 or d <= 0: continue
        lam = float(v.get('lambda_addiction', 0))
        if not (15.0 <= lam <= 19.0): continue
        key = tuple(sorted((k, x) for k, x in v.items() if k not in FREE))
        groups.setdefault(key, []).append((lam, float(v['addiction_scalar_1']), b, d))
    best = max(groups.values(), key=len)
    X = np.column_stack([np.ones(len(best)), [math.log(p[0]) for p in best],
                         [math.log(p[1]) for p in best]])
    rows = []
    for i in (2, 3):
        c, *_ = np.linalg.lstsq(X, np.array([math.log(p[i]) for p in best]), rcond=None)
        rows.append(c[1:])
    return np.array(rows), len(best)

def main():
    # THE CAP IS ON THE DAMAGE, NOT ON THE STEP. One fraction for every
    # instrument is the wrong control: a half step on pi_eu drifts b by +20 per
    # cent and a half step on value_of_life drifts it by -61, and only the first
    # is inside the band the drug-block repair was verified over. So each
    # instrument gets the largest fraction that keeps |b drift| under the cap,
    # which lets the weakly coupled ones move properly instead of being held
    # back to the pace of the worst.
    cap = float(sys.argv[1]) if len(sys.argv) > 1 else 0.20
    base = open(os.path.join(HERE, 'points', BASE + '.txt')).read(); bv = vec(base)
    A, n = drug_jac()
    print(f'drug block refit on {n} points, condition {np.linalg.cond(A):.0f}\n')
    arms = {}
    for f in glob.glob(os.path.join(HERE, 'points', '*.txt')):
        t = open(f).read(); v = vec(t)
        if set(v) != set(bv): continue
        d = [k for k in v if v[k] != bv[k]]
        if len(d) == 1 and d[0] in BOUNDS and d[0] not in FREE:
            arms[d[0]] = (t, float(v[d[0]]))
    out = []
    print(f"{'instrument':52s} {'frac':>5s} {'b drift':>8s} {'ld drift':>9s} {'lambda':>8s} {'as1':>10s}")
    for p, (t, x1) in sorted(arms.items()):
        x0 = float(bv[p])
        full_b = math.log(mom(t, 'b') / mom(base, 'b'))
        frac = min(1.0, abs(math.log(1 + cap) / full_b)) if abs(full_b) > 1e-9 else 1.0
        s = frac * math.log(x1 / x0)
        db = frac * full_b
        dd = frac * math.log(mom(t, 'lambda_d') / mom(base, 'lambda_d'))
        fix = np.linalg.solve(A, np.array([-db, -dd]))
        nv = dict(bv)
        lo, hi = BOUNDS[p]; nv[p] = f'{max(lo,min(hi,x0*math.exp(s))):.7g}'
        for q, z in zip(FREE, fix):
            y0 = float(bv[q]); lo2, hi2 = BOUNDS[q]
            nv[q] = f'{max(lo2,min(hi2,y0*math.exp(z))):.7g}'
        print(f'{p:52s} {frac:5.2f} {100*(math.exp(db)-1):+7.0f}% '
              f'{100*(math.exp(dd)-1):+8.0f}% {float(nv["lambda_addiction"]):8.3f} '
              f'{float(nv["addiction_scalar_1"]):10.6f}')
        out.append('bash code/run_one_point.sh ' + ' '.join(f'{k}={nv[k]}' for k in sorted(nv)))
    with open(os.path.join(HERE, 'NESTED.txt'), 'w') as fh:
        fh.write('\n'.join(out) + '\n')
    print(f'\n{len(out)} compensated steps written to NESTED.txt (|b drift| capped at {100*cap:.0f}%)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
