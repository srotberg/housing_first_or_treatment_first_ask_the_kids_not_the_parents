# extend_seeds_C70.py <run dir> <T = 50 loop dir> -- remote_tr70_Cu.sh's seeds (16 October; the author: "I say do 70").
# The rule-C T = 50 run's loop-3 paths (price, pi_V, rent, house price, lump sum; years 1-49) are kept as they are for
# years 1-49 and extended to years 50-69 by a geometric approach to the terminal value, half the remaining gap closed
# every five years, not a jump:
#   x(t) = xT + (x(49) - xT) * 0.5 ** ((t - 49) / 5),   t = 50..69
# The price and pi_V terminals are the values stage_tr_fix.sh staged flat (the re-solved terminal Treatment First arm's);
# the house price and rent paths of loop 3 are flat and the lump sum is zero from year 2, so their terminal is their own
# year-49 value. The staged flat price and pi_V files are kept as *_path_seed.staged.txt, and the terminals written to
# terminal_values.txt, so the horizon check can read them after a relaunch has overwritten the seeds.
import sys
n, src = sys.argv[1], sys.argv[2]


def vals(p):
    return [float(l) for l in open(p) if l.strip() and not l.strip().startswith('#')]


staged = {}
for name in ('drug_price', 'pi_v'):
    flat = vals(f'{n}/{name}_path_seed.txt')
    assert len(flat) == 69 and max(flat) - min(flat) < 1e-15, (name, len(flat))
    staged[name] = flat[0]
    with open(f'{n}/{name}_path_seed.staged.txt', 'w') as f:
        f.write(open(f'{n}/{name}_path_seed.txt').read())
out = []
for name in ('drug_price', 'pi_v', 'rent', 'house_price', 'lump_sum'):
    a = vals(f'{src}/{name}_path_seed_out.txt')
    assert len(a) == 49, (name, len(a))
    if name in staged:
        xT, how = staged[name], 'rule-C terminal'
    else:
        xT, how = a[-1], 'terminal (its own year-49 value)'
        assert name == 'lump_sum' or max(a[39:]) - min(a[39:]) < 1e-12, (name, 'not flat over years 40-49')
    x = a + [xT + (a[-1] - xT) * 0.5 ** ((t - 49) / 5) for t in range(50, 70)]
    assert len(x) == 69
    if name == 'pi_v':
        assert all(1e-5 < v < 1 for v in x), 'pi_V seed on a bound'
    if name in ('rent', 'house_price'):
        assert min(x) > 0, name
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: years 1-49 from {src}, years 50-69 half the gap to the {how} {xT:.12f} closed every '
                f'five years\n # periods 1 to 69\n')
        f.writelines(f'{v:25.15f}\n' for v in x)
    out.append(f'{name}: year 1 {x[0]:.6f}, 49 {x[48]:.6f}, 59 {x[58]:.6f}, 69 {x[68]:.6f}, terminal {xT:.6f}')
with open(f'{n}/terminal_values.txt', 'w') as f:
    f.writelines(f'{k} {v:.15f}\n' for k, v in staged.items())
print('; '.join(out))
