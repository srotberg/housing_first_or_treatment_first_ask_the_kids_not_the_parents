"""A second Newton step on the pi_V path, from loop 0_r1's partial forward pass (years 1-45, killed by a container
restart at 10:25 on 5 Oct). Same model as code/transition_2c/newton_piv.py (H(t+1) = rho H(t) + a pi_V(t) + c,
spending k H), refitted on loops 0, 1 and the partial 0_r1; applied to the pi_V path loop 0_r1 ran (the restart seed).
Years with no residual (46-59) take the last measured step."""
import re, sys
import numpy as np
SP = '/tmp/claude-0/-home-user-housing-first-or-treatment-first/43825369-02f4-5759-bc82-a1a582111d14/scratchpad/'
def rd(f):
    H, S, P, R = {}, {}, {}, {}
    for l in open(f, errors='replace'):
        m = re.match(r'\s*TRANSITION VOUCHER CENSUS t=\s*(\d+).*holding=\s*(\S+)', l)
        if m: H[int(m.group(1))] = float(m.group(2))
        m = re.match(r'\s*TRANSITION BUDGET SPEND t=\s*(\d+).*vouchers_2=\s*(\S+)', l)
        if m: S[int(m.group(1))] = float(m.group(2))
        m = re.match(r'\s*TRANSITION MECH t=\s*(\d+).*pi_v=\s*(\S+)', l)
        if m: P[int(m.group(1))] = float(m.group(2))
        m = re.match(r'\s*TRANSITION BUDGET loop=\s*\d+\s+t=\s*(\d+).*residual=\s*(\S+)', l)
        if m: R[int(m.group(1))] = float(m.group(2))
    return H, S, P, R
X, y, ks = [], [], []
for f in ('loop0_fwd.log', 'loop1_fwd.log', 'loop0r1_partial.log'):
    H, S, P, R = rd(SP + f)
    for t in range(1, 59):
        if t in H and t + 1 in H and t in P:
            X.append([H[t], P[t], 1.0]); y.append(H[t + 1])
    ks += [S[t] / H[t] for t in S if t in H]
X, y = np.array(X), np.array(y)
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
rho, a, c = coef
k = float(np.mean(ks))
print(f'fit on {len(y)} points: H(t+1) = {rho:.4f} H(t) + {a:.4f} pi_V(t) + {c:.4f}; worst miss '
      f'{np.max(np.abs(X @ coef - y)):.2e}; k = {k:.4f} ({min(ks):.4f}-{max(ks):.4f})')
H, S, P, R = rd(SP + 'loop0r1_partial.log')
base = [float(l) for l in open('/home/user/housing_first_or_treatment_first/results/transition_2c/restart_r1/pi_v_path_seed.txt')
        if l.strip() and not l.strip().startswith('#')]
assert len(base) == 59
tmax = max(R)
DAMP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
dH = {1: 0.0}
dpi = [None] * 59
for t in range(2, tmax + 1):
    dH[t] = R[t] / k
    dpi[t - 2] = (dH[t] - rho * dH[t - 1]) / a
last = dpi[tmax - 2]
# years without a residual: the last measured step, tapered linearly to zero at year 59, which the terminal steady
# state pins (loop 1's end: pi_V 8.87 left a surplus of the long-run slope times the shortfall to 9.61)
n = 59 - (tmax - 1)
dpi = [d if d is not None else last * (59 - (i + 1)) / n for i, d in enumerate(dpi)]
new = [max(s + DAMP * d, 0.25 * s) for s, d in zip(base, dpi)]
print(f'damping {DAMP}; residuals measured to t={tmax}; years {tmax}-59 taper the year-{tmax-1} step to zero at 59')
for t in (1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 44, 45, 50, 55, 59):
    print(f'  t={t:2d}  ran {100*base[t-1]:6.2f}  step {100*DAMP*dpi[t-1]:+6.3f}  new {100*new[t-1]:6.2f}  '
          f'res(t+1) {R.get(t+1, float("nan")):+.5f}')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as f:
        f.write(f' # pi_v path: the restart seed (loop 0_r1 ran it) plus a second Newton step from loop 0_r1 years 1-{tmax}, damping {DAMP}\n'
                f' # H(t+1) = {rho:.5f} H(t) + {a:.5f} pi_V(t) + {c:.5f}; spending = {k:.5f} H; years {tmax}-59 taper the year-{tmax-1} step to zero at 59\n')
        f.writelines(f'{x:25.15f}\n' for x in new)
    print('written', sys.argv[2])
