# rescale_seeds_C.py <run dir> <rule-A loop dir> <price x0> <pi_V x0> -- remote_tr50_C.sh's seeds (13 October).
# Rule A's converged T = 70 paths (69 years) keep their shape and are rescaled onto the rule-C run's horizon and terminal:
#   x_C(t) = x0 + (x_A(s) - x0) * (x_C(T) - x0) / (x_A(T) - x0),   s = 1 + (t - 1) * 68 / (T_C - 2)
# x0 the no-policy value, x_A(T) rule A's last year, x_C(T) the value stage_tr_fix.sh staged flat (the rule-C terminal
# arm's), so the path starts where rule A's did relative to its own terminal and ends exactly on rule C's. The
# transition moves each year's price at most 0.5 per cent a loop (max_drug_price_move), so the seed's level matters.
import sys
n, seeds, p0, v0 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
for name, x0 in (('drug_price', p0), ('pi_v', v0)):
    a = [float(l) for l in open(f'{seeds}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(a) == 69, (name, len(a))
    flat = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    m = len(flat)
    assert m >= 3 and max(flat) - min(flat) < 1e-15, (name, m)
    xT, aT = flat[0], a[-1]
    assert abs(aT - x0) > 1e-4, (name, aT, x0)
    k = (xT - x0) / (aT - x0)
    assert 0 < k < 5, (name, k)
    vals = []
    for t in range(1, m + 1):
        s = 1 + (t - 1) * 68 / (m - 1)               # rule A's year, 1..69
        i = min(int(s), 68); w = s - i               # between a[i-1] and a[i]
        xa = a[i - 1] + w * (a[min(i, 68)] - a[i - 1])
        vals.append(x0 + (xa - x0) * k)
    assert abs(vals[-1] - xT) < 1e-9 * max(1, abs(xT)), (name, vals[-1], xT)
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: rule A\'s T = 70 loop 2 ({seeds}) rescaled to rule C: x0 {x0:.9f}, rule A end {aT:.9f}, '
                f'rule-C terminal {xT:.12f}, factor {k:.4f}, 69 years onto {m}\n # periods 1 to {m}\n')
        f.writelines(f'{x:25.15f}\n' for x in vals)
    pick = [1, 2, 5, 10, 25, m]
    print(f'{name}: factor {k:.4f}; ' + ', '.join(f't={t} {vals[t-1]:.6f}' for t in pick))
