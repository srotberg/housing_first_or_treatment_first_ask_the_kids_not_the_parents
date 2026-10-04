"""A one-time Newton step on the pi_V path of the T = 60 transition, from the model's own voucher accounting.
Holders H(t+1) = rho*H(t) + a*pi_V(t) + c (pi_V(t) steps the residual at t+1: the Fortran's 'THE RESIDUAL AT t STEPS
pi_V(t-1)'), voucher spending S(t) = k*H(t). The budget residual is revenue minus the constraint, so closing it
needs dS(t) = res(t). Fitted on loops 0 and 1 pooled; applied to loop 1's saved path."""
import re, sys
import numpy as np

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
for f in ('loop0_fwd.log', 'loop1_fwd.log'):
    H, S, P, R = rd(f)
    for t in range(1, 59):
        X.append([H[t], P[t], 1.0]); y.append(H[t + 1])
    ks += [S[t] / H[t] for t in range(1, 60)]
X, y = np.array(X), np.array(y)
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
rho, a, c = coef
fit = X @ coef
k = float(np.mean(ks))
print(f'fit H(t+1) = {rho:.4f} H(t) + {a:.4f} pi_V(t) + {c:.4f}; worst miss {np.max(np.abs(fit - y)):.2e} '
      f'(H about {np.mean(y):.2f}); k = S/H = {k:.4f} (range {min(ks):.4f}-{max(ks):.4f})')

H, S, P, R = rd('loop1_fwd.log')
seed = [float(l) for l in open('/home/user/e2_run/code/tr2c_t60/pi_v_path_seed_out.txt')
        if l.strip() and not l.strip().startswith('#')]
assert len(seed) == 59
DAMP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
dH = {1: 0.0}
dpi = [0.0] * 59
for t in range(2, 60):                       # dS(t) = res(t)  ->  dH(t) = res(t)/k
    dH[t] = R[t] / k
    dpi[t - 2] = (dH[t] - rho * dH[t - 1]) / a     # pi_V(t-1) moves H(t)
dpi[58] = dpi[57]                            # the last free period takes t-1's value
new = [max(s + DAMP * d, 0.25 * s) for s, d in zip(seed, dpi)]
print(f'damping {DAMP}')
for t in (1, 2, 3, 5, 10, 20, 30, 40, 45, 50, 55, 59):
    print(f'  t={t:2d}  loop-1 out {100*seed[t-1]:6.2f}  step {100*DAMP*dpi[t-1]:+6.2f}  new {100*new[t-1]:6.2f}  '
          f'res(t+1) {R.get(t+1, float("nan")):+.4f}')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as f:
        f.write(f' # pi_v path: loop 1 (T = 60, 04 Oct) plus a Newton step from the voucher accounting, damping {DAMP}\n'
                f' # H(t+1) = {rho:.5f} H(t) + {a:.5f} pi_V(t) + {c:.5f}; spending = {k:.5f} H; periods 1 to 59\n')
        f.writelines(f'{x:25.15f}\n' for x in new)
    print('written', sys.argv[2])
