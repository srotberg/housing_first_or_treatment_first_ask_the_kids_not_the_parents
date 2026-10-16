# rescale_seeds_CA70.py <run dir> <seed loop dir> <price x0> <pi_V x0> -- remote_tr70_CAu.sh's seeds (16 October, 21:20).
# rescale_seeds_CA.py for a T = 70 run: the converged rule-C T = 50 paths (results/transition_2c_t50_Cu/loop3, 49 years) are
# rescaled onto the rule-CA terminal year by year as there,
#   x_CA(t) = x0 + (x_C(t) - x0) * (x_CA(T) - x0) / (x_C(T) - x0),   t = 1..49,
# which ends exactly on the CA terminal, and held at that terminal for years 50-69. x0 is the no-policy (corrected Housing
# First) value and x_CA(T) the value stage_tr_fix.sh staged flat (the rule-CA terminal arm's). The header carries
# 'CA terminal <x>', which horizon_check_CA.py reads. Only the price and pi_V seeds are replaced; the rent, house price
# and lump sum keep the flat seeds stage_tr_fix.sh wrote.
import sys
n, seeds, p0, v0 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
for name, x0 in (('drug_price', p0), ('pi_v', v0)):
    a = [float(l) for l in open(f'{seeds}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    flat = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    m = len(flat)
    assert len(a) == 49 and m == 69, (name, len(a), m)
    assert max(flat) - min(flat) < 1e-15, (name, 'staged seed not flat')
    xT, aT = flat[0], a[-1]
    assert abs(aT - x0) > 1e-4, (name, aT, x0)
    k = (xT - x0) / (aT - x0)
    assert 0 < k < 20, (name, k)          # the CA terminal on the same side of no policy as rule C's
    vals = [x0 + (x - x0) * k for x in a]
    assert abs(vals[-1] - xT) < 1e-9 * max(1, abs(xT)), (name, vals[-1], xT)
    vals += [xT] * (m - len(vals))
    if name == 'pi_v':
        assert all(1e-5 < v < 1 for v in vals), 'pi_V seed on a bound'
    else:
        assert min(vals) > 0, 'drug price seed not positive'
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: rule C\'s T = 50 ({seeds}) rescaled to rule CA, then held at the terminal: x0 {x0:.9f}, '
                f'rule C end {aT:.9f}, CA terminal {xT:.12f}, factor {k:.4f}\n # periods 1 to {m}\n')
        f.writelines(f'{x:25.15f}\n' for x in vals)
    pick = [1, 2, 5, 10, 25, 49, m]
    print(f'{name}: factor {k:.4f}; ' + ', '.join(f't={t} {vals[t-1]:.6f}' for t in pick))
